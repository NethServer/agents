# Redis, actions and the agent SDK

## Redis namespace ownership

Redis is the only state store. Nothing is persisted to the filesystem by an action.
The leader node runs the writable master; worker nodes run read-only replicas. The
leader is resolved through `cluster/environment NODE_ID`, then `node/<id>/vpn`.

| Prefix | Owner | Holds |
|---|---|---|
| `cluster/…` | cluster agent | environment, module_node, module_uuid, module_domains, repository/, backup_repository/, backup/, user_domain/, smarthost, subscription, override/modules |
| `node/<id>/…` | node agent | environment, vpn, ui_name |
| `module/<id>/…` | module agent | environment, flags, srv/, ui_name, ui_note |
| `task/<agent>/<task-id>/…` | Go agent | context, output, error, exit_code — all expire after a few hours |
| `<agent-id>/tasks` | any enqueuer | task queue, consumed with BRPOP |
| `<agent>/roles/<role>` | grants API | SET of action glob patterns |
| `roles/<username>` | grants API | HASH mapping agent_id to role |

Pub/sub channels: `progress/<agent>/task/<uuid>` carries task progress to the UI;
`<agent>/event/<event-name>` carries events between agents, for example
`cluster/event/module-added`. Event names are past tense.

Never write role keys directly. Use `cluster.grants.grant()` and its siblings in
`core/imageroot/usr/local/agent/pypkg/cluster/grants.py`, which handle the wildcard
expansion in the ACTION, ON and TO clauses. The public entry points are the
`grant-actions` and `revoke-actions` cluster actions.

For the exhaustive key list with types and descriptions, read `docs/core/database.md`.

## Where actions and events live

Four roots, each belonging to a different agent:

| Path under `core/imageroot` | Agent |
|---|---|
| `var/lib/nethserver/cluster/actions/` | cluster agent, leader only |
| `var/lib/nethserver/node/actions/` | node agent, one per node |
| `var/lib/nethserver/node/events/` | node agent event handlers |
| `usr/local/agent/actions/` | the module lifecycle actions every module inherits |

Cluster actions, leader only. There are 85 of them; the table names the groups and
a representative few, not the full set. `ls` the directory for that.

| Group | Actions |
|---|---|
| Module lifecycle | `add-module`, `remove-module`, `update-module`, `clone-module`, `import-module`, the `list-*` family |
| Node membership | `add-node`, `join-node`, `promote-node`, `remove-node` |
| User domains | `add-user`, `alter-user`, `add-internal-provider`, `add-external-provider`, `bind-user-domains` |
| Backup and restore | `add-backup`, `run-backup`, `add-backup-repository`, `restore-cluster`, `restore-module` |
| Cluster administration | `create-cluster`, `join-cluster`, `get-cluster-status`, `set-fqdn`, `grant-actions`, `revoke-actions`, `set-smarthost`, `set-subscription` |

Node actions, one set per node, 30 in total — again a sample. The event handlers,
in contrast, are the complete list.

| Group | Actions |
|---|---|
| Firewall | `add-custom-zone`, `add-rich-rules`, `add-public-service` |
| Networking | `add-tun`, `allocate-ports`, `deallocate-ports` |
| Module hosting | `add-module`, `remove-module`, `restart-module` |
| Maintenance | `update-os`, `update-core`, `start-support-session` |
| Events | `acl-changed`, `backup-destination-changed`, `backup-schedule-changed`, `default-instance-changed`, `leader-changed`, `subscription-changed`, `vpn-changed` |

The actions under `usr/local/agent/actions/` — `create-module`, `destroy-module`,
`clone-module`, `import-module`, `restore-module`, `update-module`, `get-status`,
`list-volumes`, `list-service-providers`, `transfer-state` — are inherited by every
module. Changing one changes the contract of every ns8-* module in existence.

> **⚠️ Only the `cluster` agent and `api-server` may LPUSH tasks into Redis.**
> Module agents submit tasks through the api-server HTTP API. `agent.tasks` therefore
> only works from an action step running on a cluster node, because the API server
> accepts agent credentials from loopback and the cluster VPN only. See
> `docs/core/agents.md`.

## Writing a core action step

`AGENTS.md` shows the Python skeleton and `core/agent/AGENTS.md` lists the exit codes
and the injected variables. Neither states the four rules below, and every one of them
is load-bearing in the existing core actions.

**stdout belongs to the action, logs go to stderr.** The agent captures stdout and
parses it as the action output. A stray `print()` corrupts it, and most existing core
action steps already follow the rule. Prefix a Python log line with a systemd
severity constant, or redirect once at the top of a shell script:

```python
import sys, agent
print("informational message", file=sys.stderr)
print(agent.SD_WARNING + "unexpected but recoverable", file=sys.stderr)
print(agent.SD_ERR + "critical failure", file=sys.stderr)
```

```bash
exec 1>&2   # everything below now goes to journald
```

`SD_INFO`, `SD_NOTICE`, `SD_WARNING` and `SD_ERR` are journal priority prefixes.
journald parses them to set the level.

**Signal a bad input differently from a broken invariant.** For input the user can
fix, set the task status and emit a field-level error list. The default exit code
after `validation-failed` is 10; overriding it with a small action-specific number is
normal, as `cluster/actions/set-smarthost/01validate_settings` does with 2, 3 and 4:

```python
agent.set_status('validation-failed')
json.dump([{'field': 'smarthost', 'parameter': 'smarthost',
            'value': data['smarthost'], 'error': 'cannot_connect_to_server'}],
          fp=sys.stdout)
sys.exit(3)
```

For an invariant that should never break, `agent.assert_exp(cond, "message")` prints a
stack trace to stderr and exits 2. Any non-zero exit halts the remaining steps. Read
the exit code table in `core/agent/AGENTS.md` before picking a number — part of the
range is reserved to the agent itself.

**Pick the right call for the right target.** `agent.tasks.run()` is a tracked RPC to
another agent's action and returns `{'exit_code': int, 'output': dict}`; check the
exit code yourself. `agent.run_helper()` is a local subprocess returning a
`CompletedProcess`; call `.check_returncode()` on it. Reaching for `run_helper` where
the work belongs to another agent bypasses the task framework, so nothing is tracked
and nothing shows up in the UI.

`run()` is one of five entry points, and `docs/core/agents.md` documents only that
one. A fan-out over several nodes should not be a loop of `run()` calls:

| Call | Returns | Use for |
|---|---|---|
| `run(agent_id, action, data)` | one result | a single tracked RPC |
| `run_nowait(...)` | a task id | fire and forget, poll later |
| `runp(tasks)` | a result per task, same order | one action across several agents at once |
| `runp_nowait(tasks)` | a task id per task | the same, without waiting |
| `runp_brief(tasks)` | the count of failures | a fan-out where only "did any fail" matters, errors already on stderr |

`run()` is itself a one-element `runp()`. Each entry of `tasks` is a dict with
`agent_id`, `action` and `data`. Beware that `runp` returns exceptions *inside* the
result list rather than raising, so a failed task is an `Exception` object where a
result was expected — `runp_brief` exists to absorb exactly that. `set-fqdn/20set_node_fqdn`
is the model: it validates every node in parallel, then acts on one.

**Secrets are obscured on the way into Redis, but only by suffix.** Before persisting
`task/<agent>/<task-id>/context`, the agent walks the payload and replaces any value
whose key *ends with* `password`, `secret`, `token`, `key` or `pass` with `"XXX"`
(the `sensitiveList` slice in `core/agent/htask.go`). `my_api_token` is masked;
`token_expiry` is not. Name
fields accordingly, and remember this only protects the stored task context — it is
not a substitute for keeping a credential out of `agent.set_env()`, which writes
plain text readable by every module on the node.

### The `agent` package is public API as much as the inherited actions

`core/imageroot/usr/local/agent/pypkg/` holds three packages: `agent`, the SDK every
action imports, `cluster`, leader-only helpers such as `grants.py`, and `node`.

`import agent` needs no path setup because `install-core.sh` drops a `pypkg.pth` into
the core interpreter's site-packages. The `PYTHONPATH` entries in an agent's
`state/agent.env` are unrelated — they add that agent's *own* extra packages, and
`05set_agentenv_path`, an `update-core` hook (`references/build-test-ship.md`), is what
keeps them in step.

No page in `docs/` is a reference for what `agent` exposes; mentions are scattered
through the module pages. Read the source before writing a helper that may already
exist — firewall zones and rich rules, port allocation, restic backup, volume
arguments, Traefik routes and certificates, service discovery and user domain binding
are all in there. `grep '^def ' pypkg/agent/__init__.py` is the index.

Every ns8-* module imports this package. A changed signature is a breaking change for
repositories you will never see, exactly like the inherited actions.

### Agent identity is not what the module documentation says

The cluster and node agents are instances of the same `agent@.service` template as
every module agent, but their `state/agent.env` overrides the defaults. One command
shows the whole mechanism — the default, the two overrides, and the unit that
consumes it:

```bash
grep -rn AGENT_BASEACTIONS_DIR core/imageroot
```

| Variable | Module agent | Cluster agent | Node agent |
|---|---|---|---|
| `AGENT_ID` | `module/<id>` | `cluster` | `node/1` |
| `REDIS_USER` | module credentials | `cluster` | `node/1` |
| `AGENT_BASEACTIONS_DIR` | `/usr/local/agent/actions` | *empty* | *empty* |

That last row matters. `--actionsdir` is repeatable, so a module agent serves the
inherited base actions plus its own. The cluster and node agents blank the variable
out and therefore serve **only** the actions in their own tree. Do not assume
`create-module` or `get-status` is reachable on them.

