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
          <span class="loading-title">Smart Toilet Monitoring</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">IoT Smart Hygiene Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="smart-toilet-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Van /></el-icon>
          Smart Toilet Monitoring
        </h1>
        <div class="page-subtitle">Real-time occupancy, hygiene, and consumables monitoring</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="exportData">
          <el-icon><Download /></el-icon> Export Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
        <el-button type="danger" plain @click="triggerEmergencyClean">
          <el-icon><Warning /></el-icon> Emergency Clean
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Van /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalToilets }}</div>
          <div class="stat-label">Total Toilets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.availableToilets }}</div>
          <div class="stat-label">Available</div>
          <div class="stat-trend up">Occupancy: {{ stats.occupancyRate }}%</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.avgWaitTime }}<span class="stat-unit">min</span></div>
          <div class="stat-label">Avg Wait Time</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Delete /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.cleaningRequired }}</div>
          <div class="stat-label">Cleaning Required</div>
          <div class="stat-trend down">↓ {{ stats.cleaningChange }} vs yesterday</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Soap Level</div>
        <div class="metric-value">{{ metrics.soapLevel }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.soapLevel" :stroke-width="8" :color="getProgressColor(metrics.soapLevel)" />
        <div class="metric-sub">Refill needed below 20%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Toilet Paper Level</div>
        <div class="metric-value">{{ metrics.tpLevel }}<span class="stat-unit">%</span></div>
        <el-progress :percentage="metrics.tpLevel" :stroke-width="8" :color="getProgressColor(metrics.tpLevel)" />
        <div class="metric-sub">Avg rolls remaining: {{ metrics.tpRollsLeft }}</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Air Quality</div>
        <div class="metric-value">{{ metrics.airQuality }}<span class="stat-unit">ppm</span></div>
        <div class="metric-trend" :class="metrics.airQuality > 50 ? 'negative' : 'positive'">
          {{ metrics.airQuality > 50 ? 'Poor' : 'Good' }}
        </div>
        <div class="metric-sub">Odor level: {{ metrics.odorLevel }}/10</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Today's Usage</div>
        <div class="metric-value">{{ metrics.todayUsage }}<span class="stat-unit">visits</span></div>
        <div class="metric-trend positive">↑ {{ metrics.usageGrowth }}% vs yesterday</div>
      </div>
    </div>

    <!-- Toilet Map Grid -->
    <div class="toilet-map-section">
      <div class="section-header">
        <span class="section-title">
          <el-icon><Grid /></el-icon>
          Toilet Facility Map
        </span>
        <div class="legend">
          <span><span class="legend-dot available"></span> Available</span>
          <span><span class="legend-dot occupied"></span> Occupied</span>
          <span><span class="legend-dot cleaning"></span> Cleaning</span>
          <span><span class="legend-dot maintenance"></span> Maintenance</span>
          <span><span class="legend-dot low-soap"></span> Low Soap</span>
          <span><span class="legend-dot low-tp"></span> Low TP</span>
        </div>
      </div>

      <div class="toilet-grid">
        <div
            v-for="toilet in toilets"
            :key="toilet.id"
            class="toilet-card"
            :class="toilet.status"
            @click="showToiletDetail(toilet)"
        >
          <div class="toilet-header">
            <span class="toilet-name">{{ toilet.name }}</span>
            <el-tag :type="getStatusTagType(toilet.status)" size="small">
              {{ getStatusLabel(toilet.status) }}
            </el-tag>
          </div>
          <div class="toilet-location">
            <el-icon><Location /></el-icon>
            {{ toilet.location }}
          </div>
          <div class="toilet-sensors">
            <div class="sensor-item" :class="{ warning: toilet.soapLevel < 20 }">
              <el-icon><Dish /></el-icon>
              <span>Soap: {{ toilet.soapLevel }}%</span>
            </div>
            <div class="sensor-item" :class="{ warning: toilet.tpLevel < 20 }">
              <el-icon><Tickets /></el-icon>
              <span>TP: {{ toilet.tpLevel }}%</span>
            </div>
            <div class="sensor-item" :class="{ warning: toilet.odorLevel > 7 }">
              <el-icon><WindPower /></el-icon>
              <span>Odor: {{ toilet.odorLevel }}/10</span>
            </div>
          </div>
          <div class="toilet-occupancy">
            <div class="occupancy-info">
              <span class="label">Current User:</span>
              <span class="value">{{ toilet.currentUser || 'None' }}</span>
            </div>
            <div class="duration-info" v-if="toilet.occupiedSince">
              <el-icon><Timer /></el-icon>
              {{ formatDuration(toilet.occupiedSince) }}
            </div>
          </div>
          <div class="toilet-actions">
            <el-button size="small" type="primary" link @click.stop="markCleaned(toilet)">
              <el-icon><Check /></el-icon> Mark Cleaned
            </el-button>
            <el-button size="small" type="warning" link @click.stop="reportIssue(toilet)">
              <el-icon><Warning /></el-icon> Report Issue
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="locationFilter" placeholder="Location" clearable style="width: 150px">
          <el-option label="Floor 1" value="Floor 1" />
          <el-option label="Floor 2" value="Floor 2" />
          <el-option label="Floor 3" value="Floor 3" />
          <el-option label="Lobby" value="Lobby" />
          <el-option label="Office Wing" value="Office Wing" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Available" value="available" />
          <el-option label="Occupied" value="occupied" />
          <el-option label="Cleaning" value="cleaning" />
          <el-option label="Maintenance" value="maintenance" />
        </el-select>
        <el-select v-model="alertFilter" placeholder="Alerts" clearable style="width: 130px">
          <el-option label="Low Soap" value="low-soap" />
          <el-option label="Low TP" value="low-tp" />
          <el-option label="High Odor" value="high-odor" />
          <el-option label="Long Wait" value="long-wait" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Usage Pattern</span>
          <span class="chart-subtitle">Last 24 hours</span>
        </div>
        <div class="chart-container" ref="usageChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Consumables Status</span>
          <span class="chart-subtitle">Soap & Toilet Paper levels</span>
        </div>
        <div class="chart-container" ref="consumablesChartEl"></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Floor-wise Occupancy</span>
          <span class="chart-subtitle">By location</span>
        </div>
        <div class="chart-container" ref="floorChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cleaning Alerts Timeline</span>
          <span class="chart-subtitle">Last 7 days</span>
        </div>
        <div class="chart-container" ref="alertChartEl"></div>
      </div>
    </div>

    <!-- Alerts Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">
          <el-icon><BellFilled /></el-icon>
          Recent Alerts & Events
        </span>
        <el-button size="small" @click="viewAllAlerts">View All →</el-button>
      </div>
      <el-table :data="paginatedAlerts" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="time" label="Time" width="160" />
        <el-table-column prop="toiletName" label="Toilet" width="120" />
        <el-table-column prop="location" label="Location" width="140" />
        <el-table-column prop="type" label="Alert Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getAlertTypeTag(row.type)" size="small">
              {{ row.type }}
            </el-tag>
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

    <!-- Toilet Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Toilet ${selectedToilet?.name}`" width="550px">
      <div v-if="selectedToilet" class="toilet-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Toilet ID">{{ selectedToilet.id }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedToilet.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(selectedToilet.status)" size="small">
              {{ getStatusLabel(selectedToilet.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Current User">{{ selectedToilet.currentUser || 'None' }}</el-descriptions-item>
          <el-descriptions-item label="Soap Level">
            <el-progress :percentage="selectedToilet.soapLevel" :stroke-width="6" />
          </el-descriptions-item>
          <el-descriptions-item label="Toilet Paper Level">
            <el-progress :percentage="selectedToilet.tpLevel" :stroke-width="6" />
          </el-descriptions-item>
          <el-descriptions-item label="Odor Level">{{ selectedToilet.odorLevel }}/10</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedToilet.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Humidity">{{ selectedToilet.humidity }}%</el-descriptions-item>
          <el-descriptions-item label="Last Cleaning">{{ selectedToilet.lastCleaning }}</el-descriptions-item>
          <el-descriptions-item label="Next Cleaning Due">{{ selectedToilet.nextCleaningDue }}</el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions">
          <el-button type="success" @click="markCleaned(selectedToilet)">Mark Cleaned</el-button>
          <el-button type="warning" @click="scheduleMaintenance(selectedToilet)">Schedule Maintenance</el-button>
          <el-button type="danger" plain @click="triggerEmergencyCleanForToilet(selectedToilet)">Emergency Clean</el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Issue Report Dialog -->
    <el-dialog v-model="issueDialogVisible" title="Report Issue" width="450px">
      <el-form :model="issueForm">
        <el-form-item label="Issue Type">
          <el-select v-model="issueForm.type" style="width: 100%">
            <el-option label="Broken Fixture" value="broken" />
            <el-option label="Clogged" value="clogged" />
            <el-option label="Leaking" value="leaking" />
            <el-option label="No Water" value="no-water" />
            <el-option label="Electrical Issue" value="electrical" />
            <el-option label="Other" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input type="textarea" v-model="issueForm.description" rows="3" placeholder="Describe the issue..." />
        </el-form-item>
        <el-form-item label="Priority">
          <el-radio-group v-model="issueForm.priority">
            <el-radio label="high">High</el-radio>
            <el-radio label="medium">Medium</el-radio>
            <el-radio label="low">Low</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="issueDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitIssue">Submit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Van, CircleCheck, Clock, Delete, Download, Refresh, Warning,
  Location, Dish, Tickets, WindPower, Grid, RefreshLeft,
  Timer, Check, BellFilled
} from '@element-plus/icons-vue'

// ==================== Types ====================
interface Toilet {
  id: string
  name: string
  location: string
  status: 'available' | 'occupied' | 'cleaning' | 'maintenance'
  currentUser: string | null
  occupiedSince: string | null
  soapLevel: number
  tpLevel: number
  tpRollsLeft: number
  odorLevel: number
  temperature: number
  humidity: number
  lastCleaning: string
  nextCleaningDue: string
  usageCount: number
  avgDuration: number
}

interface Alert {
  id: string
  time: string
  toiletId: string
  toiletName: string
  location: string
  type: string
  message: string
  status: 'active' | 'resolved'
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading smart toilet data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading smart toilet data...',
  'Fetching sensor readings...',
  'Loading occupancy status...',
  'Analyzing consumables...',
  'Almost ready...'
]

// ==================== Mock Data ====================
const generateToilets = (): Toilet[] => {
  const locations = [
    { floor: 'Floor 1', count: 6, prefix: 'F1' },
    { floor: 'Floor 2', count: 4, prefix: 'F2' },
    { floor: 'Floor 3', count: 4, prefix: 'F3' },
    { floor: 'Lobby', count: 2, prefix: 'LB' },
    { floor: 'Office Wing', count: 5, prefix: 'OW' }
  ]

  const toilets: Toilet[] = []
  let idCounter = 1

  for (const loc of locations) {
    for (let i = 1; i <= loc.count; i++) {
      const gender = i % 2 === 0 ? 'Men' : 'Women'
      const statuses: Toilet['status'][] = ['available', 'occupied', 'available', 'occupied', 'cleaning', 'maintenance']
      const status = statuses[Math.floor(Math.random() * statuses.length)]

      const occupiedSince = status === 'occupied'
          ? new Date(Date.now() - Math.random() * 30 * 60 * 1000).toLocaleString()
          : null

      const soapLevel = Math.floor(Math.random() * 100)
      const tpLevel = Math.floor(Math.random() * 100)
      const odorLevel = Math.floor(Math.random() * 10)

      const lastCleaning = new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString()
      const nextCleaningDue = new Date(Date.now() + Math.random() * 4 * 60 * 60 * 1000).toLocaleString()

      toilets.push({
        id: `T-${String(idCounter).padStart(3, '0')}`,
        name: `${loc.floor} ${gender}'s ${String(i).padStart(2, '0')}`,
        location: loc.floor,
        status,
        currentUser: status === 'occupied' ? `User_${Math.floor(Math.random() * 100)}` : null,
        occupiedSince,
        soapLevel,
        tpLevel,
        tpRollsLeft: Math.floor(tpLevel / 20),
        odorLevel,
        temperature: Math.floor(22 + Math.random() * 5),
        humidity: Math.floor(40 + Math.random() * 30),
        lastCleaning,
        nextCleaningDue,
        usageCount: Math.floor(Math.random() * 150),
        avgDuration: Math.floor(5 + Math.random() * 10)
      })
      idCounter++
    }
  }
  return toilets
}

const generateAlerts = (toilets: Toilet[]): Alert[] => {
  const alerts: Alert[] = []
  const alertTypes = [
    { type: 'Low Soap', tag: 'warning', message: 'Soap dispenser needs refill' },
    { type: 'Low Toilet Paper', tag: 'warning', message: 'Toilet paper roll is running low' },
    { type: 'High Odor', tag: 'danger', message: 'Odor level exceeds threshold' },
    { type: 'Long Wait Time', tag: 'info', message: 'Unusually long occupancy time detected' },
    { type: 'Cleaning Required', tag: 'warning', message: 'Scheduled cleaning overdue' },
    { type: 'Maintenance Needed', tag: 'danger', message: 'Fixture requires maintenance' }
  ]

  for (const toilet of toilets) {
    if (toilet.soapLevel < 20) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString(),
        toiletId: toilet.id,
        toiletName: toilet.name,
        location: toilet.location,
        type: 'Low Soap',
        message: `Soap level at ${toilet.soapLevel}% - refill needed`,
        status: Math.random() > 0.3 ? 'active' : 'resolved'
      })
    }
    if (toilet.tpLevel < 20) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString(),
        toiletId: toilet.id,
        toiletName: toilet.name,
        location: toilet.location,
        type: 'Low Toilet Paper',
        message: `Toilet paper at ${toilet.tpLevel}% - ${toilet.tpRollsLeft} rolls remaining`,
        status: Math.random() > 0.3 ? 'active' : 'resolved'
      })
    }
    if (toilet.odorLevel > 7) {
      alerts.push({
        id: `ALT-${String(alerts.length + 1).padStart(4, '0')}`,
        time: new Date(Date.now() - Math.random() * 12 * 60 * 60 * 1000).toLocaleString(),
        toiletId: toilet.id,
        toiletName: toilet.name,
        location: toilet.location,
        type: 'High Odor',
        message: `Odor level at ${toilet.odorLevel}/10 - ventilation recommended`,
        status: Math.random() > 0.2 ? 'active' : 'resolved'
      })
    }
  }

  return alerts.sort((a, b) => b.time.localeCompare(a.time))
}

const toilets = ref<Toilet[]>(generateToilets())
const alerts = ref<Alert[]>(generateAlerts(toilets.value))

// ==================== State ====================
const locationFilter = ref('')
const statusFilter = ref('')
const alertFilter = ref('')
const detailDialogVisible = ref(false)
const issueDialogVisible = ref(false)
const selectedToilet = ref<Toilet | null>(null)
const selectedIssueToilet = ref<Toilet | null>(null)
const alertCurrentPage = ref(1)
const alertPageSize = ref(10)

const issueForm = ref({
  type: 'other',
  description: '',
  priority: 'medium'
})

// Chart refs
let usageChart: echarts.ECharts | null = null
let consumablesChart: echarts.ECharts | null = null
let floorChart: echarts.ECharts | null = null
let alertChart: echarts.ECharts | null = null

const usageChartEl = ref<HTMLElement | null>(null)
const consumablesChartEl = ref<HTMLElement | null>(null)
const floorChartEl = ref<HTMLElement | null>(null)
const alertChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalToilets = toilets.value.length
  const availableToilets = toilets.value.filter(t => t.status === 'available').length
  const occupiedToilets = toilets.value.filter(t => t.status === 'occupied').length
  const cleaningRequired = toilets.value.filter(t => t.status === 'cleaning' || t.soapLevel < 20 || t.tpLevel < 20).length
  const occupancyRate = Math.round((occupiedToilets / totalToilets) * 100)
  const avgWaitTime = Math.round(occupiedToilets / (availableToilets + 1) * 3)

  return {
    totalToilets,
    availableToilets,
    occupiedToilets,
    cleaningRequired,
    occupancyRate,
    avgWaitTime,
    cleaningChange: 8
  }
})

const metrics = computed(() => {
  const avgSoap = Math.round(toilets.value.reduce((acc, t) => acc + t.soapLevel, 0) / toilets.value.length)
  const avgTp = Math.round(toilets.value.reduce((acc, t) => acc + t.tpLevel, 0) / toilets.value.length)
  const avgTpRolls = Math.round(toilets.value.reduce((acc, t) => acc + t.tpRollsLeft, 0) / toilets.value.length)
  const avgAirQuality = Math.round(toilets.value.reduce((acc, t) => acc + t.odorLevel * 10, 0) / toilets.value.length)
  const totalUsage = toilets.value.reduce((acc, t) => acc + t.usageCount, 0)

  return {
    soapLevel: avgSoap,
    tpLevel: avgTp,
    tpRollsLeft: avgTpRolls,
    airQuality: avgAirQuality,
    odorLevel: (avgAirQuality / 10).toFixed(1),
    todayUsage: totalUsage,
    usageGrowth: 5
  }
})

const filteredToilets = computed(() => {
  let filtered = [...toilets.value]

  if (locationFilter.value) {
    filtered = filtered.filter(t => t.location === locationFilter.value)
  }
  if (statusFilter.value) {
    filtered = filtered.filter(t => t.status === statusFilter.value)
  }
  if (alertFilter.value) {
    if (alertFilter.value === 'low-soap') {
      filtered = filtered.filter(t => t.soapLevel < 20)
    } else if (alertFilter.value === 'low-tp') {
      filtered = filtered.filter(t => t.tpLevel < 20)
    } else if (alertFilter.value === 'high-odor') {
      filtered = filtered.filter(t => t.odorLevel > 7)
    } else if (alertFilter.value === 'long-wait') {
      filtered = filtered.filter(t => t.status === 'occupied')
    }
  }

  return filtered
})

const filteredAlerts = computed(() => {
  let filtered = [...alerts.value]
  if (locationFilter.value) {
    filtered = filtered.filter(a => a.location === locationFilter.value)
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

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    available: 'success', occupied: 'danger', cleaning: 'warning', maintenance: 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    available: 'Available', occupied: 'Occupied', cleaning: 'Cleaning', maintenance: 'Maintenance'
  }
  return map[status] || status
}

const getAlertTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Low Soap': 'warning', 'Low Toilet Paper': 'warning', 'High Odor': 'danger',
    'Long Wait Time': 'info', 'Cleaning Required': 'warning', 'Maintenance Needed': 'danger'
  }
  return map[type] || 'info'
}

const formatDuration = (since: string) => {
  const sinceDate = new Date(since)
  const now = new Date()
  const minutes = Math.floor((now.getTime() - sinceDate.getTime()) / (1000 * 60))
  return `${minutes} min`
}

const resetFilters = () => {
  locationFilter.value = ''
  statusFilter.value = ''
  alertFilter.value = ''
  alertCurrentPage.value = 1
  ElMessage.success('Filters reset')
}

const showToiletDetail = (toilet: Toilet) => {
  selectedToilet.value = toilet
  detailDialogVisible.value = true
}

const markCleaned = (toilet: Toilet) => {
  const index = toilets.value.findIndex(t => t.id === toilet.id)
  if (index !== -1) {
    toilets.value[index].status = 'available'
    toilets.value[index].lastCleaning = new Date().toLocaleString()
    toilets.value[index].nextCleaningDue = new Date(Date.now() + 4 * 60 * 60 * 1000).toLocaleString()
    toilets.value[index].soapLevel = Math.min(100, toilets.value[index].soapLevel + 30)
    toilets.value[index].tpLevel = Math.min(100, toilets.value[index].tpLevel + 40)
    toilets.value[index].odorLevel = Math.max(0, toilets.value[index].odorLevel - 5)
    ElMessage.success(`${toilet.name} marked as cleaned`)
  }
  detailDialogVisible.value = false
  refreshCharts()
}

const reportIssue = (toilet: Toilet) => {
  selectedIssueToilet.value = toilet
  issueForm.value = { type: 'other', description: '', priority: 'medium' }
  issueDialogVisible.value = true
}

const submitIssue = () => {
  if (selectedIssueToilet.value) {
    const newAlert: Alert = {
      id: `ALT-${String(alerts.value.length + 1).padStart(4, '0')}`,
      time: new Date().toLocaleString(),
      toiletId: selectedIssueToilet.value.id,
      toiletName: selectedIssueToilet.value.name,
      location: selectedIssueToilet.value.location,
      type: 'Maintenance Needed',
      message: issueForm.value.description || `Issue reported: ${issueForm.value.type}`,
      status: 'active'
    }
    alerts.value.unshift(newAlert)

    const index = toilets.value.findIndex(t => t.id === selectedIssueToilet.value!.id)
    if (index !== -1) {
      toilets.value[index].status = 'maintenance'
    }

    ElMessage.success('Issue reported successfully')
  }
  issueDialogVisible.value = false
  refreshCharts()
}

const resolveAlert = (alert: Alert) => {
  const index = alerts.value.findIndex(a => a.id === alert.id)
  if (index !== -1) {
    alerts.value[index].status = 'resolved'
    ElMessage.success('Alert resolved')
  }
}

const triggerEmergencyClean = () => {
  ElMessageBox.confirm('This will trigger an emergency cleaning for all toilets. Continue?', 'Emergency Clean', {
    confirmButtonText: 'Yes',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    toilets.value.forEach((toilet, index) => {
      if (toilet.status === 'occupied') {
        toilets.value[index].status = 'cleaning'
      }
    })
    ElMessage.success('Emergency cleaning triggered')
    refreshCharts()
  }).catch(() => {})
}

const triggerEmergencyCleanForToilet = (toilet: Toilet) => {
  ElMessageBox.confirm(`Trigger emergency cleaning for ${toilet.name}?`, 'Emergency Clean', {
    confirmButtonText: 'Yes',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = toilets.value.findIndex(t => t.id === toilet.id)
    if (index !== -1) {
      toilets.value[index].status = 'cleaning'
      ElMessage.success(`Emergency cleaning triggered for ${toilet.name}`)
    }
    detailDialogVisible.value = false
    refreshCharts()
  }).catch(() => {})
}

const scheduleMaintenance = (toilet: Toilet) => {
  ElMessage.info(`Maintenance scheduled for ${toilet.name}`)
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all alerts')
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
  toilets.value = generateToilets()
  alerts.value = generateAlerts(toilets.value)
  refreshCharts()
  refreshing.value = false
  tableLoading.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Chart Functions ====================
const initUsageChart = () => {
  if (!usageChartEl.value) return
  if (usageChart) usageChart.dispose()

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const usageData = [2, 1, 0, 0, 0, 1, 5, 15, 28, 42, 38, 35, 32, 30, 28, 25, 22, 28, 32, 35, 28, 18, 10, 4]

  usageChart = echarts.init(usageChartEl.value)
  usageChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: hours, axisLabel: { rotate: 45, interval: 3 } },
    yAxis: { type: 'value', name: 'Usage Count' },
    series: [{
      type: 'line', data: usageData, smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle', symbolSize: 4
    }]
  })
}

const initConsumablesChart = () => {
  if (!consumablesChartEl.value) return
  if (consumablesChart) consumablesChart.dispose()

  const toiletNames = toilets.value.slice(0, 10).map(t => t.name.split(' ').slice(-1)[0])
  const soapData = toilets.value.slice(0, 10).map(t => t.soapLevel)
  const tpData = toilets.value.slice(0, 10).map(t => t.tpLevel)

  consumablesChart = echarts.init(consumablesChartEl.value)
  consumablesChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Soap Level', 'Toilet Paper Level'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: toiletNames },
    yAxis: { type: 'value', name: 'Level (%)', max: 100 },
    series: [
      { name: 'Soap Level', type: 'bar', data: soapData, itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] } },
      { name: 'Toilet Paper Level', type: 'bar', data: tpData, itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const initFloorChart = () => {
  if (!floorChartEl.value) return
  if (floorChart) floorChart.dispose()

  const floors = ['Floor 1', 'Floor 2', 'Floor 3', 'Lobby', 'Office Wing']
  const occupancyData = floors.map(floor => {
    const floorToilets = toilets.value.filter(t => t.location === floor)
    const occupied = floorToilets.filter(t => t.status === 'occupied').length
    return Math.round((occupied / (floorToilets.length || 1)) * 100)
  })

  floorChart = echarts.init(floorChartEl.value)
  floorChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: floors },
    yAxis: { type: 'value', name: 'Occupancy (%)', max: 100 },
    series: [{
      type: 'bar', data: occupancyData,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value < 30) return '#22c55e'
          if (value < 70) return '#f59e0b'
          return '#ef4444'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initAlertChart = () => {
  if (!alertChartEl.value) return
  if (alertChart) alertChart.dispose()

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const alertCounts = [12, 8, 15, 10, 18, 22, 14]

  alertChart = echarts.init(alertChartEl.value)
  alertChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: days },
    yAxis: { type: 'value', name: 'Alert Count' },
    series: [{
      type: 'line', data: alertCounts, smooth: true,
      lineStyle: { color: '#ef4444', width: 3 },
      areaStyle: { opacity: 0.1 },
      symbol: 'circle', symbolSize: 6,
      label: { show: true, position: 'top' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initUsageChart()
    initConsumablesChart()
    initFloorChart()
    initAlertChart()
  })
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [usageChart, consumablesChart, floorChart, alertChart]
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
  const charts = [usageChart, consumablesChart, floorChart, alertChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.smart-toilet-page {
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

/* Loading Screen */
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
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
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
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-trend {
  font-size: 11px;
  margin-top: 8px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 8px;
}

/* Toilet Map Section */
.toilet-map-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #64748b;
  flex-wrap: wrap;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}

.legend-dot.available { background: #22c55e; }
.legend-dot.occupied { background: #ef4444; }
.legend-dot.cleaning { background: #f59e0b; }
.legend-dot.maintenance { background: #6b7280; }
.legend-dot.low-soap { background: #3b82f6; }
.legend-dot.low-tp { background: #8b5cf6; }

.toilet-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.toilet-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}

.toilet-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #cbd5e1;
}

.toilet-card.available { border-left: 4px solid #22c55e; }
.toilet-card.occupied { border-left: 4px solid #ef4444; }
.toilet-card.cleaning { border-left: 4px solid #f59e0b; }
.toilet-card.maintenance { border-left: 4px solid #6b7280; }

.toilet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.toilet-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.toilet-location {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
}

.toilet-sensors {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.sensor-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #475569;
}

.sensor-item.warning {
  color: #ef4444;
  font-weight: 500;
}

.toilet-occupancy {
  background: #f1f5f9;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 12px;
  font-size: 12px;
  display: flex;
  justify-content: space-between;
}

.toilet-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
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
  flex-wrap: wrap;
  gap: 12px;
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
  height: 280px;
  width: 100%;
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

/* Toilet Detail */
.toilet-detail {
  padding: 8px;
}

.detail-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Responsive */
@media (max-width: 1000px) {
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
  .legend {
    justify-content: center;
  }
  .toilet-grid {
    grid-template-columns: 1fr;
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