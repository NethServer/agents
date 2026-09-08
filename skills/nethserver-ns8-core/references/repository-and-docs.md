# ns8-core repository and its own documentation

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

## Delegation tables

Do not restate what the repository already documents. Read the authoritative source
instead. The repository's own files, first:

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

When a claim here needs checking, grep for the identifier it names.

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

