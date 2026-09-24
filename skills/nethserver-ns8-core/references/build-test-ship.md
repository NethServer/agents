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

Building an image and installing it on a throwaway node proves the code runs. It does
not migrate a cluster that is already installed. A new Redis key, a changed grant, a
renamed unit: none of it reaches an existing installation unless an update hook does
it. This is the part `AGENTS.md` does not mention at all, and `docs/core/updates.md`
is the reference.

`update-core ghcr.io/nethserver/core:<tag>` runs in two stages. The first updates the
core image on every node; the second lets the leader update the core modules. Three
hook directories are executed along the way, and the one to pick depends on when the
change has to happen:

| Directory under `core/imageroot` | Stage | Runs on |
|---|---|---|
| `var/lib/nethserver/node/update-core.d/` | 1, after the image is replaced | every node |
| `var/lib/nethserver/cluster/update-core-pre-modules.d/` | 2, before core modules update | leader |
| `var/lib/nethserver/cluster/update-core-post-modules.d/` | 2, after they update | leader |

Five rules govern those scripts, and the first two are the ones that bite:

- A file without the executable bit is **skipped**, and the message saying so is
  emitted at debug severity. A hook committed without `chmod +x` never runs and
  nothing visible says why.
- They run in alphabetical order, which is why the existing ones are numbered
  (`05set_agentenv_path`, `10reload_agents`, `50update_grants`, `95cleanup_images`).
- A non-zero exit prints a warning and execution **continues** with the next script.
  This is the opposite of an action, where a non-zero step aborts the sequence. A hook
  cannot stop a bad update; it can only decline to make things worse. The two runners
  reach that outcome differently: the node loop in `update-core/60run_scriptdir` never
  tracks failures, while `cluster/bin/run-scriptdir` counts them and exits 1 — a code
  its only caller, `update-core/70update_modules`, then discards. Reading the cluster
  runner alone suggests failures propagate. They do not.
- A hook can be run **more than once**, so it must be idempotent. Write it to converge
  on the desired state, never to apply a delta.
- The scripts come from the newly installed image, not the one being replaced. A hook
  therefore always describes the migration *into* its own version.

Read the existing hooks before writing one. `50update_grants` exists on both the node
and the cluster side and is a good model for a converging script.

Two details of the first stage matter during development. The node compares the image
tag with the installed one as Semver and installs only if it is greater. A tag that is
not valid Semver — a branch name — does not merely lose that comparison, it is
assigned `0.0.0` as the incoming version while a non-Semver *installed* tag is
assigned `9999.9999.9999`, so `update-core/50update` exits before pulling anything.
That comparison, not the pull, is what stops a branch build. Below it sits a second
effect in the same direction: without `--force` the pull runs through
`podman-pull-missing`, which fetches only a tag absent from local storage. Hence
`--force`, and hence a branch tag that appears to do nothing:

```bash
update-core ghcr.io/nethserver/core:my-branch --force
update-core ghcr.io/nethserver/core:<tag> --nodes 1 2   # discouraged outside development
```

Additional images listed in the core image label `org.nethserver.images` are pulled
along with it. And if the first stage fails on any node, the leader aborts the whole
update before the second stage begins.

## Developer CLI helpers

`core/imageroot/usr/local/bin/` and `usr/local/sbin/` install the cluster-wide
commands — `api-cli`, `runagent`, `volumectl`, `acl-load`, `switch-leader`,
`update-core`, `grant-actions` and the rest. The `nethserver-admin` skill documents
them from the operator's side; use it rather than rediscovering them here.

One of them is a development tool more than an operational one. `runagent` executes a
command inside an agent's environment, with that agent's `AGENT_ID`, `REDIS_USER`,
`PATH` and working directory already set:

```bash
runagent -l                       # which agents are running
runagent python3 ./50update       # -m defaults to cluster
runagent -m node ./50update       # the node agent
runagent -m <module_id> <command> # a module agent
```

It changes directory to that agent's `AGENT_STATE_DIR` first; `-c` keeps the current
directory instead, which is what you want when replaying a step straight out of a
source tree. That is how a single action step gets exercised by hand while it is being
written, without building and pushing an image.

