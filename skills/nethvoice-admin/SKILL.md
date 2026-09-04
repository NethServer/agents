---
name: nethvoice-admin
description: Use when a production NS8 task concerns NethVoice, ns8-nethvoice, ns8-nethvoice-proxy, NethCTI, or their SIP/RTP path.
license: GPLv3
metadata:
  version: 0.1.1
  author: NethServer project contributors
  hermes:
    tags: [nethvoice, ns8, production, voip, sip, rtp, asterisk, freepbx, kamailio, nethcti]
---

# NethVoice production administration

Use this skill as the NethVoice layer on top of `nethserver-admin`. Read only the references needed for the incident.

## Foundation gate

Before SSH, shell, `api-cli`, `runagent`, or any NS8 operation:

1. Activate `nethserver-admin` and follow its target, access, action-discovery, logging, and post-change rules.
2. If `nethserver-admin` is unavailable or cannot be loaded, stop safely. Report that the required NS8 operations layer is missing; do not improvise commands from this skill.
3. Confirm the user has authorized access to the named production system. Diagnosis authorization does not imply permission to change it.

## Source precedence

Resolve conflicts in this order:

1. Installed action list, installed input/output schemas, installed scripts, and observed runtime state.
2. Source at the exact installed image version or digest.
3. Current `ns8-nethvoice` and `ns8-nethvoice-proxy` source.
4. NethVoice and NS8 administrator documentation.

Record the installed versions and the source revision consulted. Never guess an action name, JSON field, service/container name, port, path, database schema, or expected unit state.

## Production workflow

- Begin read-only. Identify the failing layer before requesting a change.
- Before every change, establish the exact host, node ID, NethVoice and proxy module IDs, installed versions, incident scope and timeline, independently verified active-call state, maintenance constraints, expected impact, rollback, and verification plan.
- Obtain explicit approval for the exact mutation and impact window. Also obtain explicit approval that names the scope and impact window before test calls, SIP/RTP/TLS probes, traces, packet capture, debug logging, service restarts, or any operation that can create traffic, expose communications data, or disturb calls.
- Treat broad configuration, CTI/integration, and rebranding actions as potentially telephony-restarting even when their names sound narrow. Inspect the installed action implementation first.
- Prefer the narrowest supported installed action. Use a break-glass procedure only when its stated preconditions are all proven and no supported action covers the repair.
- Never write NS8 Redis directly, run speculative SQL, edit generated FreePBX/Asterisk configuration, dump secrets, or place an outgoing call without approval.

## Reference map

| Need | Read |
| --- | --- |
| Components, node-local proxy topology, dependencies, dynamic ports, routes, certificates, expected and conditional services | `references/architecture.md` |
| Symptom-led diagnosis for registration, trunks, calls, audio/RTP, WebRTC, CTI, Janus, Tancredi, reports, Satellite, LDAP, databases, certificates, or NAT; bounded logs | `references/diagnostics.md` |
| Configuration, upgrade, backup/restore, certificate or service recovery, rollback, active-call gates, and all break-glass work | `references/repair-and-lifecycle.md` |
| Any logs, databases, traces, recordings, transcripts, credentials, API keys, integrations, or customer-identifying evidence | `references/sensitive-data.md` |

Use `scripts/collect_diagnostics.py` for a passive, aggregate-first local snapshot when appropriate. It is not a repair tool and is not a substitute for installed action/schema discovery.

## Required completion

After every change, verify and report all applicable items: service and container state plus restart counts; NethVoice-to-proxy routes; certificate assignment/state; Asterisk process/version/uptime; independently queried active calls and channels; the affected application behavior; NS8 audit evidence; and whether rollback is still available, was used, or was retired. A successful action exit code alone is not success.

End diagnosis or change work with an incident record containing: target and installed versions; authorized scope and impact window; sanitized timeline; evidence and source provenance; actions/commands and approvals; changes or an explicit “none”; verification results; sensitive-data handling; remaining risk; and rollback status.
