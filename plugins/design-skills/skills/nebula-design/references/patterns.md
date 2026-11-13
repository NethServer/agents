# NDS patterns: ready-made compositions

From the "Patterns" section of Storybook (`stories/Pattern*.stories.ts` in nethesis/vue-components, v3.16.0). Each pattern has an English and an Italian story: open them when in doubt. Start from these when building a page or a flow. The list with links is in `site/components-index.md`; the copy rules they follow are in `site/writing-guidelines.md`.

## Contents
1. Table page (list + toolbar + empty states)
2. Create item drawer (create / edit)
3. Delete item modal
4. Success toast notification
5. Inline error notification
6. Empty state
7. New password form
8. Library helpers

---

## 1. Table page

Top to bottom:
1. **Page title**: the name of the page in the menu, usually the plural object (`Phonebook contacts`), with `NeHeading`.
2. **Description + create button**: one sentence `List of <objects>, including <main attributes>.` in `max-w-2xl text-gray-600 dark:text-gray-400` (Text/Tertiary neutral), Primary `size="lg"` `Create <object>` with `circle-plus` on its right (below it on small screens). Container `mb-8 grid gap-x-4 gap-y-2 sm:grid-cols-[1fr_auto] sm:items-center`.
   - Without a description, the create button goes on the right of the toolbar (above it on small screens).
   - With no objects yet, the create button is **only** in the empty state (one Primary per page).
3. **Toolbar** `mb-6 flex flex-wrap items-center gap-4`: `NeTextInput is-search` placeholder `Filter <objects>` (**standard width 320 px**: `class="w-full sm:w-80"`), one `NeDropdownFilterV2` per data category (label = column name), `NeSortDropdown`, Tertiary `Reset filters` (**team rule: always visible, disabled when no filter differs from its default**; it resets the text filter too, never the sort).
4. **Content**, one of:
   - loading → `NeTable :loading="true"` (skeleton), never an empty state
   - nothing created → `NeEmptyState` Solid section icon, `No <objects> configured` + a description (almost always), Primary lg `Create <object>`
   - filters match nothing → `NeEmptyState` `magnifying-glass`, `No <objects> found` / `Try changing your search filters.`, Tertiary lg `Reset filters` (only a text filter → description `Try different or fewer words.`; **the button is always `Reset filters`**, team rule)
   - data → `NeTable` + `NePaginator` in `#paginator`
5. **Row actions** (last column, no header), team rules that differ from the Storybook pattern:
   - object without a page of its own: Tertiary `Edit` (`pen-to-square`), which opens the edit drawer showing all its data; object with a dedicated page: Tertiary `Details` (`eye`, + object name for screen readers);
   - kebab: `NeDropdown` (`align-to-right`) with its Tertiary icon button (`ellipsis-vertical`, primary color, `Open menu`): the other actions, then a **divider**, then `Delete` (`trash`, `danger: true`);
   - the name in the first column is plain text, **not clickable** (Storybook shows it as a link-styled button);
   - statuses as icon + label, never badges (`components.md` §4);
   - header cells Text/Primary neutral, every body cell Text/Secondary neutral Regular.
   Every `NeTableCell` has `:data-label` (card layout on small screens), the actions cell too (`Actions`): in cards the buttons are the value of that row, left-aligned (`-ml-2.5 flex gap-2 xl:ml-0 xl:justify-end`), see `figma-components.md` §8.

Standard labels from the pattern: `Sort`, `Sort by`, `Sort direction`, `Ascending`, `Descending`, `Open filter`, `No options`, `Continue typing to show more options`, `Clear search`, `Filter options`, `Go to previous page`, `Go to next page`, `Pagination`, `Show`, `Actions`.

```vue
<NeHeading tag="h1">Phonebook contacts</NeHeading>
<div class="mb-8 grid gap-x-4 gap-y-2 sm:grid-cols-[1fr_auto] sm:items-center">
  <p class="max-w-2xl text-gray-600 dark:text-gray-400">
    List of phonebook contacts, including phone number and company.
  </p>
  <NeButton v-if="contacts.length" kind="primary" size="lg" class="mt-2 justify-self-start sm:mt-0">
    <template #prefix><FontAwesomeIcon :icon="faCirclePlus" aria-hidden="true" /></template>
    Create contact
  </NeButton>
</div>
<div class="mb-6 flex flex-wrap items-center gap-4">
  <NeTextInput v-model="textFilter" is-search placeholder="Filter contacts" aria-label="Filter contacts"
    clear-search-label="Clear search" class="w-full sm:w-80" />
  <NeDropdownFilterV2 v-model="companyFilter" kind="checkbox" label="Company" :options="companyOptions"
    clear-filter-label="Clear selection" open-menu-aria-label="Open filter" no-options-label="No options"
    more-options-hidden-label="Continue typing to show more options" clear-search-label="Clear search"
    options-filter-placeholder="Filter options" />
  <NeSortDropdown v-model:sort-key="sortKey" v-model:sort-descending="sortDescending" label="Sort"
    :options="sortOptions" open-menu-aria-label="Open menu" sort-by-label="Sort by"
    sort-direction-label="Sort direction" ascending-label="Ascending" descending-label="Descending" />
  <NeButton kind="tertiary" @click="resetFilters">Reset filters</NeButton>
</div>
<!-- then: NeTable :loading / NeEmptyState (no items configured) / NeEmptyState (no items found) / NeTable + NePaginator -->
```

In product code strings go through `t()`; in mockups write the real English text.

## 2. Create item drawer

Radio buttons are always stacked vertically (team rule).


`NeSideDrawer` opened by the create button. Title `Create contact`; fields with noun labels (`Name`, `Phone number`, `Company` marked `Optional`), placeholder `e.g. +39 0123 456789`, validation `Enter a name`, `Enter a valid phone number`; footer Tertiary `Cancel` + Primary `Create` (loading while saving; pending decision, the site still says `Create contact`). Save error → `NeInlineNotification kind="error"` `Cannot create contact` / `Network error. Check your connection and reload the page.` First field focused, Enter saves. After saving the drawer closes and the Success toast pattern runs (if the change is applied immediately).

Edit: same drawer, title `Edit contact`, main button `Save`.

Long or multi-step forms → a page with `NeStepper`, `Previous` / `Next`, last step labelled with the real action (`Install`, `Create`), never `Done`.

## 3. Delete item modal

Kebab `Delete` → `NeModal kind="warning"`, title `Delete phonebook contact`, body `Phonebook contact Jane Doe will be deleted.`, `Cancel` + `Delete` (`primary-button-kind="danger"`, loading while deleting) → success toast `Phonebook contact deleted` / `Phonebook contact Jane Doe has been deleted`.

Type to confirm (deletions that lose a lot of data): title `Delete user`, body `User Alice Fox will be permanently deleted. Their personal files will be deleted too.`, `NeTextInput` labelled `Type 'Alice Fox' to confirm`, Delete disabled until it matches.

## 4. Success toast notification

After create / update / delete applied immediately: `User created` / `User Alice Fox has been created`, `User updated` / `... has been updated`, `User deleted` / `... has been deleted`. None when the result is already visible on the page, none for staged changes (NethSecurity "Unsaved changes"). Use the product's notification store.

## 5. Inline error notification

Network error: `Cannot save phonebook contact` / `Network error. Check your connection and reload the page.` Generic: same title / `Something went wrong.` Server errors by kind: field errors → validation text from an i18n key; object-state errors without a field → the server message as it is, capital first letter; network and 5xx → a fixed text, never the server message.

## 6. Empty state

Stories: No items (`No voicemail messages` / `You currently have no voicemail messages.`, voicemail icon, no action), No items configured (`No users configured`, `user-group`, Primary `Create user`; the team adds a description here too), No items found (`No users found` / `Try changing your search filters.`, `magnifying-glass`, Tertiary `Reset filters`), Restricted page (`Restricted page` / `It seems that you don't have the necessary permissions to view this page.`, `ban`, Primary `Go to Dashboard` with `arrow-right`). Details in `components.md` §6.

## 7. New password form

`NeTextInput is-password` + `NePasswordRequirements` with `usePasswordRequirements`; requirements checked while typing, errors shown after a submit attempt; confirmation field labelled `Confirm new password` with `Passwords do not match`; button `Change password`.

## 8. Library helpers

`useItemPagination`, `useSort`, `usePasswordRequirements`, `sortByProperty`, `getAxiosErrorMessage`, `byteFormat1024`/`byteFormat1000`, `kbpsFormat`, date helpers (`formatDateTime`, `formatRelativeTime`, `formatDurationLoc`…), `savePreference`/`getPreference`. Mention them in the handoff when a screen needs them.
