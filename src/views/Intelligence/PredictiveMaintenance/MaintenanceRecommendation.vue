<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Calendar, Tools, Ticket
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Analyzing maintenance data...',
  'Generating recommendations...',
  'Calculating priorities...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedPriority = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const scheduleVisible = ref(false)
const chartRef = ref(null)

let recommendationChart: echarts.ECharts | null = null

// Priority filters
const priorityOptions = [
  { value: 'all', label: 'All Priorities' },
  { value: 'urgent', label: 'Urgent', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'predictive', label: 'Predictive' },
  { value: 'preventive', label: 'Preventive' },
  { value: 'corrective', label: 'Corrective' }
]

// Maintenance recommendations data
const recommendations = ref([
  {
    id: 'REC001', equipment: 'Chiller-1', type: 'predictive', priority: 'urgent',
    title: 'Compressor Replacement Required', description: 'Vibration analysis indicates imminent compressor failure. Replace within 7 days.',
    estimatedCost: 12500, estimatedHours: 8, impact: 'Critical - System downtime risk',
    benefits: 'Prevents complete system failure, extends equipment life',
    assignedTo: 'HVAC Team', dueDate: '2024-01-20', status: 'pending',
    confidence: 92, roi: 'High'
  },
  {
    id: 'REC002', equipment: 'AHU-2', type: 'predictive', priority: 'high',
    title: 'Bearing Replacement', description: 'Bearing wear detected. Schedule replacement within 14 days.',
    estimatedCost: 3500, estimatedHours: 4, impact: 'High - Efficiency loss',
    benefits: 'Restores efficiency, prevents motor damage',
    assignedTo: 'HVAC Team', dueDate: '2024-01-28', status: 'pending',
    confidence: 85, roi: 'Medium'
  },
  {
    id: 'REC003', equipment: 'Cooling Tower', type: 'preventive', priority: 'medium',
    title: 'Fan Motor Lubrication', description: 'Regular maintenance due. Lubricate fan motor bearings.',
    estimatedCost: 500, estimatedHours: 2, impact: 'Medium - Minor efficiency impact',
    benefits: 'Extends motor life, prevents unexpected failure',
    assignedTo: 'Maintenance Team', dueDate: '2024-02-05', status: 'pending',
    confidence: 95, roi: 'Low'
  },
  {
    id: 'REC004', equipment: 'Main Switchboard', type: 'preventive', priority: 'low',
    title: 'Thermal Imaging Inspection', description: 'Quarterly thermal scan to detect hot spots.',
    estimatedCost: 800, estimatedHours: 3, impact: 'Low - Preventive check',
    benefits: 'Identifies potential issues early',
    assignedTo: 'Electrical Team', dueDate: '2024-02-15', status: 'pending',
    confidence: 98, roi: 'Low'
  },
  {
    id: 'REC005', equipment: 'VFD Pump', type: 'predictive', priority: 'high',
    title: 'Seal Replacement', description: 'Seal degradation detected. Replace to prevent leakage.',
    estimatedCost: 2800, estimatedHours: 3, impact: 'High - Potential leakage',
    benefits: 'Prevents water damage, maintains efficiency',
    assignedTo: 'Mechanical Team', dueDate: '2024-01-25', status: 'pending',
    confidence: 82, roi: 'Medium'
  },
  {
    id: 'REC006', equipment: 'AHU-1', type: 'corrective', priority: 'medium',
    title: 'Filter Replacement', description: 'Filters are at 80% capacity. Replace to maintain air quality.',
    estimatedCost: 350, estimatedHours: 1, impact: 'Medium - Air quality impact',
    benefits: 'Improves air quality, reduces energy consumption',
    assignedTo: 'HVAC Team', dueDate: '2024-02-01', status: 'pending',
    confidence: 96, roi: 'Low'
  },
  {
    id: 'REC007', equipment: 'Chiller-2', type: 'predictive', priority: 'urgent',
    title: 'Refrigerant Leak Repair', description: 'Refrigerant levels dropping. Immediate repair needed.',
    estimatedCost: 4800, estimatedHours: 6, impact: 'Critical - Cooling loss',
    benefits: 'Restores cooling capacity, environmental compliance',
    assignedTo: 'HVAC Team', dueDate: '2024-01-18', status: 'pending',
    confidence: 88, roi: 'High'
  },
  {
    id: 'REC008', equipment: 'Air Compressor', type: 'preventive', priority: 'low',
    title: 'Oil Change Service', description: 'Scheduled oil change and filter replacement.',
    estimatedCost: 450, estimatedHours: 2, impact: 'Low - Routine maintenance',
    benefits: 'Extends compressor life, maintains efficiency',
    assignedTo: 'Mechanical Team', dueDate: '2024-02-20', status: 'pending',
    confidence: 99, roi: 'Low'
  }
])

// Recommendation statistics
const recStats = reactive({
  total: 0,
  urgent: 0,
  high: 0,
  medium: 0,
  low: 0,
  predictive: 0,
  preventive: 0,
  corrective: 0,
  totalCost: 0,
  avgConfidence: 0
})

// Schedule form
const scheduleForm = reactive({
  recommendationId: '',
  scheduledDate: '',
  assignedTeam: '',
  notes: ''
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
        r.equipment.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.title.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedPriority.value !== 'all') {
    filtered = filtered.filter(r => r.priority === selectedPriority.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(r => r.type === selectedType.value)
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
    legend: { data: ['Number of Recommendations'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Urgent', 'High', 'Medium', 'Low'] },
    yAxis: { type: 'value', name: 'Count' },
    series: [{
      name: 'Number of Recommendations',
      type: 'bar',
      data: [recStats.urgent, recStats.high, recStats.medium, recStats.low],
      itemStyle: {
        color: (params: any) => {
          const colors = ['#F56C6C', '#F56C6C', '#E6A23C', '#67C23A']
          return colors[params.dataIndex]
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const updateStats = () => {
  recStats.total = recommendations.value.length
  recStats.urgent = recommendations.value.filter(r => r.priority === 'urgent').length
  recStats.high = recommendations.value.filter(r => r.priority === 'high').length
  recStats.medium = recommendations.value.filter(r => r.priority === 'medium').length
  recStats.low = recommendations.value.filter(r => r.priority === 'low').length
  recStats.predictive = recommendations.value.filter(r => r.type === 'predictive').length
  recStats.preventive = recommendations.value.filter(r => r.type === 'preventive').length
  recStats.corrective = recommendations.value.filter(r => r.type === 'corrective').length
  recStats.totalCost = recommendations.value.reduce((sum, r) => sum + r.estimatedCost, 0)
  recStats.avgConfidence = Math.round(recommendations.value.reduce((sum, r) => sum + r.confidence, 0) / recommendations.value.length)

  // Update chart
  if (recommendationChart) {
    recommendationChart.setOption({
      series: [{
        data: [recStats.urgent, recStats.high, recStats.medium, recStats.low]
      }]
    })
  }
}

const handleResize = () => {
  recommendationChart?.resize()
}

// ==================== Recommendation Functions ====================
const refreshData = async () => {
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

const openSchedule = (rec: any) => {
  selectedRecommendation.value = rec
  scheduleForm.recommendationId = rec.id
  scheduleForm.scheduledDate = ''
  scheduleForm.assignedTeam = rec.assignedTo
  scheduleForm.notes = ''
  scheduleVisible.value = true
}

const scheduleMaintenance = async () => {
  if (!scheduleForm.scheduledDate) {
    ElMessage.warning('Please select a scheduled date')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = recommendations.value.findIndex(r => r.id === scheduleForm.recommendationId)
  if (index !== -1) {
    recommendations.value[index].status = 'scheduled'
    recommendations.value[index].dueDate = scheduleForm.scheduledDate
    recommendations.value[index].assignedTo = scheduleForm.assignedTeam
  }

  scheduleVisible.value = false
  ElMessage.success('Maintenance scheduled successfully')
}

const approveRecommendation = async (rec: any) => {
  await ElMessageBox.confirm(
      `Approve maintenance recommendation for ${rec.equipment}?`,
      'Confirm Approval',
      {
        confirmButtonText: 'Approve',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )

  const index = recommendations.value.findIndex(r => r.id === rec.id)
  if (index !== -1) {
    recommendations.value[index].status = 'approved'
  }

  ElMessage.success('Recommendation approved')
}

const dismissRecommendation = async (rec: any) => {
  await ElMessageBox.confirm(
      `Dismiss recommendation for ${rec.equipment}?`,
      'Confirm Dismiss',
      {
        confirmButtonText: 'Dismiss',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  const index = recommendations.value.findIndex(r => r.id === rec.id)
  if (index !== -1) {
    recommendations.value.splice(index, 1)
  }

  updateStats()
  ElMessage.info('Recommendation dismissed')
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
    case 'urgent': return '#F56C6C'
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getPriorityIcon = (priority: string) => {
  switch (priority) {
    case 'urgent': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'predictive': return '🔮'
    case 'preventive': return '🛡️'
    case 'corrective': return '🔧'
    default: return '📋'
  }
}

const formatCurrency = (value: number) => {
  return `$${value.toLocaleString()}`
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
          <span class="loading-title">Loading Maintenance Recommendations</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Predictive Maintenance - Recommendations</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="maintenance-recommendation-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Maintenance Recommendations</h1>
        <p class="page-subtitle">AI-powered maintenance suggestions to optimize equipment reliability</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshData" :loading="loading">
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
          <el-icon><Tools /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ recStats.total }}</div>
          <div class="stat-label">Total Recommendations</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ recStats.urgent }} Urgent</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon cost-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatCurrency(recStats.totalCost) }}</div>
          <div class="stat-label">Estimated Cost</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+15% this quarter</span>
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
        <div class="stat-icon breakdown-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ recStats.predictive }}</div>
          <div class="stat-label">Predictive</div>
        </div>
        <div class="stat-trend">
          <span>{{ recStats.preventive }} Preventive | {{ recStats.corrective }} Corrective</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Recommendations by Priority</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="rec-chart" style="height: 280px"></div>
    </div>

    <!-- Priority Legend -->
    <div class="priority-legend">
      <div class="legend-item">
        <span class="legend-dot urgent"></span>
        <span>Urgent - Immediate Action Required</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot high"></span>
        <span>High - Schedule Within 14 Days</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot medium"></span>
        <span>Medium - Plan Within Month</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot low"></span>
        <span>Low - Routine Planning</span>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search equipment..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="priority-filters">
          <button
              v-for="p in priorityOptions"
              :key="p.value"
              class="priority-chip"
              :class="{ active: selectedPriority === p.value }"
              @click="selectedPriority = p.value"
          >
            <span class="chip-dot" :style="{ background: p.color }"></span>
            <span>{{ p.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedType" placeholder="Type" clearable style="width: 140px">
          <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
    </div>

    <!-- Recommendations Grid -->
    <div class="recommendations-grid">
      <div
          v-for="rec in filteredRecommendations"
          :key="rec.id"
          class="rec-card"
          :class="rec.priority"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="rec-type">
            <span class="type-icon">{{ getTypeIcon(rec.type) }}</span>
            <span class="type-name">{{ rec.type.toUpperCase() }}</span>
          </div>
          <div class="priority-badge" :style="{ background: getPriorityColor(rec.priority) }">
            {{ getPriorityIcon(rec.priority) }} {{ rec.priority.toUpperCase() }}
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="equipment-name">{{ rec.equipment }}</h4>
          <h5 class="rec-title">{{ rec.title }}</h5>
          <p class="rec-description">{{ rec.description }}</p>

          <!-- Cost & Impact -->
          <div class="cost-impact">
            <div class="cost">
              <span class="label">Est. Cost:</span>
              <span class="value">{{ formatCurrency(rec.estimatedCost) }}</span>
            </div>
            <div class="impact">
              <span class="label">Impact:</span>
              <span class="value">{{ rec.impact }}</span>
            </div>
            <div class="hours">
              <span class="label">Est. Hours:</span>
              <span class="value">{{ rec.estimatedHours }} hrs</span>
            </div>
          </div>

          <!-- Benefits -->
          <div class="benefits">
            <span class="benefits-icon">✨</span>
            <span class="benefits-text">{{ rec.benefits }}</span>
          </div>

          <!-- Confidence Bar -->
          <div class="confidence-section">
            <div class="confidence-label">Confidence Score: {{ rec.confidence }}%</div>
            <div class="confidence-bar">
              <div class="bar-fill" :style="{ width: rec.confidence + '%', background: getPriorityColor(rec.priority) }"></div>
            </div>
          </div>

          <!-- Assignment & Due Date -->
          <div class="assignment">
            <div class="assigned">
              <span class="label">Assigned to:</span>
              <span class="value">{{ rec.assignedTo }}</span>
            </div>
            <div class="due-date">
              <span class="label">Due:</span>
              <span class="value" :class="{ overdue: new Date(rec.dueDate) < new Date() }">
                {{ rec.dueDate }}
              </span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="roi-badge" :class="rec.roi.toLowerCase()">
            ROI: {{ rec.roi }}
          </div>
          <div class="card-actions">
            <el-button size="small" @click.stop="viewDetails(rec)">Details</el-button>
            <el-button size="small" type="primary" @click.stop="openSchedule(rec)">Schedule</el-button>
            <el-button size="small" @click.stop="approveRecommendation(rec)">Approve</el-button>
            <el-button size="small" @click.stop="dismissRecommendation(rec)">Dismiss</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredRecommendations.length === 0" class="empty-state">
      <el-empty description="No recommendations found">
        <el-button type="primary">Reset Filters</el-button>
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
    <el-dialog v-model="detailsVisible" :title="selectedRecommendation?.title" width="650px">
      <div class="dialog-content">
        <div class="priority-summary" :class="selectedRecommendation?.priority">
          <div class="priority-tag">
            {{ getPriorityIcon(selectedRecommendation?.priority) }} {{ selectedRecommendation?.priority?.toUpperCase() }}
          </div>
          <div class="type-tag">
            {{ getTypeIcon(selectedRecommendation?.type) }} {{ selectedRecommendation?.type?.toUpperCase() }}
          </div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Equipment">{{ selectedRecommendation?.equipment }}</el-descriptions-item>
          <el-descriptions-item label="Recommendation ID">{{ selectedRecommendation?.id }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedRecommendation?.description }}</el-descriptions-item>
          <el-descriptions-item label="Estimated Cost">{{ formatCurrency(selectedRecommendation?.estimatedCost) }}</el-descriptions-item>
          <el-descriptions-item label="Estimated Hours">{{ selectedRecommendation?.estimatedHours }} hours</el-descriptions-item>
          <el-descriptions-item label="Impact">{{ selectedRecommendation?.impact }}</el-descriptions-item>
          <el-descriptions-item label="Benefits">{{ selectedRecommendation?.benefits }}</el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ selectedRecommendation?.confidence }}%</el-descriptions-item>
          <el-descriptions-item label="ROI">{{ selectedRecommendation?.roi }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedRecommendation?.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Due Date">{{ selectedRecommendation?.dueDate }}</el-descriptions-item>
          <el-descriptions-item label="Status">{{ selectedRecommendation?.status }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedRecommendation?.priority === 'urgent'" class="urgent-alert">
          <el-alert
              title="Urgent Action Required"
              type="error"
              show-icon
              :closable="false"
          >
            <template #default>
              <p>This recommendation requires immediate attention. Schedule within 7 days to prevent equipment failure.</p>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="openSchedule(selectedRecommendation)">Schedule Maintenance</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Dialog -->
    <el-dialog v-model="scheduleVisible" title="Schedule Maintenance" width="500px">
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="Equipment">
          <span>{{ selectedRecommendation?.equipment }}</span>
        </el-form-item>
        <el-form-item label="Recommendation">
          <span>{{ selectedRecommendation?.title }}</span>
        </el-form-item>
        <el-form-item label="Scheduled Date" required>
          <el-date-picker
              v-model="scheduleForm.scheduledDate"
              type="date"
              placeholder="Select date"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Assign Team">
          <el-input v-model="scheduleForm.assignedTeam" placeholder="Team name" />
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="scheduleForm.notes" type="textarea" rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleVisible = false">Cancel</el-button>
        <el-button type="primary" @click="scheduleMaintenance">Schedule</el-button>
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
.maintenance-recommendation-container {
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
  margin-bottom: 24px;
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

.cost-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.confidence-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.breakdown-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
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
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
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

/* Priority Legend */
.priority-legend {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 24px;
  padding: 12px 20px;
  background: white;
  border-radius: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.urgent { background: #F56C6C; }
.legend-dot.high { background: #F56C6C; }
.legend-dot.medium { background: #E6A23C; }
.legend-dot.low { background: #67C23A; }

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

.priority-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.priority-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.priority-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.priority-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Recommendations Grid */
.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.rec-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.rec-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.rec-card.urgent {
  border-left: 4px solid #F56C6C;
}

.rec-card.high {
  border-left: 4px solid #F56C6C;
}

.rec-card.medium {
  border-left: 4px solid #E6A23C;
}

.rec-card.low {
  border-left: 4px solid #67C23A;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.rec-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
}

.type-name {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 12px;
}

.priority-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.equipment-name {
  font-size: 14px;
  color: #909399;
  margin: 0 0 4px 0;
}

.rec-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
}

.rec-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.cost-impact {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 12px;
}

.cost, .impact, .hours {
  text-align: center;
  flex: 1;
}

.cost .label, .impact .label, .hours .label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.cost .value, .impact .value, .hours .value {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.benefits {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #f0f9ff;
  border-radius: 12px;
  margin-bottom: 12px;
}

.benefits-icon {
  font-size: 14px;
}

.benefits-text {
  font-size: 12px;
  color: #409eff;
  font-weight: 500;
}

.confidence-section {
  margin-bottom: 12px;
}

.confidence-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.confidence-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.confidence-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.assignment {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.assignment .label {
  color: #909399;
}

.assignment .value {
  color: #1e293b;
  font-weight: 500;
}

.assignment .value.overdue {
  color: #f56c6c;
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

.roi-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.roi-badge.high {
  background: #f0f9ff;
  color: #67c23a;
}

.roi-badge.medium {
  background: #fdf6ec;
  color: #e6a23c;
}

.roi-badge.low {
  background: #fef0f0;
  color: #f56c6c;
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

/* Dialog Styles */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.priority-summary {
  display: flex;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
}

.priority-summary.urgent {
  background: #fef0f0;
}

.priority-summary.high {
  background: #fef0f0;
}

.priority-summary.medium {
  background: #fdf6ec;
}

.priority-summary.low {
  background: #f0f9ff;
}

.priority-tag, .type-tag {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.priority-summary.urgent .priority-tag { background: #f56c6c; color: white; }
.priority-summary.high .priority-tag { background: #f56c6c; color: white; }
.priority-summary.medium .priority-tag { background: #e6a23c; color: white; }
.priority-summary.low .priority-tag { background: #67c23a; color: white; }

.type-tag {
  background: white;
  color: #409eff;
}

.urgent-alert {
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .recommendations-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }
}

@media (max-width: 768px) {
  .maintenance-recommendation-container {
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

  .priority-filters {
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

  .cost-impact {
    flex-direction: column;
    gap: 8px;
  }

  .card-footer {
    flex-direction: column;
    gap: 12px;
  }

  .card-actions {
    justify-content: center;
  }

  .priority-legend {
    flex-direction: column;
    align-items: center;
  }
}
</style>