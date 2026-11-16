#!/usr/bin/env bash
# A NethSecurity flow that shows a success toast for a change that is only staged.
set -euo pipefail
cat > flow.md <<'STRINGS'
# Edit port forward (NethSecurity mockup)

1. On the Port forward page, the user clicks Edit on the row "Web server".
2. The drawer "Edit port forward" opens, with the fields and the buttons Cancel and Save.
3. The user clicks Save. The drawer closes.
4. A green toast appears: "Port forward Web server has been saved successfully!"
5. The change is applied later, when the user clicks "Unsaved changes" in the top bar and then "Apply changes".
STRINGS
