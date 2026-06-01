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
        <div class="loading-tip">Data Hall Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="data-hall">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Data Hall Management</h2>
        <p class="subtitle">Monitor and manage data center halls, racks, power, and cooling infrastructure</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddHallDialog">
          <el-icon><Plus /></el-icon> Add Data Hall
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
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <div class="stat-value">{{ dataHalls.length }}</div>
          <div class="stat-label">Total Data Halls</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalRacks }}</div>
          <div class="stat-label">Total Racks</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">⚡</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalPowerCapacity }} kW</div>
          <div class="stat-label">Total Power Capacity</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">❄️</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCoolingCapacity }} kW</div>
          <div class="stat-label">Total Cooling Capacity</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by hall name or location..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Operational" value="operational" />
          <el-option label="Maintenance" value="maintenance" />
          <el-option label="Planned" value="planned" />
        </el-select>
      </div>
    </div>

    <!-- Data Halls Grid -->
    <div class="halls-grid">
      <div v-for="hall in filteredHalls" :key="hall.id" class="hall-card" :class="hall.status">
        <div class="hall-header">
          <div class="hall-icon">🏢</div>
          <div class="hall-info">
            <div class="hall-name">{{ hall.name }}</div>
            <div class="hall-code">{{ hall.code }}</div>
          </div>
          <div class="hall-status">
            <span class="status-badge" :class="hall.status">{{ getStatusText(hall.status) }}</span>
          </div>
        </div>

        <div class="hall-location">
          <el-icon><Location /></el-icon>
          <span>{{ hall.buildingName }} - {{ hall.location }}</span>
        </div>

        <!-- Key Metrics -->
        <div class="hall-metrics">
          <div class="metric-item">
            <div class="metric-value">{{ hall.rackCount }}</div>
            <div class="metric-label">Racks</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ hall.powerCapacity }} kW</div>
            <div class="metric-label">Power</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ hall.coolingCapacity }} kW</div>
            <div class="metric-label">Cooling</div>
          </div>
          <div class="metric-item">
            <div class="metric-value">{{ hall.avgTemp }}°C</div>
            <div class="metric-label">Avg Temp</div>
          </div>
        </div>

        <!-- Power & Cooling Utilization -->
        <div class="utilization-section">
          <div class="utilization-item">
            <span class="util-label">Power Utilization</span>
            <el-progress :percentage="hall.powerUtilization" :stroke-width="8" :color="getUtilizationColor(hall.powerUtilization)" />
            <span class="util-value">{{ hall.powerUtilization }}%</span>
          </div>
          <div class="utilization-item">
            <span class="util-label">Cooling Utilization</span>
            <el-progress :percentage="hall.coolingUtilization" :stroke-width="8" :color="getUtilizationColor(hall.coolingUtilization)" />
            <span class="util-value">{{ hall.coolingUtilization }}%</span>
          </div>
        </div>

        <div class="hall-footer">
          <div class="hall-pue">
            <span class="pue-label">PUE:</span>
            <span class="pue-value" :class="getPUEClass(hall.pue)">{{ hall.pue }}</span>
          </div>
          <div class="hall-actions">
            <el-button size="small" type="primary" plain @click="viewHall(hall)">
              <el-icon><View /></el-icon> View
            </el-button>
            <el-button size="small" type="info" plain @click="editHall(hall)">
              <el-icon><Edit /></el-icon> Edit
            </el-button>
            <el-button size="small" type="danger" plain @click="deleteHall(hall)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredHalls.length === 0" class="empty-state">
      <div class="empty-icon">🏢</div>
      <div class="empty-title">No data halls found</div>
      <div class="empty-desc">Add a data hall to start managing your data center infrastructure</div>
      <el-button type="primary" @click="openAddHallDialog">Add Data Hall</el-button>
    </div>

    <!-- Add/Edit Data Hall Dialog -->
    <el-dialog v-model="showHallDialog" :title="dialogTitle" width="650px">
      <el-form :model="hallForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Hall Name" required>
              <el-input v-model="hallForm.name" placeholder="e.g., Data Hall A" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Hall Code">
              <el-input v-model="hallForm.code" placeholder="e.g., DH-A-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="hallForm.buildingId" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="hallForm.location" placeholder="e.g., Floor 1, East Wing" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Rack Count">
              <el-input-number v-model="hallForm.rackCount" :min="0" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Power Capacity (kW)">
              <el-input-number v-model="hallForm.powerCapacity" :min="0" :step="50" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Cooling Capacity (kW)">
              <el-input-number v-model="hallForm.coolingCapacity" :min="0" :step="50" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Area (sqm)">
              <el-input-number v-model="hallForm.area" :min="0" :step="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Tier Level">
              <el-select v-model="hallForm.tierLevel" style="width: 100%">
                <el-option label="Tier I" value="Tier I" />
                <el-option label="Tier II" value="Tier II" />
                <el-option label="Tier III" value="Tier III" />
                <el-option label="Tier IV" value="Tier IV" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="hallForm.status">
            <el-radio label="operational">Operational</el-radio>
            <el-radio label="maintenance">Maintenance</el-radio>
            <el-radio label="planned">Planned</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="hallForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHallDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveHall">Save Hall</el-button>
      </template>
    </el-dialog>

    <!-- Data Hall Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedHall?.name" width="750px">
      <div v-if="selectedHall">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Hall ID">{{ selectedHall.id }}</el-descriptions-item>
          <el-descriptions-item label="Hall Code">{{ selectedHall.code }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedHall.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedHall.location }}</el-descriptions-item>
          <el-descriptions-item label="Tier Level">{{ selectedHall.tierLevel }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedHall.status]">{{ getStatusText(selectedHall.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Area">{{ formatNumber(selectedHall.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Rack Count">{{ selectedHall.rackCount }}</el-descriptions-item>
          <el-descriptions-item label="Power Capacity">{{ selectedHall.powerCapacity }} kW</el-descriptions-item>
          <el-descriptions-item label="Power Utilization">{{ selectedHall.powerUtilization }}%</el-descriptions-item>
          <el-descriptions-item label="Cooling Capacity">{{ selectedHall.coolingCapacity }} kW</el-descriptions-item>
          <el-descriptions-item label="Cooling Utilization">{{ selectedHall.coolingUtilization }}%</el-descriptions-item>
          <el-descriptions-item label="Average Temperature">{{ selectedHall.avgTemp }}°C</el-descriptions-item>
          <el-descriptions-item label="Average Humidity">{{ selectedHall.avgHumidity }}%</el-descriptions-item>
          <el-descriptions-item label="PUE">{{ selectedHall.pue }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedHall.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editHall(selectedHall); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading data hall information...',
  'Fetching infrastructure data...',
  'Calculating utilization metrics...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
}

// Data Hall interface
interface DataHall {
  id: number
  name: string
  code: string
  buildingId: number
  buildingName: string
  location: string
  rackCount: number
  powerCapacity: number
  powerUsed: number
  powerUtilization: number
  coolingCapacity: number
  coolingUsed: number
  coolingUtilization: number
  area: number
  avgTemp: number
  avgHumidity: number
  pue: number
  tierLevel: string
  status: string
  description: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Data Center A' },
  { id: 2, name: 'Data Center B' }
])

// Sample data halls data
const dataHalls = ref<DataHall[]>([
  {
    id: 1,
    name: 'Data Hall A1',
    code: 'DH-A1',
    buildingId: 1,
    buildingName: 'Data Center A',
    location: 'Floor 1, East Wing',
    rackCount: 48,
    powerCapacity: 500,
    powerUsed: 380,
    powerUtilization: 76,
    coolingCapacity: 450,
    coolingUsed: 340,
    coolingUtilization: 75.6,
    area: 320,
    avgTemp: 22.5,
    avgHumidity: 48,
    pue: 1.48,
    tierLevel: 'Tier III',
    status: 'operational',
    description: 'Primary production data hall with N+1 redundancy'
  },
  {
    id: 2,
    name: 'Data Hall A2',
    code: 'DH-A2',
    buildingId: 1,
    buildingName: 'Data Center A',
    location: 'Floor 2, West Wing',
    rackCount: 52,
    powerCapacity: 600,
    powerUsed: 520,
    powerUtilization: 86.7,
    coolingCapacity: 550,
    coolingUsed: 490,
    coolingUtilization: 89.1,
    area: 380,
    avgTemp: 23.2,
    avgHumidity: 46,
    pue: 1.52,
    tierLevel: 'Tier III',
    status: 'operational',
    description: 'High-density compute zone - nearing capacity'
  },
  {
    id: 3,
    name: 'Data Hall B1',
    code: 'DH-B1',
    buildingId: 2,
    buildingName: 'Data Center B',
    location: 'Floor 1, North Wing',
    rackCount: 36,
    powerCapacity: 400,
    powerUsed: 280,
    powerUtilization: 70,
    coolingCapacity: 380,
    coolingUsed: 260,
    coolingUtilization: 68.4,
    area: 280,
    avgTemp: 22.0,
    avgHumidity: 47,
    pue: 1.44,
    tierLevel: 'Tier III',
    status: 'operational',
    description: 'Cloud services zone'
  },
  {
    id: 4,
    name: 'Data Hall B2',
    code: 'DH-B2',
    buildingId: 2,
    buildingName: 'Data Center B',
    location: 'Floor 2, South Wing',
    rackCount: 24,
    powerCapacity: 300,
    powerUsed: 180,
    powerUtilization: 60,
    coolingCapacity: 280,
    coolingUsed: 160,
    coolingUtilization: 57.1,
    area: 220,
    avgTemp: 21.8,
    avgHumidity: 48,
    pue: 1.42,
    tierLevel: 'Tier III',
    status: 'maintenance',
    description: 'Under cooling system upgrade'
  },
  {
    id: 5,
    name: 'Data Hall C1',
    code: 'DH-C1',
    buildingId: 1,
    buildingName: 'Data Center A',
    location: 'Floor 3, South Wing',
    rackCount: 60,
    powerCapacity: 800,
    powerUsed: 620,
    powerUtilization: 77.5,
    coolingCapacity: 720,
    coolingUsed: 560,
    coolingUtilization: 77.8,
    area: 450,
    avgTemp: 22.8,
    avgHumidity: 47,
    pue: 1.46,
    tierLevel: 'Tier IV',
    status: 'planned',
    description: 'Future expansion data hall - planned Q2 2025'
  }
])

// UI State
const searchText = ref('')
const filterStatus = ref('all')
const showHallDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedHall = ref<DataHall | null>(null)

const hallForm = ref({
  name: '',
  code: '',
  buildingId: 1,
  location: '',
  rackCount: 0,
  powerCapacity: 0,
  coolingCapacity: 0,
  area: 0,
  tierLevel: 'Tier III',
  status: 'operational',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Data Hall' : 'Add Data Hall')

const totalRacks = computed(() => dataHalls.value.reduce((sum, h) => sum + h.rackCount, 0))
const totalPowerCapacity = computed(() => dataHalls.value.reduce((sum, h) => sum + h.powerCapacity, 0))
const totalCoolingCapacity = computed(() => dataHalls.value.reduce((sum, h) => sum + h.coolingCapacity, 0))

const filteredHalls = computed(() => {
  let filtered = [...dataHalls.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(h =>
        h.name.toLowerCase().includes(keyword) ||
        h.code.toLowerCase().includes(keyword) ||
        h.location.toLowerCase().includes(keyword)
    )
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(h => h.status === filterStatus.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    operational: 'Operational',
    maintenance: 'Maintenance',
    planned: 'Planned'
  }
  return map[status] || status
}

const getUtilizationColor = (percentage: number) => {
  if (percentage >= 85) return '#f56c6c'
  if (percentage >= 70) return '#e6a23c'
  return '#67c23a'
}

const getPUEClass = (pue: number) => {
  if (pue >= 1.5) return 'pue-high'
  if (pue >= 1.4) return 'pue-medium'
  return 'pue-good'
}

// Data Hall CRUD operations
const openAddHallDialog = () => {
  isEditing.value = false
  hallForm.value = {
    name: '',
    code: '',
    buildingId: buildings.value[0]?.id || 1,
    location: '',
    rackCount: 0,
    powerCapacity: 0,
    coolingCapacity: 0,
    area: 0,
    tierLevel: 'Tier III',
    status: 'operational',
    description: ''
  }
  showHallDialog.value = true
}

const editHall = (hall: DataHall) => {
  isEditing.value = true
  selectedHall.value = hall
  hallForm.value = {
    name: hall.name,
    code: hall.code,
    buildingId: hall.buildingId,
    location: hall.location,
    rackCount: hall.rackCount,
    powerCapacity: hall.powerCapacity,
    coolingCapacity: hall.coolingCapacity,
    area: hall.area,
    tierLevel: hall.tierLevel,
    status: hall.status,
    description: hall.description || ''
  }
  showHallDialog.value = true
}

const saveHall = () => {
  if (!hallForm.value.name.trim()) {
    ElMessage.warning('Please enter data hall name')
    return
  }

  const building = buildings.value.find(b => b.id === hallForm.value.buildingId)

  if (!building) {
    ElMessage.warning('Please select a building')
    return
  }

  if (isEditing.value && selectedHall.value) {
    const index = dataHalls.value.findIndex(h => h.id === selectedHall.value!.id)
    if (index !== -1) {
      dataHalls.value[index] = {
        ...dataHalls.value[index],
        name: hallForm.value.name,
        code: hallForm.value.code,
        buildingId: hallForm.value.buildingId,
        buildingName: building.name,
        location: hallForm.value.location,
        rackCount: hallForm.value.rackCount,
        powerCapacity: hallForm.value.powerCapacity,
        coolingCapacity: hallForm.value.coolingCapacity,
        area: hallForm.value.area,
        tierLevel: hallForm.value.tierLevel,
        status: hallForm.value.status,
        description: hallForm.value.description
      }
      ElMessage.success('Data hall updated successfully')
    }
  } else {
    const newHall: DataHall = {
      id: Date.now(),
      name: hallForm.value.name,
      code: hallForm.value.code || `DH-${dataHalls.value.length + 1}`,
      buildingId: hallForm.value.buildingId,
      buildingName: building.name,
      location: hallForm.value.location,
      rackCount: hallForm.value.rackCount,
      powerCapacity: hallForm.value.powerCapacity,
      powerUsed: 0,
      powerUtilization: 0,
      coolingCapacity: hallForm.value.coolingCapacity,
      coolingUsed: 0,
      coolingUtilization: 0,
      area: hallForm.value.area,
      avgTemp: 22,
      avgHumidity: 45,
      pue: 1.45,
      tierLevel: hallForm.value.tierLevel,
      status: hallForm.value.status,
      description: hallForm.value.description
    }
    dataHalls.value.push(newHall)
    ElMessage.success('Data hall added successfully')
  }

  showHallDialog.value = false
}

const viewHall = (hall: DataHall) => {
  selectedHall.value = hall
  showDetailDialog.value = true
}

const deleteHall = (hall: DataHall) => {
  ElMessageBox.confirm(
      `Delete data hall "${hall.name}"? This will also remove all associated rack data.`,
      'Delete Data Hall',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = dataHalls.value.findIndex(h => h.id === hall.id)
    if (index !== -1) {
      dataHalls.value.splice(index, 1)
      ElMessage.success('Data hall deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredHalls.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `data_halls_${new Date().toISOString().split('T')[0]}.json`
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
.data-hall {
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

/* Halls Grid */
.halls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.hall-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.hall-card.maintenance { border-left-color: #e6a23c; }
.hall-card.planned { border-left-color: #909399; }
.hall-card.operational { border-left-color: #67c23a; }

.hall-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.hall-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.hall-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.hall-info {
  flex: 1;
}

.hall-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.hall-code {
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

.status-badge.operational { background: #e8f5e9; color: #67c23a; }
.status-badge.maintenance { background: #fff7e6; color: #e6a23c; }
.status-badge.planned { background: #f5f5f5; color: #909399; }

.hall-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.hall-metrics {
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

.utilization-section {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.utilization-item {
  margin-bottom: 8px;
}

.util-item:last-child {
  margin-bottom: 0;
}

.util-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.util-value {
  font-size: 11px;
  font-weight: 500;
  margin-left: 8px;
}

.hall-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.hall-pue {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f8f9fa;
  border-radius: 20px;
}

.pue-label {
  font-size: 11px;
  color: #909399;
}

.pue-value {
  font-size: 14px;
  font-weight: 700;
}

.pue-value.pue-good { color: #67c23a; }
.pue-value.pue-medium { color: #e6a23c; }
.pue-value.pue-high { color: #f56c6c; }

.hall-actions {
  display: flex;
  gap: 8px;
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

/* Dialog */
:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .data-hall { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .halls-grid { grid-template-columns: 1fr; }
  .hall-metrics { grid-template-columns: repeat(2, 1fr); }
  .hall-footer { flex-direction: column; align-items: flex-start; }
}
</style>