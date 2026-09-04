# Frontend: Vue 2 UI

## Stack & Vuex
Vue 2.6, Vuex, Vue Router, IBM Carbon Design System, `@nethserver/ns8-ui-lib`.
Views: `ui/src/views/` — Components: `ui/src/components/`

```javascript
import { mapState } from "vuex";
import { TaskService, UtilService, IconService, StorageService, QueryParamService, PageTitleService, DateTimeService } from "@nethserver/ns8-ui-lib";
export default {
  mixins: [TaskService, UtilService, IconService, QueryParamService, PageTitleService], // add StorageService, DateTimeService, LottieService if needed
  computed: { ...mapState(["instanceName", "core", "appName"]) },
}
```

- `core` = parent NS8 shell Vue instance (iframe). `this.core.$root.$once(...)`.
- `instanceName` = module ID e.g. `imapsync1`. Auto-extracted from URL by App.vue.
- Routes: `status` (default `/`), `settings`, `tasks`, `about`. Navigate: `this.goToAppPage(this.instanceName, "settings")` (UtilService) — NOT `this.$router.push()`.
- **Before writing utility code, check `ns8-ui-lib/src/lib-mixins/`** — all already importable.

| Mixin | Key methods |
|---|---|
| `TaskService` | `createModuleTaskForApp()`, `createNodeTaskForApp()`, `createErrorNotificationForApp()`, `createNotificationForApp()`, `getTaskStatus()`, `getTaskKind()` |
| `UtilService` | `getErrorMessage()`, `clearErrors()`, `focusElement()`, `goToAppPage()`, `getUuid()`, `sortByProperty(prop)`, `isJson(s)`, `tryParseJson(s)` |
| `DateTimeService` | `formatDate` (date-fns), `formatDateDistance`, `parseIsoDate`, `dateIsBefore`, `formatInTimeZone(date,fmt,tz)` |
| `StorageService` | `getFromStorage("myKey")` → object\|null, `saveToStorage("myKey", obj)`, `deleteFromStorage("myKey")` — localStorage wrappers keyed per module instance. Do NOT use `localStorage` directly. |
| `QueryParamService` | `queryParamsToDataForApp()`, `watchQueryData()` — sync URL params ↔ data |
| `IconService` | **~150 icons in `data()` — NEVER import manually without checking `ns8-ui-lib/src/lib-mixins/icon.js` first.** Use as `:icon="Save20"` directly. Available (partial list): `Save20` `TrashCan20` `Edit20` `Add20` `Close20` `Search20` `Settings20` `Information16` `Information20` `CheckmarkFilled20` `ErrorFilled20` `Warning20` `WarningAlt20` `Restart20` `Download20` `ArrowRight20` `ChevronDown20` `ChevronUp20` `ChevronLeft20` `ChevronRight20` `ArrowDown20` `Rocket20` `Power20` `Password20` `Checkmark20` `Reset20` `Launch20` `Link20` `Upgrade20` `Tools20` `Document20` `Folder20` `User20` `Group20` `Filter20` `Time20` `Hourglass20` `DataBase20` `DataBackup20` `Certificate20` `Firewall20` `Router20` `Catalog20` `Events20` `Email20` `Locked20` `OverflowMenuVertical20` `ZoomIn20` `CloudUpload20` |
| `PageTitleService` | Sets browser tab title |
| `LottieService` | Lottie helpers |

## Action call pattern

```javascript
import { to } from "await-to-js";

data: () => ({
  loading: { getConfiguration: false, configureModule: false },
  error:   { getConfiguration: "", configureModule: "", myField: "" },
  myField: "",
}),

created() { this.getConfiguration(); },

async getConfiguration() {
  this.loading.getConfiguration = true;
  const eventId = this.getUuid();
  this.core.$root.$once(`get-configuration-completed-${eventId}`, this.getConfigurationCompleted);
  this.core.$root.$once(`get-configuration-aborted-${eventId}`,   this.getConfigurationAborted);
  const res = await to(this.createModuleTaskForApp(this.instanceName, {
    action: "get-configuration",
    extra: { title: this.$t("action.get-configuration"), isNotificationHidden: true, eventId },
  }));
  if (res[0]) { this.error.getConfiguration = this.getErrorMessage(res[0]); this.loading.getConfiguration = false; }
},
getConfigurationCompleted(taskContext, taskResult) {
  this.myField = taskResult.output.my_field;
  this.loading.getConfiguration = false;
},

async configureModule() {
  if (!this.validateConfigureModule()) return;
  this.loading.configureModule = true;
  const eventId = this.getUuid();
  this.core.$root.$once(`configure-module-validation-failed-${eventId}`, this.configureModuleValidationFailed);
  this.core.$root.$once(`configure-module-completed-${eventId}`,         this.configureModuleCompleted);
  this.core.$root.$once(`configure-module-aborted-${eventId}`,           this.configureModuleAborted);
  const res = await to(this.createModuleTaskForApp(this.instanceName, {
    action: "configure-module",
    data: { my_field: this.myField },
    extra: { title: this.$t("settings.configuring"), eventId },
  }));
  if (res[0]) { this.error.configureModule = this.getErrorMessage(res[0]); this.loading.configureModule = false; }
},

validateConfigureModule() {
  this.clearErrors(this);
  if (!this.myField) { this.error.myField = "common.required"; this.focusElement("myField"); return false; }
  return true;
},
configureModuleAborted(taskResult, taskContext) {
  console.error(`${taskContext.action} aborted`, taskResult);
  this.error.configureModule = this.$t("error.generic_error");
  this.loading.configureModule = false;
},
configureModuleCompleted(taskContext, taskResult) {
  this.loading.configureModule = false;
  // apply taskResult.output if needed
},
configureModuleValidationFailed(validationErrors) {
  this.loading.configureModule = false;
  for (const e of validationErrors) { this.error[e.parameter] = this.$t("settings." + e.error); }
  this.focusElement(validationErrors[0].parameter);
},
```

Backend validation payload: `[{field, parameter, value, error}]` — `parameter` maps to `error` object key.

## Task progress

Add `isProgressNotified: true` in `extra`, use `$on` (not `$once`) for repeated events.
Unregister in **all terminal states** (completed, aborted, validation-failed):

```javascript
this.myProgress = 0;
this.core.$root.$on(`${taskAction}-progress-${eventId}`, this.myActionProgressUpdated);
// extra: { ..., isProgressNotified: true, eventId }
// in every terminal callback:
this.core.$root.$off(`${taskContext.action}-progress-${taskContext.extra.eventId}`);
// progress handler:
myActionProgressUpdated(progress) { this.myProgress = progress; }, // 0-100
```

```html
<NsProgressBar :value="myProgress" :indeterminate="!myProgress" />
```

Both sides required: backend `agent.set_progress(0-100)` + frontend `isProgressNotified: true`. See the Backend § Agent SDK above.

## Template

For icons not in `IconService`, import manually: `import Play20 from "@carbon/icons-vue/es/play--outline/20"` + `components: { Play20 }`.
Pattern: `@carbon/icons-vue/es/<kebab-name>/<size>`. Variants use double dash: `play--outline`, `add--alt`.

```html
<cv-form @submit.prevent="configureModule">
  <NsTextInput v-model.trim="myField" :label="$t('s.label')" ref="myField"
    :invalid-message="$t(error.myField)" :disabled="loading.configureModule" />

  <NsComboBox v-model.trim="myField" :title="$t('s.title')" :label="$t('s.placeholder')"
    :options="list" :invalid-message="$t(error.myField)" ref="myField"
    :disabled="loading.getConfiguration || loading.configureModule" />

  <NsButton kind="primary" :icon="Save20" :loading="loading.configureModule"
    :disabled="loading.getConfiguration || loading.configureModule">
    {{ $t("settings.save") }}
  </NsButton>

  <NsInlineNotification v-if="error.configureModule" kind="error"
    :title="$t('action.configure-module')" :description="error.configureModule" :showCloseButton="false" />
</cv-form>
```

`ref="myField"` must match `focusElement("myField")`.

## ns8-ui-lib components

> **⚠️ COMPONENT PRIORITY — strictly enforced:**
> 1. **Use `Ns*` (ns8-ui-lib) first.** Check the list below before anything else.
> 2. **Only use `cv-*` (Carbon Vue) if no `Ns*` equivalent exists.**
> Never use `cv-slider`, `cv-toggle`, `cv-text-input`, etc. when `NsSlider`, `NsToggle`, `NsTextInput` exist.
> Wrong: `<cv-slider>` — Correct: `<NsSlider>`

Source: `github.com/NethServer/ns8-ui-lib` — read `src/lib-components/<Name>.vue` for props.

`NsButton` `NsTextInput` `NsPasswordInput` `NsComboBox` `NsComboSearchBox` `NsMultiSelect`
`NsToggle` `NsCheckbox` `NsSlider` `NsByteSlider` `NsTimePicker` `NsModal` `NsDangerDeleteModal`
`NsInlineNotification` `NsToastNotification` `NsDataTable` `NsPagination` `NsEmptyState`
`NsStatusCard` `NsInfoCard` `NsTile` `NsTabs` `NsProgress` `NsProgressBar`
`NsSystemdServiceCard` `NsSystemLogsCard` `NsWizard` `NsCodeSnippet` `NsTag`

**Vue filters** (global, no import): `{{ n | byteFormat }}` `{{ n | humanFormat }}` `{{ n | mibFormat }}` `{{ n | gibFormat }}` `{{ s | secondsFormat }}` `{{ s | secondsLongFormat }}`. Source: `ns8-ui-lib/src/lib-filters/filters.js`.

**NsWizard** props: `visible`, `isLastStep` (Next→Finish), `isNextLoading`, `isNextDisabled`, `isPreviousShown`, `isCancelShown`. Slots: `#title` `#content`. Events: `@cancel` `@previousStep` `@nextStep`.

```html
<NsWizard :visible="isWizardVisible" :isLastStep="currentStep === steps.length - 1"
  :isNextLoading="loading.nextStep" @cancel="isWizardVisible = false"
  @previousStep="currentStep--" @nextStep="handleNextStep">
  <template #title>{{ $t("wizard.title") }}</template>
  <template #content><!-- step content --></template>
</NsWizard>
```

## Translations

**ONLY edit `ui/public/i18n/en/translation.json`.**
All other language files (`fr/`, `it/`, `de/`, etc.) are auto-generated by Renovate — never touch them manually.
If you add or rename a key, add/rename it in `en/translation.json` only. Do NOT create or modify any other `translation.json`.
