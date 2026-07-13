# NS8 security threat taxonomy & severity rubric

## Categories

| Tag | Meaning |
|-----|---------|
| `auth` | Authentication / authorization defects (JWT, login, authz bypass, 2FA) |
| `action-input` | Unvalidated / injectable input into action & event scripts |
| `redis-privilege` | Misuse of the privileged Redis boundary, ACL gaps, secret exposure via Redis |
| `api-moduled` | api-moduled handler injection, scope bypass, env leakage |
| `secrets` | Hardcoded/logged/leaked secrets, missing redaction |
| `proxy-trust` | X-Forwarded-For / trusted-proxy over-trust |
| `container` | Image hardening (delegated to nethserver-containerfile) |

## Severity rubric

Rate by **impact x reachability**, from the perspective of the lowest-privileged
actor who can trigger it.

- **critical** — unauthenticated or any-authenticated-user path to privilege
  escalation, remote code execution, secret disclosure, or full auth bypass.
  Example: forged input reaches a privileged Redis write; command injection in
  an api-moduled handler callable with an unscoped token.
- **high** — authenticated-user path to significant impact, or a missing
  control that removes a security boundary. Example: an action with no
  `validate-input.json` whose input reaches a shell; GET route exposing data
  that should be authorized.
- **medium** — requires unusual conditions or yields limited impact. Example:
  secret written to task output visible only to admins; over-broad
  `AMLD_EXPORT_ENV`.
- **low** — defense-in-depth gap, hard to exploit. Example: missing rate-limit
  where lockout exists elsewhere.
- **info** — hygiene / pointer (e.g. "review this Containerfile with
  nethserver-containerfile").

## Reachability qualifiers (record in `impact`)

- **unauth** — reachable without a token (`/api/login`, `http-basic` route,
  public Traefik route).
- **any-user** — reachable by any JWT holder (remember: all GET requests bypass
  api-server authorization).
- **priv** — requires leader/privileged agent context.
- **module-local** — only exploitable from inside the module boundary.
