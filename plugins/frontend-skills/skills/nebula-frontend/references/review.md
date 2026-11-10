# Reviewing against the design system

Review what was asked: a component, a page, or the whole frontend. Report the problems; change
code only if asked to.

## Mechanical checks

Run `scripts/review-checks.sh`, in the folder of this skill, first. Run it from the frontend
folder, the one with `package.json` (in My Nethesis, `frontend`; in NethServer 8 core,
`core/ui`), and pass the files or folders in scope (default `src`):

```bash
bash <skill folder>/scripts/review-checks.sh src/views/CustomersView.vue src/components/customers
```

It finds the English i18n file and the kind of project from `package.json`, and prints one
section for each check, with `none` when nothing matches:

- in every project: i18n keys the code uses that the English file lacks, and terms the glossary
  lists under avoid;
- not in NethServer 8 projects built with Carbon, which get only the text checks: font weights,
  hex and arbitrary colors, `style` attributes and arbitrary values, text dimmed with opacity,
  click handlers on elements that are not buttons or links, links without an address,
  `aria-label` on elements that show text, icons not imported one by one;
- only in projects that use `@nethesis/vue-components`: raw elements that usually have a
  component (not in vue-components itself), deprecated components, and the `@deprecated` lines
  of the installed version (of `src` in vue-components).

Pass `--en <file>` when it finds no English file, and `--text-only` to run only the text checks.
The matches are candidates, not certain problems: read each one before reporting it.

Search the files in scope for each name of the deprecated section. A class from
`foundations.json` that looks like an arbitrary value, such as the drawer shadow, is a token, not
a problem. An `aria-label` that starts with the visible text, such as `Show password` on a
`Show` button, is right.

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
  the glossary lists under `avoid` (`references/text.md`); server messages shown where the
  writing guidelines ("Error messages") want a text from the i18n files: a field error that is
  not turned into a key, or a network error or a 5xx that reaches the user as it is, such as
  `error.message` bound to the description of a notification with nothing in the project that
  replaces it (look for an HTTP interceptor first); the message of a 4xx with no field is right
  as it is; i18n keys the code uses that the English file lacks; props of `Ne*` components that
  end in `Label` left to their English default in a project with i18n. List them for a component
  with `grep -oE '\b[a-z][a-zA-Z]*Label\b'
  node_modules/@nethesis/vue-components/dist/components/<Name>.vue.d.ts | sort -u`.
- **Italian translations**: when developers edit the Italian file (`references/text.md`), check
  it too: terms the glossary lists under `avoid.it`, translations other than its `it`, and the
  Italian rules of the writing guidelines. When only Weblate edits it, report these for the
  translators.
- **Accessibility**, by the rules of
  https://nethesis.github.io/nebula-design-system/accessibility.md: form fields without a label,
  or a label linked to the wrong field (two fields with the same `id`); click handlers on
  elements that are not buttons or links, and links without an `href` (`NeLink` with only
  `@click`), which the keyboard cannot reach; focus rings removed without a replacement; an
  `aria-label` that replaces the visible text of a link or a button instead of containing it;
  text dimmed with opacity (`text-gray-900/60`, `opacity-70`), except on disabled controls,
  archived or turned-off items included (they take the tertiary neutral text and icon tokens and
  a status); status shown by color alone; overlays built by hand instead of `NeModal` or
  `NeSideDrawer`; a `lang` attribute that does not follow the interface language.

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
