# Reviewing against the design system

Review what was asked: a component, a page, or the whole frontend. Report the problems; change
code only if asked to.

## Mechanical checks

Run these first on the files in scope, adapting the path. They find candidates, not certain
problems: read each match before reporting it.

```bash
# weights the design system does not use
grep -rnE 'font-(semibold|bold|extrabold|black)\b' src --include=*.vue
# hex or arbitrary colors in templates and scripts
grep -rnE '#[0-9a-fA-F]{3,8}\b|(bg|text|border|ring|fill|stroke)-\[#' src --include=*.vue
# raw elements that usually have a component
grep -rnE '<(button|input|select|textarea|table)\b' src --include=*.vue
# deprecated components
grep -rnE '\b(NeBadge|NeDropdownFilter|NeToastNotification)\b' src --include=*.vue
```

The last pattern matches the names without `V2`; update it from the `[Deprecated]` titles in the
Storybook index (`references/components.md`).

## What to check

- **Components**: custom markup where a component or a pattern exists; classes that override a
  component instead of using its props; deprecated components.
- **Colors**: hex or arbitrary values; Tailwind palette classes where the project defines a
  semantic color for that role; palette names instead of `primary-*`; colors without a dark
  theme value (`references/colors.md`).
- **Typography**: weights other than `font-normal` and `font-medium`; sizes outside the text
  styles of `foundations.json`.
- **Icons**: icons not from Font Awesome Solid or the Nethesis packages; decorative icons without
  `aria-hidden="true"`; icon-only buttons without an accessible label and a tooltip.
- **Text**: literal strings instead of i18n keys; texts that break the writing guidelines; terms
  the glossary lists under `avoid` (`references/text.md`).
- **Accessibility**: form fields without a label, interactive elements that cannot be reached or
  used with the keyboard, focus rings removed.

## Report

Group the problems by file, most serious first. For each one give:

- `path:line`;
- the problem, in one sentence;
- the rule it breaks, with a link to its source (the Storybook story, the section of the writing
  guidelines, the glossary term, the color token);
- the fix, as a short code change when it is obvious.

End with what you did not check, if anything.
