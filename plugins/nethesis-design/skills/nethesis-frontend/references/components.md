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

## Finding what exists

The Storybook pages cannot be read, but its index can:

```
https://nethesis.github.io/vue-components/index.json
```

Each entry of `entries` has a `title` (`Patterns/Delete item modal`, `Components/NeButton`,
`Components/NeBadge [Deprecated]`), a `type` (`docs` or `story`) and an `importPath`, the source
file of the stories in the vue-components repository. Read that file for the usage: the
template, the props passed in each story and the texts.

```
https://raw.githubusercontent.com/nethesis/vue-components/main/stories/NeButton.stories.ts
https://raw.githubusercontent.com/nethesis/vue-components/main/stories/PatternTablePage.stories.ts
```

- Components marked `[Deprecated]` have a newer version, usually with the `V2` suffix
  (`NeBadgeV2`, `NeDropdownFilterV2`, `NeToastNotificationV2`). Use the new one.
- The source of a component, when the stories are not enough:
  `https://raw.githubusercontent.com/nethesis/vue-components/main/src/components/<Name>.vue`.

## The installed version

The Storybook shows the latest version; the project may have an older one. Before using a
component, a prop or an event, check the installed version:

- `node_modules/@nethesis/vue-components/package.json` for the version;
- `node_modules/@nethesis/vue-components/dist/main.d.ts` for what the package exports;
- `node_modules/@nethesis/vue-components/dist/components/<Name>.vue.d.ts` for the props, slots
  and events.

If the project's version lacks a component or a prop that the task needs, say so and suggest
updating the dependency instead of rebuilding it.

## Usage

```vue
<script setup lang="ts">
import { NeButton, NeTextInput } from '@nethesis/vue-components'
</script>
```

The project's main CSS file imports `@nethesis/vue-components/theme.css` and declares
`@source` on the package; both are needed for the components to be styled. Dark theme uses the
`.dark` class on an ancestor (`@custom-variant dark`), and every component supports it.
