<template>
  <div class="digital-twin-container">
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
            <span class="loading-title">Loading Digital Twin</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Digital Twin Integration Platform</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="digital-twin-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Digital Twin Integration</h1>
          <p class="page-subtitle">Real-time 3D visualization and asset synchronization</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="importModel">
            <el-icon><Upload /></el-icon>
            Import Model
          </el-button>
          <el-button @click="syncData">
            <el-icon><Refresh /></el-icon>
            Sync Now
          </el-button>
          <el-button @click="exportSnapshot">
            <el-icon><Camera /></el-icon>
            Export Snapshot
          </el-button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="twin-layout">
        <!-- Left Sidebar - Asset Tree -->
        <div class="twin-sidebar">
          <div class="sidebar-header">
            <el-input v-model="assetSearch" placeholder="Search assets..." prefix-icon="Search" clearable />
          </div>
          <div class="asset-tree">
            <el-tree :data="assetTreeData" :props="treeProps" node-key="id" default-expand-all highlight-current
                     @current-change="onAssetSelect" :expand-on-click-node="false">
              <template #default="{ node, data }">
                <div class="tree-node">
                  <el-icon class="node-icon" :style="{ color: getAssetStatusColor(data.status) }">
                    <component :is="getAssetIcon(data.type)" />
                  </el-icon>
                  <span class="node-label">{{ data.name }}</span>
                  <el-tag v-if="data.status" :type="getStatusTagType(data.status)" size="small" class="node-tag">
                    {{ data.status }}
                  </el-tag>
                </div>
              </template>
            </el-tree>
          </div>
        </div>

        <!-- Center - 3D Viewer -->
        <div class="twin-viewer">
          <div class="viewer-toolbar">
            <div class="toolbar-left">
              <el-button-group>
                <el-button size="small" @click="resetCamera">
                  <el-icon><RefreshLeft /></el-icon>
                  Reset
                </el-button>
                <el-button size="small" @click="toggleAutoRotate">
                  <el-icon><VideoCamera /></el-icon>
                  {{ autoRotate ? 'Stop' : 'Auto Rotate' }}
                </el-button>
                <el-button size="small" @click="toggleFullscreen">
                  <el-icon><FullScreen /></el-icon>
                  Fullscreen
                </el-button>
              </el-button-group>
            </div>
            <div class="toolbar-right">
              <el-select v-model="viewMode" size="small" style="width: 120px">
                <el-option label="3D View" value="3d" />
                <el-option label="Top View" value="top" />
                <el-option label="Side View" value="side" />
                <el-option label="Walkthrough" value="walk" />
              </el-select>
              <el-slider v-model="zoomLevel" :min="50" :max="200" size="small" style="width: 120px; margin-left: 12px" />
            </div>
          </div>
          <div ref="viewerContainer" class="viewer-container">
            <canvas ref="canvasRef" class="viewer-canvas"></canvas>
            <!-- Overlay Info Panel -->
            <div v-if="selectedAsset" class="asset-info-panel">
              <div class="panel-header">
                <span class="panel-title">{{ selectedAsset.name }}</span>
                <el-button link @click="selectedAsset = null">
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              <div class="panel-content">
                <div class="info-row">
                  <span class="label">Type:</span>
                  <span class="value">{{ selectedAsset.type }}</span>
                </div>
                <div class="info-row">
                  <span class="label">Status:</span>
                  <el-tag :type="getStatusTagType(selectedAsset.status)" size="small">{{ selectedAsset.status }}</el-tag>
                </div>
                <div class="info-row">
                  <span class="label">Temperature:</span>
                  <span class="value" :style="{ color: getTempColor(selectedAsset.temperature) }">
                    {{ selectedAsset.temperature }}°C
                  </span>
                </div>
                <div class="info-row">
                  <span class="label">Humidity:</span>
                  <span class="value">{{ selectedAsset.humidity }}%</span>
                </div>
                <div class="info-row">
                  <span class="label">Power:</span>
                  <span class="value">{{ selectedAsset.power }} kW</span>
                </div>
                <div class="info-row">
                  <span class="label">Last Sync:</span>
                  <span class="value">{{ selectedAsset.lastSync }}</span>
                </div>
              </div>
              <div class="panel-actions">
                <el-button size="small" @click="locateAsset(selectedAsset)">Locate</el-button>
                <el-button size="small" type="primary" @click="viewAssetDetails(selectedAsset)">Details</el-button>
              </div>
            </div>
            <!-- Sync Indicator -->
            <div class="sync-indicator" :class="{ syncing: isSyncing }">
              <el-icon><Connection /></el-icon>
              <span>{{ isSyncing ? 'Syncing...' : 'Connected' }}</span>
            </div>
          </div>
        </div>

        <!-- Right Sidebar - Real-time Data -->
        <div class="twin-sidebar-right">
          <el-tabs v-model="activeTab" class="data-tabs">
            <el-tab-pane label="Real-time Metrics" name="metrics">
              <div class="metrics-list">
                <div class="metric-item" v-for="metric in realtimeMetrics" :key="metric.name">
                  <div class="metric-header">
                    <span class="metric-name">{{ metric.name }}</span>
                    <el-icon :style="{ color: metric.trend === 'up' ? '#f59e0b' : '#10b981' }">
                      <CaretTop v-if="metric.trend === 'up'" />
                      <CaretBottom v-else />
                    </el-icon>
                  </div>
                  <div class="metric-value">{{ metric.value }}{{ metric.unit }}</div>
                  <div class="metric-change">{{ metric.change }}% vs last hour</div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Alert Timeline" name="alerts">
              <div class="alert-list">
                <div v-for="alert in recentAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
                  <div class="alert-icon">
                    <el-icon><WarningFilled /></el-icon>
                  </div>
                  <div class="alert-content">
                    <div class="alert-title">{{ alert.title }}</div>
                    <div class="alert-time">{{ alert.time }}</div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Twin Analytics" name="analytics">
              <div ref="analyticsChartRef" class="analytics-chart"></div>
              <div class="analytics-stats">
                <div class="stat">
                  <span class="stat-label">Model Accuracy</span>
                  <span class="stat-value">98.5%</span>
                </div>
                <div class="stat">
                  <span class="stat-label">Sync Latency</span>
                  <span class="stat-value">{{ syncLatency }}ms</span>
                </div>
                <div class="stat">
                  <span class="stat-label">Active Devices</span>
                  <span class="stat-value">{{ activeDevices }}/{{ totalDevices }}</span>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>

      <!-- BIM Integration Section -->
      <div class="bim-section">
        <div class="section-header">
          <h3>BIM Model Integration</h3>
          <el-button type="primary" link @click="manageModels">
            Manage Models <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
        <div class="bim-models">
          <div v-for="model in bimModels" :key="model.id" class="bim-card" @click="loadBimModel(model)">
            <div class="bim-preview" :style="{ backgroundImage: `url(${model.preview})` }">
              <div class="bim-overlay">
                <el-icon><View /></el-icon>
              </div>
            </div>
            <div class="bim-info">
              <span class="bim-name">{{ model.name }}</span>
              <span class="bim-version">{{ model.version }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Sync Status Bar -->
      <div class="sync-status-bar">
        <div class="status-left">
          <el-icon><Connection /></el-icon>
          <span>Digital Twin Active</span>
          <el-divider direction="vertical" />
          <span>Last Sync: {{ lastSyncTime }}</span>
        </div>
        <div class="status-right">
          <span :class="{ 'status-warning': syncDrift > 100 }">
            Sync Drift: {{ syncDrift }}ms
          </span>
        </div>
      </div>
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAssetDetail?.name" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Asset ID">{{ selectedAssetDetail?.id }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedAssetDetail?.type }}</el-descriptions-item>
        <el-descriptions-item label="Manufacturer">{{ selectedAssetDetail?.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="Model">{{ selectedAssetDetail?.model }}</el-descriptions-item>
        <el-descriptions-item label="Installation Date">{{ selectedAssetDetail?.installDate }}</el-descriptions-item>
        <el-descriptions-item label="Warranty Status">
          <el-tag :type="selectedAssetDetail?.warrantyStatus === 'active' ? 'success' : 'danger'">
            {{ selectedAssetDetail?.warrantyStatus }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Temperature">
          <span :style="{ color: getTempColor(selectedAssetDetail?.temperature) }">
            {{ selectedAssetDetail?.temperature }}°C
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Humidity">{{ selectedAssetDetail?.humidity }}%</el-descriptions-item>
        <el-descriptions-item label="Power Consumption">{{ selectedAssetDetail?.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Energy Efficiency">{{ selectedAssetDetail?.efficiency }}%</el-descriptions-item>
        <el-descriptions-item label="Maintenance History" :span="2">
          <ul>
            <li v-for="record in selectedAssetDetail?.maintenanceHistory" :key="record.date">
              {{ record.date }}: {{ record.action }}
            </li>
          </ul>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="locateAsset(selectedAssetDetail)">Locate in 3D</el-button>
      </template>
    </el-dialog>

    <!-- Import Model Dialog -->
    <el-dialog v-model="importDialogVisible" title="Import BIM Model" width="500px">
      <el-upload drag multiple :auto-upload="false" :on-change="handleFileChange" accept=".ifc,.rvt,.dwg,.gltf">
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">Drop IFC/RVT/DWG/GLTF file here or <em>click to upload</em></div>
        <template #tip>
          <div class="el-upload__tip">Supported formats: IFC, RVT, DWG, GLTF (Max 500MB)</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="uploadModel">Import</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Upload, Refresh, Camera, Search, RefreshLeft, VideoCamera, FullScreen,
  Close, Connection, WarningFilled, CaretTop, CaretBottom, ArrowRight,
  View, UploadFilled, Cpu, Monitor, SetUp, Grid, DataLine
} from '@element-plus/icons-vue'

// ==================== 3D Rendering Setup ====================
let scene: any = null
let camera: any = null
let renderer: any = null
let controls: any = null
let animationId: number | null = null

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing 3D engine...')

// ==================== Reactive Data ====================
const assetSearch = ref('')
const viewMode = ref('3d')
const zoomLevel = ref(100)
const autoRotate = ref(false)
const activeTab = ref('metrics')
const selectedAsset = ref<any>(null)
const isSyncing = ref(false)
const syncLatency = ref(45)
const syncDrift = ref(32)
const lastSyncTime = ref('2024-01-15 14:32:25')
const activeDevices = ref(156)
const totalDevices = ref(168)
const detailDialogVisible = ref(false)
const importDialogVisible = ref(false)
const selectedAssetDetail = ref<any>(null)
const viewerContainer = ref<HTMLElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const analyticsChartRef = ref<HTMLElement | null>(null)

// Asset Tree Data
const assetTreeData = ref([
  {
    id: 1,
    name: 'Data Center East',
    type: 'building',
    children: [
      {
        id: 11,
        name: 'Floor 1',
        type: 'floor',
        children: [
          { id: 111, name: 'CRAC-01', type: 'crac', status: 'active', temperature: 22.5, humidity: 48, power: 12.3, lastSync: '2024-01-15 14:32:20' },
          { id: 112, name: 'CRAC-02', type: 'crac', status: 'active', temperature: 23.1, humidity: 47, power: 11.8, lastSync: '2024-01-15 14:32:22' },
          { id: 113, name: 'PDU-01', type: 'pdu', status: 'active', temperature: 28.5, humidity: 45, power: 45.2, lastSync: '2024-01-15 14:32:18' },
          { id: 114, name: 'Server Rack A01', type: 'rack', status: 'active', temperature: 24.2, humidity: 46, power: 8.5, lastSync: '2024-01-15 14:32:15' },
        ]
      },
      {
        id: 12,
        name: 'Floor 2',
        type: 'floor',
        children: [
          { id: 121, name: 'UPS-01', type: 'ups', status: 'active', temperature: 26.0, humidity: 44, power: 78.5, lastSync: '2024-01-15 14:32:10' },
          { id: 122, name: 'UPS-02', type: 'ups', status: 'maintenance', temperature: 27.3, humidity: 43, power: 65.2, lastSync: '2024-01-15 14:32:12' },
          { id: 123, name: 'Chiller-01', type: 'chiller', status: 'warning', temperature: 18.5, humidity: 52, power: 95.0, lastSync: '2024-01-15 14:32:08' },
        ]
      }
    ]
  },
  {
    id: 2,
    name: 'Data Center West',
    type: 'building',
    children: [
      {
        id: 21,
        name: 'Floor 1',
        type: 'floor',
        children: [
          { id: 211, name: 'CRAC-03', type: 'crac', status: 'active', temperature: 22.8, humidity: 49, power: 13.1, lastSync: '2024-01-15 14:32:05' },
          { id: 212, name: 'Server Rack B01', type: 'rack', status: 'active', temperature: 23.9, humidity: 47, power: 9.2, lastSync: '2024-01-15 14:32:02' },
        ]
      }
    ]
  }
])

const treeProps = { children: 'children', label: 'name' }

// Real-time Metrics
const realtimeMetrics = ref([
  { name: 'Total Power', value: 342.8, unit: 'kW', change: '+5.2', trend: 'up' },
  { name: 'PUE', value: 1.42, unit: '', change: '-0.03', trend: 'down' },
  { name: 'Avg Temperature', value: 24.2, unit: '°C', change: '+0.5', trend: 'up' },
  { name: 'Cooling Efficiency', value: 87.3, unit: '%', change: '+2.1', trend: 'up' },
])

// Recent Alerts
const recentAlerts = ref([
  { id: 1, title: 'Chiller-01 temperature spike detected', severity: 'warning', time: '2 min ago' },
  { id: 2, title: 'UPS-01 battery health degraded', severity: 'critical', time: '15 min ago' },
  { id: 3, title: 'CRAC-03 fan speed abnormal', severity: 'info', time: '1 hour ago' },
  { id: 4, title: 'Network latency spike', severity: 'warning', time: '2 hours ago' },
])

// BIM Models
const bimModels = ref([
  { id: 1, name: 'Data Center East', version: 'v2.3.0', preview: 'https://via.placeholder.com/200x120/3b82f6/white?text=DC+East' },
  { id: 2, name: 'Data Center West', version: 'v1.8.2', preview: 'https://via.placeholder.com/200x120/10b981/white?text=DC+West' },
  { id: 3, name: 'Cooling Plant', version: 'v3.1.0', preview: 'https://via.placeholder.com/200x120/f59e0b/white?text=Cooling+Plant' },
  { id: 4, name: 'UPS Room', version: 'v1.2.5', preview: 'https://via.placeholder.com/200x120/8b5cf6/white?text=UPS+Room' },
])

// Helper Functions
const getAssetIcon = (type: string) => {
  const icons: Record<string, any> = {
    building: Grid,
    floor: Monitor,
    crac: SetUp,
    pdu: Connection,
    rack: Cpu,
    ups: DataLine,
    chiller: SetUp
  }
  return icons[type] || Cpu
}

const getAssetStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    active: '#10b981',
    maintenance: '#f59e0b',
    warning: '#ef4444',
    critical: '#dc2626'
  }
  return colors[status] || '#6b7280'
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    active: 'success',
    maintenance: 'warning',
    warning: 'danger',
    critical: 'danger'
  }
  return types[status] || 'info'
}

const getTempColor = (temp: number) => {
  if (temp < 22) return '#10b981'
  if (temp < 26) return '#3b82f6'
  if (temp < 30) return '#f59e0b'
  return '#ef4444'
}

// Actions
const importModel = () => {
  importDialogVisible.value = true
}

const syncData = () => {
  isSyncing.value = true
  setTimeout(() => {
    isSyncing.value = false
    lastSyncTime.value = new Date().toLocaleString()
    ElMessage.success('Data synchronized successfully')
  }, 2000)
}

const exportSnapshot = () => {
  if (canvasRef.value) {
    const link = document.createElement('a')
    link.download = 'digital-twin-snapshot.png'
    link.href = canvasRef.value.toDataURL()
    link.click()
    ElMessage.success('Snapshot exported')
  }
}

const resetCamera = () => {
  if (controls) {
    controls.target.set(0, 0, 0)
    controls.update()
  }
  ElMessage.info('Camera reset')
}

const toggleAutoRotate = () => {
  autoRotate.value = !autoRotate.value
  if (controls) {
    controls.autoRotate = autoRotate.value
    controls.update()
  }
}

const toggleFullscreen = () => {
  const elem = viewerContainer.value
  if (!elem) return
  if (!document.fullscreenElement) {
    elem.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const onAssetSelect = (data: any) => {
  if (data && data.temperature !== undefined) {
    selectedAsset.value = data
  } else {
    selectedAsset.value = null
  }
}

const locateAsset = (asset: any) => {
  if (controls) {
    // Simulate camera movement to asset location
    controls.target.set(Math.random() * 10 - 5, Math.random() * 5, Math.random() * 10 - 5)
    controls.update()
    ElMessage.success(`Locating ${asset.name}...`)
  }
}

const viewAssetDetails = (asset: any) => {
  selectedAssetDetail.value = {
    ...asset,
    manufacturer: 'Schneider Electric',
    model: 'Smart Asset v2',
    installDate: '2022-03-15',
    warrantyStatus: 'active',
    efficiency: 92,
    maintenanceHistory: [
      { date: '2024-01-10', action: 'Quarterly inspection completed' },
      { date: '2023-10-05', action: 'Firmware update v2.3.1' },
      { date: '2023-07-12', action: 'Filter replacement' },
    ]
  }
  detailDialogVisible.value = true
}

const manageModels = () => {
  ElMessage.info('Model management interface will open')
}

const loadBimModel = (model: any) => {
  ElMessage.success(`Loading ${model.name} model...`)
}

const handleFileChange = (file: any) => {
  console.log('File selected:', file)
}

const uploadModel = () => {
  ElMessage.success('Model import started')
  importDialogVisible.value = false
}

// Initialize 3D Scene
const init3D = async () => {
  await nextTick()
  if (!canvasRef.value || !viewerContainer.value) return

  const container = viewerContainer.value
  const width = container.clientWidth
  const height = container.clientHeight

  // Dynamically import Three.js
  const THREE = await import('three')
  const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js')

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0a0e27)
  scene.fog = new THREE.FogExp2(0x0a0e27, 0.002)

  // Camera
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(15, 12, 20)
  camera.lookAt(0, 0, 0)

  // Renderer
  renderer = new THREE.WebGLRenderer({ canvas: canvasRef.value, antialias: true })
  renderer.setSize(width, height)
  renderer.setPixelRatio(window.devicePixelRatio)
  renderer.shadowMap.enabled = true

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.autoRotate = false
  controls.enableZoom = true
  controls.zoomSpeed = 1.2
  controls.enablePan = true
  controls.panSpeed = 0.8
  controls.target.set(0, 0, 0)

  // Lighting
  // Ambient light
  const ambientLight = new THREE.AmbientLight(0x404060)
  scene.add(ambientLight)

  // Directional light
  const dirLight = new THREE.DirectionalLight(0xffffff, 1)
  dirLight.position.set(5, 10, 7)
  dirLight.castShadow = true
  dirLight.receiveShadow = true
  scene.add(dirLight)

  // Fill light
  const fillLight = new THREE.PointLight(0x4466cc, 0.3)
  fillLight.position.set(-2, 3, 4)
  scene.add(fillLight)

  // Back light
  const backLight = new THREE.PointLight(0xffaa66, 0.2)
  backLight.position.set(0, 2, -5)
  scene.add(backLight)

  // Grid helper
  const gridHelper = new THREE.GridHelper(30, 20, 0x3b82f6, 0x2d3748)
  gridHelper.position.y = -2
  scene.add(gridHelper)

  // Create building structure
  // Floor base
  const floorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.3, metalness: 0.1 })
  const floorBase = new THREE.Mesh(new THREE.BoxGeometry(12, 0.2, 10), floorMat)
  floorBase.position.set(0, -1.5, 0)
  floorBase.receiveShadow = true
  scene.add(floorBase)

  // Glass walls
  const glassMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, roughness: 0.1, metalness: 0.8, transparent: true, opacity: 0.3 })
  const walls = [
    { pos: [0, 0.5, -5.2], size: [12, 4, 0.1] },
    { pos: [0, 0.5, 5.2], size: [12, 4, 0.1] },
    { pos: [-6.2, 0.5, 0], size: [0.1, 4, 10] },
    { pos: [6.2, 0.5, 0], size: [0.1, 4, 10] }
  ]
  walls.forEach(wall => {
    const wallMesh = new THREE.Mesh(new THREE.BoxGeometry(wall.size[0], wall.size[1], wall.size[2]), glassMat)
    wallMesh.position.set(wall.pos[0], wall.pos[1], wall.pos[2])
    scene.add(wallMesh)
  })

  // Roof
  const roofMat = new THREE.MeshStandardMaterial({ color: 0x2d3748, roughness: 0.5, metalness: 0.3 })
  const roof = new THREE.Mesh(new THREE.BoxGeometry(12.5, 0.2, 10.5), roofMat)
  roof.position.set(0, 2.2, 0)
  scene.add(roof)

  // CRAC units (blue cubes)
  const cracMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, emissive: 0x1e3a8a, emissiveIntensity: 0.2 })
  const cracPositions = [[-3, -0.5, -3], [3, -0.5, -3], [-3, -0.5, 3], [3, -0.5, 3]]
  cracPositions.forEach(pos => {
    const crac = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.5, 1.2), cracMat)
    crac.position.set(pos[0], pos[1], pos[2])
    crac.castShadow = true
    scene.add(crac)
  })

  // Server racks (silver)
  const rackMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.7, roughness: 0.3 })
  const rackPositions = [[-1, -0.8, -1], [1, -0.8, -1], [-1, -0.8, 1], [1, -0.8, 1], [0, -0.8, 0]]
  rackPositions.forEach(pos => {
    const rack = new THREE.Mesh(new THREE.BoxGeometry(0.8, 2, 1), rackMat)
    rack.position.set(pos[0], pos[1], pos[2])
    rack.castShadow = true
    scene.add(rack)
  })

  // UPS units (orange)
  const upsMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0x78350f, emissiveIntensity: 0.1 })
  const ups = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.8, 1), upsMat)
  ups.position.set(-2, -0.2, 2)
  ups.castShadow = true
  scene.add(ups)

  const ups2 = new THREE.Mesh(new THREE.BoxGeometry(1.5, 1.8, 1), upsMat)
  ups2.position.set(2, -0.2, 2)
  ups2.castShadow = true
  scene.add(ups2)

  // Floating particles for visual effect
  const particleCount = 500
  const particlesGeometry = new THREE.BufferGeometry()
  const particlePositions = new Float32Array(particleCount * 3)
  for (let i = 0; i < particleCount; i++) {
    particlePositions[i * 3] = (Math.random() - 0.5) * 30
    particlePositions[i * 3 + 1] = (Math.random() - 0.5) * 8
    particlePositions[i * 3 + 2] = (Math.random() - 0.5) * 25
  }
  particlesGeometry.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3))
  const particleMat = new THREE.PointsMaterial({ color: 0x3b82f6, size: 0.05, transparent: true, opacity: 0.5 })
  const particles = new THREE.Points(particlesGeometry, particleMat)
  scene.add(particles)

  // Animation loop
  const animate = () => {
    if (autoRotate.value && controls) {
      controls.update()
    }
    if (renderer && scene && camera) {
      renderer.render(scene, camera)
    }
    animationId = requestAnimationFrame(animate)
  }
  animate()

  // Handle resize
  const handleResize = () => {
    if (!container || !camera || !renderer) return
    const newWidth = container.clientWidth
    const newHeight = container.clientHeight
    camera.aspect = newWidth / newHeight
    camera.updateProjectionMatrix()
    renderer.setSize(newWidth, newHeight)
  }
  window.addEventListener('resize', handleResize)

  return () => {
    window.removeEventListener('resize', handleResize)
  }
}

// Initialize Analytics Chart
let analyticsChart: echarts.ECharts | null = null

const initAnalyticsChart = () => {
  if (!analyticsChartRef.value) return
  analyticsChart = echarts.init(analyticsChartRef.value)
  analyticsChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value', name: 'Sync Accuracy (%)' },
    series: [{
      type: 'line', data: [98.2, 98.5, 98.8, 98.3, 98.9, 99.1, 98.7],
      smooth: true, lineStyle: { color: '#3b82f6', width: 2 },
      areaStyle: { opacity: 0.1, color: '#3b82f6' },
      symbol: 'circle', symbolSize: 6
    }]
  })
}

// Loading Simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Watch for view mode changes
watch(viewMode, (mode) => {
  if (!camera) return
  switch (mode) {
    case 'top':
      camera.position.set(0, 20, 0)
      controls.target.set(0, 0, 0)
      break
    case 'side':
      camera.position.set(20, 0, 0)
      controls.target.set(0, 0, 0)
      break
    case 'walk':
      camera.position.set(5, 1.6, 5)
      controls.target.set(0, 1.6, 0)
      break
    default:
      camera.position.set(15, 12, 20)
      controls.target.set(0, 0, 0)
  }
  controls.update()
})

watch(zoomLevel, (level) => {
  if (camera) {
    const distance = 20 * (200 / level) / 2
    const direction = new THREE.Vector3().subVectors(camera.position, controls.target).normalize()
    camera.position.copy(controls.target.clone().add(direction.multiplyScalar(distance)))
    controls.update()
  }
})

// Simulate real-time data updates
let dataInterval: ReturnType<typeof setInterval> | null = null

const startDataSimulation = () => {
  dataInterval = setInterval(() => {
    // Update random metrics
    realtimeMetrics.value[0].value = +(Math.random() * 50 + 320).toFixed(1)
    realtimeMetrics.value[1].value = +(Math.random() * 0.2 + 1.35).toFixed(2)
    realtimeMetrics.value[2].value = +(Math.random() * 4 + 22).toFixed(1)
    realtimeMetrics.value[3].value = +(Math.random() * 10 + 82).toFixed(1)

    // Random sync latency
    syncLatency.value = Math.floor(Math.random() * 30 + 35)
    syncDrift.value = Math.floor(Math.random() * 50 + 15)

    // Update selected asset data if any
    if (selectedAsset.value) {
      const asset = selectedAsset.value
      asset.temperature = +(asset.temperature + (Math.random() - 0.5) * 0.3).toFixed(1)
      asset.humidity = Math.floor(asset.humidity + (Math.random() - 0.5) * 2)
      asset.power = +(asset.power + (Math.random() - 0.5) * 0.5).toFixed(1)
    }
  }, 3000)
}

onMounted(async () => {
  const interval = startLoading()
  setTimeout(async () => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(async () => {
      isLoaded.value = true
      await nextTick()
      setTimeout(async () => {
        await init3D()
        initAnalyticsChart()
        startDataSimulation()
      }, 200)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  if (dataInterval) clearInterval(dataInterval)
  if (analyticsChart) analyticsChart.dispose()
  if (renderer) renderer.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.digital-twin-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

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
}

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 320px;
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

/* ==================== Main Content ==================== */
.digital-twin-main {
  padding: 24px 32px;
  min-height: 100vh;
  color: #e2e8f0;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Twin Layout */
.twin-layout {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  min-height: 600px;
}

/* Left Sidebar */
.twin-sidebar {
  width: 280px;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid rgba(71, 85, 105, 0.3);
}

.asset-tree {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 6px 0;
}

.node-icon {
  font-size: 16px;
}

.node-label {
  flex: 1;
  font-size: 13px;
}

.node-tag {
  transform: scale(0.9);
}

/* Center Viewer */
.twin-viewer {
  flex: 1;
  background: #0a0e27;
  border-radius: 20px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.viewer-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(71, 85, 105, 0.3);
}

.viewer-container {
  flex: 1;
  position: relative;
}

.viewer-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

.asset-info-panel {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 260px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 16px;
  border: 1px solid rgba(59, 130, 246, 0.3);
  overflow: hidden;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.2);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
}

.panel-title {
  font-weight: 600;
  font-size: 14px;
}

.panel-content {
  padding: 12px 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px solid rgba(71, 85, 105, 0.2);
}

.info-row .label {
  color: #94a3b8;
}

.info-row .value {
  color: #f1f5f9;
  font-weight: 500;
}

.panel-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid rgba(71, 85, 105, 0.2);
}

.sync-indicator {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: rgba(16, 185, 129, 0.9);
  border-radius: 20px;
  font-size: 12px;
  color: white;
}

.sync-indicator.syncing {
  background: rgba(245, 158, 11, 0.9);
  animation: pulse 1s infinite;
}

/* Right Sidebar */
.twin-sidebar-right {
  width: 300px;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.data-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.data-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 12px 16px 0;
  background: rgba(15, 23, 42, 0.5);
}

.data-tabs :deep(.el-tabs__content) {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.metrics-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item {
  padding: 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 12px;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.metric-name {
  font-size: 13px;
  color: #94a3b8;
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  color: #f1f5f9;
}

.metric-change {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.5);
}

.alert-item.warning { border-left: 3px solid #f59e0b; }
.alert-item.critical { border-left: 3px solid #ef4444; }
.alert-item.info { border-left: 3px solid #3b82f6; }

.alert-icon {
  font-size: 18px;
}
.alert-item.warning .alert-icon { color: #f59e0b; }
.alert-item.critical .alert-icon { color: #ef4444; }
.alert-item.info .alert-icon { color: #3b82f6; }

.alert-title {
  font-size: 13px;
  font-weight: 500;
}

.alert-time {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.analytics-chart {
  height: 200px;
  margin-bottom: 16px;
}

.analytics-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(71, 85, 105, 0.3);
}

.stat {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
}

.stat-label {
  font-size: 13px;
  color: #94a3b8;
}

.stat-value {
  font-size: 13px;
  font-weight: 600;
  color: #3b82f6;
}

/* BIM Section */
.bim-section {
  background: rgba(30, 41, 59, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
}

.bim-models {
  display: flex;
  gap: 16px;
  overflow-x: auto;
}

.bim-card {
  flex-shrink: 0;
  width: 160px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.bim-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.bim-preview {
  height: 90px;
  background-size: cover;
  background-position: center;
  position: relative;
  background-color: #1e293b;
}

.bim-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  transition: opacity 0.2s;
}

.bim-card:hover .bim-overlay {
  opacity: 1;
}

.bim-overlay .el-icon {
  font-size: 24px;
  color: white;
}

.bim-info {
  padding: 8px 12px;
}

.bim-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
}

.bim-version {
  display: block;
  font-size: 11px;
  color: #64748b;
}

/* Sync Status Bar */
.sync-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  font-size: 13px;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-warning {
  color: #f59e0b;
}

/* Element Plus Overrides */
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}

:deep(.el-tree) {
  background: transparent;
  color: #e2e8f0;
}

:deep(.el-tree-node__content:hover) {
  background: rgba(59, 130, 246, 0.1);
}

:deep(.el-tree-node.is-current > .el-tree-node__content) {
  background: rgba(59, 130, 246, 0.2);
}

:deep(.el-tabs__item) {
  color: #94a3b8;
}

:deep(.el-tabs__item.is-active) {
  color: #3b82f6;
}

:deep(.el-tabs__active-bar) {
  background: #3b82f6;
}

:deep(.el-input__wrapper) {
  background: rgba(15, 23, 42, 0.6);
  box-shadow: none;
  border: 1px solid rgba(71, 85, 105, 0.3);
}

:deep(.el-input__inner) {
  color: #e2e8f0;
}

:deep(.el-slider__runway) {
  background: rgba(71, 85, 105, 0.3);
}

:deep(.el-slider__bar) {
  background: #3b82f6;
}

:deep(.el-dialog) {
  background: #1e293b;
}

:deep(.el-dialog__title) {
  color: #f1f5f9;
}

:deep(.el-descriptions__label) {
  background: #0f172a;
  color: #94a3b8;
}

:deep(.el-descriptions__content) {
  background: #1e293b;
  color: #f1f5f9;
}

/* Responsive */
@media (max-width: 1200px) {
  .digital-twin-main { padding: 16px; }
  .twin-layout { flex-direction: column; }
  .twin-sidebar, .twin-sidebar-right { width: 100%; }
  .twin-viewer { min-height: 400px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .viewer-toolbar { flex-direction: column; gap: 12px; align-items: stretch; }
  .toolbar-left, .toolbar-right { justify-content: center; }
}
</style>