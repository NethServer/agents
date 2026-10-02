# Resolve commit attribution

Use the `HARNESS` and `MODEL` definitions in
[SKILL.md](../SKILL.md#ai-agent-footers). Apply the source precedence below,
then read only the lookup section for the active harness.

## Source precedence and fallback

- Prefer exact runtime metadata for the active invocation, after any model
  switch or skill/agent override. Otherwise use metadata tied to the
  identified current session, turn, and active branch as described below.
  Historical records are insufficient if they predate a switch or override.
- Accept an explicit identity supplied by the user for this current
  session/invocation. A model mentioned in an example or a previous plan is
  not a current identity declaration.
- Generic self-descriptions such as "based on GPT-6", configuration defaults,
  previous commits, and available-model lists do not establish the active
  model. A catalog can supply a display label only by matching an
  independently established current model ID.
- Preserve versions, suffixes, casing, and provider-qualified IDs. Do not
  manufacture a display label by capitalizing or expanding an ID, or infer
  a version from a family alias such as `sonnet`.
- Reasoning effort and service tier are separate settings, not part of
  `MODEL`. Do not append them to the resolved identity.
- Use existing, accessible metadata sources. Do not install integrations or
  configure status lines just for attribution. If no exact current identity
  can be established, ask the user for the current harness and full model
  label or ID before committing. If exact sources for the same active
  invocation conflict, state the conflicting values and ask which is current.
  A generic label or a demonstrably older selection is not such a conflict.

## Codex

Use exact current-turn model metadata when it is exposed. For a local
session, the rollout provides a fallback:

1. Read `CODEX_THREAD_ID` and the effective Codex home (`CODEX_HOME`, default
   `~/.codex`). Locate the rollout for that thread under `sessions/`, or
   `archived_sessions/` if applicable. Do not choose the newest file across
   all sessions or infer the session from the working directory alone.
2. Verify that the rollout's `session_meta` record has
   `payload.id == CODEX_THREAD_ID`. Read the latest `turn_context` record's
   `payload.model` (the turn's `turn_context.model`), checking that the record
   belongs to the active turn. Earlier turns can name different models.
3. Match that exact ID against `models_cache.json` in the same Codex home:
   use the matching `models[]` entry's `slug` and `display_name`. A missing
   cache entry or incomplete label means using the exact ID, not selecting a
   nearby catalog entry.

For example, current metadata `gpt-6-astra` with a matching catalog label
`GPT-6-Astra` yields `Assisted-by: Codex:GPT-6-Astra`. The generic identity
`GPT-6` does not override that evidence. Without that label, use
`Assisted-by: Codex:gpt-6-astra`. These are examples, not a fixed model map.

Read only the session/model fields needed for attribution. If the current
turn or session cannot be identified, use the shared fallback.
See [Codex session locations](https://learn.chatgpt.com/docs/reference/troubleshooting#feedback-and-logs).

## Claude Code

Use the exact runtime model identity supplied in context, or exposed
metadata for the identified current session/invocation. Resolve the model
actually in effect after this skill's `model: sonnet` override; the alias
alone does not identify a version, and the earlier session model may no
longer apply. An override that was not applied does not establish identity
either. See [skill model overrides](https://code.claude.com/docs/en/skills#frontmatter-reference).

If current status-line metadata is already available, inspect `model.id`
and `model.display_name`, tied to its `session_id` and current invocation.
Use the display name only when complete; a label such as `Sonnet` requires
the full `model.id` instead. Do not assume a status snapshot predating the
skill override describes this invocation. See
[available metadata](https://code.claude.com/docs/en/statusline#available-data).

## Pi

Prefer exposed current-session model metadata, such as `session.model`,
with its provider, ID, and name. If inspecting existing session records,
first identify the current session and active leaf. Follow the active
branch through entry `id`/`parentId` links; abandoned branches can contain
newer records for other models. See
[session lifecycle](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md#session-lifecycle).

On that branch, assistant message `provider`/`model` fields identify the
model that answered. Account for `model_change` entries (`provider` and
`modelId`) and confirm which model applies to this invocation. A selected
virtual model may differ from the physical model recorded on the assistant
message; use the resolved invocation identity. See
[session format](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/session-format.md).

Use a complete name associated with the resolved model, or the exact
provider-qualified ID (`provider/modelId`) when falling back to an ID.
If the active branch or current model cannot be established, use the shared
fallback; do not guess from the last line in an arbitrary session file.

## OpenCode

Prefer the exact provider/model identity injected into runtime context.
The [runtime implementation](https://github.com/anomalyco/opencode/blob/v1.18.32/packages/opencode/src/session/system.ts#L69)
supplies `model.providerID/model.api.id`; preserve that qualification when
using the ID as `MODEL`.

If runtime identity is absent, inspect the identified current session's
message metadata for the active invocation (`providerID` and `modelID`)
and the corresponding resolved model descriptor. The message's catalog
`modelID` can be an alias: follow its descriptor to `api.id` and use the
exact provider/API model ID, or a complete display name associated with it.
Do not treat a friendly alias as a full model label. See
[model descriptor resolution](https://github.com/anomalyco/opencode/blob/v1.18.32/packages/opencode/src/provider/provider.ts#L1400).

Account for [agent model overrides](https://opencode.ai/docs/agents/#model)
and model switches. A default or earlier message does not prove the current
selection. If the current invocation or alias mapping cannot be resolved
from accessible metadata, use the shared fallback.
