# Applying the NDS foundations in mockups

The values live on the design system site and are mirrored here: colors in `site/colors.md`, typography, iconography, spacing, border, focus ring, elevation and shadow in `site/foundations.md`, icons by meaning in `site/icons.md`, accessibility in `site/accessibility.md`. This file only says how to use them. Never hardcode hex, RGB or OKLCH: use Tailwind classes, built from the tokens.

## Product primary color

Each product has its own primary palette; in code it is always `primary-*` (`text-primary-700 dark:text-primary-500`), never the palette name, because each product maps `primary` to its palette in its theme CSS.

| Product | Palette | Active light / dark | Focus ring |
|---|---|---|---|
| NethSecurity | Cyan | primary-700 / primary-500 | primary-500 |
| NethVoice | Emerald | primary-700 / primary-500 | primary-500 |
| NethLink | Blue | primary-700 / primary-500 | primary-500 |
| NethService | Orange | primary-700 / primary-500 | primary-500 |
| My Nethesis | Sky | primary-700 / primary-500 (hover primary-900 / 300) | primary-500 |
| NethSpot | Purple | primary-700 / primary-500 (only Active and Favicon tokens defined) | — |

Hover, focus, favicon and placeholder shades: `Product Primary` in `site/colors.md`.

Theme mapping block, only if a prototype needs it:

```css
@theme {
  --color-primary-50: var(--color-emerald-50);
  /* … every shade … */
  --color-primary-950: var(--color-emerald-950);
}
```

Some products define `@utility` classes on these tokens (NethSecurity `src/assets/main.css`: `text-primary-neutral`, `text-secondary-neutral`, `text-tertiary-neutral`…). When building inside such a repo, prefer them to raw pairs.

## Choosing colors

Always start from a semantic token of `site/colors.md` and use its `classes` (both themes):

- Text: `Text/Primary neutral` (`text-gray-900 dark:text-gray-50`) for main text, `Text/Secondary neutral` (`text-gray-700 dark:text-gray-200`), `Text/Tertiary neutral` (`text-gray-600 dark:text-gray-400`) for page descriptions and less important text, `Text/Danger`, `Text/Warning`, product links `text-primary-700 dark:text-primary-500`.
- Surfaces (**pending decision**: Figma variables updated, `site/colors.md` still has the old descriptions until the colors are re-exported):
  - L0 `bg-white dark:bg-gray-950`: first and main surfaces such as sidebar and top bar
  - L1 `bg-gray-50 dark:bg-gray-900`: page background, drawer background (`NeSideDrawer` already uses it)
  - L2 `bg-gray-100 dark:bg-gray-800`: content on L1 (default background of `NeEmptyState`)
  - L2 invert `bg-white dark:bg-gray-950`: alternative content on L1, such as cards (`NeCard` default) and the empty states of the Storybook patterns
  - L3 `bg-gray-200 dark:bg-gray-700`: content on L2; L4 `bg-gray-300 dark:bg-gray-600`: content on L3
- Neutral = Gray (structure). Secondary = Indigo (non-semantic emphasis: tooltip icons, neutral badges, selected items), never for a status.
- Status: Information Blue, Success Green, Warning Amber, Error/Danger **Rose** (not Red). Red only appears in the NethVoice "Calls and status", presence and phone island tokens.
- Badges, inline notifications, rounded icons, borders and rings have their own tokens: use them instead of picking shades.

## Accessibility rules that change how a mockup looks

From `site/accessibility.md` (WCAG 2.2 AA):
- Text contrast ≥ 4.5:1: take text colors from Text tokens. **Don't dim text with opacity** (`text-gray-900/60`, `opacity-70`): use a lighter Text token. Opacity only for disabled controls (`disabled:opacity-50`).
- An archived or turned-off item is **not disabled**: its row keeps its actions, text in `Text/Tertiary neutral`, icons `Icon/Tertiary neutral`, and the status written in the status column (`Archived` with its icon).
- Color is never the only signal: badges have labels, notifications have icon + title, invalid fields have a message, not just a red border.
- Every action is a button or a link (a clickable row also has a Details button inside); a link (`NeLink`) always has an `href`, an action that opens a modal/drawer or runs something is a button (Tertiary `NeButton`); focus ring always visible; every field has a visible label (placeholders are lighter and never carry information); icon buttons have an accessible name equal to the tooltip; the accessible name of a button or link that shows text includes that text, best at its start (no `aria-label` replacing it; add context as hidden text after it, as for Details); icons next to text are `aria-hidden`.

## Typography

Poppins, only Regular (body) and Medium (headings, labels, buttons). Body text in product UI is usually `text-sm`. Headings: `NeHeading` with the text styles H1–H7 of `site/foundations.md`. Running text (page descriptions) at most `max-w-2xl` (672 px); tables and forms can be wider. `text-xxs` (10 px) is not a Tailwind size.

## Icons

**Where to take them in mockups and prototypes:** from the Nebula Design System artifact, `project/assets/icons/icon-data.js` (Solid, Light and Nethesis custom icons as SVG, names in PascalCase, Light variants ending in `Light`: `block-brick-fire` → `BlockBrickFire`, inactive sidebar `HouseLight`), or the `Icon` component of its bundle. Never placeholders, never Font Awesome from the internet (it lacks the Light and custom icons).

Font Awesome Solid free, plus Nethesis custom icons (ns-solid, ns-brands) where `site/icons.md` uses them; Nethesis Light only for inactive main-sidebar sections. Same meaning = same icon in every product: look up the meaning in `site/icons.md` first, respect its "Avoid" column, and never use a custom icon without a meaning without asking. When a meaning is missing, **ask the designer before choosing** (pending decision): propose the fitting Nethesis custom icons that have no meaning yet (last section of `site/icons.md`, which the team draws because the products use them) and a Font Awesome Solid icon that no other meaning uses. Once chosen, the meaning goes to the dictionary. Sizes: 12 px service icons, 16 px (`size-4`) default, 20 px rounded icon, 24 px cards/sidebar/top bar, 32 px file input, 48 px empty state. `NeEmptyState`, `NeRoundedIcon`, `NeDropdown` size their icons themselves.

## Spacing, border, focus, elevation, shadow

- Spacing: Tailwind scale only (step × 4 px), no arbitrary values. Recurring values: page description block `mb-8`, toolbar `mb-6 … gap-4`, card padding handled by `NeCard`.
- Radius and border width: Tailwind classes (components already apply theirs).
- Focus ring 1: `focus-visible:ring-2 focus-visible:ring-primary-500`; focus ring 2 adds `focus-visible:ring-offset-2`; on a status background use the status ring classes. In the dark theme the ring takes `Product Primary/Focus` dark = `primary-200` (`dark:focus-visible:ring-primary-200`; pending decision, see SKILL.md).
- Shadows: `shadow-xs` … `shadow-2xl` plus the drawer shadow; gray instead of black in the dark theme. Components include theirs.
- Dark mode: every color class has its `dark:` counterpart (the token `classes` already do).

## AI

AI-specific actions use an indigo → pink gradient (AI button): see `components.md` §11.
