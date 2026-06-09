<template>
  <div class="savings-verification-container">
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
            <span class="loading-title">Loading Savings Verification</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Energy Savings Measurement & Verification</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="savings-verification-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Savings Verification</h1>
          <p class="page-subtitle">Measure, verify and report energy savings from implemented projects</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="runVerification">
            <el-icon><Cpu /></el-icon>
            Run Verification
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="scheduleAudit">
            <el-icon><Calendar /></el-icon>
            Schedule Audit
          </el-button>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon blue">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Total Verified Savings</span>
                <span class="card-value">{{ formatNumber(totalVerifiedSavings) }} kWh</span>
                <el-progress :percentage="85" :stroke-width="6" color="#3b82f6" :show-text="false" />
                <span class="card-hint">{{ ((totalVerifiedSavings / totalExpectedSavings) * 100).toFixed(1) }}% of target</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon green">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Cost Savings</span>
                <span class="card-value">${{ formatNumber(totalCostSavings) }}</span>
                <el-progress :percentage="75" :stroke-width="6" color="#10b981" :show-text="false" />
                <span class="card-hint">YTD savings</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon orange">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Carbon Reduction</span>
                <span class="card-value">{{ totalCarbonReduction }} tCO₂e</span>
                <el-progress :percentage="80" :stroke-width="6" color="#f59e0b" :show-text="false" />
                <span class="card-hint">Verified emissions reduction</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="overview-card">
              <div class="card-icon purple">
                <el-icon><Document /></el-icon>
              </div>
              <div class="card-info">
                <span class="card-label">Active Projects</span>
                <span class="card-value">{{ activeProjects }}</span>
                <el-progress :percentage="100" :stroke-width="6" color="#8b5cf6" :show-text="false" />
                <span class="card-hint">Under verification</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Savings Trend Chart -->
      <div class="trend-section">
        <el-card class="trend-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Verified Savings Trend</span>
            </div>
            <el-radio-group v-model="trendPeriod" size="small">
              <el-radio-button label="monthly">Monthly</el-radio-button>
              <el-radio-button label="quarterly">Quarterly</el-radio-button>
              <el-radio-button label="yearly">Yearly</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <canvas id="savingsTrendChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- Projects List -->
      <div class="projects-section">
        <div class="section-header">
          <h3>Projects Under Verification</h3>
          <el-input v-model="searchQuery" placeholder="Search projects..." prefix-icon="Search" style="width: 250px" clearable />
        </div>
        <div class="projects-grid">
          <div v-for="project in filteredProjects" :key="project.id" class="project-card">
            <div class="project-header">
              <div class="project-title">
                <span class="project-name">{{ project.name }}</span>
                <el-tag :type="getStatusTagType(project.status)" size="small">{{ project.status }}</el-tag>
              </div>
              <div class="project-date">{{ project.startDate }} - {{ project.endDate }}</div>
            </div>
            <div class="project-metrics">
              <div class="metric">
                <span class="metric-label">Expected Savings</span>
                <span class="metric-value">{{ formatNumber(project.expectedSavings) }} kWh</span>
              </div>
              <div class="metric">
                <span class="metric-label">Verified Savings</span>
                <span class="metric-value" :style="{ color: project.verifiedSavings >= project.expectedSavings ? '#10b981' : '#f59e0b' }">
                  {{ formatNumber(project.verifiedSavings) }} kWh
                </span>
              </div>
              <div class="metric">
                <span class="metric-label">Verification Rate</span>
                <el-progress :percentage="(project.verifiedSavings / project.expectedSavings) * 100" :stroke-width="8" />
              </div>
              <div class="metric">
                <span class="metric-label">Methodology</span>
                <span class="metric-value">{{ project.methodology }}</span>
              </div>
            </div>
            <div class="project-actions">
              <el-button size="small" @click="viewProjectDetails(project)">View Details</el-button>
              <el-button size="small" type="primary" @click="updateVerification(project)">Update</el-button>
              <el-button size="small" @click="downloadReport(project)">Report</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Measurement & Verification Details -->
      <div class="mv-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="mv-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>Measurement Methodology</span>
                </div>
              </div>
              <div class="mv-content">
                <div class="methodology-item">
                  <div class="methodology-header">
                    <el-icon><Check /></el-icon>
                    <span>IPMVP Option A</span>
                  </div>
                  <p>Retrofit Isolation - Key Parameter Measurement</p>
                  <el-tag size="small">Lighting Projects</el-tag>
                </div>
                <div class="methodology-item">
                  <div class="methodology-header">
                    <el-icon><Check /></el-icon>
                    <span>IPMVP Option B</span>
                  </div>
                  <p>Retrofit Isolation - All Parameter Measurement</p>
                  <el-tag size="small">HVAC, Chiller Projects</el-tag>
                </div>
                <div class="methodology-item">
                  <div class="methodology-header">
                    <el-icon><Check /></el-icon>
                    <span>IPMVP Option C</span>
                  </div>
                  <p>Whole Facility - Utility Bill Analysis</p>
                  <el-tag size="small">Comprehensive Projects</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="mv-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Clock /></el-icon>
                  <span>Measurement Periods</span>
                </div>
              </div>
              <div class="mv-content">
                <div class="period-item">
                  <div class="period-header">
                    <span class="period-name">Baseline Period</span>
                    <el-tag type="info" size="small">Pre-Implementation</el-tag>
                  </div>
                  <p>January 1, 2023 - December 31, 2023 (12 months)</p>
                  <div class="period-data">Baseline Energy: 2,850,000 kWh</div>
                </div>
                <div class="period-item">
                  <div class="period-header">
                    <span class="period-name">Reporting Period</span>
                    <el-tag type="success" size="small">Current</el-tag>
                  </div>
                  <p>January 1, 2024 - Present ({{ reportingMonths }} months)</p>
                  <div class="period-data">Current Energy: {{ formatNumber(currentEnergy) }} kWh</div>
                </div>
                <div class="period-item">
                  <div class="period-header">
                    <span class="period-name">Adjustments Applied</span>
                  </div>
                  <ul class="adjustments-list">
                    <li>Weather normalization: <strong>-2.5%</strong></li>
                    <li>IT load adjustment: <strong>+1.8%</strong></li>
                    <li>Operating hours: <strong>0%</strong></li>
                  </ul>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Savings Breakdown by Category -->
      <div class="breakdown-section">
        <el-card class="breakdown-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><PieChart /></el-icon>
              <span>Savings Breakdown by Category</span>
            </div>
          </div>
          <div class="chart-container">
            <canvas id="savingsBreakdownChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- Verification Log -->
      <div class="log-section">
        <div class="section-header">
          <h3>Verification Log</h3>
          <el-button type="primary" link @click="viewAllLogs">View All →</el-button>
        </div>
        <el-table :data="verificationLogs" stripe class="log-table">
          <el-table-column prop="date" label="Date" width="120" />
          <el-table-column prop="project" label="Project" width="200" />
          <el-table-column prop="action" label="Action" />
          <el-table-column prop="savings" label="Verified Savings (kWh)" width="180">
            <template #default="{ row }">
              {{ formatNumber(row.savings) }}
            </template>
          </el-table-column>
          <el-table-column prop="verifier" label="Verifier" width="120" />
          <el-table-column label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Approved' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateFullReport">
          <el-icon><Document /></el-icon>
          Generate Full Verification Report
        </el-button>
        <el-button size="large" @click="scheduleVerification">
          <el-icon><Calendar /></el-icon>
          Schedule Next Verification
        </el-button>
        <el-button size="large" @click="comparePeriods">
          <el-icon><TrendCharts /></el-icon>
          Compare Periods
        </el-button>
      </div>
    </div>

    <!-- Project Details Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedProject?.name" width="700px">
      <div class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedProject?.status)">{{ selectedProject?.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Period">{{ selectedProject?.startDate }} - {{ selectedProject?.endDate }}</el-descriptions-item>
          <el-descriptions-item label="Expected Savings">{{ formatNumber(selectedProject?.expectedSavings) }} kWh</el-descriptions-item>
          <el-descriptions-item label="Verified Savings">{{ formatNumber(selectedProject?.verifiedSavings) }} kWh</el-descriptions-item>
          <el-descriptions-item label="Methodology">{{ selectedProject?.methodology }}</el-descriptions-item>
          <el-descriptions-item label="Verification Rate">{{ ((selectedProject?.verifiedSavings / selectedProject?.expectedSavings) * 100).toFixed(1) }}%</el-descriptions-item>
          <el-descriptions-item label="Measurement Points" :span="2">
            <ul class="measurement-points">
              <li>Power meters: 12 installed</li>
              <li>Temperature sensors: 24 installed</li>
              <li>Flow meters: 4 installed</li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item label="Adjustments Applied" :span="2">
            <ul>
              <li>Weather normalization: -2.5%</li>
              <li>IT load: +1.8%</li>
            </ul>
          </el-descriptions-item>
        </el-descriptions>
        <div class="detail-chart">
          <h4>Monthly Savings Trend</h4>
          <canvas id="projectSavingsChart" style="height: 200px"></canvas>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="updateVerification(selectedProject)">Update Verification</el-button>
      </template>
    </el-dialog>

    <!-- Update Verification Dialog -->
    <el-dialog v-model="updateDialogVisible" title="Update Verification Data" width="500px">
      <el-form>
        <el-form-item label="Verified Savings (kWh)">
          <el-input-number v-model="updateSavings" :min="0" :step="1000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Measurement Period">
          <el-date-picker v-model="updatePeriod" type="monthrange" range-separator="to" start-placeholder="Start" end-placeholder="End" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input type="textarea" :rows="3" placeholder="Add verification notes..." v-model="updateNotes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="updateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveVerificationUpdate">Submit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Cpu, Download, Calendar, TrendCharts, Coin, Document,
  DataAnalysis, Clock, PieChart, Search, Check
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading savings verification data...')

// ==================== Reactive Data ====================
const trendPeriod = ref('monthly')
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const updateDialogVisible = ref(false)
const selectedProject = ref<any>(null)
const updateSavings = ref(0)
const updatePeriod = ref<[Date, Date] | null>(null)
const updateNotes = ref('')

// Summary metrics
const totalExpectedSavings = ref(1850000)
const totalVerifiedSavings = ref(1572500)
const totalCostSavings = computed(() => totalVerifiedSavings.value * 0.12)
const totalCarbonReduction = computed(() => totalVerifiedSavings.value * 0.0004)
const activeProjects = ref(4)
const reportingMonths = ref(6)
const currentEnergy = ref(1250000)

// Projects data
const projects = ref([
  {
    id: 1, name: 'Chiller Efficiency Upgrade', status: 'Active', startDate: '2024-01-01', endDate: '2024-12-31',
    expectedSavings: 450000, verifiedSavings: 382500, methodology: 'IPMVP Option B', category: 'cooling',
    implementationDate: '2024-01-15', measurementPoints: 8
  },
  {
    id: 2, name: 'LED Lighting Retrofit', status: 'Completed', startDate: '2024-02-01', endDate: '2024-06-30',
    expectedSavings: 125000, verifiedSavings: 131250, methodology: 'IPMVP Option A', category: 'lighting',
    implementationDate: '2024-02-10', measurementPoints: 4
  },
  {
    id: 3, name: 'VFD Installation - CRAC Fans', status: 'Active', startDate: '2024-03-01', endDate: '2024-09-30',
    expectedSavings: 280000, verifiedSavings: 210000, methodology: 'IPMVP Option B', category: 'cooling',
    implementationDate: '2024-03-15', measurementPoints: 6
  },
  {
    id: 4, name: 'Hot Aisle Containment', status: 'Active', startDate: '2024-04-01', endDate: '2024-10-31',
    expectedSavings: 320000, verifiedSavings: 256000, methodology: 'IPMVP Option C', category: 'cooling',
    implementationDate: '2024-04-20', measurementPoints: 12
  },
  {
    id: 5, name: 'UPS Efficiency Optimization', status: 'Planned', startDate: '2024-05-01', endDate: '2024-11-30',
    expectedSavings: 180000, verifiedSavings: 0, methodology: 'IPMVP Option B', category: 'power',
    implementationDate: '2024-05-10', measurementPoints: 4
  },
  {
    id: 6, name: 'Free Cooling Implementation', status: 'Active', startDate: '2024-06-01', endDate: '2024-12-31',
    expectedSavings: 495000, verifiedSavings: 247500, methodology: 'IPMVP Option B', category: 'cooling',
    implementationDate: '2024-06-15', measurementPoints: 10
  }
])

// Verification logs
const verificationLogs = ref([
  { date: '2024-06-15', project: 'Chiller Efficiency Upgrade', action: 'Monthly Verification', savings: 42500, verifier: 'John Smith', status: 'Approved' },
  { date: '2024-06-10', project: 'LED Lighting Retrofit', action: 'Final Verification', savings: 131250, verifier: 'Sarah Johnson', status: 'Approved' },
  { date: '2024-06-05', project: 'VFD Installation - CRAC Fans', action: 'Quarterly Verification', savings: 52500, verifier: 'Mike Chen', status: 'Pending' },
  { date: '2024-05-20', project: 'Hot Aisle Containment', action: 'Initial Verification', savings: 64000, verifier: 'John Smith', status: 'Approved' }
])

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    'Active': 'warning',
    'Completed': 'success',
    'Planned': 'info'
  }
  return types[status] || 'info'
}

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  return projects.value.filter(p => p.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

// Chart instances
let savingsTrendChart: echarts.ECharts | null = null
let savingsBreakdownChart: echarts.ECharts | null = null
let projectSavingsChart: echarts.ECharts | null = null

// Chart initialization
const initSavingsTrendChart = () => {
  const canvas = document.getElementById('savingsTrendChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (savingsTrendChart) savingsTrendChart.dispose()
  savingsTrendChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  let monthlyData: number[] = []
  let quarterlyData: number[] = []
  let yearlyData: number[] = []

  if (trendPeriod.value === 'monthly') {
    monthlyData = [125000, 132000, 141000, 148000, 156000, 162000, 168000, 172000, 165000, 158000, 152000, 145000]
    savingsTrendChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} kWh' },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], name: 'Month' },
      yAxis: { type: 'value', name: 'Energy Savings (kWh)' },
      series: [{
        type: 'line', data: monthlyData, smooth: true,
        lineStyle: { color: '#3b82f6', width: 3 },
        areaStyle: { opacity: 0.3, color: '#3b82f6' },
        symbol: 'circle', symbolSize: 8,
        label: { show: true, position: 'top', formatter: (p: any) => formatNumber(p.value) }
      }]
    })
  } else if (trendPeriod.value === 'quarterly') {
    quarterlyData = [398000, 466000, 505000, 455000]
    savingsTrendChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} kWh' },
      xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'], name: 'Quarter' },
      yAxis: { type: 'value', name: 'Energy Savings (kWh)' },
      series: [{
        type: 'bar', data: quarterlyData,
        itemStyle: { borderRadius: [8, 8, 0, 0], color: '#10b981' },
        label: { show: true, position: 'top', formatter: (p: any) => formatNumber(p.value) }
      }]
    })
  } else {
    yearlyData = [1250000, 1572500, 1850000]
    savingsTrendChart.setOption({
      tooltip: { trigger: 'axis', formatter: '{b}: {c} kWh' },
      xAxis: { type: 'category', data: ['2022', '2023', '2024'], name: 'Year' },
      yAxis: { type: 'value', name: 'Energy Savings (kWh)' },
      series: [{
        type: 'line', data: yearlyData, smooth: true,
        lineStyle: { color: '#f59e0b', width: 3 },
        areaStyle: { opacity: 0.3, color: '#f59e0b' },
        symbol: 'circle', symbolSize: 8,
        label: { show: true, position: 'top', formatter: (p: any) => formatNumber(p.value) }
      }]
    })
  }
}

const initSavingsBreakdownChart = () => {
  const canvas = document.getElementById('savingsBreakdownChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (savingsBreakdownChart) savingsBreakdownChart.dispose()
  savingsBreakdownChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  savingsBreakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} kWh)' },
    legend: { top: 'bottom' },
    series: [{
      type: 'pie', radius: ['45%', '70%'],
      data: [
        { value: 896000, name: 'Cooling Optimization', itemStyle: { color: '#3b82f6' } },
        { value: 131250, name: 'Lighting Upgrade', itemStyle: { color: '#10b981' } },
        { value: 210000, name: 'VFD Installation', itemStyle: { color: '#f59e0b' } },
        { value: 247500, name: 'Free Cooling', itemStyle: { color: '#8b5cf6' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

const initProjectSavingsChart = () => {
  const canvas = document.getElementById('projectSavingsChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 200

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (projectSavingsChart) projectSavingsChart.dispose()
  projectSavingsChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
  const expected = [75, 75, 75, 75, 75, 75]
  const actual = [62, 68, 72, 78, 82, 85]

  projectSavingsChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Savings Rate (%)', max: 100 },
    series: [
      { name: 'Expected', type: 'line', data: expected, lineStyle: { color: '#909399', width: 2, type: 'dashed' }, symbol: 'diamond', symbolSize: 6 },
      { name: 'Actual', type: 'line', data: actual, lineStyle: { color: '#10b981', width: 2 }, areaStyle: { opacity: 0.2 }, symbol: 'circle', symbolSize: 6 }
    ]
  })
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initSavingsTrendChart()
    initSavingsBreakdownChart()
  }, 100)
}

// Actions
const runVerification = () => {
  ElMessage.success('Verification process started. Results will be available shortly.')
}

const exportReport = () => {
  ElMessage.success('Report export started')
}

const scheduleAudit = () => {
  ElMessage.info('Audit scheduling interface will open')
}

const viewProjectDetails = (project: any) => {
  selectedProject.value = project
  detailDialogVisible.value = true
  setTimeout(() => initProjectSavingsChart(), 100)
}

const updateVerification = (project: any) => {
  selectedProject.value = project
  updateSavings.value = project.verifiedSavings
  updateDialogVisible.value = true
}

const downloadReport = (project: any) => {
  ElMessage.success(`Downloading report for ${project.name}`)
}

const saveVerificationUpdate = () => {
  if (selectedProject.value) {
    selectedProject.value.verifiedSavings = updateSavings.value
    ElMessage.success('Verification data updated')
  }
  updateDialogVisible.value = false
}

const generateFullReport = () => {
  ElMessage.success('Full verification report generation started')
}

const scheduleVerification = () => {
  ElMessage.info('Verification scheduling interface will open')
}

const comparePeriods = () => {
  ElMessage.info('Period comparison tool will open')
}

const viewAllLogs = () => {
  ElMessage.info('Viewing all verification logs')
}

// Watch for period changes
watch(trendPeriod, () => {
  initSavingsTrendChart()
})

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (savingsTrendChart) savingsTrendChart.resize()
    if (savingsBreakdownChart) savingsBreakdownChart.resize()
    if (projectSavingsChart) projectSavingsChart.resize()
  }, 200)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          refreshAllCharts()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (savingsTrendChart) savingsTrendChart.dispose()
  if (savingsBreakdownChart) savingsBreakdownChart.dispose()
  if (projectSavingsChart) projectSavingsChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.savings-verification-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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

/* ==================== Main Content ==================== */
.savings-verification-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overview Cards */
.overview-section {
  margin-bottom: 24px;
}

.overview-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.card-icon.blue { background: #eff6ff; color: #3b82f6; }
.card-icon.green { background: #ecfdf5; color: #10b981; }
.card-icon.orange { background: #fffbeb; color: #f59e0b; }
.card-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.card-info {
  flex: 1;
}

.card-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.card-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.card-hint {
  display: block;
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Trend Section */
.trend-section {
  margin-bottom: 24px;
}

.trend-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-title .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.chart-container {
  width: 100%;
  min-height: 350px;
  position: relative;
}

/* Projects Section */
.projects-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 20px;
}

.project-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.project-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-name {
  font-weight: 600;
  color: #1e293b;
}

.project-date {
  font-size: 11px;
  color: #64748b;
}

.project-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.project-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* MV Section */
.mv-section {
  margin-bottom: 24px;
}

.mv-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.mv-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.methodology-item,
.period-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.methodology-header,
.period-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.methodology-header .el-icon {
  color: #10b981;
}

.period-name {
  font-weight: 600;
  color: #1e293b;
}

.methodology-item p,
.period-item p {
  font-size: 12px;
  color: #64748b;
  margin: 0 0 8px 0;
}

.period-data {
  font-size: 12px;
  font-weight: 500;
  color: #3b82f6;
  margin-top: 8px;
}

.adjustments-list {
  margin: 8px 0 0;
  padding-left: 20px;
}

.adjustments-list li {
  font-size: 12px;
  color: #64748b;
  margin: 4px 0;
}

/* Breakdown Section */
.breakdown-section {
  margin-bottom: 24px;
}

.breakdown-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Log Section */
.log-section {
  margin-bottom: 24px;
}

.log-table {
  border-radius: 16px;
  overflow: hidden;
}

/* Detail Content */
.detail-content {
  padding: 8px 0;
}

.measurement-points {
  margin: 0;
  padding-left: 20px;
}

.detail-chart {
  margin-top: 20px;
}

.detail-chart h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 12px 0;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 20px;
}

/* Responsive */
@media (max-width: 1200px) {
  .savings-verification-main { padding: 16px; }
  .projects-grid { grid-template-columns: 1fr; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .card-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .project-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .project-metrics { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>