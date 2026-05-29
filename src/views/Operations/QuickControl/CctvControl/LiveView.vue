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
        <div class="loading-tip">CCTV Live View</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Live View Page Content -->
  <div v-else class="live-view-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><VideoCamera /></el-icon>
          <span>CCTV Control</span>
        </div>
        <h1>Live View</h1>
        <p class="subtitle">Real-time surveillance camera feeds with PTZ control and playback capabilities</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          <span>Export</span>
        </button>
        <button class="action-btn" @click="openFullscreen">
          <el-icon><FullScreen /></el-icon>
          <span>Fullscreen</span>
        </button>
      </div>
    </div>

    <!-- Main Camera View -->
    <div class="main-camera-section">
      <div class="main-camera-container">
        <div class="camera-placeholder">
          <div class="camera-stream">
            <video
                v-if="currentCamera && currentCamera.status === 'online'"
                ref="mainVideoRef"
                :src="VIDEO_URL"
                autoplay
                muted
                loop
                playsinline
                class="camera-feed"
                @loadeddata="onVideoLoaded"
            ></video>
            <div v-else class="offline-placeholder">
              <el-icon><VideoCamera /></el-icon>
              <span>Camera Offline</span>
            </div>
            <div class="camera-overlay">
              <div class="camera-info">
                <span class="camera-name">{{ currentCamera?.name || 'Select Camera' }}</span>
                <span class="camera-time">{{ currentTime }}</span>
              </div>
              <div class="camera-controls">
                <button class="ctrl-btn" @click="takeSnapshot">
                  <el-icon><Camera /></el-icon>
                </button>
                <button class="ctrl-btn" @click="startRecording" v-if="!isRecording">
                  <el-icon><VideoCamera /></el-icon>
                </button>
                <button class="ctrl-btn recording" @click="stopRecording" v-else>
                  <el-icon><VideoPause /></el-icon>
                </button>
                <button class="ctrl-btn" @click="toggleAudio">
                  <el-icon><Microphone /></el-icon>
                </button>
              </div>
            </div>
          </div>
          <div class="recording-indicator" v-if="isRecording">
            <span class="recording-dot"></span>
            <span>RECORDING</span>
          </div>
          <div class="live-badge">
            <span class="live-dot"></span>
            <span>LIVE</span>
          </div>
        </div>
      </div>

      <!-- PTZ Controls -->
      <div class="ptz-controls">
        <div class="ptz-section">
          <div class="ptz-title">PTZ Control</div>
          <div class="ptz-pad">
            <div class="ptz-row">
              <button class="ptz-btn" @click="ptzMove('up')">
                <el-icon><ArrowUp /></el-icon>
              </button>
            </div>
            <div class="ptz-row">
              <button class="ptz-btn" @click="ptzMove('left')">
                <el-icon><ArrowLeft /></el-icon>
              </button>
              <button class="ptz-btn center" @click="ptzHome">
                <el-icon><HomeFilled /></el-icon>
              </button>
              <button class="ptz-btn" @click="ptzMove('right')">
                <el-icon><ArrowRight /></el-icon>
              </button>
            </div>
            <div class="ptz-row">
              <button class="ptz-btn" @click="ptzMove('down')">
                <el-icon><ArrowDown /></el-icon>
              </button>
            </div>
          </div>
          <div class="zoom-controls">
            <button class="zoom-btn" @click="ptzZoom('in')">
              <el-icon><ZoomIn /></el-icon>
              <span>Zoom In</span>
            </button>
            <button class="zoom-btn" @click="ptzZoom('out')">
              <el-icon><ZoomOut /></el-icon>
              <span>Zoom Out</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Camera Grid -->
    <div class="cameras-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><Camera /></el-icon></div>
          <h3>Available Cameras</h3>
          <span class="camera-count">{{ filteredCameras.length }} cameras</span>
        </div>
        <div class="header-right">
          <div class="filter-group">
            <input type="text" v-model="searchText" placeholder="Search cameras..." class="search-input" />
          </div>
          <select v-model="locationFilter" class="filter-select">
            <option value="all">All Locations</option>
            <option value="A">Building A</option>
            <option value="B">Building B</option>
            <option value="C">Building C</option>
            <option value="DC">Data Center</option>
            <option value="Exterior">Exterior</option>
          </select>
        </div>
      </div>
      <div class="cameras-grid">
        <div
            v-for="camera in filteredCameras"
            :key="camera.id"
            class="camera-card"
            :class="{ active: currentCamera?.id === camera.id }"
            @click="selectCamera(camera)"
        >
          <div class="camera-thumbnail">
            <video
                :data-src="VIDEO_URL"
                muted
                loop
                playsinline
                class="thumbnail-video"
                :autoplay="camera.status === 'online'"
                v-if="camera.status === 'online'"
                @mouseenter="playThumbnail"
                @mouseleave="pauseThumbnail"
            ></video>
            <div v-else class="offline-thumbnail">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="camera-status" :class="camera.status">
              <span class="status-dot"></span>
              <span>{{ camera.status === 'online' ? 'Live' : 'Offline' }}</span>
            </div>
          </div>
          <div class="camera-info">
            <div class="camera-name">{{ camera.name }}</div>
            <div class="camera-location">{{ camera.location }}</div>
          </div>
          <div class="camera-stats">
            <span><el-icon><Timer /></el-icon> {{ camera.bitrate }}</span>
            <span><el-icon><TrendCharts /></el-icon> {{ camera.fps }} fps</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Recordings -->
    <div class="recordings-section">
      <div class="section-header">
        <div class="header-left">
          <div class="header-icon"><el-icon><VideoCamera /></el-icon></div>
          <h3>Recent Recordings</h3>
        </div>
        <div class="header-right">
          <button class="view-all-btn">View All Recordings →</button>
        </div>
      </div>
      <div class="recordings-grid">
        <div v-for="rec in recentRecordings" :key="rec.id" class="recording-card">
          <div class="recording-thumbnail">
            <video :src="VIDEO_URL" muted class="thumbnail-video"></video>
            <div class="recording-duration">{{ rec.duration }}</div>
          </div>
          <div class="recording-info">
            <div class="recording-name">{{ rec.name }}</div>
            <div class="recording-time">{{ rec.time }}</div>
          </div>
          <div class="recording-actions">
            <button class="play-btn" @click="playRecording(rec)">
              <el-icon><VideoPlay /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Snapshot Dialog -->
    <div v-if="snapshotDialogVisible" class="modal-overlay" @click.self="snapshotDialogVisible = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Snapshot Captured</h3>
          <button class="modal-close" @click="snapshotDialogVisible = false">×</button>
        </div>
        <div class="modal-body">
          <div class="snapshot-preview">
            <img :src="snapshotImage" alt="Snapshot" />
          </div>
          <div class="snapshot-info">
            <p>Camera: <strong>{{ currentCamera?.name }}</strong></p>
            <p>Time: <strong>{{ snapshotTime }}</strong></p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="dialog-btn cancel" @click="snapshotDialogVisible = false">Close</button>
          <button class="dialog-btn confirm" @click="downloadSnapshot">Download</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  Refresh, Download, VideoCamera, FullScreen, Camera, VideoPause,
  Microphone, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, HomeFilled,
  ZoomIn, ZoomOut, Timer, TrendCharts, VideoPlay
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Connecting to cameras...', 'Loading video streams...', 'Almost ready...']

// Video URL
const VIDEO_URL = 'https://aegisnx.com/wp-content/uploads/2025/12/firlvideo.mp4'

// Data Models
interface Camera {
  id: number
  name: string
  location: string
  building: string
  status: 'online' | 'offline'
  bitrate: string
  fps: number
}

interface Recording {
  id: number
  name: string
  time: string
  duration: string
}

// State
const currentCamera = ref<Camera | null>(null)
const currentTime = ref('')
const isRecording = ref(false)
const searchText = ref('')
const locationFilter = ref('all')
const snapshotDialogVisible = ref(false)
const snapshotImage = ref('')
const snapshotTime = ref('')
const mainVideoRef = ref<HTMLVideoElement | null>(null)
let timeInterval: ReturnType<typeof setInterval> | null = null

// Mock Data - All cameras online
const cameras = ref<Camera[]>([
  { id: 1, name: 'Main Entrance', location: 'Building A - Ground Floor', building: 'A', status: 'online', bitrate: '2.5 Mbps', fps: 30 },
  { id: 2, name: 'North Wing', location: 'Building A - Floor 1', building: 'A', status: 'online', bitrate: '2.1 Mbps', fps: 25 },
  { id: 3, name: 'South Wing', location: 'Building A - Floor 1', building: 'A', status: 'online', bitrate: '2.3 Mbps', fps: 30 },
  { id: 4, name: 'Executive Corridor', location: 'Building A - Floor 2', building: 'A', status: 'online', bitrate: '1.8 Mbps', fps: 25 },
  { id: 5, name: 'Server Room', location: 'Data Center', building: 'DC', status: 'online', bitrate: '3.2 Mbps', fps: 30 },
  { id: 6, name: 'Loading Dock', location: 'Building B - Ground Floor', building: 'B', status: 'online', bitrate: '2.0 Mbps', fps: 25 },
  { id: 7, name: 'Parking Lot North', location: 'Exterior', building: 'Exterior', status: 'online', bitrate: '2.0 Mbps', fps: 20 },
  { id: 8, name: 'Parking Lot South', location: 'Exterior', building: 'Exterior', status: 'online', bitrate: '2.0 Mbps', fps: 20 },
  { id: 9, name: 'Cafeteria', location: 'Building B - Floor 1', building: 'B', status: 'online', bitrate: '1.5 Mbps', fps: 25 },
  { id: 10, name: 'Security Office', location: 'Building B - Floor 1', building: 'B', status: 'online', bitrate: '1.9 Mbps', fps: 25 }
])

const recentRecordings = ref<Recording[]>([
  { id: 1, name: 'Main Entrance - May 29, 2025', time: '10:30 AM', duration: '2:30' },
  { id: 2, name: 'North Wing - May 29, 2025', time: '09:45 AM', duration: '5:15' },
  { id: 3, name: 'Server Room - May 28, 2025', time: '16:20 PM', duration: '3:45' },
  { id: 4, name: 'Parking Lot - May 28, 2025', time: '08:00 AM', duration: '8:00' }
])

// Computed
const filteredCameras = computed(() => {
  let result = [...cameras.value]
  if (locationFilter.value !== 'all') {
    result = result.filter(c => c.building === locationFilter.value)
  }
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(c =>
        c.name.toLowerCase().includes(search) ||
        c.location.toLowerCase().includes(search)
    )
  }
  return result
})

// Functions
const initThumbnailVideos = () => {
  nextTick(() => {
    const thumbnails = document.querySelectorAll('.thumbnail-video')
    thumbnails.forEach((video: HTMLVideoElement) => {
      if (video && !video.src) {
        video.src = VIDEO_URL
        video.load()
        // 只在鼠标悬停时播放，节省资源
      }
    })
  })
}

const playThumbnail = (event: MouseEvent) => {
  const video = event.currentTarget as HTMLVideoElement
  if (video) {
    video.play().catch(e => console.log('Auto-play prevented:', e))
  }
}

const pauseThumbnail = (event: MouseEvent) => {
  const video = event.currentTarget as HTMLVideoElement
  if (video) {
    video.pause()
  }
}

const selectCamera = (camera: Camera) => {
  currentCamera.value = camera
  ElMessage.success(`Switched to ${camera.name}`)
  // 重新加载主视频以确保播放
  nextTick(() => {
    if (mainVideoRef.value) {
      mainVideoRef.value.load()
      mainVideoRef.value.play().catch(e => console.log('Play error:', e))
    }
  })
}

const onVideoLoaded = () => {
  console.log('Video loaded and playing')
}

const updateCurrentTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString()
}

const takeSnapshot = () => {
  if (!currentCamera.value || !mainVideoRef.value) {
    ElMessage.warning('No camera selected')
    return
  }
  // 从视频中截取当前帧
  const canvas = document.createElement('canvas')
  canvas.width = mainVideoRef.value.videoWidth
  canvas.height = mainVideoRef.value.videoHeight
  const ctx = canvas.getContext('2d')
  if (ctx && mainVideoRef.value) {
    ctx.drawImage(mainVideoRef.value, 0, 0, canvas.width, canvas.height)
    snapshotImage.value = canvas.toDataURL('image/jpeg')
    snapshotTime.value = new Date().toLocaleString()
    snapshotDialogVisible.value = true
    ElMessage.success('Snapshot captured')
  } else {
    ElMessage.warning('Cannot capture snapshot')
  }
}

const downloadSnapshot = () => {
  const link = document.createElement('a')
  link.download = `snapshot_${Date.now()}.jpg`
  link.href = snapshotImage.value
  link.click()
  ElMessage.success('Snapshot downloaded')
  snapshotDialogVisible.value = false
}

const startRecording = () => {
  if (!currentCamera.value) {
    ElMessage.warning('No camera selected')
    return
  }
  isRecording.value = true
  ElMessage.success(`Recording started - ${currentCamera.value.name}`)

  // 模拟5秒后自动停止
  setTimeout(() => {
    if (isRecording.value) {
      isRecording.value = false
      ElMessage.success('Recording stopped and saved')
    }
  }, 10000)
}

const stopRecording = () => {
  isRecording.value = false
  ElMessage.success('Recording stopped and saved')
}

const toggleAudio = () => {
  if (mainVideoRef.value) {
    mainVideoRef.value.muted = !mainVideoRef.value.muted
    ElMessage.info(mainVideoRef.value.muted ? 'Audio muted' : 'Audio enabled')
  }
}

const ptzMove = (direction: string) => {
  if (!currentCamera.value) {
    ElMessage.warning('No camera selected')
    return
  }
  ElMessage.info(`PTZ ${direction} - ${currentCamera.value.name}`)
}

const ptzHome = () => {
  if (!currentCamera.value) {
    ElMessage.warning('No camera selected')
    return
  }
  ElMessage.info(`PTZ Home - ${currentCamera.value.name}`)
}

const ptzZoom = (action: string) => {
  if (!currentCamera.value) {
    ElMessage.warning('No camera selected')
    return
  }
  ElMessage.info(`Zoom ${action} - ${currentCamera.value.name}`)
}

const openFullscreen = () => {
  const elem = document.querySelector('.main-camera-container')
  if (elem?.requestFullscreen) {
    elem.requestFullscreen()
  }
}

const playRecording = (rec: Recording) => {
  // 创建临时视频元素播放
  const video = document.createElement('video')
  video.src = VIDEO_URL
  video.controls = true
  video.autoplay = true
  video.className = 'floating-video'
  document.body.appendChild(video)

  // 点击关闭
  video.onclick = () => {
    video.pause()
    video.remove()
  }

  ElMessage.info(`Playing recording: ${rec.name} - Click video to close`)
}

const refreshData = () => {
  // 重新加载主视频
  if (mainVideoRef.value) {
    mainVideoRef.value.load()
    mainVideoRef.value.play().catch(e => console.log('Play error:', e))
  }
  ElMessage.success('Camera feeds refreshed')
}

const exportReport = () => {
  ElMessage.info('Exporting camera report...')
}

// Watch for current camera changes
watch(currentCamera, () => {
  nextTick(() => {
    if (mainVideoRef.value) {
      mainVideoRef.value.load()
      mainVideoRef.value.play().catch(e => console.log('Play error:', e))
    }
  })
})

// Lifecycle
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
      if (onlineCam) currentCamera.value = onlineCam
      setTimeout(() => {
        initThumbnailVideos()
      }, 500)
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
.live-view-page {
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
  background: linear-gradient(135deg, #ef4444, #dc2626);
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

/* Main Camera Section */
.main-camera-section {
  display: flex;
  gap: 20px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}
.main-camera-container {
  flex: 3;
  position: relative;
}
.camera-placeholder {
  background: #0f172a;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #334155;
  position: relative;
}
.camera-stream {
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  background: #0f172a;
}
.camera-feed {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.offline-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: #0f172a;
  color: #64748b;
  font-size: 16px;
}
.offline-placeholder .el-icon {
  font-size: 48px;
}
.camera-overlay {
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
.camera-time {
  color: #94a3b8;
  font-size: 11px;
}
.camera-controls {
  display: flex;
  gap: 10px;
}
.ctrl-btn {
  background: rgba(0, 0, 0, 0.6);
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
}
.ctrl-btn:hover {
  background: #3b82f6;
}
.ctrl-btn.recording {
  background: #ef4444;
  animation: pulse 1s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.recording-indicator {
  position: absolute;
  top: 16px;
  left: 16px;
  background: #ef4444;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}
.live-badge {
  position: absolute;
  top: 16px;
  right: 16px;
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
.recording-dot {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: pulse 1s infinite;
}

/* PTZ Controls */
.ptz-controls {
  flex: 1;
  background: #1e293b;
  border-radius: 20px;
  padding: 20px;
  border: 1px solid #334155;
}
.ptz-section {
  text-align: center;
}
.ptz-title {
  color: white;
  font-weight: 600;
  margin-bottom: 20px;
  font-size: 14px;
}
.ptz-pad {
  display: inline-block;
  background: #0f172a;
  padding: 16px;
  border-radius: 20px;
  margin-bottom: 20px;
}
.ptz-row {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin: 8px 0;
}
.ptz-btn {
  width: 48px;
  height: 48px;
  background: #334155;
  border: none;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
  font-size: 20px;
}
.ptz-btn:hover {
  background: #3b82f6;
}
.ptz-btn.center {
  background: #3b82f6;
}
.ptz-btn.center:hover {
  background: #2563eb;
}
.zoom-controls {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}
.zoom-btn {
  flex: 1;
  padding: 10px;
  background: #334155;
  border: none;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
  font-size: 14px;
}
.zoom-btn:hover {
  background: #3b82f6;
}

/* Cameras Section */
.cameras-section, .recordings-section {
  background: #1e293b;
  border-radius: 20px;
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
.camera-count {
  background: #334155;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  color: #94a3b8;
}
.header-right {
  display: flex;
  gap: 12px;
}
.search-input {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 10px;
  font-size: 13px;
  background: #0f172a;
  color: white;
  width: 200px;
}
.search-input::placeholder {
  color: #64748b;
}
.filter-select {
  padding: 8px 12px;
  border: 1px solid #334155;
  border-radius: 10px;
  font-size: 13px;
  background: #0f172a;
  color: white;
}

/* Cameras Grid */
.cameras-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.camera-card {
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}
.camera-card:hover {
  transform: translateY(-2px);
  border-color: #3b82f6;
}
.camera-card.active {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
}
.camera-thumbnail {
  position: relative;
  padding-bottom: 56.25%;
  background: #0f172a;
}
.thumbnail-video, .thumbnail-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.offline-thumbnail {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  color: #64748b;
  font-size: 32px;
}
.camera-status {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 600;
}
.camera-status.online {
  background: #10b981;
  color: white;
}
.camera-status.offline {
  background: #64748b;
  color: white;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: white;
}
.camera-info {
  padding: 12px;
}
.camera-name {
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}
.camera-location {
  font-size: 11px;
  color: #94a3b8;
}
.camera-stats {
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  border-top: 1px solid #334155;
  font-size: 11px;
  color: #64748b;
}
.camera-stats .el-icon {
  margin-right: 4px;
  vertical-align: middle;
}

/* Recordings Grid */
.recordings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.recording-card {
  background: #0f172a;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.recording-thumbnail {
  position: relative;
  padding-bottom: 60%;
  background: #0f172a;
}
.recording-thumbnail .thumbnail-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.recording-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  color: white;
}
.recording-info {
  padding: 12px;
}
.recording-name {
  font-weight: 500;
  color: white;
  font-size: 13px;
  margin-bottom: 4px;
}
.recording-time {
  font-size: 11px;
  color: #64748b;
}
.recording-actions {
  padding: 8px 12px;
  border-top: 1px solid #334155;
}
.play-btn {
  width: 100%;
  padding: 8px;
  background: #3b82f6;
  border: none;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
}
.play-btn:hover {
  background: #2563eb;
}

.view-all-btn {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
}
.view-all-btn:hover {
  background: rgba(59, 130, 246, 0.1);
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
  width: 500px;
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
.modal-body { padding: 24px; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #334155;
}
.snapshot-preview {
  text-align: center;
  margin-bottom: 16px;
}
.snapshot-preview img {
  max-width: 100%;
  border-radius: 12px;
}
.snapshot-info {
  text-align: center;
  color: #cbd5e1;
  font-size: 13px;
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
.dialog-btn.cancel:hover { background: #475569; }
.dialog-btn.confirm {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}
.dialog-btn.confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

/* Floating video for playback */
.floating-video {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  max-width: 800px;
  z-index: 2000;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  cursor: pointer;
}
</style>