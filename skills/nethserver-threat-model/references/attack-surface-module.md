# Attack surface — ns8-<app> module

Reference for threat-modeling an external NS8 application module. A module is a
container-packaged app orchestrated by ns8-core; it does not ship the API
server or agent, but it defines actions, may run `api-moduled`, and exposes
services through Traefik.

## Module layout (typical)

```
<repo>/
  AGENTS.md
  imageroot/
    actions/<action-name>/        # numbered step scripts + validate-*.json
    events/<event-name>/          # event handler scripts
    bin/                          # helper executables
    systemd/                      # module systemd units
  <Containerfile(s)>
  build-images.sh
```

## Entry points

### Actions (`imageroot/actions/<name>/`)
Same model as core: numbered step scripts run by the agent as the **module
user** (rootless). Inputs arrive as JSON on stdin. `validate-input.json`
missing = unvalidated entry point. Actions are invoked via
`api-cli run module/<module_id>/<action>`.

### Events (`imageroot/events/<name>/`)
Triggered by cluster events. Inputs come from the event payload — another
externally-influenced input path; apply the same input-validation checks.

### api-moduled handlers
Some modules (e.g. ns8-samba, ns8-openldap) run `api-moduled` to offer a
self-service portal. Handlers under `handlers/<name>/post` are HTTP-reachable
code-execution points. Same rules as core api-moduled: scope claim, env
injection, command injection.

### Exposed services
- Traefik routes (HTTP/S) — check `set-route` usage and route labels.
- TCP/UDP ports declared for the firewall
  (`org.nethserver.tcp-ports` / `udp-ports`, port allocation via
  `list-ports`/`add-public-service`).

## Privilege model

- Module actions run as the **module user**, rootless (since Core 3.20 rootless
  users may have `/sbin/nologin`; operate via `runagent -m <module_id>`).
- A module may request privileged cluster actions — check for calls that reach
  the leader / privileged Redis (`redis_connect(privileged=True)` if the module
  ships agent Python that runs in a privileged context, or actions that invoke
  cluster-level operations).

## Secrets

- Module secrets typically live in Redis under `module/<module_id>/...` and in
  the module environment file. Check they are never echoed to stdout (task
  output is stored in Redis and visible via the API), never logged, never baked
  into container layers (defer image checks to `nethserver-containerfile`).

## Containers

Rootless, pinned, no-secrets-in-layers. Enumerate `Containerfile`s and their
`FROM`/`USER`/`EXPOSE`, but delegate the actual hardening review to the
`nethserver-containerfile` skill.
