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
        <div class="loading-tip">White Space Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="white-space-management">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>White Space Management</h2>
        <p class="subtitle">Manage available/unoccupied spaces, leasing, and space utilization</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddSpaceDialog">
          <el-icon><Plus /></el-icon> Add Space
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
        <div class="stat-icon">📐</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalSpaces }}</div>
          <div class="stat-label">Total Spaces</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(availableArea) }}</div>
          <div class="stat-label">Available Area (sqm)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgUtilization }}%</div>
          <div class="stat-label">Avg Utilization</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-info">
          <div class="stat-value">${{ formatNumber(totalPotentialRevenue) }}k</div>
          <div class="stat-label">Potential Revenue</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by space name, building or zone..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Available" value="available" />
          <el-option label="Leased" value="leased" />
          <el-option label="Reserved" value="reserved" />
          <el-option label="Under Negotiation" value="negotiation" />
        </el-select>
        <el-select v-model="filterSpaceType" placeholder="Space Type" clearable style="width: 160px">
          <el-option label="All Types" value="all" />
          <el-option label="Office" value="office" />
          <el-option label="Retail" value="retail" />
          <el-option label="Warehouse" value="warehouse" />
          <el-option label="Data Center" value="datacenter" />
          <el-option label="Common Area" value="common" />
        </el-select>
      </div>
    </div>

    <!-- White Spaces Grid -->
    <div class="spaces-grid">
      <div v-for="space in filteredSpaces" :key="space.id" class="space-card" :class="space.status">
        <div class="space-header">
          <div class="space-icon">{{ getSpaceIcon(space.spaceType) }}</div>
          <div class="space-info">
            <div class="space-name">{{ space.name }}</div>
            <div class="space-code">{{ space.code }}</div>
          </div>
          <div class="space-status">
            <span class="status-badge" :class="space.status">{{ getStatusText(space.status) }}</span>
          </div>
        </div>

        <div class="space-location">
          <el-icon><Location /></el-icon>
          <span>{{ space.buildingName }} - Floor {{ space.floorLevel }} ({{ space.floorCode }})</span>
        </div>

        <div class="space-details">
          <div class="detail-row">
            <span class="detail-label">Area</span>
            <span class="detail-value">{{ formatNumber(space.area) }} sqm</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Space Type</span>
            <span class="detail-value">{{ getSpaceTypeLabel(space.spaceType) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Utilization</span>
            <span class="detail-value">{{ space.utilization }}%</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Monthly Rent</span>
            <span class="detail-value">${{ formatNumber(space.monthlyRent) }}</span>
          </div>
        </div>

        <div class="space-stats">
          <div class="stat-item" v-if="space.status === 'leased'">
            <div class="stat-number">{{ space.tenantName || '-' }}</div>
            <div class="stat-label-sm">Tenant</div>
          </div>
          <div class="stat-item" v-if="space.status === 'leased'">
            <div class="stat-number">{{ space.leaseEndDate || '-' }}</div>
            <div class="stat-label-sm">Lease End</div>
          </div>
          <div class="stat-item" v-if="space.status === 'available'">
            <div class="stat-number">{{ space.vacantDays }} days</div>
            <div class="stat-label-sm">Vacant</div>
          </div>
          <div class="stat-item" v-if="space.status === 'reserved'">
            <div class="stat-number">{{ space.reservedFor || '-' }}</div>
            <div class="stat-label-sm">Reserved For</div>
          </div>
        </div>

        <div class="space-actions">
          <el-button size="small" type="primary" plain @click="viewSpace(space)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editSpace(space)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button v-if="space.status === 'available'" size="small" type="success" plain @click="markAsLeased(space)">
            <el-icon><CircleCheck /></el-icon> Mark Leased
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteSpace(space)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredSpaces.length === 0" class="empty-state">
      <div class="empty-icon">📐</div>
      <div class="empty-title">No spaces found</div>
      <div class="empty-desc">Add a white space to start managing available areas</div>
      <el-button type="primary" @click="openAddSpaceDialog">Add Space</el-button>
    </div>

    <!-- Add/Edit Space Dialog -->
    <el-dialog v-model="showSpaceDialog" :title="dialogTitle" width="650px">
      <el-form :model="spaceForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Space Name" required>
              <el-input v-model="spaceForm.name" placeholder="Enter space name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Space Code">
              <el-input v-model="spaceForm.code" placeholder="e.g., SP-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Building" required>
          <el-select v-model="spaceForm.buildingId" placeholder="Select building" style="width: 100%">
            <el-option v-for="b in buildings" :key="b.id" :label="b.name" :value="b.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Floor" required>
          <el-select v-model="spaceForm.floorId" placeholder="Select floor" style="width: 100%" :disabled="!spaceForm.buildingId">
            <el-option v-for="f in availableFloors" :key="f.id" :label="`Floor ${f.level} - ${f.code}`" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Space Type">
              <el-select v-model="spaceForm.spaceType" style="width: 100%">
                <el-option label="Office" value="office" />
                <el-option label="Retail" value="retail" />
                <el-option label="Warehouse" value="warehouse" />
                <el-option label="Data Center" value="datacenter" />
                <el-option label="Common Area" value="common" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Area (sqm)">
              <el-input-number v-model="spaceForm.area" :min="0" :step="10" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Status">
              <el-select v-model="spaceForm.status" style="width: 100%">
                <el-option label="Available" value="available" />
                <el-option label="Leased" value="leased" />
                <el-option label="Reserved" value="reserved" />
                <el-option label="Under Negotiation" value="negotiation" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Monthly Rent (SGD)">
              <el-input-number v-model="spaceForm.monthlyRent" :min="0" :step="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="spaceForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSpaceDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveSpace">Save Space</el-button>
      </template>
    </el-dialog>

    <!-- Space Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedSpace?.name" width="750px">
      <div v-if="selectedSpace">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Space ID">{{ selectedSpace.id }}</el-descriptions-item>
          <el-descriptions-item label="Space Code">{{ selectedSpace.code }}</el-descriptions-item>
          <el-descriptions-item label="Building">{{ selectedSpace.buildingName }}</el-descriptions-item>
          <el-descriptions-item label="Floor">Floor {{ selectedSpace.floorLevel }} ({{ selectedSpace.floorCode }})</el-descriptions-item>
          <el-descriptions-item label="Space Type">{{ getSpaceTypeLabel(selectedSpace.spaceType) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedSpace.status]">{{ getStatusText(selectedSpace.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Area">{{ formatNumber(selectedSpace.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Utilization">{{ selectedSpace.utilization }}%</el-descriptions-item>
          <el-descriptions-item label="Monthly Rent">${{ formatNumber(selectedSpace.monthlyRent) }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedSpace.tenantName" label="Tenant">{{ selectedSpace.tenantName }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedSpace.leaseStartDate" label="Lease Start">{{ selectedSpace.leaseStartDate }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedSpace.leaseEndDate" label="Lease End">{{ selectedSpace.leaseEndDate }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedSpace.vacantDays > 0" label="Vacant Days">{{ selectedSpace.vacantDays }} days</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedSpace.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editSpace(selectedSpace); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>

    <!-- Mark as Leased Dialog -->
    <el-dialog v-model="showLeaseDialog" title="Mark Space as Leased" width="500px">
      <el-form :model="leaseForm" label-width="120px">
        <el-form-item label="Space">
          <span>{{ selectedSpace?.name }}</span>
        </el-form-item>
        <el-form-item label="Tenant Name" required>
          <el-input v-model="leaseForm.tenantName" placeholder="Enter tenant name" />
        </el-form-item>
        <el-form-item label="Lease Start Date">
          <el-date-picker v-model="leaseForm.leaseStartDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Lease End Date">
          <el-date-picker v-model="leaseForm.leaseEndDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Monthly Rent">
          <el-input-number v-model="leaseForm.monthlyRent" :min="0" :step="100" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showLeaseDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmMarkAsLeased">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading white space data...',
  'Fetching space information...',
  'Calculating utilization rates...',
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

// White Space interface
interface WhiteSpace {
  id: number
  name: string
  code: string
  buildingId: number
  buildingName: string
  floorId: number
  floorLevel: number
  floorCode: string
  spaceType: string
  area: number
  utilization: number
  status: string
  monthlyRent: number
  tenantName: string | null
  leaseStartDate: string | null
  leaseEndDate: string | null
  vacantDays: number
  reservedFor: string | null
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
  { id: 6, buildingId: 3, level: 1, code: '01' },
  { id: 7, buildingId: 3, level: 2, code: '02' }
])

// Sample white spaces data
const whiteSpaces = ref<WhiteSpace[]>([
  {
    id: 1,
    name: 'East Wing Office Suite',
    code: 'WS-EW-01',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    spaceType: 'office',
    area: 450,
    utilization: 0,
    status: 'available',
    monthlyRent: 18000,
    tenantName: null,
    leaseStartDate: null,
    leaseEndDate: null,
    vacantDays: 45,
    reservedFor: null,
    description: 'Premium office space with city view'
  },
  {
    id: 2,
    name: 'Retail Space - Lobby Level',
    code: 'WS-RTL-02',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 1,
    floorLevel: 1,
    floorCode: 'L1',
    spaceType: 'retail',
    area: 280,
    utilization: 0,
    status: 'negotiation',
    monthlyRent: 14000,
    tenantName: null,
    leaseStartDate: null,
    leaseEndDate: null,
    vacantDays: 30,
    reservedFor: null,
    description: 'Prime retail space near main entrance'
  },
  {
    id: 3,
    name: 'Data Center White Space',
    code: 'WS-DC-03',
    buildingId: 1,
    buildingName: 'Marina Bay Tower',
    floorId: 3,
    floorLevel: 3,
    floorCode: 'L3',
    spaceType: 'datacenter',
    area: 120,
    utilization: 0,
    status: 'reserved',
    monthlyRent: 15000,
    tenantName: null,
    leaseStartDate: null,
    leaseEndDate: null,
    vacantDays: 0,
    reservedFor: 'CloudTech Solutions',
    description: 'Raised floor data center space with cooling'
  },
  {
    id: 4,
    name: 'West Wing Office',
    code: 'WS-WW-04',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 5,
    floorLevel: 2,
    floorCode: '2F',
    spaceType: 'office',
    area: 320,
    utilization: 0,
    status: 'available',
    monthlyRent: 12800,
    tenantName: null,
    leaseStartDate: null,
    leaseEndDate: null,
    vacantDays: 60,
    reservedFor: null,
    description: 'Open plan office space'
  },
  {
    id: 5,
    name: 'Warehouse Space Unit A',
    code: 'WS-WH-05',
    buildingId: 3,
    buildingName: 'Tech Park North',
    floorId: 6,
    floorLevel: 1,
    floorCode: '01',
    spaceType: 'warehouse',
    area: 800,
    utilization: 0,
    status: 'available',
    monthlyRent: 20000,
    tenantName: null,
    leaseStartDate: null,
    leaseEndDate: null,
    vacantDays: 20,
    reservedFor: null,
    description: 'High ceiling warehouse with loading dock'
  },
  {
    id: 6,
    name: 'Common Area - Sky Garden',
    code: 'WS-CA-06',
    buildingId: 2,
    buildingName: 'Central Plaza',
    floorId: 5,
    floorLevel: 2,
    floorCode: '2F',
    spaceType: 'common',
    area: 500,
    utilization: 65,
    status: 'available',
    monthlyRent: 0,
    tenantName: null,
    leaseStartDate: null,
    leaseEndDate: null,
    vacantDays: 0,
    reservedFor: null,
    description: 'Common area for events and gatherings'
  }
])

// UI State
const searchText = ref('')
const filterStatus = ref('all')
const filterSpaceType = ref('all')
const showSpaceDialog = ref(false)
const showDetailDialog = ref(false)
const showLeaseDialog = ref(false)
const isEditing = ref(false)
const selectedSpace = ref<WhiteSpace | null>(null)

const spaceForm = ref({
  name: '',
  code: '',
  buildingId: 1,
  floorId: 1,
  spaceType: 'office',
  area: 0,
  status: 'available',
  monthlyRent: 0,
  description: ''
})

const leaseForm = ref({
  tenantName: '',
  leaseStartDate: null,
  leaseEndDate: null,
  monthlyRent: 0
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Space' : 'Add Space')

const totalSpaces = computed(() => whiteSpaces.value.length)
const availableArea = computed(() => whiteSpaces.value.filter(s => s.status === 'available').reduce((sum, s) => sum + s.area, 0))
const avgUtilization = computed(() => Math.round(whiteSpaces.value.reduce((sum, s) => sum + s.utilization, 0) / whiteSpaces.value.length))
const totalPotentialRevenue = computed(() => whiteSpaces.value.filter(s => s.status === 'available').reduce((sum, s) => sum + s.monthlyRent, 0) / 1000)

const availableFloors = computed(() => {
  if (!spaceForm.value.buildingId) return []
  return floors.value.filter(f => f.buildingId === spaceForm.value.buildingId)
})

const filteredSpaces = computed(() => {
  let filtered = [...whiteSpaces.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(keyword) ||
        s.code.toLowerCase().includes(keyword) ||
        s.buildingName.toLowerCase().includes(keyword)
    )
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(s => s.status === filterStatus.value)
  }

  if (filterSpaceType.value !== 'all') {
    filtered = filtered.filter(s => s.spaceType === filterSpaceType.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(0) + 'k'
  return num.toLocaleString()
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    available: 'Available',
    leased: 'Leased',
    reserved: 'Reserved',
    negotiation: 'Negotiation'
  }
  return map[status] || status
}

const getSpaceIcon = (type: string) => {
  const map: Record<string, string> = {
    office: '💼',
    retail: '🛍️',
    warehouse: '📦',
    datacenter: '💿',
    common: '🏞️'
  }
  return map[type] || '📍'
}

const getSpaceTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    office: 'Office',
    retail: 'Retail',
    warehouse: 'Warehouse',
    datacenter: 'Data Center',
    common: 'Common Area'
  }
  return map[type] || type
}

// Watch building change
watch(() => spaceForm.value.buildingId, (newVal) => {
  if (newVal && availableFloors.value.length > 0) {
    spaceForm.value.floorId = availableFloors.value[0].id
  }
})

// Space CRUD operations
const openAddSpaceDialog = () => {
  isEditing.value = false
  spaceForm.value = {
    name: '',
    code: '',
    buildingId: buildings.value[0]?.id || 1,
    floorId: 1,
    spaceType: 'office',
    area: 0,
    status: 'available',
    monthlyRent: 0,
    description: ''
  }
  showSpaceDialog.value = true
}

const editSpace = (space: WhiteSpace) => {
  isEditing.value = true
  selectedSpace.value = space
  spaceForm.value = {
    name: space.name,
    code: space.code,
    buildingId: space.buildingId,
    floorId: space.floorId,
    spaceType: space.spaceType,
    area: space.area,
    status: space.status,
    monthlyRent: space.monthlyRent,
    description: space.description || ''
  }
  showSpaceDialog.value = true
}

const saveSpace = () => {
  if (!spaceForm.value.name.trim()) {
    ElMessage.warning('Please enter space name')
    return
  }

  const building = buildings.value.find(b => b.id === spaceForm.value.buildingId)
  const floor = floors.value.find(f => f.id === spaceForm.value.floorId)

  if (!building || !floor) {
    ElMessage.warning('Please select building and floor')
    return
  }

  if (isEditing.value && selectedSpace.value) {
    const index = whiteSpaces.value.findIndex(s => s.id === selectedSpace.value!.id)
    if (index !== -1) {
      whiteSpaces.value[index] = {
        ...whiteSpaces.value[index],
        name: spaceForm.value.name,
        code: spaceForm.value.code,
        buildingId: spaceForm.value.buildingId,
        buildingName: building.name,
        floorId: spaceForm.value.floorId,
        floorLevel: floor.level,
        floorCode: floor.code,
        spaceType: spaceForm.value.spaceType,
        area: spaceForm.value.area,
        status: spaceForm.value.status,
        monthlyRent: spaceForm.value.monthlyRent,
        description: spaceForm.value.description
      }
      ElMessage.success('Space updated successfully')
    }
  } else {
    const newSpace: WhiteSpace = {
      id: Date.now(),
      name: spaceForm.value.name,
      code: spaceForm.value.code || `WS-${whiteSpaces.value.length + 1}`,
      buildingId: spaceForm.value.buildingId,
      buildingName: building.name,
      floorId: spaceForm.value.floorId,
      floorLevel: floor.level,
      floorCode: floor.code,
      spaceType: spaceForm.value.spaceType,
      area: spaceForm.value.area,
      utilization: 0,
      status: spaceForm.value.status,
      monthlyRent: spaceForm.value.monthlyRent,
      tenantName: null,
      leaseStartDate: null,
      leaseEndDate: null,
      vacantDays: 0,
      reservedFor: null,
      description: spaceForm.value.description
    }
    whiteSpaces.value.push(newSpace)
    ElMessage.success('Space added successfully')
  }

  showSpaceDialog.value = false
}

const viewSpace = (space: WhiteSpace) => {
  selectedSpace.value = space
  showDetailDialog.value = true
}

const deleteSpace = (space: WhiteSpace) => {
  ElMessageBox.confirm(
      `Delete space "${space.name}"? This action cannot be undone.`,
      'Delete Space',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = whiteSpaces.value.findIndex(s => s.id === space.id)
    if (index !== -1) {
      whiteSpaces.value.splice(index, 1)
      ElMessage.success('Space deleted successfully')
    }
  }).catch(() => {})
}

const markAsLeased = (space: WhiteSpace) => {
  selectedSpace.value = space
  leaseForm.value = {
    tenantName: '',
    leaseStartDate: null,
    leaseEndDate: null,
    monthlyRent: space.monthlyRent
  }
  showLeaseDialog.value = true
}

const confirmMarkAsLeased = () => {
  if (!leaseForm.value.tenantName.trim()) {
    ElMessage.warning('Please enter tenant name')
    return
  }

  if (selectedSpace.value) {
    const index = whiteSpaces.value.findIndex(s => s.id === selectedSpace.value!.id)
    if (index !== -1) {
      whiteSpaces.value[index] = {
        ...whiteSpaces.value[index],
        status: 'leased',
        tenantName: leaseForm.value.tenantName,
        leaseStartDate: leaseForm.value.leaseStartDate ? new Date(leaseForm.value.leaseStartDate).toISOString().split('T')[0] : null,
        leaseEndDate: leaseForm.value.leaseEndDate ? new Date(leaseForm.value.leaseEndDate).toISOString().split('T')[0] : null,
        monthlyRent: leaseForm.value.monthlyRent,
        vacantDays: 0
      }
      ElMessage.success('Space marked as leased')
    }
  }
  showLeaseDialog.value = false
}

const exportData = () => {
  const data = JSON.stringify(filteredSpaces.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `white_spaces_${new Date().toISOString().split('T')[0]}.json`
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
.white-space-management {
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

/* Spaces Grid */
.spaces-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.space-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.space-card.leased { border-left-color: #409eff; }
.space-card.reserved { border-left-color: #e6a23c; }
.space-card.negotiation { border-left-color: #f59e0b; }
.space-card.available { border-left-color: #67c23a; }

.space-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.space-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.space-icon {
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

.space-info {
  flex: 1;
}

.space-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.space-code {
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

.status-badge.available { background: #e8f5e9; color: #67c23a; }
.status-badge.leased { background: #e6f7ff; color: #409eff; }
.status-badge.reserved { background: #fff7e6; color: #e6a23c; }
.status-badge.negotiation { background: #fff7e6; color: #f59e0b; }

.space-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.space-details {
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

.space-stats {
  margin-bottom: 16px;
  padding: 8px 0;
}

.stat-item {
  text-align: center;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 8px;
}

.stat-number {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.stat-label-sm {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

.space-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
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
  .white-space-management { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .spaces-grid { grid-template-columns: 1fr; }
  .space-details { grid-template-columns: 1fr; }
}
</style>