<template>
  <div class="ifrs-s2-container">
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
            <span class="loading-title">Loading IFRS S2 Compliance Center</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Climate-related Financial Disclosures</div>
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
            <span class="page-title">IFRS S2 - Climate-related Disclosures</span>
            <el-tag type="danger" effect="dark" size="large">Compliance Center</el-tag>
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
                <span>Disclosure Status</span>
              </div>
              <div class="card-value">85%</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" />
                <span class="status-text">In Progress</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Check /></el-icon>
                <span>Compliance Rating</span>
              </div>
              <div class="card-value">B+</div>
              <div class="card-footer">
                <el-rate v-model="rating" disabled show-score text-color="#ff9900" score-template="{value}pts" />
                <span>Industry Avg: B</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Calendar /></el-icon>
                <span>Reporting Deadline</span>
              </div>
              <div class="card-value">45 Days</div>
              <div class="card-footer">
                <el-progress :percentage="75" :stroke-width="8" status="warning" />
                <span>2024-12-31</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Data Completeness</span>
              </div>
              <div class="card-value">92%</div>
              <div class="card-footer">
                <el-progress :percentage="92" :stroke-width="8" status="success" />
                <span>Good</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Governance Tab -->
          <el-tab-pane label="Governance" name="governance">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Climate Governance Structure</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="governanceChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-panel">
                    <el-descriptions :column="1" border>
                      <el-descriptions-item label="Board Oversight">
                        <el-tag type="success">Established</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="Climate Committee">
                        <el-tag type="success">Active</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="Risk Management Integration">
                        <el-tag type="success">Integrated</el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="Reporting Frequency">
                        Quarterly
                      </el-descriptions-item>
                      <el-descriptions-item label="Last Review">
                        September 15, 2024
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Strategy Tab -->
          <el-tab-pane label="Strategy" name="strategy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Climate Scenarios & Risk Assessment</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="scenarioChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="risk-matrix">
                    <h4>Physical Risks</h4>
                    <el-progress :percentage="65" :format="() => 'High'" status="exception" />
                    <el-progress :percentage="40" :format="() => 'Medium'" />
                    <el-progress :percentage="20" :format="() => 'Low'" />
                    <h4 style="margin-top: 20px">Transition Risks</h4>
                    <el-progress :percentage="70" :format="() => 'High'" status="exception" />
                    <el-progress :percentage="50" :format="() => 'Medium'" />
                    <el-progress :percentage="15" :format="() => 'Low'" />
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Risk Management Tab -->
          <el-tab-pane label="Risk Management" name="riskManagement">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Risk Identification & Mitigation</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <div class="risk-table">
                    <el-table :data="riskData" border style="width: 100%">
                      <el-table-column prop="riskType" label="Risk Type" width="180" />
                      <el-table-column prop="likelihood" label="Likelihood" />
                      <el-table-column prop="impact" label="Impact" />
                      <el-table-column prop="mitigation" label="Mitigation Strategy" />
                      <el-table-column prop="status" label="Status">
                        <template #default="{ row }">
                          <el-tag :type="row.status === 'Active' ? 'danger' : 'success'">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="chart-container">
                    <div ref="riskChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Metrics & Targets Tab -->
          <el-tab-pane label="Metrics & Targets" name="metrics">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Climate Metrics & Performance Targets</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="emissionsChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="targets-panel">
                    <el-collapse v-model="activeCollapse">
                      <el-collapse-item title="Scope 1 Emissions" name="1">
                        <div>Target: -25% by 2030 (baseline 2020)</div>
                        <el-progress :percentage="35" :format="() => '8% reduction achieved'" />
                      </el-collapse-item>
                      <el-collapse-item title="Scope 2 Emissions" name="2">
                        <div>Target: 100% renewable electricity by 2025</div>
                        <el-progress :percentage="68" :format="() => '68% achieved'" status="success" />
                      </el-collapse-item>
                      <el-collapse-item title="Scope 3 Emissions" name="3">
                        <div>Target: -15% by 2030 (baseline 2020)</div>
                        <el-progress :percentage="20" :format="() => '3% reduction achieved'" />
                      </el-collapse-item>
                      <el-collapse-item title="Net Zero Commitment" name="4">
                        <div>Target: Net Zero by 2050</div>
                        <el-progress :percentage="15" :format="() => 'On track'" status="warning" />
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Gap Analysis Tab -->
          <el-tab-pane label="Gap Analysis" name="gapAnalysis">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><List /></el-icon>
                <span>IFRS S2 Disclosure Gap Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="gap-table">
                    <el-table :data="gapData" border style="width: 100%">
                      <el-table-column prop="disclosure" label="Disclosure Requirement" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getStatusType(row.status)">
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
                    <div ref="gapChartRef" style="height: 300px"></div>
                  </div>
                  <div class="compliance-checklist">
                    <div class="checklist-header">
                      <el-icon><Check /></el-icon>
                      <span>Compliance Checklist</span>
                    </div>
                    <el-checkbox-group v-model="checkedItems">
                      <el-checkbox v-for="item in checklistItems" :key="item.value" :label="item.value">
                        {{ item.label }}
                      </el-checkbox>
                    </el-checkbox-group>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateReport">
          <el-icon><Download /></el-icon>
          Generate Compliance Report
        </el-button>
        <el-button size="large" @click="exportData">
          <el-icon><Share /></el-icon>
          Export Data
        </el-button>
        <el-button size="large" @click="scheduleAudit">
          <el-icon><Clock /></el-icon>
          Schedule Audit
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
const loadingMessage = ref('Initializing climate data...')

const loadingMessages = [
  'Preparing compliance framework...',
  'Loading governance structures...',
  'Analyzing climate scenarios...',
  'Calculating emission metrics...',
  'Validating disclosure requirements...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('governance')
const activeCollapse = ref(['1'])
const rating = ref(3.5)
const checkedItems = ref(['governance', 'risk', 'emissions'])

// Chart refs
const governanceChartRef = ref<HTMLElement | null>(null)
const scenarioChartRef = ref<HTMLElement | null>(null)
const riskChartRef = ref<HTMLElement | null>(null)
const emissionsChartRef = ref<HTMLElement | null>(null)
const gapChartRef = ref<HTMLElement | null>(null)

// Chart instances for cleanup
let chartInstances: echarts.ECharts[] = []

// Table data
const riskData = ref([
  {
    riskType: 'Physical - Extreme Weather',
    likelihood: 'High',
    impact: 'High',
    mitigation: 'Business continuity planning, insurance coverage',
    status: 'Active'
  },
  {
    riskType: 'Transition - Carbon Pricing',
    likelihood: 'Medium',
    impact: 'High',
    mitigation: 'Carbon offset program, efficiency improvements',
    status: 'Active'
  },
  {
    riskType: 'Physical - Sea Level Rise',
    likelihood: 'Low',
    impact: 'Medium',
    mitigation: 'Site assessment, adaptation planning',
    status: 'Monitoring'
  },
  {
    riskType: 'Transition - Regulatory Change',
    likelihood: 'Medium',
    impact: 'Medium',
    mitigation: 'Regulatory tracking, policy advocacy',
    status: 'Active'
  },
  {
    riskType: 'Reputational Risk',
    likelihood: 'High',
    impact: 'Medium',
    mitigation: 'Stakeholder engagement, transparent reporting',
    status: 'Active'
  }
])

const gapData = ref([
  {
    disclosure: 'Governance disclosure of climate-related risks',
    status: 'Compliant',
    action: 'None - Maintain current documentation'
  },
  {
    disclosure: 'Climate scenario analysis for all material risks',
    status: 'Partial',
    action: 'Complete scenario analysis for transition risks'
  },
  {
    disclosure: 'Scope 3 emissions inventory',
    status: 'Partial',
    action: 'Expand supplier data collection'
  },
  {
    disclosure: 'Climate resilience assessment',
    status: 'Non-compliant',
    action: 'Conduct full resilience assessment'
  },
  {
    disclosure: 'Internal carbon price disclosure',
    status: 'Compliant',
    action: 'None - Maintain current documentation'
  },
  {
    disclosure: 'Targets aligned with net-zero pathways',
    status: 'Partial',
    action: 'Validate targets with SBTi'
  }
])

const checklistItems = ref([
  { label: 'Board-level climate oversight', value: 'governance' },
  { label: 'Climate risk assessment completed', value: 'risk' },
  { label: 'Scenario analysis performed', value: 'scenario' },
  { label: 'Emissions inventory verified', value: 'emissions' },
  { label: 'Targets approved by SBTi', value: 'targets' },
  { label: 'Transition plan documented', value: 'plan' }
])

// Methods
const goBack = () => {
  router.back()
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'Compliant':
      return 'success'
    case 'Partial':
      return 'warning'
    case 'Non-compliant':
      return 'danger'
    default:
      return 'info'
  }
}

const generateReport = () => {
  ElMessage.success('Compliance report generation started. You will receive a notification when ready.')
}

const exportData = () => {
  ElMessage.success('Data export started. File will be downloaded shortly.')
}

const scheduleAudit = () => {
  ElMessage.info('Audit scheduling interface will open in a new window.')
}

// Chart initialization
const initGovernanceChart = () => {
  if (governanceChartRef.value) {
    const chart = echarts.init(governanceChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: '5%', left: 'center' },
      series: [{
        name: 'Governance Structure',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: { show: true, formatter: '{b}: {d}%' },
        emphasis: { scale: true },
        data: [
          { value: 45, name: 'Board of Directors', itemStyle: { color: '#5470c6' } },
          { value: 25, name: 'Climate Committee', itemStyle: { color: '#fac858' } },
          { value: 20, name: 'Executive Management', itemStyle: { color: '#ee6666' } },
          { value: 10, name: 'External Advisory', itemStyle: { color: '#73c0de' } }
        ]
      }]
    })
    chartInstances.push(chart)
  }
}

const initScenarioChart = () => {
  if (scenarioChartRef.value) {
    const chart = echarts.init(scenarioChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Physical Risk', 'Transition Risk'] },
      xAxis: { type: 'category', data: ['2030', '2040', '2050'] },
      yAxis: { type: 'value', name: 'Risk Exposure' },
      series: [
        {
          name: 'Physical Risk',
          type: 'line',
          data: [45, 65, 85],
          smooth: true,
          lineStyle: { color: '#ee6666', width: 3 },
          areaStyle: { opacity: 0.3 }
        },
        {
          name: 'Transition Risk',
          type: 'line',
          data: [55, 75, 70],
          smooth: true,
          lineStyle: { color: '#5470c6', width: 3 },
          areaStyle: { opacity: 0.3 }
        }
      ]
    })
    chartInstances.push(chart)
  }
}

const initRiskChart = () => {
  if (riskChartRef.value) {
    const chart = echarts.init(riskChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Risk Distribution',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 35, name: 'Physical Risks', itemStyle: { color: '#ee6666' } },
          { value: 40, name: 'Transition Risks', itemStyle: { color: '#fac858' } },
          { value: 15, name: 'Regulatory Risks', itemStyle: { color: '#5470c6' } },
          { value: 10, name: 'Reputational Risks', itemStyle: { color: '#73c0de' } }
        ],
        emphasis: { scale: true }
      }]
    })
    chartInstances.push(chart)
  }
}

const initEmissionsChart = () => {
  if (emissionsChartRef.value) {
    const chart = echarts.init(emissionsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'] },
      xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
      yAxis: { type: 'value', name: 'tCO₂e (thousands)' },
      series: [
        {
          name: 'Scope 1',
          type: 'bar',
          data: [125, 118, 112, 108, 115],
          itemStyle: { color: '#5470c6' }
        },
        {
          name: 'Scope 2',
          type: 'bar',
          data: [85, 78, 68, 55, 48],
          itemStyle: { color: '#91cc75' }
        },
        {
          name: 'Scope 3',
          type: 'bar',
          data: [450, 445, 438, 430, 420],
          itemStyle: { color: '#fac858' }
        }
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
        name: 'Compliance Status',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 45, name: 'Compliant', itemStyle: { color: '#67c23a' } },
          { value: 35, name: 'Partial', itemStyle: { color: '#e6a23c' } },
          { value: 20, name: 'Non-compliant', itemStyle: { color: '#f56c6c' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' },
        emphasis: { scale: true }
      }]
    })
    chartInstances.push(chart)
  }
}

// Handle window resize
const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

// Loading simulation
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
      // Initialize charts after content is loaded
      setTimeout(() => {
        initGovernanceChart()
        initScenarioChart()
        initRiskChart()
        initEmissionsChart()
        initGapChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

// Cleanup
onUnmounted(() => {
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.ifrs-s2-container {
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
.ifrs-s2-container {
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

.info-panel, .targets-panel {
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.risk-matrix {
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.risk-matrix h4 {
  margin-bottom: 12px;
  color: #606266;
}

.risk-matrix .el-progress {
  margin-bottom: 16px;
}

.risk-table {
  border-radius: 8px;
  overflow: hidden;
}

.gap-table {
  border-radius: 8px;
  overflow: hidden;
}

.compliance-checklist {
  margin-top: 20px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.checklist-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

.compliance-checklist .el-checkbox {
  display: block;
  margin-bottom: 12px;
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

:deep(.el-descriptions__label) {
  font-weight: 600;
}

:deep(.el-progress__text) {
  font-size: 12px;
}

:deep(.el-rate) {
  display: inline-block;
}
</style>