<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Maintenance Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Maintenance Performance Intelligence</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="maintenance-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          Maintenance Analytics
        </h1>
        <div class="page-subtitle">Monitor maintenance performance and KPI metrics</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="generateReport">
          <el-icon><Document /></el-icon> Generate Report
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Tickets /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalOrders }}</div>
          <div class="stat-label">Total Work Orders</div>
          <div class="stat-trend up">↑ {{ stats.orderGrowth }}% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.completedOrders }}</div>
          <div class="stat-label">Completed</div>
          <div class="stat-trend up">↑ {{ stats.completionGrowth }}% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Loading /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.inProgressOrders }}</div>
          <div class="stat-label">In Progress</div>
          <div class="stat-trend down">↓ {{ stats.inProgressChange }}% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.overdueOrders }}</div>
          <div class="stat-label">Overdue</div>
          <div class="stat-trend up">↑ {{ stats.overdueGrowth }}% vs last month</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">MTTR</div>
        <div class="metric-value">{{ metrics.mttr }} <span class="metric-unit">hours</span></div>
        <div class="metric-trend" :class="metrics.mttrTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.mttrTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.mttrTrend) }}% vs target
        </div>
        <div class="metric-target">Target: ≤ {{ metrics.mttrTarget }} hours</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">MTBF</div>
        <div class="metric-value">{{ metrics.mtbf }} <span class="metric-unit">days</span></div>
        <div class="metric-trend" :class="metrics.mtbfTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.mtbfTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.mtbfTrend) }}% vs target
        </div>
        <div class="metric-target">Target: ≥ {{ metrics.mtbfTarget }} days</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">On-Time Completion</div>
        <div class="metric-value">{{ metrics.onTimeRate }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.onTimeTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.onTimeTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.onTimeTrend) }}% vs last month
        </div>
        <div class="metric-target">Target: ≥ {{ metrics.onTimeTarget }}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Avg Response Time</div>
        <div class="metric-value">{{ metrics.avgResponseTime }} <span class="metric-unit">min</span></div>
        <div class="metric-trend" :class="metrics.responseTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.responseTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.responseTrend) }}% vs target
        </div>
        <div class="metric-target">Target: ≤ {{ metrics.responseTarget }} min</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Work Order Trends</span>
          <el-select v-model="trendPeriod" size="small" style="width: 100px" @change="updateTrendChart">
            <el-option label="Last 6 Months" value="6" />
            <el-option label="Last 12 Months" value="12" />
          </el-select>
        </div>
        <div class="chart-container" ref="trendChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Work Order by Type</span>
          <span class="chart-subtitle">Current month distribution</span>
        </div>
        <div class="chart-container" ref="typeChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Vendor Performance</span>
          <span class="chart-subtitle">Completion rate by vendor</span>
        </div>
        <div class="chart-container" ref="vendorChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Top Failure Assets</span>
          <span class="chart-subtitle">Most frequent failure assets</span>
        </div>
        <div class="chart-container" ref="assetChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by order ID or asset..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="typeFilter" placeholder="Order Type" clearable style="width: 140px">
          <el-option label="Corrective" value="corrective" />
          <el-option label="Preventive" value="preventive" />
          <el-option label="Predictive" value="predictive" />
          <el-option label="Emergency" value="emergency" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Completed" value="completed" />
          <el-option label="In Progress" value="in-progress" />
          <el-option label="Pending" value="pending" />
          <el-option label="Overdue" value="overdue" />
        </el-select>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
      </div>
      <div class="filter-right">
        <span class="filter-label">Overall Performance Score: </span>
        <el-progress :percentage="performanceScore" :stroke-width="8" :color="getScoreColor(performanceScore)" style="width: 150px" />
      </div>
    </div>

    <!-- Work Orders Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Recent Work Orders</span>
        <el-button size="small" @click="viewAllOrders">View All Orders →</el-button>
      </div>
      <el-table :data="paginatedOrders" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="Order ID" width="120" />
        <el-table-column prop="title" label="Title" min-width="200" />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ getTypeText(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="asset" label="Asset" width="180" />
        <el-table-column prop="vendor" label="Vendor" width="150" />
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="completion" label="Completion" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.completion" :stroke-width="6" :color="getProgressColor(row.completion)" />
          </template>
        </el-table-column>
        <el-table-column prop="dueDate" label="Due Date" width="120" />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewOrderDetail(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Order Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Work Order: ${selectedOrder?.id}`" width="800px">
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Order Title">{{ selectedOrder.title }}</el-descriptions-item>
          <el-descriptions-item label="Order Type">
            <el-tag :type="getTypeTagType(selectedOrder.type)" size="small">{{ getTypeText(selectedOrder.type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Asset">{{ selectedOrder.asset }}</el-descriptions-item>
          <el-descriptions-item label="Vendor">{{ selectedOrder.vendor }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTagType(selectedOrder.priority)" size="small">{{ selectedOrder.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedOrder.status)" size="small">{{ getStatusText(selectedOrder.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Created Date">{{ selectedOrder.createdDate }}</el-descriptions-item>
          <el-descriptions-item label="Due Date">{{ selectedOrder.dueDate }}</el-descriptions-item>
          <el-descriptions-item label="Completed Date">{{ selectedOrder.completedDate || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ selectedOrder.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        </el-descriptions>

        <!-- Timeline -->
        <div class="timeline-section">
          <div class="section-title">Activity Timeline</div>
          <el-timeline>
            <el-timeline-item
                v-for="activity in selectedOrder.timeline"
                :key="activity.id"
                :timestamp="activity.time"
                :type="activity.type"
                placement="top"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="updateOrderStatus(selectedOrder)">Update Status</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts, Document, Download, Refresh, Tickets, CircleCheck,
  Loading, Warning, Search, Plus
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading maintenance data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading maintenance data...',
  'Fetching work orders...',
  'Calculating KPI metrics...',
  'Loading vendor performance...',
  'Almost ready...'
]

// ==================== Types ====================
interface WorkOrder {
  id: string
  title: string
  type: 'corrective' | 'preventive' | 'predictive' | 'emergency'
  asset: string
  vendor: string
  priority: 'High' | 'Medium' | 'Low'
  status: 'completed' | 'in-progress' | 'pending' | 'overdue'
  completion: number
  dueDate: string
  createdDate: string
  completedDate: string | null
  assignedTo: string
  description: string
  timeline: Activity[]
}

interface Activity {
  id: number
  time: string
  content: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}

// ==================== Mock Data ====================
const workOrders = ref<WorkOrder[]>([
  {
    id: 'WO-001', title: 'UPS Battery Replacement', type: 'corrective', asset: 'UPS-01', vendor: 'Schneider Electric',
    priority: 'High', status: 'completed', completion: 100, dueDate: '2024-05-20', createdDate: '2024-05-15',
    completedDate: '2024-05-19', assignedTo: 'John Tan', description: 'Replace aging UPS batteries that show signs of degradation.',
    timeline: [
      { id: 1, time: '2024-05-15 09:00', content: 'Work order created', type: 'info' },
      { id: 2, time: '2024-05-15 10:30', content: 'Assigned to John Tan', type: 'primary' },
      { id: 3, time: '2024-05-16 14:00', content: 'Parts ordered', type: 'warning' },
      { id: 4, time: '2024-05-19 11:00', content: 'Batteries replaced successfully', type: 'success' },
      { id: 5, time: '2024-05-19 15:00', content: 'Work order completed', type: 'success' }
    ]
  },
  {
    id: 'WO-002', title: 'CRAC Unit Cooling Issue', type: 'emergency', asset: 'CRAC-03', vendor: 'Vertiv Singapore',
    priority: 'High', status: 'in-progress', completion: 60, dueDate: '2024-06-01', createdDate: '2024-05-28',
    completedDate: null, assignedTo: 'Mike Chen', description: 'CRAC unit not cooling properly, temperature rising in data center.',
    timeline: [
      { id: 1, time: '2024-05-28 08:30', content: 'Emergency work order created', type: 'danger' },
      { id: 2, time: '2024-05-28 09:15', content: 'Assigned to Mike Chen', type: 'primary' },
      { id: 3, time: '2024-05-28 11:00', content: 'Initial diagnosis completed - compressor issue', type: 'warning' },
      { id: 4, time: '2024-05-29 10:00', content: 'Parts on order', type: 'info' }
    ]
  },
  {
    id: 'WO-003', title: 'Generator Monthly Test', type: 'preventive', asset: 'GEN-01', vendor: 'Caterpillar Singapore',
    priority: 'Medium', status: 'completed', completion: 100, dueDate: '2024-05-25', createdDate: '2024-05-20',
    completedDate: '2024-05-24', assignedTo: 'Ahmad Ibrahim', description: 'Monthly generator load bank test and inspection.',
    timeline: [
      { id: 1, time: '2024-05-20 09:00', content: 'Preventive maintenance scheduled', type: 'info' },
      { id: 2, time: '2024-05-24 13:00', content: 'Generator test completed - all parameters normal', type: 'success' }
    ]
  },
  {
    id: 'WO-004', title: 'Chiller Vibration Analysis', type: 'predictive', asset: 'Chiller-02', vendor: 'Trane Singapore',
    priority: 'Medium', status: 'completed', completion: 100, dueDate: '2024-05-18', createdDate: '2024-05-10',
    completedDate: '2024-05-17', assignedTo: 'Lim Wei Ming', description: 'Predictive maintenance vibration analysis on Chiller #2.',
    timeline: [
      { id: 1, time: '2024-05-10 10:00', content: 'Predictive maintenance triggered by IoT sensors', type: 'info' },
      { id: 2, time: '2024-05-15 09:00', content: 'Vibration analysis performed', type: 'primary' },
      { id: 3, time: '2024-05-17 14:00', content: 'Analysis complete - minor bearing wear detected', type: 'warning' }
    ]
  },
  {
    id: 'WO-005', title: 'Electrical Panel Inspection', type: 'preventive', asset: 'Panel-P1', vendor: 'ABB Singapore',
    priority: 'Low', status: 'pending', completion: 0, dueDate: '2024-06-10', createdDate: '2024-05-25',
    completedDate: null, assignedTo: 'Sarah Koh', description: 'Quarterly electrical panel thermal inspection.',
    timeline: [
      { id: 1, time: '2024-05-25 11:00', content: 'Work order created', type: 'info' },
      { id: 2, time: '2024-05-26 09:00', content: 'Assigned to Sarah Koh', type: 'primary' }
    ]
  },
  {
    id: 'WO-006', title: 'UPS Firmware Update', type: 'corrective', asset: 'UPS-02', vendor: 'Eaton Singapore',
    priority: 'High', status: 'overdue', completion: 30, dueDate: '2024-05-15', createdDate: '2024-05-01',
    completedDate: null, assignedTo: 'John Tan', description: 'Firmware update to address known bug.',
    timeline: [
      { id: 1, time: '2024-05-01 14:00', content: 'Work order created', type: 'info' },
      { id: 2, time: '2024-05-02 10:00', content: 'Assigned to John Tan', type: 'primary' },
      { id: 3, time: '2024-05-10 09:00', content: 'Firmware downloaded, awaiting maintenance window', type: 'warning' }
    ]
  },
  {
    id: 'WO-007', title: 'Cooling Tower Cleaning', type: 'preventive', asset: 'CT-01', vendor: 'Johnson Controls',
    priority: 'Medium', status: 'in-progress', completion: 45, dueDate: '2024-06-05', createdDate: '2024-05-22',
    completedDate: null, assignedTo: 'Mike Chen', description: 'Bi-annual cooling tower basin and fill cleaning.',
    timeline: [
      { id: 1, time: '2024-05-22 08:00', content: 'Preventive maintenance scheduled', type: 'info' },
      { id: 2, time: '2024-05-28 09:00', content: 'Cleaning started', type: 'primary' }
    ]
  },
  {
    id: 'WO-008', title: 'Fire Alarm System Test', type: 'preventive', asset: 'FirePanel-01', vendor: 'Honeywell',
    priority: 'High', status: 'completed', completion: 100, dueDate: '2024-05-12', createdDate: '2024-05-05',
    completedDate: '2024-05-11', assignedTo: 'Ahmad Ibrahim', description: 'Monthly fire alarm system testing.',
    timeline: [
      { id: 1, time: '2024-05-05 12:00', content: 'Work order created', type: 'info' },
      { id: 2, time: '2024-05-11 14:00', content: 'Testing completed - all systems functional', type: 'success' }
    ]
  },
  {
    id: 'WO-009', title: 'Leak Detection Sensor Repair', type: 'corrective', asset: 'LeakSensor-05', vendor: 'Siemens Singapore',
    priority: 'High', status: 'overdue', completion: 15, dueDate: '2024-05-10', createdDate: '2024-05-03',
    completedDate: null, assignedTo: 'Lim Wei Ming', description: 'Faulty leak detection sensor in data center.',
    timeline: [
      { id: 1, time: '2024-05-03 15:00', content: 'Work order created', type: 'info' },
      { id: 2, time: '2024-05-04 10:00', content: 'Assigned to Lim Wei Ming', type: 'primary' },
      { id: 3, time: '2024-05-08 09:00', content: 'Parts ordered - awaiting delivery', type: 'warning' }
    ]
  },
  {
    id: 'WO-010', title: 'HVAC Filter Replacement', type: 'preventive', asset: 'AHU-03', vendor: 'Daikin Singapore',
    priority: 'Low', status: 'completed', completion: 100, dueDate: '2024-05-30', createdDate: '2024-05-18',
    completedDate: '2024-05-29', assignedTo: 'Sarah Koh', description: 'Monthly HVAC air filter replacement.',
    timeline: [
      { id: 1, time: '2024-05-18 09:00', content: 'Preventive maintenance scheduled', type: 'info' },
      { id: 2, time: '2024-05-29 11:00', content: 'Filters replaced', type: 'success' }
    ]
  }
])

// ==================== State ====================
const searchText = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const trendPeriod = ref('6')
const detailDialogVisible = ref(false)
const selectedOrder = ref<WorkOrder | null>(null)

// Chart refs
let trendChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null
let vendorChart: echarts.ECharts | null = null
let assetChart: echarts.ECharts | null = null

const trendChartEl = ref<HTMLElement | null>(null)
const typeChartEl = ref<HTMLElement | null>(null)
const vendorChartEl = ref<HTMLElement | null>(null)
const assetChartEl = ref<HTMLElement | null>(null)

// ==================== Computed Stats ====================
const stats = computed(() => {
  const totalOrders = workOrders.value.length
  const completedOrders = workOrders.value.filter(o => o.status === 'completed').length
  const inProgressOrders = workOrders.value.filter(o => o.status === 'in-progress').length
  const overdueOrders = workOrders.value.filter(o => o.status === 'overdue').length

  return {
    totalOrders,
    completedOrders,
    inProgressOrders,
    overdueOrders,
    orderGrowth: 12.5,
    completionGrowth: 8.3,
    inProgressChange: 5.2,
    overdueGrowth: 3.1
  }
})

const metrics = computed(() => {
  // 计算 MTTR (平均修复时间) - 仅已完成工单
  const completedOrdersWithTime = workOrders.value.filter(o => o.status === 'completed' && o.completedDate)
  let totalResolutionHours = 0
  completedOrdersWithTime.forEach(order => {
    const created = new Date(order.createdDate)
    const completed = new Date(order.completedDate!)
    const hoursDiff = (completed.getTime() - created.getTime()) / (1000 * 60 * 60)
    totalResolutionHours += hoursDiff
  })
  const mttr = completedOrdersWithTime.length > 0 ? (totalResolutionHours / completedOrdersWithTime.length).toFixed(1) : '0'

  // MTBF (平均无故障时间) - 模拟数据
  const mtbf = 45.2
  const onTimeRate = Math.round((workOrders.value.filter(o => o.status === 'completed' && new Date(o.completedDate!) <= new Date(o.dueDate)).length / stats.value.completedOrders) * 100) || 0

  // 平均响应时间
  const avgResponseTime = 28

  return {
    mttr: parseFloat(mttr),
    mttrTarget: 4,
    mttrTrend: -8.5,
    mtbf: mtbf,
    mtbfTarget: 40,
    mtbfTrend: 13,
    onTimeRate,
    onTimeTarget: 90,
    onTimeTrend: 5,
    avgResponseTime,
    responseTarget: 30,
    responseTrend: -6.7
  }
})

const performanceScore = computed(() => {
  const onTimeScore = (metrics.value.onTimeRate / metrics.value.onTimeTarget) * 35
  const mttrScore = Math.max(0, (1 - metrics.value.mttr / metrics.value.mttrTarget)) * 35
  const mtbfScore = Math.min(35, (metrics.value.mtbf / metrics.value.mtbfTarget) * 35)
  return Math.min(100, Math.round(onTimeScore + mttrScore + mtbfScore))
})

// ==================== Filtered Data ====================
const filteredOrders = computed(() => {
  let filtered = [...workOrders.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(o =>
        o.id.toLowerCase().includes(search) ||
        o.title.toLowerCase().includes(search) ||
        o.asset.toLowerCase().includes(search)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(o => o.type === typeFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(o => o.status === statusFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const start = dateRange.value[0]
    const end = dateRange.value[1]
    filtered = filtered.filter(o => {
      const created = new Date(o.createdDate)
      return created >= start && created <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredOrders.value.length)

const paginatedOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredOrders.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getTypeText = (type: string): string => {
  const map: Record<string, string> = { corrective: 'Corrective', preventive: 'Preventive', predictive: 'Predictive', emergency: 'Emergency' }
  return map[type] || type
}

const getTypeTagType = (type: string): string => {
  const map: Record<string, string> = { corrective: 'warning', preventive: 'info', predictive: 'success', emergency: 'danger' }
  return map[type] || 'info'
}

const getPriorityTagType = (priority: string): string => {
  const map: Record<string, string> = { High: 'danger', Medium: 'warning', Low: 'info' }
  return map[priority] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { completed: 'Completed', 'in-progress': 'In Progress', pending: 'Pending', overdue: 'Overdue' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { completed: 'success', 'in-progress': 'warning', pending: 'info', overdue: 'danger' }
  return map[status] || 'info'
}

const getProgressColor = (progress: number): string => {
  if (progress >= 100) return '#22c55e'
  if (progress >= 70) return '#3b82f6'
  if (progress >= 30) return '#f59e0b'
  return '#ef4444'
}

const getScoreColor = (score: number): string => {
  if (score >= 80) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

// ==================== Chart Functions ====================
const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) trendChart.dispose()

  const months = trendPeriod.value === '6'
      ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
      : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  // 模拟月度工单数据
  const createdData = [24, 28, 32, 35, 38, 42]
  const completedData = [20, 24, 28, 30, 34, 38]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Created', 'Completed'], bottom: 0 },
    grid: { top: 40, left: 50, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Number of Orders' },
    series: [
      { name: 'Created', type: 'line', data: createdData, smooth: true, lineStyle: { color: '#3b82f6', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1 } },
      { name: 'Completed', type: 'line', data: completedData, smooth: true, lineStyle: { color: '#22c55e', width: 3 }, symbol: 'circle', symbolSize: 8, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initTypeChart = () => {
  if (!typeChartEl.value) return
  if (typeChart) typeChart.dispose()

  const typeCount = {
    corrective: workOrders.value.filter(o => o.type === 'corrective').length,
    preventive: workOrders.value.filter(o => o.type === 'preventive').length,
    predictive: workOrders.value.filter(o => o.type === 'predictive').length,
    emergency: workOrders.value.filter(o => o.type === 'emergency').length
  }

  typeChart = echarts.init(typeChartEl.value)
  typeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} orders)' },
    legend: { orient: 'vertical', left: 'left', data: ['Corrective', 'Preventive', 'Predictive', 'Emergency'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: typeCount.corrective, name: 'Corrective', itemStyle: { color: '#f59e0b' } },
        { value: typeCount.preventive, name: 'Preventive', itemStyle: { color: '#3b82f6' } },
        { value: typeCount.predictive, name: 'Predictive', itemStyle: { color: '#10b981' } },
        { value: typeCount.emergency, name: 'Emergency', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const initVendorChart = () => {
  if (!vendorChartEl.value) return
  if (vendorChart) vendorChart.dispose()

  const vendorMap = new Map<string, { total: number; completed: number }>()
  workOrders.value.forEach(order => {
    const existing = vendorMap.get(order.vendor) || { total: 0, completed: 0 }
    existing.total++
    if (order.status === 'completed') existing.completed++
    vendorMap.set(order.vendor, existing)
  })

  const vendors = Array.from(vendorMap.keys()).slice(0, 6)
  const completionRates = vendors.map(v => Math.round((vendorMap.get(v)!.completed / vendorMap.get(v)!.total) * 100))

  vendorChart = echarts.init(vendorChartEl.value)
  vendorChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Completion Rate: {c}%' },
    grid: { top: 30, left: 50, right: 20, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: vendors, axisLabel: { rotate: 30, fontSize: 10, interval: 0 } },
    yAxis: { type: 'value', name: 'Completion Rate (%)', max: 100 },
    series: [{
      type: 'bar',
      data: completionRates,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value >= 90) return '#22c55e'
          if (value >= 75) return '#3b82f6'
          if (value >= 60) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initAssetChart = () => {
  if (!assetChartEl.value) return
  if (assetChart) assetChart.dispose()

  const assetMap = new Map<string, number>()
  workOrders.value.forEach(order => {
    assetMap.set(order.asset, (assetMap.get(order.asset) || 0) + 1)
  })

  const sortedAssets = Array.from(assetMap.entries()).sort((a, b) => b[1] - a[1]).slice(0, 5)

  assetChart = echarts.init(assetChartEl.value)
  assetChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: '{b}<br/>Failure Count: {c}' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: sortedAssets.map(a => a[0]), axisLabel: { rotate: 20, fontSize: 11 } },
    yAxis: { type: 'value', name: 'Number of Failures' },
    series: [{
      type: 'bar',
      data: sortedAssets.map(a => a[1]),
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#f59e0b' },
      label: { show: true, position: 'top' }
    }]
  })
}

const updateTrendChart = () => {
  initTrendChart()
}

// ==================== Actions ====================
const viewOrderDetail = (order: WorkOrder) => {
  selectedOrder.value = order
  detailDialogVisible.value = true
}

const viewAllOrders = () => {
  ElMessage.info('Viewing all work orders')
}

const updateOrderStatus = (order: WorkOrder | null) => {
  if (!order) return
  ElMessageBox.prompt('Update order status', 'Status Update', {
    confirmButtonText: 'Update',
    cancelButtonText: 'Cancel',
    inputValue: order.status,
    inputType: 'select',
    inputOptions: {
      'pending': 'Pending',
      'in-progress': 'In Progress',
      'completed': 'Completed',
      'overdue': 'Overdue'
    }
  }).then(({ value }) => {
    if (value) {
      const index = workOrders.value.findIndex(o => o.id === order.id)
      if (index !== -1) {
        workOrders.value[index].status = value as any
        if (value === 'completed' && !workOrders.value[index].completedDate) {
          workOrders.value[index].completedDate = new Date().toISOString().slice(0, 10)
          workOrders.value[index].completion = 100
        }
        ElMessage.success(`Order ${order.id} status updated to ${value}`)
        refreshCharts()
      }
    }
  })
}

const generateReport = () => {
  ElMessage.success('Generating maintenance report...')
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting maintenance data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  refreshCharts()
  ElMessage.success('Data refreshed')
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initTypeChart()
    initVendorChart()
    initAssetChart()
  })
}

// ==================== Watch ====================
watch([searchText, typeFilter, statusFilter, dateRange], () => {
  currentPage.value = 1
})

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
      isLoaded.value = true
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', () => {
    trendChart?.resize()
    typeChart?.resize()
    vendorChart?.resize()
    assetChart?.resize()
  })
})
</script>

<style scoped>
* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ==================== Main Page ==================== */
.maintenance-analytics-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #22c55e; }
.stat-trend.down { color: #ef4444; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-target {
  font-size: 11px;
  color: #64748b;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 13px;
  color: #64748b;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Order Detail */
.order-detail {
  padding: 8px;
}

.timeline-section {
  margin-top: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  max-height: 500px;
  overflow-y: auto;
}
</style>