---
name: nethserver-admin
description: Use when shell or SSH access to a NethServer 8 node is available and the agent must inspect, install, configure, update, remove, or troubleshoot NS8 modules, actions, containers, routes, logs, volumes, firewall, or service discovery.
version: 1.2.0
author: Kabutojira
license: GPLv3
metadata:
  hermes:
    tags: [ns8, nethserver8, ssh, api-cli, runagent, podman, systemd, journalctl, logcli, traefik, modules, diagnostics, sysadmin]
---

# NethServer 8 shell operations

Read the reference file for your task before running commands. Do not read all of them.

## Scope

Use this skill only after a target NS8 node is known and direct shell/SSH access is allowed. Prefer the NS8 operational surface (`api-cli`, `add-module`, `remove-module`, `runagent`, module actions, module-owned systemd units) over ad-hoc file edits.

Primary references:

- Dev manual: `https://nethserver.github.io/ns8-core/`
- Admin manual: `https://docs.nethserver.org/docs/administrator-manual`
- Module actions: `https://nethserver.github.io/ns8-core/modules/agent/`
- Rootless/rootfull: `https://nethserver.github.io/ns8-core/modules/rootless_rootfull/`
- Logs: `https://nethserver.github.io/ns8-core/core/logs/`
- Updates: `https://nethserver.github.io/ns8-core/modules/updates/`
- Traefik routes: `https://github.com/NethServer/ns8-traefik`
- NS8 diagnostic patterns: `https://github.com/Stell0/sysanal3`

## Safety rules

1. Verify host, user, OS, and cluster role before changes.
2. Inspect first; change only through the most specific supported action that addresses the task. Prefer a targeted action such as `set-route` or `set-certificate` over a broad action such as `configure-module` when both are available and the targeted action covers the required change.
3. Do not invent action names or JSON fields. Run `list-actions`, then inspect current config or module source.
4. Treat `remove-module --no-preserve`, manual volume deletion, Redis writes, and direct file edits as destructive.
5. For rootless modules, do not use `su`/SSH into the module user. Since Core 3.20 rootless users may have `/sbin/nologin`; use `runagent -m <module_id>`.
6. After every change, run the Post-change verification sequence below.
7. When editing action/event scripts, keep structured stdout clean. Send diagnostics to stderr: `echo "message" >&2`.

## Post-change verification

After every install, update, configure, restart, remove, route, certificate, or firewall change, verify the changed scope with this sequence:

1. Confirm the action or command exit code and stdout.
2. Check `get-configuration` when the module exposes it.
3. Check `get-status` for rootless modules, or the correct systemd unit status for rootfull modules.
4. Read `api-server-logs` or a short journal tail for the module.
5. Check the correct Podman context with `podman ps -a`.
6. For web apps, check route and certificate state.
7. Check the last API audit row when an API action changed state.

## Reference map

| Task | Read |
| --- | --- |
| Day-to-day operations: `api-cli`, `runagent`, `podman`, `systemctl`, `journalctl`, `redis-cli`, install/remove/update a module, configure a module, rootless vs rootfull, logs, containers/volumes/mounts, Traefik HTTP routes, issuing/replacing a certificate (`set-route`, `set-certificate`), service discovery/users/events/firewall | `references/operations.md` |
| Diagnostics and reporting: support bundle, health check, node identity/pressure, module inventory, container and unit health, read-only TLS expiry scan across endpoints, severe host log patterns, "the server is broken", troubleshooting sequence, report format | `references/diagnostics.md` |
| NethVoice / telephony issues: Asterisk, FreePBX, SIP, hairpin NAT, NethVoice proxy routes | `references/nethvoice.md` |
| CrowdSec issues: `cscli`, bans, decisions | `references/crowdsec.md` |

## Common errors to avoid

- Synthesizing undocumented `cluster/<action>` API action names instead of using the exact action names printed by `api-cli run list-actions`.
- Running root `systemctl --user` or root Podman against rootless modules.
- Hardcoding `/home/<module_id>`; custom home base paths and rootfull modules exist.
- Trusting `get-status` for rootfull modules; inspect system units/logs directly.
- Reconfiguring from memory instead of `get-configuration` output and action schema.
- Editing Redis or module files before reading logs and supported actions.
- Declaring success after an action returns without checking runtime state.
