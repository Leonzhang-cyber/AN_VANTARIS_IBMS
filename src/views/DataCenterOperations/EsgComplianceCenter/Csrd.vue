<template>
  <div class="csrd-container">
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
            <span class="loading-title">Loading CSRD Framework</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Corporate Sustainability Reporting Directive</div>
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
            <span class="page-title">CSRD - Corporate Sustainability Reporting Directive</span>
            <el-tag type="info" effect="dark" size="large">EU Directive</el-tag>
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
                <span>Overall CSRD Readiness</span>
              </div>
              <div class="card-value">68%</div>
              <div class="card-footer">
                <el-progress :percentage="68" :stroke-width="8" />
                <span class="status-text">In Progress</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Calendar /></el-icon>
                <span>Compliance Deadline</span>
              </div>
              <div class="card-value">18 mos</div>
              <div class="card-footer">
                <el-progress :percentage="30" :stroke-width="8" status="warning" />
                <span>Starting 2025 Reporting</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Applicable Entities</span>
              </div>
              <div class="card-value">15</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" status="success" />
                <span>EU Subsidiaries</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>ESRS Coverage</span>
              </div>
              <div class="card-value">71%</div>
              <div class="card-footer">
                <el-progress :percentage="71" :stroke-width="8" status="warning" />
                <span>12 of 12 Standards</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Timeline Section -->
      <div class="timeline-section">
        <el-card class="timeline-card" shadow="hover">
          <div class="timeline-header">
            <el-icon><Clock /></el-icon>
            <span>CSRD Implementation Timeline</span>
          </div>
          <el-steps :active="2" align-center finish-status="success">
            <el-step title="Preparation" description="Gap Analysis & Data Collection" />
            <el-step title="Implementation" description="Systems & Processes Setup" />
            <el-step title="Pilot Reporting" description="Internal Validation" />
            <el-step title="Assurance" description="Limited Assurance" />
            <el-step title="Compliance" description="First Official Report" />
          </el-steps>
        </el-card>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Compliance Dashboard Tab -->
          <el-tab-pane label="Compliance Dashboard" name="dashboard">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>CSRD Compliance Overview</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="complianceRadarChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="readinessChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- ESRS Standards Tab -->
          <el-tab-pane label="ESRS Standards" name="esrs">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><List /></el-icon>
                <span>European Sustainability Reporting Standards</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="24">
                  <el-tabs v-model="esrsTab" type="card" class="esrs-tabs">
                    <!-- Cross-cutting Standards -->
                    <el-tab-pane label="Cross-cutting" name="cross">
                      <el-table :data="crossCuttingStandards" border style="width: 100%">
                        <el-table-column prop="standard" label="Standard" width="150" />
                        <el-table-column prop="requirement" label="Requirement" width="250" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getStandardStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="completion" label="Completion">
                          <template #default="{ row }">
                            <el-progress :percentage="row.completion" :stroke-width="8" />
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>

                    <!-- Environmental Standards -->
                    <el-tab-pane label="Environmental (E1-E5)" name="environmental">
                      <el-table :data="environmentalStandards" border style="width: 100%">
                        <el-table-column prop="standard" label="Standard" width="150" />
                        <el-table-column prop="topic" label="Topic" width="200" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getStandardStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="progress" label="Progress">
                          <template #default="{ row }">
                            <el-progress :percentage="row.progress" :stroke-width="8" />
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>

                    <!-- Social Standards -->
                    <el-tab-pane label="Social (S1-S4)" name="social">
                      <el-table :data="socialStandards" border style="width: 100%">
                        <el-table-column prop="standard" label="Standard" width="150" />
                        <el-table-column prop="topic" label="Topic" width="200" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getStandardStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="deadline" label="Target Deadline" width="120" />
                      </el-table>
                    </el-tab-pane>

                    <!-- Governance Standards -->
                    <el-tab-pane label="Governance (G1)" name="governance">
                      <el-table :data="governanceStandards" border style="width: 100%">
                        <el-table-column prop="standard" label="Standard" width="150" />
                        <el-table-column prop="requirement" label="Requirement" width="250" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getStandardStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="action" label="Action Required" />
                      </el-table>
                    </el-tab-pane>
                  </el-tabs>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Double Materiality Tab -->
          <el-tab-pane label="Double Materiality" name="materiality">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><PieChart /></el-icon>
                <span>Double Materiality Assessment</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="materialityMatrixChartRef" style="height: 450px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="materiality-summary">
                    <div class="impact-materiality">
                      <h4>Impact Materiality (Inside-out)</h4>
                      <div v-for="item in impactMateriality" :key="item.topic" class="materiality-item">
                        <span>{{ item.topic }}</span>
                        <el-tag :type="item.level === 'High' ? 'danger' : item.level === 'Medium' ? 'warning' : 'info'" size="small">
                          {{ item.level }}
                        </el-tag>
                      </div>
                    </div>
                    <div class="financial-materiality">
                      <h4>Financial Materiality (Outside-in)</h4>
                      <div v-for="item in financialMateriality" :key="item.topic" class="materiality-item">
                        <span>{{ item.topic }}</span>
                        <el-tag :type="item.level === 'High' ? 'danger' : item.level === 'Medium' ? 'warning' : 'info'" size="small">
                          {{ item.level }}
                        </el-tag>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Disclosure Requirements Tab -->
          <el-tab-pane label="Disclosure Requirements" name="disclosures">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DocumentChecked /></el-icon>
                <span>ESRS Disclosure Requirements</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="disclosure-table">
                    <el-table :data="disclosureData" border style="width: 100%" max-height="500">
                      <el-table-column prop="esrs" label="ESRS" width="100" />
                      <el-table-column prop="disclosure" label="Disclosure Requirement" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getDisclosureStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="evidence" label="Evidence / Data Source" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="disclosure-summary">
                    <div class="summary-stat">
                      <div class="stat-number">145</div>
                      <div class="stat-label">Total Data Points</div>
                    </div>
                    <div class="summary-stat">
                      <div class="stat-number">98</div>
                      <div class="stat-label">Data Points Collected</div>
                    </div>
                    <div class="summary-stat">
                      <div class="stat-number">47</div>
                      <div class="stat-label">Gaps to Address</div>
                    </div>
                    <el-divider />
                    <div class="data-collection-status">
                      <h4>Data Collection Status</h4>
                      <el-progress :percentage="68" :stroke-width="12" />
                      <p>Target: 100% by Q3 2025</p>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Assurance & Audit Tab -->
          <el-tab-pane label="Assurance & Audit" name="assurance">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Finished /></el-icon>
                <span>Assurance Readiness</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="assuranceChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="assurance-checklist">
                    <h4>Limited Assurance Preparation</h4>
                    <el-checkbox-group v-model="assuranceItems">
                      <el-checkbox v-for="item in assuranceChecklist" :key="item.value" :label="item.value">
                        {{ item.label }}
                      </el-checkbox>
                    </el-checkbox-group>
                    <div class="audit-timeline">
                      <h4>Audit Timeline</h4>
                      <el-timeline>
                        <el-timeline-item timestamp="Q2 2025" type="primary">Internal audit readiness review</el-timeline-item>
                        <el-timeline-item timestamp="Q3 2025" type="primary">Engage external assurance provider</el-timeline-item>
                        <el-timeline-item timestamp="Q4 2025" type="warning">Limited assurance testing</el-timeline-item>
                        <el-timeline-item timestamp="Q1 2026" type="success">Assurance opinion issued</el-timeline-item>
                      </el-timeline>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Gap Analysis Tab -->
          <el-tab-pane label="Gap Analysis" name="gap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                <span>CSRD Gap Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="gap-table">
                    <el-table :data="csrdGapData" border style="width: 100%">
                      <el-table-column prop="area" label="Area" width="150" />
                      <el-table-column prop="gap" label="Gap Description" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getGapStatusType(row.status)">
                            {{ row.status }}
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
                    <h4>Remediation Roadmap</h4>
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
        <el-button type="primary" size="large" @click="generateReadinessReport">
          <el-icon><Download /></el-icon>
          Generate Readiness Report
        </el-button>
        <el-button size="large" @click="exportMateriality">
          <el-icon><Share /></el-icon>
          Export Materiality Matrix
        </el-button>
        <el-button size="large" @click="scheduleAssurance">
          <el-icon><Clock /></el-icon>
          Plan Assurance Preparation
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
const loadingMessage = ref('Loading CSRD framework...')

const loadingMessages = [
  'Loading ESRS standards...',
  'Analyzing double materiality...',
  'Mapping disclosure requirements...',
  'Assessing assurance readiness...',
  'Calculating compliance gaps...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('dashboard')
const esrsTab = ref('cross')
const assuranceItems = ref(['governance', 'processes', 'data-quality'])

// Chart refs
const complianceRadarChartRef = ref<HTMLElement | null>(null)
const readinessChartRef = ref<HTMLElement | null>(null)
const materialityMatrixChartRef = ref<HTMLElement | null>(null)
const assuranceChartRef = ref<HTMLElement | null>(null)
const gapChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Cross-cutting Standards Data
const crossCuttingStandards = ref([
  { standard: 'ESRS 1', requirement: 'General requirements', status: 'Implemented', completion: 95 },
  { standard: 'ESRS 2', requirement: 'General disclosures', status: 'Partial', completion: 75 },
  { standard: 'ESRS 2', requirement: 'Governance, strategy, risk management', status: 'Partial', completion: 70 }
])

// Environmental Standards Data
const environmentalStandards = ref([
  { standard: 'ESRS E1', topic: 'Climate change', status: 'In Progress', progress: 65 },
  { standard: 'ESRS E2', topic: 'Pollution', status: 'Partial', progress: 55 },
  { standard: 'ESRS E3', topic: 'Water & marine resources', status: 'In Progress', progress: 60 },
  { standard: 'ESRS E4', topic: 'Biodiversity & ecosystems', status: 'Not Started', progress: 25 },
  { standard: 'ESRS E5', topic: 'Resource use & circular economy', status: 'Partial', progress: 50 }
])

// Social Standards Data
const socialStandards = ref([
  { standard: 'ESRS S1', topic: 'Own workforce', status: 'In Progress', deadline: 'Q2 2025' },
  { standard: 'ESRS S2', topic: 'Workers in value chain', status: 'Not Started', deadline: 'Q3 2025' },
  { standard: 'ESRS S3', topic: 'Affected communities', status: 'Not Started', deadline: 'Q4 2025' },
  { standard: 'ESRS S4', topic: 'Consumers & end-users', status: 'Not Started', deadline: 'Q4 2025' }
])

// Governance Standards Data
const governanceStandards = ref([
  { standard: 'ESRS G1', requirement: 'Business conduct', status: 'Partial', action: 'Enhance anti-corruption policies' },
  { standard: 'ESRS G1', requirement: 'Tax strategy', status: 'Implemented', action: 'Maintain documentation' },
  { standard: 'ESRS G1', requirement: 'Supplier relationships', status: 'Partial', action: 'Expand due diligence' }
])

// Impact Materiality
const impactMateriality = ref([
  { topic: 'Climate change mitigation', level: 'High' },
  { topic: 'Energy efficiency', level: 'High' },
  { topic: 'Employee well-being', level: 'Medium' },
  { topic: 'Circular economy', level: 'Medium' },
  { topic: 'Biodiversity impact', level: 'Low' }
])

// Financial Materiality
const financialMateriality = ref([
  { topic: 'Carbon pricing risk', level: 'High' },
  { topic: 'Regulatory compliance', level: 'High' },
  { topic: 'Reputation and brand', level: 'Medium' },
  { topic: 'Supply chain disruption', level: 'Medium' },
  { topic: 'Litigation risk', level: 'Low' }
])

// Disclosure Data
const disclosureData = ref([
  { esrs: 'ESRS 2', disclosure: 'Governance structure and oversight', status: 'Partial', evidence: 'Board charters in place' },
  { esrs: 'ESRS 2', disclosure: 'Strategy and business model', status: 'Partial', evidence: 'Sustainability strategy' },
  { esrs: 'ESRS 2', disclosure: 'Materiality assessment process', status: 'Implemented', evidence: 'Assessment report' },
  { esrs: 'ESRS E1', disclosure: 'GHG emissions (Scope 1,2,3)', status: 'Partial', evidence: '2024 inventory' },
  { esrs: 'ESRS E1', disclosure: 'Energy consumption mix', status: 'Implemented', evidence: 'Utility data' },
  { esrs: 'ESRS E1', disclosure: 'Transition plan', status: 'Not Started', evidence: 'Under development' },
  { esrs: 'ESRS S1', disclosure: 'Workforce diversity metrics', status: 'Implemented', evidence: 'HR data' },
  { esrs: 'ESRS S1', disclosure: 'Health & safety performance', status: 'Partial', evidence: 'Incident data' }
])

// Assurance Checklist
const assuranceChecklist = ref([
  { label: 'Governance and oversight processes', value: 'governance' },
  { label: 'Internal controls documentation', value: 'controls' },
  { label: 'Data collection and validation', value: 'data-quality' },
  { label: 'Materiality assessment process', value: 'materiality' },
  { label: 'Stakeholder engagement evidence', value: 'stakeholder' },
  { label: 'External auditor engagement', value: 'auditor' }
])

// Gap Analysis Data
const csrdGapData = ref([
  { area: 'Data Collection', gap: 'Scope 3 emissions data incomplete', status: 'High', remediation: 'Engage suppliers for data collection' },
  { area: 'Process', gap: 'Double materiality not fully documented', status: 'Medium', remediation: 'Complete materiality report' },
  { area: 'Systems', gap: 'ESG data management system needed', status: 'High', remediation: 'Implement ESG platform' },
  { area: 'People', gap: 'CSRD expertise gaps', status: 'Medium', remediation: 'Hire CSRD specialist' },
  { area: 'Reporting', gap: 'ESRS alignment for non-EU entities', status: 'Low', remediation: 'Review applicability' }
])

// Remediation Steps
const remediationSteps = ref([
  { date: 'Q4 2024', description: 'Complete double materiality assessment', type: 'primary' },
  { date: 'Q1 2025', description: 'Implement ESG data platform', type: 'primary' },
  { date: 'Q2 2025', description: 'Collect full Scope 3 data', type: 'warning' },
  { date: 'Q3 2025', description: 'Prepare pilot disclosure', type: 'warning' },
  { date: 'Q4 2025', description: 'Engage external assurance', type: 'success' }
])

// Methods
const goBack = () => {
  router.back()
}

const getStandardStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Implemented': 'success',
    'Partial': 'warning',
    'In Progress': 'info',
    'Not Started': 'info'
  }
  return map[status] || 'info'
}

const getDisclosureStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Implemented': 'success',
    'Partial': 'warning',
    'Not Started': 'info'
  }
  return map[status] || 'info'
}

const getGapStatusType = (status: string) => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[status] || 'info'
}

const generateReadinessReport = () => {
  ElMessage.success('CSRD readiness report generation started. You will receive a notification when ready.')
}

const exportMateriality = () => {
  ElMessage.success('Materiality matrix export started. File will be downloaded shortly.')
}

const scheduleAssurance = () => {
  ElMessage.info('Assurance preparation planning interface will open in a new window.')
}

// Chart initialization
const initComplianceRadarChart = () => {
  if (complianceRadarChartRef.value) {
    const chart = echarts.init(complianceRadarChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      radar: {
        indicator: [
          { name: 'Governance', max: 100 },
          { name: 'Strategy', max: 100 },
          { name: 'Risk Management', max: 100 },
          { name: 'Metrics & Targets', max: 100 },
          { name: 'Data Quality', max: 100 },
          { name: 'Stakeholder Engagement', max: 100 }
        ],
        shape: 'circle',
        center: ['50%', '50%'],
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: [
          { value: [85, 70, 75, 65, 60, 55], name: 'Current Readiness', areaStyle: { color: 'rgba(64, 158, 255, 0.3)' } },
          { value: [100, 100, 100, 100, 100, 100], name: 'Target', areaStyle: { color: 'rgba(103, 194, 58, 0.1)' } }
        ],
        lineStyle: { width: 2 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initReadinessChart = () => {
  if (readinessChartRef.value) {
    const chart = echarts.init(readinessChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Data Collection', 'Process', 'Systems', 'People'] },
      xAxis: { type: 'category', data: ['ESRS 1-2', 'ESRS E1', 'ESRS E2-5', 'ESRS S1', 'ESRS S2-4', 'ESRS G1'] },
      yAxis: { type: 'value', name: 'Readiness %', max: 100 },
      series: [
        { name: 'Data Collection', type: 'bar', data: [80, 65, 55, 70, 40, 60], itemStyle: { color: '#5470c6' } },
        { name: 'Process', type: 'bar', data: [75, 60, 50, 65, 35, 55], itemStyle: { color: '#fac858' } },
        { name: 'Systems', type: 'bar', data: [70, 55, 45, 60, 30, 50], itemStyle: { color: '#ee6666' } },
        { name: 'People', type: 'bar', data: [65, 50, 40, 55, 25, 45], itemStyle: { color: '#73c0de' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initMaterialityMatrixChart = () => {
  if (materialityMatrixChartRef.value) {
    const chart = echarts.init(materialityMatrixChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value', name: 'Financial Materiality (Outside-in)', min: 0, max: 10 },
      yAxis: { type: 'value', name: 'Impact Materiality (Inside-out)', min: 0, max: 10 },
      series: [{
        type: 'scatter',
        data: [
          [9.2, 8.5, 'Climate Change', 'High'],
          [8.5, 7.8, 'Energy', 'High'],
          [7.5, 6.5, 'Emissions', 'High'],
          [6.8, 8.2, 'Water', 'Medium'],
          [6.2, 5.5, 'Waste', 'Medium'],
          [5.5, 7.0, 'Biodiversity', 'Medium'],
          [4.8, 4.2, 'Diversity', 'Low'],
          [4.0, 5.5, 'Supply Chain', 'Low']
        ],
        symbolSize: 25,
        label: { show: true, formatter: (params: any) => params.data[2], position: 'right' },
        itemStyle: {
          color: (params: any) => {
            const priority = params.data[3]
            return priority === 'High' ? '#f56c6c' : priority === 'Medium' ? '#e6a23c' : '#909399'
          }
        }
      }]
    })
    chartInstances.push(chart)
  }
}

const initAssuranceChart = () => {
  if (assuranceChartRef.value) {
    const chart = echarts.init(assuranceChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Assurance Readiness',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 45, name: 'Prepared', itemStyle: { color: '#67c23a' } },
          { value: 35, name: 'In Progress', itemStyle: { color: '#e6a23c' } },
          { value: 20, name: 'Not Started', itemStyle: { color: '#f56c6c' } }
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
        name: 'Gap Severity',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 40, name: 'High Priority', itemStyle: { color: '#f56c6c' } },
          { value: 45, name: 'Medium Priority', itemStyle: { color: '#e6a23c' } },
          { value: 15, name: 'Low Priority', itemStyle: { color: '#67c23a' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
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
        initComplianceRadarChart()
        initReadinessChart()
        initMaterialityMatrixChart()
        initAssuranceChart()
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
.csrd-container {
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
  border: 1px solid rgba(144, 147, 153, 0.3);
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
  border-top-color: #909399;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #409eff;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #67c23a;
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
  background: linear-gradient(90deg, #909399, #409eff, #67c23a);
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
.csrd-container {
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

/* Timeline Section */
.timeline-section {
  margin-bottom: 24px;
}

.timeline-card {
  border-radius: 12px;
}

.timeline-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.timeline-header .el-icon {
  font-size: 22px;
  color: #409eff;
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
  color: #409eff;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* ESRS Tabs */
.esrs-tabs {
  margin-top: 0;
}

/* Materiality Summary */
.materiality-summary {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.impact-materiality,
.financial-materiality {
  background: #fafafa;
  border-radius: 12px;
  padding: 16px;
}

.impact-materiality h4,
.financial-materiality h4 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 15px;
}

.materiality-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.materiality-item:last-child {
  border-bottom: none;
}

/* Disclosure Summary */
.disclosure-summary {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.summary-stat {
  margin-bottom: 20px;
}

.stat-number {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.data-collection-status {
  margin-top: 20px;
  text-align: left;
}

.data-collection-status h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
}

.data-collection-status p {
  margin: 8px 0 0;
  font-size: 12px;
  color: #909399;
}

/* Assurance Checklist */
.assurance-checklist {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.assurance-checklist h4 {
  margin: 0 0 16px 0;
}

.assurance-checklist .el-checkbox {
  display: block;
  margin-bottom: 12px;
}

.audit-timeline {
  margin-top: 24px;
}

.audit-timeline h4 {
  margin: 0 0 16px 0;
}

/* Tables */
.disclosure-table,
.gap-table {
  border-radius: 8px;
  overflow: hidden;
}

/* Remediation Timeline */
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

:deep(.el-steps) {
  margin-top: 16px;
}

:deep(.el-step__title) {
  font-size: 13px;
}

:deep(.el-step__description) {
  font-size: 11px;
}

:deep(.el-collapse-item__header) {
  font-weight: 500;
}
</style>