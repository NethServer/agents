# Interface text and translations

The rules for interface text are in the writing guidelines and the glossary of the Nethesis
Design System. Read them; do not rely on memory, and do not copy their rules into the code or
into comments.

```
https://nethesis.github.io/design-system/writing-guidelines.md
https://nethesis.github.io/design-system/glossary.json
```

- **Writing guidelines** (markdown): read the sections for the elements you write, such as
  "Buttons and actions", "Forms", "Empty states", "Modals", "Notifications". The texts of the
  vue-components patterns are examples of these rules: when a pattern disagrees with the
  guidelines or the glossary, they win.
- **Glossary** (JSON): `terms` lists the approved terms (`en`) with their definition, the
  products they apply to, the Italian translation (`it`) and the terms to avoid (`avoid.en`,
  `avoid.it`).
  `untranslatable: true` means the term stays in English in Italian too. Before you use a term
  for an object or an action, look it up, and never use a term listed under `avoid`.

## i18n files

No user-facing string goes in a template or a script as literal text: add a key to the project's
i18n files and use it through `vue-i18n` (`t()` or `$t()`).

- Find the files and the key naming in the project (for example `src/i18n/en/translation.json`
  or `src/i18n/en.json`), and follow the existing structure.
- Always add the English text.
- Italian: check who edits the Italian file (`git log --format=%an -- <file>`). If developers
  do, even when Weblate edits it too, add the Italian text, with the translations of the glossary
  and the Italian rules of the writing guidelines. If only Weblate does, do not edit it:
  translators will. Leave the other languages to Weblate.
