<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ApiError } from '@/services/api/errors'
import {
  getEsgAssociationDetail,
  getEsgCategoryDetails,
  getEsgDataQuality,
  getEsgMetricCalculation,
  getEsgTrends,
  getUesgHealth,
  getUesgMetricDetail,
  getUesgMetrics,
  getUesgMetricsBreakdown,
  type EsgAssociationDetail,
  type EsgCategoryDetail,
  type EsgDataQualitySummary,
  type EsgMetricCalculationResponse,
  type EsgMetricRecord,
  type EsgSummary,
  type EsgTrendPlaceholder,
  type UesgBreakdown,
  type UesgHealth,
} from '@/services/api/uesg'

const loading = ref(false)
const apiError = ref('')
const showDetailDrawer = ref(false)
const activeDetailTab = ref('overview')
const selectedMetric = ref<EsgMetricRecord | null>(null)
const selectedCalculation = ref<EsgMetricCalculationResponse | null>(null)
const selectedAssociation = ref<EsgAssociationDetail | null>(null)
const selectedQuality = ref<EsgDataQualitySummary | null>(null)

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

const summary = ref<EsgSummary>({
  totalMetrics: 0,
  energyMetrics: 0,
  carbonMetrics: 0,
  waterMetrics: 0,
  wasteMetrics: 0,
  environmentMetrics: 0,
  mockMetrics: 0,
  categoryDetailReady: false,
  calculationDetailReady: false,
  associationDetailReady: false,
  dataQualityReady: false,
  trendPlaceholderReady: false,
  runtimeLinkedMetrics: 0,
  meterLinkedMetrics: 0,
  carbonFactorLinkedMetrics: 0,
  reportReadyMetrics: 0,
  complianceCertifiedMetrics: 0,
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

const categories = ref<EsgCategoryDetail[]>([])
const quality = ref<EsgDataQualitySummary>({
  qualityMode: 'local-skeleton-quality',
  totalMetrics: 0,
  qualityCounts: { estimated: 0, manual: 0, measured: 0, unknown: 0 },
  runtimeLinked: false,
  certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
  limitations: [],
})
const trends = ref<EsgTrendPlaceholder>({
  trendMode: 'local-skeleton-trend',
  periods: ['current-month'],
  trendCalculated: false,
  periodComparisonReady: false,
  series: [],
  runtimeLinked: false,
  limitations: [],
  certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
})
const associationDetail = ref<EsgAssociationDetail | null>(null)

const metrics = ref<EsgMetricRecord[]>([])
const filters = reactive({
  metricCategory: '',
  metricScope: '',
  metricPeriod: '',
  siteId: '',
  systemId: '',
  dataQuality: '',
})

const fallbackCalculation: EsgMetricCalculationResponse = {
  metricId: '',
  metricName: '',
  metricCategory: '',
  calculationDetail: {
    calculationMode: 'local-skeleton-estimate',
    formulaMode: 'placeholder',
    inputReferences: [],
    assumptions: ['Calculation fallback skeleton.'],
    dataQuality: 'unknown',
    calculationReady: false,
    runtimeLinked: false,
    carbonFactorDatabaseIntegrated: false,
    meterIntegrationEnabled: false,
    notes: 'Calculation detail is local skeleton only; no certified calculation method is applied.',
    certified: false,
    greenMarkCertified: false,
    griCertified: false,
    isoCertified: false,
  },
  runtimeLinked: false,
  certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
}

const fallbackAssociation: EsgAssociationDetail = {
  associationMode: 'local-skeleton-association-detail',
  associationSummary: {
    siteAssociationCount: 0,
    systemAssociationCount: 0,
    runtimeLinkedAssociations: 0,
    assetRuntimeIntegrated: false,
  },
  siteAssociations: [],
  systemAssociations: [],
  runtimeLinked: false,
  certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
  limitations: ['Association detail fallback skeleton.'],
}

const fallbackQuality: EsgDataQualitySummary = {
  qualityMode: 'local-skeleton-quality',
  totalMetrics: 0,
  qualityCounts: { estimated: 0, manual: 0, measured: 0, unknown: 0 },
  runtimeLinked: false,
  certified: false,
  greenMarkCertified: false,
  griCertified: false,
  isoCertified: false,
  limitations: ['Data quality fallback skeleton.'],
}

const qualityOptions = computed(() => summary.value.dataQualityLevels)
const categoryOptions = computed(() => summary.value.metricCategories)
const scopeOptions = computed(() => summary.value.metricScopes)
const periodOptions = computed(() => summary.value.metricPeriods)

async function loadAll() {
  loading.value = true
  apiError.value = ''
  try {
    const [healthData, metricsData, breakdownData, categoryData, qualityData, trendData, associationData] = await Promise.all([
      getUesgHealth(),
      getUesgMetrics(filters),
      getUesgMetricsBreakdown(),
      getEsgCategoryDetails(),
      getEsgDataQuality(),
      getEsgTrends(),
      getEsgAssociationDetail(),
    ])
    health.value = healthData
    metrics.value = metricsData.items
    summary.value = metricsData.summary
    breakdown.value = breakdownData
    categories.value = categoryData.items
    quality.value = qualityData
    trends.value = trendData
    associationDetail.value = associationData
  } catch (error) {
    const message = error instanceof ApiError ? error.message : 'Failed to load UESG sustainability data.'
    apiError.value = message
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

async function openDetail(metric: EsgMetricRecord) {
  selectedMetric.value = metric
  showDetailDrawer.value = true
  activeDetailTab.value = 'overview'
  selectedCalculation.value = fallbackCalculation
  selectedAssociation.value = fallbackAssociation
  selectedQuality.value = fallbackQuality
  try {
    selectedMetric.value = await getUesgMetricDetail(metric.metricId)
  } catch {
    // keep row snapshot
  }
  try {
    selectedCalculation.value = await getEsgMetricCalculation(metric.metricId)
  } catch {
    // keep fallback
  }
  try {
    selectedAssociation.value = await getEsgAssociationDetail()
  } catch {
    // keep fallback
  }
  try {
    selectedQuality.value = await getEsgDataQuality()
  } catch {
    // keep fallback
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
      title="UESG R2 category, calculation and trend views are local skeleton readiness views. Meter integration, carbon factor governance and certification reporting are not integrated."
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
        <el-descriptions-item label="totalMetrics">{{ summary.totalMetrics }}</el-descriptions-item>
        <el-descriptions-item label="energyMetrics">{{ summary.energyMetrics }}</el-descriptions-item>
        <el-descriptions-item label="carbonMetrics">{{ summary.carbonMetrics }}</el-descriptions-item>
        <el-descriptions-item label="waterMetrics">{{ summary.waterMetrics }}</el-descriptions-item>
        <el-descriptions-item label="wasteMetrics">{{ summary.wasteMetrics }}</el-descriptions-item>
        <el-descriptions-item label="environmentMetrics">{{ summary.environmentMetrics }}</el-descriptions-item>
        <el-descriptions-item label="categoryDetailReady">{{ summary.categoryDetailReady }}</el-descriptions-item>
        <el-descriptions-item label="calculationDetailReady">{{ summary.calculationDetailReady }}</el-descriptions-item>
        <el-descriptions-item label="associationDetailReady">{{ summary.associationDetailReady }}</el-descriptions-item>
        <el-descriptions-item label="dataQualityReady">{{ summary.dataQualityReady }}</el-descriptions-item>
        <el-descriptions-item label="trendPlaceholderReady">{{ summary.trendPlaceholderReady }}</el-descriptions-item>
        <el-descriptions-item label="meterLinkedMetrics">{{ summary.meterLinkedMetrics }}</el-descriptions-item>
        <el-descriptions-item label="carbonFactorLinkedMetrics">{{ summary.carbonFactorLinkedMetrics }}</el-descriptions-item>
        <el-descriptions-item label="reportReadyMetrics">{{ summary.reportReadyMetrics }}</el-descriptions-item>
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
      <template #header>ESG Metrics Table</template>
      <el-table :data="metrics" v-loading="loading" stripe>
        <el-table-column prop="metricId" label="metricId" min-width="220" />
        <el-table-column prop="metricName" label="metricName" min-width="220" />
        <el-table-column prop="metricCategory" label="metricCategory" min-width="140" />
        <el-table-column prop="metricScope" label="metricScope" min-width="130" />
        <el-table-column prop="dataQuality" label="dataQuality" min-width="120" />
        <el-table-column label="calculationMode" min-width="190">
          <template #default="{ row }">{{ row.calculationDetail.calculationMode }}</template>
        </el-table-column>
        <el-table-column label="categoryDetail" min-width="160">
          <template #default="{ row }">
            <el-tag type="success">{{ row.metricCategory ? 'ready' : 'pending' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="value" min-width="130">
          <template #default="{ row }">{{ row.value }} {{ row.unit }}</template>
        </el-table-column>
        <el-table-column label="actions" min-width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">View Detail</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="block-space">
      <template #header>Category Breakdown Section</template>
      <el-table :data="breakdown.items" stripe>
        <el-table-column prop="category" label="category" min-width="180" />
        <el-table-column prop="count" label="count" min-width="100" />
        <el-table-column label="scopes" min-width="260">
          <template #default="{ row }">{{ row.scopes.join(', ') || '-' }}</template>
        </el-table-column>
        <el-table-column label="periods" min-width="260">
          <template #default="{ row }">{{ row.periods.join(', ') || '-' }}</template>
        </el-table-column>
      </el-table>
      <el-text class="block-space">{{ breakdown.notes }}</el-text>
    </el-card>

    <el-card class="block-space">
      <template #header>Category Details Section</template>
      <el-table :data="categories" stripe>
        <el-table-column prop="categoryName" label="categoryName" min-width="180" />
        <el-table-column prop="metricCount" label="metricCount" min-width="120" />
        <el-table-column prop="primaryUnit" label="primaryUnit" min-width="130" />
        <el-table-column label="totalValue" min-width="140">
          <template #default="{ row }">{{ row.totalValue }}</template>
        </el-table-column>
        <el-table-column label="dataQualitySummary" min-width="260">
          <template #default="{ row }">
            estimated={{ row.dataQualitySummary.estimated ?? 0 }}, measured={{ row.dataQualitySummary.measured ?? 0 }},
            manual={{ row.dataQualitySummary.manual ?? 0 }}, unknown={{ row.dataQualitySummary.unknown ?? 0 }}
          </template>
        </el-table-column>
        <el-table-column label="calculationModes" min-width="200">
          <template #default="{ row }">{{ row.calculationModes.join(', ') || '-' }}</template>
        </el-table-column>
        <el-table-column label="runtimeLinked" min-width="120">
          <template #default="{ row }">{{ row.runtimeLinked }}</template>
        </el-table-column>
        <el-table-column label="certFlags" min-width="200">
          <template #default="{ row }">
            {{ row.certified }}/{{ row.greenMarkCertified }}/{{ row.griCertified }}/{{ row.isoCertified }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="block-space">
      <template #header>Data Quality Section</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="qualityMode">{{ quality.qualityMode }}</el-descriptions-item>
        <el-descriptions-item label="totalMetrics">{{ quality.totalMetrics }}</el-descriptions-item>
        <el-descriptions-item label="estimated">{{ quality.qualityCounts.estimated ?? 0 }}</el-descriptions-item>
        <el-descriptions-item label="manual">{{ quality.qualityCounts.manual ?? 0 }}</el-descriptions-item>
        <el-descriptions-item label="measured">{{ quality.qualityCounts.measured ?? 0 }}</el-descriptions-item>
        <el-descriptions-item label="unknown">{{ quality.qualityCounts.unknown ?? 0 }}</el-descriptions-item>
      </el-descriptions>
      <el-text class="block-space">{{ quality.limitations.join(' | ') }}</el-text>
    </el-card>

    <el-card class="block-space">
      <template #header>Trend Placeholder Section</template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="trendMode">{{ trends.trendMode }}</el-descriptions-item>
        <el-descriptions-item label="trendCalculated">{{ trends.trendCalculated }}</el-descriptions-item>
        <el-descriptions-item label="periodComparisonReady">{{ trends.periodComparisonReady }}</el-descriptions-item>
        <el-descriptions-item label="periods">{{ trends.periods.join(', ') }}</el-descriptions-item>
      </el-descriptions>
      <el-text class="block-space">{{ trends.limitations.join(' | ') }}</el-text>
    </el-card>

    <el-drawer v-model="showDetailDrawer" title="Metric Detail Drawer" size="55%">
      <el-empty v-if="!selectedMetric" description="No metric selected." />
      <template v-else>
        <el-tabs v-model="activeDetailTab">
          <el-tab-pane name="overview" label="Overview">
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
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane name="calculation" label="Calculation Detail">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="calculationMode">
                {{ selectedCalculation?.calculationDetail.calculationMode }}
              </el-descriptions-item>
              <el-descriptions-item label="formulaMode">{{ selectedCalculation?.calculationDetail.formulaMode }}</el-descriptions-item>
              <el-descriptions-item label="dataQuality">{{ selectedCalculation?.calculationDetail.dataQuality }}</el-descriptions-item>
              <el-descriptions-item label="calculationReady">
                {{ selectedCalculation?.calculationDetail.calculationReady }}
              </el-descriptions-item>
              <el-descriptions-item label="assumptions">
                {{ selectedCalculation?.calculationDetail.assumptions.join(' | ') || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="notes">{{ selectedCalculation?.calculationDetail.notes }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane name="association" label="Site/System Association">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="siteAssociationCount">
                {{ selectedAssociation?.associationSummary.siteAssociationCount }}
              </el-descriptions-item>
              <el-descriptions-item label="systemAssociationCount">
                {{ selectedAssociation?.associationSummary.systemAssociationCount }}
              </el-descriptions-item>
              <el-descriptions-item label="runtimeLinkedAssociations">
                {{ selectedAssociation?.associationSummary.runtimeLinkedAssociations }}
              </el-descriptions-item>
              <el-descriptions-item label="assetRuntimeIntegrated">
                {{ selectedAssociation?.associationSummary.assetRuntimeIntegrated }}
              </el-descriptions-item>
            </el-descriptions>
            <el-divider />
            <el-table :data="selectedAssociation?.siteAssociations || []" size="small" stripe>
              <el-table-column prop="siteId" label="siteId" min-width="130" />
              <el-table-column prop="siteName" label="siteName" min-width="160" />
              <el-table-column label="metricIds" min-width="260">
                <template #default="{ row }">{{ row.metricIds.join(', ') || '-' }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane name="quality" label="Data Quality">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="qualityMode">{{ selectedQuality?.qualityMode }}</el-descriptions-item>
              <el-descriptions-item label="totalMetrics">{{ selectedQuality?.totalMetrics }}</el-descriptions-item>
              <el-descriptions-item label="estimated">{{ selectedQuality?.qualityCounts.estimated ?? 0 }}</el-descriptions-item>
              <el-descriptions-item label="manual">{{ selectedQuality?.qualityCounts.manual ?? 0 }}</el-descriptions-item>
              <el-descriptions-item label="measured">{{ selectedQuality?.qualityCounts.measured ?? 0 }}</el-descriptions-item>
              <el-descriptions-item label="unknown">{{ selectedQuality?.qualityCounts.unknown ?? 0 }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane name="limitations" label="Limitations">
            <el-text>{{ selectedMetric.limitations.join(' | ') || '-' }}</el-text>
          </el-tab-pane>
        </el-tabs>
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

