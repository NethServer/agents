# Evals of the frontend skills

Test cases for [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals), which runs
each case with and without the plugin and scores the results. They check that `nebula-frontend`
loads when it should and that it makes Claude follow the Nebula Design System.

| Case | What it checks |
| --- | --- |
| `review-table` | A review of a table with planted mistakes: opacity on archived rows, `font-bold`, hex colors, a click handler on a row, a `NeLink` without `href`, an `aria-label` that hides the visible text, a raw server message, icons registered as a pack, an icon button without a name, a term to avoid, a literal string, a raw `<table>` |
| `add-archive-action` | An archive action with its confirmation modal: component, icon, button kind, and the English and Italian texts |
| `trigger-dark-theme` | The skill loads for a dark theme fix in a Vue component |
| `no-trigger-backend` | The skill does not load for a Go task |

Each case has a `prompt.md`, a `case.yaml` that names a `fixture.sh`, which writes a small
project into the empty workspace, and `graders/`, one file per check: `regex` and `tool_used`
graders are exact, `llm` graders are judged by a second model.

## Run

Requires Claude Code 2.1.269 or later, git 2.31 or later and, on Linux, `bubblewrap` and
`socat` for the sandbox. From `plugins/frontend-skills`:

```bash
claude plugin eval . --scaffold --trust-plugin --no-publish \
  --allow-tools Bash Edit Write \
  "WebFetch(domain:nethesis.github.io)" "WebFetch(domain:raw.githubusercontent.com)"
```

- `--scaffold` runs the `fixture.sh` scripts, and `--trust-plugin` skips the first-run prompt:
  pass them only for this suite, which we wrote.
- `--allow-tools` lets Claude run the skill's commands and edit files. The domains are the ones
  the skill fetches the design system and Storybook files from: the sandbox blocks the others.
- `--no-publish` keeps the HTML report local, in `results/` (ignored by git).

A full run makes 3 runs of each case, each with and without the plugin: about 5 USD and
5 minutes. To try one change, run a single case once: `--case review-table --runs 1`
(0.30 to 0.60 USD). Add `-j 4` to run cases in parallel and `--max-cost-usd` to set a limit.

## Improve the skill

1. When the skill gets something wrong in real work, write a case that reproduces it, or add a
   grader to an existing case, and check that it fails.
2. Change the skill, then run that case until it passes.
3. Run the whole suite before pushing.
4. Compare the scores with and without the plugin. A case that scores the same without it does
   not test the skill: make it depend on a rule Claude cannot guess, such as a glossary term,
   the icon of a meaning or a writing guideline.

The fixtures are written inline in `fixture.sh`, because the script runs in the workspace and
cannot read the case directory. Test a fixture with `bash fixture.sh` in an empty directory.
