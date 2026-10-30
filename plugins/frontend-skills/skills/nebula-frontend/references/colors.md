# Colors

## Where the colors are

Each project defines its colors in its main CSS file, the one that imports Tailwind CSS (for
example `frontend/src/assets/main.css` in My Nethesis, `src/assets/main.css` in NethSecurity).
Read it before choosing a color.

- **Primary palette**: `@theme` maps `--color-primary-50` … `--color-primary-950` to the palette
  of the product (sky for My Nethesis, cyan for NethSecurity, emerald for NethVoice). Use
  `primary-*` classes, never the palette name: `text-primary-700`, not `text-sky-700`.
- **Semantic colors**: a project can define named colors for each role, with a value for the
  light and one for the dark theme, in three places:

  ```css
  :root {
    --elevation-2: var(--color-gray-100);       /* light theme */
  }
  .dark {
    --elevation-2: var(--color-gray-800);       /* dark theme */
  }
  @theme inline {
    --color-elevation-2: var(--elevation-2);    /* makes bg-elevation-2, text-…, border-… */
  }
  ```

  A semantic class (`bg-elevation-2`) needs no `dark:` variant: the variable changes with the
  theme. Prefer it to a pair of Tailwind classes whenever the project defines it.

  Some projects define them as utilities instead, as NethSecurity does:

  ```css
  @utility text-tertiary-neutral {
    @apply text-gray-600 dark:text-gray-400;
  }
  ```

A project built with another stack, or with Tailwind CSS 3 (`tailwind.config.js`), has its own
theme: use its colors, find the token of each role in `colors.json` as below, and report the
colors whose values differ from the token's. vue-components itself has no semantic colors: see
`references/library.md`.

## Choosing a color

The colors of the design system are its semantic tokens, such as `Text/Secondary neutral`,
`Elevation/L2` or `Surface/Badge/Rose`. Their values for both themes and the matching Tailwind
classes are in:

```
https://nethesis.github.io/nebula-design-system/colors.json
```

Each token in `groups[].tokens[]` has `name`, `description`, `light` and `dark` (each with the
Figma `ref`, the `hex` value and the `tailwind` color to use in code, `primary-*` for the product
palette), `classes`, the Tailwind classes for both themes (`text-gray-700 dark:text-gray-200`),
and `link`, the token in the Colors page. `classes` is null when the utility depends on the
component, as for the product primary tokens: build the classes from the two `tailwind` colors
(`bg-primary-700 dark:bg-primary-500`). The file is large: filter it with `jq` for the token
you need, for example `jq '.groups[].tokens[] | select(.name == "Text/Secondary neutral")'`.

1. Find the token for the role: from the Figma mockup (its variables use these names), or by
   group and description.
2. If the project's main CSS file already defines a semantic color with the same light and dark
   values, use it, whatever its name.
3. Otherwise add the token to the main CSS file in the form the file already uses, following the
   names already there (Figma `Elevation/L2` became `--elevation-2` in My Nethesis,
   `Text/Tertiary neutral` became `text-tertiary-neutral` in NethSecurity). If the file has no
   semantic colors yet, create the three blocks above, after the `@theme` block of the primary
   palette.
4. Use `classes` from `colors.json` directly only for a one-off color that is not worth a token.

Never write hex values, `rgb()` or arbitrary colors (`text-[#374151]`) in templates.
