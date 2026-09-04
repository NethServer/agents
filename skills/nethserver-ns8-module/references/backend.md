# Backend: actions, events, services

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
