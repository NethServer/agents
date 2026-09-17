# QA reporting and attribution

Record the tested version, upgrade baseline if used, caller scope where relevant, per-case result, and concise supporting observations. Keep detailed request/readback evidence locally when useful; the issue comment should remain short. Do not claim all cases passed if one is blocked or omitted, or claim calls/media/UI were tested from API-only evidence.

Post a GitHub comment only when the user authorized reporting there. Otherwise provide the result or a draft. This skill does not independently authorize posting, changing labels, closing issues, or publishing a release. When posting is authorized, post once and read the comment back; if the write response is ambiguous, check for an existing comment before retrying.

Use a compact report such as:

```text
QA: PASS / FAIL / PARTIAL — <module> <candidate version>

- <Issue case>: <result and decisive observation>.
- Upgrade <baseline> → <candidate>: <preservation/regression result>.
- <Any blocker or remaining limitation>.

<Cleanup or retained environment state, if relevant.>
Assisted-by: <resolved-agent-name>:<resolved-model-label>
```

### Resolve Assisted-by attribution

Include an `Assisted-by: AGENT_NAME:MODEL_VERSION` trailer in the QA report, using the same resolution policy as the conventional-commit skill. Resolve it from the current turn's runtime metadata immediately before generating the report. Do not infer the model from an introductory identity, configuration defaults, previous reports or commits, examples, or the list of available models.

For Codex, set `AGENT_NAME` to `Codex` and resolve the model locally:

1. Identify the current session using `CODEX_THREAD_ID`, falling back to `CODEX_SESSION_ID`. Locate only its matching JSONL transcript under `${CODEX_HOME:-$HOME/.codex}/sessions/`.
2. Read `payload.model` from the latest `turn_context` record. The active model can change during a session.
3. In `${CODEX_HOME:-$HOME/.codex}/models_cache.json`, find the `models` entry whose `slug` exactly matches that model ID. Use its `display_name` verbatim when available; otherwise preserve the exact model ID.

For other tools, use the current runtime's tool name and exact active model label. Keep the `Assisted-by:` key and full model label, including point releases. If the active model cannot be verified or conflicts with the user-visible selector, ask the user before publishing the report; finish the QA work, cleanup, and report draft in the meantime.

Read back the published comment and verify its trailer matches the resolved tool and model exactly. Return the comment link when publishing succeeds.
