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
        <div class="loading-tip">Floor Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="floor-management">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Floor Management</h2>
        <p class="subtitle">Manage building floors, layouts, and floor-specific configurations</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddFloorDialog">
          <el-icon><Plus /></el-icon> Add Floor
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
          <div class="stat-value">{{ totalFloors }}</div>
          <div class="stat-label">Total Floors</div>
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
          <div class="stat-value">{{ activeFloors }}</div>
          <div class="stat-label">Active Floors</div>
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
        <el-input v-model="searchText" placeholder="Search by floor name, number or building..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 180px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Active" value="active" />
          <el-option label="Under Maintenance" value="maintenance" />
          <el-option label="Vacant" value="vacant" />
        </el-select>
      </div>
    </div>

    <!-- Floors List -->
    <div class="floors-container">
      <div v-for="building in groupedFloors" :key="building.name" class="building-group">
        <div class="building-header" @click="toggleBuilding(building.name)">
          <div class="building-title">
            <span class="building-icon">🏢</span>
            <span class="building-name">{{ building.name }}</span>
            <span class="building-count">{{ building.floors.length }} floors</span>
          </div>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="expandedBuildings.includes(building.name)" />
            <ArrowRight v-else />
          </el-icon>
        </div>
        <transition name="expand">
          <div v-show="expandedBuildings.includes(building.name)" class="floors-grid">
            <div v-for="floor in building.floors" :key="floor.id" class="floor-card" :class="floor.status">
              <div class="floor-header">
                <div class="floor-number">
                  <span class="floor-icon">📍</span>
                  <span class="floor-name">Floor {{ floor.level }}</span>
                  <span class="floor-code">{{ floor.code }}</span>
                </div>
                <div class="floor-status">
                  <span class="status-badge" :class="floor.status">{{ getStatusText(floor.status) }}</span>
                </div>
              </div>

              <div class="floor-details">
                <div class="detail-row">
                  <span class="detail-label">Area</span>
                  <span class="detail-value">{{ formatNumber(floor.area) }} sqm</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Ceiling Height</span>
                  <span class="detail-value">{{ floor.ceilingHeight }} m</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Zones</span>
                  <span class="detail-value">{{ floor.zones }} zones</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">Rooms</span>
                  <span class="detail-value">{{ floor.rooms }} rooms</span>
                </div>
              </div>

              <div class="floor-stats">
                <div class="stat-item">
                  <span class="stat-number">{{ floor.occupancy }}%</span>
                  <span class="stat-label-sm">Occupancy</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ floor.devices }}</span>
                  <span class="stat-label-sm">Devices</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ floor.sensors }}</span>
                  <span class="stat-label-sm">Sensors</span>
                </div>
              </div>

              <div class="floor-actions">
                <el-button size="small" type="primary" plain @click="viewFloor(floor)">
                  <el-icon><View /></el-icon> View
                </el-button>
                <el-button size="small" type="info" plain @click="editFloor(floor)">
                  <el-icon><Edit /></el-icon> Edit
                </el-button>
                <el-button size="small" type="danger" plain @click="deleteFloor(floor)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="floors.length === 0" class="empty-state">
      <div class="empty-icon">📍</div>
      <div class="empty-title">No floors found</div>
      <div class="empty-desc">Add a floor to start managing floor layouts</div>
      <el-button type="primary" @click="openAddFloorDialog">Add Floor</el-button>
    </div>

    <!-- Add/Edit Floor Dialog -->
    <el-dialog v-model="showFloorDialog" :title="dialogTitle" width="600px">
      <el-form :model="floorForm" label-width="120px">
        <el-form-item label="Building" required>
          <el-select v-model="floorForm.buildingId" placeholder="Select building" style="width: 100%" @change="onBuildingChange">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Floor Level" required>
              <el-input-number v-model="floorForm.level" :min="-2" :max="100" style="width: 100%" placeholder="e.g., 1, 2, -1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Floor Code">
              <el-input v-model="floorForm.code" placeholder="e.g., L1, B1, 02F" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Area (sqm)" required>
          <el-input-number v-model="floorForm.area" :min="0" :step="50" style="width: 100%" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Ceiling Height (m)">
              <el-input-number v-model="floorForm.ceilingHeight" :min="2" :max="10" :step="0.1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status">
              <el-select v-model="floorForm.status" style="width: 100%">
                <el-option label="Active" value="active" />
                <el-option label="Under Maintenance" value="maintenance" />
                <el-option label="Vacant" value="vacant" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Number of Zones">
              <el-input-number v-model="floorForm.zones" :min="0" :max="50" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Number of Rooms">
              <el-input-number v-model="floorForm.rooms" :min="0" :max="200" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="floorForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showFloorDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveFloor">Save Floor</el-button>
      </template>
    </el-dialog>

    <!-- Floor Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="`Floor ${selectedFloor?.level} - ${selectedFloor?.buildingName}`" width="700px">
      <div v-if="selectedFloor">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Floor ID">{{ selectedFloor.id }}</el-descriptions-item>
          <el-descriptions-item label="Floor Code">{{ selectedFloor.code }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedFloor.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Level">{{ selectedFloor.level }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedFloor.status]">{{ getStatusText(selectedFloor.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Total Area">{{ formatNumber(selectedFloor.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Ceiling Height">{{ selectedFloor.ceilingHeight }} m</el-descriptions-item>
          <el-descriptions-item label="Number of Zones">{{ selectedFloor.zones }}</el-descriptions-item>
          <el-descriptions-item label="Number of Rooms">{{ selectedFloor.rooms }}</el-descriptions-item>
          <el-descriptions-item label="Active Devices">{{ selectedFloor.devices }}</el-descriptions-item>
          <el-descriptions-item label="Connected Sensors">{{ selectedFloor.sensors }}</el-descriptions-item>
          <el-descriptions-item label="Occupancy Rate">{{ selectedFloor.occupancy }}%</el-descriptions-item>
          <el-descriptions-item label="Last Inspection">{{ selectedFloor.lastInspection || '2025-01-15' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedFloor.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editFloor(selectedFloor); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading floor data...',
  'Fetching building information...',
  'Organizing floor layouts...',
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
  buildingName: string
  level: number
  code: string
  area: number
  ceilingHeight: number
  zones: number
  rooms: number
  devices: number
  sensors: number
  occupancy: number
  status: string
  description: string
  lastInspection: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  { id: 1, name: 'Marina Bay Tower' },
  { id: 2, name: 'Central Plaza' },
  { id: 3, name: 'Tech Park North' },
  { id: 4, name: 'Retail Pavilion' },
  { id: 5, name: 'Data Hub South' }
])

// Sample floors data
const floors = ref<Floor[]>([
  {
    id: 1,
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    level: 1,
    code: 'L1',
    area: 1850,
    ceilingHeight: 3.2,
    zones: 8,
    rooms: 24,
    devices: 85,
    sensors: 120,
    occupancy: 92,
    status: 'active',
    description: 'Main lobby, reception, and retail area',
    lastInspection: '2025-01-10'
  },
  {
    id: 2,
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    level: 2,
    code: 'L2',
    area: 1820,
    ceilingHeight: 3.0,
    zones: 8,
    rooms: 28,
    devices: 92,
    sensors: 130,
    occupancy: 88,
    status: 'active',
    description: 'Office spaces and meeting rooms',
    lastInspection: '2025-01-10'
  },
  {
    id: 3,
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    level: 3,
    code: 'L3',
    area: 1820,
    ceilingHeight: 3.0,
    zones: 8,
    rooms: 26,
    devices: 88,
    sensors: 125,
    occupancy: 85,
    status: 'active',
    description: 'Executive offices',
    lastInspection: '2025-01-10'
  },
  {
    id: 4,
    buildingId: 2,
    buildingName: 'Central Plaza',
    level: 1,
    code: 'G',
    area: 2100,
    ceilingHeight: 3.5,
    zones: 10,
    rooms: 15,
    devices: 75,
    sensors: 110,
    occupancy: 95,
    status: 'active',
    description: 'Grand lobby and retail gallery',
    lastInspection: '2025-01-05'
  },
  {
    id: 5,
    buildingId: 2,
    buildingName: 'Central Plaza',
    level: 2,
    code: '2F',
    area: 2080,
    ceilingHeight: 3.0,
    zones: 9,
    rooms: 22,
    devices: 82,
    sensors: 118,
    occupancy: 82,
    status: 'maintenance',
    description: 'Office spaces - under renovation',
    lastInspection: '2025-01-05'
  },
  {
    id: 6,
    buildingId: 2,
    buildingName: 'Central Plaza',
    level: 3,
    code: '3F',
    area: 2080,
    ceilingHeight: 3.0,
    zones: 9,
    rooms: 24,
    devices: 86,
    sensors: 122,
    occupancy: 80,
    status: 'active',
    description: 'Conference and event spaces',
    lastInspection: '2025-01-05'
  },
  {
    id: 7,
    buildingId: 3,
    buildingName: 'Tech Park North',
    level: 1,
    code: '01',
    area: 3200,
    ceilingHeight: 4.5,
    zones: 6,
    rooms: 12,
    devices: 65,
    sensors: 95,
    occupancy: 98,
    status: 'active',
    description: 'Manufacturing and production floor',
    lastInspection: '2025-01-12'
  },
  {
    id: 8,
    buildingId: 3,
    buildingName: 'Tech Park North',
    level: 2,
    code: '02',
    area: 3100,
    ceilingHeight: 4.0,
    zones: 6,
    rooms: 10,
    devices: 58,
    sensors: 88,
    occupancy: 96,
    status: 'active',
    description: 'R&D laboratories',
    lastInspection: '2025-01-12'
  },
  {
    id: 9,
    buildingId: 4,
    buildingName: 'Retail Pavilion',
    level: 1,
    code: '1F',
    area: 2800,
    ceilingHeight: 4.0,
    zones: 12,
    rooms: 35,
    devices: 55,
    sensors: 80,
    occupancy: 97,
    status: 'active',
    description: 'Retail and dining outlets',
    lastInspection: '2025-01-08'
  },
  {
    id: 10,
    buildingId: 4,
    buildingName: 'Retail Pavilion',
    level: 2,
    code: '2F',
    area: 2750,
    ceilingHeight: 3.5,
    zones: 11,
    rooms: 32,
    devices: 52,
    sensors: 76,
    occupancy: 94,
    status: 'active',
    description: 'Fashion and lifestyle stores',
    lastInspection: '2025-01-08'
  },
  {
    id: 11,
    buildingId: 5,
    buildingName: 'Data Hub South',
    level: 1,
    code: 'DC1',
    area: 4200,
    ceilingHeight: 5.0,
    zones: 4,
    rooms: 6,
    devices: 520,
    sensors: 380,
    occupancy: 78,
    status: 'maintenance',
    description: 'Server hall A - cooling system upgrade',
    lastInspection: '2025-01-02'
  },
  {
    id: 12,
    buildingId: 5,
    buildingName: 'Data Hub South',
    level: 2,
    code: 'DC2',
    area: 4100,
    ceilingHeight: 4.8,
    zones: 4,
    rooms: 6,
    devices: 510,
    sensors: 375,
    occupancy: 82,
    status: 'active',
    description: 'Server hall B',
    lastInspection: '2025-01-02'
  }
])

// UI State
const searchText = ref('')
const filterBuilding = ref('all')
const filterStatus = ref('all')
const expandedBuildings = ref<string[]>(['Marina Bay Tower', 'Central Plaza'])
const showFloorDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedFloor = ref<Floor | null>(null)

const floorForm = ref({
  buildingId: 1,
  level: 1,
  code: '',
  area: 0,
  ceilingHeight: 3.0,
  zones: 0,
  rooms: 0,
  status: 'active',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Floor' : 'Add Floor')

const totalFloors = computed(() => floors.value.length)
const totalArea = computed(() => floors.value.reduce((sum, f) => sum + f.area, 0))
const activeFloors = computed(() => floors.value.filter(f => f.status === 'active').length)
const avgOccupancy = computed(() => Math.round(floors.value.reduce((sum, f) => sum + f.occupancy, 0) / floors.value.length))

const uniqueBuildings = computed(() => {
  const buildingsSet = new Set(floors.value.map(f => f.buildingName))
  return Array.from(buildingsSet)
})

const filteredFloors = computed(() => {
  let filtered = [...floors.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(f =>
        f.buildingName.toLowerCase().includes(keyword) ||
        f.code.toLowerCase().includes(keyword) ||
        f.level.toString().includes(keyword)
    )
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(f => f.buildingName === filterBuilding.value)
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(f => f.status === filterStatus.value)
  }

  return filtered
})

const groupedFloors = computed(() => {
  const groups: { [key: string]: Floor[] } = {}
  filteredFloors.value.forEach(floor => {
    if (!groups[floor.buildingName]) {
      groups[floor.buildingName] = []
    }
    groups[floor.buildingName].push(floor)
  })
  return Object.entries(groups).map(([name, floors]) => ({
    name,
    floors: floors.sort((a, b) => a.level - b.level)
  }))
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: 'Active',
    maintenance: 'Maintenance',
    vacant: 'Vacant'
  }
  return map[status] || status
}

const onBuildingChange = (buildingId: number) => {
  const building = buildings.value.find(b => b.id === buildingId)
  if (building) {
    // Auto-generate floor code based on existing floors count
    const existingFloors = floors.value.filter(f => f.buildingId === buildingId)
    const nextLevel = existingFloors.length + 1
    floorForm.value.code = `L${nextLevel}`
  }
}

const toggleBuilding = (buildingName: string) => {
  const index = expandedBuildings.value.indexOf(buildingName)
  if (index === -1) {
    expandedBuildings.value.push(buildingName)
  } else {
    expandedBuildings.value.splice(index, 1)
  }
}

// Floor CRUD operations
const openAddFloorDialog = () => {
  isEditing.value = false
  floorForm.value = {
    buildingId: buildings.value[0]?.id || 1,
    level: 1,
    code: '',
    area: 0,
    ceilingHeight: 3.0,
    zones: 0,
    rooms: 0,
    status: 'active',
    description: ''
  }
  showFloorDialog.value = true
}

const editFloor = (floor: Floor) => {
  isEditing.value = true
  selectedFloor.value = floor
  floorForm.value = {
    buildingId: floor.buildingId,
    level: floor.level,
    code: floor.code,
    area: floor.area,
    ceilingHeight: floor.ceilingHeight,
    zones: floor.zones,
    rooms: floor.rooms,
    status: floor.status,
    description: floor.description || ''
  }
  showFloorDialog.value = true
}

const saveFloor = () => {
  const building = buildings.value.find(b => b.id === floorForm.value.buildingId)
  if (!building) {
    ElMessage.warning('Please select a building')
    return
  }

  if (floorForm.value.area <= 0) {
    ElMessage.warning('Please enter a valid area')
    return
  }

  if (isEditing.value && selectedFloor.value) {
    const index = floors.value.findIndex(f => f.id === selectedFloor.value!.id)
    if (index !== -1) {
      floors.value[index] = {
        ...floors.value[index],
        buildingId: floorForm.value.buildingId,
        buildingName: building.name,
        level: floorForm.value.level,
        code: floorForm.value.code,
        area: floorForm.value.area,
        ceilingHeight: floorForm.value.ceilingHeight,
        zones: floorForm.value.zones,
        rooms: floorForm.value.rooms,
        status: floorForm.value.status,
        description: floorForm.value.description
      }
      ElMessage.success('Floor updated successfully')
    }
  } else {
    const newFloor: Floor = {
      id: Date.now(),
      buildingId: floorForm.value.buildingId,
      buildingName: building.name,
      level: floorForm.value.level,
      code: floorForm.value.code || `L${floorForm.value.level}`,
      area: floorForm.value.area,
      ceilingHeight: floorForm.value.ceilingHeight,
      zones: floorForm.value.zones,
      rooms: floorForm.value.rooms,
      devices: 0,
      sensors: 0,
      occupancy: 0,
      status: floorForm.value.status,
      description: floorForm.value.description,
      lastInspection: new Date().toISOString().split('T')[0]
    }
    floors.value.push(newFloor)
    ElMessage.success('Floor added successfully')
  }

  showFloorDialog.value = false
}

const viewFloor = (floor: Floor) => {
  selectedFloor.value = floor
  showDetailDialog.value = true
}

const deleteFloor = (floor: Floor) => {
  ElMessageBox.confirm(
      `Delete Floor ${floor.level} in "${floor.buildingName}"? This will also remove all zones, rooms, and devices on this floor.`,
      'Delete Floor',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = floors.value.findIndex(f => f.id === floor.id)
    if (index !== -1) {
      floors.value.splice(index, 1)
      ElMessage.success('Floor deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredFloors.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `floors_${new Date().toISOString().split('T')[0]}.json`
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
.floor-management {
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

/* Floors Container */
.floors-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.building-group {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.building-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.building-header:hover {
  background: #f0f2f5;
}

.building-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.building-icon {
  font-size: 24px;
}

.building-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.building-count {
  font-size: 12px;
  color: #909399;
  background: #e4e7ed;
  padding: 2px 8px;
  border-radius: 20px;
}

.toggle-icon {
  font-size: 20px;
  color: #909399;
  transition: transform 0.2s ease;
}

/* Floors Grid */
.floors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  padding: 20px;
}

.floor-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.floor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.floor-card.maintenance { border-left-color: #e6a23c; }
.floor-card.vacant { border-left-color: #f56c6c; }
.floor-card.active { border-left-color: #67c23a; }

.floor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.floor-number {
  display: flex;
  align-items: center;
  gap: 8px;
}

.floor-icon {
  font-size: 18px;
}

.floor-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.floor-code {
  font-size: 11px;
  color: #909399;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.active { background: #e8f5e9; color: #67c23a; }
.status-badge.maintenance { background: #fff7e6; color: #e6a23c; }
.status-badge.vacant { background: #ffefef; color: #f56c6c; }

.floor-details {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 12px;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #303133;
  font-weight: 500;
}

.floor-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 12px;
  padding: 8px 0;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.stat-label-sm {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

.floor-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Expand Transition */
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to, .expand-leave-from {
  opacity: 1;
  max-height: 2000px;
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
  .floor-management { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .floors-grid { grid-template-columns: 1fr; }
  .floor-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .floor-status { align-self: flex-start; }
}
</style>