<script setup lang="ts">
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'

interface IntegrationRow {
  id: string
  integration: string
  description: string
  enabled: boolean
  status: string
  source: string
}

const placeholderIntegrations: IntegrationRow[] = [
  {
    id: 'local-edgelink',
    integration: 'EdgeLink',
    description: 'Edge device link and field gateway connectivity',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-mqtt',
    integration: 'MQTT',
    description: 'MQTT broker connection for IoT ingest',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-webhook',
    integration: 'Webhook',
    description: 'Inbound/outbound HTTP webhook integrations',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-email-gateway',
    integration: 'Email Gateway',
    description: 'External email gateway for system messages',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-external-ibms',
    integration: 'External ONE',
    description: 'Federation with external ONE instances',
    enabled: false,
    status: 'Not configured',
    source: 'Local placeholder / API pending',
  },
]
</script>

<template>
  <div class="integration-settings-page">
    <RouteL3ContentPanel />

    <el-card shadow="never">
      <template #header>
        <div class="page-header">
          <div>
            <h1>Integration Settings</h1>
            <p>Prepare external integration configuration for ONE operations.</p>
          </div>
        </div>
      </template>

      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="Pending backend integration configuration API / Contract pending"
        description="No integration settings endpoint is defined in current OpenAPI contracts. Integration rows and controls below are local placeholders only. No API keys or secrets are shown."
        class="page-alert"
      />

      <el-form label-position="top" class="settings-form">
        <el-form-item label="Integration type filter (preview)">
          <el-select model-value="" placeholder="All integrations" disabled>
            <el-option label="EdgeLink" value="edgelink" />
            <el-option label="MQTT" value="mqtt" />
            <el-option label="Webhook" value="webhook" />
            <el-option label="Email Gateway" value="email-gateway" />
            <el-option label="External ONE" value="external-ibms" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table :data="placeholderIntegrations" row-key="id" class="integration-table">
        <el-table-column prop="integration" label="Integration" width="140" />
        <el-table-column prop="description" label="Description" min-width="240" show-overflow-tooltip />
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

      <el-empty description="Backend integration configuration API not connected — showing local placeholder integrations only." />
    </el-card>
  </div>
</template>

<style scoped>
.integration-settings-page {
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

.integration-table {
  margin-bottom: 16px;
}

.action-row {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
</style>
