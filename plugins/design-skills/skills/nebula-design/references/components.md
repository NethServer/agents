# NDS components → `@nethesis/vue-components`

Which component to use, and the rules of the UX team that the site and Storybook don't have. Everything else is read from the sources (see "Reading the site" in `SKILL.md`), not repeated here:
- copy of buttons, filters, empty states, modals, toasts and errors: the sections of the same name in `site/writing-guidelines.md`, with the terms of `site/glossary.md`;
- icons: `site/icons.md`; colors: `site/colors.md`;
- what each component is for, deprecated → replacement: `site/components-index.md`;
- props, slots and how a component looks and behaves: its Storybook story or `vue-components/src/components/<Name>.vue`.

If this file disagrees with the site or Storybook, the site wins for text, icons and colors, Storybook wins for how a component looks and behaves, except where a rule here is marked as a team rule or pending decision.

## Contents
1. Which component for which need
2. Button (`NeButton`)
3. Icon button (`NeButton` icon-only + `NeTooltip`)
4. Badge (`NeBadgeV2`) and statuses
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
| Menu of actions (kebab) of a row, card or page | `NeDropdown` | `NeDropdownFilterV2` |
| Filter a table/list by a data category | `NeDropdownFilterV2` | `NeDropdown`, deprecated `NeDropdownFilter` |
| Sort a table/list | `NeSortDropdown` (neutral trigger `Sort` + `chevron-down`, never Primary or the product color) | custom select, a Secondary `NeButton` as trigger |
| Status of an object (Enabled, Disabled, Expired…) | icon + label (team rule, §4) | badge, colored text alone, a colored dot alone |
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
| One choice among a few, all visible | `NeRadioSelection`, options **always stacked vertically** (team rule; `card` for cards) | dropdown, radio buttons in a row |
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
| Grouped content block, dashboard card | `NeCard` | |
| New password with requirements | `NePasswordRequirements` + `usePasswordRequirements` | |

---

## 2. Button — `NeButton`

Kinds and labels: "Buttons and actions" in `site/writing-guidelines.md`; icons by action in `site/icons.md`. On top of them:
- **One Primary per view**: when the empty state shows the create button, the page header doesn't. Paired actions in modals and drawers are Tertiary + Primary, never two Primary. Danger only to confirm a destructive action.
- Page-level primary and empty-state buttons use `size="lg"`; row, toolbar and modal buttons the default size. Sizes follow Storybook, not the Figma names.
- Disabled = 50% opacity, the only allowed use of opacity.
- **Pending decision:** the create button of a drawer or a modal shows only the action, `Create` (drawer `Create contact` → `Create`). Page header and empty-state buttons keep the object (`Create contact`). Edit drawers end with `Save`.
- **Row actions (team rule):** when the object has no page of its own, its details are shown in the **edit drawer**: the visible row action is Tertiary `Edit` (`pen-to-square`), the other actions are in the kebab, and the name in the first column is **plain text, not clickable**. `Details` with the eye icon only opens a dedicated page of the object.
- AI actions: see §11.

---

## 3. Icon button — `NeButton` icon-only + `NeTooltip`

Shape (Figma "Icon button"): square 36×36, padding 10, radius 6, icon 16 px; kinds Primary, Secondary, Tertiary (plus AI Light / AI Dark in Figma); hover fills the whole square. No Danger variant: a destructive icon button is Tertiary and opens a confirmation. Build it as Storybook does: the `NeButton` "Icon Only" story wrapped in `NeTooltip` with `trigger-event="mouseenter focus"` (the default `click` is wrong for icon buttons), and an `aria-label` equal to the tooltip. Tooltip text and accessible name: `site/accessibility.md` and "Buttons and actions" in the guidelines.

### Kebab menu (team rule from the Nebula Figma file)

- The trigger is the **Icon button, Type Tertiary** (`ellipsis-vertical`): a **square 36×36** button with the icon in the product primary color, no background, and a square hover in `Surface/Button/Tertiary Hover`. Never a text-button shape. It is the default of `NeDropdown`. Accessible name `Open menu`.
- Items without the object (`Edit`, `Delete`). Danger items go **last, after a divider** (`NeDropdown` item whose `id` contains `divider`).

### Table text (team rule from the Nebula Figma file)

Header cells in `Text/Primary neutral`; **every body cell, including the first column, in `Text/Secondary neutral`, Regular**. No Medium or bold names in rows.

---

## 4. Badge — `NeBadgeV2` and statuses

- **Team rule (pending decision): never use a badge for a status.** A status is always **icon + label**: the status icon of `site/icons.md` in its Icon token color (`site/colors.md`), followed by the label in `Text/Primary neutral` (or `Text/Secondary neutral`). The site's accessibility page and the `NeBadgeV2` description in Storybook still mention badges for statuses.
- Badges only for a category, role or type and for selected removable items; colors from the Badge tokens of `site/colors.md`, same color = same meaning, never color for variety.

---

## 5. Dropdown filter — `NeDropdownFilterV2`

Labels, Reset vs Clear and search inside the filter: "Table filters" in `site/writing-guidelines.md`. Team rules for the toolbar (always-visible `Reset filters`, its label in empty states): `patterns.md` §1.

---

## 6. Empty state — `NeEmptyState`

Cases and copy: "Empty states" in `site/writing-guidelines.md`; icons: the section or object icon of `site/icons.md`, `magnifying-glass` when filters match nothing. Team rules:
- Always an icon, **Solid** (never Light).
- **A description almost always**: the site marks it optional for some cases, but the team strongly recommends it because it gives users the context; leave it out only when there is nothing useful to say (`No port forwards configured` / `Create a port forward to make a service of your local network reachable from the internet.`).
- With no objects yet, the create button (Primary lg) is only here, not in the page header. At most two actions, stacked, Primary first then Tertiary.
- Surface: the empty states of the Storybook patterns sit on a card, `bg-white dark:bg-gray-950` (L2 invert); the component's own default is L2.

---

## 7. Modal — `NeModal`

Copy: "Modals", "Delete confirmation" and "Archive and destroy confirmation" in `site/writing-guidelines.md`. Component: Storybook. One rule that is neither: `kind` describes the message, the button the consequence, so a destructive confirmation is `kind="warning"` with `primary-button-kind="danger"`, not `error`.

---

## 8. Side drawer — `NeSideDrawer`

A modal panel from the right for a form or details too long for a modal (Create item drawer pattern, `patterns.md` §2). Footer Tertiary `Cancel` + Primary `Create` (pending decision) / `Save`. Look: `figma-components.md` §2.

---

## 9. Toast notification — `NeToastNotificationV2`

Copy and when to use it: "Success notifications" in `site/writing-guidelines.md`. Team rule: **no toast for changes that are not applied yet.** In NethSecurity many changes are staged: the top bar shows "Unsaved changes", which opens the list of pending changes to apply all at once (services restart once). A toast would say something happened that hasn't. Only actions applied immediately get a success toast; errors are shown as usual.

---

## 10. Inline notification — `NeInlineNotification`

Copy: "Error messages" and "Inline notifications" in `site/writing-guidelines.md`. Pending decision: the Italian of `Something went wrong.` is `Qualcosa è andato storto.`

---

## 11. Gaps between guidelines and library

- **AI button / AI icon button**: required for every action that invokes AI (Rewrite, Summarize, Generate…), not in the library yet. Spec: same anatomy, sizes and states as `NeButton`; gradient from indigo (left) to pink (right) with Tailwind `indigo`/`pink` shades (exact shades not documented: flag them); white label/icon in light theme, dark in dark theme. Icon: `site/icons.md` has no AI meaning yet and the custom `ai-spark` has no agreed meaning (already reported to the UX team): ask the designer which icon to use before drawing it, proposing the custom `ai-spark` (ns-solid) and `wand-magic-sparkles` (Font Awesome Solid, used by no other meaning). Flag the component in the handoff.
- **Icon button**: no dedicated component; compose it as in §3.
- Anything else the guidelines require that no component supports: say so, pick the closest compliant option, don't invent a look-alike.
