---
name: nethserver-ns8-core
description: 'Navigate and modify the ns8-core repository itself — the Go agent, api-server, api-moduled, the cluster and node actions and events, the core UI, and the core test suites. Use inside a checkout of NethServer/ns8-core, the tree carrying core/agent/, core/api-server/, core/api-moduled/, core/imageroot/ and core/build-image.sh. For writing ns8-* application modules use nethserver-ns8-module; for operating a live cluster over SSH use nethserver-admin. Answers questions such as: why go build fails in core/api-server; where a cluster or node action lives and who may enqueue it; why an action step corrupts its output or loses its logs; how to run the core UI with hot reload against a real node; why a modern Vue or Carbon idiom will not build here; which of the three test loops to run; how to push a branch image onto a test node; why an update hook did not run; how a change reaches clusters that are already installed'
---

# NethServer 8 core development

ns8-core is a production platform with thousands of installations. Breaking changes
are not allowed. Read the delegation table below before writing anything: most
conventions are already documented inside the repository, and this skill deliberately
does not repeat them.

Primary references:

- Repository: `https://github.com/NethServer/ns8-core`
- Dev manual, generated from `docs/`: `https://nethserver.github.io/ns8-core/`
- Product documentation hub: `https://docs.nethserver.org/`
- Administrator manual, the user-facing behaviour core has to preserve:
  `https://docs.nethserver.org/docs/administrator-manual`
- Development handbook, issues, PRs, version numbering:
  `https://handbook.nethserver.org/`
- Reusable CI workflows and the `run-ns8-tests` helper:
  `https://github.com/NethServer/ns8-github-actions`

## Scope and delegation

This skill covers ns8-core as an object of development. It does not restate what the
repository already documents. Read the authoritative source instead.

The repository's own files, first:

| Question | Read |
|---|---|
| Component table, architecture overview | `AGENTS.md` (Architecture, Components) |
| Action step numbering, Python action skeleton | `AGENTS.md` (How actions work) |
| UI task/event model, `eventId` generation | `AGENTS.md` (UI task/event model) |
| Build commands, buildah, CGO flags | `AGENTS.md` (Build) |
| Lint commands | `AGENTS.md` (Lint) |
| Commit style, branch naming, JSON schema rules, Weblate | `AGENTS.md` (Conventions) |
| Agent task protocol, `AGENT_COMFD`, exit codes, env vars | `core/agent/AGENTS.md` |
| api-server routes, JWT config, environment variables | `core/api-server/AGENTS.md` |
| api-moduled handler layout, `AMLD_*` variables | `core/api-moduled/AGENTS.md` |

Each Go component ships two documents, and the `AGENTS.md` above is the shorter one.
The `README.md` beside it is the reference — three to four times the length, and the
only place several protocols are written down at all:

| Question | Read |
|---|---|
| Action execution model, file descriptors, action outcome and validation | `core/agent/README.md` |
| `set-status`, `set-progress`, `set-weight` command syntax | `core/agent/README.md` |
| Builtin actions every agent serves, `list-actions` and `cancel-task` | `core/agent/README.md` |
| WebSocket frame protocol: `logs-start`, `logs-stop`, task events | `core/api-server/README.md` |
| Login, basic auth and 2FA API lists, network access restrictions | `core/api-server/README.md` |
| `api-server-logs` usage and commands | `core/api-server/README.md` |
| Implementing an api-moduled handler, command execution, authorization | `core/api-moduled/README.md` |

Then the developer manual. `docs/core/` documents the platform subsystems, and every
one of them is implemented in this repository unless the page says otherwise:

| Subsystem | Read |
|---|---|
| Redis key reference, types and ownership | `docs/core/database.md` |
| Event catalogue, channel naming, publishing | `docs/core/events.md` |
| Agent, task queue, `agent.tasks` API | `docs/core/agents.md` |
| JSON Schema validation framework | `docs/core/validation.md` |
| Test suite reference | `docs/core/testing.md` |
| API server design, authentication, audit | `docs/core/api_server.md` |
| Where files land on a node, `/usr/local/{bin,sbin}` | `docs/core/filesystem.md` |
| Loki, promtail, `logcli`, log retention | `docs/core/logs.md` |
| firewalld zones, rich rules, public services | `docs/core/firewall.md` |
| WireGuard mesh between nodes | `docs/core/vpn.md` |
| TUN devices handed to rootless containers | `docs/core/tun.md` |
| `ports_manager`, the per-node `ports.sqlite` | `docs/core/port_allocation.md` |
| Traefik routes, TLS certificates, ACME | `docs/core/proxy_certificates.md` |
| Account providers, LDAP proxy, domain binding | `docs/core/user_domains.md` |
| Restic repositories, schedules, restore | `docs/core/backup_restore.md` |
| Cloning an instance, and how it differs from restore | `docs/core/clone_module.md` |
| Core and module update flow, the update hooks | `docs/core/updates.md` |
| Application repositories and their indexes | `docs/core/software_repositories.md` |
| Prometheus, node_exporter, alerting | `docs/core/metrics.md` |
| Telemetry and `phonehome.timer` | `docs/core/phone_home.md` |
| Subscription and its effect on repositories | `docs/core/subscription.md` |
| Outbound SMTP relay configuration | `docs/core/smarthost.md` |

| UI | Read |
|---|---|
| Core UI components, shortcuts, notification rules, dev setup | `docs/ui/core.md` |
| ns8-ui-lib development, release and local tarball install | `docs/ui/library.md` |
| Module UI guidelines | `docs/ui/modules.md` |
| Localization workflow | `docs/ui/translation.md` |

| Process | Read |
|---|---|
| Installing a custom core image, module override | `docs/quickstart.md` |
| Release flow for the core itself | `docs/development_process.md` |
| Architecture rationale, what runs where | `docs/design.md` |
| Image build pipeline and SBOM generation | `docs/build_system.md` |
| How the API documentation is generated and published | `docs/api.md` |

Two of these carry consequences worth knowing before reading them. `docs/api.md`
explains that the API reference is generated from the `validate-input.json` and
`validate-output.json` files and published to an `apidoc-<branch>` branch: keeping a
schema in step with its action is not housekeeping, it is what publishes the
documentation. And `CONTRIBUTING` delegates the entire contribution process to
`docs/development_process.md`, so that page, not this skill, is the authority on
releasing.

This skill cites files and identifiers, never line numbers. The code moves, and a
stale line number points at the wrong thing without ever saying so, while a name that
has been renamed returns nothing and tells you it moved. When a claim here needs
checking, grep for the identifier it names.

`docs/` is a Jekyll site published at nethserver.github.io/ns8-core, and it is more
detailed than the code comments. Treat it as ground truth. Do not confuse it with the
separate `NethServer/ns8-docs` repository, which holds end-user documentation.

## Repository map

```
core/agent/          Go daemon. Pops tasks from Redis, runs action steps as subprocesses.
core/api-server/     Go + Gin. REST + WebSocket + JWT + SQLite audit. Talks to Redis.
core/api-moduled/    Go. Stateless per-module REST server. No Redis, no audit, no WS.
core/imageroot/      Filesystem tree baked into the core image: cluster and node
                     agents, their actions and events, the Python agent package,
                     cluster-wide CLI helpers, systemd units.
core/ui/             Vue 2 + Carbon admin UI. Consumes the published
                     @nethserver/ns8-ui-lib package.
core/tests/          Robot Framework integration suite, run against a live cluster.
core/build-image.sh  Builds every image with buildah. Source of truth, no Makefile.
core/install.sh      Bare-metal bootstrap for a fresh node.
core/rclone/         Sidecar image trees. build-image.sh assembles each one with
core/rsync/          buildah from an Alpine base, alongside the redis and restic
core/support/        images. None of them has a Containerfile. support/ is the
                     OpenVPN client behind the start-support-session node action.
docs/                Jekyll developer manual.
```

"Core" is bigger than this repository. A handful of modules are versioned with the
core and updated by it rather than by the user. They live in their own `ns8-*`
repositories, but `update-core` updates their instances as part of a core release, so
a core change that alters a contract they rely on has to land in step with them.

Which modules those are is not decided here, so do not trust a list written down in
this file or any other. Membership is the `core_module` entry of the Redis set
`module/<id>/flags`. It usually arrives from the image label `org.nethserver.flags`,
declared in the module's own `build-images.sh`, but a module may also write it itself
— `ns8-samba` does, from `import-module/01core_module`. Ask a live cluster instead:

```bash
api-cli run list-core-modules | jq .
```

Two things in this tree are easy to get wrong:

> **⚠️ `core/api-server/api-server-logs.go` is a second binary in the same package
> directory.** `go build .` does not produce it. Build the server explicitly with
> `go build api-server.go`.

> **⚠️ The three Go components are three independent modules**, each with its own
> `go.mod`. There is no workspace file. Run `go fmt` in the directory you touched.

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
`05set_agentenv_path`, the update hook cited later, is what keeps them in step.

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

## Calling an action from the core UI

`AGENTS.md` names `createModuleTaskForApp` as an example and moves on. There are in
fact five task services in `@nethserver/ns8-ui-lib`, and picking the wrong one is a
silent mistake: the call reaches the wrong queue, or no queue at all.

| Target agent | Method | POST endpoint | Redis queue |
|---|---|---|---|
| cluster | `createClusterTask(taskData)` | `/cluster/tasks` | `cluster/tasks` |
| node | `createNodeTask(nodeId, taskData)` | `/node/<id>/tasks` | `node/<id>/tasks` |
| module | `createModuleTaskForApp(moduleId, taskData)` | `/module/<id>/tasks` | `module/<id>/tasks` |

The `ForApp` suffix is not about the target, it is about the **caller**. A bare method
reads the API URL from `this.$root.apiUrl`, which only exists in the core shell. A
`ForApp` method reads `window.parent.core.$root.apiUrl`, which is how a module UI
running in an iframe reaches the shell that hosts it. `createClusterTaskForApp` and
`createNodeTaskForApp` are the iframe counterparts of the first two rows.

There is no bare `createModuleTask`. The core UI calls `createModuleTaskForApp`
anyway, and it works because `core/ui/src/main.js` assigns the root Vue instance to
`window.core`: in the top window, `window.parent.core` resolves to itself.

`taskData` is the same shape everywhere:

```js
const eventId = this.getUuid();
this.$root.$once(`${taskAction}-completed-${eventId}`, this.onCompleted);

await this.createClusterTask({
  action: taskAction,
  data: { /* action input, validated against validate-input.json */ },
  extra: {
    title: this.$t("action." + taskAction),
    description: this.$t("common.processing"),
    isNotificationHidden: true,   // omit to let the notification drawer show it
    eventId,
  },
});
```

`data` is what the action step reads from stdin. `extra` never reaches the action; it
drives the notification drawer and the progress bar. Set `isProgressNotified: true`
in `extra` when the action calls `agent.set_progress()`.

## Working on the core UI

`AGENTS.md` says Vue 2 and Carbon, and points at `@nethserver/ns8-ui-lib` for the task
services. Four things it leaves out cost real time.

**The stack is a major generation behind the ecosystem defaults, and writing modern
idioms here produces code that does not build.** Renovate manages npm and gomod with
an automerge preset, so patch and minor numbers move on their own — always read
`core/ui/package.json` for the current pin rather than trusting any number written
down elsewhere, this file included. The generations move rarely, and they are what
changes the code you write:

| Area | Generation in use | Do not reach for |
|---|---|---|
| Vue | 2.x, recent enough for the composition API | Vue 3, or `<script setup>` |
| Router and store | `vue-router` 3, `vuex` 3 | Router 4, Vuex 4, Pinia |
| Design system | Carbon v10 (`carbon-components` 10, `@carbon/vue` 2) | Carbon v11, what the online docs show |
| Build tooling | Vue CLI 4, so webpack | Vite |
| Vue lint rules | `eslint-plugin-vue` 6 | the current rule set |

**ns8-ui-lib is an external package, not a directory of this repository.** It lives at
`NethServer/ns8-ui-lib`, and its components are the ones prefixed `Ns` — `NsButton`,
`NsInlineNotification`. Two facts about it are easy to get wrong.

The published version and the consumed version drift apart on purpose. Every
consumer pins with a caret, and a caret never crosses a major, so a library major
release reaches nobody until each repository bumps it deliberately. The core UI, and
every module repository, sit wherever they were last bumped — in practice they are
spread over several majors at any time. Check all three before assuming a component
or a prop exists:

```bash
grep ns8-ui-lib core/ui/package.json          # what the core UI consumes
npm view @nethserver/ns8-ui-lib version       # what is published
grep ns8-ui-lib <module>/ui/package.json      # what a given module consumes
```

Shipping a library fix does need an upstream release (`npm run publish:patch|minor|major`,
see `docs/ui/library.md`), but *testing* one does not: `npm run build-pack` produces a
tarball that installs straight into this repository with
`yarn add /path/to/nethserver-ns8-ui-lib-x.y.z.tgz`. Use that to validate a change
before releasing it.

**Core UI styling is not local to the core UI.** After the build, `build-image.sh`
runs `tidy` over `dist/index.html`, collects the emitted `app~*.css` chunks and
concatenates them into a single `dist/css/core.css`
(`core/build-image.sh`, under the echo "Provide core style to external modules"). Every
external module UI loads that file. A change to a shared style rule ships to every
module in the cluster, not just to the screen being worked on.

**The build has two constraints that bite locally.** It runs on the Node image pinned
in `core/build-image.sh`, with `NODE_OPTIONS=--openssl-legacy-provider`, which
webpack 4 requires on any recent Node. And `yarn install --immutable` means a
lockfile that drifts from `package.json` fails the build rather than being repaired
silently.

Lint is `plugin:vue/essential` plus `eslint:recommended` and prettier
(`core/ui/.eslintrc.js`). That is the loosest Vue rule set; `yarn lint` passing says
very little about correctness.

### Running the core UI on localhost against a real node

Unlike the backend, the UI has a live loop: a dev server with hot reload on the
workstation, talking to a real leader node. `docs/ui/core.md` has the full procedure,
including the Podman and VS Code Dev Containers variants. Three steps in it are the
ones that block people:

1. Copy `core/ui/public/config/config.development.js.sample` to
   `config.development.js` and set `API_ENDPOINT` and `WS_ENDPOINT` to the leader
   node address.
2. Disable the CORS check on that node, otherwise every request is rejected:

   ```bash
   echo GIN_MODE=debug >> /etc/nethserver/api-server.env
   systemctl restart api-server
   ```

3. Accept the self-signed certificate once, by opening
   `https://<node>/cluster-admin/api/login` in a browser tab. Use the same FQDN or IP
   there as in `config.development.js` — a certificate accepted on the hostname does
   not cover the address, and the requests keep failing.

Then start the dev server. `core/ui/Containerfile` builds the image for it:

```bash
cd core/ui
podman build -t ns8-core-dev .
podman run -ti -v $(pwd):/app:Z --network=host --name ns8-core --replace ns8-core-dev serve
```

`--network=host` is not optional, hot reload does not work without it. Swapping the
trailing `serve` for `build` or `storybook` runs those instead. Running the dev server
and Storybook at the same time is the one combination that needs a different shape,
because a second `yarn` in the same container fails — start `serve` as above, then
attach to the running container:

```bash
podman exec -ti ns8-core yarn storybook
```

A plain `yarn serve` on the workstation and a VS Code Dev Containers setup are the two
other supported paths; `docs/ui/core.md` describes both.

## api-server internals

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
- Task queues and result keys are the ones listed above: `cluster/tasks`,
  `node/<id>/tasks`, `module/<id>/tasks`, and `task/<agent>/<task-id>/…`.

api-moduled is a different animal. It has no Redis client, no audit database and no
WebSocket. Routing is filesystem-based: `POST /api/<handler>` executes
`handlers/<handler>/post` with the request JSON on stdin. Do not add cluster
awareness to it.

## Test loops

Three loops, with very different costs. Pick the smallest one that can fail.

```bash
# 1. Go agent, seconds, no cluster needed.
#    Builds the binary, starts an ephemeral Podman Redis, runs the Robot suite
#    in core/agent/test/ against fixture actions and events.
cd core/agent && bash test-agent.sh

# 2. UI. There is no unit suite — package.json has no test script. This is a
#    linter, and a loose one. The real UI cases are Robot cases in loop 3.
cd core/ui && yarn lint

# 3. Integration, minutes, requires a live leader node reachable over SSH.
#    run-ns8-tests comes from the external NethServer/ns8-github-actions repo.
#    UI cases are tagged ui and excluded unless RUN_UI_TESTS is set.
cd core && run-ns8-tests <LEADER_NODE> [robot_options]
cd core && RUN_UI_TESTS=true run-ns8-tests <LEADER_NODE>
```

The integration suite reads `SSH_KEYFILE`, `RUN_UI_TESTS` and `COREMODULES` from the
environment. Suites live in numbered directories such as
`core/tests/10__cluster_sanity/`, share `keywords.resource`, and follow the same
numbering discipline as action steps: `00` installs, `99` uninstalls. Use
`--exclude install` and `--exclude uninstall` to iterate against a cluster that is
already provisioned.

Shell code must pass `shellcheck`. There is no Python linter configuration in the
repository; follow the style of the surrounding action scripts.

## Iterating against a test node

This concerns the backend. The UI has its own live loop, described above.

There is no rsync or scp helper that pushes a working tree onto a running node. The
loop goes through a container image:

1. `cd core && bash build-image.sh` — buildah, reusing the persistent
   `gobuilder-core` and `nodebuilder-core` containers for caching.
2. `buildah push` the image to a personal tag on ghcr.io.
3. On the test node, `podman rmi` the tag first if it was already pulled, otherwise
   the old layers are reused.
4. Point the cluster at the new image. For a **core** image, override the resolution
   map:

   ```bash
   redis-cli hset cluster/override/modules <image-name> <image-url>
   # e.g. redis-cli hset cluster/override/modules samba ghcr.io/nethserver/samba:rootless
   ```

   The hash maps an image *name* to a full URL and is read by
   `core/imageroot/var/lib/nethserver/cluster/actions/add-module/50update`. For an
   application module the commands are direct instead: `add-module <image-url>
   <node-id>` for a new instance, `update-module <image-url> <instance-id> --force` to
   re-push a mutable tag onto an existing one — same `--force`, same reason as on
   `update-core`.

`core/install.sh` accepts custom core images as positional arguments, which is the
fastest path when bootstrapping a throwaway node from a branch build.

## Shipping a change to existing clusters

Building an image and installing it on a throwaway node proves the code runs. It does
not migrate a cluster that is already installed. A new Redis key, a changed grant, a
renamed unit: none of it reaches an existing installation unless an update hook does
it. This is the part `AGENTS.md` does not mention at all, and `docs/core/updates.md`
is the reference.

`update-core ghcr.io/nethserver/core:<tag>` runs in two stages. The first updates the
core image on every node; the second lets the leader update the core modules. Three
hook directories are executed along the way, and the one to pick depends on when the
change has to happen:

| Directory under `core/imageroot` | Stage | Runs on |
|---|---|---|
| `var/lib/nethserver/node/update-core.d/` | 1, after the image is replaced | every node |
| `var/lib/nethserver/cluster/update-core-pre-modules.d/` | 2, before core modules update | leader |
| `var/lib/nethserver/cluster/update-core-post-modules.d/` | 2, after they update | leader |

Five rules govern those scripts, and the first two are the ones that bite:

- A file without the executable bit is **skipped**, and the message saying so is
  emitted at debug severity. A hook committed without `chmod +x` never runs and
  nothing visible says why.
- They run in alphabetical order, which is why the existing ones are numbered
  (`05set_agentenv_path`, `10reload_agents`, `50update_grants`, `95cleanup_images`).
- A non-zero exit prints a warning and execution **continues** with the next script.
  This is the opposite of an action, where a non-zero step aborts the sequence. A hook
  cannot stop a bad update; it can only decline to make things worse. The two runners
  reach that outcome differently: the node loop in `update-core/60run_scriptdir` never
  tracks failures, while `cluster/bin/run-scriptdir` counts them and exits 1 — a code
  its only caller, `update-core/70update_modules`, then discards. Reading the cluster
  runner alone suggests failures propagate. They do not.
- A hook can be run **more than once**, so it must be idempotent. Write it to converge
  on the desired state, never to apply a delta.
- The scripts come from the newly installed image, not the one being replaced. A hook
  therefore always describes the migration *into* its own version.

Read the existing hooks before writing one. `50update_grants` exists on both the node
and the cluster side and is a good model for a converging script.

Two details of the first stage matter during development. The node compares the image
tag with the installed one as Semver and installs only if it is greater. A tag that is
not valid Semver — a branch name — does not merely lose that comparison, it is
assigned `0.0.0` as the incoming version while a non-Semver *installed* tag is
assigned `9999.9999.9999`, so `update-core/50update` exits before pulling anything.
That comparison, not the pull, is what stops a branch build. Below it sits a second
effect in the same direction: without `--force` the pull runs through
`podman-pull-missing`, which fetches only a tag absent from local storage. Hence
`--force`, and hence a branch tag that appears to do nothing:

```bash
update-core ghcr.io/nethserver/core:my-branch --force
update-core ghcr.io/nethserver/core:<tag> --nodes 1 2   # discouraged outside development
```

Additional images listed in the core image label `org.nethserver.images` are pulled
along with it. And if the first stage fails on any node, the leader aborts the whole
update before the second stage begins.

## Developer CLI helpers

`core/imageroot/usr/local/bin/` and `usr/local/sbin/` install the cluster-wide
commands — `api-cli`, `runagent`, `volumectl`, `acl-load`, `switch-leader`,
`update-core`, `grant-actions` and the rest. The `nethserver-admin` skill documents
them from the operator's side; use it rather than rediscovering them here.

One of them is a development tool more than an operational one. `runagent` executes a
command inside an agent's environment, with that agent's `AGENT_ID`, `REDIS_USER`,
`PATH` and working directory already set:

```bash
runagent -l                       # which agents are running
runagent python3 ./50update       # -m defaults to cluster
runagent -m node ./50update       # the node agent
runagent -m <module_id> <command> # a module agent
```

It changes directory to that agent's `AGENT_STATE_DIR` first; `-c` keeps the current
directory instead, which is what you want when replaying a step straight out of a
source tree. That is how a single action step gets exercised by hand while it is being
written, without building and pushing an image.

## Common mistakes

> **⚠️ WRONG:** writing state to a file under `/var/lib` inside an action.
> **CORRECT:** store it in Redis via `agent.redis_connect()`. Filesystem state does
> not replicate to other nodes and is lost on module restore.

> **⚠️ WRONG:** shipping a change that needs migrating and stopping at the image.
> **CORRECT:** add an idempotent script to the matching `update-core` hook directory.
> Nothing else migrates an installed cluster.

> **⚠️ WRONG:** assuming an inherited action under `usr/local/agent/actions/` is core-
> internal. **CORRECT:** treat it as public API. Every ns8-* module inherits it.
