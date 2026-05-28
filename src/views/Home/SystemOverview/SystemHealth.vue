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
        <div class="loading-tip">Not Developed Yet</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- System Health Page Content -->
  <div v-else class="system-health-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h1>System Health</h1>
        <p class="subtitle">Real-time monitoring of overall system health status and performance metrics</p>
      </div>
      <div class="header-actions">
        <el-button :icon="Refresh" @click="refreshData">Refresh</el-button>
        <el-button type="primary" :icon="Download" @click="exportReport">Export Report</el-button>
      </div>
    </div>

    <!-- Overall Health Score Card -->
    <div class="overall-health-card">
      <div class="health-score-container">
        <div class="health-score">
          <el-progress
              type="circle"
              :percentage="healthScore"
              :color="getHealthColor(healthScore)"
              :width="140"
              :stroke-width="12"
          >
            <template #default>
              <div class="score-text">
                <span class="score-value">{{ healthScore }}%</span>
                <span class="score-label">Overall Health</span>
              </div>
            </template>
          </el-progress>
        </div>
        <div class="health-summary">
          <div class="summary-item">
            <div class="summary-status good">
              <el-icon><CircleCheckFilled /></el-icon>
              <span>Healthy Systems</span>
              <strong>{{ healthyCount }}</strong>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-status warning">
              <el-icon><WarningFilled /></el-icon>
              <span>Warning Systems</span>
              <strong>{{ warningCount }}</strong>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-status critical">
              <el-icon><CircleCloseFilled /></el-icon>
              <span>Critical Systems</span>
              <strong>{{ criticalCount }}</strong>
            </div>
          </div>
          <div class="summary-item">
            <div class="summary-status offline">
              <el-icon><Link /></el-icon>
              <span>Offline Systems</span>
              <strong>{{ offlineCount }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- System Categories Tabs -->
    <div class="system-tabs">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Systems" name="all" />
        <el-tab-pane label="HVAC Systems" name="hvac" />
        <el-tab-pane label="Electrical Systems" name="electrical" />
        <el-tab-pane label="Lighting Systems" name="lighting" />
        <el-tab-pane label="Plumbing Systems" name="plumbing" />
        <el-tab-pane label="Security Systems" name="security" />
        <el-tab-pane label="Data Center" name="datacenter" />
      </el-tabs>
    </div>

    <!-- Systems Grid -->
    <div class="systems-grid" v-loading="gridLoading">
      <div v-for="system in filteredSystems" :key="system.id" class="system-card" :class="getStatusClass(system.status)">
        <div class="card-header">
          <div class="system-icon" :class="getStatusClass(system.status)">
            <el-icon :size="28"><component :is="system.icon" /></el-icon>
          </div>
          <div class="system-info">
            <h3>{{ system.name }}</h3>
            <span class="system-location">{{ system.location }}</span>
          </div>
          <el-dropdown @command="(cmd: string) => handleAction(cmd, system)">
            <el-button link :icon="MoreFilled" class="more-btn" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="details">View Details</el-dropdown-item>
                <el-dropdown-item command="history">View History</el-dropdown-item>
                <el-dropdown-item command="alert" divided>Configure Alert</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <div class="card-body">
          <div class="health-status">
            <span class="status-label">Health Status</span>
            <el-tag :type="getStatusTagType(system.status)" size="large" effect="dark">
              {{ getStatusLabel(system.status) }}
            </el-tag>
          </div>

          <div class="health-metrics">
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">System Uptime</span>
                <span class="metric-value">{{ system.uptime }}</span>
              </div>
              <el-progress :percentage="system.uptimePercent" :color="getHealthColor(system.uptimePercent)" :stroke-width="6" :show-text="false" />
            </div>
            <div class="metric-item">
              <div class="metric-header">
                <span class="metric-label">Performance</span>
                <span class="metric-value">{{ system.performance }}%</span>
              </div>
              <el-progress :percentage="system.performance" :color="getHealthColor(system.performance)" :stroke-width="6" :show-text="false" />
            </div>
          </div>

          <div class="alert-summary" v-if="system.activeAlerts > 0">
            <el-icon><Warning /></el-icon>
            <span>{{ system.activeAlerts }} active {{ system.activeAlerts === 1 ? 'alert' : 'alerts' }}</span>
          </div>
          <div class="alert-summary healthy" v-else>
            <el-icon><CircleCheck /></el-icon>
            <span>No active alerts</span>
          </div>
        </div>

        <div class="card-footer">
          <el-button size="small" :icon="Monitor" @click="viewSystemDetails(system)">Monitor</el-button>
          <el-button size="small" :icon="DataLine" @click="viewMetrics(system)">Metrics</el-button>
        </div>
      </div>
    </div>

    <!-- Real-time Alerts Section -->
    <div class="alerts-section">
      <div class="section-header">
        <h2>
          <el-icon><BellFilled /></el-icon>
          Recent Alerts
        </h2>
        <el-button link type="primary" @click="viewAllAlerts">View All Alerts →</el-button>
      </div>
      <div class="alerts-list">
        <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
          <div class="alert-icon">
            <el-icon v-if="alert.severity === 'critical'"><CircleCloseFilled /></el-icon>
            <el-icon v-else-if="alert.severity === 'warning'"><WarningFilled /></el-icon>
            <el-icon v-else><InfoFilled /></el-icon>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-desc">{{ alert.description }}</div>
            <div class="alert-time">{{ formatRelativeTime(alert.timestamp) }}</div>
          </div>
          <div class="alert-actions">
            <el-button size="small" type="primary" link @click="acknowledgeAlert(alert)">Acknowledge</el-button>
          </div>
        </div>
        <div v-if="recentAlerts.length === 0" class="no-alerts">
          <el-empty description="No recent alerts" :image-size="80" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh,
  Download,
  MoreFilled,
  Monitor,
  DataLine,
  BellFilled,
  Warning,
  CircleCheck,
  CircleCheckFilled,
  WarningFilled,
  CircleCloseFilled,
  InfoFilled,
  Link
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const gridLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface SystemHealth {
  id: string
  name: string
  location: string
  category: string
  status: 'healthy' | 'warning' | 'critical' | 'offline'
  uptime: string
  uptimePercent: number
  performance: number
  activeAlerts: number
  icon: any
  lastCheck: string
}

interface Alert {
  id: string
  title: string
  description: string
  severity: 'critical' | 'warning' | 'info'
  timestamp: string
  systemId: string
}

// ==================== Mock Data ====================
const systems = ref<SystemHealth[]>([
  {
    id: 'hvac-1',
    name: 'Chiller Plant System',
    location: 'Building A, Basement',
    category: 'hvac',
    status: 'healthy',
    uptime: '99.95%',
    uptimePercent: 99.95,
    performance: 98.5,
    activeAlerts: 0,
    icon: 'Cpu',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'hvac-2',
    name: 'AHU System',
    location: 'Building B, Floor 3',
    category: 'hvac',
    status: 'warning',
    uptime: '98.20%',
    uptimePercent: 98.2,
    performance: 87.3,
    activeAlerts: 2,
    icon: 'Cpu',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'electrical-1',
    name: 'Main Power Distribution',
    location: 'Building A, Electrical Room',
    category: 'electrical',
    status: 'healthy',
    uptime: '99.98%',
    uptimePercent: 99.98,
    performance: 99.2,
    activeAlerts: 0,
    icon: 'Lightning',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'electrical-2',
    name: 'UPS System',
    location: 'Data Center',
    category: 'electrical',
    status: 'critical',
    uptime: '95.50%',
    uptimePercent: 95.5,
    performance: 82.1,
    activeAlerts: 3,
    icon: 'Lightning',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'lighting-1',
    name: 'Smart Lighting Control',
    location: 'Building A & B',
    category: 'lighting',
    status: 'healthy',
    uptime: '99.87%',
    uptimePercent: 99.87,
    performance: 97.8,
    activeAlerts: 0,
    icon: 'Sunny',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'plumbing-1',
    name: 'Water Supply System',
    location: 'Building A, Basement',
    category: 'plumbing',
    status: 'warning',
    uptime: '97.40%',
    uptimePercent: 97.4,
    performance: 89.5,
    activeAlerts: 1,
    icon: 'Water',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'security-1',
    name: 'Access Control System',
    location: 'All Buildings',
    category: 'security',
    status: 'healthy',
    uptime: '99.92%',
    uptimePercent: 99.92,
    performance: 99.5,
    activeAlerts: 0,
    icon: 'Lock',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'security-2',
    name: 'CCTV System',
    location: 'All Buildings',
    category: 'security',
    status: 'warning',
    uptime: '98.75%',
    uptimePercent: 98.75,
    performance: 91.2,
    activeAlerts: 1,
    icon: 'Camera',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'datacenter-1',
    name: 'Server Cooling System',
    location: 'Data Center',
    category: 'datacenter',
    status: 'critical',
    uptime: '96.30%',
    uptimePercent: 96.3,
    performance: 78.4,
    activeAlerts: 2,
    icon: 'Cpu',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'datacenter-2',
    name: 'Environmental Monitoring',
    location: 'Data Center',
    category: 'datacenter',
    status: 'healthy',
    uptime: '99.98%',
    uptimePercent: 99.98,
    performance: 99.9,
    activeAlerts: 0,
    icon: 'Cloudy',
    lastCheck: new Date().toISOString()
  },
  {
    id: 'hvac-3',
    name: 'FCU Network',
    location: 'Building B, All Floors',
    category: 'hvac',
    status: 'offline',
    uptime: '82.00%',
    uptimePercent: 82,
    performance: 65.0,
    activeAlerts: 5,
    icon: 'Cpu',
    lastCheck: new Date().toISOString()
  }
])

const recentAlerts = ref<Alert[]>([
  {
    id: 'alert-1',
    title: 'UPS Battery Low',
    description: 'UPS battery capacity below 30%. Replacement recommended within 7 days.',
    severity: 'critical',
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    systemId: 'electrical-2'
  },
  {
    id: 'alert-2',
    title: 'Server Room Temperature High',
    description: 'Temperature exceeding threshold (27.5°C / 81.5°F). Check cooling system.',
    severity: 'critical',
    timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    systemId: 'datacenter-1'
  },
  {
    id: 'alert-3',
    title: 'AHU Filter Clogged',
    description: 'Pressure differential indicates filter replacement needed.',
    severity: 'warning',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    systemId: 'hvac-2'
  },
  {
    id: 'alert-4',
    title: 'Water Pressure Low',
    description: 'Water supply pressure below normal range. Inspect pumps and valves.',
    severity: 'warning',
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    systemId: 'plumbing-1'
  },
  {
    id: 'alert-5',
    title: 'CCTV Camera Offline',
    description: 'Camera 12 (North Entrance) has lost connection.',
    severity: 'info',
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    systemId: 'security-2'
  }
])

// ==================== Computed ====================
const activeTab = ref('all')

const filteredSystems = computed(() => {
  if (activeTab.value === 'all') return systems.value
  return systems.value.filter(s => s.category === activeTab.value)
})

const healthScore = computed(() => {
  const total = filteredSystems.value.length
  if (total === 0) return 100

  const healthyWeight = 100
  const warningWeight = 60
  const criticalWeight = 30
  const offlineWeight = 0

  const totalScore = filteredSystems.value.reduce((sum, system) => {
    switch (system.status) {
      case 'healthy': return sum + healthyWeight
      case 'warning': return sum + warningWeight
      case 'critical': return sum + criticalWeight
      case 'offline': return sum + offlineWeight
      default: return sum + 0
    }
  }, 0)

  return Math.round(totalScore / total)
})

const healthyCount = computed(() => systems.value.filter(s => s.status === 'healthy').length)
const warningCount = computed(() => systems.value.filter(s => s.status === 'warning').length)
const criticalCount = computed(() => systems.value.filter(s => s.status === 'critical').length)
const offlineCount = computed(() => systems.value.filter(s => s.status === 'offline').length)

// ==================== Helper Functions ====================
const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    healthy: 'Healthy',
    warning: 'Warning',
    critical: 'Critical',
    offline: 'Offline'
  }
  return map[status] || status
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    healthy: 'success',
    warning: 'warning',
    critical: 'danger',
    offline: 'info'
  }
  return map[status] || 'info'
}

const getStatusClass = (status: string) => {
  const map: Record<string, string> = {
    healthy: 'status-healthy',
    warning: 'status-warning',
    critical: 'status-critical',
    offline: 'status-offline'
  }
  return map[status] || ''
}

const getHealthColor = (percentage: number) => {
  if (percentage >= 85) return '#67c23a'
  if (percentage >= 60) return '#e6a23c'
  return '#f56c6c'
}

const formatRelativeTime = (timestamp: string) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  return date.toLocaleDateString()
}

// ==================== Actions ====================
const refreshData = async () => {
  gridLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success('System health data refreshed')
  gridLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting system health report...')
}

const handleTabChange = () => {
  // Tab changed
}

const handleAction = (command: string, system: SystemHealth) => {
  switch (command) {
    case 'details':
      ElMessage.info(`Viewing details for ${system.name}`)
      break
    case 'history':
      ElMessage.info(`Viewing history for ${system.name}`)
      break
    case 'alert':
      ElMessage.info(`Configuring alerts for ${system.name}`)
      break
  }
}

const viewSystemDetails = (system: SystemHealth) => {
  ElMessage.info(`Monitoring ${system.name}`)
}

const viewMetrics = (system: SystemHealth) => {
  ElMessage.info(`Viewing metrics for ${system.name}`)
}

const viewAllAlerts = () => {
  ElMessage.info('Viewing all alerts')
}

const acknowledgeAlert = (alert: Alert) => {
  ElMessage.success(`Alert acknowledged: ${alert.title}`)
  // Remove from list
  recentAlerts.value = recentAlerts.value.filter(a => a.id !== alert.id)
}

// ==================== Loading Animation ====================
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
.system-health-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0 0 4px 0;
}

.header-title .subtitle {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Overall Health Card */
.overall-health-card {
  background: white;
  border-radius: 16px;
  padding: 24px 32px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.health-score-container {
  display: flex;
  align-items: center;
  gap: 48px;
  flex-wrap: wrap;
}

.health-score {
  flex-shrink: 0;
}

.score-text {
  text-align: center;
}

.score-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
}

.score-label {
  font-size: 12px;
  color: #909399;
}

.health-summary {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.summary-item {
  min-width: 120px;
}

.summary-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.summary-status .el-icon {
  font-size: 20px;
}

.summary-status.good .el-icon,
.summary-status.good strong {
  color: #67c23a;
}

.summary-status.warning .el-icon,
.summary-status.warning strong {
  color: #e6a23c;
}

.summary-status.critical .el-icon,
.summary-status.critical strong {
  color: #f56c6c;
}

.summary-status.offline .el-icon,
.summary-status.offline strong {
  color: #909399;
}

.summary-status span {
  color: #606266;
  flex: 1;
}

.summary-status strong {
  font-size: 18px;
  margin-left: auto;
}

/* System Tabs */
.system-tabs {
  background: white;
  border-radius: 12px;
  padding: 0 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

:deep(.el-tabs__header) {
  margin: 0;
}

/* Systems Grid */
.systems-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.system-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border-left: 4px solid transparent;
}

.system-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.system-card.status-healthy {
  border-left-color: #67c23a;
}

.system-card.status-warning {
  border-left-color: #e6a23c;
}

.system-card.status-critical {
  border-left-color: #f56c6c;
}

.system-card.status-offline {
  border-left-color: #909399;
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.system-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.system-icon.status-healthy {
  background: #e8f8f0;
  color: #67c23a;
}

.system-icon.status-warning {
  background: #fff7e8;
  color: #e6a23c;
}

.system-icon.status-critical {
  background: #ffe8e8;
  color: #f56c6c;
}

.system-icon.status-offline {
  background: #f0f0f0;
  color: #909399;
}

.system-info {
  flex: 1;
}

.system-info h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: #1f2f3d;
}

.system-location {
  font-size: 12px;
  color: #909399;
}

.more-btn {
  color: #909399;
}

.card-body {
  margin-bottom: 16px;
}

.health-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.status-label {
  font-size: 13px;
  color: #606266;
}

.health-metrics {
  margin-bottom: 12px;
}

.metric-item {
  margin-bottom: 12px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
}

.metric-label {
  color: #909399;
}

.metric-value {
  color: #1f2f3d;
  font-weight: 500;
}

.alert-summary {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #fef0f0;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 13px;
}

.alert-summary.healthy {
  background: #e8f8f0;
  color: #67c23a;
}

.card-footer {
  display: flex;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

/* Alerts Section */
.alerts-section {
  background: white;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1f2f3d;
}

.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 16px;
  background: #fafafa;
  border-radius: 12px;
  transition: background 0.2s;
}

.alert-item:hover {
  background: #f5f7fa;
}

.alert-item.critical .alert-icon {
  color: #f56c6c;
}

.alert-item.warning .alert-icon {
  color: #e6a23c;
}

.alert-item.info .alert-icon {
  color: #409eff;
}

.alert-icon .el-icon {
  font-size: 20px;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.alert-desc {
  font-size: 13px;
  color: #606266;
  margin-bottom: 6px;
}

.alert-time {
  font-size: 11px;
  color: #c0c4cc;
}

.alert-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.alert-item:hover .alert-actions {
  opacity: 1;
}

.no-alerts {
  padding: 40px 0;
}
</style>