<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'

const route = useRoute()

const bareRoutes = new Set(['/login', '/403'])

const showLayout = computed(() => !bareRoutes.has(route.path))
</script>

<template>
  <AppLayout v-if="showLayout" />
  <router-view v-else />
</template>
