# Icons: which icon for which meaning

> Mirror of https://nethesis.github.io/nebula-design-system/?page=iconography#icon-meanings, synced on 2026-11-10 by `scripts/sync_site.py`. Do not edit: the site is the source of truth. If the live site disagrees, follow the site.

Use the same icon for the same meaning in every product; NethServer 8 modules, which follow the Carbon Design System, are excluded. icon is the kebab-case name: import it as fa + PascalCase (circle-plus: faCirclePlus) from the package of its pack, and pass the imported object to FontAwesomeIcon. Sidebar entries use the ns-light icon for the inactive section and the solid one for the active section. avoid lists the Font Awesome Solid icons not to use for that meaning. products lists the products that use the entry; without it, the entry applies to every product. glossary lists the terms of the glossary for the actions and objects of the entry. link is the entry in the Iconography page, to cite in reviews. When a meaning is missing, choose a Font Awesome Solid icon that no other meaning uses. Do not use the custom icons listed in customIconsWithoutMeaning: they have no agreed meaning yet.

Packages: fa-solid = Font Awesome Solid (`@fortawesome/free-solid-svg-icons`); ns-solid = Nethesis Solid (`@nethesis/nethesis-solid-svg-icons`); ns-light = Nethesis Light (`@nethesis/nethesis-light-svg-icons`); ns-brands = Nethesis Brands (`@nethesis/nethesis-brands-svg-icons`).

`icon` is the kebab-case name: in code it is `fa` + PascalCase (`circle-plus` → `faCirclePlus`).

## Contents
- Actions
- Navigation
- Interface controls
- Status
- Sidebar sections
- Nethesis objects
- Brands
- Custom icons without a meaning

## Actions

Buttons and menu items that do something.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Create or add** | `circle-plus` | fa-solid | Buttons that create a new object or add an existing one, such as "Create user" or "Add member", also in empty states. |  | `plus` | All |  |
| **Add a row** | `plus` | fa-solid | Add another row of fields inside a form, such as another IP address. | Buttons that create or add an object. |  | All |  |
| **Edit** | `pen-to-square` | fa-solid | Change the data of an object. |  | `pen` | All |  |
| **Delete** | `trash` | fa-solid | Permanently destroy an object. | Taking an object out of a list or an association. |  | All |  |
| **Remove** | `circle-minus` | fa-solid | Take an object out of a list or an association without destroying it, such as a user from a group. |  | `minus`, `trash` | All |  |
| **Duplicate** | `clone` | fa-solid | Create a new object as a copy of an existing one. |  | `copy` | All |  |
| **Copy to clipboard** | `copy` | fa-solid | Copy a value, such as a key or a link, to the clipboard. | Duplicating an object. |  | All |  |
| **Download** | `circle-arrow-down` | fa-solid | Download a file, such as a backup or a report. |  | `download`, `arrow-down` | All |  |
| **Import or upload** | `circle-arrow-up` | fa-solid | Import data or upload a file, such as a list of customers or a configuration. | Updating software. | `upload`, `arrow-up`, `file-import` | All |  |
| **Export to CSV** | `file-csv` | fa-solid | Export data to a CSV file. |  |  | All |  |
| **Export to PDF** | `file-pdf` | fa-solid | Export data to a PDF file. |  |  | All |  |
| **Refresh** | `arrows-rotate` | fa-solid | Load the data of a page or a list again. |  | `rotate`, `arrow-rotate-right` | All |  |
| **Update** | `arrows-rotate` | fa-solid | Update software to a newer version, or show that an update is available. |  | `circle-arrow-up` | All |  |
| **Restore or reset** | `arrow-rotate-left` | fa-solid | Bring back a previous state, such as a backup, or the default values, such as a factory reset. |  | `rotate-left` | All |  |
| **Save** | `floppy-disk` | fa-solid | Save the changes of a form, on buttons that show an icon. |  |  | All |  |
| **Settings** | `gear` | fa-solid | Open the settings of a page, a feature or the product. | Configuring a single item. | `sliders` | All |  |
| **Configure** | `wrench` | fa-solid | Configure a single item, such as a network interface or an alert. |  | `sliders` | All |  |
| **Revoke or block** | `ban` | fa-solid | Revoke or block access, such as an API key or an add-on. | The disabled status. |  | All |  |
| **Archive** | `box-archive` | fa-solid | Move an object to the archive, from where it can be restored. |  |  | All |  |
| **Suspend** | `circle-pause` | fa-solid | Suspend an object, such as a customer or a system, without deleting it. |  |  | All |  |
| **Reactivate** | `circle-play` | fa-solid | Reactivate a suspended object. |  |  | All |  |
| **Details** | `eye` | fa-solid | The Details button of a table row or a card, which opens the page of the object. |  |  | All | NethSecurity uses magnifying-glass-plus to show where an object is used. |
| **Search** | `magnifying-glass` | fa-solid | Search fields and text filters, and empty states with no search results. |  |  | All |  |
| **Sign in** | `arrow-right-to-bracket` | fa-solid | Enter a product with your credentials. |  | `right-to-bracket` | All |  |
| **Sign out** | `arrow-right-from-bracket` | fa-solid | Leave a product and end your session. |  | `right-from-bracket` | All |  |

## Navigation

Links and buttons that move somewhere else.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Go to** | `arrow-right` | fa-solid | Links and buttons to another page of the same product, such as "Go to systems". | Links to other sites. |  | All |  |
| **Open an external site** | `arrow-up-right-from-square` | fa-solid | Links and buttons that open another site or product, in a new tab. |  |  | All |  |
| **Next** | `arrow-right` | fa-solid | Move to the next step. |  |  | All |  |
| **Previous** | `arrow-left` | fa-solid | Move to the previous step. |  |  | All |  |

## Interface controls

Controls that are part of the interface of every product.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Close** | `xmark` | fa-solid | Close a modal, a drawer or a notification. |  |  | All |  |
| **Expand** | `chevron-down` | fa-solid | Open a menu, a section or a row that shows more content. |  | `angle-down`, `caret-down` | All |  |
| **Collapse** | `chevron-up` | fa-solid | Close an expanded menu, section or row. |  | `angle-up`, `caret-up` | All |  |
| **More actions** | `ellipsis-vertical` | fa-solid | The menu with the other actions of a row or a card, as in NeDropdown. |  | `bars` | All |  |
| **Open the sidebar** | `bars` | fa-solid | The button that opens the main sidebar on small screens. | Menus of actions. |  | All |  |
| **Help** | `circle-question` | fa-solid | Open help, or a tooltip with more information about a field. |  | `question` | All |  |
| **Show password** | `eye` | fa-solid | Show the text of a password field. |  |  | All |  |
| **Hide password** | `eye-slash` | fa-solid | Hide the text of a password field. |  |  | All |  |
| **Drag to reorder** | `grip-vertical` | fa-solid | The handle to drag a row to another position, such as a firewall rule. |  |  | All |  |
| **Notifications** | `bell` | fa-solid | Open the notifications of the product. |  |  | All |  |
| **Account** | `circle-user` | fa-solid | Open the menu or the settings of your account. |  |  | All |  |
| **Dark theme** | `moon` | fa-solid | Switch to the dark theme. |  |  | All |  |
| **Light theme** | `sun` | fa-solid | Switch to the light theme. |  |  | All |  |

## Status

Notifications, messages and states of objects.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Information** | `circle-info` | fa-solid | Notifications and messages that give information. |  |  | All |  |
| **Success** | `circle-check` | fa-solid | Notifications and messages of an action that ended well. |  |  | All |  |
| **Warning** | `triangle-exclamation` | fa-solid | Something that needs attention: warning notifications and messages, and objects with a problem, such as active alerts, an outdated version or a system that has never sent its inventory. | An action that failed, which is an error. | `circle-exclamation` | All | NethVoice CTI uses circle-exclamation for emergency queues. |
| **Error** | `circle-xmark` | fa-solid | Notifications and messages of an action that failed. |  |  | All |  |
| **Enabled** | `circle-check` | fa-solid | The status of an enabled feature or object. |  | `check` | All |  |
| **Disabled** | `circle-xmark` | fa-solid | The status of a disabled feature or object. |  | `xmark`, `ban` | All |  |

## Sidebar sections

The sections of the main sidebar: the Light icon when the section is not active, the Solid icon when it is.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Dashboard** | `house` | ns-light (inactive) + fa-solid (active) | The home page of the product. |  |  | My Nethesis, NethSecurity |  |
| **Monitoring and statistics** | `chart-line` | ns-light (inactive) + fa-solid (active) | Monitoring pages, and the Queue manager of NethVoice CTI. |  |  | NethSecurity, NethVoice |  |
| **Systems and units** | `server` | ns-light (inactive) + fa-solid (active) | Systems in My Nethesis, units in the NethSecurity controller, and the System section of NethSecurity. |  |  | My Nethesis, NethSecurity |  |
| **Network** | `network-wired` | ns-light (inactive) + fa-solid (active) | Network settings. |  |  | NethSecurity |  |
| **Users** | `user-group` | ns-light (inactive) + fa-solid (active) | Users, and the user objects of NethSecurity. |  |  | My Nethesis, NethSecurity |  |
| **Firewall** | `block-brick-fire` | ns-light (inactive) + ns-solid (active) | Firewall settings. |  |  | NethSecurity |  |
| **Security** | `shield-halved` | ns-light (inactive) + fa-solid (active) | Security features, such as Threat shield. |  |  | NethSecurity |  |
| **VPN** | `globe` | ns-light (inactive) + fa-solid (active) | VPN settings. |  |  | NethSecurity |  |
| **Distributors** | `globe` | ns-light (inactive) + fa-solid (active) | The distributors of My Nethesis. |  |  | My Nethesis |  |
| **Resellers** | `city` | ns-light (inactive) + fa-solid (active) | The resellers of My Nethesis. |  |  | My Nethesis |  |
| **Customers** | `building` | ns-light (inactive) + fa-solid (active) | The customers of My Nethesis. |  |  | My Nethesis |  |
| **Logs** | `list` | ns-light (inactive) + fa-solid (active) | Logs. |  |  | NethSecurity |  |
| **Settings** | `gear` | ns-light (inactive) + fa-solid (active) | Settings of the product or of the account. |  |  | NethSecurity, NethVoice |  |
| **Alerts** | `triangle-exclamation` | ns-light (inactive) + fa-solid (active) | Alerts. |  |  | My Nethesis |  |
| **Applications** | `grid-2` | ns-light (inactive) + ns-solid (active) | The applications of the systems. |  |  | My Nethesis | My Nethesis shows the Nethesis Solid grid-one when the section is active, instead of grid-2. |
| **Add-ons** | `puzzle-piece` | ns-light (inactive) + fa-solid (active) | Add-ons. |  |  | My Nethesis |  |
| **Rebranding** | `palette` | ns-light (inactive) + fa-solid (active) | Rebranding. |  |  | My Nethesis |  |
| **Unit groups** | `unit-groups` | ns-light (inactive) + ns-solid (active) | The unit groups of the NethSecurity controller. |  |  | NethSecurity |  |
| **Operators** | `headset` | ns-light (inactive) + fa-solid (active) | Operators. |  |  | NethVoice |  |
| **Queues** | `users` | ns-light (inactive) + fa-solid (active) | Queues. |  |  | NethVoice |  |
| **Phonebook** | `address-book` | ns-light (inactive) + fa-solid (active) | Phonebook. |  |  | NethVoice |  |
| **History** | `clock-rotate-left` | ns-light (inactive) + fa-solid (active) | The history of calls. |  |  | NethVoice |  |
| **Applications** | `cubes` | ns-light (inactive) + fa-solid (active) | The Applications section of NethVoice CTI, with the integrations of other applications. |  |  | NethVoice |  |

## Nethesis objects

Objects and actions that only a Nethesis custom icon represents.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Applications** | `grid-one` | ns-solid | Applications, in tables, cards and counters. |  |  | My Nethesis |  |
| **Unit group** | `unit-groups` | ns-solid | Unit groups of the NethSecurity controller. |  |  | NethSecurity |  |
| **Firewall** | `block-brick-fire` | ns-solid | Firewall rules, such as their empty state. |  |  | NethSecurity |  |
| **No data** | `empty-set` | ns-solid | Charts and cards with no data to show. |  |  | NethSecurity |  |
| **Missed call** | `missed` | ns-solid | The status of a missed call. |  |  | NethVoice |  |
| **Pick up a call** | `phone-arrow-down-left` | ns-solid | Pick up a call that rings on another phone. |  |  | NethVoice |  |
| **Desk phone** | `office-phone` | ns-solid | Physical phones, among the devices of a user. |  |  | NethVoice |  |
| **Record** | `record` | ns-solid | Record an audio message, such as a voicemail greeting. |  |  | NethVoice |  |
| **Video sources** | `camera-security` | ns-solid | Video sources, such as security cameras. |  |  | NethVoice |  |
| **Standard layout** | `grid-2` | ns-solid | Show items in a grid. |  |  | NethVoice |  |
| **Grouped layout** | `grid-dividers` | ns-solid | Show items in a grid, divided into groups. |  |  | NethVoice |  |

## Brands

Logos of other companies and services.

| Meaning | Icon | Pack | Use | Not for | Avoid | Products | Notes |
|---|---|---|---|---|---|---|---|
| **Gravatar** | `gravatar` | ns-brands | The logo of Gravatar, such as for a profile picture taken from it. |  |  | NethVoice |  |
| **Netflix** | `netflix` | ns-brands | The logo of Netflix. |  |  | NethSecurity |  |
| **NordVPN** | `nord-vpn` | ns-brands | The logo of NordVPN. |  |  | NethSecurity |  |
| **X** | `square-x-twitter` | ns-brands | The logo of X, formerly Twitter. |  |  | NethSecurity |  |

## Custom icons without a meaning

They have no agreed meaning yet. The site says not to use them; the skill proposes them to the designer as candidates when a meaning is missing (see Pending decisions in SKILL.md), never uses them without asking.

- ns-solid: `ai-spark`, `arrows-repeat`, `broken-repeat`, `buildings`, `child-task`, `circle-completing`, `close`, `display-slash`, `double-exclamation`, `ear-listen`, `elaborate`, `grid-round`, `hangup`, `open`, `parent-task`, `shorten`, `sum`, `traffic-cone`
- ns-light: `calendar-day`, `clipboard-list`, `cloud`, `credit-card`, `envelope`, `message`, `office-phone`, `route`, `star`, `wrench`
