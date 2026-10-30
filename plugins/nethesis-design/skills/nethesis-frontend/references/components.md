# Components and patterns

`@nethesis/vue-components` holds the Vue 3 components of Nethesis interfaces (`Ne*`) and the
patterns: ready-made combinations of components for a whole interaction, such as the delete
confirmation modal or the table page.

## Pattern, component or custom markup

1. **Pattern** when the task is a whole interaction a pattern covers. Copy its structure and
   texts, then adapt the data.
2. **Component** when the case differs from the pattern or is a single element.
3. **Custom markup** only when no component fits. Build it with Tailwind classes that match the
   components (same spacing, radius, ring and semantic colors), and say in your answer which
   part is custom.

## Common cases

The patterns named below are in the `patterns` of `components.json` (see "Finding what exists"),
with their Storybook links and the code of their stories.

- **Loading**: `NeSkeleton` in place of the content that is loading; for a table, the `loading`
  prop of `NeTable`.
- **Nothing to show**: `NeEmptyState`, with a title, a description and, when there is a next
  step, an action. Follow the *Empty state* pattern.
- **An error in a page or a form**: `NeInlineNotification`. Follow the *Inline error
  notification* pattern.
- **The result of an action** the user should notice, such as an object created or deleted: a
  toast, `NeToastNotificationV2`. Follow the *Success toast notification* pattern. After closing
  a modal or a drawer, show the toast once the closing animation has ended, about 500 ms later,
  or it appears while the dialog is still moving.
- **Creating or editing an object**: a form in a side drawer, opened by the create button of the
  page or the Edit action of a row. Follow the *Create item drawer* pattern.
- **Deleting**: follow the *Delete item modal* pattern; its *Type to confirm* story is for
  deletions that lose a lot of data. Products that archive objects before destroying them, such
  as My Nethesis, follow the "Archive and destroy confirmation" of the writing guidelines.
- **A status** (enabled, expired, online…): `NeBadgeV2`.
- **Buttons that start an action**: `NeButton` with the `kind` its story uses for that role, and
  `loading` bound while the action runs. Only one `primary` button per view or dialog: the
  others are `secondary` or `tertiary`. A button that confirms a destructive action is `danger`,
  in place of the `primary`.
- **Tables on small screens**: `NeTable` shows each row as a card below its `cardBreakpoint`.
  Follow the *Table page* pattern for a page that lists objects. Write the rest of the layout
  mobile first, with the Tailwind breakpoints (`sm:`, `md:`, `lg:`…).

## Forms

- Every field has a `label`. Show validation errors through `invalidMessage`, not with separate
  text, and helper text through `helperText`.
- Validate with the library and the helpers the project already uses (valibot in My Nethesis
  and NethSecurity): find an existing form and follow it.
- An error that is not about one field, such as a failed save, goes in an
  `NeInlineNotification` (*Inline error notification* pattern).
- For a new password, follow the *New password form* pattern.
- The texts of labels, helper texts and validation messages follow the "Forms" section of the
  writing guidelines (`references/text.md`).

## Finding what exists

The Storybook pages cannot be read. Read the list of its components and patterns instead:

```
https://nethesis.github.io/vue-components/components.json
```

Fetch it with `curl -s` and filter it with `jq`, for example
`jq -r '.components[] | "\(.name): \(.description)"'`. Each entry of `components` and
`patterns` has:

- `description`: what it is for, and which component to use in the cases it does not cover.
  Choose by the description, not by the name.
- `deprecated` and `replacedBy`: never use a deprecated component; use its `replacedBy`.
- `parts`: components documented with this one (`NeTableHead`, `NeTableRow`… with `NeTable`).
- `storiesSource`: the code of its stories. Read it before using the component or the pattern:
  the template, the props passed in each story and the texts.
- `componentSource`: the code of the component, when the stories are not enough.
- `link` and `stories[].link`: its Storybook pages, to cite in a review.

Deprecated props, types and functions are not in `components.json`: the installed package marks
them with `@deprecated`, with their replacement
(`grep -rn -A3 @deprecated node_modules/@nethesis/vue-components/dist --include=*.d.ts`: the name
is on the lines after the comment). The `multiple` prop of `NeCombobox` is one: use
`NeMultiselectCombobox`.

## The installed version

The Storybook and `components.json` are built from the main branch of vue-components: their
`version` is the latest release, and they may include changes not released yet. The project may
have an older version. Before using a component, a prop or an event, check the installed version:

- `node_modules/@nethesis/vue-components/package.json` for the version;
- `node_modules/@nethesis/vue-components/dist/main.d.ts` for what the package exports;
- `node_modules/@nethesis/vue-components/dist/components/<Name>.vue.d.ts` for the props, slots
  and events. The defaults of the props are not there: they are in the component's
  `componentSource` (latest version) or in `dist/vue-components.js` (installed version).

If the version in `node_modules` differs from the one in `package-lock.json`, say so: the
developer should run `npm ci`. Write for the version of the lockfile.

If that version lacks a component or a prop that the task needs, say so and suggest updating the
dependency instead of rebuilding it. Until it is updated, use the closest component the version
has, with a `TODO` comment that names the one to use. The code of the patterns follows the latest
version: if it does not work with the installed one, adapt it and say so.

## Usage and setup

```vue
<script setup lang="ts">
import { NeButton, NeTextInput } from '@nethesis/vue-components'
</script>
```

The project's main CSS file imports `@nethesis/vue-components/theme.css` and declares
`@source` on the package; both are needed for the components to be styled. Dark theme uses the
`.dark` class on an ancestor (`@custom-variant dark`), and every component supports it.

To set up a new project, follow the Installation, Fontawesome and Font sections of the README of
vue-components (https://github.com/nethesis/vue-components#installation): the theme and
`@source`, the Font Awesome CSS in a layer below Tailwind, and Poppins Regular and Medium.
