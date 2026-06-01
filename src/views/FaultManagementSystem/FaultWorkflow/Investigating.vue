<script setup lang="ts">
import { ref, onMounted, nextTick, computed, watch, onUnmounted } from 'vue'
import { Search, Document, User, CircleCheck, Check } from "@element-plus/icons-vue"
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// Mock statistics data
const stats = ref({
  new: 8,
  assigned: 12,
  investigating: 24,
  resolved: 31,
  closed: 156
})

// Mock investigating work orders data
const workOrders = ref([
  {
    id: 'WO-2024-001',
    title: 'AHU-03 Supply Air Temperature Fluctuation',
    deviceName: 'AHU-03',
    siteName: 'Data Center A',
    severity: 'Critical',
    investigator: 'John Zhang',
    startTime: '2024-01-15 09:30:00',
    description: 'AHU-03 supply air temperature fluctuated from 18°C to 26°C within 15 minutes, exceeding normal range',
    analysis: 'Preliminary diagnosis indicates temperature sensor drift or valve actuator failure'
  },
  {
    id: 'WO-2024-002',
    title: 'UPS-01 Persistent High Load',
    deviceName: 'UPS-01',
    siteName: 'Data Center B',
    severity: 'Warning',
    investigator: 'Sarah Li',
    startTime: '2024-01-15 10:15:00',
    description: 'UPS-01 load rate reached 85%, approaching warning threshold',
    analysis: 'Checking for new equipment connections, analyzing load distribution'
  },
  {
    id: 'WO-2024-003',
    title: 'Cooling Tower Fan Abnormal Noise',
    deviceName: 'CT-02',
    siteName: 'Central Plant',
    severity: 'Critical',
    investigator: 'Mike Wang',
    startTime: '2024-01-15 11:00:00',
    description: 'Cooling Tower CT-02 emits periodic metallic friction noise during operation',
    analysis: 'Possible bearing wear or fan blade imbalance, on-site acoustic inspection needed'
  },
  {
    id: 'WO-2024-004',
    title: 'Smoke Detector False Alarm',
    deviceName: 'Smoke Detector #B1-12',
    siteName: 'Office B1 Floor',
    severity: 'Minor',
    investigator: 'Emma Zhao',
    startTime: '2024-01-15 13:20:00',
    description: 'Smoke Detector #B1-12 frequently triggers false alarms, no smoke on site',
    analysis: 'Sensor dust accumulation or aging, requires cleaning or replacement'
  },
  {
    id: 'WO-2024-005',
    title: 'Access Controller Offline',
    deviceName: 'ACU-05',
    siteName: 'Server Room Entrance',
    severity: 'Critical',
    investigator: 'David Sun',
    startTime: '2024-01-15 14:45:00',
    description: 'Access controller ACU-05 has been offline for over 30 minutes, card access unavailable',
    analysis: 'Network communication failure or power supply issue, checking switch ports'
  },
  {
    id: 'WO-2024-006',
    title: 'Chiller Efficiency Degradation',
    deviceName: 'CH-01',
    siteName: 'Data Center A',
    severity: 'Warning',
    investigator: 'Lisa Zhou',
    startTime: '2024-01-15 16:00:00',
    description: 'Chiller CH-01 COP dropped from 5.2 to 4.5, abnormal energy increase',
    analysis: 'Condenser fouling or refrigerant leakage, analyzing operational parameters'
  },
  {
    id: 'WO-2024-007',
    title: 'Camera Feed Loss',
    deviceName: 'Camera DC-Hall-03',
    siteName: 'Data Center Hall',
    severity: 'Major',
    investigator: 'Tom Chen',
    startTime: '2024-01-15 17:30:00',
    description: 'Camera DC-Hall-03 video feed lost, black screen displayed',
    analysis: 'POE switch failure or camera hardware issue, checking network connectivity'
  },
  {
    id: 'WO-2024-008',
    title: 'VFD Communication Intermittent',
    deviceName: 'VFD-Pump-02',
    siteName: 'Mechanical Room',
    severity: 'Major',
    investigator: 'Anna Wu',
    startTime: '2024-01-16 08:20:00',
    description: 'VFD-Pump-02 experiences intermittent communication loss every 15-30 minutes',
    analysis: 'RS485 bus termination issue or electrical interference, checking wiring'
  },
  {
    id: 'WO-2024-009',
    title: 'BMS Server High CPU Usage',
    deviceName: 'BMS-SRV-01',
    siteName: 'Control Room',
    severity: 'Warning',
    investigator: 'Chris Liu',
    startTime: '2024-01-16 09:45:00',
    description: 'BMS server CPU usage consistently above 85%, causing slow response',
    analysis: 'Memory leak in historian service, analyzing process logs'
  },
  {
    id: 'WO-2024-010',
    title: 'Water Leak Detection Alert',
    deviceName: 'Leak Sensor CRAC-05',
    siteName: 'Data Center A',
    severity: 'Critical',
    investigator: 'Rachel Guo',
    startTime: '2024-01-16 10:30:00',
    description: 'Water leak sensor under CRAC-05 triggered, moisture detected',
    analysis: 'Condensate drain line blockage or supply line leak, investigating source'
  }
])

// Search and pagination
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart reference
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

const filteredWorkOrders = computed(() => {
  if (!searchKeyword.value) return workOrders.value
  const keyword = searchKeyword.value.toLowerCase()
  return workOrders.value.filter(
      order => order.id.toLowerCase().includes(keyword) ||
          order.deviceName.toLowerCase().includes(keyword) ||
          order.title.toLowerCase().includes(keyword)
  )
})

const paginatedWorkOrders = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredWorkOrders.value.slice(start, end)
})

const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
}

const severityTagType = (severity: string): string => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'Major': 'warning',
    'Warning': 'warning',
    'Minor': 'info'
  }
  return map[severity] || 'info'
}

// Dialog state
const detailVisible = ref(false)
const selectedOrder = ref<any>(null)

const viewDetail = (order: any) => {
  selectedOrder.value = order
  detailVisible.value = true
}

const resolveFault = (order: any) => {
  ElMessageBox.confirm(
      `Mark work order ${order.id} as resolved? This will move it to "Resolved" status.`,
      'Confirm Resolution',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'success'
      }
  ).then(() => {
    ElMessage.success(`Work order ${order.id} marked as resolved`)
    workOrders.value = workOrders.value.filter(wo => wo.id !== order.id)
    stats.value.investigating--
    stats.value.resolved++
  }).catch(() => {})
}

const escalateFault = (order: any) => {
  ElMessageBox.confirm(
      `Escalate work order ${order.id} to higher level support?`,
      'Confirm Escalation',
      {
        confirmButtonText: 'Escalate',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.warning(`Work order ${order.id} escalated to Level 2 support`)
  }).catch(() => {})
}

const initChart = () => {
  if (chartRef.value) {
    // Dispose existing instance if any
    if (chartInstance) {
      chartInstance.dispose()
    }

    chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: ['New', 'Investigating', 'Resolved'],
        left: 'right',
        textStyle: { color: '#606266' }
      },
      grid: {
        left: '3%',
        right: '4%',
        top: '5%',
        bottom: '5%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15', 'Jan 16'],
        axisLabel: { rotate: 0 }
      },
      yAxis: {
        type: 'value',
        name: 'Number of Faults',
        nameLocation: 'middle',
        nameGap: 45
      },
      series: [
        {
          name: 'New',
          type: 'bar',
          data: [6, 7, 5, 8, 4, 9, 7],
          itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] },
          barWidth: '25%'
        },
        {
          name: 'Investigating',
          type: 'bar',
          data: [12, 14, 13, 16, 18, 22, 24],
          itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] },
          barWidth: '25%'
        },
        {
          name: 'Resolved',
          type: 'line',
          data: [8, 10, 9, 12, 14, 16, 18],
          itemStyle: { color: '#67C23A' },
          smooth: true,
          symbol: 'circle',
          lineStyle: { width: 2 }
        }
      ]
    })
  }
}

// Handle window resize
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// Watch for isLoaded to initialize chart after DOM is ready
watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initChart()
      window.addEventListener('resize', handleResize)
    })
  }
})

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
    }, 400)
  }, 2000)
})

// Cleanup
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Fault Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="fault-workflow-investigating">
    <!-- Page Header -->
    <div class="page-header">
      <h2>Fault Workflow - Investigating</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
        <el-breadcrumb-item>Fault Management</el-breadcrumb-item>
        <el-breadcrumb-item>Fault Workflow</el-breadcrumb-item>
        <el-breadcrumb-item>Investigating</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon investigating">
            <el-icon><Search /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.investigating }}</div>
            <div class="stat-label">Investigating</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon new">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.new }}</div>
            <div class="stat-label">New</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon assigned">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.assigned }}</div>
            <div class="stat-label">Assigned</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon resolved">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.resolved }}</div>
            <div class="stat-label">Resolved</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon closed">
            <el-icon><Check /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.closed }}</div>
            <div class="stat-label">Closed</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Two Column Layout -->
    <div class="two-columns">
      <!-- Left: Fault Trend Chart - Full height card -->
      <el-card class="trend-chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Fault Trends (Last 7 Days)</span>
            <el-button type="primary" link>Details</el-button>
          </div>
        </template>
        <div class="chart-container">
          <div ref="chartRef" class="chart"></div>
        </div>
      </el-card>

      <!-- Right: Work Orders List -->
      <el-card class="work-order-list" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Investigating Work Orders</span>
            <el-input
                v-model="searchKeyword"
                placeholder="Search by ID / Device Name"
                clearable
                style="width: 220px"
                :prefix-icon="Search"
            />
          </div>
        </template>
        <el-table :data="paginatedWorkOrders" stripe style="width: 100%">
          <el-table-column prop="id" label="Work Order ID" width="140" align="center" />
          <el-table-column prop="title" label="Fault Title" min-width="200" show-overflow-tooltip align="center" />
          <el-table-column prop="deviceName" label="Device" width="150" align="center" />
          <el-table-column prop="siteName" label="Site" width="120" align="center" />
          <el-table-column prop="severity" label="Severity" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="severityTagType(row.severity)" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="investigator" label="Investigator" width="100" align="center" />
          <el-table-column prop="startTime" label="Start Time" width="160" align="center" />
          <el-table-column label="Actions" width="230" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">Details</el-button>
              <el-button type="success" link @click="resolveFault(row)">Resolve</el-button>
              <el-button type="warning" link @click="escalateFault(row)">Escalate</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="filteredWorkOrders.length"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="Work Order Details" width="600px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="Work Order ID">{{ selectedOrder.id }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="severityTagType(selectedOrder.severity)">{{ selectedOrder.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Fault Title" :span="2">{{ selectedOrder.title }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedOrder.deviceName }}</el-descriptions-item>
        <el-descriptions-item label="Site">{{ selectedOrder.siteName }}</el-descriptions-item>
        <el-descriptions-item label="Investigator">{{ selectedOrder.investigator }}</el-descriptions-item>
        <el-descriptions-item label="Start Time">{{ selectedOrder.startTime }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        <el-descriptions-item label="Preliminary Analysis" :span="2">{{ selectedOrder.analysis || 'Pending' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">Close</el-button>
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
.fault-workflow-investigating {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
}

.stat-card :deep(.el-card__body) {
  padding: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.investigating {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.stat-icon.new {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.stat-icon.assigned {
  background-color: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.stat-icon.resolved {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.stat-icon.closed {
  background-color: rgba(96, 98, 102, 0.1);
  color: #606266;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
  align-items: stretch;
}

/* Trend Chart Card - Full height */
.trend-chart-card {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.trend-chart-card :deep(.el-card__header) {
  flex-shrink: 0;
}

.trend-chart-card :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.chart-container {
  flex: 1;
  width: 100%;
  min-height: 680px;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 680px;
}

/* Work Order List Card */
.work-order-list {
  border-radius: 12px;
  display: flex;
  flex-direction: column;
}

.work-order-list :deep(.el-card__body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

/* Make table scrollable within card */
.work-order-list :deep(.el-table) {
  flex: 1;
  overflow: auto;
}

@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  }
  .two-columns {
    grid-template-columns: 1fr;
  }
  .chart-container {
    min-height: 350px;
  }
  .chart {
    min-height: 330px;
  }
}
</style>