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
        <div class="loading-tip">Space Type Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="space-type">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Space Type Management</h2>
        <p class="subtitle">Define and manage space classifications, categories, and attributes</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddTypeDialog">
          <el-icon><Plus /></el-icon> Add Space Type
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
        <div class="stat-icon">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ spaceTypes.length }}</div>
          <div class="stat-label">Total Types</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏗️</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCategories }}</div>
          <div class="stat-label">Categories</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🟢</div>
        <div class="stat-info">
          <div class="stat-value">{{ activeCount }}</div>
          <div class="stat-label">Active Types</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📐</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgAreaRange }}</div>
          <div class="stat-label">Avg Area Range (sqm)</div>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="search-bar">
      <el-input v-model="searchText" placeholder="Search by type name, code or category..." clearable :prefix-icon="Search" style="width: 300px" />
      <span class="results-count">{{ filteredTypes.length }} space types found</span>
    </div>

    <!-- Space Types Grid -->
    <div class="types-grid">
      <div v-for="type in filteredTypes" :key="type.id" class="type-card" :class="type.status">
        <div class="type-header">
          <div class="type-icon">{{ getTypeIcon(type.icon) }}</div>
          <div class="type-info">
            <div class="type-name">{{ type.name }}</div>
            <div class="type-code">{{ type.code }}</div>
          </div>
          <div class="type-status">
            <span class="status-badge" :class="type.status">{{ type.status === 'active' ? 'Active' : 'Inactive' }}</span>
          </div>
        </div>

        <div class="type-description">{{ type.description }}</div>

        <div class="type-details">
          <div class="detail-row">
            <span class="detail-label">Category</span>
            <span class="detail-value">{{ type.category }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Area Range</span>
            <span class="detail-value">{{ type.minArea }} - {{ type.maxArea }} sqm</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Default Capacity</span>
            <span class="detail-value">{{ type.defaultCapacity }} people</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Spaces Count</span>
            <span class="detail-value">{{ type.spacesCount }}</span>
          </div>
        </div>

        <div class="type-attributes">
          <div class="attributes-title">Standard Attributes</div>
          <div class="attributes-list">
            <el-tag v-for="attr in type.attributes.slice(0, 4)" :key="attr" size="small" type="info" effect="plain">
              {{ attr }}
            </el-tag>
            <el-tag v-if="type.attributes.length > 4" size="small" type="info" effect="plain">
              +{{ type.attributes.length - 4 }}
            </el-tag>
          </div>
        </div>

        <div class="type-actions">
          <el-button size="small" type="primary" plain @click="viewType(type)">
            <el-icon><View /></el-icon> View
          </el-button>
          <el-button size="small" type="info" plain @click="editType(type)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteType(type)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredTypes.length === 0" class="empty-state">
      <div class="empty-icon">📋</div>
      <div class="empty-title">No space types found</div>
      <div class="empty-desc">Add a space type to start classifying your spaces</div>
      <el-button type="primary" @click="openAddTypeDialog">Add Space Type</el-button>
    </div>

    <!-- Add/Edit Space Type Dialog -->
    <el-dialog v-model="showTypeDialog" :title="dialogTitle" width="600px">
      <el-form :model="typeForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Type Name" required>
              <el-input v-model="typeForm.name" placeholder="e.g., Executive Office" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Type Code">
              <el-input v-model="typeForm.code" placeholder="e.g., EXEC-OFF" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Category">
          <el-select v-model="typeForm.category" style="width: 100%">
            <el-option label="Office" value="Office" />
            <el-option label="Meeting" value="Meeting" />
            <el-option label="Conference" value="Conference" />
            <el-option label="Collaboration" value="Collaboration" />
            <el-option label="Amenity" value="Amenity" />
            <el-option label="Technical" value="Technical" />
            <el-option label="Storage" value="Storage" />
            <el-option label="Retail" value="Retail" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="typeForm.description" type="textarea" :rows="2" placeholder="Describe this space type" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Min Area (sqm)">
              <el-input-number v-model="typeForm.minArea" :min="0" :step="5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max Area (sqm)">
              <el-input-number v-model="typeForm.maxArea" :min="0" :step="5" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Default Capacity">
              <el-input-number v-model="typeForm.defaultCapacity" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Icon">
              <el-select v-model="typeForm.icon" style="width: 100%">
                <el-option label="💼 Office" value="office" />
                <el-option label="👥 Meeting" value="meeting" />
                <el-option label="🎤 Conference" value="conference" />
                <el-option label="☕ Break" value="break" />
                <el-option label="💿 Server" value="server" />
                <el-option label="📦 Storage" value="storage" />
                <el-option label="🚻 Restroom" value="restroom" />
                <el-option label="🏢 Lobby" value="lobby" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Status">
          <el-radio-group v-model="typeForm.status">
            <el-radio label="active">Active</el-radio>
            <el-radio label="inactive">Inactive</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Standard Attributes">
          <el-select v-model="typeForm.attributes" multiple filterable allow-create default-first-option placeholder="Add attributes" style="width: 100%">
            <el-option label="Power Outlets" value="Power Outlets" />
            <el-option label="Network Ports" value="Network Ports" />
            <el-option label="HVAC" value="HVAC" />
            <el-option label="Natural Light" value="Natural Light" />
            <el-option label="Window" value="Window" />
            <el-option label="Whiteboard" value="Whiteboard" />
            <el-option label="Projector" value="Projector" />
            <el-option label="Video Conference" value="Video Conference" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showTypeDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveType">Save Space Type</el-button>
      </template>
    </el-dialog>

    <!-- Space Type Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedType?.name" width="650px">
      <div v-if="selectedType">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Type ID">{{ selectedType.id }}</el-descriptions-item>
          <el-descriptions-item label="Type Code">{{ selectedType.code }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ selectedType.category }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedType.status]">{{ selectedType.status === 'active' ? 'Active' : 'Inactive' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Icon">{{ getTypeIcon(selectedType.icon) }}</el-descriptions-item>
          <el-descriptions-item label="Spaces Count">{{ selectedType.spacesCount }}</el-descriptions-item>
          <el-descriptions-item label="Area Range">{{ selectedType.minArea }} - {{ selectedType.maxArea }} sqm</el-descriptions-item>
          <el-descriptions-item label="Default Capacity">{{ selectedType.defaultCapacity }} people</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedType.description }}</el-descriptions-item>
          <el-descriptions-item label="Standard Attributes" :span="2">
            <div class="attributes-list">
              <el-tag v-for="attr in selectedType.attributes" :key="attr" size="small" type="info" effect="plain">
                {{ attr }}
              </el-tag>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editType(selectedType); showDetailDialog = false">Edit</el-button>
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
  'Loading space type data...',
  'Fetching classification information...',
  'Organizing by category...',
  'Almost ready...'
]

// Space Type interface
interface SpaceType {
  id: number
  name: string
  code: string
  category: string
  description: string
  minArea: number
  maxArea: number
  defaultCapacity: number
  icon: string
  attributes: string[]
  status: string
  spacesCount: number
}

// Sample space types data
const spaceTypes = ref<SpaceType[]>([
  {
    id: 1,
    name: 'Executive Office',
    code: 'EXEC-OFF',
    category: 'Office',
    description: 'Private office for senior management with premium finishes',
    minArea: 25,
    maxArea: 50,
    defaultCapacity: 4,
    icon: 'office',
    attributes: ['Power Outlets', 'Network Ports', 'HVAC', 'Natural Light', 'Window', 'Executive Desk'],
    status: 'active',
    spacesCount: 12
  },
  {
    id: 2,
    name: 'Standard Office',
    code: 'STD-OFF',
    category: 'Office',
    description: 'Regular office space for general staff',
    minArea: 12,
    maxArea: 25,
    defaultCapacity: 2,
    icon: 'office',
    attributes: ['Power Outlets', 'Network Ports', 'HVAC', 'Desk', 'Chair'],
    status: 'active',
    spacesCount: 48
  },
  {
    id: 3,
    name: 'Open Plan Office',
    code: 'OPEN-OFF',
    category: 'Office',
    description: 'Open workspace for collaborative work',
    minArea: 50,
    maxArea: 200,
    defaultCapacity: 20,
    icon: 'office',
    attributes: ['Power Outlets', 'Network Ports', 'HVAC', 'Natural Light', 'Flexible Seating'],
    status: 'active',
    spacesCount: 8
  },
  {
    id: 4,
    name: 'Small Meeting Room',
    code: 'SML-MTG',
    category: 'Meeting',
    description: 'Small meeting space for 4-6 people',
    minArea: 10,
    maxArea: 18,
    defaultCapacity: 6,
    icon: 'meeting',
    attributes: ['Whiteboard', 'Monitor', 'Video Conference', 'Power Outlets', 'Network Ports'],
    status: 'active',
    spacesCount: 24
  },
  {
    id: 5,
    name: 'Large Meeting Room',
    code: 'LRG-MTG',
    category: 'Meeting',
    description: 'Large meeting space for team gatherings',
    minArea: 20,
    maxArea: 35,
    defaultCapacity: 12,
    icon: 'meeting',
    attributes: ['Whiteboard', 'Projector', 'Video Conference', 'Power Outlets', 'Network Ports'],
    status: 'active',
    spacesCount: 15
  },
  {
    id: 6,
    name: 'Boardroom',
    code: 'BRD-RM',
    category: 'Conference',
    description: 'Executive boardroom with premium AV equipment',
    minArea: 35,
    maxArea: 60,
    defaultCapacity: 16,
    icon: 'conference',
    attributes: ['Video Conference', 'Projector', 'Premium Audio', 'Power Outlets', 'Network Ports'],
    status: 'active',
    spacesCount: 4
  },
  {
    id: 7,
    name: 'Break Room',
    code: 'BRK-RM',
    category: 'Amenity',
    description: 'Pantry and relaxation area for staff',
    minArea: 15,
    maxArea: 40,
    defaultCapacity: 10,
    icon: 'break',
    attributes: ['Kitchenette', 'Microwave', 'Refrigerator', 'Seating', 'Coffee Machine'],
    status: 'active',
    spacesCount: 8
  },
  {
    id: 8,
    name: 'Server Room',
    code: 'SRV-RM',
    category: 'Technical',
    description: 'Temperature-controlled IT equipment room',
    minArea: 8,
    maxArea: 30,
    defaultCapacity: 0,
    icon: 'server',
    attributes: ['Raised Floor', 'HVAC', 'UPS Backup', 'Fire Suppression', 'Racks'],
    status: 'active',
    spacesCount: 6
  },
  {
    id: 9,
    name: 'Storage Room',
    code: 'STO-RM',
    category: 'Storage',
    description: 'General storage space for supplies and equipment',
    minArea: 5,
    maxArea: 25,
    defaultCapacity: 0,
    icon: 'storage',
    attributes: ['Shelving', 'Lockable', 'Lighting', 'Ventilation'],
    status: 'inactive',
    spacesCount: 18
  }
])

// UI State
const searchText = ref('')
const showTypeDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const selectedType = ref<SpaceType | null>(null)

const typeForm = ref({
  name: '',
  code: '',
  category: 'Office',
  description: '',
  minArea: 0,
  maxArea: 0,
  defaultCapacity: 0,
  icon: 'office',
  attributes: [] as string[],
  status: 'active'
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Space Type' : 'Add Space Type')

const totalCategories = computed(() => {
  return new Set(spaceTypes.value.map(t => t.category)).size
})

const activeCount = computed(() => spaceTypes.value.filter(t => t.status === 'active').length)

const avgAreaRange = computed(() => {
  const avgMin = Math.round(spaceTypes.value.reduce((sum, t) => sum + t.minArea, 0) / spaceTypes.value.length)
  const avgMax = Math.round(spaceTypes.value.reduce((sum, t) => sum + t.maxArea, 0) / spaceTypes.value.length)
  return `${avgMin}-${avgMax}`
})

const filteredTypes = computed(() => {
  let filtered = [...spaceTypes.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(t =>
        t.name.toLowerCase().includes(keyword) ||
        t.code.toLowerCase().includes(keyword) ||
        t.category.toLowerCase().includes(keyword)
    )
  }

  return filtered
})

// Helper functions
const getTypeIcon = (icon: string) => {
  const map: Record<string, string> = {
    office: '💼',
    meeting: '👥',
    conference: '🎤',
    break: '☕',
    server: '💿',
    storage: '📦',
    restroom: '🚻',
    lobby: '🏢'
  }
  return map[icon] || '📍'
}

// Space Type CRUD operations
const openAddTypeDialog = () => {
  isEditing.value = false
  typeForm.value = {
    name: '',
    code: '',
    category: 'Office',
    description: '',
    minArea: 0,
    maxArea: 0,
    defaultCapacity: 0,
    icon: 'office',
    attributes: [],
    status: 'active'
  }
  showTypeDialog.value = true
}

const editType = (type: SpaceType) => {
  isEditing.value = true
  selectedType.value = type
  typeForm.value = {
    name: type.name,
    code: type.code,
    category: type.category,
    description: type.description,
    minArea: type.minArea,
    maxArea: type.maxArea,
    defaultCapacity: type.defaultCapacity,
    icon: type.icon,
    attributes: [...type.attributes],
    status: type.status
  }
  showTypeDialog.value = true
}

const saveType = () => {
  if (!typeForm.value.name.trim()) {
    ElMessage.warning('Please enter space type name')
    return
  }

  if (typeForm.value.minArea > typeForm.value.maxArea && typeForm.value.maxArea > 0) {
    ElMessage.warning('Min area cannot be greater than max area')
    return
  }

  if (isEditing.value && selectedType.value) {
    const index = spaceTypes.value.findIndex(t => t.id === selectedType.value!.id)
    if (index !== -1) {
      spaceTypes.value[index] = {
        ...spaceTypes.value[index],
        name: typeForm.value.name,
        code: typeForm.value.code || typeForm.value.name.toUpperCase().replace(/\s/g, '_'),
        category: typeForm.value.category,
        description: typeForm.value.description,
        minArea: typeForm.value.minArea,
        maxArea: typeForm.value.maxArea,
        defaultCapacity: typeForm.value.defaultCapacity,
        icon: typeForm.value.icon,
        attributes: typeForm.value.attributes,
        status: typeForm.value.status
      }
      ElMessage.success('Space type updated successfully')
    }
  } else {
    const newType: SpaceType = {
      id: Date.now(),
      name: typeForm.value.name,
      code: typeForm.value.code || typeForm.value.name.toUpperCase().replace(/\s/g, '_'),
      category: typeForm.value.category,
      description: typeForm.value.description,
      minArea: typeForm.value.minArea,
      maxArea: typeForm.value.maxArea,
      defaultCapacity: typeForm.value.defaultCapacity,
      icon: typeForm.value.icon,
      attributes: typeForm.value.attributes,
      status: typeForm.value.status,
      spacesCount: 0
    }
    spaceTypes.value.push(newType)
    ElMessage.success('Space type added successfully')
  }

  showTypeDialog.value = false
}

const viewType = (type: SpaceType) => {
  selectedType.value = type
  showDetailDialog.value = true
}

const deleteType = (type: SpaceType) => {
  if (type.spacesCount > 0) {
    ElMessage.warning(`Cannot delete space type "${type.name}" because it has ${type.spacesCount} associated spaces`)
    return
  }

  ElMessageBox.confirm(
      `Delete space type "${type.name}"? This action cannot be undone.`,
      'Delete Space Type',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = spaceTypes.value.findIndex(t => t.id === type.id)
    if (index !== -1) {
      spaceTypes.value.splice(index, 1)
      ElMessage.success('Space type deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredTypes.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `space_types_${new Date().toISOString().split('T')[0]}.json`
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
.space-type {
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

/* Search Bar */
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.results-count {
  font-size: 13px;
  color: #909399;
}

/* Types Grid */
.types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.type-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.type-card.inactive { border-left-color: #909399; opacity: 0.7; }
.type-card.active { border-left-color: #67c23a; }

.type-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.type-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.type-icon {
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

.type-info {
  flex: 1;
}

.type-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.type-code {
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
.status-badge.inactive { background: #f5f5f5; color: #909399; }

.type-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.type-details {
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

.type-attributes {
  margin-bottom: 16px;
}

.attributes-title {
  font-size: 11px;
  font-weight: 600;
  color: #909399;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.attributes-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.type-actions {
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
  .space-type { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .search-bar { flex-direction: column; align-items: stretch; }
  .types-grid { grid-template-columns: 1fr; }
  .type-header { flex-wrap: wrap; }
  .type-status { margin-left: auto; }
}
</style>