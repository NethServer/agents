# @nethesis/vue-components API reference (v3.16.0)

Auto-generated from the component sources by `scripts/extract_api.py`. Props, emits, models and slots are copied verbatim. Comments are stripped.

## Table of contents

- NeSkeleton
- NeSpinner
- NeExpandable
- NeProgressBar
- NeFileInput
- NeInlineNotification
- NeRoundedIcon
- NeSideDrawer
- NeTooltip
- NeBadge (deprecated)
- NeButton
- NeCheckbox
- NeTable
- NeTableHead
- NeTableHeadCell
- NeTableBody
- NeTableRow
- NeTableCell
- NeCombobox
- NeMultiselectCombobox
- NeDropdown
- NeCard
- NeLink
- NeFormItemLabel
- NeRadioSelection
- NeCheckboxCards
- NePaginator
- NeEmptyState
- NeTabs
- NeTextArea
- NeTextInput
- NeToggle
- NeToastNotification (deprecated)
- NeModal
- NeHeading
- NeListbox
- NeDropdownFilter (deprecated)
- NeDropdownFilterV2
- NeSortDropdown
- NeAvatar
- NeBadgeV2
- NeStepper
- NeToastNotificationV2
- NePasswordRequirements

## NeSkeleton

```ts
type SkeletonSize = 'sm' | 'md' | 'lg'

const props = defineProps({
  size: {
    type: String as PropType<SkeletonSize>,
    default: 'md'
  },
  lines: {
    type: Number,
    default: 1
  }
})
```
Slots: none

## NeSpinner

```ts
export type SpinnerSize =
  | '0'
  | 'px'
  | '0.5'
  | '1'
  | '1.5'
  | '2'
  | '2.5'
  | '3'
  | '4'
  | '5'
  | '6'
  | '7'
  | '8'
  | '9'
  | '10'
  | '11'
  | '12'

export type SpinnerColor =
  'primary' | 'blue' | 'gray' | 'green' | 'red' | 'yellow' | 'pink' | 'purple' | 'white'

const props = defineProps({
  size: {
    type: String as PropType<SpinnerSize>,
    default: '4'
  },
  color: {
    type: String as PropType<SpinnerColor>,
    default: 'primary'
  }
})
```
Slots: none

## NeExpandable

```ts
const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  isExpanded: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['setExpanded'])
```
Slots: default, trigger

## NeProgressBar

```ts
export type ProgressBarSize = 'sm' | 'md' | 'lg' | 'xl'

export type ProgressBarColor =
  'primary' | 'gray' | 'blue' | 'red' | 'green' | 'yellow' | 'indigo' | 'rose' | 'amber' | 'custom'

const props = defineProps({
  progress: {
    type: Number,
    required: true,
    validator(value: number) {
      return value >= 0 && value <= 100
    }
  },
  label: {
    type: String,
    default: ''
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  size: {
    type: String as PropType<ProgressBarSize>,
    default: 'md'
  },
  color: {
    type: String as PropType<ProgressBarColor>,
    default: 'primary'
  },
  customColorClasses: {
    type: String,
    default: ''
  },
  indeterminate: {
    type: Boolean,
    default: false
  }
})
```
Slots: none

## NeFileInput

```ts
interface FileInputProps {
  modelValue?: File | File[] | null
  label?: string
  helperText?: string
  invalidMessage?: string
  dropzoneLabel: string
  progress?: number
  showProgress?: boolean
  accept?: string | undefined
}

const props = withDefaults(defineProps<FileInputProps>(), {
  modelValue: null,
  label: '',
  helperText: '',
  invalidMessage: '',
  progress: 0,
  showProgress: false,
  dropzoneLabel: 'Drag and drop or click to upload',
  accept: undefined
})

const emit = defineEmits(['update:modelValue', 'select'])
```
Slots: default

## NeInlineNotification

```ts
type NotificationKind = 'info' | 'warning' | 'error' | 'success'

const props = defineProps({
  kind: {
    type: String as PropType<NotificationKind>,
    required: true
  },
  title: {
    type: String,
    default: undefined
  },
  description: {
    type: String,
    default: undefined
  },
  showCloseButton: {
    type: Boolean,
    default: false
  },
  primaryButtonLabel: {
    type: String,
    default: undefined
  },
  secondaryButtonLabel: {
    type: String,
    default: undefined
  },
  showDetailsLabel: {
    type: String,
    default: 'Show details'
  },
  closeAriaLabel: { type: String, default: 'Dismiss' }
})

const emit = defineEmits(['close', 'primaryClick', 'secondaryClick'])
```
Slots: description, details, title

## NeRoundedIcon

```ts
export type RoundedIconKind = 'info' | 'warning' | 'error' | 'success' | 'gray'

interface RoundedIconProps {
  kind?: RoundedIconKind
  customIcon?: IconDefinition
  customForegroundClasses?: string
  customBackgroundClasses?: string
}

const props = defineProps<RoundedIconProps>()
```
Slots: none

## NeSideDrawer

```ts
const props = defineProps({
  isShown: { type: Boolean, default: false },
  title: { type: String, default: '' },
  closeOnClickOutside: { type: Boolean, default: false },
  closeAriaLabel: { type: String, default: 'Close side drawer' }
})

const emit = defineEmits(['close', 'show'])
```
Slots: default

## NeTooltip

```ts
export type TooltipPlacement =
  | 'top'
  | 'top-start'
  | 'top-end'
  | 'right'
  | 'right-start'
  | 'right-end'
  | 'bottom'
  | 'bottom-start'
  | 'bottom-end'
  | 'left'
  | 'left-start'
  | 'left-end'
  | 'auto'
  | 'auto-start'
  | 'auto-end'

export type TooltipTriggerEvent =
  'click' | 'mouseenter focus' | 'focusin' | 'mouseenter click' | 'manual'

export type TippyComponentProps = Partial<InstanceType<typeof Tippy>['$props']>

const props = defineProps({
  placement: {
    type: String as PropType<TooltipPlacement>,
    default: 'top'
  },
  triggerEvent: {
    type: String as PropType<TooltipTriggerEvent>,
    default: 'click'
  },
  interactive: {
    type: Boolean,
    default: true
  },
  tippyProps: {
    type: Object as PropType<TippyComponentProps>,
    default: undefined
  }
})
```
Slots: content, trigger

## NeBadge — DEPRECATED, do not use in new code

```ts
const props = defineProps({
  size: {
    type: String as PropType<'sm' | 'xs'>,
    default: 'sm'
  },
  kind: {
    type: String as PropType<
      'primary' | 'secondary' | 'tertiary' | 'error' | 'warning' | 'success' | 'info' | 'custom'
    >,
    default: 'secondary'
  },
  rounded: {
    type: Boolean,
    default: true
  },
  text: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: false,
    default: undefined
  },
  icon: {
    type: Object,
    required: false,
    default: undefined
  },
  iconClickable: {
    type: Boolean,
    default: false
  },
  iconPosition: {
    type: String as PropType<'left' | 'right'>,
    default: 'left'
  },
  customColorClasses: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['iconClick'])
```
Slots: none

## NeButton

```ts
export type ButtonKind = 'primary' | 'secondary' | 'tertiary' | 'danger'

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

const props = defineProps({
  kind: {
    type: String as PropType<ButtonKind>,
    default: 'secondary'
  },
  size: {
    type: String as PropType<ButtonSize>,
    default: 'md'
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingPosition: {
    type: String as PropType<'prefix' | 'suffix'>,
    default: 'prefix'
  },
  disabled: {
    type: Boolean,
    default: false
  }
})
```
Slots: default, prefix, suffix

## NeCheckbox

```ts
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  id: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  disableSelectOnLabel: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  invalidMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])
```
Slots: default, description, tooltip

## NeTable

```ts
export type Breakpoint = 'sm' | 'md' | 'lg' | 'xl' | '2xl'

const {
  ariaLabel,
  cardBreakpoint = 'md',
  loading = false,
  skeletonRows = 8,
  skeletonColumns = 4,
  sortKey = '',
  sortDescending = false
} = defineProps<{
  ariaLabel?: string
  cardBreakpoint?: Breakpoint
  loading?: boolean
  skeletonRows?: number
  skeletonColumns?: number
  sortKey?: string
  sortDescending?: boolean
}>()
```
Slots: default, paginator

## NeTableHead

Slots: default

## NeTableHeadCell

```ts
export type SortEvent = {
  key: string
  descending: boolean
}

const props = defineProps({
  columnKey: {
    type: String,
    default: ''
  },
  sortable: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits<{
  sort: [SortEvent]
}>()
```
Slots: default

## NeTableBody

Slots: default

## NeTableRow

Slots: default

## NeTableCell

```ts
defineProps({
  dataLabel: {
    type: String,
    default: ''
  }
})
```
Slots: default

## NeCombobox

```ts
export interface NeComboboxOption {
  id: string
  label: string
  description?: string
  icon?: IconDefinition
  image?: string
  rawObj?: unknown
  disabled?: boolean
}

export interface Props {
  modelValue: string | Array<NeComboboxOption>
  options: NeComboboxOption[]
  label?: string
  placeholder?: string
  helperText?: string
  invalidMessage?: string
  maxOptionsShown?: number
  multiple?: boolean
  disabled?: boolean
  showOptionsType?: boolean
  optional?: boolean
  selectedLabel: string
  showSelectedLabel?: boolean
  noResultsLabel: string
  limitedOptionsLabel: string
  noOptionsLabel: string
  acceptUserInput?: boolean
  userInputLabel: string
  optionalLabel: string
  customOptionsWidth?: string
  externalFilter?: boolean
  loadingOptions?: boolean
  selectedOption?: NeComboboxOption
}

const props = withDefaults(defineProps<Props>(), {
  options: () => [],
  label: '',
  placeholder: '',
  helperText: '',
  invalidMessage: '',
  maxOptionsShown: 50,
  multiple: false,
  disabled: false,
  showOptionsType: true,
  optional: false,
  showSelectedLabel: true,
  acceptUserInput: false,
  customOptionsWidth: '',
  externalFilter: false,
  loadingOptions: false,
  selectedOption: undefined
})

const emit = defineEmits(['update:modelValue', 'filter'])
```
Slots: tooltip

## NeMultiselectCombobox

```ts
export interface NeMultiselectComboboxOption {
  id: string
  label: string
  description?: string
  icon?: IconDefinition
  image?: string
  rawObj?: unknown
  disabled?: boolean
}

const props = withDefaults(
  defineProps<{
    options: T[]
    label?: string
    placeholder?: string
    helperText?: string
    invalidMessage?: string
    disabled?: boolean
    showOptionsType?: boolean
    optional?: boolean
    noResultsLabel: string
    noOptionsLabel: string
    acceptUserInput?: boolean
    userInputLabel: string
    optionalLabel: string
    customOptionsWidth?: string
    maxHeight?: string
    maxOptionsShown?: number
    limitedOptionsLabel: string
    externalFilter?: boolean
    loadingOptions?: boolean
    badgeKind?: NeBadgeV2Kind
    badgeCustomKindClasses?: string
    removeLabel?: string
  }>(),
  {
    options: () => [],
    label: '',
    placeholder: '',
    helperText: '',
    invalidMessage: '',
    disabled: false,
    showOptionsType: true,
    optional: false,
    acceptUserInput: false,
    customOptionsWidth: '',
    maxHeight: '8.5rem',
    maxOptionsShown: 50,
    externalFilter: false,
    loadingOptions: false,
    badgeKind: 'gray',
    badgeCustomKindClasses: '',
    removeLabel: 'Remove'
  }
)

const emit = defineEmits<{
  filter: [query: string]
}>()

const modelValue = defineModel<T[]>()
```
Slots: tooltip

## NeDropdown

```ts
export interface Props {
  items: NeDropdownItem[]
  alignToRight?: boolean
  openMenuAriaLabel?: string
  menuClasses?: string
}

export interface NeDropdownItem {
  id: string
  label?: string
  icon?: IconDefinition
  danger?: boolean
  action?: () => void
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  items: () => [],
  alignToRight: false,
  openMenuAriaLabel: 'Open menu',
  menuClasses: ''
})
```
Slots: button, menuHeader

## NeCard

```ts
const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: Array<string>,
    default: () => []
  },
  loading: {
    type: Boolean
  },
  skeletonLines: {
    type: Number,
    default: 4
  },
  errorTitle: {
    type: String,
    default: ''
  },
  errorDescription: {
    type: String,
    default: ''
  },
  menuItems: {
    type: Array<NeDropdownItem>,
    default: () => []
  },
  alternateBackground: {
    type: Boolean
  },
  uppercaseTitle: {
    type: Boolean
  }
})
```
Slots: default, title, titleTooltip, topRight

## NeLink

```ts
defineProps({
  invertedTheme: {
    type: Boolean,
    default: false
  }
})
```
Slots: default

## NeFormItemLabel

Slots: default

## NeRadioSelection

```ts
export type RadioOption = {
  id: string
  label: string
  description?: string
  icon?: IconDefinition
  image?: string
  disabled?: boolean
}

export type RadioCardSize = SelectionCardSize

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  name: {
    type: String,
    default: ''
  },
  options: {
    required: true,
    type: Array<T>
  },
  card: {
    type: Boolean,
    default: false
  },
  gridStyle: {
    type: String,
    default: 'grid-cols-3 gap-3'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  cardSize: {
    type: String as PropType<RadioCardSize>,
    default: 'md'
  },
  cardSelectionMark: {
    type: Boolean,
    default: true
  },
  invalidMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])
```
Slots: label, option, tooltip

## NeCheckboxCards

```ts
export type NeCheckboxCardsOption = {
  id: string
  label: string
  description?: string
  icon?: IconDefinition
  image?: string
  disabled?: boolean
}

export type NeCheckboxCardsSize = SelectionCardSize

const {
  options,
  label = '',
  name = '',
  gridStyle = 'grid-cols-3 gap-3',
  disabled = false,
  size = 'md',
  invalidMessage = ''
} = defineProps<{
  options: T[]
  label?: string
  name?: string
  gridStyle?: string
  disabled?: boolean
  size?: NeCheckboxCardsSize
  invalidMessage?: string
}>()

const model = defineModel<string[]>()
```
Slots: label, option, tooltip

## NePaginator

```ts
const props = defineProps({
  currentPage: {
    type: Number,
    default: 1
  },
  totalRows: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    default: 10
  },
  pageSizes: {
    type: Array<number>,
    default: [10, 25, 50, 100]
  },
  previousLabel: {
    type: String,
    required: true
  },
  nextLabel: {
    type: String,
    required: true
  },
  navPaginationLabel: {
    type: String,
    required: true
  },
  rangeOfTotalLabel: {
    type: String,
    required: true
  },
  pageSizeLabel: {
    type: String,
    required: true
  },
  listboxOptionsPanelStyle: {
    type: String,
    default: ''
  }
})

const emit = defineEmits<{
  selectPage: [page: number]
  selectPageSize: [pageSize: number]
}>()
```
Slots: none

## NeEmptyState

```ts
defineProps({
  title: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: undefined
  }
})
```
Slots: default

## NeTabs

```ts
export interface Tab {
  name: string
  label: string
}

export interface Props {
  tabs: Tab[]
  selected?: string
  srSelectTabLabel?: string
  srTabsLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  tabs: () => [],
  selected: '',
  srSelectTabLabel: 'Select a tab',
  srTabsLabel: 'Tabs'
})

const emit = defineEmits(['selectTab'])
```
Slots: none

## NeTextArea

```ts
const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  rows: {
    type: Number,
    default: 4
  },
  modelValue: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  invalidMessage: {
    type: String,
    default: ''
  },
  optional: {
    type: Boolean
  },
  optionalLabel: {
    type: String,
    default: 'Optional'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])
```
Slots: tooltip

## NeTextInput

```ts
const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  modelValue: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  invalidMessage: {
    type: String,
    default: ''
  },
  optional: {
    type: Boolean
  },
  isSearch: {
    type: Boolean,
    default: false
  },
  clearSearchLabel: {
    type: String,
    default: 'Clear'
  },
  isPassword: {
    type: Boolean,
    default: false
  },
  showPasswordLabel: {
    type: String,
    default: 'Show password'
  },
  hidePasswordLabel: {
    type: String,
    default: 'Hide password'
  },
  optionalLabel: {
    type: String,
    default: 'Optional'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])
```
Slots: prefix, suffix, tooltip

## NeToggle

```ts
type ToggleSize = 'sm' | 'md' | 'lg' | 'xl'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  },
  topLabel: {
    type: String,
    default: ''
  },
  size: {
    type: String as PropType<ToggleSize>,
    default: 'md'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  invalidMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])
```
Slots: tooltip, topTooltip

## NeToastNotification — DEPRECATED, do not use in new code

```ts
export interface NeNotification {
  id: string
  kind: 'info' | 'warning' | 'error' | 'success'
  title: string
  description?: string
  timestamp?: Date
  payload?: any
  isShown?: boolean
  primaryLabel?: string
  primaryAction?: (...args: any[]) => void
  secondaryLabel?: string
  secondaryAction?: (...args: any[]) => void
}

defineProps({
  notification: {
    type: Object as PropType<NeNotification>,
    required: true
  },
  srCloseLabel: {
    type: String,
    required: true
  },
  primaryButtonRightAligned: {
    type: Boolean,
    default: false
  },
  showCloseButton: {
    type: Boolean,
    default: false
  },
  showTimestamp: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close'])
```
Slots: icon

## NeModal

```ts
export type ModalKind = 'neutral' | 'info' | 'warning' | 'error' | 'success'

export type PrimaryButtonKind = 'primary' | 'danger'

export type ModalSize = 'md' | 'lg' | 'xl' | 'xxl'

const {
  visible = true,
  title = '',
  kind = 'neutral',
  size = 'md',
  primaryLabel = '',
  secondaryLabel = '',
  cancelLabel = '',
  primaryButtonKind = 'primary',
  primaryButtonDisabled = false,
  primaryButtonLoading = false,
  secondaryButtonKind = 'secondary',
  secondaryButtonDisabled = false,
  secondaryButtonLoading = false
} = defineProps<{
  visible?: boolean
  title?: string
  kind?: ModalKind
  size?: ModalSize
  primaryLabel?: string
  secondaryLabel?: string
  cancelLabel?: string
  primaryButtonKind?: ButtonKind
  primaryButtonDisabled?: boolean
  primaryButtonLoading?: boolean
  secondaryButtonKind?: ButtonKind
  secondaryButtonDisabled?: boolean
  secondaryButtonLoading?: boolean
  closeAriaLabel: string
}>()

const emit = defineEmits(['close', 'primaryClick', 'secondaryClick', 'show'])
```
Slots: default

## NeHeading

```ts
type HeadingTag = 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'

defineProps({
  tag: {
    type: String as PropType<HeadingTag>,
    default: 'h1'
  }
})
```
Slots: default

## NeListbox

```ts
export interface NeListboxOption {
  id: string
  label: string
  description?: string
  rawObj?: any
  disabled?: boolean
}

export interface Props {
  modelValue: string | Array<NeListboxOption>
  options: NeListboxOption[]
  label?: string
  placeholder?: string
  helperText?: string
  invalidMessage?: string
  multiple?: boolean
  disabled?: boolean
  showOptionsType?: boolean
  optional?: boolean
  noOptionsLabel: string
  optionalLabel: string
  optionsPanelStyle?: string
}

const props = withDefaults(defineProps<Props>(), {
  options: () => [],
  label: '',
  placeholder: '',
  helperText: '',
  invalidMessage: '',
  multiple: false,
  disabled: false,
  showOptionsType: true,
  optional: false,
  optionsPanelStyle: ''
})

const emit = defineEmits(['update:modelValue'])
```
Slots: tooltip

## NeDropdownFilter — DEPRECATED, do not use in new code

```ts
export type FilterKind = 'radio' | 'checkbox'

export type FilterOption = {
  id: string
  label: string
  description?: string
  disabled?: boolean
}

export type FilterOptionGroup = {
  group: string
  options: FilterOption[]
}

export interface Props {
  label: string
  options: (FilterOption | FilterOptionGroup)[]
  kind: FilterKind
  clearFilterLabel: string
  openMenuAriaLabel: string
  showClearFilter?: boolean
  showSelectionCount?: boolean
  showRadioSelection?: boolean
  noOptionsLabel: string
  showOptionsFilter?: boolean
  optionsFilterPlaceholder?: string
  maxOptionsShown?: number
  moreOptionsHiddenLabel: string
  alignToRight?: boolean
  size?: ButtonSize
  disabled?: boolean
  id?: string
  clearSearchLabel: string
  externalFilter?: boolean
  loadingOptions?: boolean
  customActionLabel?: string
}

const props = withDefaults(defineProps<Props>(), {
  showClearFilter: true,
  showSelectionCount: true,
  showRadioSelection: false,
  showOptionsFilter: false,
  clearSearchLabel: 'Clear',
  optionsFilterPlaceholder: '',
  maxOptionsShown: 25,
  alignToRight: false,
  size: 'md',
  disabled: false,
  id: '',
  externalFilter: false,
  loadingOptions: false,
  customActionLabel: ''
})

const emit = defineEmits<{
  search: [query: string]
  customAction: []
}>()

const model = defineModel<string[]>()
```
Slots: button, label

## NeDropdownFilterV2

```ts
export type FilterKind = 'radio' | 'checkbox'

export type NeDropdownFilterV2Option = {
  id: string
  label: string
  description?: string
  disabled?: boolean
}

export type NeDropdownFilterV2OptionGroup<

const props = withDefaults(
  defineProps<{
    label: string
    options: (T | NeDropdownFilterV2OptionGroup<T>)[]
    kind: FilterKind
    clearFilterLabel: string
    openMenuAriaLabel: string
    showClearFilter?: boolean
    showSelectionCount?: boolean
    showRadioSelection?: boolean
    noOptionsLabel: string
    showOptionsFilter?: boolean
    optionsFilterPlaceholder?: string
    maxOptionsShown?: number
    moreOptionsHiddenLabel: string
    alignToRight?: boolean
    size?: ButtonSize
    disabled?: boolean
    id?: string
    clearSearchLabel: string
    externalFilter?: boolean
    loadingOptions?: boolean
    customActionLabel?: string
  }>(),
  {
    showClearFilter: true,
    showSelectionCount: true,
    showRadioSelection: false,
    showOptionsFilter: false,
    clearSearchLabel: 'Clear',
    optionsFilterPlaceholder: '',
    maxOptionsShown: 25,
    alignToRight: false,
    size: 'md',
    disabled: false,
    id: '',
    externalFilter: false,
    loadingOptions: false,
    customActionLabel: ''
  }
)

const emit = defineEmits<{
  search: [query: string]
  customAction: []
}>()

const model = defineModel<T[]>()
```
Slots: button, label

## NeSortDropdown

```ts
export type SortOption = {
  id: string
  label: string
}

export interface Props {
  label: string
  options: SortOption[]
  openMenuAriaLabel: string
  sortByLabel: string
  sortDirectionLabel: string
  ascendingLabel: string
  descendingLabel: string
  alignToRight?: boolean
  size?: ButtonSize
  disabled?: boolean
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  alignToRight: false,
  size: 'md',
  disabled: false,
  id: ''
})

const sortKey = defineModel<string>()

const sortDescending = defineModel<boolean>()
```
Slots: button, label

## NeAvatar

```ts
export type AvatarSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'

const {
  size = 'md',
  img = '',
  initials = '',
  squared = false,
  alt = 'Avatar'
} = defineProps<{
  size?: AvatarSize
  img?: string
  initials?: string
  squared?: boolean
  alt?: string
}>()
```
Slots: placeholder

## NeBadgeV2

```ts
export type NeBadgeV2Kind =
  'primary' | 'indigo' | 'gray' | 'green' | 'amber' | 'rose' | 'blue' | 'custom'

const {
  size = 'sm',
  kind = 'gray',
  pill = true,
  dismissable = false,
  customKindClasses = '',
  dismissAriaLabel = 'Dismiss'
} = defineProps<{
  size?: 'xs' | 'sm'
  kind?: NeBadgeV2Kind
  pill?: boolean
  dismissable?: boolean
  customKindClasses?: string
  dismissAriaLabel?: string
}>()

const emit = defineEmits(['dismiss'])
```
Slots: default

## NeStepper

```ts
const { totalSteps, currentStep, stepLabel } = defineProps<{
  totalSteps: number
  currentStep: number
  stepLabel: string
}>()
```
Slots: none

## NeToastNotificationV2

```ts
export interface NeNotificationV2 {
  id: string
  kind: 'info' | 'warning' | 'error' | 'success'
  title: string
  description?: string
  timestamp?: Date
  payload?: Record<string, unknown>
  isShown?: boolean
  firstButtonLabel?: string
  firstButtonAction?: string
  firstButtonKind?: ButtonKind
  secondButtonLabel?: string
  secondButtonAction?: string
  secondButtonKind?: ButtonKind
}

defineProps({
  notification: {
    type: Object as PropType<NeNotificationV2>,
    required: true
  },
  srCloseLabel: {
    type: String,
    required: true
  },
  firstActionOnRight: {
    type: Boolean,
    default: false
  },
  showCloseButton: {
    type: Boolean,
    default: false
  },
  showTimestamp: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

defineEmits(['close', 'action'])
```
Slots: icon

## NePasswordRequirements

```ts
const {
  requirements,
  showErrors = false,
  metLabel = 'Requirement met',
  unmetLabel = 'Requirement not met'
} = defineProps<{
  requirements: NePasswordRequirementStatus[]
  showErrors?: boolean
  metLabel?: string
  unmetLabel?: string
}>()
```
Slots: none

