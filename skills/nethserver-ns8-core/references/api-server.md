# api-server and api-moduled internals

Read `core/api-server/AGENTS.md` first: routes, JWT lifecycle and claims, action-based
authorization with `filepath.Match`, TOTP, the SQLite audit store in WAL mode with its
`login-ok`/`auth-fail`/`create-task` events, and the Melody WebSocket relay are all there.
`core/api-server/README.md` adds the frame protocol — `logs-start`, `logs-stop`, task
events and their JSON payloads — which `docs/` does not carry. For api-moduled, its own
`core/api-moduled/AGENTS.md` documents the filesystem routing (`POST /api/<handler>` runs
`handlers/<handler>/post`), and the rule that matters is only this: do not add cluster
awareness to it.

What none of those files say:

- The GET authorization bypass carries a `TODO` in `core/api-server/middleware/middleware.go`.
  Treat it as provisional, never as a guarantee to build on.
- `/api/2FA` is exempt from authorization for both `POST` and `DELETE`, next to that
  bypass in the same function.
- Grants are re-read from Redis on every request: `IdentityHandler` calls
  `methods.RedisAuthorization`. A revoked grant therefore takes effect immediately,
  without waiting for the 14-day token expiry.
- `core/api-server/socket/socket.go` calls `melody.New()` and overrides none of its
  configuration, so the library's own defaults apply, frame size ceiling included.
