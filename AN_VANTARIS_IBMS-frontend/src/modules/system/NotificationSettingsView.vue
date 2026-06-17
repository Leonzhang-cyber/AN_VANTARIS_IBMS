<script setup lang="ts">
interface NotificationChannelRow {
  id: string
  channel: string
  description: string
  enabled: boolean
  status: string
  source: string
}

const placeholderChannels: NotificationChannelRow[] = [
  {
    id: 'local-email',
    channel: 'Email',
    description: 'Outbound email alerts for system events',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-sms',
    channel: 'SMS',
    description: 'SMS notifications for critical alerts',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-teams',
    channel: 'Teams',
    description: 'Microsoft Teams webhook notifications',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-slack',
    channel: 'Slack',
    description: 'Slack channel notifications',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-webhook',
    channel: 'Webhook',
    description: 'Generic HTTP webhook delivery',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
]
</script>

<template>
  <div class="notification-settings-page">
    <el-card shadow="never">
      <template #header>
        <div class="page-header">
          <div>
            <h1>Notification Settings</h1>
            <p>Prepare outbound notification channel settings for IBMS operations.</p>
          </div>
        </div>
      </template>

      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="Pending backend notification configuration API / Contract pending"
        description="No notification settings endpoint is defined in current OpenAPI contracts. Channel rows and controls below are local placeholders only."
        class="page-alert"
      />

      <el-form label-position="top" class="settings-form">
        <el-form-item label="Default severity filter (preview)">
          <el-select model-value="" placeholder="All severities" disabled>
            <el-option label="Info" value="info" />
            <el-option label="Warning" value="warning" />
            <el-option label="Critical" value="critical" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="placeholderChannels" row-key="id" class="channel-table">
        <el-table-column prop="channel" label="Channel" width="120" />
        <el-table-column prop="description" label="Description" min-width="220" show-overflow-tooltip />
        <el-table-column label="Enabled" width="100">
          <template #default="{ row }">
            <el-switch :model-value="row.enabled" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="140" />
        <el-table-column prop="source" label="Source" min-width="220">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.source }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="action-row">
        <el-button type="primary" disabled>Save (Pending backend API)</el-button>
        <el-button disabled>Test (Pending backend API)</el-button>
      </div>

      <el-empty description="Backend notification configuration API not connected — showing local placeholder channels only." />
    </el-card>
  </div>
</template>

<style scoped>
.notification-settings-page {
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
  max-width: 320px;
  margin-bottom: 16px;
}

.channel-table {
  margin-bottom: 16px;
}

.action-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>
