# NS8 diagnostics and reporting

## NS8 support diagnostics

Use these only after the normal NS8 action/log workflow. They encode NS8-specific support knowledge; they are not a generic Linux checklist.

### Node identity and pressure

`/home` is important because rootless module homes and private Podman storage commonly live there.

```bash
# node id and cluster metadata, read-only
cat /var/lib/nethserver/node/state/environment 2>/dev/null | grep -E '^(NODE_ID|IMAGE_URL)=' || true
grep -oP '^AGENT_ID=node/\K[0-9]+' /var/lib/nethserver/node/state/agent.env 2>/dev/null || true
redis-cli --raw get cluster/uuid 2>/dev/null || true
redis-cli --raw hget cluster/subscription system_id 2>/dev/null || true
redis-cli --raw hget node/1/vpn endpoint 2>/dev/null || true
redis-cli --raw KEYS 'node/*/vpn' 2>/dev/null | wc -l

# pressure points that often break NS8 modules
cat /proc/sys/fs/file-nr
findmnt -n -o TARGET --target /home 2>/dev/null; df -h /home 2>/dev/null
pgrep -x sngrep | while read p; do ps -o pid,etimes,cmd -p "$p"; done
```

### Historical metrics with Prometheus

If the incident has already passed and the Metrics module is installed, use
its Prometheus history to compare the affected window with a baseline before
and after it. Resolve the module ID and node from `api-cli run
list-installed-modules`, then confirm the running Prometheus container in that
module's Podman context. The commands below use `metrics1` as an example.

```bash
runagent -m metrics1 podman ps -a
runagent -m metrics1 podman port prometheus
runagent -m metrics1 podman inspect prometheus --format '{{json .Args}}'
runagent -m metrics1 podman exec prometheus promtool --version
```

An empty port listing can mean the listener is available only inside the
container. Use the loopback address and port confirmed by
`--web.listen-address`. This example uses `127.0.0.1:9091`. Inspect only the
needed startup argument and omit other arguments from the incident report.

```bash
runagent -m metrics1 podman exec prometheus promtool query instant http://127.0.0.1:9091 'count by (job) (up)'
runagent -m metrics1 podman exec prometheus promtool query instant http://127.0.0.1:9091 'count by (__name__) ({__name__=~"ns8_container_.*|node_disk_.*_total"})'
runagent -m metrics1 podman exec prometheus promtool query range --start=2026-01-01T10:00:00Z --end=2026-01-01T11:00:00Z --step=60s http://127.0.0.1:9091 '100 * max(rate(node_disk_io_time_seconds_total[3m]))'
runagent -m metrics1 podman exec prometheus promtool query range --start=2026-01-01T10:00:00Z --end=2026-01-01T11:00:00Z --step=60s http://127.0.0.1:9091 'max(rate(ns8_container_blkio_bytes_total{container="mariadb",device="sda",op="read"}[3m]))/1048576'
```

Replace the example interval with the incident timestamps in UTC, and use
the observed container and block-device labels. The third query shows disk
busy time in percent and the fourth shows container reads in MiB/s. Choose
one device layer to avoid counting the same I/O at both the physical disk
and its logical volume. Correlate metrics with access or service logs and
check scrape coverage before interpreting missing samples. If Metrics or the
relevant series are unavailable, continue with logs and the available host
diagnostics. Through Gate, submit each command separately and honor its
approval result.

### Module inventory from Redis, read-only fallback

Use when `api-cli run list-installed-modules` is unavailable or too coarse.

```bash
redis-cli --raw HGETALL cluster/module_node
mid=<module_id>
redis-cli --raw HGET "module/$mid/environment" IMAGE_URL
redis-cli --scan --pattern 'module/*/environment' | while read k; do
  mid=${k#module/}; mid=${mid%/environment}
  img=$(redis-cli --raw HGET "$k" IMAGE_URL 2>/dev/null)
  test -n "$img" && printf '%s\t%s\n' "$mid" "$img"
done | sort
```

### Compact container and unit health

This is higher signal than plain `podman ps` because it exposes restarts and non-failed dead units.

```bash
mid=<module_id>
runagent -m $mid podman ps -a --format '{{.Names}} [Status:{{.Status}}] [Restarts:{{.Restarts}}]'
runagent -m $mid systemctl --user --failed --no-legend --no-pager || true
runagent -m $mid systemctl --user list-units --type=service --no-legend --no-pager \
  | awk '$3 == "inactive" || $4 == "dead" {print}'
```

For all modules on the local node:

```bash
api-cli run list-installed-modules | jq -r '..|objects|select(has("id"))|.id' | sort -u | while read mid; do
  echo "== $mid =="
  runagent -m "$mid" podman ps -a --format '{{.Names}} [Status:{{.Status}}] [Restarts:{{.Restarts}}]' 2>/dev/null || true
  runagent -m "$mid" systemctl --user --failed --no-legend --no-pager 2>/dev/null || true
done
```

### TLS endpoint certificate check

Use for Traefik routes, NethVoice HTTPS, and SIP/TLS endpoints.

```bash
host=<fqdn>; port=443
cert=$(mktemp)
timeout 8 openssl s_client -connect "$host:$port" -servername "$host" -showcerts </dev/null 2>&1 \
  | awk '/-----BEGIN CERTIFICATE-----/{c=1} c{print} /-----END CERTIFICATE-----/{exit}' > "$cert"
openssl x509 -in "$cert" -noout
openssl x509 -in "$cert" -noout -checkhost "$host"
openssl x509 -in "$cert" -noout -checkend 0
rm -f "$cert"
```

### Severe host log patterns

Use as a quick high-signal scan before deep module debugging.

```bash
grep -E -i -m 20 'kernel panic|panic not syncing|BUG:|Oops:|general protection fault|segfault|core dumped|Out of memory:|oom-kill|soft lockup|hard LOCKUP|rcu.*stall|blocked for more than|I/O error|EXT4-fs error|Remounting filesystem read-only|XFS .*shutdown|NETDEV WATCHDOG|emergency mode|FATAL:' /var/log/messages 2>/dev/null || true
```

## Troubleshooting sequence

1. Verify target: host, user, OS, cluster status.
2. Identify module ID and node: `list-installed-modules`.
3. List actions; check `get-configuration` and `get-status`.
4. Resolve `AGENT_INSTALL_DIR` and `AGENT_STATE_DIR` with `runagent`.
5. Detect rootless/rootfull; inspect the correct systemd and Podman context.
6. Read module logs with `api-server-logs`, `logcli`, then journal/container logs.
7. Inspect routes/certs for web apps.
8. Inspect service providers, user-domain binding, events, or firewall only when relevant.
9. Change via supported action or helper command.
10. Verify state, logs, containers, routes, and audit record.

Minimal incident bundle:

```bash
mid=<module_id>
hostnamectl --static; id; cat /etc/os-release | sed -n '1,8p'
api-cli run get-cluster-status | jq .
api-cli run list-installed-modules | jq .
api-cli run module/$mid/list-actions | jq . || true
api-cli run module/$mid/get-configuration | jq . || true
api-cli run module/$mid/get-status | jq . || true
runagent -m $mid sh -lc 'id; echo "$AGENT_INSTALL_DIR"; echo "$AGENT_STATE_DIR"; if [ "$(id -u)" = 0 ]; then systemctl list-units --all "${MODULE_ID:-$mid}*" --no-pager 2>/dev/null || true; podman ps -a 2>/dev/null || true; else systemctl --user list-units --all --no-pager 2>/dev/null || true; podman ps -a 2>/dev/null || true; fi'
api-server-logs logs -e module -n $mid || true
```

## Report format

- Target: host, user, local/SSH, node ID, module ID.
- Findings: confirmed facts only.
- Actions run: exact commands/actions and payloads.
- Changes made: install/update/config/restart/remove, or none.
- Verification: command output proving result.
- Remaining risk: unknowns, degraded components, destructive actions avoided.

