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
        <div class="loading-tip">Room & Area Registry</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="room-area-registry">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Room & Area Registry</h2>
        <p class="subtitle">Manage all rooms, spaces, and areas across buildings and floors</p>
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
        <div class="stat-icon">🚪</div>
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
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <div class="stat-value">{{ uniqueBuildingsCount }}</div>
          <div class="stat-label">Buildings</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgRoomArea }}</div>
          <div class="stat-label">Avg Room Area (sqm)</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by room name, number or type..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterBuilding" placeholder="Building" clearable style="width: 180px">
          <el-option label="All Buildings" value="all" />
          <el-option v-for="b in uniqueBuildingsList" :key="b" :label="b" :value="b" />
        </el-select>
        <el-select v-model="filterRoomType" placeholder="Room Type" clearable style="width: 160px">
          <el-option label="All Types" value="all" />
          <el-option label="Office" value="office" />
          <el-option label="Meeting Room" value="meeting" />
          <el-option label="Conference" value="conference" />
          <el-option label="Break Room" value="break" />
          <el-option label="Server Room" value="server" />
          <el-option label="Storage" value="storage" />
          <el-option label="Restroom" value="restroom" />
          <el-option label="Lobby" value="lobby" />
        </el-select>
        <el-select v-model="filterFloor" placeholder="Floor" clearable style="width: 130px">
          <el-option label="All Floors" value="all" />
          <el-option v-for="f in uniqueFloors" :key="f" :label="`Floor ${f}`" :value="f" />
        </el-select>
      </div>
    </div>

    <!-- Rooms Table -->
    <div class="rooms-table-container">
      <el-table :data="paginatedRooms" stripe style="width: 100%">
        <el-table-column prop="roomNumber" label="Room No." align="center" />
        <el-table-column prop="name" label="Room Name" align="center" />
        <el-table-column prop="buildingName" label="Building" align="center" />
        <el-table-column prop="floorLevel" label="Floor"  align="center" />
        <el-table-column label="Room Type" align="center">
          <template #default="{ row }">
            <span :class="['type-badge', row.roomType]">{{ getRoomTypeLabel(row.roomType) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Area"  align="center">
          <template #default="{ row }">
            {{ formatNumber(row.area) }} sqm
          </template>
        </el-table-column>
        <el-table-column label="Capacity"  align="center">
          <template #default="{ row }">
            {{ row.capacity || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Status"  align="center">
          <template #default="{ row }">
            <span :class="['status-badge', row.status]">{{ getStatusText(row.status) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="viewRoom(row)">View</el-button>
            <el-button type="info" link size="small" @click="editRoom(row)">Edit</el-button>
            <el-button type="danger" link size="small" @click="deleteRoom(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredRooms.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredRooms.length === 0 && rooms.length > 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <div class="empty-title">No matching rooms found</div>
      <div class="empty-desc">Try adjusting your search or filter criteria</div>
      <el-button @click="resetFilters">Reset Filters</el-button>
    </div>

    <div v-if="rooms.length === 0" class="empty-state">
      <div class="empty-icon">🚪</div>
      <div class="empty-title">No rooms registered</div>
      <div class="empty-desc">Add a room to start managing your space inventory</div>
      <el-button type="primary" @click="openAddRoomDialog">Add Room</el-button>
    </div>

    <!-- Add/Edit Room Dialog -->
    <el-dialog v-model="showRoomDialog" :title="dialogTitle" width="600px">
      <el-form :model="roomForm" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Room Number" required>
              <el-input v-model="roomForm.roomNumber" placeholder="e.g., 101, A-01" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Room Name">
              <el-input v-model="roomForm.name" placeholder="e.g., Executive Office" />
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
          <el-col :span="8">
            <el-form-item label="Room Type">
              <el-select v-model="roomForm.roomType" style="width: 100%">
                <el-option label="Office" value="office" />
                <el-option label="Meeting Room" value="meeting" />
                <el-option label="Conference" value="conference" />
                <el-option label="Break Room" value="break" />
                <el-option label="Server Room" value="server" />
                <el-option label="Storage" value="storage" />
                <el-option label="Restroom" value="restroom" />
                <el-option label="Lobby" value="lobby" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Area (sqm)">
              <el-input-number v-model="roomForm.area" :min="0" :step="5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Capacity">
              <el-input-number v-model="roomForm.capacity" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="roomForm.status">
            <el-radio label="available">Available</el-radio>
            <el-radio label="occupied">Occupied</el-radio>
            <el-radio label="maintenance">Maintenance</el-radio>
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
    <el-dialog v-model="showDetailDialog" :title="selectedRoom?.name || selectedRoom?.roomNumber" width="700px">
      <div v-if="selectedRoom">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Room Number">{{ selectedRoom.roomNumber }}</el-descriptions-item>
          <el-descriptions-item label="Room Name">{{ selectedRoom.name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedRoom.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Floor">Floor {{ selectedRoom.floorLevel }} ({{ selectedRoom.floorCode }})</el-descriptions-item>
          <el-descriptions-item label="Room Type">{{ getRoomTypeLabel(selectedRoom.roomType) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedRoom.status]">{{ getStatusText(selectedRoom.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Area">{{ formatNumber(selectedRoom.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Capacity">{{ selectedRoom.capacity || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Zone">{{ selectedRoom.zone || 'Not assigned' }}</el-descriptions-item>
          <el-descriptions-item label="Department">{{ selectedRoom.department || 'Not assigned' }}</el-descriptions-item>
          <el-descriptions-item label="Last Inspection">{{ selectedRoom.lastInspection || 'Not scheduled' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedRoom.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
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
import { Plus, RefreshRight, Search, Download, View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading room registry data...',
  'Fetching building information...',
  'Organizing room inventory...',
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

// Room interface
interface Room {
  id: number
  roomNumber: string
  name: string
  buildingId: number
  buildingName: string
  floorId: number
  floorLevel: number
  floorCode: string
  roomType: string
  area: number
  capacity: number
  status: string
  zone: string
  department: string
  lastInspection: string
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
  { id: 4, buildingId: 2, level: 1, code: 'G' },
  { id: 5, buildingId: 2, level: 2, code: '2F' },
  { id: 6, buildingId: 2, level: 3, code: '3F' },
  { id: 7, buildingId: 3, level: 1, code: '01' },
  { id: 8, buildingId: 3, level: 2, code: '02' }
])

// Sample rooms data
const rooms = ref<Room[]>([
  {
    id: 1,
    roomNumber: '101',
    name: 'Executive Office',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    roomType: 'office',
    area: 45,
    capacity: 4,
    status: 'occupied',
    zone: 'Executive Zone',
    department: 'Management',
    lastInspection: '2025-01-10',
    description: 'Corner office with city view'
  },
  {
    id: 2,
    roomNumber: '102',
    name: 'Conference Room A',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    roomType: 'conference',
    area: 65,
    capacity: 20,
    status: 'available',
    zone: 'Meeting Zone',
    department: 'Shared',
    lastInspection: '2025-01-10',
    description: 'Large conference room with AV equipment'
  },
  {
    id: 3,
    roomNumber: '201',
    name: 'Open Office',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    roomType: 'office',
    area: 120,
    capacity: 25,
    status: 'occupied',
    zone: 'IT Department',
    department: 'IT',
    lastInspection: '2025-01-12',
    description: 'Open plan workspace for IT team'
  },
  {
    id: 4,
    roomNumber: '202',
    name: 'Server Room',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 2,
    floorLevel: 2,
    floorCode: 'L2',
    roomType: 'server',
    area: 35,
    capacity: 0,
    status: 'occupied',
    zone: 'IT Zone',
    department: 'IT',
    lastInspection: '2025-01-08',
    description: 'Temperature-controlled server room'
  },
  {
    id: 5,
    roomNumber: 'G-01',
    name: 'Main Lobby',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 4,
    floorLevel: 1,
    floorCode: 'G',
    roomType: 'lobby',
    area: 180,
    capacity: 50,
    status: 'available',
    zone: 'Public Zone',
    department: 'Facilities',
    lastInspection: '2025-01-05',
    description: 'Building main entrance and reception'
  },
  {
    id: 6,
    roomNumber: 'G-02',
    name: 'Break Room',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 4,
    floorLevel: 1,
    floorCode: 'G',
    roomType: 'break',
    area: 45,
    capacity: 15,
    status: 'available',
    zone: 'Amenities',
    department: 'Shared',
    lastInspection: '2025-01-05',
    description: 'Pantry and break area with kitchen'
  },
  {
    id: 7,
    roomNumber: '2F-01',
    name: 'Meeting Room B',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 5,
    floorLevel: 2,
    floorCode: '2F',
    roomType: 'meeting',
    area: 28,
    capacity: 8,
    status: 'maintenance',
    zone: 'Meeting Zone',
    department: 'Shared',
    lastInspection: '2024-12-20',
    description: 'Small meeting room - under renovation'
  },
  {
    id: 8,
    roomNumber: '101',
    name: 'Storage Room',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 7,
    floorLevel: 1,
    floorCode: '01',
    roomType: 'storage',
    area: 55,
    capacity: 0,
    status: 'occupied',
    zone: 'Warehouse Zone',
    department: 'Operations',
    lastInspection: '2025-01-14',
    description: 'Equipment and supplies storage'
  },
  {
    id: 9,
    roomNumber: '102',
    name: 'Restroom North',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 7,
    floorLevel: 1,
    floorCode: '01',
    roomType: 'restroom',
    area: 25,
    capacity: 0,
    status: 'available',
    zone: 'Amenities',
    department: 'Facilities',
    lastInspection: '2025-01-14',
    description: 'Men\'s and women\'s restroom'
  },
  {
    id: 10,
    roomNumber: '201',
    name: 'R&D Lab',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 8,
    floorLevel: 2,
    floorCode: '02',
    roomType: 'office',
    area: 95,
    capacity: 12,
    status: 'occupied',
    zone: 'R&D Zone',
    department: 'Research',
    lastInspection: '2025-01-13',
    description: 'Research and development laboratory'
  }
])

// UI State
const searchText = ref('')
const filterBuilding = ref('all')
const filterRoomType = ref('all')
const filterFloor = ref('all')
const currentPage = ref(1)
const pageSize = ref(15)
const showRoomDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedRoom = ref<Room | null>(null)

const roomForm = ref({
  roomNumber: '',
  name: '',
  buildingId: 1,
  floorId: 1,
  roomType: 'office',
  area: 0,
  capacity: 0,
  status: 'available',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Room' : 'Add Room')

const totalRooms = computed(() => rooms.value.length)
const totalArea = computed(() => rooms.value.reduce((sum, r) => sum + r.area, 0))
const uniqueBuildingsCount = computed(() => new Set(rooms.value.map(r => r.buildingName)).size)
const avgRoomArea = computed(() => Math.round(totalArea.value / totalRooms.value))

const uniqueBuildingsList = computed(() => {
  return Array.from(new Set(rooms.value.map(r => r.buildingName)))
})

const uniqueFloors = computed(() => {
  return Array.from(new Set(rooms.value.map(r => r.floorLevel))).sort((a, b) => a - b)
})

const availableFloors = computed(() => {
  if (!roomForm.value.buildingId) return []
  return floors.value.filter(f => f.buildingId === roomForm.value.buildingId)
})

const filteredRooms = computed(() => {
  let filtered = [...rooms.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.roomNumber.toLowerCase().includes(keyword) ||
        (r.name && r.name.toLowerCase().includes(keyword))
    )
  }

  if (filterBuilding.value !== 'all') {
    filtered = filtered.filter(r => r.buildingName === filterBuilding.value)
  }

  if (filterRoomType.value !== 'all') {
    filtered = filtered.filter(r => r.roomType === filterRoomType.value)
  }

  if (filterFloor.value !== 'all') {
    filtered = filtered.filter(r => r.floorLevel === parseInt(filterFloor.value))
  }

  return filtered.sort((a, b) => {
    if (a.buildingName !== b.buildingName) return a.buildingName.localeCompare(b.buildingName)
    if (a.floorLevel !== b.floorLevel) return a.floorLevel - b.floorLevel
    return a.roomNumber.localeCompare(b.roomNumber)
  })
})

const paginatedRooms = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRooms.value.slice(start, end)
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getRoomTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    office: 'Office',
    meeting: 'Meeting Room',
    conference: 'Conference',
    break: 'Break Room',
    server: 'Server Room',
    storage: 'Storage',
    restroom: 'Restroom',
    lobby: 'Lobby'
  }
  return map[type] || type
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    available: 'Available',
    occupied: 'Occupied',
    maintenance: 'Maintenance'
  }
  return map[status] || status
}

const resetFilters = () => {
  searchText.value = ''
  filterBuilding.value = 'all'
  filterRoomType.value = 'all'
  filterFloor.value = 'all'
  currentPage.value = 1
}

// Pagination
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
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
    roomNumber: '',
    name: '',
    buildingId: buildings.value[0]?.id || 1,
    floorId: 1,
    roomType: 'office',
    area: 0,
    capacity: 0,
    status: 'available',
    description: ''
  }
  showRoomDialog.value = true
}

const editRoom = (room: Room) => {
  isEditing.value = true
  selectedRoom.value = room
  roomForm.value = {
    roomNumber: room.roomNumber,
    name: room.name,
    buildingId: room.buildingId,
    floorId: room.floorId,
    roomType: room.roomType,
    area: room.area,
    capacity: room.capacity,
    status: room.status,
    description: room.description || ''
  }
  showRoomDialog.value = true
}

const saveRoom = () => {
  if (!roomForm.value.roomNumber.trim()) {
    ElMessage.warning('Please enter room number')
    return
  }

  const building = buildings.value.find(b => b.id === roomForm.value.buildingId)
  const floor = floors.value.find(f => f.id === roomForm.value.floorId)

  if (!building || !floor) {
    ElMessage.warning('Please select building and floor')
    return
  }

  if (isEditing.value && selectedRoom.value) {
    const index = rooms.value.findIndex(r => r.id === selectedRoom.value!.id)
    if (index !== -1) {
      rooms.value[index] = {
        ...rooms.value[index],
        roomNumber: roomForm.value.roomNumber,
        name: roomForm.value.name,
        buildingId: roomForm.value.buildingId,
        buildingName: building.name,
        floorId: roomForm.value.floorId,
        floorLevel: floor.level,
        floorCode: floor.code,
        roomType: roomForm.value.roomType,
        area: roomForm.value.area,
        capacity: roomForm.value.capacity,
        status: roomForm.value.status,
        description: roomForm.value.description
      }
      ElMessage.success('Room updated successfully')
    }
  } else {
    const existingRoomsOnFloor = rooms.value.filter(r => r.floorId === roomForm.value.floorId)
    const newRoom: Room = {
      id: Date.now(),
      roomNumber: roomForm.value.roomNumber,
      name: roomForm.value.name,
      buildingId: roomForm.value.buildingId,
      buildingName: building.name,
      floorId: roomForm.value.floorId,
      floorLevel: floor.level,
      floorCode: floor.code,
      roomType: roomForm.value.roomType,
      area: roomForm.value.area,
      capacity: roomForm.value.capacity,
      status: roomForm.value.status,
      zone: 'Not assigned',
      department: 'Not assigned',
      lastInspection: new Date().toISOString().split('T')[0],
      description: roomForm.value.description
    }
    rooms.value.push(newRoom)
    ElMessage.success('Room added successfully')
  }

  showRoomDialog.value = false
}

const viewRoom = (room: Room) => {
  selectedRoom.value = room
  showDetailDialog.value = true
}

const deleteRoom = (room: Room) => {
  ElMessageBox.confirm(
      `Delete room "${room.roomNumber}${room.name ? ' - ' + room.name : ''}"? This action cannot be undone.`,
      'Delete Room',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = rooms.value.findIndex(r => r.id === room.id)
    if (index !== -1) {
      rooms.value.splice(index, 1)
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
  a.download = `room_registry_${new Date().toISOString().split('T')[0]}.json`
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
.room-area-registry {
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

/* Table Container */
.rooms-table-container {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.pagination-wrapper {
  padding: 16px 20px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #ebeef5;
}

/* Badges */
.type-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.type-badge.office { background: #e6f7ff; color: #409eff; }
.type-badge.meeting { background: #e8f5e9; color: #67c23a; }
.type-badge.conference { background: #f3e5f5; color: #9c27b0; }
.type-badge.break { background: #fff7e6; color: #e6a23c; }
.type-badge.server { background: #ffefef; color: #f56c6c; }
.type-badge.storage { background: #f5f5f5; color: #909399; }
.type-badge.restroom { background: #e0f7fa; color: #00acc1; }
.type-badge.lobby { background: #fff3e0; color: #ff9800; }

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.available { background: #e8f5e9; color: #67c23a; }
.status-badge.occupied { background: #e6f7ff; color: #409eff; }
.status-badge.maintenance { background: #ffefef; color: #f56c6c; }

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
  .room-area-registry { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .rooms-table-container { overflow-x: auto; }
  .rooms-table-container :deep(.el-table) { min-width: 800px; }
}
</style>