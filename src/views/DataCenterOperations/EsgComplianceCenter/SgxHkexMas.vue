<template>
  <div class="sgx-hkex-mas-container">
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
            <span class="loading-title">Loading ESG Regulatory Frameworks</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">SGX | HKEX | MAS</div>
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
            <span class="page-title">SGX / HKEX / MAS - ESG Regulatory Compliance</span>
            <el-tag type="success" effect="dark" size="large">Asia-Pacific Hub</el-tag>
          </div>
        </template>
      </el-page-header>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card sgx-card">
              <div class="card-header">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23d32f2f'%3E%3Cpath d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E" class="regulator-icon" />
                <span>SGX Compliance</span>
              </div>
              <div class="card-value">79%</div>
              <div class="card-footer">
                <el-progress :percentage="79" :stroke-width="8" />
                <span class="status-text">Board Diversity + Climate</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card hkex-card">
              <div class="card-header">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%234caf50'%3E%3Cpath d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E" class="regulator-icon" />
                <span>HKEX Compliance</span>
              </div>
              <div class="card-value">73%</div>
              <div class="card-footer">
                <el-progress :percentage="73" :stroke-width="8" />
                <span class="status-text">ESG Guide + TCFD</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card mas-card">
              <div class="card-header">
                <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%232196f3'%3E%3Cpath d='M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5'/%3E%3C/svg%3E" class="regulator-icon" />
                <span>MAS Compliance</span>
              </div>
              <div class="card-value">68%</div>
              <div class="card-footer">
                <el-progress :percentage="68" :stroke-width="8" />
                <span class="status-text">Green Finance + Taxonomies</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>Regional Avg.</span>
              </div>
              <div class="card-value">73%</div>
              <div class="card-footer">
                <el-progress :percentage="73" :stroke-width="8" status="warning" />
                <span>Asia-Pacific Benchmark</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Regulator Navigation -->
      <div class="regulator-nav">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="nav-card sgx" :class="{ active: activeRegulator === 'sgx' }" @click="activeRegulator = 'sgx'; activeTab = 'sgx'">
              <div class="nav-icon">
                <span class="regulator-symbol">SGX</span>
              </div>
              <h3>Singapore Exchange</h3>
              <p>Climate & Board Diversity Mandates</p>
              <div class="nav-progress">
                <el-progress :percentage="79" :stroke-width="6" status="success" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="nav-card hkex" :class="{ active: activeRegulator === 'hkex' }" @click="activeRegulator = 'hkex'; activeTab = 'hkex'">
              <div class="nav-icon">
                <span class="regulator-symbol">HKEX</span>
              </div>
              <h3>Hong Kong Exchange</h3>
              <p>ESG Guide & TCFD-aligned</p>
              <div class="nav-progress">
                <el-progress :percentage="73" :stroke-width="6" status="warning" :show-text="false" />
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="nav-card mas" :class="{ active: activeRegulator === 'mas' }" @click="activeRegulator = 'mas'; activeTab = 'mas'">
              <div class="nav-icon">
                <span class="regulator-symbol">MAS</span>
              </div>
              <h3>Monetary Authority</h3>
              <p>Green Finance & Taxonomies</p>
              <div class="nav-progress">
                <el-progress :percentage="68" :stroke-width="6" status="warning" :show-text="false" />
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- SGX Tab -->
          <el-tab-pane label="SGX" name="sgx">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><OfficeBuilding /></el-icon>
                <span>SGX ESG Compliance Framework</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="sgxChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="requirements-list">
                    <h4>Key SGX Requirements</h4>
                    <el-collapse v-model="sgxCollapse">
                      <el-collapse-item title="Climate Reporting" name="climate">
                        <p>Mandatory climate reporting from FY2025 for all issuers</p>
                        <el-tag type="danger">Effective 2025</el-tag>
                      </el-collapse-item>
                      <el-collapse-item title="Board Diversity" name="diversity">
                        <p>Policy disclosure on gender, skills, and experience</p>
                        <el-tag type="warning">Comply or Explain</el-tag>
                      </el-collapse-item>
                      <el-collapse-item title="TCFD Alignment" name="tcfd">
                        <p>Four pillars: Governance, Strategy, Risk, Metrics</p>
                        <el-tag type="info">Phased approach</el-tag>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-col>
              </el-row>
              <div class="sgx-table-section">
                <h4>SGX Rulebook - ESG Metrics</h4>
                <el-table :data="sgxData" border style="width: 100%">
                  <el-table-column prop="metric" label="ESG Metric" width="250" />
                  <el-table-column prop="requirement" label="Requirement" />
                  <el-table-column prop="status" label="Status" width="120">
                    <template #default="{ row }">
                      <el-tag :type="getStatusType(row.status)">
                        {{ row.status }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>

          <!-- HKEX Tab -->
          <el-tab-pane label="HKEX" name="hkex">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>HKEX ESG Reporting Guide</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="hkexChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="timeline-section">
                    <h4>HKEX Implementation Timeline</h4>
                    <el-timeline>
                      <el-timeline-item timestamp="2024" type="primary">Mandatory climate disclosures for all issuers</el-timeline-item>
                      <el-timeline-item timestamp="2025" type="primary">TCFD-aligned reporting required</el-timeline-item>
                      <el-timeline-item timestamp="2026" type="warning">Scope 3 emissions disclosure</el-timeline-item>
                      <el-timeline-item timestamp="2027" type="success">Full ISSB alignment</el-timeline-item>
                    </el-timeline>
                  </div>
                </el-col>
              </el-row>
              <div class="hkex-table-section">
                <h4>HKEX ESG Guide - Subject Matters</h4>
                <el-table :data="hkexData" border style="width: 100%">
                  <el-table-column prop="area" label="ESG Area" width="200" />
                  <el-table-column prop="disclosure" label="Disclosure Requirement" />
                  <el-table-column prop="compliance" label="Compliance" width="120">
                    <template #default="{ row }">
                      <el-progress :percentage="row.compliance" :stroke-width="8" />
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>

          <!-- MAS Tab -->
          <el-tab-pane label="MAS" name="mas">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>MAS Green Finance Initiatives</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="masChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="taxonomy-section">
                    <h4>Singapore-Asia Taxonomy</h4>
                    <el-table :data="taxonomyData" border size="small">
                      <el-table-column prop="sector" label="Sector" width="120" />
                      <el-table-column prop="criteria" label="Green Criteria" />
                      <el-table-column prop="status" label="Status" width="100">
                        <template #default="{ row }">
                          <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
              </el-row>
              <div class="mas-initiatives">
                <h4>Key MAS Initiatives</h4>
                <el-row :gutter="20">
                  <el-col :span="8">
                    <div class="initiative-card">
                      <el-icon><Document /></el-icon>
                      <h5>Green Bond Grant</h5>
                      <p>S$100k for green bond issuance</p>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="initiative-card">
                      <el-icon><Coin /></el-icon>
                      <h5>Green FinTech Hub</h5>
                      <p>Supporting sustainable fintech</p>
                    </div>
                  </el-col>
                  <el-col :span="8">
                    <div class="initiative-card">
                      <el-icon><Connection /></el-icon>
                      <h5>Project Greenprint</h5>
                      <p>ESG data & verification platform</p>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-tab-pane>

          <!-- Cross-Regulator Comparison Tab -->
          <el-tab-pane label="Comparison" name="comparison">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Connection /></el-icon>
                <span>Cross-Regulator Comparison</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="24">
                  <div class="comparison-table">
                    <el-table :data="comparisonData" border style="width: 100%">
                      <el-table-column prop="requirement" label="Requirement" width="250" />
                      <el-table-column prop="sgx" label="SGX" width="120">
                        <template #default="{ row }">
                          <el-tag :type="row.sgx === 'Yes' ? 'success' : row.sgx === 'Partial' ? 'warning' : 'info'">
                            {{ row.sgx }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="hkex" label="HKEX" width="120">
                        <template #default="{ row }">
                          <el-tag :type="row.hkex === 'Yes' ? 'success' : row.hkex === 'Partial' ? 'warning' : 'info'">
                            {{ row.hkex }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="mas" label="MAS" width="120">
                        <template #default="{ row }">
                          <el-tag :type="row.mas === 'Yes' ? 'success' : row.mas === 'Partial' ? 'warning' : 'info'">
                            {{ row.mas }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="deadline" label="Key Deadline" />
                    </el-table>
                  </div>
                </el-col>
              </el-row>
              <div class="chart-container comparison-chart">
                <div ref="comparisonChartRef" style="height: 400px"></div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Gap Analysis Tab -->
          <el-tab-pane label="Gap Analysis" name="gap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                <span>Regulatory Gap Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="gap-table">
                    <el-table :data="gapData" border style="width: 100%">
                      <el-table-column prop="regulator" label="Regulator" width="100" />
                      <el-table-column prop="gap" label="Gap Description" width="250" />
                      <el-table-column prop="priority" label="Priority" width="100">
                        <template #default="{ row }">
                          <el-tag :type="row.priority === 'High' ? 'danger' : row.priority === 'Medium' ? 'warning' : 'info'">
                            {{ row.priority }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="remediation" label="Remediation Plan" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="gapChartRef" style="height: 280px"></div>
                  </div>
                  <div class="remediation-timeline">
                    <h4>Remediation Timeline</h4>
                    <el-timeline>
                      <el-timeline-item
                          v-for="(step, index) in remediationSteps"
                          :key="index"
                          :timestamp="step.date"
                          :type="step.type"
                      >
                        {{ step.description }}
                      </el-timeline-item>
                    </el-timeline>
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
          Generate Cross-Regulator Report
        </el-button>
        <el-button size="large" @click="exportComparison">
          <el-icon><Share /></el-icon>
          Export Comparison Matrix
        </el-button>
        <el-button size="large" @click="scheduleRemediation">
          <el-icon><Clock /></el-icon>
          Plan Remediation Activities
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading ESG regulatory frameworks...')

const loadingMessages = [
  'Loading SGX requirements...',
  'Analyzing HKEX ESG Guide...',
  'Processing MAS taxonomies...',
  'Comparing regulatory frameworks...',
  'Assessing compliance gaps...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('sgx')
const activeRegulator = ref('sgx')
const sgxCollapse = ref(['climate'])

// Chart refs
const sgxChartRef = ref<HTMLElement | null>(null)
const hkexChartRef = ref<HTMLElement | null>(null)
const masChartRef = ref<HTMLElement | null>(null)
const comparisonChartRef = ref<HTMLElement | null>(null)
const gapChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// SGX Data
const sgxData = ref([
  { metric: 'GHG Emissions (Scope 1 & 2)', requirement: 'Mandatory disclosure', status: 'Compliant' },
  { metric: 'Climate Risk Assessment', requirement: 'TCFD-aligned', status: 'Partial' },
  { metric: 'Board Diversity Policy', requirement: 'Disclose targets', status: 'Compliant' },
  { metric: 'Workplace Safety Metrics', requirement: 'Annual disclosure', status: 'Compliant' },
  { metric: 'Supplier ESG Screening', requirement: 'Describe practices', status: 'Partial' },
  { metric: 'Anti-corruption Training', requirement: 'Disclose hours', status: 'Compliant' }
])

// HKEX Data
const hkexData = ref([
  { area: 'Emissions', disclosure: 'GHG emissions data', compliance: 85 },
  { area: 'Energy', disclosure: 'Energy consumption', compliance: 90 },
  { area: 'Water', disclosure: 'Water usage & efficiency', compliance: 75 },
  { area: 'Waste', disclosure: 'Waste reduction targets', compliance: 65 },
  { area: 'Social', disclosure: 'Employment & diversity', compliance: 80 },
  { area: 'Community', disclosure: 'Investment & impact', compliance: 55 }
])

// MAS Taxonomy Data
const taxonomyData = ref([
  { sector: 'Energy', criteria: 'Solar, wind, hydrogen', status: 'Active' },
  { sector: 'Transport', criteria: 'EV, public transport', status: 'Active' },
  { sector: 'Buildings', criteria: 'Green certifications', status: 'Active' },
  { sector: 'Waste Management', criteria: 'Circular economy', status: 'Draft' },
  { sector: 'Agriculture', criteria: 'Sustainable practices', status: 'Draft' }
])

// Comparison Data
const comparisonData = ref([
  { requirement: 'Climate Reporting', sgx: 'Yes', hkex: 'Yes', mas: 'Partial', deadline: '2025' },
  { requirement: 'Board Diversity', sgx: 'Yes', hkex: 'Yes', mas: 'No', deadline: '2024' },
  { requirement: 'Scope 3 Emissions', sgx: 'Partial', hkex: 'Yes', mas: 'Partial', deadline: '2026' },
  { requirement: 'TCFD Alignment', sgx: 'Yes', hkex: 'Yes', mas: 'Partial', deadline: '2025' },
  { requirement: 'Green Taxonomy', sgx: 'No', hkex: 'No', mas: 'Yes', deadline: '2024' },
  { requirement: 'External Assurance', sgx: 'Partial', hkex: 'Partial', mas: 'No', deadline: '2025' }
])

// Gap Data
const gapData = ref([
  { regulator: 'SGX', gap: 'Scope 3 emissions data collection incomplete', priority: 'High', remediation: 'Engage suppliers for data' },
  { regulator: 'SGX', gap: 'Climate scenario analysis not completed', priority: 'Medium', remediation: 'Run 1.5°C scenario' },
  { regulator: 'HKEX', gap: 'Waste reduction targets not quantified', priority: 'Medium', remediation: 'Set measurable targets' },
  { regulator: 'HKEX', gap: 'Community investment data missing', priority: 'Low', remediation: 'Track community programs' },
  { regulator: 'MAS', gap: 'Green taxonomy alignment assessment needed', priority: 'High', remediation: 'Map activities to taxonomy' },
  { regulator: 'MAS', gap: 'Green bond reporting framework', priority: 'Medium', remediation: 'Implement tracking system' }
])

// Remediation Steps
const remediationSteps = ref([
  { date: 'Q4 2024', description: 'Complete climate scenario analysis', type: 'primary' },
  { date: 'Q1 2025', description: 'Implement Scope 3 data collection', type: 'primary' },
  { date: 'Q2 2025', description: 'Set waste reduction targets', type: 'warning' },
  { date: 'Q3 2025', description: 'Map activities to MAS taxonomy', type: 'warning' },
  { date: 'Q4 2025', description: 'Full regulatory compliance', type: 'success' }
])

// Methods
const goBack = () => {
  router.back()
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'No': 'info'
  }
  return map[status] || 'info'
}

const generateComplianceReport = () => {
  ElMessage.success('Cross-regulator compliance report generation started. You will receive a notification when ready.')
}

const exportComparison = () => {
  ElMessage.success('Comparison matrix export started. File will be downloaded shortly.')
}

const scheduleRemediation = () => {
  ElMessage.info('Remediation planning interface will open in a new window.')
}

// Chart initialization
const initSGXChart = () => {
  if (sgxChartRef.value) {
    const chart = echarts.init(sgxChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Climate', 'Social', 'Governance'] },
      radar: {
        indicator: [
          { name: 'Disclosure', max: 100 },
          { name: 'Data Quality', max: 100 },
          { name: 'Target Setting', max: 100 },
          { name: 'Assurance', max: 100 },
          { name: 'Integration', max: 100 }
        ]
      },
      series: [{
        type: 'radar',
        data: [
          { value: [85, 75, 70, 60, 80], name: 'Climate', areaStyle: { color: 'rgba(211, 47, 47, 0.2)' } },
          { value: [80, 70, 65, 55, 75], name: 'Social', areaStyle: { color: 'rgba(76, 175, 80, 0.2)' } },
          { value: [90, 80, 75, 65, 85], name: 'Governance', areaStyle: { color: 'rgba(33, 150, 243, 0.2)' } }
        ]
      }]
    })
    chartInstances.push(chart)
  }
}

const initHKEXChart = () => {
  if (hkexChartRef.value) {
    const chart = echarts.init(hkexChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Emissions', 'Energy', 'Water', 'Waste', 'Social', 'Community'] },
      yAxis: { type: 'value', name: 'Compliance %', max: 100 },
      series: [{
        type: 'bar',
        data: [85, 90, 75, 65, 80, 55],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#4caf50' },
              { offset: 1, color: '#2e7d32' }
            ]
          }
        },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initMASChart = () => {
  if (masChartRef.value) {
    const chart = echarts.init(masChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Green Finance Initiatives',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 40, name: 'Green Bonds', itemStyle: { color: '#2196f3' } },
          { value: 25, name: 'Green Loans', itemStyle: { color: '#4caf50' } },
          { value: 20, name: 'Sustainability-linked', itemStyle: { color: '#ff9800' } },
          { value: 15, name: 'Transition Finance', itemStyle: { color: '#9c27b0' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initComparisonChart = () => {
  if (comparisonChartRef.value) {
    const chart = echarts.init(comparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['SGX', 'HKEX', 'MAS'] },
      xAxis: { type: 'category', data: ['Climate', 'Diversity', 'Scope 3', 'TCFD', 'Taxonomy', 'Assurance'] },
      yAxis: { type: 'value', name: 'Compliance Score', max: 100 },
      series: [
        { name: 'SGX', type: 'bar', data: [85, 90, 60, 80, 0, 50], itemStyle: { color: '#d32f2f' } },
        { name: 'HKEX', type: 'bar', data: [80, 85, 70, 85, 0, 55], itemStyle: { color: '#4caf50' } },
        { name: 'MAS', type: 'bar', data: [50, 30, 55, 45, 80, 40], itemStyle: { color: '#2196f3' } }
      ]
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
        name: 'Gap Priority',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 35, name: 'High Priority', itemStyle: { color: '#f56c6c' } },
          { value: 50, name: 'Medium Priority', itemStyle: { color: '#e6a23c' } },
          { value: 15, name: 'Low Priority', itemStyle: { color: '#67c23a' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

// Watch for regulator changes
watch(activeRegulator, (newVal) => {
  if (newVal === 'sgx') activeTab.value = 'sgx'
  else if (newVal === 'hkex') activeTab.value = 'hkex'
  else if (newVal === 'mas') activeTab.value = 'mas'
})

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
        initSGXChart()
        initHKEXChart()
        initMASChart()
        initComparisonChart()
        initGapChart()
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
.sgx-hkex-mas-container {
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
  border: 1px solid rgba(76, 175, 80, 0.3);
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
  border-top-color: #d32f2f;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #4caf50;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #2196f3;
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
  background: linear-gradient(90deg, #d32f2f, #4caf50, #2196f3);
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
.sgx-hkex-mas-container {
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

.overview-section {
  margin: 24px 0;
}

.overview-card {
  border-radius: 12px;
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.regulator-icon {
  width: 20px;
  height: 20px;
}

.sgx-card .card-header { color: #d32f2f; }
.hkex-card .card-header { color: #4caf50; }
.mas-card .card-header { color: #2196f3; }

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  margin-bottom: 16px;
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

/* Regulator Navigation */
.regulator-nav {
  margin-bottom: 24px;
}

.nav-card {
  background: white;
  border-radius: 12px;
  padding: 24px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  height: 100%;
}

.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.1);
}

.nav-card.sgx.active { border-color: #d32f2f; background: #fef0f0; }
.nav-card.hkex.active { border-color: #4caf50; background: #ecfdf5; }
.nav-card.mas.active { border-color: #2196f3; background: #ecf5ff; }

.nav-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  border-radius: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.regulator-symbol {
  font-size: 20px;
  font-weight: 700;
}

.nav-card.sgx .nav-icon { background: #fef0f0; color: #d32f2f; }
.nav-card.hkex .nav-icon { background: #ecfdf5; color: #4caf50; }
.nav-card.mas .nav-icon { background: #ecf5ff; color: #2196f3; }

.nav-card h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
}

.nav-card p {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #909399;
}

.nav-progress {
  margin-top: 8px;
}

/* Main Content */
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
  color: #4caf50;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.requirements-list,
.timeline-section,
.taxonomy-section {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.requirements-list h4,
.timeline-section h4,
.taxonomy-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.sgx-table-section,
.hkex-table-section {
  margin-top: 24px;
}

.sgx-table-section h4,
.hkex-table-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* Initiatives */
.mas-initiatives {
  margin-top: 24px;
}

.mas-initiatives h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.initiative-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  transition: all 0.3s ease;
  height: 100%;
}

.initiative-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.initiative-card .el-icon {
  font-size: 32px;
  color: #2196f3;
  margin-bottom: 12px;
}

.initiative-card h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
}

.initiative-card p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

/* Comparison Section */
.comparison-table {
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
}

.comparison-chart {
  margin-top: 24px;
}

/* Remediation */
.remediation-timeline {
  margin-top: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.remediation-timeline h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* Action Buttons */
.action-buttons {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.action-buttons .el-button {
  border-radius: 8px;
}

/* Deep Selectors */
:deep(.el-tabs--border-card) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-progress__text) {
  font-size: 12px;
}

:deep(.el-collapse-item__header) {
  font-weight: 500;
}
</style>