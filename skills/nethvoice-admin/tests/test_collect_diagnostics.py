import ast
import datetime as dt
import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "collect_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("collect_diagnostics", SCRIPT)
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)

NOW = dt.datetime(2026, 9, 4, 10, 30, tzinfo=dt.timezone.utc)
CANARY = "NV_CANARY_DO_NOT_LEAK_7f82d1"


class FakeRunner:
    def __init__(self, nethvoice=None, proxies=None):
        self.nethvoice = nethvoice or [self.module("nethvoice43", "nethvoice", "1", "1.7.7")]
        self.proxies = proxies or [self.module("nethvoice-proxy1", "nethvoice-proxy", "1", "1.7.0")]
        self.calls = []
        self.failures = {}
        self.malformed = {}
        self.timeouts = set()
        self.stderr_canary = CANARY
        self.routes = None
        self.facts = None
        self.env_overrides = {}
        self.service_overrides = {}
        self.omit_services = set()
        self.timer_overrides = {}
        self.omit_timers = set()

    @staticmethod
    def module(module_id, module, node, version):
        source = f"ghcr.io/nethesis/{module}"
        return {
            "id": module_id,
            "module": module,
            "node": node,
            "source": source,
            "version": version,
            "digest": CANARY,
        }

    @staticmethod
    def complete(argv, stdout="", returncode=0, stderr=""):
        return subprocess.CompletedProcess(argv, returncode, stdout, stderr)

    @staticmethod
    def suffix(module_id):
        match = "".join(character for character in module_id if character.isdigit())
        return match or "1"

    def nethvoice_host(self, module_id):
        return "voice.example.test" if module_id == "nethvoice43" else f"voice{self.suffix(module_id)}.example.test"

    def sip_port(self, module_id):
        return "20025" if module_id == "nethvoice43" else str(20025 + int(self.suffix(module_id)))

    def inventory(self):
        return {
            "ghcr.io/nethesis/nethvoice": self.nethvoice,
            "ghcr.io/nethesis/nethvoice-proxy": self.proxies,
        }

    def default_routes(self):
        routes = []
        for row in self.nethvoice:
            if row["node"] != "1":
                continue
            routes.append(
                {
                    "domain": self.nethvoice_host(row["id"]),
                    "address": [
                        {
                            "uri": f"sip:10.5.4.1:{self.sip_port(row['id'])}",
                            "description": f"{row['id']}-{CANARY}",
                        }
                    ],
                }
            )
        return routes

    @staticmethod
    def default_facts():
        return {
            "nethvoice_users_count": 10,
            "nethvoice_trunks_count": 2,
            "nethvoice_inbound_routes_count": 2,
            "nethvoice_outbound_routes_count": 3,
            "nethvoice_ivr_count": 1,
            "nethvoice_queues_count": 1,
            "nethvoice_ringgroups_count": 1,
            "nethvoice_cqr_count": 0,
            "nethvoice_cti_profiles_count": 2,
            "nethvoice_cti_groups_count": 1,
            "nethvoice_cti_users_count": 8,
            "nethvoice_streaming_count": 0,
            "nethvoice_paramurl_count": 1,
            "nethvoice_announcements_count": 1,
            "nethvoice_offhour_count": 1,
            "nethvoice_devices_count": 10,
            "nethvoice_calls_last_24h": CANARY,
            "nethvoice_total_calls": CANARY,
            "nethvoice_trunks_by_provider": {CANARY: 1},
            "raw_log": CANARY,
        }

    def run(self, argv, timeout):
        argv = tuple(argv)
        self.calls.append((argv, timeout))
        if argv in self.timeouts:
            raise subprocess.TimeoutExpired(argv, timeout, output=CANARY, stderr=CANARY)
        if argv in self.failures:
            return self.complete(argv, self.failures[argv], 1, self.stderr_canary)
        if argv in self.malformed:
            return self.complete(argv, self.malformed[argv], 0, self.stderr_canary)

        if argv == ("api-cli", "run", "get-cluster-status"):
            return self.complete(
                argv,
                json.dumps(
                    {
                        "leader": True,
                        "cluster_uuid": CANARY,
                        "nodes": [
                            {
                                "id": 1,
                                "local": True,
                                "online": True,
                                "hostname": CANARY,
                                "vpn": {"ip_address": "10.5.4.1", "public_key": CANARY},
                            },
                            {"id": 2, "local": False, "online": True},
                        ],
                    }
                ),
            )
        if argv == ("api-cli", "run", "list-installed-modules"):
            return self.complete(argv, json.dumps(self.inventory()))
        if argv == ("hostnamectl", "--static"):
            return self.complete(argv, "node-one\n")
        if argv == ("cat", "/etc/os-release"):
            return self.complete(
                argv,
                f'ID="rocky"\nVERSION_ID="9.8"\nPRETTY_NAME="{CANARY}"\n',
            )
        if argv == ("ip", "-j", "address", "show"):
            return self.complete(
                argv,
                json.dumps(
                    [
                        {
                            "ifname": "wg0",
                            "address": CANARY,
                            "addr_info": [
                                {"family": "inet", "local": "10.5.4.1", "prefixlen": 32},
                            ],
                        },
                        {
                            "ifname": "lo",
                            "addr_info": [
                                {"family": "inet", "local": "127.0.0.1", "prefixlen": 8},
                            ],
                        },
                    ]
                ),
            )

        if len(argv) >= 3 and argv[:2] == ("api-cli", "run") and argv[2].startswith("module/"):
            _, module_id, action = argv[2].split("/", 2)
            is_proxy = any(row["id"] == module_id for row in self.proxies)
            if action == "list-actions":
                actions = (
                    ["list-actions", "get-configuration", "list-routes", "list-trunks"]
                    if is_proxy
                    else ["list-actions", "get-configuration", "get-ports-list", "get-facts"]
                )
                return self.complete(argv, json.dumps(actions))
            if action == "get-configuration" and is_proxy:
                return self.complete(
                    argv,
                    json.dumps(
                        {
                            "fqdn": "proxy.example.test",
                            "lets_encrypt": True,
                            "addresses": {"address": "192.0.2.10", "public_address": "198.51.100.20"},
                            "service_network": {"address": "10.5.4.1", "netmask": "255.255.255.0"},
                            "local_networks": ["192.0.2.0/24"],
                            "password": CANARY,
                        }
                    ),
                )
            if action == "get-configuration":
                return self.complete(
                    argv,
                    json.dumps(
                        {
                            "nethvoice_host": self.nethvoice_host(module_id),
                            "nethcti_ui_host": f"cti{self.suffix(module_id)}.example.test",
                            "lets_encrypt": True,
                            "timezone": "Europe/Rome",
                            "user_domain": "customers.example.test",
                            "reports_international_prefix": "+39",
                            "subscription_systemid": CANARY,
                            "api_key": CANARY,
                        }
                    ),
                )
            if action == "get-ports-list":
                port = self.sip_port(module_id)
                return self.complete(
                    argv,
                    json.dumps(
                        [
                            {"name": "Asterisk SIP", "port": port, "protocol": "udp/tcp"},
                            {"name": "Asterisk SIPS (TLS)", "port": "20026", "protocol": "tcp"},
                            {"name": "Asterisk RTP (WSS)", "port": "20002-21001", "protocol": "udp"},
                            {"name": "Janus WebRTC RTP", "port": "21002-22001", "protocol": "udp"},
                        ]
                    ),
                )
            if action == "get-facts":
                return self.complete(
                    argv,
                    json.dumps(self.facts if self.facts is not None else self.default_facts()),
                )
            if action == "list-routes":
                return self.complete(argv, json.dumps(self.routes if self.routes is not None else self.default_routes()))
            if action == "list-trunks":
                return self.complete(
                    argv,
                    json.dumps([{"rule": CANARY, "destination": {"uri": CANARY}}]),
                )

        if len(argv) >= 5 and argv[:3] == ("runagent", "-m", argv[2]):
            module_id = argv[2]
            is_proxy = any(row["id"] == module_id for row in self.proxies)
            if argv[3] == "printenv":
                values = {
                    "PROXY_IP": "10.5.4.1",
                    "ASTERISK_SIP_PORT": self.sip_port(module_id),
                    "SATELLITE_CALL_TRANSCRIPTION_ENABLED": "false",
                    "SATELLITE_VOICEMAIL_TRANSCRIPTION_ENABLED": "false",
                }
                values.update(self.env_overrides)
                if argv[4] in values:
                    return self.complete(argv, values[argv[4]] + "\n")
                return self.complete(argv, "", 1, CANARY)
            if argv[3:6] == ("podman", "ps", "-a"):
                if is_proxy:
                    output = "\n".join(
                        f"{name}|running|Up 1 day|0|ghcr.io/nethesis/nethvoice-proxy-{name}:1.7.0"
                        for name in ("redis", "postgres", "rtpengine", "kamailio")
                    )
                else:
                    output = "\n".join(
                        f"{name}|running|Up 1 day (healthy)|0|ghcr.io/nethesis/nethvoice-{name}:1.7.7"
                        for name in (
                            "mariadb",
                            "freepbx",
                            "janus",
                            "nethcti-ui",
                            "tancredi",
                            "phonebook",
                            "reports-api",
                            "reports-ui",
                            "satellite-pgsql",
                        )
                    )
                return self.complete(argv, output + "\n")
            if argv[3] == "systemctl":
                if "--type=timer" in argv:
                    names = (
                        "nethvoice-cdr-cleanup",
                        "phonebook-update",
                        "reports-scheduler",
                        "satellite-recordings-cleanup",
                    )
                    blocks = []
                    for name in names:
                        if name in self.omit_timers:
                            continue
                        state = self.timer_overrides.get(name, {})
                        blocks.append(
                            f"Result={state.get('result', 'success')}\nId={name}.timer\n"
                            f"LoadState={state.get('load_state', 'loaded')}\n"
                            f"ActiveState={state.get('active_state', 'active')}\n"
                            f"SubState={state.get('sub_state', 'waiting')}\n"
                            f"UnitFileState={state.get('unit_file_state', 'enabled')}"
                        )
                    return self.complete(argv, "\n\n".join(blocks) + "\n")

                names = ("kamailio", "postgres", "redis", "rtpengine") if is_proxy else (
                    "mariadb",
                    "freepbx",
                    "janus",
                    "nethcti-ui",
                    "tancredi",
                    "phonebook",
                    "reports-api",
                    "reports-ui",
                    "nethcti-server",
                    "nethcti-middleware",
                    "satellite",
                    "satellite-mqtt",
                    "satellite-pgsql",
                    "satellite-recordings-cleanup",
                )
                blocks = []
                for name in names:
                    if name in self.omit_services:
                        continue
                    conditional_inactive = name in {
                        "nethcti-server",
                        "nethcti-middleware",
                        "satellite",
                        "satellite-mqtt",
                        "satellite-recordings-cleanup",
                    }
                    state = self.service_overrides.get(name, {})
                    active = state.get("active_state", "inactive" if conditional_inactive else "active")
                    sub = state.get("sub_state", "dead" if conditional_inactive else "running")
                    blocks.append(
                        f"NRestarts={state.get('restart_count', 0)}\nId={name}.service\n"
                        f"LoadState={state.get('load_state', 'loaded')}\n"
                        f"ActiveState={active}\nSubState={sub}\n"
                        f"UnitFileState={state.get('unit_file_state', 'enabled')}\n"
                        f"Result={state.get('result', 'success')}"
                    )
                return self.complete(argv, "\n\n".join(blocks) + "\n")
            if argv[3:7] == ("podman", "exec", "freepbx", "asterisk"):
                command = argv[-1]
                values = {
                    "core show version": "Asterisk 18.26.3 built by root @ container\n",
                    "core show uptime seconds": "System uptime: 100\nLast reload: 90\n",
                    "core show channels count": "0 active channels\n0 active calls\n4 calls processed\n",
                    "pjsip show endpoints": f" Endpoint: {CANARY}\n\nObjects found: 12\n",
                    "pjsip show contacts": f" Contact: sip:{CANARY}@203.0.113.8\n\nObjects found: 3\n",
                }
                return self.complete(argv, values[command])

        return self.complete(argv, "", 127, CANARY)


class ExplodingRunner:
    def run(self, _argv, _timeout):
        raise RuntimeError(CANARY)


def invoke(runner, argv=None):
    output = io.StringIO()
    exit_code = collector.main(argv or [], runner=runner, stdout=output, now=NOW)
    return exit_code, json.loads(output.getvalue()), output.getvalue()


class CollectorBehaviorTests(unittest.TestCase):
    def test_single_local_instances_are_auto_selected_and_collected(self):
        code, report, serialized = invoke(FakeRunner())

        self.assertEqual(code, 0)
        self.assertEqual(report["status"], "complete")
        self.assertEqual(report["schema_version"], "1.1.0")
        self.assertEqual(report["collector_version"], "0.1.1")
        self.assertEqual(report["selected"]["nethvoice"][0]["id"], "nethvoice43")
        self.assertEqual(report["selected"]["proxy"][0]["id"], "nethvoice-proxy1")
        self.assertEqual(report["modules"]["nethvoice"][0]["asterisk"]["active_calls"], 0)
        self.assertEqual(report["modules"]["nethvoice"][0]["configuration_counts"]["trunks"], 2)
        self.assertTrue(report["proxy_topology"][0]["consistent"])
        self.assertNotIn(CANARY, serialized)

    def test_explicit_repeatable_selection_supports_multiple_instances(self):
        runner = FakeRunner(
            nethvoice=[
                FakeRunner.module("nethvoice43", "nethvoice", "1", "1.7.7"),
                FakeRunner.module("nethvoice44", "nethvoice", "1", "1.7.7"),
            ]
        )
        code, report, _ = invoke(
            runner,
            [
                "--nethvoice",
                "nethvoice43",
                "--nethvoice",
                "nethvoice44",
                "--proxy",
                "nethvoice-proxy1",
            ],
        )

        self.assertEqual(code, 0)
        self.assertEqual(
            [item["id"] for item in report["modules"]["nethvoice"]],
            ["nethvoice43", "nethvoice44"],
        )
        self.assertTrue(report["proxy_topology"][0]["consistent"])

    def test_multiple_local_instances_are_ambiguous_without_ids(self):
        runner = FakeRunner(
            nethvoice=[
                FakeRunner.module("nethvoice43", "nethvoice", "1", "1.7.7"),
                FakeRunner.module("nethvoice44", "nethvoice", "1", "1.7.7"),
            ]
        )
        code, report, _ = invoke(runner)

        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "selection_required")
        self.assertEqual(len(report["candidates"]["nethvoice"]), 2)
        self.assertFalse(any(call[0][0] == "runagent" for call in runner.calls))
        self.assertEqual(report["modules"], {"nethvoice": [], "proxy": []})

    def test_explicit_remote_module_is_rejected_before_tenant_collection(self):
        runner = FakeRunner(
            nethvoice=[FakeRunner.module("nethvoice99", "nethvoice", "2", "1.7.7")]
        )
        code, report, _ = invoke(
            runner, ["--nethvoice", "nethvoice99", "--proxy", "nethvoice-proxy1"]
        )

        self.assertEqual(code, 2)
        self.assertIn(
            {"stage": "selection.nethvoice", "code": "module_is_remote", "module_id": "nethvoice99"},
            report["errors"],
        )
        self.assertFalse(any(call[0][0] == "runagent" for call in runner.calls))

    def test_timeout_is_sanitized_and_yields_partial_report(self):
        runner = FakeRunner()
        runner.timeouts.add(("hostnamectl", "--static"))
        code, report, serialized = invoke(runner)

        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "partial")
        self.assertIn({"stage": "node.hostname", "code": "timeout"}, report["errors"])
        self.assertNotIn(CANARY, serialized)

    def test_timeout_is_capped(self):
        runner = FakeRunner()
        code, report, _ = invoke(runner, ["--command-timeout", "900"])

        self.assertEqual(code, 0)
        self.assertEqual(report["command_timeout_seconds"], 30.0)
        self.assertTrue(all(timeout == 30.0 for _, timeout in runner.calls))

    def test_invalid_timeout_is_rejected_without_running_commands(self):
        for value in ("0", "-1", "nan", "not-a-number"):
            with self.subTest(value=value):
                runner = FakeRunner()
                code, report, _ = invoke(runner, ["--command-timeout", value])
                self.assertEqual(code, 2)
                self.assertEqual(report["status"], "selection_required")
                self.assertEqual(runner.calls, [])

    def test_pretty_output_remains_one_json_document(self):
        runner = FakeRunner()
        output = io.StringIO()
        code = collector.main(["--pretty"], runner=runner, stdout=output, now=NOW)
        serialized = output.getvalue()

        self.assertEqual(code, 0)
        self.assertTrue(serialized.startswith("{\n"))
        self.assertEqual(serialized.count('"schema_version"'), 1)
        self.assertEqual(json.loads(serialized)["status"], "complete")

    def test_malformed_action_output_is_partial_without_raw_output(self):
        runner = FakeRunner()
        key = (
            "api-cli",
            "run",
            "module/nethvoice43/get-configuration",
            "--data",
            "{}",
        )
        runner.malformed[key] = f"not-json-{CANARY}"
        code, report, serialized = invoke(runner)

        self.assertEqual(code, 1)
        self.assertIn(
            {"stage": "nethvoice.configuration", "code": "invalid_json", "module_id": "nethvoice43"},
            report["errors"],
        )
        self.assertNotIn(CANARY, serialized)

    def test_inactive_wizard_and_satellite_services_are_conditional(self):
        code, report, _ = invoke(FakeRunner())
        self.assertEqual(code, 0)
        services = {
            item["name"]: item
            for item in report["modules"]["nethvoice"][0]["runtime"]["services"]
        }
        self.assertEqual(services["nethcti-server"]["expectation"], "conditional:wizard")
        self.assertEqual(services["satellite"]["expectation"], "conditional:satellite")
        self.assertEqual(
            services["satellite-pgsql"]["expectation"], "conditional:retained-state"
        )
        self.assertEqual(
            services["satellite-recordings-cleanup"]["expectation"], "conditional:timer"
        )
        timers = {
            item["name"]: item
            for item in report["modules"]["nethvoice"][0]["runtime"]["timers"]
        }
        self.assertEqual(
            timers["satellite-recordings-cleanup"]["expectation"], "conditional:timer"
        )
        finding_components = {item.get("component") for item in report["findings"]}
        self.assertNotIn("nethcti-server", finding_components)
        self.assertNotIn("satellite", finding_components)
        self.assertNotIn("satellite-pgsql", finding_components)
        self.assertNotIn("satellite-recordings-cleanup", finding_components)

    def test_inactive_and_missing_required_services_are_detected(self):
        runner = FakeRunner()
        runner.service_overrides["janus"] = {
            "active_state": "inactive",
            "sub_state": "dead",
        }
        runner.omit_services.add("phonebook")

        code, report, _ = invoke(runner)

        self.assertEqual(code, 0)
        services = {
            item["name"]: item
            for item in report["modules"]["nethvoice"][0]["runtime"]["services"]
        }
        self.assertEqual(services["janus"]["active_state"], "inactive")
        self.assertNotIn("phonebook", services)
        findings = {(item["code"], item.get("component")) for item in report["findings"]}
        self.assertIn(("required_service_inactive", "janus"), findings)
        self.assertIn(("required_service_missing", "phonebook"), findings)
        service_calls = [
            argv
            for argv, _timeout in runner.calls
            if argv[:4] == ("runagent", "-m", "nethvoice43", "systemctl")
            and "--type=service" in argv
        ]
        self.assertEqual(len(service_calls), 1)
        self.assertIn("--all", service_calls[0])

    def test_satellite_cleanup_oneshot_uses_timer_and_last_result(self):
        runner = FakeRunner()
        runner.env_overrides["SATELLITE_CALL_TRANSCRIPTION_ENABLED"] = "true"
        runner.service_overrides["satellite-recordings-cleanup"] = {
            "active_state": "activating",
            "sub_state": "start",
        }

        code, report, _ = invoke(runner)

        self.assertEqual(code, 0)
        runtime = report["modules"]["nethvoice"][0]["runtime"]
        cleanup_service = next(
            item for item in runtime["services"] if item["name"] == "satellite-recordings-cleanup"
        )
        cleanup_timer = next(
            item for item in runtime["timers"] if item["name"] == "satellite-recordings-cleanup"
        )
        self.assertEqual(cleanup_service["expectation"], "conditional:timer")
        self.assertEqual(cleanup_service["active_state"], "activating")
        self.assertEqual(cleanup_timer["expectation"], "required:enabled-feature")
        cleanup_findings = [
            item for item in report["findings"] if item.get("component") == "satellite-recordings-cleanup"
        ]
        self.assertEqual(cleanup_findings, [])

        runner = FakeRunner()
        runner.service_overrides["satellite-recordings-cleanup"] = {"result": "exit-code"}
        _code, report, _ = invoke(runner)
        self.assertIn(
            "timer_service_last_result_failed",
            [item["code"] for item in report["findings"]],
        )

        runner = FakeRunner()
        runner.env_overrides["SATELLITE_CALL_TRANSCRIPTION_ENABLED"] = "true"
        runner.omit_services.add("satellite-recordings-cleanup")
        runner.omit_timers.add("satellite-recordings-cleanup")
        _code, report, _ = invoke(runner)
        finding_codes = [item["code"] for item in report["findings"]]
        self.assertIn("required_timer_missing", finding_codes)
        self.assertIn("required_timer_service_missing", finding_codes)

    def test_missing_configuration_fact_group_is_partial(self):
        runner = FakeRunner()
        runner.facts = runner.default_facts()
        for key in collector.NV_CONFIG_COUNT_GROUPS["telephony"]:
            runner.facts.pop(key)

        code, report, _ = invoke(runner)

        self.assertEqual(code, 1)
        self.assertEqual(report["status"], "partial")
        self.assertIn(
            {
                "stage": "nethvoice.configuration_counts.telephony",
                "code": "missing_expected_facts",
                "module_id": "nethvoice43",
            },
            report["errors"],
        )

    def test_route_destination_multiset_must_match_exactly(self):
        for extra_uri, expected_code in (
            ("sip:10.5.4.1:29999", "nethvoice_proxy_route_unexpected_destination"),
            ("sip:10.5.4.1:20025", "nethvoice_proxy_route_duplicate_destination"),
        ):
            with self.subTest(extra_uri=extra_uri):
                runner = FakeRunner()
                route = runner.default_routes()[0]
                route["address"].append({"uri": extra_uri})
                runner.routes = [route]

                code, report, _ = invoke(runner)

                self.assertEqual(code, 0)
                topology = report["proxy_topology"][0]
                self.assertTrue(topology["evidence_complete"])
                self.assertFalse(topology["consistent"])
                self.assertEqual(topology["route_checks"][0]["status"], "mismatch")
                self.assertEqual(len(topology["route_checks"][0]["actual_uris"]), 2)
                self.assertIn(expected_code, [item["code"] for item in report["findings"]])

    def test_incomplete_nethvoice_identity_cannot_label_route_stale(self):
        runner = FakeRunner()
        key = (
            "api-cli",
            "run",
            "module/nethvoice43/get-configuration",
            "--data",
            "{}",
        )
        runner.malformed[key] = "{}"

        code, report, _ = invoke(runner)

        self.assertEqual(code, 1)
        topology = report["proxy_topology"][0]
        self.assertFalse(topology["evidence_complete"])
        self.assertIsNone(topology["consistent"])
        self.assertEqual(topology["route_checks"][0]["status"], "unassessed")
        self.assertEqual(topology["unmatched_routes"][0]["classification"], "unassessed")
        self.assertNotIn(
            "proxy_route_without_local_nethvoice",
            [item["code"] for item in report["findings"]],
        )

    def test_failed_collection_command_is_partial_and_stderr_is_never_exposed(self):
        runner = FakeRunner()
        key = (
            "api-cli",
            "run",
            "module/nethvoice-proxy1/list-routes",
            "--data",
            "{}",
        )
        runner.failures[key] = ""
        code, report, serialized = invoke(runner)

        self.assertEqual(code, 1)
        self.assertIn(
            {"stage": "proxy.routes", "code": "command_failed", "module_id": "nethvoice-proxy1"},
            report["errors"],
        )
        topology = report["proxy_topology"][0]
        self.assertFalse(topology["evidence_complete"])
        self.assertIsNone(topology["consistent"])
        self.assertEqual(topology["route_checks"][0]["status"], "unassessed")
        self.assertIsNone(topology["route_checks"][0]["actual_uris"])
        self.assertNotIn(
            "nethvoice_proxy_route_missing",
            [item["code"] for item in report["findings"]],
        )
        self.assertNotIn(CANARY, serialized)

    def test_malformed_route_output_remains_unknown(self):
        runner = FakeRunner()
        key = (
            "api-cli",
            "run",
            "module/nethvoice-proxy1/list-routes",
            "--data",
            "{}",
        )
        runner.malformed[key] = f"not-json-{CANARY}"

        code, report, serialized = invoke(runner)

        self.assertEqual(code, 1)
        topology = report["proxy_topology"][0]
        self.assertFalse(topology["evidence_complete"])
        self.assertIsNone(topology["consistent"])
        self.assertEqual(topology["route_checks"][0]["status"], "unassessed")
        self.assertNotIn(CANARY, serialized)

    def test_fatal_preflight_and_invalid_arguments_have_documented_exit_codes(self):
        runner = FakeRunner()
        runner.failures[("api-cli", "run", "list-installed-modules")] = ""
        code, report, _ = invoke(runner)
        self.assertEqual(code, 3)
        self.assertEqual(report["status"], "fatal")

        code, report, _ = invoke(FakeRunner(), ["--nethvoice", "../../bad"])
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "selection_required")

        code, report, _ = invoke(FakeRunner(), ["--help"])
        self.assertEqual(code, 2)
        self.assertEqual(report["status"], "selection_required")

        code, report, serialized = invoke(ExplodingRunner())
        self.assertEqual(code, 3)
        self.assertEqual(report["errors"], [{"stage": "collector", "code": "internal_error"}])
        self.assertNotIn(CANARY, serialized)

    def test_canary_cdr_log_contact_credentials_and_trunk_data_never_reach_json(self):
        runner = FakeRunner()
        runner.routes = runner.default_routes() + [
            {
                "domain": "orphan.example.test",
                "address": [{"uri": "sip:10.5.4.1:20999", "description": CANARY}],
            }
        ]
        code, report, serialized = invoke(runner)

        self.assertEqual(code, 0)
        self.assertNotIn(CANARY, serialized)
        self.assertNotIn("calls_last_24h", serialized)
        self.assertNotIn("total_calls", serialized)
        self.assertNotIn("subscription_systemid", serialized)
        self.assertNotIn("api_key", serialized)
        self.assertEqual(report["proxy_topology"][0]["trunk_count"], 1)
        self.assertEqual(
            report["proxy_topology"][0]["unmatched_routes"][0]["classification"],
            "potentially_stale",
        )


class StaticSafetyTests(unittest.TestCase):
    def test_collector_has_no_network_clients_filesystem_writes_or_shell_execution(self):
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        forbidden_imports = {"socket", "urllib", "http", "ftplib", "ssl", "requests", "pathlib", "tempfile"}
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.assertNotEqual(node.func.id, "open")
                for keyword in node.keywords:
                    if keyword.arg == "shell":
                        self.fail("collector must not pass a shell option")
        self.assertFalse(imported & forbidden_imports)
        self.assertNotIn("shell=True", source)

    def test_collector_command_surface_is_passive(self):
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        string_values = {
            node.value.lower()
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        forbidden_commands = {
            "curl",
            "wget",
            "openssl",
            "nc",
            "nmap",
            "sngrep",
            "tcpdump",
            "tshark",
            "journalctl",
            "api-server-logs",
            "logcli",
        }
        self.assertFalse(string_values & forbidden_commands)

        invoked_actions = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            if node.func.attr == "action_json" and len(node.args) >= 3:
                action = node.args[2]
                if isinstance(action, ast.Constant):
                    invoked_actions.add(action.value)
        self.assertEqual(
            invoked_actions,
            {"get-configuration", "get-ports-list", "get-facts", "list-routes", "list-trunks"},
        )


if __name__ == "__main__":
    unittest.main()
