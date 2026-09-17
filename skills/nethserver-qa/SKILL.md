---
name: nethserver-qa
description: Use when asked to execute QA test cases, verify or retest an issue, or validate a testing version on a NethServer 8 test environment.
---

# NethServer 8 QA

Verify an issue's expectations against the requested module version on the
supplied QA environment. Produce evidence for each case and leave the
environment in a documented state. This skill covers live acceptance testing;
code review, security scanning, and release publishing are separate tasks.

Read [QA workflow](references/qa-workflow.md) before running tests. Read the
other references only when the corresponding task is needed. Before preparing
the final report or issue comment, read
[Reporting and attribution](references/reporting.md).

## Reference map

| Task | Read |
| --- | --- |
| Issue cases, prerequisites, fixture setup, fresh installation, upgrade preservation, readiness, failure classification, cleanup | [QA workflow](references/qa-workflow.md) |
| SSH, module/node discovery, deployed schemas, `api-cli`, `runagent`, installation/update commands, service state, evidence handling | [NS8 operations](references/ns8-operations.md) |
| Role definitions versus assignments, restricted module callers, fresh API authentication, denial checks, permission restoration | [Module authorization](references/module-authorization.md) |
| Short QA results, authorized GitHub comments, publication readback, runtime model detection for `Assisted-by` | [Reporting and attribution](references/reporting.md) |
