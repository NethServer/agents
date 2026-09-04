# api-server and api-moduled internals

Beyond the routes and configuration listed in `core/api-server/AGENTS.md`:

- Authentication is a Redis ACL credential check at login, optionally followed by
  TOTP. The issued JWT carries only the username and the 2FA flag — no roles, no
  action list. Permissions are re-read from Redis on every request by the identity
  handler, so a revoked grant takes effect without waiting for token expiry.
- Authorization is action-based, not role-based. The requested action is matched
  against the user's authorized action patterns with `filepath.Match`, in both
  `core/api-server/middleware/middleware.go` and `core/api-server/methods/auth.go`.
  GET requests bypass the authorization check — as does `POST /api/2FA`. The GET
  exemption carries a `TODO` in `middleware.go`, so treat it as provisional rather
  than as a guarantee to build on.
- The audit log is a SQLite database in WAL mode. Three action names are recorded:
  `login-ok`, `auth-fail` and `create-task` (`core/api-server/methods/audit.go` and
  `core/api-server/methods/tasks.go`).
- The WebSocket bridge is Melody. It subscribes to `progress/*` with `PSubscribe`
  and relays every message to connected clients
  (`core/api-server/socket/socket.go`). Clients authenticate by sending an
  `authorize` socket action carrying the JWT. `socket.go` calls `melody.New()` and
  overrides none of its configuration, so the library's own defaults — frame size
  ceiling included — are what apply. The frame protocol itself — `logs-start`,
  `logs-stop`, task events, with their JSON payloads — is written down in
  `core/api-server/README.md`, not in `docs/`.
- Task queues and result keys are the ones in `references/actions-and-agent-sdk.md`: `cluster/tasks`,
  `node/<id>/tasks`, `module/<id>/tasks`, and `task/<agent>/<task-id>/…`.

api-moduled is a different animal. It has no Redis client, no audit database and no
WebSocket. Routing is filesystem-based: `POST /api/<handler>` executes
`handlers/<handler>/post` with the request JSON on stdin. Do not add cluster
awareness to it.

