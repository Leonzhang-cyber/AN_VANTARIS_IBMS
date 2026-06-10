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
        <div class="loading-tip">ONVIF Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="onvif-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>ONVIF</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>ONVIF Gateway Management</h1>
        <p class="description">Manage ONVIF camera devices, video streams, PTZ control, and event monitoring</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="primary" @click="openAddDeviceDialog">
          <el-icon><Plus /></el-icon>
          Add Device
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span>{{ stat.subTitle }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Device Discovery -->
    <el-card class="discovery-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Device Discovery</span>
          <div class="discovery-controls">
            <el-input
                v-model="discoveryIp"
                placeholder="IP Range (e.g., 192.168.1.0/24)"
                style="width: 200px"
                size="small"
            />
            <el-button type="primary" size="small" @click="startDiscovery" :loading="discovering">
              <el-icon><Search /></el-icon> Discover
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="discoveredDevices" stripe style="width: 100%" v-loading="discovering">
        <el-table-column prop="name" label="Device Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="port" label="Port" width="80" />
        <el-table-column prop="manufacturer" label="Manufacturer" width="150" />
        <el-table-column prop="model" label="Model" width="150" />
        <el-table-column prop="firmware" label="Firmware" width="120" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="importDevice(row)">Import</el-button>
            <el-button link type="info" size="small" @click="testDevice(row)">Test</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- ONVIF Devices Table -->
    <el-card class="devices-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>ONVIF Devices</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or IP"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Online" value="Online" />
              <el-option label="Offline" value="Offline" />
              <el-option label="Warning" value="Warning" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchDevices" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDevices" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Device Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP Address" width="140" />
        <el-table-column prop="port" label="Port" width="70" />
        <el-table-column prop="manufacturer" label="Manufacturer" width="130" />
        <el-table-column prop="profileCount" label="Profiles" width="80" align="center" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Online' ? 'success' : row.status === 'Warning' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Online' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewProfiles(row)">Profiles</el-button>
            <el-button link type="success" size="small" @click="viewLiveStream(row)">Live View</el-button>
            <el-button link type="info" size="small" @click="ptzControl(row)">PTZ</el-button>
            <el-button link type="danger" size="small" @click="deleteDevice(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDevices.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Video Profiles Section -->
    <el-card class="profiles-card" shadow="hover" v-if="selectedDevice">
      <template #header>
        <div class="card-header">
          <span>Video Profiles - {{ selectedDevice.name }}</span>
          <div class="profile-actions">
            <el-button size="small" @click="refreshProfiles">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="videoProfiles" stripe size="small">
        <el-table-column prop="token" label="Token" width="120" />
        <el-table-column prop="name" label="Profile Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="resolution" label="Resolution" width="120" />
        <el-table-column prop="framerate" label="Framerate" width="80" align="center" />
        <el-table-column prop="encoding" label="Encoding" width="100" />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="previewStream(row)">Preview</el-button>
            <el-button link type="success" size="small" @click="setAsPrimary(row)">Set Primary</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Live View Dialog -->
    <el-dialog v-model="liveDialogVisible" :title="`Live View - ${currentDevice?.name}`" width="900px" destroy-on-close>
      <div class="live-view">
        <div class="video-container">
          <div class="video-placeholder">
            <img :src="liveImageUrl" v-if="liveImageUrl" class="video-frame" />
            <div v-else class="video-placeholder-content">
              <el-icon :size="64"><VideoCamera /></el-icon>
              <p>Connecting to camera stream...</p>
            </div>
          </div>
          <div class="video-controls" v-if="currentDevice?.ptzSupported">
            <div class="ptz-controls">
              <el-button-group>
                <el-button size="small" @click="ptzMove('up')">
                  <el-icon><ArrowUp /></el-icon>
                </el-button>
              </el-button-group>
              <div class="ptz-middle">
                <el-button-group>
                  <el-button size="small" @click="ptzMove('left')">
                    <el-icon><ArrowLeft /></el-icon>
                  </el-button>
                  <el-button size="small" @click="ptzMove('stop')">
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                  <el-button size="small" @click="ptzMove('right')">
                    <el-icon><ArrowRight /></el-icon>
                  </el-button>
                </el-button-group>
              </div>
              <el-button-group>
                <el-button size="small" @click="ptzMove('down')">
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
              </el-button-group>
            </div>
            <div class="zoom-controls">
              <el-button size="small" @click="ptzZoom('in')">
                <el-icon><ZoomIn /></el-icon> Zoom In
              </el-button>
              <el-button size="small" @click="ptzZoom('out')">
                <el-icon><ZoomOut /></el-icon> Zoom Out
              </el-button>
              <el-button size="small" @click="ptzHome">
                <el-icon><HomeFilled /></el-icon> Home
              </el-button>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="liveDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="takeSnapshot">Take Snapshot</el-button>
      </template>
    </el-dialog>

    <!-- PTZ Control Dialog -->
    <el-dialog v-model="ptzDialogVisible" title="PTZ Control" width="550px" destroy-on-close>
      <div class="ptz-panel">
        <div class="ptz-joystick">
          <div class="joystick-pad">
            <div class="joystick-row">
              <div class="joystick-cell"></div>
              <div class="joystick-cell">
                <el-button circle size="small" @click="ptzMove('up')">
                  <el-icon><ArrowUp /></el-icon>
                </el-button>
              </div>
              <div class="joystick-cell"></div>
            </div>
            <div class="joystick-row">
              <div class="joystick-cell">
                <el-button circle size="small" @click="ptzMove('left')">
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
              </div>
              <div class="joystick-cell">
                <el-button circle size="small" @click="ptzMove('stop')">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </div>
              <div class="joystick-cell">
                <el-button circle size="small" @click="ptzMove('right')">
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="joystick-row">
              <div class="joystick-cell"></div>
              <div class="joystick-cell">
                <el-button circle size="small" @click="ptzMove('down')">
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
              </div>
              <div class="joystick-cell"></div>
            </div>
          </div>
        </div>
        <div class="ptz-zoom-section">
          <div class="zoom-control">
            <span>Zoom:</span>
            <el-slider v-model="zoomLevel" :min="0" :max="100" @change="ptzZoomTo" />
          </div>
          <div class="preset-controls">
            <span>Presets:</span>
            <el-button-group>
              <el-button size="small" @click="ptzPreset(1)">Preset 1</el-button>
              <el-button size="small" @click="ptzPreset(2)">Preset 2</el-button>
              <el-button size="small" @click="ptzPreset(3)">Preset 3</el-button>
              <el-button size="small" @click="ptzPreset(4)">Preset 4</el-button>
            </el-button-group>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="ptzDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Device Dialog -->
    <el-dialog v-model="deviceDialogVisible" :title="dialogMode === 'add' ? 'Add ONVIF Device' : 'Edit ONVIF Device'" width="600px" destroy-on-close class="device-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="deviceForm" :rules="deviceRules" ref="deviceFormRef" label-width="120px">
            <el-form-item label="Device Name" prop="name">
              <el-input v-model="deviceForm.name" placeholder="Enter device name" />
            </el-form-item>
            <el-form-item label="IP Address" prop="ipAddress">
              <el-input v-model="deviceForm.ipAddress" placeholder="192.168.1.100" />
            </el-form-item>
            <el-form-item label="Port" prop="port">
              <el-input-number v-model="deviceForm.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Username" prop="username">
              <el-input v-model="deviceForm.username" placeholder="admin" />
            </el-form-item>
            <el-form-item label="Password" prop="password">
              <el-input v-model="deviceForm.password" type="password" placeholder="password" show-password />
            </el-form-item>
            <el-form-item label="RTSP Port" prop="rtspPort">
              <el-input-number v-model="deviceForm.rtspPort" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="deviceForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Connection Timeout (ms)">
              <el-input-number v-model="deviceForm.timeout" :min="1000" :max="30000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="deviceForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Enable Motion Detection">
              <el-switch v-model="deviceForm.motionDetection" />
            </el-form-item>
            <el-form-item label="Enable Audio">
              <el-switch v-model="deviceForm.audioEnabled" />
            </el-form-item>
            <el-form-item label="PTZ Supported">
              <el-switch v-model="deviceForm.ptzSupported" />
            </el-form-item>
            <el-form-item label="Enable Logging">
              <el-switch v-model="deviceForm.enableLogging" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="deviceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testDeviceConnection" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveDevice">
          Save Device
        </el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Device Connected' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Device:</strong> {{ testResult.details.device }}</p>
          <p><strong>Manufacturer:</strong> {{ testResult.details.manufacturer }}</p>
          <p><strong>Model:</strong> {{ testResult.details.model }}</p>
          <p><strong>Firmware:</strong> {{ testResult.details.firmware }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Snapshot Dialog -->
    <el-dialog v-model="snapshotDialogVisible" title="Snapshot" width="600px" destroy-on-close>
      <div class="snapshot-container">
        <img :src="snapshotUrl" class="snapshot-image" />
        <div class="snapshot-info">
          <p>Captured: {{ snapshotTime }}</p>
          <p>Device: {{ currentDevice?.name }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="snapshotDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadSnapshot">Download</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download,
  Delete, Connection, Edit, VideoCamera, ZoomIn, ZoomOut,
  HomeFilled, ArrowLeft, ArrowRight, User
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing ONVIF gateway...', 'Discovering devices...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const discovering = ref(false)
const testing = ref(false)
const deviceDialogVisible = ref(false)
const liveDialogVisible = ref(false)
const ptzDialogVisible = ref(false)
const testDialogVisible = ref(false)
const snapshotDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedDevice = ref<any>(null)
const currentDevice = ref<any>(null)
const discoveryIp = ref('192.168.1.0/24')
const searchKeyword = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const zoomLevel = ref(50)
const liveImageUrl = ref('')
const snapshotUrl = ref('')
const snapshotTime = ref('')

const deviceFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'ONVIF Devices', value: '12', trend: 3, icon: 'VideoCamera', bgColor: '#409eff', key: 'devices', subTitle: 'Online: 10' },
  { title: 'Video Profiles', value: '24', trend: 2, icon: 'Document', bgColor: '#67c23a', key: 'profiles', subTitle: 'Active: 22' },
  { title: 'Recordings', value: '1.2 TB', trend: 8, icon: 'Clock', bgColor: '#e6a23c', key: 'storage', subTitle: 'Last 30 days' },
  { title: 'Motion Events', value: '156', trend: -5, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'events', subTitle: 'Last 24h' }
])

const discoveredDevices = ref([
  { name: 'Camera-01', ipAddress: '192.168.1.100', port: 80, manufacturer: 'Hikvision', model: 'DS-2CD2T25', firmware: 'V5.5.0' },
  { name: 'Camera-02', ipAddress: '192.168.1.101', port: 80, manufacturer: 'Dahua', model: 'IPC-HFW1230', firmware: 'V2.800' },
  { name: 'Camera-03', ipAddress: '192.168.1.102', port: 80, manufacturer: 'Axis', model: 'P3364-V', firmware: '6.50' }
])

const devices = ref([
  { id: 1, name: 'Main Entrance Camera', ipAddress: '192.168.1.100', port: 80, manufacturer: 'Hikvision', profileCount: 3, status: 'Online', lastSeen: '2024-01-20 10:30:00', ptzSupported: true, username: 'admin', password: '****' },
  { id: 2, name: 'Parking Lot Camera', ipAddress: '192.168.1.101', port: 80, manufacturer: 'Dahua', profileCount: 2, status: 'Online', lastSeen: '2024-01-20 10:28:00', ptzSupported: false },
  { id: 3, name: 'Lobby PTZ Camera', ipAddress: '192.168.1.102', port: 80, manufacturer: 'Axis', profileCount: 4, status: 'Online', lastSeen: '2024-01-20 10:32:00', ptzSupported: true },
  { id: 4, name: 'East Wing Camera', ipAddress: '192.168.1.103', port: 80, manufacturer: 'Hikvision', profileCount: 2, status: 'Warning', lastSeen: '2024-01-20 10:25:00', ptzSupported: false },
  { id: 5, name: 'Server Room Camera', ipAddress: '192.168.1.104', port: 80, manufacturer: 'Sony', profileCount: 2, status: 'Online', lastSeen: '2024-01-20 10:29:00', ptzSupported: false }
])

const videoProfiles = ref([
  { token: 'profile1', name: 'Main Stream', resolution: '1920x1080', framerate: 30, encoding: 'H.264' },
  { token: 'profile2', name: 'Sub Stream', resolution: '640x480', framerate: 15, encoding: 'H.264' },
  { token: 'profile3', name: 'Mobile Stream', resolution: '352x240', framerate: 10, encoding: 'MJPEG' }
])

// ==================== Computed ====================
const filteredDevices = computed(() => {
  let filtered = [...devices.value]
  if (searchKeyword.value) filtered = filtered.filter(d => d.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || d.ipAddress.includes(searchKeyword.value))
  if (statusFilter.value) filtered = filtered.filter(d => d.status === statusFilter.value)
  return filtered
})

const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDevices.value.slice(start, end)
})

// ==================== Helper Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting ONVIF configuration...')
const fetchDevices = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Devices refreshed') }, 500) }

const startDiscovery = () => {
  discovering.value = true
  setTimeout(() => {
    discovering.value = false
    ElMessage.success(`Discovered ${discoveredDevices.value.length} devices`)
  }, 2000)
}

const importDevice = (device: any) => {
  deviceForm.name = device.name
  deviceForm.ipAddress = device.ipAddress
  deviceForm.port = device.port
  deviceForm.manufacturer = device.manufacturer
  deviceDialogVisible.value = true
  dialogMode.value = 'add'
  ElMessage.success(`Device ${device.name} imported`)
}

const testDevice = (device: any) => {
  ElMessage.info(`Testing connection to ${device.name}...`)
  setTimeout(() => { ElMessage.success(`${device.name} is reachable`) }, 1000)
}

const openAddDeviceDialog = () => {
  dialogMode.value = 'add'
  Object.assign(deviceForm, {
    id: null, name: '', ipAddress: '', port: 80, username: '', password: '',
    rtspPort: 554, description: '', timeout: 5000, autoReconnect: true,
    motionDetection: false, audioEnabled: false, ptzSupported: false, enableLogging: true
  })
  deviceDialogVisible.value = true
}

const editDevice = (device: any) => {
  dialogMode.value = 'edit'
  Object.assign(deviceForm, device)
  deviceDialogVisible.value = true
}

const testDeviceConnection = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Successfully connected to ONVIF device'
    testResult.details = {
      device: deviceForm.ipAddress,
      manufacturer: deviceForm.manufacturer || 'Generic',
      model: 'IP Camera',
      firmware: '1.0',
      responseTime: 45
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveDevice = async () => {
  if (!deviceFormRef.value) return
  await deviceFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Device added successfully' : 'Device updated successfully')
      deviceDialogVisible.value = false
    }
  })
}

const deleteDevice = (device: any) => {
  ElMessageBox.confirm(`Delete device "${device.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = devices.value.findIndex(d => d.id === device.id)
    if (index !== -1) { devices.value.splice(index, 1); if (selectedDevice.value?.id === device.id) selectedDevice.value = null; ElMessage.success(`Deleted: ${device.name}`) }
  }).catch(() => {})
}

const viewProfiles = (device: any) => {
  selectedDevice.value = device
}

const refreshProfiles = () => {
  ElMessage.success('Profiles refreshed')
}

const viewLiveStream = (device: any) => {
  currentDevice.value = device
  liveDialogVisible.value = true
  simulateLiveStream()
}

const ptzControl = (device: any) => {
  currentDevice.value = device
  ptzDialogVisible.value = true
}

const previewStream = (profile: any) => {
  ElMessage.info(`Previewing ${profile.name} stream`)
}

const setAsPrimary = (profile: any) => {
  ElMessage.success(`${profile.name} set as primary stream`)
}

const simulateLiveStream = () => {
  let frame = 0
  const images = [
    'https://picsum.photos/800/450?random=1',
    'https://picsum.photos/800/450?random=2',
    'https://picsum.photos/800/450?random=3',
    'https://picsum.photos/800/450?random=4'
  ]
  const interval = setInterval(() => {
    if (!liveDialogVisible.value) {
      clearInterval(interval)
      return
    }
    liveImageUrl.value = images[frame % images.length]
    frame++
  }, 2000)
}

const ptzMove = (direction: string) => {
  const movements: Record<string, string> = {
    'up': 'Moving up',
    'down': 'Moving down',
    'left': 'Moving left',
    'right': 'Moving right',
    'stop': 'Stopped'
  }
  ElMessage.info(movements[direction] || direction)
}

const ptzZoom = (direction: string) => {
  if (direction === 'in') {
    zoomLevel.value = Math.min(100, zoomLevel.value + 10)
    ElMessage.info(`Zooming in to ${zoomLevel.value}%`)
  } else {
    zoomLevel.value = Math.max(0, zoomLevel.value - 10)
    ElMessage.info(`Zooming out to ${zoomLevel.value}%`)
  }
}

const ptzZoomTo = (value: number) => {
  ElMessage.info(`Zoom set to ${value}%`)
}

const ptzHome = () => {
  ElMessage.info('Moving to home position')
  zoomLevel.value = 50
}

const ptzPreset = (num: number) => {
  ElMessage.info(`Moving to preset ${num}`)
}

const takeSnapshot = () => {
  snapshotUrl.value = liveImageUrl.value
  snapshotTime.value = new Date().toLocaleString()
  snapshotDialogVisible.value = true
}

const downloadSnapshot = () => {
  ElMessage.success('Snapshot downloaded')
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Form ====================
const deviceForm = reactive({
  id: null, name: '', ipAddress: '', port: 80, username: '', password: '',
  rtspPort: 554, description: '', timeout: 5000, autoReconnect: true,
  motionDetection: false, audioEnabled: false, ptzSupported: false, enableLogging: true
})

const deviceRules = {
  name: [{ required: true, message: 'Please enter device name', trigger: 'blur' }],
  ipAddress: [{ required: true, message: 'Please enter IP address', trigger: 'blur' }],
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchDevices() }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
/* Loading screen styles */
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
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
.loading-dots {
  display: inline-flex;
  gap: 2px;
}
.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
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
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
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
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main page styles */
.onvif-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header .breadcrumb { margin-bottom: 8px; }
.page-header h1 { font-size: 28px; font-weight: 600; color: #303133; margin: 0 0 8px 0; }
.page-header .description { color: #909399; font-size: 14px; margin: 0; }
.page-header .header-actions { display: flex; gap: 12px; }

.stats-row { margin-bottom: 20px; }
.stat-card { cursor: pointer; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card .stat-content { display: flex; justify-content: space-between; align-items: center; }
.stat-card .stat-info { flex: 1; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.stat-card .stat-trend { font-size: 12px; display: flex; align-items: center; gap: 4px; }
.stat-card .stat-trend.up { color: #67c23a; }
.stat-card .stat-trend.down { color: #f56c6c; }
.stat-card .stat-trend .trend-label { color: #909399; margin-left: 4px; }
.stat-card .stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-card .stat-footer { margin-top: 12px; padding-top: 8px; border-top: 1px solid #ebeef5; font-size: 12px; color: #909399; }

.discovery-card, .devices-card, .profiles-card { margin-bottom: 20px; }
.discovery-card .card-header, .devices-card .card-header, .profiles-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.discovery-card .discovery-controls, .devices-card .table-actions, .profiles-card .profile-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.live-view .video-container {
  text-align: center;
  .video-placeholder {
    background: #1a1a2e;
    min-height: 450px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    .video-placeholder-content {
      text-align: center;
      color: #666;
      .el-icon { font-size: 64px; margin-bottom: 16px; }
    }
    .video-frame { width: 100%; max-height: 450px; object-fit: contain; border-radius: 8px; }
  }
  .video-controls {
    margin-top: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;
    .ptz-controls {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      .ptz-middle { margin: 0 8px; display: inline-block; }
    }
    .zoom-controls { margin-top: 12px; display: flex; justify-content: center; gap: 8px; }
  }
}

.ptz-panel {
  .ptz-joystick { display: flex; justify-content: center; margin-bottom: 24px; }
  .joystick-pad {
    display: grid;
    grid-template-columns: repeat(3, 60px);
    grid-template-rows: repeat(3, 60px);
    gap: 4px;
    background: #f5f7fa;
    padding: 16px;
    border-radius: 16px;
    .joystick-cell { display: flex; align-items: center; justify-content: center; }
  }
  .ptz-zoom-section { margin-top: 16px; .zoom-control { margin-bottom: 16px; display: flex; align-items: center; gap: 16px; span { width: 50px; } .el-slider { flex: 1; } } .preset-controls { display: flex; align-items: center; gap: 16px; } }
}

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.device-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

.snapshot-container { text-align: center; .snapshot-image { max-width: 100%; border-radius: 8px; } .snapshot-info { margin-top: 16px; color: #909399; } }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>