# Backup, restore, volumes, upgrades

## Backup & Restore

### Declaring what to back up (state-include.conf)
`imageroot/etc/state-include.conf` lists paths relative to the module home. Use `state/<file>` for files in `AGENT_STATE_DIR` and `volumes/<name>` for Podman volumes (`<module_id>-<name>` when rootful). `state/environment` is always included automatically.

**Only include files that are NOT provided by the module image.** If a file in `state/` is derived from or identical to a file shipped in `imageroot/` (e.g. `state/initdb.d/init.sql` copied from `imageroot/sql/init.sql`), do NOT back it up — regenerate it during restore instead. Back up only:
- User data volumes (`volumes/myapp-data`)
- SQL/DB dumps (`state/mydb.sql`, `state/mydb.pg_dump`)
- Secrets generated at install time (`state/passwords.env`)
- Any runtime state not reproducible from the image

### Restore sequence
`imageroot/actions/restore-module/` — numbered steps, `10restore` inherited (Restic).

- `06copyenv` — restore env vars from `request['environment']` via `agent.set_env()`
- `40restoreDB` — load SQL dump via ephemeral container (see patterns below)
- `50call-configure-module` — call `configure-module` with restored env vars via `agent.tasks.run()`

> **⚠️ `50call-configure-module` must pass ALL vars restored by `06copyenv`**, not just the Traefik ones.
> `06copyenv` restores every non-secret env var set by `agent.set_env()`.
> Missing any var leaves `configure-module` with wrong/empty defaults.
>
> Pattern — read from `os.environ` (already populated by `06copyenv`), map to `configure-module` input:
> ```python
> agent.tasks.run("module/" + os.environ["MODULE_ID"], action="configure-module", data={
>     "host":      os.environ["TRAEFIK_HOST"],
>     "http2https": os.environ.get("TRAEFIK_HTTP2HTTPS", "false") == "true",
>     # ALL other fields accepted by configure-module — check validate-input.json
> })
> ```
> Read `configure-module/validate-input.json` to enumerate every required/optional field.

### MariaDB
- **Dump** (`imageroot/bin/module-dump-state`, CWD=`state/`): `podman exec mariadb-app mysqldump --databases mydb --default-character-set=utf8mb4 --single-transaction --quick --add-drop-table --skip-dump-date > mydb.sql`
- **Cleanup** (`imageroot/bin/module-cleanup-state`): `rm -vf mydb.sql`
- **Restore** (`40restoreDB`): move `mydb.sql` into `initdb.d/`, add `zz_restore.sh` that calls `docker_temp_server_stop`, launch ephemeral `${MARIADB_IMAGE}` with `--volume=./initdb.d:/docker-entrypoint-initdb.d:z --volume mysql-data:/var/lib/mysql/:Z`. MariaDB entrypoint auto-executes the SQL, then the script stops the container.
- **Reference**: ns8-sogo

`state-include.conf`: `state/mydb.sql` + `volumes/mysql-data`

### PostgreSQL
- **Dump** (`imageroot/bin/module-dump-state`): `podman exec postgres-app pg_dump -U myuser --format=c mydb > mydb.pg_dump` (custom format for `pg_restore`)
- **Cleanup** (`imageroot/bin/module-cleanup-state`): `rm -vf mydb.pg_dump`
- **Restore** (`40restore-postgres`): create `restore/mydb_restore.sh` with `pg_restore --no-owner --no-privileges`, launch ephemeral `${POSTGRES_IMAGE}` with dump **piped via stdin** (`< mydb.pg_dump`), script calls `docker_temp_server_stop` on exit.
- **Reference**: ns8-mattermost

`state-include.conf`: `state/mydb.pg_dump` + `volumes/postgres-data`

### Clone vs restore
- **restore-module**: Restic restores files listed in `etc/state-include.conf` → `40restoreDB` loads SQL dump → `50call-configure-module` reconfigures
- **clone-module**: no Restic restore, no SQL dump — only `50call-configure-module` (fresh DB, env vars from `os.environ` set by clone framework)

Dump/cleanup scripts (`imageroot/bin/module-dump-state`, `imageroot/bin/module-cleanup-state`) only run during backup — not during clone or restore.

### Volume persistence
Named Podman volumes are created automatically on first use — no label required.
Mount in the systemd service:
```
--volume mysql-data:/var/lib/mysql/:Z
--volume postgres-data:/var/lib/postgresql/data:Z
```

### Additional disks
`--label="org.nethserver.volumes=vol1 vol2"` — marks volumes as candidates for additional-disk placement. At install, the UI prompts the sysadmin to assign them to an extra disk (slower but bigger). Without the label, volumes land in Podman default under the module home. Only use for bulk data (DB, mail, media). Assignments in `/etc/nethserver/volumes.conf`, managed via `volumectl`.

### SELinux volume label flags
- `:z` (shared) — volume accessible by multiple containers within the same pod
- `:Z` (private) — volume exclusive to a single container/service

## Upgrade Hooks
Scripts in `imageroot/update-module.d/` run on `update-module` in lexicographic order.
If a script fails, execution continues with the next one — each script is independent.

Recommended layout: `05`-`06` pre-restart migrations, `30restart` (`systemctl --user try-restart`), `50`-`60` post-restart reindex/cleanup.
Version-specific migrations go before `30restart` so the new code starts on updated data.
