<template>
  <div class="operations-dashboard-container">
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
            <span class="loading-title">Loading Command Center</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Operations Dashboard - Real-time Monitoring</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="dashboard-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Operations Dashboard</h1>
          <p class="page-subtitle">Real-time monitoring and command center for facility operations</p>
        </div>
        <div class="header-actions">
          <div class="time-display">
            <el-icon><Clock /></el-icon>
            <span>{{ currentTime }}</span>
          </div>
          <el-button type="primary" @click="refreshAllData">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button @click="fullscreenMode">
            <el-icon><FullScreen /></el-icon>
            Fullscreen
          </el-button>
          <el-button @click="exportDashboard">
            <el-icon><Download /></el-icon>
            Export
          </el-button>
        </div>
      </div>

      <!-- Global Status Banner -->
      <div class="global-status" :class="globalStatusClass">
        <div class="status-icon">
          <el-icon><component :is="globalStatusIcon" /></el-icon>
        </div>
        <div class="status-content">
          <span class="status-title">{{ globalStatusTitle }}</span>
          <span class="status-message">{{ globalStatusMessage }}</span>
        </div>
        <div class="status-actions">
          <el-button size="small" type="primary" plain @click="viewIncidents">View Incidents</el-button>
          <el-button size="small" plain @click="acknowledgeStatus">Acknowledge</el-button>
        </div>
      </div>

      <!-- KPI Cards Row -->
      <el-row :gutter="20" class="kpi-row">
        <el-col :span="6">
          <div class="kpi-card">
            <div class="kpi-icon red">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="kpi-info">
              <span class="kpi-label">Critical Alarms</span>
              <span class="kpi-value">{{ criticalAlarms }}</span>
              <span class="kpi-trend up">+{{ alarmTrend.critical }}</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="kpi-card">
            <div class="kpi-icon orange">
              <el-icon><Bell /></el-icon>
            </div>
            <div class="kpi-info">
              <span class="kpi-label">Major Alarms</span>
              <span class="kpi-value">{{ majorAlarms }}</span>
              <span class="kpi-trend up">+{{ alarmTrend.major }}</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="kpi-card">
            <div class="kpi-icon blue">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="kpi-info">
              <span class="kpi-label">Active Faults</span>
              <span class="kpi-value">{{ activeFaults }}</span>
              <span class="kpi-trend down">-{{ faultTrend }}</span>
            </div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="kpi-card">
            <div class="kpi-icon green">
              <el-icon><SuccessFilled /></el-icon>
            </div>
            <div class="kpi-info">
              <span class="kpi-label">System Health</span>
              <span class="kpi-value">{{ systemHealth }}%</span>
              <span class="kpi-trend up">+{{ healthTrend }}%</span>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- Main Dashboard Grid -->
      <el-row :gutter="20" class="dashboard-grid">
        <!-- Real-time Alarms Panel -->
        <el-col :span="8">
          <el-card class="dashboard-card alarm-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><BellFilled /></el-icon>
                  Real-time Alarms
                </span>
                <el-button link @click="viewAllAlarms">View All →</el-button>
              </div>
            </template>
            <div class="alarm-list">
              <div v-for="alarm in recentAlarms" :key="alarm.id" class="alarm-item" :class="alarm.severity">
                <div class="alarm-icon">
                  <el-icon><WarningFilled /></el-icon>
                </div>
                <div class="alarm-content">
                  <div class="alarm-title">{{ alarm.title }}</div>
                  <div class="alarm-location">{{ alarm.location }}</div>
                  <div class="alarm-time">{{ alarm.time }}</div>
                </div>
                <div class="alarm-actions">
                  <el-button size="small" circle @click="acknowledgeAlarm(alarm)">
                    <el-icon><Check /></el-icon>
                  </el-button>
                </div>
              </div>
              <div v-if="recentAlarms.length === 0" class="no-alarms">
                <el-icon><SuccessFilled /></el-icon>
                <span>No active alarms</span>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Site Health Map -->
        <el-col :span="8">
          <el-card class="dashboard-card site-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Location /></el-icon>
                  Site Health Map
                </span>
                <el-select v-model="siteFilter" size="small" style="width: 100px">
                  <el-option label="All Sites" value="all" />
                  <el-option label="Data Center" value="datacenter" />
                  <el-option label="Office" value="office" />
                </el-select>
              </div>
            </template>
            <div class="site-map">
              <div v-for="site in filteredSites" :key="site.id" class="site-item" @click="selectSite(site)">
                <div class="site-status" :class="site.status">
                  <div class="status-dot"></div>
                </div>
                <div class="site-info">
                  <span class="site-name">{{ site.name }}</span>
                  <span class="site-location">{{ site.location }}</span>
                </div>
                <div class="site-metrics">
                  <span class="metric" :class="getSiteTempClass(site.temperature)">
                    {{ site.temperature }}°C
                  </span>
                  <span class="metric">{{ site.power }} kW</span>
                </div>
                <el-progress :percentage="site.health" :stroke-width="6" :color="getHealthColor(site.health)" />
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Incident Center -->
        <el-col :span="8">
          <el-card class="dashboard-card incident-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Flag /></el-icon>
                  Active Incidents
                </span>
                <el-button link @click="createIncident">+ Create</el-button>
              </div>
            </template>
            <div class="incident-list">
              <div v-for="incident in activeIncidents" :key="incident.id" class="incident-item">
                <div class="incident-priority" :class="incident.priority">
                  {{ incident.priority }}
                </div>
                <div class="incident-info">
                  <div class="incident-title">{{ incident.title }}</div>
                  <div class="incident-details">
                    <span><el-icon><User /></el-icon> {{ incident.assignee }}</span>
                    <span><el-icon><Timer /></el-icon> {{ incident.duration }}</span>
                  </div>
                </div>
                <div class="incident-progress">
                  <el-progress :percentage="incident.progress" :stroke-width="4" :show-text="false" />
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Second Row Charts -->
      <el-row :gutter="20" class="dashboard-grid">
        <el-col :span="12">
          <el-card class="dashboard-card chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><TrendCharts /></el-icon>
                  System Performance Trends
                </span>
                <div class="chart-controls">
                  <el-radio-group v-model="trendPeriod" size="small">
                    <el-radio-button label="hour">Hour</el-radio-button>
                    <el-radio-button label="day">Day</el-radio-button>
                    <el-radio-button label="week">Week</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div ref="performanceChartRef" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="dashboard-card chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><PieChart /></el-icon>
                  Alarm Distribution
                </span>
                <el-select v-model="alarmCategory" size="small" style="width: 100px">
                  <el-option label="By Severity" value="severity" />
                  <el-option label="By System" value="system" />
                </el-select>
              </div>
            </template>
            <div ref="alarmDistributionChartRef" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Third Row - Resource Dispatch & Work Orders -->
      <el-row :gutter="20" class="dashboard-grid">
        <el-col :span="8">
          <el-card class="dashboard-card dispatch-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Van /></el-icon>
                  Resource Dispatch
                </span>
                <el-button link @click="viewDispatch">Manage →</el-button>
              </div>
            </template>
            <div class="dispatch-list">
              <div v-for="resource in activeResources" :key="resource.id" class="dispatch-item">
                <div class="dispatch-avatar" :style="{ background: resource.color }">
                  <el-icon><User /></el-icon>
                </div>
                <div class="dispatch-info">
                  <span class="dispatch-name">{{ resource.name }}</span>
                  <span class="dispatch-task">{{ resource.task }}</span>
                </div>
                <div class="dispatch-eta">
                  <el-tag size="small" :type="getEtaTagType(resource.eta)">{{ resource.eta }}</el-tag>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="dashboard-card workorder-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Document /></el-icon>
                  Work Orders
                </span>
                <el-button link @click="viewWorkOrders">View All →</el-button>
              </div>
            </template>
            <div class="workorder-stats">
              <div class="stat-item">
                <span class="stat-value">{{ workOrders.pending }}</span>
                <span class="stat-label">Pending</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ workOrders.inProgress }}</span>
                <span class="stat-label">In Progress</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ workOrders.completed }}</span>
                <span class="stat-label">Completed</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ workOrders.overdue }}</span>
                <span class="stat-label">Overdue</span>
              </div>
            </div>
            <div class="workorder-list">
              <div v-for="order in recentWorkOrders" :key="order.id" class="workorder-item">
                <div class="workorder-priority" :class="order.priority">{{ order.priority }}</div>
                <div class="workorder-info">
                  <span class="workorder-title">{{ order.title }}</span>
                  <span class="workorder-asset">{{ order.asset }}</span>
                </div>
                <div class="workorder-date">{{ order.date }}</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="dashboard-card energy-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Lightning /></el-icon>
                  Energy Snapshot
                </span>
                <el-button link @click="viewEnergyDetails">Details →</el-button>
              </div>
            </template>
            <div class="energy-metrics">
              <div class="energy-main">
                <div class="energy-value">{{ currentPower }}<span>kW</span></div>
                <div class="energy-label">Current Power Demand</div>
              </div>
              <div class="energy-stats">
                <div class="energy-stat">
                  <span class="stat-label">Today's Usage</span>
                  <span class="stat-value">{{ todayUsage }} kWh</span>
                </div>
                <div class="energy-stat">
                  <span class="stat-label">Peak Demand</span>
                  <span class="stat-value">{{ peakDemand }} kW</span>
                </div>
                <div class="energy-stat">
                  <span class="stat-label">PUE</span>
                  <span class="stat-value">{{ pueValue }}</span>
                </div>
              </div>
            </div>
            <div ref="energyTrendChartRef" class="mini-chart"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Fourth Row - GIS Map & Situation Awareness -->
      <el-row :gutter="20" class="dashboard-grid">
        <el-col :span="16">
          <el-card class="dashboard-card map-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><Location /></el-icon>
                  Site Map & Incident Locations
                </span>
                <div class="map-controls">
                  <el-button-group size="small">
                    <el-button @click="mapZoomIn">
                      <el-icon><ZoomIn /></el-icon>
                    </el-button>
                    <el-button @click="mapZoomOut">
                      <el-icon><ZoomOut /></el-icon>
                    </el-button>
                    <el-button @click="resetMap">
                      <el-icon><RefreshLeft /></el-icon>
                    </el-button>
                  </el-button-group>
                </div>
              </div>
            </template>
            <div ref="mapContainer" class="map-container">
              <div class="map-placeholder">
                <div class="map-grid">
                  <div v-for="i in 9" :key="i" class="map-cell"></div>
                </div>
                <div class="map-markers">
                  <div v-for="site in sitesWithAlerts" :key="site.id" class="map-marker" :style="{ left: site.x + '%', top: site.y + '%' }">
                    <div class="marker-pulse" :class="site.alertLevel"></div>
                    <div class="marker-tooltip">{{ site.name }}</div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="dashboard-card situation-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><View /></el-icon>
                  Situation Awareness
                </span>
                <el-button link @click="refreshSituation">Refresh</el-button>
              </div>
            </template>
            <div class="situation-timeline">
              <div v-for="event in situationEvents" :key="event.id" class="situation-event">
                <div class="event-time">{{ event.time }}</div>
                <div class="event-content">
                  <div class="event-title">{{ event.title }}</div>
                  <div class="event-desc">{{ event.description }}</div>
                </div>
                <div class="event-status" :class="event.status">
                  {{ event.status }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Executive Summary Footer -->
      <div class="executive-summary">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-header">
            <span class="summary-title">Executive Summary</span>
            <span class="summary-date">{{ summaryDate }}</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="4">
              <div class="summary-item">
                <span class="item-label">MTBF</span>
                <span class="item-value">{{ mtbf }} days</span>
                <span class="item-trend up">+5%</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="summary-item">
                <span class="item-label">MTTR</span>
                <span class="item-value">{{ mttr }} hrs</span>
                <span class="item-trend down">-8%</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="summary-item">
                <span class="item-label">Availability</span>
                <span class="item-value">{{ availability }}%</span>
                <span class="item-trend up">+0.5%</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="summary-item">
                <span class="item-label">Energy Savings</span>
                <span class="item-value">{{ energySavings }}%</span>
                <span class="item-trend up">+2.3%</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="summary-item">
                <span class="item-label">Compliance</span>
                <span class="item-value">{{ complianceRate }}%</span>
                <span class="item-trend up">+3%</span>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="summary-item">
                <span class="item-label">Carbon Saved</span>
                <span class="item-value">{{ carbonSaved }}t</span>
                <span class="item-trend up">+12%</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>
    </div>

    <!-- Incident Detail Dialog -->
    <el-dialog v-model="incidentDialogVisible" title="Incident Details" width="600px">
      <el-form>
        <el-form-item label="Title">
          <span>{{ selectedIncident?.title }}</span>
        </el-form-item>
        <el-form-item label="Priority">
          <el-tag :type="getPriorityTagType(selectedIncident?.priority)">{{ selectedIncident?.priority }}</el-tag>
        </el-form-item>
        <el-form-item label="Description">
          <el-input type="textarea" :rows="3" v-model="incidentDescription" />
        </el-form-item>
        <el-form-item label="Assign To">
          <el-select v-model="incidentAssignee" placeholder="Select assignee">
            <el-option label="John Smith - Lead Engineer" value="john" />
            <el-option label="Sarah Chen - HVAC Specialist" value="sarah" />
            <el-option label="Mike Johnson - Electrical" value="mike" />
          </el-select>
        </el-form-item>
        <el-form-item label="Estimated Resolution">
          <el-date-picker v-model="incidentEta" type="datetime" placeholder="Select ETA" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="incidentDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="updateIncident">Update Incident</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Clock, Refresh, FullScreen, Download, WarningFilled, Bell, Cpu,
  SuccessFilled, Location, Flag, User, Timer, TrendCharts, PieChart,
  Van, Document, Lightning, ZoomIn, ZoomOut, RefreshLeft, View,
  Check, Plus, BellFilled, DataLine, Edit, Delete, Setting, HomeFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing command center...')

// ==================== Time ====================
const currentTime = ref('')
let timeInterval: ReturnType<typeof setInterval> | null = null

// ==================== Dashboard Data ====================
const criticalAlarms = ref(3)
const majorAlarms = ref(8)
const activeFaults = ref(12)
const systemHealth = ref(96.8)

const alarmTrend = ref({ critical: 2, major: 3 })
const faultTrend = ref(4)
const healthTrend = ref(1.2)

// Sites Data
const sites = ref([
  { id: 1, name: 'DC East - Building A', location: 'Singapore', status: 'warning', temperature: 26.5, power: 1250, health: 87, x: 35, y: 40, alertLevel: 'warning' },
  { id: 2, name: 'DC West - Data Hall', location: 'London', status: 'critical', temperature: 28.2, power: 980, health: 72, x: 65, y: 35, alertLevel: 'critical' },
  { id: 3, name: 'Office Tower', location: 'New York', status: 'healthy', temperature: 22.5, power: 450, health: 98, x: 20, y: 60, alertLevel: 'healthy' },
  { id: 4, name: 'Data Center North', location: 'Tokyo', status: 'healthy', temperature: 23.1, power: 1100, health: 94, x: 80, y: 55, alertLevel: 'healthy' },
  { id: 5, name: 'Cooling Plant', location: 'Frankfurt', status: 'warning', temperature: 24.8, power: 320, health: 82, x: 50, y: 25, alertLevel: 'warning' },
  { id: 6, name: 'Backup Facility', location: 'Sydney', status: 'healthy', temperature: 21.5, power: 280, health: 96, x: 75, y: 70, alertLevel: 'healthy' },
])

const siteFilter = ref('all')
const filteredSites = computed(() => {
  if (siteFilter.value === 'all') return sites.value
  return sites.value.filter(s => s.name.toLowerCase().includes(siteFilter.value))
})

const sitesWithAlerts = computed(() => sites.value.filter(s => s.alertLevel !== 'healthy'))

// Recent Alarms
const recentAlarms = ref([
  { id: 1, title: 'Chiller-01 High Temperature', location: 'DC East - Floor 2', time: '2 min ago', severity: 'critical' },
  { id: 2, title: 'UPS Battery Degradation', location: 'UPS Room A', time: '15 min ago', severity: 'major' },
  { id: 3, title: 'Server Rack Overload', location: 'Data Hall 1', time: '32 min ago', severity: 'critical' },
  { id: 4, title: 'Cooling Tower Low Flow', location: 'Cooling Plant', time: '1 hour ago', severity: 'major' },
  { id: 5, title: 'Network Switch Failure', location: 'Network Room', time: '2 hours ago', severity: 'warning' },
])

// Active Incidents
const activeIncidents = ref([
  { id: 1, title: 'Cooling System Failure - DC East', priority: 'critical', assignee: 'John Smith', duration: '2h 15m', progress: 65 },
  { id: 2, title: 'UPS Maintenance - Building A', priority: 'high', assignee: 'Sarah Chen', duration: '45m', progress: 30 },
  { id: 3, title: 'Network Latency Issues', priority: 'medium', assignee: 'Mike Johnson', duration: '3h', progress: 80 },
  { id: 4, title: 'Temperature Anomaly - Rack A01', priority: 'low', assignee: 'Lisa Wong', duration: '1h 20m', progress: 45 },
])

// Work Orders
const workOrders = ref({
  pending: 18,
  inProgress: 12,
  completed: 156,
  overdue: 3
})

const recentWorkOrders = ref([
  { id: 1, title: 'Chiller Annual Maintenance', asset: 'Chiller-01', priority: 'high', date: '2024-01-15' },
  { id: 2, title: 'UPS Battery Replacement', asset: 'UPS-02', priority: 'critical', date: '2024-01-14' },
  { id: 3, title: 'Filter Replacement', asset: 'CRAC-03', priority: 'medium', date: '2024-01-13' },
  { id: 4, title: 'Firmware Update', asset: 'PDU-01', priority: 'low', date: '2024-01-12' },
])

// Resources
const activeResources = ref([
  { id: 1, name: 'John Smith', task: 'Emergency Response', eta: 'On Site', color: '#ef4444' },
  { id: 2, name: 'Sarah Chen', task: 'HVAC Repair', eta: '10 min', color: '#f59e0b' },
  { id: 3, name: 'Mike Johnson', task: 'UPS Maintenance', eta: '30 min', color: '#3b82f6' },
  { id: 4, name: 'Lisa Wong', task: 'Inspection', eta: '2 hours', color: '#10b981' },
])

// Energy Data
const currentPower = ref(1245)
const todayUsage = ref(18750)
const peakDemand = ref(1650)
const pueValue = ref(1.42)

// Executive Summary
const mtbf = ref(124)
const mttr = ref(2.8)
const availability = ref(99.95)
const energySavings = ref(15.2)
const complianceRate = ref(94)
const carbonSaved = ref(1250)
const summaryDate = ref('')

// Chart Controls
const trendPeriod = ref('hour')
const alarmCategory = ref('severity')

// Dialog State
const incidentDialogVisible = ref(false)
const selectedIncident = ref<any>(null)
const incidentDescription = ref('')
const incidentAssignee = ref('')
const incidentEta = ref('')

// Global Status
const globalStatusClass = computed(() => {
  if (criticalAlarms.value > 0) return 'critical'
  if (majorAlarms.value > 5) return 'warning'
  return 'healthy'
})

const globalStatusIcon = computed(() => {
  if (criticalAlarms.value > 0) return 'WarningFilled'
  if (majorAlarms.value > 5) return 'Bell'
  return 'SuccessFilled'
})

const globalStatusTitle = computed(() => {
  if (criticalAlarms.value > 0) return 'Critical Situation Detected'
  if (majorAlarms.value > 5) return 'Warning: Multiple Alarms'
  return 'All Systems Operational'
})

const globalStatusMessage = computed(() => {
  if (criticalAlarms.value > 0) return `${criticalAlarms.value} critical alarms require immediate attention`
  if (majorAlarms.value > 5) return `${majorAlarms.value} major alarms active`
  return `System health at ${systemHealth.value}% - Normal operation`
})

// Situation Events
const situationEvents = ref([
  { id: 1, time: '14:32', title: 'Power Spike Detected', description: 'Voltage fluctuation in UPS output', status: 'resolved' },
  { id: 2, time: '14:15', title: 'Temperature Alert', description: 'Chiller-01 temperature exceeded threshold', status: 'investigating' },
  { id: 3, time: '13:58', title: 'Maintenance Started', description: 'Preventive maintenance on CRAC-03', status: 'in-progress' },
  { id: 4, time: '13:30', title: 'Network Incident', description: 'Switch reboot completed successfully', status: 'resolved' },
  { id: 5, time: '12:45', title: 'Security Alert', description: 'Unauthorized access attempt at DC East', status: 'investigating' },
])

// Chart Refs
const performanceChartRef = ref<HTMLElement | null>(null)
const alarmDistributionChartRef = ref<HTMLElement | null>(null)
const energyTrendChartRef = ref<HTMLElement | null>(null)
const mapContainer = ref<HTMLElement | null>(null)

// Chart Instances
let performanceChart: echarts.ECharts | null = null
let alarmDistributionChart: echarts.ECharts | null = null
let energyTrendChart: echarts.ECharts | null = null

// Helper Functions
const getHealthColor = (health: number) => {
  if (health >= 90) return '#10b981'
  if (health >= 70) return '#f59e0b'
  return '#ef4444'
}

const getSiteTempClass = (temp: number) => {
  if (temp < 24) return 'good'
  if (temp < 27) return 'warning'
  return 'critical'
}

const getEtaTagType = (eta: string) => {
  if (eta === 'On Site') return 'danger'
  if (eta.includes('min')) return 'warning'
  return 'info'
}

const getPriorityTagType = (priority: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return types[priority] || 'info'
}

// Actions
const refreshAllData = () => {
  ElMessage.success('Dashboard data refreshed')
}

const fullscreenMode = () => {
  const elem = document.documentElement
  if (!document.fullscreenElement) {
    elem.requestFullscreen()
    ElMessage.success('Fullscreen mode enabled')
  } else {
    document.exitFullscreen()
  }
}

const exportDashboard = () => {
  ElMessage.success('Dashboard export started')
}

const viewIncidents = () => {
  ElMessage.info('Viewing all incidents')
}

const acknowledgeStatus = () => {
  ElMessage.info('Status acknowledged')
}

const viewAllAlarms = () => {
  ElMessage.info('Viewing all alarms')
}

const acknowledgeAlarm = (alarm: any) => {
  ElMessage.success(`Alarm "${alarm.title}" acknowledged`)
  const index = recentAlarms.value.findIndex(a => a.id === alarm.id)
  if (index !== -1) recentAlarms.value.splice(index, 1)
  if (alarm.severity === 'critical') criticalAlarms.value--
  else if (alarm.severity === 'major') majorAlarms.value--
}

const selectSite = (site: any) => {
  ElMessage.info(`Selected site: ${site.name}`)
}

const createIncident = () => {
  incidentDialogVisible.value = true
  selectedIncident.value = null
  incidentDescription.value = ''
}

const viewDispatch = () => {
  ElMessage.info('Opening dispatch management')
}

const viewWorkOrders = () => {
  ElMessage.info('Viewing all work orders')
}

const viewEnergyDetails = () => {
  ElMessage.info('Opening energy analytics')
}

const refreshSituation = () => {
  ElMessage.success('Situation awareness refreshed')
}

const updateIncident = () => {
  ElMessage.success('Incident updated successfully')
  incidentDialogVisible.value = false
}

const mapZoomIn = () => {
  ElMessage.info('Map zoom in')
}

const mapZoomOut = () => {
  ElMessage.info('Map zoom out')
}

const resetMap = () => {
  ElMessage.info('Map reset')
}

// Chart Initialization
const initPerformanceChart = () => {
  if (!performanceChartRef.value) return
  if (performanceChart) performanceChart.dispose()
  performanceChart = echarts.init(performanceChartRef.value)

  const hourData = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
  const dayData = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const weekData = ['Week 1', 'Week 2', 'Week 3', 'Week 4']

  performanceChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Temperature', 'Power Usage', 'Efficiency'], bottom: 0, left: 'center' },
    xAxis: { type: 'category', data: hourData },
    yAxis: [{ type: 'value', name: 'Temperature (°C)' }, { type: 'value', name: 'Power (kW)' }],
    series: [
      { name: 'Temperature', type: 'line', data: [24.2, 24.5, 24.8, 25.1, 25.3, 25.0, 24.7, 24.4, 24.1], lineStyle: { color: '#f59e0b', width: 2 }, smooth: true, yAxisIndex: 0 },
      { name: 'Power Usage', type: 'line', data: [1150, 1180, 1220, 1250, 1280, 1260, 1230, 1200, 1170], lineStyle: { color: '#3b82f6', width: 2 }, smooth: true, yAxisIndex: 1 },
      { name: 'Efficiency', type: 'bar', data: [92, 93, 94, 94, 93, 95, 96, 95, 94], itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] }, yAxisIndex: 0 }
    ]
  })
}

const initAlarmDistributionChart = () => {
  if (!alarmDistributionChartRef.value) return
  if (alarmDistributionChart) alarmDistributionChart.dispose()
  alarmDistributionChart = echarts.init(alarmDistributionChartRef.value)

  alarmDistributionChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie', radius: ['40%', '70%'], data: [
        { name: 'Critical', value: 3, itemStyle: { color: '#ef4444' } },
        { name: 'Major', value: 8, itemStyle: { color: '#f59e0b' } },
        { name: 'Warning', value: 15, itemStyle: { color: '#3b82f6' } },
        { name: 'Info', value: 22, itemStyle: { color: '#10b981' } }
      ], label: { show: true, formatter: '{b}: {d}%' }, emphasis: { scale: true }
    }]
  })
}

const initEnergyTrendChart = () => {
  if (!energyTrendChartRef.value) return
  if (energyTrendChart) energyTrendChart.dispose()
  energyTrendChart = echarts.init(energyTrendChartRef.value)

  energyTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['00', '04', '08', '12', '16', '20', '24'] },
    yAxis: { type: 'value', name: 'kW' },
    series: [{
      type: 'line', data: [850, 820, 950, 1250, 1180, 1050, 920],
      smooth: true, lineStyle: { color: '#f59e0b', width: 2 },
      areaStyle: { opacity: 0.1, color: '#f59e0b' }, symbol: 'circle', symbolSize: 6
    }]
  })
}

// Watch for period changes
watch(trendPeriod, () => initPerformanceChart())
watch(alarmCategory, () => initAlarmDistributionChart())

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
  summaryDate.value = now.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Simulate real-time updates
let dataInterval: ReturnType<typeof setInterval> | null = null

const startDataSimulation = () => {
  dataInterval = setInterval(() => {
    // Randomly update metrics
    criticalAlarms.value = Math.floor(Math.random() * 5) + 1
    majorAlarms.value = Math.floor(Math.random() * 10) + 3
    activeFaults.value = Math.floor(Math.random() * 15) + 5
    systemHealth.value = +(95 + Math.random() * 4).toFixed(1)
    currentPower.value = Math.floor(Math.random() * 300) + 1100
    pueValue.value = +(1.38 + Math.random() * 0.08).toFixed(2)

    // Random new alarms
    if (Math.random() > 0.7) {
      const newAlarm = {
        id: Date.now(),
        title: 'New alarm detected',
        location: 'Unknown',
        time: 'Just now',
        severity: Math.random() > 0.7 ? 'critical' : 'major'
      }
      recentAlarms.value.unshift(newAlarm)
      if (recentAlarms.value.length > 10) recentAlarms.value.pop()
    }
  }, 5000)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (performanceChart) performanceChart.resize()
    if (alarmDistributionChart) alarmDistributionChart.resize()
    if (energyTrendChart) energyTrendChart.resize()
  }, 200)
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initPerformanceChart()
          initAlarmDistributionChart()
          initEnergyTrendChart()
          startDataSimulation()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  if (performanceChart) performanceChart.dispose()
  if (alarmDistributionChart) alarmDistributionChart.dispose()
  if (energyTrendChart) energyTrendChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.operations-dashboard-container {
  min-height: 100vh;
  background: #f0f2f6;
}

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

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
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
  width: 320px;
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
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
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
.dashboard-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 12px;
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

/* Global Status Banner */
.global-status {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  border-radius: 16px;
  margin-bottom: 24px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.global-status.critical {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-left: 4px solid #ef4444;
}

.global-status.warning {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border-left: 4px solid #f59e0b;
}

.global-status.healthy {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-left: 4px solid #10b981;
}

.status-icon {
  font-size: 28px;
}
.global-status.critical .status-icon { color: #ef4444; }
.global-status.warning .status-icon { color: #f59e0b; }
.global-status.healthy .status-icon { color: #10b981; }

.status-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.status-title {
  font-weight: 700;
  font-size: 16px;
  color: #1e293b;
}

.status-message {
  font-size: 13px;
  color: #64748b;
}

/* KPI Cards */
.kpi-row {
  margin-bottom: 24px;
}

.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
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

.kpi-icon.red { background: #fef2f2; color: #ef4444; }
.kpi-icon.orange { background: #fffbeb; color: #f59e0b; }
.kpi-icon.blue { background: #eff6ff; color: #3b82f6; }
.kpi-icon.green { background: #ecfdf5; color: #10b981; }

.kpi-info {
  flex: 1;
}

.kpi-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.kpi-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.kpi-trend {
  display: inline-block;
  font-size: 12px;
  margin-top: 4px;
}

.kpi-trend.up { color: #ef4444; }
.kpi-trend.down { color: #10b981; }

/* Dashboard Cards */
.dashboard-card {
  border-radius: 20px;
  margin-bottom: 24px;
  overflow: hidden;
}

.dashboard-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
}

.card-title .el-icon {
  color: #3b82f6;
}

/* Alarm List */
.alarm-list {
  max-height: 320px;
  overflow-y: auto;
}

.alarm-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  transition: all 0.2s;
}

.alarm-item.critical { border-left: 3px solid #ef4444; }
.alarm-item.major { border-left: 3px solid #f59e0b; }
.alarm-item.warning { border-left: 3px solid #3b82f6; }

.alarm-icon {
  font-size: 20px;
}
.alarm-item.critical .alarm-icon { color: #ef4444; }
.alarm-item.major .alarm-icon { color: #f59e0b; }
.alarm-item.warning .alarm-icon { color: #3b82f6; }

.alarm-content {
  flex: 1;
}

.alarm-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.alarm-location {
  font-size: 11px;
  color: #64748b;
}

.alarm-time {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 4px;
}

.no-alarms {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
}

.no-alarms .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

/* Site Map */
.site-map {
  max-height: 320px;
  overflow-y: auto;
}

.site-item {
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.site-item:hover {
  background: #f8fafc;
}

.site-status {
  width: 100%;
  margin-bottom: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.site-status.critical .status-dot { background: #ef4444; box-shadow: 0 0 0 2px #fee2e2; }
.site-status.warning .status-dot { background: #f59e0b; box-shadow: 0 0 0 2px #fef3c7; }
.site-status.healthy .status-dot { background: #10b981; box-shadow: 0 0 0 2px #d1fae5; }

.site-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.site-name {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.site-location {
  font-size: 11px;
  color: #94a3b8;
}

.site-metrics {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
}

.site-metrics .metric {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #f1f5f9;
}

.site-metrics .metric.good { color: #10b981; }
.site-metrics .metric.warning { color: #f59e0b; }
.site-metrics .metric.critical { color: #ef4444; }

/* Incident List */
.incident-list {
  max-height: 320px;
  overflow-y: auto;
}

.incident-item {
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
}

.incident-priority {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.incident-priority.critical { background: #fef2f2; color: #ef4444; }
.incident-priority.high { background: #fffbeb; color: #f59e0b; }
.incident-priority.medium { background: #eff6ff; color: #3b82f6; }
.incident-priority.low { background: #ecfdf5; color: #10b981; }

.incident-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 6px;
}

.incident-details {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 8px;
}

.incident-details .el-icon {
  margin-right: 4px;
}

/* Chart Containers */
.chart-container {
  height: 300px;
  width: 100%;
}

.mini-chart {
  height: 80px;
  width: 100%;
  margin-top: 12px;
}

/* Dispatch List */
.dispatch-list {
  max-height: 280px;
  overflow-y: auto;
}

.dispatch-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
}

.dispatch-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.dispatch-info {
  flex: 1;
}

.dispatch-name {
  display: block;
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.dispatch-task {
  display: block;
  font-size: 11px;
  color: #64748b;
}

/* Work Orders */
.workorder-stats {
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #64748b;
}

.workorder-list {
  max-height: 200px;
  overflow-y: auto;
}

.workorder-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.workorder-priority {
  width: 50px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.workorder-priority.critical { color: #ef4444; }
.workorder-priority.high { color: #f59e0b; }
.workorder-priority.medium { color: #3b82f6; }
.workorder-priority.low { color: #10b981; }

.workorder-info {
  flex: 1;
}

.workorder-title {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.workorder-asset {
  display: block;
  font-size: 10px;
  color: #94a3b8;
}

.workorder-date {
  font-size: 10px;
  color: #94a3b8;
}

/* Energy Metrics */
.energy-metrics {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.energy-main {
  text-align: center;
}

.energy-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.energy-value span {
  font-size: 14px;
  color: #64748b;
}

.energy-label {
  font-size: 11px;
  color: #64748b;
}

.energy-stats {
  flex: 1;
}

.energy-stat {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.energy-stat .stat-label {
  color: #64748b;
}

.energy-stat .stat-value {
  font-weight: 600;
  color: #1e293b;
}

/* Map Container */
.map-container {
  height: 320px;
  position: relative;
  border-radius: 12px;
  overflow: hidden;
}

.map-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  position: relative;
  border-radius: 12px;
}

.map-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  height: 100%;
  opacity: 0.1;
}

.map-cell {
  border: 1px solid #3b82f6;
}

.map-markers {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.map-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
}

.marker-pulse {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.marker-pulse.critical {
  background: #ef4444;
  box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.4);
}

.marker-pulse.warning {
  background: #f59e0b;
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.4);
}

.marker-pulse.healthy {
  background: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.4);
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  75% { transform: scale(1.5); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}

.marker-tooltip {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  background: #1e293b;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

.map-marker:hover .marker-tooltip {
  opacity: 1;
}

/* Situation Timeline */
.situation-timeline {
  max-height: 320px;
  overflow-y: auto;
}

.situation-event {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
}

.event-time {
  font-size: 11px;
  font-weight: 600;
  color: #3b82f6;
  min-width: 45px;
}

.event-content {
  flex: 1;
}

.event-title {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.event-desc {
  font-size: 11px;
  color: #64748b;
}

.event-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #e2e8f0;
}

.event-status.resolved { background: #d1fae5; color: #10b981; }
.event-status.investigating { background: #fef3c7; color: #f59e0b; }
.event-status.in-progress { background: #dbeafe; color: #3b82f6; }

/* Executive Summary */
.executive-summary {
  margin-top: 8px;
}

.summary-card {
  border-radius: 20px;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.summary-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.summary-date {
  font-size: 12px;
  color: #64748b;
}

.summary-item {
  text-align: center;
}

.item-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.item-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.item-trend {
  display: block;
  font-size: 10px;
}

.item-trend.up { color: #10b981; }
.item-trend.down { color: #ef4444; }

/* Responsive */
@media (max-width: 1200px) {
  .dashboard-main { padding: 16px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .header-actions { flex-wrap: wrap; }
  .global-status { flex-direction: column; text-align: center; }
}
</style>