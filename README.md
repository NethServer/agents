# NethServer Coding Agent Skills

A collection of coding agent skills tailored to [NethServer](https://github.com/NethServer) development guidelines.
These skills are derived from the [NethServer Development Handbook](https://nethserver.github.io/dev/).

## Available skills

Skill definitions live under the `skills/` directory.

Once installed, activate a skill by typing its `/` name (or let the agent pick it automatically):

- `/nethserver-admin` — inspect, install, configure, and troubleshoot NS8 nodes over shell/SSH
- `/nethserver-containerfile` — write and review secure, production-ready Containerfiles
- `/nethserver-issue` — write well-structured GitHub issues
- `/nethserver-ns8-core` — navigate and modify the ns8-core platform repository itself
- `/nethserver-ns8-module` — develop and review NS8 modules (backend + frontend conventions)
- `/nethserver-pr` — create and manage pull requests
- `/nethserver-release` — create module and package releases following semver
- `/conventional-commit` — conventional commit messages with intelligent staging

## Install as a Claude Code plugin

This repository is a Claude Code plugin marketplace. In your Claude Code session:

```
/plugin marketplace add NethServer/agents
/plugin install nethserver-skills@nethserver
/reload-plugins
```

No plugin `version` is pinned, so every push to the default branch counts as a new version.
Claude Code refreshes installed marketplaces in the background (this is a public repo, so the
pull needs no credentials), so you pick up new and updated skills automatically — no reinstall
needed. Force an immediate refresh with `/plugin marketplace update nethserver`.

### Uninstall (Claude Code only)

These commands apply only to the Claude Code plugin install above:

```
/plugin uninstall nethserver-skills@nethserver
/plugin marketplace remove nethserver
/reload-plugins
```

`uninstall` removes the plugin but keeps the marketplace registered; `marketplace remove`
also drops the catalog entry. After `/reload-plugins` the skills disappear from the `/` menu.

## Usage

Once installed, everything is namespaced under the plugin (`nethserver-skills:`).

**Automatic** — when your task matches a skill's `description`, the agent *may* load it on
its own. This is model-decided and not guaranteed; for a specific skill, name it explicitly
(see below). Example prompts that tend to trigger a match:

> "Review this Containerfile"
>
> "Add a configure-module action to my ns8 module"

**Slash menu** — type `/` and pick the skill by name (e.g. `/nethserver-ns8-module`).
The grey `(nethserver-skills)` label shown beside it is the source plugin, not part of the name.

**Explicit** — you can also invoke a skill by its fully-qualified name:

```
nethserver-skills:nethserver-ns8-module
nethserver-skills:nethserver-containerfile
nethserver-skills:nethserver-pr
```
