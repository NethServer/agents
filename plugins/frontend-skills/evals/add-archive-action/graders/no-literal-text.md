---
type: llm
focus:
  source: file
  path: src/components/CustomersTable.vue
---

Every text the user sees or that screen readers read in the component comes from an i18n key through `t(...)`, including the modal title, description, button labels and the modal's `close-aria-label`, and the label or accessible name of the delete button. It fails on a literal English string in the template or on a `Ne*` label prop left to its default when the modal shows that element.
