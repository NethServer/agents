#!/usr/bin/env bash
# A small Vue 3 project whose table breaks several Nebula rules.
set -euo pipefail
mkdir -p src/components src/i18n/en
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
    "status": "Status",
    "archived": "Archived",
    "active": "Active",
    "modify_customer": "Modify customer",
    "systems": "Systems",
    "show_systems": "Show the systems of {name}",
    "show_notes": "Show notes",
    "cannot_retrieve_customers": "Cannot retrieve customers"
  }
}
FIXTURE
cat > src/components/CustomersTable.vue <<'FIXTURE'
<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { library } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { NeButton, NeHeading, NeInlineNotification, NeLink } from '@nethesis/vue-components'

library.add(fas)

type Customer = { id: string; name: string; vat: string; systems: number; archived: boolean }

defineProps<{ customers: Customer[]; error?: Error }>()
const emit = defineEmits<{
  open: [id: string]
  edit: [id: string]
  remove: [id: string]
  notes: [id: string]
}>()
const { t } = useI18n()
</script>

<template>
  <div>
    <NeHeading tag="h3" class="mb-4 font-bold">{{ t('customers.title') }}</NeHeading>
    <NeInlineNotification
      v-if="error"
      kind="error"
      :title="t('customers.cannot_retrieve_customers')"
      :description="error.message"
    />
    <p v-if="!customers.length" class="text-sm">No customers found</p>
    <table v-else class="w-full text-sm">
      <thead>
        <tr>
          <th>{{ t('customers.name') }}</th>
          <th>{{ t('customers.vat_number') }}</th>
          <th>{{ t('customers.systems') }}</th>
          <th>{{ t('customers.status') }}</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="customer in customers"
          :key="customer.id"
          class="cursor-pointer"
          @click="emit('open', customer.id)"
        >
          <td :class="{ 'opacity-50': customer.archived }">{{ customer.name }}</td>
          <td :class="{ 'opacity-50': customer.archived }">{{ customer.vat }}</td>
          <td>
            <router-link
              :to="`/customers/${customer.id}/systems`"
              :aria-label="t('customers.show_systems', { name: customer.name })"
              @click.stop
            >
              {{ customer.systems }}
            </router-link>
          </td>
          <td>
            <span :style="{ color: customer.archived ? '#9ca3af' : '#15803d' }">
              {{ customer.archived ? t('customers.archived') : t('customers.active') }}
            </span>
          </td>
          <td class="flex gap-2">
            <NeLink @click.stop="emit('notes', customer.id)">{{ t('customers.show_notes') }}</NeLink>
            <NeButton kind="tertiary" size="sm" @click.stop="emit('edit', customer.id)">
              {{ t('customers.modify_customer') }}
            </NeButton>
            <NeButton
              kind="tertiary"
              size="sm"
              :disabled="customer.archived"
              class="disabled:opacity-50"
              @click.stop="emit('remove', customer.id)"
            >
              <FontAwesomeIcon :icon="['fas', 'trash']" />
            </NeButton>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
FIXTURE
