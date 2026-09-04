# Module layout and authorization

## Container image versions and Renovate

Third-party images pulled at runtime are declared in `build-images.sh` via:
```bash
--label="org.nethserver.images=docker.io/mariadb:11.4.12 docker.io/xwiki:16.10.18-mariadb-tomcat"
```

**RULE: always use a fully pinned version tag — never a floating tag like `lts`, `latest`, or `11.4-lts`.**
Renovate reads this label to track upstream releases and open automatic update PRs.
A floating tag gives Renovate nothing to compare against — updates are silently skipped.

Correct: `mariadb:11.4.12`, `nginx:1.27.5`
Wrong: `mariadb:11.4-lts`, `nginx:latest`

**RULE: never invent or guess a version tag. Always verify the tag exists before using it.**
Check available tags on Docker Hub before writing any image reference:
```bash
# List available tags for an image
curl -s "https://hub.docker.com/v2/repositories/library/mariadb/tags/?page_size=20" \
  | python3 -c "import sys,json; [print(t['name']) for t in json.load(sys.stdin)['results']]"
```
Or browse `https://hub.docker.com/_/mariadb/tags` directly. A non-existent tag silently fails at pull time and breaks the module.

---

## Module directory layout
```
build-images.sh          # Container image build + authorization declarations
imageroot/
  actions/               # Backend action handlers (Python 3 + bash)
  events/                # Event handlers triggered by platform events
  bin/                   # Utility scripts called by actions or systemd
  bin/module-dump-state  # (optional) runs before Restic backup — export DB/data to state/
  bin/module-cleanup-state # (optional) runs after backup — remove temp dump files
  systemd/user/          # Systemd user service units
  update-module.d/       # Upgrade hooks (run on module update)
  etc/state-include.conf # ALL paths to include in Restic backup (state/ and volumes/)
ui/                      # Vue.js 2 frontend
tests/                   # Robot Framework integration tests
```

---

## Authorization model

### Declaring privileges (build-images.sh)
Authorizations are declared as container labels in `build-images.sh`:
```bash
--label="org.nethserver.authorizations=node:fwadm traefik@node:routeadm mail@any:mailadm"
```
Format: `<scope>:<role>`. Multiple roles on the same scope: `node:fwadm,portsadm`.

**Scopes:** `node` (node agent), `cluster` (cluster agent), `<module>@node` (first instance on same node), `<module>@any` (all instances of that module).

**Available roles:**

| Role | Defined by | Purpose |
|---|---|---|
| `fwadm` | ns8-core / node | firewall rules (public services, zones, rich rules) |
| `portsadm` | ns8-core / node | port allocation |
| `tunadm` | ns8-core / node | TUN device + fwadm actions |
| `reader` | ns8-core | `get-*`, `show-*`, `read-*` |
| `routeadm` | ns8-traefik | manage Traefik routes |
| `certadm` | ns8-traefik | certificate management |
| `fulladm` | ns8-traefik | routeadm + certadm |
| `mailadm` | ns8-mail | master credentials, relay rules, BCC |
| `accountconsumer` | cluster | bind/use a user domain (LDAP) |
| `accountprovider` | cluster | provide a user domain |
| `selfadm` | built-in | module's own actions (auto-granted) |

### selfadm — module calling its own actions
A module can grant itself the right to call its own actions via Redis in
`imageroot/actions/create-module/10grants`:
```bash
redis-exec SADD "${AGENT_ID}/roles/selfadm" "action-name"
```
Use this when an action needs to trigger another action of the same module.
