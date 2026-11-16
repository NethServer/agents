#!/usr/bin/env bash
# Mockup texts whose only mistakes are glossary terms.
set -euo pipefail
cat > security.md <<'STRINGS'
# Security overview (NethSecurity mockup)

- Card title: Threatshield IP
- Card description: Blocks malicious IP addresses on this firewall.
- Card title: Multi-WAN
- Card description: Uses several internet connections of the device together.
- Row action on a blocklist: Remove (it permanently deletes the blocklist)
- Session expired message: Your session has expired. Log in again.
STRINGS
