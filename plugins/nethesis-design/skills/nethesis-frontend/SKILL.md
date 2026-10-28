---
name: nethesis-frontend
description: 'Use when writing, changing or reviewing the frontend of a Nethesis product built with Vue 3, Tailwind CSS and @nethesis/vue-components (My Nethesis, NethSecurity, NethVoice and others): pages, components, forms, tables, modals, notifications, colors, dark theme, interface text and translations, also from a Figma link, a mockup image or a description. Also use to check that a page, a component or a whole project follows the Nethesis Design System, and when adding or changing a component of @nethesis/vue-components itself. Not for NethServer 8 modules (Vue 2 with Carbon and ns8-ui-lib).'
---

# Nethesis frontend

Write and review frontend code that follows the Nethesis Design System. Read the reference file
for your task before writing code. Do not read all of them.

## Scope

Check `package.json` first. This skill applies when the project uses Vue 3, Tailwind CSS and
`@nethesis/vue-components`. If it uses Vue 2, `carbon-components-vue` or
`@nethserver/ns8-ui-lib`, it is a NethServer 8 interface, which follows the Carbon Design
System: say so, and apply only the writing guidelines and the glossary to its text
(`references/text.md`), nothing else from this skill.

If the project is `@nethesis/vue-components` itself (the `name` in `package.json`), the design
rules of this skill apply to its components too. Follow its `AGENTS.md` and `CONTRIBUTING.md`
for the rest: no hard-coded text, exports, stories with their description, deprecations.

## Sources, in this order

1. **`@nethesis/vue-components`**, its components and patterns, documented in the Storybook
   (https://nethesis.github.io/vue-components/). The main source. `references/components.md`
2. **Writing guidelines and glossary** of the Nethesis Design System. `references/text.md`
3. **Colors and foundations**, only when the task needs them: a color that is not in the
   project yet, a text style, an icon size, a shadow. `references/colors.md`, and
   https://nethesis.github.io/design-system/foundations.json for the rest. Icons:
   https://nethesis.github.io/design-system/icons.json.

The Storybook and the design system site are built in the browser: fetching their pages returns
no content. Read the plain files the reference files point to.

## Reference map

| Task | Read |
|---|---|
| Choosing a component or a pattern, its props, slots and events, deprecated components, the installed version | `references/components.md` |
| Labels, titles, descriptions, buttons, empty states, modals, notifications, validation messages, terms, Italian translations, i18n files | `references/text.md` |
| Colors, semantic tokens, `main.css`, dark theme, primary palette of the product | `references/colors.md` |
| Building from a Figma link, a mockup image or a description | `references/mockups.md` |
| Reviewing a component, a page or a project against the design system | `references/review.md` |

## Always applies

- Use a pattern or a component of `@nethesis/vue-components` before writing your own markup.
  Change it through its props and slots, not by overriding its classes. (`references/components.md`)
- Never use a deprecated component, prop or function in new code: `deprecated` in
  `components.json`, `@deprecated` in the installed package.
  (`references/components.md`)
- Colors come from the semantic tokens of the project's main CSS file, in both the light and the
  dark theme. No hex values or arbitrary colors in templates. (`references/colors.md`)
- Text uses only two weights of Poppins: `font-normal` and `font-medium`. Never `font-semibold`
  or `font-bold`.
- Icons: `FontAwesomeIcon` with the free Solid icons, each imported by name (never a whole
  icon pack); a Nethesis custom icon only when Font Awesome has none. Take the icon for each
  meaning (create, edit, delete, download, status…) from
  https://nethesis.github.io/design-system/icons.json, never an icon it lists under `avoid`.
  An icon next to a text label gets `aria-hidden="true"`; an icon without text needs an
  accessible label and a tooltip.
- Style with Tailwind classes on the spacing scale (`p-4`, `gap-6`): no `style` attributes, and
  no arbitrary values (`w-[137px]`) unless nothing else works.
- Every user-facing string goes in the i18n files, written by the writing guidelines with the
  terms of the glossary. (`references/text.md`)
- Interactive elements must work with the keyboard and keep a visible focus ring. Form fields
  need a label.
