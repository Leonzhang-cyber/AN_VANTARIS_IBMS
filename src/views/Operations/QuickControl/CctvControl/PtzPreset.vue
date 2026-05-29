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
        <div class="loading-tip">PTZ Preset</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- PTZ Preset Page Content -->
  <div v-else class="ptz-preset-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Camera /></el-icon>
          <span>CCTV Control</span>
        </div>
        <h1>PTZ Preset Management</h1>
        <p class="subtitle">Save, recall, and manage camera preset positions for quick navigation</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportPresets">
          <el-icon><Download /></el-icon>
          <span>Export</span>
        </button>
      </div>
    </div>

    <!-- Camera Selector & Live Preview -->
    <div class="camera-section">
      <div class="camera-selector-card">
        <div class="section-header">
          <div class="header-left">
            <div class="header-icon"><el-icon><VideoCamera /></el-icon></div>
            <h3>Select Camera</h3>
          </div>
        </div>
        <div class="camera-list">
          <div
              v-for="cam in cameras"
              :key="cam.id"
              class="camera-item"
              :class="{ active: selectedCamera?.id === cam.id }"
              @click="selectCamera(cam)"
          >
            <div class="camera-avatar" :class="cam.status">
              <el-icon><Camera /></el-icon>
            </div>
            <div class="camera-details">
              <div class="camera-name">{{ cam.name }}</div>
              <div class="camera-location">{{ cam.location }}</div>
            </div>
            <div class="camera-status-badge" :class="cam.status">
              {{ cam.status === 'online' ? 'Live' : 'Offline' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Live Preview -->
      <div class="live-preview-card">
        <div class="section-header">
          <div class="header-left">
            <div class="header-icon"><el-icon><VideoCamera /></el-icon></div>
            <h3>Live View</h3>
          </div>
          <div class="live-badge" v-if="selectedCamera?.status === 'online'">
            <span class="live-dot"></span>
            <span>LIVE</span>
          </div>
        </div>
        <div class="preview-container">
          <div class="video-wrapper">
            <video
                ref="previewVideoRef"
                :src="VIDEO_URL"
                autoplay
                muted
                loop
                playsinline
                class="preview-video"
                v-if="selectedCamera?.status === 'online'"
            ></video>
            <div v-else class="offline-placeholder">
              <el-icon><VideoCamera /></el-icon>
              <span>Camera Offline</span>
            </div>
            <div class="preview-overlay">
              <div class="camera-info">
                <span class="camera-name">{{ selectedCamera?.name || 'Select Camera' }}</span>
                <span class="camera-time">{{ currentTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- PTZ Presets Section -->
    <div class="presets-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Star /></el-icon></div>
          <h3>Saved Presets</h3>
          <span class="preset-count">{{ filteredPresets.length }} presets</span>
        </div>
        <div class="header-right">
          <button class="create-preset-btn" @click="openCreatePresetDialog" :disabled="!selectedCamera">
            <el-icon><Plus /></el-icon>
            Save Current Position
          </button>
        </div>
      </div>

      <div v-if="filteredPresets.length === 0" class="empty-presets">
        <div class="empty-icon">
          <el-icon><Star /></el-icon>
        </div>
        <h4>No Presets Saved</h4>
        <p>Save camera positions as presets for quick navigation</p>
      </div>

      <div v-else class="presets-grid">
        <div v-for="preset in filteredPresets" :key="preset.id" class="preset-card">
          <div class="preset-header">
            <div class="preset-thumb">
              <img :src="preset.thumbnail" :alt="preset.name" />
              <div class="preset-number">{{ preset.number }}</div>
            </div>
          </div>
          <div class="preset-info">
            <div class="preset-name">{{ preset.name }}</div>
            <div class="preset-description">{{ preset.description }}</div>
            <div class="preset-meta">
              <span><el-icon><Clock /></el-icon> {{ preset.createdAt }}</span>
            </div>
          </div>
          <div class="preset-actions">
            <button class="action-btn-small recall" @click="recallPreset(preset)">
              <el-icon><VideoPlay /></el-icon>
              Recall
            </button>
            <button class="action-btn-small update" @click="updatePreset(preset)">
              <el-icon><Edit /></el-icon>
              Update
            </button>
            <button class="action-btn-small delete" @click="deletePreset(preset)">
              <el-icon><Delete /></el-icon>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Preset Dialog -->
    <div v-if="presetDialogVisible" class="modal-overlay" @click.self="presetDialogVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ isEditing ? 'Edit Preset' : 'Save New Preset' }}</h3>
          <button class="modal-close" @click="presetDialogVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Preset Name</label>
            <input type="text" v-model="presetForm.name" placeholder="e.g., Main Entrance, Server Room View" class="form-input" />
          </div>
          <div class="form-group">
            <label>Description (Optional)</label>
            <input type="text" v-model="presetForm.description" placeholder="Describe this preset..." class="form-input" />
          </div>
          <div class="form-group">
            <label>Preset Number</label>
            <select v-model="presetForm.number" class="form-select">
              <option v-for="n in 16" :key="n" :value="n">Preset {{ n }}</option>
            </select>
          </div>
          <div class="preview-info" v-if="selectedCamera">
            <div class="info-row">
              <span class="info-label">Camera:</span>
              <span class="info-value">{{ selectedCamera.name }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Current Position:</span>
              <span class="info-value">Pan: {{ mockPan }}° | Tilt: {{ mockTilt }}° | Zoom: {{ mockZoom }}x</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="presetDialogVisible = false">Cancel</button>
          <button class="dialog-btn confirm" @click="savePreset">Save Preset</button>
        </div>
      </div>
    </div>

    <!-- PTZ Control Panel -->
    <div class="ptz-control-card">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Setting /></el-icon></div>
          <h3>Manual PTZ Control</h3>
        </div>
        <div class="position-info">
          <span>Pan: {{ mockPan }}°</span>
          <span>Tilt: {{ mockTilt }}°</span>
          <span>Zoom: {{ mockZoom }}x</span>
        </div>
      </div>

      <div class="ptz-controls">
        <div class="ptz-pad">
          <div class="ptz-row">
            <button class="ptz-btn" @click="ptzMove('up')" :disabled="!selectedCamera">
              <el-icon><ArrowUp /></el-icon>
            </button>
          </div>
          <div class="ptz-row">
            <button class="ptz-btn" @click="ptzMove('left')" :disabled="!selectedCamera">
              <el-icon><ArrowLeft /></el-icon>
            </button>
            <button class="ptz-btn center" @click="ptzHome" :disabled="!selectedCamera">
              <el-icon><HomeFilled /></el-icon>
            </button>
            <button class="ptz-btn" @click="ptzMove('right')" :disabled="!selectedCamera">
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
          <div class="ptz-row">
            <button class="ptz-btn" @click="ptzMove('down')" :disabled="!selectedCamera">
              <el-icon><ArrowDown /></el-icon>
            </button>
          </div>
        </div>
        <div class="zoom-controls">
          <button class="zoom-btn" @click="ptzZoom('in')" :disabled="!selectedCamera">
            <el-icon><ZoomIn /></el-icon>
            <span>Zoom In</span>
          </button>
          <button class="zoom-btn" @click="ptzZoom('out')" :disabled="!selectedCamera">
            <el-icon><ZoomOut /></el-icon>
            <span>Zoom Out</span>
          </button>
        </div>
        <div class="speed-control">
          <label>Pan/Tilt Speed</label>
          <input type="range" v-model="ptzSpeed" min="1" max="10" step="1" class="speed-slider" />
          <span class="speed-value">{{ ptzSpeed }}</span>
        </div>
      </div>
    </div>

    <!-- Recall Success Toast -->
    <div v-if="recallSuccessVisible" class="toast-notification success">
      <el-icon><SuccessFilled /></el-icon>
      <span>Preset recalled successfully</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Refresh, Download, Camera, VideoCamera, Star, Plus, VideoPlay,
  Edit, Delete, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, HomeFilled,
  ZoomIn, ZoomOut, Clock, Setting, SuccessFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Connecting to cameras...', 'Loading presets...', 'Almost ready...']

// Video URL
const VIDEO_URL = 'https://aegisnx.com/wp-content/uploads/2025/12/firlvideo.mp4'

// Data Models
interface Camera {
  id: number
  name: string
  location: string
  status: 'online' | 'offline'
}

interface PTZPreset {
  id: number
  cameraId: number
  number: number
  name: string
  description: string
  thumbnail: string
  createdAt: string
  pan: number
  tilt: number
  zoom: number
}

// State
const selectedCamera = ref<Camera | null>(null)
const previewVideoRef = ref<HTMLVideoElement | null>(null)
const currentTime = ref('')
const ptzSpeed = ref(5)
const mockPan = ref(0)
const mockTilt = ref(0)
const mockZoom = ref(1)
const presetDialogVisible = ref(false)
const isEditing = ref(false)
const recallSuccessVisible = ref(false)
let recallTimeout: ReturnType<typeof setTimeout> | null = null

const presetForm = ref({
  id: null as number | null,
  name: '',
  description: '',
  number: 1
})

// Mock Data - Cameras
const cameras = ref<Camera[]>([
  { id: 1, name: 'Main Entrance', location: 'Building A - Ground Floor', status: 'online' },
  { id: 2, name: 'North Wing', location: 'Building A - Floor 1', status: 'online' },
  { id: 3, name: 'South Wing', location: 'Building A - Floor 1', status: 'online' },
  { id: 4, name: 'Executive Corridor', location: 'Building A - Floor 2', status: 'online' },
  { id: 5, name: 'Server Room', location: 'Data Center', status: 'online' },
  { id: 6, name: 'Parking Lot North', location: 'Exterior', status: 'offline' },
  { id: 7, name: 'Cafeteria', location: 'Building B - Floor 1', status: 'online' },
  { id: 8, name: 'Security Office', location: 'Building B - Floor 1', status: 'online' }
])

// Mock Data - Presets
const presets = ref<PTZPreset[]>([
  { id: 1, cameraId: 1, number: 1, name: 'Main Entrance', description: 'Front gate view', thumbnail: 'https://picsum.photos/id/20/200/120', createdAt: '2025-05-28', pan: 0, tilt: 0, zoom: 1 },
  { id: 2, cameraId: 1, number: 2, name: 'Reception Desk', description: 'Lobby area', thumbnail: 'https://picsum.photos/id/21/200/120', createdAt: '2025-05-28', pan: 45, tilt: -10, zoom: 1.5 },
  { id: 3, cameraId: 5, number: 1, name: 'Server Rack A', description: 'Main server row', thumbnail: 'https://picsum.photos/id/26/200/120', createdAt: '2025-05-27', pan: 0, tilt: 0, zoom: 2 },
  { id: 4, cameraId: 5, number: 2, name: 'Cooling System', description: 'HVAC monitoring', thumbnail: 'https://picsum.photos/id/27/200/120', createdAt: '2025-05-27', pan: 90, tilt: 0, zoom: 1 },
  { id: 5, cameraId: 2, number: 1, name: 'North Corridor', description: 'Main hallway', thumbnail: 'https://picsum.photos/id/22/200/120', createdAt: '2025-05-26', pan: 0, tilt: 0, zoom: 1 }
])

// Computed
const filteredPresets = computed(() => {
  if (!selectedCamera.value) return []
  return presets.value.filter(p => p.cameraId === selectedCamera.value?.id)
})

// Functions
const selectCamera = (camera: Camera) => {
  selectedCamera.value = camera
  ElMessage.success(`Switched to ${camera.name}`)
  // Reset mock PTZ values for new camera
  mockPan.value = 0
  mockTilt.value = 0
  mockZoom.value = 1
}

const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString()
}

const ptzMove = (direction: string) => {
  if (!selectedCamera.value) return
  const step = ptzSpeed.value * 5
  switch (direction) {
    case 'up':
      mockTilt.value = Math.min(90, mockTilt.value + step)
      break
    case 'down':
      mockTilt.value = Math.max(-90, mockTilt.value - step)
      break
    case 'left':
      mockPan.value = Math.max(-180, mockPan.value - step)
      break
    case 'right':
      mockPan.value = Math.min(180, mockPan.value + step)
      break
  }
  ElMessage.info(`${direction.toUpperCase()} - Pan: ${mockPan.value}°, Tilt: ${mockTilt.value}°`)
}

const ptzHome = () => {
  if (!selectedCamera.value) return
  mockPan.value = 0
  mockTilt.value = 0
  mockZoom.value = 1
  ElMessage.info('Camera returned to home position')
}

const ptzZoom = (action: string) => {
  if (!selectedCamera.value) return
  if (action === 'in') {
    mockZoom.value = Math.min(10, mockZoom.value + 0.5)
  } else {
    mockZoom.value = Math.max(1, mockZoom.value - 0.5)
  }
  ElMessage.info(`Zoom ${action === 'in' ? 'in' : 'out'} - ${mockZoom.value}x`)
}

const openCreatePresetDialog = () => {
  if (!selectedCamera.value) {
    ElMessage.warning('Please select a camera first')
    return
  }
  isEditing.value = false
  presetForm.value = {
    id: null,
    name: '',
    description: '',
    number: filteredPresets.value.length + 1
  }
  presetDialogVisible.value = true
}

const updatePreset = (preset: PTZPreset) => {
  isEditing.value = true
  presetForm.value = {
    id: preset.id,
    name: preset.name,
    description: preset.description,
    number: preset.number
  }
  presetDialogVisible.value = true
}

const savePreset = () => {
  if (!selectedCamera.value) return
  if (!presetForm.value.name.trim()) {
    ElMessage.warning('Please enter a preset name')
    return
  }

  if (isEditing.value && presetForm.value.id) {
    const index = presets.value.findIndex(p => p.id === presetForm.value.id)
    if (index !== -1) {
      presets.value[index] = {
        ...presets.value[index],
        name: presetForm.value.name,
        description: presetForm.value.description,
        number: presetForm.value.number
      }
      ElMessage.success('Preset updated successfully')
    }
  } else {
    const newPreset: PTZPreset = {
      id: Date.now(),
      cameraId: selectedCamera.value.id,
      number: presetForm.value.number,
      name: presetForm.value.name,
      description: presetForm.value.description,
      thumbnail: `https://picsum.photos/id/${Math.floor(Math.random() * 50) + 20}/200/120`,
      createdAt: new Date().toISOString().slice(0, 10),
      pan: mockPan.value,
      tilt: mockTilt.value,
      zoom: mockZoom.value
    }
    presets.value.push(newPreset)
    ElMessage.success('Preset saved successfully')
  }
  presetDialogVisible.value = false
}

const recallPreset = (preset: PTZPreset) => {
  if (!selectedCamera.value || selectedCamera.value.id !== preset.cameraId) {
    ElMessage.warning('Please select the correct camera first')
    return
  }
  mockPan.value = preset.pan
  mockTilt.value = preset.tilt
  mockZoom.value = preset.zoom

  recallSuccessVisible.value = true
  if (recallTimeout) clearTimeout(recallTimeout)
  recallTimeout = setTimeout(() => {
    recallSuccessVisible.value = false
  }, 2000)

  ElMessage.success(`Recalled preset: ${preset.name}`)
}

const deletePreset = (preset: PTZPreset) => {
  const index = presets.value.findIndex(p => p.id === preset.id)
  if (index !== -1) {
    presets.value.splice(index, 1)
    ElMessage.success(`Deleted preset: ${preset.name}`)
  }
}

const refreshData = () => {
  if (previewVideoRef.value) {
    previewVideoRef.value.load()
    previewVideoRef.value.play().catch(e => console.log('Play error:', e))
  }
  ElMessage.success('Data refreshed')
}

const exportPresets = () => {
  ElMessage.info('Exporting presets...')
}

// Start time update
let timeInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      updateCurrentTime()
      timeInterval = setInterval(updateCurrentTime, 1000)
      // Set default camera
      const onlineCam = cameras.value.find(c => c.status === 'online')
      if (onlineCam) selectedCamera.value = onlineCam

      nextTick(() => {
        if (previewVideoRef.value) {
          previewVideoRef.value.play().catch(e => console.log('Play error:', e))
        }
      })
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (recallTimeout) clearTimeout(recallTimeout)
})
</script>

<style scoped>
/* Loading Screen */
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
.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
  font-weight: 500;
}
.loading-subtip {
  font-size: 11px;
  color: #64748b;
  letter-spacing: 0.5px;
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Main Content */
.ptz-preset-page {
  padding: 24px;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b2e 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #334155;
  background: #1e293b;
  color: #cbd5e1;
}
.action-btn:hover {
  transform: translateY(-2px);
  background: #334155;
}
.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}

/* Camera Section */
.camera-section {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}
.camera-selector-card, .live-preview-card, .ptz-control-card {
  background: #1e293b;
  border-radius: 20px;
  padding: 20px;
  border: 1px solid #334155;
}
.camera-selector-card {
  flex: 1;
  min-width: 280px;
}
.live-preview-card {
  flex: 2;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.header-left h3 {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}

/* Camera List */
.camera-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.camera-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #0f172a;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}
.camera-item:hover {
  background: #334155;
}
.camera-item.active {
  border-color: #3b82f6;
  background: #1e3a5f;
}
.camera-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}
.camera-avatar.online {
  background: #10b981;
  color: white;
}
.camera-avatar.offline {
  background: #64748b;
  color: white;
}
.camera-details {
  flex: 1;
}
.camera-name {
  font-weight: 600;
  color: white;
  margin-bottom: 2px;
}
.camera-location {
  font-size: 11px;
  color: #94a3b8;
}
.camera-status-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 20px;
}
.camera-status-badge.online {
  background: #10b981;
  color: white;
}
.camera-status-badge.offline {
  background: #64748b;
  color: white;
}

/* Live Preview */
.preview-container {
  position: relative;
}
.video-wrapper {
  position: relative;
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
}
.preview-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.offline-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #0f172a;
  color: #64748b;
  min-height: 250px;
}
.offline-placeholder .el-icon {
  font-size: 48px;
}
.preview-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 12px;
}
.camera-info {
  display: flex;
  flex-direction: column;
}
.camera-name {
  color: white;
  font-weight: 600;
  font-size: 14px;
}
.camera-time {
  color: #94a3b8;
  font-size: 11px;
}
.live-badge {
  background: #ef4444;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  animation: pulse 1s infinite;
}
.live-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

/* Presets Section */
.presets-section {
  background: #1e293b;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 28px;
  border: 1px solid #334155;
}
.preset-count {
  background: #334155;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  color: #94a3b8;
}
.create-preset-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.create-preset-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.create-preset-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-presets {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  background: #334155;
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  color: #64748b;
}
.empty-presets h4 {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0 0 8px 0;
}
.empty-presets p {
  font-size: 14px;
  color: #64748b;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}
.preset-card {
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.2s;
}
.preset-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}
.preset-header {
  position: relative;
}
.preset-thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}
.preset-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.preset-number {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}
.preset-info {
  padding: 12px;
}
.preset-name {
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}
.preset-description {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 6px;
}
.preset-meta {
  font-size: 10px;
  color: #64748b;
}
.preset-meta .el-icon {
  margin-right: 2px;
  vertical-align: middle;
}
.preset-actions {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid #334155;
}
.action-btn-small {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.action-btn-small.recall {
  background: #3b82f6;
  color: white;
}
.action-btn-small.recall:hover {
  background: #2563eb;
}
.action-btn-small.update {
  background: #f59e0b;
  color: white;
}
.action-btn-small.update:hover {
  background: #d97706;
}
.action-btn-small.delete {
  background: #ef4444;
  color: white;
}
.action-btn-small.delete:hover {
  background: #dc2626;
}

/* PTZ Control Card */
.ptz-control-card {
  margin-bottom: 0;
}
.position-info {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}
.ptz-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 30px;
  justify-content: center;
  align-items: center;
}
.ptz-pad {
  background: #0f172a;
  padding: 20px;
  border-radius: 24px;
  display: inline-block;
}
.ptz-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 8px 0;
}
.ptz-btn {
  width: 56px;
  height: 56px;
  background: #334155;
  border: none;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
  font-size: 24px;
}
.ptz-btn:hover:not(:disabled) {
  background: #3b82f6;
}
.ptz-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.ptz-btn.center {
  background: #3b82f6;
}
.ptz-btn.center:hover:not(:disabled) {
  background: #2563eb;
}
.zoom-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.zoom-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  background: #334155;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}
.zoom-btn:hover:not(:disabled) {
  background: #3b82f6;
}
.zoom-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.speed-control {
  display: flex;
  align-items: center;
  gap: 12px;
}
.speed-control label {
  font-size: 13px;
  color: #94a3b8;
}
.speed-slider {
  width: 150px;
  height: 4px;
  -webkit-appearance: none;
  background: #334155;
  border-radius: 4px;
}
.speed-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #3b82f6;
  border-radius: 50%;
  cursor: pointer;
}
.speed-value {
  font-size: 13px;
  font-weight: 600;
  color: #3b82f6;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: #1e293b;
  border-radius: 24px;
  width: 480px;
  max-width: 90%;
  overflow: hidden;
  border: 1px solid #334155;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #334155;
}
.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0;
}
.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #94a3b8;
}
.modal-body {
  padding: 24px;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #334155;
}

.form-group {
  margin-bottom: 16px;
}
.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #cbd5e1;
  margin-bottom: 6px;
}
.form-input, .form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #334155;
  border-radius: 10px;
  background: #0f172a;
  color: white;
  font-size: 14px;
}
.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #3b82f6;
}
.preview-info {
  background: #0f172a;
  border-radius: 12px;
  padding: 12px;
  margin-top: 16px;
}
.info-row {
  display: flex;
  margin-bottom: 6px;
}
.info-label {
  width: 100px;
  color: #64748b;
  font-size: 12px;
}
.info-value {
  color: #cbd5e1;
  font-size: 12px;
}

.dialog-btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.dialog-btn.cancel {
  background: #334155;
  color: #cbd5e1;
}
.dialog-btn.cancel:hover {
  background: #475569;
}
.dialog-btn.confirm {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}
.dialog-btn.confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  bottom: 30px;
  right: 30px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  background: #1e293b;
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  z-index: 1100;
  animation: slideIn 0.3s ease;
}
.toast-notification.success .el-icon {
  color: #10b981;
}
@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>