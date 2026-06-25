<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'
import * as menuApi from '@/services/api/menu'
import { normalizeBackendMenu } from '@/services/menu/menu-normalizer'
import { resolveBaseUrl } from '@/services/api/request'

const menuMode = ref<'dynamic' | 'fallback' | 'checking'>('checking')

const settingsForm = reactive({
  applicationName: readEnvString('VITE_ONE_APP_NAME', readEnvString('VITE_IBMS_APP_NAME', 'VANTARIS ONE')),
  apiBaseUrl: resolveBaseUrl(),
  debugEnabled: readDebugFlag(),
  menuMode: 'checking',
  permissionEnforcement: 'backend-controlled',
})

const menuModeLabel = computed(() => {
  if (menuMode.value === 'checking') {
    return 'Checking…'
  }
  return menuMode.value === 'dynamic' ? 'dynamic' : 'fallback'
})

function readEnvString(key: string, fallback: string): string {
  const value = import.meta.env[key]
  if (typeof value === 'string' && value.trim()) {
    return value.trim()
  }
  return fallback
}

function readDebugFlag(): boolean {
  const value = (import.meta.env.VITE_ONE_ENABLE_DEBUG ?? import.meta.env.VITE_IBMS_ENABLE_DEBUG)
  if (typeof value === 'string') {
    return value.trim().toLowerCase() === 'true'
  }
  return Boolean(value)
}

async function detectMenuMode(): Promise<void> {
  menuMode.value = 'checking'
  settingsForm.menuMode = 'checking'

  try {
    const response = await menuApi.getMenus()
    const normalized = normalizeBackendMenu(response)
    menuMode.value = normalized.length > 0 ? 'dynamic' : 'fallback'
  } catch {
    menuMode.value = 'fallback'
  }

  settingsForm.menuMode = menuModeLabel.value
}

onMounted(() => {
  void detectMenuMode()
})
</script>

<template>
  <div class="settings-page">
    <RouteL3ContentPanel />

    <el-card shadow="never">
      <template #header>
        <div class="page-header">
          <div>
            <h1>System Settings</h1>
            <p>Review and prepare configurable system options for ONE operations.</p>
          </div>
        </div>
      </template>

      <el-alert
        type="info"
        show-icon
        :closable="false"
        title="Read-only configuration preview"
        description="Values reflect frontend environment and runtime menu behavior. Persistent system configuration API is not yet available."
        class="page-alert"
      />

      <el-form label-position="top" class="settings-form">
        <el-form-item label="Application Name">
          <el-input v-model="settingsForm.applicationName" readonly />
        </el-form-item>

        <el-form-item label="API Base URL">
          <el-input v-model="settingsForm.apiBaseUrl" readonly />
        </el-form-item>

        <el-form-item label="Debug Enabled">
          <el-switch v-model="settingsForm.debugEnabled" disabled />
        </el-form-item>

        <el-form-item label="Menu Mode">
          <el-select v-model="settingsForm.menuMode" disabled>
            <el-option label="dynamic" value="dynamic" />
            <el-option label="fallback" value="fallback" />
            <el-option label="checking" value="checking" />
          </el-select>
        </el-form-item>

        <el-form-item label="Permission Enforcement">
          <el-input v-model="settingsForm.permissionEnforcement" readonly />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" disabled>
            Pending backend configuration API
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 16px;
}

.page-header h1 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.875rem;
}

.page-alert {
  margin-bottom: 16px;
}

.settings-form {
  max-width: 520px;
}
</style>
