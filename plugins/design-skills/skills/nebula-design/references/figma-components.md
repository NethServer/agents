# Nebula Figma components: specs read from the file

Source: the Nebula Design System Figma file (`ZRZzzlqb9GfB9Xdz6iGufh`), read on 2026-11-10 with the Figma connector. **The Figma component wins** over Storybook classes and over this file when they differ: read it again when in doubt (see "How to read a component" at the end). Token names are the Figma variables; their Tailwind classes are in `site/colors.md`.

## Contents
1. Rules for every component
2. Side drawer
3. Text input
4. Radio selection
5. Icon button
6. Main sidebar
7. How to read a component
8. Library look to copy in prototypes

---

## 1. Rules for every component

- **Draw only what is visible by default.** Boolean properties that are off by default (e.g. the resize control of the sidebar, "Show 4/5" options of Radio selection, "Show helper", "Optional", "Info") are elements the team hasn't decided or doesn't want by default: don't draw them unless the designer asks.
- Every interactive element has its **focus state** from Figma: focus ring 1 (2 px ring) on fields, focus ring 2 (2 px gap + 2 px ring) on buttons, radio, checkbox, toggle. Ring color = `Product Primary/<product>/Focus`: **light `primary-500`, dark `primary-200`** (so `focus:ring-primary-500 dark:focus:ring-primary-200`). Make sure no `dark:ring-*` class of the resting state overrides the focus color in dark mode.
- Hover, selected and disabled states come from the component's variants, never invented.

## 2. Side drawer (`NeSideDrawer`)

Component "Side drawer", variants Product × Type (Default, Sections).

- Panel 540 px wide, `Elevation/L1` background, shadow `Shadow/Drawer`, padding 24, vertical gap 24, over the `Surface/Overlay` dimmed page.
- **Title row**: title `text-xl` (20 px) Medium, `Text/Primary neutral`; close icon button `xmark` 16 px on the right, in **`Icon/Primary neutral`** (`text-gray-900 dark:text-gray-50`), never the product color (Storybook `NeSideDrawer` uses `text-gray-700 dark:text-gray-200`: Figma wins); the same applies to the close button of `NeModal`; **divider below** (`Border/Ring/Layout divider`, 1 px) with 24 px padding below the title.
- **Content**: fields with vertical gap 32; **divider below** (1 px) with 32 px padding below the last field.
- **Actions**: right after the content (not a sticky footer, no full-width bar), **right-aligned**, gap 24: Tertiary (Cancel) then Primary, both size lg (padding 8/12, radius 6).
- Type=Sections: same, with section titles between groups of fields.

## 3. Text input (`NeTextInput`)

- Label: 14 px Medium, `Text/Secondary neutral`, 8 px above the field. "Optional" on the right of the label only when the field is optional (property off by default).
- Field: 36 px high, padding 8/12, radius 6, `Surface/Background/Input`, 1 px ring `Border/Ring/Button` (`ring-gray-300 dark:ring-gray-500`), text 14 px Regular `Text/Primary neutral`, placeholder `Text/Placeholder`.
- States: Enable, **Focus** (no gray ring; Focus ring 1 = 2 px `Product Primary/Focus`), Read only, Disable. Helper text below (off by default) in `Text/Tertiary neutral`.
- **Invalid** (from `NeTextInput`): ring `ring-rose-700 dark:ring-rose-500`, and **on focus the ring stays rose** (`focus:ring-rose-500`), never the product focus color; `circle-exclamation` 16 px `text-rose-700 dark:text-rose-400` inside the field on the right (`pr-10`); the message replaces the helper text, `text-rose-700 dark:text-rose-400`. When one message covers two fields (e.g. `Enter at least one list URL`), both fields take the invalid state and the message.

## 4. Radio selection (`NeRadioSelection`)

- Optional title 14 px Medium `Text/Secondary neutral`, 8 px above the list. Options **stacked vertically, gap 16**.
- Each option: radio 16 px + 10 px gap + label 14 px Regular `Text/Secondary neutral`, optional description 14 px Regular `Text/Tertiary neutral` below the label.
- Radio (`_input radio`): circle 16 px.
  - Not selected: `Surface/Background/Input` with a 1 px `Border/Ring/Input` ring.
  - **Selected: filled `Product Primary/<product>/Active`, with a 6 px white dot in the center** (`Surface/Toggle/Switch`).
  - Focus: Focus ring 2 (2 px gap white/black + 2 px `Product Primary/Focus`). Hover variant exists for both.
- Default shows 3 options; options 4 and 5 are off by default. Invalid message and info icon off by default.

## 5. Icon button (`NeButton` icon-only)

Square 36×36, padding 10, radius 6, icon 16 px. Types Primary, Secondary, Tertiary (+ AI Light, AI Dark); states Enabled, Hovered (fills the whole square: Tertiary uses `Surface/Button/Tertiary Hover`), Focused, Disabled. The kebab of table rows is the Tertiary one (`components.md`).

## 6. Main sidebar

Component "Main sidebar + labels" (node 1427:791), variants NethSecurity, NethVoice, User portal, Controller, My Nethesis. Full NethSecurity values: `products/nethsecurity.md`. The **resize control at the bottom is off by default: don't draw it.**

## 7. How to read a component

When a screen needs a component not described here, or a detail is missing:
1. `search_design_system` on the Nebula file, restricted to the Nebula library (the file also has Carbon libraries: ignore them for Nebula products).
2. A **read-only** `use_figma` call (after loading the figma-use skill) on the component set: variant names, `componentPropertyDefinitions` with their defaults, and for the variant of the product: sizes, padding, gap, radius, fills, strokes and effects with their bound variables and effect styles, text styles. `get_screenshot` for a visual check.
3. Draw it with those values and add the spec here (sections 2–6) in the next skill update.


---

## 8. Library look to copy in prototypes

Read from `@nethesis/vue-components` (Storybook wins for look and behavior). A prototype that redraws these by hand must match them; these are the details that were drawn wrong before.

- **Tooltip** (`NeTooltip`, tippy theme `tailwind`): `bg-gray-800 border-gray-800 text-gray-50 shadow-2xl`, dark `bg-gray-100 border-gray-100 text-gray-900`; text 14 px, line height 1.4, padding 5/9 px, radius 4 px, **max width 350 px, text wraps**; **always an 8 px arrow** pointing to the trigger; placement `top` by default, flips below when there is no room; it is mounted outside its container, so it is never clipped by a table or a card. Default trigger: `circle-info` 16 px `text-indigo-500 dark:text-indigo-300`.
- **Kebab menu** (`NeDropdown`): panel `min-w-40 rounded-md bg-white py-2 shadow-lg ring-1 ring-gray-200 dark:bg-gray-950 dark:ring-gray-700`, `mt-2.5`, aligned to the right edge of the trigger; items `px-4 py-2 text-sm`, icon 20 px `mr-2`. **When the menu opens with the mouse, no item is highlighted** (only keyboard opening moves focus to the first item). Normal item `text-gray-700 dark:text-gray-50`, hover `bg-gray-200 text-gray-900 dark:bg-gray-700 dark:text-gray-50`. **Danger item** `text-rose-700 dark:text-rose-500`, hover/active **`bg-rose-700 text-white dark:bg-rose-600 dark:text-white`** (not a gray hover).
- **Paginator** (`NePaginator`): bar `border-t border-gray-300 bg-white px-6 py-3 text-sm text-gray-700 dark:border-gray-600 dark:bg-gray-950 dark:text-gray-100`; left `1 - 10 of 44`, then `Show` + **`NeListbox`** (not a native select): button `min-h-9 rounded-md bg-white py-1.5 pl-3 pr-10 ring-1 ring-inset ring-gray-300 shadow-sm hover:bg-gray-200/70 dark:bg-gray-950 dark:ring-gray-600`, `chevron-down` 12 px `text-gray-500` on the right; options `py-2 pl-3 pr-9`, active `bg-gray-100 dark:bg-gray-800`, selected `font-medium` + `check` in primary on the right. Pages: `h-10 text-base`, joined cells `border border-gray-300 px-4 text-gray-500 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-900`, first `rounded-s-lg`, last `rounded-e-lg`, current `bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-white`.
- **Table** (`NeTable`): container `rounded-lg border border-gray-300 shadow-sm dark:border-gray-600`, header `bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-50`, cells `px-6 py-4`, header cells `px-6 py-3 font-medium`, rows `divide-gray-300 dark:divide-gray-600` with hover `bg-gray-100 dark:bg-gray-800`. **Card layout** (below `card-breakpoint`): every cell is a row of two columns, label (`font-medium` Text/Primary neutral) on the left, value on the right; the **actions are the value of the `Actions` row**, left-aligned (`-ml-2.5 flex gap-2`, then `xl:ml-0 xl:justify-end` in table mode), never a separate block at the bottom right of the card. A row without actions shows no `Actions` row.
- **Dropdown filter and Sort triggers** (`NeDropdownFilterV2`, `NeSortDropdown`): neutral button `text-gray-700 ring-1 ring-gray-300 shadow-sm hover:bg-gray-200/70 dark:text-gray-100 dark:ring-gray-500`, label + gray `NeBadgeV2` xs with the count + `chevron-down` 12 px; never Primary or the product color. Panel `min-w-40 px-4 py-2 mt-2.5 ring-gray-900/5`; checkbox filters start with the `Clear selection` link.
- **Inline notification** (`NeInlineNotification`): `rounded-md border-l-4 p-4 text-sm`, icon 16 px, title `font-medium mb-2`. Info `border-blue-500 bg-blue-100` (dark `border-blue-300 bg-blue-900`), Warning `border-amber-500 bg-amber-100` (dark `border-amber-300 bg-amber-700`), Error `border-rose-500 bg-rose-100` (dark `border-rose-300 bg-rose-900`).
