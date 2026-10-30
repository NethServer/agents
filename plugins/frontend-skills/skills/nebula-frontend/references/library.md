# Changing @nethesis/vue-components

Follow the library's `AGENTS.md` and `CONTRIBUTING.md` for exports, stories, descriptions and
deprecations. This file adds what the design system needs.

- **Before writing**: read the component's source and the components that already show the same
  element, such as a description, a close button or a footer (`NeModal`, `NeEmptyState`,
  `NeCard`…). Use the same text style, color and spacing, so that the element looks the same in
  every component.
- **Colors**: the library defines no semantic colors, and `src/styles/theme.css` reaches every
  product. Use the `classes` of the token in `colors.json` (`references/colors.md`).
- **Texts**: every text the user sees or hears is a prop. A fixed text, such as a label or an
  aria label, gets an English default written by the writing guidelines (`references/text.md`).
  Optional content, such as a title or a description, defaults to `''`.
- **Compatibility**: add props, slots and events; do not rename or remove them.
- **Accessibility**: besides the keyboard and the focus ring, give dialogs a name and a
  description: the title in Headless UI's `DialogTitle`, as `NeModal` does, and the description in
  `DialogDescription`.
- **Stories**: a story for each new variant, with texts that follow the writing guidelines, and
  the description in `parameters.docs.description.component` updated. Check the patterns that use
  the component (`stories/Pattern*.stories.ts`) and update them when the change affects them.

## Checks

The library has no type-check or test script. Run `npm run lint`, `npm run format` (it checks only
`src/`: run Prettier on the stories you changed too), `npm run build` and
`npm run build-storybook`, which also builds `components.json`.

Then open each story you changed in the light and the dark theme, at desktop and phone width:
`npm run storybook`, then `http://localhost:6006/iframe.html?id=<story-id>&globals=theme:dark`
(the story id ends the `link` of the story in `components.json`).

Of the commands of `references/review.md`, skip the check for raw elements, which the components
are made of, and replace the two deprecation checks with `grep -rn -A3 @deprecated src`.
