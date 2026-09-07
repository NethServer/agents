# Platform contracts — read the manual, don't reimplement

The developer manual is generated from the `docs/` tree of `NethServer/ns8-core` and
specifies the platform contracts a module relies on. It is the authority; this skill
only covers what it leaves implicit.

Page `docs/modules/<name>.md` publishes at `https://nethserver.github.io/ns8-core/modules/<name>/`.

| Subject | `<name>` |
|---|---|
| Agent, action protocol | `agent` |
| Backup and restore | `backup_restore` |
| TLS certificates | `certificates` |
| Reusable code snippets | `code_snippets` |
| Database | `database` |
| Images | `images` |
| Metadata | `metadata` |
| Network | `network` |
| New module tutorial, build and deploy loop | `new_module` |
| Port allocation | `port_allocation` |
| Rootless vs rootfull | `rootless_rootfull` |
| Service providers | `service_providers` |
| Systemd units | `systemd_units` |
| Testing | `testing` |
| Updates, `update-module.d/` | `updates` |
| Volumes | `volumes` |
| Community certification | `certification` |
