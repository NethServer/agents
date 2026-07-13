# NethServer Coding Agent Skills

A collection of coding agent skills tailored to [NethServer](https://github.com/NethServer) development guidelines.
These skills are derived from the [NethServer Development Handbook](https://nethserver.github.io/dev/).

## Available skills

Skills are saved under the `skills` directory.

## Usage

Invoke a skill by name in your Agent chat session:

```
/nethserver-containerfile
/nethserver-pr
/nethserver-issue
/nethserver-release
/conventional-commit
/nethserver-threat-model
/nethserver-security-audit
/nethserver-security-verify
```

Or reference it naturally:

> "Review this Dockerfile using the nethserver-dockerfile skill"  
> "Help me open a PR with nethserver-pr"

## NS8 security audit harness

Three skills form a defensive-security pipeline for auditing `ns8-core` or any
`ns8-<app>` module and validating findings against a live cluster node:

1. **`/nethserver-threat-model`** — map the attack surface (actions,
   api-moduled handlers, exposed routes/ports, Redis privilege usage, secret
   flows, trust boundaries). Produces `THREAT_MODEL.md`.
2. **`/nethserver-security-audit`** — static audit scoped by the threat model,
   covering auth/authorization, action/event input validation, the Redis
   privilege boundary, api-moduled handler injection, secrets, and
   proxy/X-Forwarded-For trust. Produces `FINDINGS.json` + `FINDINGS.md`.
3. **`/nethserver-security-verify`** — confirm each finding against a live NS8
   leader with **read-only** probes (`api-cli`/`runagent`/`podman`/`curl`).
   Produces `VERIFIED.md`. Requests live-node access up front; degrades to
   static reasoning without it. No state changes unless explicitly authorized.

Run them in order, or run any stage standalone (verify consumes any
`FINDINGS.json`). Container-image hardening is delegated to
`/nethserver-containerfile`.
