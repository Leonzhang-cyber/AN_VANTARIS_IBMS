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
        <div class="loading-tip">Technical Rooms Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="technical-rooms">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Technical Rooms</h2>
        <p class="subtitle">Manage MEP rooms, equipment spaces, and critical infrastructure areas</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddRoomDialog">
          <el-icon><Plus /></el-icon> Add Room
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
        <div class="stat-icon">🔧</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalRooms }}</div>
          <div class="stat-label">Total Rooms</div>
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
          <div class="stat-value">{{ operationalCount }}</div>
          <div class="stat-label">Operational</div>
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
        <el-input v-model="searchText" placeholder="Search by room name, code or type..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 180px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildings" :key="b" :label="b" :value="b" />
        </el-select>
        <el-select v-model="filterRoomType" placeholder="Room Type" clearable style="width: 160px">
          <el-option label="All Types" value="all" />
          <el-option label="Electrical Room" value="electrical" />
          <el-option label="Server Room" value="server" />
          <el-option label="HVAC Room" value="hvac" />
          <el-option label="UPS Room" value="ups" />
          <el-option label="Pump Room" value="pump" />
          <el-option label="Generator Room" value="generator" />
          <el-option label="Chiller Plant" value="chiller" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Operational" value="operational" />
          <el-option label="Maintenance" value="maintenance" />
          <el-option label="Offline" value="offline" />
        </el-select>
      </div>
    </div>

    <!-- Technical Rooms Grid -->
    <div class="rooms-grid">
      <div v-for="room in filteredRooms" :key="room.id" class="room-card" :class="room.status">
        <div class="room-header">
          <div class="room-icon">{{ getRoomIcon(room.roomType) }}</div>
          <div class="room-info">
            <div class="room-name">{{ room.name }}</div>
            <div class="room-code">{{ room.code }}</div>
          </div>
          <div class="room-status">
            <span class="status-badge" :class="room.status">{{ getStatusText(room.status) }}</span>
          </div>
        </div>

        <div class="room-location">
          <el-icon><Location /></el-icon>
          <span>{{ room.buildingName }} - Floor {{ room.floorLevel }} ({{ room.floorCode }})</span>
        </div>

        <div class="room-details">
          <div class="detail-row">
            <span class="detail-label">Area</span>
            <span class="detail-value">{{ formatNumber(room.area) }} sqm</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Room Type</span>
            <span class="detail-value">{{ getRoomTypeLabel(room.roomType) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Temperature</span>
            <span class="detail-value" :class="getTempClass(room.temperature)">{{ room.temperature }}°C</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Humidity</span>
            <span class="detail-value" :class="getHumidityClass(room.humidity)">{{ room.humidity }}%</span>
          </div>
        </div>

        <div class="room-stats">
          <div class="stat-item">
            <div class="stat-number">{{ room.equipmentCount }}</div>
            <div class="stat-label-sm">Equipment</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ room.lastInspection || 'N/A' }}</div>
            <div class="stat-label-sm">Last Inspection</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ room.alerts?.length || 0 }}</div>
            <div class="stat-label-sm">Alerts</div>
          </div>
        </div>

        <div class="room-alerts" v-if="room.alerts && room.alerts.length > 0">
          <div v-for="alert in room.alerts.slice(0, 2)" :key="alert.time" class="alert-item">
            <el-icon><Warning /></el-icon>
            <span>{{ alert.message }}</span>
          </div>
          <div v-if="room.alerts.length > 2" class="alert-more">+{{ room.alerts.length - 2 }} more alerts</div>
        </div>

        <div class="room-actions">
          <el-button size="small" type="primary" plain @click="viewRoom(room)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editRoom(room)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteRoom(room)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredRooms.length === 0" class="empty-state">
      <div class="empty-icon">🔧</div>
      <div class="empty-title">No technical rooms found</div>
      <div class="empty-desc">Add a technical room to start managing MEP spaces</div>
      <el-button type="primary" @click="openAddRoomDialog">Add Room</el-button>
    </div>

    <!-- Add/Edit Room Dialog -->
    <el-dialog v-model="showRoomDialog" :title="dialogTitle" width="650px">
      <el-form :model="roomForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Room Name" required>
              <el-input v-model="roomForm.name" placeholder="Enter room name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Room Code">
              <el-input v-model="roomForm.code" placeholder="e.g., ER-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="roomForm.buildingId" placeholder="Select building" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Floor" required>
          <el-select v-model="roomForm.floorId" placeholder="Select floor" style="width: 100%" :disabled="!roomForm.buildingId">
            <el-option v-for="f in availableFloors" :key="f.id" :label="`Floor ${f.level} - ${f.code}`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Room Type">
              <el-select v-model="roomForm.roomType" style="width: 100%">
                <el-option label="Electrical Room" value="electrical" />
                <el-option label="Server Room" value="server" />
                <el-option label="HVAC Room" value="hvac" />
                <el-option label="UPS Room" value="ups" />
                <el-option label="Pump Room" value="pump" />
                <el-option label="Generator Room" value="generator" />
                <el-option label="Chiller Plant" value="chiller" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Area (sqm)">
              <el-input-number v-model="roomForm.area" :min="0" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Temperature Setpoint">
              <el-input-number v-model="roomForm.tempSetpoint" :min="15" :max="30" :step="0.5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Humidity Setpoint">
              <el-input-number v-model="roomForm.humiditySetpoint" :min="30" :max="70" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="roomForm.status">
            <el-radio label="operational">Operational</el-radio>
            <el-radio label="maintenance">Maintenance</el-radio>
            <el-radio label="offline">Offline</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="roomForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoomDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveRoom">Save Room</el-button>
      </template>
    </el-dialog>

    <!-- Room Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedRoom?.name" width="750px">
      <div v-if="selectedRoom">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Room ID">{{ selectedRoom.id }}</el-descriptions-item>
          <el-descriptions-item label="Room Code">{{ selectedRoom.code }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedRoom.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Floor">Floor {{ selectedRoom.floorLevel }} ({{ selectedRoom.floorCode }})</el-descriptions-item>
          <el-descriptions-item label="Room Type">{{ getRoomTypeLabel(selectedRoom.roomType) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedRoom.status]">{{ getStatusText(selectedRoom.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Area">{{ formatNumber(selectedRoom.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Equipment Count">{{ selectedRoom.equipmentCount }}</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ selectedRoom.temperature }}°C</el-descriptions-item>
          <el-descriptions-item label="Humidity">{{ selectedRoom.humidity }}%</el-descriptions-item>
          <el-descriptions-item label="Last Inspection">{{ selectedRoom.lastInspection }}</el-descriptions-item>
          <el-descriptions-item label="Next Inspection">{{ selectedRoom.nextInspection }}</el-descriptions-item>
          <el-descriptions-item label="Access Level">{{ selectedRoom.accessLevel }}</el-descriptions-item>
          <el-descriptions-item label="Fire Suppression">{{ selectedRoom.fireSuppression }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedRoom.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="selectedRoom.alerts && selectedRoom.alerts.length > 0" class="detail-alerts">
          <h4>Active Alerts</h4>
          <el-table :data="selectedRoom.alerts" size="small">
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
        <el-button type="primary" @click="editRoom(selectedRoom); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location, Warning } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading technical rooms data...',
  'Fetching MEP room information...',
  'Checking equipment status...',
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

// Technical Room interface
interface TechnicalRoom {
  id: number
  name: string
  code: string
  buildingId: number
  buildingName: string
  floorId: number
  floorLevel: number
  floorCode: string
  roomType: string
  area: number
  temperature: number
  humidity: number
  equipmentCount: number
  status: string
  lastInspection: string
  nextInspection: string
  accessLevel: string
  fireSuppression: string
  alerts: { severity: string; message: string; time: string }[]
  description: string
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
  { id: 4, buildingId: 1, level: -1, code: 'B1' },
  { id: 5, buildingId: 2, level: 1, code: 'G' },
  { id: 6, buildingId: 2, level: 2, code: '2F' },
  { id: 7, buildingId: 3, level: 1, code: '01' }
])

// Sample technical rooms data
const technicalRooms = ref<TechnicalRoom[]>([
  {
    id: 1,
    name: 'Main Electrical Room',
    code: 'MER-01',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    roomType: 'electrical',
    area: 120,
    temperature: 24.5,
    humidity: 45,
    equipmentCount: 28,
    status: 'operational',
    lastInspection: '2025-01-10',
    nextInspection: '2025-04-10',
    accessLevel: 'Restricted',
    fireSuppression: 'FM200',
    alerts: [],
    description: 'Main electrical distribution room'
  },
  {
    id: 2,
    name: 'UPS Room',
    code: 'UPS-01',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    roomType: 'ups',
    area: 65,
    temperature: 22.0,
    humidity: 42,
    equipmentCount: 12,
    status: 'operational',
    lastInspection: '2025-01-08',
    nextInspection: '2025-04-08',
    accessLevel: 'Restricted',
    fireSuppression: 'Novec 1230',
    alerts: [],
    description: 'UPS battery room'
  },
  {
    id: 3,
    name: 'Server Room A',
    code: 'SRV-A-03',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 3,
    floorLevel: 3,
    floorCode: 'L3',
    roomType: 'server',
    area: 85,
    temperature: 19.5,
    humidity: 48,
    equipmentCount: 45,
    status: 'operational',
    lastInspection: '2025-01-12',
    nextInspection: '2025-04-12',
    accessLevel: 'High Security',
    fireSuppression: 'Inergen',
    alerts: [
      { severity: 'warning', message: 'High temperature alarm - Cooling system degraded', time: '2025-01-16 08:30:00' }
    ],
    description: 'Primary IT server room'
  },
  {
    id: 4,
    name: 'Chiller Plant Room',
    code: 'CHP-01',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 4,
    floorLevel: -1,
    floorCode: 'B1',
    roomType: 'chiller',
    area: 280,
    temperature: 28.0,
    humidity: 55,
    equipmentCount: 8,
    status: 'operational',
    lastInspection: '2025-01-05',
    nextInspection: '2025-04-05',
    accessLevel: 'Restricted',
    fireSuppression: 'Water Sprinkler',
    alerts: [],
    description: 'Central chiller plant'
  },
  {
    id: 5,
    name: 'Generator Room',
    code: 'GEN-01',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 5,
    floorLevel: 1,
    floorCode: 'G',
    roomType: 'generator',
    area: 95,
    temperature: 26.5,
    humidity: 50,
    equipmentCount: 4,
    status: 'maintenance',
    lastInspection: '2024-12-20',
    nextInspection: '2025-03-20',
    accessLevel: 'Restricted',
    fireSuppression: 'CO2',
    alerts: [
      { severity: 'critical', message: 'Generator fuel leak detected', time: '2025-01-15 14:20:00' },
      { severity: 'warning', message: 'Scheduled maintenance overdue', time: '2025-01-10 09:00:00' }
    ],
    description: 'Emergency diesel generators'
  },
  {
    id: 6,
    name: 'Pump Room',
    code: 'PMP-01',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 5,
    floorLevel: 1,
    floorCode: 'G',
    roomType: 'pump',
    area: 45,
    temperature: 25.0,
    humidity: 60,
    equipmentCount: 6,
    status: 'operational',
    lastInspection: '2025-01-14',
    nextInspection: '2025-04-14',
    accessLevel: 'Restricted',
    fireSuppression: 'Water Sprinkler',
    alerts: [],
    description: 'Water pump and pressure control'
  },
  {
    id: 7,
    name: 'HVAC Control Room',
    code: 'HVAC-CTL',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 7,
    floorLevel: 1,
    floorCode: '01',
    roomType: 'hvac',
    area: 35,
    temperature: 23.0,
    humidity: 47,
    equipmentCount: 15,
    status: 'operational',
    lastInspection: '2025-01-11',
    nextInspection: '2025-04-11',
    accessLevel: 'Restricted',
    fireSuppression: 'HFC-227ea',
    alerts: [],
    description: 'HVAC control panel room'
  }
])

// UI State
const searchText = ref('')
const filterBuilding = ref('all')
const filterRoomType = ref('all')
const filterStatus = ref('all')
const showRoomDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedRoom = ref<TechnicalRoom | null>(null)

const roomForm = ref({
  name: '',
  code: '',
  buildingId: 1,
  floorId: 1,
  roomType: 'electrical',
  area: 0,
  tempSetpoint: 22,
  humiditySetpoint: 50,
  status: 'operational',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Room' : 'Add Room')

const totalRooms = computed(() => technicalRooms.value.length)
const totalArea = computed(() => technicalRooms.value.reduce((sum, r) => sum + r.area, 0))
const operationalCount = computed(() => technicalRooms.value.filter(r => r.status === 'operational').length)
const alertCount = computed(() => technicalRooms.value.reduce((sum, r) => sum + (r.alerts?.length || 0), 0))

const uniqueBuildings = computed(() => {
  const buildingsSet = new Set(technicalRooms.value.map(r => r.buildingName))
  return Array.from(buildingsSet)
})

const availableFloors = computed(() => {
  if (!roomForm.value.buildingId) return []
  return floors.value.filter(f => f.buildingId === roomForm.value.buildingId)
})

const filteredRooms = computed(() => {
  let filtered = [...technicalRooms.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(keyword) ||
        r.code.toLowerCase().includes(keyword)
    )
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(r => r.buildingName === filterBuilding.value)
  }

  if (filterRoomType.value !== 'all') {
    filtered = filtered.filter(r => r.roomType === filterRoomType.value)
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(r => r.status === filterStatus.value)
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
    offline: 'Offline'
  }
  return map[status] || status
}

const getRoomIcon = (type: string) => {
  const map: Record<string, string> = {
    electrical: '⚡',
    server: '💿',
    hvac: '❄️',
    ups: '🔋',
    pump: '💧',
    generator: '🔌',
    chiller: '❄️'
  }
  return map[type] || '🔧'
}

const getRoomTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    electrical: 'Electrical Room',
    server: 'Server Room',
    hvac: 'HVAC Room',
    ups: 'UPS Room',
    pump: 'Pump Room',
    generator: 'Generator Room',
    chiller: 'Chiller Plant'
  }
  return map[type] || type
}

const getTempClass = (temp: number) => {
  if (temp > 26) return 'temp-high'
  if (temp < 18) return 'temp-low'
  return 'temp-normal'
}

const getHumidityClass = (humidity: number) => {
  if (humidity > 60) return 'humidity-high'
  if (humidity < 35) return 'humidity-low'
  return 'humidity-normal'
}

// Watch building change
watch(() => roomForm.value.buildingId, (newVal) => {
  if (newVal && availableFloors.value.length > 0) {
    roomForm.value.floorId = availableFloors.value[0].id
  }
})

// Room CRUD operations
const openAddRoomDialog = () => {
  isEditing.value = false
  roomForm.value = {
    name: '',
    code: '',
    buildingId: buildings.value[0]?.id || 1,
    floorId: 1,
    roomType: 'electrical',
    area: 0,
    tempSetpoint: 22,
    humiditySetpoint: 50,
    status: 'operational',
    description: ''
  }
  showRoomDialog.value = true
}

const editRoom = (room: TechnicalRoom) => {
  isEditing.value = true
  selectedRoom.value = room
  roomForm.value = {
    name: room.name,
    code: room.code,
    buildingId: room.buildingId,
    floorId: room.floorId,
    roomType: room.roomType,
    area: room.area,
    tempSetpoint: room.temperature,
    humiditySetpoint: room.humidity,
    status: room.status,
    description: room.description || ''
  }
  showRoomDialog.value = true
}

const saveRoom = () => {
  if (!roomForm.value.name.trim()) {
    ElMessage.warning('Please enter room name')
    return
  }

  const building = buildings.value.find(b => b.id === roomForm.value.buildingId)
  const floor = floors.value.find(f => f.id === roomForm.value.floorId)

  if (!building || !floor) {
    ElMessage.warning('Please select building and floor')
    return
  }

  if (isEditing.value && selectedRoom.value) {
    const index = technicalRooms.value.findIndex(r => r.id === selectedRoom.value!.id)
    if (index !== -1) {
      technicalRooms.value[index] = {
        ...technicalRooms.value[index],
        name: roomForm.value.name,
        code: roomForm.value.code,
        buildingId: roomForm.value.buildingId,
        buildingName: building.name,
        floorId: roomForm.value.floorId,
        floorLevel: floor.level,
        floorCode: floor.code,
        roomType: roomForm.value.roomType,
        area: roomForm.value.area,
        temperature: roomForm.value.tempSetpoint,
        humidity: roomForm.value.humiditySetpoint,
        status: roomForm.value.status,
        description: roomForm.value.description
      }
      ElMessage.success('Room updated successfully')
    }
  } else {
    const newRoom: TechnicalRoom = {
      id: Date.now(),
      name: roomForm.value.name,
      code: roomForm.value.code || `RM-${technicalRooms.value.length + 1}`,
      buildingId: roomForm.value.buildingId,
      buildingName: building.name,
      floorId: roomForm.value.floorId,
      floorLevel: floor.level,
      floorCode: floor.code,
      roomType: roomForm.value.roomType,
      area: roomForm.value.area,
      temperature: roomForm.value.tempSetpoint,
      humidity: roomForm.value.humiditySetpoint,
      equipmentCount: 0,
      status: roomForm.value.status,
      lastInspection: new Date().toISOString().split('T')[0],
      nextInspection: new Date(new Date().setMonth(new Date().getMonth() + 3)).toISOString().split('T')[0],
      accessLevel: 'Restricted',
      fireSuppression: 'To be configured',
      alerts: [],
      description: roomForm.value.description
    }
    technicalRooms.value.push(newRoom)
    ElMessage.success('Room added successfully')
  }

  showRoomDialog.value = false
}

const viewRoom = (room: TechnicalRoom) => {
  selectedRoom.value = room
  showDetailDialog.value = true
}

const deleteRoom = (room: TechnicalRoom) => {
  ElMessageBox.confirm(
      `Delete room "${room.name}"? This will also remove all associated equipment records.`,
      'Delete Room',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = technicalRooms.value.findIndex(r => r.id === room.id)
    if (index !== -1) {
      technicalRooms.value.splice(index, 1)
      ElMessage.success('Room deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredRooms.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `technical_rooms_${new Date().toISOString().split('T')[0]}.json`
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
.technical-rooms {
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

/* Rooms Grid */
.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.room-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.room-card.maintenance { border-left-color: #e6a23c; }
.room-card.offline { border-left-color: #f56c6c; }
.room-card.operational { border-left-color: #67c23a; }

.room-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.room-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.room-icon {
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

.room-info {
  flex: 1;
}

.room-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.room-code {
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
.status-badge.offline { background: #ffefef; color: #f56c6c; }

.room-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.room-details {
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

.temp-high { color: #f56c6c; }
.temp-low { color: #409eff; }
.temp-normal { color: #67c23a; }
.humidity-high { color: #f56c6c; }
.humidity-low { color: #409eff; }
.humidity-normal { color: #67c23a; }

.room-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 8px 0;
  background: #f8f9fa;
  border-radius: 12px;
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

.room-alerts {
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

.alert-item:last-child {
  margin-bottom: 0;
}

.alert-more {
  font-size: 10px;
  color: #909399;
  margin-top: 4px;
  text-align: right;
}

.room-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* Detail Dialog */
.detail-alerts {
  margin-top: 20px;
}

.detail-alerts h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
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
  .technical-rooms { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .rooms-grid { grid-template-columns: 1fr; }
  .room-details { grid-template-columns: 1fr; }
  .room-stats { flex-wrap: wrap; gap: 12px; }
}
</style>