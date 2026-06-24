<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import { getUmmsGaR2Workspace, type UmmsGaR2Workspace, type UmmsGaR2WorkOrder } from '@/services/api/umms'

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
</script>

<template>
  <section class="umms-page" v-loading="loading">
    <header class="workspace-head">
      <div>
        <p class="eyebrow">Work Management / Maintenance</p>
        <h1>{{ workspace?.workspaceTitle || 'UMMS Maintenance Workspace' }}</h1>
        <p class="summary">
          Customer-facing maintenance command workspace for work orders, asset context, SLA risk, assignments, evidence, and reporting.
        </p>
      </div>
      <div class="head-badges">
        <el-tag type="success" effect="light">Read-only</el-tag>
        <el-tag type="info" effect="light">{{ workspace?.capability || 'Maintenance operations' }}</el-tag>
      </div>
    </header>

    <el-alert
      v-if="apiError"
      class="section-gap"
      type="warning"
      show-icon
      :closable="false"
      :title="apiError"
    />

    <template v-if="workspace">
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
