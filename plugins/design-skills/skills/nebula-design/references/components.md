# NDS components → `@nethesis/vue-components`

Which component to use and the design rules that go with it. The text rules (button labels, modal and toast copy, empty-state copy, filters) live on the design system site: `site/writing-guidelines.md`, with the terms of `site/glossary.md`. Icons come from `site/icons.md`. What each component is for, according to the library itself: `site/components-index.md`. Exact props, emits and slots: `components-api.md`.

If this file disagrees with the site or Storybook, the site wins for text, icons and colors, Storybook wins for how a component looks and behaves.

## Contents
1. Which component for which need
2. Button (`NeButton`)
3. Icon button (`NeButton` icon-only + `NeTooltip`)
4. Badge (`NeBadgeV2`)
5. Dropdown filter (`NeDropdownFilterV2`)
6. Empty state (`NeEmptyState`)
7. Modal (`NeModal`)
8. Side drawer (`NeSideDrawer`)
9. Toast notification (`NeToastNotificationV2`)
10. Inline notification (`NeInlineNotification`)
11. Gaps between guidelines and library

---

## 1. Which component for which need

| Need | Use | Not |
|---|---|---|
| Trigger an action | `NeButton` | a hand-styled `<button>`, a click on a `div` or a row |
| Go to another page or an external site | `NeLink` with an `href` (or a button labelled `Go to …` / `Open …`) | `NeButton` styled as a link; `NeLink` without `href` for an action (use a Tertiary `NeButton`) |
| Compact familiar action in table/toolbar/card | `NeButton` icon-only + `NeTooltip` | icon without tooltip |
| Menu of actions (kebab) of a row, card or page | `NeDropdown` (its default trigger: Tertiary icon button, primary color) | `NeDropdownFilterV2` |
| Filter a table/list by a data category | `NeDropdownFilterV2` | `NeDropdown`, deprecated `NeDropdownFilter` |
| Sort a table/list | `NeSortDropdown` (default trigger: neutral button, gray text and ring, label `Sort` + `chevron-down`; never Primary or the product color) | custom select, a Secondary `NeButton` as trigger |
| Status of an object (Enabled, Disabled, Expired…) | icon + label (team rule, see §4) | badge, colored text alone, a colored dot alone |
| Category, role, type; removable selected item | `NeBadgeV2` | deprecated `NeBadge` |
| Picture or initials of a user | `NeAvatar` | |
| Page or list with nothing to show | `NeEmptyState` | plain paragraph |
| Content loading | `NeSkeleton`, `NeTable :loading`, `NeCard` loading | `NeEmptyState` |
| Short wait (inside a button: `loading`) | `NeSpinner` | |
| Progress of a long task | `NeProgressBar` (`indeterminate` if unknown) | |
| Decision, confirmation, short form | `NeModal` | |
| Long form or details | `NeSideDrawer` or a page | `NeModal` |
| Result of an action, for a few seconds | `NeToastNotificationV2` | modal, deprecated `NeToastNotification` |
| Error or message that stays in the page/form | `NeInlineNotification` | empty state, modal |
| Tabular data | `NeTable` + parts + `NePaginator` in the `paginator` slot | raw `<table>` |
| One-line text / search / password | `NeTextInput` (`is-search`, `is-password`) | raw `<input>` |
| Long text | `NeTextArea` | |
| One choice among a few, all visible | `NeRadioSelection`, options always stacked vertically (`card` for cards) | dropdown, radio buttons in a row |
| One choice from a short list | `NeListbox` (the select) | |
| One choice from a long list, typing to filter | `NeCombobox` (`multiple` is deprecated) | |
| Several choices among a few | `NeCheckboxCards` | |
| Several choices from a long list | `NeMultiselectCombobox` | `NeCombobox multiple` |
| Single checkbox | `NeCheckbox` | |
| On/off setting | `NeToggle` | checkbox |
| One file | `NeFileInput` | |
| Advanced settings that would make the page long | `NeExpandable` | |
| Views of the same page/object | `NeTabs` | |
| Page/section title | `NeHeading` (one `h1` per page) | hand-sized `<h*>` |
| Multi-step flow | `NeStepper` | |
| Grouped content block, dashboard card | `NeCard` (has its own loading and error) | |
| New password with requirements | `NePasswordRequirements` + `usePasswordRequirements` | |

Never use deprecated components in new designs: `site/components-index.md` names their replacement.

---

## 2. Button — `NeButton`

`kind`: `primary` | `secondary` (default) | `tertiary` | `danger`. Slots: default (label), `prefix` and `suffix` (icons). Props: `size`, `loading`, `disabled`.

- **Primary**: the main action of a view or dialog. **One per view**: when the empty state shows the create button, the page header doesn't.
- **Secondary**: the other actions (Refresh, Preview).
- **Tertiary**: minor or dismissive actions (Cancel, Reset filters, Edit or Details in a row).
- **Danger**: only to confirm a destructive action (the Delete of a confirmation modal). Never for non-destructive actions.
- **AI**: actions that invoke AI. Not in the library yet: see section 11.

Behavior: paired actions in modals and drawers are Tertiary + Primary (Cancel + Create); never two Primary side by side. `loading` while the action runs (the spinner replaces the icon). Disabled = 50% opacity, the only allowed use of opacity. Page-level primary and empty-state buttons use `size="lg"`; row, toolbar and modal buttons the default size. Sizes follow Storybook, not the Figma names.

Labels and icons: follow "Buttons and actions" in `site/writing-guidelines.md`. In short:
- Verb + object (`Create user`); glossary verbs: Create new, Add existing, Edit, Delete to destroy, Remove from a list, Uninstall an application.
- **Pending decision** (not on the site yet, see `SKILL.md`): the create button of a drawer or a modal shows only the action, `Create` (the title already names the object: drawer `Create contact` → `Create`). The page header and empty-state buttons keep the object (`Create contact`). Edit drawers end with `Save` (not "Save changes").
- **Row actions (team rule):** when the object has no page of its own, its details are shown in the **edit drawer**: the visible row action is Tertiary `Edit` (`pen-to-square`), the other actions are in the kebab, and the name in the first column is **plain text, not clickable**. `Details` with the eye icon only opens a dedicated page of the object (not View/See details); `Show details` only for content that opens in place.
- Actions in the kebab menu of a row/card omit the object: `Edit`, `Delete`.
- `Go to <page>` inside the product (arrow-right icon), `Open <site>` for external sites (arrow-up-right-from-square).
- Icons: `circle-plus` for Create/Add, `pen-to-square` Edit, `trash` Delete, `circle-minus` Remove, `circle-arrow-down` Download, `circle-arrow-up` Import/Upload, `arrows-rotate` Refresh, `floppy-disk` Save. Full list and icons to avoid: `site/icons.md`.

```vue
<NeButton kind="primary" size="lg" @click="openCreateDrawer">
  <template #prefix><FontAwesomeIcon :icon="faCirclePlus" aria-hidden="true" /></template>
  Create user
</NeButton>
```

---

## 3. Icon button — `NeButton` icon-only + `NeTooltip`

Shape (Figma "Icon button"): square 36×36, padding 10, radius 6, icon 16 px; kinds Primary, Secondary, Tertiary; hover fills the whole square. Build it as Storybook does: the `NeButton` "Icon Only" story wrapped in `NeTooltip` with `trigger-event="mouseenter focus"` (the default `click` is wrong for icon buttons), and an `aria-label` with the same text as the tooltip. Kinds: primary, secondary, tertiary. No Danger variant: a destructive icon button is Tertiary and opens a confirmation.

- Use for compact familiar actions in toolbars, tables, cards, and to close dialogs. Not for complex or unfamiliar actions.
- Kinds in the Nebula Figma file: Primary, Secondary, Tertiary (plus AI Light / AI Dark).
- Tooltip = accessible name = the action, not the icon (on a button that shows text, the accessible name must include that text, best at its start: no `aria-label` replacing it): `Delete user`, `Copy phone number` (not Trash, Click here). No final period.
- A disabled icon button can use its tooltip to say why it is unavailable. Never put information the user needs only in a tooltip.

```vue
<NeTooltip trigger-event="mouseenter focus" placement="top">
  <template #trigger>
    <NeButton kind="tertiary" aria-label="Copy phone number" @click="copyPhone(contact)">
      <FontAwesomeIcon :icon="faCopy" class="size-4" aria-hidden="true" />
    </NeButton>
  </template>
  <template #content>Copy phone number</template>
</NeTooltip>
```

---

### Kebab menu (team rule from the Nebula Figma file)

- The kebab trigger is the **Icon button, Type Tertiary** (Figma component "Icon button", `ellipsis-vertical`): a **square 36×36** button (padding 10, radius 6, icon 16 px) with the icon in the product primary color, no background, and a square hover in `Surface/Button/Tertiary Hover` (`bg-gray-200/70 dark:bg-gray-600/30`). Never a text-button shape (wider than tall). It is the default of `NeDropdown`. Accessible name `Open menu`.
- Items without the object (`Edit`, `Delete`). Danger items (`Delete`, `Destroy`…) go **last, separated from the others by a divider** (`NeDropdown` item whose `id` contains `divider`).

### Table text (team rule from the Nebula Figma file)

Header cells in `Text/Primary neutral` (`text-gray-900 dark:text-gray-50`); **every body cell, including the first column, in `Text/Secondary neutral` (`text-gray-700 dark:text-gray-200`), Regular**. No Medium or bold names in rows.

## 4. Badge — `NeBadgeV2`

`kind`: `primary` | `indigo` | `gray` (default) | `green` | `amber` | `rose` | `blue` | `custom`. `pill` (default true) = rounded; `:pill="false"` = squared. `dismissable` + `@dismiss` to remove it.

- **Team rule (pending decision): never use a badge for a status.** A status is always **icon + label**: the status icon of `site/icons.md` in its Icon token color (Enabled `circle-check` `text-green-700 dark:text-green-500`, Disabled `circle-xmark` `text-gray-700 dark:text-gray-400`, Warning `triangle-exclamation` amber, Error `circle-xmark` rose) followed by the label in `Text/Primary neutral` (or `Text/Secondary neutral`). The site's accessibility page and the `NeBadgeV2` description in Storybook still mention badges for statuses.
- Use badges for a category, role or type (Admin, Queue, Controller) and for selected removable items. Not for actions, navigation or sentences.
- Rounded for status and categories; squared for selected removable items (multiselect values, active filters).
- Same color = same meaning everywhere: green Enabled/success, gray Disabled, rose error/blocked/expired, amber warning, blue information; categories without a status use `indigo` or `gray`. Colors come from the Badge tokens in `site/colors.md`. Never color for variety.
- Color is never the only signal: the badge always has a label.
- Labels: one or two words, sentence case, no punctuation. Status labels (icon + label) are adjectives or past participles (Enabled, not Enable; not OK/Normal).

---

## 5. Dropdown filter — `NeDropdownFilterV2`

`kind`: `checkbox` (several values, shows the count) | `radio` (one value). `v-model` = array of selected option objects. Options `{ id, label, description?, disabled? }` or groups. A search field appears with `showOptionsFilter` or past `maxOptionsShown`.

- One data category per filter. Label = noun used in the table (`Company`, `Status`), never "Filter by…" or "Select…". Options parallel in grammar.
- Selections apply immediately; the menu stays open while selecting; the count follows the label, never replaced by option names; never show a zero count.
- Every filter has a default. Reset vs Clear, exactly as "Table filters" in `site/writing-guidelines.md`:
  - `Reset filters`: all filters of a table, from the toolbar (Tertiary) or the no-results empty state. Also when all defaults are empty.
  - `Reset selection`: inside a dropdown filter that has something selected by default.
  - `Clear selection`: inside a dropdown filter with nothing selected by default.
  - `Clear filter`: when the only filter of a table or collection is a text filter (empty state).
  - `Clear search`: the clear button of the text filter (screen readers only).
- Search inside the filter: placeholder `Filter options` (or contextual, e.g. `Filter users`); no results → `No options`. No empty-state component inside the dropdown.
- Look: menu wide enough for labels and descriptions, aligned to the trigger's start edge.

---

## 6. Empty state — `NeEmptyState`

Props: `icon`, `title`, `description`; default slot: the action. Give it the card surface: `class="bg-white dark:bg-gray-950"` (Elevation L0). The component sizes its icon (48 px).

Pick the case from "Empty states" in `site/writing-guidelines.md` (cases and copy are there). With icons and actions:

| Case | Icon | Action |
|---|---|---|
| Nothing created yet (`No users configured`) | the section icon (`site/icons.md` sidebar/objects) | Primary lg `Create user` with `circle-plus` — the only create button on the page |
| Nothing to show, nothing to create (`No voicemail messages`) | section icon | none |
| Items will appear over time (`No notifications yet`) | section icon | none |
| Filters match nothing (`No users found` / `Try changing your search filters.`) | `magnifying-glass` | Tertiary lg `Reset filters` |
| Only a text filter, no match (`Try different or fewer words.`) | `magnifying-glass` | Tertiary lg `Clear filter` |
| Feature turned off (`Threat Shield DNS is disabled`) | feature icon | the action that enables it, if users can |
| No permission (`Restricted page`) | `ban` | Primary lg `Go to Dashboard` with `arrow-right` |

Rules: always an icon, **Solid** (never Light), from the dictionary or the section; **a description almost always**: the site marks it optional for some cases, but the team strongly recommends it because it gives users the context, so leave it out only when there is nothing useful to say (e.g. `No port forwards configured` / `Create a port forward to make a service of your local network reachable from the internet.`); title = the state, plural object, no instructions; description = reason or next step, without repeating the title; at most two actions, stacked, Primary first then Tertiary. Not for loading (skeleton) or recoverable errors (inline notification). A process in progress inside a guided flow can use an empty state with no action.

---

## 7. Modal — `NeModal`

Props: `title`, `kind` (`neutral` | `info` | `warning` | `error` | `success`), `size`, `primaryLabel`, `secondaryLabel`, `cancelLabel`, `primaryButtonKind` (`primary` | `danger`), `*Disabled`, `*Loading`, `closeAriaLabel`. Body in the default slot. The component places the buttons (main action last). It keeps focus inside and closes with Esc.

- Use for a confirmation, a short form, a message that needs an answer. Not for passive "done" feedback (toast), recoverable errors (inline notification), long forms (drawer or page).
- Copy: "Modals", "Delete confirmation" and "Archive and destroy confirmation" in `site/writing-guidelines.md`. Title = action (`Delete user`) or noun for information (`Connection details`), never a question; main button repeats the title verb (`Perform factory reset` → `Reset`); `Cancel` when there's something to abandon; an informative modal has only `Close`.
- Delete: `kind="warning"`, title `Delete <object type>`, body `User Alice Fox will be permanently deleted.` (no quotes around the name) + side effects, buttons Cancel + `Delete` (`primary-button-kind="danger"`). Type to confirm (`Type 'Alice Fox' to confirm`, straight quotes) only when the deletion destroys data, many objects or dependents; main button disabled until it matches.
- Archive (My Nethesis): `Archive <object type>`, Primary `Archive`, says it can be restored, no type-to-confirm. Destroy: as Delete with `Destroy`, says it cannot be undone.
- `kind` describes the message, the button describes the consequence: a destructive confirmation is `warning` + danger button, not `error`.
- Three buttons only for two real outcomes (Unsaved changes: Cancel · Don't save · Save).

---

## 8. Side drawer — `NeSideDrawer`

A modal panel from the right for a form or details too long for a modal (Create item drawer pattern). Title `Create contact` / `Edit contact`; footer Tertiary `Cancel` + Primary `Create` (pending decision) / `Save`; first field focused, Enter saves; an `NeInlineNotification` (`Cannot create contact`) above the footer when saving fails; Primary `loading` while saving.

---

## 9. Toast notification — `NeToastNotificationV2`

The result of an action, shown for a few seconds at the edge of the screen, up to two actions. Copy: "Success notifications" in `site/writing-guidelines.md`.

- Title: past tense, no names, no articles: `User created`, `User updated`, `User deleted`.
- Description: `<Object type> <name> has been created` (`User Alice Fox has been created`), no final period for one short sentence. Several unnamed objects: `Voicemail has been enabled for the selected users`; counts: `8 users have been imported from the CSV file`.
- **No toast when the result is already visible on the page.**
- **No toast for changes that are not applied yet.** In NethSecurity many changes are staged: the top bar shows "Unsaved changes", which opens the list of pending changes to apply all at once (services restart once). A toast would say something happened that hasn't. Only actions applied immediately get a success toast. Errors are shown as usual.

---

## 10. Inline notification — `NeInlineNotification`

`kind`: info | warning | error | success; `title`, `description`, optional buttons and `details` slot. It stays in the page until the problem is solved or the user closes it.

- Title on one line, description one sentence. Errors: title `Cannot <verb> <object>` (`Cannot save phonebook contact`), description cause + fix (`Network error. Check your connection and reload the page.`); `Something went wrong.` only when the cause is really unknown. Server errors by kind ("Error messages" in `site/writing-guidelines.md`): about a field → the field's validation text from an i18n key; about the state of an object with no field → the server message as it is, capital first letter (`Customer is already suspended`); network errors and 5xx → a fixed text, never the server message (`Network error. Check your connection and reload the page.`, `Something went wrong.`). Error codes and internal details never as main text.

---

## 11. Gaps between guidelines and library

- **AI button / AI icon button**: required for every action that invokes AI (Rewrite, Summarize, Generate…), not in the library yet. Spec: same anatomy, sizes and states as `NeButton`; gradient from indigo (left) to pink (right) with Tailwind `indigo`/`pink` shades (exact shades not documented: flag them); white label/icon in light theme, dark in dark theme. Icon: `site/icons.md` has no AI meaning yet and the custom `ai-spark` has no agreed meaning (already reported to the UX team): ask the designer which icon to use before drawing it, proposing the custom `ai-spark` (ns-solid) and `wand-magic-sparkles` (Font Awesome Solid, used by no other meaning). Flag the component in the handoff.
- **Icon button**: no dedicated component; compose it as in section 3.
- Anything else the guidelines require that no component supports: say so, pick the closest compliant option, don't invent a look-alike.
