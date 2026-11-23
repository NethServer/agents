#!/usr/bin/env bash
# A small Vue 3 project with a customers table that follows Nebula, in a git
# repository where developers edit both i18n files.
set -euo pipefail
mkdir -p src/components src/i18n/en src/i18n/it
cat > package.json <<'FIXTURE'
{
  "name": "customers-ui",
  "private": true,
  "type": "module",
  "dependencies": {
    "@fortawesome/fontawesome-svg-core": "^6.7.2",
    "@fortawesome/free-solid-svg-icons": "^6.7.2",
    "@fortawesome/vue-fontawesome": "^3.0.8",
    "@nethesis/vue-components": "^3.15.1",
    "vue": "^3.5.13",
    "vue-i18n": "^11.1.11"
  },
  "devDependencies": {
    "@tailwindcss/vite": "^4.1.14",
    "tailwindcss": "^4.1.14",
    "vite": "^6.3.6"
  }
}
FIXTURE
cat > src/i18n/en/translation.json <<'FIXTURE'
{
  "customers": {
    "title": "Customers",
    "name": "Name",
    "vat_number": "VAT number",
    "edit": "Edit"
  }
}
FIXTURE
cat > src/i18n/it/translation.json <<'FIXTURE'
{
  "customers": {
    "title": "Clienti",
    "name": "Nome",
    "vat_number": "Partita IVA",
    "edit": "Modifica"
  }
}
FIXTURE
cat > src/components/CustomersTable.vue <<'FIXTURE'
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { faPen } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  NeButton,
  NeTable,
  NeTableBody,
  NeTableCell,
  NeTableHead,
  NeTableHeadCell,
  NeTableRow
} from '@nethesis/vue-components'

type Customer = { id: string; name: string; vat: string }

defineProps<{ customers: Customer[] }>()
const emit = defineEmits<{ edit: [id: string] }>()
const { t } = useI18n()
</script>

<template>
  <NeTable :aria-label="t('customers.title')">
    <NeTableHead>
      <NeTableHeadCell>{{ t('customers.name') }}</NeTableHeadCell>
      <NeTableHeadCell>{{ t('customers.vat_number') }}</NeTableHeadCell>
      <NeTableHeadCell />
    </NeTableHead>
    <NeTableBody>
      <NeTableRow v-for="customer in customers" :key="customer.id">
        <NeTableCell :data-label="t('customers.name')">{{ customer.name }}</NeTableCell>
        <NeTableCell :data-label="t('customers.vat_number')">{{ customer.vat }}</NeTableCell>
        <NeTableCell>
          <NeButton kind="tertiary" size="sm" @click="emit('edit', customer.id)">
            <template #prefix>
              <FontAwesomeIcon :icon="faPen" aria-hidden="true" />
            </template>
            {{ t('customers.edit') }}
          </NeButton>
        </NeTableCell>
      </NeTableRow>
    </NeTableBody>
  </NeTable>
</template>
FIXTURE
git init -q
git -c user.name='Alice Fox' -c user.email=alice@example.com add .
git -c user.name='Alice Fox' -c user.email=alice@example.com commit -q -m 'feat: add the customers table'
