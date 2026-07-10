# Checks — api-moduled handlers (`api-moduled`)

Scope: modules (and core) that run `api-moduled`. Handlers are on-disk
executables reached over HTTP: `POST /api/<h>` -> `handlers/<h>/post`, JSON on
stdin, JSON on stdout. Known users: ns8-samba, ns8-openldap self-service
portals.

## M1. Command injection in handlers
The handler is an arbitrary executable. If it passes stdin fields to a shell,
to `ldapmodify`/`smbpasswd`/`useradd`, or builds commands by string
interpolation, unvalidated input = code execution as the module user.
- Confirm each handler validates input (`validate-input.json`) AND quotes/uses
  argument arrays rather than shell strings.
- Severity: critical if reachable with an unscoped token (see M3); high
  otherwise.
- verify_hint: on a test node, POST a benign injection marker to the handler,
  observe rejection or safe handling.

## M2. Missing input schema on a handler
Handler directory without `validate-input.json` = unvalidated HTTP input
straight into the executable. Same weight as action I1 but higher reachability
(direct HTTP).
- Severity: high (critical if the handler reaches a shell).
- verify_hint: POST unexpected JSON, expect pre-exec rejection.

## M3. Scope claim absent = unrestricted token
api-moduled JWT `scope` is an optional array of allowed handler names.
**Absent scope = the token may call ANY handler.** If the login handler issues
tokens without a scope claim, every authenticated user can invoke every handler
including privileged ones.
- Confirm `handlers/login/post` sets a least-privilege `scope`.
- Severity: high/critical.
- verify_hint: obtain a token via login, decode it, check for a `scope` claim;
  attempt a handler not intended for that user, expect 403.

## M4. Over-broad AMLD_EXPORT_ENV
`AMLD_EXPORT_ENV` names host env vars exported into every handler process.
Listing secrets (DB passwords, JWT secret) here leaks them to all handlers,
widening the impact of M1.
- Severity: medium; high if a secret is exported and a handler is
  injection-prone.
- verify_hint: static-only (inspect the api-moduled unit/env config).

## M5. Empty / weak AMLD_JWT_SECRET
`AMLD_JWT_SECRET` must be set. Empty = broken auth (unsigned/forgeable tokens).
- Severity: critical.
- verify_hint: static-only; confirm the env is set from a generated secret, not
  a default.

## M6. Output leakage
Handler stdout is the HTTP response body. Secrets or internal errors written to
stdout are returned to the caller. Missing `validate-output.json` lets
unexpected fields (incl. secrets) pass through.
- Severity: medium-high.
