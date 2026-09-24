---
name: nethserver-issue
description: Use when the user asks to open a GitHub issue, file a NethServer bug report, request a feature, or mentions "/issue".
model: sonnet
---

# NethServer Issue Writing Guidelines

## Overview

Write clear, actionable GitHub issues following NethServer project conventions.
Source: [NethServer Development Handbook — Issues](https://handbook.nethserver.org/issues/)

---

## Writing style

Use simple, plain English and avoid technical jargon — bug reports and
feature requests are read by people with varying technical backgrounds
(support staff, partners, QA, non-native English speakers). Prefer
everyday words over internal terminology, spell out acronyms on first
use, and describe symptoms/behavior from the user's perspective rather
than in implementation terms.

---

## Before opening an issue

Issues are **not** a to-do list. Open an issue only when you are ready to produce a formal output (code change, new container image, package). If you are exploring an idea or hunting a hard-to-reproduce bug, open a **community discussion** first:

- [community.nethserver.org](https://community.nethserver.org) — English, public
- [partner.nethesis.it](https://partner.nethesis.it) — Italian, partners only

Create an issue once the problem is confirmed and the work can be formally described.

---

## Text formatting

GitHub renders issue titles and descriptions as HTML, so paragraphs
reflow to the reader's viewport. Do **not** hard-wrap body text at a
fixed column (e.g. 72 chars) — write each paragraph as a single long
line. Use blank lines to separate paragraphs and Markdown lists/
headings for structure. This differs from commit messages, which are
plain text and must stay wrapped (see the `conventional-commit`
skill).

---

## Issue types

Choose the correct GitHub issue type when opening an issue, and do not use any label:

| Type | When to use |
|---|---|
| **Bug** | A defect that must be fixed (e.g., a process crashes, a feature behaves incorrectly) |
| **Feature** | An improvement or new capability (e.g., new UI panel, new API endpoint) |
| **Design** | UI/UX design work; output is a mockup (Figma, image) |
| **Backend** | Backend implementation sub-task (API, package update, service logic) |
| **Frontend** | Frontend implementation sub-task (UI panel, page) |
| **Task** | Specific work item that is not a bug or feature (refactoring, documentation) |
| **Draft** | Idea not yet ready for development; used for backlog planning |

Sub-issues (Backend, Frontend, Design, Task) are children of a parent Bug or Feature issue.
QA testing targets the **parent issue**, not sub-issues.

---

## Writing a bug report

Use the **Bug** issue type (not the bug label). Use the bug template at https://github.com/NethServer/dev/blob/master/.github/ISSUE_TEMPLATE/bug_report.md

**Tips**:
- Be precise about the version — bugs are often version-specific.
- Include the minimal steps to reproduce reliably.
- Good text formatting and screenshots make the report much more useful.

---

## Writing a feature request

Use the **Feature** type. Use the feature template at https://github.com/NethServer/dev/blob/master/.github/ISSUE_TEMPLATE/feature_request.md

**Tips**:
- Avoid technical jargon; describe the feature from the user's perspective.
- Images and mockups make feature requests much easier to evaluate.
- Link to any community discussion where this was already debated.

---

## Where to file issues

- NethServer / NethVoice: [github.com/NethServer/dev/issues/new](https://github.com/NethServer/dev/issues/new)
- NethSecurity: [github.com/NethServer/nethsecurity/issues/new](https://github.com/NethServer/nethsecurity/issues/new)

> **Never report security vulnerabilities as public GitHub issues.**
> Use the [GitHub Security Advisory](https://github.com/NethServer/dev/security/advisories/new) form or email `sviluppo@nethesis.it`.

---

## Project and milestone assignment

After opening an issue, add it to the matching org-level GitHub Project, if possible:

| Product | Project |
|---|---|
| NethServer | [github.com/orgs/NethServer/projects/8](https://github.com/orgs/NethServer/projects/8) |
| NethVoice | [github.com/orgs/NethServer/projects/11](https://github.com/orgs/NethServer/projects/11) |
| NethSecurity | [github.com/orgs/NethServer/projects/10](https://github.com/orgs/NethServer/projects/10) |

```bash
gh project item-add <project-number> --owner NethServer --url <issue-url>
```

NethServer/dev hosts both NethServer and NethVoice issues, so determine the product from
the issue content before picking the project — NethVoice issues conventionally start the
title with `NethVoice: `. If it is genuinely ambiguous, ask rather than guessing.

For **NethServer** and **NethVoice** issues only, also set the Milestone to the current
one for that product — NethSecurity issues are left without a milestone. The current
milestone is the open one for that product with the nearest due date:

```bash
gh api repos/NethServer/dev/milestones --jq '.[] | select(.state=="open") | {title,due_on}'
gh issue edit <issue-number> --repo NethServer/dev --milestone "<milestone title>"
```

Skip project or milestone assignment rather than failing the issue creation if you lack
the permissions or cannot confidently determine either one, and say so when reporting the
issue URL.
