# Live validation, 2026-10-21

The user authorized test calls, configuration changes, reloads, restarts and disruption only on the development instance `nethvoice72` at `makako.sf.nethserver.net`. The observed host FQDN is `makako.makako.sf.nethserver.net`, NS8 node 1, Rocky Linux 9.8. No PSTN destinations or existing users were called. No Lazy Members patch was modified.

Installed NethVoice: `ghcr.io/nethesis/nethvoice:fpbx17`, module digest `sha256:4aaeed15f420486a6fde31fc79e9fc7beef2a4891f40d8f555309b865b982a61`. FreePBX 17 with Asterisk 22.10.0. Node-local proxy: `nethvoice-proxy4`, image version `pr-228.160-1.3fb1f3e`, digest `sha256:b87cb6ed837c93532def337e3dd9e637e8055b28647112923cb4dd020ff529eb`.

Observed signaling route: `voice3.makako.sf.nethserver.net` -> proxy domain dispatcher -> `sip:10.5.4.1:22999` (Asterisk UDP). Asterisk TCP is 20172; clients used the proxy public UDP listener `46.101.162.171:5060`. Asterisk endpoint outbound_proxy remained `sip:10.5.4.1:5060;lr`. The three clients used SIP 15101..15103 and disjoint RTP bases 31000/31010/31020. No shared proxy configuration changes or restarts were made.

The fixture used three previously unused extensions and a dedicated queue, all carrying a random `nvtest-…` owner marker. Original inventory: 105 extensions and 4 queues. Fixture changes went through inspected installed Core/Queues APIs and `fwconsole reload`; dynamic queue membership used AMI. Each completed run removed its resources through the same APIs. Test dependencies stayed in the module user's test workspace/Podman image cache; production images were not changed.

## Executed tests

| Live test | Result and evidence |
| --- | --- |
| Three simultaneous PJSUA registrations | PASS, real REGISTER responses from the PBX through the proxy |
| Caller -> A, A -> caller, caller -> B, B -> caller | PASS, SIP ringing/manual answer/CONFIRMED/disconnect plus correlated Asterisk DialBegin/BridgeEnter |
| Genuine no-answer | PASS, received INVITE/180 without 200, PBX timeout, Asterisk DialEnd=NOANSWER |
| Explicit busy rejection | PASS, SIP 486 and Asterisk DialEnd=BUSY |
| Queue membership controls | PASS, add/order, pause, penalty change, unpause, remove/re-add; state-changing AMI events checked |
| A -> no answer -> B -> answer | PASS, actual SIP INVITE order, AgentRingNoAnswer(A), AgentConnect(B), same-call ODBC queue_log RINGNOANSWER(A)/CONNECT(B)/COMPLETECALLER(B) |
| Change behavior during a queue call | PASS, B switched to automatic answer only after A was already ringing; same A -> B assertions |
| Repetition | PASS, one initial baseline, three repetitions, two repetitions after stricter correlation/cleanup fixes, and one final repetition. Both queue variants ran in the last six repetitions |
| Independent daemon/CLI controls | PASS, three daemon starts, manual answer/hangup, no-answer, busy, unregister/register and stop |
| Control isolation | PASS, all three listeners bound to 127.0.0.1; invalid control token rejected; PJSUA telnet listener disabled |
| SIGTERM cleanup | PASS, live client terminated, control state removed; final cleanup checked absence of test resources |
| Audio port discovery | PASS, observed conference port IDs and sanitized roles returned |
| Lazy Members on/off comparison | SKIP, installed supported Queues API does not expose a lazymembers setter |

The initial attempts did not pass: one registration timeout exposed buffered CLI output, and a retry returned SIP 483 because the proxy classified internal-node-originated clients as outbound PBX traffic. `stdbuf` and the observed public client path resolved those causes. An initial independent-daemon attempt also failed due to the RPC `state` parameter collision; its fixture/clients were removed and the corrected interface passed. These failures are not counted as successful queue tests.

The final representative suite contains 11 PASS scenarios and one SKIP (Lazy Members); the earlier three-repeat suite contains 29 PASS and one SKIP. The separate daemon validation contains nine PASS checks. The [sanitized JSON report](automated-sip-report.example.json) contains exact per-run counts, source-report hashes, scenario results and one call's correlated SIP/AMI/queue_log evidence using opaque identifiers. It is a derivative, not a fabricated example.

## Limits

The verified fixture is a **linear, equal-penalty strategy baseline**, ring timeout 4 seconds, retry 1 second, ringinuse=no and autopause=no. It does not demonstrate Lazy Members correctness: no supported installed setter was found and none was bypassed. Other strategies, nonzero initial penalties, autopause variants and a second tenant/node remain unverified live. Runtime penalty/pause changes were exercised. No media playback/recording, RTP quality, TLS, CDR/CEL assertions or CI integration was claimed. Forced SIGKILL/node-loss recovery has unit coverage for ownership and failure handling but is distinct from the live SIGTERM path.

No packet capture, SIP logger, RTP debug, recording or transcript collection was enabled. Reports contain only test-call metadata; the committed derivative replaces extension and unique/linked identifiers with labels. Temporary credential inputs are removed during cleanup. Test CDR/queue_log history remains in the PBX, as expected for real calls.

## Final reconciliation

Independent post-test checks found 105 extensions and 4 queues (the original counts), no occupied fixture numbers, zero active calls, zero test channels, zero test contacts, no test containers, no control-state files and no PJSUA credential files. The proxy domain route still targets `sip:10.5.4.1:22999`. FreePBX, MariaDB, Kamailio and RTPengine remained active with NRestarts=0; their process start timestamps predate the task. Asterisk uptime advanced continuously from approximately 19h26m to 19h57m, with only configuration reloads.

Other instance services had newer start timestamps during the exercise: NethCTI server at 10:10:47 UTC (NRestarts=1), phonebook at 10:26:24 UTC, reports API/UI at 10:28:39 UTC (NRestarts=0). The harness issued no explicit service-restart command; these observed restarts are recorded as impact, without attributing a cause not established by the available logs. All were active at reconciliation. A bounded user-journal query yielded no matching systemd lifecycle messages. TLS/certificate assignment was not changed; TLS behavior was not tested.

The recovery CLI was also exercised live against an owned, saved fixture with no running clients: PASS, resources removed and counts restored. This does not claim forced-client registration-expiry validation. The NS8 audit database was queried read-only using Python sqlite3 (the sqlite3 CLI is absent); it had no rows matching this module. Direct FreePBX and AMI operations are recorded here and in test reports rather than being represented as NS8 API mutations.

Local validation: 52 unit/contract tests PASS, Python compilation PASS, skill frontmatter/reference validation PASS. Independent review exercised failure paths and the resulting corrections have regression coverage.

After collecting the sanitized derivative, private raw reports, stale recovery manifests and temporary run directories were removed. The four reusable harness scripts and pinned PJSUA image cache remain intentionally installed under the module user for subsequent development tests; no test fixture configuration remains.
