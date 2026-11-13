#!/usr/bin/env bash
# A Vue 3 component whose text is unreadable in the dark theme.
set -euo pipefail
mkdir -p src/components
cat > package.json <<'FIXTURE'
{
  "name": "status-ui",
  "private": true,
  "type": "module",
  "dependencies": {
    "@nethesis/vue-components": "^3.15.1",
    "vue": "^3.5.13"
  },
  "devDependencies": {
    "tailwindcss": "^4.1.14"
  }
}
FIXTURE
cat > src/components/ServiceStatus.vue <<'FIXTURE'
<script setup lang="ts">
defineProps<{ name: string; running: boolean }>()
</script>

<template>
  <div class="flex items-center gap-2 rounded-md bg-white p-3 dark:bg-gray-900">
    <span class="text-gray-900">{{ name }}</span>
    <span :class="running ? 'text-green-700' : 'text-gray-600'">
      {{ running ? 'Running' : 'Stopped' }}
    </span>
  </div>
</template>
FIXTURE
