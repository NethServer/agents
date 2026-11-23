---
type: regex
pattern: 'are you sure|>\s*(OK|Yes|Confirm|Submit)\s*<'
flags: i
match: not_contains
target:
  source: file
  path: speed-dials.html
---
