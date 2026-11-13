# Redis, actions and the agent SDK

## Redis namespace ownership

Redis is the only state store. The leader runs the writable master, workers run
read-only replicas. `docs/core/database.md` has the full key list.

| Prefix | Owner |
|---|---|
| `cluster/…` | cluster agent |
| `node/<id>/…` | node agent |
| `module/<id>/…` | module agent |
| `task/<agent>/<task-id>/…` | Go agent, expires after a few hours |
| `<agent>/roles/<role>`, `roles/<username>` | grants API |

Never write role keys directly. Use `cluster.grants.grant()` and its siblings in
`core/imageroot/usr/local/agent/pypkg/cluster/grants.py`. They expand the wildcards in
the ACTION, ON and TO clauses. The public entry points are the `grant-actions` and
`revoke-actions` cluster actions.

## Where actions and events live

| Path under `core/imageroot` | Agent |
|---|---|
| `var/lib/nethserver/cluster/actions/` | cluster agent, leader only |
| `var/lib/nethserver/node/actions/` | node agent, one per node |
| `var/lib/nethserver/node/events/` | node agent event handlers |
| `usr/local/agent/actions/` | inherited by every module |

`ls` a directory for its actions. An inherited action may share a name with a cluster
action, like `update-module` or `restore-module`, but it is different code.

> **⚠️ Only the `cluster` agent and `api-server` may LPUSH into `cluster/tasks`.**
> Measured with `ACL DRYRUN` on a live leader (core 3.22.0-dev.3): `cluster` and
> `api-server` are accepted on both `cluster/tasks` and `node/<id>/tasks`; a node agent
> is accepted on its own `node/<id>/tasks` and refused on `cluster/tasks`; a module agent
> is refused on both and reaches only `module/<id>/tasks`.
>
> `agent.tasks` still works from any agent, subject to its grants. For the transports and
> the `endpoint=` argument, see `docs/core/agents.md`.
>
> Check it on any node without writing anything:
> `redis-cli ACL DRYRUN module/<id> LPUSH cluster/tasks x`

## Writing a core action step

`AGENTS.md` shows the Python skeleton. `core/agent/AGENTS.md` lists the exit codes,
the injected variables and the `SD_*` log prefixes. The rules below are not written there.

**stdout is the action output.** The agent parses it, and a stray `print()` corrupts
it. Print logs to stderr, or start a bash step with `exec 1>&2`.

**Bad input and broken invariant exit differently.** For input the user can fix, call
`agent.set_status('validation-failed')`, dump a list of
`{'field', 'parameter', 'value', 'error'}` dicts to stdout and exit.
`cluster/actions/set-smarthost/01validate_settings` is the model. For an invariant,
`agent.assert_exp(cond, "message")` exits 2 with a stack trace. Pick a custom exit code
in `1-7` or `32-255`: `8-31` belong to the agent.

**`agent.tasks.run()` targets another agent, `agent.run_helper()` runs locally.**
`run()` returns `{'exit_code': int, 'output': dict}`, check the exit code yourself.
`run_helper()` returns a `CompletedProcess` and does not raise, call
`.check_returncode()` on it. Using `run_helper` for another agent's work
bypasses the task framework: nothing is tracked, nothing shows in the UI.

`docs/core/agents.md` documents only `run()`. There are five entry points:

| Call | Returns | Use for |
|---|---|---|
| `run(agent_id, action, data)` | one result | a single tracked RPC |
| `run_nowait(...)` | a task id | fire and forget |
| `runp(tasks)` | a result per task, same order | one action on several agents |
| `runp_nowait(tasks)` | a task id per task | the same, without waiting |
| `runp_brief(tasks)` | the count of failures | only "did any fail" matters |

Each entry of `tasks` is a dict with `agent_id`, `action` and `data`. `runp` returns
exceptions inside the result list instead of raising. `set-fqdn/20set_node_fqdn` is the
model for a fan-out.

**Secret masking works by key suffix.** Before storing the task context, the agent
replaces with `"XXX"` any value whose key ends with `password`, `secret`, `token`, `key`
or `pass` (`sensitiveList` in `core/agent/htask.go`). `my_api_token` is masked,
`token_expiry` is not. This does not cover `agent.set_env()`, which writes plain text
readable by every module on the node.

## The Python packages are public API

`core/imageroot/usr/local/agent/pypkg/` holds `agent`, `cluster` and `node`.
`install-core.sh` drops a `pypkg.pth` into the core interpreter, so all three import
from any agent, module agents included. Every ns8-* module imports `agent`.

`cluster` is said to be leader-only, but two submodules are not. `cluster.backup` is
used by `node/bin/run-backup`, `node/bin/rclonegwctl`,
`node/actions/validate-backup-destination` and the inherited `list-backup-repositories`.
`cluster.userdomains` is imported by `agent/ldapproxy.py`. `node.ports_manager` runs on
every node. Grep the callers before changing a signature.

The `PYTHONPATH` entries in an agent's `state/agent.env` are unrelated. They add that
agent's own packages, kept in step by the `05set_agentenv_path` update hook.

No page in `docs/` lists what `agent` exposes. `grep '^def ' pypkg/agent/__init__.py`
is the index. Check it before writing a helper: firewall, ports, restic, volumes,
Traefik, certificates, service discovery and user domains are already there. Read the
`redis_connect()` docstring before opening a connection.

## Cluster and node agents serve only their own actions

The cluster and node agents use the same `agent@.service` template as module agents.
Their `state/agent.env` overrides the defaults:

| Variable | Module agent | Cluster agent | Node agent |
|---|---|---|---|
| `AGENT_ID` | `module/<id>` | `cluster` | `node/1` |
| `REDIS_USER` | module credentials | `cluster` | `node/1` |
| `AGENT_BASEACTIONS_DIR` | `/usr/local/agent/actions` | *empty* | *empty* |

With `AGENT_BASEACTIONS_DIR` empty, the cluster and node agents do not serve the
inherited actions. `create-module` or `get-status` is not reachable on them.
`grep -rn AGENT_BASEACTIONS_DIR core/imageroot` shows the whole mechanism.
