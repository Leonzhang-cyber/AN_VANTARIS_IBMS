<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import { getUmmsGaR2Workspace, type UmmsGaR2Workspace } from '@/services/api/umms'

const tabs = [
  'Overview',
  'Work Orders',
  'Task Board',
  'Maintenance Plans',
  'Engineer Dispatch',
  'Asset Context',
  'Event Context',
  'Evidence Linkage',
  'Reports',
  'Customer Acceptance',
  'Role Views',
  'Guardrails',
]

const loading = ref(false)
const apiError = ref('')
const activeTab = ref('Overview')
const workspace = ref<UmmsGaR2Workspace | null>(null)

const statusBadges = computed(() => {
  const data = workspace.value
  if (!data) return []
  return [
    'Production Demo Ready',
    'Read-only Mode',
    'Not POC',
    data.capability,
    data.visualStyle,
  ]
})

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
  <section class="umms-r2-page" v-loading="loading">
    <header class="workspace-head">
      <div>
        <p class="eyebrow">Work Management / Maintenance capability</p>
        <h1>UMMS Production-grade Maintenance Workspace</h1>
        <p class="summary">
          Read-only customer demo readiness for work orders, task dispatch, maintenance plans, evidence, reports, and role views.
        </p>
      </div>
      <div class="badge-stack">
        <el-tag v-for="badge in statusBadges" :key="badge" effect="light" round>{{ badge }}</el-tag>
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
      <section class="overview-grid section-gap">
        <article v-for="card in workspace.overviewCards" :key="card.label" class="metric-card">
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
          <em>{{ card.status }}</em>
        </article>
      </section>

      <section class="section-gap context-strip">
        <div>
          <span>Future controlled action path</span>
          <strong>{{ workspace.futureExecutionPath }}</strong>
        </div>
        <div>
          <span>Server planning</span>
          <strong>{{ workspace.appNonDbTarget }} app / {{ workspace.dbOnlyTarget }} DB-only</strong>
        </div>
      </section>

      <el-tabs v-model="activeTab" type="card" class="section-gap workspace-tabs">
        <el-tab-pane v-for="tab in tabs" :key="tab" :label="tab" :name="tab">
          <template v-if="tab === 'Overview'">
            <div class="section-title">Maintenance Overview</div>
            <el-descriptions :column="3" border>
              <el-descriptions-item label="scope">{{ workspace.scope }}</el-descriptions-item>
              <el-descriptions-item label="mode">{{ workspace.mode }}</el-descriptions-item>
              <el-descriptions-item label="readiness">{{ workspace.readinessLevel }}</el-descriptions-item>
              <el-descriptions-item label="productionDemoReady">{{ workspace.productionDemoReady }}</el-descriptions-item>
              <el-descriptions-item label="poc">{{ workspace.poc }}</el-descriptions-item>
              <el-descriptions-item label="temporaryDemo">{{ workspace.temporaryDemo }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'Work Orders'">
            <div class="section-title">Work Order Management</div>
            <el-table :data="workspace.workOrders" stripe border>
              <el-table-column prop="workOrderId" label="Work Order" min-width="160" />
              <el-table-column prop="title" label="Title" min-width="240" />
              <el-table-column prop="maintenanceType" label="Type" min-width="150" />
              <el-table-column prop="status" label="Status" min-width="150" />
              <el-table-column prop="priority" label="Priority" min-width="120" />
              <el-table-column prop="assignedEngineer" label="Engineer" min-width="160" />
              <el-table-column prop="linkedUcdeEvidence" label="UCDE Evidence" min-width="170" />
              <el-table-column prop="linkedUhmiPanel" label="UHMI Linkage" min-width="220" />
              <el-table-column prop="readOnly" label="Read-only" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Task Board'">
            <div class="section-title">Maintenance Task Board</div>
            <el-table :data="workspace.maintenanceTasks" stripe border>
              <el-table-column prop="taskId" label="Task" min-width="160" />
              <el-table-column prop="taskName" label="Task Name" min-width="240" />
              <el-table-column prop="workOrderId" label="Work Order" min-width="160" />
              <el-table-column prop="engineer" label="Engineer" min-width="150" />
              <el-table-column prop="role" label="Role" min-width="120" />
              <el-table-column prop="checklistStatus" label="Checklist" min-width="170" />
              <el-table-column prop="evidenceRequired" label="Evidence Required" min-width="220" />
              <el-table-column prop="readOnly" label="Read-only" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Maintenance Plans'">
            <div class="section-title">Preventive Maintenance Plan</div>
            <el-table :data="workspace.preventiveMaintenancePlans" stripe border>
              <el-table-column prop="planId" label="Plan" min-width="150" />
              <el-table-column prop="planName" label="Plan Name" min-width="230" />
              <el-table-column prop="systemName" label="System" min-width="190" />
              <el-table-column prop="assetGroup" label="Asset Group" min-width="160" />
              <el-table-column prop="frequency" label="Frequency" min-width="130" />
              <el-table-column prop="nextDueDate" label="Next Due" min-width="140" />
              <el-table-column prop="complianceStatus" label="Compliance" min-width="150" />
            </el-table>
            <div class="section-title inner-title">Corrective Maintenance Flow</div>
            <el-table :data="workspace.correctiveMaintenanceFlow" stripe border>
              <el-table-column prop="flowId" label="Flow" min-width="150" />
              <el-table-column prop="triggerEvent" label="Trigger Event" min-width="160" />
              <el-table-column prop="linkedAsset" label="Asset" min-width="170" />
              <el-table-column prop="diagnosticStep" label="Diagnostic Step" min-width="260" />
              <el-table-column prop="approvalBoundary" label="Approval Boundary" min-width="260" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Engineer Dispatch'">
            <div class="section-title">Engineer Dispatch</div>
            <el-table :data="workspace.engineerDispatch" stripe border>
              <el-table-column prop="engineerId" label="Engineer ID" min-width="140" />
              <el-table-column prop="engineerName" label="Engineer" min-width="170" />
              <el-table-column prop="availability" label="Availability" min-width="140" />
              <el-table-column prop="siteZone" label="Site Zone" min-width="160" />
              <el-table-column prop="role" label="Role" min-width="130" />
              <el-table-column prop="shift" label="Shift" min-width="120" />
              <el-table-column prop="readOnly" label="Read-only" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Asset Context'">
            <div class="section-title">Asset Maintenance Context</div>
            <el-table :data="workspace.assetContext" stripe border>
              <el-table-column prop="assetId" label="Asset ID" min-width="160" />
              <el-table-column prop="assetName" label="Asset" min-width="190" />
              <el-table-column prop="systemName" label="System" min-width="190" />
              <el-table-column prop="category" label="Category" min-width="130" />
              <el-table-column prop="location" label="Location" min-width="190" />
              <el-table-column prop="zone" label="Zone" min-width="100" />
              <el-table-column prop="readOnly" label="Read-only" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Event Context'">
            <div class="section-title">Event / Fault Context</div>
            <el-table :data="workspace.eventContext" stripe border>
              <el-table-column prop="eventId" label="Event" min-width="150" />
              <el-table-column prop="severity" label="Severity" min-width="120" />
              <el-table-column prop="sourceSystem" label="Source" min-width="180" />
              <el-table-column prop="linkedAsset" label="Asset" min-width="190" />
              <el-table-column prop="linkedWorkOrder" label="Work Order" min-width="170" />
              <el-table-column prop="evidenceLinked" label="Evidence" min-width="150" />
              <el-table-column prop="status" label="Status" min-width="150" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Evidence Linkage'">
            <div class="section-title">UCDE Evidence Linkage</div>
            <el-table :data="workspace.evidenceLinkage" stripe border>
              <el-table-column prop="linkage" label="Linkage" min-width="220" />
              <el-table-column prop="coverage" label="Coverage" min-width="320" />
              <el-table-column prop="readOnly" label="Read-only" min-width="120" />
            </el-table>
            <p class="linkage-note">UHMI Linkage remains read-only through panel context and evidence snapshots.</p>
          </template>

          <template v-else-if="tab === 'Reports'">
            <div class="section-title">Reports Linkage</div>
            <el-table :data="workspace.reportLinkage" stripe border>
              <el-table-column prop="report" label="Report" min-width="260" />
              <el-table-column prop="status" label="Status" min-width="140" />
              <el-table-column prop="readOnly" label="Read-only" min-width="120" />
            </el-table>
          </template>

          <template v-else-if="tab === 'Customer Acceptance'">
            <div class="section-title">Customer Acceptance View</div>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Decision">{{ workspace.customerAcceptance.decision }}</el-descriptions-item>
              <el-descriptions-item label="Maintenance overview">{{ workspace.customerAcceptance.maintenanceOverview }}</el-descriptions-item>
              <el-descriptions-item label="Evidence summary">{{ workspace.customerAcceptance.evidenceSummary }}</el-descriptions-item>
              <el-descriptions-item label="Report snapshot">{{ workspace.customerAcceptance.reportSnapshot }}</el-descriptions-item>
            </el-descriptions>
          </template>

          <template v-else-if="tab === 'Role Views'">
            <div class="section-title">Role-based Views</div>
            <div class="role-grid">
              <article v-for="(items, role) in workspace.roleViews" :key="role" class="role-card">
                <h3>{{ role }}</h3>
                <ul>
                  <li v-for="item in items" :key="item">{{ item }}</li>
                </ul>
              </article>
            </div>
          </template>

          <template v-else>
            <div class="section-title">Guardrails</div>
            <div class="guardrail-grid">
              <el-tag v-for="item in workspace.guardrails" :key="item" type="info" effect="light" round>{{ item }}</el-tag>
            </div>
            <el-descriptions class="inner-title" :column="3" border>
              <el-descriptions-item label="No Work Order Write">{{ workspace.workOrderWrite }}</el-descriptions-item>
              <el-descriptions-item label="No DB Write">{{ workspace.dbWrite }}</el-descriptions-item>
              <el-descriptions-item label="No Runtime Activation">{{ workspace.runtimeActivation }}</el-descriptions-item>
              <el-descriptions-item label="No Direct Device Control">{{ workspace.deviceControl }}</el-descriptions-item>
              <el-descriptions-item label="No EDGE Command Execution">{{ workspace.edgeCommandExecution }}</el-descriptions-item>
              <el-descriptions-item label="No LINK Command Execution">{{ workspace.linkCommandExecution }}</el-descriptions-item>
            </el-descriptions>
          </template>
        </el-tab-pane>
      </el-tabs>
    </template>
  </section>
</template>

<style scoped>
.umms-r2-page {
  min-height: 100%;
  padding: 20px;
  background: #f4fbf8;
  color: #203331;
}

.workspace-head {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
  border: 1px solid #d6ebe5;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 12px 28px rgb(34 82 73 / 8%);
}

.workspace-head h1 {
  margin: 4px 0 8px;
  font-size: 28px;
  line-height: 1.2;
  letter-spacing: 0;
}

.eyebrow,
.summary,
.context-strip span,
.metric-card span {
  margin: 0;
  color: #647b76;
}

.eyebrow {
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

.summary {
  max-width: 760px;
}

.badge-stack,
.guardrail-grid {
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  justify-content: flex-end;
  gap: 8px;
}

.section-gap {
  margin-top: 16px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.metric-card,
.role-card,
.context-strip,
.workspace-tabs {
  border: 1px solid #d6ebe5;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 10px 24px rgb(34 82 73 / 7%);
}

.metric-card {
  padding: 14px;
}

.metric-card strong {
  display: block;
  margin: 8px 0 4px;
  color: #007f73;
  font-size: 26px;
  line-height: 1;
}

.metric-card em {
  color: #26796f;
  font-style: normal;
}

.context-strip {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(260px, 1fr);
  gap: 14px;
  padding: 14px;
}

.context-strip strong {
  display: block;
  margin-top: 4px;
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

.inner-title {
  margin-top: 16px;
}

.linkage-note {
  margin: 12px 0 0;
  color: #41625d;
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.role-card {
  padding: 14px;
}

.role-card h3 {
  margin: 0 0 8px;
  color: #007f73;
}

.role-card ul {
  margin: 0;
  padding-left: 18px;
}

@media (max-width: 780px) {
  .workspace-head,
  .context-strip {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .badge-stack {
    justify-content: flex-start;
  }
}
</style>
