# Reviewing against the design system

Review what was asked: a component, a page, or the whole frontend. Report the problems; change
code only if asked to.

## Mechanical checks

Run these first, from the frontend folder (in My Nethesis, `frontend`; in NethServer 8 core,
`core/ui`). They find candidates, not certain problems: read each match before reporting it. In a
NethServer 8 project built with Carbon, run only the text checks.

Text checks, for every project with i18n files:

```bash
# the files in scope: src for the whole frontend, or the files of a page
scope=src
# the file types: templates, and templates with scripts (React: *.tsx, and *.tsx with *.ts;
# Vue 2: *.vue with *.js)
views='--include=*.vue'
code='--include=*.vue --include=*.ts'
# the English i18n file (references/text.md)
en=src/i18n/en/translation.json
# keys the code uses that the English file lacks: the user sees the key path. Written for t('…')
# and $t('…') with dots in the path; keys built at run time show up cut, ignore them
grep -rhoE "\bt\(['\"][a-zA-Z0-9_.-]+['\"]" $scope $code | sed -E "s/.*\(['\"]//; s/['\"]$//" |
  sort -u | while read -r k; do
    jq -e --arg k "$k" 'getpath($k | split("."))' $en >/dev/null || echo "missing: $k"
  done
# terms the glossary lists under avoid, with the approved terms, skipping lines that already use
# them; a word avoided for an action can be right in another meaning ("New password")
curl -s https://nethesis.github.io/nebula-design-system/glossary.json |
  jq -r '[.terms[].en] as $ok | [.terms[] | .en as $t | .avoid.en[]? | {avoid: ., term: $t}]
    | group_by(.avoid)[] | select(.[0].avoid as $a | $ok | index($a) | not)
    | "\(.[0].avoid)\t\(map(.term) | join("|"))"' |
  while IFS=$'\t' read -r avoid terms; do
    grep -nwF -- "$avoid" $en | grep -vF -f <(tr '|' '\n' <<<"$terms") |
      sed "s/^/[$avoid → ${terms//|/ or }] /"
  done
```

Checks of components, colors, icons and code, for projects built with Tailwind CSS and
`@nethesis/vue-components`, and for colors and icons in other stacks:

```bash
# weights the design system does not use
grep -rnE 'font-(semibold|bold|extrabold|black)\b' $scope $views
# hex, rgb() or arbitrary colors
grep -rnE '#[0-9a-fA-F]{3,8}\b|rgba?\(|(bg|text|border|ring|fill|stroke)-\[#' $scope $views
# raw elements that usually have a component
grep -rnE '<(button|input|select|textarea|table)\b' $scope $views
# styles outside Tailwind classes (style="…" and style={{…}}), and arbitrary values
grep -rnE '\bstyle=["{]|\b[a-z-]+-\[[0-9.]+(px|rem)\]' $scope $views
# click handlers on an element that is not a button or a link: each match names the element
# the handler belongs to, the last tag opened on its line or before it (Prettier wraps tags)
for f in $(grep -rlE '@click|v-on:click|onClick=' $scope $views); do
  awk -v f="$f" '/<[A-Za-z]/ { if (match($0, /<[A-Za-z][A-Za-z0-9.-]*/)) tag = substr($0, RSTART + 1, RLENGTH - 1) }
    /@click|v-on:click|onClick=/ && tag !~ /^(NeButton|NeLink|button|a|RouterLink|router-link|Button|Link)$/ {
      print f ":" FNR ": <" tag ">" }' "$f"
done
# text dimmed with opacity, skipping disabled controls and transitions; a dimmed row of an
# archived or turned-off item is text, not a disabled control: report it
grep -rnE '\btext-[a-z]+-[0-9]+/[0-9]+|\bopacity-[0-9]+\b' $scope $views |
  grep -vE 'disabled|cursor-not-allowed|enter-|leave-'
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
  (writing guidelines, "Style"); i18n keys the code uses that the English file lacks; props of
  `Ne*` components that end in `Label` left to their
  English default in a project with i18n. List them for a component with
  `grep -oE '\b[a-z][a-zA-Z]*Label\b' node_modules/@nethesis/vue-components/dist/components/<Name>.vue.d.ts | sort -u`.
- **Italian translations**: when developers edit the Italian file (`references/text.md`), check
  it too: terms the glossary lists under `avoid.it`, translations other than its `it`, and the
  Italian rules of the writing guidelines. When only Weblate edits it, report these for the
  translators.
- **Accessibility**, by the rules of
  https://nethesis.github.io/nebula-design-system/accessibility.md: form fields without a label,
  or a label linked to the wrong field (two fields with the same `id`); click handlers on
  elements that are not buttons or links, which the keyboard cannot reach; focus rings removed
  without a replacement; text dimmed with opacity (`text-gray-900/60`, `opacity-70`), except on
  disabled controls, archived or turned-off items included (they take the tertiary neutral text
  and icon tokens and a status); status shown by color alone; overlays built by hand instead of `NeModal`
  or `NeSideDrawer`; a `lang` attribute that does not follow the interface language.

## Report

Group the problems by file, most serious first. For each one give:

- the severity: **critical** (broken or inaccessible for some users), **high** (wrong component,
  color or text the user sees), **medium** (inconsistent with the design system, but works),
  **low** (style or naming). For example: a control that the keyboard cannot reach, with no
  other way to do the same thing, is critical; text below the WCAG AA contrast, a deprecated
  component, an i18n key path shown to the user and a term the glossary lists under `avoid` are
  high; a gray one step away from the token, an icon other than the one of its
  meaning and an English label that screen readers read in the Italian interface are medium;
- `path:line`;
- the problem, in one sentence;
- the rule it breaks, with a link to its source. Components and patterns, glossary terms, icon
  meanings and color tokens have their own `link` in `components.json`, `glossary.json`,
  `icons.json` and `colors.json`. A section of the writing guidelines is
  `https://nethesis.github.io/nebula-design-system/?page=writing-guidelines#<heading>`, with the
  heading written lowercase with hyphens (`#buttons-and-actions`). For a rule that comes only from this
  skill, cite the skill;
- the fix, as a short code change when it is obvious.

End with what you did not check, if anything. A review does not run the app: list the checks of
"Before you finish" in SKILL.md that the developer should do after the fixes.
