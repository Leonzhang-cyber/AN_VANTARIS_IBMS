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
          <span class="loading-title">Smart Hygiene Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Odor / Occupancy / Consumables Monitoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="hygiene-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          Smart Hygiene Analytics
        </h1>
        <div class="page-subtitle">Real-time odor, occupancy & consumables monitoring dashboard</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Three Core Metrics - Gauge Style -->
    <div class="gauge-row">
      <div class="gauge-card">
        <div class="gauge-title">
          <el-icon><WindPower /></el-icon>
          Overall Odor Index
        </div>
        <div class="gauge-container">
          <div class="gauge-value" :class="getOdorClass(metrics.overallOdor)">
            {{ metrics.overallOdor }}
            <span class="gauge-unit">/10</span>
          </div>
          <div class="gauge-bar">
            <div class="gauge-fill" :style="{ width: (metrics.overallOdor * 10) + '%', background: getOdorGradient(metrics.overallOdor) }"></div>
          </div>
          <div class="gauge-labels">
            <span>Fresh</span>
            <span>Moderate</span>
            <span>Unpleasant</span>
            <span>Severe</span>
          </div>
        </div>
        <div class="gauge-footer">
          <span class="trend" :class="metrics.odorTrend > 0 ? 'negative' : 'positive'">
            {{ metrics.odorTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.odorTrend) }}% vs last hour
          </span>
        </div>
      </div>

      <div class="gauge-card">
        <div class="gauge-title">
          <el-icon><User /></el-icon>
          Overall Occupancy Rate
        </div>
        <div class="gauge-container">
          <div class="gauge-value" :class="getOccupancyClass(metrics.overallOccupancy)">
            {{ metrics.overallOccupancy }}<span class="gauge-unit">%</span>
          </div>
          <div class="gauge-bar">
            <div class="gauge-fill" :style="{ width: metrics.overallOccupancy + '%', background: getOccupancyGradient(metrics.overallOccupancy) }"></div>
          </div>
          <div class="gauge-labels">
            <span>Low</span>
            <span>Normal</span>
            <span>High</span>
            <span>Peak</span>
          </div>
        </div>
        <div class="gauge-footer">
          <span>Current: {{ metrics.activeUsers }} users</span>
          <span>Peak today: {{ metrics.peakOccupancy }}%</span>
        </div>
      </div>

      <div class="gauge-card">
        <div class="gauge-title">
          <el-icon><Tickets /></el-icon>
          Consumables Health
        </div>
        <div class="gauge-container">
          <div class="gauge-value" :class="getConsumablesClass(metrics.consumablesHealth)">
            {{ metrics.consumablesHealth }}<span class="gauge-unit">%</span>
          </div>
          <div class="gauge-bar">
            <div class="gauge-fill" :style="{ width: metrics.consumablesHealth + '%', background: getConsumablesGradient(metrics.consumablesHealth) }"></div>
          </div>
          <div class="gauge-labels">
            <span>Critical</span>
            <span>Low</span>
            <span>Good</span>
            <span>Optimal</span>
          </div>
        </div>
        <div class="gauge-footer">
          <span>{{ metrics.lowSoapCount }} low soap</span>
          <span>{{ metrics.lowTPCount }} low TP</span>
        </div>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-row">
      <div class="stat-mini-card">
        <div class="stat-mini-icon blue">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-mini-info">
          <div class="stat-mini-value">{{ stats.avgVisitDuration }}<span class="unit">min</span></div>
          <div class="stat-mini-label">Avg Visit Duration</div>
        </div>
      </div>
      <div class="stat-mini-card">
        <div class="stat-mini-icon green">
          <el-icon><TurnOff /></el-icon>
        </div>
        <div class="stat-mini-info">
          <div class="stat-mini-value">{{ stats.turnoverRate }}<span class="unit">/hr</span></div>
          <div class="stat-mini-label">Turnover Rate</div>
        </div>
      </div>
      <div class="stat-mini-card">
        <div class="stat-mini-icon orange">
          <el-icon><Delete /></el-icon>
        </div>
        <div class="stat-mini-info">
          <div class="stat-mini-value">{{ stats.dailyConsumablesUsage }}<span class="unit">units</span></div>
          <div class="stat-mini-label">Daily Consumables Usage</div>
        </div>
      </div>
      <div class="stat-mini-card">
        <div class="stat-mini-icon purple">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-mini-info">
          <div class="stat-mini-value">{{ stats.peakHour }}</div>
          <div class="stat-mini-label">Peak Hour</div>
        </div>
      </div>
    </div>

    <!-- Main Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">
            <el-icon><TrendCharts /></el-icon>
            Odor & Occupancy Trends
          </span>
          <span class="chart-subtitle">Last 24 hours</span>
        </div>
        <div class="chart-container" ref="trendChartEl" style="height: 320px"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">
            <el-icon><PieChart /></el-icon>
            Odor Sources
          </span>
          <span class="chart-subtitle">By location</span>
        </div>
        <div class="chart-container" ref="odorSourceChartEl" style="height: 320px"></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">
            <el-icon><Histogram /></el-icon>
            Consumables Consumption
          </span>
          <span class="chart-subtitle">Last 7 days</span>
        </div>
        <div class="chart-container" ref="consumptionChartEl" style="height: 300px"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">
            <el-icon><PieChart /></el-icon>
            Occupancy by Zone
          </span>
          <span class="chart-subtitle">Current status</span>
        </div>
        <div class="chart-container" ref="zoneOccupancyChartEl" style="height: 300px"></div>
      </div>
    </div>

    <!-- Real-time Sensors Grid -->
    <div class="section-header">
      <span class="section-title">
        <el-icon><Connection /></el-icon>
        Real-time Sensor Data
      </span>
      <el-button size="small" @click="viewAllSensors">View All Sensors →</el-button>
    </div>

    <div class="sensors-grid">
      <div
          v-for="sensor in filteredSensors"
          :key="sensor.id"
          class="sensor-card"
          :class="sensor.status"
      >
        <div class="sensor-header">
          <span class="sensor-name">{{ sensor.name }}</span>
          <span class="sensor-location">{{ sensor.location }}</span>
        </div>
        <div class="sensor-readings">
          <div class="reading">
            <span class="reading-label">Odor</span>
            <span class="reading-value" :class="getOdorClass(sensor.odorLevel)">
              {{ sensor.odorLevel }}/10
            </span>
            <div class="reading-bar">
              <div class="reading-fill" :style="{ width: (sensor.odorLevel * 10) + '%', background: getOdorGradient(sensor.odorLevel) }"></div>
            </div>
          </div>
          <div class="reading">
            <span class="reading-label">Occupancy</span>
            <span class="reading-value" :class="getOccupancyClass(sensor.occupancyRate)">
              {{ sensor.occupancyRate }}%
            </span>
            <div class="reading-bar">
              <div class="reading-fill" :style="{ width: sensor.occupancyRate + '%', background: getOccupancyGradient(sensor.occupancyRate) }"></div>
            </div>
          </div>
          <div class="reading-row">
            <div class="reading-small">
              <span class="reading-label">Soap</span>
              <el-progress :percentage="sensor.soapLevel" :stroke-width="6" :color="getProgressColor(sensor.soapLevel)" />
            </div>
            <div class="reading-small">
              <span class="reading-label">TP</span>
              <el-progress :percentage="sensor.tpLevel" :stroke-width="6" :color="getProgressColor(sensor.tpLevel)" />
            </div>
          </div>
        </div>
        <div class="sensor-footer">
          <span class="last-update">Updated: {{ sensor.lastUpdate }}</span>
          <el-button size="small" type="primary" link @click="viewSensorDetail(sensor)">Details</el-button>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="locationFilter" placeholder="Location" clearable style="width: 140px">
          <el-option label="Floor 1" value="Floor 1" />
          <el-option label="Floor 2" value="Floor 2" />
          <el-option label="Floor 3" value="Floor 3" />
          <el-option label="Lobby" value="Lobby" />
          <el-option label="Office Wing" value="Office Wing" />
        </el-select>
        <el-select v-model="alertFilter" placeholder="Alert Type" clearable style="width: 140px">
          <el-option label="High Odor" value="high-odor" />
          <el-option label="High Occupancy" value="high-occupancy" />
          <el-option label="Low Soap" value="low-soap" />
          <el-option label="Low TP" value="low-tp" />
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
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Alerts Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">
          <el-icon><BellFilled /></el-icon>
          Active Alerts
        </span>
      </div>
      <el-table :data="paginatedAlerts" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="location" label="Location" width="140" />
        <el-table-column prop="type" label="Alert Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getAlertTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTag(row.severity)" size="small">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" min-width="250" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'resolved' ? 'success' : 'danger'" size="small">
              {{ row.status === 'resolved' ? 'Resolved' : 'Active' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="resolveAlert(row)" v-if="row.status !== 'resolved'">
              Resolve
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="alertCurrentPage"
            v-model:page-size="alertPageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredAlerts.length"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Sensor Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Sensor ${selectedSensor?.name}`" width="550px">
      <div v-if="selectedSensor" class="sensor-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Sensor ID">{{ selectedSensor.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedSensor.location }}</el-descriptions-item>
          <el-descriptions-item label="Odor Level">
            <span :class="getOdorClass(selectedSensor.odorLevel)">{{ selectedSensor.odorLevel }}/10</span>
          </el-descriptions-item>
          <el-descriptions-item label="Occupancy Rate">{{ selectedSensor.occupancyRate }}%</el-descriptions-item>
          <el-descriptions-item label="Soap Level">
            <el-progress :percentage="selectedSensor.soapLevel" :stroke-width="8" />
          </el-descriptions-item>
          <el-descriptions-item label="Toilet Paper Level">
            <el-progress :percentage="selectedSensor.tpLevel" :stroke-width="8" />
          </el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedSensor.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Humidity">{{ selectedSensor.humidity }}%</el-descriptions-item>
          <el-descriptions-item label="Last Update">{{ selectedSensor.lastUpdate }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="selectedSensor.status === 'normal' ? 'success' : 'danger'" size="small">
              {{ selectedSensor.status === 'normal' ? 'Normal' : 'Alert' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="triggerMaintenance(selectedSensor)">Trigger Maintenance</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, Download, Refresh, WindPower, User, Tickets,
  Timer, TurnOff, Delete, Clock, TrendCharts, PieChart,
  Histogram, Connection, RefreshLeft, BellFilled
} from '@element-plus/icons-vue'

// ==================== Types ====================
interface Sensor {
  id: string
  name: string
  location: string
  odorLevel: number
  occupancyRate: number
  soapLevel: number
  tpLevel: number
  temperature: number
  humidity: number
  lastUpdate: string
  status: 'normal' | 'alert'
}

interface Alert {
  id: string
  time: string
  location: string
  type: string
  severity: 'High' | 'Medium' | 'Low'
  message: string
  status: 'active' | 'resolved'
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading hygiene analytics...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading hygiene analytics...',
  'Fetching sensor data...',
  'Calculating occupancy metrics...',
  'Analyzing consumables...',
  'Almost ready...'
]

// ==================== Mock Data ====================
const generateSensors = (): Sensor[] => {
  const locations = ['Floor 1', 'Floor 2', 'Floor 3', 'Lobby', 'Office Wing']
  const sensors: Sensor[] = []

  for (let i = 0; i < 16; i++) {
    const location = locations[Math.floor(Math.random() * locations.length)]
    const gender = i % 2 === 0 ? 'Men' : 'Women'
    const odorLevel = Math.floor(Math.random() * 10)
    const occupancyRate = Math.floor(Math.random() * 100)

    sensors.push({
      id: `SEN-${String(i + 1).padStart(3, '0')}`,
      name: `${location} ${gender}'s Sensor ${Math.floor(i / 2) + 1}`,
      location: location,
      odorLevel: odorLevel,
      occupancyRate: occupancyRate,
      soapLevel: Math.floor(Math.random() * 100),
      tpLevel: Math.floor(Math.random() * 100),
      temperature: Math.floor(20 + Math.random() * 8),
      humidity: Math.floor(40 + Math.random() * 30),
      lastUpdate: new Date().toLocaleTimeString(),
      status: odorLevel > 7 || occupancyRate > 85 ? 'alert' : 'normal'
    })
  }
  return sensors
}

const generateAlerts = (sensors: Sensor[]): Alert[] => {
  const alerts: Alert[] = []
  const now = new Date()

  for (const sensor of sensors) {
    if (sensor.odorLevel > 7) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(now.getTime() - Math.random() * 60 * 60 * 1000).toLocaleString(),
        location: sensor.location,
        type: 'High Odor',
        severity: sensor.odorLevel > 8 ? 'High' : 'Medium',
        message: `Odor level at ${sensor.odorLevel}/10 - ventilation recommended`,
        status: Math.random() > 0.3 ? 'active' : 'resolved'
      })
    }
    if (sensor.occupancyRate > 85) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(now.getTime() - Math.random() * 60 * 60 * 1000).toLocaleString(),
        location: sensor.location,
        type: 'High Occupancy',
        severity: 'Medium',
        message: `Occupancy rate at ${sensor.occupancyRate}% - high traffic`,
        status: 'active'
      })
    }
    if (sensor.soapLevel < 20) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(now.getTime() - Math.random() * 60 * 60 * 1000).toLocaleString(),
        location: sensor.location,
        type: 'Low Soap',
        severity: 'High',
        message: `Soap level at ${sensor.soapLevel}% - refill needed`,
        status: 'active'
      })
    }
    if (sensor.tpLevel < 20) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(now.getTime() - Math.random() * 60 * 60 * 1000).toLocaleString(),
        location: sensor.location,
        type: 'Low TP',
        severity: 'High',
        message: `Toilet paper at ${sensor.tpLevel}% - restock required`,
        status: 'active'
      })
    }
  }

  return alerts.sort((a, b) => b.time.localeCompare(a.time))
}

const sensors = ref<Sensor[]>(generateSensors())
const alerts = ref<Alert[]>(generateAlerts(sensors.value))

// ==================== State ====================
const locationFilter = ref('')
const alertFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const detailDialogVisible = ref(false)
const selectedSensor = ref<Sensor | null>(null)
const alertCurrentPage = ref(1)
const alertPageSize = ref(10)

// Chart refs
let trendChart: echarts.ECharts | null = null
let odorSourceChart: echarts.ECharts | null = null
let consumptionChart: echarts.ECharts | null = null
let zoneOccupancyChart: echarts.ECharts | null = null

const trendChartEl = ref<HTMLElement | null>(null)
const odorSourceChartEl = ref<HTMLElement | null>(null)
const consumptionChartEl = ref<HTMLElement | null>(null)
const zoneOccupancyChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const metrics = computed(() => {
  const avgOdor = sensors.value.reduce((acc, s) => acc + s.odorLevel, 0) / sensors.value.length
  const avgOccupancy = sensors.value.reduce((acc, s) => acc + s.occupancyRate, 0) / sensors.value.length
  const avgSoap = sensors.value.reduce((acc, s) => acc + s.soapLevel, 0) / sensors.value.length
  const avgTp = sensors.value.reduce((acc, s) => acc + s.tpLevel, 0) / sensors.value.length
  const consumablesHealth = Math.round((avgSoap + avgTp) / 2)

  const activeUsers = Math.round(sensors.value.reduce((acc, s) => {
    const totalSpots = 6
    return acc + Math.round((s.occupancyRate / 100) * totalSpots)
  }, 0))

  const lowSoapCount = sensors.value.filter(s => s.soapLevel < 20).length
  const lowTPCount = sensors.value.filter(s => s.tpLevel < 20).length

  return {
    overallOdor: parseFloat(avgOdor.toFixed(1)),
    overallOccupancy: Math.round(avgOccupancy),
    consumablesHealth,
    odorTrend: Math.random() > 0.5 ? Math.round(Math.random() * 15) : -Math.round(Math.random() * 15),
    activeUsers,
    peakOccupancy: Math.max(...sensors.value.map(s => s.occupancyRate)),
    lowSoapCount,
    lowTPCount
  }
})

const stats = computed(() => {
  return {
    avgVisitDuration: Math.floor(8 + Math.random() * 7),
    turnoverRate: (Math.random() * 3 + 1).toFixed(1),
    dailyConsumablesUsage: Math.floor(150 + Math.random() * 100),
    peakHour: `${Math.floor(10 + Math.random() * 8)}:00`
  }
})

const filteredSensors = computed(() => {
  let filtered = [...sensors.value]
  if (locationFilter.value) {
    filtered = filtered.filter(s => s.location === locationFilter.value)
  }
  if (alertFilter.value === 'high-odor') {
    filtered = filtered.filter(s => s.odorLevel > 7)
  }
  if (alertFilter.value === 'high-occupancy') {
    filtered = filtered.filter(s => s.occupancyRate > 85)
  }
  if (alertFilter.value === 'low-soap') {
    filtered = filtered.filter(s => s.soapLevel < 20)
  }
  if (alertFilter.value === 'low-tp') {
    filtered = filtered.filter(s => s.tpLevel < 20)
  }
  return filtered
})

const filteredAlerts = computed(() => {
  let filtered = [...alerts.value]
  if (locationFilter.value) {
    filtered = filtered.filter(a => a.location === locationFilter.value)
  }
  if (alertFilter.value) {
    filtered = filtered.filter(a => {
      if (alertFilter.value === 'high-odor') return a.type === 'High Odor'
      if (alertFilter.value === 'high-occupancy') return a.type === 'High Occupancy'
      if (alertFilter.value === 'low-soap') return a.type === 'Low Soap'
      if (alertFilter.value === 'low-tp') return a.type === 'Low TP'
      return true
    })
  }
  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(a => {
      const alertTime = new Date(a.time)
      return alertTime >= start && alertTime <= end
    })
  }
  return filtered
})

const paginatedAlerts = computed(() => {
  const start = (alertCurrentPage.value - 1) * alertPageSize.value
  const end = start + alertPageSize.value
  return filteredAlerts.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getProgressColor = (value: number) => {
  if (value > 70) return '#22c55e'
  if (value > 30) return '#f59e0b'
  return '#ef4444'
}

const getOdorClass = (value: number) => {
  if (value <= 3) return 'odor-good'
  if (value <= 6) return 'odor-moderate'
  if (value <= 8) return 'odor-bad'
  return 'odor-severe'
}

const getOdorGradient = (value: number) => {
  if (value <= 3) return 'linear-gradient(90deg, #22c55e, #a3e635)'
  if (value <= 6) return 'linear-gradient(90deg, #f59e0b, #fbbf24)'
  if (value <= 8) return 'linear-gradient(90deg, #ef4444, #f97316)'
  return 'linear-gradient(90deg, #7f1d1d, #dc2626)'
}

const getOccupancyClass = (value: number) => {
  if (value <= 30) return 'occupancy-low'
  if (value <= 70) return 'occupancy-normal'
  return 'occupancy-high'
}

const getOccupancyGradient = (value: number) => {
  if (value <= 30) return 'linear-gradient(90deg, #22c55e, #a3e635)'
  if (value <= 70) return 'linear-gradient(90deg, #3b82f6, #60a5fa)'
  return 'linear-gradient(90deg, #ef4444, #f97316)'
}

const getConsumablesClass = (value: number) => {
  if (value <= 30) return 'consumables-critical'
  if (value <= 60) return 'consumables-low'
  if (value <= 80) return 'consumables-good'
  return 'consumables-optimal'
}

const getConsumablesGradient = (value: number) => {
  if (value <= 30) return 'linear-gradient(90deg, #ef4444, #f97316)'
  if (value <= 60) return 'linear-gradient(90deg, #f59e0b, #fbbf24)'
  if (value <= 80) return 'linear-gradient(90deg, #3b82f6, #60a5fa)'
  return 'linear-gradient(90deg, #22c55e, #a3e635)'
}

const getAlertTag = (type: string) => {
  const map: Record<string, string> = {
    'High Odor': 'danger', 'High Occupancy': 'warning',
    'Low Soap': 'warning', 'Low TP': 'warning'
  }
  return map[type] || 'info'
}

const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = { 'High': 'danger', 'Medium': 'warning', 'Low': 'info' }
  return map[severity] || 'info'
}

const resetFilters = () => {
  locationFilter.value = ''
  alertFilter.value = ''
  dateRange.value = null
  alertCurrentPage.value = 1
  ElMessage.success('Filters reset')
}

const viewSensorDetail = (sensor: Sensor) => {
  selectedSensor.value = sensor
  detailDialogVisible.value = true
}

const viewAllSensors = () => {
  ElMessage.info('Viewing all sensors')
}

const resolveAlert = (alert: Alert) => {
  const index = alerts.value.findIndex(a => a.id === alert.id)
  if (index !== -1) {
    alerts.value[index].status = 'resolved'
    ElMessage.success('Alert resolved')
  }
}

const triggerMaintenance = (sensor: Sensor | null) => {
  if (sensor) {
    ElMessage.info(`Maintenance scheduled for ${sensor.name}`)
    detailDialogVisible.value = false
  }
}

const exportData = () => {
  ElMessage.success('Exporting report...')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  sensors.value = generateSensors()
  alerts.value = generateAlerts(sensors.value)
  refreshCharts()
  refreshing.value = false
  tableLoading.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Chart Functions ====================
const initTrendChart = () => {
  if (!trendChartEl.value) return
  if (trendChart) trendChart.dispose()

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const odorData = Array.from({ length: 24 }, () => Math.floor(Math.random() * 10))
  const occupancyData = Array.from({ length: 24 }, () => Math.floor(Math.random() * 100))

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Odor Index', 'Occupancy Rate'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: [{ type: 'value', name: 'Odor (0-10)', min: 0, max: 10 },
      { type: 'value', name: 'Occupancy (%)', min: 0, max: 100 }],
    series: [
      { name: 'Odor Index', type: 'line', data: odorData, smooth: true, lineStyle: { color: '#8b5cf6', width: 2 }, yAxisIndex: 0, areaStyle: { opacity: 0.1 } },
      { name: 'Occupancy Rate', type: 'line', data: occupancyData, smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, yAxisIndex: 1, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initOdorSourceChart = () => {
  if (!odorSourceChartEl.value) return
  if (odorSourceChart) odorSourceChart.dispose()

  const locations = ['Floor 1', 'Floor 2', 'Floor 3', 'Lobby', 'Office Wing']
  const odorData = locations.map(loc => {
    const locSensors = sensors.value.filter(s => s.location === loc)
    return Math.round(locSensors.reduce((acc, s) => acc + s.odorLevel, 0) / (locSensors.length || 1))
  })

  odorSourceChart = echarts.init(odorSourceChartEl.value)
  odorSourceChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: locations, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Average Odor Level', max: 10 },
    series: [{
      type: 'bar', data: odorData,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => getOdorGradient(params.value)
      },
      label: { show: true, position: 'top', formatter: '{c}/10' }
    }]
  })
}

const initConsumptionChart = () => {
  if (!consumptionChartEl.value) return
  if (consumptionChart) consumptionChart.dispose()

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const soapData = [85, 78, 65, 58, 45, 38, 32]
  const tpData = [90, 82, 70, 62, 50, 42, 35]

  consumptionChart = echarts.init(consumptionChartEl.value)
  consumptionChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Soap Consumption', 'TP Consumption'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: 'Remaining (%)', min: 0, max: 100 },
    series: [
      { name: 'Soap Consumption', type: 'line', data: soapData, smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'TP Consumption', type: 'line', data: tpData, smooth: true, lineStyle: { color: '#10b981', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initZoneOccupancyChart = () => {
  if (!zoneOccupancyChartEl.value) return
  if (zoneOccupancyChart) zoneOccupancyChart.dispose()

  const locations = ['Floor 1', 'Floor 2', 'Floor 3', 'Lobby', 'Office Wing']
  const occupancyData = locations.map(loc => {
    const locSensors = sensors.value.filter(s => s.location === loc)
    return Math.round(locSensors.reduce((acc, s) => acc + s.occupancyRate, 0) / (locSensors.length || 1))
  })

  zoneOccupancyChart = echarts.init(zoneOccupancyChartEl.value)
  zoneOccupancyChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
    legend: { orient: 'vertical', left: 'left', data: locations },
    series: [{
      type: 'pie', radius: '55%', center: ['50%', '50%'],
      data: locations.map((loc, i) => ({ name: loc, value: occupancyData[i] })),
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initTrendChart()
    initOdorSourceChart()
    initConsumptionChart()
    initZoneOccupancyChart()
  })
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [trendChart, odorSourceChart, consumptionChart, zoneOccupancyChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
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
      isLoaded.value = true
      refreshCharts()
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  const charts = [trendChart, odorSourceChart, consumptionChart, zoneOccupancyChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.hygiene-analytics-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

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

/* Loading Screen (same as previous pages) */
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
  font-size: 24px;
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

/* Gauge Row */
.gauge-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.gauge-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.gauge-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.gauge-title {
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.gauge-container {
  text-align: center;
}

.gauge-value {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 12px;
}

.gauge-unit {
  font-size: 18px;
  font-weight: normal;
  color: #64748b;
}

.gauge-bar {
  height: 12px;
  background: #e2e8f0;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 8px;
}

.gauge-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.3s ease;
}

.gauge-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #94a3b8;
  margin-bottom: 12px;
}

.gauge-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.trend.positive { color: #22c55e; }
.trend.negative { color: #ef4444; }

.odor-good { color: #22c55e; }
.odor-moderate { color: #f59e0b; }
.odor-bad { color: #f97316; }
.odor-severe { color: #dc2626; }

.occupancy-low { color: #22c55e; }
.occupancy-normal { color: #3b82f6; }
.occupancy-high { color: #ef4444; }

.consumables-critical { color: #ef4444; }
.consumables-low { color: #f59e0b; }
.consumables-good { color: #3b82f6; }
.consumables-optimal { color: #22c55e; }

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-mini-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-mini-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.stat-mini-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-mini-icon.green { background: #dcfce7; color: #22c55e; }
.stat-mini-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-mini-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-mini-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-mini-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-mini-label {
  font-size: 12px;
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

.chart-card.large {
  flex: 1.5;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  width: 100%;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 24px 0 16px;
}

.section-title {
  font-weight: 600;
  font-size: 18px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Sensors Grid */
.sensors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.sensor-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  border-left: 4px solid #22c55e;
  transition: all 0.2s;
}

.sensor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.sensor-card.alert {
  border-left-color: #ef4444;
  background: #fef2f2;
}

.sensor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sensor-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.sensor-location {
  font-size: 12px;
  color: #64748b;
}

.sensor-readings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reading {
  margin-bottom: 4px;
}

.reading-label {
  font-size: 11px;
  color: #64748b;
  display: block;
  margin-bottom: 4px;
}

.reading-value {
  font-size: 14px;
  font-weight: 600;
  margin-left: 8px;
}

.reading-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 4px;
}

.reading-fill {
  height: 100%;
  border-radius: 3px;
}

.reading-row {
  display: flex;
  gap: 16px;
}

.reading-small {
  flex: 1;
}

.sensor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.last-update {
  font-size: 10px;
  color: #94a3b8;
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
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Sensor Detail */
.sensor-detail {
  padding: 8px;
}

/* Responsive */
@media (max-width: 1000px) {
  .gauge-row, .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .sensors-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .gauge-row, .stats-row {
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
  padding: 20px;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
</style>