---
name: nethserver-issue
description: 'Write well-structured GitHub issues following NethServer contribution guidelines. Use when the user asks to open an issue, file a bug report, request a feature, or mentions "/issue". Supports: (1) Bug report template with component, reproduction steps, and expected behavior, (2) Feature request template with user value and references, (3) Issue type selection (Bug/Feature/Design/Backend/Frontend/Task/Draft), (4) Label guidance (testing, verified, milestone goal), (5) Security vulnerability reporting rules and correct tracker URLs'
---

# NethServer Issue Writing Guidelines

## Overview

Write clear, actionable GitHub issues following NethServer project conventions.
Source: [NethServer Development Handbook — Issues](https://nethserver.github.io/dev/issues/)

---

## Before opening an issue

Issues are **not** a to-do list. Open an issue only when you are ready to produce a formal output (code change, new container image, package). If you are exploring an idea or hunting a hard-to-reproduce bug, open a **community discussion** first:

- [community.nethserver.org](https://community.nethserver.org) — English, public
- [partner.nethesis.it](https://partner.nethesis.it) — Italian, partners only

Create an issue once the problem is confirmed and the work can be formally described.

---

## Issue types

Choose the correct type when opening an issue:

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

Use the **Bug** type. Include all of the following:

```markdown
## Component and version

<Name of the affected component and its version, e.g., "nethserver-mail 3.2.1">

## Steps to reproduce

1. <First step>
2. <Second step>
3. ...

## Expected behavior

<What should happen>

## Actual behavior

<What actually happens — describe the error clearly>

## Suggested fix or workaround

<Optional: any ideas on what may cause it or how to fix it>

## Relevant logs or output

<Paste relevant log lines, command output, or screenshots>
```

**Tips**:
- Be precise about the version — bugs are often version-specific.
- Include the minimal steps to reproduce reliably.
- Good text formatting and screenshots make the report much more useful.

---

## Writing a feature request

Use the **Feature** type. Include all of the following:

```markdown
## Description

<Describe the feature in plain language that anyone can understand.
Use examples to illustrate the use case.>

<Explain who benefits from this and why it matters.>

## Alternative solutions

<Describe any alternative approaches you considered and why you rejected them.>

## References

<Links to external documentation, related projects, or prior discussions.>
```

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