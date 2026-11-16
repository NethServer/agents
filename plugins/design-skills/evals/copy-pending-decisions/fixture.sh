#!/usr/bin/env bash
# Mockup texts that look fine by generic rules but break the NDS pending decisions.
set -euo pipefail
cat > contacts.md <<'STRINGS'
# Phonebook contacts (NethVoice mockup)

- Page title: Contacts
- Page header button: Create contact
- Create drawer title: Create contact
- Create drawer buttons: Cancel, Create contact
- Edit drawer buttons: Cancel, Save
- Table column "Status": a yellow badge that says "Expired", a green badge that says "Active"
- Error message when the list can't be loaded: Something went wrong.
STRINGS
