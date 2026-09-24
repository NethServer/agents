# Repair and lifecycle procedures

All changes inherit the router's preflight, approval, active-call, verification, and incident-report gates. Read `sensitive-data.md` whenever evidence or backups can contain communications or credentials.

## Supported-change workflow

1. Pin the target host/node/module IDs and installed image versions/digests.
2. Discover the installed action and read its input schema and implementation, including transitive task calls, unit restarts, route/certificate writes, and events.
3. Capture sanitized before-state, current supported configuration, health/restart counters, active calls/channels, route/certificate state, audit position, and rollback material.
4. Build the smallest schema-valid payload. Preserve required current fields. Treat `configure-module`, CTI/integration, NethHotel, and rebranding changes as disruptive until source proves otherwise.
5. Present exact impact, window, payload with secrets redacted, rollback and verification; obtain explicit approval.
6. Run one change at a time. Stop on unexpected output/state; do not stack speculative fixes.
7. Perform the complete verification from `../SKILL.md` and record rollback status.

## Independent active-call gate

Before restarting Asterisk, FreePBX, the proxy, RTPengine, CTI services that may cascade into telephony, or running an action that can do so:

- Query Asterisk directly inside the discovered running FreePBX container with the installed CLI and parse `core show channels count` for both active channels and active calls.
- Repeat immediately before the disruptive step. Correlate with any approved CTI/operator view when available.
- Do not rely solely on a convenience restart helper's embedded check. If that helper cannot query Asterisk, independently query it; a helper failure is not proof of zero calls.
- If either independently parsed count is non-zero, defer until calls drain or obtain explicit emergency approval that accepts terminating those calls.
- If a valid zero count cannot be obtained, defer. Proceed only under explicit emergency approval that names the inability to determine active calls and accepts call loss.

## Configuration and upgrades

Use the installed targeted action where available. Broad configuration can rewrite routes, proxy values, users, reports, certificates, and start/restart multiple services. For NAT, port, trunk, extension, and FreePBX changes, prefer supported UI/actions and Apply Config behavior over generated-file edits.

For an upgrade, confirm release path and compatibility for both NethVoice and its node-local proxy, current backups, free capacity, active calls, maintenance window, installed update action/schema, and documented rollback feasibility. Snapshot versions/digests and restart counts. Afterward verify migrations, containers/units, Asterisk, route targets, certificates, CTI/provisioning/reports/Satellite conditions, audit evidence, and rollback availability.

## Backup, restore, and node loss

Use NS8 backup/restore actions and documented UI workflows. Verify a recent usable backup, destination access, encryption-key custody, source module version, restore target node resources, user-domain dependency, and node-local proxy placement before starting.

For recovery after node loss:

1. Recover the NS8 cluster/destination configuration according to the administrator manual, then select the exact application backup and target node.
2. Ensure a compatible proxy exists on that target node before bringing NethVoice into service.
3. Let installed restore actions reconstruct databases, AstDB, environment, volumes, routes, and services. Do not replay hand-written SQL or copy another instance's dynamic ports.
4. Re-request/reassign Let's Encrypt certificates: application Let's Encrypt certificates are not restored with an application backup. Uploaded certificate behavior follows the restored node's Traefik backup/state.
5. Restore proxy routes/trunks only through installed actions. Serialize each route/trunk action; wait at least the installed restore delay (current source uses five seconds) before the next reload and verify Kamailio remains active/ready between operations. Never issue concurrent runtime reloads.
6. Verify every restored domain maps to the new node-local address and that instance's current Asterisk SIP port. Remove an old route only after proving no retained/restoring instance owns it and receiving approval.

## Certificate recovery

Determine which layer is broken and whether the certificate is requested, uploaded, node-local, or a container-imported copy. Prefer the installed certificate action/event or a narrowly scoped supported configuration action. Validate name assignment and expiry/state passively first; active handshakes require approval. Never display or copy a private key into command output. Certificate deletion/replacement can restart Traefik or telephony components and requires an impact window.

## Persistent proxy route repair

An unmatched route is only a candidate for cleanup. Check the full cluster inventory, node placement, preserved/restoring modules, the route's expected owner, and the current NethVoice host/port before declaring it stale. Save the single route through the installed read action, excluding descriptions or other tenant data, and prepare the exact inverse action. If removal is justified, inspect the installed `remove-route` schema/implementation, obtain explicit approval, run only that supported action, then validate persistent and Kamailio runtime state. Serialize it with any adjacent reload-producing action and observe the installed delay.

## Targeted service recovery

Prefer a supported health/recovery action. If none exists, discover the exact installed unit and dependency chain, capture bounded sanitized logs and restart counters, rule out an expected conditional inactive state, and obtain approval for that unit only. Apply the independent active-call gate when the unit is telephony-adjacent. In a confirmed rootless module context, the narrow fallback is `runagent -m "$mid" systemctl --user restart "$discovered_unit"`; do not substitute names from this document. Then verify dependencies, container identity, restart delta, application behavior and audit trail. Do not restart every service as diagnosis.

## Break glass: malformed empty-extension AstDB entry

Use only for the exact `AMPUSER` entry whose family/key represents an empty extension and `cidname`; do not dump the family or its values.

1. Confirm the installed Asterisk behavior/source and prove the exact key exists with a source-filtered count that emits only `0` or `1`.
2. Capture a protected AstDB backup or supported module backup, its hash, ownership/mode, and a rollback procedure without printing the entry value. Verify the count is exactly one.
3. Confirm active calls and obtain explicit approval for the exact Asterisk CLI deletion.
4. Delete only the confirmed family/key using the installed Asterisk database CLI; do not use SQL against AstDB. For versions whose installed CLI matches the recorded source, the exact mutation is `asterisk -rx 'database del AMPUSER/ cidname'`; execute it inside the discovered FreePBX container only after the approval above.
5. Re-run the count, check Asterisk health and affected behavior. Roll back from the protected value/backup only if verification fails; record and securely remove temporary rollback material when retention is no longer approved.

## Break glass: stale Kamailio runtime table

Use only when installed `list-routes`/`list-trunks` or version-confirmed PostgreSQL evidence proves persistent state is correct, while a version-confirmed passive Kamailio runtime view is stale.

1. Back up/export the affected persistent rows through the installed module mechanism; record counts and a hash, not trunk patterns or credentials.
2. Confirm Kamailio is otherwise healthy and active calls/impact are understood. Obtain explicit approval.
3. Prefer reapplying the exact supported route/trunk action. If it cannot safely be used, invoke only the installed-version-confirmed runtime reload command for the affected table. Recorded current source uses Kamailio RPCs `domain.reload`, `dialplan.reload`, and `dispatcher.reload`; do not assume all three, their order, or their wrapper on another installed version.
4. Serialize reloads. After each, verify Kamailio service/container readiness and route behavior; preserve at least the installed restore delay (five seconds in the recorded current source) before another reload of the same table.
5. If Kamailio destabilizes or persistent/runtime state diverges, stop, use the prepared rollback/recovery command, and do not continue through the route list.

## Break glass: version-confirmed SQL or file repair

This is a last resort when no supported action exists and installed source/schema proves the exact defect and repair.

- Obtain explicit approval for the exact statement/file, expected row/file count, impact and rollback.
- Make a protected backup; prove it can be read; record a sanitized location, hash, owner/mode and restore command.
- Capture before evidence with an exact predicate/hash. Require an expected row count (normally one) or exact original hash; abort on mismatch.
- For SQL, use a transaction and the least-privileged database/context. Show the reviewed literal statement with secrets redacted; never interpolate untrusted identifiers or values.
- For files, never edit generated FreePBX/Asterisk output. Work only on an installed-source-confirmed authoritative file, stage same-filesystem, preserve owner/mode/SELinux context, validate syntax, and atomically replace.
- Capture after count/hash and application verification. Keep an executable rollback command and test its precondition. No direct Redis write is permitted even under break glass.

## Rollback closure

State whether rollback was unused and remains viable, was executed and verified, or is retired after approved cleanup. Never claim rollback from the mere existence of a backup; verify its identity, scope, permissions, and restore preconditions.
