# Checks — secrets & proxy trust (`secrets`, `proxy-trust`)

Scope: both core and modules.

## Secrets (`secrets`)

### S1. Hardcoded credentials
Grep for secrets committed in source: passwords, API keys, private keys, tokens
in `.py`/`.sh`/`.go`/`.json`/`.env` and Containerfiles.
- Pattern: `password =`, `secret =`, `-----BEGIN * PRIVATE KEY-----`,
  high-entropy string literals, `ARG`/`ENV` with secret-looking names.
- Severity: critical if a real credential; info for obvious placeholders.
- verify_hint: static-only.

### S2. Secrets in logs / task output
Secrets written to stdout (task output, stored in Redis, API-readable), to
`journalctl`, or to log files. See I4/M6.
- api-server has `SENSITIVE_LIST` to redact values from audit/logs — check
  every secret env name is listed there.
- Severity: high if secret reaches API-readable output; medium for logs.
- verify_hint: trigger the action/handler on a test node, read task output/log,
  confirm redaction.

### S3. Secrets baked into container layers
Defer to `nethserver-containerfile`. Emit an `info` pointer finding per
Containerfile that copies `.env`/keys or sets secret `ARG`/`ENV`.

### S4. Missing SENSITIVE_LIST coverage
api-server redacts only the env names listed in `SENSITIVE_LIST`. A new secret
env not added there is logged in cleartext.
- Severity: medium.
- verify_hint: static-only (cross-check secret env names vs SENSITIVE_LIST).

## Proxy trust (`proxy-trust`)

### P1. Over-trusted X-Forwarded-For
api-server sits behind a proxy. If it trusts all proxies
(e.g. Gin `SetTrustedProxies(nil)` / trusting `0.0.0.0/0`), a client-supplied
`X-Forwarded-For` is accepted verbatim — the audit log records an
attacker-chosen client IP, and any IP-based logic is spoofable.
- Pattern: `SetTrustedProxies`, `TrustedPlatform`, `X-Forwarded-For` /
  `X-Real-IP` handling; trusting the full range or not restricting to the known
  proxy CIDR.
- Severity: medium (log integrity / spoofed source IP); high if any
  authorization or rate-limit decision keys on the client IP.
- verify_hint: `curl -H 'X-Forwarded-For: 1.2.3.4' https://<leader>/api/login`
  with bad creds, then check the audit log records `1.2.3.4` = confirmed
  forgery. (Read-only: a single failed login is non-destructive; confirm rate
  limits first.)

### P2. Trusting X-Forwarded-Host / -Proto for redirects or links
Reflected forwarded headers used to build URLs (password-reset links, CORS,
redirects) enable host-header injection.
- Severity: medium-high depending on use.
- verify_hint: probe with a spoofed `X-Forwarded-Host`, inspect any generated
  URL.
