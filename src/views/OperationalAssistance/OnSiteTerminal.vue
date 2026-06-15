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
          <span class="loading-title">Loading On-Site Terminal</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IBMS Field Operations & On-Site Management System</div>
      </div>
    </div>
  </div>

  <!-- Main Content - Kiosk/Terminal Optimized -->
  <div v-else class="terminal-container">
    <!-- Header - Large for Touch -->
    <div class="terminal-header">
      <div class="header-left">
        <div class="logo">
          <el-icon :size="32"><Cpu /></el-icon>
          <span>IBMS On-Site Terminal</span>
        </div>
        <div class="location-info">
          <el-icon><Location /></el-icon>
          <span>{{ currentLocation }}</span>
        </div>
      </div>
      <div class="header-right">
        <div class="time-display">
          <div class="time-large">{{ currentTime }}</div>
          <div class="date-small">{{ currentDate }}</div>
        </div>
        <el-avatar :size="48" :icon="UserFilled" class="user-avatar" />
        <div class="user-info-terminal">
          <div class="user-name">{{ operatorName }}</div>
          <div class="user-role">{{ operatorRole }}</div>
        </div>
      </div>
    </div>

    <!-- Main Terminal Grid - Large Touch-Friendly Cards -->
    <div class="terminal-grid">
      <!-- Quick Access Panel -->
      <el-card class="quick-access-card" shadow="hover" body-style="{ padding: '20px' }">
        <template #header>
          <div class="card-header">
            <span><el-icon><Grid /></el-icon> Quick Access</span>
            <el-button text type="primary" @click="customizeQuickAccess">Customize</el-button>
          </div>
        </template>
        <div class="quick-access-grid">
          <div v-for="action in quickActions" :key="action.id" class="quick-action-tile" @click="executeQuickAction(action)">
            <div class="tile-icon" :style="{ backgroundColor: action.color }">
              <el-icon :size="32"><component :is="action.icon" /></el-icon>
            </div>
            <span class="tile-label">{{ action.label }}</span>
          </div>
        </div>
      </el-card>

      <!-- Site Overview Dashboard -->
      <el-card class="dashboard-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><DataBoard /></el-icon> Site Overview</span>
            <div class="site-controls">
              <el-select v-model="selectedZone" size="large" placeholder="Select Zone" style="width: 180px">
                <el-option label="Entire Facility" value="all" />
                <el-option label="Data Hall A" value="hall_a" />
                <el-option label="Data Hall B" value="hall_b" />
                <el-option label="Mechanical Room" value="mech" />
                <el-option label="Office Area" value="office" />
              </el-select>
              <el-button type="primary" size="large" @click="refreshDashboard">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
            </div>
          </div>
        </template>
        <div class="dashboard-stats">
          <div class="stat-tile">
            <div class="stat-number-large">{{ dashboardStats.devicesTotal }}</div>
            <div class="stat-label">Total Devices</div>
            <div class="stat-sub">Online: {{ dashboardStats.devicesOnline }}</div>
          </div>
          <div class="stat-tile">
            <div class="stat-number-large" :class="{ 'critical': dashboardStats.criticalAlarms > 0 }">{{ dashboardStats.criticalAlarms }}</div>
            <div class="stat-label">Critical Alarms</div>
            <div class="stat-sub">Active: {{ dashboardStats.activeAlarms }}</div>
          </div>
          <div class="stat-tile">
            <div class="stat-number-large">{{ dashboardStats.activeWorkOrders }}</div>
            <div class="stat-label">Work Orders</div>
            <div class="stat-sub">High Priority: {{ dashboardStats.highPriorityWO }}</div>
          </div>
          <div class="stat-tile">
            <div class="stat-number-large">{{ dashboardStats.energyUsage }}kW</div>
            <div class="stat-label">Current Power</div>
            <div class="stat-sub">Today: {{ dashboardStats.energyToday }} kWh</div>
          </div>
        </div>
      </el-card>

      <!-- Real-Time Monitoring -->
      <div class="monitoring-section">
        <el-card class="monitoring-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><TrendCharts /></el-icon> Real-Time Monitoring</span>
              <div class="metric-switch">
                <el-radio-group v-model="selectedMetric" size="large">
                  <el-radio-button label="temperature">Temperature</el-radio-button>
                  <el-radio-button label="humidity">Humidity</el-radio-button>
                  <el-radio-button label="power">Power Load</el-radio-button>
                </el-radio-group>
              </div>
            </div>
          </template>
          <div ref="monitoringChartRef" class="monitoring-chart"></div>
        </el-card>

        <!-- Critical Systems Status -->
        <el-card class="systems-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Cpu /></el-icon> Critical Systems</span>
              <el-button text type="primary" @click="viewAllSystems">View All</el-button>
            </div>
          </template>
          <div class="systems-grid">
            <div v-for="system in criticalSystems" :key="system.name" class="system-tile" @click="viewSystem(system)">
              <div class="system-icon" :class="system.status">
                <el-icon :size="28"><component :is="system.icon" /></el-icon>
              </div>
              <div class="system-info">
                <div class="system-name">{{ system.name }}</div>
                <div class="system-status">
                  <el-tag :type="system.status === 'online' ? 'success' : system.status === 'warning' ? 'warning' : 'danger'" size="large">
                    {{ system.status }}
                  </el-tag>
                </div>
              </div>
              <div class="system-value">{{ system.value }}</div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Active Alarms - Large Touch List -->
      <el-card class="alarms-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><BellFilled /></el-icon> Active Alarms</span>
            <div class="alarm-filters">
              <el-select v-model="alarmFilter" size="large" placeholder="Filter" style="width: 140px">
                <el-option label="All Alarms" value="all" />
                <el-option label="Critical" value="critical" />
                <el-option label="Major" value="major" />
                <el-option label="Warning" value="warning" />
              </el-select>
              <el-button type="danger" size="large" plain @click="acknowledgeAllAlarms">
                Acknowledge All
              </el-button>
            </div>
          </div>
        </template>
        <div class="alarms-list">
          <div v-for="alarm in filteredAlarms" :key="alarm.id" :class="['alarm-row', alarm.severity]" @click="viewAlarmDetails(alarm)">
            <div class="alarm-indicator" :class="alarm.severity"></div>
            <div class="alarm-icon">
              <el-icon><WarningFilled /></el-icon>
            </div>
            <div class="alarm-content">
              <div class="alarm-title">{{ alarm.title }}</div>
              <div class="alarm-location">
                <el-icon><Location /></el-icon> {{ alarm.location }}
              </div>
            </div>
            <div class="alarm-time">{{ alarm.time }}</div>
            <el-button size="large" type="primary" plain @click.stop="acknowledgeAlarm(alarm)">
              Acknowledge
            </el-button>
          </div>
          <div v-if="filteredAlarms.length === 0" class="no-alarms">
            <el-empty description="No active alarms" :image-size="80" />
          </div>
        </div>
      </el-card>

      <!-- Work Orders & Tasks -->
      <div class="tasks-section">
        <el-card class="workorders-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> Assigned Tasks</span>
              <el-button type="primary" size="large" @click="createNewWorkOrder">
                <el-icon><Plus /></el-icon> New Task
              </el-button>
            </div>
          </template>
          <div class="workorders-list">
            <div v-for="task in assignedTasks" :key="task.id" class="task-item" @click="viewTaskDetails(task)">
              <div class="task-priority" :class="task.priority">
                <span>{{ task.priority }}</span>
              </div>
              <div class="task-info">
                <div class="task-title">{{ task.title }}</div>
                <div class="task-location">{{ task.location }}</div>
              </div>
              <div class="task-progress">
                <el-progress :percentage="task.progress" :stroke-width="8" :show-text="false" />
                <span class="progress-text">{{ task.progress }}%</span>
              </div>
              <el-button size="large" type="success" plain @click.stop="updateTaskProgress(task)">
                Update
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- Nearby Equipment -->
        <el-card class="equipment-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Monitor /></el-icon> Nearby Equipment</span>
              <el-input
                  v-model="equipmentSearch"
                  placeholder="Search equipment..."
                  size="large"
                  style="width: 200px"
                  clearable
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </div>
          </template>
          <div class="equipment-list">
            <div v-for="eq in filteredEquipment" :key="eq.id" class="equipment-row" @click="viewEquipment(eq)">
              <div class="eq-icon" :class="eq.status">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="eq-info">
                <div class="eq-name">{{ eq.name }}</div>
                <div class="eq-location">{{ eq.location }}</div>
              </div>
              <div class="eq-status">
                <el-tag :type="eq.status === 'online' ? 'success' : eq.status === 'warning' ? 'warning' : 'danger'" size="large">
                  {{ eq.status }}
                </el-tag>
              </div>
              <el-button size="large" type="info" plain @click.stop="viewEquipmentDetails(eq)">
                Details
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Emergency & Quick Actions Footer -->
      <div class="footer-actions">
        <div class="emergency-button" @click="emergencyProtocol">
          <el-icon><WarningFilled /></el-icon>
          <span>EMERGENCY PROTOCOL</span>
        </div>
        <div class="action-buttons">
          <div class="footer-action" @click="callSecurity">
            <el-icon><Lock /></el-icon>
            <span>Security</span>
          </div>
          <div class="footer-action" @click="callMaintenance">
            <el-icon><Tools /></el-icon>
            <span>Maintenance</span>
          </div>
          <div class="footer-action" @click="callHelpDesk">
            <el-icon><Headset /></el-icon>
            <span>Help Desk</span>
          </div>
          <div class="footer-action" @click="openManual">
            <el-icon><Reading /></el-icon>
            <span>Manual</span>
          </div>
          <div class="footer-action" @click="scanQRCode">
            <el-icon><Camera /></el-icon>
            <span>Scan QR</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Cpu, Location, UserFilled, Grid, DataBoard, Refresh, TrendCharts, BellFilled,
  WarningFilled, Document, Plus, Monitor, Search, Lock, Tools, Headset, Reading,
  Camera, Setting, VideoCamera, Sunny, Guide, ScaleToOriginal
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing On-Site Terminal...')

const loadingMessages = [
  'Initializing On-Site Terminal...',
  'Connecting to facility systems...',
  'Loading site data...',
  'Terminal ready for operation!'
]

// Terminal info
const currentTime = ref('')
const currentDate = ref('')
const operatorName = ref('John Anderson')
const operatorRole = ref('Facility Operator')
const currentLocation = ref('Data Center A - Main Control Room')
let timeInterval: number

// Quick actions
const quickActions = ref([
  { id: 1, label: 'View Alarms', icon: 'BellFilled', color: '#ef4444', action: 'viewAlarms' },
  { id: 2, label: 'Work Orders', icon: 'Document', color: '#3b82f6', action: 'viewWorkOrders' },
  { id: 3, label: 'Equipment', icon: 'Monitor', color: '#10b981', action: 'viewEquipment' },
  { id: 4, label: 'Emergency', icon: 'WarningFilled', color: '#f59e0b', action: 'emergency' },
  { id: 5, label: 'Scan QR', icon: 'Camera', color: '#8b5cf6', action: 'scanQR' },
  { id: 6, label: 'Reports', icon: 'DataAnalysis', color: '#ec489a', action: 'reports' },
  { id: 7, label: 'Maintenance', icon: 'Tools', color: '#06b6d4', action: 'maintenance' },
  { id: 8, label: 'Help', icon: 'Headset', color: '#84cc16', action: 'help' }
])

// Dashboard
const selectedZone = ref('all')
const dashboardStats = ref({
  devicesTotal: 342,
  devicesOnline: 318,
  criticalAlarms: 3,
  activeAlarms: 12,
  activeWorkOrders: 18,
  highPriorityWO: 5,
  energyUsage: 245,
  energyToday: 1850
})

// Monitoring
const selectedMetric = ref('temperature')
let monitoringChart: echarts.ECharts | null = null
let monitoringInterval: number

// Critical systems
const criticalSystems = ref([
  { name: 'HVAC System', icon: 'Sunny', status: 'online', value: '22.5°C' },
  { name: 'Power Supply', icon: 'ScaleToOriginal', status: 'online', value: '480V' },
  { name: 'UPS System', icon: 'Setting', status: 'warning', value: '78% Load' },
  { name: 'Fire Safety', icon: 'Guide', status: 'online', value: 'Normal' },
  { name: 'Security', icon: 'Lock', status: 'online', value: 'All Clear' },
  { name: 'Cooling', icon: 'Guide', status: 'online', value: '65% Capacity' }
])

// Alarms
const alarmFilter = ref('all')
const activeAlarms = ref([
  { id: 1, severity: 'critical', title: 'High Temperature in Data Hall A', location: 'Data Hall A - Row 3', time: '08:45 AM' },
  { id: 2, severity: 'critical', title: 'UPS Battery Failure Imminent', location: 'UPS Room', time: '09:15 AM' },
  { id: 3, severity: 'major', title: 'Chiller #2 Pressure High', location: 'Chiller Plant', time: '09:30 AM' },
  { id: 4, severity: 'major', title: 'Network Communication Lost', location: 'Switch Room B', time: '09:45 AM' },
  { id: 5, severity: 'warning', title: 'Filter Maintenance Due', location: 'AHU-101', time: '10:00 AM' },
  { id: 6, severity: 'warning', title: 'High Humidity Detected', location: 'Server Room', time: '10:15 AM' }
])

const filteredAlarms = computed(() => {
  if (alarmFilter.value === 'all') return activeAlarms.value
  return activeAlarms.value.filter(a => a.severity === alarmFilter.value)
})

// Tasks
const assignedTasks = ref([
  { id: 101, title: 'Chiller #2 Inspection', location: 'Chiller Plant Room', priority: 'high', progress: 45 },
  { id: 102, title: 'AHU Filter Replacement', location: 'Floor 3 AHU Room', priority: 'medium', progress: 0 },
  { id: 103, title: 'UPS Battery Check', location: 'UPS Room', priority: 'high', progress: 80 },
  { id: 104, title: 'Temperature Sensor Calibration', location: 'Data Hall A', priority: 'low', progress: 30 },
  { id: 105, title: 'Fire Alarm Test', location: 'All Floors', priority: 'medium', progress: 100 }
])

// Equipment
const equipmentSearch = ref('')
const nearbyEquipment = ref([
  { id: 201, name: 'Chiller #1', location: 'Chiller Plant - Zone A', status: 'online' },
  { id: 202, name: 'AHU-101', location: 'Floor 1 AHU Room', status: 'online' },
  { id: 203, name: 'UPS #2', location: 'UPS Room - Rack 3', status: 'warning' },
  { id: 204, name: 'Cooling Tower CT-1', location: 'Rooftop - North', status: 'online' },
  { id: 205, name: 'Fire Panel FP-1', location: 'Security Center', status: 'online' },
  { id: 206, name: 'BACnet Router', location: 'Server Room', status: 'offline' },
  { id: 207, name: 'VFD-202', location: 'HVAC Plant', status: 'warning' },
  { id: 208, name: 'Lighting Controller', location: 'Office Area', status: 'online' }
])

const filteredEquipment = computed(() => {
  if (!equipmentSearch.value) return nearbyEquipment.value
  return nearbyEquipment.value.filter(e =>
      e.name.toLowerCase().includes(equipmentSearch.value.toLowerCase()) ||
      e.location.toLowerCase().includes(equipmentSearch.value.toLowerCase())
  )
})

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  currentDate.value = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
}

// Initialize monitoring chart
const initMonitoringChart = () => {
  const chartDom = document.querySelector('.monitoring-chart') as HTMLElement
  if (!chartDom) return
  monitoringChart = echarts.init(chartDom)
  updateMonitoringChart()
}

const updateMonitoringChart = () => {
  if (!monitoringChart) return

  const data = generateMetricData()
  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '5%', right: '5%', top: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'category', data: data.times, axisLabel: { rotate: 0, fontSize: 12 } },
    yAxis: { type: 'value', name: getMetricUnit(), nameTextStyle: { fontSize: 12 } },
    series: [{
      name: selectedMetric.value,
      type: 'line',
      smooth: true,
      data: data.values,
      lineStyle: { width: 3, color: '#3b82f6' },
      areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#3b82f6' }, { offset: 1, color: '#93c5fd' }
        ]) },
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: { color: '#3b82f6', borderColor: '#fff', borderWidth: 2 }
    }]
  }
  monitoringChart.setOption(option)
}

const generateMetricData = () => {
  const times = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
  let values: number[] = []

  if (selectedMetric.value === 'temperature') {
    values = [22.5, 22.8, 23.0, 23.2, 23.5, 24.0, 24.2, 24.5, 24.3, 23.8, 23.2, 22.8]
  } else if (selectedMetric.value === 'humidity') {
    values = [55, 54, 53, 52, 51, 50, 49, 48, 49, 50, 52, 54]
  } else {
    values = [120, 118, 125, 135, 145, 142, 138, 140, 145, 150, 148, 135]
  }

  return { times, values }
}

const getMetricUnit = () => {
  switch (selectedMetric.value) {
    case 'temperature': return 'Temperature (°C)'
    case 'humidity': return 'Humidity (%)'
    case 'power': return 'Power (kW)'
    default: return ''
  }
}

const simulateDataUpdate = () => {
  if (!monitoringChart) return
  const data = generateMetricData()
  monitoringChart.setOption({ series: [{ data: data.values }] })
}

// Event handlers - Quick Actions
const executeQuickAction = (action: any) => {
  ElMessage.info(`Opening: ${action.label}`)
}

const customizeQuickAccess = () => {
  ElMessage.info('Customize quick access menu')
}

// Dashboard
const refreshDashboard = () => {
  ElMessage.info('Refreshing dashboard data...')
  dashboardStats.value = {
    devicesTotal: Math.floor(Math.random() * 100) + 300,
    devicesOnline: Math.floor(Math.random() * 80) + 250,
    criticalAlarms: Math.floor(Math.random() * 5),
    activeAlarms: Math.floor(Math.random() * 15) + 5,
    activeWorkOrders: Math.floor(Math.random() * 20) + 10,
    highPriorityWO: Math.floor(Math.random() * 8),
    energyUsage: Math.floor(Math.random() * 100) + 200,
    energyToday: Math.floor(Math.random() * 500) + 1500
  }
}

// Systems
const viewAllSystems = () => {
  ElMessage.info('Viewing all critical systems')
}

const viewSystem = (system: any) => {
  ElMessage.info(`Viewing system: ${system.name}`)
}

// Alarms
const viewAlarmDetails = (alarm: any) => {
  ElMessageBox.alert(
      `Alarm: ${alarm.title}\nLocation: ${alarm.location}\nTime: ${alarm.time}\nSeverity: ${alarm.severity.toUpperCase()}\n\nRecommended Action: Investigate immediately. Check system logs for additional details.`,
      'Alarm Details',
      { confirmButtonText: 'OK', type: 'warning' }
  )
}

const acknowledgeAlarm = (alarm: any) => {
  activeAlarms.value = activeAlarms.value.filter(a => a.id !== alarm.id)
  ElMessage.success(`Alarm acknowledged: ${alarm.title}`)
}

const acknowledgeAllAlarms = () => {
  ElMessageBox.confirm('Acknowledge all active alarms?', 'Confirm', {
    confirmButtonText: 'Yes',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    activeAlarms.value = []
    ElMessage.success('All alarms acknowledged')
  }).catch(() => {})
}

// Work Orders
const createNewWorkOrder = () => {
  ElMessage.info('Create new work order form')
}

const viewTaskDetails = (task: any) => {
  ElMessage.info(`Viewing task: ${task.title}`)
}

const updateTaskProgress = (task: any) => {
  ElMessageBox.prompt('Update progress percentage (0-100)', 'Update Task', {
    confirmButtonText: 'Update',
    cancelButtonText: 'Cancel',
    inputValue: String(task.progress),
    inputPattern: /^([0-9]|[1-9][0-9]|100)$/,
    inputErrorMessage: 'Please enter a number between 0 and 100'
  }).then(({ value }) => {
    task.progress = parseInt(value)
    ElMessage.success(`Task progress updated to ${value}%`)
  }).catch(() => {})
}

// Equipment
const viewEquipment = (eq: any) => {
  ElMessage.info(`Viewing equipment: ${eq.name}`)
}

const viewEquipmentDetails = (eq: any) => {
  ElMessageBox.alert(
      `Equipment: ${eq.name}\nLocation: ${eq.location}\nStatus: ${eq.status}\nLast Maintenance: 2024-01-15\nFirmware: v2.1.0\nManufacturer: Siemens\nModel: XYZ-123`,
      'Equipment Details',
      { confirmButtonText: 'OK', type: 'info' }
  )
}

// Footer actions
const emergencyProtocol = () => {
  ElMessageBox.confirm('ACTIVATE EMERGENCY PROTOCOL? This will alert all security personnel and activate emergency systems.', 'EMERGENCY', {
    confirmButtonText: 'ACTIVATE',
    cancelButtonText: 'Cancel',
    type: 'error',
    confirmButtonClass: 'emergency-confirm'
  }).then(() => {
    ElMessage.error('EMERGENCY PROTOCOL ACTIVATED - Security has been notified')
  }).catch(() => {})
}

const callSecurity = () => {
  ElMessage.info('Connecting to Security Control Center...')
}

const callMaintenance = () => {
  ElMessage.info('Connecting to Maintenance Department...')
}

const callHelpDesk = () => {
  ElMessage.info('Connecting to Help Desk...')
}

const openManual = () => {
  ElMessage.info('Opening operator manual...')
}

const scanQRCode = () => {
  ElMessage.info('QR Code scanner activated - Point camera at QR code')
}

// Lifecycle
onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

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
        initMonitoringChart()
        monitoringInterval = setInterval(simulateDataUpdate, 5000)
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (monitoringInterval) clearInterval(monitoringInterval)
  if (monitoringChart) monitoringChart.dispose()
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

/* ==================== Terminal Styles ==================== */
.terminal-container {
  min-height: 100vh;
  background: #0f172a;
  color: #e2e8f0;
}

/* Header */
.terminal-header {
  background: #1e293b;
  padding: 20px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #334155;
}

.header-left {
  display: flex;
  gap: 32px;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.logo span {
  color: #e2e8f0;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #334155;
  border-radius: 12px;
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.time-display {
  text-align: right;
}

.time-large {
  font-size: 28px;
  font-weight: 600;
  font-family: monospace;
}

.date-small {
  font-size: 12px;
  color: #94a3b8;
}

.user-avatar {
  background: #3b82f6;
}

.user-info-terminal {
  text-align: left;
}

.user-name {
  font-size: 16px;
  font-weight: 600;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
}

/* Main Grid */
.terminal-grid {
  padding: 24px;
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

/* Quick Access Card */
.quick-access-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 16px;
  padding: 8px;
}

.quick-action-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px 12px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s;
  background: #0f172a;
}

.quick-action-tile:hover {
  transform: translateY(-4px);
  background: #334155;
}

.tile-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.tile-label {
  font-size: 12px;
  font-weight: 500;
  color: #cbd5e1;
}

/* Dashboard Card */
.dashboard-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #e2e8f0;
  font-weight: 600;
}

.site-controls {
  display: flex;
  gap: 12px;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 8px;
}

.stat-tile {
  text-align: center;
  padding: 20px;
  background: #0f172a;
  border-radius: 16px;
}

.stat-number-large {
  font-size: 42px;
  font-weight: 700;
  color: #3b82f6;
}

.stat-number-large.critical {
  color: #ef4444;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 8px;
}

.stat-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Monitoring Section */
.monitoring-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.monitoring-card,
.systems-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
}

.metric-switch {
  background: #0f172a;
  border-radius: 8px;
  padding: 4px;
}

.monitoring-chart {
  height: 300px;
  width: 100%;
}

.systems-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.system-tile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #0f172a;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.system-tile:hover {
  background: #334155;
}

.system-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.system-icon.online {
  background: #10b98120;
  color: #10b981;
}

.system-icon.warning {
  background: #f59e0b20;
  color: #f59e0b;
}

.system-icon.offline {
  background: #ef444420;
  color: #ef4444;
}

.system-info {
  flex: 1;
}

.system-name {
  font-size: 14px;
  font-weight: 500;
  color: #e2e8f0;
}

.system-value {
  font-size: 18px;
  font-weight: 600;
  color: #3b82f6;
}

/* Alarms Card */
.alarms-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
}

.alarm-filters {
  display: flex;
  gap: 12px;
}

.alarms-list {
  max-height: 400px;
  overflow-y: auto;
}

.alarm-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #334155;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.alarm-row:hover {
  background: #334155;
}

.alarm-row.critical {
  border-left: 4px solid #ef4444;
}

.alarm-row.major {
  border-left: 4px solid #f59e0b;
}

.alarm-row.warning {
  border-left: 4px solid #eab308;
}

.alarm-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  position: absolute;
  left: 0;
}

.alarm-indicator.critical { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
.alarm-indicator.major { background: #f59e0b; }
.alarm-indicator.warning { background: #eab308; }

.alarm-icon {
  color: #ef4444;
  font-size: 24px;
}

.alarm-content {
  flex: 1;
}

.alarm-title {
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.alarm-location {
  font-size: 12px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 4px;
}

.alarm-time {
  font-size: 12px;
  color: #64748b;
  font-family: monospace;
}

.no-alarms {
  padding: 40px;
  text-align: center;
}

/* Tasks Section */
.tasks-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.workorders-card,
.equipment-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
}

.workorders-list,
.equipment-list {
  max-height: 400px;
  overflow-y: auto;
}

.task-item,
.equipment-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #334155;
  cursor: pointer;
  transition: background 0.2s;
}

.task-item:hover,
.equipment-row:hover {
  background: #334155;
}

.task-priority {
  width: 48px;
  padding: 4px 8px;
  border-radius: 8px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.task-priority.high {
  background: #ef444420;
  color: #ef4444;
}

.task-priority.medium {
  background: #f59e0b20;
  color: #f59e0b;
}

.task-priority.low {
  background: #10b98120;
  color: #10b981;
}

.task-info,
.eq-info {
  flex: 1;
}

.task-title,
.eq-name {
  font-size: 15px;
  font-weight: 500;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.task-location,
.eq-location {
  font-size: 12px;
  color: #94a3b8;
}

.task-progress {
  width: 100px;
  text-align: center;
}

.progress-text {
  font-size: 11px;
  color: #3b82f6;
  margin-top: 4px;
  display: block;
}

.eq-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.eq-icon.online {
  background: #10b98120;
  color: #10b981;
}

.eq-icon.warning {
  background: #f59e0b20;
  color: #f59e0b;
}

.eq-icon.offline {
  background: #ef444420;
  color: #ef4444;
}

/* Footer Actions */
.footer-actions {
  display: flex;
  gap: 20px;
  margin-top: 8px;
}

.emergency-button {
  flex: 1;
  background: #dc2626;
  padding: 20px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.emergency-button:hover {
  background: #b91c1c;
  transform: scale(1.02);
}

.action-buttons {
  flex: 2;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
}

.footer-action {
  background: #334155;
  padding: 20px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.footer-action:hover {
  background: #475569;
  transform: translateY(-2px);
}

.footer-action .el-icon {
  font-size: 28px;
}

.footer-action span {
  font-size: 12px;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 1200px) {
  .quick-access-grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .monitoring-section {
    grid-template-columns: 1fr;
  }

  .tasks-section {
    grid-template-columns: 1fr;
  }

  .dashboard-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .footer-actions {
    flex-direction: column;
  }

  .action-buttons {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (max-width: 768px) {
  .terminal-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-left {
    flex-direction: column;
    width: 100%;
  }

  .logo {
    width: 100%;
    justify-content: center;
  }

  .header-right {
    width: 100%;
    justify-content: space-between;
  }

  .quick-access-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .dashboard-stats {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>