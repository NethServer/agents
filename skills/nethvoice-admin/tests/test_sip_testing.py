import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import threading
import time
import subprocess
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sip_endpoint import Endpoint, TestError, protected_json, remove_owned_container, rpc, write_private
from queue_test import AMI, Suite, assert_sequence, assert_queue_log
from cleanup_test import recover_fixture


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory()
        self.config = dict(username="899901", password="CANARY-credential", domain="pbx.invalid",
                           registrar="sip:pbx.invalid", proxy="sip:127.0.0.1:5060;lr",
                           sip_port=15101, rtp_port=31000, allowed_destinations=["899902"])
        self.endpoint = Endpoint(self.config, self.work.name, "A")
        self.endpoint.send = Mock()

    def tearDown(self):
        self.work.cleanup()

    def test_registration_and_failure_are_distinct(self):
        ep = self.endpoint
        ep.feed("sip:899901@pbx.invalid: registration success, status=200 (OK)")
        self.assertEqual(ep.snapshot()["registration"], "registered")
        ep.feed("SIP registration failed, status=403 (Forbidden)")
        with self.assertRaisesRegex(TestError, "registration failed"):
            ep.wait(lambda s: s["registration"] == "registered", 0.01)

    def test_incoming_default_rings_without_answer(self):
        ep = self.endpoint
        ep.feed("Incoming call for account 0!")
        ep.send.assert_called_once_with("call answer 180")
        self.assertEqual(ep.snapshot()["call"], "INCOMING")
        ep.feed("Authorization: Digest CANARY-credential")
        self.assertNotIn("CANARY", json.dumps(ep.snapshot()))
        ep.action("answer")
        ep.send.assert_called_with("call answer 200")
        ep.feed("Call 0 state changed to CONFIRMED")
        self.assertEqual(ep.snapshot()["call"], "CONFIRMED")

    def test_reject_on_demand_and_new_generation(self):
        ep = self.endpoint
        ep.feed("Incoming call for account 0!")
        ep.action("reject", code=486)
        ep.send.assert_called_with("call answer 486")
        ep.feed("Call 0 is DISCONNECTED [reason=486 (Busy Here)]")
        self.assertEqual(ep.snapshot()["code"], 486)
        ep.feed("Incoming call for account 0!")
        self.assertEqual(ep.snapshot()["incoming"], 2)
        self.assertEqual(ep.snapshot()["generation"], 2)
        self.assertIsNone(ep.snapshot()["code"])

    def test_timeout_and_unexpected_state(self):
        self.endpoint.state["alive"] = True
        with self.assertRaisesRegex(TestError, "timeout"):
            self.endpoint.wait(lambda s: s["call"] == "CONFIRMED", 0.001)
        with self.assertRaisesRegex(TestError, "no ringing"):
            self.endpoint.action("answer")
        with self.assertRaises(TestError):
            self.endpoint.action("reject", code=200)

    def test_destination_allowlist(self):
        with self.assertRaisesRegex(TestError, "allowlist"):
            self.endpoint.action("call", destination="003900000000")
        self.endpoint.action("call", destination="899902")
        self.endpoint.send.assert_called_once_with("call new sip:899902@pbx.invalid")
        with self.assertRaisesRegex(TestError, "already has"):
            self.endpoint.action("call", destination="899902")

    def test_configuration_security(self):
        path = Path(self.work.name) / "config.json"
        path.write_text(json.dumps(self.config))
        path.chmod(0o644)
        with self.assertRaisesRegex(TestError, "0600"):
            protected_json(path)
        path.chmod(0o600)
        self.assertEqual(protected_json(path), self.config)

    def test_start_failure_removes_secret_file_and_owned_container(self):
        ep = self.endpoint
        ep.wait = Mock(side_effect=TestError("SIP registration failed"))
        process = Mock()
        process.stdout = io.StringIO("SIP registration failed, status=403\n")
        process.poll.return_value = 0
        with patch("sip_endpoint.subprocess.Popen", return_value=process) as popen, \
             patch("sip_endpoint.subprocess.run", return_value=Mock(returncode=0)) as run:
            with self.assertRaisesRegex(TestError, "registration failed"):
                ep.start()
            self.assertFalse(ep.directory.exists())
            self.assertIn(ep.name, run.call_args[0][0])
            command = popen.call_args[0][0]
            self.assertNotIn("CANARY", " ".join(command))
            self.assertNotIn("--cli-telnet-port", " ".join(command))
            ep.close()  # Failure cleanup is safe to repeat.

    def test_cleanup_after_interruption(self):
        ep = self.endpoint
        ep.wait = Mock(side_effect=KeyboardInterrupt)
        process = Mock(stdout=io.StringIO(""))
        process.poll.return_value = 0
        with patch("sip_endpoint.subprocess.Popen", return_value=process), \
             patch("sip_endpoint.subprocess.run", return_value=Mock(returncode=0)):
            with self.assertRaises(KeyboardInterrupt):
                ep.start()
            self.assertFalse(ep.directory.exists())

    def test_runtime_cleanup_timeout_still_deletes_secret_and_kills_process(self):
        ep = self.endpoint
        config_file = ep.directory / "pjsua.conf"
        config_file.write_text("CANARY")
        ep.process = Mock()
        ep.process.poll.return_value = None
        with patch("sip_endpoint.subprocess.run", side_effect=subprocess.TimeoutExpired("podman", 20)):
            with self.assertRaisesRegex(TestError, "cleanup unavailable"):
                ep.close()
        ep.process.kill.assert_called_once()
        self.assertFalse(config_file.exists())

    def test_recovery_refuses_foreign_container_label(self):
        with patch("sip_endpoint.subprocess.run", return_value=Mock(returncode=0)), \
             patch("sip_endpoint.checked", return_value="foreign-label") as command:
            with self.assertRaisesRegex(TestError, "ownership mismatch"):
                remove_owned_container("nvtest-A-abcdef12", "A")
            self.assertEqual(command.call_count, 1)

    def test_rpc_wait_accepts_state_parameter(self):
        sock = Mock()
        sock.makefile.return_value.readline.return_value = b'{"call":"EARLY"}\n'
        connection = Mock()
        connection.__enter__ = Mock(return_value=sock)
        connection.__exit__ = Mock(return_value=False)
        with patch("sip_endpoint.socket.create_connection", return_value=connection):
            result = rpc({"control_port": 23231, "token": "test-token"}, "wait", state="RINGING", timeout=15)
        self.assertEqual(result["call"], "EARLY")
        request = json.loads(sock.sendall.call_args.args[0])
        self.assertEqual(request["state"], "RINGING")
        self.assertEqual(request["action"], "wait")

    def test_failed_report_write_preserves_previous_complete_json(self):
        path = Path(self.work.name) / "report.json"
        write_private(path, {"status": "FAIL"})
        with self.assertRaises(TypeError):
            write_private(path, {"not_serializable": object()})
        self.assertEqual(protected_json(path), {"status": "FAIL"})
        self.assertEqual(list(Path(self.work.name).glob(".nvtest-*")), [])


class QueueTests(unittest.TestCase):
    def test_ami_cursors_and_evidence_survive_full_event_buffer(self):
        ami = AMI.__new__(AMI)
        ami.extensions, ami.queue, ami.linked = ["899901"], "899910", set()
        ami.events, ami.responses, ami.sequence = [], {}, 0
        ami.condition = threading.Condition()
        ami.closed = False
        frame = b"Event: DialBegin\r\nChannel: PJSIP/899901-00000001\r\nUniqueid: old\r\n\r\n"
        ami.file = io.BytesIO(frame * 20000)
        ami.read()
        self.assertEqual(len(ami.events), 20000)

        with tempfile.TemporaryDirectory() as directory:
            config = dict(owner="nvtest-abcdef012345", strategy="linear", ring_timeout=4,
                          retry=1, ringinuse=False, autopause="no", lazy=False, penalties=[0, 0])
            suite = Suite(Mock(), config, directory, str(Path(directory) / "report.json"))
            suite.ami = ami

            def action():
                cursor = ami.cursor()
                ami.file = io.BytesIO(frame.replace(b"Uniqueid: old", b"Uniqueid: new") * 2)
                ami.read()
                event = ami.wait(lambda e: e["Event"] == "DialBegin", since=cursor, timeout=0.01)
                self.assertEqual(event["Uniqueid"], "new")
                self.assertEqual(event["seq"], cursor + 1)

            suite.scenario("buffer-rollover", "new events remain visible", action)
            scenario = suite.report["scenarios"][-1]
            self.assertEqual(scenario["status"], "PASS")
            self.assertEqual([e["seq"] for e in scenario["evidence"]["ami"]], [20001, 20002])
            self.assertEqual(len(ami.events), 20000)
            self.assertEqual(ami.cursor(), 20002)
            with self.assertRaises(TestError):
                ami.wait(lambda e: True, since=ami.cursor(), timeout=0.01)

    def test_recovery_checks_current_owner_before_affecting_calls(self):
        pbx = Mock()
        pbx.fixture.side_effect = TestError("current owner mismatch")
        config = dict(owner="nvtest-abcdef012345", extensions=["899901", "899902", "899903"],
                      target_host=socket.getfqdn(), module=os.environ.get("MODULE_ID"),
                      clients={"A": "nvtest-A-abcdef12"})
        with patch("cleanup_test.protected_json", return_value=config), \
             patch("cleanup_test.remove_owned_container") as remove:
            with self.assertRaises(TestError):
                recover_fixture("/tmp/saved/fixture.json", pbx)
            pbx.fixture.assert_called_once_with("verify", config)
            pbx.cli.assert_not_called()
            remove.assert_not_called()

    def test_audio_port_output_excludes_uri_and_path(self):
        with tempfile.TemporaryDirectory() as directory:
            endpoint = Endpoint({}, directory, "A")
            endpoint.feed("Conference ports:")
            endpoint.feed("Port #03[ 8KHz/20ms/1] sip:899901@pbx.invalid transmitting to: #0")
            endpoint.feed("Port #04[ 8KHz/20ms/1] /private/approved.wav transmitting to: #3")
            endpoint.feed("Account list:")
            event = endpoint.events[-1]
            self.assertEqual(event["ports"], [{"id": 3, "role": "call"}, {"id": 4, "role": "file"}])
            self.assertNotIn("private", json.dumps(event))
            self.assertNotIn("pbx.invalid", json.dumps(event))
    def test_malformed_adapter_response_can_never_report_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            config = dict(owner="nvtest-abcdef012345", extensions=["899901", "899902", "899903"], queue="899910",
                          strategy="linear", ring_timeout=4, retry=1, ringinuse=False, autopause="no", lazy=False,
                          penalties=[0, 0])
            pbx = Mock()
            pbx.fixture.return_value = {}
            pbx.cli.return_value = "0 active calls"
            report = Path(directory) / "report.json"
            suite = Suite(pbx, config, directory, str(report))
            self.assertEqual(suite.run(), 1)
            self.assertEqual(json.loads(report.read_text())["status"], "FAIL")

    def test_unregister_failure_does_not_skip_client_close(self):
        with tempfile.TemporaryDirectory() as directory:
            config = dict(owner="nvtest-abcdef012345", extensions=["899901", "899902", "899903"], queue="899910",
                          strategy="linear", ring_timeout=4, retry=1, ringinuse=False, autopause="no", lazy=False,
                          penalties=[0, 0])
            pbx = Mock()
            pbx.cli.return_value = "0 active calls"
            suite = Suite(pbx, config, directory, str(Path(directory) / "report.json"))
            ep = Mock(state={"alive": True, "call": "IDLE"})
            ep.action.side_effect = TestError("SIP state timeout")
            suite.endpoints = {"caller": ep}
            suite.cleanup()
            ep.close.assert_called_once()
            self.assertEqual(suite.report["scenarios"][-1]["status"], "FAIL")
    def test_queue_log_must_correlate_members_and_call(self):
        rows = [dict(callid="test-id", event=event, member=member) for event, member in
                [("RINGNOANSWER", "A"), ("CONNECT", "B"), ("COMPLETECALLER", "B")]]
        assert_queue_log(rows, "test-id")
        for bad in ([], rows[:2], [dict(r, callid="different") for r in rows],
                    [dict(r, member="A") for r in rows]):
            with self.assertRaises(TestError):
                assert_queue_log(bad, "test-id")
    def test_ring_sequence_rejects_repeat_and_wrong_order(self):
        assert_sequence(["A", "B"], ["A", "B"])
        for actual in (["A", "A"], ["B", "A"], ["A"], []):
            with self.assertRaises(TestError):
                assert_sequence(actual, ["A", "B"])

    def test_ami_discards_other_instances(self):
        ami = AMI.__new__(AMI)
        ami.extensions, ami.queue, ami.linked = ["899901", "899902"], "899910", {"controlled-id"}
        self.assertFalse(ami.relevant({"Channel": "PJSIP/201-deadbeef", "Queue": "200"}))
        self.assertTrue(ami.relevant({"DestChannel": "PJSIP/899902-0000001"}))
        self.assertFalse(ami.relevant({"DestChannel": "PJSIP/8999020-0000001"}))
        self.assertTrue(ami.relevant({"Linkedid": "controlled-id"}))

    def test_partial_setup_is_failed_and_fixture_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            config = dict(owner="nvtest-abcdef012345", extensions=["899901", "899902", "899903"], queue="899910",
                          strategy="linear", ring_timeout=4, retry=1, ringinuse=False, autopause="no", lazy=False,
                          penalties=[0, 0])
            pbx = Mock()
            def fixture(operation, config):
                if operation == "inspect":
                    return {"occupied": [], "lazy_configurable": False}
                if operation == "create":
                    raise TestError("partial fixture setup failed")
                return {"removed": True}
            pbx.fixture.side_effect = fixture
            pbx.cli.return_value = "0 active calls\n"
            suite = Suite(pbx, config, directory, str(Path(directory) / "report.json"))
            self.assertEqual(suite.run(), 1)
            scenarios = suite.report["scenarios"]
            self.assertTrue(any(s["status"] == "FAIL" for s in scenarios))
            self.assertTrue(any(c.args[0] == "delete" for c in pbx.fixture.call_args_list))
            self.assertEqual(scenarios[-1]["name"], "cleanup")
            self.assertFalse((Path(directory) / "fixture.json").exists())

    def test_failed_cleanup_preserves_recovery_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            config = dict(owner="nvtest-abcdef012345", extensions=["899901", "899902", "899903"], queue="899910",
                          strategy="linear", ring_timeout=4, retry=1, ringinuse=False, autopause="no", lazy=False,
                          penalties=[0, 0])
            pbx = Mock()
            pbx.fixture.side_effect = TestError("fixture removal failed")
            pbx.cli.return_value = "0 active calls"
            suite = Suite(pbx, config, directory, str(Path(directory) / "report.json"))
            suite.created = True
            manifest = Path(directory) / "fixture.json"
            manifest.write_text("{}")
            suite.cleanup()
            self.assertEqual(suite.report["scenarios"][-1]["status"], "FAIL")
            self.assertTrue(manifest.exists())


if __name__ == "__main__":
    unittest.main()
