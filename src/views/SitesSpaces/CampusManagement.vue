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
        <div class="loading-tip">Campus Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="campus-management">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Campus Management</h2>
        <p class="subtitle">Manage multi-building campuses, facilities, and campus-wide operations</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddCampusDialog">
          <el-icon><Plus /></el-icon> Add Campus
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
        <div class="stat-icon">🏫</div>
        <div class="stat-info">
          <div class="stat-value">{{ campuses.length }}</div>
          <div class="stat-label">Total Campuses</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalBuildings }}</div>
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
        <div class="stat-icon">👥</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCapacity.toLocaleString() }}</div>
          <div class="stat-label">Total Capacity</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by campus name, location or code..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterRegion" placeholder="Region" clearable style="width: 160px">
          <el-option label="All Regions" value="all" />
          <el-option label="Singapore" value="Singapore" />
          <el-option label="Malaysia" value="Malaysia" />
          <el-option label="Indonesia" value="Indonesia" />
          <el-option label="Thailand" value="Thailand" />
          <el-option label="Vietnam" value="Vietnam" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Active" value="active" />
          <el-option label="Under Development" value="development" />
          <el-option label="Planned" value="planned" />
        </el-select>
      </div>
    </div>

    <!-- Campuses Grid -->
    <div class="campuses-grid">
      <div v-for="campus in filteredCampuses" :key="campus.id" class="campus-card" :class="campus.status">
        <div class="campus-header">
          <div class="campus-icon">{{ getCampusIcon(campus.type) }}</div>
          <div class="campus-info">
            <div class="campus-name">{{ campus.name }}</div>
            <div class="campus-code">{{ campus.code }}</div>
          </div>
          <div class="campus-status">
            <span class="status-badge" :class="campus.status">{{ getStatusText(campus.status) }}</span>
          </div>
        </div>

        <div class="campus-location">
          <el-icon><Location /></el-icon>
          <span>{{ campus.address }}, {{ campus.city }}, {{ campus.country }}</span>
        </div>

        <div class="campus-stats">
          <div class="stat-item">
            <div class="stat-number">{{ campus.buildings }}</div>
            <div class="stat-label-sm">Buildings</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ formatNumber(campus.area) }}</div>
            <div class="stat-label-sm">sqm</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ campus.capacity.toLocaleString() }}</div>
            <div class="stat-label-sm">Capacity</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ campus.occupancy }}%</div>
            <div class="stat-label-sm">Occupancy</div>
          </div>
        </div>

        <div class="campus-details">
          <div class="detail-row">
            <span class="detail-label">📍 Region</span>
            <span class="detail-value">{{ campus.country }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">📅 Established</span>
            <span class="detail-value">{{ campus.established }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">👤 Campus Director</span>
            <span class="detail-value">{{ campus.director }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🔌 Power Usage</span>
            <span class="detail-value">{{ campus.powerUsage }} MWh/month</span>
          </div>
        </div>

        <div class="campus-actions">
          <el-button size="small" type="primary" plain @click="viewCampus(campus)">
            <el-icon><View /></el-icon> View
          </el-button>
          <el-button size="small" type="info" plain @click="editCampus(campus)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteCampus(campus)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredCampuses.length === 0" class="empty-state">
      <div class="empty-icon">🏫</div>
      <div class="empty-title">No campuses found</div>
      <div class="empty-desc">Add a campus to start managing multi-building facilities</div>
      <el-button type="primary" @click="openAddCampusDialog">Add Campus</el-button>
    </div>

    <!-- Add/Edit Campus Dialog -->
    <el-dialog v-model="showCampusDialog" :title="dialogTitle" width="650px">
      <el-form :model="campusForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Campus Name" required>
              <el-input v-model="campusForm.name" placeholder="Enter campus name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Campus Code">
              <el-input v-model="campusForm.code" placeholder="e.g., SGP-MAIN" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Country/Region">
              <el-select v-model="campusForm.country" style="width: 100%">
                <el-option label="Singapore" value="Singapore" />
                <el-option label="Malaysia" value="Malaysia" />
                <el-option label="Indonesia" value="Indonesia" />
                <el-option label="Thailand" value="Thailand" />
                <el-option label="Vietnam" value="Vietnam" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="City">
              <el-input v-model="campusForm.city" placeholder="City" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Status">
              <el-select v-model="campusForm.status" style="width: 100%">
                <el-option label="Active" value="active" />
                <el-option label="Under Development" value="development" />
                <el-option label="Planned" value="planned" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Address" required>
          <el-input v-model="campusForm.address" placeholder="Street address" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Total Area (sqm)">
              <el-input-number v-model="campusForm.area" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Number of Buildings">
              <el-input-number v-model="campusForm.buildings" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Total Capacity">
              <el-input-number v-model="campusForm.capacity" :min="0" :step="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Campus Director">
              <el-input v-model="campusForm.director" placeholder="Director name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Established Year">
              <el-input-number v-model="campusForm.established" :min="1900" :max="2025" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Campus Type">
              <el-select v-model="campusForm.type" style="width: 100%">
                <el-option label="Corporate" value="corporate" />
                <el-option label="Industrial" value="industrial" />
                <el-option label="Technology" value="tech" />
                <el-option label="Mixed Use" value="mixed" />
                <el-option label="Research" value="research" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Time Zone">
              <el-select v-model="campusForm.timezone" style="width: 100%">
                <el-option label="UTC+8 (Singapore/Beijing)" value="UTC+8" />
                <el-option label="UTC+7 (Bangkok/Jakarta)" value="UTC+7" />
                <el-option label="UTC+6 (Yangon)" value="UTC+6" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="campusForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCampusDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveCampus">Save Campus</el-button>
      </template>
    </el-dialog>

    <!-- Campus Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedCampus?.name" width="750px">
      <div v-if="selectedCampus">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Campus ID">{{ selectedCampus.id }}</el-descriptions-item>
          <el-descriptions-item label="Campus Code">{{ selectedCampus.code }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ getCampusTypeLabel(selectedCampus.type) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedCampus.status]">{{ getStatusText(selectedCampus.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Location" :span="2">{{ selectedCampus.address }}, {{ selectedCampus.city }}, {{ selectedCampus.country }}</el-descriptions-item>
          <el-descriptions-item label="Total Area">{{ formatNumber(selectedCampus.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Number of Buildings">{{ selectedCampus.buildings }}</el-descriptions-item>
          <el-descriptions-item label="Total Capacity">{{ selectedCampus.capacity.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Current Occupancy">{{ selectedCampus.occupancy }}%</el-descriptions-item>
          <el-descriptions-item label="Campus Director">{{ selectedCampus.director }}</el-descriptions-item>
          <el-descriptions-item label="Established">{{ selectedCampus.established }}</el-descriptions-item>
          <el-descriptions-item label="Time Zone">{{ selectedCampus.timezone }}</el-descriptions-item>
          <el-descriptions-item label="Power Usage">{{ selectedCampus.powerUsage }} MWh/month</el-descriptions-item>
          <el-descriptions-item label="Water Usage">{{ selectedCampus.waterUsage }} m³/month</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedCampus.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editCampus(selectedCampus); showDetailDialog = false">Edit</el-button>
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
  'Loading campus data...',
  'Fetching building information...',
  'Organizing by region...',
  'Almost ready...'
]

// Campus interface
interface Campus {
  id: number
  name: string
  code: string
  type: string
  status: string
  country: string
  city: string
  address: string
  area: number
  buildings: number
  capacity: number
  occupancy: number
  director: string
  established: number
  timezone: string
  powerUsage: number
  waterUsage: number
  description: string
}

// Sample campuses data
const campuses = ref<Campus[]>([
  {
    id: 1,
    name: 'Marina Bay Corporate Campus',
    code: 'MBS-CMP-01',
    type: 'corporate',
    status: 'active',
    country: 'Singapore',
    city: 'Singapore',
    address: '8 Marina Boulevard',
    area: 125000,
    buildings: 4,
    capacity: 8500,
    occupancy: 92,
    director: 'Johnathan Lee',
    established: 2015,
    timezone: 'UTC+8',
    powerUsage: 2850,
    waterUsage: 3200,
    description: 'Flagship corporate headquarters with smart building technologies'
  },
  {
    id: 2,
    name: 'Jurong Industrial Park',
    code: 'JIP-02',
    type: 'industrial',
    status: 'active',
    country: 'Singapore',
    city: 'Singapore',
    address: '15 Jurong West Street',
    area: 85000,
    buildings: 6,
    capacity: 3200,
    occupancy: 88,
    director: 'Michael Tan',
    established: 2010,
    timezone: 'UTC+8',
    powerUsage: 4200,
    waterUsage: 1800,
    description: 'Light industrial and logistics hub'
  },
  {
    id: 3,
    name: 'One-North Tech Hub',
    code: 'ONTH-03',
    type: 'tech',
    status: 'active',
    country: 'Singapore',
    city: 'Singapore',
    address: '5 One-North Gateway',
    area: 68000,
    buildings: 5,
    capacity: 5200,
    occupancy: 95,
    director: 'Sarah Chen',
    established: 2018,
    timezone: 'UTC+8',
    powerUsage: 2350,
    waterUsage: 2100,
    description: 'Technology and innovation campus'
  },
  {
    id: 4,
    name: 'Iskandar Development',
    code: 'IDR-04',
    type: 'mixed',
    status: 'development',
    country: 'Malaysia',
    city: 'Johor Bahru',
    address: 'Medini 7, Iskandar Puteri',
    area: 180000,
    buildings: 8,
    capacity: 12500,
    occupancy: 45,
    director: 'David Lim',
    established: 2022,
    timezone: 'UTC+8',
    powerUsage: 1850,
    waterUsage: 2800,
    description: 'Mixed-use development under construction - Phase 1 operational'
  },
  {
    id: 5,
    name: 'Bangkok Riverside Complex',
    code: 'BKK-RIV-05',
    type: 'mixed',
    status: 'active',
    country: 'Thailand',
    city: 'Bangkok',
    address: '299 Charoen Nakhon Road',
    area: 95000,
    buildings: 3,
    capacity: 4800,
    occupancy: 78,
    director: 'Lisa Wong',
    established: 2019,
    timezone: 'UTC+7',
    powerUsage: 2100,
    waterUsage: 2600,
    description: 'Commercial and retail complex'
  },
  {
    id: 6,
    name: 'Jakarta Smart City',
    code: 'JKT-SC-06',
    type: 'tech',
    status: 'planned',
    country: 'Indonesia',
    city: 'Jakarta',
    address: 'Sudirman Central Business District',
    area: 120000,
    buildings: 4,
    capacity: 6800,
    occupancy: 0,
    director: 'Emma Zhao',
    established: 2025,
    timezone: 'UTC+7',
    powerUsage: 0,
    waterUsage: 0,
    description: 'Planned smart campus - construction starting Q1 2026'
  }
])

// UI State
const searchText = ref('')
const filterRegion = ref('all')
const filterStatus = ref('all')
const showCampusDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedCampus = ref<Campus | null>(null)

const campusForm = ref({
  name: '',
  code: '',
  type: 'corporate',
  status: 'active',
  country: 'Singapore',
  city: '',
  address: '',
  area: 0,
  buildings: 1,
  capacity: 0,
  director: '',
  established: 2020,
  timezone: 'UTC+8',
  description: ''
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Campus' : 'Add Campus')

const totalBuildings = computed(() => campuses.value.reduce((sum, c) => sum + c.buildings, 0))
const totalArea = computed(() => campuses.value.reduce((sum, c) => sum + c.area, 0))
const totalCapacity = computed(() => campuses.value.reduce((sum, c) => sum + c.capacity, 0))

const filteredCampuses = computed(() => {
  let filtered = [...campuses.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(keyword) ||
        c.code.toLowerCase().includes(keyword) ||
        c.address.toLowerCase().includes(keyword)
    )
  }

  if (filterRegion.value !== 'all') {
    filtered = filtered.filter(c => c.country === filterRegion.value)
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(c => c.status === filterStatus.value)
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
    active: 'Active',
    development: 'Development',
    planned: 'Planned'
  }
  return map[status] || status
}

const getCampusIcon = (type: string) => {
  const map: Record<string, string> = {
    corporate: '🏢',
    industrial: '🏭',
    tech: '💻',
    mixed: '🏙️',
    research: '🔬'
  }
  return map[type] || '🏫'
}

const getCampusTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    corporate: 'Corporate',
    industrial: 'Industrial',
    tech: 'Technology',
    mixed: 'Mixed Use',
    research: 'Research'
  }
  return map[type] || type
}

// Campus CRUD operations
const openAddCampusDialog = () => {
  isEditing.value = false
  campusForm.value = {
    name: '',
    code: '',
    type: 'corporate',
    status: 'active',
    country: 'Singapore',
    city: '',
    address: '',
    area: 0,
    buildings: 1,
    capacity: 0,
    director: '',
    established: 2020,
    timezone: 'UTC+8',
    description: ''
  }
  showCampusDialog.value = true
}

const editCampus = (campus: Campus) => {
  isEditing.value = true
  selectedCampus.value = campus
  campusForm.value = {
    name: campus.name,
    code: campus.code,
    type: campus.type,
    status: campus.status,
    country: campus.country,
    city: campus.city,
    address: campus.address,
    area: campus.area,
    buildings: campus.buildings,
    capacity: campus.capacity,
    director: campus.director,
    established: campus.established,
    timezone: campus.timezone,
    description: campus.description || ''
  }
  showCampusDialog.value = true
}

const saveCampus = () => {
  if (!campusForm.value.name.trim()) {
    ElMessage.warning('Please enter campus name')
    return
  }
  if (!campusForm.value.city.trim()) {
    ElMessage.warning('Please enter city')
    return
  }
  if (!campusForm.value.address.trim()) {
    ElMessage.warning('Please enter address')
    return
  }

  if (isEditing.value && selectedCampus.value) {
    const index = campuses.value.findIndex(c => c.id === selectedCampus.value!.id)
    if (index !== -1) {
      campuses.value[index] = {
        ...campuses.value[index],
        name: campusForm.value.name,
        code: campusForm.value.code,
        type: campusForm.value.type,
        status: campusForm.value.status,
        country: campusForm.value.country,
        city: campusForm.value.city,
        address: campusForm.value.address,
        area: campusForm.value.area,
        buildings: campusForm.value.buildings,
        capacity: campusForm.value.capacity,
        director: campusForm.value.director,
        established: campusForm.value.established,
        timezone: campusForm.value.timezone,
        description: campusForm.value.description,
        powerUsage: campusForm.value.status === 'active' ? 2000 : 0,
        waterUsage: campusForm.value.status === 'active' ? 2500 : 0,
        occupancy: campusForm.value.status === 'active' ? 70 : 0
      }
      ElMessage.success('Campus updated successfully')
    }
  } else {
    const newCampus: Campus = {
      id: Date.now(),
      name: campusForm.value.name,
      code: campusForm.value.code || `CMP-${campuses.value.length + 1}`,
      type: campusForm.value.type,
      status: campusForm.value.status,
      country: campusForm.value.country,
      city: campusForm.value.city,
      address: campusForm.value.address,
      area: campusForm.value.area,
      buildings: campusForm.value.buildings,
      capacity: campusForm.value.capacity,
      occupancy: 0,
      director: campusForm.value.director,
      established: campusForm.value.established,
      timezone: campusForm.value.timezone,
      powerUsage: 0,
      waterUsage: 0,
      description: campusForm.value.description
    }
    campuses.value.push(newCampus)
    ElMessage.success('Campus added successfully')
  }

  showCampusDialog.value = false
}

const viewCampus = (campus: Campus) => {
  selectedCampus.value = campus
  showDetailDialog.value = true
}

const deleteCampus = (campus: Campus) => {
  ElMessageBox.confirm(
      `Delete campus "${campus.name}"? This will also remove all associated buildings, floors, zones, and devices.`,
      'Delete Campus',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = campuses.value.findIndex(c => c.id === campus.id)
    if (index !== -1) {
      campuses.value.splice(index, 1)
      ElMessage.success('Campus deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredCampuses.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `campuses_${new Date().toISOString().split('T')[0]}.json`
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
.campus-management {
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

/* Campuses Grid */
.campuses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.campus-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.campus-card.development { border-left-color: #e6a23c; }
.campus-card.planned { border-left-color: #909399; }
.campus-card.active { border-left-color: #67c23a; }

.campus-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.campus-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.campus-icon {
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

.campus-info {
  flex: 1;
}

.campus-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.campus-code {
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
.status-badge.development { background: #fff7e6; color: #e6a23c; }
.status-badge.planned { background: #f5f5f5; color: #909399; }

.campus-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.campus-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
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

.campus-details {
  margin-bottom: 16px;
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

.campus-actions {
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
  .campus-management { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .campuses-grid { grid-template-columns: 1fr; }
  .campus-stats { grid-template-columns: repeat(2, 1fr); }
}
</style>