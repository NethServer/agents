# Reviewing against the design system

Review what was asked: a component, a page, or the whole frontend. Report the problems; change
code only if asked to.

## Mechanical checks

Run these first. They find candidates, not certain problems: read each match before reporting
it.

```bash
# the files in scope: src for the whole frontend, or the files of a page
scope=src
# weights the design system does not use
grep -rnE 'font-(semibold|bold|extrabold|black)\b' $scope --include=*.vue
# hex or arbitrary colors in templates and scripts
grep -rnE '#[0-9a-fA-F]{3,8}\b|(bg|text|border|ring|fill|stroke)-\[#' $scope --include=*.vue
# raw elements that usually have a component
grep -rnE '<(button|input|select|textarea|table)\b' $scope --include=*.vue
# styles outside Tailwind classes, and arbitrary values
grep -rnE '\bstyle="|\b[a-z-]+-\[[0-9.]+(px|rem)\]' $scope --include=*.vue
# icons not imported one by one: whole packs, library.add() (faLibrary.add() too), icons named
# by string
grep -rnE "import \{ (fas|far|fab|fal) \}|[lL]ibrary\.add\(|['\"]fa[srlb]['\"], *['\"][a-z0-9-]+['\"]|['\"]fa-(solid|regular|light|brands) fa-" $scope --include=*.vue --include=*.ts
# deprecated components, from components.json (references/components.md)
deprecated=$(curl -s https://nethesis.github.io/vue-components/components.json |
  jq -r '[.components[] | select(.deprecated) | .name] | join("|")')
grep -rnE "\b($deprecated)\b" $scope --include=*.vue --include=*.ts
# deprecated props, types and functions of the installed version, with the lines that name them
grep -rn -A3 @deprecated node_modules/@nethesis/vue-components/dist --include=*.d.ts
```

Search the files in scope for each name the last command finds.

When a whole project uses the same pattern, such as icons named by string in every file, report
it once for the project with a few examples, not line by line.

## What to check

- **Components**: custom markup where a component or a pattern exists; classes that override a
  component instead of using its props; deprecated components; more than one `primary` button
  in a view or dialog.
- **Colors**: hex or arbitrary values; Tailwind palette classes where the project defines a
  semantic color for that role; palette names instead of `primary-*`; colors without a dark
  theme value (`references/colors.md`).
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
- **Accessibility**: form fields without a label, interactive elements that cannot be reached or
  used with the keyboard, focus rings removed.

## Report

Group the problems by file, most serious first. For each one give:

- the severity: **critical** (broken or inaccessible for some users), **high** (wrong component,
  color or text the user sees), **medium** (inconsistent with the design system, but works),
  **low** (style or naming). A deprecated component is high; an icon other than the one of its
  meaning is medium, and so is an English label that screen readers read in the Italian
  interface;
- `path:line`;
- the problem, in one sentence;
- the rule it breaks, with a link to its source. Components and patterns, glossary terms, icon
  meanings and color tokens have their own `link` in `components.json`, `glossary.json`,
  `icons.json` and `colors.json`. A section of the writing guidelines is
  `https://nethesis.github.io/design-system/?page=writing-guidelines#<heading>`, with the heading
  written lowercase with hyphens (`#buttons-and-actions`). For a rule that comes only from this
  skill, cite the skill;
- the fix, as a short code change when it is obvious.

End with what you did not check, if anything.
