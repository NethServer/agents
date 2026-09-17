# NS8 QA workflow

## Establish the test contract

Read the issue body, relevant comments, and linked implementation or test instructions. Identify the exact candidate version, affected module, prerequisites, and expected behavior. Check repository instructions when using its code or tests.

Turn the issue's cases into a small execution checklist: prerequisite, caller identity, operation, expected observation, and cleanup. Keep issue-level case results separate from individual assertions. Inspect existing test suites before running them: NS8 suites can reconfigure or remove an application.

Use these outcomes:

- **PASS:** the required behavior was observed on the requested version.
- **FAIL:** the intended test ran and contradicted its expected behavior.
- **BLOCKED:** a missing prerequisite or environment problem prevented the test.
- **NOT RUN:** the test was omitted; state why.

Infer routine setup choices from the supplied QA context. Ask only for missing information that prevents safe progress, while continuing independent cases. A QA request covers necessary preparation of the designated test environment, but does not authorize deleting pre-existing applications, testing another environment, or repairing unrelated product defects.

## Inspect and prepare the environment

Read [NS8 operations](ns8-operations.md) for command examples, deployed schemas, startup checks, and lifecycle testing.

- Inventory actual node/module IDs, installed versions, relevant image digests, service state, and required dependencies. Hostnames do not establish which modules are installed. Module instance counters can contain gaps.
- Resolve source repositories and image repositories from observed remotes or module metadata. They may belong to different organizations.
- Inspect the deployed action schema and relevant code for the version under test. An input of `null`, `{}`, and an omitted property are different. Do not assume the repository's current branch matches the installed release.
- Snapshot affected configuration, application records, and authorization assignments before modifying them. Capture only required fields: environment files, user-domain responses, service metadata, and logs can contain credentials.
- Install or configure missing prerequisites when that follows from the requested QA setup. Check available resources before installing large dependencies, and reuse suitable existing services.

Use the supplied access method without embedding passwords, tokens, or real environment details in reusable scripts. Store any necessary sensitive local evidence privately; publish only sanitized results.

## Execute the cases

Use the interface the case is about: UI behavior needs UI verification; action/API behavior can use API calls. Administrator calls are suitable for fixture setup, not proof of a restricted caller's permissions.

For permission cases, read [Module authorization](module-authorization.md). Verify role definitions and effective caller assignments separately. Use actual module credentials through the API authorization boundary, with fresh authentication after grant changes. A validation error or failed task is not evidence of access denial.

Create uniquely identifiable fixtures that do not overwrite existing records. For state changes, assert both the action result and readback: creation appears in retrieval/listing, updates replace the intended values without duplicates, and deletion removes the record. Verify protected records remain unchanged after denied operations.

For **fresh installation**, use a genuinely new instance of the requested image and record its resulting configuration or role definitions. An upgraded instance does not prove the fresh-install path.

For **upgrade**, establish a real older-version instance with representative data and applicable caller grants. Record the baseline version and snapshots, perform the supported update, then verify the candidate version, data preservation, changed behavior, and existing functionality. Compare logical records with ordering normalized where order is not significant. Do not simulate an upgrade by editing role keys or invoke the update hooks manually as a substitute for the lifecycle action.

When only one instance is allowed per node, plan the fresh/upgrade sequence before installing dependencies. A disposable candidate instance can establish the fresh-install case, then be removed before creating the older baseline and upgrading it. Remove only the disposable instance created by this run; use another authorized fixture or report a blocker when pre-existing state prevents that sequence.

Wait for task completion and meaningful application readiness. A successful container start, agent registration, or available web page may precede database initialization and usable application services. Bound waits and retries; inspect the current task step or service state when progress stops. Recheck after a demonstrated state change rather than repeatedly rerunning a failure.

Distinguish fixture mistakes and harness assumptions from product defects. Retain the original observation, correct the setup when within scope, and rerun affected checks. Do not patch the candidate to obtain a passing result. Continue unaffected cases when another case fails or is blocked.

## Clean up

Restore temporary caller grants and remove only run-owned records, even after failure. Restore saved values rather than clearing whole permission hashes or tables. Verify the remaining application data and service state, and note any intentionally retained test-version applications or dependencies. Preserve sanitized evidence before removing temporary runners and closing SSH sessions.
