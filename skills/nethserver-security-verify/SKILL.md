---
name: nethserver-security-verify
description: 'Validate NS8 security audit findings against a live NethServer 8 cluster node. Use after nethserver-security-audit, when the user asks to confirm/verify findings on a real node, or mentions "/security-verify". Reads FINDINGS.json, runs read-only probes via api-cli/runagent/podman/curl on the leader, and classifies each finding as confirmed/not-reproducible/not-applicable in VERIFIED.md. Third stage of the NS8 security audit harness. Read-only by default; mutations require explicit opt-in.'
---

# NethServer 8 Security Verify

## Overview

Third and final stage of the NS8 security audit harness. Take the static
findings and confirm which are actually reproducible on a running cluster, so
the team acts on real issues, not on plausible-but-wrong ones.

Harness order: nethserver-threat-model -> nethserver-security-audit ->
**nethserver-security-verify**.

## Step 0 — Request live-node access (do this first)

Verification quality is **materially better with a live node.** Before doing
anything else, ask the user for access and tell them why:

> "To verify these findings properly I need SSH / `api-cli` access to a live
> NS8 leader node (a test/staging cluster, not production). With it I can run
> read-only probes that confirm each finding is actually reproducible. Without
> it I can only reason statically and every finding stays 'unverified'. What
> node can I use, and how do I reach it (SSH host/user, or an `api-cli` login)?"

Prefer a **test/staging** node — verification touches auth and input paths.
If a default target is configured (e.g. `rl1.leader.default.gs.nethserver.net`),
name it and confirm it is safe to probe before using it.

If the user declines or has no node: proceed in **static mode** — reason about
reachability from the code, mark findings `unverified (no live node)`, and say
in the report that live confirmation was not performed.

## Step 1 — Preflight (reuse nethserver8 safety rules)

On the target node, before probing:

- Verify host identity, OS, and **cluster role**; confirm it is the leader (or
  connect to the leader) — `api-cli run get-cluster-status | jq .leader`.
- Confirm this is the intended (ideally non-production) node.
- Ensure `api-cli` works: `api-cli login` if a 401 is returned.
- Never `su`/SSH into a rootless module user; use `runagent -m <module_id>`.

## Step 2 — Verify each finding (READ-ONLY)

Load `FINDINGS.json`. For each finding, use its `verify_hint` and the recipes
in `references/probes.md`. The helper `scripts/live-probe.sh` bundles the common
read-only probes.

Classify each finding:

- **confirmed** — the probe reproduced the issue. Record exact command +
  observed result in `verify_evidence`.
- **not-reproducible** — probe ran, issue did not manifest (control present,
  input rejected, route denied). Record what happened.
- **not-applicable** — finding does not apply to this deployment (feature not
  installed, path unreachable).
- **unverified** — could not test (no live node, or `static-only` hint).

### Read-only discipline (non-negotiable)

- Default mode makes **no state changes**: no `add-module`, `remove-module`,
  `update-module`, no Redis writes, no file edits, no user/password changes.
- Probes are limited to: `list-*`/`get-*` actions, reading task output,
  `redis-cli --scan`/read commands via `runagent`, `podman top`/`inspect`,
  `curl` GET / a single failed-auth POST, `journalctl` reads.
- **Do not brute-force** `/api/login`. A single failed login to check
  audit-log IP recording is acceptable only after confirming no lockout risk.
- Any state-changing probe requires explicit user opt-in (`--allow-mutations`)
  AND you must list each mutation and get confirmation before running it.
- Keep structured stdout clean; send diagnostics to stderr.

## Step 3 — Write VERIFIED.md and update FINDINGS.json

- Rewrite each finding's `status` in `FINDINGS.json`, add `verify_evidence`.
- Write `VERIFIED.md`: summary table (id, severity, status), then per-finding
  detail with the probe command and observed result. Order confirmed-critical
  first.

## Step 4 — Report

Tell the user: X confirmed, Y not-reproducible, Z not-applicable, W unverified.
Lead with confirmed criticals/highs — those are the actionable set. If run in
static mode, state that plainly.
