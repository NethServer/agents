#!/usr/bin/env python3
"""Run controlled SIP and queue tests locally in an authorized NS8 module context."""
import argparse
import contextlib
import json
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time

from sip_endpoint import Endpoint, TestError, checked, write_private


class AMI:
    """AMI events and correlated actions. Credentials and unrelated events are discarded."""
    def __init__(self, config, extensions, queue):
        self.extensions, self.queue = extensions, queue
        self.events, self.responses, self.linked = [], {}, set()
        self.sequence = 0
        self.condition = threading.Condition()
        self.write_lock = threading.Lock()
        self.closed = False
        self.socket = socket.create_connection((config["host"], int(config["port"])), timeout=10)
        self.socket.settimeout(None)
        self.file = self.socket.makefile("rb")
        threading.Thread(target=self.read, daemon=True).start()
        try:
            self.action("Login", Username=config["username"], Secret=config["secret"], Events="on")
        except BaseException:
            self.close()
            raise

    def relevant(self, frame):
        if frame.get("Queue") == self.queue:
            return True
        for key in ("Channel", "DestChannel", "Interface", "MemberName"):
            if any(re.search(r"(?:PJSIP/|Local/)" + re.escape(ext) + r"(?:[-@/]|$)", frame.get(key, ""))
                   for ext in self.extensions):
                return True
        return any(frame.get(key) in self.linked for key in ("Uniqueid", "Linkedid", "DestUniqueid", "DestLinkedid"))

    def read(self):
        frame = {}
        try:
            while True:
                raw = self.file.readline(65536)
                if not raw:
                    break
                line = raw.decode(errors="replace").strip()
                if not line:
                    with self.condition:
                        if "Response" in frame:
                            self.responses[frame.get("ActionID")] = frame
                        elif "Event" in frame and self.relevant(frame):
                            for key in ("Uniqueid", "Linkedid", "DestUniqueid", "DestLinkedid"):
                                if frame.get(key):
                                    self.linked.add(frame[key])
                            allowed = ("Event", "Queue", "Channel", "DestChannel", "Interface", "MemberName",
                                       "Uniqueid", "Linkedid", "DestUniqueid", "DestLinkedid", "DialStatus", "Reason",
                                       "Status", "Penalty", "Paused", "Ringinuse", "HoldTime", "RingTime")
                            event = {k: v for k, v in frame.items() if k in allowed}
                            self.sequence += 1
                            event["seq"] = self.sequence
                            event["time"] = time.time()
                            self.events.append(event)
                            if len(self.events) > 20000:
                                self.events.pop(0)
                        self.condition.notify_all()
                    frame = {}
                elif ":" in line:
                    key, value = line.split(":", 1)
                    frame[key] = value.strip()
        except (OSError, ValueError):
            pass
        finally:
            with self.condition:
                self.closed = True
                self.condition.notify_all()

    def action(self, name, **values):
        action_id = secrets.token_hex(8)
        values = dict(Action=name, ActionID=action_id, **values)
        if any("\n" in str(v) or "\r" in str(v) for v in values.values()):
            raise TestError("unsafe AMI parameter")
        with self.write_lock:
            self.socket.sendall(("\r\n".join(f"{k}: {v}" for k, v in values.items()) + "\r\n\r\n").encode())
        deadline = time.monotonic() + 10
        with self.condition:
            while action_id not in self.responses and not self.closed:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TestError("AMI action timeout")
                self.condition.wait(remaining)
            response = self.responses.pop(action_id, {})
        if response.get("Response") != "Success":
            raise TestError("AMI action failed: " + name)
        return response

    def cursor(self):
        with self.condition:
            return self.sequence

    def events_since(self, since):
        with self.condition:
            return [event for event in self.events if event["seq"] > since]

    def wait(self, predicate, since=0, timeout=20):
        deadline = time.monotonic() + timeout
        with self.condition:
            while True:
                for event in self.events_since(since):
                    if predicate(event):
                        return event
                remaining = deadline - time.monotonic()
                if remaining <= 0 or self.closed:
                    raise TestError("AMI event timeout")
                self.condition.wait(remaining)

    def close(self):
        with contextlib.suppress(OSError):
            self.socket.shutdown(socket.SHUT_RDWR)
        self.file.close()
        self.socket.close()


class PBX:
    def __init__(self, container="freepbx", adapter=None):
        self.container = container
        self.helper = (Path(adapter) if adapter else Path(__file__).with_name("queue_fixture.php")).read_text().removeprefix("<?php")

    def fixture(self, operation, config):
        output = checked(["podman", "exec", "-i", self.container, "php", "-r", self.helper],
                         input=json.dumps(dict(config, operation=operation)))
        try:
            return json.loads(output)
        except ValueError:
            raise TestError("invalid fixture response (output withheld)") from None

    def cli(self, command):
        return checked(["podman", "exec", self.container, "asterisk", "-rx", command])

    def reload(self):
        try:
            result = subprocess.run(["podman", "exec", self.container, "fwconsole", "reload"],
                                    capture_output=True, timeout=90)
        except subprocess.TimeoutExpired:
            raise TestError("FreePBX reload timed out") from None
        if result.returncode:
            raise TestError("FreePBX reload failed (output withheld)")

    def log_size(self):
        try:
            return ("file", int(checked(["podman", "exec", self.container, "stat", "-c", "%s", "/var/log/asterisk/queue_log"]).strip()))
        except TestError:
            return ("odbc", self.fixture("log-cursor", {})["cursor"])

    def queue_log(self, offset, queue):
        backend, offset = offset
        if backend == "odbc":
            return self.fixture("queue-log", {"queue": queue, "cursor": offset})
        # The whole bounded window stays in memory; retain only this dedicated queue.
        output = checked(["podman", "exec", self.container, "sh", "-c",
                          'tail -c +"$1" /var/log/asterisk/queue_log | head -c 1048577',
                          "sh", str(offset + 1)])
        if len(output) > 1024 * 1024:
            raise TestError("queue_log window exceeded 1 MiB")
        result = []
        for line in output.splitlines():
            fields = line.split("|")
            if len(fields) >= 5 and fields[2] == queue:
                result.append(dict(time=fields[0], callid=fields[1], queue=fields[2], member=fields[3],
                                   event=fields[4], data=fields[5:]))
        return result


def assert_sequence(actual, expected):
    if actual != expected:
        raise TestError("unexpected ring sequence: " + " -> ".join(actual))


def assert_queue_log(logs, callid, first="A", second="B"):
    rows = [row for row in logs if row["callid"] == callid]
    sequence = [(row["event"], row["member"]) for row in rows
                if row["event"] in ("RINGNOANSWER", "CONNECT")]
    if sequence != [("RINGNOANSWER", first), ("CONNECT", second)]:
        raise TestError("queue_log member/outcome sequence mismatch")
    if not any(row["event"].startswith("COMPLETE") and row["member"] == second for row in rows):
        raise TestError("queue_log completion missing for answering member")


class Suite:
    def __init__(self, pbx, config, workdir, report_path, repeats=2):
        self.pbx, self.config, self.workdir, self.report_path = pbx, config, Path(workdir), report_path
        self.config["target_host"] = socket.getfqdn()
        self.config["module"] = os.environ.get("MODULE_ID")
        self.endpoints, self.ami = {}, None
        self.repeats = repeats
        self.report = {"schema": 1, "run_id": config["owner"], "started": time.time(),
                       "target": {"host": socket.getfqdn(), "module": os.environ.get("MODULE_ID")},
                       "configuration": {k: config[k] for k in ("strategy", "ring_timeout", "retry", "ringinuse", "autopause", "lazy", "penalties")},
                       "scenarios": []}
        self.created = False
        self.pending_evidence = {}
        self.planned = {"setup": "three real SIP registrations"}
        for repetition in range(1, repeats + 1):
            for origin, target in (("caller", "A"), ("A", "caller"), ("caller", "B"), ("B", "caller")):
                self.planned[f"direct-{origin}-{target}-{repetition}"] = "ring, manual answer, bridge and hangup"
            for name, expected in (("no-answer", "real ringing followed by PBX NOANSWER"),
                                   ("busy", "callee rejects 486 and Asterisk reports BUSY"),
                                   ("queue-controls", "add, pause, penalty, unpause, remove members"),
                                   ("queue-sequence", "A -> no answer -> B -> answer"),
                                   ("queue-live-behavior", "change B to answer while A rings; A -> B")):
                self.planned[f"{name}-{repetition}"] = expected
        self.planned["lazy-members"] = "paired Lazy Members on/off comparison"

    def record(self, name, status, expected, actual, evidence=None):
        item = dict(name=name, status=status, expected=expected, actual=actual, evidence=evidence or {})
        self.report["scenarios"].append(item)
        write_private(self.report_path, self.report)
        print(f"{status} {name}: {actual}", flush=True)

    def scenario(self, name, expected, action):
        starts = {key: ep.sequence for key, ep in self.endpoints.items()}
        ami_start = self.ami.cursor() if self.ami else 0
        started = time.time()
        evidence = {}
        self.pending_evidence = {}
        try:
            evidence = action() or {}
            status, actual = "PASS", expected
        except Exception as error:
            status, actual = "FAIL", str(error) if isinstance(error, TestError) else "scenario operation failed"
        finally:
            evidence.update(self.pending_evidence)
            evidence["started"] = started
            evidence["ended"] = time.time()
            evidence["sip"] = {key: [e for e in ep.snapshot()["events"] if e["seq"] > starts[key]]
                               for key, ep in self.endpoints.items()}
            evidence["ami"] = self.ami.events_since(ami_start) if self.ami else []
            cleanup_errors = self.clear_calls()
            if cleanup_errors:
                status, actual = "FAIL", "scenario call cleanup failed"
                evidence["cleanup_errors"] = cleanup_errors
        self.record(name, status, expected, actual, evidence)
        if cleanup_errors:
            raise TestError("cannot continue with uncleared calls")

    def clear_calls(self):
        errors = []
        for label, ep in self.endpoints.items():
            try:
                if ep.state["alive"] and ep.state["call"] not in ("IDLE", "DISCONNECTED"):
                    ep.action("hangup")
                    ep.wait(lambda s: s["call"] == "DISCONNECTED", 10)
                ep.behavior = "ignore"
            except (TestError, OSError):
                errors.append(label)
        return errors

    def direct(self, caller, callee, mode):
        a, b = self.endpoints[caller], self.endpoints[callee]
        before = b.state["incoming"]
        start = self.ami.cursor()
        b.behavior = "ignore"
        a.action("call", destination=b.config["username"])
        b.wait(lambda s: s["incoming"] > before and s["call"] in ("INCOMING", "EARLY"), 15)
        ringing = self.ami.wait(lambda e: e["Event"] == "DialBegin" and b.config["username"] in e.get("DestChannel", ""), start, 15)
        def same_call(event):
            return event.get("Linkedid") == ringing.get("Linkedid") and event.get("Linkedid") is not None
        if mode == "answer":
            b.action("answer")
            b.wait(lambda s: s["call"] == "CONFIRMED", 10)
            a.wait(lambda s: s["call"] == "CONFIRMED", 10)
            self.ami.wait(lambda e: e["Event"] == "BridgeEnter" and e.get("Uniqueid") == ringing.get("DestUniqueid")
                          and same_call(e), start, 10)
            a.action("hangup")
            b.wait(lambda s: s["call"] == "DISCONNECTED", 10)
        elif mode == "reject":
            b.action("reject", code=486)
            b.wait(lambda s: s["call"] == "DISCONNECTED" and s["code"] == 486, 10)
            self.ami.wait(lambda e: e["Event"] == "DialEnd" and e.get("DialStatus") == "BUSY" and same_call(e)
                          and e.get("DestUniqueid") == ringing.get("DestUniqueid"), start, 10)
        elif mode == "no-answer":
            b.wait(lambda s: s["call"] == "DISCONNECTED", 15)
            self.ami.wait(lambda e: e["Event"] == "DialEnd" and e.get("DialStatus") == "NOANSWER" and same_call(e)
                          and e.get("DestUniqueid") == ringing.get("DestUniqueid"), start, 10)
            if any(e["kind"] == "call" and e.get("state") == "CONFIRMED" for e in b.events if e["time"] >= ringing["time"]):
                raise TestError("no-answer endpoint unexpectedly answered")
        return {"dial_uniqueid": ringing.get("Uniqueid"), "linkedid": ringing.get("Linkedid")}

    def add_members(self):
        queue = self.config["queue"]
        # Remove/re-add only our own dynamic members, making linear order explicit.
        for label in ("A", "B"):
            interface = "PJSIP/" + self.endpoints[label].config["username"]
            with contextlib.suppress(TestError):
                self.ami.action("QueueRemove", Queue=queue, Interface=interface)
        for label, penalty in zip(("A", "B"), self.config["penalties"]):
            interface = "PJSIP/" + self.endpoints[label].config["username"]
            self.ami.action("QueueAdd", Queue=queue, Interface=interface, MemberName=label,
                            StateInterface=interface, Penalty=penalty, Paused="false",
                            RingInUse="true" if self.config["ringinuse"] else "false")

    def queue_call(self, change_behavior=False):
        self.add_members()
        start = self.ami.cursor()
        offset = self.pbx.log_size()
        initial = {k: ep.sequence for k, ep in self.endpoints.items()}
        caller, first, second = (self.endpoints[k] for k in ("caller", "A", "B"))
        first.behavior = second.behavior = "ignore"
        caller.action("call", destination=self.config["queue"])
        enter = self.ami.wait(lambda e: e["Event"] == "QueueCallerJoin", start, 15)
        callid = enter["Uniqueid"]
        self.pending_evidence = {"uniqueid": callid, "linkedid": enter.get("Linkedid")}
        first.wait(lambda s: any(e["kind"] == "invite" and e["seq"] > initial["A"] for e in s["events"]), 15)
        if change_behavior:
            # Change B only after A is already ringing, within the same queue call.
            second.action("behavior", behavior="answer")
            self.pending_evidence["behavior_change"] = {"endpoint": "B", "behavior": "answer", "time": time.time()}
        first.wait(lambda s: s["call"] == "DISCONNECTED", self.config["ring_timeout"] + 12)
        self.ami.wait(lambda e: e["Event"] == "AgentRingNoAnswer" and e.get("Uniqueid") == callid
                      and e.get("Interface") == "PJSIP/" + first.config["username"], start, 10)
        # Catch A ringing again immediately rather than silently waiting for B.
        deadline = time.monotonic() + self.config["ring_timeout"] + self.config["retry"] + 15
        while True:
            invites = sorted((e for key in ("A", "B") for e in self.endpoints[key].snapshot()["events"]
                              if e["kind"] == "invite" and e["seq"] > initial[key]), key=lambda e: e["time"])
            actual = [e["endpoint"] for e in invites]
            self.pending_evidence["ring_sequence"] = actual
            if len(actual) >= 2:
                assert_sequence(actual, ["A", "B"])
                break
            if time.monotonic() >= deadline:
                raise TestError("queue second member timeout; sequence=" + " -> ".join(actual))
            with second.condition:
                second.condition.wait(min(0.2, max(0, deadline - time.monotonic())))
        if not change_behavior:
            second.action("answer")
        second.wait(lambda s: s["call"] == "CONFIRMED", 10)
        connect = self.ami.wait(lambda e: e["Event"] == "AgentConnect" and e.get("Uniqueid") == callid, start, 10)
        if connect.get("Interface") != "PJSIP/" + second.config["username"]:
            raise TestError("wrong queue member connected")
        caller.action("hangup")
        second.wait(lambda s: s["call"] == "DISCONNECTED", 10)
        # queue_log may be written after the AMI event; bounded polling of file events.
        deadline = time.monotonic() + 10
        while True:
            logs = [e for e in self.pbx.queue_log(offset, self.config["queue"]) if e["callid"] == callid]
            self.pending_evidence["queue_log"] = logs
            events = [e["event"] for e in logs]
            if "RINGNOANSWER" in events and "CONNECT" in events and any(e.startswith("COMPLETE") for e in events):
                break
            if time.monotonic() > deadline:
                raise TestError("missing correlated queue_log RINGNOANSWER/CONNECT/COMPLETE")
            with self.ami.condition:
                self.ami.condition.wait(0.2)
        assert_queue_log(logs, callid)
        return {"ring_sequence": actual, "uniqueid": callid, "linkedid": enter.get("Linkedid"),
                "queue_log": logs, "queue_status": self.pbx.cli("queue show " + self.config["queue"])}

    def member_controls(self):
        self.add_members()
        interface = "PJSIP/" + self.endpoints["A"].config["username"]
        queue = self.config["queue"]
        for action, params in [("QueuePause", {"Paused": "true"}), ("QueuePenalty", {"Penalty": "1"}),
                               ("QueuePause", {"Paused": "false"}), ("QueueRemove", {})]:
            start = self.ami.cursor()
            self.ami.action(action, Queue=queue, Interface=interface, **params)
            expected_event = {"QueuePause": "QueueMemberPause", "QueuePenalty": "QueueMemberPenalty",
                              "QueueRemove": "QueueMemberRemoved"}[action]
            event = self.ami.wait(lambda e: e["Event"] == expected_event and e.get("Interface") == interface, start, 10)
            if action == "QueuePause" and event.get("Paused") != ("1" if params["Paused"] == "true" else "0"):
                raise TestError("member pause state mismatch")
            if action == "QueuePenalty" and event.get("Penalty") != "1":
                raise TestError("member penalty mismatch")
        self.add_members()
        return {"queue_status": self.pbx.cli("queue show " + queue)}

    def run(self):
        try:
            inspect = self.pbx.fixture("inspect", self.config)
            self.report["inventory"] = inspect
            if inspect["occupied"]:
                raise TestError("fixture numbers already occupied; select unused numbers")
            if self.config["lazy"] and not inspect["lazy_configurable"]:
                self.record("lazy-members", "SKIP", "configured Lazy Members queue", "installed API has no Lazy Members setter")
                raise TestError("requested fixture feature unsupported")
            self.report["asterisk"] = self.pbx.cli("core show version").strip()
            self.report["calls_before"] = self.pbx.cli("core show calls").strip()
            self.created = True  # Cleanup also handles a partially completed create.
            write_private(self.workdir / "fixture.json", self.config)
            fixture = self.pbx.fixture("create", self.config)
            self.pbx.reload()
            self.report["fixture"] = {k: v for k, v in fixture.items() if k != "accounts"}
            creds = self.pbx.fixture("ami", {})
            self.ami = AMI(creds, self.config["extensions"], self.config["queue"])
            del creds
            for index, (label, account) in enumerate(zip(("caller", "A", "B"), fixture.pop("accounts"))):
                endpoint_config = dict(account, domain=self.config["domain"], registrar="sip:" + self.config["domain"],
                                       proxy=self.config["client_proxy"], sip_port=self.config["sip_base"] + index,
                                       rtp_port=self.config["rtp_base"] + index * 10,
                                       allowed_destinations=self.config["extensions"] + [self.config["queue"]])
                endpoint = Endpoint(endpoint_config, self.workdir, label)
                self.endpoints[label] = endpoint
                self.config.setdefault("clients", {})[label] = endpoint.name
                write_private(self.workdir / "fixture.json", self.config)
                endpoint.start()
            self.record("setup", "PASS", "three real SIP registrations", "three real SIP registrations")
            for repetition in range(1, self.repeats + 1):
                for origin, target in (("caller", "A"), ("A", "caller"), ("caller", "B"), ("B", "caller")):
                    self.scenario(f"direct-{origin}-{target}-{repetition}", "ring, manual answer, bridge and hangup",
                                  lambda a=origin, b=target: self.direct(a, b, "answer"))
                self.scenario(f"no-answer-{repetition}", "real ringing followed by PBX NOANSWER",
                              lambda: self.direct("caller", "A", "no-answer"))
                self.scenario(f"busy-{repetition}", "callee rejects 486 and Asterisk reports BUSY",
                              lambda: self.direct("caller", "B", "reject"))
                self.scenario(f"queue-controls-{repetition}", "add, pause, penalty, unpause, remove members", self.member_controls)
                self.scenario(f"queue-sequence-{repetition}", "A -> no answer -> B -> answer", self.queue_call)
                self.scenario(f"queue-live-behavior-{repetition}", "change B to answer while A rings; A -> B",
                              lambda: self.queue_call(change_behavior=True))
            if not inspect["lazy_configurable"]:
                self.record("lazy-members", "SKIP", "paired Lazy Members on/off comparison",
                            "installed FreePBX API has no Lazy Members setter; strategy baseline only")
        except (Exception, KeyboardInterrupt) as error:
            self.record("setup-or-run", "FAIL", "suite completes", str(error) if isinstance(error, TestError) else "operation failed or interrupted")
            ran = {item["name"] for item in self.report["scenarios"]}
            for name, expected in self.planned.items():
                if name not in ran:
                    self.record(name, "SKIP", expected, "prerequisite setup/run failed")
        finally:
            try:
                self.cleanup()
            except Exception:
                self.record("cleanup", "FAIL", "complete cleanup", "unexpected cleanup failure; use saved manifest")
            self.report["ended"] = time.time()
            self.report["status"] = "FAIL" if any(s["status"] == "FAIL" for s in self.report["scenarios"]) else "PASS"
            write_private(self.report_path, self.report)
        return 1 if self.report["status"] == "FAIL" else 0

    def cleanup(self):
        errors = self.clear_calls()
        for label, endpoint in self.endpoints.items():
            try:
                if endpoint.state["alive"]:
                    endpoint.action("unregister")
                    aor = self.pbx.cli("pjsip show aor " + endpoint.config["username"])
                    if re.search(r"(?m)^\s*Contact:\s+(?!<)\S", aor):
                        errors.append("stale-registration-" + label)
            except (TestError, OSError, subprocess.TimeoutExpired):
                errors.append("endpoint-" + label)
            finally:
                try:
                    endpoint.close()
                except (TestError, OSError, subprocess.TimeoutExpired):
                    errors.append("endpoint-close-" + label)
        if self.ami:
            for label in ("A", "B"):
                if label in self.endpoints:
                    with contextlib.suppress(TestError, OSError):
                        self.ami.action("QueueRemove", Queue=self.config["queue"],
                                        Interface="PJSIP/" + self.endpoints[label].config["username"])
            self.ami.close()
        if self.created:
            try:
                self.pbx.fixture("delete", self.config)
                self.pbx.reload()
                result = self.pbx.fixture("inspect", self.config)
                if result["occupied"]:
                    errors.append("fixture-removal")
            except (TestError, OSError, ValueError):
                errors.append("fixture-removal")
        try:
            channels = self.pbx.cli("core show channels concise")
            if any(re.search(r"(?:PJSIP/|Local/)" + re.escape(ext) + r"[-@/]", channels) for ext in self.config["extensions"]):
                errors.append("orphan-test-channels")
        except TestError:
            errors.append("channel-check")
        self.record("cleanup", "FAIL" if errors else "PASS", "no owned clients, calls or fixture configuration",
                    ", ".join(errors) if errors else "no owned clients, calls or fixture configuration")
        if not errors:
            (self.workdir / "fixture.json").unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authorized-test", action="store_true", required=True)
    parser.add_argument("--expected-host", required=True)
    parser.add_argument("--module", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--proxy", required=True, help="observed proxy SIP URI with ;lr")
    parser.add_argument("--endpoint-proxy", help="observed Asterisk endpoint outbound_proxy (defaults to --proxy)")
    parser.add_argument("--extensions", nargs=3, default=["899901", "899902", "899903"])
    parser.add_argument("--queue", default="899910")
    parser.add_argument("--strategy", default="linear")
    parser.add_argument("--ring-timeout", type=int, default=4)
    parser.add_argument("--retry", type=int, default=1)
    parser.add_argument("--ringinuse", action="store_true")
    parser.add_argument("--autopause", choices=["no", "yes", "all"], default="no")
    parser.add_argument("--lazy", action="store_true")
    parser.add_argument("--penalties", nargs=2, type=int, default=[0, 0])
    parser.add_argument("--sip-base", type=int, default=15101)
    parser.add_argument("--rtp-base", type=int, default=31000)
    parser.add_argument("--repeat", type=int, default=2)
    parser.add_argument("--report", required=True)
    parser.add_argument("--workdir", required=True, help="new, private fixture workspace; retained on cleanup failure")
    parser.add_argument("--fixture-adapter", help="reviewed PHP adapter for a different installed FreePBX API")
    args = parser.parse_args()
    os.umask(0o077)
    if args.expected_host != socket.getfqdn() or args.module != os.environ.get("MODULE_ID"):
        parser.error("host/module identity mismatch; use runagent on the authorized node")
    if args.repeat < 1 or args.repeat > 20:
        parser.error("repeat must be 1..20")
    config = dict(owner="nvtest-" + secrets.token_hex(6), extensions=args.extensions, queue=args.queue,
                  domain=args.domain, client_proxy=args.proxy,
                  endpoint_proxy=args.endpoint_proxy if args.endpoint_proxy is not None else args.proxy,
                  strategy=args.strategy, ring_timeout=args.ring_timeout, retry=args.retry,
                  ringinuse=args.ringinuse, autopause=args.autopause, lazy=args.lazy, penalties=args.penalties,
                  maxwait=60, sip_base=args.sip_base, rtp_base=args.rtp_base)
    Path(args.workdir).mkdir(mode=0o700, parents=True, exist_ok=False)
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupt)
    return Suite(PBX(adapter=args.fixture_adapter), config, args.workdir, args.report, args.repeat).run()


if __name__ == "__main__":
    sys.exit(main())
