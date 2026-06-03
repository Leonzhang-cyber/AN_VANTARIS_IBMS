<template>
  <div v-if="isPageLoaded" class="cctv-page">
    <div class="main-view">
      <div class="three-columns">
        <!-- Left Column: Camera Tree + Device Status -->
        <div class="col-left">
          <!-- Camera Groups / Tree -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <div class="header-left">
                <el-icon><VideoCamera /></el-icon>
                <span>Camera Groups</span>
              </div>
              <div class="header-right">
                <el-badge :value="totalCameras" :hidden="totalCameras === 0" class="header-badge">
                  <el-button size="small" type="primary" link class="add-camera-btn" @click="showAddCameraDialog">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                </el-badge>
              </div>
            </div>
            <div class="camera-tree">
              <div v-for="group in cameraGroups" :key="group.id" class="camera-group">
                <div class="group-header" @click="toggleGroup(group.id)">
                  <el-icon><Folder /></el-icon>
                  <span>{{ group.name }}</span>
                  <span class="group-count">{{ group.cameras.length }}</span>
                  <el-icon class="group-arrow"><ArrowDown v-if="group.expanded" /><ArrowRight v-else /></el-icon>
                </div>
                <div v-show="group.expanded" class="camera-list">
                  <div v-for="cam in group.cameras" :key="cam.id"
                       class="camera-item"
                       :class="{ active: currentCamera?.id === cam.id }"
                       @click="selectCamera(cam)">
                    <div class="cam-status" :class="cam.status"></div>
                    <div class="cam-info">
                      <span class="cam-name">{{ cam.name }}</span>
                      <span class="cam-location-sm">{{ cam.location }}</span>
                    </div>
                    <div class="cam-badges">
                      <el-tag v-if="cam.hasMotion" size="small" type="danger" effect="dark" class="motion-tag">Motion</el-tag>
                      <el-tag v-if="cam.recording" size="small" type="success" effect="dark" class="rec-tag">REC</el-tag>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Device Health Monitor -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>Device Health</span>
            </div>
            <div class="device-health">
              <div class="health-metrics">
                <div class="health-metric">
                  <div class="metric-icon online">🟢</div>
                  <div class="metric-info">
                    <span class="metric-label">Online</span>
                    <strong class="metric-value">{{ onlineCameras }}</strong>
                  </div>
                </div>
                <div class="health-metric">
                  <div class="metric-icon offline">🔴</div>
                  <div class="metric-info">
                    <span class="metric-label">Offline</span>
                    <strong class="metric-value">{{ offlineCameras }}</strong>
                  </div>
                </div>
                <div class="health-metric">
                  <div class="metric-icon recording">🔵</div>
                  <div class="metric-info">
                    <span class="metric-label">Recording</span>
                    <strong class="metric-value">{{ recordingCameras }}</strong>
                  </div>
                </div>
              </div>
              <div class="bandwidth-usage">
                <div class="bandwidth-header">
                  <span>Bandwidth Usage</span>
                  <strong>{{ bandwidthUsage.toFixed(1) }} Mbps</strong>
                </div>
                <el-progress :percentage="bandwidthPercent" :stroke-width="6" :color="bandwidthColor" />
              </div>
            </div>
          </el-card>

          <!-- PTZ Presets -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><Position /></el-icon>
              <span>PTZ Presets</span>
              <el-button size="small" text @click="showManagePresets">Manage</el-button>
            </div>
            <div class="presets-grid">
              <div v-for="preset in ptzPresets" :key="preset.id"
                   class="preset-item"
                   @click="gotoPreset(preset)">
                <div class="preset-thumb">
                  <div class="preset-overlay">
                    <span class="preset-icon">{{ preset.icon }}</span>
                  </div>
                </div>
                <div class="preset-info">
                  <span class="preset-name">{{ preset.name }}</span>
                  <el-button size="small" text class="preset-set-btn" @click.stop="setPreset(preset)">Set</el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Storage Status -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><Timer /></el-icon>
              <span>Storage Status</span>
            </div>
            <div class="recording-stats">
              <div class="stat-row">
                <span>Today's Recordings</span>
                <strong>{{ todayRecordings }}</strong>
              </div>
              <div class="stat-row">
                <span>Storage Used</span>
                <strong>{{ storageUsed.toFixed(1) }} / {{ storageTotal }} TB</strong>
                <el-progress :percentage="storagePercent" :stroke-width="6" :show-text="false" :color="storageColor" />
              </div>
              <div class="stat-row">
                <span>Retention Period</span>
                <strong>{{ retentionDays }} days</strong>
              </div>
              <div class="stat-row">
                <span>Estimated Remaining</span>
                <strong>{{ remainingDays }} days</strong>
              </div>
            </div>
          </el-card>

          <!-- System Performance Metrics -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>System Performance</span>
            </div>
            <div class="performance-metrics">
              <div class="perf-row">
                <span>CPU Usage</span>
                <el-progress :percentage="cpuUsage" :stroke-width="6" :color="cpuColor" />
                <strong>{{ cpuUsage }}%</strong>
              </div>
              <div class="perf-row">
                <span>Memory Usage</span>
                <el-progress :percentage="memoryUsage" :stroke-width="6" :color="memoryColor" />
                <strong>{{ memoryUsage }}%</strong>
              </div>
              <div class="perf-row">
                <span>Network Latency</span>
                <el-progress :percentage="latencyPercent" :stroke-width="6" :color="latencyColor" />
                <strong>{{ networkLatency }} ms</strong>
              </div>
              <div class="perf-row">
                <span>Packet Loss</span>
                <el-progress :percentage="packetLoss" :stroke-width="6" :color="packetColor" />
                <strong>{{ packetLoss }}%</strong>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Center Column: Main Video Player + PTZ Controls -->
        <div class="col-center">
          <div class="title-row" v-if="!isMobile">
            <h1 class="page-title">CCTV Surveillance</h1>
            <span class="live-time" v-if="isFullscreen">{{ currentTime }}</span>
          </div>
          <div class="title-row" v-if="isMobile">
            <h1 class="page-title">CCTV</h1>
            <span class="live-time">{{ currentTime }}</span>
          </div>

          <!-- Main Video Player -->
          <div class="video-player-card">
            <div v-if="!currentCamera" class="no-camera-placeholder">
              <el-icon :size="64"><VideoCamera /></el-icon>
              <p>Select a camera to view</p>
            </div>
            <div v-else class="video-wrapper">
              <video
                  ref="videoPlayer"
                  class="video-stream"
                  :src="currentCamera.streamUrl"
                  autoplay
                  muted
                  loop
                  playsinline
                  @loadeddata="onVideoLoaded"
                  @error="onVideoError"
              ></video>
              <div class="video-info-overlay">
                <div class="video-info-left">
                  <span class="cam-name">{{ currentCamera.name }}</span>
                  <span class="cam-location">{{ currentCamera.location }}</span>
                </div>
                <div class="video-info-right">
                  <span class="live-badge">LIVE</span>
                  <span class="resolution-badge">{{ currentResolution }}</span>
                  <span class="fps-badge">{{ currentFPS }} fps</span>
                </div>
              </div>
            </div>
          </div>

          <!-- PTZ Control Panel -->
          <el-card class="card glass-card modern-ptz-card" shadow="hover" v-if="currentCamera?.ptz">
            <div class="ptz-tabs">
              <div class="ptz-tab" :class="{ active: activePtzTab === 'control' }" @click="activePtzTab = 'control'">
                <el-icon><Operation /></el-icon>
                <span>Control</span>
              </div>
              <div class="ptz-tab" :class="{ active: activePtzTab === 'presets' }" @click="activePtzTab = 'presets'">
                <el-icon><Star /></el-icon>
                <span>Presets</span>
              </div>
              <div class="ptz-tab" :class="{ active: activePtzTab === 'advanced' }" @click="activePtzTab = 'advanced'">
                <el-icon><Setting /></el-icon>
                <span>Advanced</span>
              </div>
            </div>

            <div v-show="activePtzTab === 'control'" class="ptz-control-content">
              <div class="zoom-focus-section">
                <div class="control-card">
                  <div class="control-header">
                    <el-icon><ZoomIn /></el-icon>
                    <span>Zoom</span>
                  </div>
                  <div class="control-value">{{ zoomLevel.toFixed(1) }}x</div>
                  <div class="control-buttons">
                    <el-button circle size="small" :icon="ZoomIn" @click="ptzZoom('in')" />
                    <el-button circle size="small" :icon="ZoomOut" @click="ptzZoom('out')" />
                  </div>
                </div>
                <div class="control-card">
                  <div class="control-header">
                    <el-icon><Refresh /></el-icon>
                    <span>Focus</span>
                  </div>
                  <div class="control-value">{{ focusLevel.toFixed(1) }}%</div>
                  <div class="control-buttons">
                    <el-button size="small" @click="ptzFocusNear">Near</el-button>
                    <el-button size="small" @click="ptzFocusFar">Far</el-button>
                    <el-button size="small" type="primary" @click="ptzAutoFocus">Auto</el-button>
                  </div>
                </div>
                <div class="control-card">
                  <div class="control-header">
                    <el-icon><Sunny /></el-icon>
                    <span>Iris</span>
                  </div>
                  <div class="control-value">{{ irisLevel.toFixed(1) }}%</div>
                  <div class="control-buttons">
                    <el-button size="small" @click="ptzIrisOpen">Open</el-button>
                    <el-button size="small" @click="ptzIrisClose">Close</el-button>
                    <el-button size="small" type="primary" @click="ptzIrisAuto">Auto</el-button>
                  </div>
                </div>
              </div>

              <div class="speed-section">
                <div class="section-label">Pan/Tilt Speed</div>
                <div class="speed-control-modern">
                  <span class="speed-value">{{ ptzSpeed.toFixed(0) }}%</span>
                  <el-slider v-model="ptzSpeed" :min="1" :max="100" @change="ptzSpeedChange" />
                  <div class="speed-buttons">
                    <el-button size="small" @click="ptzSpeed = 25">Slow</el-button>
                    <el-button size="small" @click="ptzSpeed = 50">Normal</el-button>
                    <el-button size="small" @click="ptzSpeed = 75">Fast</el-button>
                  </div>
                </div>
              </div>

              <div class="aux-section">
                <div class="section-label">Aux Functions</div>
                <div class="aux-grid">
                  <button class="aux-btn" @click="ptzAux('wiper')">
                    <el-icon><WindPower /></el-icon>
                    <span>Wiper</span>
                  </button>
                  <button class="aux-btn" @click="ptzAux('light')">
                    <el-icon><Sunny /></el-icon>
                    <span>Light</span>
                  </button>
                  <button class="aux-btn" @click="ptzAux('alarm')">
                    <el-icon><Bell /></el-icon>
                    <span>Alarm</span>
                  </button>
                  <button class="aux-btn" @click="ptzAux('heater')">
                    <el-icon><HotWater /></el-icon>
                    <span>Heater</span>
                  </button>
                </div>
              </div>

              <div class="action-buttons">
                <el-button :icon="FullScreen" @click="toggleFullVideo">Fullscreen</el-button>
                <el-button :icon="Refresh" @click="ptzHome">Home</el-button>
                <el-button :icon="Refresh" @click="ptzReset">Reset</el-button>
                <el-button :icon="VideoCamera" @click="ptzStartCruise">Cruise</el-button>
                <el-button :icon="Position" @click="ptzPatrol">Patrol</el-button>
              </div>
            </div>

            <div v-show="activePtzTab === 'presets'" class="ptz-presets-content">
              <div class="presets-header">
                <span>Saved Presets</span>
                <el-button size="small" type="primary" @click="addNewPreset">+ Add Preset</el-button>
              </div>
              <div class="presets-list">
                <div v-for="preset in ptzPresets" :key="preset.id" class="preset-card" @click="gotoPreset(preset)">
                  <div class="preset-card-thumb">
                    <div class="preset-card-icon">{{ preset.icon }}</div>
                  </div>
                  <div class="preset-card-info">
                    <div class="preset-card-name">{{ preset.name }}</div>
                    <div class="preset-card-details">Zoom: {{ preset.zoom.toFixed(1) }}x</div>
                  </div>
                  <el-button size="small" text class="preset-card-delete" @click.stop="deletePreset(preset.id)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="patrol-settings">
                <div class="section-label">Auto Patrol</div>
                <div class="patrol-controls">
                  <el-select v-model="selectedPatrolPresets" multiple placeholder="Select presets" size="small">
                    <el-option v-for="p in ptzPresets" :key="p.id" :label="p.name" :value="p.id" />
                  </el-select>
                  <el-button type="primary" size="small" @click="startPatrol">Start</el-button>
                  <el-button size="small" @click="stopPatrol">Stop</el-button>
                </div>
              </div>
            </div>

            <div v-show="activePtzTab === 'advanced'" class="ptz-advanced-content">
              <div class="advanced-grid">
                <div class="advanced-item">
                  <div class="advanced-label">Motion Sensitivity</div>
                  <el-slider v-model="motionSensitivity" :min="0" :max="100" />
                  <span class="advanced-value">{{ motionSensitivity.toFixed(0) }}%</span>
                </div>
                <div class="advanced-item">
                  <div class="advanced-label">Privacy Masking</div>
                  <el-switch v-model="privacyMasking" />
                  <el-button size="small" v-if="privacyMasking" @click="configurePrivacyMask">Configure</el-button>
                </div>
                <div class="advanced-item">
                  <div class="advanced-label">PTZ Limit Stops</div>
                  <el-button size="small" @click="configureLimits">Set Limits</el-button>
                  <el-button size="small" @click="clearLimits">Clear</el-button>
                </div>
                <div class="advanced-item">
                  <div class="advanced-label">Image Settings</div>
                  <div class="image-settings">
                    <div>Brightness: <el-slider v-model="brightness" :min="0" :max="100" style="width: 120px" /></div>
                    <div>Contrast: <el-slider v-model="contrast" :min="0" :max="100" style="width: 120px" /></div>
                    <div>Saturation: <el-slider v-model="saturation" :min="0" :max="100" style="width: 120px" /></div>
                  </div>
                </div>
              </div>
            </div>
          </el-card>

          <!-- Simple control bar for non-PTZ cameras -->
          <el-card class="card glass-card simple-control-card" shadow="hover" v-if="currentCamera && !currentCamera?.ptz">
            <div class="simple-controls">
              <el-button :icon="FullScreen" @click="toggleFullVideo">Fullscreen</el-button>
              <el-button :icon="Refresh" @click="refreshStream">Refresh</el-button>
              <el-button :icon="VideoPlay" @click="toggleRecording">Record</el-button>
              <el-button :icon="Camera" @click="takeSnapshot">Snapshot</el-button>
            </div>
          </el-card>
        </div>

        <!-- Right Column -->
        <div class="col-right">
          <!-- Real-time Alerts -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><BellFilled /></el-icon>
              <span>Real-time Alerts</span>
              <el-badge :value="unreadEvents" :hidden="unreadEvents === 0" class="event-badge" />
            </div>
            <div class="alert-list">
              <div v-for="event in alarmEvents.slice(0, 5)" :key="event.id"
                   class="alert-item"
                   :class="event.severity"
                   @click="playbackByEvent(event)">
                <div class="alert-icon">
                  <el-icon v-if="event.type === 'motion'"><View /></el-icon>
                  <el-icon v-else-if="event.type === 'smoking'"><WarningFilled /></el-icon>
                  <el-icon v-else-if="event.type === 'fire'"><WarningFilled /></el-icon>
                  <el-icon v-else><Bell /></el-icon>
                </div>
                <div class="alert-content">
                  <div class="alert-title">{{ event.title }}</div>
                  <div class="alert-meta">
                    <span class="alert-camera">{{ event.camera }}</span>
                    <span class="alert-time">{{ event.time }}</span>
                  </div>
                </div>
                <el-button size="small" text class="alert-action" @click.stop="playbackByEvent(event)">View</el-button>
              </div>
            </div>
          </el-card>

          <!-- AI Detection Feed -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><Cpu /></el-icon>
              <span>AI Detection</span>
              <el-tag size="small" type="warning" effect="dark">Live</el-tag>
            </div>
            <div class="detection-feed">
              <div v-for="detection in aiDetections" :key="detection.id" class="detection-feed-item">
                <div class="detection-feed-icon" :class="detection.type">
                  <span v-if="detection.type === 'fire'">🔥</span>
                  <span v-else-if="detection.type === 'smoking'">🚬</span>
                  <span v-else-if="detection.type === 'person'">👤</span>
                  <span v-else>🚶</span>
                </div>
                <div class="detection-feed-info">
                  <div class="detection-feed-type">{{ detection.typeLabel }}</div>
                  <div class="detection-feed-confidence">Confidence: {{ detection.confidence.toFixed(1) }}%</div>
                </div>
                <div class="detection-feed-time">{{ detection.time }}</div>
              </div>
            </div>
          </el-card>

          <!-- Playback Timeline -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><VideoPlay /></el-icon>
              <span>Playback</span>
              <el-button size="small" text @click="openFullPlayback">Timeline</el-button>
            </div>
            <div class="playback-controls">
              <div class="date-selector">
                <el-date-picker
                    v-model="playbackDate"
                    type="date"
                    placeholder="Select date"
                    size="small"
                    :clearable="false"
                    @change="loadPlaybackTimeline"
                />
              </div>
              <div class="timeline-slider">
                <el-slider
                    v-model="playbackTime"
                    :min="0"
                    :max="86400"
                    :format-tooltip="formatPlaybackTime"
                    @change="seekPlayback"
                />
              </div>
              <div class="playback-buttons">
                <el-button :icon="VideoPlay" size="small" @click="startPlayback" :disabled="!playbackReady" />
                <el-button :icon="VideoPause" size="small" @click="pausePlayback" :disabled="!playbackReady" />
                <el-button :icon="Download" size="small" @click="downloadRecording" :disabled="!playbackReady" />
              </div>
            </div>
          </el-card>

          <!-- System Summary -->
          <el-card class="card glass-card" shadow="hover">
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>System Summary</span>
            </div>
            <div class="system-summary">
              <div class="summary-item">
                <div class="summary-icon">📹</div>
                <div class="summary-info">
                  <span class="summary-label">Total Cameras</span>
                  <strong class="summary-value">{{ totalCameras }}</strong>
                </div>
              </div>
              <div class="summary-item">
                <div class="summary-icon">⚠️</div>
                <div class="summary-info">
                  <span class="summary-label">Active Alarms</span>
                  <strong class="summary-value alarm-count">{{ unreadEvents }}</strong>
                </div>
              </div>
              <div class="summary-item">
                <div class="summary-icon">💾</div>
                <div class="summary-info">
                  <span class="summary-label">Recording Today</span>
                  <strong class="summary-value">{{ todayRecordings }}</strong>
                </div>
              </div>
              <div class="summary-item">
                <div class="summary-icon">🕐</div>
                <div class="summary-info">
                  <span class="summary-label">Uptime</span>
                  <strong class="summary-value">{{ systemUptime }}</strong>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- Add Camera Dialog -->
    <el-dialog v-model="addCameraDialogVisible" title="Add Camera" :width="isMobile ? '95%' : '450px'">
      <el-form :model="newCamera" label-position="top">
        <el-form-item label="Camera Name" required>
          <el-input v-model="newCamera.name" placeholder="e.g., Main Entrance" />
        </el-form-item>
        <el-form-item label="Group" required>
          <el-select v-model="newCamera.groupId" placeholder="Select group" style="width: 100%">
            <el-option v-for="group in cameraGroups" :key="group.id" :label="group.name" :value="group.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Stream URL">
          <el-input v-model="newCamera.streamUrl" placeholder="https:// or rtsp://" />
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="newCamera.location" placeholder="e.g., Lobby, 1F" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addCameraDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="addCamera">Add</el-button>
      </template>
    </el-dialog>

    <!-- Fullscreen Video Dialog -->
    <el-dialog v-model="fullVideoVisible" fullscreen :show-close="false" class="full-video-dialog">
      <div class="full-video-container">
        <video
            ref="fullVideoPlayer"
            class="full-video-stream"
            :src="currentCamera?.streamUrl"
            autoplay
            muted
            loop
            playsinline
        ></video>
        <div class="full-video-ptz-controls" v-if="currentCamera?.ptz">
          <el-button circle :icon="ZoomIn" @click="ptzZoom('in')" />
          <el-button circle :icon="ZoomOut" @click="ptzZoom('out')" />
          <el-button circle :icon="Close" @click="closeFullVideo" />
        </div>
      </div>
    </el-dialog>
  </div>

  <!-- Loading Screen -->
  <div v-else class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Loading</span>
          <span class="loading-dots">...</span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Initializing CCTV Surveillance System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  VideoCamera, Folder, Position, Timer, VideoPlay, VideoPause, Download,
  BellFilled, View, WarningFilled, Bell, Cpu, Plus, ArrowDown, ArrowRight,
  Operation, ZoomIn, ZoomOut, Refresh, FullScreen, Close,
  Setting, Star, Sunny, Camera, Monitor, Delete, WindPower, HotWater,
  DataAnalysis, InfoFilled
} from '@element-plus/icons-vue'

import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  const pinia = instance?.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Video URLs ====================
const FIRE_VIDEO_URL = 'https://aegisnx.com/wp-content/uploads/2025/12/firlvideo.mp4'
const SMOKING_VIDEO_URL = 'https://aegisnx.com/wp-content/uploads/2025/12/smokingVidoe.mp4'

// ==================== Loading State ====================
const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing modules...')
const loadingMessages = ['Initializing modules...', 'Loading video streams...', 'Connecting to NVR...', 'Loading AI models...', 'Almost ready...']

// ==================== Real-time Clock ====================
const currentTime = ref('')
let clockTimer = null

const updateTime = () => {
  const now = new Date()
  const utc = now.getTime() + (now.getTimezoneOffset() * 60000)
  const sgTime = new Date(utc + (8 * 3600000))
  const year = sgTime.getFullYear()
  const month = String(sgTime.getMonth() + 1).padStart(2, '0')
  const day = String(sgTime.getDate()).padStart(2, '0')
  const hours = String(sgTime.getHours()).padStart(2, '0')
  const minutes = String(sgTime.getMinutes()).padStart(2, '0')
  const seconds = String(sgTime.getSeconds()).padStart(2, '0')
  const ms = String(sgTime.getMilliseconds()).padStart(3, '0')
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${ms} SGT`
}

// ==================== Video Elements ====================
const videoPlayer = ref(null)
const fullVideoPlayer = ref(null)

// ==================== Camera Data ====================
const cameraGroups = ref([
  {
    id: 1, name: 'Critical Areas', expanded: true,
    cameras: [
      { id: 101, name: 'Fire Exit Camera', location: 'Fire Exit - East Wing', status: 'online', ptz: true, hasMotion: true, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 102, name: 'Smoking Zone Camera', location: 'Smoking Area - West Wing', status: 'online', ptz: true, hasMotion: true, recording: true, streamUrl: SMOKING_VIDEO_URL }
    ]
  },
  {
    id: 2, name: 'Parking Areas', expanded: false,
    cameras: [
      { id: 201, name: 'Parking Entrance', location: 'B1 - Entrance Gate', status: 'online', ptz: true, hasMotion: false, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 202, name: 'Parking Interior', location: 'B1 - Central Zone', status: 'online', ptz: false, hasMotion: true, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 203, name: 'EV Charging', location: 'B1 - EV Station', status: 'online', ptz: false, hasMotion: false, recording: true, streamUrl: FIRE_VIDEO_URL }
    ]
  },
  {
    id: 3, name: 'Office Areas', expanded: false,
    cameras: [
      { id: 301, name: 'Office 1F', location: '1st Floor Open Area', status: 'online', ptz: false, hasMotion: false, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 302, name: 'Office 2F', location: '2nd Floor Open Area', status: 'online', ptz: false, hasMotion: false, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 303, name: 'Meeting Room A', location: '2F - Meeting Room A', status: 'online', ptz: true, hasMotion: false, recording: false, streamUrl: FIRE_VIDEO_URL }
    ]
  },
  {
    id: 4, name: 'Critical Facilities', expanded: false,
    cameras: [
      { id: 401, name: 'Server Room', location: 'Data Center', status: 'online', ptz: false, hasMotion: false, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 402, name: 'Electrical Room', location: 'MDF Room', status: 'online', ptz: false, hasMotion: false, recording: true, streamUrl: FIRE_VIDEO_URL },
      { id: 403, name: 'Loading Dock', location: 'Warehouse Entrance', status: 'online', ptz: true, hasMotion: true, recording: true, streamUrl: FIRE_VIDEO_URL }
    ]
  }
])

const currentCamera = ref(null)

// PTZ Control Values
const ptzSpeed = ref(50)
const zoomLevel = ref(1.0)
const focusLevel = ref(50.0)
const irisLevel = ref(50.0)
const motionSensitivity = ref(70)
const privacyMasking = ref(false)
const brightness = ref(50)
const contrast = ref(50)
const saturation = ref(50)
const selectedPatrolPresets = ref([])
const activePtzTab = ref('control')

const currentResolution = ref('1920x1080')
const currentFPS = ref(30)

// Device Health
const onlineCameras = computed(() => cameraGroups.value.reduce((t, g) => t + g.cameras.filter(c => c.status === 'online').length, 0))
const offlineCameras = computed(() => cameraGroups.value.reduce((t, g) => t + g.cameras.filter(c => c.status === 'offline').length, 0))
const recordingCameras = computed(() => cameraGroups.value.reduce((t, g) => t + g.cameras.filter(c => c.recording).length, 0))
const totalCameras = computed(() => cameraGroups.value.reduce((t, g) => t + g.cameras.length, 0))

const bandwidthUsage = ref(45.2)
const bandwidthPercent = computed(() => parseFloat(((bandwidthUsage.value / 100) * 100).toFixed(1)))
const bandwidthColor = computed(() => {
  if (bandwidthPercent.value < 50) return '#34d399'
  if (bandwidthPercent.value < 80) return '#f59e0b'
  return '#ef4444'
})

const storageUsed = ref(3.8)
const storageTotal = ref(8)
const storagePercent = computed(() => (storageUsed.value / storageTotal.value) * 100)
const storageColor = computed(() => {
  if (storagePercent.value < 50) return '#34d399'
  if (storagePercent.value < 80) return '#f59e0b'
  return '#ef4444'
})
const retentionDays = ref(30)
const remainingDays = computed(() => {
  const dailyUsage = storageUsed.value / retentionDays.value
  return Math.floor((storageTotal.value - storageUsed.value) / dailyUsage)
})

// System Performance Data
const cpuUsage = ref(42)
const memoryUsage = ref(38)
const networkLatency = ref(23)
const packetLoss = ref(0.2)
const systemUptime = ref('12d 8h 32m')

// Performance Colors
const cpuColor = computed(() => {
  if (cpuUsage.value < 50) return '#34d399'
  if (cpuUsage.value < 80) return '#f59e0b'
  return '#ef4444'
})
const memoryColor = computed(() => {
  if (memoryUsage.value < 50) return '#34d399'
  if (memoryUsage.value < 80) return '#f59e0b'
  return '#ef4444'
})
const latencyColor = computed(() => {
  if (networkLatency.value < 30) return '#34d399'
  if (networkLatency.value < 60) return '#f59e0b'
  return '#ef4444'
})
const packetColor = computed(() => {
  if (packetLoss.value < 0.5) return '#34d399'
  if (packetLoss.value < 1) return '#f59e0b'
  return '#ef4444'
})

const latencyPercent = computed(() => {
  return Math.min((networkLatency.value / 100) * 100, 100)
})

const ptzPresets = ref([
  { id: 1, name: 'Entrance', icon: '🚪', zoom: 1.0 },
  { id: 2, name: 'Counter', icon: '💼', zoom: 2.0 },
  { id: 3, name: 'Elevator', icon: '🛗', zoom: 1.5 },
  { id: 4, name: 'Staircase', icon: '📐', zoom: 1.0 }
])

const todayRecordings = ref(24)

const unreadEvents = ref(4)
const alarmEvents = ref([
  { id: 1, severity: 'critical', type: 'fire', title: 'Fire/Smoke Detected', camera: 'Fire Exit Camera', time: '2 min ago' },
  { id: 2, severity: 'warning', type: 'smoking', title: 'Smoking Detected', camera: 'Smoking Zone Camera', time: '5 min ago' },
  { id: 3, severity: 'warning', type: 'motion', title: 'Motion Detected', camera: 'Parking Interior', time: '15 min ago' },
  { id: 4, severity: 'info', type: 'disconnect', title: 'Camera Offline', camera: 'Meeting Room A', time: '1 hour ago' }
])

const aiDetections = ref([
  { id: 1, type: 'fire', typeLabel: 'Fire/Smoke', confidence: 94.2, time: 'Just now' },
  { id: 2, type: 'smoking', typeLabel: 'Smoking', confidence: 87.3, time: '5 min ago' },
  { id: 3, type: 'person', typeLabel: 'Person', confidence: 96.1, time: '12 min ago' },
  { id: 4, type: 'motion', typeLabel: 'Motion', confidence: 78.5, time: '20 min ago' }
])

const playbackDate = ref(new Date())
const playbackTime = ref(36000)
const playbackReady = ref(false)

const isMobile = ref(false)
const fullVideoVisible = ref(false)
const addCameraDialogVisible = ref(false)
const newCamera = ref({ name: '', groupId: null, streamUrl: '', location: '' })
const recordingActive = ref(false)

// ==================== PTZ Methods ====================
const ptzZoom = (action) => {
  if (action === 'in') zoomLevel.value = parseFloat((Math.min(zoomLevel.value + 0.5, 30)).toFixed(1))
  else zoomLevel.value = parseFloat((Math.max(zoomLevel.value - 0.5, 1)).toFixed(1))
  ElMessage.info(`${action === 'in' ? 'Zoom In' : 'Zoom Out'} to ${zoomLevel.value.toFixed(1)}x`)
}

const ptzFocusNear = () => {
  focusLevel.value = parseFloat((Math.min(focusLevel.value + 5, 100)).toFixed(1))
  ElMessage.info(`Focus Near: ${focusLevel.value.toFixed(1)}%`)
}

const ptzFocusFar = () => {
  focusLevel.value = parseFloat((Math.max(focusLevel.value - 5, 0)).toFixed(1))
  ElMessage.info(`Focus Far: ${focusLevel.value.toFixed(1)}%`)
}

const ptzAutoFocus = () => {
  ElMessage.info('Auto focusing...')
  setTimeout(() => { focusLevel.value = 50.0; ElMessage.success('Focus completed') }, 1000)
}

const ptzIrisOpen = () => {
  irisLevel.value = parseFloat((Math.min(irisLevel.value + 5, 100)).toFixed(1))
  ElMessage.info(`Iris Open: ${irisLevel.value.toFixed(1)}%`)
}

const ptzIrisClose = () => {
  irisLevel.value = parseFloat((Math.max(irisLevel.value - 5, 0)).toFixed(1))
  ElMessage.info(`Iris Close: ${irisLevel.value.toFixed(1)}%`)
}

const ptzIrisAuto = () => {
  ElMessage.info('Auto iris...')
  setTimeout(() => { irisLevel.value = 60.0; ElMessage.success('Iris adjusted') }, 800)
}

const ptzSpeedChange = (val) => ElMessage.info(`Speed set to ${val}%`)
const ptzAux = (cmd) => ElMessage.info(`${cmd} activated`)
const ptzHome = () => { ElMessage.info('Moving to home'); zoomLevel.value = 1.0 }
const ptzReset = () => {
  ptzSpeed.value = 50; zoomLevel.value = 1.0; focusLevel.value = 50.0; irisLevel.value = 50.0
  ElMessage.info('Reset completed')
}
const ptzStartCruise = () => ElMessage.info('Cruise mode started')
const ptzPatrol = () => ElMessage.info('Patrol mode started')
const gotoPreset = (preset) => { ElMessage.success(`Moving to: ${preset.name}`); zoomLevel.value = preset.zoom }
const setPreset = (preset) => { preset.zoom = zoomLevel.value; ElMessage.success(`Preset ${preset.name} saved`) }
const addNewPreset = () => ElMessage.info('Add new preset')
const deletePreset = (id) => { ptzPresets.value = ptzPresets.value.filter(p => p.id !== id); ElMessage.success('Preset deleted') }
const startPatrol = () => { if (selectedPatrolPresets.value.length) ElMessage.info(`Patrol started with ${selectedPatrolPresets.value.length} presets`) }
const stopPatrol = () => ElMessage.info('Patrol stopped')
const configurePrivacyMask = () => ElMessage.info('Configure privacy mask')
const configureLimits = () => ElMessage.info('Configure limits')
const clearLimits = () => ElMessage.info('Limits cleared')
const showManagePresets = () => activePtzTab.value = 'presets'
const toggleRecording = () => ElMessage.info(`Recording ${recordingActive.value ? 'stopped' : 'started'}`)
const takeSnapshot = () => ElMessage.success('Snapshot saved')

// ==================== Camera Methods ====================
const toggleGroup = (groupId) => {
  const group = cameraGroups.value.find(g => g.id === groupId)
  if (group) group.expanded = !group.expanded
}

const selectCamera = (camera) => {
  if (videoPlayer.value) videoPlayer.value.pause()
  currentCamera.value = camera
  ElMessage.success(`Switched to ${camera.name}`)
  nextTick(() => {
    if (videoPlayer.value && camera.streamUrl) {
      videoPlayer.value.load()
      videoPlayer.value.play().catch(() => {})
    }
  })
}

const refreshStream = () => {
  if (videoPlayer.value && currentCamera.value?.streamUrl) {
    videoPlayer.value.load()
    videoPlayer.value.play().catch(e => console.warn(e))
    ElMessage.success('Stream refreshed')
  }
}

const onVideoLoaded = () => {}
const onVideoError = () => ElMessage.error('Failed to load video stream')

const showAddCameraDialog = () => {
  newCamera.value = { name: '', groupId: null, streamUrl: '', location: '' }
  addCameraDialogVisible.value = true
}

const addCamera = () => {
  if (!newCamera.value.name || !newCamera.value.groupId) {
    ElMessage.warning('Please fill camera name and select group')
    return
  }
  const group = cameraGroups.value.find(g => g.id === newCamera.value.groupId)
  if (group) {
    group.cameras.push({
      id: Date.now(), name: newCamera.value.name, location: newCamera.value.location || 'Unknown',
      status: 'online', ptz: false, hasMotion: false, recording: true, streamUrl: newCamera.value.streamUrl || ''
    })
    ElMessage.success(`Camera ${newCamera.value.name} added`)
  }
  addCameraDialogVisible.value = false
}

const formatPlaybackTime = (val) => `${Math.floor(val / 3600).toString().padStart(2, '0')}:${Math.floor((val % 3600) / 60).toString().padStart(2, '0')}`
const loadPlaybackTimeline = () => { playbackReady.value = true; ElMessage.success('Recordings loaded') }
const seekPlayback = (val) => ElMessage.info(`Seek to ${formatPlaybackTime(val)}`)
const startPlayback = () => ElMessage.info('Playback started')
const pausePlayback = () => ElMessage.info('Playback paused')
const downloadRecording = () => ElMessage.success('Download started')
const playbackByEvent = (event) => { playbackDate.value = new Date(); playbackTime.value = 36000; playbackReady.value = true; ElMessage.info(`Playing back ${event.camera}`) }
const openFullPlayback = () => ElMessage.info('Full timeline')

const toggleFullVideo = () => { fullVideoVisible.value = true }
const closeFullVideo = () => {
  fullVideoVisible.value = false
  if (videoPlayer.value && currentCamera.value?.streamUrl) nextTick(() => videoPlayer.value.play())
}

const preloadAssets = async () => {
  let progress = 0, idx = 0
  const msgInterval = setInterval(() => { if (idx < loadingMessages.length - 1) loadingMessage.value = loadingMessages[++idx] }, 800)
  const progInterval = setInterval(() => { if (progress < 90) progress += Math.random() * 10; loadingProgress.value = Math.min(progress, 90) }, 100)
  await new Promise(r => setTimeout(r, 1500))
  clearInterval(msgInterval); clearInterval(progInterval)
  loadingProgress.value = 100
  await new Promise(r => setTimeout(r, 500))
  isPageLoaded.value = true
  nextTick(() => { const firstCam = cameraGroups.value[0]?.cameras[0]; if (firstCam) selectCamera(firstCam) })
}

let alarmTimer = null
const startAlarmSimulation = () => {
  alarmTimer = setInterval(() => {
    if (Math.random() > 0.7) {
      const types = [{ type: 'fire', title: 'Fire/Smoke', camera: 'Fire Exit Camera', severity: 'critical' }]
      alarmEvents.value.unshift({ id: Date.now(), ...types[0], time: 'Just now' })
      if (alarmEvents.value.length > 10) alarmEvents.value.pop()
      unreadEvents.value++
    }
    if (Math.random() > 0.8) {
      const detTypes = [{ type: 'fire', typeLabel: 'Fire/Smoke', confidence: 85 + Math.random() * 14 }]
      aiDetections.value.unshift({ id: Date.now(), ...detTypes[0], confidence: parseFloat((85 + Math.random() * 14).toFixed(1)), time: 'Just now' })
      if (aiDetections.value.length > 8) aiDetections.value.pop()
    }
    todayRecordings.value += Math.floor(Math.random() * 2)
    storageUsed.value = parseFloat((storageUsed.value + Math.random() * 0.03).toFixed(1))
    bandwidthUsage.value = parseFloat((40 + Math.random() * 30).toFixed(1))

    // 更新性能数据
    cpuUsage.value = parseFloat((30 + Math.random() * 40).toFixed(1))
    memoryUsage.value = parseFloat((25 + Math.random() * 45).toFixed(1))
    networkLatency.value = parseFloat((10 + Math.random() * 40).toFixed(0))
    packetLoss.value = parseFloat((0.1 + Math.random() * 0.5).toFixed(1))
  }, 8000)
}

const checkMobile = () => { isMobile.value = window.innerWidth < 768 }
const handleResize = () => checkMobile()

onMounted(async () => {
  checkMobile()
  updateTime()
  clockTimer = setInterval(updateTime, 100)
  window.addEventListener('resize', handleResize)
  await preloadAssets()
  startAlarmSimulation()
})

onBeforeUnmount(() => {
  clearInterval(clockTimer)
  clearInterval(alarmTimer)
  window.removeEventListener('resize', handleResize)
  if (videoPlayer.value) videoPlayer.value.pause()
})
</script>

<style scoped>
* {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
*::-webkit-scrollbar {
  display: none;
  width: 0;
  height: 0;
}

/* Loading Screen */
.loading-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #0a1620 0%, #03060c 100%);
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
  background: rgba(15, 25, 45, 0.6);
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
}
.loading-tip {
  font-size: 13px;
  color: #94a3b8;
  letter-spacing: 1px;
  margin-bottom: 8px;
}
.loading-subtip {
  font-size: 11px;
  color: #efefef;
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

/* Main Page */
.cctv-page {
  height: 100%;
  background: radial-gradient(circle at 10% 20%, #0a1620, #03060c);
  padding: 24px;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow-y: auto;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
  margin-bottom: 20px;
}
.page-title {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #e2e8f0, #60a5fa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin: 0;
}
.live-time {
  position: absolute;
  right: 0;
  font-size: 14px;
  font-weight: 600;
  color: #facc15;
  font-family: monospace;
  padding: 6px 14px;
  background: rgba(15, 25, 45, 0.6);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  backdrop-filter: blur(8px);
}

.main-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.three-columns {
  flex: 1;
  display: flex;
  gap: 20px;
  align-items: stretch;
  min-height: 0;
}

.col-left, .col-right {
  width: 320px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  min-height: 0;
}
.col-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 0;
}

.glass-card {
  background: rgba(15, 25, 45, 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 20px;
  transition: all 0.3s;
}
.glass-card:hover {
  background: rgba(15, 25, 45, 0.8);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-3px);
}
.card {
  background: transparent;
}
.card-header {
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 15px;
  color: #e2e8f0;
  border-left: 4px solid #3b82f6;
  padding-left: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Camera Tree */
.camera-tree {
  max-height: 320px;
  overflow-y: auto;
}
.camera-group {
  margin-bottom: 8px;
}
.group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 6px;
  cursor: pointer;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  color: #e2e8f0;
}
.group-header .group-count {
  margin-left: auto;
  font-size: 11px;
  color: #94a3b8;
  background: rgba(0,0,0,0.3);
  padding: 0 6px;
  border-radius: 10px;
}
.camera-list {
  padding-left: 24px;
}
.camera-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  color: #94a3b8;
}
.camera-item:hover {
  background: rgba(59, 130, 246, 0.2);
  color: #e2e8f0;
}
.camera-item.active {
  background: rgba(59, 130, 246, 0.3);
  color: #60a5fa;
}
.cam-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.cam-status.online {
  background: #34d399;
  box-shadow: 0 0 6px #34d399;
}
.cam-status.offline {
  background: #ef4444;
}
.cam-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.cam-name {
  font-size: 12px;
  font-weight: 500;
}
.cam-location-sm {
  font-size: 10px;
  color: #efefef;
}
.cam-badges {
  display: flex;
  gap: 4px;
}
.motion-tag, .rec-tag {
  font-size: 9px;
  padding: 0 4px;
  height: 16px;
  line-height: 16px;
}

/* Device Health */
.device-health {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.health-metrics {
  display: flex;
  gap: 16px;
  justify-content: space-around;
}
.health-metric {
  display: flex;
  align-items: center;
  gap: 8px;
}
.metric-icon {
  font-size: 20px;
}
.metric-info {
  display: flex;
  flex-direction: column;
}
.metric-label {
  font-size: 10px;
  color: #94a3b8;
}
.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
}
.bandwidth-usage {
  padding-top: 8px;
  border-top: 1px solid rgba(148,163,184,0.15);
}
.bandwidth-header {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 6px;
}

/* PTZ Presets */
.presets-grid {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.preset-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
  cursor: pointer;
  width: 130px;
}
.preset-item:hover {
  background: rgba(59, 130, 246, 0.25);
  transform: translateX(4px);
}
.preset-thumb {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preset-icon {
  font-size: 20px;
}
.preset-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.preset-name {
  font-size: 12px;
  color: #cbd5e1;
}
.preset-set-btn {
  opacity: 0;
}
.preset-item:hover .preset-set-btn {
  opacity: 1;
}

/* Storage Status */
.recording-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}
.stat-row strong {
  color: #facc15;
}
.stat-row .el-progress {
  width: 100%;
  margin-top: 4px;
}

/* Performance Metrics */
.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.perf-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.perf-row span {
  font-size: 12px;
  color: #94a3b8;
  min-width: 95px;
}
.perf-row .el-progress {
  flex: 1;
}
.perf-row strong {
  font-size: 12px;
  color: #facc15;
  min-width: 40px;
  text-align: right;
}

/* System Summary */
.system-summary {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
}
.summary-icon {
  font-size: 24px;
  width: 36px;
  text-align: center;
}
.summary-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.summary-label {
  font-size: 12px;
  color: #94a3b8;
}
.summary-value {
  font-size: 16px;
  font-weight: 700;
  color: #60a5fa;
}
.summary-value.alarm-count {
  color: #ef4444;
}

/* Video Player - 关键样式：高度自适应比例 */
.video-player-card {
  width: 100%;
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.video-wrapper {
  width: 100%;
  position: relative;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 16px;
  overflow: hidden;
}

.video-stream {
  width: 100%;
  height: auto;
  object-fit: contain;
  background: #000;
  display: block;
}

.no-camera-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #efefef;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 16px;
}

.video-info-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 10px 15px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.7), transparent);
  pointer-events: none;
}
.video-info-left {
  display: flex;
  gap: 10px;
}
.video-info-left .cam-name {
  color: #fff;
  font-weight: 600;
}
.video-info-left .cam-location {
  color: #94a3b8;
  font-size: 11px;
}
.video-info-right {
  display: flex;
  gap: 8px;
}
.live-badge {
  color: #ff3b30;
  animation: blink 1s infinite;
}
.resolution-badge, .fps-badge {
  background: rgba(0, 0, 0, 0.6);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  color: #60a5fa;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* PTZ Controls */
.modern-ptz-card {
  min-height: auto;
}
.ptz-tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid rgba(96,165,250,0.2);
  margin-bottom: 16px;
}
.ptz-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  cursor: pointer;
  color: #94a3b8;
}
.ptz-tab:hover {
  color: #e2e8f0;
  background: rgba(59,130,246,0.1);
}
.ptz-tab.active {
  color: #60a5fa;
  border-bottom: 2px solid #60a5fa;
}
.section-label {
  font-size: 11px;
  font-weight: 600;
  color: #60a5fa;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.zoom-focus-section {
  display: flex;
  gap: 16px;
  justify-content: space-around;
}
.control-card {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: rgba(59,130,246,0.08);
  border-radius: 12px;
}
.control-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: #94a3b8;
  font-size: 12px;
  margin-bottom: 8px;
}
.control-value {
  font-size: 20px;
  font-weight: 700;
  color: #facc15;
  margin-bottom: 8px;
}
.control-buttons {
  display: flex;
  gap: 6px;
  justify-content: center;
}
.speed-section {
  padding: 0 8px;
}
.speed-control-modern {
  display: flex;
  align-items: center;
  gap: 12px;
}
.speed-value {
  font-size: 14px;
  font-weight: 600;
  color: #facc15;
  min-width: 45px;
}
.speed-control-modern .el-slider {
  flex: 1;
}
.speed-buttons {
  display: flex;
  gap: 6px;
}
.aux-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}
.aux-btn {
  padding: 10px;
  background: rgba(59,130,246,0.15);
  border: 1px solid rgba(59,130,246,0.3);
  border-radius: 10px;
  color: #cbd5e1;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.aux-btn:hover {
  background: rgba(59,130,246,0.3);
  transform: translateY(-2px);
}
.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  padding-top: 8px;
  border-top: 1px solid rgba(96,165,250,0.2);
}
.action-buttons .el-button {
  background: rgba(59,130,246,0.15);
  border-color: rgba(59,130,246,0.3);
}

/* Presets Tab */
.presets-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 250px;
  overflow-y: auto;
}
.preset-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: rgba(59,130,246,0.1);
  border-radius: 12px;
  cursor: pointer;
}
.preset-card:hover {
  background: rgba(59,130,246,0.2);
}
.preset-card-thumb {
  width: 50px;
  height: 50px;
  background: #1e293b;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.preset-card-info {
  flex: 1;
}
.preset-card-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}
.patrol-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.patrol-controls .el-select {
  flex: 1;
  min-width: 150px;
}

/* Advanced Tab */
.advanced-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.advanced-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(148,163,184,0.1);
}
.advanced-label {
  font-size: 12px;
  color: #cbd5e1;
  min-width: 140px;
}
.image-settings {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.image-settings > div {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #94a3b8;
}

/* Simple controls */
.simple-control-card {
  min-height: auto;
}
.simple-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
  padding: 8px 0;
}
.simple-controls .el-button {
  background: rgba(59,130,246,0.15);
  border-color: rgba(59,130,246,0.3);
}

/* Alert List */
.alert-list {
  max-height: 260px;
  overflow-y: auto;
}
.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid rgba(148,163,184,0.15);
  cursor: pointer;
}
.alert-item.critical { border-left: 3px solid #ef4444; }
.alert-item.warning { border-left: 3px solid #f59e0b; }
.alert-item:hover { background: rgba(59,130,246,0.1); }
.alert-title {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  font-weight: bold;
}
.alert-meta {
  display: flex;
  gap: 12px;
  font-size: 10px;
  color: #efefef;
}
.alert-action { opacity: 0; }
.alert-item:hover .alert-action { opacity: 1; }

/* Detection Feed */
.detection-feed {
  max-height: 240px;
  overflow-y: auto;
}
.detection-feed-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid rgba(148,163,184,0.1);
}
.detection-feed-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.detection-feed-icon.fire { background: rgba(239,68,68,0.2); }
.detection-feed-icon.smoking { background: rgba(245,158,11,0.2); }
.detection-feed-icon.person { background: rgba(59,130,246,0.2); }
.detection-feed-type {
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
}
.detection-feed-confidence {
  font-size: 10px;
  color: #efefef;
}

.detection-feed-time {
  color: #ef4444;
}

/* Playback */
.playback-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.date-selector { display: flex; justify-content: center; }
.timeline-slider { width: 100%; }
.playback-buttons {
  display: flex;
  gap: 8px;
  justify-content: center;
}

/* Snapshot Grid */
.snapshot-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.snapshot-preview {
  height: 70px;
  background: #1e293b;
  border-radius: 8px;
}
.snapshot-time {
  font-size: 10px;
  color: #efefef;
  text-align: center;
  margin-top: 4px;
}

/* Fullscreen */
.full-video-dialog :deep(.el-dialog) {
  background: black;
}
.full-video-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  display: flex;
  justify-content: center;
  align-items: center;
}
.full-video-stream {
  width: 100%;
  height: auto;
  max-height: 100vh;
  object-fit: contain;
}
.full-video-ptz-controls {
  position: fixed;
  right: 20px;
  bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 1001;
}
.full-video-ptz-controls .el-button {
  background: rgba(0, 0, 0, 0.6);
  border: none;
  color: white;
}
.full-video-ptz-controls .el-button:hover {
  background: rgba(59, 130, 246, 0.8);
}

/* Mobile */
@media (max-width: 768px) {
  .cctv-page { padding: 16px; }
  .page-title { font-size: 26px; }
  .live-time { position: static; font-size: 11px; }
  .three-columns { flex-direction: column; }
  .col-left, .col-right { width: 100%; }
  .zoom-focus-section { flex-direction: column; }
  .aux-grid { grid-template-columns: repeat(2, 1fr); }
  .no-camera-placeholder { min-height: 250px; }
}
</style>

<style>
.el-card__body {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.col-left .el-card,
.col-right .el-card {
  overflow: visible;
  height: auto;
  flex-shrink: 0;
}
.chart-card .el-card__body {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>