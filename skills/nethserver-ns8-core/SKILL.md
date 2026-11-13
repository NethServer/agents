---
name: nethserver-ns8-core
description: 'Use when working in NethServer/ns8-core — core/agent/, core/api-server/, core/api-moduled/, core/imageroot/, core/ui/, core/tests/, update-core.d/. Read it before searching the tree by hand: cluster and node actions, events, the Go builds, the core UI, the test loops, update-core hooks. Also use on core symptoms: a core UI page that hangs or loads slowly, a cluster task that never completes, an action step that halts the steps after it, a Go build that fails on a second func main, an update-core hook that runs without effect, app versions missing from the software center. Not for ns8-* modules (use nethserver-ns8-module) or live clusters (nethserver-admin).'
---

# NethServer 8 core development

Read the reference row for your task before your first grep, not only before you write:
diagnosing an existing behaviour counts. Read that one file, not all of them.

## Scope

ns8-core is a production platform with thousands of installations. Breaking changes
are not allowed. The repository documents most conventions itself (`AGENTS.md`, the
per-component `AGENTS.md` and `README.md`, `docs/`), and this skill does not repeat
them. `references/repository-and-docs.md` maps each question to the file that answers it.

For an ns8-* module use `nethserver-ns8-module`. For a live cluster use `nethserver-admin`.

Cite files and identifiers, never line numbers. A stale line number silently points at
the wrong code. A renamed identifier returns nothing, so you notice.

## Reference map

| Task | Read |
|---|---|
| Where the repository documents itself: the `AGENTS.md`/`README.md`/`docs/` delegation tables, manual and handbook URLs, repository tree, what "core" covers beyond this repository, `core_module` membership, the two `func main` in `core/api-server`, the three independent `go.mod` | `references/repository-and-docs.md` |
| Redis key ownership and pub/sub channels, role grants, where cluster and node actions and event handlers live, the inherited module actions, writing an action step (stdout/stderr, `agent.set_status`, `agent.assert_exp`, exit codes, `agent.tasks` entry points, secret masking), the `agent`/`cluster`/`node` Python packages, agent identity and `AGENT_BASEACTIONS_DIR` | `references/actions-and-agent-sdk.md` |
| Calling an action from a UI (`createClusterTask`, `createNodeTask`, `createModuleTaskForApp`, the `ForApp` suffix, `taskData`), Vue 2 / Carbon v10 / Vue CLI 4 generations, `@nethserver/ns8-ui-lib` versions and local tarball testing, `core.css` shipped to every module UI, build constraints, running the dev server against a real node | `references/core-ui.md` |
| api-server authentication, action-based authorization, audit log, Melody WebSocket bridge, api-moduled — where `core/api-server/AGENTS.md` answers, and the four things it does not: the `TODO` on the GET bypass, the `/api/2FA` exemptions, grants re-read on every request, `melody.New()` left unconfigured | `references/api-server.md` |
| The three test loops and their cost, `run-ns8-tests`, Robot suite layout, `shellcheck`, building an image and pointing a test node at it, `cluster/override/modules`, `update-core` stages and its three hook directories, `runagent` and the cluster-wide CLI helpers | `references/build-test-ship.md` |

## Always applies

- stdout is the action output. Log to stderr. (`references/actions-and-agent-sdk.md`)
- A non-zero exit in an action step halts the next steps. In an `update-core` hook it
  only warns. (`references/build-test-ship.md`)
- Only the `cluster` agent and api-server may LPUSH into `cluster/tasks` and a node
  queue. Other agents go through `agent.tasks`, see `docs/core/agents.md`.
  (`references/actions-and-agent-sdk.md`)
- The inherited actions under `core/imageroot/usr/local/agent/actions/` and the
  `agent`, `cluster` and `node` Python packages are public API. Grep the callers
  before changing a signature. (`references/actions-and-agent-sdk.md`)
- Store state in Redis, never on the filesystem. Filesystem state does not replicate
  and is lost on restore.
- An image never migrates an installed cluster. A migration needs an idempotent,
  executable script in an `update-core` hook directory. (`references/build-test-ship.md`)
- Build api-server with `go build api-server.go`, not `go build .`. Run `go fmt` in the
  Go module you touched. (`references/repository-and-docs.md`)
- Keep `validate-input.json` and `validate-output.json` in step with their action. The
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
