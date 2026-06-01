<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Bell, User, Location, Phone,
  VideoCamera, Lock, DataAnalysis,
  Timer, Check, Close, Edit, Delete,
  Lightning, Connection, Sunny
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing power monitoring system...',
  'Connecting to UPS and generator systems...',
  'Loading critical load data...',
  'Ready for emergency response...'
]

// Power status
const powerStatus = ref({
  utilityStatus: 'Normal',
  upsStatus: 'Ready',
  generatorStatus: 'Standby',
  batteryRuntime: 'N/A',
  loadPercent: 65,
  estimatedRestoreTime: 'N/A'
})

// Emergency status
const emergencyStatus = ref({
  isActive: false,
  outageType: 'None',
  affectedAreas: [] as string[],
  triggeredAt: '',
  estimatedDuration: 'N/A',
  responseTeamDispatched: false
})

// Power zones
const powerZones = ref([
  { id: 'zone-1', name: 'Data Center A', status: 'normal', priority: 'Critical', upsBackup: true, generatorCoverage: true, load: 65, alerts: [] },
  { id: 'zone-2', name: 'Data Center B', status: 'normal', priority: 'Critical', upsBackup: true, generatorCoverage: true, load: 58, alerts: [] },
  { id: 'zone-3', name: 'Server Room', status: 'normal', priority: 'Critical', upsBackup: true, generatorCoverage: true, load: 72, alerts: [] },
  { id: 'zone-4', name: 'Office Areas', status: 'normal', priority: 'Standard', upsBackup: false, generatorCoverage: false, load: 45, alerts: [] },
  { id: 'zone-5', name: 'HVAC Systems', status: 'warning', priority: 'Standard', upsBackup: false, generatorCoverage: true, load: 38, alerts: [{ type: 'Voltage Fluctuation', time: '09:15:00' }] },
  { id: 'zone-6', name: 'Lighting', status: 'normal', priority: 'Standard', upsBackup: false, generatorCoverage: true, load: 25, alerts: [] },
  { id: 'zone-7', name: 'Security Systems', status: 'normal', priority: 'Critical', upsBackup: true, generatorCoverage: true, load: 15, alerts: [] },
  { id: 'zone-8', name: 'Elevators', status: 'normal', priority: 'Standard', upsBackup: false, generatorCoverage: true, load: 20, alerts: [] }
])

// UPS Systems
const upsSystems = ref([
  { id: 'UPS-01', name: 'Main UPS Unit 1', status: 'Online', load: 62, batteryCharge: 92, runtime: 18.5, location: 'Data Center A', lastTest: '2025-01-15' },
  { id: 'UPS-02', name: 'Main UPS Unit 2', status: 'Online', load: 58, batteryCharge: 94, runtime: 20.2, location: 'Data Center B', lastTest: '2025-01-14' },
  { id: 'UPS-03', name: 'Server Room UPS', status: 'Online', load: 45, batteryCharge: 88, runtime: 15.8, location: 'Server Room', lastTest: '2025-01-13' },
  { id: 'UPS-04', name: 'Security UPS', status: 'Online', load: 28, batteryCharge: 96, runtime: 25.0, location: 'Security Office', lastTest: '2025-01-12' }
])

// Generators
const generators = ref([
  { id: 'GEN-01', name: 'Emergency Generator 1', status: 'Standby', fuelLevel: 92, loadCapacity: 1000, runtime: 0, lastTest: '2025-01-15', location: 'Generator Room A' },
  { id: 'GEN-02', name: 'Emergency Generator 2', status: 'Standby', fuelLevel: 88, loadCapacity: 1000, runtime: 0, lastTest: '2025-01-14', location: 'Generator Room B' },
  { id: 'GEN-03', name: 'Portable Generator', status: 'Ready', fuelLevel: 75, loadCapacity: 500, runtime: 0, lastTest: '2025-01-10', location: 'Maintenance Bay' }
])

// Critical loads
const criticalLoads = ref([
  { name: 'IT Equipment', priority: 'Critical', powerRequired: 450, upsProtected: true, generatorCovered: true, currentStatus: 'Normal' },
  { name: 'Security Systems', priority: 'Critical', powerRequired: 75, upsProtected: true, generatorCovered: true, currentStatus: 'Normal' },
  { name: 'Communication Systems', priority: 'Critical', powerRequired: 50, upsProtected: true, generatorCovered: true, currentStatus: 'Normal' },
  { name: 'Medical Equipment', priority: 'High', powerRequired: 30, upsProtected: true, generatorCovered: true, currentStatus: 'Normal' },
  { name: 'HVAC Critical', priority: 'High', powerRequired: 200, upsProtected: false, generatorCovered: true, currentStatus: 'Normal' }
])

// Incident history
const incidentHistory = ref([
  { id: 'PWR-001', date: '2025-01-15', time: '14:30:00', duration: '45 min', affected: 'Office Areas', cause: 'Grid Fluctuation', resolution: 'Auto Restored', restoredBy: 'Utility' },
  { id: 'PWR-002', date: '2025-01-12', time: '22:15:00', duration: '2h 30m', affected: 'Partial Building', cause: 'Transformer Fault', resolution: 'Manual Restore', restoredBy: 'Facilities' },
  { id: 'PWR-003', date: '2025-01-08', time: '08:45:00', duration: '15 min', affected: 'Data Center', cause: 'UPS Test', resolution: 'Generator Start', restoredBy: 'System' },
  { id: 'PWR-004', date: '2025-01-05', time: '16:20:00', duration: '1h', affected: 'HVAC Systems', cause: 'Scheduled Maintenance', resolution: 'Completed', restoredBy: 'Facilities' }
])

// Emergency contacts
const emergencyContacts = ref([
  { name: 'Utility Company', number: '555-0100', type: 'External', responseTime: '30-60 min' },
  { name: 'Facilities Manager', number: '555-0199', type: 'Internal', responseTime: '5 min' },
  { name: 'Generator Service', number: '555-0188', type: 'Vendor', responseTime: '45-60 min' },
  { name: 'UPS Support', number: '555-0177', type: 'Vendor', responseTime: '30-45 min' }
])

// UI State
const showUPS = ref(false)
const showGenerators = ref(false)
const showHistory = ref(false)
const showLoadAnalysis = ref(false)
const searchKeyword = ref('')

const filteredZones = computed(() => {
  if (!searchKeyword.value) return powerZones.value
  return powerZones.value.filter(z =>
      z.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const getZoneStatusColor = (status: string) => {
  switch(status) {
    case 'outage': return '#F56C6C'
    case 'warning': return '#E6A23C'
    case 'normal': return '#67C23A'
    default: return '#909399'
  }
}

const getZoneStatusText = (status: string) => {
  switch(status) {
    case 'outage': return 'OUTAGE'
    case 'warning': return 'Warning'
    case 'normal': return 'Normal'
    default: return 'Unknown'
  }
}

const getPriorityColor = (priority: string) => {
  switch(priority) {
    case 'Critical': return '#F56C6C'
    case 'High': return '#E6A23C'
    case 'Standard': return '#409EFF'
    case 'Low': return '#67C23A'
    default: return '#909399'
  }
}

// Emergency actions
const simulateOutage = () => {
  ElMessageBox.confirm(
      'SIMULATE POWER OUTAGE?\n\nThis will test emergency response procedures without affecting actual power.',
      'Simulate Outage',
      {
        confirmButtonText: 'Start Simulation',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.info('Power outage simulation started - Testing backup systems')
    setTimeout(() => {
      ElMessage.success('Simulation completed - All backup systems operational')
    }, 5000)
  }).catch(() => {})
}

const startGenerator = (gen: any) => {
  ElMessageBox.confirm(
      `Start ${gen.name}? This will begin generator operation.`,
      'Start Generator',
      {
        confirmButtonText: 'Start',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    gen.status = 'Running'
    gen.runtime = 0
    ElMessage.success(`${gen.name} started successfully`)

    // Simulate runtime increment
    const interval = setInterval(() => {
      gen.runtime += 0.5
      if (gen.runtime >= 10) clearInterval(interval)
    }, 1000)
  }).catch(() => {})
}

const stopGenerator = (gen: any) => {
  ElMessageBox.confirm(
      `Stop ${gen.name}?`,
      'Stop Generator',
      {
        confirmButtonText: 'Stop',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    gen.status = 'Standby'
    ElMessage.success(`${gen.name} stopped`)
  }).catch(() => {})
}

const activateEmergency = () => {
  ElMessageBox.confirm(
      'ACTIVATE POWER OUTAGE EMERGENCY PROTOCOL?\n\nThis will:\n- Notify facilities team\n- Monitor critical loads\n- Prepare generator startup\n- Log outage start time',
      'Power Outage Emergency',
      {
        confirmButtonText: 'Activate',
        cancelButtonText: 'Cancel',
        type: 'error'
      }
  ).then(() => {
    emergencyStatus.value.isActive = true
    emergencyStatus.value.outageType = 'Full Building'
    emergencyStatus.value.triggeredAt = new Date().toLocaleString()
    emergencyStatus.value.estimatedDuration = 'Unknown - Assessing'
    powerStatus.value.utilityStatus = 'Outage'

    // Set affected zones
    const affected = powerZones.value.filter(z => !z.upsBackup).map(z => z.name)
    emergencyStatus.value.affectedAreas = affected

    ElMessage.error('POWER OUTAGE EMERGENCY ACTIVATED - Backup systems engaging')

    // Auto-start generators
    setTimeout(() => {
      generators.value.forEach(gen => {
        if (gen.status === 'Standby') {
          gen.status = 'Running'
        }
      })
      powerStatus.value.generatorStatus = 'Running'
      ElMessage.warning('Generators started - Critical loads protected')
    }, 3000)
  }).catch(() => {})
}

const deactivateEmergency = () => {
  ElMessageBox.confirm(
      'Deactivate power outage emergency?\n\nConfirm that utility power has been restored.',
      'Deactivate Emergency',
      {
        confirmButtonText: 'Deactivate',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    emergencyStatus.value.isActive = false
    powerStatus.value.utilityStatus = 'Normal'
    ElMessage.success('Power outage emergency deactivated')
  }).catch(() => {})
}

const transferToGenerator = () => {
  ElMessageBox.confirm(
      'Transfer critical loads to generator power?\n\nThis will switch from utility to generator supply.',
      'Transfer to Generator',
      {
        confirmButtonText: 'Transfer',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    ElMessage.success('Transfer complete - Running on generator power')
    powerStatus.value.utilityStatus = 'Outage'
    powerStatus.value.generatorStatus = 'Running'
  }).catch(() => {})
}

const transferToUtility = () => {
  ElMessageBox.confirm(
      'Transfer loads back to utility power?\n\nConfirm utility power is stable.',
      'Transfer to Utility',
      {
        confirmButtonText: 'Transfer',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    ElMessage.success('Transfer complete - Running on utility power')
    powerStatus.value.utilityStatus = 'Normal'
    powerStatus.value.generatorStatus = 'Standby'
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.info('Refreshing power data...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
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
        <div class="loading-tip">Power Outage Response</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="power-outage">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Power Outage Response</h2>
        <p class="subtitle">Emergency power management and critical load protection</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="showUPS = true">
          <el-icon><Connection /></el-icon> UPS Systems
        </el-button>
        <el-button @click="showGenerators = true">
          <el-icon><Tools /></el-icon> Generators
        </el-button>
        <el-button @click="showLoadAnalysis = true">
          <el-icon><DataAnalysis /></el-icon> Load Analysis
        </el-button>
        <el-button @click="showHistory = true">
          <el-icon><Document /></el-icon> History
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Power Status Banner -->
    <div class="status-banner">
      <div class="status-item">
        <span class="status-label">Utility Power:</span>
        <span class="status-value" :style="{ color: powerStatus.utilityStatus === 'Normal' ? '#67C23A' : '#F56C6C' }">
          {{ powerStatus.utilityStatus }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">UPS Status:</span>
        <span class="status-value">{{ powerStatus.upsStatus }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">Generator:</span>
        <span class="status-value" :style="{ color: powerStatus.generatorStatus === 'Running' ? '#67C23A' : '#909399' }">
          {{ powerStatus.generatorStatus }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">Total Load:</span>
        <span class="status-value">{{ powerStatus.loadPercent }}%</span>
      </div>
    </div>

    <!-- Active Emergency Banner -->
    <div v-if="emergencyStatus.isActive" class="emergency-banner">
      <div class="emergency-icon">⚡</div>
      <div class="emergency-info">
        <div class="emergency-title">POWER OUTAGE EMERGENCY ACTIVE</div>
        <div class="emergency-time">🕐 Occurred: {{ emergencyStatus.triggeredAt }}</div>
        <div class="emergency-areas">📍 Affected: {{ emergencyStatus.affectedAreas.join(', ') }}</div>
      </div>
      <div class="emergency-actions">
        <el-button type="danger" size="large" @click="deactivateEmergency">CLEAR EMERGENCY</el-button>
      </div>
    </div>

    <!-- Quick Action Buttons -->
    <div class="quick-actions">
      <div class="section-header">
        <span>Emergency Power Actions</span>
        <el-tag type="danger" size="small">Immediate</el-tag>
      </div>
      <div class="action-buttons">
        <el-button type="danger" plain size="large" @click="activateEmergency">
          <el-icon><Warning /></el-icon> Report Outage
        </el-button>
        <el-button type="warning" plain size="large" @click="transferToGenerator">
          <el-icon><Lightning /></el-icon> Transfer to Generator
        </el-button>
        <el-button type="success" plain size="large" @click="transferToUtility">
          <el-icon><Sunny /></el-icon> Transfer to Utility
        </el-button>
        <el-button type="info" plain size="large" @click="simulateOutage">
          <el-icon><Operation /></el-icon> Simulate Outage
        </el-button>
      </div>
    </div>

    <!-- Power Zones -->
    <div class="zones-section">
      <div class="section-header">
        <span>Power Zones</span>
        <el-input v-model="searchKeyword" placeholder="Search zones..." clearable style="width: 200px" :prefix-icon="Search" />
      </div>
      <div class="zones-grid">
        <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="zone.status">
          <div class="zone-header">
            <div class="zone-name">{{ zone.name }}</div>
            <div class="zone-status" :style="{ color: getZoneStatusColor(zone.status) }">
              {{ getZoneStatusText(zone.status) }}
            </div>
          </div>
          <div class="zone-priority">
            <el-tag :type="zone.priority === 'Critical' ? 'danger' : 'info'" size="small">
              {{ zone.priority }} Priority
            </el-tag>
          </div>
          <div class="zone-stats">
            <div class="zone-stat">Load: {{ zone.load }}%</div>
            <div class="zone-stat">UPS: {{ zone.upsBackup ? 'Yes' : 'No' }}</div>
            <div class="zone-stat">Generator: {{ zone.generatorCoverage ? 'Yes' : 'No' }}</div>
          </div>
          <div class="zone-alerts" v-if="zone.alerts.length > 0">
            <div v-for="alert in zone.alerts" :key="alert.time" class="alert-item-small">
              <el-icon><Warning /></el-icon> {{ alert.type }} at {{ alert.time }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- UPS Systems -->
    <el-card class="ups-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Connection /></el-icon> UPS Systems Status</span>
          <el-tag type="info" size="small">Backup Power</el-tag>
        </div>
      </template>
      <div class="ups-grid">
        <div v-for="ups in upsSystems" :key="ups.id" class="ups-card-item">
          <div class="ups-name">{{ ups.name }}</div>
          <div class="ups-status">{{ ups.status }}</div>
          <div class="ups-load">Load: {{ ups.load }}%</div>
          <div class="ups-battery">Battery: {{ ups.batteryCharge }}%</div>
          <div class="ups-runtime">Runtime: {{ ups.runtime }} min</div>
          <div class="ups-location">{{ ups.location }}</div>
        </div>
      </div>
    </el-card>

    <!-- Generators -->
    <el-card class="generators-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Tools /></el-icon> Emergency Generators</span>
          <el-tag type="warning" size="small">Standby Power</el-tag>
        </div>
      </template>
      <div class="generators-grid">
        <div v-for="gen in generators" :key="gen.id" class="generator-card">
          <div class="gen-name">{{ gen.name }}</div>
          <div class="gen-status" :class="gen.status === 'Running' ? 'running' : 'standby'">
            {{ gen.status }}
          </div>
          <div class="gen-fuel">Fuel: {{ gen.fuelLevel }}%</div>
          <div class="gen-capacity">Capacity: {{ gen.loadCapacity }} kW</div>
          <div class="gen-runtime" v-if="gen.runtime > 0">Runtime: {{ gen.runtime }} hrs</div>
          <div class="gen-location">{{ gen.location }}</div>
          <div class="gen-actions">
            <el-button v-if="gen.status === 'Standby'" size="small" type="success" @click="startGenerator(gen)">Start</el-button>
            <el-button v-if="gen.status === 'Running'" size="small" type="danger" @click="stopGenerator(gen)">Stop</el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Emergency Contacts -->
    <el-card class="contacts-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Phone /></el-icon> Emergency Power Contacts</span>
          <el-tag type="danger" size="small">24/7 Available</el-tag>
        </div>
      </template>
      <div class="contacts-grid">
        <div v-for="contact in emergencyContacts" :key="contact.name" class="contact-card">
          <div class="contact-name">{{ contact.name }}</div>
          <div class="contact-number"><el-icon><Phone /></el-icon> {{ contact.number }}</div>
          <div class="contact-type">{{ contact.type }} • Response: {{ contact.responseTime }}</div>
        </div>
      </div>
    </el-card>

    <!-- UPS Systems Dialog -->
    <el-dialog v-model="showUPS" title="UPS Systems Detail" width="800px">
      <el-table :data="upsSystems" stripe>
        <el-table-column prop="id" label="ID" width="90" />
        <el-table-column prop="name" label="Name" min-width="150" />
        <el-table-column prop="status" label="Status" width="90">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="load" label="Load" width="80">
          <template #default="{ row }">
            <el-progress :percentage="row.load" :stroke-width="6" :show-text="false" />
          </template>
        </el-table-column>
        <el-table-column prop="batteryCharge" label="Battery" width="80">
          <template #default="{ row }">
            <el-progress :percentage="row.batteryCharge" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="runtime" label="Runtime (min)" width="100" />
        <el-table-column prop="location" label="Location" min-width="120" />
        <el-table-column prop="lastTest" label="Last Test" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="showUPS = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Generators Dialog -->
    <el-dialog v-model="showGenerators" title="Generators Detail" width="800px">
      <el-table :data="generators" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Name" min-width="150" />
        <el-table-column label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Running' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fuelLevel" label="Fuel" width="80">
          <template #default="{ row }">
            <el-progress :percentage="row.fuelLevel" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="loadCapacity" label="Capacity (kW)" width="100" />
        <el-table-column prop="location" label="Location" min-width="140" />
        <el-table-column prop="lastTest" label="Last Test" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="showGenerators = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Load Analysis Dialog -->
    <el-dialog v-model="showLoadAnalysis" title="Critical Load Analysis" width="800px">
      <el-table :data="criticalLoads" stripe>
        <el-table-column prop="name" label="Load" min-width="150" />
        <el-table-column label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="row.priority === 'Critical' ? 'danger' : 'warning'" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="powerRequired" label="Power (kW)" width="100" />
        <el-table-column label="UPS Protected" width="100">
          <template #default="{ row }">
            <el-icon :color="row.upsProtected ? '#67C23A' : '#909399'">{{ row.upsProtected ? 'CircleCheck' : 'CircleClose' }}</el-icon>
          </template>
        </el-table-column>
        <el-table-column label="Generator Covered" width="120">
          <template #default="{ row }">
            <el-icon :color="row.generatorCovered ? '#67C23A' : '#909399'">{{ row.generatorCovered ? 'CircleCheck' : 'CircleClose' }}</el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="currentStatus" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.currentStatus === 'Normal' ? 'success' : 'danger'" size="small">{{ row.currentStatus }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="showLoadAnalysis = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Incident History Dialog -->
    <el-dialog v-model="showHistory" title="Power Incident History" width="800px">
      <el-table :data="incidentHistory" stripe>
        <el-table-column prop="date" label="Date" width="100" />
        <el-table-column prop="time" label="Time" width="80" />
        <el-table-column prop="duration" label="Duration" width="90" />
        <el-table-column prop="affected" label="Affected Areas" min-width="130" />
        <el-table-column prop="cause" label="Cause" min-width="120" />
        <el-table-column prop="resolution" label="Resolution" min-width="120" />
        <el-table-column prop="restoredBy" label="Restored By" width="100" />
      </el-table>
      <template #footer>
        <el-button @click="showHistory = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.power-outage {
  padding: 24px;
  background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #e65100, #ff9800);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #e65100;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Status Banner */
.status-banner {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  gap: 20px;
}

.status-item {
  display: flex;
  gap: 8px;
  font-size: 14px;
}

.status-label { color: #909399; }
.status-value { font-weight: 600; color: #303133; }

/* Emergency Banner */
.emergency-banner {
  background: linear-gradient(135deg, #e65100, #ff9800);
  border-radius: 20px;
  padding: 20px 24px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  flex-wrap: wrap;
  animation: pulse-orange 1s infinite;
}

@keyframes pulse-orange {
  0%, 100% { box-shadow: 0 0 0 0 rgba(230, 81, 0, 0.4); }
  50% { box-shadow: 0 0 0 20px rgba(230, 81, 0, 0); }
}

.emergency-icon { font-size: 48px; }
.emergency-info { flex: 1; }
.emergency-title { font-weight: 700; font-size: 24px; margin-bottom: 4px; }
.emergency-time, .emergency-areas { font-size: 13px; opacity: 0.9; }

/* Quick Actions */
.quick-actions {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 15px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 180px;
}

/* Zones Section */
.zones-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.zone-card {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.2s ease;
  border-left: 4px solid #67C23A;
}

.zone-card.outage { border-left-color: #F56C6C; background: #fff0f0; }
.zone-card.warning { border-left-color: #E6A23C; }

.zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.zone-name { font-weight: 600; font-size: 16px; }
.zone-status { font-weight: 600; font-size: 13px; }

.zone-priority { margin-bottom: 8px; }

.zone-stats {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 12px;
}

.zone-alerts {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.alert-item-small {
  font-size: 12px;
  color: #F56C6C;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

/* UPS Grid */
.ups-card, .generators-card, .contacts-card {
  border-radius: 20px;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.ups-grid, .generators-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.ups-card-item, .generator-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
}

.ups-name, .gen-name { font-weight: 600; margin-bottom: 4px; }
.ups-status, .gen-status { font-size: 12px; font-weight: 600; margin-bottom: 8px; }
.gen-status.running { color: #67C23A; }
.gen-status.standby { color: #909399; }
.ups-load, .ups-battery, .ups-runtime, .ups-location,
.gen-fuel, .gen-capacity, .gen-runtime, .gen-location {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.gen-actions { margin-top: 8px; }

/* Contacts Grid */
.contacts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.contact-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
}

.contact-name { font-weight: 600; margin-bottom: 4px; }
.contact-number { font-size: 13px; color: #409EFF; margin-bottom: 4px; display: flex; align-items: center; gap: 4px; }
.contact-type { font-size: 11px; color: #909399; }

/* Responsive */
@media (max-width: 768px) {
  .power-outage { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
  .zones-grid { grid-template-columns: 1fr; }
  .ups-grid, .generators-grid { grid-template-columns: 1fr; }
  .status-banner { flex-direction: column; }
}
</style>