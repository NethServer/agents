---
name: nethserver-ns8-module
description: 'Use when working in an ns8-* module repository — writing or reviewing action and event handlers, systemd units, backup/restore, build-images.sh, or the Vue.js UI — or when the repo is laid out as imageroot/ + ui/, or mentions "org.nethserver.*" labels. Also use on module symptoms: an action step that fails or halts the sequence, log lines that never reach journald, a password or secret to store, a backup or restore that loses data, a task that reports no progress to the UI, a missing authorization scope, containers of a pod starting in the wrong order. Not for NethServer/ns8-core itself, which keeps its code under core/ with build-image.sh in the singular — use nethserver-ns8-core there.'
---

# NethServer 8 module development

Read the reference file for your task before writing code. Do not read all of them.

## Overview

NS8 is a modular Linux server platform. Each module runs in a Podman container,
rootless by default. Some modules require rootful mode — declared in `build-images.sh`
via `--label="org.nethserver.rootfull=1"`.

Backend lives under `imageroot/` (Python 3 + bash). Frontend lives under `ui/` (Vue.js 2).
Pick the one reference file that matches your task from the map below.

## Reference map

| Task | Read |
|---|---|
| Module directory layout, `imageroot/` structure, container image pinning/Renovate in `build-images.sh`, authorization scopes/roles, `org.nethserver.authorizations=` labels, `selfadm` | `references/layout-and-authorization.md` |
| Writing or reviewing an action handler, `validate-input.json`/`validate-output.json`, event handlers, `org.nethserver.*` labels beyond images, injected env vars (`AGENT_ID`, `MODULE_ID`, ...), error signaling (`agent.set_status`, `agent.assert_exp`), journald logging (`agent.SD_ERR`, stderr), Agent SDK (`import agent`), `agent.set_env()`, secrets pattern, `tasks.run` vs `run_helper`, service providers / Redis service discovery, `ExecStartPre` discovery scripts, Ldapproxy, events/Redis pub-sub, systemd units, pod ordering (`BindsTo=`, `Before=`, `After=`), `configure-module/80start_services` | `references/backend.md` |
| Backup and restore, `imageroot/etc/state-include.conf`, `module-dump-state`/`module-cleanup-state`, `imageroot/actions/restore-module/`, `06copyenv`, `40restoreDB`, `50call-configure-module`, MariaDB/PostgreSQL dump and restore, clone-module vs restore-module, volume persistence, `org.nethserver.volumes=` additional disks, SELinux `:z`/`:Z` flags, `imageroot/update-module.d/` upgrade hooks | `references/backup-restore.md` |
| Vue 2 frontend under `ui/`, Vuex state (`core`, `instanceName`), `ns8-ui-lib` mixins (`TaskService`, `UtilService`, `IconService`, ...), action call pattern (`createModuleTaskForApp`), task progress (`isProgressNotified`, `agent.set_progress`), Carbon `cv-*` vs `Ns*` components, `NsWizard`, Vue filters, i18n / `ui/public/i18n/en/translation.json` | `references/frontend.md` |

## Always applies

- Always use a fully pinned image tag in `org.nethserver.images=` (e.g. `mariadb:11.4.12`) — never a floating tag like `lts` or `latest`; Renovate can't track floating tags. Verify the tag exists on Docker Hub before using it. (`references/layout-and-authorization.md`)
- Declare every authorization scope/role a module needs as `org.nethserver.authorizations=<scope>:<role>` in `build-images.sh`. (`references/layout-and-authorization.md`)
- stdout is reserved for action JSON output — all log messages must go to stderr (`agent.SD_ERR`/`SD_WARNING`/etc. in Python, `exec 1>&2` in bash). (`references/backend.md`)
- Never store passwords/tokens/secrets via `agent.set_env()` — it writes to Redis in plain text, readable by all modules on the node. Use the secrets file pattern instead. (`references/backend.md`)
- Non-zero exit from any action step or event handler step halts the remaining sequence. (`references/backend.md`)
- Starting only the pod's `<module>.service` does NOT start its children — list every service explicitly in `systemctl --user try-restart`. (`references/backend.md`)
- In `restore-module`, `50call-configure-module` must pass ALL vars restored by `06copyenv`, not just a subset — check `configure-module/validate-input.json`. (`references/backup-restore.md`)
- In the frontend, `Ns*` (ns8-ui-lib) components take priority over `cv-*` (Carbon Vue) — only fall back to `cv-*` when no `Ns*` equivalent exists. (`references/frontend.md`)

## Testing
Robot Framework tests in `tests/`. Run in order by filename: install → test → uninstall.
