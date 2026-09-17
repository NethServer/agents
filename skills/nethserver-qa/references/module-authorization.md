# Module authorization verification

Use this procedure when the issue concerns role definitions, restricted actions, caller grants, or authorization regressions. Do not expand unrelated QA into a security scan.

## Definitions and assignments are different

The following Redis structures are useful on NS8; verify the deployed core implementation when behavior differs:

| Structure | Meaning |
| --- | --- |
| `<target-agent>/roles/<role>` | Set of actions or patterns allowed by that role on the target |
| `roles/<caller-agent>` | Hash mapping target agents to that caller's roles, commonly comma-separated |
| `cluster/authorizations/module/<module-id>` | Declarative module authorizations applied by lifecycle operations |

For example, an action set under `module/<target>/roles/<role>` does not itself grant that role to another module. The cluster `grant-actions`/`revoke-actions` actions change shared **role definitions**; they are not a substitute for assigning a role to a caller.

Inside an administrator `runagent` Python process, inspect narrowly scoped keys with `agent.redis_connect(privileged=True)`. Use `smembers` for a role definition and `hgetall` for a caller's role map. Do not dump Redis ACL passwords or unrelated data.

Check the requested role exactly when the case requires an exact action set. Do not assume unrelated core roles contain only one entry: `selfadm` can contain `*` plus explicit actions added by core. For self-access regression, compare the pre-upgrade definition and exercise representative actions under the module's own credentials.

## Establish the caller fixture

Choose a real module identity suitable for the test. Audit its grants on the target and any applicable broader permissions; avoid administrator, owner, wildcard, or reader grants that would invalidate the intended denial tests. Permissions on unrelated modules do not automatically invalidate the caller fixture. Rootful modules can legitimately have Unix UID 0: verify the API identity, not UID alone.

Snapshot the affected assignment before changing it. Where supported by the installed core, the helper used for assignments is:

```python
import agent
import cluster.grants

rdb = agent.redis_connect(privileged=True)
# caller and target are full agent IDs, e.g. module/<observed ID>.
before = rdb.hgetall(f"roles/{caller}")
cluster.grants.alter_user(
    rdb, user=caller, revoke=False, role=role, on_clause=target,
)
assert rdb.hget(f"roles/{caller}", target) == role
```

Read the helper implementation before adapting it to an unfamiliar core version. Avoid wildcard selectors. Role assignment can replace the target's existing role list rather than merge with it. Restore the exact previous field in a `finally` block: use `hset` if it previously existed and `hdel` if it did not. Do not delete the caller's entire role hash or change the target's shared role definition to grant one caller access.

Lifecycle operations may reapply declarative authorizations. For upgrade regressions, use an actual existing caller grant where possible, snapshot it, and verify it afterward. Do not mistake a lifecycle refresh of a temporary manual grant for a failure of the newly defined role.

## Exercise the API as that module

Run a Python caller in `runagent -m <caller-module>` and use that environment's credentials. Calling `api-cli` as root, submitting through the cluster Redis endpoint, or reusing an administrator bearer token can produce a false authorization pass. Inspect the installed `api-cli` shebang and environment handling before relying on nested `runagent ... api-cli` invocations, particularly for rootful modules.

Obtain a fresh module login after each grant change and pass its token explicitly. This avoids both CLI and `agent.tasks` token caches, which can otherwise test a stale identity or role set. Keep credentials and tokens in memory.

The following is a caller pattern for a small temporary runner. Arguments are the full target agent ID and action; stdin contains the JSON payload. The default endpoint below is the usual NS8 internal API address; confirm it on the node rather than exposing the internal API publicly.

```python
import json
import os
import sys

import agent.tasks
import requests
from aiohttp import ClientResponseError

target, action = sys.argv[1:3]
payload = json.load(sys.stdin)
identity = os.environ["REDIS_USER"]
assert identity == os.environ["AGENT_ID"]
assert identity.startswith("module/")
endpoint = "http://cluster-leader:9311"

login = requests.post(
    endpoint + "/api/login",
    json={"username": identity, "password": os.environ["REDIS_PASSWORD"]},
    timeout=20,
)
login.raise_for_status()
token = login.json()["token"]

try:
    response = agent.tasks.run(
        agent_id=target, action=action, data=payload,
        endpoint=endpoint, auth_token=token, retry_attempts=3,
    )
    # Add case-specific assertions on response["output"] here.
    # Log only selected non-secret output fields, not the entire response.
    print(json.dumps({
        "caller": identity, "target": target, "action": action,
        "api_result": "accepted", "exit_code": response["exit_code"],
    }))
except ClientResponseError as error:
    print(json.dumps({
        "caller": identity, "target": target, "action": action,
        "http_status": error.status,
    }))
```

Invoke such a runner using the observed caller module ID, for example:

```bash
runagent -m "$qa_caller_module" python3 "$qa_caller_script" \
  "module/$qa_target_module" "$qa_action" < "$qa_input_file"
```

Bound the outer runner/task duration according to the action. Keep assertions and expected outcomes in the supervising harness: the example reports observations, and a zero runner exit code alone does not prove that the action was allowed or denied.

For an allowed action, require API submission success, task `exit_code == 0`, and the expected readback. For a denied action, require the deployed API's authorization-denial response, normally HTTP 403. HTTP 401 is a login failure; schema validation errors, service failures, timeouts, and arbitrary nonzero exits are not successful denial checks. Use valid inputs so the negative case isolates authorization.

## Coverage and restoration

Cover the identities required by the issue: caller with no applicable grant, caller with only the new role, an existing narrower role that should still work, and the module's own identity where self-access matters. Do not require this entire matrix for issues that do not concern those identities.

For CRUD, verify create, retrieve, list, update through the documented action, and remove. Use a distinct valid destination/value for updates and confirm there is no duplicate record. For denied writes/removals, verify the protected data and configuration are unchanged. Revoke temporary grants, authenticate again, and confirm access is denied when revocation behavior is part of the case.

Use administrator credentials only to set up and clean up fixtures, read authorization metadata, and make independent state observations. Restore temporary grants even when an assertion fails, then verify the caller's original assignment and application state.
