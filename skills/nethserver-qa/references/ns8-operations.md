# NS8 operations for QA

These patterns were exercised against NS8, but the installed core and application schemas remain authoritative. Run administration commands on the designated QA node. Replace variables with values discovered for the current run.

## Access and discovery

Reuse the user's working SSH configuration or connection. Keep a task-specific control socket and known-hosts file in a private directory when reusing connections. Do not disable host-key checking. If the local SSH configuration itself is unusable, a scoped `-F /dev/null` connection can help only when it does not discard required proxy, identity, or host-verification settings; leave the system SSH configuration unchanged.

Useful initial commands:

```bash
hostname
command -v api-cli runagent add-module remove-module
runagent --list-modules
api-cli run cluster/list-installed-modules --data null
df -h /
free -h
```

`cluster/list-installed-modules` returns groups of instances; use their actual IDs, node, source, version, and digest. Confirm the schema before adapting these commands to another core version. For user-domain prerequisites, select only required names/provider IDs from the response; `cluster/list-user-domains` can return LDAP bind credentials.

Determine module paths through its environment instead of assuming every module lives under `/home`:

```bash
runagent -m "$qa_module" python3 - <<'PY'
import os
print("agent:", os.environ["AGENT_ID"])
print("install:", os.environ["AGENT_INSTALL_DIR"])
print("state:", os.environ["AGENT_STATE_DIR"])
PY
```

Typical layouts are `/home/<module>/.config` for rootless modules and `/var/lib/nethserver/<module>` for rootful modules. Actions and input/output schemas live under the install directory's `actions/`; update hooks may be under `update-module.d/`. Core cluster actions commonly live under `/var/lib/nethserver/cluster/actions/`. Use observed paths rather than creating absent directories.

Do not print the full process environment or `agent.env`, `environment`, `passwords.env`, or token caches. Read selected non-secret keys when necessary.

## Calling actions

For administrator setup and observation, the usual CLI shape is:

```bash
api-cli run "module/$qa_module/$qa_action" --data - < "$qa_input_file"
```

Generate JSON using a serializer or a quoted heredoc. Read the action's `validate-input.json` first and inspect its output schema before logging results. An optional address field should be omitted when unused if the schema rejects an empty string. Some core actions require JSON `null` rather than an empty object.

Check both process/task exit status and returned data. Preserve failure output, but sanitize credentials before displaying or publishing it. For long operations, keep the running task/session and resume observation; an empty output window does not mean the operation failed or should be resubmitted.

NS8 Python helpers are available inside `runagent` environments. `agent.tasks.run` typically returns `exit_code`, `output`, and `error`. A cluster administrator can use `redis://cluster-leader` for setup. That endpoint does **not** establish that a non-administrator caller passed API authorization; use the separate authorization procedure for that case.

## Installation and upgrade

Use exact image references supplied by the user or verified from the relevant release. Do not substitute `latest` for a requested testing version.

```bash
add-module "$qa_candidate_image" "$qa_node_id"
```

Capture the returned module ID and image URL, and read back installed metadata. Module IDs are allocated, not necessarily `<name>1`. Also inspect relevant running component images after an update; the wrapper module metadata alone may not reveal a failed service rollout.

The cluster update action commonly accepts:

```json
{
  "module_url": "<exact candidate image reference>",
  "instances": ["<observed module ID>"]
}
```

After checking the installed schema, submit the payload:

```bash
api-cli run cluster/update-module --data - < "$qa_upgrade_input"
```

Use `force` only when the current task and its documented semantics require it. Calling an update action with the same installed version is not evidence of an older-to-newer upgrade. Do not downgrade a populated application merely to manufacture a baseline; create an authorized older-version fixture instead.

Before upgrading, save representative logical records, relevant configuration, role definitions/assignments, and source/version/digest. Afterward verify preservation and rerun the issue's behavior checks. Include relationships and record counts when they matter, not just existence of one record.

If a temporary instance must be removed, first verify it was created for this run and has no needed data or dependents. `remove-module --no-preserve "$qa_disposable_module"` deletes its state; it is appropriate for a disposable fixture, not general cleanup of pre-existing applications.

## Readiness and transient setup failures

For a rootless module, inspect services in its user context:

```bash
runagent -m "$qa_module" systemctl --user is-active "$qa_service"
runagent -m "$qa_module" systemctl --user list-jobs --no-pager
runagent -m "$qa_module" podman ps --format '{{.Names}} {{.Image}} {{.Status}}'
```

Rootful modules may need different systemd/service commands; inspect their units. Avoid dumping container inspections or command lines that can contain secrets.

Choose a readiness observation relevant to the case: a successful action and readback, a health endpoint, database availability, an active protocol listener, or a completed application initialization task. Installation, configuration, and first application startup can finish at different times. Inspect progress before classifying a dependency's temporary failure as a defect in the candidate.

Apply documented initialization steps when needed. Do not generalize application-specific repairs into mandatory QA setup or keep installing unrelated components to work around a blocker. If a prerequisite still fails without a clear, scoped remedy, record it as blocked and continue independent tests.

## Evidence and cleanup

Use a run-specific private directory and record only what is needed to reproduce the result: timestamp, version/digest, caller identity and role, operation, expected result, actual result, and selected readback fields. Keep credential-bearing raw artifacts out of repositories and public comments.

Track created records and original values as soon as setup changes them, so failure cleanup is possible. Restore exact prior assignments, remove run-owned records, and compare the remaining logical state with the initial snapshot. Leave the requested candidate and useful configured dependencies in place when that is the intended QA outcome, and say what was retained. Remove disposable runners and close connection masters after collecting evidence.
