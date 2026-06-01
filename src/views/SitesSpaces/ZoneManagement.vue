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
        <div class="loading-tip">Zone Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="zone-management">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Zone Management</h2>
        <p class="subtitle">Manage building zones, functional areas, and zone-specific configurations</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddZoneDialog">
          <el-icon><Plus /></el-icon> Add Zone
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
        <div class="stat-icon">🗺️</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalZones }}</div>
          <div class="stat-label">Total Zones</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📐</div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(totalArea) }}</div>
          <div class="stat-label">Total Area (sqm)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-info">
          <div class="stat-value">{{ activeZones }}</div>
          <div class="stat-label">Active Zones</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgOccupancy }}%</div>
          <div class="stat-label">Avg Occupancy</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by zone name, code or type..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 180px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
        <el-select v-model="filterType" placeholder="Zone Type" clearable style="width: 160px">
          <el-option label="All Types" value="all" />
          <el-option label="Office" value="office" />
          <el-option label="Meeting" value="meeting" />
          <el-option label="Break Area" value="break" />
          <el-option label="Server Room" value="server" />
          <el-option label="Storage" value="storage" />
          <el-option label="Production" value="production" />
          <el-option label="Retail" value="retail" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 130px">
          <el-option label="All Status" value="all" />
          <el-option label="Active" value="active" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
      </div>
    </div>

    <!-- Zones Grid -->
    <div class="zones-grid">
      <div v-for="zone in filteredZones" :key="zone.id" class="zone-card" :class="zone.type">
        <div class="zone-header">
          <div class="zone-icon">{{ getZoneIcon(zone.type) }}</div>
          <div class="zone-info">
            <div class="zone-name">{{ zone.name }}</div>
            <div class="zone-code">{{ zone.code }}</div>
          </div>
          <div class="zone-status">
            <span class="status-badge" :class="zone.status">{{ zone.status === 'active' ? 'Active' : 'Inactive' }}</span>
          </div>
        </div>

        <div class="zone-location">
          <el-icon><Location /></el-icon>
          <span>{{ zone.buildingName }} - Floor {{ zone.floorLevel }} ({{ zone.floorCode }})</span>
        </div>

        <div class="zone-details">
          <div class="detail-row">
            <span class="detail-label">Area</span>
            <span class="detail-value">{{ formatNumber(zone.area) }} sqm</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Type</span>
            <span class="detail-value">{{ getTypeLabel(zone.type) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Devices</span>
            <span class="detail-value">{{ zone.devices }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Sensors</span>
            <span class="detail-value">{{ zone.sensors }}</span>
          </div>
        </div>

        <div class="zone-stats">
          <div class="stat-item">
            <span class="stat-number">{{ zone.occupancy }}%</span>
            <span class="stat-label-sm">Occupancy</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ zone.temp }}°C</span>
            <span class="stat-label-sm">Temperature</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ zone.humidity }}%</span>
            <span class="stat-label-sm">Humidity</span>
          </div>
        </div>

        <div class="zone-actions">
          <el-button size="small" type="primary" plain @click="viewZone(zone)">
            <el-icon><View /></el-icon> View
          </el-button>
          <el-button size="small" type="info" plain @click="editZone(zone)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteZone(zone)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredZones.length === 0" class="empty-state">
      <div class="empty-icon">🗺️</div>
      <div class="empty-title">No zones found</div>
      <div class="empty-desc">Add a zone to start managing functional areas</div>
      <el-button type="primary" @click="openAddZoneDialog">Add Zone</el-button>
    </div>

    <!-- Add/Edit Zone Dialog -->
    <el-dialog v-model="showZoneDialog" :title="dialogTitle" width="600px">
      <el-form :model="zoneForm" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Zone Name" required>
              <el-input v-model="zoneForm.name" placeholder="Enter zone name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Zone Code">
              <el-input v-model="zoneForm.code" placeholder="e.g., ZN-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="zoneForm.buildingId" placeholder="Select building" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Floor" required>
          <el-select v-model="zoneForm.floorId" placeholder="Select floor" style="width: 100%" :disabled="!zoneForm.buildingId">
            <el-option v-for="f in availableFloors" :key="f.id" :label="`Floor ${f.level} - ${f.code}`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Zone Type">
              <el-select v-model="zoneForm.type" style="width: 100%">
                <el-option label="Office" value="office" />
                <el-option label="Meeting Room" value="meeting" />
                <el-option label="Break Area" value="break" />
                <el-option label="Server Room" value="server" />
                <el-option label="Storage" value="storage" />
                <el-option label="Production" value="production" />
                <el-option label="Retail" value="retail" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Area (sqm)">
              <el-input-number v-model="zoneForm.area" :min="0" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Temperature Setpoint">
              <el-input-number v-model="zoneForm.tempSetpoint" :min="18" :max="26" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Humidity Setpoint">
              <el-input-number v-model="zoneForm.humiditySetpoint" :min="30" :max="70" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="zoneForm.status">
            <el-radio label="active">Active</el-radio>
            <el-radio label="inactive">Inactive</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="zoneForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showZoneDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveZone">Save Zone</el-button>
      </template>
    </el-dialog>

    <!-- Zone Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedZone?.name" width="700px">
      <div v-if="selectedZone">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Zone ID">{{ selectedZone.id }}</el-descriptions-item>
          <el-descriptions-item label="Zone Code">{{ selectedZone.code }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedZone.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Floor">Floor {{ selectedZone.floorLevel }} ({{ selectedZone.floorCode }})</el-descriptions-item>
          <el-descriptions-item label="Type">{{ getTypeLabel(selectedZone.type) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedZone.status]">{{ selectedZone.status === 'active' ? 'Active' : 'Inactive' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Area">{{ formatNumber(selectedZone.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Occupancy">{{ selectedZone.occupancy }}%</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedZone.temp }}°C</el-descriptions-item>
          <el-descriptions-item label="Humidity">{{ selectedZone.humidity }}%</el-descriptions-item>
          <el-descriptions-item label="Active Devices">{{ selectedZone.devices }}</el-descriptions-item>
          <el-descriptions-item label="Connected Sensors">{{ selectedZone.sensors }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedZone.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editZone(selectedZone); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading zone data...',
  'Fetching building information...',
  'Organizing zones by type...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
}

// Floor interface
interface Floor {
  id: number
  buildingId: number
  level: number
  code: string
}

// Zone interface
interface Zone {
  id: number
  name: string
  code: string
  buildingId: number
  buildingName: string
  floorId: number
  floorLevel: number
  floorCode: string
  type: string
  area: number
  devices: number
  sensors: number
  occupancy: number
  temp: number
  humidity: number
  status: string
  description: string
  tempSetpoint: number
  humiditySetpoint: number
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Marina Bay Tower' },
  { id: 2, name: 'Central Plaza' },
  { id: 3, name: 'Tech Park North' }
])

// Sample floors data
const floors = ref<Floor[]>([
  { id: 1, buildingId: 1, level: 1, code: 'L1' },
  { id: 2, buildingId: 1, level: 2, code: 'L2' },
  { id: 3, buildingId: 1, level: 3, code: 'L3' },
  { id: 4, buildingId: 2, level: 1, code: 'G' },
  { id: 5, buildingId: 2, level: 2, code: '2F' },
  { id: 6, buildingId: 2, level: 3, code: '3F' },
  { id: 7, buildingId: 3, level: 1, code: '01' },
  { id: 8, buildingId: 3, level: 2, code: '02' }
])

// Sample zones data
const zones = ref<Zone[]>([
  {
    id: 1,
    name: 'Executive Office North',
    code: 'EO-N-01',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    type: 'office',
    area: 120,
    devices: 8,
    sensors: 12,
    occupancy: 85,
    temp: 22.5,
    humidity: 48,
    status: 'active',
    description: 'Executive offices with city view',
    tempSetpoint: 22,
    humiditySetpoint: 50
  },
  {
    id: 2,
    name: 'Executive Office South',
    code: 'EO-S-02',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    type: 'office',
    area: 110,
    devices: 7,
    sensors: 10,
    occupancy: 78,
    temp: 22.8,
    humidity: 47,
    status: 'active',
    description: 'South-facing executive suites',
    tempSetpoint: 22,
    humiditySetpoint: 50
  },
  {
    id: 3,
    name: 'Conference Center',
    code: 'CONF-03',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    type: 'meeting',
    area: 250,
    devices: 15,
    sensors: 20,
    occupancy: 65,
    temp: 21.5,
    humidity: 45,
    status: 'active',
    description: 'Large conference and event space',
    tempSetpoint: 21,
    humiditySetpoint: 45
  },
  {
    id: 4,
    name: 'Break Room A',
    code: 'BRK-A-04',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    type: 'break',
    area: 80,
    devices: 5,
    sensors: 8,
    occupancy: 42,
    temp: 23.0,
    humidity: 50,
    status: 'active',
    description: 'Pantry and lounge area',
    tempSetpoint: 23,
    humiditySetpoint: 50
  },
  {
    id: 5,
    name: 'Server Room',
    code: 'SRV-05',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 3,
    floorLevel: 3,
    floorCode: 'L3',
    type: 'server',
    area: 45,
    devices: 45,
    sensors: 35,
    occupancy: 0,
    temp: 18.5,
    humidity: 42,
    status: 'active',
    description: 'IT server room - restricted access',
    tempSetpoint: 18,
    humiditySetpoint: 45
  },
  {
    id: 6,
    name: 'Retail Zone A',
    code: 'RTL-A-06',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 4,
    floorLevel: 1,
    floorCode: 'G',
    type: 'retail',
    area: 350,
    devices: 12,
    sensors: 18,
    occupancy: 92,
    temp: 23.5,
    humidity: 52,
    status: 'active',
    description: 'Premium retail space',
    tempSetpoint: 23,
    humiditySetpoint: 50
  },
  {
    id: 7,
    name: 'Open Office West',
    code: 'OO-W-07',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 5,
    floorLevel: 2,
    floorCode: '2F',
    type: 'office',
    area: 280,
    devices: 22,
    sensors: 28,
    occupancy: 88,
    temp: 22.2,
    humidity: 48,
    status: 'maintenance',
    description: 'Open plan office - under renovation',
    tempSetpoint: 22,
    humiditySetpoint: 50
  },
  {
    id: 8,
    name: 'Production Line 1',
    code: 'PROD-1-08',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 7,
    floorLevel: 1,
    floorCode: '01',
    type: 'production',
    area: 450,
    devices: 35,
    sensors: 40,
    occupancy: 95,
    temp: 24.0,
    humidity: 55,
    status: 'active',
    description: 'Main production line',
    tempSetpoint: 24,
    humiditySetpoint: 55
  },
  {
    id: 9,
    name: 'R&D Lab Alpha',
    code: 'LAB-A-09',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 8,
    floorLevel: 2,
    floorCode: '02',
    type: 'office',
    area: 180,
    devices: 18,
    sensors: 22,
    occupancy: 82,
    temp: 21.8,
    humidity: 46,
    status: 'active',
    description: 'Research and development laboratory',
    tempSetpoint: 22,
    humiditySetpoint: 50
  },
  {
    id: 10,
    name: 'Storage Warehouse',
    code: 'STO-10',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 7,
    floorLevel: 1,
    floorCode: '01',
    type: 'storage',
    area: 320,
    devices: 6,
    sensors: 10,
    occupancy: 35,
    temp: 25.0,
    humidity: 58,
    status: 'active',
    description: 'Equipment and supplies storage',
    tempSetpoint: 25,
    humiditySetpoint: 60
  }
])

// UI State
const searchText = ref('')
const filterBuilding = ref('all')
const filterType = ref('all')
const filterStatus = ref('all')
const showZoneDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedZone = ref<Zone | null>(null)

const zoneForm = ref({
  name: '',
  code: '',
  buildingId: 1,
  floorId: 1,
  type: 'office',
  area: 0,
  tempSetpoint: 22,
  humiditySetpoint: 50,
  status: 'active',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Zone' : 'Add Zone')

const totalZones = computed(() => zones.value.length)
const totalArea = computed(() => zones.value.reduce((sum, z) => sum + z.area, 0))
const activeZones = computed(() => zones.value.filter(z => z.status === 'active').length)
const avgOccupancy = computed(() => Math.round(zones.value.reduce((sum, z) => sum + z.occupancy, 0) / zones.value.length))

const uniqueBuildings = computed(() => {
  const buildingsSet = new Set(zones.value.map(z => z.buildingName))
  return Array.from(buildingsSet)
})

const availableFloors = computed(() => {
  if (!zoneForm.value.buildingId) return []
  return floors.value.filter(f => f.buildingId === zoneForm.value.buildingId)
})

const filteredZones = computed(() => {
  let filtered = [...zones.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(z =>
        z.name.toLowerCase().includes(keyword) ||
        z.code.toLowerCase().includes(keyword)
    )
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(z => z.buildingName === filterBuilding.value)
  }

  if (filterType.value !== 'all') {
    filtered = filtered.filter(z => z.type === filterType.value)
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(z => z.status === filterStatus.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    office: 'Office',
    meeting: 'Meeting Room',
    break: 'Break Area',
    server: 'Server Room',
    storage: 'Storage',
    production: 'Production',
    retail: 'Retail'
  }
  return map[type] || type
}

const getZoneIcon = (type: string) => {
  const map: Record<string, string> = {
    office: '💼',
    meeting: '👥',
    break: '☕',
    server: '💿',
    storage: '📦',
    production: '🏭',
    retail: '🛍️'
  }
  return map[type] || '📍'
}

// Watch building change to reset floor selection
watch(() => zoneForm.value.buildingId, (newVal) => {
  if (newVal && availableFloors.value.length > 0) {
    zoneForm.value.floorId = availableFloors.value[0].id
  }
})

// Zone CRUD operations
const openAddZoneDialog = () => {
  isEditing.value = false
  zoneForm.value = {
    name: '',
    code: '',
    buildingId: buildings.value[0]?.id || 1,
    floorId: 1,
    type: 'office',
    area: 0,
    tempSetpoint: 22,
    humiditySetpoint: 50,
    status: 'active',
    description: ''
  }
  showZoneDialog.value = true
}

const editZone = (zone: Zone) => {
  isEditing.value = true
  selectedZone.value = zone
  zoneForm.value = {
    name: zone.name,
    code: zone.code,
    buildingId: zone.buildingId,
    floorId: zone.floorId,
    type: zone.type,
    area: zone.area,
    tempSetpoint: zone.tempSetpoint,
    humiditySetpoint: zone.humiditySetpoint,
    status: zone.status,
    description: zone.description || ''
  }
  showZoneDialog.value = true
}

const saveZone = () => {
  if (!zoneForm.value.name.trim()) {
    ElMessage.warning('Please enter zone name')
    return
  }

  const building = buildings.value.find(b => b.id === zoneForm.value.buildingId)
  const floor = floors.value.find(f => f.id === zoneForm.value.floorId)

  if (!building || !floor) {
    ElMessage.warning('Please select building and floor')
    return
  }

  if (isEditing.value && selectedZone.value) {
    const index = zones.value.findIndex(z => z.id === selectedZone.value!.id)
    if (index !== -1) {
      zones.value[index] = {
        ...zones.value[index],
        name: zoneForm.value.name,
        code: zoneForm.value.code,
        buildingId: zoneForm.value.buildingId,
        buildingName: building.name,
        floorId: zoneForm.value.floorId,
        floorLevel: floor.level,
        floorCode: floor.code,
        type: zoneForm.value.type,
        area: zoneForm.value.area,
        tempSetpoint: zoneForm.value.tempSetpoint,
        humiditySetpoint: zoneForm.value.humiditySetpoint,
        status: zoneForm.value.status,
        description: zoneForm.value.description
      }
      ElMessage.success('Zone updated successfully')
    }
  } else {
    const existingZonesOnFloor = zones.value.filter(z => z.floorId === zoneForm.value.floorId)
    const newZone: Zone = {
      id: Date.now(),
      name: zoneForm.value.name,
      code: zoneForm.value.code || `ZN-${existingZonesOnFloor.length + 1}`,
      buildingId: zoneForm.value.buildingId,
      buildingName: building.name,
      floorId: zoneForm.value.floorId,
      floorLevel: floor.level,
      floorCode: floor.code,
      type: zoneForm.value.type,
      area: zoneForm.value.area,
      devices: 0,
      sensors: 0,
      occupancy: 0,
      temp: 22,
      humidity: 50,
      status: zoneForm.value.status,
      description: zoneForm.value.description,
      tempSetpoint: zoneForm.value.tempSetpoint,
      humiditySetpoint: zoneForm.value.humiditySetpoint
    }
    zones.value.push(newZone)
    ElMessage.success('Zone added successfully')
  }

  showZoneDialog.value = false
}

const viewZone = (zone: Zone) => {
  selectedZone.value = zone
  showDetailDialog.value = true
}

const deleteZone = (zone: Zone) => {
  ElMessageBox.confirm(
      `Delete zone "${zone.name}"? This will also remove all associated devices and sensors.`,
      'Delete Zone',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = zones.value.findIndex(z => z.id === zone.id)
    if (index !== -1) {
      zones.value.splice(index, 1)
      ElMessage.success('Zone deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredZones.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `zones_${new Date().toISOString().split('T')[0]}.json`
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
.zone-management {
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

/* Zones Grid */
.zones-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.zone-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-top: 4px solid #67c23a;
}

.zone-card.office { border-top-color: #409eff; }
.zone-card.meeting { border-top-color: #8b5cf6; }
.zone-card.break { border-top-color: #f59e0b; }
.zone-card.server { border-top-color: #ef4444; }
.zone-card.storage { border-top-color: #909399; }
.zone-card.production { border-top-color: #10b981; }
.zone-card.retail { border-top-color: #ec489a; }

.zone-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.zone-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.zone-icon {
  width: 48px;
  height: 48px;
  background: #f8f9fa;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.zone-info {
  flex: 1;
}

.zone-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.zone-code {
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

.status-badge.active { background: #e8f5e9; color: #67c23a; }
.status-badge.inactive { background: #ffefef; color: #f56c6c; }

.zone-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.zone-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #303133;
  font-weight: 500;
}

.zone-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 8px 0;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
}

.stat-label-sm {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

.zone-actions {
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

/* Dialog */
:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .zone-management { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .zones-grid { grid-template-columns: 1fr; }
  .zone-details { grid-template-columns: 1fr; }
}
</style>