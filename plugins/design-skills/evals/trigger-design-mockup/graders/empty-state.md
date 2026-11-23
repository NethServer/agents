---
type: llm
focus:
  source: file
  path: speed-dials.html
---

The prototype has an empty state for when there are no speed dials, with an icon, a title, a description and a `Create speed dial` button; while that empty state is shown the page header does not show a second `Create speed dial` button (one Primary action per view). Fail if there is no empty state or if both create buttons show at the same time.
