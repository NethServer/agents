# NDS patterns: ready-made compositions

The patterns are the "Patterns" section of Storybook: `stories/Pattern*.stories.ts` in nethesis/vue-components, each with an English and an Italian story. Start from them when building a page or a flow: read the story for the layout, the components, the standard labels (Sort, Filter options, Go to next page…) and the code; the copy follows `site/writing-guidelines.md`. The list with links is in `site/components-index.md`.

This file only has what the UX team does differently from the stories, or adds to them.

## Contents
1. Table page
2. Create item drawer
3. Delete item modal
4. Success toast notification
5. Inline error notification
6. Empty state
7. Library helpers

---

## 1. Table page

Story: `PatternTablePage`. Team rules on top of it:
- **Description + create button** on the same row, the button on its right (below it on small screens), never on the filter row. Without a description, the create button goes on the right of the toolbar. With no objects yet, the create button is **only** in the empty state.
- **Text filter**: standard width 320 px (`w-full sm:w-80`).
- **`Reset filters` always visible** in the toolbar, disabled when no filter differs from its default; it resets the text filter too, never the sort. In the no-results empty state the button is **always `Reset filters`**, also when the only filter is the text one.
- **Row actions** (last column, no header), different from the story:
  - object without a page of its own: Tertiary `Edit` (`pen-to-square`), opening the edit drawer with all its data; object with a dedicated page: Tertiary `Details` (`eye`, + object name for screen readers);
  - kebab with the other actions, then a **divider**, then `Delete` (`danger: true`), see `components.md` §3;
  - the name in the first column is plain text, **not clickable** (the story shows it as a link-styled button);
  - statuses as icon + label, never badges (`components.md` §4);
  - header cells Text/Primary neutral, every body cell Text/Secondary neutral Regular.
- Every `NeTableCell` has `:data-label` (card layout on small screens), the actions cell too (`Actions`); in cards the buttons are left-aligned, see `figma-components.md` §8.
- States to draw: loading (`NeTable :loading`, never an empty state), nothing created, filters match nothing, data.

In product code strings go through `t()`; in mockups write the real English text.

## 2. Create item drawer

Story: `PatternCreateItemDrawer`. Team rules: footer Tertiary `Cancel` + Primary `Create` (pending decision: the story and the site still say `Create contact`); radio buttons always stacked vertically; edit variant titled `Edit <object>` with `Save`. After saving, the Success toast pattern runs only if the change is applied immediately. Long or multi-step forms → a page with `NeStepper`.

## 3. Delete item modal

Story: `PatternDeleteItemModal`; copy and type to confirm: "Delete confirmation" in the guidelines. Opened from the `Delete` item of the kebab.

## 4. Success toast notification

Story: `PatternSuccessToastNotification`; copy: "Success notifications". No toast for NethSecurity staged changes (`components.md` §9). Use the product's notification store.

## 5. Inline error notification

Story: `PatternInlineErrorNotification`; copy: "Error messages".

## 6. Empty state

Story: `PatternEmptyState`. Team rules in `components.md` §6 (Solid icon, a description almost always, also for "No items configured").

## 7. Library helpers

The library exports composables and helpers (pagination, sort, password requirements, byte and date formatting, preferences, Axios error messages): see `vue-components/src/composables` and `src/lib`. Mention them in the handoff when a screen needs them.
