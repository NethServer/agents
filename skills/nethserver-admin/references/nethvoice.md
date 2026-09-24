# NethVoice safe quick entry

This reference stops at safe NS8 discovery. Activate `nethvoice-admin` before any NethVoice SSH/shell command beyond the discovery below. If that skill is unavailable, stop and report the missing production operations layer; do not reconstruct telephony procedures from memory.

## Safe discovery

Confirm the host/node first, then list only module placement and version fields:

```bash
api-cli run get-cluster-status \
  | jq '{leader, nodes: [.nodes[] | {id, local, online}]}'
api-cli run list-installed-modules \
  | jq '[to_entries[] as $image | $image.value[]? | select(.module == "nethvoice" or .module == "nethvoice-proxy") | {id: .id, module: .module, source: .source, version: .version, node: .node}]'
```

For each exact local module ID, discover action names before inspecting an action or schema:

```bash
api-cli run module/<module_id>/list-actions | jq .
```

NethVoice depends on the proxy assigned to the same node. Each NethVoice host route must ultimately target that node's service-discovery address and the instance's dynamically allocated Asterisk SIP port. The dedicated skill owns the safe method for resolving and verifying this relationship.

After the dedicated skill is active, its allowlist-only `../../nethvoice-admin/scripts/collect_diagnostics.py` is the preferred quick topology check; it compares the discovered route without printing raw contacts, trunks, logs, or database rows.

Do not use this quick entry to print raw contacts/endpoints, call forwards, queue members, trunk patterns, log lines, database values, environment/password files, or customer identifiers. Do not perform DNS/SIP/RTP/TLS probes, test calls, traces, captures, debug toggles, service restarts, configuration, SQL, file edits, or Redis writes without the dedicated skill's preflight and approval gates.
