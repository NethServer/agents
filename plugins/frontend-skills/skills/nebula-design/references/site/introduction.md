# Nebula Design System

> Mirror of https://nethesis.github.io/nebula-design-system/?page=introduction, synced on 2026-11-10 by `scripts/sync_site.py`. Do not edit: the site is the source of truth. If the live site disagrees, follow the site.

The Nebula Design System is made of three parts, to use together:

- **This site**: the rules shared by all products, whatever technology they are built with.
- **[vue-components Storybook](https://nethesis.github.io/vue-components/)**: the Vue components
  and patterns of `@nethesis/vue-components`, with their props and live examples.
- **[Nebula Figma file](https://www.figma.com/design/ZRZzzlqb9GfB9Xdz6iGufh/Nebula-Design-System)**: the designs,
  open to the members of the Nethesis Figma team.

It applies to the user interfaces of NethSecurity, NethVoice and My Nethesis, and in part to
[NethServer 8](#nethserver-8).

## What you find here

- [Writing guidelines](writing-guidelines.md): how to write interface text, from voice and
  tone to the text of buttons, forms, empty states, modals and notifications.
- [Glossary](glossary.md): the approved terms, with their Italian translations and the terms to
  avoid. Weblate uses it when translating Nethesis products.
- Foundations: [colors](colors.md), [typography](foundations.md),
  [iconography](icons.md), [spacing and border](foundations.md),
  [elevation and shadow](foundations.md), and
  [accessibility](accessibility.md).

## Use it with a coding agent

The `nebula-frontend` skill makes a coding agent follow Nebula when it writes or reviews a
frontend. It reads the rules from this site and from the Storybook, so it is always up to date.
It is in the `frontend-skills` plugin of [NethServer/agents](https://github.com/NethServer/agents),
for Claude Code only for now. In a Claude Code session, run:

```
/plugin marketplace add NethServer/agents
/plugin install frontend-skills@nethserver
/reload-plugins
```

Other agents can read the same rules from [`llms.txt`](https://nethesis.github.io/nebula-design-system/llms.txt), the index of the files this
site publishes for them.

## NethServer 8

NethServer 8 uses the Carbon Design System, not Nebula: only the
[writing guidelines](writing-guidelines.md) and the [glossary](glossary.md) apply to it. The
foundations and the vue-components library do not. For its components and visual style, see:

- [Carbon Design System v10](https://v10.carbondesignsystem.com/): the design system.
- [ns8-ui-lib Storybook](https://nethserver.github.io/ns8-ui-lib/): the NethServer 8 components.
- [Carbon Components Vue Storybook](https://vue.carbondesignsystem.com/vue2/): the Carbon
  components for Vue 2.
