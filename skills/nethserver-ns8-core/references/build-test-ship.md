# Testing, test nodes and shipping a change

## Test loops

`AGENTS.md` (Test) gives the commands and `docs/core/testing.md` the `run-ns8-tests`
options, variables and tags. Pick the smallest loop that can fail:

1. `core/agent/test-agent.sh`: seconds, no cluster, an ephemeral Redis in Podman.
2. `yarn lint` in `core/ui`: there is no UI unit suite, `package.json` has no test
   script. The real UI cases are Robot cases tagged `ui` in loop 3.
3. `run-ns8-tests`: minutes, a live leader over SSH. Against a provisioned cluster,
   add `--exclude install --exclude uninstall`.

There is no Python linter configuration. Follow the surrounding action scripts.

## Iterating against a test node

This concerns the backend. The UI has its own live loop, in `references/core-ui.md`.

No helper pushes a working tree onto a running node. Every change goes through an
image: `core/build-image.sh`, `buildah push` to a personal tag, then the node.
`docs/quickstart.md` covers `install.sh` with custom images, `podman rmi` of a stale
tag and `cluster/override/modules`.

To re-push a mutable tag onto an existing application instance, use
`update-module <image-url> <instance-id> --force`, same reason as on `update-core`.

## Shipping a change to existing clusters

A new image does not migrate an installed cluster. A new Redis key, a changed grant, a
renamed unit reach existing installations only through an update hook.
`docs/core/updates.md` describes the two stages, the order and the idempotency rule.
Pick the directory by when the change must happen:

| Directory under `core/imageroot` | Stage | Runs on |
|---|---|---|
| `var/lib/nethserver/node/update-core.d/` | 1, after the image is replaced | every node |
| `var/lib/nethserver/cluster/update-core-pre-modules.d/` | 2, before core modules update | leader |
| `var/lib/nethserver/cluster/update-core-post-modules.d/` | 2, after they update | leader |

Traps the docs do not state:

- A hook without the executable bit is skipped, with only a debug-level message.
- A failing hook never stops the update. `cluster/bin/run-scriptdir` exits 1, but its
  caller `update-core/70update_modules` discards that code.
- Scripts come from the new image, so a hook always describes the migration into its
  own version.
- New grants go in `cluster/update-core-pre-modules.d/50update_grants`. The node copy
  has not changed since 2.4.
- A branch tag is not Semver, so it counts as `0.0.0` and `update-core/50update` exits
  before pulling. `docs/core/updates.md` says the update continues. The code wins.
  Without `--force` the pull also skips a tag already in local storage.
- Once a branch tag is installed, it counts as `9999.9999.9999`. Every later update,
  even to a release tag, needs `--force`.

```bash
update-core ghcr.io/nethserver/core:my-branch --force
update-core ghcr.io/nethserver/core:<tag> --nodes 1 2   # discouraged outside development
```

## Developer CLI helpers

The `nethserver-admin` skill documents the cluster-wide commands (`api-cli`,
`runagent`, `volumectl`, `update-core` and the rest). `runagent` is the development one:
it runs a command in an agent's environment, so you can replay a step without building
an image.

```bash
runagent -l                        # which agents are running
runagent -c python3 ./50update     # cluster agent, keep the current directory
runagent -m node -c ./50update     # the node agent
runagent -m <module_id> <command>  # a module agent
```

Without `-c`, `runagent` changes directory to the agent's `AGENT_STATE_DIR` first.
