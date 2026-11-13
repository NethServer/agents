# Colors: semantic tokens

> Mirror of https://nethesis.github.io/nebula-design-system/?page=colors, synced on 2026-11-10 by `scripts/sync_site.py`. Do not edit: the site is the source of truth. If the live site disagrees, follow the site.

Use these semantic tokens, not the colors of the palettes. light and dark are the values of a token in the two themes; tailwind is the Tailwind color to use in code. In code, the primary palette is the palette of the product, so the Product Primary and product link tokens use primary-* colors. classes are the Tailwind classes for both themes; they are null when the utility depends on the component (text, background, border…) or when a value has no Tailwind color: then build them from the two tailwind colors, as in text-primary-700 dark:text-primary-500. link is the token in the Colors page, to cite in reviews.

Exported from the Nebula Figma file on 2026-10-26.

## Contents
- Product Primary
- Text
- Elevation
- Icon
- Surface
- Border
- Utility

## Product Primary

The main color of each product, for buttons, checkboxes, radio buttons and other interactive elements.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Product Primary/NethSecurity/Active | Cyan/700 (primary-700) | Cyan/500 (primary-500) | — | Primary active NethSecurity components like buttons, checkbox, radio buttons |
| Product Primary/NethSecurity/Hover | Cyan/800 (primary-800) | Cyan/300 (primary-300) | — | Hover for primary NethSecurity components like buttons, checkbox, radio buttons |
| Product Primary/NethSecurity/Focus | Cyan/500 (primary-500) | Cyan/200 (primary-200) | — | Focus NethSecurity components |
| Product Primary/NethSecurity/Favicon | Cyan/600 (primary-600) | Cyan/600 (primary-600) | — | Focus NethSecurity components |
| Product Primary/NethSecurity/Placeholder | Cyan/100 (primary-100) | Cyan/900 (primary-900) | — | Focus NethSecurity components |
| Product Primary/NethVoice/Active | Emerald/700 (primary-700) | Emerald/500 (primary-500) | — | Primary active NethVoice components like buttons, checkbox, radio buttons |
| Product Primary/NethVoice/Hover | Emerald/800 (primary-800) | Emerald/300 (primary-300) | — | Hover for primary NethVoice components like buttons, checkbox, radio buttons |
| Product Primary/NethVoice/Focus | Emerald/500 (primary-500) | Emerald/200 (primary-200) | — | Focus NethVoice components |
| Product Primary/NethVoice/Favicon | Emerald/600 (primary-600) | Emerald/600 (primary-600) | — | Focus NethVoice components |
| Product Primary/NethVoice/Placeholder | Emerald/100 (primary-100) | Emerald/900 (primary-900) | — | Focus NethVoice components |
| Product Primary/NethLink/Active | Blue/700 (primary-700) | Blue/500 (primary-500) | — | Primary active NethLink components like buttons, checkbox, radio buttons |
| Product Primary/NethLink/Hover | Blue/800 (primary-800) | Blue/300 (primary-300) | — | Hover for primary NethLink components like buttons, checkbox, radio buttons |
| Product Primary/NethLink/Focus | Blue/500 (primary-500) | Blue/200 (primary-200) | — | Focus NethLink components |
| Product Primary/NethLink/Favicon | Blue/600 (primary-600) | Blue/600 (primary-600) | — | Focus NethLink components |
| Product Primary/NethService/Active | Orange/700 (primary-700) | Orange/500 (primary-500) | — | Primary active NethService components like buttons, checkbox, radio buttons |
| Product Primary/NethService/Hover | Orange/800 (primary-800) | Orange/300 (primary-300) | — | Hover for primary NethService components like buttons, checkbox, radio buttons |
| Product Primary/NethService/Focus | Orange/500 (primary-500) | Orange/200 (primary-200) | — | Focus NethService components |
| Product Primary/NethService/Favicon | Orange/600 (primary-600) | Orange/600 (primary-600) | — | Focus NethService components |
| Product Primary/NethSpot/Active | Purple/700 (primary-700) | Purple/500 (primary-500) | — |  |
| Product Primary/NethServer/Logo text | Nethesis/Light blue (#009edb) | White (white) | — |  |
| Product Primary/NethServer/Logo icon | Nethesis/Light blue (#009edb) | White (white) | — |  |
| Product Primary/NethServer/Logo icon text | White (white) | Nethesis/Light blue (#009edb) | — |  |
| Product Primary/NethSpot/Favicon | Purple/600 (primary-600) | Purple/600 (primary-600) | — |  |
| Product Primary/My Nethesis/Active | Sky/700 (primary-700) | Sky/500 (primary-500) | — | Primary active NethService components like buttons, checkbox, radio buttons |
| Product Primary/My Nethesis/Hover | Sky/900 (primary-900) | Sky/300 (primary-300) | — | Hover for primary NethService components like buttons, checkbox, radio buttons |
| Product Primary/My Nethesis/Focus | Sky/500 (primary-500) | Sky/200 (primary-200) | — | Focus NethService components |
| Product Primary/My Nethesis/Favicon | Sky/600 (primary-600) | Sky/600 (primary-600) | — | Focus NethService components |
| Product Primary/My Nethesis/Logo | Nethesis/Gray MyNethesis (#1e1e1c) | White (white) | — | Focus NethService components |

## Text

All the text of the interface: headings, titles, body text, placeholders, button labels.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Text/Primary neutral | Gray/900 (gray-900) | Gray/50 (gray-50) | `text-gray-900 dark:text-gray-50` |  |
| Text/Primary invert neutral | Gray/50 (gray-50) | Gray/900 (gray-900) | `text-gray-50 dark:text-gray-900` |  |
| Text/Secondary | Indigo/700 (indigo-700) | Indigo/500 (indigo-500) | `text-indigo-700 dark:text-indigo-500` |  |
| Text/Secondary neutral | Gray/700 (gray-700) | Gray/200 (gray-200) | `text-gray-700 dark:text-gray-200` |  |
| Text/Tertiary neutral | Gray/600 (gray-600) | Gray/400 (gray-400) | `text-gray-600 dark:text-gray-400` |  |
| Text/Placeholder | Gray/400 (gray-400) | Gray/500 (gray-500) | `text-gray-400 dark:text-gray-500` | Placeholder text inside components like text-input |
| Text/Danger | Rose/700 (rose-700) | Rose/500 (rose-500) | `text-rose-700 dark:text-rose-500` | For description text on rose background |
| Text/Warning | Amber/700 (amber-700) | Amber/500 (amber-500) | `text-amber-700 dark:text-amber-500` | For description text on rose background |
| Text/Inputs | Gray/900 (gray-900) | Gray/50 (gray-50) | `text-gray-900 dark:text-gray-50` | Text inside components like text-input |
| Text/Link/NethSecurity | Cyan/700 (primary-700) | Cyan/500 (primary-500) | `text-primary-700 dark:text-primary-500` |  |
| Text/Buttons | White (white) | Gray/950 (gray-950) | `text-white dark:text-gray-950` |  |
| Text/Link/NethSecurity invert | Cyan/500 (primary-500) | Cyan/700 (primary-700) | `text-primary-500 dark:text-primary-700` |  |
| Text/Link/NethVoice | Emerald/700 (primary-700) | Emerald/500 (primary-500) | `text-primary-700 dark:text-primary-500` |  |
| Text/White | White (white) | White (white) | `text-white dark:text-white` |  |
| Text/Link/NethVoice invert | Emerald/500 (primary-500) | Emerald/700 (primary-700) | `text-primary-500 dark:text-primary-700` |  |
| Text/Link/MyNethesis invert | Sky/500 (primary-500) | Sky/700 (primary-700) | `text-primary-500 dark:text-primary-700` |  |
| Text/Link/NethLink | Blue/700 (primary-700) | Blue/500 (primary-500) | `text-primary-700 dark:text-primary-500` |  |
| Text/Black | Black (black) | Black (black) | `text-black dark:text-black` |  |
| Text/Link/NethService | Orange/700 (primary-700) | Orange/500 (primary-500) | `text-primary-700 dark:text-primary-500` |  |
| Text/Link/Nethesis | Nethesis/Light blue (#009edb) | Nethesis/Light blue (#009edb) | — |  |
| Text/Badge/Gray | Gray/800 (gray-800) | Gray/100 (gray-100) | `text-gray-800 dark:text-gray-100` |  |
| Text/Badge/Rose | Rose/800 (rose-800) | Rose/100 (rose-100) | `text-rose-800 dark:text-rose-100` |  |
| Text/Badge/Amber | Amber/800 (amber-800) | Amber/50 (amber-50) | `text-amber-800 dark:text-amber-50` |  |
| Text/Badge/Green | Green/800 (green-800) | Green/50 (green-50) | `text-green-800 dark:text-green-50` |  |
| Text/Badge/Indigo | Indigo/800 (indigo-800) | Indigo/100 (indigo-100) | `text-indigo-800 dark:text-indigo-100` |  |
| Text/Badge/Cyan | Cyan/800 (cyan-800) | Cyan/100 (cyan-100) | `text-cyan-800 dark:text-cyan-100` |  |
| Text/Badge/Blue | Blue/800 (blue-800) | Blue/100 (blue-100) | `text-blue-800 dark:text-blue-100` |  |
| Text/Badge/Emerald | Emerald/800 (emerald-800) | Emerald/50 (emerald-50) | `text-emerald-800 dark:text-emerald-50` |  |
| Text/Badge/Orange | Orange/800 (orange-800) | Orange/100 (orange-100) | `text-orange-800 dark:text-orange-100` |  |
| Text/Badge/Yellow | Yellow/700 (yellow-700) | Yellow/100 (yellow-100) | `text-yellow-700 dark:text-yellow-100` |  |
| Text/Badge/Teal | Teal/800 (teal-800) | Teal/100 (teal-100) | `text-teal-800 dark:text-teal-100` |  |
| Text/Badge/Pink | Pink/800 (pink-800) | Pink/100 (pink-100) | `text-pink-800 dark:text-pink-100` |  |
| Text/Badge/Sky | Sky/800 (sky-800) | Sky/100 (sky-100) | `text-sky-800 dark:text-sky-100` |  |
| Text/Badge/Purple | Purple/800 (purple-800) | Purple/100 (purple-100) | `text-purple-800 dark:text-purple-100` |  |
| Text/Inline notification/Information/Title | Blue/800 (blue-800) | Blue/100 (blue-100) | `text-blue-800 dark:text-blue-100` | Title or primary text on info background |
| Text/Inline notification/Information/Description | Blue/700 (blue-700) | Blue/200 (blue-200) | `text-blue-700 dark:text-blue-200` | For description text on info background |
| Text/Inline notification/Success/Title | Green/800 (green-800) | Green/100 (green-100) | `text-green-800 dark:text-green-100` | Title or primary text on success background |
| Text/Inline notification/Success/Description | Green/700 (green-700) | Green/200 (green-200) | `text-green-700 dark:text-green-200` | For description text on success background |
| Text/Inline notification/Warning/Title | Amber/800 (amber-800) | Amber/50 (amber-50) | `text-amber-800 dark:text-amber-50` | Title or primary text on warning background |
| Text/Inline notification/Warning/Description | Amber/700 (amber-700) | Amber/100 (amber-100) | `text-amber-700 dark:text-amber-100` | For description text on warning background |
| Text/Inline notification/Error/Title | Rose/800 (rose-800) | Rose/100 (rose-100) | `text-rose-800 dark:text-rose-100` | Title or primary text on rose background |
| Text/Inline notification/Error/Description | Rose/700 (rose-700) | Rose/200 (rose-200) | `text-rose-700 dark:text-rose-200` | For description text on rose background |
| Text/Calls and status/Online | Green/700 (green-700) | Green/500 (green-500) | `text-green-700 dark:text-green-500` | Icons or content not text |
| Text/Calls and status/Busy | Red/700 (red-700) | Red/500 (red-500) | `text-red-700 dark:text-red-500` | Icons or content not text |
| Text/Calls and status/Busy on L2 | Red/700 (red-700) | Red/400 (red-400) | `text-red-700 dark:text-red-400` | Icons or content not text |
| Text/Calls and status/Offline | Gray/700 (gray-700) | Gray/400 (gray-400) | `text-gray-700 dark:text-gray-400` | Icons or content not text |
| Text/Calls and status/Pause | Amber/700 (amber-700) | Amber/500 (amber-500) | `text-amber-700 dark:text-amber-500` | Icons or content not text |

## Elevation

The backgrounds of the interface: page, top bar, sidebar, cards.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Elevation/L0 | White (white) | Gray/950 (gray-950) | `bg-white dark:bg-gray-950` | Background color for content on S0 (es: cards) |
| Elevation/L1 | Gray/50 (gray-50) | Gray/900 (gray-900) | `bg-gray-50 dark:bg-gray-900` | Background color for first surface (es: page bg, drawer bg) |
| Elevation/L2 | Gray/100 (gray-100) | Gray/800 (gray-800) | `bg-gray-100 dark:bg-gray-800` | Background color for content on S0 (es: cards) |
| Elevation/L2 invert | White (white) | Gray/950 (gray-950) | `bg-white dark:bg-gray-950` | Background color for content on S0 (es: cards) |
| Elevation/L3 | Gray/200 (gray-200) | Gray/700 (gray-700) | `bg-gray-200 dark:bg-gray-700` | Background color for content on S0 (es: cards) |
| Elevation/L4 | Gray/300 (gray-300) | Gray/600 (gray-600) | `bg-gray-300 dark:bg-gray-600` | Background color for content on S0 (es: cards) |

## Icon

Icons, by role.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Icon/Tooltip | Indigo/800 (indigo-800) | Indigo/300 (indigo-300) | `text-indigo-800 dark:text-indigo-300` |  |
| Icon/Primary neutral | Gray/900 (gray-900) | Gray/50 (gray-50) | `text-gray-900 dark:text-gray-50` |  |
| Icon/Primary invert | White (white) | Gray/950 (gray-950) | `text-white dark:text-gray-950` |  |
| Icon/Secondary | Indigo/700 (indigo-700) | Indigo/500 (indigo-500) | `text-indigo-700 dark:text-indigo-500` |  |
| Icon/Favourite | Indigo/700 (indigo-700) | Indigo/400 (indigo-400) | `text-indigo-700 dark:text-indigo-400` |  |
| Icon/Secondary neutral | Gray/700 (gray-700) | Gray/200 (gray-200) | `text-gray-700 dark:text-gray-200` |  |
| Icon/Tertiary neutral | Gray/600 (gray-600) | Gray/400 (gray-400) | `text-gray-600 dark:text-gray-400` |  |
| Icon/Danger | Rose/700 (rose-700) | Rose/500 (rose-500) | `text-rose-700 dark:text-rose-500` |  |
| Icon/Enabled | Green/700 (green-700) | Green/500 (green-500) | `text-green-700 dark:text-green-500` |  |
| Icon/Disabled | Gray/700 (gray-700) | Gray/400 (gray-400) | `text-gray-700 dark:text-gray-400` |  |
| Icon/Warning | Amber/700 (amber-700) | Amber/500 (amber-500) | `text-amber-700 dark:text-amber-500` |  |
| Icon/Information | Blue/700 (blue-700) | Blue/500 (blue-500) | `text-blue-700 dark:text-blue-500` |  |
| Icon/Badge/Gray | Gray/800 (gray-800) | Gray/100 (gray-100) | `text-gray-800 dark:text-gray-100` |  |
| Icon/On surface/Info | Blue/800 (blue-800) | Blue/100 (blue-100) | `text-blue-800 dark:text-blue-100` |  |
| Icon/On surface/Success | Green/800 (green-800) | Green/100 (green-100) | `text-green-800 dark:text-green-100` |  |
| Icon/On surface/Warning | Amber/800 (amber-800) | Amber/50 (amber-50) | `text-amber-800 dark:text-amber-50` |  |
| Icon/On surface/Error | Rose/800 (rose-800) | Rose/100 (rose-100) | `text-rose-800 dark:text-rose-100` |  |
| Icon/On surface/Empty state | Gray/400 (gray-400) | Gray/500 (gray-500) | `text-gray-400 dark:text-gray-500` |  |
| Icon/Badge/Rose | Rose/800 (rose-800) | Rose/100 (rose-100) | `text-rose-800 dark:text-rose-100` |  |
| Icon/Badge/Amber | Amber/800 (amber-800) | Amber/50 (amber-50) | `text-amber-800 dark:text-amber-50` |  |
| Icon/Badge/Green | Green/800 (green-800) | Green/50 (green-50) | `text-green-800 dark:text-green-50` |  |
| Icon/Badge/Indigo | Indigo/800 (indigo-800) | Indigo/100 (indigo-100) | `text-indigo-800 dark:text-indigo-100` |  |
| Icon/Badge/Teal | Teal/800 (teal-800) | Teal/100 (teal-100) | `text-teal-800 dark:text-teal-100` |  |
| Icon/Badge/Cyan | Cyan/800 (cyan-800) | Cyan/100 (cyan-100) | `text-cyan-800 dark:text-cyan-100` |  |
| Icon/Badge/Blue | Blue/800 (blue-800) | Blue/100 (blue-100) | `text-blue-800 dark:text-blue-100` |  |
| Icon/Badge/Emerald | Emerald/800 (emerald-800) | Emerald/50 (emerald-50) | `text-emerald-800 dark:text-emerald-50` |  |
| Icon/Badge/Orange | Orange/800 (orange-800) | Orange/100 (orange-100) | `text-orange-800 dark:text-orange-100` |  |
| Icon/Badge/Yellow | Yellow/700 (yellow-700) | Yellow/100 (yellow-100) | `text-yellow-700 dark:text-yellow-100` |  |
| Icon/Badge/Pink | Pink/800 (pink-800) | Pink/100 (pink-100) | `text-pink-800 dark:text-pink-100` |  |
| Icon/Badge/Sky | Sky/800 (sky-800) | Sky/100 (sky-100) | `text-sky-800 dark:text-sky-100` |  |
| Icon/Badge/Purple | Purple/800 (purple-800) | Purple/100 (purple-100) | `text-purple-800 dark:text-purple-100` |  |
| Icon/Rounded icon/Green | Green/700 (green-700) | Green/50 (green-50) | `text-green-700 dark:text-green-50` |  |
| Icon/Rounded icon/Rose | Rose/700 (rose-700) | Rose/50 (rose-50) | `text-rose-700 dark:text-rose-50` |  |
| Icon/Rounded icon/Blue | Blue/700 (blue-700) | Blue/50 (blue-50) | `text-blue-700 dark:text-blue-50` |  |
| Icon/Rounded icon/Gray | Gray/700 (gray-700) | Gray/50 (gray-50) | `text-gray-700 dark:text-gray-50` |  |
| Icon/Rounded icon/Light gray | Gray/300 (gray-300) | Gray/600 (gray-600) | `text-gray-300 dark:text-gray-600` |  |
| Icon/Rounded icon/Teal | Teal/700 (teal-700) | Teal/50 (teal-50) | `text-teal-700 dark:text-teal-50` |  |
| Icon/Rounded icon/Indigo | Indigo/700 (indigo-700) | Indigo/50 (indigo-50) | `text-indigo-700 dark:text-indigo-50` |  |
| Icon/Rounded icon/Cyan | Cyan/700 (cyan-700) | Cyan/50 (cyan-50) | `text-cyan-700 dark:text-cyan-50` |  |
| Icon/Rounded icon/Violet | Violet/700 (violet-700) | Violet/50 (violet-50) | `text-violet-700 dark:text-violet-50` |  |
| Icon/Rounded icon/Emerald | Emerald/700 (emerald-700) | Emerald/50 (emerald-50) | `text-emerald-700 dark:text-emerald-50` |  |
| Icon/Rounded icon/Orange | Orange/700 (orange-700) | Orange/50 (orange-50) | `text-orange-700 dark:text-orange-50` |  |
| Icon/Rounded icon/Pink | Pink/700 (pink-700) | Pink/50 (pink-50) | `text-pink-700 dark:text-pink-50` |  |
| Icon/Rounded icon/Purple | Purple/700 (purple-700) | Purple/50 (purple-50) | `text-purple-700 dark:text-purple-50` |  |
| Icon/Rounded icon/Sky | Sky/700 (sky-700) | Sky/50 (sky-50) | `text-sky-700 dark:text-sky-50` |  |
| Icon/Rounded icon/Pink My Nethesis | Pink/600 (pink-600) | Pink/400 (pink-400) | `text-pink-600 dark:text-pink-400` |  |
| Icon/Rounded icon/Purple My Nethesis | Purple/700 (purple-700) | Purple/400 (purple-400) | `text-purple-700 dark:text-purple-400` |  |
| Icon/Rounded icon/Blue My Nethesis | Blue/700 (blue-700) | Blue/400 (blue-400) | `text-blue-700 dark:text-blue-400` |  |
| Icon/Rounded icon/Yellow My Nethesis | Yellow/600 (yellow-600) | Yellow/500 (yellow-500) | `text-yellow-600 dark:text-yellow-500` |  |
| Icon/White | White (white) | White (white) | `text-white dark:text-white` |  |
| Icon/Calls and status/Online | Green/700 (green-700) | Green/500 (green-500) | `text-green-700 dark:text-green-500` | Icons or content not text |
| Icon/Calls and status/Busy | Red/700 (red-700) | Red/500 (red-500) | `text-red-700 dark:text-red-500` | Icons or content not text |
| Icon/Calls and status/Offline | Gray/700 (gray-700) | Gray/400 (gray-400) | `text-gray-700 dark:text-gray-400` | Icons or content not text |
| Icon/Calls and status/Pause | Amber/700 (amber-700) | Amber/500 (amber-500) | `text-amber-700 dark:text-amber-500` | Icons or content not text |
| Icon/Phone island/Record bg | White (white) | Red/700 (red-700) | `text-white dark:text-red-700` |  |
| Icon/Phone island/Record centre | Red/700 (red-700) | White (white) | `text-red-700 dark:text-white` |  |

## Surface

The other surfaces, by role: inputs, badges, notifications, buttons.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Surface/Background/Input | White (white) | Gray/950 (gray-950) | `bg-white dark:bg-gray-950` |  |
| Surface/Background/Input hover | Gray/200 (gray-200) | Gray/700 (gray-700) | `bg-gray-200 dark:bg-gray-700` |  |
| Surface/Background/Table tag | Indigo/300 (indigo-300) | Indigo/800 (indigo-800) | `bg-indigo-300 dark:bg-indigo-800` |  |
| Surface/Background/Tooltip | Gray/800 (gray-800) | Gray/100 (gray-100) | `bg-gray-800 dark:bg-gray-100` |  |
| Surface/Background/Progress bar | Gray/300 (gray-300) | Gray/600 (gray-600) | `bg-gray-300 dark:bg-gray-600` | Icons or content not text |
| Surface/Background/New email | Indigo/100 (indigo-100) | Indigo/950 (indigo-950) | `bg-indigo-100 dark:bg-indigo-950` | Icons or content not text |
| Surface/Badge/Gray | Gray/200 (gray-200) | Gray/600 (gray-600) | `bg-gray-200 dark:bg-gray-600` |  |
| Surface/Changes-badge/Update | Blue/50 (blue-50) | Blue/950 (blue-950) | `bg-blue-50 dark:bg-blue-950` |  |
| Surface/Changes-badge/Create | Green/50 (green-50) | Green/950 (green-950) | `bg-green-50 dark:bg-green-950` |  |
| Surface/Changes-badge/Delete | Rose/50 (rose-50) | Rose/950 (rose-950) | `bg-rose-50 dark:bg-rose-950` |  |
| Surface/Changes-badge/Indigo | Indigo/50 (indigo-50) | Indigo/950 (indigo-950) | `bg-indigo-50 dark:bg-indigo-950` |  |
| Surface/Badge/Rose | Rose/100 (rose-100) | Rose/700 (rose-700) | `bg-rose-100 dark:bg-rose-700` |  |
| Surface/Badge/Amber | Amber/100 (amber-100) | Amber/700 (amber-700) | `bg-amber-100 dark:bg-amber-700` |  |
| Surface/Badge/Green | Green/100 (green-100) | Green/700 (green-700) | `bg-green-100 dark:bg-green-700` |  |
| Surface/Badge/Indigo | Indigo/100 (indigo-100) | Indigo/700 (indigo-700) | `bg-indigo-100 dark:bg-indigo-700` |  |
| Surface/Badge/Teal | Teal/100 (teal-100) | Teal/700 (teal-700) | `bg-teal-100 dark:bg-teal-700` |  |
| Surface/Badge/Pink | Pink/100 (pink-100) | Pink/700 (pink-700) | `bg-pink-100 dark:bg-pink-700` |  |
| Surface/Badge/Sky | Sky/100 (sky-100) | Sky/700 (sky-700) | `bg-sky-100 dark:bg-sky-700` |  |
| Surface/Badge/Cyan NethSecurity | Cyan/100 (cyan-100) | Cyan/700 (cyan-700) | `bg-cyan-100 dark:bg-cyan-700` |  |
| Surface/Badge/Emerald NethVoice | Emerald/100 (emerald-100) | Emerald/700 (emerald-700) | `bg-emerald-100 dark:bg-emerald-700` |  |
| Surface/Badge/Blue NethLink | Blue/100 (blue-100) | Blue/700 (blue-700) | `bg-blue-100 dark:bg-blue-700` |  |
| Surface/Badge/Orange NethService | Orange/100 (orange-100) | Orange/700 (orange-700) | `bg-orange-100 dark:bg-orange-700` |  |
| Surface/Badge/Yellow | Yellow/100 (yellow-100) | Yellow/700 (yellow-700) | `bg-yellow-100 dark:bg-yellow-700` |  |
| Surface/Badge/Purple | Purple/100 (purple-100) | Purple/700 (purple-700) | `bg-purple-100 dark:bg-purple-700` |  |
| Surface/Button/Secondary Hover | Opacity/Gray-200 A70 (gray-200/70) | Opacity/Gray-600 A30 (gray-600/30) | `bg-gray-200/70 dark:bg-gray-600/30` |  |
| Surface/Card/Secondary Hover | Opacity/Gray-200 A70 (gray-200/70) | Opacity/Gray-600 A30 (gray-600/30) | `bg-gray-200/70 dark:bg-gray-600/30` |  |
| Surface/Card/Tertiary Hover | Opacity/Gray-200 A70 (gray-200/70) | Opacity/Gray-600 A30 (gray-600/30) | `bg-gray-200/70 dark:bg-gray-600/30` |  |
| Surface/Card/Focus ring black white | White (white) | Black (black) | `bg-white dark:bg-black` |  |
| Surface/Card/Accent/Emerald | Emerald/50 (emerald-50) | Emerald/900 (emerald-900) | `bg-emerald-50 dark:bg-emerald-900` |  |
| Surface/Card/Phone island/Active | Gray/700 (gray-700) | Gray/300 (gray-300) | `bg-gray-700 dark:bg-gray-300` |  |
| Surface/Card/Phone island/Hover | Gray/800 (gray-800) | Gray/50 (gray-50) | `bg-gray-800 dark:bg-gray-50` |  |
| Surface/Card/Phone island/Call | Green/700 (green-700) | Green/500 (green-500) | `bg-green-700 dark:bg-green-500` |  |
| Surface/Card/Phone island/Call hover | Green/800 (green-800) | Green/300 (green-300) | `bg-green-800 dark:bg-green-300` |  |
| Surface/Card/Phone island/Close | Red/700 (red-700) | Red/500 (red-500) | `bg-red-700 dark:bg-red-500` |  |
| Surface/Card/Phone island/Close hover | Red/800 (red-800) | Red/300 (red-300) | `bg-red-800 dark:bg-red-300` |  |
| Surface/Inline notification/Info | Blue/100 (blue-100) | Blue/900 (blue-900) | `bg-blue-100 dark:bg-blue-900` | Background for components like InlineNotification |
| Surface/Inline notification/Success | Green/100 (green-100) | Green/900 (green-900) | `bg-green-100 dark:bg-green-900` | Background for components like InlineNotification |
| Surface/Inline notification/Warning | Amber/100 (amber-100) | Amber/700 (amber-700) | `bg-amber-100 dark:bg-amber-700` | Background for components like InlineNotification |
| Surface/Inline notification/Error | Rose/100 (rose-100) | Rose/900 (rose-900) | `bg-rose-100 dark:bg-rose-900` | Background for components like InlineNotification |
| Surface/Button/Tertiary Hover | Opacity/Gray-200 A70 (gray-200/70) | Opacity/Gray-600 A30 (gray-600/30) | `bg-gray-200/70 dark:bg-gray-600/30` |  |
| Surface/Button/Focus ring black white | White (white) | Black (black) | `bg-white dark:bg-black` |  |
| Surface/Button/Danger/Active | Rose/700 (rose-700) | Rose/600 (rose-600) | `bg-rose-700 dark:bg-rose-600` |  |
| Surface/Button/Danger/Hover | Rose/800 (rose-800) | Rose/500 (rose-500) | `bg-rose-800 dark:bg-rose-500` |  |
| Surface/Info | Blue/700 (blue-700) | Blue/200 (blue-200) | `bg-blue-700 dark:bg-blue-200` | Icons or content not text |
| Surface/Rounded icon/Blue | Blue/100 (blue-100) | Blue/700 (blue-700) | `bg-blue-100 dark:bg-blue-700` | Icons or content not text |
| Surface/Phone island/Background | Gray/50 (gray-50) | Gray/950 (gray-950) | `bg-gray-50 dark:bg-gray-950` | Icons or content not text |
| Surface/Phone island/Sidebar | Gray/700 (gray-700) | Gray/700 (gray-700) | `bg-gray-700 dark:bg-gray-700` | Icons or content not text |
| Surface/Phone island/Sidebar hover | Gray/600 (gray-600) | Gray/600 (gray-600) | `bg-gray-600 dark:bg-gray-600` | Icons or content not text |
| Surface/Rounded icon/Gray | Gray/100 (gray-100) | Gray/700 (gray-700) | `bg-gray-100 dark:bg-gray-700` | Icons or content not text |
| Surface/Rounded icon/Gray My Nethesis | Gray/200 (gray-200) | Gray/700 (gray-700) | `bg-gray-200 dark:bg-gray-700` | Icons or content not text |
| Surface/Rounded icon/Light Gray | Gray/900 (gray-900) | Gray/50 (gray-50) | `bg-gray-900 dark:bg-gray-50` | Icons or content not text |
| Surface/Rounded icon/Green | Green/100 (green-100) | Green/700 (green-700) | `bg-green-100 dark:bg-green-700` | Icons or content not text |
| Surface/Rounded icon/Indigo | Indigo/100 (indigo-100) | Indigo/700 (indigo-700) | `bg-indigo-100 dark:bg-indigo-700` | Icons or content not text |
| Surface/Rounded icon/Rose | Rose/100 (rose-100) | Rose/700 (rose-700) | `bg-rose-100 dark:bg-rose-700` | Icons or content not text |
| Surface/Rounded icon/Teal | Teal/100 (teal-100) | Teal/700 (teal-700) | `bg-teal-100 dark:bg-teal-700` | Icons or content not text |
| Surface/Rounded icon/Cyan | Cyan/100 (cyan-100) | Cyan/700 (cyan-700) | `bg-cyan-100 dark:bg-cyan-700` | Icons or content not text |
| Surface/Rounded icon/Violet | Violet/100 (violet-100) | Violet/700 (violet-700) | `bg-violet-100 dark:bg-violet-700` | Icons or content not text |
| Surface/Rounded icon/Emerald | Emerald/100 (emerald-100) | Emerald/700 (emerald-700) | `bg-emerald-100 dark:bg-emerald-700` | Icons or content not text |
| Surface/Rounded icon/Orange | Orange/100 (orange-100) | Orange/700 (orange-700) | `bg-orange-100 dark:bg-orange-700` | Icons or content not text |
| Surface/Rounded icon/Pink | Pink/100 (pink-100) | Pink/700 (pink-700) | `bg-pink-100 dark:bg-pink-700` | Icons or content not text |
| Surface/Rounded icon/Purple | Purple/100 (purple-100) | Purple/700 (purple-700) | `bg-purple-100 dark:bg-purple-700` | Icons or content not text |
| Surface/Rounded icon/Sky | Sky/100 (sky-100) | Sky/700 (sky-700) | `bg-sky-100 dark:bg-sky-700` | Icons or content not text |
| Surface/Success | Green/700 (green-700) | Green/200 (green-200) | `bg-green-700 dark:bg-green-200` | Icons or content not text |
| Surface/Warning | Amber/700 (amber-700) | Amber/100 (amber-100) | `bg-amber-700 dark:bg-amber-100` | Icons or content not text |
| Surface/Error | Rose/700 (rose-700) | Rose/200 (rose-200) | `bg-rose-700 dark:bg-rose-200` | Icons or content not text |
| Surface/Skeleton | Gray/200 (gray-200) | Gray/700 (gray-700) | `bg-gray-200 dark:bg-gray-700` | Icons or content not text |
| Surface/Scrollbar | Gray/400 (gray-400) | Gray/400 (gray-400) | `bg-gray-400 dark:bg-gray-400` | Icons or content not text |
| Surface/Scrollbar bg | Gray/200 (gray-200) | Gray/800 (gray-800) | `bg-gray-200 dark:bg-gray-800` | Icons or content not text |
| Surface/Overlay | Opacity/Gray-500 A75 (gray-500/75) | Opacity/Gray-700 A75 (gray-700/75) | `bg-gray-500/75 dark:bg-gray-700/75` |  |
| Surface/Overlay indigo 10% | Opacity/Indigo-300 A10 (indigo-300/10) | Opacity/Indigo-500 A10 (indigo-500/10) | `bg-indigo-300/10 dark:bg-indigo-500/10` |  |
| Surface/Overlay indigo 20% | Opacity/Indigo-300 A20 (indigo-300/20) | Opacity/Indigo-500 A20 (indigo-500/20) | `bg-indigo-300/20 dark:bg-indigo-500/20` |  |
| Surface/Presence/Online | Green/500 (green-500) | Green/500 (green-500) | `bg-green-500 dark:bg-green-500` |  |
| Surface/Presence/Busy | Red/500 (red-500) | Red/500 (red-500) | `bg-red-500 dark:bg-red-500` |  |
| Surface/Presence/DND | Gray/950 (gray-950) | Gray/950 (gray-950) | `bg-gray-950 dark:bg-gray-950` |  |
| Surface/Presence/Offline | Gray/500 (gray-500) | Gray/500 (gray-500) | `bg-gray-500 dark:bg-gray-500` |  |
| Surface/Notification button/Information/Active | Blue/800 (blue-800) | Blue/100 (blue-100) | `bg-blue-800 dark:bg-blue-100` |  |
| Surface/Toggle/Switch | White (white) | White (white) | `bg-white dark:bg-white` | Icons or content not text |
| Surface/Toggle/Background disabled | Gray/400 (gray-400) | Gray/400 (gray-400) | `bg-gray-400 dark:bg-gray-400` | Icons or content not text |
| Surface/Notification button/Information/Hover | Blue/200 (blue-200) | Blue/800 (blue-800) | `bg-blue-200 dark:bg-blue-800` |  |
| Surface/Notification button/Information/Focus | Blue/500 (blue-500) | Blue/200 (blue-200) | `bg-blue-500 dark:bg-blue-200` |  |
| Surface/Notification button/Success/Active | Green/800 (green-800) | Green/100 (green-100) | `bg-green-800 dark:bg-green-100` |  |
| Surface/Notification button/Success/Hover | Green/200 (green-200) | Green/800 (green-800) | `bg-green-200 dark:bg-green-800` |  |
| Surface/Notification button/Success/Focus | Green/500 (green-500) | Green/200 (green-200) | `bg-green-500 dark:bg-green-200` |  |
| Surface/Notification button/Warning/Active | Amber/800 (amber-800) | Amber/50 (amber-50) | `bg-amber-800 dark:bg-amber-50` |  |
| Surface/Notification button/Warning/Hover | Amber/200 (amber-200) | Amber/800 (amber-800) | `bg-amber-200 dark:bg-amber-800` |  |
| Surface/Notification button/Warning/Focus | Amber/500 (amber-500) | Amber/200 (amber-200) | `bg-amber-500 dark:bg-amber-200` |  |
| Surface/Notification button/Error/Active | Rose/800 (rose-800) | Rose/100 (rose-100) | `bg-rose-800 dark:bg-rose-100` |  |
| Surface/Notification button/Error/Hover | Rose/200 (rose-200) | Rose/800 (rose-800) | `bg-rose-200 dark:bg-rose-800` |  |
| Surface/Notification button/Error/Focus | Rose/500 (rose-500) | Rose/200 (rose-200) | `bg-rose-500 dark:bg-rose-200` |  |
| Surface/Button/Phone island/Active | Gray/700 (gray-700) | Gray/300 (gray-300) | `bg-gray-700 dark:bg-gray-300` |  |
| Surface/Button/Phone island/Hover | Gray/800 (gray-800) | Gray/50 (gray-50) | `bg-gray-800 dark:bg-gray-50` |  |
| Surface/Button/Phone island/Call | Green/700 (green-700) | Green/500 (green-500) | `bg-green-700 dark:bg-green-500` |  |
| Surface/Button/Phone island/Call hover | Green/800 (green-800) | Green/300 (green-300) | `bg-green-800 dark:bg-green-300` |  |
| Surface/Button/Phone island/Close | Red/700 (red-700) | Red/500 (red-500) | `bg-red-700 dark:bg-red-500` |  |
| Surface/Button/Phone island/Close hover | Red/800 (red-800) | Red/300 (red-300) | `bg-red-800 dark:bg-red-300` |  |

## Border

Rings and accent borders of components.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Border/Ring/Button | Gray/300 (gray-300) | Gray/500 (gray-500) | `ring-gray-300 dark:ring-gray-500` |  |
| Border/Ring/Input | Gray/300 (gray-300) | Gray/500 (gray-500) | `ring-gray-300 dark:ring-gray-500` |  |
| Border/Ring/Input read only | Gray/200 (gray-200) | Gray/600 (gray-600) | `ring-gray-200 dark:ring-gray-600` |  |
| Border/Ring/Secondary | Gray/300 (gray-300) | Gray/700 (gray-700) | `ring-gray-300 dark:ring-gray-700` |  |
| Border/Ring/Layout divider | Gray/200 (gray-200) | Gray/700 (gray-700) | `ring-gray-200 dark:ring-gray-700` |  |
| Border/Ring/Error-focus | Rose/500 (rose-500) | Rose/400 (rose-400) | `ring-rose-500 dark:ring-rose-400` | Border for components like InlineNotification |
| Border/Ring/Toast | Gray 500 5% (gray-500/5) | Gray 500 10% (gray-500/10) | `ring-gray-500/5 dark:ring-gray-500/10` | Border for components like InlineNotification |
| Border/Accent/Indigo | Indigo/500 (indigo-500) | Indigo/400 (indigo-400) | `border-indigo-500 dark:border-indigo-400` | Border for components like InlineNotification |
| Border/Accent/Green | Green/500 (green-500) | Green/400 (green-400) | `border-green-500 dark:border-green-400` | Border for components like InlineNotification |
| Border/Accent/Amber | Amber/500 (amber-500) | Amber/400 (amber-400) | `border-amber-500 dark:border-amber-400` | Border for components like InlineNotification |
| Border/Accent/Rose | Rose/700 (rose-700) | Rose/500 (rose-500) | `border-rose-700 dark:border-rose-500` |  |
| Border/Accent/Gray | Gray/700 (gray-700) | Gray/500 (gray-500) | `border-gray-700 dark:border-gray-500` |  |
| Border/Accent/Blue | Blue/700 (blue-700) | Blue/500 (blue-500) | `border-blue-700 dark:border-blue-500` |  |
| Border/Accent/Violet | Violet/700 (violet-700) | Violet/500 (violet-500) | `border-violet-700 dark:border-violet-500` |  |

## Utility

Colors for special cases, such as pulsing indicators.

| Token | Light | Dark | Classes | Description |
|---|---|---|---|---|
| Utility/Green | Lime/700 (lime-700) | Lime/400 (lime-400) | — |  |
| Utility/Yellow | Yellow/700 (yellow-700) | Yellow/400 (yellow-400) | — |  |
| Utility/Sky | Sky/700 (sky-700) | Sky/400 (sky-400) | — |  |
| Utility/Pulsing green | None (#15803d4d) | None (#22c55e4d) | — |  |
| Utility/Pulsing red | None (#b91c1c4d) | None (#ef44444d) | — |  |
