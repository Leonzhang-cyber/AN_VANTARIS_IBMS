<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  RefreshRight, Warning, CircleCheck, Clock,
  Monitor, Tools, Search, Setting,
  Operation, Document, Grid, List,
  Sunny, Moon, Connection, HomeFilled,
  Switch, Check, Close, Edit, Delete,
  Plus, CopyDocument, TrendCharts, DataAnalysis,
  Lightning, Timer, Lock, User, Bell, VideoCamera,
  Star, StarFilled, MoreFilled
} from "@element-plus/icons-vue"
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Initializing custom scene manager...',
  'Loading user configurations...',
  'Applying personalized settings...',
  'Ready for operation...'
]

// Custom scenes data
const customScenes = ref([
  {
    id: 'scene-1',
    name: 'Morning Welcome',
    description: 'Warm lighting and comfortable temperature for morning hours',
    icon: 'Sunny',
    isActive: false,
    isFavorite: true,
    lastUsed: '2025-01-16 08:00:00',
    schedule: 'Weekdays 08:00',
    settings: {
      hvac: { coolingSetpoint: 22, heatingSetpoint: 20, fanSpeed: 'Auto' },
      lighting: { brightness: 85, occupancySensing: true },
      blinds: { position: 30, autoAdjust: true }
    },
    devices: ['HVAC', 'Lighting', 'Blinds'],
    tags: ['Morning', 'Comfort']
  },
  {
    id: 'scene-2',
    name: 'Focus Mode',
    description: 'Reduced distractions and optimized lighting for concentration',
    icon: 'DataAnalysis',
    isActive: false,
    isFavorite: true,
    lastUsed: '2025-01-15 14:30:00',
    schedule: null,
    settings: {
      hvac: { coolingSetpoint: 21, heatingSetpoint: 21, fanSpeed: 'Low' },
      lighting: { brightness: 70, occupancySensing: true },
      blinds: { position: 60, autoAdjust: false }
    },
    devices: ['HVAC', 'Lighting', 'Blinds'],
    tags: ['Work', 'Productivity']
  },
  {
    id: 'scene-3',
    name: 'Meeting Ready',
    description: 'Professional lighting and comfortable temperature for meetings',
    icon: 'User',
    isActive: false,
    isFavorite: true,
    lastUsed: '2025-01-15 10:00:00',
    schedule: 'Weekdays 10:00, 14:00',
    settings: {
      hvac: { coolingSetpoint: 22, heatingSetpoint: 21, fanSpeed: 'Auto' },
      lighting: { brightness: 90, occupancySensing: true },
      blinds: { position: 20, autoAdjust: true }
    },
    devices: ['HVAC', 'Lighting', 'Blinds'],
    tags: ['Meeting', 'Professional']
  },
  {
    id: 'scene-4',
    name: 'Evening Relax',
    description: 'Dimmed lighting and cooler temperature for evening relaxation',
    icon: 'Moon',
    isActive: false,
    isFavorite: false,
    lastUsed: '2025-01-15 19:00:00',
    schedule: 'Daily 19:00',
    settings: {
      hvac: { coolingSetpoint: 23, heatingSetpoint: 19, fanSpeed: 'Low' },
      lighting: { brightness: 50, occupancySensing: true },
      blinds: { position: 80, autoAdjust: true }
    },
    devices: ['HVAC', 'Lighting', 'Blinds'],
    tags: ['Evening', 'Relax']
  },
  {
    id: 'scene-5',
    name: 'Weekend Mode',
    description: 'Energy saving but comfortable for weekend activities',
    icon: 'HomeFilled',
    isActive: false,
    isFavorite: true,
    lastUsed: '2025-01-14 09:00:00',
    schedule: 'Weekends 09:00',
    settings: {
      hvac: { coolingSetpoint: 23, heatingSetpoint: 19, fanSpeed: 'Auto' },
      lighting: { brightness: 65, occupancySensing: true },
      blinds: { position: 50, autoAdjust: true }
    },
    devices: ['HVAC', 'Lighting', 'Blinds'],
    tags: ['Weekend', 'Comfort']
  },
  {
    id: 'scene-6',
    name: 'Presentation Mode',
    description: 'Optimized for presentations with dimmed front lights',
    icon: 'Monitor',
    isActive: false,
    isFavorite: false,
    lastUsed: '2025-01-13 11:30:00',
    schedule: null,
    settings: {
      hvac: { coolingSetpoint: 21, heatingSetpoint: 21, fanSpeed: 'Quiet' },
      lighting: { brightness: 60, occupancySensing: true },
      blinds: { position: 15, autoAdjust: false }
    },
    devices: ['HVAC', 'Lighting', 'Blinds'],
    tags: ['Presentation', 'Meeting']
  }
])

// Available device settings for custom scene creation
const availableSettings = ref({
  hvac: {
    coolingSetpoint: { label: 'Cooling Setpoint', type: 'number', min: 18, max: 26, unit: '°C', default: 22 },
    heatingSetpoint: { label: 'Heating Setpoint', type: 'number', min: 16, max: 24, unit: '°C', default: 20 },
    fanSpeed: { label: 'Fan Speed', type: 'select', options: ['Auto', 'Low', 'Medium', 'High', 'Quiet'], default: 'Auto' }
  },
  lighting: {
    brightness: { label: 'Brightness', type: 'slider', min: 0, max: 100, unit: '%', default: 80 },
    occupancySensing: { label: 'Occupancy Sensing', type: 'boolean', default: true }
  },
  blinds: {
    position: { label: 'Blind Position', type: 'slider', min: 0, max: 100, unit: '%', default: 40 },
    autoAdjust: { label: 'Auto Adjust', type: 'boolean', default: true }
  }
})

// Device options for scene assignment
const deviceOptions = ref([
  { value: 'HVAC', label: 'HVAC Systems', icon: 'Connection' },
  { value: 'Lighting', label: 'Lighting Systems', icon: 'Sunny' },
  { value: 'Blinds', label: 'Window Blinds', icon: 'Grid' },
  { value: 'Security', label: 'Security Systems', icon: 'Monitor' },
  { value: 'Power', label: 'Power Management', icon: 'Lightning' },
  { value: 'Audio', label: 'Audio Systems', icon: 'Bell' }
])

// Scene transition history
const transitionHistory = ref([
  { time: '08:00:00', date: '2025-01-16', scene: 'Morning Welcome', operator: 'Schedule', duration: 'Active' },
  { time: '14:30:00', date: '2025-01-15', scene: 'Focus Mode', operator: 'Manual', duration: '2h' },
  { time: '10:00:00', date: '2025-01-15', scene: 'Meeting Ready', operator: 'Schedule', duration: '1h' },
  { time: '19:00:00', date: '2025-01-15', scene: 'Evening Relax', operator: 'Manual', duration: 'Active' }
])

// UI State
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showScheduleDialog = ref(false)
const editingScene = ref<any>(null)
const newScene = ref({
  name: '',
  description: '',
  icon: 'Star',
  tags: [] as string[],
  devices: [] as string[],
  settings: {
    hvac: { coolingSetpoint: 22, heatingSetpoint: 20, fanSpeed: 'Auto' },
    lighting: { brightness: 80, occupancySensing: true },
    blinds: { position: 40, autoAdjust: true }
  }
})
const newTag = ref('')
const searchKeyword = ref('')
const viewMode = ref<'grid' | 'list'>('grid')

const filteredScenes = computed(() => {
  if (!searchKeyword.value) return customScenes.value
  const keyword = searchKeyword.value.toLowerCase()
  return customScenes.value.filter(s =>
      s.name.toLowerCase().includes(keyword) ||
      s.description.toLowerCase().includes(keyword) ||
      s.tags.some(tag => tag.toLowerCase().includes(keyword))
  )
})

const favoriteScenes = computed(() => {
  return customScenes.value.filter(s => s.isFavorite)
})

const getIconComponent = (iconName: string) => {
  const icons: Record<string, any> = {
    Sunny, Moon, HomeFilled, Monitor, DataAnalysis, User, Star
  }
  return icons[iconName] || Setting
}

const activateScene = (scene: any) => {
  ElMessageBox.confirm(
      `Apply "${scene.name}" scene? This will change lighting, HVAC, and blind settings.`,
      'Activate Scene',
      {
        confirmButtonText: 'Apply',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    // Deactivate all scenes
    customScenes.value.forEach(s => { s.isActive = false })
    scene.isActive = true
    ElMessage.success(`"${scene.name}" scene activated`)

    // Add to history
    transitionHistory.value.unshift({
      time: new Date().toLocaleTimeString(),
      date: new Date().toISOString().split('T')[0],
      scene: scene.name,
      operator: 'Manual',
      duration: 'Active'
    })
  }).catch(() => {})
}

const editScene = (scene: any) => {
  editingScene.value = JSON.parse(JSON.stringify(scene))
  showEditDialog.value = true
}

const deleteScene = (scene: any) => {
  ElMessageBox.confirm(
      `Delete scene "${scene.name}"? This action cannot be undone.`,
      'Delete Scene',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = customScenes.value.findIndex(s => s.id === scene.id)
    if (index !== -1) {
      customScenes.value.splice(index, 1)
      ElMessage.success(`"${scene.name}" deleted`)
    }
  }).catch(() => {})
}

const toggleFavorite = (scene: any) => {
  scene.isFavorite = !scene.isFavorite
  ElMessage.success(`${scene.name} ${scene.isFavorite ? 'added to' : 'removed from'} favorites`)
}

const duplicateScene = (scene: any) => {
  const newSceneData = JSON.parse(JSON.stringify(scene))
  newSceneData.id = `scene-${Date.now()}`
  newSceneData.name = `${scene.name} (Copy)`
  newSceneData.isActive = false
  newSceneData.isFavorite = false
  customScenes.value.push(newSceneData)
  ElMessage.success(`"${scene.name}" duplicated`)
}

const scheduleScene = (scene: any) => {
  editingScene.value = scene
  showScheduleDialog.value = true
}

const saveSchedule = () => {
  if (editingScene.value && editingScene.value.schedule) {
    ElMessage.success(`Schedule set for "${editingScene.value.name}"`)
    // Update the scene in the list
    const index = customScenes.value.findIndex(s => s.id === editingScene.value.id)
    if (index !== -1) {
      customScenes.value[index].schedule = editingScene.value.schedule
    }
  }
  showScheduleDialog.value = false
  editingScene.value = null
}

const createNewScene = () => {
  showCreateDialog.value = true
}

const saveNewScene = () => {
  if (!newScene.value.name.trim()) {
    ElMessage.warning('Please enter a scene name')
    return
  }

  const sceneToAdd = {
    id: `scene-${Date.now()}`,
    name: newScene.value.name,
    description: newScene.value.description || 'Custom scene',
    icon: newScene.value.icon,
    isActive: false,
    isFavorite: false,
    lastUsed: new Date().toISOString().split('T')[0],
    schedule: null,
    settings: JSON.parse(JSON.stringify(newScene.value.settings)),
    devices: newScene.value.devices,
    tags: newScene.value.tags
  }

  customScenes.value.push(sceneToAdd)
  ElMessage.success(`"${newScene.value.name}" scene created`)

  // Reset form
  newScene.value = {
    name: '',
    description: '',
    icon: 'Star',
    tags: [],
    devices: [],
    settings: {
      hvac: { coolingSetpoint: 22, heatingSetpoint: 20, fanSpeed: 'Auto' },
      lighting: { brightness: 80, occupancySensing: true },
      blinds: { position: 40, autoAdjust: true }
    }
  }
  showCreateDialog.value = false
}

const updateScene = () => {
  if (editingScene.value) {
    const index = customScenes.value.findIndex(s => s.id === editingScene.value.id)
    if (index !== -1) {
      customScenes.value[index] = JSON.parse(JSON.stringify(editingScene.value))
      ElMessage.success(`"${editingScene.value.name}" updated`)
    }
  }
  showEditDialog.value = false
  editingScene.value = null
}

const addTag = () => {
  if (newTag.value.trim() && !newScene.value.tags.includes(newTag.value.trim())) {
    newScene.value.tags.push(newTag.value.trim())
    newTag.value = ''
  }
}

const removeTag = (tag: string) => {
  const index = newScene.value.tags.indexOf(tag)
  if (index !== -1) {
    newScene.value.tags.splice(index, 1)
  }
}

const toggleDevice = (deviceValue: string) => {
  const index = newScene.value.devices.indexOf(deviceValue)
  if (index === -1) {
    newScene.value.devices.push(deviceValue)
  } else {
    newScene.value.devices.splice(index, 1)
  }
}

const refreshData = () => {
  ElMessage.info('Refreshing custom scenes...')
  setTimeout(() => {
    ElMessage.success('Data refreshed successfully')
  }, 1000)
}

onMounted(() => {
  let progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(progressInterval)
    loadingProgress.value = 100
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2000)
})
</script>

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
          <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
        </div>
        <div class="loading-progress"><div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div></div>
        <div class="loading-tip">Custom Scene Manager</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="custom-scenes">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Custom Scenes</h2>
        <p class="subtitle">Create and manage personalized building automation scenes</p>
      </div>
      <div class="header-actions">
        <div class="view-toggle">
          <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
            <el-icon><Grid /></el-icon> Grid
          </el-button>
          <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
            <el-icon><List /></el-icon> List
          </el-button>
        </div>
        <el-button type="success" @click="createNewScene">
          <el-icon><Plus /></el-icon> New Scene
        </el-button>
        <el-button type="primary" @click="refreshData">
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="search-bar">
      <el-input v-model="searchKeyword" placeholder="Search scenes by name, description or tag..." clearable :prefix-icon="Search" style="width: 320px" />
      <span class="results-count">{{ filteredScenes.length }} scenes</span>
    </div>

    <!-- Favorite Scenes Section -->
    <div v-if="favoriteScenes.length > 0" class="favorites-section">
      <div class="section-header">
        <span><el-icon><StarFilled /></el-icon> Favorite Scenes</span>
        <el-tag type="warning" size="small">Quick Access</el-tag>
      </div>
      <div class="favorites-grid">
        <div v-for="scene in favoriteScenes" :key="scene.id" class="favorite-card" @click="activateScene(scene)">
          <div class="favorite-icon">
            <el-icon><component :is="getIconComponent(scene.icon)" /></el-icon>
          </div>
          <div class="favorite-info">
            <div class="favorite-name">{{ scene.name }}</div>
            <div class="favorite-description">{{ scene.description }}</div>
          </div>
          <div class="favorite-star" @click.stop="toggleFavorite(scene)">
            <el-icon :color="scene.isFavorite ? '#E6A23C' : '#C0C4CC'"><StarFilled /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- Scenes Grid View -->
    <div v-if="viewMode === 'grid'" class="scenes-grid">
      <div v-for="scene in filteredScenes" :key="scene.id" class="scene-card" :class="{ active: scene.isActive }">
        <div class="scene-header">
          <div class="scene-icon">
            <el-icon><component :is="getIconComponent(scene.icon)" /></el-icon>
          </div>
          <div class="scene-badge" v-if="scene.isActive">ACTIVE</div>
        </div>
        <div class="scene-name">{{ scene.name }}</div>
        <div class="scene-description">{{ scene.description }}</div>
        <div class="scene-tags">
          <el-tag v-for="tag in scene.tags" :key="tag" size="small" type="info" effect="plain">{{ tag }}</el-tag>
        </div>
        <div class="scene-devices">
          <span v-for="device in scene.devices" :key="device" class="device-badge">{{ device }}</span>
        </div>
        <div class="scene-schedule" v-if="scene.schedule">
          <el-icon><Clock /></el-icon> {{ scene.schedule }}
        </div>
        <div class="scene-actions">
          <el-button size="small" type="primary" @click="activateScene(scene)">
            <el-icon><Operation /></el-icon> Apply
          </el-button>
          <el-button size="small" @click="editScene(scene)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" @click="duplicateScene(scene)">
            <el-icon><CopyDocument /></el-icon> Copy
          </el-button>
          <el-button size="small" type="danger" @click="deleteScene(scene)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Scenes List View -->
    <!-- Scenes List View -->
    <el-card v-else class="list-view-card" shadow="hover">
      <el-table :data="filteredScenes" stripe>
        <el-table-column label="Status" align="center">
          <template #default="{ row }">
            <div class="status-cell">
              <div v-if="row.isActive" class="active-indicator"></div>
              <span v-if="row.isActive" class="active-text">Active</span>
              <span v-else class="inactive-text">Inactive</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Scene"  align="center">
          <template #default="{ row }">
            <div class="scene-cell">
              <el-icon><component :is="getIconComponent(row.icon)" /></el-icon>
              <div>
                <div class="scene-name-cell">{{ row.name }}</div>
                <div class="scene-desc-cell">{{ row.description }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Tags" align="center">
          <template #default="{ row }">
            <div class="tags-cell">
              <el-tag v-for="tag in row.tags.slice(0, 2)" :key="tag" size="small" type="info" effect="plain">{{ tag }}</el-tag>
              <span v-if="row.tags.length > 2" class="more-tags">+{{ row.tags.length - 2 }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="Schedule" align="center">
          <template #default="{ row }">
            <span v-if="row.schedule">{{ row.schedule }}</span>
            <span v-else class="no-schedule">Not scheduled</span>
          </template>
        </el-table-column>
        <el-table-column prop="lastUsed" label="Last Used" align="center" />
        <el-table-column label="Actions" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="activateScene(row)">Apply</el-button>
            <el-button size="small" link @click="editScene(row)">Edit</el-button>
            <el-button size="small" link @click="scheduleScene(row)">Schedule</el-button>
            <el-button size="small" type="danger" link @click="deleteScene(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Create Scene Dialog -->
    <el-dialog v-model="showCreateDialog" title="Create Custom Scene" width="700px">
      <el-form :model="newScene" label-width="120px">
        <el-form-item label="Scene Name" required>
          <el-input v-model="newScene.name" placeholder="Enter scene name" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="newScene.description" type="textarea" :rows="2" placeholder="Describe what this scene does" />
        </el-form-item>
        <el-form-item label="Icon">
          <el-select v-model="newScene.icon" style="width: 200px">
            <el-option label="Sunny" value="Sunny" />
            <el-option label="Moon" value="Moon" />
            <el-option label="Home" value="HomeFilled" />
            <el-option label="Work" value="Monitor" />
            <el-option label="Analytics" value="DataAnalysis" />
            <el-option label="Meeting" value="User" />
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <div class="tag-input">
            <el-input v-model="newTag" placeholder="Add tag" style="width: 200px" @keyup.enter="addTag" />
            <el-button @click="addTag">Add</el-button>
          </div>
          <div class="tag-list">
            <el-tag v-for="tag in newScene.tags" :key="tag" closable @close="removeTag(tag)" style="margin-right: 8px; margin-top: 8px">
              {{ tag }}
            </el-tag>
          </div>
        </el-form-item>
        <el-form-item label="Included Devices">
          <div class="device-options">
            <el-checkbox v-for="device in deviceOptions" :key="device.value" :label="device.value" @change="toggleDevice(device.value)">
              {{ device.label }}
            </el-checkbox>
          </div>
        </el-form-item>

        <!-- HVAC Settings -->
        <div v-if="newScene.devices.includes('HVAC')" class="settings-section">
          <h4>HVAC Settings</h4>
          <div class="settings-grid">
            <div class="setting-item">
              <span class="setting-label">Cooling Setpoint</span>
              <el-input-number v-model="newScene.settings.hvac.coolingSetpoint" :min="18" :max="26" size="small" /> °C
            </div>
            <div class="setting-item">
              <span class="setting-label">Heating Setpoint</span>
              <el-input-number v-model="newScene.settings.hvac.heatingSetpoint" :min="16" :max="24" size="small" /> °C
            </div>
            <div class="setting-item">
              <span class="setting-label">Fan Speed</span>
              <el-select v-model="newScene.settings.hvac.fanSpeed" size="small" style="width: 100px">
                <el-option label="Auto" value="Auto" />
                <el-option label="Low" value="Low" />
                <el-option label="Medium" value="Medium" />
                <el-option label="High" value="High" />
              </el-select>
            </div>
          </div>
        </div>

        <!-- Lighting Settings -->
        <div v-if="newScene.devices.includes('Lighting')" class="settings-section">
          <h4>Lighting Settings</h4>
          <div class="settings-grid">
            <div class="setting-item">
              <span class="setting-label">Brightness</span>
              <el-slider v-model="newScene.settings.lighting.brightness" :min="0" :max="100" style="width: 200px" />
              <span>{{ newScene.settings.lighting.brightness }}%</span>
            </div>
            <div class="setting-item">
              <span class="setting-label">Occupancy Sensing</span>
              <el-switch v-model="newScene.settings.lighting.occupancySensing" />
            </div>
          </div>
        </div>

        <!-- Blinds Settings -->
        <div v-if="newScene.devices.includes('Blinds')" class="settings-section">
          <h4>Blind Settings</h4>
          <div class="settings-grid">
            <div class="setting-item">
              <span class="setting-label">Position</span>
              <el-slider v-model="newScene.settings.blinds.position" :min="0" :max="100" style="width: 200px" />
              <span>{{ newScene.settings.blinds.position }}%</span>
            </div>
            <div class="setting-item">
              <span class="setting-label">Auto Adjust</span>
              <el-switch v-model="newScene.settings.blinds.autoAdjust" />
            </div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveNewScene">Create Scene</el-button>
      </template>
    </el-dialog>

    <!-- Edit Scene Dialog -->
    <el-dialog v-model="showEditDialog" title="Edit Scene" width="700px">
      <div v-if="editingScene">
        <el-form :model="editingScene" label-width="120px">
          <el-form-item label="Scene Name">
            <el-input v-model="editingScene.name" />
          </el-form-item>
          <el-form-item label="Description">
            <el-input v-model="editingScene.description" type="textarea" :rows="2" />
          </el-form-item>
          <el-form-item label="Icon">
            <el-select v-model="editingScene.icon" style="width: 200px">
              <el-option label="Sunny" value="Sunny" />
              <el-option label="Moon" value="Moon" />
              <el-option label="Home" value="HomeFilled" />
              <el-option label="Work" value="Monitor" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showEditDialog = false">Cancel</el-button>
        <el-button type="primary" @click="updateScene">Save Changes</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Dialog -->
    <el-dialog v-model="showScheduleDialog" title="Schedule Scene" width="450px">
      <div v-if="editingScene">
        <el-form label-width="100px">
          <el-form-item label="Scene">
            <span>{{ editingScene.name }}</span>
          </el-form-item>
          <el-form-item label="Schedule Time">
            <el-time-picker v-model="editingScene.scheduleTime" format="HH:mm" placeholder="Select time" />
          </el-form-item>
          <el-form-item label="Repeat">
            <el-select v-model="editingScene.repeatDays" multiple placeholder="Select days" style="width: 100%">
              <el-option label="Monday" value="Mon" />
              <el-option label="Tuesday" value="Tue" />
              <el-option label="Wednesday" value="Wed" />
              <el-option label="Thursday" value="Thu" />
              <el-option label="Friday" value="Fri" />
              <el-option label="Saturday" value="Sat" />
              <el-option label="Sunday" value="Sun" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="showScheduleDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveSchedule">Save Schedule</el-button>
      </template>
    </el-dialog>

    <!-- Transition History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Scene Activation History</span>
          <el-tag type="info" size="small">Last 4 activations</el-tag>
        </div>
      </template>
      <el-table :data="transitionHistory" stripe>
        <el-table-column prop="date" label="Date" align="center" />
        <el-table-column prop="time" label="Time" align="center" />
        <el-table-column prop="scene" label="Scene"align="center"  />
        <el-table-column prop="operator" label="Activated By" align="center"  />
        <el-table-column prop="duration" label="Duration" align="center"  />
      </el-table>
    </el-card>
  </div>
</template>

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
.custom-scenes {
  padding: 24px;
  background: linear-gradient(135deg, #f5f0ff 0%, #e8e0f5 100%);
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
  background: linear-gradient(135deg, #6a1b9a, #9c27b0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #7b1fa2;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.view-toggle {
  display: flex;
  gap: 0;
  border-radius: 8px;
  overflow: hidden;
}

.view-toggle .el-button { border-radius: 0; margin: 0; }

/* Search Bar */
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 12px;
}

.results-count { font-size: 13px; color: #909399; }

/* Favorites Section */
.favorites-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 600;
  font-size: 15px;
}

.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.favorite-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.favorite-card:hover {
  background: #f0f2f5;
  transform: translateX(4px);
}

.favorite-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6a1b9a, #9c27b0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.favorite-info { flex: 1; }
.favorite-name { font-weight: 600; margin-bottom: 4px; }
.favorite-description { font-size: 12px; color: #909399; }
.favorite-star { cursor: pointer; }

/* Scenes Grid */
.scenes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.scene-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.scene-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1); }
.scene-card.active { border: 2px solid #67C23A; background: #f0f9f0; }

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.scene-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6a1b9a, #9c27b0);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: white;
}

.scene-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 8px;
  background: #67C23A;
  color: white;
  border-radius: 20px;
}

.scene-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.scene-description { font-size: 13px; color: #606266; margin-bottom: 12px; line-height: 1.4; }

.scene-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }

.scene-devices { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.device-badge { font-size: 11px; padding: 2px 8px; background: #ecf5ff; color: #409EFF; border-radius: 12px; }

.scene-schedule { font-size: 12px; color: #909399; margin-bottom: 16px; display: flex; align-items: center; gap: 4px; }

.scene-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* List View */
.list-view-card { border-radius: 20px; margin-bottom: 24px; }
.scene-cell { display: flex; align-items: center; gap: 12px; }
.scene-name-cell { font-weight: 600; }
.scene-desc-cell { font-size: 12px; color: #909399; }
.tags-cell { display: flex; gap: 4px; flex-wrap: wrap; align-items: center;justify-content: center }
.more-tags { font-size: 11px; color: #909399; }
.no-schedule { color: #c0c4cc; font-style: italic; }
.active-indicator { width: 10px; height: 10px; background: #67C23A; border-radius: 50%; }

/* Settings Section */
.settings-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.settings-section h4 { margin: 0 0 12px 0; font-size: 14px; font-weight: 600; }

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.setting-item { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.setting-label { font-size: 13px; color: #606266; min-width: 100px; }

/* Tag Input */
.tag-input { display: flex; gap: 8px; align-items: center; }
.tag-list { display: flex; flex-wrap: wrap; margin-top: 8px; }

/* Device Options */
.device-options { display: flex; gap: 16px; flex-wrap: wrap; }

/* History Card */
.history-card {
  border-radius: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

/* Responsive */
@media (max-width: 768px) {
  .custom-scenes { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .scenes-grid { grid-template-columns: 1fr; }
  .settings-grid { grid-template-columns: 1fr; }
}
/* Status Cell */
.status-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.active-indicator {
  width: 8px;
  height: 8px;
  background: #67C23A;
  border-radius: 50%;
  animation: pulse-green 1.5s infinite;
}

@keyframes pulse-green {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.active-text {
  color: #67C23A;
  font-weight: 500;
  font-size: 12px;
}

.inactive-text {
  color: #909399;
  font-size: 12px;
}

</style>

<style>

</style>