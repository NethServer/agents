---
description: Add an archive action with a confirmation modal to a table
tags: [write]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

In src/components/CustomersTable.vue, add a way to archive each customer, with a confirmation first: an archived customer can be restored later. After the user confirms, emit an `archive` event with the customer id. Keep the change in that component and in the i18n files. The dependencies are not installed, so don't run any build or check.
