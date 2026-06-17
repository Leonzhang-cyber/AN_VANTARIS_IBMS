<script setup lang="ts">
import { useRouter } from 'vue-router'

type ModuleStatus = 'available' | 'pending'

interface SystemModuleCard {
  id: string
  title: string
  description: string
  path: string
  status: ModuleStatus
  permission: string
  apiPending?: boolean
}

const router = useRouter()

const modules: SystemModuleCard[] = [
  {
    id: 'permissions',
    title: 'Permission Management',
    description: 'View and manage backend permission codes used by protected IBMS APIs.',
    path: '/system/permissions',
    status: 'available',
    permission: 'system:read',
  },
  {
    id: 'settings',
    title: 'System Settings',
    description: 'Review environment-driven configuration and prepare for backend settings API.',
    path: '/system/settings',
    status: 'available',
    permission: 'system:read',
  },
  {
    id: 'audit-logs',
    title: 'Audit Logs',
    description: 'Inspect administrative actions and security-relevant events. Backend audit query API is pending.',
    path: '/system/audit-logs',
    status: 'available',
    permission: 'audit:read',
    apiPending: true,
  },
  {
    id: 'notification-settings',
    title: 'Notification Settings',
    description: 'Configure alert channels and notification policies. Backend notification API is pending.',
    path: '/system/notification-settings',
    status: 'available',
    permission: 'system:read',
    apiPending: true,
  },
  {
    id: 'integration-settings',
    title: 'Integration Settings',
    description: 'Manage external system connectors and integration endpoints. Backend integration API is pending.',
    path: '/system/integration-settings',
    status: 'available',
    permission: 'system:read',
    apiPending: true,
  },
]

function statusLabel(status: ModuleStatus): string {
  return status === 'available' ? 'Available' : 'Pending migration'
}

function statusTagType(status: ModuleStatus): 'success' | 'info' {
  return status === 'available' ? 'success' : 'info'
}

function openModule(module: SystemModuleCard): void {
  if (module.status !== 'available') {
    return
  }
  void router.push(module.path)
}
</script>

<template>
  <div class="system-overview-page">
    <el-card shadow="never">
      <template #header>
        <div class="page-header">
          <div>
            <h1>System Administration</h1>
            <p>Manage permissions, settings, audit visibility, notifications, and integration configuration.</p>
          </div>
        </div>
      </template>

      <el-alert
        type="success"
        show-icon
        :closable="false"
        title="System admin first batch is established"
        class="page-alert"
      />

      <el-card shadow="never" class="batch-status-card">
        <p class="batch-status__lead">Available pages:</p>
        <ul class="batch-status__list">
          <li>Overview</li>
          <li>Permission Management</li>
          <li>System Settings</li>
          <li>Audit Logs</li>
          <li>Notification Settings</li>
          <li>Integration Settings</li>
        </ul>
        <p class="batch-status__note">
          Audit Logs, Notification Settings, and Integration Settings are UI placeholders until
          backend APIs are defined. Permission Management uses the system permissions API;
          System Settings is read-only until a backend configuration API exists.
        </p>
      </el-card>

      <el-row :gutter="16">
        <el-col
          v-for="module in modules"
          :key="module.id"
          :xs="24"
          :sm="12"
          :lg="8"
        >
          <el-card class="module-card" shadow="hover">
            <div class="module-card__header">
              <h2>{{ module.title }}</h2>
              <div class="module-card__tags">
                <el-tag :type="statusTagType(module.status)" size="small">
                  {{ statusLabel(module.status) }}
                </el-tag>
                <el-tag v-if="module.apiPending" type="warning" size="small">API pending</el-tag>
              </div>
            </div>

            <p class="module-card__description">{{ module.description }}</p>

            <p class="module-card__permission">
              Required permission: <code>{{ module.permission }}</code>
            </p>

            <el-button
              type="primary"
              plain
              :disabled="module.status !== 'available'"
              @click="openModule(module)"
            >
              {{ module.status === 'available' ? 'Open module' : 'Pending migration' }}
            </el-button>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<style scoped>
.system-overview-page {
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

.batch-status-card {
  margin-bottom: 16px;
}

.batch-status__lead {
  margin: 0 0 8px;
  font-weight: 600;
  font-size: 0.875rem;
}

.batch-status__list {
  margin: 0 0 12px;
  padding-left: 20px;
  color: var(--el-text-color-regular);
  font-size: 0.875rem;
  line-height: 1.6;
}

.batch-status__note {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.8125rem;
  line-height: 1.5;
}

.module-card {
  margin-bottom: 16px;
  min-height: 220px;
}

.module-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.module-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: flex-end;
}

.module-card__header h2 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.module-card__description {
  margin: 0 0 12px;
  color: var(--el-text-color-regular);
  font-size: 0.875rem;
  line-height: 1.5;
}

.module-card__permission {
  margin: 0 0 16px;
  font-size: 0.8125rem;
  color: var(--el-text-color-secondary);
}

.module-card__permission code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
</style>
