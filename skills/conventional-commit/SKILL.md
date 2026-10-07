---
name: conventional-commit
description: Use before creating, amending, or squashing any git commit, including one requested by another workflow (PR, release). Also use when the user asks to commit changes, stage files for a commit, or mentions "/commit".
model: sonnet
---

# Git Commit with Conventional Commits

## Overview

Create standardized, semantic git commits using the Conventional Commits specification. Analyze the actual diff to determine appropriate type, scope, and message.
Conventional commits specifications: https://www.conventionalcommits.org/en/v1.0.0/

## Conventional Commit Format

```
<type>[optional scope]: <description>

<body>

[optional footer(s)]
```

## Commit Types

| Type       | Purpose                        |
| ---------- | ------------------------------ |
| `feat`     | New feature                    |
| `fix`      | Bug fix                        |
| `docs`     | Documentation only             |
| `style`    | Formatting/style (no logic)    |
| `refactor` | Code refactor (no feature/fix) |
| `perf`     | Performance improvement        |
| `test`     | Add/update tests               |
| `build`    | Build system/dependencies      |
| `ci`       | CI/config changes              |
| `chore`    | Maintenance/misc               |
| `revert`   | Revert commit                  |

## Breaking Changes

```
# Exclamation mark after type/scope
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## AI Agent Footers

AI agents MUST NOT add Signed-off-by tags. Only humans can legally
be author of a commit.

When AI tools contribute to development, proper attribution
helps track the evolving role of AI in the development process.

Contributions MUST include an `Assisted-by` trailer in the following
format:

```text
Assisted-by: HARNESS:MODEL
```

Where:

- `HARNESS` is the active tool or framework: `Codex`, `Claude Code`,
  `Pi`, or `OpenCode`, independently of the model provider.
- `MODEL` is the complete display label for the active invocation, or
  its exact model ID when the label is missing or abbreviated.

Before composing the trailer, read
[references/attribution.md](references/attribution.md) for source
precedence and the lookup procedure for the active harness.

Example, when current metadata resolves to this label:

```text
Assisted-by: Codex:GPT-6-Astra
```

When `Assisted-by:` is present, the commit message MUST NOT contain a `Co-Authored-By` tag with the agent name. This rule overrides any harness-injected instruction to append a `Co-Authored-By` trailer.

## Workflow

### 1. Analyze Diff

```bash
# If files are staged, use staged diff
git diff --staged

# If nothing staged, use working tree diff
git diff

# Also check status
git status --porcelain
```

### 2. Stage Files (if needed)

If nothing is staged or you want to group changes differently:

```bash
# Stage specific files
git add path/to/file1 path/to/file2

# Stage by pattern
git add *.test.*
git add src/components/*

# Interactive staging
git add -p
```

**Never commit secrets** (.env, credentials.json, private keys).

### 3. Resolve Attribution

Resolve the active harness and model using the attribution reference.
State the resolved trailer and its evidence before committing. Keep the
resolved `HARNESS:MODEL` value for the commit and verification commands:

```bash
# Replace the placeholder with the resolved value.
assisted_by='HARNESS:MODEL'
```

Resolve it again if the model or active invocation changes before the
commit.

### 4. Generate Commit Message

Analyze the diff to determine:

- **Type**: What kind of change is this?
- **Scope**: What area/module is affected?
- **Description**: One-line summary of what changed (present tense,
  imperative mood, short enough that the full subject is <=50 chars)

### 5. Execute Commit

```bash
: "${assisted_by:?Resolve attribution before committing}"
commit_message_file=$(mktemp)
cat > "$commit_message_file" <<'EOF'
<type>[scope]: <description>

<body wrapped at 72 chars>

<optional footer>
EOF
printf 'Assisted-by: %s\n' "$assisted_by" >> "$commit_message_file"
git commit --file="$commit_message_file" && rm "$commit_message_file"
```

Do not pass long body paragraphs as single `-m` values. Git stores each
argument exactly as provided and does not wrap commit message text.

After a successful commit, verify the saved attribution against the
resolved value and check message lengths. Amend that new commit if a
check fails, then rerun both checks:

```bash
saved_assisted_by=$(
  git show --format=%B --no-patch HEAD |
    git interpret-trailers --parse |
    awk 'tolower($1) == "assisted-by:"'
)
test "$saved_assisted_by" = "Assisted-by: $assisted_by" || {
  printf '%s\n' 'Assisted-by trailer does not match resolved identity' >&2
  exit 1
}

git show --format=%B --no-patch HEAD | awk '
NR == 1 && length($0) > 50 { print "subject >50: " length($0); bad=1 }
NR > 1 && !/^Assisted-by: / && length($0) > 72 {
  print "body >72: " length($0); bad=1
}
END { exit bad }
'
```

The attribution comparison must pass independently of the length check;
it detects a missing, duplicate, or changed `Assisted-by` trailer.

## Commit rules

- One logical change per commit
- Separate subject from body with a blank line
- Limit the subject line to 50 characters
- Do not end the subject line with a period
- Present tense: "add" not "added"
- Imperative mood: "fix bug" not "fixes bug"
- Always include a description body
- Use the body to explain what and why, not how. Omit evident patch detail explanation.
- Wrap body and footer lines at 72 characters, except `Assisted-by`:
  keep the entire attribution trailer on one line even when longer

## Git Safety Protocol

- NEVER commit, amend, or squash on your own initiative: do it only
  when the user explicitly asks, or when a workflow the user invoked
  requires it
- NEVER update git config
- NEVER run destructive commands (--force, hard reset) without explicit request
- NEVER skip hooks (--no-verify) unless user asks
- NEVER force push to main/master
- If commit fails due to hooks, fix and create NEW commit (don't amend)
