# Foundations: typography, iconography, spacing, border, focus ring, elevation, shadow

> Mirror of https://nethesis.github.io/nebula-design-system/, synced on 2026-11-10 by `scripts/sync_site.py`. Do not edit: the site is the source of truth. If the live site disagrees, follow the site.

Each section has its source, the page of the site it comes from. px values are CSS pixels; rem values assume a 16 px root font size.

## Typography

Source: https://nethesis.github.io/nebula-design-system/?page=typography

Typeface **Poppins** (load both `@fontsource/poppins/400.css`, `@fontsource/poppins/500.css`).

| Weight | Value | Class | Use |
|---|---|---|---|
| Regular | 400 | `font-normal` | Body text |
| Medium | 500 | `font-medium` | Headings, labels and buttons |

Sizes:

| Name | Class | Size px | Line height px |
|---|---|---|---|
| xxs | not a Tailwind size | 10 | 12 |
| xs | text-xs | 12 | 16 |
| sm | text-sm | 14 | 20 |
| base | text-base | 16 | 24 |
| lg | text-lg | 18 | 28 |
| xl | text-xl | 20 | 28 |
| 2xl | text-2xl | 24 | 32 |
| 3xl | text-3xl | 30 | 36 |
| 4xl | text-4xl | 36 | 40 |
| 5xl | text-5xl | 48 | 48 |
| 6xl | text-6xl | 60 | 60 |
| 7xl | text-7xl | 72 | 72 |
| 8xl | text-8xl | 96 | 96 |

Line length: `max-w-2xl` (672 px). The widest a paragraph of running text should be, such as the description of a page: longer lines are hard to read. Tables, forms and other content can be wider.

Text styles, Headings:

| Token | Classes | Size / line height px | Weight |
|---|---|---|---|
| Headings/H1 | `text-4xl font-medium` | 36 / 40 | Medium |
| Headings/H2 | `text-3xl font-medium` | 30 / 36 | Medium |
| Headings/H3 | `text-2xl font-medium` | 24 / 32 | Medium |
| Headings/H4 | `text-xl font-medium` | 20 / 28 | Medium |
| Headings/H5 | `text-lg font-medium` | 18 / 28 | Medium |
| Headings/H6 | `text-base font-medium` | 16 / 24 | Medium |
| Headings/H7 | `text-sm/6 font-medium` | 14 / 24 | Medium |

Text styles, Body:

| Token | Classes | Size / line height px | Weight |
|---|---|---|---|
| Body/lg | `text-lg` | 18 / 28 | Regular |
| Body/base | `text-base` | 16 / 24 | Regular |
| Body/sm | `text-sm` | 14 / 20 | Regular |
| Body/xs | `text-xs` | 12 / 16 | Regular |
| Body/xxs | no Tailwind class | 10 / 12 | Regular |

Text styles, UI elements:

| Token | Classes | Size / line height px | Weight |
|---|---|---|---|
| UI/Button/lg | `text-sm font-medium` | 14 / 20 | Medium |
| UI/Button/sm | `text-xs font-medium` | 12 / 16 | Medium |

## Iconography

Source: https://nethesis.github.io/nebula-design-system/?page=iconography

Which icon to use for each meaning, from which package: icons.json. Font Awesome Solid icons, and Nethesis custom icons where icons.json uses them; Light custom icons only for the inactive sections of the main sidebar. Import each icon by name from its package and pass the imported object to FontAwesomeIcon, from @fortawesome/vue-fontawesome; do not register icons with library.add() to use them by name. Hide icons next to a text label with aria-hidden="true"; an icon without text needs a label and a tooltip.

| Pack | Package | Version |
|---|---|---|
| fa-solid | `@fortawesome/free-solid-svg-icons` | ^6.7.2 |
| ns-solid | `@nethesis/nethesis-solid-svg-icons` | github:nethesis/Font-Awesome#ns-solid |
| ns-light | `@nethesis/nethesis-light-svg-icons` | github:nethesis/Font-Awesome#ns-light |
| ns-brands | `@nethesis/nethesis-brands-svg-icons` | github:nethesis/Font-Awesome#ns-brands |

| Size | Class | Use |
|---|---|---|
| 12 px | `size-3` | Service icons, such as the check circle of a selection |
| 16 px | `size-4` | The most used size: buttons, badges, tooltips, text inputs, comboboxes, dropdowns, tables |
| 20 px | `size-5` | Rounded icon |
| 24 px | `size-6` | Cards, sidebar and top bar |
| 32 px | `size-8` | File input |
| 48 px | `size-12` | Empty state |

## Spacing and border

Source: https://nethesis.github.io/nebula-design-system/?page=spacing-and-border

Spacing is the Tailwind scale (step × 4 px): 0=0px, 0.5=2px, 1=4px, 1.5=6px, 2=8px, 2.5=10px, 3=12px, 3.5=14px, 4=16px, 5=20px, 6=24px, 7=28px, 8=32px, 9=36px, 10=40px, 11=44px, 12=48px, 14=56px, 16=64px, 20=80px, 24=96px, 28=112px, 32=128px, 36=144px, 40=160px, 44=176px, 48=192px, 52=208px, 56=224px, 60=240px, 64=256px, 72=288px, 80=320px, 96=384px.

Radius:

| Token | Class | px |
|---|---|---|
| radius/rounded-none | `rounded-none` | 0 |
| radius/rounded-xs | `rounded-xs` | 2 |
| radius/rounded-sm | `rounded-sm` | 4 |
| radius/rounded-md | `rounded-md` | 6 |
| radius/rounded-lg | `rounded-lg` | 8 |
| radius/rounded-xl | `rounded-xl` | 12 |
| radius/rounded-2xl | `rounded-2xl` | 16 |
| radius/rounded-3xl | `rounded-3xl` | 24 |
| radius/rounded-full | `rounded-full` | 9999 |

Border width:

| Token | Class | px |
|---|---|---|
| width/border-0 | `border-0` | 0 |
| width/border-1 | `border` | 1 |
| width/border-2 | `border-2` | 2 |
| width/border-4 | `border-4` | 4 |
| width/border-8 | `border-8` | 8 |

### Focus ring

The focus ring shows which element has the keyboard focus. Focus ring 1 is a 2 px ring around the element; focus ring 2 leaves a 2 px gap between the element and the ring. In code, the primary palette is the palette of the product, so the classes are the same in every product: focus-visible:ring-2 focus-visible:ring-primary-500 for focus ring 1, plus focus-visible:ring-offset-2 for focus ring 2. On a status color, focus ring 2 uses the classes of that status. styles are the box-shadow values of the Figma effect styles.

- Focus ring/1: `0 0 0 2px <ring color>`
- Focus ring/2: `0 0 0 2px <gap color, white by default>, 0 0 0 4px <ring color>, 0 1px 2px 0 rgb(0 0 0 / 0.05)`

| Product | Palette | Ring | Primary |
|---|---|---|---|
| NethSecurity | cyan | #06b6d4 | #0e7490 |
| NethVoice | emerald | #10b981 | #047857 |
| NethLink | blue | #3b82f6 | #1d4ed8 |
| NethService | orange | #f97316 | #c2410c |
| My Nethesis | sky | #0ea5e9 | #0369a1 |

Status colors (focus ring 2 on colored backgrounds):

| Status | Classes |
|---|---|
| Info | `ring-blue-500 ring-offset-blue-100` |
| Success | `ring-green-500 ring-offset-green-100` |
| Warning | `ring-amber-500 ring-offset-amber-100` |
| Error | `ring-rose-500 ring-offset-rose-100` |

## Elevation and shadow

Source: https://nethesis.github.io/nebula-design-system/?page=elevation-and-shadow

Each elevation level, from L0 to L4, is a surface color of the gray palette, for the backgrounds of the page, the top bar, the sidebar and the cards; L2 invert uses the L0 color to stand out on an L1 surface. Shadows apply to components such as cards, buttons, modals and tooltips; in the dark theme they are gray instead of black.

| Level | Light | Dark | Classes |
|---|---|---|---|
| L0 | white | gray-950 | `bg-white dark:bg-gray-950` |
| L1 | gray-50 | gray-900 | `bg-gray-50 dark:bg-gray-900` |
| L2 | gray-100 | gray-800 | `bg-gray-100 dark:bg-gray-800` |
| L3 | gray-200 | gray-700 | `bg-gray-200 dark:bg-gray-700` |
| L4 | gray-300 | gray-600 | `bg-gray-300 dark:bg-gray-600` |
| L2 invert | white | gray-950 | `bg-white dark:bg-gray-950` |

| Token | Class | Light | Dark |
|---|---|---|---|
| shadow/xs | `shadow-xs` | 0 1px 2px 0 rgb(0 0 0 / 0.05) | 0 1px 2px 0 rgb(75 85 99 / 0.05) |
| shadow/sm | `shadow-sm` | 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1) | 0 1px 3px 0 rgb(75 85 99 / 0.1), 0 1px 2px -1px rgb(75 85 99 / 0.1) |
| shadow/md | `shadow-md` | 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) | 0 4px 6px -1px rgb(75 85 99 / 0.1), 0 2px 4px -2px rgb(75 85 99 / 0.1) |
| shadow/lg | `shadow-lg` | 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1) | 0 10px 15px -3px rgb(75 85 99 / 0.1), 0 4px 6px -4px rgb(75 85 99 / 0.1) |
| shadow/xl | `shadow-xl` | 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1) | 0 20px 25px -5px rgb(75 85 99 / 0.1), 0 8px 10px -6px rgb(75 85 99 / 0.1) |
| shadow/2xl | `shadow-2xl` | 0 25px 50px -12px rgb(0 0 0 / 0.25) | 0 25px 50px -12px rgb(75 85 99 / 0.25) |
| shadow/drawer | `shadow-[0px_20px_40px_0_rgba(0,0,0,0.2)] dark:shadow-[0px_20px_40px_0_rgba(0,0,0,0.6)]` | 0 20px 40px 0 rgb(0 0 0 / 0.2) | 0 20px 40px 0 rgb(0 0 0 / 0.6) |
