<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
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
  'consumption-overview': {
    title: 'Consumption Overview',
    subtitle: 'Energy consumption view across sites, systems, meter quality, and report-ready indicators.',
    primaryAction: 'Review consumption',
    metrics: [
      { label: 'Energy Signals', value: '58', note: 'Signals included in current view' },
      { label: 'High Consumption', value: '9', note: 'Consumption items requiring review' },
      { label: 'Meter Coverage', value: '94%', note: 'Meters represented in reporting view' },
      { label: 'Reports Ready', value: '6', note: 'Consumption reports ready' },
    ],
    rows: [
      { item: 'Review consumption baseline', focus: 'Site and system consumption', status: 'Ready' },
      { item: 'Open high consumption items', focus: 'Exception analysis', status: 'Review' },
      { item: 'Prepare energy report', focus: 'Customer reporting', status: 'Ready' },
    ],
  },
  'demand-peak': {
    title: 'Demand / Peak',
    subtitle: 'Demand and peak-load view for high-load zones, exception periods, and operational response.',
    primaryAction: 'Review peak demand',
    metrics: [
      { label: 'Peak Events', value: '11', note: 'Demand peaks under review' },
      { label: 'High Load Zones', value: '4', note: 'Zones with elevated load' },
      { label: 'Load Shift Items', value: '6', note: 'Optimization candidates' },
      { label: 'Evidence Links', value: '10', note: 'Peak records with evidence' },
    ],
    rows: [
      { item: 'Review peak events', focus: 'Demand and time window', status: 'Active' },
      { item: 'Open high-load zones', focus: 'Zone and asset impact', status: 'Review' },
      { item: 'Prepare demand report', focus: 'Peak evidence and reporting', status: 'Ready' },
    ],
  },
  'energy-intensity': {
    title: 'Energy Intensity',
    subtitle: 'Energy intensity by site, system, floor area, operating profile, and customer reporting period.',
    primaryAction: 'Review intensity',
    metrics: [
      { label: 'Intensity Metrics', value: '18', note: 'Intensity indicators tracked' },
      { label: 'Above Target', value: '5', note: 'Metrics above expected band' },
      { label: 'Improving', value: '9', note: 'Metrics trending better' },
      { label: 'Report Ready', value: '4', note: 'Intensity summaries prepared' },
    ],
    rows: [
      { item: 'Review intensity dashboard', focus: 'Site and system intensity', status: 'Ready' },
      { item: 'Open above-target metrics', focus: 'Operational optimization', status: 'Review' },
      { item: 'Prepare intensity evidence', focus: 'Customer-ready metric trace', status: 'Ready' },
    ],
  },
  'meter-health': {
    title: 'Meter Health',
    subtitle: 'Meter quality and readiness view across data gaps, flatline indicators, and evidence records.',
    primaryAction: 'Review meter health',
    metrics: [
      { label: 'Meters', value: '126', note: 'Meters in coverage view' },
      { label: 'Healthy Meters', value: '118', note: 'Meters reporting normally' },
      { label: 'Quality Review', value: '8', note: 'Meters requiring review' },
      { label: 'Evidence Links', value: '16', note: 'Meter health evidence records' },
    ],
    rows: [
      { item: 'Review meter health', focus: 'Meter availability and quality', status: 'Ready' },
      { item: 'Open quality review items', focus: 'Data gaps and flatline signals', status: 'Review' },
      { item: 'Check meter evidence', focus: 'Evidence-linked meter records', status: 'Ready' },
    ],
  },
  'energy-exceptions': {
    title: 'Energy Exceptions',
    subtitle: 'Energy exception queue covering unusual consumption, high demand, meter quality, and evidence status.',
    primaryAction: 'Review exceptions',
    metrics: [
      { label: 'Exceptions', value: '13', note: 'Energy exceptions under review' },
      { label: 'High Impact', value: '4', note: 'Exceptions with service impact' },
      { label: 'Evidence Ready', value: '10', note: 'Exceptions with traceable evidence' },
      { label: 'Report Items', value: '6', note: 'Items ready for reporting' },
    ],
    rows: [
      { item: 'Review exception queue', focus: 'Energy anomalies and impact', status: 'Active' },
      { item: 'Open high-impact exception', focus: 'Site and asset context', status: 'High' },
      { item: 'Prepare exception evidence', focus: 'Evidence and reporting', status: 'Ready' },
    ],
  },
  'carbon-overview': {
    title: 'Carbon Overview',
    subtitle: 'Carbon reporting view across energy linkage, emissions summary, evidence, and ESG reporting.',
    primaryAction: 'Review carbon',
    metrics: [
      { label: 'Carbon Metrics', value: '14', note: 'Carbon indicators tracked' },
      { label: 'Energy Linked', value: '12', note: 'Carbon metrics linked to energy signals' },
      { label: 'Evidence Ready', value: '11', note: 'Carbon evidence records' },
      { label: 'Reports Ready', value: '3', note: 'Carbon reports prepared' },
    ],
    rows: [
      { item: 'Review carbon summary', focus: 'Emissions and energy linkage', status: 'Ready' },
      { item: 'Open carbon evidence', focus: 'Traceability and assumptions', status: 'Ready' },
      { item: 'Prepare ESG report', focus: 'Customer reporting package', status: 'Ready' },
    ],
  },
  'esg-metrics': {
    title: 'ESG Metrics',
    subtitle: 'ESG metric view across energy, carbon, water, waste, data quality, and evidence readiness.',
    primaryAction: 'Review ESG metrics',
    metrics: [
      { label: 'ESG Metrics', value: '24', note: 'Metrics in ESG view' },
      { label: 'Quality Review', value: '5', note: 'Metrics needing quality review' },
      { label: 'Evidence Linked', value: '19', note: 'Metrics with evidence records' },
      { label: 'Report Ready', value: '6', note: 'Metrics ready for reporting' },
    ],
    rows: [
      { item: 'Review ESG metric set', focus: 'Metric category and period', status: 'Ready' },
      { item: 'Open quality review', focus: 'Data quality and source evidence', status: 'Review' },
      { item: 'Prepare metric evidence', focus: 'Traceable ESG records', status: 'Ready' },
    ],
  },
  'green-mark-support': {
    title: 'Green Mark Support',
    subtitle: 'Green Mark support view for evidence, energy indicators, compliance items, and report readiness.',
    primaryAction: 'Review Green Mark support',
    metrics: [
      { label: 'Support Items', value: '16', note: 'Green Mark support items tracked' },
      { label: 'Evidence Ready', value: '13', note: 'Items with evidence records' },
      { label: 'Open Gaps', value: '3', note: 'Items requiring review' },
      { label: 'Reports Ready', value: '2', note: 'Reports ready for review' },
    ],
    rows: [
      { item: 'Review support checklist', focus: 'Green Mark evidence readiness', status: 'Review' },
      { item: 'Open evidence gaps', focus: 'Missing or incomplete records', status: 'Active' },
      { item: 'Prepare support report', focus: 'Customer-ready package', status: 'Ready' },
    ],
  },
  'utility-baseline': {
    title: 'Utility Baseline',
    subtitle: 'Utility baseline view for electricity, water, period comparisons, and data quality review.',
    primaryAction: 'Review baseline',
    metrics: [
      { label: 'Baseline Periods', value: '12', note: 'Periods represented in baseline' },
      { label: 'Utility Signals', value: '36', note: 'Utility indicators tracked' },
      { label: 'Quality Review', value: '4', note: 'Baseline records needing review' },
      { label: 'Evidence Links', value: '15', note: 'Baseline evidence records' },
    ],
    rows: [
      { item: 'Review utility baseline', focus: 'Period and utility comparison', status: 'Ready' },
      { item: 'Open quality review', focus: 'Data gaps and assumptions', status: 'Review' },
      { item: 'Prepare baseline evidence', focus: 'Evidence-linked baseline package', status: 'Ready' },
    ],
  },
  'reduction-initiatives': {
    title: 'Reduction Initiatives',
    subtitle: 'Reduction initiative view across opportunities, action status, savings estimate, and evidence.',
    primaryAction: 'Review initiatives',
    metrics: [
      { label: 'Initiatives', value: '9', note: 'Reduction initiatives tracked' },
      { label: 'Active Actions', value: '6', note: 'Actions currently in progress' },
      { label: 'Savings Items', value: '5', note: 'Items with savings estimates' },
      { label: 'Evidence Ready', value: '7', note: 'Initiatives with evidence' },
    ],
    rows: [
      { item: 'Review reduction initiatives', focus: 'Action status and savings potential', status: 'Active' },
      { item: 'Open savings candidates', focus: 'Optimization and impact', status: 'Review' },
      { item: 'Prepare initiative evidence', focus: 'Customer-ready evidence trail', status: 'Ready' },
    ],
  },
  'sustainability-evidence': {
    title: 'Sustainability Evidence',
    subtitle: 'Evidence view for sustainability metrics, energy exceptions, baselines, and customer reports.',
    primaryAction: 'Review evidence',
    metrics: [
      { label: 'Evidence Records', value: '42', note: 'Sustainability evidence records' },
      { label: 'Metric Links', value: '24', note: 'Metrics linked to evidence' },
      { label: 'Report Links', value: '6', note: 'Reports linked to evidence' },
      { label: 'Open Reviews', value: '5', note: 'Evidence items requiring review' },
    ],
    rows: [
      { item: 'Review sustainability evidence', focus: 'Metric and report traceability', status: 'Ready' },
      { item: 'Open evidence reviews', focus: 'Customer-facing evidence quality', status: 'Review' },
      { item: 'Prepare evidence export', focus: 'ESG evidence package', status: 'Ready' },
    ],
  },
  'esg-reports': {
    title: 'ESG Reports',
    subtitle: 'ESG report view across sustainability summaries, compliance support, evidence bundles, and exports.',
    primaryAction: 'Open ESG reports',
    metrics: [
      { label: 'ESG Reports', value: '6', note: 'Reports available for review' },
      { label: 'Evidence Bundles', value: '8', note: 'Evidence bundles linked to reports' },
      { label: 'Open Reviews', value: '2', note: 'Reports requiring review' },
      { label: 'Ready Exports', value: '4', note: 'Reports ready for export' },
    ],
    rows: [
      { item: 'Review ESG report list', focus: 'Report category and readiness', status: 'Ready' },
      { item: 'Open report evidence', focus: 'Evidence bundle linkage', status: 'Ready' },
      { item: 'Prepare customer export', focus: 'Customer-ready report package', status: 'Ready' },
    ],
  },
  'energy-opportunities': {
    title: 'Energy Opportunities',
    subtitle: 'Optimization opportunity view for operating schedules, setpoints, savings, and action planning.',
    primaryAction: 'Review opportunities',
    metrics: [
      { label: 'Opportunities', value: '15', note: 'Energy improvement candidates' },
      { label: 'High Value', value: '5', note: 'Candidates with higher impact' },
      { label: 'Action Plans', value: '7', note: 'Action plans in progress' },
      { label: 'Evidence Ready', value: '9', note: 'Opportunity evidence records' },
    ],
    rows: [
      { item: 'Review opportunity list', focus: 'Savings and operational impact', status: 'Active' },
      { item: 'Open high-value candidates', focus: 'Priority optimization actions', status: 'Review' },
      { item: 'Prepare action evidence', focus: 'Evidence and reporting', status: 'Ready' },
    ],
  },
  'setpoint-review': {
    title: 'Setpoint Review',
    subtitle: 'Setpoint optimization view across comfort, energy, operating schedule, and savings opportunities.',
    primaryAction: 'Review setpoints',
    metrics: [
      { label: 'Setpoint Items', value: '18', note: 'Setpoints tracked for review' },
      { label: 'Optimization Items', value: '7', note: 'Setpoints with savings potential' },
      { label: 'Comfort Watch', value: '3', note: 'Items requiring comfort review' },
      { label: 'Evidence Links', value: '11', note: 'Setpoint evidence records' },
    ],
    rows: [
      { item: 'Review setpoint candidates', focus: 'Energy and comfort balance', status: 'Review' },
      { item: 'Open optimization actions', focus: 'Savings and schedule alignment', status: 'Active' },
      { item: 'Prepare setpoint evidence', focus: 'Traceable setpoint package', status: 'Ready' },
    ],
  },
  'schedule-review': {
    title: 'Schedule Review',
    subtitle: 'Schedule optimization view for equipment runtime, occupancy alignment, and opportunity actions.',
    primaryAction: 'Review schedules',
    metrics: [
      { label: 'Schedules', value: '24', note: 'Operating schedules tracked' },
      { label: 'Mismatch Items', value: '6', note: 'Schedules requiring review' },
      { label: 'Savings Candidates', value: '5', note: 'Schedules with savings potential' },
      { label: 'Evidence Links', value: '10', note: 'Schedule evidence records' },
    ],
    rows: [
      { item: 'Review schedule alignment', focus: 'Occupancy and runtime match', status: 'Review' },
      { item: 'Open savings candidates', focus: 'Schedule optimization', status: 'Active' },
      { item: 'Prepare schedule evidence', focus: 'Evidence and report support', status: 'Ready' },
    ],
  },
  'savings-estimate': {
    title: 'Savings Estimate',
    subtitle: 'Savings estimate view for optimization actions, impact range, evidence, and report readiness.',
    primaryAction: 'Review savings',
    metrics: [
      { label: 'Savings Items', value: '12', note: 'Savings estimates tracked' },
      { label: 'High Confidence', value: '5', note: 'Items with stronger evidence' },
      { label: 'Review Needed', value: '4', note: 'Items needing validation' },
      { label: 'Report Ready', value: '6', note: 'Savings summaries ready' },
    ],
    rows: [
      { item: 'Review savings estimate', focus: 'Impact and confidence range', status: 'Ready' },
      { item: 'Open validation items', focus: 'Assumptions and evidence', status: 'Review' },
      { item: 'Prepare savings report', focus: 'Customer-ready optimization report', status: 'Ready' },
    ],
  },
}

const fallbackCustomerSection = customerSections['consumption-overview']

function normalizeL3Id(value: unknown, defaultKey: string): string {
  const raw = typeof value === 'string' && value ? value : defaultKey
  const normalized = raw.replace(/-\d+$/, '')
  return customerSections[normalized] ? normalized : defaultKey
}

const activeCustomerSection = computed(() => customerSections[normalizeL3Id(route.query.l3, 'consumption-overview')] ?? fallbackCustomerSection)

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
    notes: 'Calculation detail is shown for operational review; formal certification is outside this view.',
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
    <div class="customer-section-card">
      <div class="customer-section-head">
        <div>
          <p class="section-kicker">Selected sustainability section</p>
          <h2>{{ activeCustomerSection.title }}</h2>
          <p>{{ activeCustomerSection.subtitle }}</p>
        </div>
        <el-button type="primary" plain>{{ activeCustomerSection.primaryAction }}</el-button>
      </div>
      <div class="customer-metric-grid">
        <article v-for="metric in activeCustomerSection.metrics" :key="metric.label" class="customer-metric">
          <span>{{ metric.label }}</span>
          <strong>{{ metric.value }}</strong>
          <em>{{ metric.note }}</em>
        </article>
      </div>
      <el-row :gutter="12" class="block-space">
        <el-col :xs="24" :md="8">
          <el-card shadow="never">
            <template #header>Energy Pain Points</template>
            <ul class="inline-list">
              <li>{{ activeCustomerSection.title }} must connect anomaly, equipment behavior, occupancy, and meter quality.</li>
              <li>Peak demand and weekend consumption can be caused by schedule drift or failed setpoints.</li>
              <li>Compliance evidence is weak when savings estimates lack meter and operational context.</li>
            </ul>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-card shadow="never">
            <template #header>Recommended Actions</template>
            <ul class="inline-list">
              <li>Compare consumption anomalies against HVAC schedule, occupancy, and equipment state.</li>
              <li>Prioritize actions with measurable savings and low comfort risk.</li>
              <li>Attach meter quality and calculation evidence before ESG or Green Mark reporting.</li>
            </ul>
          </el-card>
        </el-col>
        <el-col :xs="24" :md="8">
          <el-card shadow="never">
            <template #header>Evidence / Reports</template>
            <ul class="inline-list">
              <li>Meter evidence supports carbon and savings claims.</li>
              <li>Reduction initiatives should map to owner, action, expected saving, and verification status.</li>
              <li>Export package should explain anomaly cause and customer value.</li>
            </ul>
          </el-card>
        </el-col>
      </el-row>
      <el-table :data="activeCustomerSection.rows" stripe border class="customer-section-table">
        <el-table-column prop="item" label="Action" min-width="240" />
        <el-table-column prop="focus" label="Focus Area" min-width="260" />
        <el-table-column prop="status" label="Status" min-width="140" />
      </el-table>
    </div>

    <el-alert
      v-if="apiError"
      type="warning"
      show-icon
      :closable="false"
      :title="customerUnavailableMessage"
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

.customer-section-card {
  border: 1px solid #dbe7e4;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
}

.customer-section-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.customer-section-head h2 {
  margin: 0 0 8px;
  color: #0f172a;
  font-size: 22px;
}

.customer-section-head p {
  margin: 0;
  color: #52615d;
}

.section-kicker {
  margin-bottom: 8px !important;
  color: #0f766e !important;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.customer-metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.customer-metric {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  background: #f8fbfa;
}

.customer-metric span,
.customer-metric em {
  display: block;
  color: #64748b;
  font-style: normal;
}

.customer-metric strong {
  display: block;
  margin: 6px 0;
  color: #0f766e;
  font-size: 24px;
}

.customer-section-table {
  margin-top: 16px;
}

.block-space {
  margin-top: 12px;
}
</style>
