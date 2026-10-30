# Building from a mockup or a description

The request comes in one of three ways. In each, the result is built from components and
patterns of `@nethesis/vue-components` (`references/components.md`), not copied pixel by pixel.

## A Figma link

Use the Figma MCP server, if it is available, on the node in the link only.

- The link has the file key and the node: `figma.com/design/<fileKey>/<name>?node-id=1-2`
  means node `1:2`.
- Read that node only: `create_session` with the file key, which the server requires first,
  then one `get_design_context` on the node; add `get_screenshot` only if the structure is
  unclear. Do not browse the rest of the file, its pages or its components, and do not search
  the design system or Code Connect: the Figma plan allows few calls a month, shared by the
  whole team.
- If the Figma server is not available, or the link has no `node-id`, ask for an image of the
  frame instead.

What to take from the design:

- **Components**: Figma instances are named after the components (`Button`, `Text input`,
  `Badge`…). Use the matching `Ne*` component and its props, not the generated markup.
- **Colors**: Figma variables have the names of the semantic tokens (`Text/Secondary neutral`,
  `Elevation/L2`). Map them as in `references/colors.md`.
- **Text**: the texts of the mockup are a draft. Check them against the writing guidelines and
  the glossary (`references/text.md`), which win when they disagree.
- **Layout and spacing**: Tailwind spacing classes (`gap-4`, `p-6`), not pixel values.

## An image of the mockup

Identify the components and the layout from the image, then proceed as with a Figma link.
Colors and sizes are only estimates from an image: choose the closest semantic token and the
closest Tailwind spacing step, and say which ones you guessed.

## A description

Start from the pattern that matches the request, if any (a table page, a delete confirmation,
an empty state…), then add the components the description asks for. Ask before inventing
content that the description does not give, such as table columns or form fields; if you cannot
ask, choose, and list your choices in your answer.
