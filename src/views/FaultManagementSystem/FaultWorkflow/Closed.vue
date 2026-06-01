<script setup lang="ts">
import { ref, onMounted, nextTick, watch, onUnmounted, computed } from 'vue'
import { Search, Document, User, CircleCheck, Check, Clock, ArrowRight, Trophy, Star, TrendCharts, DataAnalysis, Tickets, Filter, RefreshRight } from "@element-plus/icons-vue"
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
  totalClosed: 187,
  avgResolutionTime: 4.2,
  onTimeClosure: 94.8,
  customerSatisfaction: 4.6,
  reopenedCount: 8
})

// Mock closed work orders data
const workOrders = ref([
  {
    id: 'CLS-2024-001',
    title: 'AHU-02 Fan Belt Slippage',
    deviceName: 'AHU-02',
    siteName: 'Data Center A',
    severity: 'Major',
    assignee: 'John Zhang',
    closedBy: 'John Zhang',
    startTime: '2024-01-14 08:30:00',
    closedTime: '2024-01-14 14:20:00',
    resolution: 'Replaced worn fan belt, tension adjusted',
    verification: 'Verified by shift supervisor - operation confirmed',
    satisfaction: 5,
    tags: ['Mechanical', 'Preventive']
  },
  {
    id: 'CLS-2024-002',
    title: 'BMS Database Connection Timeout',
    deviceName: 'BMS-SRV-02',
    siteName: 'Control Room',
    severity: 'Warning',
    assignee: 'Sarah Li',
    closedBy: 'Sarah Li',
    startTime: '2024-01-14 10:00:00',
    closedTime: '2024-01-14 11:30:00',
    resolution: 'Restarted database service, optimized connection pool',
    verification: 'Monitoring shows stable connections for 48 hours',
    satisfaction: 4,
    tags: ['Software', 'Database']
  },
  {
    id: 'CLS-2024-003',
    title: 'Lighting Control Panel Offline',
    deviceName: 'LCP-B2-01',
    siteName: 'Office Building B2',
    severity: 'Minor',
    assignee: 'Mike Wang',
    closedBy: 'Mike Wang',
    startTime: '2024-01-13 15:45:00',
    closedTime: '2024-01-14 09:15:00',
    resolution: 'Power cycled panel, firmware updated',
    verification: 'All lighting zones responding correctly',
    satisfaction: 3,
    tags: ['Electrical', 'Firmware']
  },
  {
    id: 'CLS-2024-004',
    title: 'Chilled Water Pump Vibration High',
    deviceName: 'CHWP-03',
    siteName: 'Central Plant',
    severity: 'Critical',
    assignee: 'Emma Zhao',
    closedBy: 'Emma Zhao',
    startTime: '2024-01-13 09:00:00',
    closedTime: '2024-01-14 16:30:00',
    resolution: 'Realigned pump coupling, replaced bearings',
    verification: 'Vibration readings within normal range for 24h',
    satisfaction: 5,
    tags: ['Mechanical', 'Critical']
  },
  {
    id: 'CLS-2024-005',
    title: 'Smoke Detector Battery Low',
    deviceName: 'Smoke Detector #3F-08',
    siteName: 'Office Building 3F',
    severity: 'Minor',
    assignee: 'David Sun',
    closedBy: 'David Sun',
    startTime: '2024-01-12 11:20:00',
    closedTime: '2024-01-12 14:45:00',
    resolution: 'Replaced battery, tested functionality',
    verification: 'Detector passed self-test and communication check',
    satisfaction: 4,
    tags: ['Safety', 'Routine']
  },
  {
    id: 'CLS-2024-006',
    title: 'UPS-02 Bypass Mode Active',
    deviceName: 'UPS-02',
    siteName: 'Data Center B',
    severity: 'Critical',
    assignee: 'Lisa Zhou',
    closedBy: 'Lisa Zhou',
    startTime: '2024-01-12 08:15:00',
    closedTime: '2024-01-13 10:00:00',
    resolution: 'Replaced faulty rectifier module',
    verification: 'UPS running in normal mode, batteries charging',
    satisfaction: 5,
    tags: ['Power', 'UPS']
  },
  {
    id: 'CLS-2024-007',
    title: 'CRAC-02 High Humidity Alarm',
    deviceName: 'CRAC-02',
    siteName: 'Data Center A',
    severity: 'Major',
    assignee: 'Tom Chen',
    closedBy: 'Tom Chen',
    startTime: '2024-01-11 13:00:00',
    closedTime: '2024-01-12 11:00:00',
    resolution: 'Cleaned condensate drain, recalibrated humidity sensor',
    verification: 'Humidity stable at 48-52% for 24h',
    satisfaction: 4,
    tags: ['HVAC', 'Calibration']
  },
  {
    id: 'CLS-2024-008',
    title: 'Access Card Reader Unresponsive',
    deviceName: 'Reader EastGate',
    siteName: 'Main Entrance',
    severity: 'Major',
    assignee: 'Anna Wu',
    closedBy: 'Anna Wu',
    startTime: '2024-01-11 09:30:00',
    closedTime: '2024-01-11 15:20:00',
    resolution: 'Replaced reader, checked wiring',
    verification: 'Card reads successful for all test badges',
    satisfaction: 4,
    tags: ['Security', 'Hardware']
  },
  {
    id: 'CLS-2024-009',
    title: 'Cooling Tower CT-01 Low Flow',
    deviceName: 'CT-01',
    siteName: 'Central Plant',
    severity: 'Major',
    assignee: 'Chris Liu',
    closedBy: 'Chris Liu',
    startTime: '2024-01-10 14:00:00',
    closedTime: '2024-01-11 16:00:00',
    resolution: 'Cleaned strainers, adjusted bypass valve',
    verification: 'Flow rate returned to nominal 850 GPM',
    satisfaction: 4,
    tags: ['HVAC', 'Plumbing']
  },
  {
    id: 'CLS-2024-010',
    title: 'VFD Overheating Alarm',
    deviceName: 'VFD-AHU-04',
    siteName: 'Data Center A',
    severity: 'Warning',
    assignee: 'Rachel Guo',
    closedBy: 'Rachel Guo',
    startTime: '2024-01-10 10:30:00',
    closedTime: '2024-01-10 16:45:00',
    resolution: 'Cleaned heatsink, checked cooling fan',
    verification: 'Temperature stable at 52°C under load',
    satisfaction: 5,
    tags: ['Electrical', 'VFD']
  },
  {
    id: 'CLS-2024-011',
    title: 'Water Leak Sensor False Alarm',
    deviceName: 'Leak Sensor CRAC-04',
    siteName: 'Data Center B',
    severity: 'Info',
    assignee: 'John Zhang',
    closedBy: 'John Zhang',
    startTime: '2024-01-09 20:15:00',
    closedTime: '2024-01-10 08:30:00',
    resolution: 'Sensor recalibrated, sensitivity adjusted',
    verification: 'No further false alarms in 48h',
    satisfaction: 4,
    tags: ['Sensors', 'Calibration']
  },
  {
    id: 'CLS-2024-012',
    title: 'Generator Weekly Test Failure',
    deviceName: 'Gen-01',
    siteName: 'Data Center A',
    severity: 'Critical',
    assignee: 'Lisa Zhou',
    closedBy: 'Lisa Zhou',
    startTime: '2024-01-09 09:00:00',
    closedTime: '2024-01-09 15:30:00',
    resolution: 'Replaced fuel filter, bled air from system',
    verification: 'Generator passed full load bank test',
    satisfaction: 5,
    tags: ['Power', 'Generator']
  }
])

// Monthly closure data for chart
const monthlyClosureData = ref([
  { month: 'Aug', count: 42, avgTime: 5.1 },
  { month: 'Sep', count: 38, avgTime: 4.8 },
  { month: 'Oct', count: 45, avgTime: 4.5 },
  { month: 'Nov', count: 52, avgTime: 4.3 },
  { month: 'Dec', count: 48, avgTime: 4.0 },
  { month: 'Jan', count: 56, avgTime: 3.9 }
])

// Top failure categories
const topCategories = ref([
  { name: 'HVAC', count: 34, percentage: 28.3 },
  { name: 'Power', count: 28, percentage: 23.3 },
  { name: 'Controls', count: 22, percentage: 18.3 },
  { name: 'Security', count: 18, percentage: 15.0 },
  { name: 'Network', count: 12, percentage: 10.0 },
  { name: 'Other', count: 6, percentage: 5.1 }
])

// Search and pagination
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const selectedSeverity = ref('')
const selectedTag = ref('')

// Chart references
const chartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null
let categoryChartInstance: echarts.ECharts | null = null

const allTags = computed(() => {
  const tagsSet = new Set<string>()
  workOrders.value.forEach(order => {
    order.tags.forEach(tag => tagsSet.add(tag))
  })
  return Array.from(tagsSet).sort()
})

const filteredWorkOrders = computed(() => {
  let filtered = workOrders.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(order =>
        order.id.toLowerCase().includes(keyword) ||
        order.deviceName.toLowerCase().includes(keyword) ||
        order.title.toLowerCase().includes(keyword) ||
        order.closedBy.toLowerCase().includes(keyword)
    )
  }

  if (selectedSeverity.value) {
    filtered = filtered.filter(order => order.severity === selectedSeverity.value)
  }

  if (selectedTag.value) {
    filtered = filtered.filter(order => order.tags.includes(selectedTag.value))
  }

  return filtered
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
    'Minor': 'info',
    'Info': 'info'
  }
  return map[severity] || 'info'
}

// Calculate resolution time in hours
const getResolutionTime = (startTime: string, closedTime: string): string => {
  const start = new Date(startTime)
  const closed = new Date(closedTime)
  const diffHours = (closed.getTime() - start.getTime()) / (1000 * 60 * 60)
  if (diffHours < 1) {
    return `${Math.round(diffHours * 60)}m`
  }
  if (diffHours < 24) {
    return `${diffHours.toFixed(1)}h`
  }
  return `${(diffHours / 24).toFixed(1)}d`
}

// Dialog state
const detailVisible = ref(false)
const selectedOrder = ref<any>(null)

const viewDetail = (order: any) => {
  selectedOrder.value = order
  detailVisible.value = true
}

const getSatisfactionIcon = (rating: number) => {
  if (rating >= 4.5) return '🎉'
  if (rating >= 3.5) return '👍'
  if (rating >= 2.5) return '😐'
  return '👎'
}

// Initialize trend chart
const initTrendChart = () => {
  if (chartRef.value) {
    if (chartInstance) chartInstance.dispose()

    chartInstance = echarts.init(chartRef.value)
    chartInstance.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' }
      },
      legend: {
        data: ['Tickets Closed', 'Avg Resolution Time (hrs)'],
        left: 'left',
        top: 0,
        textStyle: { color: '#606266' }
      },
      grid: {
        left: '3%',
        right: '6%',
        top: '15%',
        bottom: '8%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: monthlyClosureData.value.map(d => d.month),
        axisLabel: { rotate: 0, fontWeight: 500 }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Closed Tickets',
          nameLocation: 'middle',
          nameGap: 45,
          axisLabel: { formatter: '{value}' }
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
          name: 'Tickets Closed',
          type: 'bar',
          data: monthlyClosureData.value.map(d => d.count),
          itemStyle: {
            color: '#67C23A',
            borderRadius: [8, 8, 0, 0],
            shadowColor: 'rgba(103, 194, 58, 0.3)',
            shadowBlur: 10
          },
          barWidth: '40%',
          label: {
            show: true,
            position: 'top',
            formatter: '{c}'
          }
        },
        {
          name: 'Avg Resolution Time (hrs)',
          type: 'line',
          yAxisIndex: 1,
          data: monthlyClosureData.value.map(d => d.avgTime),
          itemStyle: { color: '#E6A23C' },
          smooth: true,
          symbol: 'circle',
          symbolSize: 8,
          lineStyle: { width: 3 },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}h'
          }
        }
      ]
    })
  }
}

// Initialize category pie chart
const initCategoryChart = () => {
  if (categoryChartRef.value) {
    if (categoryChartInstance) categoryChartInstance.dispose()

    categoryChartInstance = echarts.init(categoryChartRef.value)
    categoryChartInstance.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {d}% ({c} tickets)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'center',
        textStyle: { color: '#606266' }
      },
      series: [
        {
          name: 'Failure Categories',
          type: 'pie',
          radius: ['40%', '65%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontWeight: 'bold'
            }
          },
          data: topCategories.value.map(cat => ({
            name: cat.name,
            value: cat.count,
            itemStyle: {
              color: cat.name === 'HVAC' ? '#409EFF' :
                  cat.name === 'Power' ? '#F56C6C' :
                      cat.name === 'Controls' ? '#E6A23C' :
                          cat.name === 'Security' ? '#909399' :
                              cat.name === 'Network' ? '#67C23A' : '#C0C4CC'
            }
          }))
        }
      ]
    })
  }
}

const handleResize = () => {
  if (chartInstance) chartInstance.resize()
  if (categoryChartInstance) categoryChartInstance.resize()
}

watch(isLoaded, (loaded) => {
  if (loaded) {
    nextTick(() => {
      initTrendChart()
      initCategoryChart()
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
  if (chartInstance) chartInstance?.dispose()
  if (categoryChartInstance) categoryChartInstance?.dispose()
})

// Reset filters
const resetFilters = () => {
  searchKeyword.value = ''
  selectedSeverity.value = ''
  selectedTag.value = ''
  currentPage.value = 1
}
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
  <div v-else class="fault-workflow-closed">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Closed Work Orders</h2>
        <p class="subtitle">Historical records of resolved and verified incidents</p>
      </div>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
        <el-breadcrumb-item>Fault Management</el-breadcrumb-item>
        <el-breadcrumb-item>Fault Workflow</el-breadcrumb-item>
        <el-breadcrumb-item>Closed</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon total">
            <el-icon><Tickets /></el-icon>
          </div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.totalClosed }}</span>
            <span class="kpi-label">Total Closed</span>
          </div>
          <div class="kpi-trend up">
            <el-icon><TrendCharts /></el-icon>
            +12%
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon time">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.avgResolutionTime }}h</span>
            <span class="kpi-label">Avg Resolution</span>
          </div>
          <div class="kpi-trend down">
            <el-icon><TrendCharts /></el-icon>
            -0.5h
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon ontime">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.onTimeClosure }}%</span>
            <span class="kpi-label">On-Time Closure</span>
          </div>
          <div class="kpi-trend up">
            <el-icon><TrendCharts /></el-icon>
            +3.2%
          </div>
        </div>
      </el-card>
      <el-card class="kpi-card" shadow="hover">
        <div class="kpi-content">
          <div class="kpi-icon satisfaction">
            <el-icon><Star /></el-icon>
          </div>
          <div class="kpi-info">
            <span class="kpi-value">{{ stats.customerSatisfaction }}</span>
            <span class="kpi-label">Satisfaction</span>
          </div>
          <div class="kpi-trend up">
            <el-icon><TrendCharts /></el-icon>
            +0.2
          </div>
        </div>
      </el-card>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <el-card class="trend-chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Monthly Closure Performance</span>
            <el-tag type="success" size="small">Last 6 Months</el-tag>
          </div>
        </template>
        <div ref="chartRef" class="trend-chart"></div>
      </el-card>

      <el-card class="category-chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>Failure Categories Distribution</span>
            <el-tag type="info" size="small">By Ticket Volume</el-tag>
          </div>
        </template>
        <div ref="categoryChartRef" class="category-chart"></div>
      </el-card>
    </div>

    <!-- Closed Work Orders Table -->
    <el-card class="work-order-table-card" shadow="hover">
      <template #header>
        <div class="table-header">
          <span class="table-title">Closed Work Orders Archive</span>
          <div class="table-filters">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by ID, Device, Title..."
                clearable
                style="width: 220px"
                :prefix-icon="Search"
            />
            <el-select v-model="selectedSeverity" placeholder="Severity" clearable style="width: 120px">
              <el-option label="Critical" value="Critical" />
              <el-option label="Major" value="Major" />
              <el-option label="Warning" value="Warning" />
              <el-option label="Minor" value="Minor" />
              <el-option label="Info" value="Info" />
            </el-select>
            <el-select v-model="selectedTag" placeholder="Tag" clearable style="width: 130px">
              <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
            </el-select>
            <el-button type="primary" link @click="resetFilters">
              <el-icon><RefreshRight /></el-icon> Reset
            </el-button>
          </div>
        </div>
      </template>
      <el-table :data="paginatedWorkOrders" stripe style="width: 100%">
        <el-table-column prop="id" label="Ticket ID" width="120" />
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="deviceName" label="Device" width="140" />
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="severityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Tags" width="150">
          <template #default="{ row }">
            <div class="tags-container">
              <el-tag v-for="tag in row.tags" :key="tag" size="small" type="info" effect="plain">
                {{ tag }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="closedBy" label="Closed By" width="110" />
        <el-table-column label="Duration" width="100">
          <template #default="{ row }">
            <span class="duration-badge">
              <el-icon><Clock /></el-icon>
              {{ getResolutionTime(row.startTime, row.closedTime) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="Satisfaction" width="100">
          <template #default="{ row }">
            <div class="satisfaction">
              <span class="satisfaction-icon">{{ getSatisfactionIcon(row.satisfaction) }}</span>
              <span>{{ row.satisfaction }}/5</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="closedTime" label="Closed At" width="150" />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewDetail(row)">
              <el-icon><Search /></el-icon> View
            </el-button>
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

    <!-- Detail Dialog -->
    <el-dialog v-model="detailVisible" title="Closed Ticket Details" width="700px">
      <el-descriptions :column="2" border v-if="selectedOrder">
        <el-descriptions-item label="Ticket ID" :span="2">
          <span class="ticket-id">{{ selectedOrder.id }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="Title" :span="2">{{ selectedOrder.title }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedOrder.deviceName }}</el-descriptions-item>
        <el-descriptions-item label="Site">{{ selectedOrder.siteName }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="severityTagType(selectedOrder.severity)">{{ selectedOrder.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Tags">
          <div class="tags-container">
            <el-tag v-for="tag in selectedOrder.tags" :key="tag" size="small">{{ tag }}</el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Assignee">{{ selectedOrder.assignee }}</el-descriptions-item>
        <el-descriptions-item label="Closed By">{{ selectedOrder.closedBy }}</el-descriptions-item>
        <el-descriptions-item label="Start Time">{{ selectedOrder.startTime }}</el-descriptions-item>
        <el-descriptions-item label="Closed Time">{{ selectedOrder.closedTime }}</el-descriptions-item>
        <el-descriptions-item label="Resolution Duration">
          <el-tag type="success">
            {{ getResolutionTime(selectedOrder.startTime, selectedOrder.closedTime) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Resolution" :span="2">{{ selectedOrder.resolution }}</el-descriptions-item>
        <el-descriptions-item label="Verification" :span="2">{{ selectedOrder.verification }}</el-descriptions-item>
        <el-descriptions-item label="Satisfaction Rating">
          <div class="satisfaction">
            <span class="satisfaction-icon">{{ getSatisfactionIcon(selectedOrder.satisfaction) }}</span>
            <span>{{ selectedOrder.satisfaction }}/5</span>
          </div>
        </el-descriptions-item>
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
.fault-workflow-closed {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #303133, #606266);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  border-radius: 20px;
  transition: all 0.3s ease;
  border: none;
}

.kpi-card:hover {
  transform: translateY(-4px);
}

.kpi-card :deep(.el-card__body) {
  padding: 20px;
}

.kpi-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.kpi-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.kpi-icon.time {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.kpi-icon.ontime {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.kpi-icon.satisfaction {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
}

.kpi-info {
  flex: 1;
}

.kpi-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.kpi-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.kpi-trend {
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 4px 8px;
  border-radius: 20px;
}

.kpi-trend.up {
  color: #67c23a;
  background: rgba(103, 194, 58, 0.1);
}

.kpi-trend.down {
  color: #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 0.8fr;
  gap: 20px;
  margin-bottom: 24px;
}

.trend-chart-card,
.category-chart-card {
  border-radius: 20px;
}

.trend-chart-card :deep(.el-card__body),
.category-chart-card :deep(.el-card__body) {
  padding: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.trend-chart {
  width: 100%;
  height: 320px;
}

.category-chart {
  width: 100%;
  height: 320px;
}

/* Table Card */
.work-order-table-card {
  border-radius: 20px;
}

.work-order-table-card :deep(.el-card__body) {
  padding: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.table-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.table-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tags-container {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.duration-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: #67c23a;
  font-weight: 500;
}

.satisfaction {
  display: flex;
  align-items: center;
  gap: 6px;
}

.satisfaction-icon {
  font-size: 16px;
}

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

.ticket-id {
  font-family: monospace;
  font-weight: 600;
  color: #409eff;
}

/* Responsive */
@media (max-width: 1200px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .trend-chart,
  .category-chart {
    height: 280px;
  }
}

@media (max-width: 768px) {
  .fault-workflow-closed {
    padding: 16px;
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .table-filters {
    width: 100%;
    flex-direction: column;
  }

  .table-filters .el-input,
  .table-filters .el-select {
    width: 100% !important;
  }
}
</style>