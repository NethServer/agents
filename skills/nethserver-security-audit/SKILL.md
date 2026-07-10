---
name: nethserver-security-audit
description: 'Audit a NethServer 8 target (ns8-core or an ns8-<app> module) for NS8-specific security defects: auth/authorization bypass, unvalidated action input, Redis privilege leaks, api-moduled handler injection, secret mishandling, and proxy/XFF trust. Use when the user asks for a security audit/review of NS8 code, or mentions "/security-audit". Produces FINDINGS.json + FINDINGS.md. Second stage of the NS8 security audit harness; consumes THREAT_MODEL.md when present, feeds nethserver-security-verify.'
---

# NethServer 8 Security Audit

## Overview

Second stage of the NS8 security audit harness. Statically audit the target for
NS8-specific security defects and emit machine-readable findings that the
verify stage can confirm against a live node.

Harness order: nethserver-threat-model -> **nethserver-security-audit** ->
nethserver-security-verify.

This skill is read-only on the target. It reads code; it does not modify it.

## Inputs

- The target checkout (ns8-core or an ns8-module).
- `THREAT_MODEL.md` if present (from `nethserver-threat-model`). If absent, run
  `nethserver-threat-model` first, or proceed and scope from the code directly
  — but say so in the report.

## Step 1 — Seed with the anti-pattern scanner

Run the deterministic grep-seeder to get a candidate list. It is a recall
floor, not the audit itself — it produces `file:line` leads, never verdicts.

```bash
bash scripts/scan-antipatterns.sh <target-dir>
```

Treat every hit as a lead to investigate by reading the surrounding code. Do
not report a scanner hit as a finding without reading and confirming it.

## Step 2 — Audit each domain (fan out in parallel)

Six domains, each with a reference checklist. **Dispatch one subagent per
domain in parallel** (like a parallel-worker code review); each subagent reads
its checklist, examines the relevant entry points from the threat model, and
returns findings in the schema below. If not running subagents, work the
domains sequentially.

| Domain | Checklist | Category tag |
|--------|-----------|--------------|
| Auth / authorization | `references/checks-auth.md` | `auth` |
| Action / event input | `references/checks-action-input.md` | `action-input` |
| Redis privilege | `references/checks-redis.md` | `redis-privilege` |
| api-moduled handlers | `references/checks-api-moduled.md` | `api-moduled` |
| Secrets & proxy trust | `references/checks-secrets.md` | `secrets` / `proxy-trust` |
| Containers | (delegate) | `container` |

Severity rubric lives in `references/taxonomy.md`. Container findings: do not
re-derive image rules — cross-reference the `nethserver-containerfile` skill
and record a single pointer finding per Containerfile that needs its review.

## Step 3 — Every finding needs a verify_hint

A finding is only useful if the verify stage can test it. For each finding,
write a `verify_hint`: a concrete, **read-only** probe against a live node that
would confirm or refute it (e.g. an `api-cli`/curl call and the expected
result). If a finding is not live-testable (pure code-quality), say so in the
hint: `"static-only: <reason>"`.

## Step 4 — Emit findings

Write two files to the target root.

### FINDINGS.json
Array of objects, this exact schema:

```json
{
  "id": "NS8-AUTH-001",
  "category": "auth|action-input|redis-privilege|api-moduled|secrets|proxy-trust|container",
  "severity": "critical|high|medium|low|info",
  "title": "short imperative title",
  "location": {"file": "relative/path.go", "line": 42},
  "target_type": "core|module",
  "evidence": "code excerpt or exact pattern matched",
  "impact": "what an attacker gains, concretely",
  "verify_hint": "read-only probe + expected result, or 'static-only: reason'",
  "status": "unverified"
}
```

ID scheme: `NS8-<CATEGORY-ABBR>-<NNN>`, e.g. `NS8-AUTH-001`,
`NS8-REDIS-002`, `NS8-AMLD-001`, `NS8-INPUT-003`, `NS8-SECRET-001`,
`NS8-PROXY-001`.

### FINDINGS.md
Human summary: counts by severity, then one section per finding
(id, severity, location, impact, verify_hint). Order critical -> info.

## Step 5 — Handoff

Report to the user: N findings by severity, and that the next step is
`nethserver-security-verify` against a live node to confirm them. State clearly
that findings are `unverified` until the verify stage runs.

## Rules

- No false confidence: only report what you read and understood. Rank by
  severity honestly; do not pad.
- Never modify the target during the audit.
- Prefer precise `file:line`. If a finding spans a pattern, cite the primary
  site.
