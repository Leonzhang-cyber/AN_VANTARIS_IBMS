<template>
  <!-- Loading Screen -->
  <div v-if="!isPageLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
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
        <div class="loading-tip">Predictive Work Orders</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="workorders-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <div class="title-icon predictive-icon">
            <el-icon><TrendCharts /></el-icon>
          </div>
          Predictive Work Orders
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalOrders }} Total Predictions
          </div>
          <div class="stat-badge critical">
            <span class="pulse-dot"></span>
            {{ highRiskCount }} High Risk
          </div>
          <div class="stat-badge">
            {{ pendingCount }} Pending Review
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh Predictions
        </el-button>
        <el-button type="primary" @click="runPredictionModel">
          <el-icon><DataAnalysis /></el-icon>
          Run AI Prediction
        </el-button>
      </div>
    </div>

    <!-- AI Prediction Summary Cards -->
    <div class="ai-summary">
      <div class="summary-card">
        <div class="summary-icon">
          <el-icon><Cpu /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">Model Accuracy</div>
          <div class="summary-value">{{ modelAccuracy }}<span class="unit">%</span></div>
          <div class="summary-trend up">+{{ accuracyImprovement }}% vs last month</div>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">Predictions Generated</div>
          <div class="summary-value">{{ predictionsGenerated }}</div>
          <div class="summary-trend up">+{{ predictionsGrowth }}% this week</div>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">RUL Accuracy</div>
          <div class="summary-value">{{ rulAccuracy }}<span class="unit">%</span></div>
          <div class="summary-trend up">{{ rulImprovement }}% improvement</div>
        </div>
      </div>
      <div class="summary-card">
        <div class="summary-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="summary-content">
          <div class="summary-label">Cost Avoided</div>
          <div class="summary-value">${{ costAvoided }}<span class="unit">K</span></div>
          <div class="summary-trend up">YTD savings</div>
        </div>
      </div>
    </div>

    <!-- Risk Level Distribution -->
    <div class="risk-distribution">
      <div class="risk-section">
        <div class="risk-header">
          <span class="risk-title">Risk Level Distribution</span>
          <span class="risk-subtitle">Based on AI model predictions</span>
        </div>
        <div class="risk-bars">
          <div class="risk-bar-item">
            <div class="risk-bar-label">
              <span class="risk-dot critical"></span>
              High Risk
              <span class="risk-count">{{ highRiskCount }}</span>
            </div>
            <div class="risk-bar-track">
              <div class="risk-bar-fill critical" :style="{ width: highRiskPercent + '%' }"></div>
            </div>
            <div class="risk-bar-value">{{ highRiskPercent }}%</div>
          </div>
          <div class="risk-bar-item">
            <div class="risk-bar-label">
              <span class="risk-dot warning"></span>
              Medium Risk
              <span class="risk-count">{{ mediumRiskCount }}</span>
            </div>
            <div class="risk-bar-track">
              <div class="risk-bar-fill warning" :style="{ width: mediumRiskPercent + '%' }"></div>
            </div>
            <div class="risk-bar-value">{{ mediumRiskPercent }}%</div>
          </div>
          <div class="risk-bar-item">
            <div class="risk-bar-label">
              <span class="risk-dot normal"></span>
              Low Risk
              <span class="risk-count">{{ lowRiskCount }}</span>
            </div>
            <div class="risk-bar-track">
              <div class="risk-bar-fill normal" :style="{ width: lowRiskPercent + '%' }"></div>
            </div>
            <div class="risk-bar-value">{{ lowRiskPercent }}%</div>
          </div>
        </div>
      </div>
      <div ref="riskChartRef" class="risk-chart"></div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="Search by WO #, asset, or prediction..." size="default" style="width: 260px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-select v-model="riskFilter" placeholder="Risk Level" size="default" style="width: 130px" clearable>
          <el-option label="All Risks" value="all" />
          <el-option label="High Risk" value="high" />
          <el-option label="Medium Risk" value="medium" />
          <el-option label="Low Risk" value="low" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" size="default" style="width: 130px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Pending Review" value="pending" />
          <el-option label="Approved" value="approved" />
          <el-option label="In Progress" value="in_progress" />
          <el-option label="Completed" value="completed" />
        </el-select>
        <el-select v-model="assetTypeFilter" placeholder="Asset Type" size="default" style="width: 140px" clearable>
          <el-option label="All Assets" value="all" />
          <el-option label="UPS" value="UPS" />
          <el-option label="HVAC" value="HVAC" />
          <el-option label="CRAC" value="CRAC" />
          <el-option label="PDU" value="PDU" />
          <el-option label="Chiller" value="Chiller" />
        </el-select>
      </div>
    </div>

    <!-- Predictive Work Orders Table -->
    <div class="card table-card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><List /></el-icon>
          AI-Generated Predictive Work Orders
        </div>
        <div class="table-info">
          Showing {{ paginatedOrders.length }} of {{ filteredOrders.length }} predictions
        </div>
      </div>
      <el-table :data="paginatedOrders" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="woNumber" label="WO #" width="120" sortable />
        <el-table-column prop="predictionTitle" label="Prediction Title" min-width="200" />
        <el-table-column prop="assetName" label="Asset" width="140" />
        <el-table-column prop="assetType" label="Asset Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getAssetTypeTag(row.assetType)" size="small">{{ row.assetType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="riskLevel" label="Risk Level" width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTag(row.riskLevel)" size="small">{{ getRiskText(row.riskLevel) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="Confidence" width="110" sortable>
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :color="getConfidenceColor(row.confidence)" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="rul" label="RUL (days)" width="100" sortable>
          <template #default="{ row }">
            <span :class="{ 'critical': row.rul < 7, 'warning': row.rul < 30 }">{{ row.rul }} days</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="detectedDate" label="Detected" width="110" sortable />
        <el-table-column prop="suggestedDate" label="Suggested By" width="110" sortable />
        <el-table-column label="Actions" fixed="right" width="160">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewPrediction(row)">
              <el-icon><View /></el-icon>
              Details
            </el-button>
            <el-button type="success" link size="small" @click="approveOrder(row)" v-if="row.status === 'pending'">
              <el-icon><CircleCheck /></el-icon>
              Approve
            </el-button>
            <el-dropdown @command="(cmd) => handleAction(cmd, row)">
              <el-button type="info" link size="small">
                More <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="schedule">Schedule Work</el-dropdown-item>
                  <el-dropdown-item command="dismiss">Dismiss</el-dropdown-item>
                  <el-dropdown-item command="feedback">Provide Feedback</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
      <div class="card-footer">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="filteredOrders.length"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handlePageSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- Failure Mode Analysis -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><DataAnalysis /></el-icon>
          Top Failure Modes (AI Analysis)
        </div>
      </div>
      <div class="failure-modes">
        <div v-for="mode in failureModes" :key="mode.name" class="failure-mode">
          <div class="mode-info">
            <span class="mode-name">{{ mode.name }}</span>
            <span class="mode-count">{{ mode.count }} predictions</span>
          </div>
          <div class="mode-bar">
            <div class="mode-bar-track">
              <div class="mode-bar-fill" :style="{ width: mode.percent + '%', background: mode.color }"></div>
            </div>
          </div>
          <div class="mode-actions">
            <el-button size="small" type="primary" link @click="viewFailureMode(mode)">Analyze</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Prediction Confidence Trend -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Prediction Confidence Trend (Last 30 Days)
        </div>
        <el-radio-group v-model="confidencePeriod" size="small">
          <el-radio-button label="week">Weekly</el-radio-button>
          <el-radio-button label="month">Monthly</el-radio-button>
        </el-radio-group>
      </div>
      <div ref="confidenceChartRef" class="chart-container"></div>
    </div>

    <!-- Prediction Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`AI Prediction #${selectedOrder?.woNumber}`" width="700px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="WO Number">{{ selectedOrder.woNumber }}</el-descriptions-item>
        <el-descriptions-item label="Risk Level">
          <el-tag :type="getRiskTag(selectedOrder.riskLevel)">{{ getRiskText(selectedOrder.riskLevel) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Prediction Title" :span="2">{{ selectedOrder.predictionTitle }}</el-descriptions-item>
        <el-descriptions-item label="Asset">{{ selectedOrder.assetName }}</el-descriptions-item>
        <el-descriptions-item label="Asset Type">{{ selectedOrder.assetType }}</el-descriptions-item>
        <el-descriptions-item label="Confidence">{{ selectedOrder.confidence }}%</el-descriptions-item>
        <el-descriptions-item label="RUL">{{ selectedOrder.rul }} days</el-descriptions-item>
        <el-descriptions-item label="Detected Date">{{ selectedOrder.detectedDate }}</el-descriptions-item>
        <el-descriptions-item label="Suggested By Date">{{ selectedOrder.suggestedDate }}</el-descriptions-item>
        <el-descriptions-item label="Status">{{ getStatusText(selectedOrder.status) }}</el-descriptions-item>
        <el-descriptions-item label="Failure Mode" :span="2">{{ selectedOrder.failureMode }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        <el-descriptions-item label="Recommended Action" :span="2">{{ selectedOrder.recommendedAction }}</el-descriptions-item>
        <el-descriptions-item label="Supporting Data" :span="2">
          <ul class="supporting-data">
            <li v-for="(data, idx) in selectedOrder.supportingData" :key="idx">{{ data }}</li>
          </ul>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="approveOrder(selectedOrder)" v-if="selectedOrder?.status === 'pending'">
          Approve & Create Work Order
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch  } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Refresh, DataAnalysis, TrendCharts, Search, List, View, CircleCheck, ArrowDown, Cpu, DataLine, Money } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading AI prediction models...',
  'Analyzing asset health data...',
  'Calculating remaining useful life...',
  'Almost ready...'
]

// ==================== Data State ====================
const searchText = ref('')
const riskFilter = ref('all')
const statusFilter = ref('all')
const assetTypeFilter = ref('all')
const confidencePeriod = ref('week')
const detailDialogVisible = ref(false)
const selectedOrder = ref<any>(null)

const pagination = ref({ page: 1, pageSize: 15 })

// AI Summary Stats
const modelAccuracy = ref(94.2)
const accuracyImprovement = ref(3.5)
const predictionsGenerated = ref(156)
const predictionsGrowth = ref(12)
const rulAccuracy = ref(87.5)
const rulImprovement = ref(5.2)
const costAvoided = ref(128)

// Risk counts
const highRiskCount = ref(8)
const mediumRiskCount = ref(12)
const lowRiskCount = ref(18)
const totalOrders = computed(() => highRiskCount.value + mediumRiskCount.value + lowRiskCount.value)
const pendingCount = ref(15)
const highRiskPercent = computed(() => Math.round((highRiskCount.value / totalOrders.value) * 100))
const mediumRiskPercent = computed(() => Math.round((mediumRiskCount.value / totalOrders.value) * 100))
const lowRiskPercent = computed(() => Math.round((lowRiskCount.value / totalOrders.value) * 100))

// Predictive Order Interface
interface PredictiveOrder {
  id: number
  woNumber: string
  predictionTitle: string
  assetName: string
  assetType: string
  riskLevel: string
  confidence: number
  rul: number
  status: string
  detectedDate: string
  suggestedDate: string
  failureMode: string
  description: string
  recommendedAction: string
  supportingData: string[]
}

// Mock Predictive Work Orders Data
const workOrders = ref<PredictiveOrder[]>([
  { id: 1, woNumber: 'AI-001', predictionTitle: 'UPS Battery End of Life Predicted', assetName: 'UPS-01', assetType: 'UPS', riskLevel: 'high', confidence: 92, rul: 5, status: 'pending', detectedDate: '2024-06-01', suggestedDate: '2024-06-06', failureMode: 'Capacity Degradation', description: 'Battery capacity has degraded to 65% of nominal. AI model predicts failure within 5 days based on degradation trend.', recommendedAction: 'Schedule battery replacement immediately. Order replacement batteries.', supportingData: ['Capacity trend: 98% → 85% → 72% → 65% over 90 days', 'Internal resistance increased by 35%', 'Temperature history within normal range'] },
  { id: 2, woNumber: 'AI-002', predictionTitle: 'CRAC Compressor Failure Risk', assetName: 'CRAC-01', assetType: 'CRAC', riskLevel: 'high', confidence: 88, rul: 8, status: 'pending', detectedDate: '2024-06-02', suggestedDate: '2024-06-10', failureMode: 'Compressor Wear', description: 'Vibration analysis indicates bearing wear. Compressor current draw increased by 15%.', recommendedAction: 'Schedule compressor inspection and bearing replacement.', supportingData: ['Vibration increased from 2.1 to 4.8 mm/s', 'Current draw: +15%', 'Runtime: 28,000 hours'] },
  { id: 3, woNumber: 'AI-003', predictionTitle: 'Chiller Efficiency Degradation', assetName: 'Chiller-01', assetType: 'Chiller', riskLevel: 'medium', confidence: 78, rul: 21, status: 'approved', detectedDate: '2024-05-28', suggestedDate: '2024-06-18', failureMode: 'Heat Exchanger Fouling', description: 'Approach temperature increased by 3°C. AI predicts 15% efficiency loss within 3 weeks.', recommendedAction: 'Schedule heat exchanger cleaning and water treatment review.', supportingData: ['Approach temperature: 2.5°C → 5.5°C', 'kW/ton increased by 12%', 'Head pressure elevated'] },
  { id: 4, woNumber: 'AI-004', predictionTitle: 'PDU Fan Bearing Failure', assetName: 'PDU-A01', assetType: 'PDU', riskLevel: 'high', confidence: 85, rul: 3, status: 'in_progress', detectedDate: '2024-06-03', suggestedDate: '2024-06-06', failureMode: 'Bearing Wear', description: 'Fan RPM fluctuations detected. Acoustic analysis indicates bearing wear.', recommendedAction: 'Replace cooling fan assembly.', supportingData: ['RPM variation: ±8%', 'Noise level: increased 12dB', 'Bearing temperature: +8°C'] },
  { id: 5, woNumber: 'AI-005', predictionTitle: 'UPS Capacitor Aging', assetName: 'UPS-02', assetType: 'UPS', riskLevel: 'medium', confidence: 82, rul: 35, status: 'pending', detectedDate: '2024-05-25', suggestedDate: '2024-06-29', failureMode: 'Capacitor Degradation', description: 'ESR increased on DC link capacitors. Ripple voltage above threshold.', recommendedAction: 'Monitor closely. Plan capacitor replacement in next maintenance window.', supportingData: ['ESR: +25% from baseline', 'Ripple voltage: +18%', 'Operating hours: 42,000'] },
  { id: 6, woNumber: 'AI-006', predictionTitle: 'Cooling Tower Motor Imbalance', assetName: 'CT-01', assetType: 'HVAC', riskLevel: 'low', confidence: 68, rul: 55, status: 'completed', detectedDate: '2024-05-20', suggestedDate: '2024-07-14', failureMode: 'Mechanical Imbalance', description: 'Slight motor vibration detected. AI predicts gradual degradation.', recommendedAction: 'Inspect and balance fan assembly during next PM.', supportingData: ['Vibration: 3.2 mm/s (threshold: 5.0)', 'Bearings: normal', 'Motor current: stable'] },
  { id: 7, woNumber: 'AI-007', predictionTitle: 'Generator Fuel System Issue', assetName: 'GEN-01', assetType: 'Generator', riskLevel: 'high', confidence: 91, rul: 12, status: 'approved', detectedDate: '2024-06-01', suggestedDate: '2024-06-13', failureMode: 'Fuel Contamination', description: 'Fuel quality sensor detected water content above limit.', recommendedAction: 'Test fuel quality and perform fuel polishing.', supportingData: ['Water content: 250 ppm (limit: 200)', 'Fuel age: 180 days', 'Recent temperature fluctuations'] }
])

const filteredOrders = computed(() => {
  let filtered = workOrders.value

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(o =>
        o.woNumber.toLowerCase().includes(search) ||
        o.predictionTitle.toLowerCase().includes(search) ||
        o.assetName.toLowerCase().includes(search)
    )
  }

  if (riskFilter.value !== 'all') {
    filtered = filtered.filter(o => o.riskLevel === riskFilter.value)
  }

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(o => o.status === statusFilter.value)
  }

  if (assetTypeFilter.value !== 'all') {
    filtered = filtered.filter(o => o.assetType === assetTypeFilter.value)
  }

  return filtered
})

const paginatedOrders = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize
  return filteredOrders.value.slice(start, start + pagination.value.pageSize)
})

// Failure Modes Data
const failureModes = ref([
  { name: 'Battery Degradation', count: 12, percent: 32, color: '#f56c6c' },
  { name: 'Bearing Wear', count: 8, percent: 21, color: '#e6a23c' },
  { name: 'Compressor Failure', count: 6, percent: 16, color: '#f97316' },
  { name: 'Capacitor Aging', count: 5, percent: 13, color: '#409eff' },
  { name: 'Fan Failure', count: 4, percent: 11, color: '#67c23a' },
  { name: 'Other', count: 3, percent: 7, color: '#909399' }
])

// Confidence trend data
const weeklyConfidenceData = ref<number[]>([88, 89, 90, 92, 91, 93, 94])
const monthlyConfidenceData = ref<number[]>([85, 86, 88, 89, 90, 92, 91, 92, 93, 94, 94, 95])
const weekLabels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7']
const monthLabels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

// Helper functions
const getRiskTag = (risk: string) => {
  const map: Record<string, string> = { high: 'danger', medium: 'warning', low: 'info' }
  return map[risk] || 'info'
}

const getRiskText = (risk: string) => {
  const map: Record<string, string> = { high: 'High', medium: 'Medium', low: 'Low' }
  return map[risk] || risk
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = { pending: 'warning', approved: 'primary', in_progress: 'warning', completed: 'success' }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = { pending: 'Pending Review', approved: 'Approved', in_progress: 'In Progress', completed: 'Completed' }
  return map[status] || status
}

const getAssetTypeTag = (type: string) => {
  const map: Record<string, string> = { UPS: 'danger', HVAC: 'warning', CRAC: 'warning', PDU: 'success', Chiller: 'primary', Generator: 'danger' }
  return map[type] || 'info'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 85) return '#67c23a'
  if (confidence >= 70) return '#e6a23c'
  return '#f56c6c'
}

// Actions
const viewPrediction = (order: PredictiveOrder) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

const approveOrder = (order: PredictiveOrder) => {
  ElMessageBox.confirm(`Approve prediction "${order.predictionTitle}" and create work order?`, 'Confirm', {
    confirmButtonText: 'Approve & Create',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    order.status = 'approved'
    ElMessage.success(`Work order created from AI prediction`)
  }).catch(() => {})
}

const runPredictionModel = () => {
  ElMessage.success('AI prediction model executed successfully')
}

const viewFailureMode = (mode: any) => {
  ElMessage.info(`Analyzing failure mode: ${mode.name}`)
}

const handleAction = (command: string, order: PredictiveOrder) => {
  if (command === 'schedule') {
    ElMessage.info(`Schedule work for ${order.woNumber}`)
  } else if (command === 'dismiss') {
    ElMessageBox.confirm(`Dismiss prediction "${order.predictionTitle}"?`, 'Confirm', {
      confirmButtonText: 'Dismiss',
      cancelButtonText: 'Cancel',
      type: 'warning'
    }).then(() => {
      ElMessage.success(`Prediction dismissed`)
    }).catch(() => {})
  } else if (command === 'feedback') {
    ElMessage.info(`Provide feedback on prediction accuracy`)
  }
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  tableLoading.value = false
  refreshing.value = false
  ElMessage.success('AI predictions refreshed')
}

const handlePageSizeChange = () => { pagination.value.page = 1 }
const handlePageChange = () => {}

// ==================== Chart Functions ====================
const riskChartRef = ref<HTMLElement>()
const confidenceChartRef = ref<HTMLElement>()
let riskChart: echarts.ECharts | null = null
let confidenceChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    // Risk Distribution Pie Chart
    if (riskChartRef.value) {
      if (riskChart) riskChart.dispose()
      riskChart = echarts.init(riskChartRef.value)
      riskChart.setOption({
        backgroundColor: 'transparent',
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left', textStyle: { color: '#606266' } },
        series: [{
          type: 'pie', radius: '55%', center: ['50%', '50%'],
          data: [
            { value: highRiskCount.value, name: 'High Risk', itemStyle: { color: '#f56c6c' } },
            { value: mediumRiskCount.value, name: 'Medium Risk', itemStyle: { color: '#e6a23c' } },
            { value: lowRiskCount.value, name: 'Low Risk', itemStyle: { color: '#67c23a' } }
          ],
          label: { show: true, formatter: '{b}: {d}%', color: '#606266' }
        }]
      })
    }

    // Confidence Trend Chart
    if (confidenceChartRef.value) {
      if (confidenceChart) confidenceChart.dispose()
      confidenceChart = echarts.init(confidenceChartRef.value)
      updateConfidenceChart()
    }

    window.addEventListener('resize', () => {
      riskChart?.resize()
      confidenceChart?.resize()
    })
  })
}

const updateConfidenceChart = () => {
  if (!confidenceChart) return

  const isWeekly = confidencePeriod.value === 'week'
  const data = isWeekly ? weeklyConfidenceData.value : monthlyConfidenceData.value
  const labels = isWeekly ? weekLabels : monthLabels

  confidenceChart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '8%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#606266' }, axisLine: { lineStyle: { color: '#dcdfe6' } } },
    yAxis: { type: 'value', name: 'Confidence (%)', min: 70, max: 100, axisLabel: { color: '#606266' }, splitLine: { lineStyle: { color: '#ebeef5' } } },
    series: [{
      type: 'line', data: data, smooth: true,
      lineStyle: { color: '#409eff', width: 2 },
      areaStyle: { opacity: 0.1, color: '#409eff' },
      symbol: 'circle', symbolSize: 6, itemStyle: { color: '#409eff' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isPageLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initCharts()
        }, 100)
      })
    }, 500)
  }, 2500)
}

watch(confidencePeriod, () => {
  updateConfidenceChart()
})

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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
.workorders-dashboard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f5 100%);
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  background: white;
  padding: 16px 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1f2f3d;
  margin: 0;
}

.title-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.predictive-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-stats {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.stat-badge.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* AI Summary Cards */
.ai-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.summary-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s;
}

.summary-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.summary-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #667eea;
}

.summary-content {
  flex: 1;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.summary-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
}

.summary-trend {
  font-size: 11px;
  margin-top: 4px;
}

.summary-trend.up { color: #67c23a; }

/* Risk Distribution */
.risk-distribution {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.risk-section {
  flex: 1;
}

.risk-header {
  margin-bottom: 16px;
}

.risk-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
  display: block;
}

.risk-subtitle {
  font-size: 12px;
  color: #909399;
}

.risk-bars {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.risk-bar-item {
  width: 100%;
}

.risk-bar-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
}

.risk-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.risk-dot.critical { background: #f56c6c; }
.risk-dot.warning { background: #e6a23c; }
.risk-dot.normal { background: #67c23a; }

.risk-count {
  margin-left: auto;
  font-weight: 600;
  color: #1f2f3d;
}

.risk-bar-track {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.risk-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.risk-bar-fill.critical { background: #f56c6c; }
.risk-bar-fill.warning { background: #e6a23c; }
.risk-bar-fill.normal { background: #67c23a; }

.risk-bar-value {
  text-align: right;
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.risk-chart {
  width: 280px;
  height: 200px;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* Card */
.card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.table-info {
  font-size: 13px;
  color: #909399;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  background: #fafafa;
}

.table-card {
  overflow-x: auto;
}

/* Failure Modes */
.failure-modes {
  padding: 16px;
}

.failure-mode {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.mode-info {
  width: 200px;
  display: flex;
  justify-content: space-between;
}

.mode-name {
  font-weight: 500;
  color: #1f2f3d;
}

.mode-count {
  font-size: 12px;
  color: #909399;
}

.mode-bar {
  flex: 1;
}

.mode-bar-track {
  height: 8px;
  background: #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.mode-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

/* Chart */
.chart-container {
  width: 100%;
  height: 320px;
  padding: 16px;
}

/* Supporting Data */
.supporting-data {
  margin: 0;
  padding-left: 20px;
}

.supporting-data li {
  font-size: 12px;
  color: #606266;
  margin: 4px 0;
}

/* Critical/ Warning text */
.critical {
  color: #f56c6c;
  font-weight: 600;
}

.warning {
  color: #e6a23c;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 1200px) {
  .ai-summary {
    grid-template-columns: repeat(2, 1fr);
  }
  .risk-distribution {
    flex-direction: column;
  }
  .risk-chart {
    width: 100%;
    height: 250px;
  }
}

@media (max-width: 900px) {
  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-group .el-input,
  .filter-group .el-select {
    width: 100% !important;
  }
  .failure-mode {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .mode-info {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .workorders-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .ai-summary {
    grid-template-columns: 1fr;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-table) {
  background: transparent;
  --el-table-header-bg-color: #fafafa;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-border-color: #e4e7ed;
}

:deep(.el-table th.el-table__cell) {
  background-color: #fafafa;
  color: #1f2f3d;
}

:deep(.el-table td.el-table__cell) {
  color: #606266;
}

:deep(.el-pagination) {
  --el-pagination-bg-color: transparent;
  --el-pagination-button-bg-color: #f5f7fa;
  --el-pagination-hover-color: #409eff;
}

:deep(.el-dialog) {
  background: #ffffff;
  border-radius: 12px;
}

:deep(.el-dialog__title) {
  color: #1f2f3d;
}

:deep(.el-progress-bar__outer) {
  background-color: #e4e7ed;
}
</style>