---
name: nethserver-release
description: Use when the user asks to release a new NethServer 8 or NethVoice module version, tag a module release, bump a module version number, promote a pre-release to stable, or mentions "/release". Not for the NethSecurity repositories, which release on their own rules.
model: haiku
---

# NethServer Release

## Overview

Tag and publish NethServer module or package releases using the correct versioning scheme.
Source: [NethServer Development Handbook — Version Numbering Rules](https://handbook.nethserver.org/version_numbering/)

Scope: NethServer 8 and NethVoice modules, plus `ns8-nethsecurity-controller`. The
NethSecurity repositories themselves are out of scope — they publish no pre-releases, the
firmware releases from a push to the `release` branch rather than from a tag, and
`nethsecurity-ui` is driven by release-please. Stop and ask the author rather than applying
the rules below there.

---

## ⚠️ Default: testing release

**Always produce a testing/pre-release by default.**
Only switch to a stable release if the user explicitly asks for it (e.g., "stable release", "release to production", "bump stable").

| User says | Release type |
|---|---|
| "release", "tag", "bump version" | **Testing** (default) |
| "stable release", "release to production", "promote to stable" | **Stable** |

---

## Version format

### NethServer 8 and NethVoice

Format: `MAJOR.MINOR.PATCH[-testing.N]`

> Build metadata (`+`) is **not permitted** — it conflicts with OCI image tag specifications.

```
# Stable release
1.2.7

# Testing / pre-release (default)
1.3.0-testing.1
1.3.0-testing.2
```

---

## Choosing the version increment

Ask the user (or infer from the changes) which kind of increment is needed:

| Change type | Increment | When |
|---|---|---|
| **Major** | `X.0.0` | Non-backward compatible change; behavioral breaking change; manual upgrade procedure required |
| **Minor** | `x.Y.0` | New feature visible to the end-user; requires documentation change or release note |
| **Patch** | `x.y.Z` | Bug fixes; internal improvements; no user-visible behavior change |

### Update rules (NethServer 8 / NethVoice)

All releases must comply with:
1. New features, enhancements, and bug fixes must **not change the behavior of existing systems**.
2. New behaviors must be **enabled through explicit, documented sysadmin actions**.
3. Modules must support **updates from any previous release within the same major version**.

---

## Workflow

### Step 1 — Determine release type

```
Is this a stable release? → User must say so explicitly.
Default → testing pre-release.
```

### Step 2 — Determine version number

Look at the current version (e.g., from `git tag --sort=-v:refname | head -5`) and decide the increment.

```bash
# List recent tags
git tag --sort=-v:refname | head -10
```

### Step 3 — Construct the version string

```bash
# Testing release (default)
NEW_VERSION="1.3.0-testing.1"

# Stable release (only on explicit request)
NEW_VERSION="1.3.0"
```

For testing releases, increment the `.N` suffix if a testing release for that version already exists:
- `1.3.0-testing.1` → `1.3.0-testing.2` → ... → `1.3.0` (stable, when ready)

### Step 4 — Install the `gh ns8` extension (once)

NethServer 8 and NethVoice modules are released with the
[NethServer/gh-ns8](https://github.com/NethServer/gh-ns8) GitHub CLI extension.
It replaces the former `gh ns8-release-module` extension.

```bash
gh extension install NethServer/gh-ns8
```

Run the commands below from the repository root. Add `--repo owner/ns8-module` to target
another repository.

### Step 5 — Check the repository status

```bash
gh ns8 module-release check
```

The output lists the PRs merged since the latest release and the linked issues, grouped as:

| Group | Meaning |
|---|---|
| **Ready to release** | Verified issues whose PRs are all merged into `main` |
| **To be released** | Verified issues with PRs still open — ready once they are merged |
| **Release blockers** | Issues in progress or testing with PRs already merged into `main` |

Issues in progress or testing whose PRs are still open do not block the release.

A **stable** release can be created only when there are no release blockers. A testing
release can be created at any time, but review the output anyway so the release notes are
correct.

### Step 6 — Create the release

```bash
# Testing release (default): the next -testing.N name is generated automatically
gh ns8 module-release create --testing

# Testing release with an explicit name
gh ns8 module-release create --testing 1.3.0-testing.1

# Stable release (explicit only), with the linked issues in the release notes
gh ns8 module-release create --with-linked-issues 1.3.0
```

Some modules add extra content to the release notes, such as the `HEAD` of external
components. Follow the "Release procedure" section of the module README when present.

### Step 7 — After a stable release: clean up and notify

```bash
# Remove the testing pre-releases between the previous stable release and this one
gh ns8 module-release clean 1.3.0

# Comment every linked issue with the released version
gh ns8 module-release comment 1.3.0
```

`comment` works for testing releases too: it adds a "Testing release" comment to the
linked issues.

After a stable release, open the issue links printed by `comment`, close the issues and
remove the `verified` label.

#### Manual tag (when the gh extension is not applicable)

```bash
# Tag
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"

# Push tag
git push origin "$NEW_VERSION"
```

---

## Pre-release → stable promotion checklist

Before promoting a testing release to stable, verify:

- [ ] QA testing completed — issue has the `verified` label
- [ ] All related PRs merged
- [ ] Documentation updated (README, admin manual, user manual)
- [ ] i18n strings at 100% for English and Italian (NethServer 8 / NethVoice)
- [ ] No known exploitable vulnerabilities in the release
- [ ] SBOM generated and attached to the release (`.cdx.json`)
- [ ] Announcement/release notes prepared

---

## Examples

```bash
# Current latest release: 2.1.0
# User asks: "release a new testing version with the new dashboard feature"

# → Minor bump (new user-visible feature), testing by default
gh ns8 module-release check
gh ns8 module-release create --testing 2.2.0-testing.1

# Later: "promote to stable"
# → Stable release, only because the user explicitly requested it
gh ns8 module-release check            # must show no release blockers
gh ns8 module-release create --with-linked-issues 2.2.0
gh ns8 module-release clean 2.2.0
gh ns8 module-release comment 2.2.0
```
