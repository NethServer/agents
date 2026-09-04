# Core UI

## Calling an action from the core UI

`AGENTS.md` names `createModuleTaskForApp` as an example and moves on. There are in
fact five task services in `@nethserver/ns8-ui-lib`, and picking the wrong one is a
silent mistake: the call reaches the wrong queue, or no queue at all.

| Target agent | Method | POST endpoint | Redis queue |
|---|---|---|---|
| cluster | `createClusterTask(taskData)` | `/cluster/tasks` | `cluster/tasks` |
| node | `createNodeTask(nodeId, taskData)` | `/node/<id>/tasks` | `node/<id>/tasks` |
| module | `createModuleTaskForApp(moduleId, taskData)` | `/module/<id>/tasks` | `module/<id>/tasks` |

The `ForApp` suffix is not about the target, it is about the **caller**. A bare method
reads the API URL from `this.$root.apiUrl`, which only exists in the core shell. A
`ForApp` method reads `window.parent.core.$root.apiUrl`, which is how a module UI
running in an iframe reaches the shell that hosts it. `createClusterTaskForApp` and
`createNodeTaskForApp` are the iframe counterparts of the first two rows.

There is no bare `createModuleTask`. The core UI calls `createModuleTaskForApp`
anyway, and it works because `core/ui/src/main.js` assigns the root Vue instance to
`window.core`: in the top window, `window.parent.core` resolves to itself.

`taskData` is the same shape everywhere:

```js
const eventId = this.getUuid();
this.$root.$once(`${taskAction}-completed-${eventId}`, this.onCompleted);

await this.createClusterTask({
  action: taskAction,
  data: { /* action input, validated against validate-input.json */ },
  extra: {
    title: this.$t("action." + taskAction),
    description: this.$t("common.processing"),
    isNotificationHidden: true,   // omit to let the notification drawer show it
    eventId,
  },
});
```

`data` is what the action step reads from stdin. `extra` never reaches the action; it
drives the notification drawer and the progress bar. Set `isProgressNotified: true`
in `extra` when the action calls `agent.set_progress()`.

## Working on the core UI

`AGENTS.md` says Vue 2 and Carbon, and points at `@nethserver/ns8-ui-lib` for the task
services. Four things it leaves out cost real time.

**The stack is a major generation behind the ecosystem defaults, and writing modern
idioms here produces code that does not build.** Renovate manages npm and gomod with
an automerge preset, so patch and minor numbers move on their own — always read
`core/ui/package.json` for the current pin rather than trusting any number written
down elsewhere, this file included. The generations move rarely, and they are what
changes the code you write:

| Area | Generation in use | Do not reach for |
|---|---|---|
| Vue | 2.x, recent enough for the composition API | Vue 3, or `<script setup>` |
| Router and store | `vue-router` 3, `vuex` 3 | Router 4, Vuex 4, Pinia |
| Design system | Carbon v10 (`carbon-components` 10, `@carbon/vue` 2) | Carbon v11, what the online docs show |
| Build tooling | Vue CLI 4, so webpack | Vite |
| Vue lint rules | `eslint-plugin-vue` 6 | the current rule set |

**ns8-ui-lib is an external package, not a directory of this repository.** It lives at
`NethServer/ns8-ui-lib`, and its components are the ones prefixed `Ns` — `NsButton`,
`NsInlineNotification`. Two facts about it are easy to get wrong.

The published version and the consumed version drift apart on purpose. Every
consumer pins with a caret, and a caret never crosses a major, so a library major
release reaches nobody until each repository bumps it deliberately. The core UI, and
every module repository, sit wherever they were last bumped — in practice they are
spread over several majors at any time. Check all three before assuming a component
or a prop exists:

```bash
grep ns8-ui-lib core/ui/package.json          # what the core UI consumes
npm view @nethserver/ns8-ui-lib version       # what is published
grep ns8-ui-lib <module>/ui/package.json      # what a given module consumes
```

Shipping a library fix does need an upstream release (`npm run publish:patch|minor|major`,
see `docs/ui/library.md`), but *testing* one does not: `npm run build-pack` produces a
tarball that installs straight into this repository with
`yarn add /path/to/nethserver-ns8-ui-lib-x.y.z.tgz`. Use that to validate a change
before releasing it.

**Core UI styling is not local to the core UI.** After the build, `build-image.sh`
runs `tidy` over `dist/index.html`, collects the emitted `app~*.css` chunks and
concatenates them into a single `dist/css/core.css`
(`core/build-image.sh`, under the echo "Provide core style to external modules"). Every
external module UI loads that file. A change to a shared style rule ships to every
module in the cluster, not just to the screen being worked on.

**The build has two constraints that bite locally.** It runs on the Node image pinned
in `core/build-image.sh`, with `NODE_OPTIONS=--openssl-legacy-provider`, which
webpack 4 requires on any recent Node. And `yarn install --immutable` means a
lockfile that drifts from `package.json` fails the build rather than being repaired
silently.

Lint is `plugin:vue/essential` plus `eslint:recommended` and prettier
(`core/ui/.eslintrc.js`). That is the loosest Vue rule set; `yarn lint` passing says
very little about correctness.

### Running the core UI on localhost against a real node

Unlike the backend, the UI has a live loop: a dev server with hot reload on the
workstation, talking to a real leader node. `docs/ui/core.md` has the full procedure,
including the Podman and VS Code Dev Containers variants. Three steps in it are the
ones that block people:

1. Copy `core/ui/public/config/config.development.js.sample` to
   `config.development.js` and set `API_ENDPOINT` and `WS_ENDPOINT` to the leader
   node address.
2. Disable the CORS check on that node, otherwise every request is rejected:

   ```bash
   echo GIN_MODE=debug >> /etc/nethserver/api-server.env
   systemctl restart api-server
   ```

3. Accept the self-signed certificate once, by opening
   `https://<node>/cluster-admin/api/login` in a browser tab. Use the same FQDN or IP
   there as in `config.development.js` — a certificate accepted on the hostname does
   not cover the address, and the requests keep failing.

Then start the dev server. `core/ui/Containerfile` builds the image for it:

```bash
cd core/ui
podman build -t ns8-core-dev .
podman run -ti -v $(pwd):/app:Z --network=host --name ns8-core --replace ns8-core-dev serve
```

`--network=host` is not optional, hot reload does not work without it. Swapping the
trailing `serve` for `build` or `storybook` runs those instead. Running the dev server
and Storybook at the same time is the one combination that needs a different shape,
because a second `yarn` in the same container fails — start `serve` as above, then
attach to the running container:

```bash
podman exec -ti ns8-core yarn storybook
```

A plain `yarn serve` on the workstation and a VS Code Dev Containers setup are the two
other supported paths; `docs/ui/core.md` describes both.

