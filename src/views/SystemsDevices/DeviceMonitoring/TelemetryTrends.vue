<template>
  <!-- ==================== Loading Screen ==================== -->
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
        <div class="loading-tip">Telemetry Trends</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- ==================== Main Content ==================== -->
  <div v-else class="telemetry-trends-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/systems-devices/device-inventory' }">
            Systems & Devices
          </el-breadcrumb-item>
          <el-breadcrumb-item>Device Monitoring</el-breadcrumb-item>
          <el-breadcrumb-item>Telemetry Trends</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button :icon="Refresh" @click="refreshData" :loading="refreshing">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportData">Export Report</el-button>
      </div>
    </div>

    <!-- 设备选择和筛选 -->
    <div class="selection-panel">
      <div class="selection-row">
        <div class="selection-item">
          <label>Device</label>
          <el-select
              v-model="selectedDeviceId"
              placeholder="Select device"
              filterable
              clearable
              style="width: 280px"
              @change="onDeviceChange"
          >
            <el-option
                v-for="device in deviceList"
                :key="device.id"
                :label="`${device.name} (${device.model})`"
                :value="device.id"
            >
              <div class="device-option">
                <span class="status-dot" :class="device.status"></span>
                <span>{{ device.name }}</span>
                <span class="option-model">{{ device.model }}</span>
              </div>
            </el-option>
          </el-select>
        </div>
        <div class="selection-item">
          <label>Metric</label>
          <el-select
              v-model="selectedMetrics"
              placeholder="Select metrics"
              multiple
              collapse-tags
              collapse-tags-tooltip
              style="width: 300px"
              @change="onMetricChange"
          >
            <el-option label="Temperature (°C)" value="temperature" />
            <el-option label="Power (kW)" value="power" />
            <el-option label="Humidity (%)" value="humidity" />
            <el-option label="Efficiency (%)" value="efficiency" />
            <el-option label="Pressure (kPa)" value="pressure" />
            <el-option label="Flow Rate (m³/h)" value="flowRate" />
            <el-option label="CO₂ Level (ppm)" value="co2" />
            <el-option label="Vibration (mm/s)" value="vibration" />
          </el-select>
        </div>
        <div class="selection-item">
          <label>Time Range</label>
          <el-select v-model="timeRange" style="width: 150px" @change="onTimeRangeChange">
            <el-option label="Last 24 Hours" value="24h" />
            <el-option label="Last 3 Days" value="3d" />
            <el-option label="Last 7 Days" value="7d" />
            <el-option label="Last 30 Days" value="30d" />
            <el-option label="Last 90 Days" value="90d" />
            <el-option label="Custom" value="custom" />
          </el-select>
        </div>
        <div v-if="timeRange === 'custom'" class="selection-item">
          <label>Custom Range</label>
          <el-date-picker
              v-model="customDateRange"
              type="daterange"
              range-separator="-"
              start-placeholder="Start"
              end-placeholder="End"
              style="width: 260px"
              @change="onCustomRangeChange"
          />
        </div>
        <div class="selection-item">
          <label>Aggregation</label>
          <el-select v-model="aggregation" style="width: 120px" @change="refreshCharts">
            <el-option label="Raw" value="raw" />
            <el-option label="Hourly Avg" value="hourly" />
            <el-option label="Daily Avg" value="daily" />
            <el-option label="Weekly Avg" value="weekly" />
            <el-option label="Monthly Avg" value="monthly" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards" v-if="selectedDevice">
      <div class="stat-card">
        <div class="stat-icon"><el-icon><ColdDrink /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ currentStats.temperature }}°C</span>
          <span class="stat-label">Current Temp</span>
        </div>
        <div class="stat-change" :class="getChangeClass(currentStats.tempChange)">
          {{ formatChange(currentStats.tempChange) }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Odometer /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ currentStats.power }} kW</span>
          <span class="stat-label">Current Power</span>
        </div>
        <div class="stat-change" :class="getChangeClass(currentStats.powerChange)">
          {{ formatChange(currentStats.powerChange) }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><Sunny /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ currentStats.humidity }}%</span>
          <span class="stat-label">Current Humidity</span>
        </div>
        <div class="stat-change" :class="getChangeClass(currentStats.humidityChange)">
          {{ formatChange(currentStats.humidityChange) }}
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon"><el-icon><MagicStick /></el-icon></div>
        <div class="stat-info">
          <span class="stat-value">{{ currentStats.efficiency }}%</span>
          <span class="stat-label">Current Efficiency</span>
        </div>
        <div class="stat-change" :class="getChangeClass(currentStats.efficiencyChange)">
          {{ formatChange(currentStats.efficiencyChange) }}
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 主趋势图 -->
      <div class="chart-card main-chart">
        <div class="chart-header">
          <h3><el-icon><TrendCharts /></el-icon> Telemetry Trends</h3>
          <div class="chart-actions">
            <el-radio-group v-model="chartType" size="small" @change="refreshCharts">
              <el-radio-button value="line">Line</el-radio-button>
              <el-radio-button value="area">Area</el-radio-button>
              <el-radio-button value="bar">Bar</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div ref="mainChartRef" class="main-chart-container"></div>
      </div>

      <!-- 多指标对比图 -->
      <div class="chart-card comparison-chart">
        <div class="chart-header">
          <h3><el-icon><DataAnalysis /></el-icon> Multi-Metric Comparison</h3>
          <el-button size="small" text @click="toggleComparisonMetrics">Select Metrics</el-button>
        </div>
        <div ref="comparisonChartRef" class="comparison-chart-container"></div>
      </div>

      <!-- 统计分析 -->
      <div class="stats-panel">
        <div class="stats-header">
          <h3><el-icon><DataLine /></el-icon> Statistical Analysis</h3>
          <span class="stats-period">{{ timeRangeLabel }}</span>
        </div>
        <el-table :data="statisticsData" stripe size="small" style="width: 100%">
          <el-table-column prop="metric" label="Metric" />
          <el-table-column prop="min" label="Min">
            <template #default="{ row }">{{ row.min }}{{ row.unit }}</template>
          </el-table-column>
          <el-table-column prop="max" label="Max">
            <template #default="{ row }">{{ row.max }}{{ row.unit }}</template>
          </el-table-column>
          <el-table-column prop="avg" label="Average">
            <template #default="{ row }">{{ row.avg }}{{ row.unit }}</template>
          </el-table-column>
          <el-table-column prop="median" label="Median">
            <template #default="{ row }">{{ row.median }}{{ row.unit }}</template>
          </el-table-column>
          <el-table-column prop="stdDev" label="Std Dev">
            <template #default="{ row }">{{ row.stdDev }}{{ row.unit }}</template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 异常检测 -->
      <div class="anomaly-panel" v-if="anomalies.length > 0">
        <div class="anomaly-header">
          <h3><el-icon><WarningFilled /></el-icon> Anomaly Detection</h3>
          <el-tag type="danger">{{ anomalies.length }} anomalies detected</el-tag>
        </div>
        <div class="anomaly-list">
          <div v-for="anomaly in anomalies" :key="anomaly.id" class="anomaly-item">
            <div class="anomaly-icon"><el-icon><WarningFilled /></el-icon></div>
            <div class="anomaly-content">
              <div class="anomaly-title">{{ anomaly.metric }} - {{ anomaly.type }}</div>
              <div class="anomaly-detail">Value: {{ anomaly.value }} at {{ formatDateTime(anomaly.timestamp) }}</div>
              <div class="anomaly-recommendation">Recommendation: {{ anomaly.recommendation }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据导出区域 -->
      <div class="export-panel">
        <div class="export-header">
          <h3><el-icon><Download /></el-icon> Export Data</h3>
        </div>
        <div class="export-options">
          <el-button :icon="Download" @click="exportCSV">Export as CSV</el-button>
          <el-button :icon="Download" @click="exportExcel">Export as Excel</el-button>
          <el-button :icon="Download" @click="exportPDF">Export as PDF</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, TrendCharts, DataAnalysis, DataLine,
  ColdDrink, Odometer, Sunny, MagicStick, WarningFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading telemetry data...')
const refreshing = ref(false)
const loadingMessages = ['Initializing...', 'Loading device data...', 'Fetching telemetry...', 'Rendering charts...', 'Almost ready...']

// ==================== State ====================
const selectedDeviceId = ref('')
const selectedMetrics = ref(['temperature', 'power', 'efficiency'])
const timeRange = ref('24h')
const customDateRange = ref<[Date, Date] | null>(null)
const aggregation = ref('hourly')
const chartType = ref('line')
let mainChart: echarts.ECharts | null = null
let comparisonChart: echarts.ECharts | null = null
const mainChartRef = ref<HTMLElement>()
const comparisonChartRef = ref<HTMLElement>()
let refreshTimer: number

// ==================== Data ====================
interface Device {
  id: string
  name: string
  model: string
  manufacturer: string
  status: string
  systemType: string
}

interface TelemetryDataPoint {
  timestamp: string
  temperature: number
  power: number
  humidity: number
  efficiency: number
  pressure?: number
  flowRate?: number
  co2?: number
  vibration?: number
}

interface Anomaly {
  id: string
  metric: string
  type: string
  value: number
  timestamp: string
  recommendation: string
}

const deviceList = ref<Device[]>([
  { id: '1', name: 'AHU-B2-01 Air Handler', model: 'Carrier 39G', manufacturer: 'Carrier', status: 'online', systemType: 'hvac' },
  { id: '2', name: 'FCU-B2-01 Fan Coil', model: 'Daikin FXMQ', manufacturer: 'Daikin', status: 'online', systemType: 'hvac' },
  { id: '3', name: 'CH-B2-01 Chiller', model: 'Carrier AquaEdge', manufacturer: 'Carrier', status: 'warning', systemType: 'hvac' },
  { id: '4', name: 'EF-B2-02 Exhaust Fan', model: 'Greenheck CUBE', manufacturer: 'Greenheck', status: 'error', systemType: 'hvac' },
  { id: '5', name: 'LIGHT-B2-01 Controller', model: 'Philips Dynalite', manufacturer: 'Philips', status: 'online', systemType: 'lighting' },
  { id: '6', name: 'PUMP-B2-02 Booster', model: 'Grundfos CR', manufacturer: 'Grundfos', status: 'warning', systemType: 'plumbing' }
])

const telemetryData = ref<TelemetryDataPoint[]>([])
const anomalies = ref<Anomaly[]>([])

// 获取时间范围的小时数
const getHoursFromRange = (range: string): number => {
  switch (range) {
    case '24h': return 24
    case '3d': return 72
    case '7d': return 168
    case '30d': return 720
    case '90d': return 2160
    default: return 24
  }
}

// 格式化时间标签 - 修复NaN问题
const formatTimeLabel = (timestamp: string, aggType: string): string => {
  const date = new Date(timestamp)
  if (isNaN(date.getTime())) {
    // 如果日期无效，返回原始字符串
    return timestamp
  }

  if (aggType === 'daily') {
    return `${date.getMonth() + 1}/${date.getDate()}`
  }
  if (aggType === 'hourly') {
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`
  }
  if (aggType === 'monthly') {
    return `${date.getFullYear()}-${date.getMonth() + 1}`
  }
  // 默认格式
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`
}

// 生成模拟遥测数据
const generateTelemetryData = (deviceId: string, range: string): TelemetryDataPoint[] => {
  const now = new Date()
  const hours = getHoursFromRange(range)
  const interval = 3600000 // 1 hour

  const data: TelemetryDataPoint[] = []
  const device = deviceList.value.find(d => d.id === deviceId)
  const isHVAC = device?.systemType === 'hvac'

  for (let i = hours; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * interval)
    const hourOfDay = timestamp.getHours()
    const dayOfWeek = timestamp.getDay()
    const isBusinessHour = hourOfDay >= 8 && hourOfDay <= 18
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6

    // 基础值
    let baseTemp = 22
    let basePower = 10
    let baseHumidity = 50
    let baseEfficiency = 92

    if (device?.systemType === 'hvac') {
      baseTemp = 23
      basePower = 15
    } else if (device?.systemType === 'lighting') {
      basePower = 5
    } else if (device?.systemType === 'plumbing') {
      baseTemp = 28
      basePower = 8
    }

    // 业务时段影响
    const businessFactor = isBusinessHour && !isWeekend ? 1.3 : 0.7
    const randomFactor = () => 0.85 + Math.random() * 0.3

    data.push({
      timestamp: timestamp.toISOString(),
      temperature: +(baseTemp * (isBusinessHour ? 1.1 : 0.9) * randomFactor()).toFixed(1),
      power: +(basePower * businessFactor * randomFactor()).toFixed(1),
      humidity: +(baseHumidity * (isBusinessHour ? 1.05 : 0.95) * randomFactor()).toFixed(0),
      efficiency: +(Math.min(98, baseEfficiency * (isBusinessHour ? 0.98 : 1.02) * randomFactor())).toFixed(1),
      pressure: isHVAC ? +(250 + (Math.random() - 0.5) * 50).toFixed(0) : undefined,
      flowRate: isHVAC ? +(1000 + Math.random() * 500).toFixed(0) : undefined,
      co2: device?.systemType === 'fas' ? +(400 + Math.random() * 100).toFixed(0) : undefined,
      vibration: device?.systemType === 'hvac' ? +(0.5 + Math.random() * 2).toFixed(1) : undefined
    })
  }
  return data
}

// 检测异常
const detectAnomalies = (data: TelemetryDataPoint[]): Anomaly[] => {
  const anomaliesList: Anomaly[] = []
  const metrics = ['temperature', 'power', 'efficiency']

  metrics.forEach(metric => {
    const values = data.map(d => d[metric as keyof TelemetryDataPoint] as number).filter(v => v !== undefined)
    if (values.length === 0) return

    const mean = values.reduce((a, b) => a + b, 0) / values.length
    const stdDev = Math.sqrt(values.map(v => Math.pow(v - mean, 2)).reduce((a, b) => a + b, 0) / values.length)
    const threshold = mean + 2 * stdDev
    const lowerThreshold = mean - 2 * stdDev

    data.forEach((point, idx) => {
      const value = point[metric as keyof TelemetryDataPoint] as number
      if (value !== undefined) {
        if (value > threshold) {
          anomaliesList.push({
            id: `${metric}-${idx}-${Date.now()}`,
            metric: getMetricLabel(metric),
            type: 'High Value',
            value: value,
            timestamp: point.timestamp,
            recommendation: `Investigate high ${getMetricLabel(metric)} reading. Possible equipment issue.`
          })
        } else if (value < lowerThreshold) {
          anomaliesList.push({
            id: `${metric}-${idx}-${Date.now()}`,
            metric: getMetricLabel(metric),
            type: 'Low Value',
            value: value,
            timestamp: point.timestamp,
            recommendation: `Low ${getMetricLabel(metric)} detected. Check sensor calibration.`
          })
        }
      }
    })
  })

  return anomaliesList.slice(0, 10)
}

// 聚合数据
const aggregateData = (data: TelemetryDataPoint[], aggType: string): TelemetryDataPoint[] => {
  if (aggType === 'raw') return data

  const grouped: Map<string, TelemetryDataPoint[]> = new Map()

  data.forEach(point => {
    const date = new Date(point.timestamp)
    if (isNaN(date.getTime())) return

    let key: string
    if (aggType === 'hourly') {
      key = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()} ${date.getHours()}:00`
    } else if (aggType === 'daily') {
      key = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`
    } else if (aggType === 'weekly') {
      const weekNum = Math.ceil(date.getDate() / 7)
      key = `${date.getFullYear()}-W${weekNum}`
    } else {
      key = `${date.getFullYear()}-${date.getMonth() + 1}`
    }

    if (!grouped.has(key)) grouped.set(key, [])
    grouped.get(key)!.push(point)
  })

  const aggregated: TelemetryDataPoint[] = []
  for (const [key, points] of grouped) {
    const avgPoint: TelemetryDataPoint = {
      timestamp: key,
      temperature: parseFloat((points.reduce((s, p) => s + p.temperature, 0) / points.length).toFixed(1)),
      power: parseFloat((points.reduce((s, p) => s + p.power, 0) / points.length).toFixed(1)),
      humidity: Math.round(points.reduce((s, p) => s + p.humidity, 0) / points.length),
      efficiency: parseFloat((points.reduce((s, p) => s + p.efficiency, 0) / points.length).toFixed(1))
    }
    if (points[0].pressure !== undefined) {
      avgPoint.pressure = Math.round(points.reduce((s, p) => s + (p.pressure || 0), 0) / points.length)
    }
    if (points[0].flowRate !== undefined) {
      avgPoint.flowRate = Math.round(points.reduce((s, p) => s + (p.flowRate || 0), 0) / points.length)
    }
    aggregated.push(avgPoint)
  }

  return aggregated
}

// 当前统计
const currentStats = computed(() => {
  if (telemetryData.value.length === 0) {
    return { temperature: 0, power: 0, humidity: 0, efficiency: 0, tempChange: 0, powerChange: 0, humidityChange: 0, efficiencyChange: 0 }
  }
  const latest = telemetryData.value[telemetryData.value.length - 1]
  const previous = telemetryData.value[telemetryData.value.length - 2] || latest
  return {
    temperature: latest.temperature,
    power: latest.power,
    humidity: latest.humidity,
    efficiency: latest.efficiency,
    tempChange: previous.temperature ? ((latest.temperature - previous.temperature) / previous.temperature) * 100 : 0,
    powerChange: previous.power ? ((latest.power - previous.power) / previous.power) * 100 : 0,
    humidityChange: latest.humidity - previous.humidity,
    efficiencyChange: latest.efficiency - previous.efficiency
  }
})

// 统计分析数据
const statisticsData = computed(() => {
  const data = telemetryData.value
  if (data.length === 0) return []

  const metrics = [
    { key: 'temperature', label: 'Temperature (°C)', unit: '°C' },
    { key: 'power', label: 'Power (kW)', unit: ' kW' },
    { key: 'humidity', label: 'Humidity (%)', unit: '%' },
    { key: 'efficiency', label: 'Efficiency (%)', unit: '%' }
  ]

  return metrics.map(metric => {
    const values = data.map(d => d[metric.key as keyof TelemetryDataPoint] as number).filter(v => v !== undefined && !isNaN(v))
    if (values.length === 0) {
      return { metric: metric.label, unit: metric.unit, min: '-', max: '-', avg: '-', median: '-', stdDev: '-' }
    }
    const sorted = [...values].sort((a, b) => a - b)
    const sum = values.reduce((a, b) => a + b, 0)
    const mean = sum / values.length
    const variance = values.map(v => Math.pow(v - mean, 2)).reduce((a, b) => a + b, 0) / values.length

    return {
      metric: metric.label,
      unit: metric.unit,
      min: Math.min(...values).toFixed(1),
      max: Math.max(...values).toFixed(1),
      avg: mean.toFixed(1),
      median: sorted[Math.floor(sorted.length / 2)]?.toFixed(1) || '-',
      stdDev: Math.sqrt(variance).toFixed(2)
    }
  })
})

const timeRangeLabel = computed(() => {
  const labels: Record<string, string> = { '24h': 'Last 24 Hours', '3d': 'Last 3 Days', '7d': 'Last 7 Days', '30d': 'Last 30 Days', '90d': 'Last 90 Days' }
  return labels[timeRange.value] || 'Custom Range'
})

// Helper函数
const getMetricLabel = (key: string): string => {
  const labels: Record<string, string> = {
    temperature: 'Temperature', power: 'Power', humidity: 'Humidity',
    efficiency: 'Efficiency', pressure: 'Pressure', flowRate: 'Flow Rate',
    co2: 'CO₂ Level', vibration: 'Vibration'
  }
  return labels[key] || key
}

const getChangeClass = (change: number) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return ''
}

const formatChange = (change: number) => {
  if (change === 0 || isNaN(change)) return '0%'
  return `${change > 0 ? '+' : ''}${change.toFixed(1)}%`
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  if (isNaN(date.getTime())) return dateStr
  return date.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// 获取x轴数据 - 修复NaN问题
const getXAxisData = (): string[] => {
  const data = telemetryData.value
  if (data.length === 0) return []

  return data.map(point => {
    if (aggregation.value === 'daily') {
      const date = new Date(point.timestamp)
      if (isNaN(date.getTime())) return point.timestamp
      return `${date.getMonth() + 1}/${date.getDate()}`
    }
    if (aggregation.value === 'hourly') {
      const date = new Date(point.timestamp)
      if (isNaN(date.getTime())) return point.timestamp
      return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`
    }
    if (aggregation.value === 'monthly') {
      const date = new Date(point.timestamp)
      if (isNaN(date.getTime())) return point.timestamp
      return `${date.getFullYear()}-${date.getMonth() + 1}`
    }
    // raw data
    const date = new Date(point.timestamp)
    if (isNaN(date.getTime())) return point.timestamp
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:00`
  })
}

// 图表初始化
const initMainChart = () => {
  if (!mainChartRef.value) return
  if (mainChart) mainChart.dispose()
  mainChart = echarts.init(mainChartRef.value)

  const data = telemetryData.value
  if (data.length === 0) return

  const xAxisData = getXAxisData()

  // 如果x轴数据有问题，不渲染
  if (xAxisData.length === 0 || xAxisData.some(x => x === 'Invalid Date' || x === 'NaN')) {
    console.warn('Invalid xAxis data')
    return
  }

  const series = selectedMetrics.value.map(metric => ({
    name: getMetricLabel(metric),
    type: chartType.value === 'bar' ? 'bar' : 'line',
    data: data.map(d => {
      const val = d[metric as keyof TelemetryDataPoint] as number
      return isNaN(val) ? 0 : val
    }),
    smooth: chartType.value === 'line',
    symbol: chartType.value === 'line' ? 'circle' : 'none',
    symbolSize: 4,
    lineStyle: { width: 2 },
    areaStyle: chartType.value === 'area' ? { opacity: 0.1 } : undefined
  }))

  const colors: Record<string, string> = { temperature: '#f56c6c', power: '#e6a23c', humidity: '#409eff', efficiency: '#67c23a' }

  mainChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: series.map(s => s.name), top: 0, right: 0 },
    grid: { top: 50, right: 20, bottom: 30, left: 50, containLabel: true },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: 45, interval: Math.floor(xAxisData.length / 10) } },
    yAxis: { type: 'value', name: 'Value' },
    series: series.map(s => ({ ...s, itemStyle: { color: colors[s.name.toLowerCase()] || '#409eff' } }))
  })
}

const initComparisonChart = () => {
  if (!comparisonChartRef.value) return
  if (comparisonChart) comparisonChart.dispose()
  comparisonChart = echarts.init(comparisonChartRef.value)

  const data = telemetryData.value
  if (data.length === 0) return

  // 采样数据点，避免过多
  const step = Math.max(1, Math.floor(data.length / 20))
  const sampledData = data.filter((_, i) => i % step === 0)

  const xAxisData = sampledData.map(point => {
    const date = new Date(point.timestamp)
    if (isNaN(date.getTime())) return point.timestamp
    return `${date.getMonth() + 1}/${date.getDate()}`
  })

  comparisonChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature', 'Power', 'Efficiency'], top: 0 },
    grid: { top: 50, right: 20, bottom: 30, left: 50, containLabel: true },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: 45 } },
    yAxis: [
      { type: 'value', name: 'Temperature (°C)' },
      { type: 'value', name: 'Power (kW) / Efficiency (%)' }
    ],
    series: [
      { name: 'Temperature', type: 'line', data: sampledData.map(d => d.temperature), yAxisIndex: 0, lineStyle: { color: '#f56c6c', width: 2 }, symbol: 'circle' },
      { name: 'Power', type: 'line', data: sampledData.map(d => d.power), yAxisIndex: 1, lineStyle: { color: '#e6a23c', width: 2 }, symbol: 'diamond' },
      { name: 'Efficiency', type: 'line', data: sampledData.map(d => d.efficiency), yAxisIndex: 1, lineStyle: { color: '#67c23a', width: 2 }, symbol: 'triangle' }
    ]
  })
}

// 数据加载
const loadData = async () => {
  if (!selectedDeviceId.value) return
  refreshing.value = true

  await new Promise(resolve => setTimeout(resolve, 500))
  let newData = generateTelemetryData(selectedDeviceId.value, timeRange.value)

  if (aggregation.value !== 'raw') {
    newData = aggregateData(newData, aggregation.value)
  }

  telemetryData.value = newData
  anomalies.value = detectAnomalies(telemetryData.value)

  await nextTick()
  initMainChart()
  initComparisonChart()
  refreshing.value = false
}

const onDeviceChange = () => { if (selectedDeviceId.value) loadData() }
const onMetricChange = () => initMainChart()
const onTimeRangeChange = () => loadData()
const onCustomRangeChange = () => { if (customDateRange.value) loadData() }
const refreshCharts = () => { initMainChart(); initComparisonChart() }
const refreshData = () => loadData()

// 导出功能
const exportData = () => ElMessage.info('Generating report...')
const exportCSV = () => ElMessage.success('CSV export started')
const exportExcel = () => ElMessage.success('Excel export started')
const exportPDF = () => ElMessage.success('PDF export started')
const toggleComparisonMetrics = () => ElMessage.info('Select metrics for comparison')

// 自动刷新
const startAutoRefresh = () => {
  refreshTimer = window.setInterval(() => {
    if (selectedDeviceId.value) {
      let newData = generateTelemetryData(selectedDeviceId.value, timeRange.value)
      if (aggregation.value !== 'raw') {
        newData = aggregateData(newData, aggregation.value)
      }
      telemetryData.value = newData
      anomalies.value = detectAnomalies(telemetryData.value)
      initMainChart()
      initComparisonChart()
    }
  }, 30000)
}

// 窗口大小适配
const handleResize = () => {
  if (mainChart) mainChart.resize()
  if (comparisonChart) comparisonChart.resize()
}

// 生命周期
onMounted(() => {
  let msgIdx = 0
  const msgInt = setInterval(() => {
    if (msgIdx < loadingMessages.length - 1) {
      msgIdx++
      loadingMessage.value = loadingMessages[msgIdx]
    }
  }, 400)

  const progInt = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(msgInt)
    clearInterval(progInt)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      if (deviceList.value.length) {
        selectedDeviceId.value = deviceList.value[0].id
        loadData()
      }
      startAutoRefresh()
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  clearInterval(refreshTimer)
  window.removeEventListener('resize', handleResize)
  if (mainChart) mainChart.dispose()
  if (comparisonChart) comparisonChart.dispose()
})

watch(selectedMetrics, () => initMainChart())
watch(chartType, () => initMainChart())
watch(aggregation, () => loadData())
</script>

<style scoped>
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
.loading-overlay { position: relative; width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.telemetry-trends-page { padding: 20px; background: #f5f7fa; min-height: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px; }

.selection-panel { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.selection-row { display: flex; flex-wrap: wrap; gap: 20px; align-items: flex-end; }
.selection-item { display: flex; flex-direction: column; gap: 6px; }
.selection-item label { font-size: 12px; font-weight: 500; color: #64748b; }
.device-option { display: flex; align-items: center; gap: 8px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; }
.status-dot.online { background: #10b981; }
.status-dot.warning { background: #f59e0b; }
.status-dot.error { background: #ef4444; }
.option-model { font-size: 11px; color: #94a3b8; margin-left: auto; }

.stats-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
.stat-card { background: white; border-radius: 16px; padding: 20px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); }
.stat-icon .el-icon { font-size: 32px; color: #3b82f6; }
.stat-info { text-align: center; }
.stat-value { font-size: 28px; font-weight: 700; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }
.stat-change { font-size: 13px; font-weight: 500; }
.stat-change.positive { color: #10b981; }
.stat-change.negative { color: #ef4444; }

.charts-container { display: flex; flex-direction: column; gap: 20px; }
.chart-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.chart-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; }
.main-chart-container { width: 100%; height: 400px; }
.comparison-chart-container { width: 100%; height: 300px; }

.stats-panel, .anomaly-panel, .export-panel { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); }
.stats-header, .anomaly-header, .export-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.stats-header h3, .anomaly-header h3, .export-header h3 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 16px; }
.stats-period { font-size: 12px; color: #94a3b8; }

.anomaly-list { display: flex; flex-direction: column; gap: 12px; max-height: 300px; overflow-y: auto; }
.anomaly-item { display: flex; gap: 12px; padding: 12px; background: #fef2f2; border-radius: 8px; border-left: 3px solid #ef4444; }
.anomaly-icon .el-icon { font-size: 20px; color: #ef4444; }
.anomaly-content { flex: 1; }
.anomaly-title { font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.anomaly-detail { font-size: 12px; color: #64748b; margin-bottom: 4px; }
.anomaly-recommendation { font-size: 12px; color: #3b82f6; }

.export-options { display: flex; gap: 12px; flex-wrap: wrap; }

@media (max-width: 1024px) { .stats-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .stats-cards { grid-template-columns: 1fr; }
  .selection-row { flex-direction: column; align-items: stretch; }
  .selection-item { width: 100%; }
  .selection-item .el-select, .selection-item .el-date-editor { width: 100% !important; }
  .main-chart-container { height: 300px; }
  .comparison-chart-container { height: 250px; }
}
</style>