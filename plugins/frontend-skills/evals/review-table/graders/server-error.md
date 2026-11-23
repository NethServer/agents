---
type: llm
weight: 1
---

The review reports that the error notification binds `error.message` as its description, so a network error (such as `Network Error`) or a server fault reaches the user as it is, and says to show a fixed text from the i18n files for those, such as one that says to check the connection. Saying that the message of a 4xx with no field can stay as it is, or asking to check whether the project replaces the message elsewhere, is welcome but not required.
