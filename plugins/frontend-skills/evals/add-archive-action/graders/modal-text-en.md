---
type: llm
focus:
  source: file
  path: src/i18n/en/translation.json
---

The English i18n file has the texts of the archive confirmation, following these rules: the title is `Archive customer`, in sentence case; the description names the customer through a parameter (such as `{name}`), says that it will be archived and that it can be restored later; the confirm button says `Archive` and the other button `Cancel`. It fails on quotes around the customer name (`'{name}'`), on a question (`Are you sure?`), on `Confirm`, `OK` or `Yes` as the button, on `Deactivate` or `Trash`, on asking to type the name to confirm, or when a text the component shows is missing from the file.
