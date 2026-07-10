# Checks — authentication & authorization (`auth`)

Scope: `core/api-server` (Go), the UI JWT handling, and any module that issues
or validates tokens. Modules without their own API can skip most of this.

## A1. GET requests bypass authorization
api-server applies the authorizer only to non-GET methods. **Every GET route is
reachable by any authenticated user regardless of their authorized-actions
list.** Audit each GET route: does it return data or trigger behavior that
should be action-authorized? A GET that leaks another module's task
context/output, node data, or audit records is a finding.
- Pattern: GET route in `api-server.go` returning sensitive data; authorizer in
  `middleware/` short-circuiting on `c.Request.Method == "GET"`.
- Severity: high if it exposes cross-tenant/cross-module data; medium otherwise.
- verify_hint: `api-cli login` as a low-privilege user, `curl` the GET route,
  expect 200 with data = confirmed.

## A2. Authorization wildcard over-match
Authz uses `filepath.Match` against authorized-action patterns. A pattern like
`*` or `module/*` may grant more than intended. Check how patterns are stored
and whether any default/role grants broad wildcards.
- Severity: high if a low-priv role gets a broad wildcard.
- verify_hint: authorize a restricted user, attempt a non-listed action,
  expect 403.

## A3. JWT secret handling
`SECRET` (api-server) / `AMLD_JWT_SECRET` (api-moduled) sign the JWT.
- Empty/default/hardcoded secret = critical (token forgery).
- Secret logged or echoed = high.
- Check secret is loaded from env, never committed, sufficient length.
- verify_hint: static-only (cannot read prod secret); confirm code path.

## A4. JWT expiry / rotation
api-server JWT is 14 days; api-moduled default 4h. Long expiry with no
revocation is a design risk. Check: is there logout/token invalidation? Are
expired tokens rejected on WebSocket ping-pong (should be)?
- Severity: medium (long-lived tokens), low if revocation exists.

## A5. 2FA enforcement gaps
TOTP 2FA is enforced at login when enabled. Check the authorizer exemptions
(`/api/2FA` POST/DELETE are intentionally exempt) are not broader than needed,
and that a partially-authenticated (pre-2FA) token cannot call other routes.
- Severity: high if a pre-2FA token reaches protected routes.
- verify_hint: enable 2FA on a test user, attempt an action with the pre-OTP
  token, expect rejection.

## A6. Unauthenticated routes
`POST /api/login`, `POST /api/logout`, and
`GET /api/module/:id/http-basic/:action` need no JWT. Verify the http-basic
route validates basic-auth credentials and cannot be used to reach arbitrary
actions.
- Severity: high if http-basic reaches unintended actions.
- verify_hint: curl the http-basic route with no/invalid creds, expect 401.

## A7. Rate limiting on login
Is `/api/login` rate-limited / lockout-protected? Absence enables brute force.
- Severity: medium (low if fail2ban/edge protection is documented).
- verify_hint: (read-only, do NOT brute force prod) confirm middleware presence
  in code; note as static-only unless a safe single-probe exists.
