---
type: llm
focus:
  source: file
  path: src/i18n/it/translation.json
---

The Italian i18n file has the same keys as the English one for the archive confirmation, translated with these rules: the title is `Archivia cliente`; the description names the customer through the same parameter and says that it can be restored (`ripristinare`); the buttons are `Archivia` and `Annulla`. Labels use the imperative (`Archivia`), not the infinitive (`Archiviare`). It fails when the Italian keys are missing, on quotes around the customer name, or on `Cancella`, `Disattiva` or `Elimina`.
