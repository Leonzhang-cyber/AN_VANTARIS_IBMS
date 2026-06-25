<script setup lang="ts">
import { reactive, ref } from 'vue'
import RouteL3ContentPanel from '@/components/RouteL3ContentPanel.vue'

interface AuditLogPlaceholderRow {
  id: string
  timestamp: string
  actor: string
  action: string
  severity: 'info' | 'warning' | 'error'
  source: string
}

const keyword = ref('')
const severity = ref('')
const dateRange = ref<[Date, Date] | null>(null)

const filters = reactive({
  keyword,
  severity,
  dateRange,
})

const placeholderRows: AuditLogPlaceholderRow[] = [
  {
    id: 'local-placeholder-1',
    timestamp: '—',
    actor: 'Local placeholder',
    action: 'No backend audit API connected',
    severity: 'info',
    source: 'Local placeholder / API pending',
  },
  {
    id: 'local-placeholder-2',
    timestamp: '—',
    actor: 'Local placeholder',
    action: 'Contract pending for audit log query',
    severity: 'warning',
    source: 'Local placeholder / API pending',
  },
]

function severityTagType(value: string): 'info' | 'warning' | 'danger' {
  if (value === 'error') {
    return 'danger'
  }
  if (value === 'warning') {
    return 'warning'
  }
  return 'info'
}
</script>

<template>
  <div class="audit-logs-page">
    <RouteL3ContentPanel />

    <el-card shadow="never">
      <template #header>
        <div class="page-header">
          <div>
            <h1>Audit Logs</h1>
            <p>Review security-relevant operation traces and permission-sensitive actions.</p>
          </div>
        </div>
      </template>

      <el-alert
        type="warning"
        show-icon
        :closable="false"
        title="Pending backend audit API / Contract pending"
        description="No audit log query endpoint is defined in current OpenAPI contracts. Filters and table rows below are local placeholders only."
        class="page-alert"
      />

      <el-card shadow="never" class="filter-card">
        <template #header>Filters (read-only preview)</template>
        <div class="filter-row">
          <el-input
            v-model="filters.keyword"
            placeholder="Keyword"
            disabled
            clearable
          />
          <el-select v-model="filters.severity" placeholder="Severity" disabled clearable>
            <el-option label="Info" value="info" />
            <el-option label="Warning" value="warning" />
            <el-option label="Error" value="error" />
          </el-select>
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start date"
            end-placeholder="End date"
            disabled
          />
          <el-button type="primary" disabled>Search (API pending)</el-button>
        </div>
      </el-card>

      <el-table :data="placeholderRows" row-key="id" class="audit-table">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="actor" label="Actor" min-width="140" />
        <el-table-column prop="action" label="Action" min-width="220" show-overflow-tooltip />
        <el-table-column label="Severity" width="120">
          <template #default="{ row }">
            <el-tag :type="severityTagType(row.severity)" size="small">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" min-width="220">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.source }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <el-empty description="Backend audit log API not connected — showing local placeholder rows only." />
    </el-card>
  </div>
</template>

<style scoped>
.audit-logs-page {
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

.filter-card {
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-row .el-input,
.filter-row .el-select {
  width: 200px;
}

.audit-table {
  margin-bottom: 16px;
}
</style>
