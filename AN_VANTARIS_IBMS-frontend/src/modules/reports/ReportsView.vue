<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getReportsGaR13Workspace, type ReportsGaR13Workspace } from '@/services/api/reports'

type CustomerSection = {
  title: string
  subtitle: string
  primaryAction: string
  metrics: Array<{ label: string; value: string; note: string }>
  rows: Array<{ item: string; focus: string; status: string }>
}

const route = useRoute()
const customerUnavailableMessage = 'Live service is temporarily unavailable. Showing the latest available operational view.'

const customerSections: Record<string, CustomerSection> = {
  'operations-reports': {
    title: 'Operations Reports',
    subtitle: 'Operations report view across daily situation, service impact, evidence, and customer-ready summaries.',
    primaryAction: 'Open operations report',
    metrics: [
      { label: 'Operations Reports', value: '9', note: 'Reports available for operations review' },
      { label: 'Ready Exports', value: '6', note: 'Exports prepared for review' },
      { label: 'Evidence Bundles', value: '14', note: 'Evidence-linked report bundles' },
      { label: 'Open Reviews', value: '3', note: 'Reports requiring review' },
    ],
    rows: [
      { item: 'Review daily operations report', focus: 'Situation, actions and evidence', status: 'Ready' },
      { item: 'Open service impact summary', focus: 'Customer impact and mitigation', status: 'Review' },
      { item: 'Prepare operations export', focus: 'Customer-ready report pack', status: 'Ready' },
    ],
  },
  'alarm-reports': {
    title: 'Alarm Reports',
    subtitle: 'Alarm reporting view for critical alarms, repeated alarms, acknowledgement, and evidence export.',
    primaryAction: 'Open alarm report',
    metrics: [
      { label: 'Alarm Reports', value: '7', note: 'Alarm reports available' },
      { label: 'Critical Reports', value: '3', note: 'Critical alarm reports ready' },
      { label: 'Repeated Alarm Items', value: '12', note: 'Items included in repeated alarm review' },
      { label: 'Evidence Links', value: '24', note: 'Alarm evidence links' },
    ],
    rows: [
      { item: 'Review critical alarm report', focus: 'Priority and acknowledgement posture', status: 'Ready' },
      { item: 'Open repeated alarm analysis', focus: 'Repeated sources and systems', status: 'Review' },
      { item: 'Export alarm evidence', focus: 'Evidence-backed alarm package', status: 'Ready' },
    ],
  },
  'fault-reports': {
    title: 'Fault Reports',
    subtitle: 'Fault reporting across open faults, impact, root cause review, work order linkage, and evidence.',
    primaryAction: 'Open fault report',
    metrics: [
      { label: 'Fault Reports', value: '6', note: 'Fault reports available' },
      { label: 'Open Faults', value: '26', note: 'Faults represented in reports' },
      { label: 'WO Linked', value: '18', note: 'Faults linked to work orders' },
      { label: 'Evidence Ready', value: '21', note: 'Fault evidence ready' },
    ],
    rows: [
      { item: 'Review fault impact report', focus: 'Impact and service exposure', status: 'Ready' },
      { item: 'Open root cause evidence', focus: 'RCA and supporting evidence', status: 'Review' },
      { item: 'Prepare fault export', focus: 'Customer-ready fault package', status: 'Ready' },
    ],
  },
  'maintenance-reports': {
    title: 'Maintenance Reports',
    subtitle: 'Maintenance report view for work orders, preventive plans, SLA aging, assignments, and closure evidence.',
    primaryAction: 'Open maintenance report',
    metrics: [
      { label: 'Maintenance Reports', value: '8', note: 'Maintenance reports available' },
      { label: 'Open WOs', value: '42', note: 'Work orders represented' },
      { label: 'PM Due', value: '14', note: 'Preventive maintenance items included' },
      { label: 'Closure Evidence', value: '8', note: 'Closure evidence packages' },
    ],
    rows: [
      { item: 'Review maintenance summary', focus: 'Work order status and SLA', status: 'Ready' },
      { item: 'Open PM report', focus: 'Preventive maintenance schedule', status: 'Ready' },
      { item: 'Prepare closure evidence report', focus: 'Customer closure summary', status: 'Review' },
    ],
  },
  'energy-reports': {
    title: 'Energy Reports',
    subtitle: 'Energy report view across consumption, exceptions, ESG metrics, baselines, and optimization actions.',
    primaryAction: 'Open energy report',
    metrics: [
      { label: 'Energy Reports', value: '6', note: 'Energy reports available' },
      { label: 'Exceptions', value: '13', note: 'Energy exceptions represented' },
      { label: 'ESG Links', value: '19', note: 'ESG-linked evidence records' },
      { label: 'Savings Items', value: '12', note: 'Savings estimates included' },
    ],
    rows: [
      { item: 'Review energy summary', focus: 'Consumption and exception trends', status: 'Ready' },
      { item: 'Open ESG evidence', focus: 'Sustainability evidence bundle', status: 'Ready' },
      { item: 'Prepare savings report', focus: 'Optimization opportunity package', status: 'Review' },
    ],
  },
  'compliance-reports': {
    title: 'Compliance Reports',
    subtitle: 'Compliance reporting across controls, evidence, audit readiness, exceptions, and customer handoff.',
    primaryAction: 'Open compliance report',
    metrics: [
      { label: 'Compliance Reports', value: '5', note: 'Compliance reports available' },
      { label: 'Controls Tracked', value: '36', note: 'Controls represented' },
      { label: 'Open Exceptions', value: '3', note: 'Exceptions requiring review' },
      { label: 'Evidence Ready', value: '29', note: 'Controls with evidence records' },
    ],
    rows: [
      { item: 'Review compliance report', focus: 'Controls and evidence status', status: 'Ready' },
      { item: 'Open exception evidence', focus: 'Exception review and mitigation', status: 'Review' },
      { item: 'Prepare audit package', focus: 'Audit-ready report export', status: 'Ready' },
    ],
  },
  'customer-delivery-reports': {
    title: 'Customer Delivery Reports',
    subtitle: 'Customer delivery reports for handoff packages, acceptance items, evidence, risks, and signoff.',
    primaryAction: 'Open delivery report',
    metrics: [
      { label: 'Delivery Reports', value: '7', note: 'Customer delivery reports available' },
      { label: 'Acceptance Items', value: '12', note: 'Acceptance items represented' },
      { label: 'Evidence Packs', value: '10', note: 'Evidence packs linked' },
      { label: 'Open Risks', value: '4', note: 'Delivery risks requiring review' },
    ],
    rows: [
      { item: 'Review customer delivery report', focus: 'Acceptance and handoff status', status: 'Ready' },
      { item: 'Open handoff evidence', focus: 'Customer evidence package', status: 'Ready' },
      { item: 'Prepare signoff report', focus: 'Customer-ready signoff pack', status: 'Review' },
    ],
  },
  'pdf-export': {
    title: 'PDF Export',
    subtitle: 'PDF export queue for customer reports, evidence bundles, audit packs, and handoff packages.',
    primaryAction: 'Review PDF queue',
    metrics: [
      { label: 'PDF Packages', value: '11', note: 'PDF packages prepared' },
      { label: 'Customer Packs', value: '5', note: 'Customer packages in queue' },
      { label: 'Evidence Packs', value: '4', note: 'Evidence packages queued' },
      { label: 'Open Reviews', value: '2', note: 'Exports needing review' },
    ],
    rows: [
      { item: 'Review PDF export queue', focus: 'Report package readiness', status: 'Ready' },
      { item: 'Open customer PDF package', focus: 'Customer handoff package', status: 'Ready' },
      { item: 'Check export audit record', focus: 'Export evidence and audit', status: 'Ready' },
    ],
  },
  'excel-export': {
    title: 'Excel Export',
    subtitle: 'Excel export queue for tabular operational reports, maintenance data, energy data, and audit lists.',
    primaryAction: 'Review Excel queue',
    metrics: [
      { label: 'Excel Packages', value: '9', note: 'Excel packages prepared' },
      { label: 'Data Tables', value: '18', note: 'Tables ready for export' },
      { label: 'Evidence Links', value: '12', note: 'Exports linked to evidence' },
      { label: 'Open Reviews', value: '2', note: 'Exports needing review' },
    ],
    rows: [
      { item: 'Review Excel export queue', focus: 'Table exports and data coverage', status: 'Ready' },
      { item: 'Open maintenance export', focus: 'Work order and SLA rows', status: 'Ready' },
      { item: 'Check export audit trail', focus: 'Export event evidence', status: 'Ready' },
    ],
  },
  'evidence-bundle': {
    title: 'Evidence Bundle',
    subtitle: 'Evidence bundle export view for UCDE traceability, report support, audit review, and customer handoff.',
    primaryAction: 'Review evidence bundle',
    metrics: [
      { label: 'Evidence Bundles', value: '14', note: 'Evidence bundles prepared' },
      { label: 'Customer Bundles', value: '7', note: 'Customer-ready evidence bundles' },
      { label: 'Audit Bundles', value: '5', note: 'Audit-ready bundles' },
      { label: 'Open Reviews', value: '4', note: 'Bundles requiring review' },
    ],
    rows: [
      { item: 'Review evidence bundles', focus: 'Traceability and report support', status: 'Ready' },
      { item: 'Open customer evidence bundle', focus: 'Customer handoff package', status: 'Ready' },
      { item: 'Prepare audit evidence bundle', focus: 'Audit-ready export package', status: 'Review' },
    ],
  },
  'customer-handoff-package': {
    title: 'Customer Handoff Package',
    subtitle: 'Customer handoff package view across reports, evidence, acceptance items, risks, and export readiness.',
    primaryAction: 'Review handoff package',
    metrics: [
      { label: 'Handoff Packages', value: '5', note: 'Customer handoff packages prepared' },
      { label: 'Reports Included', value: '18', note: 'Reports linked to packages' },
      { label: 'Evidence Included', value: '32', note: 'Evidence records linked' },
      { label: 'Open Risks', value: '4', note: 'Risks requiring review' },
    ],
    rows: [
      { item: 'Review handoff package', focus: 'Reports, evidence and acceptance state', status: 'Ready' },
      { item: 'Open risk items', focus: 'Delivery risks and mitigations', status: 'Review' },
      { item: 'Prepare customer export', focus: 'Customer-ready package', status: 'Ready' },
    ],
  },
  'scheduled-exports': {
    title: 'Scheduled Exports',
    subtitle: 'Scheduled export view for recurring reports, customer packages, audit exports, and owner review.',
    primaryAction: 'Review schedule',
    metrics: [
      { label: 'Scheduled Exports', value: '8', note: 'Exports scheduled for review' },
      { label: 'Customer Exports', value: '4', note: 'Customer exports scheduled' },
      { label: 'Audit Exports', value: '2', note: 'Audit exports scheduled' },
      { label: 'Owner Reviews', value: '3', note: 'Schedules requiring owner review' },
    ],
    rows: [
      { item: 'Review export schedule', focus: 'Frequency and owner state', status: 'Ready' },
      { item: 'Open customer export schedule', focus: 'Customer handoff cadence', status: 'Review' },
      { item: 'Check export audit trail', focus: 'Scheduled export evidence', status: 'Ready' },
    ],
  },
  'export-history': {
    title: 'Export History',
    subtitle: 'Export history view across report packages, evidence bundles, customer handoff, and audit records.',
    primaryAction: 'Review export history',
    metrics: [
      { label: 'Export Events', value: '28', note: 'Export events in history' },
      { label: 'Customer Events', value: '11', note: 'Customer package exports' },
      { label: 'Evidence Events', value: '9', note: 'Evidence bundle exports' },
      { label: 'Audit Events', value: '8', note: 'Audit export records' },
    ],
    rows: [
      { item: 'Review export history', focus: 'Export events and packages', status: 'Ready' },
      { item: 'Open customer export event', focus: 'Customer handoff evidence', status: 'Ready' },
      { item: 'Check audit export record', focus: 'Audit trail and evidence', status: 'Ready' },
    ],
  },
  'export-audit': {
    title: 'Export Audit',
    subtitle: 'Export audit view across export requests, package contents, evidence records, and review status.',
    primaryAction: 'Review export audit',
    metrics: [
      { label: 'Audit Records', value: '28', note: 'Export audit records' },
      { label: 'Open Reviews', value: '3', note: 'Audit records requiring review' },
      { label: 'Evidence Links', value: '22', note: 'Audit records with evidence' },
      { label: 'Ready Packages', value: '11', note: 'Packages ready for customer review' },
    ],
    rows: [
      { item: 'Review export audit', focus: 'Request, package and evidence records', status: 'Ready' },
      { item: 'Open audit review items', focus: 'Export records needing review', status: 'Review' },
      { item: 'Prepare audit report', focus: 'Export audit package', status: 'Ready' },
    ],
  },
}

const fallbackCustomerSection = customerSections['operations-reports']

function normalizeL3Id(value: unknown, defaultKey: string): string {
  const raw = typeof value === 'string' && value ? value : defaultKey
  const normalized = raw.replace(/-\d+$/, '')
  return customerSections[normalized] ? normalized : defaultKey
}

const activeCustomerSection = computed(() => customerSections[normalizeL3Id(route.query.l3, 'operations-reports')] ?? fallbackCustomerSection)

const tabs = ['Overview', 'Report Library', 'Customer Report Pack', 'Engineer Report Pack', 'Admin Report Pack', 'UMMS Reports', 'UHMI Reports', 'UCDE Evidence Reports', 'Customer Delivery Reports', 'Foundation Diagnostics Reports', 'Export Center', 'Guardrails']
const activeTab = ref('Overview')
const loading = ref(false)
const error = ref('')
const workspace = ref<ReportsGaR13Workspace | null>(null)

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
    error.value = customerUnavailableMessage
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
        <p class="eyebrow">Selected reports section</p>
        <h1>{{ activeCustomerSection.title }}</h1>
        <p class="summary">{{ activeCustomerSection.subtitle }}</p>
      </div>
      <el-button type="primary" plain>{{ activeCustomerSection.primaryAction }}</el-button>
    </header>

    <el-alert v-if="error" class="section-gap" type="warning" show-icon :closable="false" :title="error" />

    <template v-if="workspace">
      <section class="card-grid section-gap">
        <article v-for="metric in activeCustomerSection.metrics" :key="metric.label" class="metric-card">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <em>{{ metric.note }}</em>
        </article>
      </section>

      <el-table :data="activeCustomerSection.rows" stripe border class="section-gap">
        <el-table-column prop="item" label="Action" min-width="240" />
        <el-table-column prop="focus" label="Focus Area" min-width="260" />
        <el-table-column prop="status" label="Status" min-width="140" />
      </el-table>

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
