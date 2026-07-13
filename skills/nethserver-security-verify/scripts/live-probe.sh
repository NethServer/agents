#!/usr/bin/env bash
#
# live-probe.sh — read-only helper for the NS8 security verify stage.
#
# Bundles non-destructive preflight + inventory probes against a live NS8
# leader. Makes NO state changes. For finding-specific probes, use the recipes
# in references/probes.md.
#
# Usage:
#   live-probe.sh preflight            # cluster role, nodes, modules
#   live-probe.sh routes               # exposed routes / ports
#   live-probe.sh xff <leader-host>    # X-Forwarded-For forgery check (1 failed login)
#   live-probe.sh rootless <module_id> # confirm container runs non-root
#
# Requires api-cli (and jq) on the current node; run from/near the leader.

set -euo pipefail

die() { echo "error: $*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"; }

need api-cli

cmd="${1:-preflight}"
shift || true

case "$cmd" in
  preflight)
    need jq
    echo "== cluster status ==" >&2
    api-cli run get-cluster-status | jq '{leader, nodes: (.nodes|keys)}'
    echo "== installed modules ==" >&2
    api-cli run list-installed-modules | jq -r '.[].id'
    ;;

  routes)
    # list-routes may not exist on all versions; fall back gracefully
    api-cli run list-routes 2>/dev/null || \
      echo "note: list-routes unavailable; inspect Traefik config manually" >&2
    ;;

  xff)
    host="${1:-}"; [ -n "$host" ] || die "usage: live-probe.sh xff <leader-host>"
    need curl; need jq
    echo "== single forged-XFF failed login (non-destructive) ==" >&2
    echo "WARNING: confirm no account lockout on user 'sec-probe' before running." >&2
    curl -s -o /dev/null -w 'login http=%{http_code}\n' \
         -H 'X-Forwarded-For: 203.0.113.99' \
         -X POST "https://${host}/api/login" \
         -d '{"username":"sec-probe","password":"wrong-on-purpose"}'
    echo "== audit entries for sec-probe (check recorded IP) ==" >&2
    api-cli run list-audit --data '{"user":"sec-probe"}' 2>/dev/null | jq '.[].ip' || \
      echo "note: adjust audit action name to this version" >&2
    ;;

  rootless)
    mod="${1:-}"; [ -n "$mod" ] || die "usage: live-probe.sh rootless <module_id>"
    echo "== container user for module $mod ==" >&2
    # shellcheck disable=SC2016  # podman Go-template must stay literal for the remote shell
    runagent -m "$mod" bash -c 'podman ps --format "{{.Names}}" | while read -r c; do
        printf "%s user=" "$c"; podman inspect "$c" --format "{{.Config.User}}"; done'
    ;;

  *)
    die "unknown subcommand: $cmd (use preflight|routes|xff|rootless)"
    ;;
esac
