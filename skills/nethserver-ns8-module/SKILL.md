---
name: nethserver-ns8-module
description: 'Develop and review NethServer 8 modules following project conventions. Use when working in an ns8-* module repository — writing action or event handlers, systemd units, backup/restore, build-images.sh, or the Vue.js frontend — or when the repo is laid out as imageroot/ + ui/, or mentions "org.nethserver.*" labels. Supports: (1) Module architecture and directory layout, (2) Authorization model with scopes, roles, and selfadm, (3) Backend patterns — agent SDK, Redis, journald logging, secret handling, service discovery, systemd pod ordering, (4) Backup and restore for MariaDB and PostgreSQL, (5) Frontend patterns — Vue 2, Vuex, Carbon, ns8-ui-lib component priority, task progress, i18n'
---

# NethServer 8 module development

## Overview

NS8 is a modular Linux server platform. Each module runs in a Podman container,
rootless by default. Some modules require rootful mode — declared in `build-images.sh`
via `--label="org.nethserver.rootfull=1"`.

Backend lives under `imageroot/` (Python 3 + bash). Frontend lives under `ui/` (Vue.js 2).
Read the **Backend** sections when touching actions, events, systemd, or backup; read the
**Frontend** sections when touching `ui/`.

---

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

---

## Action Handlers
Each action is a directory under `imageroot/actions/<action-name>/`.
Scripts inside execute in lexicographic order: `10grants`, `20read`, `80start_services`, etc.
Python scripts use the NS8 agent SDK (`import agent`).
Bash scripts use standard POSIX shell.

Base actions inherited automatically (no need to implement):
- `create-module` — install + pull image
- `destroy-module` — cleanup (traefik, firewall, systemd)
- `get-status` — runtime status (rootless and rootful)
- `list-service-providers` — service discovery

### JSON data flow

Every action step receives input as JSON on stdin and writes output as JSON to stdout:

```python
import json, sys

data = json.load(sys.stdin)           # read input from UI / caller
result = {"key": data["key"]}
json.dump(result, fp=sys.stdout)      # write output back
```

Input/output schemas live in `validate-input.json` / `validate-output.json` at the action
root (JSON Schema Draft 7). The platform validates them before/after execution — define
them to get free input sanitization.

### Injected environment variables

The NS8 platform injects these vars into every action and event handler:

| Variable | Value |
|---|---|
| `AGENT_ID` | Module agent identity, e.g. `module/imapsync1` |
| `MODULE_ID` | Module instance ID, e.g. `imapsync1` |
| `NODE_ID` | Node integer ID |
| `AGENT_STATE_DIR` | Absolute path to `state/` directory |
| `AGENT_INSTALL_DIR` | Absolute path to `imageroot/` |
| `REDIS_USER` | Redis auth username |
| `REDIS_PASSWORD` | Redis auth password |

Module-specific vars (set via `agent.set_env()` during `configure-module`) are loaded from
`state/environment` and available as plain `os.environ` reads in all subsequent actions.

### Error signaling

Three patterns, pick by context:

**Validation failure** — invalid input the user can fix:
```python
agent.set_status('validation-failed')
json.dump([{'field': 'mail_server', 'parameter': 'mail_server', 'value': data['mail_server'], 'error': 'not_valid'}], fp=sys.stdout)
sys.exit(3)
```

**Assertion** — invariant that should never fail (stack trace to stderr + `sys.exit(2)`):
```python
agent.assert_exp(some_condition, "error message")
```

**Subprocess / cross-module failure** — see `tasks.run vs run_helper` below.

Non-zero exit from any step halts the action sequence.

Modules with a UI must implement:
- `configure-module` — validate + apply config
- `get-configuration` — return current config (mirrors configure-module input)

### Logging to journald

**stdout is reserved for action output (JSON). All log messages must go to stderr.**
The NS8 agent framework captures stdout as the action's return value — printing to stdout corrupts the output.

In Python scripts:
```python
import sys, agent
print("informational message", file=sys.stderr)              # plain log
print(agent.SD_WARNING + "something unexpected", file=sys.stderr)  # warning level
print(agent.SD_ERR + "critical failure", file=sys.stderr)          # error level
```

In bash scripts, redirect stdout to stderr at the top of the file:
```bash
exec 1>&2   # all subsequent echo/printf go to journald
```

`agent.SD_WARNING`, `agent.SD_ERR`, `agent.SD_INFO`, `agent.SD_NOTICE` are systemd journal priority prefixes — journald parses them to set log level.

### Agent SDK (Python)
```python
import agent

# High-level env helpers — no Redis connection needed
agent.set_env("KEY", "value")   # add/update env var in state/environment
agent.unset_env("KEY")          # remove env var from state/environment
```

> **⚠️ SECURITY — `agent.set_env()` writes to Redis plain text, readable by ALL modules on the node. NEVER store passwords/tokens/secrets via `agent.set_env()`.**
>
> **Secret pattern:** generate in `create-module/10genpasswords` → write `state/passwords.env` (mode 0600) → declare in `etc/state-include.conf` (Restic backup) → load via systemd `EnvironmentFile=-%S/state/passwords.env` → inject into container via `--env-file=%S/state/passwords.env`. Restic restores the file on `restore-module` — no extra action needed. Non-secret vars (`TRAEFIK_HOST`, `LDAP_DOMAIN`, etc.) use `agent.set_env()` normally.
>
> ```python
> # create-module/10genpasswords
> import secrets, os
> p = os.path.join(os.environ["AGENT_STATE_DIR"], "passwords.env")
> with open(p, "w") as f:
>     f.write(f"DB_PASSWORD={secrets.token_urlsafe(16)}\n")
> os.chmod(p, 0o600)
> ```

#### Progress reporting
Requires frontend `isProgressNotified: true` (see the Frontend § Task progress below):
```python
import os, agent
agent.set_progress(50)        # emit 0-100 to frontend progress bar
agent.set_weight(os.path.basename(__file__), 0)  # exclude step from auto-progress (validation steps)
```

#### tasks.run vs run_helper

```python
# Cross-module RPC — tracked by NS8 task framework, returns output dict
response = agent.tasks.run("module/mail1", action='list-user-mailboxes', data={})
agent.assert_exp(response['exit_code'] == 0)
mailboxes = response['output']['user_mailboxes']

# Local subprocess — synchronous, blocks until done
agent.run_helper("run-imapsync", "restart", task_id).check_returncode()
agent.run_helper("systemctl", "--user", "try-restart", "myapp.service").check_returncode()
```

| | `tasks.run` | `run_helper` |
|---|---|---|
| Target | Another module's action (or selfadm) | Local script in `imageroot/bin/` or any binary |
| Returns | `{'exit_code': int, 'output': dict}` | `CompletedProcess` — call `.check_returncode()` |
| Use for | Inter-module calls, selfadm delegation | Service management, podman, local helpers |

## Service Providers
Modules expose services to other modules via Redis hash keys:
```
module/<module_id>/srv/<transport>/<service_name>
```
Typical fields: `host`, `port`.

Discovering services (Python) — `redis_connect` is needed here for direct Redis access:
```python
rdb = agent.redis_connect(use_replica=True)   # use_replica: works even if cluster leader is unreachable
providers = agent.list_service_providers(rdb, 'imap', 'tcp', {'module_uuid': uuid})
host = providers[0]['host']
```

When a service endpoint changes, the provider fires an event named
`<service-name>-changed` with payload `{"module_id": "...", "module_uuid": "..."}`.

### Discovery scripts (ExecStartPre)

Run at container startup (`ExecStartPre=` in systemd unit) — resolve external services and write results to a `.env` file loaded by the main service. Exit non-zero aborts startup. References: ns8-sogo `imageroot/bin/discover-service`, ns8-mail `imageroot/bin/discover-services`.

**Service endpoint discovery:**
```python
import os, sys, agent

rdb = agent.redis_connect(use_replica=True)  # replica: works even if cluster leader unreachable
providers = agent.list_service_providers(rdb, 'imap', 'tcp', {'module_uuid': os.environ['MAIL_SERVER']})
if len(providers) != 1:
    print(agent.SD_ERR + "Cannot find imap service", file=sys.stderr)
    sys.exit(4)

tmpfile = "discovery.env." + str(os.getpid()) + ".tmp"
with open(tmpfile, "w") as f:
    print(f"IMAP_HOST={providers[0]['host']}", file=f)
    print(f"IMAP_PORT={providers[0]['port']}", file=f)
os.replace(tmpfile, "discovery.env")  # atomic — never leaves partial file
```

**LDAP discovery** (use `Ldapproxy`, not Redis direct):
```python
from agent.ldapproxy import Ldapproxy

try:
    odom = Ldapproxy().get_domain(os.environ['LDAP_DOMAIN'])
    'host' in odom  # raises if odom is None (domain not configured)
except:
    # Restore: domain may be unavailable — use placeholder so container starts
    odom = {'host': '127.0.0.1', 'port': 20000, 'schema': 'rfc2307',
            'base_dn': 'dc=invalid', 'bind_dn': 'cn=x,dc=invalid', 'bind_password': 'invalid'}

tmpfile = "discovery.env." + str(os.getpid()) + ".tmp"
with open(tmpfile, "w") as f:
    print(f"LDAP_HOST={odom['host']}", file=f)
    # ... bind_dn, bind_password, schema, base_dn
os.replace(tmpfile, "discovery.env")
```

`agent.SD_ERR` — systemd error-level prefix. `os.replace()` — atomic write. Always `use_replica=True` in startup scripts.

## Events
Events are Redis channel messages. Channel format: `module/<module_id>/event/<event_name>`.
Name events in **past tense**: `mail-settings-changed`, `ldap-provider-changed`.

Firing an event:
```bash
redis-cli PUBLISH "module/mymodule1/event/my-settings-changed" '{"module_id":"mymodule1","module_uuid":"..."}'
```

### Handlers
Live in `imageroot/events/<event-name>/` — executable scripts, work like action steps.
Payload arrives on **stdin** as JSON. **Non-zero exit halts remaining steps.**
Injected env vars: `AGENT_EVENT_SOURCE`, `AGENT_EVENT_NAME`.

Pattern: `event = json.load(sys.stdin)` → filter with `sys.exit(0)` if not relevant → apply change → `agent.run_helper('systemctl', '--user', '-T', 'try-restart', ...)`.
`-T` removes the default timeout. `agent.certificate_event_matches(event, hostname)` — built-in helper for `certificate-changed`.

### Built-in platform events
Module channel `module/<id>/event/<name>`: `user-domain-changed`, `ldap-provider-changed`,
`certificate-changed`, `mail-settings-changed`, `backup-status-changed`.
Node channel `node/<id>/event/<name>`: `fqdn-changed`.
Cluster channel `cluster/event/<name>`: `module-added`, `module-removed`, `leader-changed`.

## Systemd Services

### Naming convention
- Single service: `<module>.service`
- Multi-service (pod pattern): `<module>.service` (pod master) + `<component>-app.service` (children)

### Multi-service ordering (pod pattern)

Boot order: **pod → DB → app**. Each unit must declare its relationships explicitly.

**Pod master (`<module>.service`)** — owns the pod, must declare all children:
```ini
[Unit]
Requires=mariadb-app.service myapp-app.service
Before=mariadb-app.service myapp-app.service
```

**DB service (`mariadb-app.service`)** — starts after pod, before app:
```ini
[Unit]
BindsTo=<module>.service
After=<module>.service
Before=myapp-app.service
```

**App service (`myapp-app.service`)** — starts last, after pod and DB:
```ini
[Unit]
BindsTo=<module>.service
After=<module>.service mariadb-app.service
```

`BindsTo=` ensures children stop automatically when the pod dies. Without it, children keep running as orphans.

### Conditional service start (configure-module/80start_services)
Services are enabled and started only after successful configuration.

> **⚠️ WRONG — starting only the pod service does NOT start children:**
> ```bash
> systemctl --user restart <module>.service   # WRONG — children stay down
> ```
> systemd does NOT cascade restarts to children automatically.

**CORRECT — list every service explicitly** to guarantee `Before=`/`After=` order is respected:
```bash
systemctl --user enable <module>.service
# Use try-restart if the service may not be running yet (e.g. first configure)
systemctl --user try-restart <module>.service db-app.service app-app.service
```
All three (or more) services must appear in the command. Order matters: pod first, then DB, then app.

## Backup & Restore

### Declaring what to back up (state-include.conf)
`imageroot/etc/state-include.conf` lists paths relative to the module home. Use `state/<file>` for files in `AGENT_STATE_DIR` and `volumes/<name>` for Podman volumes (`<module_id>-<name>` when rootful). `state/environment` is always included automatically.

**Only include files that are NOT provided by the module image.** If a file in `state/` is derived from or identical to a file shipped in `imageroot/` (e.g. `state/initdb.d/init.sql` copied from `imageroot/sql/init.sql`), do NOT back it up — regenerate it during restore instead. Back up only:
- User data volumes (`volumes/myapp-data`)
- SQL/DB dumps (`state/mydb.sql`, `state/mydb.pg_dump`)
- Secrets generated at install time (`state/passwords.env`)
- Any runtime state not reproducible from the image

### Restore sequence
`imageroot/actions/restore-module/` — numbered steps, `10restore` inherited (Restic).

- `06copyenv` — restore env vars from `request['environment']` via `agent.set_env()`
- `40restoreDB` — load SQL dump via ephemeral container (see patterns below)
- `50call-configure-module` — call `configure-module` with restored env vars via `agent.tasks.run()`

> **⚠️ `50call-configure-module` must pass ALL vars restored by `06copyenv`**, not just the Traefik ones.
> `06copyenv` restores every non-secret env var set by `agent.set_env()`.
> Missing any var leaves `configure-module` with wrong/empty defaults.
>
> Pattern — read from `os.environ` (already populated by `06copyenv`), map to `configure-module` input:
> ```python
> agent.tasks.run("module/" + os.environ["MODULE_ID"], action="configure-module", data={
>     "host":      os.environ["TRAEFIK_HOST"],
>     "http2https": os.environ.get("TRAEFIK_HTTP2HTTPS", "false") == "true",
>     # ALL other fields accepted by configure-module — check validate-input.json
> })
> ```
> Read `configure-module/validate-input.json` to enumerate every required/optional field.

### MariaDB
- **Dump** (`imageroot/bin/module-dump-state`, CWD=`state/`): `podman exec mariadb-app mysqldump --databases mydb --default-character-set=utf8mb4 --single-transaction --quick --add-drop-table --skip-dump-date > mydb.sql`
- **Cleanup** (`imageroot/bin/module-cleanup-state`): `rm -vf mydb.sql`
- **Restore** (`40restoreDB`): move `mydb.sql` into `initdb.d/`, add `zz_restore.sh` that calls `docker_temp_server_stop`, launch ephemeral `${MARIADB_IMAGE}` with `--volume=./initdb.d:/docker-entrypoint-initdb.d:z --volume mysql-data:/var/lib/mysql/:Z`. MariaDB entrypoint auto-executes the SQL, then the script stops the container.
- **Reference**: ns8-sogo

`state-include.conf`: `state/mydb.sql` + `volumes/mysql-data`

### PostgreSQL
- **Dump** (`imageroot/bin/module-dump-state`): `podman exec postgres-app pg_dump -U myuser --format=c mydb > mydb.pg_dump` (custom format for `pg_restore`)
- **Cleanup** (`imageroot/bin/module-cleanup-state`): `rm -vf mydb.pg_dump`
- **Restore** (`40restore-postgres`): create `restore/mydb_restore.sh` with `pg_restore --no-owner --no-privileges`, launch ephemeral `${POSTGRES_IMAGE}` with dump **piped via stdin** (`< mydb.pg_dump`), script calls `docker_temp_server_stop` on exit.
- **Reference**: ns8-mattermost

`state-include.conf`: `state/mydb.pg_dump` + `volumes/postgres-data`

### Clone vs restore
- **restore-module**: Restic restores files listed in `etc/state-include.conf` → `40restoreDB` loads SQL dump → `50call-configure-module` reconfigures
- **clone-module**: no Restic restore, no SQL dump — only `50call-configure-module` (fresh DB, env vars from `os.environ` set by clone framework)

Dump/cleanup scripts (`imageroot/bin/module-dump-state`, `imageroot/bin/module-cleanup-state`) only run during backup — not during clone or restore.

### Volume persistence
Named Podman volumes are created automatically on first use — no label required.
Mount in the systemd service:
```
--volume mysql-data:/var/lib/mysql/:Z
--volume postgres-data:/var/lib/postgresql/data:Z
```

### Additional disks
`--label="org.nethserver.volumes=vol1 vol2"` — marks volumes as candidates for additional-disk placement. At install, the UI prompts the sysadmin to assign them to an extra disk (slower but bigger). Without the label, volumes land in Podman default under the module home. Only use for bulk data (DB, mail, media). Assignments in `/etc/nethserver/volumes.conf`, managed via `volumectl`.

### SELinux volume label flags
- `:z` (shared) — volume accessible by multiple containers within the same pod
- `:Z` (private) — volume exclusive to a single container/service

## Upgrade Hooks
Scripts in `imageroot/update-module.d/` run on `update-module` in lexicographic order.
If a script fails, execution continues with the next one — each script is independent.

Recommended layout: `05`-`06` pre-restart migrations, `30restart` (`systemctl --user try-restart`), `50`-`60` post-restart reindex/cleanup.
Version-specific migrations go before `30restart` so the new code starts on updated data.

---

## Stack & Vuex
Vue 2.6, Vuex, Vue Router, IBM Carbon Design System, `@nethserver/ns8-ui-lib`.
Views: `ui/src/views/` — Components: `ui/src/components/`

```javascript
import { mapState } from "vuex";
import { TaskService, UtilService, IconService, StorageService, QueryParamService, PageTitleService, DateTimeService } from "@nethserver/ns8-ui-lib";
export default {
  mixins: [TaskService, UtilService, IconService, QueryParamService, PageTitleService], // add StorageService, DateTimeService, LottieService if needed
  computed: { ...mapState(["instanceName", "core", "appName"]) },
}
```

- `core` = parent NS8 shell Vue instance (iframe). `this.core.$root.$once(...)`.
- `instanceName` = module ID e.g. `imapsync1`. Auto-extracted from URL by App.vue.
- Routes: `status` (default `/`), `settings`, `tasks`, `about`. Navigate: `this.goToAppPage(this.instanceName, "settings")` (UtilService) — NOT `this.$router.push()`.
- **Before writing utility code, check `ns8-ui-lib/src/lib-mixins/`** — all already importable.

| Mixin | Key methods |
|---|---|
| `TaskService` | `createModuleTaskForApp()`, `createNodeTaskForApp()`, `createErrorNotificationForApp()`, `createNotificationForApp()`, `getTaskStatus()`, `getTaskKind()` |
| `UtilService` | `getErrorMessage()`, `clearErrors()`, `focusElement()`, `goToAppPage()`, `getUuid()`, `sortByProperty(prop)`, `isJson(s)`, `tryParseJson(s)` |
| `DateTimeService` | `formatDate` (date-fns), `formatDateDistance`, `parseIsoDate`, `dateIsBefore`, `formatInTimeZone(date,fmt,tz)` |
| `StorageService` | `getFromStorage("myKey")` → object\|null, `saveToStorage("myKey", obj)`, `deleteFromStorage("myKey")` — localStorage wrappers keyed per module instance. Do NOT use `localStorage` directly. |
| `QueryParamService` | `queryParamsToDataForApp()`, `watchQueryData()` — sync URL params ↔ data |
| `IconService` | **~150 icons in `data()` — NEVER import manually without checking `ns8-ui-lib/src/lib-mixins/icon.js` first.** Use as `:icon="Save20"` directly. Available (partial list): `Save20` `TrashCan20` `Edit20` `Add20` `Close20` `Search20` `Settings20` `Information16` `Information20` `CheckmarkFilled20` `ErrorFilled20` `Warning20` `WarningAlt20` `Restart20` `Download20` `ArrowRight20` `ChevronDown20` `ChevronUp20` `ChevronLeft20` `ChevronRight20` `ArrowDown20` `Rocket20` `Power20` `Password20` `Checkmark20` `Reset20` `Launch20` `Link20` `Upgrade20` `Tools20` `Document20` `Folder20` `User20` `Group20` `Filter20` `Time20` `Hourglass20` `DataBase20` `DataBackup20` `Certificate20` `Firewall20` `Router20` `Catalog20` `Events20` `Email20` `Locked20` `OverflowMenuVertical20` `ZoomIn20` `CloudUpload20` |
| `PageTitleService` | Sets browser tab title |
| `LottieService` | Lottie helpers |

## Action call pattern

```javascript
import { to } from "await-to-js";

data: () => ({
  loading: { getConfiguration: false, configureModule: false },
  error:   { getConfiguration: "", configureModule: "", myField: "" },
  myField: "",
}),

created() { this.getConfiguration(); },

async getConfiguration() {
  this.loading.getConfiguration = true;
  const eventId = this.getUuid();
  this.core.$root.$once(`get-configuration-completed-${eventId}`, this.getConfigurationCompleted);
  this.core.$root.$once(`get-configuration-aborted-${eventId}`,   this.getConfigurationAborted);
  const res = await to(this.createModuleTaskForApp(this.instanceName, {
    action: "get-configuration",
    extra: { title: this.$t("action.get-configuration"), isNotificationHidden: true, eventId },
  }));
  if (res[0]) { this.error.getConfiguration = this.getErrorMessage(res[0]); this.loading.getConfiguration = false; }
},
getConfigurationCompleted(taskContext, taskResult) {
  this.myField = taskResult.output.my_field;
  this.loading.getConfiguration = false;
},

async configureModule() {
  if (!this.validateConfigureModule()) return;
  this.loading.configureModule = true;
  const eventId = this.getUuid();
  this.core.$root.$once(`configure-module-validation-failed-${eventId}`, this.configureModuleValidationFailed);
  this.core.$root.$once(`configure-module-completed-${eventId}`,         this.configureModuleCompleted);
  this.core.$root.$once(`configure-module-aborted-${eventId}`,           this.configureModuleAborted);
  const res = await to(this.createModuleTaskForApp(this.instanceName, {
    action: "configure-module",
    data: { my_field: this.myField },
    extra: { title: this.$t("settings.configuring"), eventId },
  }));
  if (res[0]) { this.error.configureModule = this.getErrorMessage(res[0]); this.loading.configureModule = false; }
},

validateConfigureModule() {
  this.clearErrors(this);
  if (!this.myField) { this.error.myField = "common.required"; this.focusElement("myField"); return false; }
  return true;
},
configureModuleAborted(taskResult, taskContext) {
  console.error(`${taskContext.action} aborted`, taskResult);
  this.error.configureModule = this.$t("error.generic_error");
  this.loading.configureModule = false;
},
configureModuleCompleted(taskContext, taskResult) {
  this.loading.configureModule = false;
  // apply taskResult.output if needed
},
configureModuleValidationFailed(validationErrors) {
  this.loading.configureModule = false;
  for (const e of validationErrors) { this.error[e.parameter] = this.$t("settings." + e.error); }
  this.focusElement(validationErrors[0].parameter);
},
```

Backend validation payload: `[{field, parameter, value, error}]` — `parameter` maps to `error` object key.

## Task progress

Add `isProgressNotified: true` in `extra`, use `$on` (not `$once`) for repeated events.
Unregister in **all terminal states** (completed, aborted, validation-failed):

```javascript
this.myProgress = 0;
this.core.$root.$on(`${taskAction}-progress-${eventId}`, this.myActionProgressUpdated);
// extra: { ..., isProgressNotified: true, eventId }
// in every terminal callback:
this.core.$root.$off(`${taskContext.action}-progress-${taskContext.extra.eventId}`);
// progress handler:
myActionProgressUpdated(progress) { this.myProgress = progress; }, // 0-100
```

```html
<NsProgressBar :value="myProgress" :indeterminate="!myProgress" />
```

Both sides required: backend `agent.set_progress(0-100)` + frontend `isProgressNotified: true`. See the Backend § Agent SDK above.

## Template

For icons not in `IconService`, import manually: `import Play20 from "@carbon/icons-vue/es/play--outline/20"` + `components: { Play20 }`.
Pattern: `@carbon/icons-vue/es/<kebab-name>/<size>`. Variants use double dash: `play--outline`, `add--alt`.

```html
<cv-form @submit.prevent="configureModule">
  <NsTextInput v-model.trim="myField" :label="$t('s.label')" ref="myField"
    :invalid-message="$t(error.myField)" :disabled="loading.configureModule" />

  <NsComboBox v-model.trim="myField" :title="$t('s.title')" :label="$t('s.placeholder')"
    :options="list" :invalid-message="$t(error.myField)" ref="myField"
    :disabled="loading.getConfiguration || loading.configureModule" />

  <NsButton kind="primary" :icon="Save20" :loading="loading.configureModule"
    :disabled="loading.getConfiguration || loading.configureModule">
    {{ $t("settings.save") }}
  </NsButton>

  <NsInlineNotification v-if="error.configureModule" kind="error"
    :title="$t('action.configure-module')" :description="error.configureModule" :showCloseButton="false" />
</cv-form>
```

`ref="myField"` must match `focusElement("myField")`.

## ns8-ui-lib components

> **⚠️ COMPONENT PRIORITY — strictly enforced:**
> 1. **Use `Ns*` (ns8-ui-lib) first.** Check the list below before anything else.
> 2. **Only use `cv-*` (Carbon Vue) if no `Ns*` equivalent exists.**
> Never use `cv-slider`, `cv-toggle`, `cv-text-input`, etc. when `NsSlider`, `NsToggle`, `NsTextInput` exist.
> Wrong: `<cv-slider>` — Correct: `<NsSlider>`

Source: `github.com/NethServer/ns8-ui-lib` — read `src/lib-components/<Name>.vue` for props.

`NsButton` `NsTextInput` `NsPasswordInput` `NsComboBox` `NsComboSearchBox` `NsMultiSelect`
`NsToggle` `NsCheckbox` `NsSlider` `NsByteSlider` `NsTimePicker` `NsModal` `NsDangerDeleteModal`
`NsInlineNotification` `NsToastNotification` `NsDataTable` `NsPagination` `NsEmptyState`
`NsStatusCard` `NsInfoCard` `NsTile` `NsTabs` `NsProgress` `NsProgressBar`
`NsSystemdServiceCard` `NsSystemLogsCard` `NsWizard` `NsCodeSnippet` `NsTag`

**Vue filters** (global, no import): `{{ n | byteFormat }}` `{{ n | humanFormat }}` `{{ n | mibFormat }}` `{{ n | gibFormat }}` `{{ s | secondsFormat }}` `{{ s | secondsLongFormat }}`. Source: `ns8-ui-lib/src/lib-filters/filters.js`.

**NsWizard** props: `visible`, `isLastStep` (Next→Finish), `isNextLoading`, `isNextDisabled`, `isPreviousShown`, `isCancelShown`. Slots: `#title` `#content`. Events: `@cancel` `@previousStep` `@nextStep`.

```html
<NsWizard :visible="isWizardVisible" :isLastStep="currentStep === steps.length - 1"
  :isNextLoading="loading.nextStep" @cancel="isWizardVisible = false"
  @previousStep="currentStep--" @nextStep="handleNextStep">
  <template #title>{{ $t("wizard.title") }}</template>
  <template #content><!-- step content --></template>
</NsWizard>
```

## Translations

**ONLY edit `ui/public/i18n/en/translation.json`.**
All other language files (`fr/`, `it/`, `de/`, etc.) are auto-generated by Renovate — never touch them manually.
If you add or rename a key, add/rename it in `en/translation.json` only. Do NOT create or modify any other `translation.json`.

---

## Testing
Robot Framework tests in `tests/`. Run in order by filename: install → test → uninstall.
