# CrowdSec diagnostics

## CrowdSec diagnostics

Use when local/cluster clients cannot reach services and a CrowdSec module exists.

```bash
cs=<crowdsec_module_id>
container=$(runagent -m $cs podman ps --format '{{.Names}}' | grep -i crowdsec | head -1)
ip -o addr show | awk '{print $4}' | cut -d/ -f1 | grep -Ev '^(127\.|::1$)' | sort -u | while read ip; do
  echo "== $ip =="
  runagent -m $cs podman exec "$container" cscli decisions list -i "$ip" -o raw 2>/dev/null || true
done
```

