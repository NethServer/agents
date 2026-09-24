#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Passive, allowlist-only diagnostics for local NS8 NethVoice modules."""

import argparse
import datetime as dt
import ipaddress
import json
import re
import subprocess
import sys
from collections import Counter


SCHEMA_VERSION = "1.1.0"
COLLECTOR_VERSION = "0.1.1"
DEFAULT_TIMEOUT = 8.0
MAX_TIMEOUT = 30.0
MAX_OUTPUT_CHARS = 1_000_000
RESTART_WARNING_THRESHOLD = 5

MODULE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
HOST_RE = re.compile(r"^(?=.{1,253}$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.?$")
VERSION_RE = re.compile(r"^[0-9A-Za-z][0-9A-Za-z._+~-]{0,63}$")
IMAGE_RE = re.compile(r"^[a-z0-9.-]+(?::[0-9]+)?(?:/[a-zA-Z0-9._-]+)+(?:[:@][a-zA-Z0-9._:+-]+)?$")
INTERFACE_RE = re.compile(r"^[a-zA-Z0-9_.:@-]{1,32}$")
TIMEZONE_RE = re.compile(r"^[a-zA-Z0-9_+./-]{1,64}$")
PREFIX_RE = re.compile(r"^(?:\+|00)[0-9]{1,4}$")
PORT_RE = re.compile(r"^([0-9]{1,5})(?:-([0-9]{1,5}))?$")

NV_CONFIG_COUNT_GROUPS = {
    "users": ("nethvoice_users_count",),
    "telephony": (
        "nethvoice_trunks_count",
        "nethvoice_inbound_routes_count",
        "nethvoice_outbound_routes_count",
        "nethvoice_ivr_count",
        "nethvoice_queues_count",
        "nethvoice_ringgroups_count",
        "nethvoice_cqr_count",
    ),
    "cti": (
        "nethvoice_cti_profiles_count",
        "nethvoice_cti_groups_count",
        "nethvoice_cti_users_count",
        "nethvoice_streaming_count",
        "nethvoice_paramurl_count",
        "nethvoice_announcements_count",
        "nethvoice_offhour_count",
    ),
    "devices": ("nethvoice_devices_count",),
}
PORT_NAME_MAP = {
    "Asterisk SIP": "asterisk_sip",
    "Asterisk SIPS (TLS)": "asterisk_sips",
    "Asterisk IAX": "asterisk_iax",
    "Asterisk WSS (WebRTC)": "asterisk_wss",
    "Asterisk recordings SFTP": "recordings_sftp",
    "Asterisk RTP (WSS)": "asterisk_rtp",
    "NethCTI TLS (Nethifier)": "nethcti_tls",
    "Phonebook LDAPS": "phonebook_ldaps",
    "Janus WebRTC RTP": "janus_rtp",
}

NV_COMPONENTS = {
    "freepbx",
    "get-certificate",
    "janus",
    "mariadb",
    "nethcti-middleware",
    "nethcti-server",
    "nethcti-ui",
    "nethvoice-cdr-cleanup",
    "nethvoice-hotel-alarms",
    "phonebook",
    "phonebook-update",
    "reports-api",
    "reports-redis",
    "reports-scheduler",
    "reports-ui",
    "satellite",
    "satellite-mqtt",
    "satellite-pgsql",
    "satellite-recordings-cleanup",
    "sftp",
    "tancredi",
    "watcher",
}
PROXY_COMPONENTS = {"kamailio", "postgres", "redis", "rtpengine"}

NV_REQUIRED = {
    "freepbx",
    "janus",
    "mariadb",
    "nethcti-ui",
    "phonebook",
    "reports-api",
    "reports-ui",
    "tancredi",
}
NV_WIZARD_CONDITIONAL = {"nethcti-server", "nethcti-middleware"}
NV_SATELLITE_RUNTIME = {"satellite", "satellite-mqtt"}
NV_SATELLITE_DATABASE = {"satellite-pgsql"}
NV_TIMER_DRIVEN_SERVICES = {"satellite-recordings-cleanup"}
NV_TIMER_COMPONENTS = {
    "nethvoice-cdr-cleanup",
    "phonebook-update",
    "reports-scheduler",
    "satellite-recordings-cleanup",
}
NV_ON_DEMAND = {
    "get-certificate",
    "nethvoice-cdr-cleanup",
    "nethvoice-hotel-alarms",
    "phonebook-update",
    "reports-redis",
    "reports-scheduler",
    "sftp",
    "watcher",
}


class CliError(Exception):
    """Raised for a deliberately sanitized CLI error."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, _message):
        raise CliError("invalid_arguments")


class CommandRunner:
    """Run fixed argument vectors without a shell."""

    def run(self, argv, timeout):
        return subprocess.run(
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso_utc(value):
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_timeout(value):
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("invalid timeout")
    if not parsed > 0:
        raise argparse.ArgumentTypeError("invalid timeout")
    return min(parsed, MAX_TIMEOUT)


def parse_args(argv):
    parser = JsonArgumentParser(add_help=False)
    parser.add_argument("--nethvoice", action="append", default=[])
    parser.add_argument("--proxy", action="append", default=[])
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--command-timeout", type=parse_timeout, default=DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)
    for module_id in args.nethvoice + args.proxy:
        if not MODULE_ID_RE.fullmatch(module_id):
            raise CliError("invalid_module_id")
    args.nethvoice = list(dict.fromkeys(args.nethvoice))
    args.proxy = list(dict.fromkeys(args.proxy))
    return args


def base_report(now, timeout):
    return {
        "schema_version": SCHEMA_VERSION,
        "collector_version": COLLECTOR_VERSION,
        "collected_at": iso_utc(now),
        "command_timeout_seconds": timeout,
        "status": "initializing",
        "node": {},
        "candidates": {"nethvoice": [], "proxy": []},
        "selected": {"nethvoice": [], "proxy": []},
        "modules": {"nethvoice": [], "proxy": []},
        "proxy_topology": [],
        "findings": [],
        "errors": [],
    }


def emit(report, pretty, stdout):
    kwargs = {"sort_keys": True}
    if pretty:
        kwargs["indent"] = 2
    else:
        kwargs["separators"] = (",", ":")
    stdout.write(json.dumps(report, **kwargs))
    stdout.write("\n")


def safe_hostname(value):
    if not isinstance(value, str) or not HOST_RE.fullmatch(value):
        return None
    return value.rstrip(".").lower()


def safe_version(value):
    if isinstance(value, (int, float)):
        value = str(value)
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        return None
    return value


def safe_image(value):
    if not isinstance(value, str) or not IMAGE_RE.fullmatch(value):
        return None
    return value


def safe_ip(value):
    if not isinstance(value, str):
        return None
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return None


def safe_network(value):
    if not isinstance(value, str):
        return None
    try:
        return str(ipaddress.ip_network(value, strict=False))
    except ValueError:
        return None


def safe_nonnegative_int(value):
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    if parsed < 0 or parsed > 10**12:
        return None
    return parsed


def safe_port(value):
    if not isinstance(value, str):
        value = str(value)
    match = PORT_RE.fullmatch(value)
    if not match:
        return None
    first = int(match.group(1))
    last = int(match.group(2) or first)
    if first < 1 or last > 65535 or first > last:
        return None
    return str(first) if first == last else f"{first}-{last}"


def safe_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


class Collector:
    def __init__(self, report, runner, timeout):
        self.report = report
        self.runner = runner
        self.timeout = timeout

    def add_error(self, stage, code, module_id=None):
        item = {"stage": stage, "code": code}
        if module_id and MODULE_ID_RE.fullmatch(module_id):
            item["module_id"] = module_id
        self.report["errors"].append(item)

    def add_finding(self, severity, code, module_id=None, component=None, details=None):
        item = {"severity": severity, "code": code}
        if module_id and MODULE_ID_RE.fullmatch(module_id):
            item["module_id"] = module_id
        if component in NV_COMPONENTS or component in PROXY_COMPONENTS:
            item["component"] = component
        if details:
            item["details"] = details
        self.report["findings"].append(item)

    def command(self, argv, stage, module_id=None, allow_missing=False):
        try:
            result = self.runner.run(list(argv), self.timeout)
        except subprocess.TimeoutExpired:
            self.add_error(stage, "timeout", module_id)
            return None
        except FileNotFoundError:
            self.add_error(stage, "command_unavailable", module_id)
            return None
        except OSError:
            self.add_error(stage, "execution_failed", module_id)
            return None
        stdout = result.stdout or ""
        if len(stdout) > MAX_OUTPUT_CHARS:
            self.add_error(stage, "output_limit_exceeded", module_id)
            return None
        if result.returncode != 0:
            if allow_missing and result.returncode == 1 and not stdout.strip():
                return None
            self.add_error(stage, "command_failed", module_id)
            return None
        return stdout

    def json_command(self, argv, stage, module_id=None, expected_type=None):
        output = self.command(argv, stage, module_id)
        if output is None:
            return None
        try:
            data = json.loads(output)
        except (TypeError, ValueError):
            self.add_error(stage, "invalid_json", module_id)
            return None
        if expected_type is not None and not isinstance(data, expected_type):
            self.add_error(stage, "invalid_shape", module_id)
            return None
        return data

    def preflight(self):
        status = self.json_command(
            ["api-cli", "run", "get-cluster-status"],
            "preflight.cluster_status",
            expected_type=dict,
        )
        inventory = self.json_command(
            ["api-cli", "run", "list-installed-modules"],
            "preflight.module_inventory",
            expected_type=dict,
        )
        if status is None or inventory is None:
            return None

        local_nodes = []
        for node in status.get("nodes", []):
            if not isinstance(node, dict) or node.get("local") is not True:
                continue
            node_id = str(node.get("id", ""))
            if node_id.isdigit():
                local_nodes.append((node_id, node))
        if len(local_nodes) != 1:
            self.add_error("preflight.cluster_status", "local_node_not_unique")
            return None

        local_node_id, local_node = local_nodes[0]
        self.report["node"] = {
            "node_id": local_node_id,
            "role": "leader" if status.get("leader") is True else "worker",
            "online": local_node.get("online") is True,
        }
        vpn = local_node.get("vpn")
        if isinstance(vpn, dict):
            vpn_address = safe_ip(vpn.get("ip_address"))
            if vpn_address:
                self.report["node"]["cluster_vpn_address"] = vpn_address

        candidates = {"nethvoice": [], "proxy": []}
        for source_key, rows in inventory.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                module_name = row.get("module")
                if module_name == "nethvoice":
                    kind = "nethvoice"
                elif module_name == "nethvoice-proxy":
                    kind = "proxy"
                else:
                    continue
                module_id = row.get("id")
                node_id = str(row.get("node", row.get("node_id", "")))
                if not isinstance(module_id, str) or not MODULE_ID_RE.fullmatch(module_id) or not node_id.isdigit():
                    continue
                source = safe_image(row.get("source")) or safe_image(source_key)
                version = safe_version(row.get("version"))
                candidate = {
                    "id": module_id,
                    "node_id": node_id,
                    "local": node_id == local_node_id,
                }
                if source:
                    candidate["source"] = source
                if version:
                    candidate["version"] = version
                candidates[kind].append(candidate)
        for kind in candidates:
            candidates[kind].sort(key=lambda item: (item["node_id"], item["id"]))
        self.report["candidates"] = candidates
        return local_node_id

    def select(self, requested):
        selected = {"nethvoice": [], "proxy": []}
        valid = True
        for kind in ("nethvoice", "proxy"):
            candidates = self.report["candidates"][kind]
            by_id = {item["id"]: item for item in candidates}
            explicit = requested[kind]
            if explicit:
                for module_id in explicit:
                    item = by_id.get(module_id)
                    if item is None:
                        self.add_error(f"selection.{kind}", "unknown_module_id")
                        valid = False
                    elif not item["local"]:
                        self.add_error(f"selection.{kind}", "module_is_remote", module_id)
                        valid = False
                    else:
                        selected[kind].append(item)
            else:
                local = [item for item in candidates if item["local"]]
                if len(local) == 1:
                    selected[kind] = local
                elif not local:
                    self.add_error(f"selection.{kind}", "no_local_candidate")
                    valid = False
                else:
                    self.add_error(f"selection.{kind}", "ambiguous_local_candidates")
                    valid = False
        self.report["selected"] = selected
        return valid

    def collect_node(self):
        hostname = self.command(["hostnamectl", "--static"], "node.hostname")
        if hostname is not None:
            parsed = safe_hostname(hostname.strip())
            if parsed:
                self.report["node"]["hostname"] = parsed
            else:
                self.add_error("node.hostname", "invalid_output")

        os_release = self.command(["cat", "/etc/os-release"], "node.os")
        if os_release is not None:
            values = {}
            for line in os_release.splitlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key in {"ID", "VERSION_ID"}:
                    values[key] = value.strip().strip('"')
            os_id = values.get("ID")
            os_version = values.get("VERSION_ID")
            if os_id and re.fullmatch(r"[a-z0-9._-]{1,32}", os_id):
                self.report["node"].setdefault("os", {})["id"] = os_id
            if os_version and re.fullmatch(r"[0-9A-Za-z._-]{1,32}", os_version):
                self.report["node"].setdefault("os", {})["version_id"] = os_version
            if set(self.report["node"].get("os", {})) != {"id", "version_id"}:
                self.add_error("node.os", "invalid_output")

        addresses = self.json_command(
            ["ip", "-j", "address", "show"],
            "node.local_addresses",
            expected_type=list,
        )
        if addresses is not None:
            result = []
            for interface in addresses:
                if not isinstance(interface, dict):
                    continue
                name = interface.get("ifname")
                if not isinstance(name, str) or not INTERFACE_RE.fullmatch(name):
                    continue
                for address in interface.get("addr_info", []):
                    if not isinstance(address, dict):
                        continue
                    parsed = safe_ip(address.get("local"))
                    prefix = safe_nonnegative_int(address.get("prefixlen"))
                    if not parsed or prefix is None or ipaddress.ip_address(parsed).is_loopback:
                        continue
                    family = "ipv4" if ipaddress.ip_address(parsed).version == 4 else "ipv6"
                    result.append(
                        {"interface": name, "family": family, "address": parsed, "prefix_length": prefix}
                    )
            result.sort(key=lambda item: (item["interface"], item["family"], item["address"]))
            self.report["node"]["local_addresses"] = result
            if not result:
                self.add_error("node.local_addresses", "no_valid_addresses")

    def get_actions(self, module_id):
        actions = self.json_command(
            ["api-cli", "run", f"module/{module_id}/list-actions"],
            "module.actions",
            module_id,
            list,
        )
        if actions is None:
            return set()
        return {item for item in actions if isinstance(item, str) and re.fullmatch(r"[a-z0-9-]{1,64}", item)}

    def action_json(self, module_id, actions, action, stage, expected_type):
        if action not in actions:
            self.add_error(stage, "unsupported_by_installed_version", module_id)
            return None
        return self.json_command(
            ["api-cli", "run", f"module/{module_id}/{action}", "--data", "{}"],
            stage,
            module_id,
            expected_type,
        )

    def env_value(self, module_id, key, stage, validator, required=False):
        output = self.command(
            ["runagent", "-m", module_id, "printenv", key],
            stage,
            module_id,
            allow_missing=not required,
        )
        if output is None:
            return None
        lines = output.splitlines()
        if len(lines) != 1:
            self.add_error(stage, "invalid_output", module_id)
            return None
        value = validator(lines[0].strip())
        if value is None:
            self.add_error(stage, "invalid_output", module_id)
        return value

    def collect_runtime(self, module_id, kind, features):
        components = NV_COMPONENTS if kind == "nethvoice" else PROXY_COMPONENTS
        container_output = self.command(
            [
                "runagent",
                "-m",
                module_id,
                "podman",
                "ps",
                "-a",
                "--format",
                "{{.Names}}|{{.State}}|{{.Status}}|{{.Restarts}}|{{.Image}}",
            ],
            "runtime.containers",
            module_id,
        )
        containers = []
        unknown_containers = 0
        if container_output is not None:
            for line in container_output.splitlines():
                parts = line.split("|", 4)
                if len(parts) != 5:
                    continue
                name, state_raw, status_raw, restarts_raw, image_raw = parts
                if name not in components:
                    unknown_containers += 1
                    continue
                state = state_raw.strip().lower()
                if state not in {"configured", "created", "exited", "paused", "removing", "running", "stopped", "unknown"}:
                    state = "unknown"
                restarts = safe_nonnegative_int(restarts_raw)
                item = {
                    "name": name,
                    "state": state,
                    "health": "unhealthy" if "(unhealthy)" in status_raw.lower() else (
                        "healthy" if "(healthy)" in status_raw.lower() else "not_reported"
                    ),
                    "expectation": self.expectation(kind, name, features),
                }
                if restarts is not None:
                    item["restart_count"] = restarts
                image = safe_image(image_raw.strip())
                if image:
                    item["image"] = image
                containers.append(item)
                self.runtime_findings(module_id, item, is_service=False)
        containers.sort(key=lambda item: item["name"])
        if container_output is not None and not containers:
            self.add_error("runtime.containers", "no_known_components", module_id)

        service_output = self.command(
            [
                "runagent",
                "-m",
                module_id,
                "systemctl",
                "--user",
                "show",
                "--all",
                "--type=service",
                "--property=Id",
                "--property=LoadState",
                "--property=ActiveState",
                "--property=SubState",
                "--property=UnitFileState",
                "--property=NRestarts",
                "--property=Result",
            ],
            "runtime.services",
            module_id,
        )
        services = []
        service_names = set()
        unknown_services = 0
        if service_output is not None:
            for block in re.split(r"\n\s*\n", service_output.strip()):
                values = {}
                for line in block.splitlines():
                    if "=" in line:
                        key, value = line.split("=", 1)
                        values[key] = value
                unit_id = values.get("Id", "")
                name = unit_id[:-8] if unit_id.endswith(".service") else ""
                if name not in components:
                    if unit_id:
                        unknown_services += 1
                    continue
                active = values.get("ActiveState", "unknown").lower()
                sub = values.get("SubState", "unknown").lower()
                load = values.get("LoadState", "unknown").lower()
                if active not in {"active", "inactive", "failed", "activating", "deactivating", "reloading", "unknown"}:
                    active = "unknown"
                if sub not in {"running", "exited", "dead", "failed", "start", "stop", "auto-restart", "unknown"}:
                    sub = "unknown"
                if load not in {"loaded", "not-found", "masked", "error", "unknown"}:
                    load = "unknown"
                item = {
                    "name": name,
                    "load_state": load,
                    "active_state": active,
                    "sub_state": sub,
                    "expectation": self.expectation(kind, name, features),
                }
                restarts = safe_nonnegative_int(values.get("NRestarts"))
                if restarts is not None:
                    item["restart_count"] = restarts
                unit_file = values.get("UnitFileState", "")
                if re.fullmatch(r"[a-z-]{1,24}", unit_file):
                    item["unit_file_state"] = unit_file
                result = values.get("Result", "").lower()
                if re.fullmatch(r"[a-z-]{1,32}", result):
                    item["result"] = result
                services.append(item)
                self.runtime_findings(module_id, item, is_service=True)
        services.sort(key=lambda item: item["name"])
        if service_output is not None and not services:
            self.add_error("runtime.services", "no_known_components", module_id)
        if service_output is not None:
            service_names = {item["name"] for item in services}
            for name in sorted(components - service_names):
                if self.expectation(kind, name, features).startswith("required"):
                    self.add_finding(
                        "error",
                        "required_service_missing",
                        module_id,
                        name,
                    )

        timers = []
        unknown_timers = 0
        if kind == "nethvoice":
            timer_output = self.command(
                [
                    "runagent",
                    "-m",
                    module_id,
                    "systemctl",
                    "--user",
                    "show",
                    "--all",
                    "--type=timer",
                    "--property=Id",
                    "--property=LoadState",
                    "--property=ActiveState",
                    "--property=SubState",
                    "--property=UnitFileState",
                    "--property=Result",
                ],
                "runtime.timers",
                module_id,
            )
            if timer_output is not None:
                for block in re.split(r"\n\s*\n", timer_output.strip()):
                    values = {}
                    for line in block.splitlines():
                        if "=" in line:
                            key, value = line.split("=", 1)
                            values[key] = value
                    unit_id = values.get("Id", "")
                    name = unit_id[:-6] if unit_id.endswith(".timer") else ""
                    if name not in NV_TIMER_COMPONENTS:
                        if unit_id:
                            unknown_timers += 1
                        continue
                    active = values.get("ActiveState", "unknown").lower()
                    sub = values.get("SubState", "unknown").lower()
                    load = values.get("LoadState", "unknown").lower()
                    if active not in {
                        "active",
                        "inactive",
                        "failed",
                        "activating",
                        "deactivating",
                        "reloading",
                        "unknown",
                    }:
                        active = "unknown"
                    if sub not in {"waiting", "elapsed", "dead", "failed", "unknown"}:
                        sub = "unknown"
                    if load not in {"loaded", "not-found", "masked", "error", "unknown"}:
                        load = "unknown"
                    item = {
                        "name": name,
                        "load_state": load,
                        "active_state": active,
                        "sub_state": sub,
                        "expectation": self.timer_expectation(name, features),
                    }
                    unit_file = values.get("UnitFileState", "")
                    if re.fullmatch(r"[a-z-]{1,24}", unit_file):
                        item["unit_file_state"] = unit_file
                    result = values.get("Result", "").lower()
                    if re.fullmatch(r"[a-z-]{1,32}", result):
                        item["result"] = result
                    timers.append(item)
                    self.timer_findings(module_id, item)
                timer_names = {item["name"] for item in timers}
                cleanup_required = self.timer_expectation(
                    "satellite-recordings-cleanup", features
                ).startswith("required")
                if cleanup_required:
                    if "satellite-recordings-cleanup" not in timer_names:
                        self.add_finding(
                            "error",
                            "required_timer_missing",
                            module_id,
                            "satellite-recordings-cleanup",
                        )
                    if (
                        service_output is not None
                        and "satellite-recordings-cleanup" not in service_names
                    ):
                        self.add_finding(
                            "error",
                            "required_timer_service_missing",
                            module_id,
                            "satellite-recordings-cleanup",
                        )
        timers.sort(key=lambda item: item["name"])
        return {
            "containers": containers,
            "other_container_count": unknown_containers,
            "services": services,
            "other_service_count": unknown_services,
            "timers": timers,
            "other_timer_count": unknown_timers,
        }

    def expectation(self, kind, name, features):
        if kind == "proxy":
            return "required"
        if name in NV_REQUIRED:
            return "required"
        if name in NV_WIZARD_CONDITIONAL:
            return "conditional:wizard"
        if name in NV_SATELLITE_RUNTIME:
            flags = [
                features.get("satellite_call_transcription"),
                features.get("satellite_voicemail_transcription"),
            ]
            return "required:enabled-feature" if any(value is True for value in flags) else "conditional:satellite"
        if name in NV_SATELLITE_DATABASE:
            flags = [
                features.get("satellite_call_transcription"),
                features.get("satellite_voicemail_transcription"),
            ]
            return (
                "required:enabled-feature"
                if any(value is True for value in flags)
                else "conditional:retained-state"
            )
        if name in NV_TIMER_DRIVEN_SERVICES:
            return "conditional:timer"
        if name in NV_ON_DEMAND:
            return "conditional:on-demand"
        return "conditional:installed-version"

    def timer_expectation(self, name, features):
        flags = [
            features.get("satellite_call_transcription"),
            features.get("satellite_voicemail_transcription"),
        ]
        if name == "satellite-recordings-cleanup" and any(value is True for value in flags):
            return "required:enabled-feature"
        return "conditional:timer"

    def runtime_findings(self, module_id, item, is_service):
        expectation = item["expectation"]
        name = item["name"]
        restarts = item.get("restart_count")
        if restarts is not None and restarts > RESTART_WARNING_THRESHOLD:
            self.add_finding(
                "warning",
                "service_restart_count_high" if is_service else "container_restart_count_high",
                module_id,
                name,
                {"restart_count": restarts},
            )
        if is_service:
            active = item["active_state"]
            if active == "failed":
                self.add_finding("error", "service_failed", module_id, name)
            elif expectation.startswith("required") and active != "active":
                self.add_finding("error", "required_service_inactive", module_id, name, {"active_state": active})
            if name in NV_TIMER_DRIVEN_SERVICES and item.get("result") not in {None, "success"}:
                self.add_finding(
                    "error",
                    "timer_service_last_result_failed",
                    module_id,
                    name,
                    {"result": item["result"]},
                )
        else:
            state = item["state"]
            if item["health"] == "unhealthy":
                self.add_finding("error", "container_unhealthy", module_id, name)
            if expectation.startswith("required") and state != "running":
                self.add_finding("error", "required_container_not_running", module_id, name, {"state": state})

    def timer_findings(self, module_id, item):
        name = item["name"]
        active = item["active_state"]
        if active == "failed" or item.get("result") not in {None, "success"}:
            self.add_finding("error", "timer_failed", module_id, name)
        elif item["expectation"].startswith("required") and active != "active":
            self.add_finding(
                "error",
                "required_timer_inactive",
                module_id,
                name,
                {"active_state": active},
            )

    def filter_nethvoice_config(self, raw):
        config = {}
        host = safe_hostname(raw.get("nethvoice_host"))
        cti_host = safe_hostname(raw.get("nethcti_ui_host"))
        if host:
            config["nethvoice_host"] = host
        if cti_host:
            config["nethcti_ui_host"] = cti_host
        lets_encrypt = safe_bool(raw.get("lets_encrypt"))
        if lets_encrypt is not None:
            config["lets_encrypt"] = lets_encrypt
        timezone = raw.get("timezone")
        if isinstance(timezone, str) and TIMEZONE_RE.fullmatch(timezone):
            config["timezone"] = timezone
        prefix = raw.get("reports_international_prefix")
        if isinstance(prefix, str) and PREFIX_RE.fullmatch(prefix):
            config["reports_international_prefix"] = prefix
        user_domain = raw.get("user_domain")
        config["user_domain_configured"] = isinstance(user_domain, str) and bool(user_domain)
        return config

    def filter_proxy_config(self, raw):
        config = {}
        fqdn = safe_hostname(raw.get("fqdn"))
        if fqdn:
            config["fqdn"] = fqdn
        lets_encrypt = safe_bool(raw.get("lets_encrypt"))
        if lets_encrypt is not None:
            config["lets_encrypt"] = lets_encrypt
        addresses = raw.get("addresses")
        if isinstance(addresses, dict):
            filtered = {}
            for source_key, output_key in (("address", "address"), ("public_address", "public_address")):
                parsed = safe_ip(addresses.get(source_key))
                if parsed:
                    filtered[output_key] = parsed
            if filtered:
                config["addresses"] = filtered
        service_network = raw.get("service_network")
        if isinstance(service_network, dict):
            address = safe_ip(service_network.get("address"))
            netmask = service_network.get("netmask")
            network = safe_network(f"{address}/{netmask}") if address and isinstance(netmask, str) else None
            if address and network:
                config["service_network"] = {"address": address, "network": network}
        local_networks = raw.get("local_networks")
        if isinstance(local_networks, list):
            filtered_networks = sorted({network for item in local_networks if (network := safe_network(item))})
            config["local_networks"] = filtered_networks
        return config

    def filter_ports(self, raw, module_id):
        result = {}
        invalid = False
        for item in raw:
            if not isinstance(item, dict):
                invalid = True
                continue
            key = PORT_NAME_MAP.get(item.get("name"))
            port = safe_port(item.get("port"))
            protocol = item.get("protocol")
            if key is None or port is None or protocol not in {"tcp", "udp", "udp/tcp"}:
                invalid = True
                continue
            result[key] = {"port": port, "protocol": protocol}
        if invalid:
            self.add_error("nethvoice.dynamic_ports", "invalid_shape", module_id)
        return result

    def filter_counts(self, raw, module_id):
        result = {}
        for group, keys in NV_CONFIG_COUNT_GROUPS.items():
            missing = [key for key in keys if key not in raw]
            if missing:
                self.add_error(
                    f"nethvoice.configuration_counts.{group}",
                    "missing_expected_facts",
                    module_id,
                )
            for key in keys:
                if key not in raw:
                    continue
                value = safe_nonnegative_int(raw.get(key))
                if value is None:
                    self.add_error(
                        f"nethvoice.configuration_counts.{group}",
                        "invalid_output",
                        module_id,
                    )
                else:
                    result[key.removeprefix("nethvoice_").removesuffix("_count")] = value
        return result

    def collect_asterisk(self, module_id, containers):
        freepbx = next((item for item in containers if item["name"] == "freepbx"), None)
        if freepbx is None or freepbx.get("state") != "running":
            self.add_error("asterisk.preflight", "freepbx_container_not_running", module_id)
            return {}

        def cli(command, stage):
            return self.command(
                ["runagent", "-m", module_id, "podman", "exec", "freepbx", "asterisk", "-rx", command],
                stage,
                module_id,
            )

        result = {}
        version_output = cli("core show version", "asterisk.version")
        if version_output is not None:
            match = re.search(r"\bAsterisk\s+([0-9][0-9A-Za-z._+-]{0,31})\b", version_output)
            if match:
                result["version"] = match.group(1)
            else:
                self.add_error("asterisk.version", "invalid_output", module_id)

        uptime_output = cli("core show uptime seconds", "asterisk.uptime")
        if uptime_output is not None:
            uptime = re.search(r"^System uptime:\s*([0-9]+)\s*$", uptime_output, re.MULTILINE)
            reload_age = re.search(r"^Last reload:\s*([0-9]+)\s*$", uptime_output, re.MULTILINE)
            if uptime:
                result["system_uptime_seconds"] = int(uptime.group(1))
            if reload_age:
                result["last_reload_seconds"] = int(reload_age.group(1))
            if not uptime:
                self.add_error("asterisk.uptime", "invalid_output", module_id)

        channels_output = cli("core show channels count", "asterisk.active_calls")
        if channels_output is not None:
            channels = re.search(r"^([0-9]+) active channels?\s*$", channels_output, re.MULTILINE)
            calls = re.search(r"^([0-9]+) active calls?\s*$", channels_output, re.MULTILINE)
            if channels and calls:
                result["active_channels"] = int(channels.group(1))
                result["active_calls"] = int(calls.group(1))
            else:
                self.add_error("asterisk.active_calls", "invalid_output", module_id)

        for command, key, stage in (
            ("pjsip show endpoints", "endpoint_count", "asterisk.endpoint_count"),
            ("pjsip show contacts", "contact_count", "asterisk.contact_count"),
        ):
            output = cli(command, stage)
            if output is None:
                continue
            matches = re.findall(r"^Objects found:\s*([0-9]+)\s*$", output, re.MULTILINE)
            if matches:
                result[key] = int(matches[-1])
            else:
                self.add_error(stage, "invalid_output", module_id)
        return result

    def collect_nethvoice(self, candidate):
        module_id = candidate["id"]
        actions = self.get_actions(module_id)
        record = {
            "id": module_id,
            "placement": {"node_id": candidate["node_id"], "local": True},
            "image": {key: candidate[key] for key in ("source", "version") if key in candidate},
            "configuration": {},
            "features": {},
            "dynamic_ports": {},
            "configuration_counts": {},
            "runtime": {},
            "asterisk": {},
        }
        for field in ("source", "version"):
            if field not in candidate:
                self.add_error("module.image", f"missing_{field}", module_id)

        raw_config = self.action_json(
            module_id, actions, "get-configuration", "nethvoice.configuration", dict
        )
        if raw_config is not None:
            record["configuration"] = self.filter_nethvoice_config(raw_config)
            if "nethvoice_host" not in record["configuration"]:
                self.add_error("nethvoice.configuration", "missing_nethvoice_host", module_id)

        proxy_ip = self.env_value(
            module_id, "PROXY_IP", "nethvoice.proxy_address", safe_ip, required=True
        )
        sip_port = self.env_value(
            module_id, "ASTERISK_SIP_PORT", "nethvoice.asterisk_sip_port", safe_port, required=True
        )
        if proxy_ip:
            record["configuration"]["proxy_address"] = proxy_ip

        feature_specs = (
            ("SATELLITE_CALL_TRANSCRIPTION_ENABLED", "satellite_call_transcription"),
            ("SATELLITE_VOICEMAIL_TRANSCRIPTION_ENABLED", "satellite_voicemail_transcription"),
        )
        for env_key, output_key in feature_specs:
            value = self.env_value(
                module_id,
                env_key,
                f"nethvoice.feature.{output_key}",
                safe_bool,
                required=False,
            )
            if value is not None:
                record["features"][output_key] = value

        raw_ports = self.action_json(
            module_id, actions, "get-ports-list", "nethvoice.dynamic_ports", list
        )
        if raw_ports is not None:
            record["dynamic_ports"] = self.filter_ports(raw_ports, module_id)
            if not record["dynamic_ports"]:
                self.add_error("nethvoice.dynamic_ports", "no_allowlisted_ports", module_id)
        if sip_port:
            action_sip = record["dynamic_ports"].get("asterisk_sip", {}).get("port")
            if action_sip and action_sip != sip_port:
                self.add_finding(
                    "error",
                    "asterisk_sip_port_mismatch",
                    module_id,
                    details={"environment": sip_port, "installed_action": action_sip},
                )

        raw_facts = self.action_json(
            module_id, actions, "get-facts", "nethvoice.configuration_counts", dict
        )
        if raw_facts is not None:
            record["configuration_counts"] = self.filter_counts(raw_facts, module_id)
            if not record["configuration_counts"]:
                self.add_error("nethvoice.configuration_counts", "no_allowlisted_counts", module_id)

        record["runtime"] = self.collect_runtime(module_id, "nethvoice", record["features"])
        record["asterisk"] = self.collect_asterisk(module_id, record["runtime"]["containers"])
        record["_route"] = {
            "domain": record["configuration"].get("nethvoice_host"),
            "host": proxy_ip,
            "port": sip_port,
        }
        return record

    def parse_sip_uri(self, value):
        if not isinstance(value, str):
            return None
        match = re.fullmatch(r"sip:(?:\[([0-9A-Fa-f:]+)\]|([a-zA-Z0-9.-]+)):([0-9]{1,5})", value)
        if not match:
            return None
        host_raw = match.group(1) or match.group(2)
        host = safe_ip(host_raw) or safe_hostname(host_raw)
        port = safe_port(match.group(3))
        if host is None or port is None or "-" in port:
            return None
        rendered_host = f"[{host}]" if ":" in host else host
        return {"host": host, "port": int(port), "uri": f"sip:{rendered_host}:{port}"}

    def filter_routes(self, raw, module_id):
        result = []
        invalid = False
        for item in raw:
            if not isinstance(item, dict):
                invalid = True
                continue
            domain = safe_hostname(item.get("domain"))
            addresses = item.get("address")
            if domain is None or not isinstance(addresses, list):
                invalid = True
                continue
            destinations = []
            for address in addresses:
                parsed = self.parse_sip_uri(address.get("uri")) if isinstance(address, dict) else None
                if parsed is None:
                    invalid = True
                else:
                    destinations.append(parsed)
            result.append({"domain": domain, "destinations": destinations})
        if invalid:
            self.add_error("proxy.routes", "invalid_shape", module_id)
        result.sort(key=lambda item: item["domain"])
        return result, not invalid

    def collect_proxy(self, candidate):
        module_id = candidate["id"]
        actions = self.get_actions(module_id)
        record = {
            "id": module_id,
            "placement": {"node_id": candidate["node_id"], "local": True},
            "image": {key: candidate[key] for key in ("source", "version") if key in candidate},
            "configuration": {},
            "runtime": {},
            "route_count": None,
            "trunk_count": None,
            "_routes": None,
            "_routes_complete": False,
        }
        for field in ("source", "version"):
            if field not in candidate:
                self.add_error("module.image", f"missing_{field}", module_id)
        raw_config = self.action_json(
            module_id, actions, "get-configuration", "proxy.configuration", dict
        )
        if raw_config is not None:
            record["configuration"] = self.filter_proxy_config(raw_config)
            if "fqdn" not in record["configuration"]:
                self.add_error("proxy.configuration", "missing_fqdn", module_id)
        raw_routes = self.action_json(module_id, actions, "list-routes", "proxy.routes", list)
        if raw_routes is not None:
            record["route_count"] = len(raw_routes)
            routes, routes_complete = self.filter_routes(raw_routes, module_id)
            if routes_complete:
                record["_routes"] = routes
                record["_routes_complete"] = True
        raw_trunks = self.action_json(module_id, actions, "list-trunks", "proxy.trunks", list)
        if raw_trunks is not None:
            record["trunk_count"] = len(raw_trunks)
        record["runtime"] = self.collect_runtime(module_id, "proxy", {})
        return record

    def build_topology(self, nethvoice_records, proxy_records):
        local_addresses = {
            item["address"] for item in self.report["node"].get("local_addresses", [])
        }
        vpn = self.report["node"].get("cluster_vpn_address")
        if vpn:
            local_addresses.add(vpn)
        selected_all_local = len(nethvoice_records) == len(
            [item for item in self.report["candidates"]["nethvoice"] if item["local"]]
        )

        expected_records = {}
        expected_by_domain = {}
        identities_complete = selected_all_local
        for module in nethvoice_records:
            expected = module.get("_route", {})
            domain = expected.get("domain")
            host = expected.get("host")
            port_text = expected.get("port")
            port = int(port_text) if isinstance(port_text, str) and port_text.isdigit() else None
            complete = bool(domain and host and port is not None)
            identity = {
                "domain": domain,
                "host": host,
                "port": port,
                "complete": complete,
            }
            expected_records[module["id"]] = identity
            if complete:
                expected_by_domain.setdefault(domain, []).append((host, port))
            else:
                identities_complete = False

        for proxy in proxy_records:
            routes_complete = proxy.get("_routes_complete") is True
            routes = proxy.get("_routes") or []
            by_domain = {}
            for route in routes:
                by_domain.setdefault(route["domain"], []).extend(route["destinations"])
            checks = []
            expected_domains = set(expected_by_domain)
            topology_evidence_complete = routes_complete and identities_complete
            for module in nethvoice_records:
                expected = expected_records[module["id"]]
                domain = expected["domain"]
                host = expected["host"]
                port = expected["port"]
                item = {"nethvoice_id": module["id"], "status": "unassessed"}
                if domain:
                    item["domain"] = domain
                if host and port:
                    rendered_host = f"[{host}]" if ":" in host else host
                    item["expected_uri"] = f"sip:{rendered_host}:{port}"
                actual = by_domain.get(domain, []) if routes_complete and domain else []
                item["actual_uris"] = (
                    sorted(entry["uri"] for entry in actual) if routes_complete and domain else None
                )
                if not topology_evidence_complete or not expected["complete"]:
                    item["status"] = "unassessed"
                elif Counter((entry["host"], entry["port"]) for entry in actual) == Counter(
                    expected_by_domain[domain]
                ):
                    item["status"] = "match"
                elif not actual:
                    item["status"] = "missing"
                    self.add_finding("error", "nethvoice_proxy_route_missing", module["id"])
                else:
                    item["status"] = "mismatch"
                    self.add_finding("error", "nethvoice_proxy_route_mismatch", module["id"])
                if host and local_addresses and host not in local_addresses:
                    self.add_finding(
                        "warning",
                        "nethvoice_proxy_address_not_local",
                        module["id"],
                        details={"proxy_address": host},
                    )
                checks.append(item)

            if topology_evidence_complete:
                for domain, expected_destinations in expected_by_domain.items():
                    actual_counter = Counter(
                        (entry["host"], entry["port"]) for entry in by_domain.get(domain, [])
                    )
                    expected_counter = Counter(expected_destinations)
                    unexpected_count = sum(
                        count
                        for destination, count in actual_counter.items()
                        if destination not in expected_counter
                    )
                    duplicate_count = sum(
                        max(count - max(expected_counter.get(destination, 0), 1), 0)
                        for destination, count in actual_counter.items()
                    )
                    if unexpected_count:
                        self.add_finding(
                            "error",
                            "nethvoice_proxy_route_unexpected_destination",
                            proxy["id"],
                            details={"domain": domain, "count": unexpected_count},
                        )
                    if duplicate_count:
                        self.add_finding(
                            "error",
                            "nethvoice_proxy_route_duplicate_destination",
                            proxy["id"],
                            details={"domain": domain, "count": duplicate_count},
                        )

            unmatched = []
            stale_classification_allowed = topology_evidence_complete
            for domain, destinations in sorted(by_domain.items()):
                if domain in expected_domains:
                    continue
                unmatched.append(
                    {
                        "domain": domain,
                        "uris": sorted(item["uri"] for item in destinations),
                        "classification": (
                            "potentially_stale" if stale_classification_allowed else "unassessed"
                        ),
                    }
                )
                if stale_classification_allowed:
                    self.add_finding(
                        "warning",
                        "proxy_route_without_local_nethvoice",
                        proxy["id"],
                    )
            self.report["proxy_topology"].append(
                {
                    "proxy_id": proxy["id"],
                    "route_count": proxy.get("route_count"),
                    "trunk_count": proxy.get("trunk_count"),
                    "route_checks": sorted(checks, key=lambda item: item["nethvoice_id"]),
                    "unmatched_routes": sorted(unmatched, key=lambda item: item["domain"]),
                    "evidence_complete": topology_evidence_complete,
                    "consistent": (
                        all(item["status"] == "match" for item in checks) and not unmatched
                        if topology_evidence_complete
                        else None
                    ),
                }
            )


def run_collection(args, runner, now):
    report = base_report(now, args.command_timeout)
    collector = Collector(report, runner, args.command_timeout)
    local_node = collector.preflight()
    if local_node is None:
        report["status"] = "fatal"
        return report, 3
    requested = {"nethvoice": args.nethvoice, "proxy": args.proxy}
    if not collector.select(requested):
        report["status"] = "selection_required"
        return report, 2

    collector.collect_node()
    nethvoice_records = [collector.collect_nethvoice(item) for item in report["selected"]["nethvoice"]]
    proxy_records = [collector.collect_proxy(item) for item in report["selected"]["proxy"]]
    collector.build_topology(nethvoice_records, proxy_records)

    for record in nethvoice_records:
        record.pop("_route", None)
    for record in proxy_records:
        record.pop("_routes", None)
        record.pop("_routes_complete", None)
    report["modules"] = {"nethvoice": nethvoice_records, "proxy": proxy_records}
    report["status"] = "partial" if report["errors"] else "complete"
    return report, 1 if report["errors"] else 0


def main(argv=None, runner=None, stdout=None, now=None):
    argv = sys.argv[1:] if argv is None else argv
    stdout = sys.stdout if stdout is None else stdout
    now = utc_now() if now is None else now
    try:
        args = parse_args(argv)
    except (CliError, SystemExit):
        report = base_report(now, DEFAULT_TIMEOUT)
        report["status"] = "selection_required"
        report["errors"].append({"stage": "arguments", "code": "invalid_arguments"})
        emit(report, False, stdout)
        return 2
    try:
        report, exit_code = run_collection(args, runner or CommandRunner(), now)
    except Exception:
        report = base_report(now, args.command_timeout)
        report["status"] = "fatal"
        report["errors"].append({"stage": "collector", "code": "internal_error"})
        exit_code = 3
    emit(report, args.pretty, stdout)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
