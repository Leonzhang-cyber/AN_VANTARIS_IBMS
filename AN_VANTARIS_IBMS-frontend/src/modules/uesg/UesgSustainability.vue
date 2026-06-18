<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import {
  getUesgAssociations,
  getUesgHealth,
  getUesgMetricDetail,
  getUesgMetrics,
  getUesgMetricsBreakdown,
  type UesgAssociations,
  type UesgBreakdown,
  type UesgHealth,
  type UesgMetric,
  type UesgMetricsSummary,
} from '@/services/api/uesg'

const loading = ref(false)
const apiError = ref('')
const showDetailDrawer = ref(false)
const selectedMetric = ref<UesgMetric | null>(null)

const health = ref<UesgHealth>({
  status: 'unknown',
  moduleId: 'uesg',
  moduleName: 'UESG Sustainability',
  provider: 'local-uesg-provider',
  runtimeMode: 'skeleton',
  sourceSemantics: 'ibms-neutral',
  mockData: true,
  readOnly: true,
  controlActionsEnabled: false,
  meterIntegrationEnabled: false,
  edgeRuntimeIntegrated: false,
  linkRuntimeIntegrated: false,
  carbonFactorDatabaseIntegrated: false,
  totalMetrics: 0,
  runtimeLinkedMetrics: 0,
  certified: false,
  iec62443Certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
})

const summary = ref<UesgMetricsSummary>({
  totalMetrics: 0,
  energyMetrics: 0,
  carbonMetrics: 0,
  waterMetrics: 0,
  wasteMetrics: 0,
  environmentMetrics: 0,
  mockMetrics: 0,
  runtimeLinkedMetrics: 0,
  certifiedMetrics: 0,
  iec62443CertifiedMetrics: 0,
  greenMarkCertifiedMetrics: 0,
  griCertifiedMetrics: 0,
  isoCertifiedMetrics: 0,
  metricCategories: [],
  metricScopes: [],
  metricPeriods: [],
  dataQualityLevels: [],
  limitations: [],
})

const breakdown = ref<UesgBreakdown>({
  breakdownMode: 'local-skeleton-breakdown',
  items: [],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
  notes: '',
})

const associations = ref<UesgAssociations>({
  associationMode: 'local-skeleton-associations',
  items: [],
  runtimeLinked: false,
  certified: false,
  iec62443Certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
  notes: '',
})

const metrics = ref<UesgMetric[]>([])
const filters = reactive({
  metricCategory: '',
  metricScope: '',
  metricPeriod: '',
  siteId: '',
  systemId: '',
  dataQuality: '',
})

const fallbackMetrics: UesgMetric[] = [
  {
    metricId: 'energy-electricity-monthly',
    metricName: 'Monthly Electricity Usage (Fallback)',
    metricCategory: 'energy',
    metricScope: 'site',
    metricPeriod: 'monthly',
    siteId: 'site-main',
    siteName: 'Main Site',
    systemId: '',
    systemName: '',
    value: 0,
    unit: 'kWh',
    dataQuality: 'estimated',
    sourceSystem: 'vantaris-one-platform',
    sourceRecordId: 'fallback-uesg',
    provider: 'local-uesg-provider',
    runtimeMode: 'skeleton',
    sourceSemantics: 'ibms-neutral',
    mockData: true,
    readOnly: true,
    controlActionsEnabled: false,
    meterIntegrationEnabled: false,
    edgeRuntimeIntegrated: false,
    linkRuntimeIntegrated: false,
    carbonFactorDatabaseIntegrated: false,
    createdAt: '',
    updatedAt: '',
    tags: ['fallback'],
    metadata: {},
    limitations: ['Fallback record only.'],
    runtimeLinked: false,
    certified: false,
    iec62443Certified: false,
    greenMarkCertified: false,
    griCertified: false,
    isoCertified: false,
  },
]

const qualityOptions = computed(() => summary.value.dataQualityLevels)
const categoryOptions = computed(() => summary.value.metricCategories)
const scopeOptions = computed(() => summary.value.metricScopes)
const periodOptions = computed(() => summary.value.metricPeriods)

async function loadAll() {
  loading.value = true
  apiError.value = ''
  try {
    const [healthData, metricsData, breakdownData, associationsData] = await Promise.all([
      getUesgHealth(),
      getUesgMetrics(filters),
      getUesgMetricsBreakdown(),
      getUesgAssociations(),
    ])
    health.value = healthData
    metrics.value = metricsData.items
    summary.value = metricsData.summary
    breakdown.value = breakdownData
    associations.value = associationsData
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'Failed to load UESG sustainability data.'
    apiError.value = message
    metrics.value = fallbackMetrics
  } finally {
    loading.value = false
  }
}

function resetFilters() {
  filters.metricCategory = ''
  filters.metricScope = ''
  filters.metricPeriod = ''
  filters.siteId = ''
  filters.systemId = ''
  filters.dataQuality = ''
  void loadAll()
}

async function openDetail(metric: UesgMetric) {
  selectedMetric.value = metric
  showDetailDrawer.value = true
  try {
    selectedMetric.value = await getUesgMetricDetail(metric.metricId)
  } catch {
    // keep table row as fallback detail.
  }
}

onMounted(() => {
  void loadAll()
})
</script>

<template>
  <section class="uesg-page">
    <div class="hero-row">
      <h2>UESG Sustainability</h2>
      <div class="hero-tags">
        <el-tag type="success">status: {{ health.status }}</el-tag>
        <el-tag type="info">runtime: {{ health.runtimeMode }}</el-tag>
        <el-tag type="warning">provider: {{ health.provider }}</el-tag>
        <el-tag type="info">readOnly: {{ health.readOnly }}</el-tag>
      </div>
    </div>

    <el-alert
      type="info"
      show-icon
      :closable="false"
      title="UESG R1 uses local skeleton ESG metrics. Meter integration, carbon factor database, EDGE/LINK integration and certification reporting are not integrated."
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
      <template #header>Summary cards</template>
      <el-descriptions :column="4" border>
        <el-descriptions-item label="totalMetrics">{{ summary.totalMetrics }}</el-descriptions-item>
        <el-descriptions-item label="energyMetrics">{{ summary.energyMetrics }}</el-descriptions-item>
        <el-descriptions-item label="carbonMetrics">{{ summary.carbonMetrics }}</el-descriptions-item>
        <el-descriptions-item label="waterMetrics">{{ summary.waterMetrics }}</el-descriptions-item>
        <el-descriptions-item label="wasteMetrics">{{ summary.wasteMetrics }}</el-descriptions-item>
        <el-descriptions-item label="environmentMetrics">{{ summary.environmentMetrics }}</el-descriptions-item>
        <el-descriptions-item label="mockMetrics">{{ summary.mockMetrics }}</el-descriptions-item>
        <el-descriptions-item label="runtimeLinkedMetrics">{{ summary.runtimeLinkedMetrics }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card class="block-space">
      <template #header>Filters</template>
      <el-form :inline="true" label-width="120px">
        <el-form-item label="metricCategory">
          <el-select v-model="filters.metricCategory" clearable placeholder="All">
            <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="metricScope">
          <el-select v-model="filters.metricScope" clearable placeholder="All">
            <el-option v-for="item in scopeOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="metricPeriod">
          <el-select v-model="filters.metricPeriod" clearable placeholder="All">
            <el-option v-for="item in periodOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item label="siteId">
          <el-input v-model="filters.siteId" clearable placeholder="e.g. site-main" />
        </el-form-item>
        <el-form-item label="systemId">
          <el-input v-model="filters.systemId" clearable placeholder="e.g. system-mechanical" />
        </el-form-item>
        <el-form-item label="dataQuality">
          <el-select v-model="filters.dataQuality" clearable placeholder="All">
            <el-option v-for="item in qualityOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadAll">Apply</el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="block-space">
      <template #header>ESG Metrics table</template>
      <el-table :data="metrics" v-loading="loading" stripe>
        <el-table-column prop="metricId" label="metricId" min-width="220" />
        <el-table-column prop="metricName" label="metricName" min-width="220" />
        <el-table-column prop="metricCategory" label="metricCategory" min-width="140" />
        <el-table-column prop="metricScope" label="metricScope" min-width="130" />
        <el-table-column prop="metricPeriod" label="metricPeriod" min-width="130" />
        <el-table-column prop="siteId" label="siteId" min-width="120" />
        <el-table-column prop="systemId" label="systemId" min-width="170" />
        <el-table-column prop="dataQuality" label="dataQuality" min-width="120" />
        <el-table-column label="value" min-width="130">
          <template #default="{ row }">{{ row.value }} {{ row.unit }}</template>
        </el-table-column>
        <el-table-column label="actions" min-width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">Detail</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="block-space">
      <template #header>Category Breakdown section</template>
      <el-table :data="breakdown.items" stripe>
        <el-table-column prop="category" label="category" min-width="160" />
        <el-table-column prop="count" label="count" min-width="100" />
        <el-table-column label="scopes" min-width="240">
          <template #default="{ row }">{{ row.scopes.join(', ') || '-' }}</template>
        </el-table-column>
        <el-table-column label="periods" min-width="240">
          <template #default="{ row }">{{ row.periods.join(', ') || '-' }}</template>
        </el-table-column>
      </el-table>
      <el-text class="block-space">{{ breakdown.notes }}</el-text>
    </el-card>

    <el-card class="block-space">
      <template #header>Associations section</template>
      <el-table :data="associations.items" stripe>
        <el-table-column prop="associationId" label="associationId" min-width="220" />
        <el-table-column prop="metricId" label="metricId" min-width="220" />
        <el-table-column prop="siteId" label="siteId" min-width="120" />
        <el-table-column prop="systemId" label="systemId" min-width="170" />
        <el-table-column prop="associationType" label="associationType" min-width="180" />
        <el-table-column prop="notes" label="notes" min-width="260" />
      </el-table>
    </el-card>

    <el-drawer v-model="showDetailDrawer" title="Metric Detail drawer" size="45%">
      <el-empty v-if="!selectedMetric" description="No metric selected." />
      <template v-else>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="metricId">{{ selectedMetric.metricId }}</el-descriptions-item>
          <el-descriptions-item label="metricName">{{ selectedMetric.metricName }}</el-descriptions-item>
          <el-descriptions-item label="category/scope/period">
            {{ selectedMetric.metricCategory }} / {{ selectedMetric.metricScope }} / {{ selectedMetric.metricPeriod }}
          </el-descriptions-item>
          <el-descriptions-item label="site/system">
            {{ selectedMetric.siteId || '-' }} / {{ selectedMetric.systemId || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="value">{{ selectedMetric.value }} {{ selectedMetric.unit }}</el-descriptions-item>
          <el-descriptions-item label="dataQuality">{{ selectedMetric.dataQuality }}</el-descriptions-item>
          <el-descriptions-item label="sourceSemantics">{{ selectedMetric.sourceSemantics }}</el-descriptions-item>
          <el-descriptions-item label="readOnly">{{ selectedMetric.readOnly }}</el-descriptions-item>
          <el-descriptions-item label="certified">{{ selectedMetric.certified }}</el-descriptions-item>
          <el-descriptions-item label="greenMarkCertified">{{ selectedMetric.greenMarkCertified }}</el-descriptions-item>
          <el-descriptions-item label="griCertified">{{ selectedMetric.griCertified }}</el-descriptions-item>
          <el-descriptions-item label="isoCertified">{{ selectedMetric.isoCertified }}</el-descriptions-item>
        </el-descriptions>
      </template>
    </el-drawer>
  </section>
</template>

<style scoped>
.uesg-page {
  padding: 16px;
}

.hero-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.hero-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.block-space {
  margin-top: 12px;
}
</style>

