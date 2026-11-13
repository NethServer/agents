# NethSecurity: product shell and specifics

From the Nebula Figma file (sidebar) and the NethSecurity UI code (github.com/NethServer/nethsecurity-ui: `StandaloneTopBar.vue`, `SideMenu.vue`, `i18n/en.json`), read on 2026-11-10. Draw this shell around every NethSecurity page mockup or prototype, unless the designer asks for the content area only. If the designer's Figma shows something different, follow Figma and say what differs.

Primary palette: Cyan. Product name in the UI: NethSecurity; each installation is a "unit" (glossary).

## Layout

- Desktop (`lg` and up): **sidebar** on the left, then the content. Below `lg` the sidebar becomes a drawer opened by the `bars` button in the top bar (`Open sidebar` / `Close sidebar`).
- Content: `main` with `py-10`, inner `px-4 sm:px-6 lg:px-8`, on the L1 page background.

## Sidebar

Source: the Figma component **"Main sidebar + labels"**, variant Product=NethSecurity (Nebula file, node 1427:791), read on 2026-11-10. **Figma wins over the code** for the look (the code has 288 px and `font-semibold`). Labels: the code's "Logs" is correct (Figma's "Log" is a Figma error).

- 300 px wide, L0 `bg-white dark:bg-gray-950`, right border; logo row 50 px (padding 11/24) with the real **NethSecurity logo**, 200×28, in `Product Primary/Active` (export the `logo-nethsecurity` component from Figma as SVG, or use the logo components of the Nebula Design System artifact; never a text placeholder); sections list with padding 8 and gap 8. The resize control at the bottom (`circle-chevron-left`) is **off by default** in the component (not decided yet): don't draw it.
- **Section item** (`_sidebar section + label NethSecurity`): 50 px high, radius 6 (`rounded-md`), icon 24 px + label with gap 16, label **16 px Medium** (`text-base font-medium`, line height 24).
  - Inactive: **Light** icon, icon and label in `Text/Tertiary neutral` (`text-gray-600 dark:text-gray-400`, never lighter or brighter), padding 12; sections with children end with `angle-down` 16 px, same color. Hover: `Elevation/L2`.
  - Parent of the active subsection: Solid icon, label `Text/Primary neutral`, no background, `angle-up`.
  - Active: **Solid** icon in `Icon/Primary neutral`, label `Text/Primary neutral`, background `Elevation/L2` (`bg-gray-100 dark:bg-gray-800`), and a 4×36 bar in `Product Primary/Active` (`primary-700`/`primary-500`) on the left edge.
- **Subsection item** (`_subsection element`): 32 px high, 16 px.
  - Inactive: **Regular**, `Text/Tertiary neutral`, left padding 56.
  - Active: **Medium**, `Text/Primary neutral`, on an `Elevation/L2` pill (radius 6, padding 4/12/4/16) starting 40 px from the left, with a **4 px left border in `Product Primary/Active`** (`border-l-4 border-primary-700 dark:border-primary-500`).
- Sections (icon from `site/icons.md`), labels as in Figma:
  - Dashboard (`house`)
  - Monitoring (`chart-line`): Real time monitor, Netify Informatics, Ping latency monitor, Metrics
  - System (`server`): Subscription, System settings, SSH, Backup and restore, Reboot and shutdown, Update, Storage, Factory reset, Certificates, Controller
  - Network (`network-wired`): Interfaces and devices, DNS and DHCP, Routes, MultiWAN, Hotspot, Reverse proxy, QoS
  - Users and objects (`user-group`): Users database, Objects
  - Firewall (`block-brick-fire`, Nethesis custom): Port forward, NAT, Rules, Conntrack
  - Security (`shield-halved`) and VPN (`globe`), with children
  - Logs (`list`), last, no children
  - Children come from `SideMenu.vue` and `i18n/en.json` of the code; check them in Figma when a page needs them.

## Top bar

`sticky top-0 h-16`, L0 `bg-white dark:bg-gray-950`, `border-b border-gray-200 dark:border-gray-700 shadow-sm`, `px-4 sm:px-6 lg:px-8`, `gap-x-4 lg:gap-x-6`. Left: `bars` button (mobile only) and a 1 px separator; then empty space (global search slot). Right, in order:
1. **Unsaved changes** — only when there are staged changes: `NeButton kind="primary"` with `pen-to-square` prefix and the label `Unsaved changes` (it pulses when a change is added). It opens the modal "Configuration changes" with `Apply changes` / `Revert changes`.
2. `Controller` badge (primary) with tooltip, only when the unit is managed by a Controller.
3. Unit name (desktop only), with an `award` icon and tooltip `Subscription active` when the subscription is active.
4. Vertical separator `h-6 w-px bg-gray-200 dark:bg-gray-700`.
5. Help: `circle-question` 24 px, link to the documentation, tooltip `Help`.
6. Notifications: `bell` 24 px, tooltip `Notifications`, accessible name `Show notifications`; a rose dot (`size-3`) when there are notifications.
7. Account: circle with the initial of the username (`size-8 rounded-full bg-gray-200 text-gray-700`) + `chevron-down` 12 px, opening an `NeDropdown` (Account settings, Sign out…); tooltip `Account`.

Top bar icon buttons: `rounded-full p-2.5 text-gray-600 hover:bg-gray-100 hover:text-gray-900` (dark: `text-gray-300 hover:bg-gray-800 hover:text-gray-50`), with a tooltip on hover and focus.

## Behavior that changes the design

- **Staged changes**: most saves and deletions are not applied immediately; they go to "Unsaved changes" in the top bar. **No success toast** for them (`components.md` §9).
- Page titles and descriptions exist in `i18n/en.json` (e.g. `standalone.port_forward.title` = "Port forward", with its description): reuse them instead of inventing new ones, and propose fixes only when they break the writing guidelines.
