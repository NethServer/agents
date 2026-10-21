# Automated SIP and queue tests

Read this only for explicitly authorized active testing. Keep the foundation, production and sensitive-data rules in the parent skill. Calls, fixture creation, FreePBX reloads and communications metadata collection require authorization for this instance. Never dial PSTN numbers or existing users. The runner accepts only its three fixture extensions and its queue as destinations.

## Architecture and provenance

The canonical implementation lives alongside this reference in `../scripts/sip_endpoint.py`, `../scripts/queue_test.py`, `../scripts/queue_fixture.php` and `../scripts/cleanup_test.py`. It reuses the PJSUA container and CLI documented by [ns8-nethvoice's nethvoice-testing skill](https://github.com/nethesis/ns8-nethvoice/blob/376fafda7a76adb420679d5503cbb7995aa6876c/.agents/skills/nethvoice-testing/SKILL.md). The installed FreePBX 17 Core/Queues code on the target was inspected before using its APIs. The NethVoice checkout inspected was `98b7f4f3e932d9059e68aa6f181ab78999c19e55`; upstream fpbx17 was `376fafda7a76adb420679d5503cbb7995aa6876c` at investigation time. Installed code remains authoritative.

PJSUA is the SIP implementation; Python supervises it, parses whitelisted state events, and sends its existing CLI commands. Each client uses private stdin/stdout pipes. `stdbuf` enables timely log delivery without a terminal. No PJSUA telnet listener is started. The optional endpoint daemon exposes a distinct control port on **127.0.0.1 only**, authenticated by a token in an owner-only state file. SIP/RTP ports must be distinct for every client; allow ten RTP ports per endpoint. One simultaneous call per endpoint avoids ambiguous current-call controls. Multiple endpoints operate independently.

The pinned, live-tested image is `ghcr.io/stell0/pjsua@sha256:9a6374528aa19074b4702cb45d6fe8ecd9817cdc492b4aa1265d1b788884389e` (PJSUA 2.17). It was obtained from `ghcr.io/stell0/pjsua:latest`. Revalidate help, binary paths, CLI and `stdbuf` before changing the digest. No production image changes or test packages are needed. For developer/CI use, check out a pinned revision of NethServer/agents and invoke these scripts from it; do not copy the harness into ns8-nethvoice/tests. A thin CI invocation may reference that checkout.

`queue_fixture.php` is the installed-version adapter. It calls `Core::generateDefaultUserSettings`, `addUser`, `generateDefaultDeviceSettings`, `addDevice`, `delDevice`, `delUser`, and the Queues module's `queues_add`, `queues_get`, `queues_del`. Changes follow a collision check across FreePBX destinations, users/devices and queues. Cleanup verifies the random owner marker before deleting anything. It does not issue database writes or edit generated configuration. AMI controls temporary dynamic members. Read-only queue_log SQL is restricted to the verified ODBC schema, a starting cursor, and the dedicated queue.

## Preflight and installation

1. Activate nethserver-admin and nethvoice-admin. Verify host/node/module identities, installed versions, active calls, module actions/schemas and services. Record authorization, intended duration, scope, rollback and baseline counts. Inspect installed Core/Queues API definitions against the adapter. FreePBX reload affects this PBX's configuration; no shared proxy restart is necessary.
2. Discover `NETHVOICE_HOST`, the node-local proxy module, its domain route, advertised/public listener, and protocol-specific Asterisk ports. Confirm with `get-ports-list`, `pjsip show transports` and the proxy's supported `get-route` action. Do not infer UDP from `ASTERISK_SIP_PORT`: it can be TCP-only.
3. Run Python 3.9+ and Podman in **this module's context**, using `runagent -m MODULE`. The FreePBX container must expose PHP, fwconsole, Asterisk, the Core/Queues API and AMI. The default adapter targets the observed FreePBX 17 API; use `--fixture-adapter /reviewed/adapter.php` only after reviewing another installed API. Check AMI availability and the queue_log backend before testing. No direct SQL mutations are allowed.
4. Copy the four scripts into a new mode-0700 directory under the discovered `AGENT_STATE_DIR`, owned by the module user. Pull the pinned image in that module's Podman context. Choose unused numeric destinations and unallocated client SIP/RTP ports. Run unit tests locally with `python3 -m unittest discover -s skills/nethvoice-admin/tests`.

### Proxy routing trap

Register **through the proxy** if the Asterisk endpoint's `outbound_proxy` sends calls through it. Healthy registration alone does not prove inbound INVITEs reach the client. The fixture uses the observed Asterisk-to-proxy URI and preserves the client's registration contact (`rewrite_contact=no`, `force_rport=no`); the proxy owns the signaling path.

On the live node, using the WireGuard/internal proxy address as the **client** proxy caused source classification as PBX-originated traffic and `483 Too Many Hops`. Using the observed public listener for clients resolved it; Asterisk still used its internal proxy URI. Accordingly, `--proxy` (client path) and `--endpoint-proxy` (Asterisk path) are independent. Never change the shared proxy to work around a test-client routing mistake. A deliberately direct Asterisk test needs separately proven direct registration/contact routing and an explicitly empty endpoint proxy; it does not validate the proxy.

## Run the deterministic fixture

The runner creates caller, A and B plus an empty test queue, registers all three real SIP clients, adds A then B dynamically, executes the tests, unregisters clients and removes the fixture. Defaults use `linear`, equal penalties, four-second member timeout, one-second retry, `ringinuse=no`, `autopause=no`. These settings make ordering a strategy baseline. Do not interpret that ordering as proof of Lazy Members.

The hostnames, addresses and module IDs below are placeholders; replace them with the authorized target values. Example **only after discovering these values** (executed inside `runagent -m nethvoice1 sh -lc ...`, in the copied harness directory):

```bash
python3 queue_test.py \
  --authorized-test \
  --expected-host test-node.example.org --module nethvoice1 \
  --domain voice.example.org \
  --proxy 'sip:203.0.113.10:5060;lr' \
  --endpoint-proxy 'sip:10.0.0.10:5060;lr' \
  --extensions 899901 899902 899903 --queue 899910 \
  --strategy linear --ring-timeout 4 --retry 1 --penalties 0 0 \
  --repeat 3 --workdir "$AGENT_STATE_DIR/nvtest-harness/run-new" \
  --report "$AGENT_STATE_DIR/nvtest-harness/report-new.json"
```

Workdir must be new. Reports are mode 0600 and contain controlled-call metadata. The host must equal `socket.getfqdn()` and `MODULE_ID` must match `--module`; the authorization flag is an explicit acknowledgement, not a replacement for user authorization. Exit 0 means no failing scenarios; inspect SKIPs separately. Exit 1 means setup, assertion or cleanup failed. stdout is a short per-scenario summary.

Parameters: `--strategy`, `--ring-timeout`, `--retry`, `--ringinuse`, `--autopause no|yes|all`, `--penalties A B`, `--lazy`, `--sip-base`, `--rtp-base`, `--repeat 1..20`. The default expected sequence remains A then B. Selecting ringall, unequal penalties or autopause can change routing; a mismatch is a failed sequential assertion, not evidence of a Lazy Members defect. For another scenario, import `Suite`/`Endpoint` and use their bounded waits and AMI controls rather than adding sleeps or a new SIP stack.

**Lazy Members:** the observed installed Queues API has no setter for `lazymembers`. `--lazy` reports SKIP for that feature and FAIL for unsupported fixture setup, before creating anything. The default baseline reports the paired Lazy Members comparison as SKIP. Do not force it with SQL or generated-file edits. A reviewed adapter for an installed supported setter must return `lazy_configurable=true`, apply/verify the setting in `create`/`configure`, and preserve the other contract operations (`inspect`, `verify`, `delete`, `ami`, `log-cursor`, `queue-log`). Run matched scenarios with the same strategy, members, order, penalties, retry and timeout, changing only Lazy Members. Test a strategy that would otherwise reoffer A, such as an appropriate penalty/ringall case, and assert that negative control as well. Autopause must be off to isolate Lazy Members. The baseline alone cannot establish this feature's correctness.

## Independent endpoint control

Supply an approved JSON credential file, owned by the invoking module user with mode 0600. Create it through a protected provisioning process or `getpass`/stdin; never put passwords in arguments, command history, a report, an environment dump or a committed file. Required keys:

```json
{
  "username": "899901",
  "password": "<protected input; never commit a real value>",
  "domain": "voice.example.org",
  "registrar": "sip:voice.example.org",
  "proxy": "sip:203.0.113.10:5060;lr",
  "sip_port": 15101,
  "rtp_port": 31000,
  "duration": 120,
  "allowed_destinations": ["899902", "899903", "899910"]
}
```

```bash
python3 sip_endpoint.py start --config /protected/caller.json \
  --state /protected/caller.state --control-port 23231
python3 sip_endpoint.py status --state /protected/caller.state
python3 sip_endpoint.py call --state /protected/caller.state \
  --params '{"destination":"899902"}'
python3 sip_endpoint.py wait --state /protected/member-a.state \
  --params '{"state":"RINGING","timeout":15}'
python3 sip_endpoint.py answer --state /protected/member-a.state
python3 sip_endpoint.py hangup --state /protected/caller.state
python3 sip_endpoint.py unregister --state /protected/caller.state
python3 sip_endpoint.py stop --state /protected/caller.state
```

Start A and B similarly with different config/state files, SIP/RTP ports and control ports (for example 23232/23233). `start` waits for registration. `register` refreshes a stopped registration; `unregister` waits for SIP unregistration. `ring` and `no-answer` set incoming behavior to ignore: the client sends 180 and never 200, letting the PBX cancel it at its own timeout. `answer` requires a ringing call. `reject --params '{"code":486}'` returns Busy Here; choose another 300..699 status when needed. `behavior --params '{"behavior":"answer"}'` or `'{"behavior":"reject","code":486}'` sets future INVITE handling; `ignore` restores manual control. These changes can occur while another endpoint is already ringing. `wait` accepts `state`, `timeout` and `after` (event sequence cursor). Status includes registration, current call state, last disconnect code, INVITE count and timestamped events. `duration` bounds a connected call independently of the controller.

Audio is optional and is not an acceptance prerequisite. `play_file` and `record_file` config keys mount approved paths; recording requires separate purpose/retention authorization. The WAV recorder uses `--auto-rec`; `play` connects observed conference ports with `source` and `target`. Use `audio-list` to return observed port IDs and roles, then pass them to `play`; never assume a conference slot. The default live tests use null audio and collect no recordings, transcripts or packet captures.

## Queue operations and evidence

`Suite.add_members()` uses AMI QueueRemove/QueueAdd in explicit order with penalty, paused state, state interface and ringinuse. The controls scenario applies QueuePause/QueuePenalty/QueueRemove and asserts the corresponding AMI events. `queue_call(change_behavior=True)` switches B to automatic answer only after A has received its INVITE. An agent can use the same AMI object for supported QueueAdd, QueueRemove, QueuePause and QueuePenalty operations during a call; restrict them to the owned queue and endpoints.

Every scenario reports PASS/FAIL/SKIP, expected and actual results, and evidence. SIP INVITEs determine the actual ringing order. Direct calls also require Asterisk DialBegin, BridgeEnter, and SIP CONFIRMED; no-answer requires DialEnd=NOANSWER, and rejection requires BUSY. Queue calls require A's real SIP ringing/disconnection, correlated AgentRingNoAnswer, B's INVITE/CONFIRMED and AgentConnect to B, plus queue_log RINGNOANSWER(A), CONNECT(B), COMPLETE(B) with the same Asterisk uniqueid. Caller CONFIRMED alone is insufficient because a queue can answer into MOH.

Waits are event-driven with deadlines; queue_log availability uses bounded polling. AMI uniqueid/linkedid and timestamps correlate both legs. Raw PJSUA logs and unrelated AMI events are discarded. Queue status is restricted to the owned queue. File queue_log and the observed ODBC schema are supported. CDR/CEL are supplementary diagnostics, not substituted for the queue assertions; collect them only if SIP/AMI/queue_log disagree. No global SIP/RTP debug logging is enabled. Unexpected `A -> A`, missing events, setup failures and cleanup errors fail the test.

Use the report's scenario evidence to distinguish an endpoint/proxy failure from a queue selection failure. Keep private reports in the approved test directory only; publish a derivative with extension labels and opaque call IDs. The live validation reference includes a sanitized example. Unit tests cover mocked PJSUA output, failed registration, timeouts, invalid state, destination restrictions, evidence correlation and cleanup after failure/interruption.

## Cleanup and automation

The suite's `finally` block clears test calls, unregisters/stops exact owned containers, removes the owned queue/extensions through FreePBX, reloads, checks fixture absence, and checks test channels. Cleanup failures are FAIL and preserve the protected fixture manifest for recovery. Never use a wildcard container removal or hang up all PBX channels. After an interruption, inspect the saved manifest and ownership before retrying cleanup. SIGTERM/SIGINT trigger cleanup; SIGKILL or a lost node requires explicit recovery and registration-expiry checks.

Before reporting completion, independently verify zero test channels, no test contacts/clients, restored extension/queue counts, module/container state and restart counts, Asterisk uptime, and unchanged proxy route/certificate assignment. FreePBX/AMI operations do not appear as NS8 API configuration changes; record that distinction. Test CDR/queue_log entries intentionally remain as operational history. Remove private credentials, raw metadata reports and temporary script copies at the end of the approved retention window. Keep sanitized evidence in the repository only.

For automated development, invoke the runner over SSH inside `runagent` with a unique workdir/report, retain its exit code and restricted JSON artifact, and always execute recovery if the controller is lost. Pin both agents revision and PJSUA digest. Do not put test dependencies in the NethVoice image. See `automated-sip-live-validation.md` for exactly what has and has not been exercised.

Recovery after confirming the original controller has exited (same host and module context):

```bash
python3 cleanup_test.py --authorized-test \
  --expected-host test-node.example.org --module nethvoice1 \
  --manifest "$AGENT_STATE_DIR/nvtest-harness/run-new/fixture.json" \
  --report "$AGENT_STATE_DIR/nvtest-harness/recovery.json"
```

For an orphan standalone endpoint, replace `--manifest` with `--endpoint-state /protected/caller.state`. Use normal `stop` while its controller is alive. Recovery checks the saved host/module, current FreePBX ownership before any hangup, and exact container labels before removal. It never kills a PID from a stale file. Forced termination cannot send a SIP unregister; independently confirm contact removal/expiry (default registration interval 120 seconds). A recovery failure retains the manifest/state and returns nonzero.
