---
type: regex
pattern: 'primary-button-kind="[^"]*danger'
match: not_contains
target:
  source: file
  path: src/components/CustomersTable.vue
---
