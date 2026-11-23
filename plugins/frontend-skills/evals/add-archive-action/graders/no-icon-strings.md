---
type: regex
pattern: 'library\.add|\[\s*''fas'''
match: not_contains
target:
  source: file
  path: src/components/CustomersTable.vue
---
