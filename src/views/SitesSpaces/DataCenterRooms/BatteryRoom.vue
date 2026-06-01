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
        <div class="loading-tip">Battery Room Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="battery-room">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Battery Room Management</h2>
        <p class="subtitle">Monitor and manage battery systems, strings, cells, and backup power health</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddBatteryDialog">
          <el-icon><Plus /></el-icon> Add Battery String
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
        <div class="stat-icon">🔋</div>
        <div class="stat-info">
          <div class="stat-value">{{ batteryStrings.length }}</div>
          <div class="stat-label">Battery Strings</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalBatteries }}</div>
          <div class="stat-label">Total Batteries</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgHealth }}%</div>
          <div class="stat-label">Avg Battery Health</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚠️</div>
        <div class="stat-info">
          <div class="stat-value">{{ criticalCount }}</div>
          <div class="stat-label">Critical Health</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by room name, string ID or location..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterStatus" placeholder="Health Status" clearable style="width: 160px">
          <el-option label="All Status" value="all" />
          <el-option label="Good (80-100%)" value="good" />
          <el-option label="Warning (60-79%)" value="warning" />
          <el-option label="Critical (<60%)" value="critical" />
        </el-select>
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 160px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
      </div>
    </div>

    <!-- Battery Strings Grid -->
    <div class="batteries-grid">
      <div v-for="battery in filteredBatteries" :key="battery.id" class="battery-card" :class="getHealthClass(battery.avgHealth)">
        <div class="battery-header">
          <div class="battery-icon">🔋</div>
          <div class="battery-info">
            <div class="battery-name">{{ battery.name }}</div>
            <div class="battery-id">{{ battery.stringId }}</div>
          </div>
          <div class="battery-status">
            <span class="health-badge" :class="getHealthClass(battery.avgHealth)">{{ getHealthText(battery.avgHealth) }}</span>
          </div>
        </div>

        <div class="battery-location">
          <el-icon><Location /></el-icon>
          <span>{{ battery.buildingName }} - {{ battery.roomName }}</span>
        </div>

        <!-- Key Metrics -->
        <div class="battery-metrics">
          <div class="metric-item">
            <div class="metric-value">{{ battery.batteryCount }}</div>
            <div class="metric-label">Batteries</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ battery.voltage }} V</div>
            <div class="metric-label">String Voltage</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ battery.capacity }} Ah</div>
            <div class="metric-label">Capacity</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ battery.temperature }}°C</div>
            <div class="metric-label">Temp</div>
          </div>
        </div>

        <!-- Health Progress -->
        <div class="health-section">
          <div class="health-label">Overall String Health</div>
          <el-progress :percentage="battery.avgHealth" :stroke-width="12" :color="getHealthColor(battery.avgHealth)" />
        </div>

        <!-- Cell Health Bars -->
        <div class="cells-preview">
          <div class="cells-title">Battery Cells Status</div>
          <div class="cells-bars">
            <div v-for="(cell, idx) in battery.cells.slice(0, 6)" :key="idx" class="cell-bar" :style="{ height: cell.health + '%', background: getHealthColor(cell.health) }" :title="`Cell ${idx + 1}: ${cell.health}%`"></div>
            <div v-if="battery.cells.length > 6" class="cell-more">+{{ battery.cells.length - 6 }}</div>
          </div>
        </div>

        <div class="battery-alerts" v-if="battery.alerts && battery.alerts.length > 0">
          <div v-for="alert in battery.alerts.slice(0, 2)" :key="alert.time" class="alert-item">
            <el-icon><Warning /></el-icon>
            <span>{{ alert.message }}</span>
          </div>
          <div v-if="battery.alerts.length > 2" class="alert-more">+{{ battery.alerts.length - 2 }} more alerts</div>
        </div>

        <div class="battery-actions">
          <el-button size="small" type="primary" plain @click="viewBattery(battery)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editBattery(battery)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteBattery(battery)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredBatteries.length === 0" class="empty-state">
      <div class="empty-icon">🔋</div>
      <div class="empty-title">No battery strings found</div>
      <div class="empty-desc">Add a battery string to start managing backup power systems</div>
      <el-button type="primary" @click="openAddBatteryDialog">Add Battery String</el-button>
    </div>

    <!-- Add/Edit Battery String Dialog -->
    <el-dialog v-model="showBatteryDialog" :title="dialogTitle" width="700px">
      <el-form :model="batteryForm" label-width="140px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="String Name" required>
              <el-input v-model="batteryForm.name" placeholder="e.g., UPS Battery String A" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="String ID">
              <el-input v-model="batteryForm.stringId" placeholder="e.g., BSTR-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="batteryForm.buildingId" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Room Name">
          <el-input v-model="batteryForm.roomName" placeholder="e.g., Battery Room A" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Battery Count">
              <el-input-number v-model="batteryForm.batteryCount" :min="0" :step="4" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="String Voltage (V)">
              <el-input-number v-model="batteryForm.voltage" :min="0" :step="12" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Capacity (Ah)">
              <el-input-number v-model="batteryForm.capacity" :min="0" :step="50" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Manufacturer">
              <el-input v-model="batteryForm.manufacturer" placeholder="e.g., EnerSys" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Battery Type">
              <el-select v-model="batteryForm.batteryType" style="width: 100%">
                <el-option label="VRLA" value="VRLA" />
                <el-option label="Lithium-Ion" value="Lithium-Ion" />
                <el-option label="Ni-Cd" value="Ni-Cd" />
                <el-option label="Flooded" value="Flooded" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Installation Date">
              <el-date-picker v-model="batteryForm.installationDate" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Warranty Expiry">
              <el-date-picker v-model="batteryForm.warrantyExpiry" type="date" placeholder="Select date" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="batteryForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBatteryDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveBattery">Save Battery String</el-button>
      </template>
    </el-dialog>

    <!-- Battery String Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedBattery?.name" width="800px">
      <div v-if="selectedBattery">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="String ID">{{ selectedBattery.stringId }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedBattery.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Room">{{ selectedBattery.roomName }}</el-descriptions-item>
          <el-descriptions-item label="Battery Type">{{ selectedBattery.batteryType }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedBattery.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ selectedBattery.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Warranty Expiry">{{ selectedBattery.warrantyExpiry }}</el-descriptions-item>
          <el-descriptions-item label="Last Test Date">{{ selectedBattery.lastTestDate }}</el-descriptions-item>
          <el-descriptions-item label="Next Test Due">{{ selectedBattery.nextTestDue }}</el-descriptions-item>
          <el-descriptions-item label="String Voltage">{{ selectedBattery.voltage }} V</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedBattery.capacity }} Ah</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedBattery.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Overall Health">{{ selectedBattery.avgHealth }}%</el-descriptions-item>
        </el-descriptions>

        <div class="detail-cells">
          <h4>Individual Battery Cells</h4>
          <el-table :data="selectedBattery.cells" stripe size="small">
            <el-table-column type="index" label="#" width="50" />
            <el-table-column prop="name" label="Cell Name" width="100" />
            <el-table-column label="Health" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
              </template>
            </el-table-column>
            <el-table-column prop="voltage" label="Voltage (V)" width="100" />
            <el-table-column prop="temperature" label="Temp (°C)" width="100" />
            <el-table-column prop="resistance" label="Resistance (mΩ)" width="120" />
            <el-table-column label="Status" width="100">
              <template #default="{ row }">
                <span :class="['cell-status', getHealthClass(row.health)]">{{ getCellStatusText(row.health) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="selectedBattery.alerts && selectedBattery.alerts.length > 0" class="detail-alerts">
          <h4>Active Alerts</h4>
          <el-table :data="selectedBattery.alerts" size="small">
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
        <el-button type="primary" @click="editBattery(selectedBattery); showDetailDialog = false">Edit</el-button>
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
  'Loading battery room data...',
  'Fetching battery string information...',
  'Checking battery cell health...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
}

// Battery Cell interface
interface BatteryCell {
  name: string
  health: number
  voltage: number
  temperature: number
  resistance: number
}

// Battery String interface
interface BatteryString {
  id: number
  name: string
  stringId: string
  buildingId: number
  buildingName: string
  roomName: string
  batteryCount: number
  voltage: number
  capacity: number
  temperature: number
  avgHealth: number
  batteryType: string
  manufacturer: string
  installationDate: string
  warrantyExpiry: string
  lastTestDate: string
  nextTestDue: string
  cells: BatteryCell[]
  alerts: { severity: string; message: string; time: string }[]
  description: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Data Center A' },
  { id: 2, name: 'Data Center B' }
])

// Sample battery strings data
const batteryStrings = ref<BatteryString[]>([
  {
    id: 1,
    name: 'UPS Battery String A',
    stringId: 'BSTR-UPS-A1',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Battery Room - Floor 1',
    batteryCount: 40,
    voltage: 432,
    capacity: 150,
    temperature: 26.5,
    avgHealth: 94,
    batteryType: 'VRLA',
    manufacturer: 'EnerSys',
    installationDate: '2023-06-15',
    warrantyExpiry: '2028-06-15',
    lastTestDate: '2025-01-10',
    nextTestDue: '2025-04-10',
    cells: [
      { name: 'Cell 01', health: 96, voltage: 12.8, temperature: 26, resistance: 4.2 },
      { name: 'Cell 02', health: 95, voltage: 12.7, temperature: 26, resistance: 4.3 },
      { name: 'Cell 03', health: 94, voltage: 12.7, temperature: 27, resistance: 4.4 },
      { name: 'Cell 04', health: 93, voltage: 12.6, temperature: 27, resistance: 4.5 },
      { name: 'Cell 05', health: 92, voltage: 12.6, temperature: 27, resistance: 4.6 }
    ],
    alerts: [],
    description: 'Main UPS battery string for Data Hall A'
  },
  {
    id: 2,
    name: 'UPS Battery String B',
    stringId: 'BSTR-UPS-B1',
    buildingId: 1,
    buildingName: 'Data Center A',
    roomName: 'Battery Room - Floor 1',
    batteryCount: 40,
    voltage: 428,
    capacity: 150,
    temperature: 27.8,
    avgHealth: 82,
    batteryType: 'VRLA',
    manufacturer: 'EnerSys',
    installationDate: '2023-06-15',
    warrantyExpiry: '2028-06-15',
    lastTestDate: '2025-01-10',
    nextTestDue: '2025-04-10',
    cells: [
      { name: 'Cell 01', health: 85, voltage: 12.4, temperature: 28, resistance: 5.2 },
      { name: 'Cell 02', health: 84, voltage: 12.3, temperature: 28, resistance: 5.3 },
      { name: 'Cell 03', health: 82, voltage: 12.2, temperature: 28, resistance: 5.5 },
      { name: 'Cell 04', health: 80, voltage: 12.1, temperature: 29, resistance: 5.8 },
      { name: 'Cell 05', health: 79, voltage: 12.0, temperature: 29, resistance: 6.0 }
    ],
    alerts: [
      { severity: 'warning', message: 'Battery cells showing degradation', time: '2025-01-15 10:30:00' }
    ],
    description: 'Redundant UPS battery string - schedule maintenance'
  },
  {
    id: 3,
    name: 'Emergency Lighting Battery',
    stringId: 'BSTR-EMG-L1',
    buildingId: 2,
    buildingName: 'Data Center B',
    roomName: 'Battery Room - Floor 2',
    batteryCount: 24,
    voltage: 216,
    capacity: 75,
    temperature: 25.2,
    avgHealth: 96,
    batteryType: 'Lithium-Ion',
    manufacturer: 'Tesla',
    installationDate: '2024-02-10',
    warrantyExpiry: '2034-02-10',
    lastTestDate: '2025-01-12',
    nextTestDue: '2025-04-12',
    cells: [
      { name: 'Module 1', health: 97, voltage: 54.2, temperature: 25, resistance: 2.1 },
      { name: 'Module 2', health: 96, voltage: 54.0, temperature: 25, resistance: 2.2 },
      { name: 'Module 3', health: 95, voltage: 53.8, temperature: 26, resistance: 2.3 },
      { name: 'Module 4', health: 96, voltage: 54.1, temperature: 25, resistance: 2.2 }
    ],
    alerts: [],
    description: 'Emergency lighting backup system'
  },
  {
    id: 4,
    name: 'Critical Load Battery',
    stringId: 'BSTR-CRIT-C1',
    buildingId: 2,
    buildingName: 'Data Center B',
    roomName: 'Battery Room - Floor 1',
    batteryCount: 32,
    voltage: 384,
    capacity: 200,
    temperature: 29.5,
    avgHealth: 58,
    batteryType: 'VRLA',
    manufacturer: 'C&D Technologies',
    installationDate: '2021-03-20',
    warrantyExpiry: '2026-03-20',
    lastTestDate: '2024-12-15',
    nextTestDue: '2025-03-15',
    cells: [
      { name: 'Cell 01', health: 62, voltage: 11.8, temperature: 30, resistance: 7.2 },
      { name: 'Cell 02', health: 58, voltage: 11.5, temperature: 31, resistance: 7.8 },
      { name: 'Cell 03', health: 55, voltage: 11.2, temperature: 31, resistance: 8.2 },
      { name: 'Cell 04', health: 52, voltage: 11.0, temperature: 32, resistance: 8.5 }
    ],
    alerts: [
      { severity: 'critical', message: 'Battery health critically low - replacement required', time: '2025-01-14 14:00:00' },
      { severity: 'warning', message: 'High temperature detected', time: '2025-01-14 13:45:00' }
    ],
    description: 'Critical load UPS battery - urgent replacement needed'
  }
])

// UI State
const searchText = ref('')
const filterStatus = ref('all')
const filterBuilding = ref('all')
const showBatteryDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedBattery = ref<BatteryString | null>(null)

const batteryForm = ref({
  name: '',
  stringId: '',
  buildingId: 1,
  roomName: '',
  batteryCount: 0,
  voltage: 0,
  capacity: 0,
  manufacturer: '',
  batteryType: 'VRLA',
  installationDate: null,
  warrantyExpiry: null,
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Battery String' : 'Add Battery String')

const totalBatteries = computed(() => batteryStrings.value.reduce((sum, b) => sum + b.batteryCount, 0))
const avgHealth = computed(() => Math.round(batteryStrings.value.reduce((sum, b) => sum + b.avgHealth, 0) / batteryStrings.value.length))
const criticalCount = computed(() => batteryStrings.value.filter(b => b.avgHealth < 60).length)

const uniqueBuildings = computed(() => {
  return Array.from(new Set(batteryStrings.value.map(b => b.buildingName)))
})

const filteredBatteries = computed(() => {
  let filtered = [...batteryStrings.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(b =>
        b.name.toLowerCase().includes(keyword) ||
        b.stringId.toLowerCase().includes(keyword) ||
        b.roomName.toLowerCase().includes(keyword)
    )
  }

  if (filterStatus.value !== 'all') {
    if (filterStatus.value === 'good') filtered = filtered.filter(b => b.avgHealth >= 80)
    else if (filterStatus.value === 'warning') filtered = filtered.filter(b => b.avgHealth >= 60 && b.avgHealth < 80)
    else if (filterStatus.value === 'critical') filtered = filtered.filter(b => b.avgHealth < 60)
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(b => b.buildingName === filterBuilding.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getHealthClass = (health: number) => {
  if (health >= 80) return 'good'
  if (health >= 60) return 'warning'
  return 'critical'
}

const getHealthText = (health: number) => {
  if (health >= 80) return 'Good'
  if (health >= 60) return 'Warning'
  return 'Critical'
}

const getHealthColor = (health: number) => {
  if (health >= 80) return '#67c23a'
  if (health >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getCellStatusText = (health: number) => {
  if (health >= 80) return 'Normal'
  if (health >= 60) return 'Degraded'
  return 'Critical'
}

// Battery CRUD operations
const openAddBatteryDialog = () => {
  isEditing.value = false
  batteryForm.value = {
    name: '',
    stringId: '',
    buildingId: buildings.value[0]?.id || 1,
    roomName: '',
    batteryCount: 0,
    voltage: 0,
    capacity: 0,
    manufacturer: '',
    batteryType: 'VRLA',
    installationDate: null,
    warrantyExpiry: null,
    description: ''
  }
  showBatteryDialog.value = true
}

const editBattery = (battery: BatteryString) => {
  isEditing.value = true
  selectedBattery.value = battery
  batteryForm.value = {
    name: battery.name,
    stringId: battery.stringId,
    buildingId: battery.buildingId,
    roomName: battery.roomName,
    batteryCount: battery.batteryCount,
    voltage: battery.voltage,
    capacity: battery.capacity,
    manufacturer: battery.manufacturer,
    batteryType: battery.batteryType,
    installationDate: battery.installationDate,
    warrantyExpiry: battery.warrantyExpiry,
    description: battery.description || ''
  }
  showBatteryDialog.value = true
}

const saveBattery = () => {
  if (!batteryForm.value.name.trim()) {
    ElMessage.warning('Please enter battery string name')
    return
  }

  const building = buildings.value.find(b => b.id === batteryForm.value.buildingId)

  if (!building) {
    ElMessage.warning('Please select a building')
    return
  }

  if (isEditing.value && selectedBattery.value) {
    const index = batteryStrings.value.findIndex(b => b.id === selectedBattery.value!.id)
    if (index !== -1) {
      batteryStrings.value[index] = {
        ...batteryStrings.value[index],
        name: batteryForm.value.name,
        stringId: batteryForm.value.stringId,
        buildingId: batteryForm.value.buildingId,
        buildingName: building.name,
        roomName: batteryForm.value.roomName,
        batteryCount: batteryForm.value.batteryCount,
        voltage: batteryForm.value.voltage,
        capacity: batteryForm.value.capacity,
        manufacturer: batteryForm.value.manufacturer,
        batteryType: batteryForm.value.batteryType,
        installationDate: batteryForm.value.installationDate as string,
        warrantyExpiry: batteryForm.value.warrantyExpiry as string,
        description: batteryForm.value.description
      }
      ElMessage.success('Battery string updated successfully')
    }
  } else {
    const newBattery: BatteryString = {
      id: Date.now(),
      name: batteryForm.value.name,
      stringId: batteryForm.value.stringId || `BSTR-${batteryStrings.value.length + 1}`,
      buildingId: batteryForm.value.buildingId,
      buildingName: building.name,
      roomName: batteryForm.value.roomName,
      batteryCount: batteryForm.value.batteryCount,
      voltage: batteryForm.value.voltage,
      capacity: batteryForm.value.capacity,
      temperature: 25,
      avgHealth: 100,
      batteryType: batteryForm.value.batteryType,
      manufacturer: batteryForm.value.manufacturer,
      installationDate: batteryForm.value.installationDate as string || new Date().toISOString().split('T')[0],
      warrantyExpiry: batteryForm.value.warrantyExpiry as string || '',
      lastTestDate: new Date().toISOString().split('T')[0],
      nextTestDue: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
      cells: [],
      alerts: [],
      description: batteryForm.value.description
    }
    batteryStrings.value.push(newBattery)
    ElMessage.success('Battery string added successfully')
  }

  showBatteryDialog.value = false
}

const viewBattery = (battery: BatteryString) => {
  selectedBattery.value = battery
  showDetailDialog.value = true
}

const deleteBattery = (battery: BatteryString) => {
  ElMessageBox.confirm(
      `Delete battery string "${battery.name}"? This will remove all battery cell data.`,
      'Delete Battery String',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = batteryStrings.value.findIndex(b => b.id === battery.id)
    if (index !== -1) {
      batteryStrings.value.splice(index, 1)
      ElMessage.success('Battery string deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredBatteries.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `battery_strings_${new Date().toISOString().split('T')[0]}.json`
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
.battery-room {
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

/* Batteries Grid */
.batteries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.battery-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.battery-card.good { border-left-color: #67c23a; }
.battery-card.warning { border-left-color: #e6a23c; }
.battery-card.critical { border-left-color: #f56c6c; }

.battery-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.battery-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.battery-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #10b981, #059669);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.battery-info {
  flex: 1;
}

.battery-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.battery-id {
  font-size: 11px;
  color: #909399;
}

.health-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.health-badge.good { background: #e8f5e9; color: #67c23a; }
.health-badge.warning { background: #fff7e6; color: #e6a23c; }
.health-badge.critical { background: #ffefef; color: #f56c6c; }

.battery-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.battery-metrics {
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

.health-section {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.health-label {
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
}

.cells-preview {
  margin-bottom: 16px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 12px;
}

.cells-title {
  font-size: 11px;
  font-weight: 600;
  color: #909399;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.cells-bars {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 50px;
}

.cell-bar {
  flex: 1;
  min-width: 20px;
  border-radius: 4px 4px 0 0;
  transition: height 0.2s;
}

.cell-more {
  font-size: 11px;
  color: #909399;
  padding-left: 6px;
}

.battery-alerts {
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

.battery-actions {
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

/* Detail Dialogs */
.detail-cells {
  margin-top: 20px;
}

.detail-cells h4 {
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

.cell-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.cell-status.good { background: #e8f5e9; color: #67c23a; }
.cell-status.warning { background: #fff7e6; color: #e6a23c; }
.cell-status.critical { background: #ffefef; color: #f56c6c; }

:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .battery-room { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .batteries-grid { grid-template-columns: 1fr; }
  .battery-metrics { grid-template-columns: repeat(2, 1fr); }
  .cells-bars { height: 40px; }
  .cell-bar { min-width: 15px; }
}
</style>