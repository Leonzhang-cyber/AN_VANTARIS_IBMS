<template>
  <div class="gri-container">
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
            <span class="loading-title">Loading GRI Standards Framework</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Global Reporting Initiative</div>
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
            <span class="page-title">GRI Standards - Sustainability Reporting</span>
            <el-tag type="success" effect="dark" size="large">Universal Standards</el-tag>
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
                <span>Overall GRI Compliance</span>
              </div>
              <div class="card-value">76%</div>
              <div class="card-footer">
                <el-progress :percentage="76" :stroke-width="8" />
                <span class="status-text">In accordance with GRI</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Check /></el-icon>
                <span>Universal Standards</span>
              </div>
              <div class="card-value">88%</div>
              <div class="card-footer">
                <el-progress :percentage="88" :stroke-width="8" status="success" />
                <span>GRI 1-2-3</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Sector Standards</span>
              </div>
              <div class="card-value">65%</div>
              <div class="card-footer">
                <el-progress :percentage="65" :stroke-width="8" status="warning" />
                <span>Real Estate / Data Centers</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Topic Standards</span>
              </div>
              <div class="card-value">72%</div>
              <div class="card-footer">
                <el-progress :percentage="72" :stroke-width="8" status="warning" />
                <span>Economic | Environmental | Social</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- GRI Framework Navigation -->
      <div class="framework-navigation">
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="nav-card universal" :class="{ active: activeFramework === 'universal' }" @click="activeFramework = 'universal'">
              <el-icon><Star /></el-icon>
              <h3>Universal Standards</h3>
              <p>GRI 1, 2, 3 - Foundation, General Disclosures, Material Topics</p>
              <div class="progress-badge">
                <el-progress :percentage="88" :stroke-width="6" :show-text="false" />
                <span>88%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="nav-card sector" :class="{ active: activeFramework === 'sector' }" @click="activeFramework = 'sector'">
              <el-icon><OfficeBuilding /></el-icon>
              <h3>Sector Standards</h3>
              <p>Data Centers, Real Estate, Technology</p>
              <div class="progress-badge">
                <el-progress :percentage="65" :stroke-width="6" :show-text="false" />
                <span>65%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="nav-card topic" :class="{ active: activeFramework === 'topic' }" @click="activeFramework = 'topic'">
              <el-icon><Grid /></el-icon>
              <h3>Topic Standards</h3>
              <p>Economic, Environmental, Social series</p>
              <div class="progress-badge">
                <el-progress :percentage="72" :stroke-width="6" :show-text="false" />
                <span>72%</span>
              </div>
            </div>
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
                <span>GRI Compliance Overview</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="complianceRadarChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="complianceTrendChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Universal Standards Tab -->
          <el-tab-pane label="Universal Standards" name="universal">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Star /></el-icon>
                <span>GRI Universal Standards 2021</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="standards-table">
                    <el-table :data="universalStandardsData" border style="width: 100%">
                      <el-table-column prop="standard" label="Standard" width="120" />
                      <el-table-column prop="requirement" label="Requirement" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getUniversalStatusType(row.status)">
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
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="info-panel">
                    <div class="panel-title">
                      <el-icon><InfoFilled /></el-icon>
                      <span>GRI Universal Standards</span>
                    </div>
                    <el-collapse v-model="universalCollapse">
                      <el-collapse-item title="GRI 1: Foundation 2021" name="1">
                        <p>Sets out the purpose and key concepts of the GRI Standards</p>
                        <el-progress :percentage="95" :stroke-width="6" status="success" />
                      </el-collapse-item>
                      <el-collapse-item title="GRI 2: General Disclosures 2021" name="2">
                        <p>Organization, strategy, ethics, governance, stakeholder engagement</p>
                        <el-progress :percentage="85" :stroke-width="6" />
                      </el-collapse-item>
                      <el-collapse-item title="GRI 3: Material Topics 2021" name="3">
                        <p>Process to determine material topics and list of material topics</p>
                        <el-progress :percentage="82" :stroke-width="6" />
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Sector Standards Tab -->
          <el-tab-pane label="Sector Standards" name="sector">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Sector Standards for Data Centers & Real Estate</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="sector-table">
                    <el-table :data="sectorStandardsData" border style="width: 100%">
                      <el-table-column prop="sector" label="Sector" width="180" />
                      <el-table-column prop="topic" label="Topic" width="200" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getSectorStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="disclosure" label="Disclosure" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="chart-container">
                    <div ref="sectorChartRef" style="height: 280px"></div>
                  </div>
                  <div class="action-card">
                    <h4>Industry-specific Topics</h4>
                    <el-checkbox-group v-model="sectorTopics">
                      <el-checkbox v-for="topic in sectorTopicItems" :key="topic.value" :label="topic.value">
                        {{ topic.label }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Topic Standards Tab -->
          <el-tab-pane label="Topic Standards" name="topic">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>GRI Topic Standards</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="24">
                  <el-tabs v-model="topicSubTab" type="card" class="topic-tabs">
                    <!-- Economic Series -->
                    <el-tab-pane label="Economic Series" name="economic">
                      <el-table :data="economicTopics" border style="width: 100%">
                        <el-table-column prop="topic" label="Topic" width="200" />
                        <el-table-column prop="disclosure" label="Disclosure" width="250" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getTopicStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="year" label="Latest Data" width="120" />
                      </el-table>
                    </el-tab-pane>

                    <!-- Environmental Series -->
                    <el-tab-pane label="Environmental Series" name="environmental">
                      <el-table :data="environmentalTopics" border style="width: 100%">
                        <el-table-column prop="topic" label="Topic" width="200" />
                        <el-table-column prop="disclosure" label="Disclosure" width="250" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getTopicStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="trend" label="Trend" width="100">
                          <template #default="{ row }">
                            <el-tag :type="row.trend === 'Improving' ? 'success' : 'warning'" size="small">
                              {{ row.trend }}
                            </el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                    </el-tab-pane>

                    <!-- Social Series -->
                    <el-tab-pane label="Social Series" name="social">
                      <el-table :data="socialTopics" border style="width: 100%">
                        <el-table-column prop="topic" label="Topic" width="200" />
                        <el-table-column prop="disclosure" label="Disclosure" width="250" />
                        <el-table-column prop="status" label="Status" width="120">
                          <template #default="{ row }">
                            <el-tag :type="getTopicStatusType(row.status)">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="target" label="Target" width="150" />
                      </el-table>
                    </el-tab-pane>
                  </el-tabs>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Materiality Matrix Tab -->
          <el-tab-pane label="Materiality Matrix" name="materiality">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><PieChart /></el-icon>
                <span>Material Topics Assessment</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="materialityChartRef" style="height: 450px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="materiality-list">
                    <div class="list-header">
                      <span>Material Topics</span>
                      <span>Priority</span>
                    </div>
                    <div v-for="(topic, index) in materialTopics" :key="index" class="materiality-item">
                      <div class="topic-info">
                        <el-icon><Flag /></el-icon>
                        <span>{{ topic.name }}</span>
                      </div>
                      <el-tag :type="topic.priority === 'High' ? 'danger' : topic.priority === 'Medium' ? 'warning' : 'info'" size="small">
                        {{ topic.priority }}
                      </el-tag>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Disclosure Gap Tab -->
          <el-tab-pane label="Disclosure Gap" name="gap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                <span>GRI Disclosure Gap Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="gap-table">
                    <el-table :data="griGapData" border style="width: 100%">
                      <el-table-column prop="disclosure" label="Disclosure" width="220" />
                      <el-table-column prop="standard" label="Standard" width="120" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getGapStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="action" label="Action Required" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="gapChartRef" style="height: 280px"></div>
                  </div>
                  <div class="remediation-plan">
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
        <el-button type="primary" size="large" @click="generateGRIReport">
          <el-icon><Download /></el-icon>
          Generate GRI Content Index
        </el-button>
        <el-button size="large" @click="exportDisclosures">
          <el-icon><Share /></el-icon>
          Export Disclosures
        </el-button>
        <el-button size="large" @click="scheduleMaterialityUpdate">
          <el-icon><Clock /></el-icon>
          Update Materiality Assessment
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
const loadingMessage = ref('Loading GRI framework...')

const loadingMessages = [
  'Loading GRI Universal Standards...',
  'Analyzing Sector Standards...',
  'Mapping Topic Standards...',
  'Assessing material topics...',
  'Calculating disclosure gaps...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('dashboard')
const activeFramework = ref('universal')
const universalCollapse = ref(['1'])
const topicSubTab = ref('environmental')
const sectorTopics = ref(['energy', 'emissions', 'water'])

// Chart refs
const complianceRadarChartRef = ref<HTMLElement | null>(null)
const complianceTrendChartRef = ref<HTMLElement | null>(null)
const sectorChartRef = ref<HTMLElement | null>(null)
const materialityChartRef = ref<HTMLElement | null>(null)
const gapChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Universal Standards Data
const universalStandardsData = ref([
  { standard: 'GRI 1', requirement: 'Purpose and key concepts', status: 'Compliant', completion: 100 },
  { standard: 'GRI 1', requirement: 'Reporting principles', status: 'Compliant', completion: 95 },
  { standard: 'GRI 2', requirement: 'Organization profile', status: 'Compliant', completion: 100 },
  { standard: 'GRI 2', requirement: 'Strategy and ethics', status: 'Partial', completion: 80 },
  { standard: 'GRI 2', requirement: 'Governance structure', status: 'Compliant', completion: 90 },
  { standard: 'GRI 2', requirement: 'Stakeholder engagement', status: 'Partial', completion: 75 },
  { standard: 'GRI 3', requirement: 'Material topic determination', status: 'Partial', completion: 85 },
  { standard: 'GRI 3', requirement: 'List of material topics', status: 'Compliant', completion: 90 }
])

// Sector Standards Data
const sectorStandardsData = ref([
  { sector: 'Data Centers', topic: 'Energy management', status: 'Partial', disclosure: 'GRI 302: Energy 2024' },
  { sector: 'Data Centers', topic: 'Emissions tracking', status: 'Compliant', disclosure: 'GRI 305: Emissions 2024' },
  { sector: 'Real Estate', topic: 'Water efficiency', status: 'Partial', disclosure: 'GRI 303: Water 2024' },
  { sector: 'Real Estate', topic: 'Waste management', status: 'In Progress', disclosure: 'GRI 306: Waste 2024' },
  { sector: 'Technology', topic: 'Cybersecurity', status: 'Partial', disclosure: 'GRI 418: Privacy 2024' }
])

const sectorTopicItems = ref([
  { label: 'Energy efficiency (GRI 302)', value: 'energy' },
  { label: 'GHG emissions (GRI 305)', value: 'emissions' },
  { label: 'Water consumption (GRI 303)', value: 'water' },
  { label: 'Waste reduction (GRI 306)', value: 'waste' },
  { label: 'Biodiversity impact (GRI 304)', value: 'biodiversity' }
])

// Economic Topics
const economicTopics = ref([
  { topic: 'Economic Performance', disclosure: 'Direct economic value generated', status: 'Compliant', year: '2024' },
  { topic: 'Market Presence', disclosure: 'Local hiring practices', status: 'Partial', year: '2023' },
  { topic: 'Indirect Economic Impacts', disclosure: 'Infrastructure investments', status: 'In Progress', year: 'N/A' },
  { topic: 'Procurement Practices', disclosure: 'Local supplier spending', status: 'Compliant', year: '2024' },
  { topic: 'Anti-corruption', disclosure: 'Anti-corruption policies', status: 'Compliant', year: '2024' }
])

// Environmental Topics
const environmentalTopics = ref([
  { topic: 'Materials', disclosure: 'Materials used by weight/volume', status: 'Compliant', trend: 'Improving' },
  { topic: 'Energy', disclosure: 'Energy consumption mix', status: 'Partial', trend: 'Stable' },
  { topic: 'Water', disclosure: 'Water withdrawal and discharge', status: 'Partial', trend: 'Improving' },
  { topic: 'Biodiversity', disclosure: 'Operational sites near protected areas', status: 'Compliant', trend: 'Stable' },
  { topic: 'Emissions', disclosure: 'Scope 1, 2, 3 GHG emissions', status: 'Compliant', trend: 'Improving' },
  { topic: 'Waste', disclosure: 'Waste generation and disposal', status: 'Partial', trend: 'Improving' },
  { topic: 'Environmental Compliance', disclosure: 'Non-compliance with regulations', status: 'Compliant', trend: 'Stable' }
])

// Social Topics
const socialTopics = ref([
  { topic: 'Employment', disclosure: 'Employee turnover rates', status: 'Compliant', target: '<15%' },
  { topic: 'Occupational Health & Safety', disclosure: 'Injury rates and fatalities', status: 'Compliant', target: 'Zero incidents' },
  { topic: 'Training & Education', disclosure: 'Training hours per employee', status: 'Partial', target: '40 hrs/employee' },
  { topic: 'Diversity & Equal Opportunity', disclosure: 'Diversity metrics', status: 'Compliant', target: '30% diverse leadership' },
  { topic: 'Non-discrimination', disclosure: 'Discrimination incidents', status: 'Compliant', target: 'Zero incidents' },
  { topic: 'Local Communities', disclosure: 'Community impact assessment', status: 'Partial', target: 'Q2 2025' }
])

// Material Topics
const materialTopics = ref([
  { name: 'Climate change & GHG emissions', priority: 'High' },
  { name: 'Energy efficiency', priority: 'High' },
  { name: 'Water stewardship', priority: 'High' },
  { name: 'Employee health & safety', priority: 'High' },
  { name: 'Data privacy & cybersecurity', priority: 'Medium' },
  { name: 'Circular economy & waste', priority: 'Medium' },
  { name: 'Diversity & inclusion', priority: 'Medium' },
  { name: 'Sustainable supply chain', priority: 'Low' }
])

// Gap Analysis Data
const griGapData = ref([
  { disclosure: 'GRI 2-22: Statement on sustainable development', standard: 'GRI 2', status: 'Missing', action: 'Draft sustainability statement' },
  { disclosure: 'GRI 2-29: Stakeholder engagement approach', standard: 'GRI 2', status: 'Partial', action: 'Document engagement process' },
  { disclosure: 'GRI 3-2: Process for material topic determination', standard: 'GRI 3', status: 'Partial', action: 'Detail methodology' },
  { disclosure: 'GRI 305-4: GHG emissions intensity', standard: 'GRI 305', status: 'Missing', action: 'Calculate intensity metrics' },
  { disclosure: 'GRI 306-4: Waste diverted from disposal', standard: 'GRI 306', status: 'Partial', action: 'Improve waste tracking' }
])

// Remediation Steps
const remediationSteps = ref([
  { date: 'Q4 2024', description: 'Complete GHG intensity calculation', type: 'primary' },
  { date: 'Q1 2025', description: 'Document stakeholder engagement process', type: 'primary' },
  { date: 'Q2 2025', description: 'Draft sustainability statement', type: 'warning' },
  { date: 'Q3 2025', description: 'Complete full GRI content index', type: 'success' }
])

// Methods
const goBack = () => {
  router.back()
}

const getUniversalStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'Missing': 'danger',
    'In Progress': 'info'
  }
  return map[status] || 'info'
}

const getSectorStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'In Progress': 'info'
  }
  return map[status] || 'info'
}

const getTopicStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'In Progress': 'info'
  }
  return map[status] || 'info'
}

const getGapStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Compliant': 'success',
    'Partial': 'warning',
    'Missing': 'danger'
  }
  return map[status] || 'info'
}

const generateGRIReport = () => {
  ElMessage.success('GRI Content Index generation started. You will receive a notification when ready.')
}

const exportDisclosures = () => {
  ElMessage.success('Disclosures export started. File will be downloaded shortly.')
}

const scheduleMaterialityUpdate = () => {
  ElMessage.info('Materiality assessment update scheduling will open in a new window.')
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
          { name: 'Stakeholder Engagement', max: 100 },
          { name: 'Materiality', max: 100 }
        ],
        shape: 'circle',
        center: ['50%', '50%'],
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: [
          { value: [85, 75, 80, 70, 78, 82], name: 'Current Compliance', areaStyle: { color: 'rgba(64, 158, 255, 0.3)' } }
        ],
        lineStyle: { color: '#409eff', width: 2 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initComplianceTrendChart = () => {
  if (complianceTrendChartRef.value) {
    const chart = echarts.init(complianceTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Universal', 'Sector', 'Topic'] },
      xAxis: { type: 'category', data: ['2022', '2023', '2024', '2025', '2026'] },
      yAxis: { type: 'value', name: 'Compliance %', max: 100 },
      series: [
        { name: 'Universal', type: 'line', data: [65, 75, 85, 90, 95], smooth: true, lineStyle: { color: '#5470c6', width: 2 } },
        { name: 'Sector', type: 'line', data: [40, 55, 65, 75, 85], smooth: true, lineStyle: { color: '#fac858', width: 2 } },
        { name: 'Topic', type: 'line', data: [50, 60, 72, 80, 88], smooth: true, lineStyle: { color: '#ee6666', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initSectorChart = () => {
  if (sectorChartRef.value) {
    const chart = echarts.init(sectorChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Sector Compliance',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 75, name: 'Data Centers', itemStyle: { color: '#5470c6' } },
          { value: 60, name: 'Real Estate', itemStyle: { color: '#fac858' } },
          { value: 70, name: 'Technology', itemStyle: { color: '#ee6666' } }
        ]
      }]
    })
    chartInstances.push(chart)
  }
}

const initMaterialityChart = () => {
  if (materialityChartRef.value) {
    const chart = echarts.init(materialityChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'value', name: 'Impact on Economy, Environment, Society' },
      yAxis: { type: 'value', name: 'Influence on Stakeholder Decisions' },
      series: [{
        type: 'scatter',
        data: [
          [85, 90, 'Climate change', 'High'],
          [80, 75, 'Energy', 'High'],
          [75, 80, 'Water', 'High'],
          [70, 65, 'Emissions', 'High'],
          [65, 70, 'Waste', 'Medium'],
          [60, 55, 'Biodiversity', 'Medium'],
          [50, 60, 'Diversity', 'Medium'],
          [45, 40, 'Supply chain', 'Low']
        ],
        symbolSize: 20,
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

const initGapChart = () => {
  if (gapChartRef.value) {
    const chart = echarts.init(gapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Disclosure Status',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 65, name: 'Compliant', itemStyle: { color: '#67c23a' } },
          { value: 25, name: 'Partial', itemStyle: { color: '#e6a23c' } },
          { value: 10, name: 'Missing', itemStyle: { color: '#f56c6c' } }
        ]
      }]
    })
    chartInstances.push(chart)
  }
}

// Watch for framework changes
watch(activeFramework, (newVal) => {
  if (newVal === 'universal') activeTab.value = 'universal'
  else if (newVal === 'sector') activeTab.value = 'sector'
  else if (newVal === 'topic') activeTab.value = 'topic'
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
        initComplianceRadarChart()
        initComplianceTrendChart()
        initSectorChart()
        initMaterialityChart()
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
.gri-container {
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
  border-top-color: #10b981;
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
  border-bottom-color: #3b82f6;
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
  background: linear-gradient(90deg, #10b981, #3b82f6, #8b5cf6);
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
.gri-container {
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

/* Framework Navigation */
.framework-navigation {
  margin-bottom: 24px;
}

.nav-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.nav-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.nav-card.universal.active { border-color: #10b981; background: #ecfdf5; }
.nav-card.sector.active { border-color: #f59e0b; background: #fffbeb; }
.nav-card.topic.active { border-color: #8b5cf6; background: #f5f3ff; }

.nav-card .el-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

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

.progress-badge {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.progress-badge .el-progress {
  flex: 1;
}

.main-content-card {
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

.standards-table,
.sector-table,
.gap-table {
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

.topic-tabs {
  margin-top: 0;
}

.materiality-list {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 450px;
  overflow-y: auto;
}

.list-header {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 2px solid #e4e7ed;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.materiality-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.materiality-item:hover {
  background: #f5f7fa;
}

.topic-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.remediation-plan {
  margin-top: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.remediation-plan h4 {
  margin: 0 0 12px 0;
  color: #303133;
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