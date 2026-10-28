---
name: nethesis-frontend
description: 'Use when writing, changing or reviewing the frontend of a Nethesis product, or checking that a page, a component or a whole project follows the Nethesis Design System: pages, components, forms, tables, modals, notifications, colors, dark theme, icons, interface text and translations, also from a Figma link, a mockup image or a description. Covers Vue 3 projects with Tailwind CSS and @nethesis/vue-components (My Nethesis, NethSecurity, the NethServer 8 user manager), changes to @nethesis/vue-components itself, and, for text, icons, colors and typography only, frontends built with other stacks, such as the React app of NethVoice CTI. For NethServer 8 modules built with Vue 2 and Carbon, only the text rules apply.'
---

# Nethesis frontend

Write and review frontend code that follows the Nethesis Design System. Read the reference file
for your task before writing code. Do not read all of them.

## Scope

Find the frontend's `package.json` (in My Nethesis, `frontend/package.json`) and check its
dependencies:

- **Vue 3, Tailwind CSS and `@nethesis/vue-components`**: the whole skill applies, NethServer 8
  apps built this way included.
- **`@nethesis/vue-components` itself** (its `name`): the design rules apply to its components.
  Its texts are props with English defaults, not i18n keys, and it has no installed version to
  check. Follow its `AGENTS.md` and `CONTRIBUTING.md` for stories, exports and deprecations.
- **Vue 2, `carbon-components-vue` or `@nethserver/ns8-ui-lib`**: a NethServer 8 module, which
  follows the Carbon Design System. Say so, and apply only the writing guidelines and the
  glossary (`references/text.md`).
- **Another stack, such as React** (NethVoice CTI): apply the rules for text, icons, typography,
  accessibility and foundations. For colors, no hex or arbitrary values: use the project's theme.
  Keep the project's own components, comparing their behavior with the matching `Ne*` component
  (`references/components.md`), and adapt the commands of `references/review.md` to its files
  (`*.tsx`).

When the project has its own `AGENTS.md` or `CLAUDE.md`, its rules win over this skill.

## Sources, in this order

1. **`@nethesis/vue-components`**, its components and patterns, documented in the Storybook
   (https://nethesis.github.io/vue-components/). The main source. `references/components.md`
2. **Writing guidelines and glossary** of the Nethesis Design System. `references/text.md`
3. **Icons, colors and foundations**: `icons.json` for the icon of each meaning; colors and
   foundations only when the task needs them, such as a color that is not in the project yet, a
   text style, an icon size, a shadow. `references/colors.md`, and
   https://nethesis.github.io/design-system/foundations.json for the rest.

The Storybook and the design system site are built in the browser: fetching their pages returns
no content. Read the plain files instead, all listed in
https://nethesis.github.io/design-system/llms.txt. Fetch them with `curl -s` and filter the JSON
files with `jq`: a tool that summarizes a page loses the field names.

## Reference map

| Task | Read |
|---|---|
| Choosing a component or a pattern, its props, slots and events, forms, deprecated components, the installed version, a new project | `references/components.md` |
| Labels, titles, descriptions, buttons, empty states, modals, notifications, validation messages, terms, Italian translations, i18n files | `references/text.md` |
| Colors, semantic tokens, `main.css`, dark theme, primary palette of the product | `references/colors.md` |
| Building from a Figma link, a mockup image or a description | `references/mockups.md` |
| Reviewing a component, a page or a project against the design system | `references/review.md` |

## Always applies

- Use a pattern or a component of `@nethesis/vue-components` before writing your own markup.
  Change it through its props and slots, not by overriding its classes. (`references/components.md`)
- Never use a deprecated component, prop or function in new code: `deprecated` in
  `components.json`, `@deprecated` in the installed package. (`references/components.md`)
- Colors are the semantic tokens of the design system, with a value for the light and one for
  the dark theme: the project's semantic class when it defines one, otherwise the token's
  Tailwind classes. No hex values or arbitrary colors in templates. (`references/colors.md`)
- Text uses only two weights of Poppins: `font-normal` and `font-medium`. Never `font-semibold`
  or `font-bold`.
- Icons: the icon that https://nethesis.github.io/design-system/icons.json gives for the
  meaning (create, edit, delete, download, status…), from the package of its `pack`, and never
  an icon it lists under `avoid`. For a meaning it does not list, a Font Awesome Solid icon that
  no other meaning uses. An icon next to a text label gets `aria-hidden="true"`; an icon
  without text needs an accessible label and a tooltip.
- Import each icon from the package of its pack and pass the imported object to
  `FontAwesomeIcon`:

  ```vue
  <script setup lang="ts">
  import { faTrash } from '@fortawesome/free-solid-svg-icons'
  </script>

  <template>
    <FontAwesomeIcon :icon="faTrash" aria-hidden="true" />
  </template>
  ```

  Never import a whole icon pack. Do not register icons with `library.add()` to use them by name
  (`:icon="['fas', 'trash']"`, `icon="fa-solid fa-trash"`): a wrong or unregistered name fails
  only at runtime, with an empty space instead of the icon, and the imports no longer show which
  icons a file uses. In a project that already does it, write the new code with imports, and
  convert the existing code only when asked.
- Style with Tailwind classes on the spacing scale (`p-4`, `gap-6`): no `style` attributes, and
  no arbitrary values (`w-[137px]`) unless nothing else works.
- Every user-facing string goes in the i18n files, written by the writing guidelines with the
  terms of the glossary. (`references/text.md`)
- Interactive elements must work with the keyboard and keep a visible focus ring. Form fields
  need a label.

## Before you finish

After writing or changing code:

1. Run the project's checks with the scripts of its `package.json`: lint, type-check and tests
   (in My Nethesis, `npm run pre-commit` in `frontend`).
2. Run the mechanical checks of `references/review.md` on the files you changed.
3. Check the result in the light and the dark theme, and with the keyboard: every new control
   reachable with Tab, with a visible focus ring.

Say which of these you could not do.
