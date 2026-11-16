# Applying the NDS foundations in mockups

The values live on the design system site, read live as in "Reading the site" of `SKILL.md`, and are not repeated here:
- colors, semantic tokens and their Tailwind classes, product palettes (`Product Primary`): `site/colors.md`;
- typography, text styles, line length, icon sizes, spacing, radius, border, focus ring, elevation, shadow: `site/foundations.md`;
- contrast, opacity, disabled and archived items, keyboard, focus, accessible names: `site/accessibility.md`.

This file only has how to use them in a mockup and the team decisions not on the site yet. Never hardcode hex, RGB or OKLCH, never arbitrary values: use Tailwind classes built from the tokens, each with its `dark:` counterpart.

## Product primary color

Each product has its own primary palette (NethSecurity Cyan, NethVoice Emerald, NethLink Blue, NethService Orange, My Nethesis Sky; exact shades in `Product Primary` of `site/colors.md`). In code it is always `primary-*`, never the palette name, because each product maps `primary` to its palette in its theme CSS. Theme mapping block, only if a prototype needs it:

```css
@theme {
  --color-primary-50: var(--color-emerald-50);
  /* … every shade … */
  --color-primary-950: var(--color-emerald-950);
}
```

Some products define `@utility` classes on these tokens (NethSecurity `src/assets/main.css`: `text-primary-neutral`, `text-secondary-neutral`…). When building inside such a repo, prefer them to raw pairs.

## Surfaces by elevation (pending decision)

Figma variables are updated, `site/colors.md` still has the old descriptions until the colors are re-exported:
- L0 `bg-white dark:bg-gray-950`: first and main surfaces such as sidebar and top bar
- L1 `bg-gray-50 dark:bg-gray-900`: page background, drawer background (`NeSideDrawer` already uses it)
- L2 `bg-gray-100 dark:bg-gray-800`: content on L1 (default background of `NeEmptyState`)
- L2 invert `bg-white dark:bg-gray-950`: alternative content on L1, such as cards (`NeCard` default) and the empty states of the Storybook patterns
- L3 `bg-gray-200 dark:bg-gray-700`: content on L2; L4 `bg-gray-300 dark:bg-gray-600`: content on L3

## Focus ring in the dark theme (pending decision)

The site gives `ring-primary-500` for both themes; the team uses `Product Primary/Focus` dark = `primary-200` (`dark:focus-visible:ring-primary-200`).

## Icons in mockups

**Where to take them:** from the Nebula Design System artifact, `project/assets/icons/icon-data.js` (Solid, Light and Nethesis custom icons as SVG, names in PascalCase, Light variants ending in `Light`: `block-brick-fire` → `BlockBrickFire`, inactive sidebar `HouseLight`), or the `Icon` component of its bundle. Never placeholders, never Font Awesome from the internet (it lacks the Light and custom icons).

Which icon: the meaning in `site/icons.md`, respecting its "Avoid" column. When a meaning is missing, **ask the designer before choosing** (pending decision): propose the fitting Nethesis custom icons that have no meaning yet (`customIconsWithoutMeaning`, list in `SKILL.md`) and a Font Awesome Solid icon that no other meaning uses. Once chosen, the meaning goes to the dictionary.

## AI

AI-specific actions use an indigo → pink gradient (AI button): see `components.md` §11.
