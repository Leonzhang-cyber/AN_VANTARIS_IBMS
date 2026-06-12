<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing AI recommendation engine...',
  'Analyzing system data...',
  'Generating recommendations...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedCategory = ref('all')
const selectedPriority = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)

let recommendationChart: echarts.ECharts | null = null

// Category filters
const categoryOptions = [
  { value: 'all', label: 'All Categories', icon: '📋' },
  { value: 'energy', label: 'Energy', icon: '⚡' },
  { value: 'maintenance', label: 'Maintenance', icon: '🔧' },
  { value: 'security', label: 'Security', icon: '🔒' },
  { value: 'performance', label: 'Performance', icon: '📊' },
  { value: 'cost', label: 'Cost Savings', icon: '💰' }
]

// Priority filters
const priorityOptions = [
  { value: 'all', label: 'All Priorities' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Recommendations data
const recommendations = ref([
  {
    id: 'REC001', title: 'Optimize HVAC Schedule', category: 'energy', priority: 'high',
    description: 'Based on occupancy patterns, HVAC can be reduced by 15% during off-peak hours (10 PM - 6 AM).',
    impact: 'Estimated savings: $2,500/month',
    roi: '3 months', confidence: 92, status: 'pending',
    createdAt: '2024-01-15', actions: ['View Details', 'Apply', 'Dismiss']
  },
  {
    id: 'REC002', title: 'Replace UPS Batteries', category: 'maintenance', priority: 'critical',
    description: 'UPS batteries are at 25% capacity and have exceeded recommended lifespan of 3 years.',
    impact: 'Risk of downtime during power outage',
    roi: 'Preventive action', confidence: 98, status: 'pending',
    createdAt: '2024-01-14', actions: ['View Details', 'Schedule Replacement', 'Dismiss']
  },
  {
    id: 'REC003', title: 'Adjust Lighting Schedules', category: 'energy', priority: 'medium',
    description: 'Motion sensors show low occupancy after 7 PM. Adjust lighting schedule to reduce energy waste.',
    impact: 'Estimated savings: $800/month',
    roi: '1 month', confidence: 88, status: 'pending',
    createdAt: '2024-01-13', actions: ['View Details', 'Apply', 'Dismiss']
  },
  {
    id: 'REC004', title: 'Enable Demand Response', category: 'energy', priority: 'high',
    description: 'Peak demand charges could be reduced by 20% by enabling demand response during peak hours.',
    impact: 'Estimated savings: $3,200/month',
    roi: '2 months', confidence: 85, status: 'applied',
    createdAt: '2024-01-12', actions: ['View Details', 'Applied']
  },
  {
    id: 'REC005', title: 'Update Security Camera Firmware', category: 'security', priority: 'high',
    description: '8 cameras are running outdated firmware with known security vulnerabilities.',
    impact: 'Reduce security risk',
    roi: 'Immediate', confidence: 95, status: 'pending',
    createdAt: '2024-01-11', actions: ['View Details', 'Schedule Update', 'Dismiss']
  },
  {
    id: 'REC006', title: 'Implement Predictive Maintenance', category: 'maintenance', priority: 'medium',
    description: 'AI analysis suggests AHU-3 may fail within 30 days based on vibration patterns.',
    impact: 'Prevent $50,000 equipment failure',
    roi: '1 week', confidence: 78, status: 'pending',
    createdAt: '2024-01-10', actions: ['View Details', 'Schedule Inspection', 'Dismiss']
  },
  {
    id: 'REC007', title: 'Add Variable Frequency Drives', category: 'performance', priority: 'low',
    description: 'Installing VFDs on pumps could improve efficiency by 25-30%.',
    impact: 'Estimated savings: $4,000/month',
    roi: '8 months', confidence: 82, status: 'pending',
    createdAt: '2024-01-09', actions: ['View Details', 'Calculate ROI', 'Dismiss']
  },
  {
    id: 'REC008', title: 'Optimize Chiller Sequencing', category: 'energy', priority: 'medium',
    description: 'Current chiller sequencing causes inefficiency at partial loads. Optimize based on demand.',
    impact: 'Estimated savings: $1,800/month',
    roi: '1 month', confidence: 90, status: 'applied',
    createdAt: '2024-01-08', actions: ['View Details', 'Applied']
  }
])

// Recommendation statistics
const recStats = reactive({
  total: 0,
  pending: 0,
  applied: 0,
  dismissed: 0,
  high: 0,
  medium: 0,
  low: 0,
  totalSavings: 0,
  avgConfidence: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: recommendations.value.length
})

// Filtered recommendations
const filteredRecommendations = computed(() => {
  let filtered = recommendations.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(r => r.category === selectedCategory.value)
  }
  if (selectedPriority.value !== 'all') {
    filtered = filtered.filter(r => r.priority === selectedPriority.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  recommendationChart = echarts.init(chartRef.value)
  recommendationChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Recommendations'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Energy', 'Maintenance', 'Security', 'Performance', 'Cost'] },
    yAxis: { type: 'value', name: 'Number of Recommendations' },
    series: [{
      name: 'Recommendations',
      type: 'bar',
      data: [4, 2, 1, 1, 0],
      itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top' }
    }]
  })
}

const updateStats = () => {
  recStats.total = recommendations.value.length
  recStats.pending = recommendations.value.filter(r => r.status === 'pending').length
  recStats.applied = recommendations.value.filter(r => r.status === 'applied').length
  recStats.dismissed = recommendations.value.filter(r => r.status === 'dismissed').length
  recStats.high = recommendations.value.filter(r => r.priority === 'high' || r.priority === 'critical').length
  recStats.medium = recommendations.value.filter(r => r.priority === 'medium').length
  recStats.low = recommendations.value.filter(r => r.priority === 'low').length

  const confidences = recommendations.value.map(r => r.confidence)
  recStats.avgConfidence = Math.round(confidences.reduce((a, b) => a + b, 0) / confidences.length)

  // Calculate estimated savings (simplified)
  recStats.totalSavings = 2500 + 800 + 3200 + 1800 + 4000
}

const handleResize = () => {
  recommendationChart?.resize()
}

// ==================== Recommendation Functions ====================
const refreshRecommendations = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Recommendations refreshed successfully')
}

const viewDetails = (rec: any) => {
  selectedRecommendation.value = rec
  detailsVisible.value = true
}

const applyRecommendation = async (rec: any) => {
  await ElMessageBox.confirm(
      `Apply recommendation: ${rec.title}?`,
      'Confirm Apply',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const index = recommendations.value.findIndex(r => r.id === rec.id)
  if (index !== -1) {
    recommendations.value[index].status = 'applied'
  }

  updateStats()
  loading.value = false
  ElMessage.success(`Recommendation "${rec.title}" applied successfully`)
}

const dismissRecommendation = async (rec: any) => {
  await ElMessageBox.confirm(
      `Dismiss recommendation: ${rec.title}?`,
      'Confirm Dismiss',
      {
        confirmButtonText: 'Dismiss',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  const index = recommendations.value.findIndex(r => r.id === rec.id)
  if (index !== -1) {
    recommendations.value[index].status = 'dismissed'
  }

  updateStats()
  ElMessage.info(`Recommendation dismissed`)
}

const scheduleMaintenance = (rec: any) => {
  ElMessage.info(`Scheduling maintenance for ${rec.title}`)
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'critical': return '#F56C6C'
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getPriorityIcon = (priority: string) => {
  switch (priority) {
    case 'critical': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'pending': return { class: 'status-pending', text: 'Pending' }
    case 'applied': return { class: 'status-applied', text: 'Applied' }
    case 'dismissed': return { class: 'status-dismissed', text: 'Dismissed' }
    default: return { class: '', text: status }
  }
}

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'energy': return '⚡'
    case 'maintenance': return '🔧'
    case 'security': return '🔒'
    case 'performance': return '📊'
    case 'cost': return '💰'
    default: return '📋'
  }
}

const selectedRecommendation = ref<any>(null)
</script>

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
          <span class="loading-title">Loading AI Recommendation Center</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Intelligence - AI Recommendation Center</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="recommendation-center-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI Recommendation Center</h1>
        <p class="page-subtitle">Intelligent recommendations to optimize your building operations</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshRecommendations" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><MagicStick /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ recStats.total }}</div>
          <div class="stat-label">Total Recommendations</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ recStats.pending }} Pending</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon savings-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ recStats.totalSavings.toLocaleString() }}</div>
          <div class="stat-label">Estimated Savings</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">per month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon confidence-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ recStats.avgConfidence }}%</div>
          <div class="stat-label">Avg Confidence</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="recStats.avgConfidence" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon applied-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ recStats.applied }}</div>
          <div class="stat-label">Applied</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ recStats.dismissed }} Dismissed</span>
        </div>
      </div>
    </div>

    <!-- Priority Breakdown -->
    <div class="priority-breakdown">
      <div class="priority-item high">
        <span class="priority-dot"></span>
        <span class="priority-label">High Priority</span>
        <span class="priority-count">{{ recStats.high }}</span>
        <div class="priority-bar">
          <div class="bar-fill" :style="{ width: (recStats.high / recStats.total) * 100 + '%', background: '#F56C6C' }"></div>
        </div>
      </div>
      <div class="priority-item medium">
        <span class="priority-dot"></span>
        <span class="priority-label">Medium Priority</span>
        <span class="priority-count">{{ recStats.medium }}</span>
        <div class="priority-bar">
          <div class="bar-fill" :style="{ width: (recStats.medium / recStats.total) * 100 + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
      <div class="priority-item low">
        <span class="priority-dot"></span>
        <span class="priority-label">Low Priority</span>
        <span class="priority-count">{{ recStats.low }}</span>
        <div class="priority-bar">
          <div class="bar-fill" :style="{ width: (recStats.low / recStats.total) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Recommendations by Category</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="rec-chart" style="height: 280px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search recommendations..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="category-filters">
          <button
              v-for="cat in categoryOptions"
              :key="cat.value"
              class="category-chip"
              :class="{ active: selectedCategory === cat.value }"
              @click="selectedCategory = cat.value"
          >
            <span class="chip-icon">{{ cat.icon }}</span>
            <span>{{ cat.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedPriority" placeholder="Priority" clearable style="width: 140px">
          <el-option v-for="p in priorityOptions.slice(1)" :key="p.value" :label="p.label" :value="p.value">
            <span class="priority-option-dot" :style="{ background: p.color }"></span>
            {{ p.label }}
          </el-option>
        </el-select>
      </div>
    </div>

    <!-- Recommendations Grid -->
    <div class="recommendations-grid">
      <div
          v-for="rec in filteredRecommendations"
          :key="rec.id"
          class="rec-card"
          :class="{ applied: rec.status === 'applied', dismissed: rec.status === 'dismissed' }"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-category">
            <span class="category-icon">{{ getCategoryIcon(rec.category) }}</span>
            <span class="category-name">{{ rec.category.toUpperCase() }}</span>
          </div>
          <div class="card-priority">
            <span class="priority-badge" :style="{ background: getPriorityColor(rec.priority) + '20', color: getPriorityColor(rec.priority) }">
              {{ getPriorityIcon(rec.priority) }} {{ rec.priority.toUpperCase() }}
            </span>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ rec.title }}</h4>
          <p class="card-description">{{ rec.description }}</p>

          <!-- Impact & ROI -->
          <div class="impact-info">
            <div class="impact-item">
              <span class="impact-label">Impact</span>
              <span class="impact-value">{{ rec.impact }}</span>
            </div>
            <div class="impact-item">
              <span class="impact-label">ROI</span>
              <span class="impact-value">{{ rec.roi }}</span>
            </div>
            <div class="impact-item">
              <span class="impact-label">Confidence</span>
              <span class="impact-value">{{ rec.confidence }}%</span>
            </div>
          </div>

          <!-- Confidence Bar -->
          <div class="confidence-bar">
            <div class="bar-fill" :style="{ width: rec.confidence + '%', background: rec.confidence > 85 ? '#67C23A' : rec.confidence > 70 ? '#E6A23C' : '#F56C6C' }"></div>
          </div>

          <!-- Status Badge -->
          <div class="status-badge" :class="getStatusBadge(rec.status).class">
            {{ getStatusBadge(rec.status).text }}
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-date">
            <el-icon><Clock /></el-icon>
            <span>{{ rec.createdAt }}</span>
          </div>
          <div class="card-actions">
            <el-button size="small" @click="viewDetails(rec)">Details</el-button>
            <el-button
                v-if="rec.status === 'pending'"
                size="small"
                type="primary"
                @click="applyRecommendation(rec)"
            >
              Apply
            </el-button>
            <el-button
                v-if="rec.status === 'pending'"
                size="small"
                @click="dismissRecommendation(rec)"
            >
              Dismiss
            </el-button>
            <el-button
                v-if="rec.title.includes('UPS')"
                size="small"
                type="warning"
                @click="scheduleMaintenance(rec)"
            >
              Schedule
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredRecommendations.length === 0" class="empty-state">
      <el-empty description="No recommendations found">
        <el-button type="primary">Refresh Recommendations</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredRecommendations.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[8, 12, 16, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Recommendation Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedRecommendation?.title" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Category">
          <el-tag size="small">{{ selectedRecommendation?.category?.toUpperCase() }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Priority">
          <span class="priority-badge" :style="{ background: getPriorityColor(selectedRecommendation?.priority) + '20', color: getPriorityColor(selectedRecommendation?.priority) }">
            {{ selectedRecommendation?.priority?.toUpperCase() }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <span :class="getStatusBadge(selectedRecommendation?.status).class">{{ getStatusBadge(selectedRecommendation?.status).text }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="Confidence">{{ selectedRecommendation?.confidence }}%</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedRecommendation?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="ROI">{{ selectedRecommendation?.roi }}</el-descriptions-item>
        <el-descriptions-item label="Impact" :span="2">{{ selectedRecommendation?.impact }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedRecommendation?.description }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button
            v-if="selectedRecommendation?.status === 'pending'"
            type="primary"
            @click="applyRecommendation(selectedRecommendation)"
        >
          Apply Recommendation
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

/* ==================== Main Content ==================== */
.recommendation-center-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.savings-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.confidence-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.applied-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

/* Priority Breakdown */
.priority-breakdown {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.priority-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.priority-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.priority-item.high .priority-dot { background: #F56C6C; }
.priority-item.medium .priority-dot { background: #E6A23C; }
.priority-item.low .priority-dot { background: #67C23A; }

.priority-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.priority-count {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-left: auto;
}

.priority-bar {
  width: 100%;
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 4px;
}

.priority-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.rec-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.category-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.category-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.category-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-icon {
  font-size: 14px;
}

.filters-right {
  display: flex;
  gap: 12px;
}

.priority-option-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 8px;
}

/* Recommendations Grid */
.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.rec-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.rec-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.rec-card.applied {
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border-left: 4px solid #67c23a;
}

.rec-card.dismissed {
  opacity: 0.6;
  filter: grayscale(0.1);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-category {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 18px;
}

.category-name {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 12px;
}

.priority-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.card-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.impact-info {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 12px;
}

.impact-item {
  flex: 1;
  text-align: center;
}

.impact-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.impact-value {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.confidence-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 12px;
}

.confidence-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-pending {
  background: #fdf6ec;
  color: #e6a23c;
}

.status-applied {
  background: #f0f9ff;
  color: #67c23a;
}

.status-dismissed {
  background: #f5f7fa;
  color: #909399;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.footer-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .priority-breakdown {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .recommendation-center-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .category-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }

  .impact-info {
    flex-direction: column;
  }
}
</style>