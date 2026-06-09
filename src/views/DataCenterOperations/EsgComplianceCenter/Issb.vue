<template>
  <div class="issb-container">
    <!-- Loading Screen -->
    <div v-if="!isLoaded" class="loading-container">
      <div class="loading-overlay">
        <div class="loading-content">
          <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
          </div>
          <div class="loading-text">
            <span class="loading-title">Loading ISSB Compliance Framework</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">International Sustainability Standards Board</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <el-page-header @back="goBack" content="Back">
        <template #content>
          <div class="page-header-content">
            <span class="page-title">ISSB Sustainability Disclosure Standards</span>
            <el-tag type="primary" effect="dark" size="large">Framework Hub</el-tag>
          </div>
        </template>
      </el-page-header>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>Overall Compliance</span>
              </div>
              <div class="card-value">78%</div>
              <div class="card-footer">
                <el-progress :percentage="78" :stroke-width="8" />
                <span class="status-text">IFRS S1 + S2</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Check /></el-icon>
                <span>IFRS S1 Status</span>
              </div>
              <div class="card-value">82%</div>
              <div class="card-footer">
                <el-progress :percentage="82" :stroke-width="8" status="success" />
                <span>General Requirements</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>IFRS S2 Status</span>
              </div>
              <div class="card-value">74%</div>
              <div class="card-footer">
                <el-progress :percentage="74" :stroke-width="8" status="warning" />
                <span>Climate-related</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Jurisdictions Adopted</span>
              </div>
              <div class="card-value">28</div>
              <div class="card-footer">
                <el-progress :percentage="56" :stroke-width="8" :format="() => 'Global progress'" />
                <span>Countries & Regions</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Framework Overview Cards -->
      <div class="framework-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="framework-card" shadow="hover">
              <template #header>
                <div class="framework-header">
                  <el-icon><Collection /></el-icon>
                  <span>IFRS S1 - General Requirements</span>
                </div>
              </template>
              <div class="framework-content">
                <el-progress
                    :percentage="82"
                    :stroke-width="12"
                    status="success"
                    :format="() => '82% Complete'"
                />
                <div class="framework-metrics">
                  <div class="metric-item">
                    <span class="metric-label">Core elements disclosed</span>
                    <span class="metric-value">8/10</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Material topics covered</span>
                    <span class="metric-value">12/15</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Assurance level</span>
                    <span class="metric-value">Limited</span>
                  </div>
                </div>
                <el-button type="primary" link @click="viewS1Details">
                  View detailed assessment →
                </el-button>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="framework-card" shadow="hover">
              <template #header>
                <div class="framework-header">
                  <el-icon><Sunny /></el-icon>
                  <span>IFRS S2 - Climate-related Disclosures</span>
                </div>
              </template>
              <div class="framework-content">
                <el-progress
                    :percentage="74"
                    :stroke-width="12"
                    status="warning"
                    :format="() => '74% Complete'"
                />
                <div class="framework-metrics">
                  <div class="metric-item">
                    <span class="metric-label">Governance disclosed</span>
                    <span class="metric-value">Complete</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Strategy & scenario</span>
                    <span class="metric-value">Partial</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">Metrics & targets</span>
                    <span class="metric-value">In progress</span>
                  </div>
                </div>
                <el-button type="primary" link @click="goToIFRSS2">
                  View detailed assessment →
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Compliance Dashboard Tab -->
          <el-tab-pane label="Compliance Dashboard" name="dashboard">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>ISSB Compliance Overview</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="chart-container">
                    <div ref="complianceTrendChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="s1s2ComparisonChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- IFRS S1 Tab -->
          <el-tab-pane label="IFRS S1 Requirements" name="s1">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><List /></el-icon>
                <span>General Requirements for Disclosure of Sustainability-related Financial Information</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="requirements-table">
                    <el-table :data="s1Requirements" border style="width: 100%">
                      <el-table-column prop="requirement" label="Requirement" width="280" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getS1StatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="completion" label="Completion">
                        <template #default="{ row }">
                          <el-progress
                              :percentage="row.completion"
                              :stroke-width="8"
                              :status="row.completion === 100 ? 'success' : undefined"
                          />
                        </template>
                      </el-table-column>
                      <el-table-column prop="deadline" label="Deadline" width="120" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-panel">
                    <div class="panel-title">
                      <el-icon><InfoFilled /></el-icon>
                      <span>Key Requirements Summary</span>
                    </div>
                    <el-timeline>
                      <el-timeline-item
                          v-for="(item, index) in s1Summary"
                          :key="index"
                          :type="item.type"
                          :hollow="true"
                      >
                        <div class="timeline-content">
                          <strong>{{ item.title }}</strong>
                          <p>{{ item.description }}</p>
                        </div>
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- IFRS S2 Tab -->
          <el-tab-pane label="IFRS S2 Climate" name="s2">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Climate /></el-icon>
                <span>Climate-related Disclosures</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="requirements-table">
                    <el-table :data="s2Requirements" border style="width: 100%">
                      <el-table-column prop="pillar" label="Pillar" width="150" />
                      <el-table-column prop="requirement" label="Requirement" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getS2StatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="completion" label="Completion">
                        <template #default="{ row }">
                          <el-progress
                              :percentage="row.completion"
                              :stroke-width="8"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="chart-container">
                    <div ref="s2PillarsChartRef" style="height: 300px"></div>
                  </div>
                  <div class="action-card">
                    <h4>Recommended Actions</h4>
                    <el-checkbox-group v-model="s2Actions">
                      <el-checkbox v-for="action in s2ActionItems" :key="action.value" :label="action.value">
                        {{ action.label }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Gap Analysis Tab -->
          <el-tab-pane label="Gap Analysis" name="gapAnalysis">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                <span>ISSB Disclosure Gap Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="gap-table">
                    <el-table :data="issbGapData" border style="width: 100%">
                      <el-table-column prop="disclosure" label="Disclosure Area" width="220" />
                      <el-table-column prop="standard" label="Standard" width="100" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getGapStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="gap" label="Gap Description" />
                      <el-table-column prop="remediation" label="Remediation Plan" width="200" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="gapChartRef" style="height: 280px"></div>
                  </div>
                  <div class="compliance-timeline">
                    <div class="timeline-header">
                      <el-icon><Calendar /></el-icon>
                      <span>Remediation Timeline</span>
                    </div>
                    <el-timeline>
                      <el-timeline-item
                          v-for="(milestone, index) in remediationMilestones"
                          :key="index"
                          :timestamp="milestone.date"
                          :type="milestone.type"
                      >
                        {{ milestone.description }}
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Jurisdictional Adoption Tab -->
          <el-tab-pane label="Jurisdictional Adoption" name="adoption">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Location /></el-icon>
                <span>Global ISSB Adoption Status</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="adoptionMapChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="adoption-table">
                    <el-table :data="adoptionData" border style="width: 100%" max-height="400">
                      <el-table-column prop="jurisdiction" label="Jurisdiction" width="150" />
                      <el-table-column prop="status" label="Adoption Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getAdoptionStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="effectiveDate" label="Effective Date" width="120" />
                      <el-table-column prop="notes" label="Notes" />
                    </el-table>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateComplianceReport">
          <el-icon><Download /></el-icon>
          Generate ISSB Compliance Report
        </el-button>
        <el-button size="large" @click="exportFrameworkData">
          <el-icon><Share /></el-icon>
          Export Framework Data
        </el-button>
        <el-button size="large" @click="scheduleAssessment">
          <el-icon><Clock /></el-icon>
          Schedule Assessment
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ISSB framework...')

const loadingMessages = [
  'Loading IFRS S1 requirements...',
  'Analyzing IFRS S2 climate disclosures...',
  'Mapping jurisdictional adoption...',
  'Calculating compliance metrics...',
  'Generating gap analysis...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('dashboard')
const rating = ref(3.5)
const s2Actions = ref(['governance', 'risk-management'])
const checkedItems = ref(['governance', 'risk', 'emissions'])

// Chart refs
const complianceTrendChartRef = ref<HTMLElement | null>(null)
const s1s2ComparisonChartRef = ref<HTMLElement | null>(null)
const s2PillarsChartRef = ref<HTLElement | null>(null)
const gapChartRef = ref<HTMLElement | null>(null)
const adoptionMapChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// IFRS S1 Requirements data
const s1Requirements = ref([
  { requirement: 'Governance and oversight', status: 'Compliant', completion: 100, deadline: '2024-06-30' },
  { requirement: 'Strategy and risk management', status: 'Partial', completion: 75, deadline: '2024-09-30' },
  { requirement: 'Materiality assessment', status: 'Compliant', completion: 100, deadline: '2024-06-30' },
  { requirement: 'Scope and boundary definition', status: 'Partial', completion: 80, deadline: '2024-09-30' },
  { requirement: 'Metrics and targets', status: 'In Progress', completion: 60, deadline: '2024-12-31' },
  { requirement: 'Assurance and verification', status: 'Planned', completion: 30, deadline: '2025-03-31' }
])

const s1Summary = ref([
  { title: 'Governance', description: 'Board oversight established for sustainability risks', type: 'success' },
  { title: 'Strategy', description: 'Integration with business strategy in progress', type: 'primary' },
  { title: 'Risk Management', description: 'Processes identified but not fully integrated', type: 'warning' },
  { title: 'Metrics & Targets', description: 'KPIs defined, target setting underway', type: 'info' }
])

// IFRS S2 Requirements data
const s2Requirements = ref([
  { pillar: 'Governance', requirement: 'Climate-related governance disclosure', status: 'Complete', completion: 100 },
  { pillar: 'Strategy', requirement: 'Climate scenario analysis', status: 'Partial', completion: 65 },
  { pillar: 'Strategy', requirement: 'Transition plan disclosure', status: 'Partial', completion: 55 },
  { pillar: 'Risk Management', requirement: 'Climate risk identification', status: 'Complete', completion: 90 },
  { pillar: 'Metrics & Targets', requirement: 'Scope 1,2,3 emissions', status: 'Partial', completion: 70 },
  { pillar: 'Metrics & Targets', requirement: 'Carbon intensity metrics', status: 'Complete', completion: 85 },
  { pillar: 'Metrics & Targets', requirement: 'Emissions reduction targets', status: 'In Progress', completion: 60 }
])

const s2ActionItems = ref([
  { label: 'Complete scenario analysis for 1.5°C pathway', value: 'scenario' },
  { label: 'Disclose transition plan with CAPEX alignment', value: 'transition' },
  { label: 'Verify Scope 3 emissions with suppliers', value: 'scope3' },
  { label: 'Set SBTi-approved near-term targets', value: 'targets' },
  { label: 'Integrate climate into ERM framework', value: 'risk-management' }
])

// Gap analysis data
const issbGapData = ref([
  { disclosure: 'Climate scenario analysis', standard: 'IFRS S2', status: 'Partial', gap: 'Missing 1.5°C scenario', remediation: 'Run additional scenarios by Q1 2025' },
  { disclosure: 'Scope 3 emissions', standard: 'IFRS S2', status: 'Partial', gap: 'Category 15 missing', remediation: 'Engage suppliers for data collection' },
  { disclosure: 'Transition plan', standard: 'IFRS S2', status: 'Non-compliant', gap: 'No CAPEX alignment disclosed', remediation: 'Develop transition plan by Q2 2025' },
  { disclosure: 'Materiality assessment', standard: 'IFRS S1', status: 'Compliant', gap: 'None', remediation: 'Maintain documentation' },
  { disclosure: 'Industry-based metrics', standard: 'IFRS S2', status: 'Partial', gap: 'Missing 2 of 5 metrics', remediation: 'Implement data collection systems' }
])

// Remediation milestones
const remediationMilestones = ref([
  { date: '2024-12-31', description: 'Complete Scope 3 data collection', type: 'primary' },
  { date: '2025-03-31', description: 'Run 1.5°C scenario analysis', type: 'primary' },
  { date: '2025-06-30', description: 'Submit transition plan for approval', type: 'warning' },
  { date: '2025-09-30', description: 'Achieve partial assurance on metrics', type: 'info' },
  { date: '2025-12-31', description: 'Full ISSB compliance', type: 'success' }
])

// Jurisdictional adoption data
const adoptionData = ref([
  { jurisdiction: 'United Kingdom', status: 'Adopted', effectiveDate: '2025-01-01', notes: 'UK SRS aligned' },
  { jurisdiction: 'Japan', status: 'Adopted', effectiveDate: '2025-03-31', notes: 'Voluntary from 2025' },
  { jurisdiction: 'Australia', status: 'Proposed', effectiveDate: '2025-07-01', notes: 'Consultation ongoing' },
  { jurisdiction: 'Canada', status: 'In Progress', effectiveDate: '2025-12-31', notes: 'CSSB standards' },
  { jurisdiction: 'Singapore', status: 'Adopted', effectiveDate: '2025-01-01', notes: 'Mandatory for listed' },
  { jurisdiction: 'Hong Kong', status: 'Proposed', effectiveDate: '2025-12-31', notes: 'HKEX roadmap' },
  { jurisdiction: 'European Union', status: 'Partial', effectiveDate: '2026-01-01', notes: 'ESRS equivalence' },
  { jurisdiction: 'Brazil', status: 'Adopted', effectiveDate: '2024-12-31', notes: 'First adopter' }
])

// Methods
const goBack = () => {
  router.back()
}

const goToIFRSS2 = () => {
  router.push('/data-center-operations/esg-compliance-center/ifrs-s2')
}

const viewS1Details = () => {
  ElMessage.info('Detailed IFRS S1 assessment view coming soon')
}

const getS1StatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'In Progress': 'info',
    'Planned': 'info'
  }
  return map[status] || 'info'
}

const getS2StatusType = (status: string) => {
  const map: Record<string, string> = {
    'Complete': 'success',
    'Partial': 'warning',
    'In Progress': 'info'
  }
  return map[status] || 'info'
}

const getGapStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'Non-compliant': 'danger'
  }
  return map[status] || 'info'
}

const getAdoptionStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Adopted': 'success',
    'Proposed': 'warning',
    'In Progress': 'info',
    'Partial': 'warning'
  }
  return map[status] || 'info'
}

const generateComplianceReport = () => {
  ElMessage.success('ISSB compliance report generation started. You will receive a notification when ready.')
}

const exportFrameworkData = () => {
  ElMessage.success('Framework data export started. File will be downloaded shortly.')
}

const scheduleAssessment = () => {
  ElMessage.info('Assessment scheduling interface will open in a new window.')
}

// Chart initialization
const initComplianceTrendChart = () => {
  if (complianceTrendChartRef.value) {
    const chart = echarts.init(complianceTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['IFRS S1 Compliance', 'IFRS S2 Compliance'] },
      xAxis: { type: 'category', data: ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025'] },
      yAxis: { type: 'value', name: 'Compliance %', max: 100 },
      series: [
        {
          name: 'IFRS S1 Compliance',
          type: 'line',
          data: [55, 65, 72, 78, 85],
          smooth: true,
          lineStyle: { color: '#5470c6', width: 3 },
          areaStyle: { opacity: 0.3 }
        },
        {
          name: 'IFRS S2 Compliance',
          type: 'line',
          data: [45, 55, 65, 72, 80],
          smooth: true,
          lineStyle: { color: '#fac858', width: 3 },
          areaStyle: { opacity: 0.3 }
        }
      ]
    })
    chartInstances.push(chart)
  }
}

const initS1S2ComparisonChart = () => {
  if (s1s2ComparisonChartRef.value) {
    const chart = echarts.init(s1s2ComparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: ['Governance', 'Strategy', 'Risk Mgmt', 'Metrics'] },
      xAxis: { type: 'category', data: ['IFRS S1', 'IFRS S2'] },
      yAxis: { type: 'value', name: 'Compliance %' },
      series: [
        { name: 'Governance', type: 'bar', data: [95, 100], itemStyle: { color: '#5470c6' } },
        { name: 'Strategy', type: 'bar', data: [75, 60], itemStyle: { color: '#fac858' } },
        { name: 'Risk Mgmt', type: 'bar', data: [80, 85], itemStyle: { color: '#ee6666' } },
        { name: 'Metrics', type: 'bar', data: [70, 65], itemStyle: { color: '#73c0de' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initS2PillarsChart = () => {
  if (s2PillarsChartRef.value) {
    const chart = echarts.init(s2PillarsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'IFRS S2 Pillars',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 100, name: 'Governance', itemStyle: { color: '#67c23a' } },
          { value: 65, name: 'Strategy', itemStyle: { color: '#e6a23c' } },
          { value: 90, name: 'Risk Management', itemStyle: { color: '#409eff' } },
          { value: 72, name: 'Metrics & Targets', itemStyle: { color: '#fac858' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initGapChart = () => {
  if (gapChartRef.value) {
    const chart = echarts.init(gapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Gap Status',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 40, name: 'Compliant', itemStyle: { color: '#67c23a' } },
          { value: 45, name: 'Partial', itemStyle: { color: '#e6a23c' } },
          { value: 15, name: 'Non-compliant', itemStyle: { color: '#f56c6c' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initAdoptionMapChart = () => {
  if (adoptionMapChartRef.value) {
    const chart = echarts.init(adoptionMapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { containLabel: true },
      xAxis: { type: 'category', data: ['UK', 'Japan', 'SG', 'Brazil', 'Australia', 'Canada', 'HK', 'EU'] },
      yAxis: { type: 'value', name: 'Progress' },
      series: [{
        name: 'Adoption Progress',
        type: 'bar',
        data: [95, 90, 85, 80, 60, 55, 50, 45],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#3b82f6' },
              { offset: 1, color: '#8b5cf6' }
            ]
          }
        },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

onMounted(() => {
  let messageIndex = 0
  let progressInterval: ReturnType<typeof setInterval>
  let messageInterval: ReturnType<typeof setInterval>

  messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      const increment = Math.random() * 12 + 3
      loadingProgress.value = Math.min(loadingProgress.value + increment, 100)
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      setTimeout(() => {
        initComplianceTrendChart()
        initS1S2ComparisonChart()
        initS2PillarsChart()
        initGapChart()
        initAdoptionMapChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.issb-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading-overlay {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  animation: fadeInUp 0.6s ease-out;
}

.loading-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 24px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 3px solid transparent;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots {
  display: inline-flex;
  gap: 2px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 320px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a);
  border-radius: 4px;
  transition: width 0.3s ease;
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
}

@keyframes shimmer {
  0% { background-position: 0% 0%; }
  100% { background-position: 200% 0%; }
}

.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Content Styles ==================== */
.issb-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.overview-section,
.framework-section {
  margin: 24px 0;
}

.overview-card {
  border-radius: 12px;
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.card-header .el-icon {
  font-size: 18px;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-text {
  font-size: 12px;
  color: #909399;
}

.framework-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.framework-card:hover {
  transform: translateY(-2px);
}

.framework-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.framework-header .el-icon {
  font-size: 20px;
  color: #409eff;
}

.framework-content {
  padding: 8px 0;
}

.framework-metrics {
  margin: 20px 0;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.metric-label {
  color: #606266;
}

.metric-value {
  font-weight: 500;
  color: #303133;
}

.main-content-card {
  margin-top: 20px;
  border-radius: 12px;
}

.tab-content {
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e4e7ed;
}

.section-title .el-icon {
  font-size: 22px;
  color: #409eff;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.info-panel {
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.timeline-content {
  padding-left: 8px;
}

.timeline-content strong {
  display: block;
  margin-bottom: 4px;
}

.timeline-content p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.requirements-table,
.gap-table,
.adoption-table {
  border-radius: 8px;
  overflow: hidden;
}

.action-card {
  margin-top: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.action-card h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.action-card .el-checkbox {
  display: block;
  margin-bottom: 10px;
}

.compliance-timeline {
  margin-top: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
}

.action-buttons {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.action-buttons .el-button {
  border-radius: 8px;
}

:deep(.el-tabs--border-card) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-progress__text) {
  font-size: 12px;
}

:deep(.el-descriptions__label) {
  font-weight: 600;
}
</style>