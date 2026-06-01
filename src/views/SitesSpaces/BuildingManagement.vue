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
        <div class="loading-tip">Building Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="building-management">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Building Management</h2>
        <p class="subtitle">Manage building information, structural details, and operational status</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddBuildingDialog">
          <el-icon><Plus /></el-icon> Add Building
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
          <div class="stat-value">{{ buildings.length }}</div>
          <div class="stat-label">Total Buildings</div>
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
          <div class="stat-value">{{ activeCount }}</div>
          <div class="stat-label">Active Buildings</div>
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
        <el-input v-model="searchText" placeholder="Search by building name, code or address..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Active" value="active" />
          <el-option label="Under Maintenance" value="maintenance" />
          <el-option label="Inactive" value="inactive" />
        </el-select>
        <el-select v-model="filterType" placeholder="Type" clearable style="width: 140px">
          <el-option label="All Types" value="all" />
          <el-option label="Office" value="office" />
          <el-option label="Retail" value="retail" />
          <el-option label="Industrial" value="industrial" />
          <el-option label="Mixed Use" value="mixed" />
          <el-option label="Data Center" value="datacenter" />
        </el-select>
      </div>
    </div>

    <!-- Buildings Grid -->
    <div class="buildings-grid">
      <div v-for="building in filteredBuildings" :key="building.id" class="building-card" :class="building.status">
        <div class="building-header">
          <div class="building-icon" :style="{ background: getBuildingColor(building.type) }">
            {{ getBuildingIcon(building.type) }}
          </div>
          <div class="building-info">
            <div class="building-name">{{ building.name }}</div>
            <div class="building-code">{{ building.code }}</div>
          </div>
          <div class="building-status">
            <span class="status-badge" :class="building.status">{{ getStatusText(building.status) }}</span>
          </div>
        </div>

        <div class="building-details">
          <div class="detail-row">
            <span class="detail-label">📍 Location</span>
            <span class="detail-value">{{ building.address }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">📏 Area</span>
            <span class="detail-value">{{ formatNumber(building.area) }} sqm</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🏗️ Floors</span>
            <span class="detail-value">{{ building.floors }} floors</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">📅 Built</span>
            <span class="detail-value">{{ building.yearBuilt }}</span>
          </div>
        </div>

        <div class="building-stats">
          <div class="stat-item">
            <span class="stat-number">{{ building.occupancy }}%</span>
            <span class="stat-label-sm">Occupancy</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ building.devices }}</span>
            <span class="stat-label-sm">Devices</span>
          </div>
          <div class="stat-item">
            <span class="stat-number">{{ building.floors }}</span>
            <span class="stat-label-sm">Floors</span>
          </div>
        </div>

        <div class="building-actions">
          <el-button size="small" type="primary" plain @click="viewBuilding(building)">
            <el-icon><View /></el-icon> View
          </el-button>
          <el-button size="small" type="info" plain @click="editBuilding(building)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteBuilding(building)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredBuildings.length === 0" class="empty-state">
      <div class="empty-icon">🏢</div>
      <div class="empty-title">No buildings found</div>
      <div class="empty-desc">Add a building to get started</div>
      <el-button type="primary" @click="openAddBuildingDialog">Add Building</el-button>
    </div>

    <!-- Add/Edit Building Dialog -->
    <el-dialog v-model="showBuildingDialog" :title="dialogTitle" width="600px">
      <el-form :model="buildingForm" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Building Name" required>
              <el-input v-model="buildingForm.name" placeholder="Enter building name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Building Code" required>
              <el-input v-model="buildingForm.code" placeholder="e.g., BLD-A-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Address" required>
          <el-input v-model="buildingForm.address" placeholder="Enter street address" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Building Type">
              <el-select v-model="buildingForm.type" style="width: 100%">
                <el-option label="Office" value="office" />
                <el-option label="Retail" value="retail" />
                <el-option label="Industrial" value="industrial" />
                <el-option label="Mixed Use" value="mixed" />
                <el-option label="Data Center" value="datacenter" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Number of Floors">
              <el-input-number v-model="buildingForm.floors" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Total Area (sqm)">
              <el-input-number v-model="buildingForm.area" :min="0" :step="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Year Built">
              <el-input-number v-model="buildingForm.yearBuilt" :min="1900" :max="2025" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Status">
              <el-select v-model="buildingForm.status" style="width: 100%">
                <el-option label="Active" value="active" />
                <el-option label="Under Maintenance" value="maintenance" />
                <el-option label="Inactive" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="buildingForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBuildingDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveBuilding">Save Building</el-button>
      </template>
    </el-dialog>

    <!-- Building Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedBuilding?.name" width="700px">
      <div v-if="selectedBuilding">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Building ID">{{ selectedBuilding.id }}</el-descriptions-item>
          <el-descriptions-item label="Building Code">{{ selectedBuilding.code }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedBuilding.status]">{{ getStatusText(selectedBuilding.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Type">{{ getTypeLabel(selectedBuilding.type) }}</el-descriptions-item>
          <el-descriptions-item label="Address" :span="2">{{ selectedBuilding.address }}</el-descriptions-item>
          <el-descriptions-item label="Total Area">{{ formatNumber(selectedBuilding.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Number of Floors">{{ selectedBuilding.floors }}</el-descriptions-item>
          <el-descriptions-item label="Year Built">{{ selectedBuilding.yearBuilt }}</el-descriptions-item>
          <el-descriptions-item label="Occupancy Rate">{{ selectedBuilding.occupancy }}%</el-descriptions-item>
          <el-descriptions-item label="Active Devices">{{ selectedBuilding.devices }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedBuilding.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Last Inspection">{{ selectedBuilding.lastInspection || '2025-01-15' }}</el-descriptions-item>
          <el-descriptions-item label="Next Inspection">{{ selectedBuilding.nextInspection || '2025-04-15' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editBuilding(selectedBuilding); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading building data...',
  'Fetching building information...',
  'Organizing by type...',
  'Almost ready...'
]

// Building interface
interface Building {
  id: number
  name: string
  code: string
  type: string
  status: string
  address: string
  area: number
  floors: number
  yearBuilt: number
  occupancy: number
  devices: number
  description: string
  lastInspection: string
  nextInspection: string
  manager: string
}

// Sample buildings data
const buildings = ref<Building[]>([
  {
    id: 1,
    name: 'Marina Bay Tower',
    code: 'MBT-01',
    type: 'office',
    status: 'active',
    address: '8 Marina Boulevard, Singapore 018981',
    area: 45000,
    floors: 32,
    yearBuilt: 2015,
    occupancy: 92,
    devices: 1240,
    description: 'Main corporate headquarters with smart building systems',
    lastInspection: '2025-01-10',
    nextInspection: '2025-04-10',
    manager: 'Johnathan Lee'
  },
  {
    id: 2,
    name: 'Central Plaza',
    code: 'CP-02',
    type: 'office',
    status: 'active',
    address: '3 Central Boulevard, Singapore 018984',
    area: 38000,
    floors: 28,
    yearBuilt: 2018,
    occupancy: 88,
    devices: 980,
    description: 'Mixed-use commercial tower',
    lastInspection: '2025-01-05',
    nextInspection: '2025-04-05',
    manager: 'Sarah Chen'
  },
  {
    id: 3,
    name: 'Tech Park North',
    code: 'TPN-03',
    type: 'industrial',
    status: 'active',
    address: '15 North Coast Drive, Singapore 798321',
    area: 25000,
    floors: 3,
    yearBuilt: 2020,
    occupancy: 95,
    devices: 560,
    description: 'Light industrial and R&D facility',
    lastInspection: '2025-01-12',
    nextInspection: '2025-04-12',
    manager: 'Michael Tan'
  },
  {
    id: 4,
    name: 'Retail Pavilion',
    code: 'RP-04',
    type: 'retail',
    status: 'active',
    address: '88 Orchard Road, Singapore 238858',
    area: 12000,
    floors: 5,
    yearBuilt: 2012,
    occupancy: 98,
    devices: 320,
    description: 'Premium retail and dining destination',
    lastInspection: '2025-01-08',
    nextInspection: '2025-04-08',
    manager: 'Lisa Wong'
  },
  {
    id: 5,
    name: 'Data Hub South',
    code: 'DHS-05',
    type: 'datacenter',
    status: 'maintenance',
    address: '50 Science Park Road, Singapore 117586',
    area: 18000,
    floors: 4,
    yearBuilt: 2022,
    occupancy: 75,
    devices: 2450,
    description: 'Tier IV data center facility',
    lastInspection: '2025-01-02',
    nextInspection: '2025-04-02',
    manager: 'David Lim'
  },
  {
    id: 6,
    name: 'Heritage Building',
    code: 'HB-06',
    type: 'mixed',
    status: 'active',
    address: '45 Boat Quay, Singapore 049834',
    area: 3200,
    floors: 4,
    yearBuilt: 1998,
    occupancy: 85,
    devices: 180,
    description: 'Conserved shophouse with modern amenities',
    lastInspection: '2025-01-14',
    nextInspection: '2025-04-14',
    manager: 'Amanda Ng'
  }
])

// UI State
const searchText = ref('')
const filterStatus = ref('all')
const filterType = ref('all')
const showBuildingDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedBuilding = ref<Building | null>(null)

const buildingForm = ref({
  name: '',
  code: '',
  type: 'office',
  status: 'active',
  address: '',
  area: 0,
  floors: 1,
  yearBuilt: 2000,
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Building' : 'Add Building')

const totalArea = computed(() => buildings.value.reduce((sum, b) => sum + b.area, 0))
const activeCount = computed(() => buildings.value.filter(b => b.status === 'active').length)
const avgOccupancy = computed(() => Math.round(buildings.value.reduce((sum, b) => sum + b.occupancy, 0) / buildings.value.length))

const filteredBuildings = computed(() => {
  let filtered = [...buildings.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(b =>
        b.name.toLowerCase().includes(keyword) ||
        b.code.toLowerCase().includes(keyword) ||
        b.address.toLowerCase().includes(keyword)
    )
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(b => b.status === filterStatus.value)
  }

  if (filterType.value !== 'all') {
    filtered = filtered.filter(b => b.type === filterType.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: 'Active',
    maintenance: 'Maintenance',
    inactive: 'Inactive'
  }
  return map[status] || status
}

const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    office: 'Office',
    retail: 'Retail',
    industrial: 'Industrial',
    mixed: 'Mixed Use',
    datacenter: 'Data Center'
  }
  return map[type] || type
}

const getBuildingIcon = (type: string) => {
  const map: Record<string, string> = {
    office: '🏢',
    retail: '🛍️',
    industrial: '🏭',
    mixed: '🏙️',
    datacenter: '💿'
  }
  return map[type] || '🏢'
}

const getBuildingColor = (type: string) => {
  const map: Record<string, string> = {
    office: 'linear-gradient(135deg, #667eea, #764ba2)',
    retail: 'linear-gradient(135deg, #f093fb, #f5576c)',
    industrial: 'linear-gradient(135deg, #4facfe, #00f2fe)',
    mixed: 'linear-gradient(135deg, #fa709a, #fee140)',
    datacenter: 'linear-gradient(135deg, #a8edea, #fed6e3)'
  }
  return map[type] || 'linear-gradient(135deg, #667eea, #764ba2)'
}

// Building CRUD operations
const openAddBuildingDialog = () => {
  isEditing.value = false
  buildingForm.value = {
    name: '',
    code: '',
    type: 'office',
    status: 'active',
    address: '',
    area: 0,
    floors: 1,
    yearBuilt: 2000,
    description: ''
  }
  showBuildingDialog.value = true
}

const editBuilding = (building: Building) => {
  isEditing.value = true
  selectedBuilding.value = building
  buildingForm.value = {
    name: building.name,
    code: building.code,
    type: building.type,
    status: building.status,
    address: building.address,
    area: building.area,
    floors: building.floors,
    yearBuilt: building.yearBuilt,
    description: building.description || ''
  }
  showBuildingDialog.value = true
}

const saveBuilding = () => {
  if (!buildingForm.value.name.trim()) {
    ElMessage.warning('Please enter building name')
    return
  }
  if (!buildingForm.value.code.trim()) {
    ElMessage.warning('Please enter building code')
    return
  }
  if (!buildingForm.value.address.trim()) {
    ElMessage.warning('Please enter address')
    return
  }

  if (isEditing.value && selectedBuilding.value) {
    const index = buildings.value.findIndex(b => b.id === selectedBuilding.value!.id)
    if (index !== -1) {
      buildings.value[index] = {
        ...buildings.value[index],
        name: buildingForm.value.name,
        code: buildingForm.value.code,
        type: buildingForm.value.type,
        status: buildingForm.value.status,
        address: buildingForm.value.address,
        area: buildingForm.value.area,
        floors: buildingForm.value.floors,
        yearBuilt: buildingForm.value.yearBuilt,
        description: buildingForm.value.description
      }
      ElMessage.success('Building updated successfully')
    }
  } else {
    const newBuilding: Building = {
      id: Date.now(),
      name: buildingForm.value.name,
      code: buildingForm.value.code,
      type: buildingForm.value.type,
      status: buildingForm.value.status,
      address: buildingForm.value.address,
      area: buildingForm.value.area,
      floors: buildingForm.value.floors,
      yearBuilt: buildingForm.value.yearBuilt,
      occupancy: 0,
      devices: 0,
      description: buildingForm.value.description,
      lastInspection: new Date().toISOString().split('T')[0],
      nextInspection: '',
      manager: ''
    }
    buildings.value.unshift(newBuilding)
    ElMessage.success('Building added successfully')
  }

  showBuildingDialog.value = false
}

const viewBuilding = (building: Building) => {
  selectedBuilding.value = building
  showDetailDialog.value = true
}

const deleteBuilding = (building: Building) => {
  ElMessageBox.confirm(
      `Delete building "${building.name}"? This will also remove all associated floors, zones, and devices.`,
      'Delete Building',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = buildings.value.findIndex(b => b.id === building.id)
    if (index !== -1) {
      buildings.value.splice(index, 1)
      ElMessage.success('Building deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredBuildings.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `buildings_${new Date().toISOString().split('T')[0]}.json`
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
.building-management {
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

/* Buildings Grid */
.buildings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.building-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.building-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.building-card.maintenance { border-left: 4px solid #e6a23c; }
.building-card.inactive { border-left: 4px solid #f56c6c; opacity: 0.7; }
.building-card.active { border-left: 4px solid #67c23a; }

.building-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.building-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.building-info {
  flex: 1;
}

.building-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.building-code {
  font-size: 12px;
  color: #909399;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.active { background: #e8f5e9; color: #67c23a; }
.status-badge.maintenance { background: #fff7e6; color: #e6a23c; }
.status-badge.inactive { background: #ffefef; color: #f56c6c; }

.building-details {
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #303133;
  font-weight: 500;
}

.building-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 12px 0;
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
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

.building-actions {
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
  .building-management { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .buildings-grid { grid-template-columns: 1fr; }
  .building-header { flex-wrap: wrap; }
  .building-status { margin-left: auto; }
}
</style>