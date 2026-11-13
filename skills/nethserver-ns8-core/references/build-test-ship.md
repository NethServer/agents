# Testing, test nodes and shipping a change

## Test loops

Three loops, with very different costs. Pick the smallest one that can fail.

```bash
# 1. Go agent, seconds, no cluster needed.
#    Builds the binary, starts an ephemeral Podman Redis, runs the Robot suite
#    in core/agent/test/ against fixture actions and events.
cd core/agent && bash test-agent.sh

# 2. UI. There is no unit suite — package.json has no test script. This is a
#    linter, and a loose one. The real UI cases are Robot cases in loop 3.
cd core/ui && yarn lint

# 3. Integration, minutes, requires a live leader node reachable over SSH.
#    run-ns8-tests comes from the external NethServer/ns8-github-actions repo.
#    UI cases are tagged ui and excluded unless RUN_UI_TESTS is set.
cd core && run-ns8-tests <LEADER_NODE> [robot_options]
cd core && RUN_UI_TESTS=true run-ns8-tests <LEADER_NODE>
```

The integration suite reads `SSH_KEYFILE`, `RUN_UI_TESTS` and `COREMODULES` from the
environment. Suites live in numbered directories such as
`core/tests/10__cluster_sanity/`, share `keywords.resource`, and follow the same
numbering discipline as action steps: `00` installs, `99` uninstalls. Use
`--exclude install` and `--exclude uninstall` to iterate against a cluster that is
already provisioned.

Shell code must pass `shellcheck`. There is no Python linter configuration in the
repository; follow the style of the surrounding action scripts.

## Iterating against a test node

This concerns the backend. The UI has its own live loop, in `references/core-ui.md`.

There is no rsync or scp helper that pushes a working tree onto a running node. The
loop goes through a container image:

1. `cd core && bash build-image.sh` — buildah, reusing the persistent
   `gobuilder-core` and `nodebuilder-core` containers for caching.
2. `buildah push` the image to a personal tag on ghcr.io.
3. On the test node, `podman rmi` the tag first if it was already pulled, otherwise
   the old layers are reused.
4. Point the cluster at the new image. For a **core** image, override the resolution
   map:

   ```bash
   redis-cli hset cluster/override/modules <image-name> <image-url>
   # e.g. redis-cli hset cluster/override/modules samba ghcr.io/nethserver/samba:rootless
   ```

   The hash maps an image *name* to a full URL and is read by
   `core/imageroot/var/lib/nethserver/cluster/actions/add-module/50update`. For an
   application module the commands are direct instead: `add-module <image-url>
   <node-id>` for a new instance, `update-module <image-url> <instance-id> --force` to
   re-push a mutable tag onto an existing one — same `--force`, same reason as on
   `update-core`.

`core/install.sh` accepts custom core images as positional arguments, which is the
fastest path when bootstrapping a throwaway node from a branch build.

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
- New grants go in `cluster/update-core-pre-modules.d/50update_grants`. The node copy
  is frozen.
- A branch tag is not Semver, so it counts as `0.0.0` and `update-core/50update` exits
  before pulling. Without `--force` the pull also skips a tag already in local storage.

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
