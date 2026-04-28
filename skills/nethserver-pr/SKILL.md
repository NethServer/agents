---
name: nethserver-pr
description: 'Create and manage pull requests following NethServer contribution conventions. Use when the user asks to open a PR, submit a contribution, or mentions "/pr". Supports: (1) PR title and description structure with a ready-to-use template, (2) Correct issue link format for NethServer/NethVoice and NethSecurity, (3) Reviewer and self-assignee selection, (4) Merge commit conventions with issue references for automation, (5) Draft PR guidance for work-in-progress contributions'
---

# NethServer Pull Request Guidelines

## Overview

Create and manage pull requests following NethServer project conventions.
Source: [NethServer Development Handbook — Pull Requests](https://nethserver.github.io/dev/pull_requests/)

---

## Submitting a pull request

### Checklist

Before opening a PR, verify all of the following:

1. **Target branch**: PR is submitted against `main` (for the current stable release).
2. **Title**: Brief, descriptive explanation of the feature, fix, or enhancement.
3. **Issue link**: The PR body must contain a reference to the related issue:
   - NethServer / NethVoice: `NethServer/dev#<number>` — e.g., `NethServer/dev#1122`
   - NethSecurity (main repo): `#<number>` — e.g., `#1145`
   - NethSecurity (module repo): `NethServer/nethsecurity#<number>` — e.g., `NethServer/nethsecurity#1155`
4. **Description**: Explain what was changed and how the feature/fix is supposed to work.
5. **Cross-repo dependencies**: If this PR depends on other PRs in other repositories, list them explicitly in the description.
6. **Reviewer**: Select at least one reviewer. GitHub's suggestions are usually appropriate.
7. **Assignee**: Assign yourself as the initial assignee to track ownership and status.

### PR description template

```markdown
## Summary

<Brief description of what was changed and why>

## Related issue

NethServer/dev#<number>

## How to test

<Steps to verify the change works correctly>

## Dependencies

<List any other PRs that must be merged first, if applicable>
```

---

## Managing an open pull request

After opening the PR:

1. **CI must pass**: If automated builds or tests fail, investigate the error before requesting review.
   - If the failure is an infrastructure problem, contact a developer for help.
2. **Code review**: Another developer must review the PR to confirm it:
   - Works as expected
   - Does not break existing behavior
   - Is reasonably readable
   - Has a clean commit history following the [Conventional Commits](https://www.conventionalcommits.org/) standard
3. **Address feedback**: All reviewer comments must be resolved before the PR is ready to merge.

---

## Merging a pull request

When merging, **copy the issue reference into the merge commit body** — this is required for automated tooling (changelog generation, issue notifications):

```
Merge pull request #87 from OtherDev/branchXY

Add new excellent feature

NethServer/dev#1122
```

**Squash merges** are acceptable when the commit history is noisy or you want easy revert capability.
The issue reference must appear in the squashed commit body:

```
Another feature (#89)

NethServer/dev#1133
```

Do NOT add issue references inside individual (non-merge) commit messages — this keeps the GitHub reference graph clean.

---

## Draft pull requests

Use draft PRs to share work in progress before it is ready for review:

- Recommended for ongoing development or experimental implementations.
- Can be used even before a formal issue exists.
- If no issue is linked, the draft PR **must have an assignee**.

To convert a draft to a ready PR, set it to **"Ready for review"**.

---

## Quick reference

| Situation | Action |
|---|---|
| Work in progress | Open as **draft PR** |
| Bug fix or feature ready | Open PR targeting `main` |
| NethServer/NethVoice issue | Link as `NethServer/dev#N` |
| NethSecurity main repo | Link as `#N` |
| NethSecurity module repo | Link as `NethServer/nethsecurity#N` |
| No reviewer selected | Use GitHub's reviewer suggestions |
| CI fails | Fix before requesting review |
