#!/usr/bin/env python3
"""Controlled PJSUA endpoints. Run in the authorized NS8 module's Podman context."""
import argparse
import collections
import json
import math
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import socketserver
import stat
import subprocess
import sys
import tempfile
import threading
import time

IMAGE = "ghcr.io/stell0/pjsua@sha256:9a6374528aa19074b4702cb45d6fe8ecd9817cdc492b4aa1265d1b788884389e"


class TestError(RuntimeError):
    """A deliberately sanitized operational error."""


def protected_json(path):
    path = Path(path)
    with path.open() as stream:
        info = os.fstat(stream.fileno())
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise TestError("configuration must be owned by this user with mode 0600")
        return json.load(stream)


def write_private(path, data):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".nvtest-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream, indent=2)
        os.replace(temporary, path)  # Readers never see partially written control/report JSON.
    finally:
        Path(temporary).unlink(missing_ok=True)


def checked(argv, **kwargs):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30, **kwargs)
    except (OSError, subprocess.TimeoutExpired):
        raise TestError("command unavailable or timed out") from None
    if result.returncode:
        raise TestError("command failed (output withheld)")
    return result.stdout


def remove_owned_container(name, label, runtime="podman"):
    """Recovery only: prove the exact container label before forced removal."""
    if not re.fullmatch(r"nvtest-[A-Za-z0-9_-]+-[a-f0-9]{8}", name):
        raise TestError("invalid owned container name")
    exists = subprocess.run([runtime, "container", "exists", name], capture_output=True, timeout=10)
    if exists.returncode == 1:
        return
    if exists.returncode != 0:
        raise TestError("container inventory unavailable")
    actual = checked([runtime, "inspect", "--format", '{{index .Config.Labels "org.nethvoice.test"}}', name]).strip()
    if actual != label:
        raise TestError("container ownership mismatch")
    checked([runtime, "rm", "-f", name])


class Endpoint:
    """One call at a time per endpoint; no auto-answer and no PJSUA TCP CLI."""

    def __init__(self, config, workdir, label, runtime="podman"):
        self.config, self.runtime = config, runtime
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,40}", label):
            raise TestError("invalid endpoint label")
        self.label = label
        self.directory = Path(workdir) / label
        self.directory.mkdir(mode=0o700, parents=True, exist_ok=False)
        self.name = "nvtest-" + label + "-" + secrets.token_hex(4)
        self.process = None
        self.condition = threading.Condition()
        self.input_lock = threading.Lock()
        self.state = {"registration": "starting", "call": "IDLE", "incoming": 0,
                      "generation": 0, "code": None, "registration_code": None, "alive": False,
                      "direction": None}
        self.events = collections.deque(maxlen=2048)
        self.sequence = 0
        self.behavior = "ignore"
        self.reject_code = 486
        self.closed = False
        self.audio_ports = []
        self.audio_pending = False

    def event(self, kind, **values):
        with self.condition:
            self.sequence += 1
            self.events.append(dict(seq=self.sequence, time=time.time(), endpoint=self.label,
                                    kind=kind, **values))
            self.condition.notify_all()

    def snapshot(self):
        with self.condition:
            return dict(self.state, endpoint=self.label, seq=self.sequence, events=list(self.events))

    def feed(self, line):
        """Extract only state, never retain raw SIP/log output or credentials."""
        with self.condition:
            if "Conference ports:" in line:
                self.audio_ports = []
                self.audio_pending = True
            elif "Account list:" in line and self.audio_pending:
                self.audio_pending = False
                self.event("audio-ports", ports=list(self.audio_ports))
            elif self.audio_pending and "Port #" in line:
                match = re.search(r"Port #(\d+)\[.*?\]\s+(.*?)\s+transmitting to:", line)
                if match:
                    name = match[2].lower()
                    role = "call" if "sip:" in name else "file" if ".wav" in name else "device-or-tone"
                    self.audio_ports.append({"id": int(match[1]), "role": role})
            elif "unregistration success" in line:
                self.state["registration"] = "unregistered"
                self.event("registration", state="unregistered")
            elif "registration success" in line:
                self.state["registration"] = "registered"
                self.state["registration_code"] = 200
                self.event("registration", state="registered")
            elif "registration failed" in line or "registration error" in line:
                self.state["registration"] = "failed"
                match = re.search(r"status=(\d+)", line)
                self.state["registration_code"] = int(match[1]) if match else None
                self.event("registration", state="failed", code=self.state["registration_code"])
            elif "Incoming call for account" in line:
                self.state["incoming"] += 1
                self.state["generation"] += 1
                self.state.update(call="INCOMING", code=None, direction="incoming")
                self.event("invite", generation=self.state["generation"])
                # PJSUA otherwise only sends 100 Trying. Send real 180 Ringing.
                self.send("call answer 180")
                if self.behavior == "answer":
                    self.send("call answer 200")
                elif self.behavior == "reject":
                    self.send("call answer " + str(self.reject_code))
            else:
                match = re.search(r"Call (\d+) (?:state changed to (\w+)|is (DISCONNECTED))(?:.*?reason=(\d+))?", line)
                if match:
                    state = match[2] or match[3]
                    self.state["call"] = state
                    if match[4]:
                        self.state["code"] = int(match[4])
                    self.event("call", state=state, code=self.state["code"],
                               generation=self.state["generation"])
            self.condition.notify_all()

    def _reader(self):
        try:
            for line in self.process.stdout:
                self.feed(line)
        finally:
            with self.condition:
                self.state["alive"] = False
                self.event("exit")

    def start(self, timeout=20):
        cfg = self.config
        for key in ("username", "password", "domain", "registrar", "proxy"):
            value = str(cfg.get(key, ""))
            if not value or any(c.isspace() for c in value) or any(c in value for c in '\\"\x00'):
                raise TestError("missing or unsafe SIP configuration field: " + key)
        for key in ("sip_port", "rtp_port"):
            if not 1024 <= int(cfg[key]) <= 65000:
                raise TestError("invalid endpoint port")
        options = ["--id=sip:" + cfg["username"] + "@" + cfg["domain"],
                   "--registrar=" + cfg["registrar"], "--proxy=" + cfg["proxy"],
                   "--realm=*", "--username=" + cfg["username"], "--password=" + cfg["password"],
                   "--local-port=" + str(cfg["sip_port"]), "--rtp-port=" + str(cfg["rtp_port"]),
                   "--null-audio", "--no-tcp", "--max-calls=1", "--use-cli",
                   "--log-level=4", "--app-log-level=4", "--no-color", "--reg-timeout=120",
                   "--duration=" + str(int(cfg.get("duration", 120)))]
        mounts = []
        for key, option in (("play_file", "--play-file"), ("record_file", "--rec-file")):
            if cfg.get(key):
                path = Path(cfg[key]).resolve()
                mounts += ["-v", str(path.parent) + ":/" + key + ":Z"]
                options += [option + "=/" + key + "/" + path.name]
                if key == "record_file":
                    options += ["--auto-rec"]
        config_file = self.directory / "pjsua.conf"
        config_file.write_text("\n".join(options) + "\n")
        config_file.chmod(0o600)
        argv = [self.runtime, "run", "--rm", "-i", "--name", self.name,
                "--label", "org.nethvoice.test=" + self.label, "--network", "host",
                "--entrypoint", "/usr/bin/stdbuf",
                "-v", str(self.directory.resolve()) + ":/run/nvtest:ro,Z", *mounts,
                cfg.get("image", IMAGE), "-oL", "-eL", "/usr/local/bin/pjsua",
                "--config-file=/run/nvtest/pjsua.conf"]
        try:
            self.process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                            stderr=subprocess.STDOUT, text=True, bufsize=1)
            self.state["alive"] = True
            threading.Thread(target=self._reader, daemon=True).start()
            self.wait(lambda s: s["registration"] == "registered", timeout)
            return self.snapshot()
        except BaseException:
            self.close()
            raise

    def send(self, command):
        if not self.process or self.process.poll() is not None:
            raise TestError("SIP client exited")
        with self.input_lock:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
            except (BrokenPipeError, OSError):
                raise TestError("SIP client pipe failed") from None

    def wait(self, predicate, timeout=20):
        if not math.isfinite(timeout) or timeout <= 0 or timeout > 300:
            raise TestError("wait timeout must be between 0 and 300 seconds")
        deadline = time.monotonic() + timeout
        with self.condition:
            while not predicate(self.snapshot()):
                if self.state["registration"] == "failed":
                    raise TestError("SIP registration failed (status=" + str(self.state["registration_code"]) + ")")
                if not self.state["alive"]:
                    raise TestError("SIP client exited")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TestError("SIP state timeout")
                self.condition.wait(remaining)
        return self.snapshot()

    def action(self, action, **params):
        if action in ("ring", "no-answer", "behavior"):
            behavior = params.get("behavior", "ignore")
            if behavior not in ("answer", "ignore", "reject"):
                raise TestError("invalid incoming-call behavior")
            code = int(params.get("code", 486))
            if not 300 <= code <= 699:
                raise TestError("invalid rejection code")
            self.behavior, self.reject_code = behavior, code
        elif action == "call":
            destination = str(params["destination"])
            if destination not in self.config.get("allowed_destinations", []):
                raise TestError("destination outside authorized internal allowlist")
            if self.state["call"] not in ("IDLE", "DISCONNECTED"):
                raise TestError("endpoint already has a call")
            self.state["generation"] += 1
            self.state.update(call="CALLING", code=None, direction="outgoing")
            self.send("call new sip:" + destination + "@" + self.config["domain"])
        elif action in ("answer", "reject"):
            if self.state["call"] not in ("INCOMING", "EARLY"):
                raise TestError("no ringing incoming call")
            code = int(params.get("code", 200 if action == "answer" else 486))
            if action == "reject" and not 300 <= code <= 699:
                raise TestError("invalid rejection code")
            if action == "answer" and code != 200:
                raise TestError("answer uses status 200")
            self.send("call answer " + str(code))
        elif action == "hangup":
            self.send("call hangup_all")
        elif action in ("register", "unregister"):
            self.state["registration"] = "pending"
            self.send("acc " + ("reg" if action == "register" else "unreg"))
            self.wait(lambda s: s["registration"] == ("registered" if action == "register" else "unregistered"),
                      float(params.get("timeout", 20)))
        elif action == "wait":
            after = int(params.get("after", 0))
            state = params.get("state")
            self.wait(lambda s: s["seq"] > after and (state is None or s["call"] == state or
                      (state == "RINGING" and s["direction"] == "incoming" and s["call"] in ("INCOMING", "EARLY"))),
                      float(params.get("timeout", 20)))
        elif action == "play":
            # Audio ports are returned by `audio list`; callers select the observed IDs.
            source, target = int(params["source"]), int(params["target"])
            if not {source, target}.issubset({port["id"] for port in self.audio_ports}):
                raise TestError("select observed audio-list port IDs first")
            self.send(f"audio conf_connect {source} {target}")
        elif action == "audio-list":
            after = self.sequence
            self.send("audio list")
            self.send("acc show")  # Ordered response marker, without retaining account details.
            self.wait(lambda s: any(e["kind"] == "audio-ports" and e["seq"] > after for e in s["events"]), 10)
        elif action != "status":
            raise TestError("unsupported action")
        return self.snapshot()

    def close(self):
        if self.closed:
            return
        errors = []
        if self.process:
            try:
                self.send("call hangup_all")
                self.send("acc unreg")
                self.send("shutdown")
                self.process.wait(timeout=10)
            except (TestError, subprocess.TimeoutExpired):
                pass
            try:
                result = subprocess.run([self.runtime, "rm", "-f", self.name],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
                if result.returncode:
                    exists = subprocess.run([self.runtime, "container", "exists", self.name],
                                            capture_output=True, timeout=10)
                    if exists.returncode != 1:
                        errors.append("container cleanup unverified")
            except (OSError, subprocess.TimeoutExpired):
                errors.append("container cleanup unavailable")
            try:
                if self.process.poll() is None:
                    self.process.kill()
                    self.process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                errors.append("client process cleanup failed")
        (self.directory / "pjsua.conf").unlink(missing_ok=True)
        try:
            self.directory.rmdir()
        except OSError:
            errors.append("endpoint directory cleanup failed")
        if errors:
            raise TestError("; ".join(errors))
        self.closed = True


def rpc(connection, action, **params):
    timeout = min(300, max(20, float(params.get("timeout", 20)))) + 5
    with socket.create_connection(("127.0.0.1", int(connection["control_port"])), timeout=timeout) as sock:
        sock.sendall((json.dumps(dict(token=connection["token"], action=action, **params)) + "\n").encode())
        data = sock.makefile("rb").readline(1024 * 1024)
    result = json.loads(data)
    if "error" in result:
        raise TestError(result["error"])
    return result


def serve(config_path, state_path, port):
    config = protected_json(config_path)
    token = secrets.token_urlsafe(32)
    workdir = tempfile.mkdtemp(prefix="nvtest-endpoint-")
    endpoint = Endpoint(config, workdir, "endpoint")

    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            self.request.settimeout(30)
            try:
                request = json.loads(self.rfile.readline(65536))
                if not secrets.compare_digest(str(request.pop("token", "")), token):
                    raise TestError("unauthorized control request")
                action = request.pop("action")
                if action == "stop":
                    result = {"stopping": True}
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                else:
                    result = endpoint.action(action, **request)
            except (TestError, ValueError, KeyError):
                result = {"error": "endpoint operation failed"}
            self.wfile.write((json.dumps(result) + "\n").encode())

    server = None
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    try:
        server = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
        server.daemon_threads = True
        endpoint.start()
        write_private(state_path, dict(token=token, control_port=port, pid=os.getpid(),
                                      container=endpoint.name, workdir=workdir,
                                      target_host=socket.getfqdn(), module=os.environ.get("MODULE_ID")))
        server.serve_forever(poll_interval=0.2)
    finally:
        if server:
            server.server_close()
        endpoint.close()
        Path(state_path).unlink(missing_ok=True)
        Path(workdir).rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["start", "serve", "status", "call", "ring", "answer",
                        "no-answer", "reject", "hangup", "register", "unregister", "stop", "wait", "behavior", "play", "audio-list"])
    parser.add_argument("--config")
    parser.add_argument("--state", required=True)
    parser.add_argument("--control-port", type=int)
    parser.add_argument("--params", default="{}", help="JSON action parameters; never put credentials here")
    args = parser.parse_args()
    os.umask(0o077)
    try:
        if args.action == "serve":
            serve(args.config, args.state, args.control_port)
            return 0
        if args.action == "start":
            if Path(args.state).exists():
                raise TestError("state already exists; inspect/stop the owned endpoint first")
            if not args.config or not args.control_port:
                raise TestError("start requires --config and --control-port")
            protected_json(args.config)
            child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve", "--config",
                                      str(Path(args.config).resolve()), "--state", str(Path(args.state).resolve()),
                                      "--control-port", str(args.control_port)], start_new_session=True,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deadline = time.monotonic() + 30
            while not Path(args.state).exists():
                if child.poll() is not None:
                    raise TestError("endpoint startup/registration failed")
                if time.monotonic() > deadline:
                    child.terminate()
                    child.wait(timeout=20)
                    raise TestError("endpoint startup timed out")
                time.sleep(0.1)
            print(json.dumps(rpc(protected_json(args.state), "status")))
        else:
            print(json.dumps(rpc(protected_json(args.state), args.action, **json.loads(args.params))))
            if args.action == "stop":
                deadline = time.monotonic() + 30
                while Path(args.state).exists():
                    if time.monotonic() > deadline:
                        raise TestError("stop cleanup timed out; use recovery")
                    time.sleep(0.1)
        return 0
    except (TestError, OSError, ValueError, KeyboardInterrupt):
        print(json.dumps({"error": "SIP operation failed; check protected configuration, state and runtime"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
