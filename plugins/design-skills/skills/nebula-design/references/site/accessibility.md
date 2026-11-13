# Accessibility

> Mirror of https://nethesis.github.io/nebula-design-system/?page=accessibility, synced on 2026-11-10 by `scripts/sync_site.py`. Do not edit: the site is the source of truth. If the live site disagrees, follow the site.

Nethesis user interfaces follow the [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)
at level AA. This page doesn't repeat them: it lists the choices that Nebula makes to meet them.
The components of [vue-components](https://nethesis.github.io/vue-components/) already handle
keyboard use, focus and screen readers. These rules matter when you combine components, write
your own markup or build with another stack.

## Color and contrast

- **Text has a contrast of at least 4.5:1** with its background, in both themes. Take its color
  from a Text token of the [Colors](colors.md) page: the neutral, danger, warning and product
  link tokens reach 4.5:1 on the page and card backgrounds, `Elevation/L1` and `Elevation/L0`.
- **Don't dim text with opacity**, such as `text-gray-900/60` or `opacity-70`: its contrast then
  depends on the background behind it and can't be checked once for the token. Use a lighter Text
  token instead. Opacity is only for disabled controls (`disabled:opacity-50`), which WCAG doesn't
  require to meet a contrast ratio.
- **An archived item is not disabled**, and neither is an item that is turned off, such as a
  disabled rule. Its row still has actions, such as restore or destroy, and its text is still
  read. Don't dim it with opacity: use the `Text/Tertiary neutral` token for its text and
  `Icon/Tertiary neutral` for its icons, and say its status in the status column, such as
  `Archived` with its icon.
- **The placeholder is not enough**: `Text/Placeholder` is lighter than the other Text tokens.
  Never put information only in a placeholder (see [Forms](writing-guidelines.md#forms)).
- **Color is never the only signal.** A status also has a text or an icon: a badge has a label, a
  notification has an icon and a title, a field with an error has its validation message, not just
  a red border.

| Do | Don't |
| --- | --- |
| `text-gray-600 dark:text-gray-400` for less important text | `text-gray-900/60`, `opacity-70` |
| A badge that says `Expired` | A red dot alone |
| An archived row in `Text/Tertiary neutral`, with the `Archived` status | An archived row with `opacity-50` |

## Keyboard and focus

- **Everything works with the keyboard.** An action is a button or a link, never a click handler
  on a `div`, a `span` or a table row. When a whole row or card opens something, its main
  action is also a button or a link inside it, such as **Details**.
- **A link has an address.** `NeLink` renders an `<a>`, which the keyboard skips without an
  `href`: give it the `href` of the page it opens. For an action that opens a modal or a
  drawer, or runs something, use a button (`NeButton` with `kind="tertiary"`).
- **The focus ring is always visible.** Don't remove the outline or the ring of an interactive
  element without the focus ring of [Spacing and border](foundations.md) in its place.
- **Modals and drawers keep the focus inside** while they are open, close with Esc and give the
  focus back to the element that opened them. `NeModal` and `NeSideDrawer` already do it: use them
  instead of your own overlay.

## Screen readers

- **Every form field has a visible label**, linked to the field: the `label` prop of the `Ne*`
  input components. A placeholder is never a label.
- **An icon button has an accessible name** that matches its tooltip, as in
  [Buttons and actions](writing-guidelines.md#buttons-and-actions). An icon next to a text is
  decoration: hide it from screen readers with `aria-hidden="true"`.
- **The accessible name includes the visible text**, best at its start, so that people who use
  voice control can say what they see. An `aria-label` replaces the text of the element: don't
  put one on a link or a button that already shows text, such as `3 active alerts`. To add
  context, put hidden text after the visible one, as for **Details**.
- **Text for screen readers only is translated** like the visible text. The `Ne*` components take
  it from props that end in `Label`, such as `closeAriaLabel`, with English defaults: pass them in
  the language of the interface.
- **The page language follows the interface**: when the user changes language, update the `lang`
  attribute of the `html` element, so that screen readers read Italian with an Italian voice.
