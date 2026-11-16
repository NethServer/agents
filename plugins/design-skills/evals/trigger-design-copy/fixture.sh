#!/usr/bin/env bash
# A list of strings from a mockup, outside any code project.
set -euo pipefail
cat > strings.md <<'STRINGS'
# Firewall rules page (NethSecurity mockup)

- Page title: Firewall Rules
- Button: Add new rule
- Empty state: There are no rules yet!
- Delete modal title: Are you sure you want to delete the rule?
- Delete modal button: Yes
- Toast: The rule was successfully deleted
STRINGS
