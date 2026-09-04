# NethVoice diagnostics

## NethVoice diagnostics

Use only when a local `nethvoice`, `nethvoice-proxy`, `nethcti`, `phonebook`, or `satellite` module is involved.

Find related modules:

```bash
api-cli run list-installed-modules | jq -r '..|objects|select(.id? and (.id|test("nethvoice|nethcti|phonebook|satellite")))|.id' | sort -u
redis-cli --scan --pattern 'module/*/environment' | while read k; do
  mid=${k#module/}; mid=${mid%/environment}
  img=$(redis-cli --raw HGET "$k" IMAGE_URL 2>/dev/null)
  echo "$mid $img"
done | grep -E 'nethvoice|nethcti|phonebook|satellite'
```

### FreePBX/container checks

```bash
nv=<nethvoice_module_id>
runagent -m $nv podman exec freepbx getent hosts ibm.com
runagent -m $nv podman exec freepbx cat /etc/resolv.conf
runagent -m $nv podman exec mariadb sh -c 'mysqlcheck -uroot -p${MARIADB_ROOT_PASSWORD} -A'
runagent -m $nv podman exec mariadb sh -c 'mysql -uroot -p${MARIADB_ROOT_PASSWORD} -N -B asterisk -e "SELECT `key`, val, type, id FROM kvstore_Sipsettings WHERE `key` = '\''localnets'\'';"'
runagent -m $nv podman exec freepbx sh -c 'printenv SMTP_FROM_ADDRESS; grep -E "^[[:space:]]*mailcmd[[:space:]]*=" /etc/asterisk/voicemail.conf 2>/dev/null | grep -F -- "send_email -f " || true'
```

### Asterisk state

```bash
nv=<nethvoice_module_id>
runagent -m $nv podman exec freepbx pgrep asterisk
runagent -m $nv podman exec freepbx asterisk -rx 'pjsip show contacts'
runagent -m $nv podman exec freepbx asterisk -rx 'pjsip show transports'
runagent -m $nv podman exec freepbx asterisk -rx 'database show AMPUSER' | grep -F '/AMPUSER//cidname' || true
runagent -m $nv podman exec freepbx asterisk -rx 'database show CF'
runagent -m $nv podman exec freepbx asterisk -rx 'queue show'
```

Interpretation hints:

- `/AMPUSER//cidname` is a bad empty-extension AstDB entry; remove from Asterisk CLI only when confirmed: `database del AMPUSER/ cidname`.
- `database show CF` exposes call forwards; check for loops such as `200 -> 201 -> 200`.
- Many `ringall` queues, or a `ringall` queue with many agents, can amplify call load.
- Asterisk should normally not listen directly on public `5060`/`5061`; Kamailio/proxy owns those ports.

### Asterisk full log high-signal scan

```bash
nv=<nethvoice_module_id>
runagent -m $nv podman exec freepbx sh -lc '
patterns="Too many open files|Cannot create socket|Channel allocation failed|Unable to create channel of type|we couldn'"'"'t allocate a port for RTP instance|No RTP engine was found|failed to setup RTP instance|RTP no remote address on instance|Unable to allocate RTP socket|Couldn'"'"'t negotiate stream|No translator path exists|Failed to create srtp session|SRTP (protect|unprotect)|Is endpoint registered and reachable"
grep -E -i -m 20 "$patterns" /var/log/asterisk/full 2>/dev/null || true
for f in /var/log/asterisk/full.*.gz; do test -e "$f" && gzip -cd "$f" | grep -E -i -m 20 "$patterns"; done
'
```

### NethVoice proxy route consistency

A local `nethvoice-proxy` should route each `NETHVOICE_HOST` to `sip:<wg0 IPv4>:<ASTERISK_SIP_PORT>`.

```bash
proxy=<nethvoice_proxy_module_id>
runagent -m $proxy podman exec -i postgres sh -lc '
psql -U "$POSTGRES_USER" "$POSTGRES_DB" <<SQL
COPY (
  SELECT r.target AS domain, d.destination AS uri
  FROM nethvoice_proxy_routes r
  JOIN dispatcher d ON d.setid = r.setid
  WHERE r.route_type = '\''domain'\''
  ORDER BY r.target, d.destination
) TO STDOUT WITH CSV HEADER;
SQL
'

nv=<nethvoice_module_id>
runagent -m $nv sh -lc 'grep -E "^(NETHVOICE_HOST|ASTERISK_SIP_PORT)=" "$AGENT_STATE_DIR/environment"'
ip -o -4 addr show dev wg0 | awk '{print $4}' | cut -d/ -f1 | head -1
```

### Hairpin NAT probes for SIP/NethVoice

Use only when public-IP SIP reachability from inside the LAN matters.

```bash
public_ip=$(curl -4 -fsS --max-time 5 https://api64.ipify.org || curl -4 -fsS --max-time 5 https://ipv4.icanhazip.com)
ip route get "$public_ip"
timeout 6 openssl s_client -connect "$public_ip:5061" -brief </dev/null
```

For UDP/TCP SIP hairpin, send a minimal `OPTIONS` request to `$public_ip:5060`; ensure `ss` first shows port `5060` owned by `kamailio`.

