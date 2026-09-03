# NS8 day-to-day operations

## API and action conventions

`api-cli` executes actions through the API server, or talks directly to Redis when no JWT cache is available locally. To authenticate remotely or as a user:

```bash
api-cli login
api-cli logout
```

Documented command forms:

```bash
api-cli run list-actions                              # default cluster agent
api-cli run <cluster_action> --data '{...}'           # e.g. update-module
api-cli run module/<module_id>/<action> --data '{...}'
api-cli run --agent module/<module_id> <action> --data '{...}'
api-cli run <action> --agent module/<module_id> --data '{...}'
```

Prefer bare cluster actions (`list-actions`, `get-cluster-status`, `list-installed-modules`, `update-module`). Use an API action name containing `/` only if the exact action name appears in `api-cli run list-actions` output; do not synthesize `cluster/<action>` forms. Add `--verbose` only if the literal string `--verbose` appears in `api-cli --help` output on that host.

If any `api-cli run` command returns an authentication error or HTTP 401, run `api-cli login` before retrying. If `api-cli login` fails because no local API server is reachable, verify `systemctl status api-server --no-pager`; do not fall back to direct Redis writes solely because authentication failed.

Run cluster-scoped actions (`add-module`, `remove-module`, `update-module`, `get-cluster-status`) from the cluster leader node. Before issuing a cluster-scoped action from a worker node, verify leader status with `api-cli run get-cluster-status | jq .leader` and connect to the leader when required by the host.

For multiline JSON, prefer stdin:

```bash
api-cli run module/<module_id>/<action> --data - <<'JSON'
{"key":"value"}
JSON
```

## Multi-node operations

If `list-installed-modules` shows the target module on a node different from the current shell, SSH to that node before using `runagent` or inspecting module-owned systemd and Podman state. Cluster-level actions such as `add-module`, `remove-module`, and `update-module` may be initiated only from a node where `api-cli` can reach the cluster leader. Never run `runagent -m <module_id>` from a node that does not host that module.

## Host preflight

Local:

```bash
hostnamectl --static
id
cat /etc/os-release | sed -n '1,8p'
uptime
api-cli --help
api-cli run list-actions | jq .
api-cli run get-cluster-status | jq .
api-cli run list-installed-modules | jq .
```

Remote one-shot:

```bash
ssh <target> 'hostnamectl --static; id; cat /etc/os-release | sed -n "1,8p"; uptime; api-cli --help | head -40'
```

Initial health triage:

```bash
systemctl --no-pager --type=service --state=failed
journalctl -p err -b --no-pager -n 100
api-cli run get-cluster-status | jq .
api-cli run list-installed-modules | jq .
podman ps --format '{{.Names}}\t{{.Status}}' || true
```

## Find modules and actions

List installed instances:

```bash
api-cli run list-installed-modules | jq .
api-cli run list-installed-modules | jq -r 'to_entries[] as $m | $m.value[]? | [.id, $m.key, (.node // .node_id // "?")] | @tsv'
```

Inspect one module:

```bash
mid=<module_id>
api-cli run module/$mid/list-actions | jq .
api-cli run module/$mid/get-configuration | jq . || true
api-cli run module/$mid/get-status | jq . || true        # base action is reliable mainly for rootless modules
runagent -m $mid sh -lc 'id; printenv | sort | egrep "^(MODULE_ID|MODULE_UUID|NODE_ID|AGENT_|IMAGE_|TCP_|UDP_)"'
runagent -m $mid sh -lc 'printf "install=%s\nstate=%s\n" "$AGENT_INSTALL_DIR" "$AGENT_STATE_DIR"; sed -n "1,220p" "$AGENT_STATE_DIR/environment" 2>/dev/null || true'
```

If `runagent -m <module_id>` exits non-zero or prints `module not found`, verify the module ID with `api-cli run list-installed-modules` and confirm the module is hosted on the current node. If the module exists on the current node but `runagent` still fails, check the module agent service before retrying: for rootfull modules use `systemctl status agent@<module_id> --no-pager`; for rootless modules use `runagent -m <module_id> systemctl --user status --no-pager` only after `runagent` succeeds.

Do not hardcode module paths. Resolve them from `AGENT_INSTALL_DIR` and `AGENT_STATE_DIR`. Typical paths are:

- rootless install: `/home/<module_id>/.config`
- rootless state: `/home/<module_id>/.config/state`
- rootfull install/state: `/var/lib/nethserver/<module_id>` and `/var/lib/nethserver/<module_id>/state`

## Install, remove, update

Install from enabled repository or explicit image URL:

```bash
add-module <module_name> <node_id>
add-module ghcr.io/<namespace>/<image>:<tag> <node_id>
```

For mutable development tags such as `latest`, `main`, or branch-named tags, `add-module` may reuse an image that already exists locally. Remove it on the target node first only when a fresh pull of a mutable tag is required. For versioned production tags such as `1.2.3`, do not run `podman rmi` before `add-module`.

```bash
podman rmi ghcr.io/<namespace>/<image>:<tag>
```

Remove:

```bash
remove-module <module_id>                 # preserve data
remove-module --no-preserve <module_id>   # erase module data; destructive
```

Update one or more instances:

```bash
api-cli run update-module --data '{"module_url":"ghcr.io/<namespace>/<image>:<tag>","instances":["<module_id>"]}'
api-cli run update-module --data '{"module_url":"ghcr.io/<namespace>/<image>:<tag>","instances":["<module_id>"],"force":true}'
```

Verify after install/update/remove:

Run the Post-change verification sequence. Useful commands include:

```bash
api-cli run list-installed-modules | jq .
api-cli run module/<module_id>/list-actions | jq . || true
api-cli run module/<module_id>/get-status | jq . || true
api-server-logs logs -e module -n <module_id> || true
```

## Configure a module

If the module is also exhibiting errors, complete steps 1-4 of the Troubleshooting sequence before beginning this workflow. The Troubleshooting sequence governs fault investigation; this workflow governs intentional reconfiguration.

Workflow:

1. `list-actions`
2. `get-configuration` if present
3. inspect current env and action files
4. build the smallest valid payload
5. run `configure-module`
6. run the Post-change verification sequence

Commands:

```bash
mid=<module_id>
api-cli run module/$mid/list-actions | jq .
api-cli run module/$mid/get-configuration | jq . || true
runagent -m $mid sh -lc 'find "$AGENT_INSTALL_DIR/actions" -maxdepth 2 -type f | sort | sed -n "1,200p"'
runagent -m $mid sh -lc 'find "$AGENT_INSTALL_DIR/actions/configure-module" -maxdepth 1 -type f -printf "%m %p\n" 2>/dev/null | sort'
```

Run configuration:

```bash
api-cli run module/$mid/configure-module --data - <<'JSON'
{
  "host": "app.example.org"
}
JSON
```

If validation fails, inspect:

```bash
runagent -m $mid sh -lc 'sed -n "1,240p" "$AGENT_INSTALL_DIR/actions/configure-module/validate-input.json" 2>/dev/null || true'
runagent -m $mid sh -lc 'test -s "$AGENT_INSTALL_DIR/actions/configure-module/validate-input.json" || cat "$AGENT_INSTALL_DIR/actions/configure-module/"* 2>/dev/null | head -300'
api-server-logs logs -e module -n $mid
```

Map validation error field names from `api-cli` output to the corresponding key in `validate-input.json` or the action script. Do not guess payload structure; if the schema or script cannot be resolved, report the raw validation error to the user and stop.

Preserve all fields returned by `get-configuration` in a `configure-module` payload unless `validate-input.json` explicitly omits the field from the `required` array and documents a default value for that field.

## Rootless vs rootfull operations

Detect runtime type:

```bash
runagent -m <module_id> sh -lc 'test "$(id -u)" = 0 && echo ROOTFULL || echo ROOTLESS; echo "$AGENT_INSTALL_DIR"; echo "$AGENT_STATE_DIR"'
```

Rootless modules run as their own Unix user, have private Podman storage, use user systemd units, and should be inspected through `runagent`:

```bash
runagent -m <module_id> systemctl --user list-units --all --no-pager
runagent -m <module_id> systemctl --user status <unit> --no-pager
runagent -m <module_id> journalctl --user -u <unit> --no-pager -n 200
runagent -m <module_id> podman ps -a
runagent -m <module_id> podman logs --tail 200 <container>
```

Rootfull modules run as root, share system Podman storage, use system units under `/etc/systemd/system`, and unit/volume names must be prefixed with `<module_id>`:

```bash
systemctl list-units --all '<module_id>*' --no-pager
systemctl status <module_id>.service --no-pager || systemctl status '<module_id>*' --no-pager
journalctl -u <module_id>.service --no-pager -n 200 || journalctl --no-pager -n 200 | grep -F '<module_id>'
podman ps -a
podman logs --tail 200 <container>
```

## Logs

NS8 logs are primarily in systemd journal; Loki/logcli and `api-server-logs` provide cluster/module views.

Cluster/module log tools:

```bash
api-server-logs logs -e module -n <module_id>          # follows like tail -f
api-server-logs logs -e node -n <node_id>
logcli labels module_id -q
logcli query -q --no-labels '{module_id="<module_id>"} | json | line_format "{{.MESSAGE}}"'
```

Journal patterns:

```bash
journalctl -b --no-pager -n 200
journalctl -p err -b --no-pager -n 200
journalctl -f _UID=$(id -u <rootless_module_id>)
runagent -m <rootless_module_id> journalctl --user --no-pager -n 200
```

API audit log:

```bash
sqlite3 /var/lib/nethserver/api-server/audit.db 'SELECT ID,User,Action,Timestamp FROM audit ORDER BY ID DESC LIMIT 20;'
```

## Containers, volumes, and mounts

Rootless:

```bash
runagent -m <module_id> podman ps -a
runagent -m <module_id> podman inspect <container>
runagent -m <module_id> podman system info --format='{{.Store.VolumePath}}'
runagent -m <module_id> podman volume ls
runagent -m <module_id> podman inspect <container> --format '{{json .Mounts}}' | jq .
```

Rootfull:

```bash
podman ps -a
podman inspect <container>
podman system info --format='{{.Store.VolumePath}}'
podman volume ls | grep '^local[[:space:]]\+<module_id>-' || true
podman inspect <container> --format '{{json .Mounts}}' | jq .
```

Rules:

- Persistent app data should be in Podman volumes.
- Rootfull volumes share one namespace and must use `<module_id>-` prefixes.
- Rootless volumes are private to the module user.
- On SELinux hosts, check labels; `:z` is normally used for shared container bind mounts.
- Use `volumectl` and `/etc/nethserver/volumes.conf` for node volume assignment, not manual symlink hacks.

## Traefik HTTP routes and certificates

Find Traefik instance:

```bash
api-cli run list-installed-modules | jq -r '."ghcr.io/nethserver/traefik"[]?.id'
redis-cli --raw get cluster/default_instance/traefik 2>/dev/null || true
```

Inspect routes:

```bash
tr=<traefik_id>
api-cli run list-routes --agent module/$tr | jq .
api-cli run list-routes --agent module/$tr --data '{"expand_list":true}' | jq .
api-cli run get-route --agent module/$tr --data '{"instance":"<module_id>"}' | jq .
```

Create/update route only when the module action does not already manage it:

```bash
api-cli run set-route --agent module/$tr --data - <<'JSON'
{
  "instance": "<module_id>",
  "url": "http://127.0.0.1:<port>",
  "host": "app.example.org",
  "path": "/optional-prefix",
  "lets_encrypt": true,
  "http2https": true,
  "skip_cert_verify": false
}
JSON
```

Inspect certificates:

```bash
api-cli run get-certificate --agent module/$tr --data '{"fqdn":"app.example.org"}' | jq .
api-cli run list-certificates --agent module/$tr | jq .
```

## Service discovery, users, events, firewall

Service providers:

```bash
api-cli run module/<consumer_module>/list-service-providers --data '{"service":"imap","transport":"tcp"}' | jq .
redis-cli --scan --pattern 'module/*/srv/*/*'
redis-cli hgetall module/<provider_module>/srv/tcp/<service>
```

LDAP/user-domain discovery from a module context:

```bash
runagent -m <module_id> python3 -magent.ldapproxy | jq .
```

Events:

```bash
runagent -m <module_id> sh -lc 'find "$AGENT_INSTALL_DIR/events" -maxdepth 3 -type f -printf "%m %p\n" 2>/dev/null | sort'
# Publish only when official docs or module source require event injection for this task and the user explicitly asks for that test:
redis-cli PUBLISH module/<module_id>/event/<event_name> '{"field":"value"}'
```

Firewall inspection:

```bash
firewall-cmd --get-active-zones
firewall-cmd --list-all-zones
```

Firewall changes for modules should normally be implemented by module code with `agent.add_public_service()` / `agent.remove_public_service()` and require the image authorization label `org.nethserver.authorizations=node:fwadm`. Avoid manual firewall changes unless the task explicitly asks for an emergency host-level workaround.

## Redis inspection

Use Redis inspection only when `api-cli` returns a non-zero exit code, `api-cli` is not installed on the host, or successful `api-cli` output does not contain the specific field required for the task. Do not use Redis to cross-check or supplement successful `api-cli` output. Prefer read-only commands:

```bash
redis-cli --scan --pattern 'module/<module_id>/*'
redis-cli hgetall module/<module_id>/environment
redis-cli get module/<module_id>/ui_name
redis-cli hget node/<node_id>/vpn endpoint
```

Do not write Redis keys or publish Redis messages unless official docs or module code explicitly require that operation for the task and the user explicitly asks for that test.


