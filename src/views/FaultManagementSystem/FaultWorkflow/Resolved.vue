<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import { Search, Document, User, CircleCheck, Check, Clock, ArrowRight } from "@element-plus/icons-vue"
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

// Mock resolved work orders data
const workOrders = ref([
  {
    id: 'WO-2024-011',
    title: 'AHU-02 Fan Belt Slippage',
    deviceName: 'AHU-02',
    siteName: 'Data Center A',
    severity: 'Major',
    investigator: 'John Zhang',
    resolver: 'John Zhang',
    startTime: '2024-01-14 08:30:00',
    resolvedTime: '2024-01-14 14:20:00',
    resolution: 'Replaced worn fan belt, tension adjusted',
    description: 'AHU-02 fan belt slipping causing reduced airflow',
    analysis: 'Belt wear due to extended operation, replacement performed'
  },
  {
    id: 'WO-2024-012',
    title: 'BMS Database Connection Timeout',
    deviceName: 'BMS-SRV-02',
    siteName: 'Control Room',
    severity: 'Warning',
    investigator: 'Sarah Li',
    resolver: 'Sarah Li',
    startTime: '2024-01-14 10:00:00',
    resolvedTime: '2024-01-14 11:30:00',
    resolution: 'Restarted database service, optimized connection pool',
    description: 'BMS database connection timeout causing data lag',
    analysis: 'Connection pool exhausted, increased max connections'
  },
  {
    id: 'WO-2024-013',
    title: 'Lighting Control Panel Offline',
    deviceName: 'LCP-B2-01',
    siteName: 'Office Building B2',
    severity: 'Minor',
    investigator: 'Mike Wang',
    resolver: 'Mike Wang',
    startTime: '2024-01-13 15:45:00',
    resolvedTime: '2024-01-14 09:15:00',
    resolution: 'Power cycled panel, firmware updated',
    description: 'Lighting control panel offline, lights stuck at 50%',
    analysis: 'Network switch reboot caused panel hang, firmware patch applied'
  },
  {
    id: 'WO-2024-014',
    title: 'Chilled Water Pump Vibration High',
    deviceName: 'CHWP-03',
    siteName: 'Central Plant',
    severity: 'Critical',
    investigator: 'Emma Zhao',
    resolver: 'Emma Zhao',
    startTime: '2024-01-13 09:00:00',
    resolvedTime: '2024-01-14 16:30:00',
    resolution: 'Realigned pump coupling, replaced bearings',
    description: 'Chilled water pump vibration exceeded alarm threshold',
    analysis: 'Coupling misalignment and bearing wear, full service completed'
  },
  {
    id: 'WO-2024-015',
    title: 'Smoke Detector Battery Low',
    deviceName: 'Smoke Detector #3F-08',
    siteName: 'Office Building 3F',
    severity: 'Minor',
    investigator: 'David Sun',
    resolver: 'David Sun',
    startTime: '2024-01-12 11:20:00',
    resolvedTime: '2024-01-12 14:45:00',
    resolution: 'Replaced battery, tested functionality',
    description: 'Smoke detector battery low warning',
    analysis: 'Battery reached end of life, routine replacement'
  },
  {
    id: 'WO-2024-016',
    title: 'UPS-02 Bypass Mode Active',
    deviceName: 'UPS-02',
    siteName: 'Data Center B',
    severity: 'Critical',
    investigator: 'Lisa Zhou',
    resolver: 'Lisa Zhou',
    startTime: '2024-01-12 08:15:00',
    resolvedTime: '2024-01-13 10:00:00',
    resolution: 'Replaced faulty rectifier module',
    description: 'UPS-02 running in bypass mode, battery not charging',
    analysis: 'Rectifier module failure, module replaced and tested'
  },
  {
    id: 'WO-2024-017',
    title: 'CRAC-02 High Humidity Alarm',
    deviceName: 'CRAC-02',
    siteName: 'Data Center A',
    severity: 'Major',
    investigator: 'Tom Chen',
    resolver: 'Tom Chen',
    startTime: '2024-01-11 13:00:00',
    resolvedTime: '2024-01-12 11:00:00',
    resolution: 'Cleaned condensate drain, recalibrated humidity sensor',
    description: 'CRAC-02 humidity at 65%, exceeding 55% threshold',
    analysis: 'Clogged drain line and sensor drift, cleaned and calibrated'
  },
  {
    id: 'WO-2024-018',
    title: 'Access Card Reader Unresponsive',
    deviceName: 'Reader EastGate',
    siteName: 'Main Entrance',
    severity: 'Major',
    investigator: 'Anna Wu',
    resolver: 'Anna Wu',
    startTime: '2024-01-11 09:30:00',
    resolvedTime: '2024-01-11 15:20:00',
    resolution: 'Replaced reader, checked wiring',
    description: 'East gate card reader unresponsive to badge scans',
    analysis: 'Hardware failure, reader replaced and tested'
  },
  {
    id: 'WO-2024-019',
    title: 'Cooling Tower CT-01 Low Flow',
    deviceName: 'CT-01',
    siteName: 'Central Plant',
    severity: 'Major',
    investigator: 'Chris Liu',
    resolver: 'Chris Liu',
    startTime: '2024-01-10 14:00:00',
    resolvedTime: '2024-01-11 16:00:00',
    resolution: 'Cleaned strainers, adjusted bypass valve',
    description: 'Cooling tower water flow below normal range',
    analysis: 'Strainers partially blocked, cleaned and valve adjusted'
  },
  {
    id: 'WO-2024-020',
    title: 'VFD Overheating Alarm',
    deviceName: 'VFD-AHU-04',
    siteName: 'Data Center A',
    severity: 'Warning',
    investigator: 'Rachel Guo',
    resolver: 'Rachel Guo',
    startTime: '2024-01-10 10:30:00',
    resolvedTime: '2024-01-10 16:45:00',
    resolution: 'Cleaned heatsink, checked cooling fan',
    description: 'VFD temperature at 85°C, alarm threshold 80°C',
    analysis: 'Dust accumulation on heatsink, cleaned and fan verified'
  }
])

// Search and pagination
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// Chart reference
const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const filteredWorkOrders = computed(() => {
  if (!searchKeyword.value) return workOrders.value
  const keyword = searchKeyword.value.toLowerCase()
  return workOrders.value.filter(
      order => order.id.toLowerCase().includes(keyword) ||
          order.deviceName.toLowerCase().includes(keyword) ||
          order.title.toLowerCase().includes(keyword) ||
          order.resolver.toLowerCase().includes(keyword)
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

// Calculate resolution time in hours
const getResolutionTime = (startTime: string, resolvedTime: string): string => {
  const start = new Date(startTime)
  const resolved = new Date(resolvedTime)
  const diffHours = (resolved.getTime() - start.getTime()) / (1000 * 60 * 60)
  if (diffHours < 1) {
    return `${Math.round(diffHours * 60)} min`
  }
  return `${diffHours.toFixed(1)} hrs`
}

// Dialog state
const detailVisible = ref(false)
const selectedOrder = ref<any>(null)

const viewDetail = (order: any) => {
  selectedOrder.value = order
  detailVisible.value = true
}

const reopenFault = (order: any) => {
  ElMessageBox.confirm(
      `Reopen work order ${order.id}? This will move it back to "Investigating" status.`,
      'Confirm Reopen',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.info(`Work order ${order.id} reopened for investigation`)
    workOrders.value = workOrders.value.filter(wo => wo.id !== order.id)
    stats.value.resolved--
    stats.value.investigating++
  }).catch(() => {})
}

const verifyResolution = (order: any) => {
  ElMessageBox.confirm(
      `Verify resolution for work order ${order.id} and move to "Closed"?`,
      'Confirm Verification',
      {
        confirmButtonText: 'Verify & Close',
        cancelButtonText: 'Cancel',
        type: 'success'
      }
  ).then(() => {
    ElMessage.success(`Work order ${order.id} verified and closed`)
    workOrders.value = workOrders.value.filter(wo => wo.id !== order.id)
    stats.value.resolved--
    stats.value.closed++
  }).catch(() => {})
}

const initChart = () => {
  if (chartRef.value) {
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
        data: ['Resolved', 'Closed', 'Avg Resolution Time (hrs)'],
        left: 'center',
        top: 0,
        textStyle: { color: '#606266' }
      },
      grid: {
        left: '3%',
        right: '4%',
        top: '15%',
        bottom: '8%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['Jan 10', 'Jan 11', 'Jan 12', 'Jan 13', 'Jan 14', 'Jan 15', 'Jan 16'],
        axisLabel: { rotate: 0 }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Number of Faults',
          nameLocation: 'middle',
          nameGap: 45
        },
        {
          type: 'value',
          name: 'Resolution Time (hrs)',
          nameLocation: 'middle',
          nameGap: 50,
          axisLabel: { formatter: '{value} hrs' }
        }
      ],
      series: [
        {
          name: 'Resolved',
          type: 'bar',
          data: [6, 8, 7, 5, 9, 6, 8],
          itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] },
          barWidth: '25%'
        },
        {
          name: 'Closed',
          type: 'bar',
          data: [4, 5, 6, 4, 7, 5, 6],
          itemStyle: { color: '#909399', borderRadius: [4, 4, 0, 0] },
          barWidth: '25%'
        },
        {
          name: 'Avg Resolution Time (hrs)',
          type: 'line',
          yAxisIndex: 1,
          data: [5.2, 4.8, 5.5, 4.2, 3.9, 4.5, 4.1],
          itemStyle: { color: '#E6A23C' },
          smooth: true,
          symbol: 'diamond',
          lineStyle: { width: 2, type: 'dashed' }
        }
      ]
    })
  }
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

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

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
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
  <div v-else class="fault-workflow-resolved">
    <!-- Page Header -->
    <div class="page-header">
      <h2>Fault Workflow - Resolved</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
        <el-breadcrumb-item>Fault Management</el-breadcrumb-item>
        <el-breadcrumb-item>Fault Workflow</el-breadcrumb-item>
        <el-breadcrumb-item>Resolved</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
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
      <!-- Left: Resolution Trend Chart -->
      <el-card class="trend-chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Resolution Trends (Last 7 Days)</span>
            <el-button type="primary" link>Details</el-button>
          </div>
        </template>
        <div class="chart-container">
          <div ref="chartRef" class="chart"></div>
        </div>
      </el-card>

      <!-- Right: Resolved Work Orders List -->
      <el-card class="work-order-list" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Resolved Work Orders</span>
            <el-input
                v-model="searchKeyword"
                placeholder="Search by ID / Device / Resolver"
                clearable
                style="width: 240px"
                :prefix-icon="Search"
            />
          </div>
        </template>
        <el-table :data="paginatedWorkOrders" stripe style="width: 100%">
          <el-table-column prop="id" label="Work Order ID" width="130" align="center" />
          <el-table-column prop="title" label="Fault Title" min-width="200" show-overflow-tooltip align="center" />
          <el-table-column prop="deviceName" label="Device" width="140" align="center" />
          <el-table-column prop="severity" label="Severity" width="95" align="center">
            <template #default="{ row }">
              <el-tag :type="severityTagType(row.severity)" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="resolver" label="Resolved By" width="110" />
          <el-table-column label="Resolution Time" width="110">
            <template #default="{ row }">
              <el-tooltip :content="`Started: ${row.startTime}`" placement="top">
                <span class="resolution-time">
                  <el-icon><Clock /></el-icon>
                  {{ getResolutionTime(row.startTime, row.resolvedTime) }}
                </span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="resolvedTime" label="Resolved At" width="150" align="center" />
          <el-table-column label="Actions" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="viewDetail(row)">Details</el-button>
              <el-button type="warning" link @click="reopenFault(row)">Reopen</el-button>
              <el-button type="success" link @click="verifyResolution(row)">Verify</el-button>
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
    <el-dialog v-model="detailVisible" title="Work Order Details" width="650px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="Work Order ID">{{ selectedOrder.id }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="severityTagType(selectedOrder.severity)">{{ selectedOrder.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Fault Title" :span="2">{{ selectedOrder.title }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedOrder.deviceName }}</el-descriptions-item>
        <el-descriptions-item label="Site">{{ selectedOrder.siteName }}</el-descriptions-item>
        <el-descriptions-item label="Investigator">{{ selectedOrder.investigator }}</el-descriptions-item>
        <el-descriptions-item label="Resolver">{{ selectedOrder.resolver }}</el-descriptions-item>
        <el-descriptions-item label="Start Time">{{ selectedOrder.startTime }}</el-descriptions-item>
        <el-descriptions-item label="Resolved Time">{{ selectedOrder.resolvedTime }}</el-descriptions-item>
        <el-descriptions-item label="Resolution Duration" :span="2">
          <el-tag type="success" size="small">
            {{ getResolutionTime(selectedOrder.startTime, selectedOrder.resolvedTime) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedOrder.description }}</el-descriptions-item>
        <el-descriptions-item label="Analysis" :span="2">{{ selectedOrder.analysis }}</el-descriptions-item>
        <el-descriptions-item label="Resolution" :span="2">{{ selectedOrder.resolution }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">Close</el-button>
          <el-button type="warning" @click="reopenFault(selectedOrder); detailVisible = false">Reopen</el-button>
          <el-button type="success" @click="verifyResolution(selectedOrder); detailVisible = false">Verify & Close</el-button>
        </div>
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
.fault-workflow-resolved {
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

.stat-icon.new {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.stat-icon.assigned {
  background-color: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.stat-icon.investigating {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
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

/* Trend Chart Card */
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
  min-height: 420px;
  position: relative;
}

.chart {
  width: 100%;
  height: 100%;
  min-height: 690px;
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

.resolution-time {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #67c23a;
  font-weight: 500;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
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