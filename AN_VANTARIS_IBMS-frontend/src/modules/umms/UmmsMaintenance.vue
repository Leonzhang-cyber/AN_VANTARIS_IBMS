<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ApiError } from '@/services/api/errors'
import { getUmmsGaR2Workspace, type UmmsGaR2Workspace, type UmmsGaR2WorkOrder } from '@/services/api/umms'

type CustomerSection = {
  title: string
  subtitle: string
  primaryAction: string
  targetTab: string
  metrics: Array<{ label: string; value: string; note: string }>
  rows: Array<{ item: string; focus: string; status: string }>
}

const route = useRoute()
const customerUnavailableMessage = 'Live service is temporarily unavailable. Showing the latest available operational view.'

const tabs = [
  'Overview',
  'Work Orders',
  'Preventive',
  'Predictive',
  'Assignments',
  'SLA & Aging',
  'Evidence',
  'Reports',
]

const loading = ref(false)
const apiError = ref('')
const activeTab = ref('Overview')
const workspace = ref<UmmsGaR2Workspace | null>(null)
const reportToast = ref('')

const customerSections: Record<string, CustomerSection> = {
  'open-work-orders': {
    title: 'Open Work Orders',
    subtitle: 'Open maintenance queue across assets, systems, SLA risk, engineer assignment, and evidence status.',
    primaryAction: 'Review open work orders',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Open WOs', value: '42', note: 'Open maintenance work orders' },
      { label: 'High Priority', value: '11', note: 'Critical and high priority queue' },
      { label: 'SLA Risk', value: '7', note: 'Work orders approaching breach' },
      { label: 'Evidence Pending', value: '8', note: 'Closure evidence under review' },
    ],
    rows: [
      { item: 'Review open work order queue', focus: 'Status, asset and SLA due', status: 'Active' },
      { item: 'Open high priority work orders', focus: 'Critical service impact', status: 'High' },
      { item: 'Check closure evidence', focus: 'UCDE evidence linkage', status: 'Review' },
    ],
  },
  'assigned-work-orders': {
    title: 'Assigned Work Orders',
    subtitle: 'Engineer assignment view across workload, discipline, shift availability, escalation owner, and active tasks.',
    primaryAction: 'Review assignments',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Assigned WOs', value: '27', note: 'Work orders assigned to teams' },
      { label: 'Engineers', value: '9', note: 'Engineers with active workload' },
      { label: 'Shift Coverage', value: '3', note: 'Shifts represented in workload view' },
      { label: 'Escalations', value: '4', note: 'Assignments requiring escalation owner' },
    ],
    rows: [
      { item: 'Review engineer workload', focus: 'Assigned work orders and skills', status: 'Active' },
      { item: 'Open shift availability', focus: 'Coverage and escalation owner', status: 'Ready' },
      { item: 'Prepare assignment evidence', focus: 'Workload and shift evidence', status: 'Ready' },
    ],
  },
  'emergency-work-orders': {
    title: 'Emergency Work Orders',
    subtitle: 'Emergency maintenance queue for critical assets, service impact, engineer response, and evidence trail.',
    primaryAction: 'Review emergency queue',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Emergency WOs', value: '5', note: 'Emergency work orders under review' },
      { label: 'Critical Assets', value: '4', note: 'Assets with service impact' },
      { label: 'SLA At Risk', value: '5', note: 'Emergency SLA exposure' },
      { label: 'Evidence Linked', value: '5', note: 'Emergency records with evidence' },
    ],
    rows: [
      { item: 'Review emergency queue', focus: 'Criticality and SLA due', status: 'High' },
      { item: 'Open impacted assets', focus: 'Asset and service context', status: 'Active' },
      { item: 'Prepare emergency evidence', focus: 'Evidence trail and closure state', status: 'Ready' },
    ],
  },
  'fault-linked-work-orders': {
    title: 'Fault-linked Work Orders',
    subtitle: 'Work orders created from alarms and faults with source event, impacted asset, and evidence linkage.',
    primaryAction: 'Review fault-linked WOs',
    targetTab: 'Evidence',
    metrics: [
      { label: 'Fault-linked WOs', value: '18', note: 'Work orders tied to faults' },
      { label: 'Critical Faults', value: '6', note: 'Faults with critical impact' },
      { label: 'Asset Links', value: '18', note: 'Work orders linked to assets' },
      { label: 'Evidence Ready', value: '15', note: 'Evidence-linked records' },
    ],
    rows: [
      { item: 'Review fault-linked queue', focus: 'Fault source and work order state', status: 'Active' },
      { item: 'Open source fault evidence', focus: 'Alarm / fault trace', status: 'Ready' },
      { item: 'Prepare closure record', focus: 'Work order evidence chain', status: 'Review' },
    ],
  },
  'preventive-work-orders': {
    title: 'Preventive Work Orders',
    subtitle: 'Preventive maintenance work orders by plan, frequency, due date, compliance, and checklist readiness.',
    primaryAction: 'Review preventive WOs',
    targetTab: 'Preventive',
    metrics: [
      { label: 'Preventive WOs', value: '14', note: 'Preventive work orders due soon' },
      { label: 'Due Today', value: '7', note: 'Preventive work scheduled today' },
      { label: 'Compliance Risk', value: '3', note: 'PM items needing review' },
      { label: 'Checklist Ready', value: '11', note: 'PM checklists ready' },
    ],
    rows: [
      { item: 'Review preventive queue', focus: 'Schedule and compliance state', status: 'Ready' },
      { item: 'Open PM checklist', focus: 'Checklist readiness', status: 'Active' },
      { item: 'Prepare PM evidence', focus: 'Preventive evidence package', status: 'Ready' },
    ],
  },
  'corrective-work-orders': {
    title: 'Corrective Work Orders',
    subtitle: 'Corrective maintenance view across issue source, technician action, parts readiness, and closure review.',
    primaryAction: 'Review corrective WOs',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Corrective WOs', value: '16', note: 'Corrective work orders open' },
      { label: 'Parts Watch', value: '5', note: 'Items requiring materials readiness' },
      { label: 'Engineer Updates', value: '12', note: 'Engineer updates recorded' },
      { label: 'Closure Review', value: '6', note: 'Corrective records awaiting review' },
    ],
    rows: [
      { item: 'Review corrective queue', focus: 'Source event and action status', status: 'Active' },
      { item: 'Open parts readiness', focus: 'Materials and vendor notes', status: 'Review' },
      { item: 'Prepare corrective closure', focus: 'Evidence and closure records', status: 'Ready' },
    ],
  },
  'work-order-detail': {
    title: 'Work Order Detail',
    subtitle: 'Focused work order context with asset, system, location, source fault, engineer, SLA, and evidence.',
    primaryAction: 'Review work order detail',
    targetTab: 'Work Orders',
    metrics: [
      { label: 'Context Fields', value: '12', note: 'Core customer-visible fields' },
      { label: 'Evidence Items', value: '5', note: 'Evidence linked to selected WO' },
      { label: 'SLA Fields', value: '4', note: 'SLA and aging indicators' },
      { label: 'Action Rows', value: '3', note: 'Next review actions' },
    ],
    rows: [
      { item: 'Review work order detail', focus: 'Asset, system and source fault', status: 'Ready' },
      { item: 'Open engineer update', focus: 'Engineer action and status', status: 'Active' },
      { item: 'Check closure evidence', focus: 'Evidence and approval record', status: 'Review' },
    ],
  },
  'closure-evidence': {
    title: 'Closure Evidence',
    subtitle: 'Closure evidence view for completed work, approval records, attachments, and audit traceability.',
    primaryAction: 'Review closure evidence',
    targetTab: 'Evidence',
    metrics: [
      { label: 'Closure Packages', value: '8', note: 'Closure packages under review' },
      { label: 'Attachments', value: '21', note: 'Attachments linked to closure records' },
      { label: 'Approval Records', value: '8', note: 'Closure approvals represented' },
      { label: 'Audit Ready', value: '6', note: 'Closure packages ready for audit' },
    ],
    rows: [
      { item: 'Review closure evidence', focus: 'Work order closure trail', status: 'Review' },
      { item: 'Open attachments', focus: 'Photos, notes and records', status: 'Ready' },
      { item: 'Prepare closure export', focus: 'Customer-ready evidence package', status: 'Ready' },
    ],
  },
  'pm-calendar': {
    title: 'PM Calendar',
    subtitle: 'Preventive maintenance calendar across due dates, frequency, compliance state, and checklist readiness.',
    primaryAction: 'Review PM calendar',
    targetTab: 'Preventive',
    metrics: [
      { label: 'PM Tasks', value: '24', note: 'Scheduled preventive tasks' },
      { label: 'Due Today', value: '7', note: 'PM tasks due today' },
      { label: 'Due This Week', value: '14', note: 'PM tasks due this week' },
      { label: 'Compliance Watch', value: '3', note: 'PM items requiring review' },
    ],
    rows: [
      { item: 'Review PM calendar', focus: 'Due dates and frequency', status: 'Ready' },
      { item: 'Open due-today PM', focus: 'Today schedule and owners', status: 'Active' },
      { item: 'Prepare PM report', focus: 'Compliance and evidence', status: 'Ready' },
    ],
  },
  'pm-templates': {
    title: 'PM Templates',
    subtitle: 'Preventive maintenance templates with checklist readiness, asset group coverage, and evidence rules.',
    primaryAction: 'Review PM templates',
    targetTab: 'Preventive',
    metrics: [
      { label: 'Templates', value: '18', note: 'PM templates available' },
      { label: 'Checklist Ready', value: '15', note: 'Templates with checklist coverage' },
      { label: 'Asset Groups', value: '9', note: 'Asset groups covered' },
      { label: 'Evidence Rules', value: '12', note: 'Templates with evidence rules' },
    ],
    rows: [
      { item: 'Review PM templates', focus: 'Checklist and asset coverage', status: 'Ready' },
      { item: 'Open checklist readiness', focus: 'Template completeness', status: 'Review' },
      { item: 'Prepare template evidence', focus: 'Evidence rules and audit trail', status: 'Ready' },
    ],
  },
  'pm-schedule': {
    title: 'PM Schedule',
    subtitle: 'Preventive maintenance schedule by next due date, asset group, compliance status, and owner readiness.',
    primaryAction: 'Review PM schedule',
    targetTab: 'Preventive',
    metrics: [
      { label: 'Scheduled PM', value: '24', note: 'PM items on schedule' },
      { label: 'Next Due', value: '7', note: 'Items due in the next operating day' },
      { label: 'Owner Assigned', value: '21', note: 'PM items with owner assignment' },
      { label: 'Evidence Ready', value: '18', note: 'PM evidence records ready' },
    ],
    rows: [
      { item: 'Review PM schedule', focus: 'Due date and assignment', status: 'Ready' },
      { item: 'Open owner gaps', focus: 'Unassigned PM items', status: 'Review' },
      { item: 'Prepare schedule evidence', focus: 'PM schedule evidence package', status: 'Ready' },
    ],
  },
  'engineer-calendar': {
    title: 'Engineer Calendar',
    subtitle: 'Engineer workload calendar with assignments, skills, shift availability, and escalation ownership.',
    primaryAction: 'Review engineer calendar',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Engineers', value: '9', note: 'Engineers represented' },
      { label: 'Assigned WOs', value: '27', note: 'Assigned work orders' },
      { label: 'Shift Conflicts', value: '2', note: 'Calendar conflicts requiring review' },
      { label: 'Escalations', value: '4', note: 'Items requiring escalation owner' },
    ],
    rows: [
      { item: 'Review engineer calendar', focus: 'Shift and workload coverage', status: 'Ready' },
      { item: 'Open assignment load', focus: 'Engineer capacity and skills', status: 'Active' },
      { item: 'Prepare workload evidence', focus: 'Assignment evidence record', status: 'Ready' },
    ],
  },
  'assignment-load': {
    title: 'Assignment Load',
    subtitle: 'Assignment load view for engineer capacity, assigned work orders, skill coverage, and SLA exposure.',
    primaryAction: 'Review assignment load',
    targetTab: 'Assignments',
    metrics: [
      { label: 'Assigned WOs', value: '27', note: 'Assigned work order load' },
      { label: 'High Load Engineers', value: '3', note: 'Engineers with elevated workload' },
      { label: 'Skill Gaps', value: '2', note: 'Assignments needing skill review' },
      { label: 'SLA Exposure', value: '6', note: 'Assigned items at SLA risk' },
    ],
    rows: [
      { item: 'Review load balance', focus: 'Engineer capacity and SLA risk', status: 'Review' },
      { item: 'Open skill coverage', focus: 'Discipline and availability', status: 'Active' },
      { item: 'Prepare assignment report', focus: 'Workload evidence', status: 'Ready' },
    ],
  },
  'sla-dashboard': {
    title: 'SLA Dashboard',
    subtitle: 'SLA dashboard for due soon, overdue work orders, aging buckets, MTTR, response, and escalation.',
    primaryAction: 'Review SLA dashboard',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'SLA At Risk', value: '7', note: 'Items approaching breach' },
      { label: 'Overdue', value: '3', note: 'Work orders past SLA due' },
      { label: 'Due Today', value: '9', note: 'Items due today' },
      { label: 'Avg MTTR', value: '3.8h', note: 'Rolling maintenance MTTR' },
    ],
    rows: [
      { item: 'Review SLA dashboard', focus: 'Due soon and overdue items', status: 'Active' },
      { item: 'Open escalation queue', focus: 'Supervisor review items', status: 'High' },
      { item: 'Prepare SLA report', focus: 'SLA evidence and response time', status: 'Ready' },
    ],
  },
  'breach-risk': {
    title: 'Breach Risk',
    subtitle: 'Breach risk queue for work orders nearing SLA breach, escalation owners, and customer impact.',
    primaryAction: 'Review breach risk',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'Breach Risk', value: '7', note: 'Items nearing SLA breach' },
      { label: 'Critical Risk', value: '2', note: 'Critical breach risk items' },
      { label: 'Escalation Owners', value: '5', note: 'Assigned escalation owners' },
      { label: 'Evidence Pending', value: '4', note: 'Risk items needing evidence' },
    ],
    rows: [
      { item: 'Review breach risk queue', focus: 'SLA due and owner readiness', status: 'High' },
      { item: 'Open customer impact items', focus: 'Service risk and mitigation', status: 'Review' },
      { item: 'Prepare breach evidence', focus: 'SLA and action evidence', status: 'Ready' },
    ],
  },
  'escalation-queue': {
    title: 'Escalation Queue',
    subtitle: 'Escalation queue for high-risk work orders, owners, customer impact, and closure evidence.',
    primaryAction: 'Review escalation queue',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'Escalations', value: '8', note: 'Escalation items open' },
      { label: 'High Priority', value: '5', note: 'High priority escalation items' },
      { label: 'Owner Assigned', value: '7', note: 'Items with escalation owner' },
      { label: 'Evidence Ready', value: '5', note: 'Escalations with evidence' },
    ],
    rows: [
      { item: 'Review escalation queue', focus: 'Priority and owner state', status: 'Active' },
      { item: 'Open high-priority escalation', focus: 'Customer impact and SLA', status: 'High' },
      { item: 'Prepare escalation evidence', focus: 'Action and approval trail', status: 'Ready' },
    ],
  },
  mttr: {
    title: 'MTTR',
    subtitle: 'Mean time to repair view across work order closure, system category, team response, and evidence.',
    primaryAction: 'Review MTTR',
    targetTab: 'SLA & Aging',
    metrics: [
      { label: 'Average MTTR', value: '3.8h', note: 'Rolling maintenance MTTR' },
      { label: 'Critical MTTR', value: '2.4h', note: 'Critical queue repair average' },
      { label: 'Improving Systems', value: '6', note: 'Systems trending better' },
      { label: 'Review Items', value: '3', note: 'MTTR outliers for review' },
    ],
    rows: [
      { item: 'Review MTTR trend', focus: 'System and priority performance', status: 'Ready' },
      { item: 'Open MTTR outliers', focus: 'Repair delays and root cause', status: 'Review' },
      { item: 'Prepare MTTR report', focus: 'Customer maintenance performance', status: 'Ready' },
    ],
  },
  mtbf: {
    title: 'MTBF',
    subtitle: 'Mean time between failures view for repeated failures, reliability, asset health, and improvement actions.',
    primaryAction: 'Review MTBF',
    targetTab: 'Predictive',
    metrics: [
      { label: 'MTBF Watchlist', value: '9', note: 'Assets needing reliability review' },
      { label: 'Repeated Failures', value: '6', note: 'Assets with repeated failures' },
      { label: 'Reliability Actions', value: '5', note: 'Improvement actions in progress' },
      { label: 'Evidence Ready', value: '8', note: 'Reliability records with evidence' },
    ],
    rows: [
      { item: 'Review MTBF watchlist', focus: 'Repeated failures and reliability', status: 'Review' },
      { item: 'Open reliability actions', focus: 'Improvement plan status', status: 'Active' },
      { item: 'Prepare reliability evidence', focus: 'Asset reliability report', status: 'Ready' },
    ],
  },
  'repeated-failures': {
    title: 'Repeated Failures',
    subtitle: 'Repeated failure view for high-repeat assets, fault linkage, maintenance actions, and evidence.',
    primaryAction: 'Review repeated failures',
    targetTab: 'Predictive',
    metrics: [
      { label: 'Repeated Failures', value: '6', note: 'Repeated failure cases open' },
      { label: 'High Repeat Assets', value: '4', note: 'Assets with repeated patterns' },
      { label: 'WO Linked', value: '6', note: 'Repeated failures linked to work orders' },
      { label: 'Evidence Ready', value: '5', note: 'Repeated failure evidence records' },
    ],
    rows: [
      { item: 'Review repeated failure queue', focus: 'Asset and fault pattern', status: 'Review' },
      { item: 'Open reliability work orders', focus: 'Corrective and preventive actions', status: 'Active' },
      { item: 'Prepare repeated failure evidence', focus: 'RCA and maintenance evidence', status: 'Ready' },
    ],
  },
  'predictive-risk': {
    title: 'Predictive Risk',
    subtitle: 'Predictive maintenance risk view across asset health, failure risk, anomaly summary, and recommended action.',
    primaryAction: 'Review predictive risk',
    targetTab: 'Predictive',
    metrics: [
      { label: 'Predictive Alerts', value: '5', note: 'Predictive alerts under review' },
      { label: 'High Severity', value: '2', note: 'High-severity predictive risks' },
      { label: 'Actions Recommended', value: '5', note: 'Recommended maintenance actions' },
      { label: 'Evidence Linked', value: '4', note: 'Predictive evidence records' },
    ],
    rows: [
      { item: 'Review predictive risk', focus: 'Asset health and anomaly summary', status: 'Active' },
      { item: 'Open recommended actions', focus: 'Maintenance plan alignment', status: 'Review' },
      { item: 'Prepare predictive evidence', focus: 'Risk evidence and confidence', status: 'Ready' },
    ],
  },
}

const fallbackCustomerSection = customerSections['open-work-orders']

function normalizeL3Id(value: unknown, defaultKey: string): string {
  const raw = typeof value === 'string' && value ? value : defaultKey
  const normalized = raw.replace(/-\d+$/, '')
  return customerSections[normalized] ? normalized : defaultKey
}

const activeCustomerSection = computed(() => customerSections[normalizeL3Id(route.query.l3, 'open-work-orders')] ?? fallbackCustomerSection)

const filters = reactive({
  status: '',
  priority: '',
  system: '',
  engineer: '',
  slaRisk: '',
})

const statusOptions = computed(() => uniqueValues('status'))
const priorityOptions = computed(() => uniqueValues('priority'))
const systemOptions = computed(() => uniqueValues('systemName'))
const engineerOptions = computed(() => uniqueValues('assignedEngineer'))
const slaRiskOptions = computed(() => uniqueValues('slaRisk'))

const filteredWorkOrders = computed(() => {
  const rows = workspace.value?.workOrders ?? []
  return rows.filter((row) => {
    return (!filters.status || row.status === filters.status)
      && (!filters.priority || row.priority === filters.priority)
      && (!filters.system || row.systemName === filters.system)
      && (!filters.engineer || row.assignedEngineer === filters.engineer)
      && (!filters.slaRisk || row.slaRisk === filters.slaRisk)
  })
})

const assignmentRows = computed(() => workspace.value?.engineerDispatch ?? [])
const preventiveRows = computed(() => workspace.value?.preventiveMaintenancePlans ?? [])
const predictiveRows = computed(() => workspace.value?.predictiveMaintenance ?? [])
const evidenceRows = computed(() => workspace.value?.evidenceTimeline ?? [])
const reportRows = computed(() => workspace.value?.reportLinkage ?? [])

function uniqueValues(field: keyof UmmsGaR2WorkOrder): string[] {
  const rows = workspace.value?.workOrders ?? []
  return [...new Set(rows.map((row) => String(row[field] ?? '')).filter(Boolean))].sort()
}

function tagType(value: string): 'success' | 'warning' | 'danger' | 'info' | 'primary' {
  const normalized = value.toLowerCase()
  if (normalized.includes('critical') || normalized.includes('overdue') || normalized.includes('at risk')) return 'danger'
  if (normalized.includes('high') || normalized.includes('due today') || normalized.includes('watch')) return 'warning'
  if (normalized.includes('closed') || normalized.includes('normal') || normalized.includes('on track')) return 'success'
  return 'info'
}

function openReport(report: string) {
  reportToast.value = `${report} view prepared for read-only review.`
}

async function loadWorkspace() {
  loading.value = true
  apiError.value = ''
  try {
    workspace.value = await getUmmsGaR2Workspace()
  } catch (error) {
    apiError.value = error instanceof ApiError ? error.message : 'UMMS workspace data unavailable.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadWorkspace()
})

watch(activeCustomerSection, (section) => {
  activeTab.value = section.targetTab
}, { immediate: true })
</script>

<template>
  <section class="umms-page" v-loading="loading">
    <header class="workspace-head">
      <div>
        <p class="eyebrow">Selected maintenance section</p>
        <h1>{{ activeCustomerSection.title }}</h1>
        <p class="summary">{{ activeCustomerSection.subtitle }}</p>
      </div>
      <el-button type="primary" plain>{{ activeCustomerSection.primaryAction }}</el-button>
    </header>

    <el-alert
      v-if="apiError"
      class="section-gap"
      type="warning"
      show-icon
      :closable="false"
      :title="customerUnavailableMessage"
    />

    <template v-if="workspace">
      <section class="summary-grid section-gap">
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

      <section class="summary-grid section-gap">
        <article v-for="card in workspace.overviewCards" :key="card.label" class="metric-card">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <em>{{ card.status }}</em>
        </article>
      </section>

      <section class="metadata-strip section-gap">
        <div>
          <span>L1 / L2</span>
          <strong>{{ workspace.menu.l1 }} / {{ workspace.menu.l2.join(', ') }}</strong>
        </div>
        <div>
          <span>L3 content tabs</span>
          <strong>{{ tabs.join(' · ') }}</strong>
        </div>
      </section>

      <el-tabs v-model="activeTab" type="card" class="section-gap workspace-tabs">
        <el-tab-pane v-for="tab in tabs" :key="tab" :label="tab" :name="tab">
          <template v-if="tab === 'Overview'">
            <div class="two-column">
              <section class="panel">
                <h2>Work Order Status</h2>
                <div v-for="item in workspace.statusDistribution" :key="item.key" class="bar-row">
                  <span>{{ item.key }}</span>
                  <strong>{{ item.count }}</strong>
                </div>
              </section>
              <section class="panel">
                <h2>Priority Distribution</h2>
                <div v-for="item in workspace.priorityDistribution" :key="item.key" class="bar-row">
                  <span>{{ item.key }}</span>
                  <el-tag :type="tagType(item.key)">{{ item.count }}</el-tag>
                </div>
              </section>
            </div>

            <div class="two-column section-gap">
              <section class="panel">
                <h2>SLA Risk List</h2>
                <div v-for="item in workspace.slaRiskList" :key="item.workOrderId" class="risk-row">
                  <div>
                    <strong>{{ item.workOrderId }}</strong>
                    <span>{{ item.title }}</span>
                  </div>
                  <el-tag :type="tagType(item.risk)">{{ item.risk }}</el-tag>
                </div>
              </section>
              <section class="panel">
                <h2>Fault-to-WorkOrder Conversion</h2>
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="Detected faults">{{ workspace.faultToWorkOrderConversion.detectedFaults }}</el-descriptions-item>
                  <el-descriptions-item label="Converted work orders">{{ workspace.faultToWorkOrderConversion.convertedWorkOrders }}</el-descriptions-item>
                  <el-descriptions-item label="Conversion rate">{{ workspace.faultToWorkOrderConversion.conversionRate }}</el-descriptions-item>
                  <el-descriptions-item label="Top source">{{ workspace.faultToWorkOrderConversion.topSource }}</el-descriptions-item>
                </el-descriptions>
              </section>
            </div>

            <section class="panel section-gap">
              <h2>Top Affected Systems</h2>
              <el-table :data="workspace.topAffectedSystems" stripe border>
                <el-table-column prop="systemName" label="System" min-width="160" />
                <el-table-column prop="openWorkOrders" label="Open Work Orders" min-width="160" />
                <el-table-column prop="criticality" label="Criticality" min-width="140" />
                <el-table-column prop="topAsset" label="Top Asset" min-width="220" />
              </el-table>
            </section>

            <section class="panel section-gap">
              <h2>Latest Maintenance Activities</h2>
              <div v-for="item in workspace.latestActivities" :key="`${item.time}-${item.workOrderId}`" class="timeline-row">
                <span>{{ item.time }}</span>
                <strong>{{ item.actor }}</strong>
                <p>{{ item.action }} · {{ item.workOrderId }} · {{ item.evidenceRef }}</p>
              </div>
            </section>
          </template>

          <template v-else-if="tab === 'Work Orders'">
            <section class="filter-strip">
              <el-select v-model="filters.status" clearable placeholder="Status">
                <el-option v-for="item in statusOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.priority" clearable placeholder="Priority">
                <el-option v-for="item in priorityOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.system" clearable placeholder="System">
                <el-option v-for="item in systemOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.engineer" clearable placeholder="Assigned Engineer">
                <el-option v-for="item in engineerOptions" :key="item" :label="item" :value="item" />
              </el-select>
              <el-select v-model="filters.slaRisk" clearable placeholder="SLA Risk">
                <el-option v-for="item in slaRiskOptions" :key="item" :label="item" :value="item" />
              </el-select>
            </section>
            <el-table :data="filteredWorkOrders" stripe border class="section-gap">
              <el-table-column prop="workOrderId" label="WO ID" min-width="150" fixed />
              <el-table-column prop="title" label="Title" min-width="280" />
              <el-table-column prop="sourceFault" label="Source Fault / Alarm" min-width="220" />
              <el-table-column prop="assetName" label="Asset" min-width="190" />
              <el-table-column prop="systemName" label="System" min-width="150" />
              <el-table-column prop="location" label="Location" min-width="240" />
              <el-table-column label="Priority" min-width="120">
                <template #default="{ row }"><el-tag :type="tagType(row.priority)">{{ row.priority }}</el-tag></template>
              </el-table-column>
              <el-table-column prop="status" label="Status" min-width="140" />
              <el-table-column prop="slaDue" label="SLA Due" min-width="170" />
              <el-table-column prop="assignedEngineer" label="Assigned Engineer" min-width="170" />
              <el-table-column prop="createdTime" label="Created Time" min-width="170" />
              <el-table-column prop="evidenceCount" label="Evidence Count" min-width="140" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Preventive'">
            <el-table :data="preventiveRows" stripe border>
              <el-table-column prop="planId" label="Plan" min-width="160" />
              <el-table-column prop="planName" label="Scheduled PM Task" min-width="260" />
              <el-table-column prop="frequency" label="Frequency" min-width="130" />
              <el-table-column prop="nextDueDate" label="Next Due Date" min-width="160" />
              <el-table-column prop="assetGroup" label="Asset / System" min-width="220" />
              <el-table-column prop="systemName" label="System" min-width="170" />
              <el-table-column prop="complianceStatus" label="Compliance Status" min-width="170" />
              <el-table-column prop="checklistReadiness" label="Checklist Readiness" min-width="190" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Predictive'">
            <el-table :data="predictiveRows" stripe border>
              <el-table-column prop="predictionId" label="Prediction" min-width="160" />
              <el-table-column prop="assetName" label="Asset" min-width="210" />
              <el-table-column prop="systemName" label="System" min-width="160" />
              <el-table-column prop="location" label="Location" min-width="220" />
              <el-table-column prop="failureRisk" label="Predicted Failure Risk" min-width="190" />
              <el-table-column prop="healthScore" label="Asset Health Score" min-width="170" />
              <el-table-column prop="trendSummary" label="Trend / Anomaly Summary" min-width="260" />
              <el-table-column prop="recommendedAction" label="Recommended Action" min-width="260" />
              <el-table-column prop="confidence" label="Confidence" min-width="130" />
              <el-table-column prop="severity" label="Severity" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Assignments'">
            <el-table :data="assignmentRows" stripe border>
              <el-table-column prop="engineerName" label="Engineer" min-width="180" />
              <el-table-column prop="activeWorkOrders" label="Assigned Work Orders" min-width="190" />
              <el-table-column prop="skill" label="Skill / Discipline" min-width="220" />
              <el-table-column prop="availability" label="Shift Availability" min-width="180" />
              <el-table-column prop="siteZone" label="Zone" min-width="180" />
              <el-table-column prop="shift" label="Shift" min-width="140" />
              <el-table-column prop="escalationOwner" label="Escalation Owner" min-width="190" />
            </el-table>
          </template>

          <template v-else-if="tab === 'SLA & Aging'">
            <div class="two-column">
              <section class="panel">
                <h2>Aging Buckets</h2>
                <div v-for="item in workspace.slaAging.agingBuckets" :key="item.key" class="bar-row">
                  <span>{{ item.key }}</span>
                  <strong>{{ item.count }}</strong>
                </div>
              </section>
              <section class="panel">
                <h2>MTTR / Response</h2>
                <div class="large-metric">{{ workspace.slaAging.mttrHours }}h</div>
                <p>Average MTTR</p>
                <div class="large-metric small">{{ workspace.slaAging.averageResponseMinutes }}m</div>
                <p>Average response time</p>
              </section>
            </div>
            <section class="panel section-gap">
              <h2>Due Soon / Overdue</h2>
              <el-table :data="[...workspace.slaAging.dueSoon, ...workspace.slaAging.overdue]" stripe border>
                <el-table-column prop="workOrderId" label="Work Order" min-width="150" />
                <el-table-column prop="title" label="Title" min-width="280" />
                <el-table-column prop="priority" label="Priority" min-width="120" />
                <el-table-column prop="slaDue" label="SLA Due" min-width="170" />
                <el-table-column prop="owner" label="Owner" min-width="170" />
                <el-table-column prop="risk" label="Risk" min-width="140" />
              </el-table>
            </section>
          </template>

          <template v-else-if="tab === 'Evidence'">
            <section class="panel">
              <h2>Work Order Evidence Timeline</h2>
              <div v-for="item in evidenceRows" :key="`${item.time}-${item.workOrderId}`" class="evidence-row">
                <div>
                  <strong>{{ item.time }} · {{ item.workOrderId }}</strong>
                  <p>Fault source: {{ item.faultSource }}</p>
                  <p>Operator action: {{ item.operatorAction }}</p>
                  <p>Engineer update: {{ item.engineerUpdate }}</p>
                </div>
                <div>
                  <el-tag type="info">{{ item.attachmentReference }}</el-tag>
                  <el-tag type="success">{{ item.approvalClosureRecord }}</el-tag>
                </div>
              </div>
            </section>
          </template>

          <template v-else>
            <el-alert
              v-if="reportToast"
              type="success"
              :closable="false"
              show-icon
              :title="reportToast"
              class="report-alert"
            />
            <el-table :data="reportRows" stripe border>
              <el-table-column prop="report" label="Report" min-width="260" />
              <el-table-column prop="coverage" label="Coverage" min-width="320" />
              <el-table-column prop="status" label="Status" min-width="150" />
              <el-table-column label="Entry" min-width="180">
                <template #default="{ row }">
                  <el-button type="primary" size="small" @click="openReport(row.report)">
                    {{ row.actionLabel }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </template>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<style scoped>
.umms-page {
  min-height: 100%;
  padding: 20px;
  background: #f5f8f7;
  color: #1e2d2b;
}

.workspace-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgb(38 65 58 / 8%);
}

.workspace-head h1 {
  margin: 4px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.eyebrow,
.summary,
.metadata-strip span,
.metric-card span {
  margin: 0;
  color: #60736f;
}

.eyebrow {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

.summary {
  max-width: 780px;
}

.head-badges {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: flex-end;
  gap: 8px;
}

.section-gap {
  margin-top: 16px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.metric-card,
.metadata-strip,
.workspace-tabs,
.panel {
  border: 1px solid #dbe6e2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 8px 20px rgb(38 65 58 / 6%);
}

.metric-card {
  padding: 14px;
}

.metric-card strong {
  display: block;
  margin: 8px 0 4px;
  color: #087467;
  font-size: 26px;
  line-height: 1;
}

.metric-card em {
  color: #28746a;
  font-style: normal;
}

.metadata-strip {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) minmax(0, 2fr);
  gap: 14px;
  padding: 14px;
}

.metadata-strip strong {
  display: block;
  margin-top: 4px;
}

.workspace-tabs {
  padding: 14px;
}

.two-column {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.panel {
  padding: 14px;
}

.panel h2 {
  margin: 0 0 12px;
  color: #193f3a;
  font-size: 17px;
  font-weight: 700;
}

.bar-row,
.risk-row,
.timeline-row,
.evidence-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-top: 1px solid #edf2f0;
}

.bar-row:first-of-type,
.risk-row:first-of-type,
.timeline-row:first-of-type,
.evidence-row:first-of-type {
  border-top: 0;
}

.risk-row span,
.timeline-row p,
.evidence-row p {
  display: block;
  margin: 4px 0 0;
  color: #60736f;
}

.filter-strip {
  display: grid;
  grid-template-columns: repeat(5, minmax(150px, 1fr));
  gap: 10px;
}

.large-metric {
  color: #087467;
  font-size: 34px;
  font-weight: 800;
}

.large-metric.small {
  margin-top: 12px;
  font-size: 26px;
}

.evidence-row > div:last-child {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-content: flex-start;
  gap: 8px;
}

.report-alert {
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .workspace-head,
  .metadata-strip,
  .two-column,
  .filter-strip {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .head-badges {
    justify-content: flex-start;
  }
}
</style>
