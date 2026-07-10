---
name: nethserver-threat-model
description: 'Map the security attack surface of a NethServer 8 target (ns8-core or an ns8-<app> module) before auditing it. Use when starting a security review, when the user asks to threat-model an NS8 module/core, or mentions "/threat-model". Produces THREAT_MODEL.md enumerating actions, api-moduled handlers, exposed routes/ports, Redis privilege usage, secret flows, and trust boundaries. First stage of the NS8 security audit harness (threat-model -> security-audit -> security-verify).'
---

# NethServer 8 Threat Model

## Overview

First stage of the NS8 security audit harness. Map the attack surface of a
target so the audit stage knows what to look at and the verify stage knows what
is reachable. Output is `THREAT_MODEL.md` in the target repo root.

Harness order: **nethserver-threat-model** -> nethserver-security-audit ->
nethserver-security-verify.

This skill is read-only. It inspects source; it does not modify the target.

## Step 1 — Detect target type

Decide `target_type` before anything else, because the surface differs:

- **core** — the checkout contains `core/api-server/` and `core/agent/`.
  This is the `ns8-core` repository.
- **module** — the checkout contains `imageroot/` and a top-level `AGENTS.md`
  but no `core/api-server/`. This is an `ns8-<app>` repository.

If neither matches, stop and tell the user the directory is not a recognizable
NS8 target.

Record the detected type; every later section is scoped by it. Read the
matching reference before enumerating:

- core -> `references/attack-surface-core.md`
- module -> `references/attack-surface-module.md`

## Step 2 — Enumerate the surface

Build these inventories. Use `rg`/`grep` and directory listing; do not guess.

### Actions (both types)
List every action directory under
`imageroot/var/lib/nethserver/{cluster,node,module}/actions/<name>/` (core) or
`imageroot/actions/<name>/` (module). For each, record:
- step scripts present (language),
- whether `validate-input.json` exists (missing = **unvalidated input entry
  point**, flag prominently),
- whether `validate-output.json` exists.

### api-moduled handlers (module, and core if present)
List `handlers/<name>/{post,get,...}` executables and note which carry
`validate-input.json`. Each handler is a code-execution entry point reached
over HTTP.

### Exposed routes / ports
- Traefik route definitions (`api-cli run list-routes` recipe is in the verify
  stage; here, read route config in source: look for `set-route`, Traefik
  labels, `org.nethserver.tcp-ports`/`udp-ports` in Containerfiles/services).
- Any `EXPOSE` / published ports in `Containerfile`s.

### Redis privilege boundary
Grep for every `redis_connect(privileged=True)` and every direct
`AGENT_COMMAND`/hget/hset on `secrets/*` or credential keys. List file:line.
Privileged connections are the highest-value boundary in NS8.

### Secret flows
Enumerate where secrets originate, transit, and rest:
- env vars named `*_PASSWORD`, `*_SECRET`, `*_TOKEN`, `*_KEY`,
- Redis keys under `module/*/secrets`, `cluster/*`,
- files written under `state/` or volumes.

### Trust boundaries
Summarize who can reach what: unauthenticated HTTP (`/api/login`,
`http-basic` routes), authenticated-but-any-user (JWT holders), privileged
(leader/root agent), module-local.

## Step 3 — Write THREAT_MODEL.md

Structure:

```markdown
# Threat Model: <target name> (<core|module>)

## Trust boundaries
<bullet list: actor -> what they can reach>

## Entry points
### Actions
| Action | Scope | validate-input.json | Notes |
### api-moduled handlers
| Handler | Method | validate-input.json | Notes |
### Routes / ports
| Route/Port | Auth | Notes |

## Privileged operations
| Location (file:line) | Operation | Why privileged |

## Secret flows
| Secret | Origin | Transit | At rest |

## Highest-risk areas (ranked)
1. ...
```

`THREAT_MODEL.md` feeds `nethserver-security-audit` directly — every entry
point and privileged operation listed here must be examined by the audit
stage.

## Handoff

When done, tell the user: threat model written to `THREAT_MODEL.md`, and the
next step is `nethserver-security-audit` scoped by it.
