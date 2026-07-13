# Attack surface — ns8-core

Reference for threat-modeling the `ns8-core` repository. Facts below are drawn
from the component `AGENTS.md` files; verify against the actual checkout, code
evolves.

## core/api-server (Go / Gin)

Admin REST API serving the UI.

- **Auth**: Redis-ACL credentials validated on `POST /api/login`. JWT issued,
  14-day expiry, signed with the `SECRET` env var. JWT claims carry username +
  2FA flag; `role`/`actions` claims are placeholders — real authorization is
  fetched fresh from Redis per request.
- **Authorization**: action-based, `filepath.Match` wildcard patterns against
  the user's authorized-actions list. **All GET requests bypass the authorizer
  entirely** — treat every GET route as reachable by any authenticated user.
- **2FA**: optional TOTP; enforced at login. `/api/2FA` POST/DELETE are
  explicitly exempted in the authorizer.
- **Redaction**: `SENSITIVE_LIST` env names values redacted from logs/audit.
- **Trusted proxy / XFF**: api-server sits behind a proxy; check how
  `X-Forwarded-For` and trusted-proxy CIDRs are configured. Over-trusting all
  proxies means a forged `X-Forwarded-For` is logged/acted-on verbatim.
- **Config**: env only — `LISTEN_ADDRESS`, `REDIS_ADDRESS`, `REDIS_USER`,
  `REDIS_PASSWORD`, `SECRET`, `STATIC_PATH`, `AUDIT_FILE`, `SENSITIVE_LIST`,
  `ISSUER`.
- **Routes without JWT**: `POST /api/login`, `POST /api/logout`,
  `GET /api/module/:module_id/http-basic/:action` (basic auth).
- **WebSocket** `/ws`: auth via an `authorize` action carrying the JWT payload;
  session JWT expiry re-checked on ping-pong.

Files: `api-server.go` (routes/middleware wiring), `methods/auth.go`,
`middleware/` (authenticator/authorizer/payload), `socket/`, `audit/`.

## core/api-moduled (Go)

Generic per-module HTTP API. Wraps on-disk executables with JWT + JSON Schema.

- **Handlers are directories**: `POST /api/<h>` executes `handlers/<h>/post`
  with JSON on stdin, JSON expected on stdout. Any executable can be a handler
  — command-injection surface if handler passes input to a shell.
- **Env injected into handlers**: `JWT_ID`, `JWT_CLAIMS` (full claims JSON),
  and any names listed in `AMLD_EXPORT_ENV`. Over-broad `AMLD_EXPORT_ENV` leaks
  host secrets into handler processes.
- **JWT scope claim**: optional array of allowed handler names. **Absent scope
  = unrestricted token** (can call any handler); present-but-empty = none.
- **Secret**: `AMLD_JWT_SECRET` must be set (empty = broken/insecure auth).
- **Login**: `handlers/login/post` returns claims incl. `uid`; exit 2-7 = bad
  creds, 1 or 8+ = internal error.

Files: `api-moduled.go`, `validation/validation.go`.

## core/agent (Go)

Reads tasks from Redis, executes action step scripts sequentially on behalf of
cluster/node/module. The agent is the executor of every action — the trust of
an action equals the trust of the agent running it (leader/root vs module
user).

## core/imageroot (Python / Bash)

Cluster + node action scripts and the `agent` Python package
(`usr/local/agent/pypkg/agent/`). Key APIs: `redis_connect(privileged=...)`,
`set_env`, `run_helper`, `agent.tasks.run/runp`. See the audit stage
`checks-action-input.md` and `checks-redis.md`.

## core/ui (Vue 2)

JWT stored client-side; WebSocket task/event model. XSS and token-handling
surface, lower priority than the API/action layers.
