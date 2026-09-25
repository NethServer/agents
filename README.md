# NethServer Administration and Development Agent Skills

A collection of agent skills for safe [NethServer](https://github.com/NethServer) administration and development.
Development guidance is derived from the [NethServer Development Handbook](https://nethserver.github.io/dev/).
The same skill definitions can be installed in [Claude Code](#install-as-a-claude-code-plugin),
[Codex](#install-in-codex), and [Pi](#install-in-pi).

## Available skills

Skill definitions live under the `skills/` directory.

Once installed, select a skill using your agent's [invocation syntax](#usage), or let the agent
pick it automatically:

- `nethserver-admin` — inspect, install, configure, and troubleshoot NS8 nodes over shell/SSH
- `nethvoice-admin` — diagnose, repair, and operate production NethVoice and NethVoice Proxy instances safely
- `nethserver-containerfile` — write and review secure, production-ready Containerfiles
- `nethserver-issue` — write well-structured GitHub issues
- `nethserver-ns8-core` — navigate and modify the ns8-core platform repository itself
- `nethserver-ns8-module` — develop and review NS8 modules (backend + frontend conventions)
- `nethserver-pr` — create and manage pull requests
- `nethserver-release` — create module and package releases following semver
- `conventional-commit` — conventional commit messages with intelligent staging

## Skill structure and context cost

Agents initially load each skill's name and `description`, while its `SKILL.md` body is
loaded only when the skill is invoked. Both cost context, so skills here follow two rules:

- **Descriptions state triggers only.** They say *when* to use the skill, not what it does or
  how it works. No feature lists — those belong in the body.
- **Large skills use progressive disclosure.** `SKILL.md` stays a short router: scope, the
  non-negotiable rules, and a reference map. The detail lives in `references/*.md`, and the
  agent reads only the one file its task needs.

```
skills/nethserver-ns8-module/
  SKILL.md                              # router: overview, always-applies rules, reference map
  references/layout-and-authorization.md
  references/backend.md
  references/backup-restore.md
  references/frontend.md
```

When adding to a split skill, put the content in the matching `references/` file and add a
keyword to its row in the reference map. Only add to `SKILL.md` if the rule applies no matter
which reference file gets read. Three corollaries:

- A rule lives in one place only, either the router or a reference, never both. Duplicated
  rules drift apart.
- A rule kept in the router must not depend on a section that lives in a reference file, or
  an agent reading another reference gets the rule without its content.
- Reference paths are relative to the skill directory, so `references/backend.md` means
  `skills/<skill>/references/backend.md`.

### Model overrides (Claude Code only)

Template-driven skills declare a cheaper model in frontmatter so they do not spend a
frontier-model turn on mechanical work:

| Skill | `model:` |
| --- | --- |
| `nethserver-pr`, `nethserver-release` | `haiku` |
| `conventional-commit`, `nethserver-issue`, `nethserver-containerfile` | `sonnet` |
| `nethserver-admin`, `nethserver-ns8-core`, `nethvoice-admin`, `nethserver-ns8-module` | none — these need full reasoning |

In Claude Code, the override applies to the turn that invokes the skill and is not saved to
your settings. Remove the `model:` line if you would rather always use your session model.
Codex and Pi do not use these fields to select a model. Choose the model in the client instead.

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

## Install in Codex

Codex can read this repository's `.claude-plugin/marketplace.json` and install the
`nethserver-skills` plugin. Use a Codex CLI with the `plugin` and `plugin marketplace`
commands, whose syntax was checked with version `0.157.0`.

Run these commands in your terminal:

```bash
codex plugin marketplace add NethServer/agents
codex plugin add nethserver-skills@nethserver
codex plugin list --marketplace nethserver
```

Confirm that `nethserver-skills` is installed and enabled, then start a new Codex session.
Use `/skills` or the `$` picker to find the installed skills.

To refresh the marketplace and install its current plugin contents:

```bash
codex plugin marketplace upgrade nethserver
codex plugin add nethserver-skills@nethserver
```

Start a new Codex session after updating. For a pinned installation, add the marketplace
with `--ref` instead of the first command above. Replace `0.0.3` with the published tag you
want to use:

```bash
codex plugin marketplace add NethServer/agents --ref 0.0.3
```

Marketplace updates follow the configured reference. A fixed tag keeps the installation on
that release until you explicitly select another reference.

For CLI details, see the [Codex plugin commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin)
and [marketplace commands](https://learn.chatgpt.com/docs/developer-commands#codex-plugin-marketplace).

### Uninstall (Codex only)

```bash
codex plugin remove nethserver-skills@nethserver
codex plugin marketplace remove nethserver
```

The first command removes the installed plugin. The second removes the registered marketplace.
Start a new Codex session after removal.

## Install in Pi

Pi discovers the repository's `skills/` directory when installing it as a Git package.
The commands below use the CLI syntax available in Pi `0.87.1`.

Run these commands in your terminal:

```bash
pi install git:github.com/NethServer/agents
pi list
```

Confirm that the repository appears in `pi list`, then start Pi and type `/skill:` to find
the installed skills. Personal installations are recorded in `~/.pi/agent/settings.json`.
To register the package for one project instead, run this from that project's directory:

```bash
pi install -l git:github.com/NethServer/agents
```

This records the package in `.pi/settings.json`. Pi loads project packages after the project
is trusted.

To update this package:

```bash
pi update git:github.com/NethServer/agents
```

Run `/reload` in an active Pi session after updating, or start a new session. To install a
specific release, append its Git tag. Replace `0.0.3` with the published tag you want:

```bash
pi install git:github.com/NethServer/agents@0.0.3
```

Tags and commits stay pinned during updates. Run `pi install` with the new reference when
you want to move to another release.

For package discovery and versioning, see [Pi packages](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/packages.md).
For command options, see the [Pi CLI reference](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md).

### Uninstall (Pi only)

```bash
pi remove git:github.com/NethServer/agents
```

Add `-l` when removing a project-local installation. Run `/reload` in an active Pi session
after removal, or start a new session.

## Usage

**Automatic** — when your task matches a skill's `description`, the agent *may* load it on
its own. This is model-decided and not guaranteed; for a specific skill, name it explicitly
(see below). Example prompts that tend to trigger a match:

> "Review this Containerfile"
>
> "Add a configure-module action to my ns8 module"

### Claude Code

Once installed in Claude Code, everything is namespaced under the plugin (`nethserver-skills:`).

**Slash menu** — type `/` and pick the skill by name (e.g. `/nethserver-ns8-module`).
The grey `(nethserver-skills)` label shown beside it is the source plugin, not part of the name.

**Explicit** — you can also invoke a skill by its fully-qualified name:

```
nethserver-skills:nethserver-ns8-module
nethserver-skills:nethserver-containerfile
nethserver-skills:nethserver-pr
```

### Codex

In Codex CLI or the IDE extension, run `/skills` or type `$` and select the desired skill
from the picker, such as `nethserver-ns8-module` from `nethserver-skills`. Include the selected
skill in your prompt and describe the task. See [Codex skill invocation](https://learn.chatgpt.com/docs/build-skills#how-codex-uses-skills).

### Pi

Use `/skill:<name>` to load a skill explicitly. You can append the task after the command:

```text
/skill:nethserver-ns8-module Add a configure-module action
/skill:nethserver-containerfile Review this Containerfile
/skill:nethserver-pr Draft a pull request for the current changes
```

See [Pi skill invocation](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md#understand-how-skills-load).
