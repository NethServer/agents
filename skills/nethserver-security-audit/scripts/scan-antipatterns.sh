#!/usr/bin/env bash
#
# scan-antipatterns.sh — deterministic recall floor for the NS8 security audit.
#
# Emits candidate file:line leads for the audit stage to INVESTIGATE.
# A hit is NOT a finding. It is a place to go read the code. Absence of hits
# is NOT proof of safety — the LLM audit covers what grep cannot.
#
# Usage: scan-antipatterns.sh <target-dir>
# Output: grouped file:line matches on stdout; diagnostics on stderr.

set -euo pipefail

TARGET="${1:-.}"
if [ ! -d "$TARGET" ]; then
    echo "error: target dir not found: $TARGET" >&2
    exit 1
fi

# Directories that are never part of the audited source (vendored deps, build
# output, VCS, generated docs). Excluded from every search.
EXCLUDES=(.git node_modules vendor dist build builds .venv __pycache__ docs/vendor)

# Prefer ripgrep; fall back to grep -r.
if command -v rg >/dev/null 2>&1; then
    RG_GLOBS=()
    for e in "${EXCLUDES[@]}"; do RG_GLOBS+=(--glob "!**/$e/**"); done
    SEARCH() { rg -n --no-heading -S "${RG_GLOBS[@]}" "$1" "$TARGET" 2>/dev/null || true; }
else
    echo "note: ripgrep not found, falling back to grep -rn" >&2
    GREP_EXCL=()
    for e in "${EXCLUDES[@]}"; do GREP_EXCL+=(--exclude-dir "$(basename "$e")"); done
    SEARCH() { grep -rniE "${GREP_EXCL[@]}" "$1" "$TARGET" 2>/dev/null || true; }
fi

# Prune predicate for the find-based schema-coverage check below.
prune_expr=()
for e in "${EXCLUDES[@]}"; do prune_expr+=(-path "*/$e/*" -o); done

section() {
    echo
    echo "### $1"
}

echo "# NS8 anti-pattern scan: $TARGET"
echo "# Leads only. Read the code before reporting anything as a finding."

section "action-input: shell/command execution sinks"
SEARCH 'shell\s*=\s*True'
SEARCH 'os\.(system|popen)'
SEARCH '\beval\b'
SEARCH 'subprocess\.(run|call|Popen|check_output)'

section "action-input: agent helper / task exec with possible interpolation"
SEARCH 'run_helper'
SEARCH 'tasks\.(run|runp)'
SEARCH 'AGENT_COMMAND'

section "redis-privilege: privileged connections"
SEARCH 'redis_connect\([^)]*privileged\s*=\s*True'
SEARCH 'privileged\s*=\s*True'

section "auth: authorization / JWT handling (api-server)"
SEARCH 'SetTrustedProxies'
SEARCH 'filepath\.Match'
SEARCH 'Method\s*==\s*"GET"'
SEARCH 'TrustedPlatform|X-Forwarded-For|X-Real-IP|X-Forwarded-Host'

section "api-moduled: scope / secret / env"
SEARCH 'AMLD_JWT_SECRET'
SEARCH 'AMLD_EXPORT_ENV'
SEARCH '"scope"'

section "secrets: hardcoded credential candidates"
SEARCH '(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["'"'"'][^"'"'"']{6,}'
SEARCH 'BEGIN [A-Z ]*PRIVATE KEY'

section "secrets: potential leak to stdout in shell (diagnostics not to stderr)"
SEARCH 'echo .*(password|secret|token|key)'

section "input-validation coverage: actions/handlers missing validate-input.json"
# List action/handler dirs that have step scripts but no validate-input.json.
while IFS= read -r d; do
    if [ -d "$d" ] && [ ! -f "$d/validate-input.json" ]; then
        # only report dirs that actually contain executables/steps
        if find "$d" -maxdepth 1 -type f | grep -q .; then
            echo "$d: no validate-input.json"
        fi
    fi
done < <(find "$TARGET" \( "${prune_expr[@]}" -false \) -prune -o \
              -type d \( -path '*/actions/*' -o -path '*/handlers/*' \) -print 2>/dev/null)

echo
echo "# end of scan"
