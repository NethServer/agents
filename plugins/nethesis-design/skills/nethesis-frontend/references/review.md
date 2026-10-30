# Reviewing against the design system

Review what was asked: a component, a page, or the whole frontend. Report the problems; change
code only if asked to.

## Mechanical checks

Run these first, from the frontend folder (in My Nethesis, `frontend`). They find candidates,
not certain problems: read each match before reporting it.

```bash
# the files in scope: src for the whole frontend, or the files of a page
scope=src
# the file types: templates, and templates with scripts (React: *.tsx, and *.tsx with *.ts)
views='--include=*.vue'
code='--include=*.vue --include=*.ts'
# weights the design system does not use
grep -rnE 'font-(semibold|bold|extrabold|black)\b' $scope $views
# hex, rgb() or arbitrary colors
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|(bg|text|border|ring|fill|stroke)-\[#' $scope $views
# raw elements that usually have a component
grep -rnE '<(button|input|select|textarea|table)\b' $scope $views
# styles outside Tailwind classes (style="…" and style={{…}}), and arbitrary values
grep -rnE '\bstyle=["{]|\b[a-z-]+-\[[0-9.]+(px|rem)\]' $scope $views
# click handlers not on a button or a link on the same line: check the element of each one
grep -rnE '@click|v-on:click|onClick=' $scope $views |
  grep -vE '<(NeButton|NeLink|button|a|RouterLink|router-link|Button|Link)\b'
# icons not imported one by one: whole packs, library.add() (faLibrary.add() too), icons named
# by string
grep -rnE "import \{ (fas|far|fab|fal) \}|[lL]ibrary\.add\(|['\"]fa[srlb]['\"], *['\"][a-z0-9-]+['\"]|['\"]fa-(solid|regular|light|brands) fa-" $scope $code
# only in projects that use @nethesis/vue-components:
# deprecated components, from components.json (references/components.md)
deprecated=$(curl -s https://nethesis.github.io/vue-components/components.json |
  jq -r '[.components[] | select(.deprecated) | .name] | join("|")')
grep -rnE "\b($deprecated)\b" $scope $code
# deprecated props, types and functions of the installed version, with the lines that name them
grep -rn -A3 @deprecated node_modules/@nethesis/vue-components/dist --include=*.d.ts
```

Search the files in scope for each name the last command finds. A class from `foundations.json`
that looks like an arbitrary value, such as the drawer shadow, is a token, not a problem. In
vue-components itself, follow `references/library.md` for these commands.

Review the files in scope. When a component they import from the project has problems, report
them apart and briefly, without reviewing the whole component.

When a whole project uses the same pattern, such as icons named by string in every file, report
it once for the project with a few examples, not line by line.

## What to check

- **Components**: custom markup where a component or a pattern exists; classes that override a
  component instead of using its props; deprecated components; more than one `primary` button
  in a view or dialog.
- **Colors**: hex or arbitrary values; Tailwind palette classes where the project defines a
  semantic color for that role; palette names instead of `primary-*`; colors without a dark
  theme value (`references/colors.md`). In a project with its own theme, such as one built with
  another stack, its colors whose values differ from the token's in `colors.json`.
- **Typography**: weights other than `font-normal` and `font-medium`; sizes outside the text
  styles of `foundations.json`.
- **Icons**: icons not from Font Awesome Solid or the Nethesis packages; icons not imported
  one by one (whole packs, `library.add()`, names as strings); an icon that differs from the one
  `icons.json` gives for that meaning, or that it lists under `avoid`; custom icons listed under
  `customIconsWithoutMeaning`; decorative icons without `aria-hidden="true"`; icon-only buttons
  without an accessible label and a tooltip.
- **Text**: literal strings instead of i18n keys; texts that break the writing guidelines; terms
  the glossary lists under `avoid` (`references/text.md`); raw server or exception messages
  shown as the main message of a notification, such as `error.message` bound to its description
  (writing guidelines, "Style"); props of `Ne*` components that end in `Label` left to their
  English default in a project with i18n. List them for a component with
  `grep -oE '\b[a-z][a-zA-Z]*Label\b' node_modules/@nethesis/vue-components/dist/components/<Name>.vue.d.ts | sort -u`.
- **Accessibility**: form fields without a label, or a label linked to the wrong field (two
  fields with the same `id`); click handlers on elements that are not buttons or links, which
  the keyboard cannot reach; focus rings removed; text dimmed below the WCAG AA contrast of
  4.5:1, for example with `opacity-50`.

## Report

Group the problems by file, most serious first. For each one give:

- the severity: **critical** (broken or inaccessible for some users), **high** (wrong component,
  color or text the user sees), **medium** (inconsistent with the design system, but works),
  **low** (style or naming). For example: a control that the keyboard cannot reach, with no
  other way to do the same thing, is critical; text below the WCAG AA contrast and a deprecated
  component are high; a gray one step away from the token, an icon other than the one of its
  meaning and an English label that screen readers read in the Italian interface are medium;
- `path:line`;
- the problem, in one sentence;
- the rule it breaks, with a link to its source. Components and patterns, glossary terms, icon
  meanings and color tokens have their own `link` in `components.json`, `glossary.json`,
  `icons.json` and `colors.json`. A section of the writing guidelines is
  `https://nethesis.github.io/design-system/?page=writing-guidelines#<heading>`, with the heading
  written lowercase with hyphens (`#buttons-and-actions`). For a rule that comes only from this
  skill, cite the skill;
- the fix, as a short code change when it is obvious.

End with what you did not check, if anything. A review does not run the app: list the checks of
"Before you finish" in SKILL.md that the developer should do after the fixes.
