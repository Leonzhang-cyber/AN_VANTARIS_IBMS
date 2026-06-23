<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getReportsGaR13Workspace, type ReportsGaR13Workspace } from '@/services/api/reports'

const tabs = ['Overview', 'Report Library', 'Customer Report Pack', 'Engineer Report Pack', 'Admin Report Pack', 'UMMS Reports', 'UHMI Reports', 'UCDE Evidence Reports', 'Customer Delivery Reports', 'Foundation Diagnostics Reports', 'Export Center', 'Guardrails']
const activeTab = ref('Overview')
const loading = ref(false)
const error = ref('')
const workspace = ref<ReportsGaR13Workspace | null>(null)

const badges = computed(() => workspace.value ? ['Customer Demo Report Pack', 'Export Center Preview', 'Read-only Mode'] : [])

const filteredReports = computed(() => {
  const rows = workspace.value?.reportLibrary ?? []
  if (activeTab.value === 'UMMS Reports') return rows.filter((row) => row.sourceModule === 'UMMS')
  if (activeTab.value === 'UHMI Reports') return rows.filter((row) => row.sourceModule === 'UHMI')
  if (activeTab.value === 'UCDE Evidence Reports') return rows.filter((row) => row.sourceModule === 'UCDE')
  if (activeTab.value === 'Customer Delivery Reports') return rows.filter((row) => row.sourceModule === 'Customer Delivery')
  if (activeTab.value === 'Foundation Diagnostics Reports') return rows.filter((row) => row.sourceModule === 'Foundation Diagnostics')
  return rows
})

async function loadWorkspace() {
  loading.value = true
  error.value = ''
  try {
    workspace.value = await getReportsGaR13Workspace()
  } catch {
    error.value = 'Reports & Analytics demo pack data unavailable.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadWorkspace()
})
</script>

<template>
  <section class="reports-r13-page" v-loading="loading">
    <header class="workspace-head">
      <div>
        <p class="eyebrow">Reports & Analytics</p>
        <h1>Customer Demo Report Pack</h1>
        <p class="summary">Export Center Preview for customer output, delivery handoff, audit review, and evidence-linked reports.</p>
      </div>
      <div class="badge-stack">
        <el-tag v-for="badge in badges" :key="badge" round>{{ badge }}</el-tag>
      </div>
    </header>

    <el-alert v-if="error" class="section-gap" type="warning" show-icon :closable="false" :title="error" />

    <template v-if="workspace">
      <section class="target-strip section-gap">
        <strong>APP / Reports target: {{ workspace.appNonDbTarget }}</strong>
        <strong>DB-only target: {{ workspace.dbOnlyTarget }}</strong>
        <span>{{ workspace.futureExportPath }}</span>
      </section>

      <section class="card-grid section-gap">
        <article v-for="card in workspace.reportSummaryCards" :key="card.label" class="metric-card">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <em>{{ card.status }}</em>
        </article>
      </section>

      <el-tabs v-model="activeTab" type="card" class="workspace-tabs section-gap">
        <el-tab-pane v-for="tab in tabs" :key="tab" :label="tab" :name="tab">
          <template v-if="tab === 'Overview'">
            <div class="section-title">Report Library</div>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="scope">{{ workspace.scope }}</el-descriptions-item>
              <el-descriptions-item label="mode">{{ workspace.mode }}</el-descriptions-item>
              <el-descriptions-item label="readiness">{{ workspace.readinessLevel }}</el-descriptions-item>
              <el-descriptions-item label="Customer Demo Report Pack">{{ workspace.customerDemoReportPack }}</el-descriptions-item>
              <el-descriptions-item label="Export Center Preview">{{ workspace.exportCenterPreview }}</el-descriptions-item>
              <el-descriptions-item label="Reports & Analytics">{{ workspace.visualStyle }}</el-descriptions-item>
            </el-descriptions>
            <div class="section-title inner-gap">Module Linkage</div>
            <div class="guardrail-grid">
              <el-tag v-for="item in workspace.moduleLinkage" :key="item" round type="success">{{ item }}</el-tag>
            </div>
          </template>

          <template v-else-if="tab === 'Report Library' || tab.includes('Reports')">
            <div class="section-title">{{ tab === 'Report Library' ? 'Report Library' : tab }}</div>
            <el-table :data="filteredReports" stripe border>
              <el-table-column prop="reportName" label="Report" min-width="260" />
              <el-table-column prop="reportCategory" label="Category" min-width="150" />
              <el-table-column prop="sourceModule" label="Source" min-width="170" />
              <el-table-column prop="linkedWorkspace" label="Linked Workspace" min-width="240" />
              <el-table-column prop="readinessStatus" label="Readiness" min-width="180" />
              <el-table-column prop="exportState" label="Export State" min-width="150" />
              <el-table-column prop="readOnly" label="Read-only" min-width="110" />
            </el-table>
            <p class="report-callouts" v-if="tab === 'Report Library'">
              UMMS Maintenance Report, UHMI System Status Report, UCDE Evidence Report, Customer Delivery Handoff Report,
              Foundation Diagnostics Readiness Report, Package Readiness Report, Audit / Compliance Summary Report
            </p>
          </template>

          <template v-else-if="tab === 'Customer Report Pack'">
            <div class="section-title">Customer / Engineer / Admin report packs</div>
            <ul class="pack-list">
              <li v-for="item in workspace.customerReportPack" :key="item">{{ item }}</li>
            </ul>
          </template>

          <template v-else-if="tab === 'Engineer Report Pack'">
            <div class="section-title">Engineer Report Pack</div>
            <ul class="pack-list">
              <li v-for="item in workspace.engineerReportPack" :key="item">{{ item }}</li>
            </ul>
          </template>

          <template v-else-if="tab === 'Admin Report Pack'">
            <div class="section-title">Admin Report Pack</div>
            <ul class="pack-list">
              <li v-for="item in workspace.adminReportPack" :key="item">{{ item }}</li>
            </ul>
          </template>

          <template v-else-if="tab === 'Export Center'">
            <div class="section-title">Export Center Preview</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Export Formats Preview">{{ workspace.exportCenter.supportedFormats }}</el-descriptions-item>
              <el-descriptions-item label="Export Queue Preview">{{ workspace.exportCenter.exportQueuePreview }}</el-descriptions-item>
              <el-descriptions-item label="Export Guardrails">{{ workspace.exportCenter.exportPolicy }}</el-descriptions-item>
              <el-descriptions-item label="Approval Required">{{ workspace.exportCenter.approvalRequired }}</el-descriptions-item>
              <el-descriptions-item label="No Real Export Execution">{{ workspace.exportExecuted }}</el-descriptions-item>
              <el-descriptions-item label="No PDF Generation">{{ workspace.pdfGenerated }}</el-descriptions-item>
              <el-descriptions-item label="No Excel Generation">{{ workspace.excelGenerated }}</el-descriptions-item>
              <el-descriptions-item label="No ZIP Generation">{{ workspace.zipGenerated }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else>
            <div class="section-title">Export Guardrails</div>
            <div class="guardrail-grid">
              <el-tag v-for="item in workspace.guardrails" :key="item" round type="info">{{ item }}</el-tag>
            </div>
            <el-descriptions class="inner-gap" :column="3" border>
              <el-descriptions-item label="No DB Write">{{ workspace.dbWrite }}</el-descriptions-item>
              <el-descriptions-item label="No Evidence Write">{{ workspace.evidenceWrite }}</el-descriptions-item>
              <el-descriptions-item label="No Production Activation">{{ workspace.productionActivation }}</el-descriptions-item>
              <el-descriptions-item label="No EDGE Command Execution">{{ workspace.edgeCommandExecution }}</el-descriptions-item>
              <el-descriptions-item label="No LINK Command Execution">{{ workspace.linkCommandExecution }}</el-descriptions-item>
              <el-descriptions-item label="No Runtime Activation">{{ workspace.runtimeActivation }}</el-descriptions-item>
            </el-descriptions>
          </template>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<style scoped>
.reports-r13-page {
  min-height: 100%;
  padding: 20px;
  background: #f4fbf8;
  color: #203331;
}

.workspace-head,
.target-strip,
.metric-card,
.workspace-tabs {
  border: 1px solid #d6ebe5;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 12px 28px rgb(34 82 73 / 8%);
}

.workspace-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
}

.workspace-head h1 {
  margin: 4px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.eyebrow,
.summary,
.metric-card span,
.metric-card em,
.report-callouts {
  margin: 0;
  color: #647b76;
}

.eyebrow {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

.badge-stack,
.guardrail-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.section-gap {
  margin-top: 16px;
}

.inner-gap,
.report-callouts {
  margin-top: 16px;
}

.target-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 14px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 12px;
}

.metric-card {
  padding: 14px;
}

.metric-card strong {
  display: block;
  margin: 8px 0 4px;
  color: #007f73;
  font-size: 22px;
}

.metric-card em {
  font-style: normal;
}

.workspace-tabs {
  padding: 14px;
}

.section-title {
  margin: 0 0 12px;
  color: #123f3a;
  font-size: 18px;
  font-weight: 700;
}

.pack-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.pack-list li {
  border: 1px solid #d6ebe5;
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}

@media (max-width: 820px) {
  .workspace-head,
  .target-strip {
    display: block;
  }

  .badge-stack {
    justify-content: flex-start;
    margin-top: 12px;
  }
}
</style>
