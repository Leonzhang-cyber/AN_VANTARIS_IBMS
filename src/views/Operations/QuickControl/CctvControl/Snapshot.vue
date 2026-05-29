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
        <div class="loading-tip">Snapshot Center</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Snapshot Page Content -->
  <div v-else class="snapshot-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Camera /></el-icon>
          <span>CCTV Control</span>
        </div>
        <h1>Snapshot Management</h1>
        <p class="subtitle">Capture, view, and manage camera snapshots with timestamp and annotation support</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportAllSnapshots">
          <el-icon><Download /></el-icon>
          <span>Export All</span>
        </button>
      </div>
    </div>

    <!-- Live Camera Preview & Capture -->
    <div class="capture-section">
      <div class="live-preview">
        <div class="section-header">
          <div class="header-left">
            <div class="header-icon"><el-icon><VideoCamera /></el-icon></div>
            <h3>Live Camera Preview</h3>
          </div>
          <div class="camera-selector">
            <select v-model="selectedCamera" class="camera-select">
              <option v-for="cam in cameras" :key="cam.id" :value="cam.id">
                {{ cam.name }} - {{ cam.location }}
              </option>
            </select>
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
            ></video>
            <div class="preview-overlay">
              <div class="camera-info">
                <span class="camera-name">{{ currentCameraName }}</span>
                <span class="live-time">{{ currentTime }}</span>
              </div>
              <div class="live-badge">
                <span class="live-dot"></span>
                <span>LIVE</span>
              </div>
            </div>
          </div>
          <div class="capture-controls">
            <button class="capture-btn" @click="captureSnapshot">
              <el-icon><Camera /></el-icon>
              <span>Capture Snapshot</span>
            </button>
            <div class="capture-settings">
              <label class="checkbox-label">
                <input type="checkbox" v-model="captureSettings.addTimestamp" />
                <span>Add Timestamp</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="captureSettings.addAnnotation" />
                <span>Add Annotation</span>
              </label>
              <input
                  v-if="captureSettings.addAnnotation"
                  v-model="captureSettings.annotation"
                  placeholder="Enter annotation..."
                  class="annotation-input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Snapshot Gallery -->
    <div class="gallery-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Picture /></el-icon></div>
          <h3>Snapshot Gallery</h3>
          <span class="snapshot-count">{{ filteredSnapshots.length }} snapshots</span>
        </div>
        <div class="header-right">
          <div class="filter-group">
            <input type="text" v-model="searchText" placeholder="Search snapshots..." class="search-input" />
          </div>
          <select v-model="cameraFilter" class="filter-select">
            <option value="all">All Cameras</option>
            <option v-for="cam in cameras" :key="cam.id" :value="cam.id">
              {{ cam.name }}
            </option>
          </select>
          <select v-model="dateFilter" class="filter-select">
            <option value="all">All Time</option>
            <option value="today">Today</option>
            <option value="week">Last 7 Days</option>
            <option value="month">Last 30 Days</option>
          </select>
          <button class="clear-btn" @click="clearFilters" v-if="hasActiveFilters">
            Clear Filters
          </button>
        </div>
      </div>

      <div v-if="filteredSnapshots.length === 0" class="empty-gallery">
        <div class="empty-icon">
          <el-icon><Picture /></el-icon>
        </div>
        <h4>No Snapshots Found</h4>
        <p>Capture your first snapshot using the live camera preview above</p>
      </div>

      <div v-else class="snapshots-grid">
        <div v-for="snapshot in paginatedSnapshots" :key="snapshot.id" class="snapshot-card">
          <div class="snapshot-image">
            <img :src="snapshot.imageUrl" :alt="snapshot.title" />
            <div class="snapshot-actions-overlay">
              <button class="action-icon" @click="viewSnapshot(snapshot)">
                <el-icon><ZoomIn /></el-icon>
              </button>
              <button class="action-icon" @click="downloadSnapshot(snapshot)">
                <el-icon><Download /></el-icon>
              </button>
              <button class="action-icon delete" @click="deleteSnapshot(snapshot)">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
          </div>
          <div class="snapshot-info">
            <div class="snapshot-title">{{ snapshot.title }}</div>
            <div class="snapshot-meta">
              <span class="camera"><el-icon><Camera /></el-icon> {{ snapshot.cameraName }}</span>
              <span class="time"><el-icon><Clock /></el-icon> {{ snapshot.time }}</span>
            </div>
            <div class="snapshot-annotation" v-if="snapshot.annotation">
              <el-icon><Edit /></el-icon>
              <span>{{ snapshot.annotation }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper" v-if="filteredSnapshots.length > 0">
        <button
            class="page-btn"
            @click="currentPage--"
            :disabled="currentPage === 1"
        >
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }}</span>
        <button
            class="page-btn"
            @click="currentPage++"
            :disabled="currentPage === totalPages"
        >
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
    </div>

    <!-- Snapshot Detail Modal -->
    <div v-if="viewDialogVisible" class="modal-overlay" @click.self="viewDialogVisible = false">
      <div class="modal-content large">
        <div class="modal-header">
          <h3>Snapshot Details</h3>
          <button class="modal-close" @click="viewDialogVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="detail-image">
            <img :src="viewingSnapshot?.imageUrl" :alt="viewingSnapshot?.title" />
          </div>
          <div class="detail-info">
            <div class="info-row">
              <span class="info-label">Title:</span>
              <span class="info-value">{{ viewingSnapshot?.title }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Camera:</span>
              <span class="info-value">{{ viewingSnapshot?.cameraName }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Time:</span>
              <span class="info-value">{{ viewingSnapshot?.time }}</span>
            </div>
            <div class="info-row" v-if="viewingSnapshot?.annotation">
              <span class="info-label">Annotation:</span>
              <span class="info-value">{{ viewingSnapshot?.annotation }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="viewDialogVisible = false">Close</button>
          <button class="dialog-btn confirm" @click="downloadSnapshot(viewingSnapshot!)">Download</button>
        </div>
      </div>
    </div>

    <!-- Capture Success Dialog -->
    <div v-if="captureSuccessVisible" class="modal-overlay" @click.self="captureSuccessVisible = false">
      <div class="modal-content success">
        <div class="modal-header">
          <h3>Snapshot Captured!</h3>
          <button class="modal-close" @click="captureSuccessVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="success-icon">
            <el-icon><CircleCheckFilled /></el-icon>
          </div>
          <p>Snapshot has been successfully captured and saved to gallery.</p>
          <div class="success-preview">
            <img :src="lastCapturedImage" alt="Captured" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="captureSuccessVisible = false">Continue</button>
          <button class="dialog-btn confirm" @click="viewLastSnapshot">View in Gallery</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  Refresh, Download, VideoCamera, Camera, Picture, ZoomIn, Delete,
  Clock, Edit, ArrowLeft, ArrowRight, CircleCheckFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing camera...', 'Loading snapshot gallery...', 'Almost ready...']

// Video URL
const VIDEO_URL = 'https://aegisnx.com/wp-content/uploads/2025/12/firlvideo.mp4'

// Data Models
interface Camera {
  id: number
  name: string
  location: string
}

interface Snapshot {
  id: number
  title: string
  cameraId: number
  cameraName: string
  time: string
  imageUrl: string
  annotation: string
}

// State
const selectedCamera = ref(1)
const previewVideoRef = ref<HTMLVideoElement | null>(null)
const currentTime = ref('')
const searchText = ref('')
const cameraFilter = ref('all')
const dateFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(12)
const viewDialogVisible = ref(false)
const captureSuccessVisible = ref(false)
const viewingSnapshot = ref<Snapshot | null>(null)
const lastCapturedImage = ref('')
const videoError = ref(false)

const captureSettings = ref({
  addTimestamp: true,
  addAnnotation: false,
  annotation: ''
})

// Mock Data - Cameras
const cameras = ref<Camera[]>([
  { id: 1, name: 'Main Entrance', location: 'Building A - Ground Floor' },
  { id: 2, name: 'North Wing', location: 'Building A - Floor 1' },
  { id: 3, name: 'South Wing', location: 'Building A - Floor 1' },
  { id: 4, name: 'Executive Corridor', location: 'Building A - Floor 2' },
  { id: 5, name: 'Server Room', location: 'Data Center' },
  { id: 6, name: 'Parking Lot North', location: 'Exterior' },
  { id: 7, name: 'Parking Lot South', location: 'Exterior' },
  { id: 8, name: 'Cafeteria', location: 'Building B - Floor 1' },
  { id: 9, name: 'Security Office', location: 'Building B - Floor 1' },
  { id: 10, name: 'Loading Dock', location: 'Building B - Ground Floor' }
])

// Mock Snapshots
const snapshots = ref<Snapshot[]>([
  { id: 1, title: 'Main Entrance - Morning', cameraId: 1, cameraName: 'Main Entrance', time: '2025-05-29 08:30:22', imageUrl: 'https://picsum.photos/id/20/400/300', annotation: 'Morning rush hour' },
  { id: 2, title: 'Server Room Check', cameraId: 5, cameraName: 'Server Room', time: '2025-05-29 10:15:45', imageUrl: 'https://picsum.photos/id/26/400/300', annotation: 'Temperature normal' },
  { id: 3, title: 'Parking Lot - Midday', cameraId: 6, cameraName: 'Parking Lot North', time: '2025-05-28 12:00:00', imageUrl: 'https://picsum.photos/id/29/400/300', annotation: '75% occupancy' },
  { id: 4, title: 'Executive Corridor', cameraId: 4, cameraName: 'Executive Corridor', time: '2025-05-28 09:45:30', imageUrl: 'https://picsum.photos/id/30/400/300', annotation: '' },
  { id: 5, title: 'Cafeteria - Lunch', cameraId: 8, cameraName: 'Cafeteria', time: '2025-05-27 12:30:15', imageUrl: 'https://picsum.photos/id/31/400/300', annotation: 'Peak hour' },
  { id: 6, title: 'North Wing Evening', cameraId: 2, cameraName: 'North Wing', time: '2025-05-27 18:00:00', imageUrl: 'https://picsum.photos/id/32/400/300', annotation: '' },
  { id: 7, title: 'Security Office', cameraId: 9, cameraName: 'Security Office', time: '2025-05-26 14:20:10', imageUrl: 'https://picsum.photos/id/33/400/300', annotation: 'Shift change' },
  { id: 8, title: 'South Wing', cameraId: 3, cameraName: 'South Wing', time: '2025-05-26 11:00:00', imageUrl: 'https://picsum.photos/id/34/400/300', annotation: '' },
  { id: 9, title: 'Data Center - Night', cameraId: 5, cameraName: 'Server Room', time: '2025-05-25 22:00:00', imageUrl: 'https://picsum.photos/id/35/400/300', annotation: 'All systems normal' },
  { id: 10, title: 'Loading Dock', cameraId: 10, cameraName: 'Loading Dock', time: '2025-05-25 15:30:00', imageUrl: 'https://picsum.photos/id/36/400/300', annotation: 'Delivery in progress' }
])

// Computed
const currentCameraName = computed(() => {
  const cam = cameras.value.find(c => c.id === selectedCamera.value)
  return cam ? `${cam.name} - ${cam.location}` : 'Select Camera'
})

const filteredSnapshots = computed(() => {
  let result = [...snapshots.value]

  if (cameraFilter.value !== 'all') {
    result = result.filter(s => s.cameraId === cameraFilter.value)
  }

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(s =>
        s.title.toLowerCase().includes(search) ||
        s.annotation.toLowerCase().includes(search)
    )
  }

  if (dateFilter.value !== 'all') {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()

    result = result.filter(s => {
      const snapshotDate = new Date(s.time).getTime()
      if (dateFilter.value === 'today') {
        return snapshotDate >= today
      } else if (dateFilter.value === 'week') {
        return snapshotDate >= today - 7 * 24 * 60 * 60 * 1000
      } else if (dateFilter.value === 'month') {
        return snapshotDate >= today - 30 * 24 * 60 * 60 * 1000
      }
      return true
    })
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredSnapshots.value.length / pageSize.value))
const paginatedSnapshots = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSnapshots.value.slice(start, end)
})

const hasActiveFilters = computed(() => {
  return cameraFilter.value !== 'all' || dateFilter.value !== 'all' || searchText.value !== ''
})

// Watch filters to reset page
watch([cameraFilter, dateFilter, searchText], () => {
  currentPage.value = 1
})

// Functions
const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString()
}

const captureSnapshot = () => {
  const video = previewVideoRef.value

  // 如果视频可用且有有效帧，使用视频截图
  if (video && video.videoWidth > 0 && !videoError.value) {
    try {
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')

      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

        // 添加时间戳
        if (captureSettings.value.addTimestamp) {
          ctx.font = '16px Arial'
          ctx.fillStyle = 'white'
          ctx.shadowColor = 'black'
          ctx.shadowBlur = 4
          const timestamp = new Date().toLocaleString()
          ctx.fillText(timestamp, 10, canvas.height - 10)
        }

        // 添加注释
        if (captureSettings.value.addAnnotation && captureSettings.value.annotation) {
          ctx.font = 'bold 14px Arial'
          ctx.fillStyle = '#3b82f6'
          ctx.shadowColor = 'black'
          ctx.shadowBlur = 4
          ctx.fillText(`📝 ${captureSettings.value.annotation}`, 10, 40)
        }

        const imageData = canvas.toDataURL('image/jpeg')
        saveSnapshot(imageData)
        return
      }
    } catch (e) {
      console.log('Video capture failed, using fallback')
    }
  }

  // 降级方案：生成模拟快照
  const canvas = document.createElement('canvas')
  canvas.width = 800
  canvas.height = 450
  const ctx = canvas.getContext('2d')

  if (ctx) {
    const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)
    grad.addColorStop(0, '#1a1a2e')
    grad.addColorStop(1, '#16213e')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    ctx.fillStyle = '#3b82f6'
    ctx.font = 'bold 60px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('📷', canvas.width / 2, canvas.height / 2 - 40)

    ctx.fillStyle = '#94a3b8'
    ctx.font = '18px Arial'
    ctx.fillText(currentCameraName.value, canvas.width / 2, canvas.height / 2 + 20)

    if (captureSettings.value.addTimestamp) {
      ctx.font = '14px Arial'
      ctx.fillStyle = '#cbd5e1'
      const timestamp = new Date().toLocaleString()
      ctx.fillText(timestamp, 20, canvas.height - 20)
    }

    if (captureSettings.value.addAnnotation && captureSettings.value.annotation) {
      ctx.font = 'bold 14px Arial'
      ctx.fillStyle = '#3b82f6'
      ctx.fillText(`📝 ${captureSettings.value.annotation}`, 20, 50)
    }

    ctx.strokeStyle = '#3b82f6'
    ctx.lineWidth = 3
    ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20)

    const imageData = canvas.toDataURL('image/jpeg')
    saveSnapshot(imageData)
  }
}

const saveSnapshot = (imageData: string) => {
  lastCapturedImage.value = imageData

  const cam = cameras.value.find(c => c.id === selectedCamera.value)
  const newSnapshot: Snapshot = {
    id: Date.now(),
    title: `${cam?.name || 'Camera'} - ${new Date().toLocaleTimeString()}`,
    cameraId: selectedCamera.value,
    cameraName: cam?.name || 'Unknown',
    time: new Date().toLocaleString(),
    imageUrl: imageData,
    annotation: captureSettings.value.addAnnotation ? captureSettings.value.annotation : ''
  }

  snapshots.value.unshift(newSnapshot)
  captureSuccessVisible.value = true

  captureSettings.value.annotation = ''
  captureSettings.value.addAnnotation = false

  ElMessage.success('Snapshot captured successfully')
}

const viewSnapshot = (snapshot: Snapshot) => {
  viewingSnapshot.value = snapshot
  viewDialogVisible.value = true
}

const downloadSnapshot = (snapshot: Snapshot) => {
  const link = document.createElement('a')
  link.download = `snapshot_${snapshot.id}.jpg`
  link.href = snapshot.imageUrl
  link.click()
  ElMessage.success(`Downloaded: ${snapshot.title}`)
}

const deleteSnapshot = (snapshot: Snapshot) => {
  const index = snapshots.value.findIndex(s => s.id === snapshot.id)
  if (index !== -1) {
    snapshots.value.splice(index, 1)
    ElMessage.success(`Deleted: ${snapshot.title}`)
  }
}

const exportAllSnapshots = () => {
  ElMessage.info('Exporting all snapshots as ZIP...')
}

const viewLastSnapshot = () => {
  captureSuccessVisible.value = false
  if (snapshots.value.length > 0) {
    viewSnapshot(snapshots.value[0])
  }
}

const refreshData = () => {
  if (previewVideoRef.value) {
    previewVideoRef.value.load()
    previewVideoRef.value.play().catch(e => console.log('Play error:', e))
  }
  ElMessage.success('Refreshed')
}

const clearFilters = () => {
  cameraFilter.value = 'all'
  dateFilter.value = 'all'
  searchText.value = ''
}

const handleVideoError = () => {
  videoError.value = true
  console.log('Video failed to load')
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

      // 确保视频播放
      nextTick(() => {
        if (previewVideoRef.value) {
          previewVideoRef.value.play().catch(e => {
            console.log('Auto-play prevented:', e)
          })
        }
      })
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style scoped>
/* Loading Screen - 保持不变 */
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
.snapshot-page {
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

/* Capture Section */
.capture-section {
  background: #1e293b;
  border-radius: 24px;
  padding: 20px;
  margin-bottom: 28px;
  border: 1px solid #334155;
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
.camera-selector {
  display: flex;
  gap: 12px;
}
.camera-select {
  padding: 8px 16px;
  border: 1px solid #334155;
  border-radius: 10px;
  background: #0f172a;
  color: white;
  font-size: 13px;
  cursor: pointer;
}
.preview-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}
.video-wrapper {
  flex: 2;
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
.preview-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
.live-time {
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
.capture-controls {
  flex: 1;
  background: #0f172a;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  justify-content: center;
}
.capture-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.capture-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}
.capture-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #cbd5e1;
  font-size: 13px;
  cursor: pointer;
}
.annotation-input {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: #1e293b;
  color: white;
  font-size: 13px;
  width: 100%;
}

/* Gallery Section */
.gallery-section {
  background: #1e293b;
  border-radius: 24px;
  padding: 20px;
  border: 1px solid #334155;
}
.header-right {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.filter-group {
  display: flex;
  gap: 8px;
}
.search-input {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 10px;
  background: #0f172a;
  color: white;
  width: 180px;
}
.search-input::placeholder {
  color: #64748b;
}
.filter-select {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 10px;
  background: #0f172a;
  color: white;
  cursor: pointer;
}
.clear-btn {
  padding: 8px 16px;
  background: #334155;
  border: none;
  border-radius: 10px;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
}
.clear-btn:hover {
  background: #475569;
}
.snapshot-count {
  background: #334155;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  color: #94a3b8;
}

/* Snapshots Grid */
.snapshots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 20px;
}
.snapshot-card {
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.2s;
}
.snapshot-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}
.snapshot-image {
  position: relative;
  aspect-ratio: 4 / 3;
  overflow: hidden;
}
.snapshot-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}
.snapshot-card:hover .snapshot-image img {
  transform: scale(1.05);
}
.snapshot-actions-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  opacity: 0;
  transition: opacity 0.2s;
}
.snapshot-card:hover .snapshot-actions-overlay {
  opacity: 1;
}
.action-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
  font-size: 18px;
}
.action-icon:hover {
  background: #3b82f6;
  transform: scale(1.1);
}
.action-icon.delete:hover {
  background: #ef4444;
}
.snapshot-info {
  padding: 12px;
}
.snapshot-title {
  font-weight: 600;
  color: white;
  margin-bottom: 6px;
  font-size: 14px;
}
.snapshot-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 6px;
}
.snapshot-meta .el-icon {
  margin-right: 2px;
  vertical-align: middle;
}
.snapshot-annotation {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  padding: 4px 8px;
  border-radius: 8px;
  margin-top: 6px;
}

/* Empty Gallery */
.empty-gallery {
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
.empty-gallery h4 {
  font-size: 18px;
  font-weight: 600;
  color: white;
  margin: 0 0 8px 0;
}
.empty-gallery p {
  font-size: 14px;
  color: #64748b;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #334155;
}
.page-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #334155;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled) {
  background: #3b82f6;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-info {
  color: #94a3b8;
  font-size: 14px;
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
  width: 600px;
  max-width: 90%;
  overflow: hidden;
  border: 1px solid #334155;
}
.modal-content.large {
  width: 700px;
}
.modal-content.success {
  width: 450px;
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
.detail-image {
  text-align: center;
  margin-bottom: 20px;
}
.detail-image img {
  max-width: 100%;
  border-radius: 12px;
}
.detail-info {
  background: #0f172a;
  border-radius: 12px;
  padding: 16px;
}
.info-row {
  display: flex;
  margin-bottom: 10px;
}
.info-label {
  width: 100px;
  color: #64748b;
  font-size: 13px;
}
.info-value {
  color: #cbd5e1;
  font-size: 13px;
  flex: 1;
}
.success-icon {
  text-align: center;
  font-size: 60px;
  color: #10b981;
  margin-bottom: 16px;
}
.success-preview {
  margin-top: 16px;
  text-align: center;
}
.success-preview img {
  max-width: 100%;
  border-radius: 12px;
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
</style>