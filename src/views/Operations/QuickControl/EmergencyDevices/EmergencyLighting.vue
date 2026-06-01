<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, AlarmClock, Document,
  Grid, List, DataLine
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing emergency lighting system...',
  'Establishing secure connection...',
  'Synchronizing device status...',
  'Ready for operation...'
]

// System status
const systemStatus = ref({
  overallHealth: 92,
  onlineDevices: 42,
  totalDevices: 48,
  lastSystemTest: '2025-01-15 14:30:00',
  nextAutoTest: '2025-01-22 02:00:00',
  activeAlerts: 3
})

// Emergency lighting zones
const lightingZones = ref([
  {
    id: 'zone-lobby',
    name: 'Main Lobby',
    type: 'Public Area',
    status: 'healthy',
    batteryLevel: 98,
    lightCount: 8,
    onlineLights: 8,
    lastTest: '2025-01-15',
    nextTestDue: '2025-02-15',
    scheduleTest: 'Weekly',
    autoTest: true,
    dimmingMode: 'auto',
    emergencyMode: false
  },
  {
    id: 'zone-corridor-east',
    name: 'East Corridor',
    type: 'Escape Route',
    status: 'healthy',
    batteryLevel: 95,
    lightCount: 12,
    onlineLights: 12,
    lastTest: '2025-01-14',
    nextTestDue: '2025-02-14',
    scheduleTest: 'Weekly',
    autoTest: true,
    dimmingMode: 'auto',
    emergencyMode: false
  },
  {
    id: 'zone-corridor-west',
    name: 'West Corridor',
    type: 'Escape Route',
    status: 'warning',
    batteryLevel: 72,
    lightCount: 10,
    onlineLights: 9,
    lastTest: '2025-01-10',
    nextTestDue: '2025-02-10',
    scheduleTest: 'Weekly',
    autoTest: true,
    dimmingMode: 'auto',
    emergencyMode: false,
    alerts: ['Battery health below 80%', '1 light offline - maintenance required']
  },
  {
    id: 'zone-stairwell-a',
    name: 'Stairwell A',
    type: 'Emergency Exit',
    status: 'critical',
    batteryLevel: 45,
    lightCount: 6,
    onlineLights: 5,
    lastTest: '2024-12-28',
    nextTestDue: '2025-01-28',
    scheduleTest: 'Weekly',
    autoTest: false,
    dimmingMode: 'full',
    emergencyMode: false,
    alerts: ['Battery critically low - replace immediately', 'Test overdue by 18 days', '1 light offline']
  },
  {
    id: 'zone-stairwell-b',
    name: 'Stairwell B',
    type: 'Emergency Exit',
    status: 'healthy',
    batteryLevel: 92,
    lightCount: 6,
    onlineLights: 6,
    lastTest: '2025-01-12',
    nextTestDue: '2025-02-12',
    scheduleTest: 'Weekly',
    autoTest: true,
    dimmingMode: 'auto',
    emergencyMode: false
  },
  {
    id: 'zone-exits',
    name: 'Emergency Exits',
    type: 'Exit Signage',
    status: 'warning',
    batteryLevel: 78,
    lightCount: 14,
    onlineLights: 14,
    lastTest: '2025-01-08',
    nextTestDue: '2025-02-08',
    scheduleTest: 'Daily',
    autoTest: true,
    dimmingMode: 'full',
    emergencyMode: false,
    alerts: ['Battery health below 80% on 4 units']
  },
  {
    id: 'zone-server-room',
    name: 'Server Room',
    type: 'Critical Area',
    status: 'healthy',
    batteryLevel: 96,
    lightCount: 4,
    onlineLights: 4,
    lastTest: '2025-01-13',
    nextTestDue: '2025-02-13',
    scheduleTest: 'Monthly',
    autoTest: true,
    dimmingMode: 'auto',
    emergencyMode: false
  },
  {
    id: 'zone-electrical',
    name: 'Electrical Room',
    type: 'Critical Area',
    status: 'healthy',
    batteryLevel: 94,
    lightCount: 4,
    onlineLights: 4,
    lastTest: '2025-01-11',
    nextTestDue: '2025-02-11',
    scheduleTest: 'Monthly',
    autoTest: true,
    dimmingMode: 'auto',
    emergencyMode: false
  }
])

// Individual lights data
const emergencyLights = ref([
  { id: 'EML-101', name: 'Lobby North', zone: 'Main Lobby', status: 'healthy', batteryLevel: 98, lastTest: '2025-01-15', runtime: 92, lumens: 1200, model: 'LED-EMG-1000' },
  { id: 'EML-102', name: 'Lobby South', zone: 'Main Lobby', status: 'healthy', batteryLevel: 97, lastTest: '2025-01-15', runtime: 91, lumens: 1200, model: 'LED-EMG-1000' },
  { id: 'EML-103', name: 'Lobby East', zone: 'Main Lobby', status: 'healthy', batteryLevel: 99, lastTest: '2025-01-15', runtime: 93, lumens: 1200, model: 'LED-EMG-1000' },
  { id: 'EML-104', name: 'Lobby West', zone: 'Main Lobby', status: 'healthy', batteryLevel: 96, lastTest: '2025-01-15', runtime: 90, lumens: 1200, model: 'LED-EMG-1000' },
  { id: 'EML-201', name: 'East Corridor 1', zone: 'East Corridor', status: 'healthy', batteryLevel: 95, lastTest: '2025-01-14', runtime: 88, lumens: 800, model: 'LED-EMG-800' },
  { id: 'EML-202', name: 'East Corridor 2', zone: 'East Corridor', status: 'healthy', batteryLevel: 94, lastTest: '2025-01-14', runtime: 87, lumens: 800, model: 'LED-EMG-800' },
  { id: 'EML-203', name: 'East Corridor 3', zone: 'East Corridor', status: 'warning', batteryLevel: 71, lastTest: '2025-01-10', runtime: 52, lumens: 800, model: 'LED-EMG-800' },
  { id: 'EML-301', name: 'West Corridor 1', zone: 'West Corridor', status: 'warning', batteryLevel: 72, lastTest: '2025-01-10', runtime: 54, lumens: 800, model: 'LED-EMG-800' },
  { id: 'EML-302', name: 'West Corridor 2', zone: 'West Corridor', status: 'warning', batteryLevel: 70, lastTest: '2025-01-10', runtime: 51, lumens: 800, model: 'LED-EMG-800' },
  { id: 'EML-401', name: 'Stairwell A-1', zone: 'Stairwell A', status: 'critical', batteryLevel: 45, lastTest: '2024-12-28', runtime: 28, lumens: 1000, model: 'LED-EMG-1000' },
  { id: 'EML-402', name: 'Stairwell A-2', zone: 'Stairwell A', status: 'critical', batteryLevel: 44, lastTest: '2024-12-28', runtime: 27, lumens: 1000, model: 'LED-EMG-1000' },
  { id: 'EML-501', name: 'Exit Sign A', zone: 'Emergency Exits', status: 'warning', batteryLevel: 78, lastTest: '2025-01-08', runtime: 65, lumens: 200, model: 'EXIT-LED-600' },
  { id: 'EML-502', name: 'Exit Sign B', zone: 'Emergency Exits', status: 'healthy', batteryLevel: 92, lastTest: '2025-01-12', runtime: 85, lumens: 200, model: 'EXIT-LED-600' }
])

// Settings - Initialize properly
const autoTestTimeValue = ref<Date>(new Date())
autoTestTimeValue.value.setHours(2, 0, 0, 0)

const settings = ref({
  autoTestEnabled: true,
  autoTestTime: '02:00',
  testDuration: 90,
  notificationEnabled: true,
  notificationRecipients: ['operations@ibms.com', 'facility@ibms.com'],
  lowBatteryThreshold: 80,
  criticalBatteryThreshold: 60
})

// UI State
const selectedZone = ref<any>(null)
const selectedLight = ref<any>(null)
const showZoneDetail = ref(false)
const showLightDetail = ref(false)
const showSettings = ref(false)
const viewMode = ref<'zones' | 'lights'>('zones')
const searchKeyword = ref('')
const manualTestActive = ref(false)
const testProgress = ref(0)

const getStatusColor = (status: string) => {
  switch(status) {
    case 'critical': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'healthy': return '#67C23A'
    default: return '#909399'
  }
}

const getStatusText = (status: string) => {
  switch(status) {
    case 'critical': return 'Critical'
    case 'warning': return 'Warning'
    case 'healthy': return 'Healthy'
    default: return 'Unknown'
  }
}

const getBatteryColor = (level: number) => {
  if (level < 60) return '#F56C6C'
  if (level < 80) return '#E6A23C'
  return '#67C23A'
}

const filteredZones = computed(() => {
  if (!searchKeyword.value) return lightingZones.value
  return lightingZones.value.filter(z =>
      z.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      z.type.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const filteredLights = computed(() => {
  if (!searchKeyword.value) return emergencyLights.value
  return emergencyLights.value.filter(l =>
      l.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      l.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      l.zone.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// Zone Control Actions
const performZoneTest = (zone: any) => {
  ElMessageBox.confirm(
      `Initiate emergency lighting test for ${zone.name}?\n\nDuration: ${settings.value.testDuration} seconds\nThis will simulate a power failure.`,
      'Confirm Zone Test',
      {
        confirmButtonText: 'Start Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    manualTestActive.value = true
    testProgress.value = 0
    ElMessage.info(`Testing ${zone.name}...`)

    const interval = setInterval(() => {
      testProgress.value += 10
      if (testProgress.value >= 100) {
        clearInterval(interval)
        manualTestActive.value = false
        testProgress.value = 0
        ElMessage.success(`${zone.name} test completed - All lights functional`)
        zone.lastTest = new Date().toISOString().split('T')[0]
      }
    }, (settings.value.testDuration / 10) * 1000)
  }).catch(() => {})
}

const emergencyActivateZone = (zone: any) => {
  ElMessageBox.confirm(
      `EMERGENCY OVERRIDE: Activate all emergency lights in ${zone.name}?\n\nThis will force all units to illuminate at maximum brightness.`,
      'Emergency Zone Activation',
      {
        confirmButtonText: 'ACTIVATE',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    zone.emergencyMode = true
    ElMessage.success(`${zone.name} emergency lighting activated`)
    setTimeout(() => {
      zone.emergencyMode = false
      ElMessage.info(`${zone.name} emergency mode auto-reset`)
    }, 1800000)
  }).catch(() => {})
}

const toggleAutoTest = (zone: any) => {
  zone.autoTest = !zone.autoTest
  ElMessage.success(`${zone.name} auto-test ${zone.autoTest ? 'enabled' : 'disabled'}`)
}

const scheduleMaintenance = (zone: any) => {
  ElMessageBox.confirm(
      `Create maintenance work order for ${zone.name}?\n\nThis will schedule battery replacement and inspection.`,
      'Schedule Maintenance',
      {
        confirmButtonText: 'Create Work Order',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success(`Maintenance scheduled for ${zone.name} - Work Order #WO-${Date.now()}`)
  }).catch(() => {})
}

const viewZoneDetails = (zone: any) => {
  selectedZone.value = zone
  showZoneDetail.value = true
}

// Light Control Actions
const performLightTest = (light: any) => {
  ElMessageBox.confirm(
      `Test emergency light ${light.id}?\n\nThis will verify battery and lamp functionality.`,
      'Confirm Light Test',
      {
        confirmButtonText: 'Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.info(`Testing ${light.id}...`)
    setTimeout(() => {
      if (light.batteryLevel > 50) {
        ElMessage.success(`${light.id} test passed - Battery: ${light.batteryLevel}%`)
        light.lastTest = new Date().toISOString().split('T')[0]
      } else {
        ElMessage.warning(`${light.id} test warning - Battery low: ${light.batteryLevel}%`)
      }
    }, 2000)
  }).catch(() => {})
}

const viewLightDetails = (light: any) => {
  selectedLight.value = light
  showLightDetail.value = true
}

// System Actions
const emergencyActivateAll = () => {
  ElMessageBox.confirm(
      'EMERGENCY OVERRIDE: Activate ALL emergency lighting?\n\nThis is a site-wide emergency command.',
      'Global Emergency Activation',
      {
        confirmButtonText: 'ACTIVATE ALL',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    lightingZones.value.forEach(zone => { zone.emergencyMode = true })
    ElMessage.error('EMERGENCY MODE ACTIVE - All lights illuminated')
    setTimeout(() => {
      lightingZones.value.forEach(zone => { zone.emergencyMode = false })
      ElMessage.info('Emergency mode auto-reset')
    }, 1800000)
  }).catch(() => {})
}

const runSystemTest = () => {
  ElMessageBox.confirm(
      `Run full system test on ALL emergency lighting?\n\nTest Duration: ${settings.value.testDuration} seconds`,
      'Confirm System Test',
      {
        confirmButtonText: 'Start Full Test',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    manualTestActive.value = true
    testProgress.value = 0
    ElMessage.info('System-wide test initiated')

    const interval = setInterval(() => {
      testProgress.value += 5
      if (testProgress.value >= 100) {
        clearInterval(interval)
        manualTestActive.value = false
        testProgress.value = 0
        systemStatus.value.lastSystemTest = new Date().toISOString().replace('T', ' ').slice(0, 19)
        ElMessage.success('Full system test completed - 42/48 lights functional')
      }
    }, (settings.value.testDuration / 20) * 1000)
  }).catch(() => {})
}

const exportReport = () => {
  ElMessage.success('Exporting system report...')
  setTimeout(() => {
    ElMessage.success('Report exported: emergency_lighting_report_' + new Date().toISOString().split('T')[0] + '.pdf')
  }, 1500)
}

const refreshData = () => {
  ElMessage.info('Refreshing emergency lighting data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

const saveSettings = () => {
  // Format time from Date object
  const hours = autoTestTimeValue.value.getHours().toString().padStart(2, '0')
  const minutes = autoTestTimeValue.value.getMinutes().toString().padStart(2, '0')
  settings.value.autoTestTime = `${hours}:${minutes}`
  ElMessage.success('Settings saved successfully')
  showSettings.value = false
}

const openSettings = () => {
  // Reset time picker value from saved time string
  const [hours, minutes] = settings.value.autoTestTime.split(':')
  const newDate = new Date()
  newDate.setHours(parseInt(hours), parseInt(minutes), 0, 0)
  autoTestTimeValue.value = newDate
  showSettings.value = true
}

onMounted(() => {
  let progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(progressInterval)
    loadingProgress.value = 100
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2000)
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
          <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
        </div>
        <div class="loading-progress"><div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div></div>
        <div class="loading-tip">Emergency Lighting Control System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="emergency-lighting-control">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Emergency Lighting Control</h2>
        <p class="subtitle">Centralized monitoring and control of emergency lighting systems</p>
      </div>
      <div class="header-actions">
        <div class="view-toggle">
          <el-button :type="viewMode === 'zones' ? 'primary' : 'default'" @click="viewMode = 'zones'">
            <el-icon><Grid /></el-icon> Zones
          </el-button>
          <el-button :type="viewMode === 'lights' ? 'primary' : 'default'" @click="viewMode = 'lights'">
            <el-icon><List /></el-icon> Lights
          </el-button>
        </div>
        <el-button type="danger" @click="emergencyActivateAll">
          <el-icon><Warning /></el-icon> Emergency All
        </el-button>
        <el-button @click="runSystemTest" :loading="manualTestActive">
          <el-icon><Operation /></el-icon> Test All
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Document /></el-icon> Export
        </el-button>
        <el-button @click="openSettings">
          <el-icon><Setting /></el-icon> Settings
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Test Progress Bar -->
    <div v-if="manualTestActive" class="test-progress">
      <div class="progress-header">
        <span class="progress-title">System Test in Progress</span>
        <span class="progress-percent">{{ testProgress }}%</span>
      </div>
      <el-progress :percentage="testProgress" :stroke-width="12" color="#409EFF" />
      <div class="progress-status">Testing emergency lighting functionality...</div>
    </div>

    <!-- System Status Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon total"><el-icon><Monitor /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.onlineDevices }}/{{ systemStatus.totalDevices }}</div><div class="stat-label">Online Devices</div></div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon health"><el-icon><DataLine /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.overallHealth }}%</div><div class="stat-label">System Health</div></div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon alerts"><el-icon><Warning /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.activeAlerts }}</div><div class="stat-label">Active Alerts</div></div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon test"><el-icon><AlarmClock /></el-icon></div>
          <div class="stat-info"><div class="stat-value">{{ systemStatus.nextAutoTest.split(' ')[1] }}</div><div class="stat-label">Next Auto Test</div></div>
        </div>
      </el-card>
    </div>

    <!-- Search Bar -->
    <div class="search-bar">
      <el-input v-model="searchKeyword" placeholder="Search by name, zone or type..." clearable :prefix-icon="Search" style="width: 320px" />
      <span class="results-count">{{ viewMode === 'zones' ? filteredZones.length : filteredLights.length }} results</span>
    </div>

    <!-- Zones Grid View -->
    <div v-if="viewMode === 'zones'" class="zones-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="zone.status">
        <div class="zone-header">
          <div class="zone-info"><div class="zone-name">{{ zone.name }}</div><div class="zone-type">{{ zone.type }}</div></div>
          <div class="zone-status-dot" :style="{ background: getStatusColor(zone.status) }"></div>
        </div>
        <div class="zone-stats">
          <div class="zone-stat"><span class="stat-label">Lights</span><span class="stat-value">{{ zone.onlineLights }}/{{ zone.lightCount }}</span></div>
          <div class="zone-stat"><span class="stat-label">Battery</span><span class="stat-value" :style="{ color: getBatteryColor(zone.batteryLevel) }">{{ zone.batteryLevel }}%</span></div>
          <div class="zone-stat"><span class="stat-label">Last Test</span><span class="stat-value">{{ zone.lastTest }}</span></div>
          <div class="zone-stat"><span class="stat-label">Auto Test</span><span class="stat-value">{{ zone.autoTest ? 'ON' : 'OFF' }}</span></div>
        </div>
        <div class="zone-progress"><div class="battery-bar" :style="{ width: zone.batteryLevel + '%', background: getBatteryColor(zone.batteryLevel) }"></div></div>
        <div class="zone-alerts" v-if="zone.alerts"><el-icon><Warning /></el-icon> {{ zone.alerts[0] }}</div>
        <div class="zone-actions">
          <el-button size="small" @click="viewZoneDetails(zone)"><el-icon><Search /></el-icon> Details</el-button>
          <el-button size="small" type="primary" plain @click="performZoneTest(zone)" :disabled="manualTestActive"><el-icon><Operation /></el-icon> Test</el-button>
          <el-button size="small" type="warning" plain @click="emergencyActivateZone(zone)"><el-icon><Warning /></el-icon> Emergency</el-button>
          <el-button size="small" type="info" plain @click="toggleAutoTest(zone)"><el-icon><Clock /></el-icon> Auto</el-button>
          <el-button v-if="zone.batteryLevel < 80" size="small" type="danger" plain @click="scheduleMaintenance(zone)"><el-icon><Tools /></el-icon> Maint</el-button>
        </div>
      </div>
    </div>

    <!-- Lights Grid View -->
    <div v-if="viewMode === 'lights'" class="lights-grid">
      <div v-for="light in filteredLights" :key="light.id" class="light-card">
        <div class="light-header"><div class="light-id">{{ light.id }}</div><div class="light-status-dot" :style="{ background: getStatusColor(light.status) }"></div></div>
        <div class="light-name">{{ light.name }}</div>
        <div class="light-zone">{{ light.zone }}</div>
        <div class="light-details"><span>Model: {{ light.model }}</span><span>Runtime: {{ light.runtime }} min</span></div>
        <div class="light-battery"><span class="battery-label">Battery</span><div class="battery-bar-small"><div class="battery-fill" :style="{ width: light.batteryLevel + '%', background: getBatteryColor(light.batteryLevel) }"></div></div><span class="battery-value" :style="{ color: getBatteryColor(light.batteryLevel) }">{{ light.batteryLevel }}%</span></div>
        <div class="light-actions"><el-button size="small" @click="viewLightDetails(light)">Details</el-button><el-button size="small" type="primary" plain @click="performLightTest(light)">Test</el-button></div>
      </div>
    </div>

    <!-- Zone Detail Dialog -->
    <el-dialog v-model="showZoneDetail" :title="selectedZone?.name" width="600px">
      <div v-if="selectedZone">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Zone ID">{{ selectedZone.id }}</el-descriptions-item><el-descriptions-item label="Type">{{ selectedZone.type }}</el-descriptions-item>
          <el-descriptions-item label="Status"><span :style="{ color: getStatusColor(selectedZone.status) }">{{ getStatusText(selectedZone.status) }}</span></el-descriptions-item><el-descriptions-item label="Auto Test">{{ selectedZone.autoTest ? 'Enabled' : 'Disabled' }}</el-descriptions-item>
          <el-descriptions-item label="Battery Health"><el-progress :percentage="selectedZone.batteryLevel" :stroke-width="10" :color="getBatteryColor(selectedZone.batteryLevel)" /></el-descriptions-item><el-descriptions-item label="Online Lights">{{ selectedZone.onlineLights }}/{{ selectedZone.lightCount }}</el-descriptions-item>
          <el-descriptions-item label="Last Test">{{ selectedZone.lastTest }}</el-descriptions-item><el-descriptions-item label="Next Test Due">{{ selectedZone.nextTestDue }}</el-descriptions-item>
          <el-descriptions-item label="Schedule">{{ selectedZone.scheduleTest }}</el-descriptions-item><el-descriptions-item label="Dimming Mode">{{ selectedZone.dimmingMode }}</el-descriptions-item>
        </el-descriptions>
        <div class="dialog-actions"><el-button type="primary" @click="performZoneTest(selectedZone)">Run Test</el-button><el-button type="warning" @click="emergencyActivateZone(selectedZone)">Emergency Override</el-button><el-button type="danger" @click="scheduleMaintenance(selectedZone)">Schedule Maintenance</el-button></div>
      </div>
      <template #footer><el-button @click="showZoneDetail = false">Close</el-button></template>
    </el-dialog>

    <!-- Light Detail Dialog -->
    <el-dialog v-model="showLightDetail" :title="selectedLight?.id" width="500px">
      <div v-if="selectedLight">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="Name">{{ selectedLight.name }}</el-descriptions-item><el-descriptions-item label="Zone">{{ selectedLight.zone }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedLight.model }}</el-descriptions-item><el-descriptions-item label="Status"><span :style="{ color: getStatusColor(selectedLight.status) }">{{ getStatusText(selectedLight.status) }}</span></el-descriptions-item>
          <el-descriptions-item label="Battery Health"><el-progress :percentage="selectedLight.batteryLevel" :stroke-width="10" :color="getBatteryColor(selectedLight.batteryLevel)" /></el-descriptions-item>
          <el-descriptions-item label="Runtime">{{ selectedLight.runtime }} minutes</el-descriptions-item><el-descriptions-item label="Lumens">{{ selectedLight.lumens }} lm</el-descriptions-item>
          <el-descriptions-item label="Last Test">{{ selectedLight.lastTest }}</el-descriptions-item>
        </el-descriptions>
        <div class="dialog-actions"><el-button type="primary" @click="performLightTest(selectedLight)">Run Test</el-button><el-button type="warning" @click="scheduleMaintenance({ name: selectedLight.zone })">Schedule Maintenance</el-button></div>
      </div>
      <template #footer><el-button @click="showLightDetail = false">Close</el-button></template>
    </el-dialog>

    <!-- Settings Dialog -->
    <el-dialog v-model="showSettings" title="System Settings" width="550px">
      <el-form label-width="180px">
        <el-form-item label="Auto System Test">
          <el-switch v-model="settings.autoTestEnabled" />
        </el-form-item>
        <el-form-item label="Auto Test Time">
          <el-time-picker v-model="autoTestTimeValue" format="HH:mm" />
        </el-form-item>
        <el-form-item label="Test Duration">
          <el-input-number v-model="settings.testDuration" :min="30" :max="300" /> seconds
        </el-form-item>
        <el-form-item label="Low Battery Threshold">
          <el-input-number v-model="settings.lowBatteryThreshold" :min="50" :max="90" /> %
        </el-form-item>
        <el-form-item label="Critical Threshold">
          <el-input-number v-model="settings.criticalBatteryThreshold" :min="30" :max="70" /> %
        </el-form-item>
        <el-form-item label="Email Notifications">
          <el-switch v-model="settings.notificationEnabled" />
        </el-form-item>
        <el-form-item label="Recipients">
          <el-input v-model="settings.notificationRecipients[0]" placeholder="email@example.com" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSettings = false">Cancel</el-button>
        <el-button type="primary" @click="saveSettings">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* Main Content */
.emergency-lighting-control { padding: 24px; background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%); min-height: 100vh; }
.page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; flex-wrap: wrap; gap: 16px; }
.page-header h2 { margin: 0 0 4px 0; font-size: 28px; font-weight: 700; background: linear-gradient(135deg, #303133, #606266); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.subtitle { margin: 0; color: #909399; font-size: 14px; }
.header-actions { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.view-toggle { display: flex; gap: 0; border-radius: 8px; overflow: hidden; }
.view-toggle .el-button { border-radius: 0; margin: 0; }

/* Test Progress */
.test-progress { background: white; border-radius: 16px; padding: 16px 20px; margin-bottom: 24px; border-left: 4px solid #409EFF; }
.progress-header { display: flex; justify-content: space-between; margin-bottom: 10px; font-weight: 600; }
.progress-status { font-size: 12px; color: #909399; margin-top: 10px; }

/* Stats Grid */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { border-radius: 16px; transition: all 0.3s ease; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card :deep(.el-card__body) { padding: 16px; }
.stat-content { display: flex; align-items: center; gap: 12px; }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.stat-icon.total { background: rgba(64, 158, 255, 0.1); color: #409EFF; }
.stat-icon.health { background: rgba(103, 194, 58, 0.1); color: #67C23A; }
.stat-icon.alerts { background: rgba(245, 108, 108, 0.1); color: #F56C6C; }
.stat-icon.test { background: rgba(230, 162, 60, 0.1); color: #E6A23C; }
.stat-info { flex: 1; }
.stat-value { font-size: 24px; font-weight: 700; color: #303133; line-height: 1.2; }
.stat-label { font-size: 12px; color: #909399; margin-top: 4px; }

/* Search Bar */
.search-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.results-count { font-size: 13px; color: #909399; }

/* Zones Grid */
.zones-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 20px; }
.zone-card { background: white; border-radius: 20px; padding: 20px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05); transition: all 0.3s ease; border-left: 4px solid; }
.zone-card.healthy { border-left-color: #67C23A; }
.zone-card.warning { border-left-color: #E6A23C; }
.zone-card.critical { border-left-color: #F56C6C; }
.zone-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); }
.zone-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.zone-name { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
.zone-type { font-size: 12px; color: #909399; }
.zone-status-dot { width: 12px; height: 12px; border-radius: 50%; }
.zone-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.zone-stat { display: flex; flex-direction: column; }
.zone-stat .stat-label { font-size: 11px; color: #909399; margin-bottom: 4px; }
.zone-stat .stat-value { font-size: 14px; font-weight: 600; }
.zone-progress { margin-bottom: 12px; }
.battery-bar { height: 8px; border-radius: 4px; }
.zone-alerts { font-size: 11px; color: #F56C6C; margin-bottom: 16px; display: flex; align-items: center; gap: 4px; }
.zone-actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }

/* Lights Grid */
.lights-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
.light-card { background: white; border-radius: 16px; padding: 16px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); transition: all 0.2s ease; }
.light-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1); }
.light-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.light-id { font-family: monospace; font-weight: 600; font-size: 13px; }
.light-status-dot { width: 10px; height: 10px; border-radius: 50%; }
.light-name { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.light-zone { font-size: 12px; color: #909399; margin-bottom: 8px; }
.light-details { display: flex; justify-content: space-between; font-size: 11px; color: #c0c4cc; margin-bottom: 12px; }
.light-battery { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.battery-label { font-size: 11px; color: #909399; }
.battery-bar-small { flex: 1; height: 6px; background: #e4e7ed; border-radius: 3px; overflow: hidden; }
.battery-fill { height: 100%; border-radius: 3px; }
.battery-value { font-size: 12px; font-weight: 600; }
.light-actions { display: flex; gap: 8px; justify-content: flex-end; }

/* Dialog Actions */
.dialog-actions { display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px; flex-wrap: wrap; }

/* Responsive */
@media (max-width: 1200px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) {
  .emergency-lighting-control { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .view-toggle { width: 100%; }
  .header-actions .view-toggle .el-button { flex: 1; }
  .stats-grid { grid-template-columns: 1fr; }
  .zones-grid { grid-template-columns: 1fr; }
}
</style>