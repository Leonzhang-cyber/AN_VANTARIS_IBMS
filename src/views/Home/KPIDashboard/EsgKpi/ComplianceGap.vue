<template>
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Compliance Gap Page Content -->
  <div v-else class="compliance-gap-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>Compliance Gap</h1>
        <p class="subtitle">Identify and track gaps against regulatory and ESG compliance requirements</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
        <el-button :icon="Plus" @click="addAssessment">New Assessment</el-button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-cards">
      <div class="kpi-card overall">
        <div class="kpi-icon">
          <el-icon :size="32"><DocumentChecked /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ overallCompliance }}%</div>
          <div class="kpi-label">Overall Compliance</div>
        </div>
        <div class="kpi-trend" :class="complianceTrend >= 0 ? 'positive' : 'negative'">
          <el-icon><CaretTop v-if="complianceTrend >= 0" /><CaretBottom v-else /></el-icon>
          {{ Math.abs(complianceTrend) }}%
        </div>
      </div>
      <div class="kpi-card met">
        <div class="kpi-icon">
          <el-icon :size="32"><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ metRequirements }}</div>
          <div class="kpi-label">Requirements Met</div>
        </div>
        <div class="kpi-sub">of {{ totalRequirements }} total</div>
      </div>
      <div class="kpi-card gap">
        <div class="kpi-icon">
          <el-icon :size="32"><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ openGaps }}</div>
          <div class="kpi-label">Open Gaps</div>
        </div>
        <div class="kpi-sub">Critical: {{ criticalGaps }}</div>
      </div>
      <div class="kpi-card in-progress">
        <div class="kpi-icon">
          <el-icon :size="32"><Loading /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ inProgressGaps }}</div>
          <div class="kpi-label">In Progress</div>
        </div>
        <div class="kpi-sub">Remediation Active</div>
      </div>
    </div>

    <!-- Compliance by Category Chart -->
    <div class="two-columns">
      <div class="chart-card">
        <div class="card-header">
          <h3>Compliance by Framework</h3>
        </div>
        <div class="chart-container" ref="frameworkChartRef"></div>
      </div>
      <div class="chart-card">
        <div class="card-header">
          <h3>Gap Severity Distribution</h3>
        </div>
        <div class="chart-container" ref="severityChartRef"></div>
      </div>
    </div>

    <!-- Compliance Gap Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>Compliance Gap Analysis</h3>
        <div class="header-filters">
          <el-select v-model="frameworkFilter" placeholder="All Frameworks" clearable size="default" style="width: 160px">
            <el-option label="All Frameworks" value="all" />
            <el-option label="CSRD" value="CSRD" />
            <el-option label="GRI" value="GRI" />
            <el-option label="TCFD" value="TCFD" />
            <el-option label="ISSB" value="ISSB" />
            <el-option label="SFDR" value="SFDR" />
          </el-select>
          <el-select v-model="severityFilter" placeholder="All Severities" clearable size="default" style="width: 140px">
            <el-option label="All Severities" value="all" />
            <el-option label="Critical" value="critical" />
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
          <el-select v-model="statusFilter" placeholder="All Status" clearable size="default" style="width: 140px">
            <el-option label="All Status" value="all" />
            <el-option label="Open" value="open" />
            <el-option label="In Progress" value="in-progress" />
            <el-option label="Closed" value="closed" />
          </el-select>
          <el-input
              v-model="searchText"
              placeholder="Search..."
              :prefix-icon="Search"
              style="width: 200px"
              clearable
          />
        </div>
      </div>
      <el-table :data="paginatedGaps" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="framework" label="Framework" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.framework }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requirement" label="Requirement" min-width="200" show-overflow-tooltip />
        <el-table-column prop="currentStatus" label="Current Status" width="130">
          <template #default="{ row }">
            <span>{{ row.currentStatus }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="requiredStatus" label="Required Status" width="130">
          <template #default="{ row }">
            <span>{{ row.requiredStatus }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="gap" label="Gap Description" min-width="180" show-overflow-tooltip />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dueDate" label="Due Date" width="110" sortable>
          <template #default="{ row }">
            <span :class="{ 'text-danger': isOverdue(row.dueDate) && row.status !== 'closed' }">
              {{ row.dueDate }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewGap(row)">View</el-button>
            <el-button link type="success" size="small" @click="updateProgress(row)">Update</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredGaps.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Remediation Plan -->
    <div class="remediation-section">
      <div class="section-header">
        <h2>
          <el-icon><EditPen /></el-icon>
          Remediation Action Plan
        </h2>
        <el-button type="primary" :icon="Plus" size="small" @click="addRemediationTask">Add Task</el-button>
      </div>
      <div class="remediation-list">
        <div v-for="task in remediationTasks" :key="task.id" class="remediation-item">
          <div class="task-status" :class="task.priority">
            <el-icon v-if="task.status === 'completed'"><CircleCheckFilled /></el-icon>
            <el-icon v-else-if="task.status === 'in-progress'"><Loading /></el-icon>
            <el-icon v-else><Clock /></el-icon>
          </div>
          <div class="task-content">
            <div class="task-title">{{ task.title }}</div>
            <div class="task-description">{{ task.description }}</div>
            <div class="task-meta">
              <span><el-icon><Flag /></el-icon> Framework: {{ task.framework }}</span>
              <span><el-icon><User /></el-icon> Owner: {{ task.owner }}</span>
              <span><el-icon><Timer /></el-icon> Due: {{ task.dueDate }}</span>
            </div>
          </div>
          <div class="task-progress">
            <el-progress type="circle" :percentage="task.progress" :width="50" :stroke-width="6" :color="getProgressColor(task.progress)" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Refresh,
  Download,
  Plus,
  DocumentChecked,
  CircleCheckFilled,
  WarningFilled,
  Loading,
  Search,
  EditPen,
  Clock,
  Flag,
  User,
  Timer,
  CaretTop,
  CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data Structures ====================
interface ComplianceGap {
  id: number
  framework: string
  requirement: string
  currentStatus: string
  requiredStatus: string
  gap: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  status: 'open' | 'in-progress' | 'closed'
  dueDate: string
}

interface RemediationTask {
  id: number
  title: string
  description: string
  framework: string
  owner: string
  dueDate: string
  status: string
  priority: string
  progress: number
}

// ==================== State ====================
const frameworkFilter = ref('all')
const severityFilter = ref('all')
const statusFilter = ref('all')
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart refs
const frameworkChartRef = ref<HTMLElement | null>(null)
const severityChartRef = ref<HTMLElement | null>(null)
let frameworkChart: echarts.ECharts | null = null
let severityChart: echarts.ECharts | null = null

// ==================== Mock Data ====================
const complianceGaps = ref<ComplianceGap[]>([
  { id: 1, framework: 'CSRD', requirement: 'ESRS E1 - Climate Change', currentStatus: 'Partial', requiredStatus: 'Full', gap: 'Missing scope 3 emissions calculation methodology', severity: 'high', status: 'in-progress', dueDate: '2025-06-30' },
  { id: 2, framework: 'CSRD', requirement: 'ESRS S1 - Own Workforce', currentStatus: 'Partial', requiredStatus: 'Full', gap: 'Incomplete workforce diversity data collection', severity: 'medium', status: 'open', dueDate: '2025-07-15' },
  { id: 3, framework: 'GRI', requirement: 'GRI 302 - Energy', currentStatus: 'Full', requiredStatus: 'Full', gap: 'No gap - fully compliant', severity: 'low', status: 'closed', dueDate: '2025-01-15' },
  { id: 4, framework: 'GRI', requirement: 'GRI 305 - Emissions', currentStatus: 'Partial', requiredStatus: 'Full', gap: 'Missing GHG protocol alignment documentation', severity: 'high', status: 'in-progress', dueDate: '2025-05-30' },
  { id: 5, framework: 'TCFD', requirement: 'Risk Management', currentStatus: 'Partial', requiredStatus: 'Full', gap: 'Scenario analysis not fully implemented', severity: 'critical', status: 'open', dueDate: '2025-08-15' },
  { id: 6, framework: 'TCFD', requirement: 'Metrics & Targets', currentStatus: 'Partial', requiredStatus: 'Full', gap: 'Missing forward-looking carbon intensity targets', severity: 'high', status: 'open', dueDate: '2025-09-30' },
  { id: 7, framework: 'ISSB', requirement: 'IFRS S1 - General Requirements', currentStatus: 'None', requiredStatus: 'Full', gap: 'No formal ESG disclosure policy in place', severity: 'critical', status: 'open', dueDate: '2025-10-31' },
  { id: 8, framework: 'ISSB', requirement: 'IFRS S2 - Climate', currentStatus: 'None', requiredStatus: 'Full', gap: 'Climate-related disclosures not prepared', severity: 'critical', status: 'in-progress', dueDate: '2025-12-31' },
  { id: 9, framework: 'SFDR', requirement: 'PAI Indicators', currentStatus: 'Partial', requiredStatus: 'Full', gap: 'Incomplete principal adverse impact reporting', severity: 'medium', status: 'open', dueDate: '2025-07-31' }
])

const remediationTasks = ref<RemediationTask[]>([
  { id: 1, title: 'Implement Scope 3 Emissions Tracking', description: 'Develop methodology and data collection process for scope 3 emissions across value chain.', framework: 'CSRD', owner: 'Sarah Chen', dueDate: '2025-06-30', status: 'in-progress', priority: 'high', progress: 45 },
  { id: 2, title: 'Enhance Diversity Data Collection', description: 'Implement HR system updates to capture comprehensive DEI metrics.', framework: 'CSRD', owner: 'John Smith', dueDate: '2025-07-15', status: 'open', priority: 'medium', progress: 10 },
  { id: 3, title: 'Develop Climate Scenario Analysis', description: 'Create climate scenario models for physical and transition risks.', framework: 'TCFD', owner: 'Mike Johnson', dueDate: '2025-08-15', status: 'open', priority: 'critical', progress: 25 },
  { id: 4, title: 'Establish ESG Disclosure Policy', description: 'Create formal ESG reporting policy aligned with ISSB standards.', framework: 'ISSB', owner: 'Lisa Wong', dueDate: '2025-10-31', status: 'open', priority: 'critical', progress: 5 }
])

// ==================== Computed Values ====================
const overallCompliance = computed(() => 68)
const metRequirements = computed(() => 8)
const totalRequirements = computed(() => 24)
const openGaps = computed(() => 7)
const criticalGaps = computed(() => 3)
const inProgressGaps = computed(() => 3)
const complianceTrend = computed(() => 5.2)

const filteredGaps = computed(() => {
  let result = [...complianceGaps.value]
  if (frameworkFilter.value !== 'all') {
    result = result.filter(g => g.framework === frameworkFilter.value)
  }
  if (severityFilter.value !== 'all') {
    result = result.filter(g => g.severity === severityFilter.value)
  }
  if (statusFilter.value !== 'all') {
    result = result.filter(g => g.status === statusFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(g =>
        g.requirement.toLowerCase().includes(search) ||
        g.gap.toLowerCase().includes(search) ||
        g.framework.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedGaps = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredGaps.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return map[severity] || 'info'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    open: 'danger',
    'in-progress': 'warning',
    closed: 'success'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    open: 'Open',
    'in-progress': 'In Progress',
    closed: 'Closed'
  }
  return map[status] || status
}

const getProgressColor = (percentage: number) => {
  if (percentage >= 100) return '#67c23a'
  if (percentage >= 50) return '#409eff'
  if (percentage >= 25) return '#e6a23c'
  return '#f56c6c'
}

const isOverdue = (dueDate: string) => {
  return new Date(dueDate) < new Date()
}

// ==================== Chart Functions ====================
const initFrameworkChart = () => {
  if (!frameworkChartRef.value) return
  if (frameworkChart) frameworkChart.dispose()

  frameworkChart = echarts.init(frameworkChartRef.value)

  const frameworks = ['CSRD', 'GRI', 'TCFD', 'ISSB', 'SFDR']
  const complianceRates = [65, 85, 45, 30, 55]
  const targetRates = [100, 100, 100, 100, 100]

  frameworkChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value: number) => value + '%' },
    legend: { data: ['Current Compliance', 'Target'], bottom: 0 },
    grid: { left: '10%', right: '5%', top: '5%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: frameworks },
    yAxis: { type: 'value', name: 'Compliance (%)', max: 100 },
    series: [
      { name: 'Current Compliance', type: 'bar', data: complianceRates, itemStyle: { borderRadius: [4, 4, 0, 0], color: (params: any) => params.data >= 80 ? '#67c23a' : params.data >= 60 ? '#409eff' : '#e6a23c' }, label: { show: true, position: 'top', formatter: '{c}%' } },
      { name: 'Target', type: 'line', data: targetRates, symbol: 'none', lineStyle: { width: 2, color: '#f56c6c', type: 'dashed' } }
    ]
  })
}

const initSeverityChart = () => {
  if (!severityChartRef.value) return
  if (severityChart) severityChart.dispose()

  severityChart = echarts.init(severityChartRef.value)

  severityChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} gaps ({d}%)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: [
        { name: 'Critical', value: 3, itemStyle: { color: '#f56c6c' } },
        { name: 'High', value: 4, itemStyle: { color: '#e6a23c' } },
        { name: 'Medium', value: 2, itemStyle: { color: '#409eff' } },
        { name: 'Low', value: 1, itemStyle: { color: '#67c23a' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 }
    }]
  })
}

// ==================== Actions ====================
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Compliance gap data refreshed')
  initFrameworkChart()
  initSeverityChart()
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting compliance gap report...')
}

const addAssessment = () => {
  ElMessage.info('New compliance assessment')
}

const viewGap = (row: ComplianceGap) => {
  ElMessage.info(`Viewing gap: ${row.requirement}`)
}

const updateProgress = (row: ComplianceGap) => {
  ElMessage.info(`Updating progress for: ${row.requirement}`)
}

const addRemediationTask = () => {
  ElMessage.info('Add new remediation task')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Window Resize Handler ====================
const handleResize = () => {
  frameworkChart?.resize()
  severityChart?.resize()
}

// ==================== Lifecycle ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
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
        initFrameworkChart()
        initSeverityChart()
      }, 100)
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  frameworkChart?.dispose()
  severityChart?.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
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
  font-size: 28px;
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
  width: 280px;
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
.compliance-gap-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* KPI Cards */
.kpi-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kpi-card.overall .kpi-icon { background: #e8f4ff; color: #409eff; }
.kpi-card.met .kpi-icon { background: #e8f8f0; color: #67c23a; }
.kpi-card.gap .kpi-icon { background: #ffe8e8; color: #f56c6c; }
.kpi-card.in-progress .kpi-icon { background: #fff7e8; color: #e6a23c; }

.kpi-info {
  flex: 1;
}

.kpi-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-sub {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 2px;
}

.kpi-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 13px;
  font-weight: 500;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

/* Chart Cards */
.chart-card, .table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1f2f3d;
}

.header-filters {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.chart-container {
  height: 320px;
  width: 100%;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

/* Table Styles */
.text-danger {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  padding: 20px 0 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
  margin-top: 16px;
}

/* Remediation Section */
.remediation-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.remediation-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.remediation-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 14px;
  transition: all 0.2s;
}

.remediation-item:hover {
  background: #f5f7fa;
  transform: translateX(4px);
}

.task-status {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.task-status.critical { background: #ffe8e8; color: #f56c6c; }
.task-status.high { background: #ffe8e8; color: #f56c6c; }
.task-status.medium { background: #fff7e8; color: #e6a23c; }
.task-status.low { background: #e8f8f0; color: #67c23a; }

.task-content {
  flex: 1;
}

.task-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 6px;
}

.task-description {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.task-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #909399;
}

.task-meta .el-icon {
  vertical-align: middle;
  margin-right: 4px;
}

.task-progress {
  flex-shrink: 0;
}

:deep(.el-table) {
  border-radius: 12px;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  font-weight: 600;
  color: #1f2f3d;
}
</style>