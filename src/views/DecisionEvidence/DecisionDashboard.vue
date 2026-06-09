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
        <div class="loading-tip">Decision Dashboard</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="decision-dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Decision Dashboard</h1>
        <p class="description">Decision Evidence Management · Real-time Decision Health & Pending Approvals</p>
      </div>
      <el-button type="primary" @click="handleCreateDecision">
        <el-icon><Plus /></el-icon>
        New Decision
      </el-button>
    </div>

    <!-- Stat Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts & Pending Approvals -->
    <el-row :gutter="20">
      <!-- Left: Decision Trend Chart -->
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Decision Trends (Last 12 Weeks)</span>
              <el-radio-group v-model="chartPeriod" size="small" @change="handleChartPeriodChange">
                <el-radio-button value="week">Week</el-radio-button>
                <el-radio-button value="month">Month</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-wrapper">
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
        </el-card>
      </el-col>

      <!-- Right: Decision Type Distribution & Pending Approvals -->
      <el-col :xs="24" :lg="10">
        <el-card class="distribution-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Decision Type Distribution</span>
              <el-button link type="primary" @click="handleViewAllDist">View All</el-button>
            </div>
          </template>
          <div class="chart-wrapper">
            <div ref="distChartRef" class="chart-container-small"></div>
          </div>
        </el-card>

        <el-card class="approval-card" shadow="hover" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>Pending Approvals</span>
              <el-badge :value="pendingApprovals.length" class="badge" />
            </div>
          </template>
          <div class="approval-list">
            <div v-for="item in pendingApprovals" :key="item.id" class="approval-item">
              <div class="approval-info">
                <div class="approval-title">{{ item.title }}</div>
                <div class="approval-meta">
                  <el-tag :type="getDecisionTypeTag(item.type)" size="small">{{ item.type }}</el-tag>
                  <span class="approval-time">{{ item.submitTime }}</span>
                </div>
              </div>
              <div class="approval-actions">
                <el-button link type="success" size="small" @click="handleApprove(item)">Approve</el-button>
                <el-button link type="danger" size="small" @click="handleReject(item)">Reject</el-button>
              </div>
            </div>
            <el-empty v-if="pendingApprovals.length === 0" description="No pending approvals" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Recent Decisions Table -->
    <el-card class="table-card" shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>Recent Decisions</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search decision title"
                prefix-icon="Search"
                clearable
                style="width: 220px"
                @clear="handleSearch"
                @keyup.enter="handleSearch"
            />
            <el-button :icon="Refresh" @click="fetchRecentDecisions" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDecisions" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="title" label="Decision Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getDecisionTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="initiator" label="Initiator" width="120" />
        <el-table-column prop="submitTime" label="Submit Time" width="160" />
        <el-table-column prop="approvalProgress" label="Approval Progress" width="200">
          <template #default="{ row }">
            <el-progress :percentage="row.approvalProgress" :status="row.approvalProgress === 100 ? 'success' : undefined" />
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">Details</el-button>
            <el-button link type="danger" size="small" @click="deleteDecision(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDecisions.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- New Decision Dialog -->
    <el-dialog v-model="dialogVisible" title="New Decision" width="600px" destroy-on-close>
      <el-form :model="newDecision" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="Decision Title" prop="title">
          <el-input v-model="newDecision.title" placeholder="Enter decision title" />
        </el-form-item>
        <el-form-item label="Decision Type" prop="type">
          <el-select v-model="newDecision.type" placeholder="Select type">
            <el-option label="Fault Decision" value="Fault Decision" />
            <el-option label="Maintenance Decision" value="Maintenance Decision" />
            <el-option label="ESG Decision" value="ESG Decision" />
            <el-option label="Energy Decision" value="Energy Decision" />
            <el-option label="AI Recommendation" value="AI Recommendation" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="newDecision.description" type="textarea" :rows="3" placeholder="Enter decision description" />
        </el-form-item>
        <el-form-item label="Urgency" prop="urgency">
          <el-radio-group v-model="newDecision.urgency">
            <el-radio value="Low">Low</el-radio>
            <el-radio value="Medium">Medium</el-radio>
            <el-radio value="High">High</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitDecision">Submit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Mock Data ====================
interface StatCard {
  title: string
  value: number
  trend: number
  icon: string
  bgColor: string
  key: string
}

interface PendingApproval {
  id: number
  title: string
  type: string
  submitTime: string
  initiator: string
}

interface RecentDecision {
  id: number
  title: string
  type: string
  status: string
  initiator: string
  submitTime: string
  approvalProgress: number
}

const statsCards = ref<StatCard[]>([
  { title: 'Total Decisions', value: 284, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Completed Decisions', value: 198, trend: 8, icon: 'Checked', bgColor: '#67c23a', key: 'completed' },
  { title: 'In Progress', value: 56, trend: -3, icon: 'Clock', bgColor: '#e6a23c', key: 'inProgress' },
  { title: 'Pending Approval', value: 30, trend: 15, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'pending' }
])

const pendingApprovals = ref<PendingApproval[]>([
  { id: 1, title: 'AHU-03 Cooling Tower Replacement Proposal', type: 'Maintenance Decision', submitTime: '2024-01-15 09:30', initiator: 'Zhang Ming' },
  { id: 2, title: 'Data Center PUE Optimization Plan', type: 'Energy Decision', submitTime: '2024-01-15 10:15', initiator: 'Li Fang' },
  { id: 3, title: 'ESG Scope 2 Carbon Reduction Initiative', type: 'ESG Decision', submitTime: '2024-01-14 16:20', initiator: 'Wang Li' },
  { id: 4, title: 'Elevator Fault Root Cause Analysis Report', type: 'Fault Decision', submitTime: '2024-01-14 11:00', initiator: 'Chen Jian' }
])

const recentDecisions = ref<RecentDecision[]>([
  { id: 1, title: 'Cooling Tower Variable Frequency Drive Optimization Strategy', type: 'Energy Decision', status: 'Completed', initiator: 'Zhang Ming', submitTime: '2024-01-10', approvalProgress: 100 },
  { id: 2, title: 'UPS Battery Bank Replacement Decision', type: 'Maintenance Decision', status: 'In Review', initiator: 'Liu Qiang', submitTime: '2024-01-12', approvalProgress: 60 },
  { id: 3, title: 'HVAC System AI Energy Saving Model Deployment', type: 'AI Recommendation', status: 'Pending', initiator: 'Li Fang', submitTime: '2024-01-13', approvalProgress: 20 },
  { id: 4, title: 'Lighting System Energy Consumption Benchmark Analysis', type: 'Energy Decision', status: 'Completed', initiator: 'Wang Li', submitTime: '2024-01-09', approvalProgress: 100 },
  { id: 5, title: 'Carbon Emission Data Verification Report', type: 'ESG Decision', status: 'In Review', initiator: 'Chen Jian', submitTime: '2024-01-14', approvalProgress: 50 },
  { id: 6, title: 'Campus HVAC Chiller Fault Prediction', type: 'Fault Decision', status: 'Pending', initiator: 'Zhang Ming', submitTime: '2024-01-15', approvalProgress: 30 },
])

// ==================== Reactive Variables ====================
const trendChartRef = ref<HTMLElement>()
const distChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let distChart: echarts.ECharts | null = null

const chartPeriod = ref<'week' | 'month'>('week')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const tableLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref()

const newDecision = reactive({
  title: '',
  type: '',
  description: '',
  urgency: 'Medium'
})

const formRules = {
  title: [{ required: true, message: 'Please enter decision title', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select decision type', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredDecisions = computed(() => {
  let filtered = [...recentDecisions.value]
  if (searchKeyword.value) {
    filtered = filtered.filter(d => d.title.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  }
  return filtered
})

const paginatedDecisions = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDecisions.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getDecisionTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Fault Decision': 'danger',
    'Maintenance Decision': 'warning',
    'ESG Decision': 'success',
    'Energy Decision': 'primary',
    'AI Recommendation': 'info'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Completed': 'success',
    'In Review': 'warning',
    'Pending': 'danger'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initTrendChart = () => {
  if (!trendChartRef.value) {
    console.warn('trendChartRef is not ready')
    return
  }

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Fault Decision', 'Maintenance Decision', 'ESG Decision', 'Energy Decision', 'AI Recommendation'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8', 'W9', 'W10', 'W11', 'W12'] },
    yAxis: { type: 'value', name: 'Decision Count' },
    series: [
      { name: 'Fault Decision', type: 'bar', stack: 'total', data: [5, 7, 6, 8, 9, 10, 7, 11, 13, 12, 14, 16], itemStyle: { borderRadius: [0, 0, 0, 0] } },
      { name: 'Maintenance Decision', type: 'bar', stack: 'total', data: [8, 9, 10, 11, 10, 12, 14, 13, 15, 16, 18, 20] },
      { name: 'ESG Decision', type: 'bar', stack: 'total', data: [3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18] },
      { name: 'Energy Decision', type: 'bar', stack: 'total', data: [10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 23, 25] },
      { name: 'AI Recommendation', type: 'bar', stack: 'total', data: [2, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17] }
    ]
  }
  trendChart.setOption(option)

  // Handle window resize
  const handleResize = () => {
    trendChart?.resize()
  }
  window.addEventListener('resize', handleResize)
}

const initDistChart = () => {
  if (!distChartRef.value) {
    console.warn('distChartRef is not ready')
    return
  }

  if (distChart) {
    distChart.dispose()
  }

  distChart = echarts.init(distChartRef.value)
  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [
      {
        name: 'Decision Type Distribution',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 78, name: 'Energy Decision', itemStyle: { color: '#409eff' } },
          { value: 62, name: 'Maintenance Decision', itemStyle: { color: '#e6a23c' } },
          { value: 45, name: 'Fault Decision', itemStyle: { color: '#f56c6c' } },
          { value: 38, name: 'ESG Decision', itemStyle: { color: '#67c23a' } },
          { value: 21, name: 'AI Recommendation', itemStyle: { color: '#909399' } }
        ],
        emphasis: { scale: true },
        label: { show: true, formatter: '{b}: {d}%' }
      }
    ]
  }
  distChart.setOption(option)

  // Handle window resize
  const handleResize = () => {
    distChart?.resize()
  }
  window.addEventListener('resize', handleResize)
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleChartPeriodChange = (val: 'week' | 'month') => {
  ElMessage.success(`Switched to ${val === 'week' ? 'Week' : 'Month'} view`)
  if (trendChart) {
    const newTrendData = val === 'week'
        ? [5, 7, 6, 8, 9, 10, 7, 11, 13, 12, 14, 16]
        : [28, 32, 35, 38, 42, 45, 48, 51, 55, 60, 65, 70]
    trendChart.setOption({
      series: [
        { data: newTrendData.map(() => Math.floor(Math.random() * 10) + 5) },
        { data: newTrendData.map(() => Math.floor(Math.random() * 15) + 8) },
        { data: newTrendData.map(() => Math.floor(Math.random() * 12) + 3) },
        { data: newTrendData },
        { data: newTrendData.map(() => Math.floor(Math.random() * 8) + 2) }
      ]
    })
  }
}

const handleViewAllDist = () => {
  ElMessage.info('Opening full decision type analysis report')
}

const handleApprove = (item: PendingApproval) => {
  ElMessageBox.confirm(`Approve decision "${item.title}"?`, 'Approval Confirmation', {
    confirmButtonText: 'Approve',
    cancelButtonText: 'Cancel',
    type: 'success'
  }).then(() => {
    ElMessage.success(`Approved: ${item.title}`)
    pendingApprovals.value = pendingApprovals.value.filter(i => i.id !== item.id)
    statsCards.value[3].value = pendingApprovals.value.length
  }).catch(() => {})
}

const handleReject = (item: PendingApproval) => {
  ElMessageBox.confirm(`Reject decision "${item.title}"?`, 'Approval Confirmation', {
    confirmButtonText: 'Reject',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.warning(`Rejected: ${item.title}`)
    pendingApprovals.value = pendingApprovals.value.filter(i => i.id !== item.id)
    statsCards.value[3].value = pendingApprovals.value.length
  }).catch(() => {})
}

const viewDetail = (row: RecentDecision) => {
  ElMessage.info(`Viewing decision details: ${row.title}`)
}

const deleteDecision = (row: RecentDecision) => {
  ElMessageBox.confirm(`Delete decision "${row.title}"?`, 'Delete Confirmation', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'error'
  }).then(() => {
    ElMessage.success(`Deleted: ${row.title}`)
    const index = recentDecisions.value.findIndex(d => d.id === row.id)
    if (index !== -1) recentDecisions.value.splice(index, 1)
  }).catch(() => {})
}

const handleCreateDecision = () => {
  dialogVisible.value = true
}

const submitDecision = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Decision submitted, waiting for approval')
      dialogVisible.value = false
      formRef.value?.resetFields()
      pendingApprovals.value.unshift({
        id: Date.now(),
        title: newDecision.title,
        type: newDecision.type,
        submitTime: new Date().toLocaleString(),
        initiator: 'Current User'
      })
      statsCards.value[3].value = pendingApprovals.value.length
    }
  })
}

const fetchRecentDecisions = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initDistChart()
  }, 100)
}

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
      initCharts()
      fetchRecentDecisions()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Dashboard Styles ==================== */
.decision-dashboard {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.chart-card, .distribution-card, .approval-card, .table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-wrapper {
  width: 100%;
  min-height: 300px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.chart-container-small {
  width: 100%;
  height: 280px;
}

.approval-list {
  max-height: 320px;
  overflow-y: auto;

  .approval-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #ebeef5;

    &:last-child {
      border-bottom: none;
    }

    .approval-info {
      flex: 1;

      .approval-title {
        font-weight: 500;
        margin-bottom: 6px;
      }

      .approval-meta {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 12px;
        color: #909399;
      }
    }

    .approval-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.table-card {
  .table-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>