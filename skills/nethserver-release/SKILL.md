---
name: nethserver-release
description: 'Create NethServer module or package releases following semver and project-specific versioning rules. Use when the user asks to release a new version, tag a release, bump a version number, or mentions "/release". Defaults to testing/pre-release unless stable is explicitly requested. Supports: (1) Version increment decision (major/minor/patch), (2) Testing pre-release by default (X.Y.Z-testing.N suffix), (3) Stable release only on explicit user request, (4) NethServer 8/NethVoice via gh ns8-release-module, (5) NethSecurity OpenWrt versioning conventions'
---

# NethServer Release

## Overview

Tag and publish NethServer module or package releases using the correct versioning scheme.
Source: [NethServer Development Handbook — Version Numbering Rules](https://nethserver.github.io/dev/version_numbering/)

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

### Step 4 — Tag and release

#### NethServer 8 / NethVoice — use `gh ns8-release-module`

```bash
# Install the extension (once)
gh extension install NethServer/gh-ns8-release-module

# Create a testing release (default)
gh ns8-release-module --testing

# Create a stable release (explicit only)
gh ns8-release-module
```

Refer to [NethServer/gh-ns8-release-module](https://github.com/NethServer/gh-ns8-release-module) for full options.

#### Manual tag (when gh extension is not applicable)

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
# Current latest tag: 2.1.0
# User asks: "release a new testing version with the new dashboard feature"

# → Minor bump (new user-visible feature), testing by default
git tag -a "2.2.0-testing.1" -m "Release 2.2.0-testing.1"
git push origin "2.2.0-testing.1"

# Later: "promote to stable"
# → Stable release, only because user explicitly requested it
git tag -a "2.2.0" -m "Release 2.2.0"
git push origin "2.2.0"
```
