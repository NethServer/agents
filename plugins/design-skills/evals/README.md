# Evals of the design skills

Test cases for [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals), which runs
each case with and without the plugin and scores the results. They check that `nebula-design`
loads for design work and not for code.

| Case | What it checks |
| --- | --- |
| `trigger-design-mockup` | The skill loads for an HTML prototype with no code project |
| `trigger-design-copy` | The skill loads for a review of mockup texts outside a project, and finds their mistakes |
| `no-trigger-code` | The skill does not load for a dark theme fix in a Vue component, which belongs to `nebula-frontend` |

The suite loads only this plugin, so it cannot check which of `nebula-design` and
`nebula-frontend` wins when both plugins are installed: their descriptions draw the line, code in
a frontend project for `nebula-frontend`, designs and copy outside a project for `nebula-design`.

## Run

Same requirements as the [frontend evals](../../frontend-skills/evals/README.md#run). From
`plugins/design-skills`:

```bash
claude plugin eval . --scaffold --trust-plugin --no-publish \
  --allow-tools Bash Edit Write \
  "WebFetch(domain:nethesis.github.io)" "WebFetch(domain:raw.githubusercontent.com)"
```

To try one change, run a single case once: `--case trigger-design-copy --runs 1`.
