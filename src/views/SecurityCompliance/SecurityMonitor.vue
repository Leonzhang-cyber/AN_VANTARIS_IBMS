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
          <span class="loading-title">Loading Security Monitor</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Real-time Security Monitoring & Alert System</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="security-monitor-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Security Monitor</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>Security Monitor</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-select v-model="timeRange" size="large" style="width: 140px">
          <el-option label="Last Hour" value="hour" />
          <el-option label="Last 24 Hours" value="day" />
          <el-option label="Last 7 Days" value="week" />
          <el-option label="Last 30 Days" value="month" />
        </el-select>
        <el-button type="primary" @click="refreshDashboard">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button type="info" plain @click="exportLogs">
          <el-icon><Download /></el-icon>
          Export Logs
        </el-button>
      </div>
    </div>

    <!-- Security Status Summary -->
    <div class="status-summary">
      <el-card class="status-card" shadow="hover">
        <div class="status-header">
          <span class="status-title">Overall Security Status</span>
          <el-tag :type="getOverallStatusType()" size="large">{{ overallStatus }}</el-tag>
        </div>
        <div class="status-metrics">
          <div class="metric">
            <div class="metric-value">{{ totalEvents }}</div>
            <div class="metric-label">Total Events</div>
          </div>
          <div class="metric">
            <div class="metric-value critical">{{ criticalEvents }}</div>
            <div class="metric-label">Critical</div>
          </div>
          <div class="metric">
            <div class="metric-value warning">{{ highEvents }}</div>
            <div class="metric-label">High</div>
          </div>
          <div class="metric">
            <div class="metric-value medium">{{ mediumEvents }}</div>
            <div class="metric-label">Medium</div>
          </div>
          <div class="metric">
            <div class="metric-value">{{ lowEvents }}</div>
            <div class="metric-label">Low</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Real-time Threat Map & Event Timeline -->
    <div class="monitoring-row">
      <!-- Threat Intelligence Map -->
      <el-card class="threat-map-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Location /></el-icon> Threat Intelligence Map</span>
            <div class="map-controls">
              <el-radio-group v-model="mapLayer" size="small">
                <el-radio-button label="threats">Active Threats</el-radio-button>
                <el-radio-button label="incidents">Incidents</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div ref="threatMapRef" class="threat-map"></div>
      </el-card>

      <!-- Real-time Event Timeline -->
      <el-card class="events-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><List /></el-icon> Real-time Event Timeline</span>
            <el-switch v-model="autoScroll" active-text="Auto-scroll" />
          </div>
        </template>
        <div ref="timelineContainer" class="events-timeline">
          <div v-for="event in realTimeEvents" :key="event.id" :class="['event-item', event.severity]">
            <div class="event-time">{{ event.time }}</div>
            <div class="event-icon">
              <el-icon><component :is="getEventIcon(event.type)" /></el-icon>
            </div>
            <div class="event-content">
              <div class="event-title">{{ event.title }}</div>
              <div class="event-detail">{{ event.detail }}</div>
              <div class="event-source">Source: {{ event.source }} | Destination: {{ event.destination }}</div>
            </div>
            <div class="event-actions">
              <el-button size="small" text type="primary" @click="investigateEvent(event)">Investigate</el-button>
              <el-button size="small" text type="info" @click="acknowledgeEvent(event)">Acknowledge</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Security Analytics Charts -->
    <div class="analytics-row">
      <!-- Attack Trends -->
      <el-card class="trends-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Attack Trends (Last 7 Days)</span>
            <el-button text type="primary" @click="refreshTrendsChart">Refresh</el-button>
          </div>
        </template>
        <div ref="trendsChartRef" class="trends-chart"></div>
      </el-card>

      <!-- Attack Type Distribution -->
      <el-card class="distribution-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><PieChart /></el-icon> Attack Type Distribution</span>
            <el-button text type="primary" @click="refreshDistributionChart">Refresh</el-button>
          </div>
        </template>
        <div ref="distributionChartRef" class="distribution-chart"></div>
      </el-card>
    </div>

    <!-- Top Attack Sources & Targeted Assets -->
    <div class="sources-row">
      <!-- Top Attack Sources -->
      <el-card class="sources-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><User /></el-icon> Top Attack Sources</span>
            <el-button text type="primary" @click="blockSource">Block Selected</el-button>
          </div>
        </template>
        <el-table :data="topAttackSources" stripe style="width: 100%">
          <el-table-column prop="ip" label="IP Address" width="150" />
          <el-table-column prop="location" label="Location" width="150" />
          <el-table-column prop="events" label="Events" width="100" sortable />
          <el-table-column prop="lastSeen" label="Last Seen" width="180" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="danger" @click="blockIP(row)">Block</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- Targeted Assets -->
      <el-card class="assets-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Monitor /></el-icon> Most Targeted Assets</span>
            <el-button text type="primary" @click="viewAllAssets">View All</el-button>
          </div>
        </template>
        <el-table :data="targetedAssets" stripe style="width: 100%">
          <el-table-column prop="name" label="Asset Name" width="180" />
          <el-table-column prop="type" label="Type" width="120" />
          <el-table-column prop="attacks" label="Attacks" width="100" sortable />
          <el-table-column prop="riskLevel" label="Risk Level" width="120">
            <template #default="{ row }">
              <el-tag :type="getRiskType(row.riskLevel)" size="small">{{ row.riskLevel }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="protectAsset(row)">Protect</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Active Alerts Panel -->
    <el-card class="alerts-panel" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><BellFilled /></el-icon> Active Alerts ({{ activeAlerts.length }})</span>
          <el-button type="primary" size="small" @click="acknowledgeAllAlerts">Acknowledge All</el-button>
        </div>
      </template>
      <div class="alerts-grid">
        <div v-for="alert in activeAlerts" :key="alert.id" :class="['alert-card', alert.severity]" @click="viewAlertDetails(alert)">
          <div class="alert-header">
            <el-tag :type="getSeverityTagType(alert.severity)" size="small">{{ alert.severity }}</el-tag>
            <span class="alert-time">{{ alert.time }}</span>
          </div>
          <div class="alert-title">{{ alert.title }}</div>
          <div class="alert-description">{{ alert.description }}</div>
          <div class="alert-footer">
            <span><el-icon><Location /></el-icon> {{ alert.source }}</span>
            <el-button size="small" type="primary" plain @click.stop="respondToAlert(alert)">Respond</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Security Rules & Policies Summary -->
    <div class="rules-section">
      <el-card class="rules-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Setting /></el-icon> Security Rules & Policies</span>
            <el-button text type="primary" @click="configureRules">Configure</el-button>
          </div>
        </template>
        <div class="rules-summary">
          <div class="rule-stat">
            <div class="stat-number">{{ activeRules }}</div>
            <div class="stat-label">Active Rules</div>
          </div>
          <div class="rule-stat">
            <div class="stat-number">{{ triggeredRules }}</div>
            <div class="stat-label">Triggered (24h)</div>
          </div>
          <div class="rule-stat">
            <div class="stat-number">{{ autoBlocked }}</div>
            <div class="stat-label">Auto-blocked IPs</div>
          </div>
          <div class="rule-stat">
            <div class="stat-number">{{ whitelistedIPs }}</div>
            <div class="stat-label">Whitelisted IPs</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="runThreatHunt">
          <el-icon><Search /></el-icon>
          Threat Hunt
        </el-button>
        <el-button type="success" plain @click="generateIncidentReport">
          <el-icon><Document /></el-icon>
          Incident Report
        </el-button>
        <el-button type="warning" plain @click="startForensicAnalysis">
          <el-icon><DataAnalysis /></el-icon>
          Forensic Analysis
        </el-button>
        <el-button type="info" plain @click="viewPlaybooks">
          <el-icon><Guide /></el-icon>
          Response Playbooks
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, Location, List, TrendCharts, PieChart, User,
  Monitor, BellFilled, Setting, Search, Document, DataAnalysis, Guide,
  WarningFilled, Lock, Key, Cpu, Connection, Warning
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing Security Monitor...')

const loadingMessages = [
  'Initializing Security Monitor...',
  'Connecting to security sensors...',
  'Loading threat intelligence...',
  'Monitoring system active!'
]

// Time range filter
const timeRange = ref('day')
const autoScroll = ref(true)

// Security status
const overallStatus = ref('Elevated')
const totalEvents = ref(1248)
const criticalEvents = ref(3)
const highEvents = ref(12)
const mediumEvents = ref(34)
const lowEvents = ref(56)

// Real-time events
const realTimeEvents = ref([
  { id: 1, severity: 'critical', type: 'intrusion', title: 'Potential Intrusion Detected', detail: 'Multiple failed login attempts from IP 45.123.45.67', source: '45.123.45.67', destination: 'BACnet Gateway', time: '09:45:32', acknowledged: false },
  { id: 2, severity: 'high', type: 'malware', title: 'Malware Signature Detected', detail: 'Known ransomware pattern detected on file server', source: 'File Server', destination: 'Backup System', time: '09:32:18', acknowledged: false },
  { id: 3, severity: 'high', type: 'anomaly', title: 'Unusual Traffic Pattern', detail: 'Unexpected outbound traffic to unknown IP', source: 'HVAC Controller', destination: '185.142.53.12', time: '09:28:45', acknowledged: false },
  { id: 4, severity: 'medium', type: 'access', title: 'Privilege Escalation Attempt', detail: 'User attempted unauthorized access to SCADA', source: 'User: jdoe', destination: 'SCADA Server', time: '09:15:22', acknowledged: false },
  { id: 5, severity: 'medium', type: 'vulnerability', title: 'Vulnerability Scan Detected', detail: 'Port scan detected from internal IP', source: '192.168.1.105', destination: 'Various', time: '09:08:33', acknowledged: false },
  { id: 6, severity: 'low', type: 'policy', title: 'Policy Violation', detail: 'USB device usage outside approved hours', source: 'Engineering WS-03', destination: 'USB Storage', time: '08:55:12', acknowledged: false }
])

// Top attack sources
const topAttackSources = ref([
  { ip: '45.123.45.67', location: 'Russia, Moscow', events: 234, lastSeen: '09:45:32' },
  { ip: '103.45.67.89', location: 'China, Shanghai', events: 187, lastSeen: '09:30:15' },
  { ip: '185.142.53.12', location: 'Netherlands, Amsterdam', events: 156, lastSeen: '09:28:45' },
  { ip: '89.34.56.78', location: 'Germany, Frankfurt', events: 98, lastSeen: '09:12:33' },
  { ip: '192.168.1.105', location: 'Internal Network', events: 67, lastSeen: '09:08:22' }
])

// Targeted assets
const targetedAssets = ref([
  { name: 'BACnet Gateway', type: 'OT Device', attacks: 234, riskLevel: 'Critical' },
  { name: 'SCADA Server', type: 'Control System', attacks: 187, riskLevel: 'High' },
  { name: 'HVAC Controller', type: 'OT Device', attacks: 156, riskLevel: 'High' },
  { name: 'File Server', type: 'IT Asset', attacks: 98, riskLevel: 'Medium' },
  { name: 'Engineering WS-03', type: 'Workstation', attacks: 67, riskLevel: 'Medium' }
])

// Active alerts
const activeAlerts = ref([
  { id: 1, severity: 'critical', title: 'Ransomware Activity Detected', description: 'SMB file encryption pattern detected on file shares', source: 'File Server Cluster', time: '09:32:18' },
  { id: 2, severity: 'high', title: 'Brute Force Attack', description: 'Over 100 failed login attempts on BACnet gateway', source: 'External IP 45.123.45.67', time: '09:45:32' },
  { id: 3, severity: 'high', title: 'Data Exfiltration Attempt', description: 'Large outbound data transfer to unknown IP', source: 'Database Server', time: '09:28:45' },
  { id: 4, severity: 'medium', title: 'Suspicious Process Execution', description: 'PowerShell execution with obfuscated parameters', source: 'Engineering WS-03', time: '09:15:22' }
])

// Rules stats
const activeRules = ref(147)
const triggeredRules = ref(23)
const autoBlocked = ref(8)
const whitelistedIPs = ref(15)

// Chart refs
const threatMapRef = ref<HTMLElement>()
const trendsChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()
const timelineContainer = ref<HTMLElement>()

let trendsChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null
let threatMap: echarts.ECharts | null = null

let eventInterval: number

// Helper functions
const getOverallStatusType = () => {
  if (criticalEvents.value > 0) return 'danger'
  if (highEvents.value > 5) return 'warning'
  return 'success'
}

const getEventIcon = (type: string) => {
  switch (type) {
    case 'intrusion': return 'WarningFilled'
    case 'malware': return 'Warning'
    case 'anomaly': return 'Connection'
    case 'access': return 'Key'
    case 'vulnerability': return 'Lock'
    default: return 'Setting'
  }
}

const getSeverityTagType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getRiskType = (risk: string) => {
  switch (risk) {
    case 'Critical': return 'danger'
    case 'High': return 'warning'
    case 'Medium': return 'primary'
    default: return 'info'
  }
}

// Initialize Threat Map (simulated world map with threat locations)
const initThreatMap = () => {
  if (!threatMapRef.value) return
  threatMap = echarts.init(threatMapRef.value)

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}' },
    series: [{
      type: 'scatter',
      coordinateSystem: 'geo',
      data: [
        { name: 'Moscow, RU', value: [37.6173, 55.7558], severity: 'critical' },
        { name: 'Shanghai, CN', value: [121.4737, 31.2304], severity: 'high' },
        { name: 'Amsterdam, NL', value: [4.9041, 52.3676], severity: 'high' },
        { name: 'Frankfurt, DE', value: [8.6821, 50.1109], severity: 'medium' },
        { name: 'New York, US', value: [-74.0060, 40.7128], severity: 'medium' }
      ],
      symbolSize: (val: any) => {
        if (val.severity === 'critical') return 20
        if (val.severity === 'high') return 15
        return 10
      },
      itemStyle: {
        color: (param: any) => {
          if (param.data.severity === 'critical') return '#ef4444'
          if (param.data.severity === 'high') return '#f59e0b'
          return '#3b82f6'
        }
      },
      label: { show: true, formatter: '{b}', position: 'right', offset: [5, 0] }
    }],
    geo: {
      map: 'world',
      roam: true,
      itemStyle: { borderColor: '#e2e8f0', areaColor: '#f1f5f9' },
      emphasis: { label: { show: false } }
    }
  }
  threatMap.setOption(option)
}

// Initialize trends chart
const initTrendsChart = () => {
  if (!trendsChartRef.value) return
  trendsChart = echarts.init(trendsChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Critical', 'High', 'Medium', 'Low'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value', name: 'Number of Events' },
    series: [
      { name: 'Critical', type: 'line', data: [5, 3, 4, 6, 2, 3, 4], lineStyle: { color: '#ef4444', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'High', type: 'line', data: [12, 15, 10, 14, 11, 13, 12], lineStyle: { color: '#f59e0b', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Medium', type: 'line', data: [25, 28, 30, 27, 32, 29, 34], lineStyle: { color: '#eab308', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Low', type: 'line', data: [45, 48, 52, 50, 55, 53, 56], lineStyle: { color: '#10b981', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  }
  trendsChart.setOption(option)
}

// Initialize distribution chart
const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  distributionChart = echarts.init(distributionChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 35, name: 'Brute Force', itemStyle: { color: '#ef4444' } },
        { value: 28, name: 'Malware', itemStyle: { color: '#f59e0b' } },
        { value: 18, name: 'Phishing', itemStyle: { color: '#eab308' } },
        { value: 12, name: 'DDoS', itemStyle: { color: '#8b5cf6' } },
        { value: 7, name: 'Insider Threat', itemStyle: { color: '#ec489a' } }
      ],
      label: { formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }
  distributionChart.setOption(option)
}

// Auto-scroll timeline
const scrollToBottom = async () => {
  if (autoScroll.value && timelineContainer.value) {
    await nextTick()
    timelineContainer.value.scrollTop = timelineContainer.value.scrollHeight
  }
}

// Simulate new real-time events
const simulateNewEvent = () => {
  const newEvents = [
    { severity: 'high', type: 'intrusion', title: 'New Intrusion Attempt', detail: 'Port scan detected from new IP', source: '203.45.67.89', destination: 'Web Server' },
    { severity: 'medium', type: 'access', title: 'Failed Login', detail: 'Invalid credentials on admin portal', source: '192.168.1.200', destination: 'Admin Panel' },
    { severity: 'low', type: 'policy', title: 'Configuration Change', detail: 'Firewall rule modified', source: 'Admin Workstation', destination: 'Firewall' }
  ]

  const newEvent = newEvents[Math.floor(Math.random() * newEvents.length)]
  const event = {
    id: Date.now(),
    ...newEvent,
    time: new Date().toLocaleTimeString(),
    acknowledged: false
  }

  realTimeEvents.value.unshift(event)
  if (realTimeEvents.value.length > 50) realTimeEvents.value.pop()

  // Update counts
  if (event.severity === 'critical') criticalEvents.value++
  else if (event.severity === 'high') highEvents.value++
  else if (event.severity === 'medium') mediumEvents.value++
  else lowEvents.value++
  totalEvents.value++

  scrollToBottom()
}

// Event handlers
const refreshDashboard = () => {
  ElMessage.info('Refreshing security monitor data...')
  setTimeout(() => {
    ElMessage.success('Dashboard refreshed')
  }, 1000)
}

const exportLogs = () => {
  ElMessage.info('Exporting security logs...')
  setTimeout(() => {
    ElMessage.success('Logs exported successfully')
  }, 2000)
}

const investigateEvent = (event: any) => {
  ElMessage.info(`Investigating event: ${event.title}`)
}

const acknowledgeEvent = (event: any) => {
  event.acknowledged = true
  realTimeEvents.value = realTimeEvents.value.filter(e => e.id !== event.id)
  ElMessage.success(`Event acknowledged: ${event.title}`)
}

const blockIP = (source: any) => {
  ElMessageBox.confirm(`Block IP: ${source.ip}? This will add the IP to block list.`, 'Block IP', {
    confirmButtonText: 'Block',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    topAttackSources.value = topAttackSources.value.filter(s => s.ip !== source.ip)
    autoBlocked.value++
    ElMessage.success(`IP ${source.ip} has been blocked`)
  }).catch(() => {})
}

const blockSource = () => {
  ElMessage.info('Select IP addresses to block')
}

const protectAsset = (asset: any) => {
  ElMessage.info(`Applying additional protection to: ${asset.name}`)
}

const viewAllAssets = () => {
  ElMessage.info('Viewing all assets')
}

const viewAlertDetails = (alert: any) => {
  ElMessageBox.alert(
      `Alert: ${alert.title}\nDescription: ${alert.description}\nSource: ${alert.source}\nTime: ${alert.time}\n\nRecommended Action: Investigate immediately and contain affected systems.`,
      'Alert Details',
      { confirmButtonText: 'OK', type: 'warning' }
  )
}

const respondToAlert = (alert: any) => {
  ElMessage.info(`Responding to alert: ${alert.title}`)
}

const acknowledgeAllAlerts = () => {
  ElMessageBox.confirm('Acknowledge all active alerts?', 'Confirm', {
    confirmButtonText: 'Acknowledge All',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    activeAlerts.value = []
    ElMessage.success('All alerts acknowledged')
  }).catch(() => {})
}

const configureRules = () => {
  ElMessage.info('Opening security rules configuration')
}

const runThreatHunt = () => {
  ElMessage.info('Initiating proactive threat hunt across all systems...')
  setTimeout(() => {
    ElMessage.success('Threat hunt completed. No hidden threats detected.')
  }, 5000)
}

const generateIncidentReport = () => {
  ElMessage.info('Generating incident report...')
}

const startForensicAnalysis = () => {
  ElMessage.info('Starting forensic analysis on recent incidents')
}

const viewPlaybooks = () => {
  ElMessage.info('Viewing incident response playbooks')
}

const refreshTrendsChart = () => {
  if (trendsChart) {
    trendsChart.setOption({ series: [] })
    initTrendsChart()
    ElMessage.success('Chart refreshed')
  }
}

const refreshDistributionChart = () => {
  if (distributionChart) {
    distributionChart.setOption({ series: [] })
    initDistributionChart()
    ElMessage.success('Chart refreshed')
  }
}

// Scroll timeline to bottom on new events
const scrollToBottomOnEvents = () => {
  if (autoScroll.value && timelineContainer.value) {
    scrollToBottom()
  }
}

// Watch for real-time events changes
import { watch } from 'vue'
watch(realTimeEvents, () => {
  scrollToBottomOnEvents()
}, { deep: true })

// Loading animation
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
      setTimeout(() => {
        initThreatMap()
        initTrendsChart()
        initDistributionChart()
        eventInterval = setInterval(simulateNewEvent, 15000)
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (eventInterval) clearInterval(eventInterval)
  if (trendsChart) trendsChart.dispose()
  if (distributionChart) distributionChart.dispose()
  if (threatMap) threatMap.dispose()
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Content - White Background ==================== */
.security-monitor-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Status Summary */
.status-summary {
  margin-bottom: 24px;
}

.status-card {
  border-radius: 12px;
  background: white;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.status-metrics {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.metric {
  text-align: center;
  padding: 12px 20px;
  background: #f8fafc;
  border-radius: 10px;
  min-width: 100px;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.metric-value.critical { color: #ef4444; }
.metric-value.warning { color: #f59e0b; }
.metric-value.medium { color: #eab308; }

.metric-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* Monitoring Row */
.monitoring-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.threat-map-card,
.events-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.threat-map {
  height: 400px;
  width: 100%;
}

.events-timeline {
  height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.event-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 12px;
  background: #f8fafc;
  border-left: 3px solid;
}

.event-item.critical { border-left-color: #ef4444; }
.event-item.high { border-left-color: #f59e0b; }
.event-item.medium { border-left-color: #eab308; }
.event-item.low { border-left-color: #10b981; }

.event-time {
  font-size: 11px;
  color: #64748b;
  font-family: monospace;
  min-width: 60px;
}

.event-icon {
  color: #3b82f6;
}

.event-content {
  flex: 1;
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.event-detail {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.event-source {
  font-size: 11px;
  color: #94a3b8;
}

.event-actions {
  display: flex;
  gap: 8px;
}

/* Analytics Row */
.analytics-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.trends-card,
.distribution-card {
  border-radius: 12px;
}

.trends-chart,
.distribution-chart {
  height: 320px;
  width: 100%;
}

/* Sources Row */
.sources-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.sources-card,
.assets-card {
  border-radius: 12px;
}

/* Alerts Panel */
.alerts-panel {
  margin-bottom: 24px;
  border-radius: 12px;
}

.alerts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.alert-card {
  padding: 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
}

.alert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.alert-card.critical { border-left: 4px solid #ef4444; }
.alert-card.high { border-left: 4px solid #f59e0b; }
.alert-card.medium { border-left: 4px solid #eab308; }

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.alert-time {
  font-size: 11px;
  color: #94a3b8;
}

.alert-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.alert-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.4;
}

.alert-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-footer span {
  font-size: 11px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Rules Section */
.rules-section {
  margin-bottom: 24px;
}

.rules-card {
  border-radius: 12px;
}

.rules-summary {
  display: flex;
  gap: 32px;
  padding: 8px;
}

.rule-stat {
  text-align: center;
  flex: 1;
}

.rule-stat .stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #3b82f6;
}

.rule-stat .stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .monitoring-row,
  .analytics-row,
  .sources-row {
    grid-template-columns: 1fr;
  }

  .alerts-grid {
    grid-template-columns: 1fr;
  }

  .rules-summary {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .status-metrics {
    justify-content: center;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .event-item {
    flex-direction: column;
  }

  .event-time {
    min-width: auto;
  }
}
</style>