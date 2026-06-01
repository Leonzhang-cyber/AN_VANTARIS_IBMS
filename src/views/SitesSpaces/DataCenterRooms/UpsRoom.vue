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
        <div class="loading-tip">UPS Room Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ups-room">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>UPS Room Management</h2>
        <p class="subtitle">Monitor and manage UPS systems, battery health, and power backup infrastructure</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddUPSDialog">
          <el-icon><Plus /></el-icon> Add UPS Unit
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-info">
          <div class="stat-value">{{ upsUnits.length }}</div>
          <div class="stat-label">Total UPS Units</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔋</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCapacity }} kVA</div>
          <div class="stat-label">Total Capacity</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgLoad }}%</div>
          <div class="stat-label">Avg Load</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ alertCount }}</div>
          <div class="stat-label">Active Alerts</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by UPS name, model or location..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Normal" value="normal" />
          <el-option label="Warning" value="warning" />
          <el-option label="Critical" value="critical" />
          <el-option label="Maintenance" value="maintenance" />
        </el-select>
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 160px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
      </div>
    </div>

    <!-- UPS Units Grid -->
    <div class="ups-grid">
      <div v-for="ups in filteredUPS" :key="ups.id" class="ups-card" :class="ups.status">
        <div class="ups-header">
          <div class="ups-icon">⚡</div>
          <div class="ups-info">
            <div class="ups-name">{{ ups.name }}</div>
            <div class="ups-model">{{ ups.model }}</div>
          </div>
          <div class="ups-status">
            <span class="status-badge" :class="ups.status">{{ getStatusText(ups.status) }}</span>
          </div>
        </div>

        <div class="ups-location">
          <el-icon><Location /></el-icon>
          <span>{{ ups.buildingName }} - {{ ups.location }}</span>
        </div>

        <!-- Key Metrics -->
        <div class="ups-metrics">
          <div class="metric-item">
            <div class="metric-value">{{ ups.capacity }} kVA</div>
            <div class="metric-label">Capacity</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ ups.load }}%</div>
            <div class="metric-label">Load</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ ups.batteryHealth }}%</div>
            <div class="metric-label">Battery Health</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ ups.runtime }} min</div>
            <div class="metric-label">Runtime</div>
          </div>
        </div>

        <!-- Detailed Stats -->
        <div class="ups-details">
          <div class="detail-row">
            <span class="detail-label">Input Voltage</span>
            <span class="detail-value">{{ ups.inputVoltage }} V</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Output Voltage</span>
            <span class="detail-value">{{ ups.outputVoltage }} V</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Temperature</span>
            <span class="detail-value" :class="getTempClass(ups.temperature)">{{ ups.temperature }}°C</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Efficiency</span>
            <span class="detail-value">{{ ups.efficiency }}%</span>
          </div>
        </div>

        <!-- Battery String Info -->
        <div class="battery-section">
          <div class="battery-title">Battery Strings</div>
          <div class="battery-strings">
            <div v-for="(battery, idx) in ups.batteryStrings" :key="idx" class="battery-string">
              <span class="string-name">{{ battery.name }}</span>
              <el-progress :percentage="battery.health" :stroke-width="6" :color="getBatteryColor(battery.health)" :show-text="false" />
              <span class="string-health" :style="{ color: getBatteryColor(battery.health) }">{{ battery.health }}%</span>
            </div>
          </div>
        </div>

        <div class="ups-alerts" v-if="ups.alerts && ups.alerts.length > 0">
          <div v-for="alert in ups.alerts.slice(0, 2)" :key="alert.time" class="alert-item">
            <el-icon><Warning /></el-icon>
            <span>{{ alert.message }}</span>
          </div>
          <div v-if="ups.alerts.length > 2" class="alert-more">+{{ ups.alerts.length - 2 }} more alerts</div>
        </div>

        <div class="ups-actions">
          <el-button size="small" type="primary" plain @click="viewUPS(ups)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editUPS(ups)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteUPS(ups)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredUPS.length === 0" class="empty-state">
      <div class="empty-icon">⚡</div>
      <div class="empty-title">No UPS units found</div>
      <div class="empty-desc">Add a UPS unit to start managing power backup infrastructure</div>
      <el-button type="primary" @click="openAddUPSDialog">Add UPS Unit</el-button>
    </div>

    <!-- Add/Edit UPS Dialog -->
    <el-dialog v-model="showUPSDialog" :title="dialogTitle" width="650px">
      <el-form :model="upsForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="UPS Name" required>
              <el-input v-model="upsForm.name" placeholder="e.g., UPS-01" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Model">
              <el-input v-model="upsForm.model" placeholder="e.g., Galaxy VX" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="upsForm.buildingId" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="upsForm.location" placeholder="e.g., Floor 1, UPS Room A" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Capacity (kVA)">
              <el-input-number v-model="upsForm.capacity" :min="0" :step="50" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Input Voltage (V)">
              <el-input-number v-model="upsForm.inputVoltage" :min="100" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Output Voltage (V)">
              <el-input-number v-model="upsForm.outputVoltage" :min="100" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Battery Strings">
              <el-input-number v-model="upsForm.batteryStringsCount" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Installation Date">
              <el-date-picker v-model="upsForm.installationDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="upsForm.status">
            <el-radio label="normal">Normal</el-radio>
            <el-radio label="warning">Warning</el-radio>
            <el-radio label="critical">Critical</el-radio>
            <el-radio label="maintenance">Maintenance</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="upsForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUPSDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveUPS">Save UPS Unit</el-button>
      </template>
    </el-dialog>

    <!-- UPS Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedUPS?.name" width="750px">
      <div v-if="selectedUPS">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="UPS ID">{{ selectedUPS.id }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedUPS.model }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedUPS.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedUPS.location }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedUPS.status]">{{ getStatusText(selectedUPS.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedUPS.capacity }} kVA</el-descriptions-item>
          <el-descriptions-item label="Current Load">{{ selectedUPS.load }}%</el-descriptions-item>
          <el-descriptions-item label="Input Voltage">{{ selectedUPS.inputVoltage }} V</el-descriptions-item>
          <el-descriptions-item label="Output Voltage">{{ selectedUPS.outputVoltage }} V</el-descriptions-item>
          <el-descriptions-item label="Battery Health">{{ selectedUPS.batteryHealth }}%</el-descriptions-item>
          <el-descriptions-item label="Remaining Runtime">{{ selectedUPS.runtime }} minutes</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedUPS.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Efficiency">{{ selectedUPS.efficiency }}%</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ selectedUPS.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedUPS.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedUPS.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedUPS.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedUPS.batteryStrings && selectedUPS.batteryStrings.length > 0" class="detail-batteries">
          <h4>Battery Strings</h4>
          <el-table :data="selectedUPS.batteryStrings" size="small">
            <el-table-column prop="name" label="String Name" width="120" />
            <el-table-column label="Health" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.health" :stroke-width="8" :color="getBatteryColor(row.health)" />
              </template>
            </el-table-column>
            <el-table-column prop="voltage" label="Voltage (V)" width="100" />
            <el-table-column prop="temperature" label="Temp (°C)" width="100" />
          </el-table>
        </div>

        <div v-if="selectedUPS.alerts && selectedUPS.alerts.length > 0" class="detail-alerts">
          <h4>Active Alerts</h4>
          <el-table :data="selectedUPS.alerts" size="small">
            <el-table-column label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'critical' ? 'danger' : row.severity === 'warning' ? 'warning' : 'info'" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="Message" />
            <el-table-column prop="time" label="Time" width="140" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editUPS(selectedUPS); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading UPS room data...',
  'Fetching UPS unit information...',
  'Checking battery health...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
}

// UPS Unit interface
interface UPSUnit {
  id: number
  name: string
  model: string
  buildingId: number
  buildingName: string
  location: string
  capacity: number
  load: number
  inputVoltage: number
  outputVoltage: number
  batteryHealth: number
  runtime: number
  temperature: number
  efficiency: number
  status: string
  installationDate: string
  lastMaintenance: string
  nextMaintenance: string
  batteryStrings: { name: string; health: number; voltage: number; temperature: number }[]
  alerts: { severity: string; message: string; time: string }[]
  description: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Data Center A' },
  { id: 2, name: 'Data Center B' },
  { id: 3, name: 'Central Plant' }
])

// Sample UPS units data
const upsUnits = ref<UPSUnit[]>([
  {
    id: 1,
    name: 'UPS-01',
    model: 'Galaxy VX 500',
    buildingId: 1,
    buildingName: 'Data Center A',
    location: 'Floor 1, UPS Room A',
    capacity: 500,
    load: 68,
    inputVoltage: 415,
    outputVoltage: 415,
    batteryHealth: 94,
    runtime: 28,
    temperature: 26.5,
    efficiency: 96.2,
    status: 'normal',
    installationDate: '2023-06-15',
    lastMaintenance: '2024-12-10',
    nextMaintenance: '2025-03-10',
    batteryStrings: [
      { name: 'String A', health: 96, voltage: 432, temperature: 26 },
      { name: 'String B', health: 92, voltage: 428, temperature: 27 }
    ],
    alerts: [],
    description: 'Main UPS for Data Hall A1'
  },
  {
    id: 2,
    name: 'UPS-02',
    model: 'Galaxy VX 500',
    buildingId: 1,
    buildingName: 'Data Center A',
    location: 'Floor 1, UPS Room A',
    capacity: 500,
    load: 72,
    inputVoltage: 414,
    outputVoltage: 415,
    batteryHealth: 88,
    runtime: 22,
    temperature: 27.8,
    efficiency: 95.8,
    status: 'warning',
    installationDate: '2023-06-15',
    lastMaintenance: '2024-12-10',
    nextMaintenance: '2025-03-10',
    batteryStrings: [
      { name: 'String A', health: 86, voltage: 425, temperature: 28 },
      { name: 'String B', health: 90, voltage: 429, temperature: 27 }
    ],
    alerts: [
      { severity: 'warning', message: 'Battery health below 90%', time: '2025-01-16 08:30:00' }
    ],
    description: 'Redundant UPS for Data Hall A1'
  },
  {
    id: 3,
    name: 'UPS-03',
    model: 'Symmetra PX 250',
    buildingId: 2,
    buildingName: 'Data Center B',
    location: 'Floor 1, UPS Room B',
    capacity: 250,
    load: 85,
    inputVoltage: 415,
    outputVoltage: 413,
    batteryHealth: 72,
    runtime: 12,
    temperature: 29.5,
    efficiency: 94.5,
    status: 'critical',
    installationDate: '2022-03-20',
    lastMaintenance: '2024-11-15',
    nextMaintenance: '2025-02-15',
    batteryStrings: [
      { name: 'String A', health: 68, voltage: 415, temperature: 30 },
      { name: 'String B', health: 76, voltage: 420, temperature: 29 }
    ],
    alerts: [
      { severity: 'critical', message: 'Battery health critical - replacement required', time: '2025-01-15 10:00:00' },
      { severity: 'warning', message: 'High temperature detected', time: '2025-01-15 09:45:00' }
    ],
    description: 'Critical load UPS - battery replacement needed'
  },
  {
    id: 4,
    name: 'UPS-04',
    model: '9PX 150',
    buildingId: 2,
    buildingName: 'Data Center B',
    location: 'Floor 2, UPS Room C',
    capacity: 150,
    load: 45,
    inputVoltage: 415,
    outputVoltage: 414,
    batteryHealth: 96,
    runtime: 35,
    temperature: 24.5,
    efficiency: 97.2,
    status: 'normal',
    installationDate: '2024-08-10',
    lastMaintenance: '2025-01-05',
    nextMaintenance: '2025-04-05',
    batteryStrings: [
      { name: 'String A', health: 96, voltage: 435, temperature: 24 }
    ],
    alerts: [],
    description: 'Network and security systems UPS'
  },
  {
    id: 5,
    name: 'UPS-05',
    model: 'Galaxy VX 800',
    buildingId: 1,
    buildingName: 'Data Center A',
    location: 'Floor 3, UPS Room D',
    capacity: 800,
    load: 55,
    inputVoltage: 415,
    outputVoltage: 415,
    batteryHealth: 98,
    runtime: 42,
    temperature: 25.2,
    efficiency: 96.8,
    status: 'normal',
    installationDate: '2024-01-15',
    lastMaintenance: '2025-01-10',
    nextMaintenance: '2025-04-10',
    batteryStrings: [
      { name: 'String A', health: 98, voltage: 438, temperature: 25 },
      { name: 'String B', health: 98, voltage: 437, temperature: 25 },
      { name: 'String C', health: 97, voltage: 436, temperature: 26 }
    ],
    alerts: [],
    description: 'New high-capacity UPS for expansion hall'
  }
])

// UI State
const searchText = ref('')
const filterStatus = ref('all')
const filterBuilding = ref('all')
const showUPSDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedUPS = ref<UPSUnit | null>(null)

const upsForm = ref({
  name: '',
  model: '',
  buildingId: 1,
  location: '',
  capacity: 0,
  inputVoltage: 415,
  outputVoltage: 415,
  batteryStringsCount: 0,
  installationDate: null,
  status: 'normal',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit UPS Unit' : 'Add UPS Unit')

const totalCapacity = computed(() => upsUnits.value.reduce((sum, u) => sum + u.capacity, 0))
const avgLoad = computed(() => Math.round(upsUnits.value.reduce((sum, u) => sum + u.load, 0) / upsUnits.value.length))
const alertCount = computed(() => upsUnits.value.reduce((sum, u) => sum + (u.alerts?.length || 0), 0))

const uniqueBuildings = computed(() => {
  return Array.from(new Set(upsUnits.value.map(u => u.buildingName)))
})

const filteredUPS = computed(() => {
  let filtered = [...upsUnits.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(u =>
        u.name.toLowerCase().includes(keyword) ||
        u.model.toLowerCase().includes(keyword) ||
        u.location.toLowerCase().includes(keyword)
    )
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(u => u.status === filterStatus.value)
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(u => u.buildingName === filterBuilding.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    normal: 'Normal',
    warning: 'Warning',
    critical: 'Critical',
    maintenance: 'Maintenance'
  }
  return map[status] || status
}

const getTempClass = (temp: number) => {
  if (temp > 28) return 'temp-high'
  if (temp > 26) return 'temp-warning'
  return 'temp-normal'
}

const getBatteryColor = (health: number) => {
  if (health < 70) return '#f56c6c'
  if (health < 85) return '#e6a23c'
  return '#67c23a'
}

// UPS CRUD operations
const openAddUPSDialog = () => {
  isEditing.value = false
  upsForm.value = {
    name: '',
    model: '',
    buildingId: buildings.value[0]?.id || 1,
    location: '',
    capacity: 0,
    inputVoltage: 415,
    outputVoltage: 415,
    batteryStringsCount: 0,
    installationDate: null,
    status: 'normal',
    description: ''
  }
  showUPSDialog.value = true
}

const editUPS = (ups: UPSUnit) => {
  isEditing.value = true
  selectedUPS.value = ups
  upsForm.value = {
    name: ups.name,
    model: ups.model,
    buildingId: ups.buildingId,
    location: ups.location,
    capacity: ups.capacity,
    inputVoltage: ups.inputVoltage,
    outputVoltage: ups.outputVoltage,
    batteryStringsCount: ups.batteryStrings?.length || 0,
    installationDate: ups.installationDate,
    status: ups.status,
    description: ups.description || ''
  }
  showUPSDialog.value = true
}

const saveUPS = () => {
  if (!upsForm.value.name.trim()) {
    ElMessage.warning('Please enter UPS name')
    return
  }

  const building = buildings.value.find(b => b.id === upsForm.value.buildingId)

  if (!building) {
    ElMessage.warning('Please select a building')
    return
  }

  if (isEditing.value && selectedUPS.value) {
    const index = upsUnits.value.findIndex(u => u.id === selectedUPS.value!.id)
    if (index !== -1) {
      upsUnits.value[index] = {
        ...upsUnits.value[index],
        name: upsForm.value.name,
        model: upsForm.value.model,
        buildingId: upsForm.value.buildingId,
        buildingName: building.name,
        location: upsForm.value.location,
        capacity: upsForm.value.capacity,
        inputVoltage: upsForm.value.inputVoltage,
        outputVoltage: upsForm.value.outputVoltage,
        status: upsForm.value.status,
        description: upsForm.value.description
      }
      ElMessage.success('UPS unit updated successfully')
    }
  } else {
    const newUPS: UPSUnit = {
      id: Date.now(),
      name: upsForm.value.name,
      model: upsForm.value.model,
      buildingId: upsForm.value.buildingId,
      buildingName: building.name,
      location: upsForm.value.location,
      capacity: upsForm.value.capacity,
      load: 0,
      inputVoltage: upsForm.value.inputVoltage,
      outputVoltage: upsForm.value.outputVoltage,
      batteryHealth: 100,
      runtime: 0,
      temperature: 25,
      efficiency: 96,
      status: upsForm.value.status,
      installationDate: upsForm.value.installationDate || new Date().toISOString().split('T')[0],
      lastMaintenance: new Date().toISOString().split('T')[0],
      nextMaintenance: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
      batteryStrings: [],
      alerts: [],
      description: upsForm.value.description
    }
    upsUnits.value.push(newUPS)
    ElMessage.success('UPS unit added successfully')
  }

  showUPSDialog.value = false
}

const viewUPS = (ups: UPSUnit) => {
  selectedUPS.value = ups
  showDetailDialog.value = true
}

const deleteUPS = (ups: UPSUnit) => {
  ElMessageBox.confirm(
      `Delete UPS unit "${ups.name}"? This will remove all associated battery and alert data.`,
      'Delete UPS Unit',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = upsUnits.value.findIndex(u => u.id === ups.id)
    if (index !== -1) {
      upsUnits.value.splice(index, 1)
      ElMessage.success('UPS unit deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredUPS.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ups_units_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Export completed')
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

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
    }, 400)
  }, 2000)
})
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
.ups-room {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
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
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* UPS Grid */
.ups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.ups-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.ups-card.warning { border-left-color: #e6a23c; }
.ups-card.critical { border-left-color: #f56c6c; }
.ups-card.maintenance { border-left-color: #909399; }
.ups-card.normal { border-left-color: #67c23a; }

.ups-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.ups-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.ups-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.ups-info {
  flex: 1;
}

.ups-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.ups-model {
  font-size: 11px;
  color: #909399;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.normal { background: #e8f5e9; color: #67c23a; }
.status-badge.warning { background: #fff7e6; color: #e6a23c; }
.status-badge.critical { background: #ffefef; color: #f56c6c; }
.status-badge.maintenance { background: #f5f5f5; color: #909399; }

.ups-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.ups-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.metric-item {
  text-align: center;
}

.metric-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.metric-label {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

.ups-details {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 12px;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #303133;
  font-weight: 500;
}

.temp-high { color: #f56c6c; }
.temp-warning { color: #e6a23c; }
.temp-normal { color: #67c23a; }

.battery-section {
  margin-bottom: 16px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 12px;
}

.battery-title {
  font-size: 11px;
  font-weight: 600;
  color: #909399;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.battery-strings {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.battery-string {
  display: flex;
  align-items: center;
  gap: 10px;
}

.string-name {
  font-size: 11px;
  font-weight: 500;
  width: 70px;
}

.string-health {
  font-size: 11px;
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

.ups-alerts {
  background: #fff7e6;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 16px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #e6a23c;
  margin-bottom: 4px;
}

.alert-more {
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.ups-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
  margin-top: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

/* Detail Dialog */
.detail-batteries {
  margin-top: 20px;
}

.detail-batteries h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.detail-alerts {
  margin-top: 20px;
}

.detail-alerts h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .ups-room { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .ups-grid { grid-template-columns: 1fr; }
  .ups-metrics { grid-template-columns: repeat(2, 1fr); }
  .battery-string { flex-wrap: wrap; }
}
</style>