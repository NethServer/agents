# Core UI

## Calling an action from the core UI

`@nethserver/ns8-ui-lib` has five task services. The wrong one sends the call to the
wrong queue, or to none, without any error.

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

`AGENTS.md` says Vue 2 and Carbon. Four things it leaves out:

**The stack is a major generation behind the ecosystem defaults.** Modern idioms do not
build. Renovate moves patch and minor versions, so read `core/ui/package.json` for the
current pins. The generations are what matter:

| Area | Generation in use | Do not reach for |
|---|---|---|
| Vue | 2.x, recent enough for the composition API | Vue 3, or `<script setup>` |
| Router and store | `vue-router` 3, `vuex` 3 | Router 4, Vuex 4, Pinia |
| Design system | Carbon v10 (`carbon-components` 10, `@carbon/vue` 2) | Carbon v11, what the online docs show |
| Build tooling | Vue CLI 4, so webpack | Vite |
| Vue lint rules | `eslint-plugin-vue` 6 | the current rule set |

**ns8-ui-lib is an external package**, `NethServer/ns8-ui-lib`, with the `Ns*`
components. Its Storybook is at `https://nethserver.github.io/ns8-ui-lib/`. Consumers
pin with a caret, so a library major reaches nobody until each repository bumps it. The
core UI and the modules sit on different majors. Check before assuming a prop exists:

```bash
grep ns8-ui-lib core/ui/package.json          # what the core UI consumes
npm view @nethserver/ns8-ui-lib version       # what is published
grep ns8-ui-lib <module>/ui/package.json      # what a given module consumes
```

To test a library change before releasing it, install a `npm run build-pack` tarball
(`docs/ui/library.md`).

**Core UI styling is not local to the core UI.** `core/build-image.sh` concatenates the
`app~*.css` chunks into `dist/css/core.css`, and every module UI loads it. A shared style
change ships to every module in the cluster.

**The build has two local traps.** Webpack 4 needs
`NODE_OPTIONS=--openssl-legacy-provider` on a recent Node. `yarn install --immutable`
fails when the lockfile drifts from `package.json`. `yarn lint` uses the loosest Vue
rule set (`core/ui/.eslintrc.js`) and proves little.

### Running the core UI on localhost against a real node

`docs/ui/core.md` has the procedure. Two details people miss there: accept the
self-signed certificate on the same FQDN or IP as in `config.development.js`, and keep
`--network=host` or hot reload stops working.
