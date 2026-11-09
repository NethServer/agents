# Backup, restore, volumes, upgrades

## Backup & Restore

### Declaring what to back up (state-include.conf)
`imageroot/etc/state-include.conf` lists paths relative to the module home. Use `state/<file>` for files in `AGENT_STATE_DIR` and `volumes/<name>` for Podman volumes (`<module_id>-<name>` when rootful). `state/environment` is always included automatically.

**Only include files that are NOT provided by the module image.** If a file in `state/` is derived from or identical to a file shipped in `imageroot/` (e.g. `state/initdb.d/init.sql` copied from `imageroot/sql/init.sql`), do NOT back it up — regenerate it during restore instead. Back up only:
- User data volumes (`volumes/myapp-data`)
- SQL/DB dumps (`state/mydb.sql`, `state/mydb.pg_dump`)
- Secrets generated at install time (`state/secrets/`)
- Any runtime state not reproducible from the image

### Excluding files (state-exclude.conf)
`imageroot/etc/state-exclude.conf` — paths to skip, same relative paths as `state-include.conf`, passed to restic as `--exclude-file`. Use it to drop files from an included volume, e.g. caches, temp files, or live DB files already saved by a dump in `module-dump-state`:
```
volumes/myapp-data/cache
volumes/myapp-data/app.db*
```

### Restore sequence
`imageroot/actions/restore-module/` — numbered steps, `10restore` inherited (Restic).

- `06copyenv` — restore the env vars the module needs from `request['environment']` via `agent.set_env()`
- `40restoreDB` — load SQL dump via ephemeral container (see patterns below)
- `50...` — call `configure-module` via `agent.tasks.run()`. The name varies:
  `50traefik`, `50configure`, `50call-configure-module`.

> **⚠️ The `configure-module` call must pass every field it needs**, read from the restored
> environment. Missing fields fall back to empty or default values and silently reset the
> admin's settings. Read `configure-module/validate-input.json` to list them.
>
> ```python
> renv = json.load(sys.stdin)['environment']
> ret = agent.tasks.run(agent_id=os.environ['AGENT_ID'], action='configure-module', data={
>     "host": renv["TRAEFIK_HOST"],
>     "http2https": renv["TRAEFIK_HTTP2HTTPS"] == "True",
>     # every other configure-module field
> })
> agent.assert_exp(ret['exit_code'] == 0, "configure-module failed")
> ```
> `agent.set_env()` stores booleans as `"True"`/`"False"`. Compare with `== "True"`.

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
- **restore-module**: Restic restores files listed in `etc/state-include.conf` → `40restoreDB` loads SQL dump → a `50...` step calls `configure-module`.
- **clone-module**: core copies the whole `state/` directory and every volume by rsync
  from the source, live data included. No restic, no SQL dump. The source services stop
  during the copy (rootless modules, through `transfer-state.target`). Env vars missing
  on the destination are imported from the source. The module's own `50...` step then
  calls `configure-module` with values from `os.environ`.

On clone, the request field `replace` tells whether the source is removed. When it is
`false`, the source still owns its host name. Do not register the same route twice:
ns8-discourse skips its route and asks the admin for a new host.

To skip files during the copy, add `imageroot/etc/state-filter-rules.rsync` (rsync filter
syntax). See the manual page `clone_module`.

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

Recommended layout: `05`-`10` pre-restart migrations, `20restart` (`systemctl --user try-restart`), `50`-`60` post-restart reindex/cleanup.
Version-specific migrations go before the restart step so the new code starts on updated data.
