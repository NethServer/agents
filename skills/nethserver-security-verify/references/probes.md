# Read-only probe recipes

All probes below are non-destructive. Run from the leader (or a node that can
reach it). Substitute `<leader>`, `<module_id>`, `<action>`, `<user>` as
needed. Confirm cluster role first: `api-cli run get-cluster-status | jq .leader`.

## Preflight

```bash
api-cli run get-cluster-status | jq '{leader, nodes: (.nodes|keys)}'
api-cli run list-installed-modules | jq '.[].id'
```

## auth — GET bypasses authorization (A1)

Log in as a low-privilege user, then hit a GET route that should be authorized:

```bash
api-cli login                       # as the restricted user
# read-only: fetch data that this user should not be authorized for
curl -s -H "Authorization: Bearer $TOKEN" \
     "https://<leader>/api/module/<other_module>/tasks" | jq .
# 200 with data => confirmed (GET bypassed authz)
```

## auth — authorization wildcard / restricted action (A2, A6)

```bash
# attempt an action the user is NOT authorized for; expect 403
api-cli run <privileged_action> --data '{}' ; echo "exit=$?"
# http-basic route with bad creds; expect 401
curl -s -o /dev/null -w '%{http_code}\n' -u bad:bad \
     "https://<leader>/api/module/<module_id>/http-basic/<action>"
```

## action-input — missing/loose schema (I1, I3)

```bash
# send unexpected field; a strict schema (additionalProperties:false) rejects it
api-cli run <action> --data '{"__unexpected__":"x"}' ; echo "exit=$?"
# path traversal attempt on a path-taking field; expect rejection
api-cli run <action> --data '{"path":"../../etc/does-not-exist"}' ; echo "exit=$?"
```

Do these against a **test** node only; even "read" actions can have side
effects. Prefer actions whose name starts with `list`/`get`.

## api-moduled — scope claim / handler (M2, M3)

```bash
# obtain a token from the module portal login, then decode the scope claim
TOKEN=$(curl -s -X POST https://<module-host>/api/login \
        -d '{"username":"...","password":"..."}' | jq -r .token)
echo "$TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null | jq '.scope // "ABSENT (unrestricted)"'
# call a handler the token should NOT reach; expect 403
curl -s -o /dev/null -w '%{http_code}\n' -X POST \
     -H "Authorization: Bearer $TOKEN" https://<module-host>/api/<privileged_handler>
```

## redis-privilege — ACL scoping (R2, R4)

```bash
# as the module user, attempt to read another module's key; expect permission error
runagent -m <module_id> redis-cli --scan --pattern 'module/<other_module>/*'
runagent -m <module_id> redis-cli GET 'cluster/some/privileged/key' ; echo "exit=$?"
```

## secrets — redaction / leak (S2, S4)

```bash
# read recent task output for a secret-handling action; confirm redaction
api-cli run get-task-output --data '{"task_id":"<id>"}' | grep -iE 'password|secret|token' || echo "no secret in output"
# audit log should not contain cleartext secrets
runagent journalctl -u api-server --no-pager -n 200 | grep -iE 'password=|secret=' || echo "no cleartext secret in log"
```

## proxy-trust — X-Forwarded-For forgery (P1)

```bash
# single failed login with a forged client IP; then check audit records the forged IP
curl -s -o /dev/null -H 'X-Forwarded-For: 203.0.113.99' \
     -X POST https://<leader>/api/login -d '{"username":"probe","password":"wrong"}'
api-cli run list-audit --data '{"user":"probe"}' | jq '.[].ip'
# records 203.0.113.99 => forgery confirmed
```

Only one failed login. Confirm there is no account-lockout on `probe` first.

## container — rootless verification

```bash
# confirm the module container runs as a non-root user
runagent -m <module_id> podman top <container> user huser
podman inspect <container> --format '{{.Config.User}}'
```
