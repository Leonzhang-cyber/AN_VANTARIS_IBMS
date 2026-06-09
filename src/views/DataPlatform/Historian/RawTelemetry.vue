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
        <div class="loading-tip">Raw Telemetry Data</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="raw-telemetry-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Historian</el-breadcrumb-item>
            <el-breadcrumb-item>Raw Telemetry</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Raw Telemetry Data</h1>
        <p class="description">Real-time and historical raw telemetry data from IoT sensors, devices, and SCADA systems</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Data
        </el-button>
        <el-button type="primary" @click="handleLiveView">
          <el-icon><VideoCamera /></el-icon>
          Live View
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
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
                <span class="trend-label">vs last hour</span>
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

    <!-- Real-time Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Real-time Telemetry Stream</span>
          <div class="chart-controls">
            <el-select v-model="selectedMetric" size="small" style="width: 150px">
              <el-option label="Temperature (°C)" value="temperature" />
              <el-option label="Humidity (%)" value="humidity" />
              <el-option label="Pressure (Pa)" value="pressure" />
              <el-option label="Vibration (mm/s)" value="vibration" />
              <el-option label="Power (kW)" value="power" />
            </el-select>
            <el-select v-model="selectedDevice" size="small" style="width: 180px">
              <el-option label="All Devices" value="all" />
              <el-option label="Chiller-01" value="chiller_01" />
              <el-option label="AHU-03" value="ahu_03" />
              <el-option label="CT-02" value="ct_02" />
              <el-option label="Sensor Array A1" value="sensor_a1" />
            </el-select>
            <el-button size="small" @click="refreshChart">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </div>
      </template>
      <div ref="realtimeChartRef" class="realtime-chart-container"></div>
      <div class="chart-stats">
        <span>Current: <strong>{{ currentValue }}</strong></span>
        <span>Min: <strong>{{ minValue }}</strong></span>
        <span>Max: <strong>{{ maxValue }}</strong></span>
        <span>Avg: <strong>{{ avgValue }}</strong></span>
      </div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.deviceId"
              placeholder="Device ID"
              clearable
              style="width: 180px"
              @clear="handleSearch"
          />
          <el-select v-model="filters.metricType" placeholder="Metric Type" clearable style="width: 140px">
            <el-option label="Temperature" value="temperature" />
            <el-option label="Humidity" value="humidity" />
            <el-option label="Pressure" value="pressure" />
            <el-option label="Vibration" value="vibration" />
            <el-option label="Power" value="power" />
            <el-option label="Flow Rate" value="flow_rate" />
          </el-select>
          <el-select v-model="filters.dataQuality" placeholder="Data Quality" clearable style="width: 140px">
            <el-option label="Good" value="good" />
            <el-option label="Suspect" value="suspect" />
            <el-option label="Bad" value="bad" />
          </el-select>
          <el-date-picker
              v-model="filters.timeRange"
              type="datetimerange"
              range-separator="to"
              start-placeholder="Start Time"
              end-placeholder="End Time"
              style="width: 360px"
          />
          <el-button type="primary" @click="handleSearch">Query</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Data Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Telemetry Records ({{ filteredData.length }} records)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchData" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedData" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="timestamp" label="Timestamp"  />
        <el-table-column prop="deviceId" label="Device ID"  show-overflow-tooltip />
        <el-table-column prop="deviceName" label="Device Name"  show-overflow-tooltip />
        <el-table-column prop="metric" label="Metric" >
          <template #default="{ row }">
            <el-tag :type="getMetricTag(row.metric)" size="small">{{ formatMetricName(row.metric) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="Value"  align="right">
          <template #default="{ row }">
            <span :class="getValueClass(row)">{{ row.value }} {{ row.unit }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="Unit" width="80" />
        <el-table-column prop="quality" label="Quality" >
          <template #default="{ row }">
            <el-tag :type="getQualityTag(row.quality)" size="small">{{ row.quality }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="trendAnalysis(row)">Trend</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[20, 50, 100, 200]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredData.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Data Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Telemetry Details - ${currentRecord?.deviceId}`" width="600px" destroy-on-close>
      <div class="telemetry-details" v-if="currentRecord">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Timestamp">{{ currentRecord.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Device ID">{{ currentRecord.deviceId }}</el-descriptions-item>
          <el-descriptions-item label="Device Name">{{ currentRecord.deviceName }}</el-descriptions-item>
          <el-descriptions-item label="Metric">{{ formatMetricName(currentRecord.metric) }}</el-descriptions-item>
          <el-descriptions-item label="Value">{{ currentRecord.value }} {{ currentRecord.unit }}</el-descriptions-item>
          <el-descriptions-item label="Quality">
            <el-tag :type="getQualityTag(currentRecord.quality)" size="small">{{ currentRecord.quality }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Source">{{ currentRecord.source }}</el-descriptions-item>
          <el-descriptions-item label="Protocol">{{ currentRecord.protocol || 'MQTT' }}</el-descriptions-item>
          <el-descriptions-item label="Raw Payload" :span="2">
            <pre class="raw-payload">{{ JSON.stringify(currentRecord.rawPayload, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportRecord">Export</el-button>
      </template>
    </el-dialog>

    <!-- Trend Analysis Dialog -->
    <el-dialog v-model="trendDialogVisible" title="Trend Analysis" width="800px" destroy-on-close>
      <div class="trend-container">
        <div ref="trendChartRef" class="trend-chart-container"></div>
        <div class="trend-stats">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="Mean">{{ trendStats.mean }}</el-descriptions-item>
            <el-descriptions-item label="Median">{{ trendStats.median }}</el-descriptions-item>
            <el-descriptions-item label="Std Dev">{{ trendStats.stdDev }}</el-descriptions-item>
            <el-descriptions-item label="Min">{{ trendStats.min }}</el-descriptions-item>
            <el-descriptions-item label="Max">{{ trendStats.max }}</el-descriptions-item>
            <el-descriptions-item label="Count">{{ trendStats.count }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="trendDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportTrend">Export Data</el-button>
      </template>
    </el-dialog>

    <!-- Live View Dialog -->
    <el-dialog v-model="liveDialogVisible" title="Live Telemetry Stream" width="900px" destroy-on-close>
      <div class="live-container">
        <div class="live-controls">
          <el-select v-model="liveDevice" placeholder="Select Device" style="width: 200px">
            <el-option label="Chiller-01" value="chiller_01" />
            <el-option label="AHU-03" value="ahu_03" />
            <el-option label="CT-02" value="ct_02" />
            <el-option label="Sensor Array A1" value="sensor_a1" />
          </el-select>
          <el-select v-model="liveMetric" placeholder="Select Metric" style="width: 150px">
            <el-option label="Temperature" value="temperature" />
            <el-option label="Humidity" value="humidity" />
            <el-option label="Pressure" value="pressure" />
            <el-option label="Vibration" value="vibration" />
          </el-select>
          <el-switch v-model="liveAutoRefresh" active-text="Auto Refresh" />
          <el-tag type="success" v-if="liveAutoRefresh">Live</el-tag>
        </div>
        <div ref="liveChartRef" class="live-chart-container"></div>
        <div class="live-latest">
          <span>Latest Value: <strong>{{ latestValue }}</strong></span>
          <span>Timestamp: {{ latestTimestamp }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="stopLiveStream">Stop</el-button>
        <el-button type="primary" @click="liveDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Filter, VideoCamera
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading telemetry data...',
  'Connecting to historian...',
  'Almost ready...'
]

// ==================== Chart References ====================
const realtimeChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const liveChartRef = ref<HTMLElement>()
let realtimeChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let liveChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const detailsDialogVisible = ref(false)
const trendDialogVisible = ref(false)
const liveDialogVisible = ref(false)
const currentRecord = ref<any>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const selectedMetric = ref('temperature')
const selectedDevice = ref('all')
const currentValue = ref('--')
const minValue = ref('--')
const maxValue = ref('--')
const avgValue = ref('--')

// Live view state
const liveDevice = ref('chiller_01')
const liveMetric = ref('temperature')
const liveAutoRefresh = ref(true)
const latestValue = ref('--')
const latestTimestamp = ref('--')
let liveInterval: any = null

const filters = reactive({
  deviceId: '',
  metricType: '',
  dataQuality: '',
  timeRange: null as [Date, Date] | null
})

const trendStats = reactive({
  mean: '--',
  median: '--',
  stdDev: '--',
  min: '--',
  max: '--',
  count: '--'
})

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Records', value: '2.45M', trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Active Devices', value: 156, trend: 8, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'devices' },
  { title: 'Ingestion Rate', value: '1,234/s', trend: 5, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'rate' },
  { title: 'Data Quality', value: '99.2%', trend: 0.5, icon: 'Checked', bgColor: '#f56c6c', key: 'quality' }
])

const telemetryData = ref([
  { id: 1, timestamp: '2024-01-20 08:00:00.123', deviceId: 'CH-01', deviceName: 'Chiller-01', metric: 'temperature', value: 22.5, unit: '°C', quality: 'good', source: 'BMS', protocol: 'BACnet', rawPayload: { value: 22.5, unit: 'C', timestamp: 1705737600123 } },
  { id: 2, timestamp: '2024-01-20 08:00:00.456', deviceId: 'CH-01', deviceName: 'Chiller-01', metric: 'pressure', value: 101.3, unit: 'kPa', quality: 'good', source: 'BMS', protocol: 'BACnet', rawPayload: { value: 101.3, unit: 'kPa', timestamp: 1705737600456 } },
  { id: 3, timestamp: '2024-01-20 08:00:01.234', deviceId: 'AHU-03', deviceName: 'Air Handler-03', metric: 'temperature', value: 18.2, unit: '°C', quality: 'good', source: 'SCADA', protocol: 'Modbus', rawPayload: { value: 18.2, unit: 'C', timestamp: 1705737601234 } },
  { id: 4, timestamp: '2024-01-20 08:00:01.567', deviceId: 'AHU-03', deviceName: 'Air Handler-03', metric: 'humidity', value: 45.2, unit: '%', quality: 'good', source: 'SCADA', protocol: 'Modbus', rawPayload: { value: 45.2, unit: '%', timestamp: 1705737601567 } },
  { id: 5, timestamp: '2024-01-20 08:00:02.000', deviceId: 'CT-02', deviceName: 'Cooling Tower-02', metric: 'vibration', value: 2.3, unit: 'mm/s', quality: 'suspect', source: 'IoT', protocol: 'MQTT', rawPayload: { value: 2.3, unit: 'mm/s', timestamp: 1705737602000 } },
  { id: 6, timestamp: '2024-01-20 08:00:02.345', deviceId: 'SEN-A1', deviceName: 'Sensor Array A1', metric: 'temperature', value: 23.1, unit: '°C', quality: 'good', source: 'IoT', protocol: 'MQTT', rawPayload: { value: 23.1, unit: 'C', timestamp: 1705737602345 } },
  { id: 7, timestamp: '2024-01-20 08:00:03.000', deviceId: 'SEN-A1', deviceName: 'Sensor Array A1', metric: 'humidity', value: 52.3, unit: '%', quality: 'good', source: 'IoT', protocol: 'MQTT', rawPayload: { value: 52.3, unit: '%', timestamp: 1705737603000 } },
  { id: 8, timestamp: '2024-01-20 08:00:03.500', deviceId: 'CH-01', deviceName: 'Chiller-01', metric: 'power', value: 45.2, unit: 'kW', quality: 'good', source: 'BMS', protocol: 'BACnet', rawPayload: { value: 45.2, unit: 'kW', timestamp: 1705737603500 } }
])

// Generate more mock data
for (let i = 9; i <= 100; i++) {
  const devices = [
    { id: 'CH-01', name: 'Chiller-01' },
    { id: 'AHU-03', name: 'Air Handler-03' },
    { id: 'CT-02', name: 'Cooling Tower-02' },
    { id: 'SEN-A1', name: 'Sensor Array A1' },
    { id: 'PMP-04', name: 'Pump-04' }
  ]
  const metrics = ['temperature', 'humidity', 'pressure', 'vibration', 'power', 'flow_rate']
  const qualities = ['good', 'good', 'good', 'suspect', 'bad']
  const device = devices[Math.floor(Math.random() * devices.length)]
  const metric = metrics[Math.floor(Math.random() * metrics.length)]

  telemetryData.value.push({
    id: i,
    timestamp: `2024-01-20 08:00:${Math.floor(Math.random() * 60)}.${Math.floor(Math.random() * 1000)}`,
    deviceId: device.id,
    deviceName: device.name,
    metric: metric,
    value: metric === 'temperature' ? (Math.random() * 30 + 10).toFixed(1) :
        metric === 'humidity' ? (Math.random() * 60 + 20).toFixed(1) :
            metric === 'pressure' ? (Math.random() * 50 + 80).toFixed(1) :
                metric === 'vibration' ? (Math.random() * 5 + 0.5).toFixed(1) :
                    metric === 'power' ? (Math.random() * 100 + 10).toFixed(1) :
                        (Math.random() * 100).toFixed(1),
    unit: metric === 'temperature' ? '°C' : metric === 'humidity' ? '%' : metric === 'pressure' ? 'kPa' : metric === 'vibration' ? 'mm/s' : metric === 'power' ? 'kW' : 'm³/h',
    quality: qualities[Math.floor(Math.random() * qualities.length)],
    source: Math.random() > 0.5 ? 'BMS' : 'IoT',
    protocol: Math.random() > 0.5 ? 'BACnet' : 'MQTT',
    rawPayload: { value: Math.random() * 100, timestamp: Date.now() }
  })
}

telemetryData.value.sort((a, b) => a.timestamp.localeCompare(b.timestamp))

// ==================== Computed ====================
const filteredData = computed(() => {
  let filtered = [...telemetryData.value]

  if (filters.deviceId) {
    filtered = filtered.filter(d => d.deviceId.toLowerCase().includes(filters.deviceId.toLowerCase()))
  }

  if (filters.metricType) {
    filtered = filtered.filter(d => d.metric === filters.metricType)
  }

  if (filters.dataQuality) {
    filtered = filtered.filter(d => d.quality === filters.dataQuality)
  }

  if (filters.timeRange && filters.timeRange[0] && filters.timeRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.timestamp)
      return date >= filters.timeRange![0] && date <= filters.timeRange![1]
    })
  }

  return filtered
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

// ==================== Helper Methods ====================
const formatMetricName = (metric: string) => {
  const map: Record<string, string> = {
    'temperature': 'Temperature',
    'humidity': 'Humidity',
    'pressure': 'Pressure',
    'vibration': 'Vibration',
    'power': 'Power',
    'flow_rate': 'Flow Rate'
  }
  return map[metric] || metric
}

const getMetricTag = (metric: string) => {
  const map: Record<string, string> = {
    'temperature': 'danger',
    'humidity': 'primary',
    'pressure': 'success',
    'vibration': 'warning',
    'power': 'info',
    'flow_rate': 'success'
  }
  return map[metric] || 'info'
}

const getQualityTag = (quality: string) => {
  const map: Record<string, string> = {
    'good': 'success',
    'suspect': 'warning',
    'bad': 'danger'
  }
  return map[quality] || 'info'
}

const getValueClass = (row: any) => {
  if (row.quality === 'bad') return 'value-bad'
  if (row.quality === 'suspect') return 'value-suspect'
  return 'value-good'
}

// ==================== Chart Initializations ====================
const initRealtimeChart = () => {
  if (!realtimeChartRef.value) return
  if (realtimeChart) realtimeChart.dispose()

  realtimeChart = echarts.init(realtimeChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time', name: 'Time' },
    yAxis: { type: 'value', name: 'Value' },
    series: [{
      type: 'line',
      data: [],
      smooth: true,
      lineStyle: { width: 2, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 6
    }]
  }

  realtimeChart.setOption(option)
  window.addEventListener('resize', () => realtimeChart?.resize())

  // Simulate real-time data
  startRealtimeSimulation()
}

const startRealtimeSimulation = () => {
  setInterval(() => {
    if (realtimeChart) {
      const newData = telemetryData.value
          .filter(d => d.metric === selectedMetric.value && (selectedDevice.value === 'all' || d.deviceId === selectedDevice.value))
          .slice(-50)
          .map(d => [new Date(d.timestamp).getTime(), parseFloat(d.value as string)])

      realtimeChart.setOption({
        series: [{ data: newData }]
      })

      // Update stats
      const values = newData.map(d => d[1])
      if (values.length) {
        currentValue.value = values[values.length - 1].toFixed(1)
        minValue.value = Math.min(...values).toFixed(1)
        maxValue.value = Math.max(...values).toFixed(1)
        avgValue.value = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1)
      }
    }
  }, 3000)
}

const refreshChart = () => {
  startRealtimeSimulation()
  ElMessage.success('Chart refreshed')
}

const initLiveChart = () => {
  if (!liveChartRef.value) return
  if (liveChart) liveChart.dispose()

  liveChart = echarts.init(liveChartRef.value)

  liveChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'time', name: 'Time' },
    yAxis: { type: 'value', name: 'Value' },
    series: [{ type: 'line', data: [], smooth: true, lineStyle: { width: 2, color: '#f56c6c' }, symbolSize: 6 }]
  })

  startLiveSimulation()
}

const startLiveSimulation = () => {
  if (liveInterval) clearInterval(liveInterval)

  liveInterval = setInterval(() => {
    if (liveChart && liveAutoRefresh.value) {
      const newValue = liveMetric.value === 'temperature' ? (Math.random() * 30 + 10).toFixed(1) :
          liveMetric.value === 'humidity' ? (Math.random() * 60 + 20).toFixed(1) :
              (Math.random() * 100 + 50).toFixed(1)

      const newTimestamp = Date.now()
      const currentData = (liveChart.getOption() as any).series[0].data || []
      const newData = [...currentData, [newTimestamp, parseFloat(newValue)]].slice(-50)

      liveChart.setOption({
        series: [{ data: newData }]
      })

      latestValue.value = newValue
      latestTimestamp.value = new Date(newTimestamp).toLocaleTimeString()
    }
  }, 1000)
}

const stopLiveStream = () => {
  if (liveInterval) {
    clearInterval(liveInterval)
    liveInterval = null
  }
  liveAutoRefresh.value = false
  ElMessage.info('Live stream stopped')
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.deviceId = ''
  filters.metricType = ''
  filters.dataQuality = ''
  filters.timeRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredData.value.length} telemetry records...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleLiveView = () => {
  liveDialogVisible.value = true
  nextTick(() => {
    initLiveChart()
  })
}

const fetchData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const viewDetails = (record: any) => {
  currentRecord.value = record
  detailsDialogVisible.value = true
}

const trendAnalysis = (record: any) => {
  trendDialogVisible.value = true
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)

      const historicalData = telemetryData.value
          .filter(d => d.metric === record.metric && d.deviceId === record.deviceId)
          .slice(-100)
          .map(d => [new Date(d.timestamp).getTime(), parseFloat(d.value as string)])

      trendChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'time', name: 'Time' },
        yAxis: { type: 'value', name: `Value (${record.unit})` },
        series: [{ type: 'line', data: historicalData, smooth: true, lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.1 } }]
      })

      const values = historicalData.map(d => d[1])
      trendStats.mean = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2)
      trendStats.median = values.sort((a, b) => a - b)[Math.floor(values.length / 2)].toFixed(2)
      trendStats.stdDev = Math.sqrt(values.map(v => Math.pow(v - parseFloat(trendStats.mean), 2)).reduce((a, b) => a + b, 0) / values.length).toFixed(2)
      trendStats.min = Math.min(...values).toFixed(2)
      trendStats.max = Math.max(...values).toFixed(2)
      trendStats.count = values.length.toString()
    }
  })
}

const exportRecord = () => {
  ElMessage.success('Record exported')
}

const exportTrend = () => {
  ElMessage.success('Trend data exported')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initRealtimeChart()
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
      fetchData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (liveInterval) {
    clearInterval(liveInterval)
  }
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

/* ==================== Main Page Styles ==================== */
.raw-telemetry-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

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

  .header-actions {
    display: flex;
    gap: 12px;
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

.chart-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;

    .chart-controls {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .realtime-chart-container {
    width: 100%;
    height: 350px;
  }

  .chart-stats {
    display: flex;
    gap: 24px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #ebeef5;

    span {
      font-size: 14px;
      color: #606266;
    }

    strong {
      color: #303133;
      font-size: 16px;
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.value-good {
  color: #67c23a;
  font-weight: 500;
}

.value-suspect {
  color: #e6a23c;
  font-weight: 500;
}

.value-bad {
  color: #f56c6c;
  font-weight: 500;
}

.telemetry-details {
  .raw-payload {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    overflow-x: auto;
    margin: 0;
  }
}

.trend-container {
  .trend-chart-container {
    width: 100%;
    height: 400px;
    margin-bottom: 20px;
  }
}

.live-container {
  .live-controls {
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }

  .live-chart-container {
    width: 100%;
    height: 350px;
  }

  .live-latest {
    display: flex;
    gap: 24px;
    margin-top: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    span {
      font-size: 14px;
    }

    strong {
      font-size: 18px;
      color: #f56c6c;
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>