---
name: nethserver-ns8-core
description: 'Use when working in NethServer/ns8-core — core/agent/, core/api-server/, core/api-moduled/, core/imageroot/, core/ui/, core/tests/, update-core.d/. Read it before searching the tree by hand: cluster and node actions, events, the Go builds, the core UI, the test loops, update-core hooks. Not for ns8-* modules (use nethserver-ns8-module) or live clusters (nethserver-admin).'
---

# NethServer 8 core development

Read the reference file for your task before writing anything. Do not read all of them.

## Scope

ns8-core is a production platform with thousands of installations. Breaking changes
are not allowed. Most conventions are already documented inside the repository —
`AGENTS.md`, the per-component `AGENTS.md` and `README.md`, and `docs/` — and this
skill deliberately does not repeat them. `references/repository-and-docs.md` maps
every question onto the file that answers it; read that map before grepping.

This skill covers ns8-core as an object of development. For writing an ns8-* module
use `nethserver-ns8-module`; for operating a live cluster use `nethserver-admin`.

Cite files and identifiers, never line numbers. Code moves, and a stale line number
points at the wrong thing without ever saying so, while a renamed identifier returns
nothing and tells you it moved.

## Reference map

| Task | Read |
|---|---|
| Where the repository documents itself: the `AGENTS.md`/`README.md`/`docs/` delegation tables, manual and handbook URLs, repository tree, what "core" covers beyond this repository, `core_module` membership, the two `func main` in `core/api-server`, the three independent `go.mod` | `references/repository-and-docs.md` |
| Redis key ownership and pub/sub channels, role grants, where cluster and node actions and event handlers live, the inherited module actions, writing an action step (stdout/stderr, `agent.set_status`, `agent.assert_exp`, exit codes, `agent.tasks` entry points, secret masking), the `agent`/`cluster`/`node` Python packages, agent identity and `AGENT_BASEACTIONS_DIR` | `references/actions-and-agent-sdk.md` |
| Calling an action from a UI (`createClusterTask`, `createNodeTask`, `createModuleTaskForApp`, the `ForApp` suffix, `taskData`), Vue 2 / Carbon v10 / Vue CLI 4 generations, `@nethserver/ns8-ui-lib` versions and local tarball testing, `core.css` shipped to every module UI, build constraints, running the dev server against a real node | `references/core-ui.md` |
| api-server authentication, action-based authorization and the GET bypass, SQLite audit log, Melody WebSocket bridge, and how api-moduled differs | `references/api-server.md` |
| The three test loops and their cost, `run-ns8-tests`, Robot suite layout, `shellcheck`, building an image and pointing a test node at it, `cluster/override/modules`, `update-core` stages and its three hook directories, `runagent` and the cluster-wide CLI helpers | `references/build-test-ship.md` |

## Always applies

- stdout belongs to the action output — every log line goes to stderr, prefixed with a
  journal severity constant in Python or after `exec 1>&2` in bash. (`references/actions-and-agent-sdk.md`)
- Any non-zero exit from an action step halts the remaining steps. An `update-core`
  hook is the opposite: a non-zero exit only warns and the next script still runs.
  (`references/actions-and-agent-sdk.md`, `references/build-test-ship.md`)
- Only the `cluster` agent and api-server may LPUSH tasks into Redis, so `agent.tasks`
  works only from an action step running on a cluster node. (`references/actions-and-agent-sdk.md`)
- The actions under `core/imageroot/usr/local/agent/actions/` and the `agent` Python
  package are public API — a changed signature breaks ns8-* repositories you will
  never see. (`references/actions-and-agent-sdk.md`)
- Store state in Redis, never on the filesystem: filesystem state does not replicate
  and is lost on restore. (`references/actions-and-agent-sdk.md`)
- An image never migrates an installed cluster. A change needing migration also needs
  an idempotent script in the matching `update-core` hook directory — and a hook
  without the executable bit is skipped with only a debug-level message.
  (`references/build-test-ship.md`)
- `go build .` does not build api-server: `api-server-logs.go` is a second `func main`
  in the same package directory, so build it as `go build api-server.go`. The three Go
  components are three independent modules with no workspace file — run `go fmt` in the
  directory you touched. (`references/repository-and-docs.md`)
- Keep `validate-input.json` and `validate-output.json` in step with their action: the
  published API reference is generated from them. (`references/repository-and-docs.md`)

## Common mistakes

> **⚠️ WRONG:** writing state to a file under `/var/lib` inside an action.
> **CORRECT:** store it in Redis via `agent.redis_connect()`.

> **⚠️ WRONG:** shipping a change that needs migrating and stopping at the image.
> **CORRECT:** add an idempotent script to the matching `update-core` hook directory.

> **⚠️ WRONG:** assuming an inherited action under `usr/local/agent/actions/` is core-
> internal. **CORRECT:** treat it as public API. Every ns8-* module inherits it.

> **⚠️ WRONG:** looping `agent.tasks.run()` over several nodes.
> **CORRECT:** one `runp()` call, and remember it returns exceptions inside the result
> list instead of raising.
