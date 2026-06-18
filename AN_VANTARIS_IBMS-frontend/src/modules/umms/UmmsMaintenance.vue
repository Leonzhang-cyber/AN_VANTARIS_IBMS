<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import {
  getMaintenanceAssociations,
  getMaintenanceSummary,
  getUmmsHealth,
  getWorkOrderBreakdown,
  getWorkOrderDetail,
  getWorkOrders,
  type MaintenanceAssociationModel,
  type MaintenanceSummary,
  type UmmsHealth,
  type WorkOrderBreakdown,
  type WorkOrderRecord,
} from '@/services/api/umms'

const loading = ref(false)
const apiError = ref('')
const showDetailDrawer = ref(false)
const selectedWorkOrder = ref<WorkOrderRecord | null>(null)

const health = ref<UmmsHealth>({
  status: 'unknown',
  moduleId: 'umms',
  moduleName: 'UMMS Maintenance',
  runtimeMode: 'skeleton',
  provider: 'local-umms-provider',
  sourceSemantics: 'ibms-neutral',
  readOnly: true,
  controlActionsEnabled: false,
  dispatchEnabled: false,
  mobileIntegrated: false,
  notificationIntegrated: false,
  assetRuntimeIntegrated: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  dbPersistenceIntegrated: false,
  certified: false,
  iec62443Certified: false,
})

const summary = ref<MaintenanceSummary>({
  totalWorkOrders: 0,
  preventiveCount: 0,
  correctiveCount: 0,
  inspectionCount: 0,
  safetyCount: 0,
  routineCount: 0,
  draftCount: 0,
  openCount: 0,
  plannedCount: 0,
  scheduledCount: 0,
  inReviewCount: 0,
  highPriorityCount: 0,
  mockWorkOrders: 0,
  runtimeLinkedWorkOrders: 0,
  dispatchedWorkOrders: 0,
  mobileLinkedWorkOrders: 0,
  notificationLinkedWorkOrders: 0,
  certifiedWorkOrders: 0,
  workOrderTypes: [],
  workOrderCategories: [],
  limitations: [],
  certified: false,
  iec62443Certified: false,
})

const breakdown = ref<WorkOrderBreakdown>({
  breakdownMode: 'local-skeleton-breakdown',
  byType: [],
  byStatus: [],
  byPriority: [],
  byCategory: [],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
})

const associations = ref<MaintenanceAssociationModel>({
  associationMode: 'local-skeleton-association',
  siteAssociations: [],
  systemAssociations: [],
  assetAssociations: [],
  runtimeLinked: false,
  assetRuntimeIntegrated: false,
  notes: '',
  certified: false,
  iec62443Certified: false,
})

const workOrders = ref<WorkOrderRecord[]>([])
const filters = reactive({
  workOrderType: '',
  workOrderCategory: '',
  workOrderStatus: '',
  priority: '',
  siteId: '',
  systemId: '',
  assetId: '',
})

const fallbackWorkOrders: WorkOrderRecord[] = [
  {
    workOrderId: 'wo-fallback-001',
    workOrderCode: 'UMMS-FALLBACK-001',
    title: 'Fallback Maintenance Work Order',
    description: 'Fallback local skeleton entry when API is unavailable.',
    workOrderType: 'preventive',
    workOrderCategory: 'hvac',
    workOrderStatus: 'planned',
    priority: 'medium',
    lifecycleStage: 'planning',
    siteId: 'site-main',
    siteName: 'Main Site',
    systemId: 'system-mechanical',
    systemName: 'Mechanical System',
    assetId: 'device-fallback',
    assetName: 'Fallback Asset',
    requestedBy: 'local-fallback',
    assignedTeam: 'maintenance-team',
    assignedTechnician: 'tech-placeholder',
    plannedStart: '',
    plannedEnd: '',
    createdAt: '',
    updatedAt: '',
    sourceSystem: 'local-umms-provider',
    sourceRecordId: 'fallback-wo',
    provider: 'local-umms-provider',
    runtimeMode: 'skeleton',
    sourceSemantics: 'ibms-neutral',
    mockData: true,
    readOnly: true,
    dispatchEnabled: false,
    mobileIntegrated: false,
    notificationIntegrated: false,
    assetRuntimeIntegrated: false,
    edgeRuntimeIntegrated: false,
    linkRuntimeIntegrated: false,
    tags: ['fallback'],
    metadata: {},
    limitations: ['Fallback record only.'],
    certified: false,
    iec62443Certified: false,
  },
]

const fallbackBreakdown: WorkOrderBreakdown = {
  breakdownMode: 'local-skeleton-breakdown',
  byType: [{ key: 'preventive', count: 1 }],
  byStatus: [{ key: 'planned', count: 1 }],
  byPriority: [{ key: 'medium', count: 1 }],
  byCategory: [{ key: 'hvac', count: 1 }],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
}

const fallbackAssociations: MaintenanceAssociationModel = {
  associationMode: 'local-skeleton-association',
  siteAssociations: [{ siteId: 'site-main', siteName: 'Main Site', workOrderIds: ['wo-fallback-001'], runtimeLinked: false }],
  systemAssociations: [],
  assetAssociations: [],
  runtimeLinked: false,
  assetRuntimeIntegrated: false,
  notes: 'Fallback local skeleton associations.',
  certified: false,
  iec62443Certified: false,
}

const workOrderTypeOptions = computed(() => summary.value.workOrderTypes)
const workOrderCategoryOptions = computed(() => summary.value.workOrderCategories)

async function loadAll() {
  loading.value = true
  apiError.value = ''
  try {
    const [healthData, listData, summaryData, breakdownData, associationsData] = await Promise.all([
      getUmmsHealth(),
      getWorkOrders(filters),
      getMaintenanceSummary(),
      getWorkOrderBreakdown(),
      getMaintenanceAssociations(),
    ])
    health.value = healthData
    workOrders.value = listData.workOrders
    summary.value = summaryData
    breakdown.value = breakdownData
    associations.value = associationsData
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'Failed to load UMMS maintenance data.'
    apiError.value = message
    workOrders.value = fallbackWorkOrders
    breakdown.value = fallbackBreakdown
    associations.value = fallbackAssociations
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.workOrderType = ''
  filters.workOrderCategory = ''
  filters.workOrderStatus = ''
  filters.priority = ''
  filters.siteId = ''
  filters.systemId = ''
  filters.assetId = ''
  void loadAll()
}

async function openDetail(row: WorkOrderRecord) {
  selectedWorkOrder.value = row
  showDetailDrawer.value = true
  try {
    selectedWorkOrder.value = await getWorkOrderDetail(row.workOrderId)
  } catch {
    // retain row fallback
  }
}

onMounted(() => {
  void loadAll()
})
</script>

<template>
  <section class="umms-page">
    <div class="hero-row">
      <div>
        <h2>UMMS Maintenance</h2>
        <p>Read-only maintenance workspace for VANTARIS ONE.</p>
      </div>
      <div class="hero-tags">
        <el-tag type="info">runtimeMode: {{ health.runtimeMode }}</el-tag>
        <el-tag type="warning">provider: {{ health.provider }}</el-tag>
        <el-tag type="info">sourceSemantics: {{ health.sourceSemantics }}</el-tag>
        <el-tag type="success">readOnly: {{ health.readOnly }}</el-tag>
        <el-tag type="info">dispatchEnabled: {{ health.dispatchEnabled }}</el-tag>
        <el-tag type="info">mobileIntegrated: {{ health.mobileIntegrated }}</el-tag>
        <el-tag type="info">notificationIntegrated: {{ health.notificationIntegrated }}</el-tag>
        <el-tag type="info">assetRuntimeIntegrated: {{ health.assetRuntimeIntegrated }}</el-tag>
        <el-tag type="info">edgeRuntimeIntegrated: {{ health.edgeRuntimeIntegrated }}</el-tag>
        <el-tag type="info">linkRuntimeIntegrated: {{ health.linkRuntimeIntegrated }}</el-tag>
        <el-tag type="info">certified: {{ health.certified }}</el-tag>
        <el-tag type="info">iec62443Certified: {{ health.iec62443Certified }}</el-tag>
      </div>
    </div>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="UMMS R1 uses local skeleton work orders. Dispatch workflow, mobile integration, notification delivery, EDGE/LINK integration and DB persistence are not integrated."
      class="block-space"
    />

    <el-alert
      v-if="apiError"
      type="warning"
      show-icon
      :closable="false"
      :title="`API fallback active: ${apiError}`"
      class="block-space"
    />

    <el-card class="block-space">
      <template #header>Summary Cards</template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="totalWorkOrders">{{ summary.totalWorkOrders }}</el-descriptions-item>
        <el-descriptions-item label="preventiveCount">{{ summary.preventiveCount }}</el-descriptions-item>
        <el-descriptions-item label="correctiveCount">{{ summary.correctiveCount }}</el-descriptions-item>
        <el-descriptions-item label="inspectionCount">{{ summary.inspectionCount }}</el-descriptions-item>
        <el-descriptions-item label="safetyCount">{{ summary.safetyCount }}</el-descriptions-item>
        <el-descriptions-item label="routineCount">{{ summary.routineCount }}</el-descriptions-item>
        <el-descriptions-item label="openCount">{{ summary.openCount }}</el-descriptions-item>
        <el-descriptions-item label="plannedCount">{{ summary.plannedCount }}</el-descriptions-item>
        <el-descriptions-item label="highPriorityCount">{{ summary.highPriorityCount }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinkedWorkOrders">{{ summary.runtimeLinkedWorkOrders }}</el-descriptions-item>
        <el-descriptions-item label="dispatchedWorkOrders">{{ summary.dispatchedWorkOrders }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="block-space">
      <template #header>Filters</template>
      <el-form :inline="true" label-width="140px">
        <el-form-item label="workOrderType">
          <el-select v-model="filters.workOrderType" clearable placeholder="All">
            <el-option v-for="item in workOrderTypeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="workOrderCategory">
          <el-select v-model="filters.workOrderCategory" clearable placeholder="All">
            <el-option v-for="item in workOrderCategoryOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="workOrderStatus">
          <el-input v-model="filters.workOrderStatus" clearable placeholder="e.g. planned" />
        </el-form-item>
        <el-form-item label="priority">
          <el-input v-model="filters.priority" clearable placeholder="e.g. high" />
        </el-form-item>
        <el-form-item label="siteId">
          <el-input v-model="filters.siteId" clearable placeholder="e.g. site-main" />
        </el-form-item>
        <el-form-item label="systemId">
          <el-input v-model="filters.systemId" clearable placeholder="e.g. system-mechanical" />
        </el-form-item>
        <el-form-item label="assetId">
          <el-input v-model="filters.assetId" clearable placeholder="e.g. device-chiller-01" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadAll">Apply</el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="block-space">
      <template #header>Work Orders</template>
      <el-table :data="workOrders" v-loading="loading" stripe>
        <el-table-column prop="workOrderId" label="workOrderId" min-width="220" />
        <el-table-column prop="title" label="title" min-width="220" />
        <el-table-column prop="workOrderType" label="workOrderType" min-width="130" />
        <el-table-column prop="workOrderCategory" label="workOrderCategory" min-width="150" />
        <el-table-column prop="workOrderStatus" label="workOrderStatus" min-width="140" />
        <el-table-column prop="priority" label="priority" min-width="100" />
        <el-table-column prop="siteName" label="siteName" min-width="150" />
        <el-table-column prop="systemName" label="systemName" min-width="170" />
        <el-table-column prop="assetName" label="assetName" min-width="170" />
        <el-table-column prop="assignedTeam" label="assignedTeam" min-width="150" />
        <el-table-column prop="assignedTechnician" label="assignedTechnician" min-width="170" />
        <el-table-column prop="plannedStart" label="plannedStart" min-width="180" />
        <el-table-column prop="plannedEnd" label="plannedEnd" min-width="180" />
        <el-table-column label="actions" min-width="130" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">View Detail</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="block-space">
      <template #header>Breakdown</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="breakdownMode">{{ breakdown.breakdownMode }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinked">{{ breakdown.runtimeLinked }}</el-descriptions-item>
      </el-descriptions>
      <el-row :gutter="12" class="block-space">
        <el-col :span="12">
          <h4>byType</h4>
          <el-table :data="breakdown.byType" size="small" stripe>
            <el-table-column prop="key" label="key" />
            <el-table-column prop="count" label="count" />
          </el-table>
        </el-col>
        <el-col :span="12">
          <h4>byStatus</h4>
          <el-table :data="breakdown.byStatus" size="small" stripe>
            <el-table-column prop="key" label="key" />
            <el-table-column prop="count" label="count" />
          </el-table>
        </el-col>
      </el-row>
      <el-row :gutter="12" class="block-space">
        <el-col :span="12">
          <h4>byPriority</h4>
          <el-table :data="breakdown.byPriority" size="small" stripe>
            <el-table-column prop="key" label="key" />
            <el-table-column prop="count" label="count" />
          </el-table>
        </el-col>
        <el-col :span="12">
          <h4>byCategory</h4>
          <el-table :data="breakdown.byCategory" size="small" stripe>
            <el-table-column prop="key" label="key" />
            <el-table-column prop="count" label="count" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="block-space">
      <template #header>Associations</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="associationMode">{{ associations.associationMode }}</el-descriptions-item>
        <el-descriptions-item label="assetRuntimeIntegrated">{{ associations.assetRuntimeIntegrated }}</el-descriptions-item>
      </el-descriptions>
      <el-text class="block-space">{{ associations.notes }}</el-text>
      <el-row :gutter="12" class="block-space">
        <el-col :span="8">
          <h4>siteAssociations</h4>
          <el-table :data="associations.siteAssociations" size="small" stripe>
            <el-table-column prop="siteId" label="siteId" />
            <el-table-column prop="siteName" label="siteName" />
          </el-table>
        </el-col>
        <el-col :span="8">
          <h4>systemAssociations</h4>
          <el-table :data="associations.systemAssociations" size="small" stripe>
            <el-table-column prop="systemId" label="systemId" />
            <el-table-column prop="systemName" label="systemName" />
          </el-table>
        </el-col>
        <el-col :span="8">
          <h4>assetAssociations</h4>
          <el-table :data="associations.assetAssociations" size="small" stripe>
            <el-table-column prop="assetId" label="assetId" />
            <el-table-column prop="assetName" label="assetName" />
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-drawer v-model="showDetailDrawer" title="Work Order Detail" size="50%">
      <el-empty v-if="!selectedWorkOrder" description="No work order selected." />
      <template v-else>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="overview">
            {{ selectedWorkOrder.workOrderCode }} | {{ selectedWorkOrder.title }} | {{ selectedWorkOrder.workOrderStatus }}
          </el-descriptions-item>
          <el-descriptions-item label="site/system/asset association">
            {{ selectedWorkOrder.siteName }} / {{ selectedWorkOrder.systemName }} / {{ selectedWorkOrder.assetName }}
          </el-descriptions-item>
          <el-descriptions-item label="assignedTeam / assignedTechnician">
            {{ selectedWorkOrder.assignedTeam }} / {{ selectedWorkOrder.assignedTechnician }}
          </el-descriptions-item>
          <el-descriptions-item label="lifecycleStage">{{ selectedWorkOrder.lifecycleStage }}</el-descriptions-item>
          <el-descriptions-item label="metadata">{{ selectedWorkOrder.metadata }}</el-descriptions-item>
          <el-descriptions-item label="limitations">
            {{ selectedWorkOrder.limitations.join(' | ') }}
          </el-descriptions-item>
          <el-descriptions-item label="dispatchEnabled">{{ selectedWorkOrder.dispatchEnabled }}</el-descriptions-item>
          <el-descriptions-item label="mobileIntegrated">{{ selectedWorkOrder.mobileIntegrated }}</el-descriptions-item>
          <el-descriptions-item label="notificationIntegrated">{{ selectedWorkOrder.notificationIntegrated }}</el-descriptions-item>
          <el-descriptions-item label="certified">{{ selectedWorkOrder.certified }}</el-descriptions-item>
          <el-descriptions-item label="iec62443Certified">{{ selectedWorkOrder.iec62443Certified }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </section>
</template>

<style scoped>
.umms-page {
  padding: 16px;
}

.hero-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.hero-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.block-space {
  margin-top: 12px;
}
</style>

