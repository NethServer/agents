# Symptom-driven production diagnosis

Read `sensitive-data.md` before collecting communications evidence. Stay passive until evidence identifies a narrower test and the user approves its impact.

## Safe evidence ladder

1. Establish host, node, module placement, installed images/versions, incident window, affected direction/users/features, and whether calls are active.
2. Discover installed actions and schemas. Collect configuration only through fields needed for the symptom; never print an environment or password file.
3. Run the passive collector when a broad aggregate snapshot helps:

   ```bash
   ssh root@target 'python3 - --nethvoice nethvoice43 --proxy nethvoice-proxy1 --pretty' \
     < skills/nethvoice-admin/scripts/collect_diagnostics.py
   ```

   To retain the reviewed local collector under a collision-resistant, root-only
   path in `/tmp` and launch that copy in the same authenticated SSH session:

   ```bash
   ssh root@target '
     set -eu
     collector_path=$(mktemp /tmp/nethvoice-collect-diagnostics.XXXXXX)
     tee "$collector_path" >/dev/null
     chmod 0700 "$collector_path"
     printf "collector_path=%s\n" "$collector_path" >&2
     exec python3 "$collector_path" \
       --nethvoice nethvoice43 \
       --proxy nethvoice-proxy1 \
       --pretty
   ' < skills/nethvoice-admin/scripts/collect_diagnostics.py
   ```

   The wrapper writes only the temporary path to stderr; collector stdout remains
   JSON. Use the exact discovered module IDs. The file remains in `/tmp` for hash
   verification or an approved follow-up, so remove only the printed path when it
   is no longer needed. Do not replace the random path with a predictable filename
   or download and execute a mutable remote URL.

   Exit 0 is a complete collection, 1 a valid partial report, 2 invalid/ambiguous selection, and 3 a fatal preflight failure. Health warnings can exist in a complete report. Treat topology `consistent: null`, `evidence_complete: false`, and `status: unassessed` as unknown—not as a missing route. Destination lists preserve duplicates so exact route multiplicity can be checked.
4. Inspect aggregate Asterisk state, discovered unit/container state and restart counters, installed dynamic ports, proxy route consistency, passive certificate assignment, local addresses/routes, disk/memory/file-descriptor pressure, and NS8 audit history.
5. Retrieve only a bounded log window tied to the incident. Prefer NS8 log interfaces documented by the installed Core. If the installed `api-server-logs` command follows, bound both time and rows:

   ```bash
   timeout --signal=INT 15s api-server-logs logs -e module -n "$mid" \
     | head -n 200
   ```

   Treat timeout/SIGPIPE as the expected bound only after confirming output was produced; preserve a real command failure. Apply source-side filters and redaction before sharing any line.
6. If a rootless module's user journal returns no rows, validate the account and UID, then query the host journal as root with that exact `_UID` and strict bounds:

   ```bash
   mid=<validated_local_module_id>
   uid=$(id -u -- "$mid") || exit 1
   test "$(getent passwd "$uid" | cut -d: -f1)" = "$mid" || exit 1
   journalctl -b _UID="$uid" --since '<incident-start>' --until '<incident-end>' \
     --no-pager -n 200
   ```

   Redact before sharing. Do not widen the window merely because the first query is empty.
7. Request approval before an active SIP/TLS/RTP test, call, trace, packet capture, debug toggle, browser automation that places calls, or reproduction that affects a real endpoint.

## Registration and contacts

Start with the selected instance/proxy relationship, aggregate endpoint/contact counts, Asterisk uptime, dynamic SIP/SIPS ports, Kamailio state, certificate assignment, and recent restarts. Determine whether the failure affects one endpoint class, one network, one transport, or all registrations.

For one authorized endpoint, filter evidence at the source to the minimum identifier and status. Correlate authentication/realm, transport, certificate trust, expiry, proxy route, endpoint generation, NAT/contact rewriting, and firewall ownership. Never publish `pjsip show contacts` or endpoint dumps: contact URIs can contain user, address, and device data.

## Trunks and call setup

Separate registration-based trunks from IP-authenticated/no-registration trunks. Confirm only aggregate trunk count until a particular trunk is in scope. Then compare installed provider/wizard settings, transport/realm, proxy handling, inbound domain/number route, outbound route order, codecs, and final Asterisk hangup class.

For failed calls, record direction, sanitized time, phase (INVITE, ringing, answer, teardown), and whether Asterisk created channels. Do not place a test call or reveal numbers/caller IDs without approval. Convenience “trunk status” labels are not sufficient proof; correlate Asterisk, proxy, and provider-side evidence.

## RTP, no audio, one-way audio, and 30-second drops

Signaling success does not validate media. Compare the installed Asterisk and proxy RTP ranges, node/proxy private and public addresses, `local_networks`, VPN subnets, SDP-advertised addresses, codec/SRTP/DTLS agreement, RTPengine state, and symmetric return path. Standard proxy deployments should solve NAT at the proxy; do not add remembered FreePBX NAT overrides unless the installed design intentionally bypasses the proxy.

Check hairpin NAT when LAN devices resolve NethVoice/proxy names to the public address. Check SIP ALG/NAT helpers, multi-WAN source stability, MTU, and firewall direction. A packet capture or RTP debug contains communications metadata and potentially audio; require an approved endpoint/time filter, duration, storage location, owner, cleanup time, and rollback for debug settings.

For a call already authorized and identified by one exact Call-ID, inspect the installed RTPengine command surface and then that session only. Replace the placeholders with the exact discovered proxy module ID and the user-supplied or narrowly correlated Call-ID:

```bash
runagent -m <proxy-module-id> podman exec rtpengine rtpengine-ctl --help
runagent -m <proxy-module-id> podman exec rtpengine rtpengine-ctl list sessions <call-id>
```

Keep the lookup scoped to one Call-ID. Do not replace it with an aggregate selector, enumerate unrelated sessions, or use `terminate`, configuration, debug, or other mutating control verbs. Treat the result as communications metadata: compare per-leg packet/byte counters, last-packet timing, and relay direction, then report with opaque leg labels and without reproducing the Call-ID, SIP identities, or endpoint addresses unless topology proof requires an infrastructure address. A zero or static receive counter localizes the missing media direction but does not by itself prove whether the cause is SDP, NAT/firewall, routing, or the remote endpoint.

## WebRTC, CTI, and Janus

Distinguish UI delivery, authentication, CTI server events, middleware APIs, Asterisk control, WebSocket routing, Janus signaling, and browser media. Verify CTI/Janus HTTP routes and certificate names, discovered ports, container health, restart counts, and browser errors supplied by the user.

Before treating inactive CTI server/middleware units as failed, establish whether the NethVoice wizard completed for the installed version. For a CTI-only outage with healthy calls, avoid restarting Asterisk. Diagnose CTI UI, middleware/server, LDAP/user mapping, WebSocket/session routing, and Janus independently. Administrative CTI helpers and integration/rebranding actions can reload profiles or restart telephony services; inspect and approval-gate them.

## Tancredi and provisioning

Verify the exact NethVoice host route, Tancredi service, provisioning path routing, entitlement state, phone model/firmware compatibility, DHCP/RPS method, DNS/certificate trust from the phone network, and access through NAT/hairpin paths. Provisioning URLs embed secrets: record only presence, not tokens, full URLs, MAC addresses, or generated configuration. Manufacturer RPS checks are outbound operations and require approval.

## Reports

Separate UI/API/Redis/scheduler availability from missing or delayed call data. Check discovered services, health, restart counters, queue/backlog aggregates, timezone, retention and disk capacity. CDR/CEL rows contain communications data; start with aggregate counts and narrow timestamps. Do not expose caller/callee, unique IDs, recording links, queue membership, or raw report queries in the incident record.

## Satellite and external integrations

First confirm whether transcription, voicemail transcription, summary, or other Satellite features are enabled and entitled. When transcription is disabled, the Satellite application and MQTT units may be inactive or absent, while an initialized Satellite PostgreSQL service can remain running for middleware, users, and historical transcript data. Treat the recordings-cleanup service as a timer-driven oneshot: inspect its timer and last result instead of expecting the service to remain active. When enabled, trace the aggregate pipeline: recording/event creation, Satellite service/MQTT/database health, backlog/state counts, and approved provider reachability.

For suspected OpenAI, Deepgram, ElevenLabs, CRM, hotel, or other integration failures, report credential/configuration presence as booleans only. Inspect the installed integration action before calling it: it may restart CTI or FreePBX. Do not echo API keys, provider payloads, transcript/summary text, customer-card data, external numbers, or verbose authenticated HTTP output.

## LDAP, databases, and certificates

- LDAP: verify configured domain identity by approved infrastructure name or opaque reference, provider health, binding route, certificate/time/DNS, schema compatibility, and aggregate lookup result. Never print bind passwords or user records.
- MariaDB/PostgreSQL/Redis: establish container health, capacity, connection failure class, and schema/version provenance. Prefer installed read actions and aggregate queries. Direct Redis writes are prohibited; SQL repair belongs only to the lifecycle break-glass gate.
- Certificates: distinguish Traefik HTTPS certificates, proxy SIP/TLS, WSS/Janus, and container-imported copies. Check node ownership, names, issuer/type, expiry/state, event/action result, and file hashes where safe—never private keys. Active TLS handshakes are probes and need approval.

## Diagnostic stop conditions

Stop and report uncertainty when the module is remote, selection is ambiguous, installed source/schema cannot be established for a proposed query, active-call state cannot be read before disruptive work, evidence would require secret dumping, or the next step exceeds the approved incident window.
