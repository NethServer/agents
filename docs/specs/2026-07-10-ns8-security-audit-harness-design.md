# NS8 Security Audit Harness — Design

Date: 2026-07-10
Status: Approved (brainstorming), pending implementation plan
Target repo: `nethserver/agents` (adds 3 skills alongside existing 5)

## Goal

A set of Claude Code skills that **audit** an existing NethServer 8 target
(ns8-core **or** any `ns8-<app>` module) for NS8-specific security defects,
then **validate** findings against a live cluster node. Defensive security,
skills-first, matching the `nethserver/agents` `SKILL.md` convention.

Non-goals: design-time authoring guidance, C/C++ memory-bug fuzzing, a
heavyweight Python orchestrator/sandbox pipeline. Container-image hardening is
delegated to the existing `nethserver-containerfile` skill (cross-referenced,
not duplicated).

## NS8 attack surface (what the harness reasons about)

Derived from `ns8-core` component `AGENTS.md` files and module conventions.

- **api-server** (Go/Gin): 14-day JWT with `SECRET` env key; Redis-ACL login;
  action-based authz via `filepath.Match` wildcards; **all GET requests bypass
  authorization**; optional TOTP 2FA enforced at login; `SENSITIVE_LIST`
  redaction; SQLite audit log; WebSocket JWT validation on ping-pong; trusted
  proxy / `X-Forwarded-For` handling.
- **api-moduled** (Go): filesystem handlers (`handlers/<name>/post`) executed
  with JSON on stdin and `JWT_ID` / `JWT_CLAIMS` env injected; **scope claim
  absent = unrestricted token**; `AMLD_JWT_SECRET` must be set;
  `AMLD_EXPORT_ENV` leaks host env into handlers. Command-injection and
  scope-bypass surface.
- **actions / imageroot** (Python/Bash): numbered step scripts run by the Go
  agent; missing `validate-input.json` = unvalidated stdin; injection via
  `run_helper` / `agent.tasks.run(p)` / subprocess; `redis_connect(privileged=
  True)` privilege boundary; secrets stored in Redis.
- **containers**: rootless / pinned / no-secrets-in-layers — delegated to
  `nethserver-containerfile`.
- **live node**: JWT rotation, `/api/login` rate-limiting, 2FA enforcement,
  Redis ACL reachability, exposed ports / Traefik routes, actual rootless
  container user.

## Architecture — three-stage skill harness

Mirrors the `threat-model → scan → verify` arc of Anthropic's defending-code
harness, but skills-only and NS8-native.

```
nethserver-threat-model  →  THREAT_MODEL.md
        │
        ▼
nethserver-security-audit →  FINDINGS.json + FINDINGS.md
        │
        ▼
nethserver-security-verify → VERIFIED.md   (needs live node)
```

Each stage is one skill with a single responsibility, communicating through
on-disk artifacts. Stages are independently runnable (verify accepts any
`FINDINGS.json`).

## Repository layout

```
skills/
  nethserver-threat-model/
    SKILL.md
    references/
      attack-surface-core.md      # api-server/agent/api-moduled surfaces
      attack-surface-module.md    # actions, handlers, routes, images
  nethserver-security-audit/
    SKILL.md
    references/
      taxonomy.md                 # NS8 threat categories + severities
      checks-auth.md              # JWT, authz wildcard, GET-bypass, 2FA, scope
      checks-action-input.md      # validate-input.json, injection sinks
      checks-redis.md             # privileged=True, ACL, secret keys
      checks-api-moduled.md       # handler exec, scope, env injection
      checks-secrets.md           # hardcoded, logs, SENSITIVE_LIST, XFF/proxy
    scripts/
      scan-antipatterns.sh        # grep/rg seeds -> candidate file:line list
  nethserver-security-verify/
    SKILL.md
    references/
      probes.md                   # api-cli/runagent/podman/curl recipes
    scripts/
      live-probe.sh               # read-only leader probes
README.md                         # add 3 skills to the skills table
```

## Findings schema (contract: audit -> verify)

`FINDINGS.json` — array of objects:

```json
{
  "id": "NS8-AUTH-001",
  "category": "auth|action-input|redis-privilege|api-moduled|secrets|proxy-trust|container",
  "severity": "critical|high|medium|low|info",
  "title": "GET route bypasses action authorization",
  "location": {"file": "core/api-server/middleware/authorizer.go", "line": 42},
  "target_type": "core|module",
  "evidence": "code excerpt",
  "impact": "what an attacker gains",
  "verify_hint": "curl GET /api/... as low-priv user; 200 = confirmed",
  "status": "unverified"
}
```

The verify stage rewrites `status` to `confirmed | not-reproducible |
not-applicable`, adds `verify_evidence`, and emits `VERIFIED.md`.

## Skill responsibilities

### nethserver-threat-model
Detect target type (core = presence of `core/api-server`; module = `imageroot/`
+ module `AGENTS.md`). Enumerate: actions and which carry `validate-*.json`,
api-moduled handlers, Traefik routes / exposed ports, every
`redis_connect(privileged=True)`, secret env / Redis keys, trust boundaries.
Output `THREAT_MODEL.md`.

### nethserver-security-audit
Load the threat model, run `scan-antipatterns.sh` for deterministic seeds, then
work each `checks-*.md` domain. **Fans out one subagent per domain, in
parallel** (matches trailofbits `c-review`). Each check = pattern +
why-it-matters + severity + `verify_hint`. Emit `FINDINGS.json` + `FINDINGS.md`.
Container findings cross-reference `nethserver-containerfile`.

### nethserver-security-verify
Inputs: `FINDINGS.json` + a live leader host. **The skill asks the user for
live-node SSH/`api-cli` access up front and states that verification quality is
materially better with it**; without access it degrades to static
reachability reasoning and marks findings `unverified (no live node)`. Per
finding with a `verify_hint`, run the read-only probe via
`api-cli` / `runagent` / `podman top` / curl-Traefik, confirm reachability and
reproduction, write `VERIFIED.md`. Inherits `nethserver8` skill safety rules.

## Live-node safety (non-negotiable)

- Default **read-only**: no `add/remove/update-module`, no Redis writes, no
  file edits.
- Any state-changing probe requires explicit `--allow-mutations` and must name
  each mutation before running it.
- Preflight: verify host, cluster role, and leader before probing (reuse
  `nethserver8` safety rules).
- Structured stdout kept clean; diagnostics to stderr.

## Decisions

- Audit fans out parallel per-domain subagents. (yes)
- Ship `scan-antipatterns.sh` grep-seeder as a deterministic recall floor
  alongside LLM analysis. (yes)
- Verify skill proactively requests live-machine access. (yes)

## Testing / acceptance

- **Static**: run the audit against this `ns8-core` checkout and against one
  module (`ns8-nethvoice`); it must flag the known `X-Forwarded-For` /
  trusted-proxy finding and the GET-request-bypasses-authorization behavior.
- **Live**: run verify against `rl1.leader.default.gs.nethserver.net`,
  read-only, confirming probes execute and classify findings without any
  mutation.
