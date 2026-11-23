# Evals of the design skills

Test cases for [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals), which runs
each case with and without the plugin and scores the results. They check that `nebula-design`
loads for design work and not for code, and that it makes Claude follow the rules it cannot guess:
the UX team's pending decisions, the glossary, the icon dictionary, NethSecurity's staged changes.

| Case | What it checks |
| --- | --- |
| `trigger-design-mockup` | The skill loads for an HTML prototype with no code project, and the prototype follows the team rules: drawer `Create`, action-led delete modal, empty state with the only Primary, emerald NethVoice shell |
| `trigger-design-copy` | The skill loads for a review of mockup texts outside a project, and finds their mistakes |
| `trigger-italian` | The same kind of review, asked in Italian, loads the skill |
| `copy-pending-decisions` | Pending decisions: drawer `Create` without the object, statuses as icon + label instead of badges, `Qualcosa è andato storto.` |
| `copy-glossary` | Glossary terms only, checked with exact regexes: `Threat Shield`, `MultiWAN`, `Sign in`, `unit` for a NethSecurity installation and its Italian `unità` |
| `copy-nethsecurity-toast` | No success toast for a NethSecurity change that is only staged |
| `icon-missing-meaning` | For a meaning missing from the icon dictionary, the designer is asked, with custom and Font Awesome candidates |
| `no-trigger-code` | The skill does not load for a dark theme fix in a Vue component, which belongs to `nebula-frontend` |
| `no-trigger-ns8` | The skill does not load for a NethServer 8 mockup, which uses Carbon |

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

A case that scores the same with and without the plugin (Δ 0) does not test the skill: make it
depend on a rule Claude cannot guess, as the `copy-*` and `icon-*` cases do.
