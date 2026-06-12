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
        <div class="loading-tip">Digital Twin - Asset Localization</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-localization-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Asset Localization</h1>
        <p>Locate and track assets within the digital twin environment with real-time positioning</p>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button :type="viewMode === '3d' ? 'primary' : 'default'" @click="viewMode = '3d'">
            <el-icon><Grid /></el-icon>
            3D View
          </el-button>
          <el-button :type="viewMode === '2d' ? 'primary' : 'default'" @click="viewMode = '2d'">
            <el-icon><Location /></el-icon>
            2D Map
          </el-button>
        </el-button-group>
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button @click="exportAssetData">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalAssets }}</div>
            <div class="stat-label">Total Assets</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><Location /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.localizedAssets }}</div>
            <div class="stat-label">Localized</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.recentlyUpdated }}</div>
            <div class="stat-label">Recently Updated</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.localizationAccuracy }}%</div>
            <div class="stat-label">Accuracy</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content: 3D Viewer + Asset List -->
    <el-row :gutter="20">
      <!-- 3D/2D Visualization Area -->
      <el-col :xs="24" :lg="16">
        <div class="viewer-card">
          <div class="card-header">
            <h3>{{ viewMode === '3d' ? '3D Digital Twin Viewer' : '2D Floor Plan Viewer' }}</h3>
            <div class="viewer-controls">
              <el-select v-model="currentFloor" placeholder="Select Floor" size="small" style="width: 140px">
                <el-option label="Ground Floor" value="ground" />
                <el-option label="Second Floor" value="second" />
                <el-option label="Third Floor" value="third" />
                <el-option label="Basement" value="basement" />
              </el-select>
              <el-button size="small" @click="resetView">
                <el-icon><RefreshRight /></el-icon>
                Reset View
              </el-button>
              <el-button size="small" @click="toggleWireframe" v-if="viewMode === '3d'">
                <el-icon><Grid /></el-icon>
                Wireframe
              </el-button>
            </div>
          </div>
          <div class="viewer-container" ref="viewerContainerRef">
            <canvas ref="viewerCanvasRef" class="viewer-canvas"></canvas>
            <!-- Tooltip for selected asset -->
            <div v-if="selectedAsset && hoverPosition" class="asset-tooltip" :style="tooltipStyle">
              <div class="tooltip-header">
                <strong>{{ selectedAsset.name }}</strong>
                <el-button link @click="selectedAsset = null">✕</el-button>
              </div>
              <div>Type: {{ selectedAsset.type }}</div>
              <div>Location: {{ selectedAsset.location }}</div>
              <div>Status:
                <el-tag :type="getStatusTagType(selectedAsset.status)" size="small">
                  {{ selectedAsset.status }}
                </el-tag>
              </div>
              <div>Last Updated: {{ formatTime(selectedAsset.lastUpdated) }}</div>
              <el-button size="small" type="primary" style="margin-top: 8px" @click="focusOnAsset(selectedAsset)">
                Center on Asset
              </el-button>
            </div>
          </div>
          <div class="viewer-footer">
            <div class="coordinates">
              <span>X: {{ cameraPosition.x.toFixed(2) }}</span>
              <span>Y: {{ cameraPosition.y.toFixed(2) }}</span>
              <span>Z: {{ cameraPosition.z.toFixed(2) }}</span>
            </div>
            <div class="viewer-legend">
              <span><span class="legend-dot hvac"></span> HVAC</span>
              <span><span class="legend-dot electrical"></span> Electrical</span>
              <span><span class="legend-dot plumbing"></span> Plumbing</span>
              <span><span class="legend-dot fire"></span> Fire Safety</span>
              <span><span class="legend-dot security"></span> Security</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Asset List Sidebar -->
      <el-col :xs="24" :lg="8">
        <div class="asset-list-card">
          <div class="card-header">
            <h3>Assets</h3>
            <div class="search-input">
              <el-input
                  v-model="assetSearch"
                  placeholder="Search assets..."
                  clearable
                  size="small"
                  :prefix-icon="Search"
              />
            </div>
          </div>
          <div class="filter-tabs">
            <el-radio-group v-model="assetTypeFilter" size="small">
              <el-radio-button label="">All</el-radio-button>
              <el-radio-button label="HVAC">HVAC</el-radio-button>
              <el-radio-button label="Electrical">Electrical</el-radio-button>
              <el-radio-button label="Plumbing">Plumbing</el-radio-button>
              <el-radio-button label="Fire">Fire</el-radio-button>
              <el-radio-button label="Security">Security</el-radio-button>
            </el-radio-group>
          </div>
          <div class="asset-list">
            <div
                v-for="asset in filteredAssets"
                :key="asset.id"
                class="asset-item"
                :class="{ selected: selectedAsset?.id === asset.id }"
                @click="selectAsset(asset)"
            >
              <div class="asset-icon" :class="getAssetIconClass(asset.type)">
                <el-icon><component :is="getAssetIcon(asset.type)" /></el-icon>
              </div>
              <div class="asset-info">
                <div class="asset-name">{{ asset.name }}</div>
                <div class="asset-location">{{ asset.location }}</div>
                <div class="asset-meta">
                  <el-tag :type="getStatusTagType(asset.status)" size="small">
                    {{ asset.status }}
                  </el-tag>
                  <span class="asset-id">{{ asset.id }}</span>
                </div>
              </div>
              <el-button
                  link
                  type="primary"
                  size="small"
                  class="locate-btn"
                  @click.stop="focusOnAsset(asset)"
              >
                <el-icon><View /></el-icon>
              </el-button>
            </div>
            <div v-if="filteredAssets.length === 0" class="no-assets">
              <el-empty description="No assets found" :image-size="80" />
            </div>
          </div>
          <div class="asset-list-footer">
            <span>{{ filteredAssets.length }} assets displayed</span>
            <el-button link size="small" @click="exportAssetData">
              Export All
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.asset?.name" width="550px">
      <div v-if="detailDialog.asset" class="asset-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Asset ID">{{ detailDialog.asset.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ detailDialog.asset.type }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ detailDialog.asset.location }}</el-descriptions-item>
          <el-descriptions-item label="Floor">{{ detailDialog.asset.floor }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.asset.status)">{{ detailDialog.asset.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Localization Accuracy">{{ detailDialog.asset.accuracy }}%</el-descriptions-item>
          <el-descriptions-item label="Coordinates" :span="2">
            X: {{ detailDialog.asset.position.x }}, Y: {{ detailDialog.asset.position.y }}, Z: {{ detailDialog.asset.position.z }}
          </el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ detailDialog.asset.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ formatTime(detailDialog.asset.lastUpdated) }}</el-descriptions-item>
          <el-descriptions-item label="Model ID">{{ detailDialog.asset.modelId || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="IFC GUID" :span="2" class="ifc-guid">{{ detailDialog.asset.ifcGuid || 'N/A' }}</el-descriptions-item>
        </el-descriptions>
        <div class="detail-actions">
          <el-button type="primary" @click="focusOnAsset(detailDialog.asset); detailDialog.visible = false">
            Locate in Viewer
          </el-button>
          <el-button @click="exportAsset(detailDialog.asset)">
            Export Asset Data
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  Download,
  OfficeBuilding,
  Location,
  Clock,
  DataAnalysis,
  Grid,
  RefreshRight,
  Search,
  View,
  Tools,
  Connection,
  Warning,
  Lock,
  House
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading BIM model...',
  'Indexing assets...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface Asset {
  id: string
  name: string
  type: 'HVAC' | 'Electrical' | 'Plumbing' | 'Fire' | 'Security'
  location: string
  floor: string
  status: 'Operational' | 'Maintenance' | 'Offline' | 'Alert'
  accuracy: number
  position: { x: number; y: number; z: number }
  installationDate: string
  lastUpdated: Date
  modelId?: string
  ifcGuid?: string
  description?: string
}

// ==================== 模拟数据生成 ====================
const generateMockAssets = (): Asset[] => {
  const assetTypes = ['HVAC', 'Electrical', 'Plumbing', 'Fire', 'Security'] as const
  const locations = [
    'Main Equipment Room', 'Server Room A', 'Server Room B', 'Electrical Closet 1',
    'Electrical Closet 2', 'HVAC Mechanical Room', 'Plumbing Riser', 'Fire Pump Room',
    'Security Control Room', 'Data Hall', 'Battery Room', 'Generator Room'
  ]
  const floors = ['ground', 'second', 'third', 'basement']
  const statuses: ('Operational' | 'Maintenance' | 'Offline' | 'Alert')[] =
      ['Operational', 'Operational', 'Operational', 'Operational', 'Maintenance', 'Offline', 'Alert']

  const assets: Asset[] = []

  for (let i = 1; i <= 64; i++) {
    const type = assetTypes[Math.floor(Math.random() * assetTypes.length)]
    const floor = floors[Math.floor(Math.random() * floors.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    const accuracy = status === 'Operational' ? 92 + Math.random() * 7 : 70 + Math.random() * 20

    assets.push({
      id: `AST-${String(i).padStart(4, '0')}`,
      name: `${type} Asset ${i}`,
      type: type,
      location: locations[Math.floor(Math.random() * locations.length)],
      floor: floor,
      status: status,
      accuracy: Math.floor(accuracy),
      position: {
        x: (Math.random() - 0.5) * 30,
        y: (Math.random() - 0.5) * 20,
        z: floor === 'ground' ? 0 : floor === 'second' ? 3 : floor === 'third' ? 6 : -3
      },
      installationDate: `202${Math.floor(Math.random() * 3)}-${String(Math.floor(Math.random() * 12) + 1).padStart(2, '0')}-${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}`,
      lastUpdated: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000),
      modelId: `MOD-${Math.floor(Math.random() * 1000)}`,
      ifcGuid: Math.random().toString(36).substring(2, 15).toUpperCase()
    })
  }

  return assets
}

// ==================== 响应式状态 ====================
const allAssets = ref<Asset[]>([])
const viewMode = ref<'3d' | '2d'>('3d')
const currentFloor = ref('ground')
const assetSearch = ref('')
const assetTypeFilter = ref('')
const selectedAsset = ref<Asset | null>(null)
const hoverPosition = ref(false)
const tooltipStyle = ref({})
const wireframeMode = ref(false)

const viewerCanvasRef = ref<HTMLCanvasElement | null>(null)
const viewerContainerRef = ref<HTMLDivElement | null>(null)

let animationFrameId: number | null = null
let rotationAngle = 0

const cameraPosition = reactive({ x: 10, y: 10, z: 8 })

const stats = reactive({
  totalAssets: 0,
  localizedAssets: 0,
  recentlyUpdated: 0,
  localizationAccuracy: 94
})

const detailDialog = reactive({
  visible: false,
  asset: null as Asset | null
})

// ==================== 计算属性 ====================
const filteredAssets = computed(() => {
  let filtered = [...allAssets.value]

  if (assetSearch.value) {
    const searchLower = assetSearch.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(searchLower) ||
        a.id.toLowerCase().includes(searchLower) ||
        a.location.toLowerCase().includes(searchLower)
    )
  }

  if (assetTypeFilter.value) {
    filtered = filtered.filter(a => a.type === assetTypeFilter.value)
  }

  if (currentFloor.value) {
    filtered = filtered.filter(a => a.floor === currentFloor.value)
  }

  return filtered
})

// ==================== 辅助函数 ====================
const formatTime = (date: Date) => {
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'Operational': 'success',
    'Maintenance': 'warning',
    'Offline': 'info',
    'Alert': 'danger'
  }
  return map[status] || 'info'
}

const getAssetIcon = (type: string) => {
  const map: Record<string, any> = {
    'HVAC': Tools,
    'Electrical': Connection,
    'Plumbing': Warning,
    'Fire': Warning,
    'Security': Lock
  }
  return map[type] || House
}

const getAssetIconClass = (type: string) => {
  const map: Record<string, string> = {
    'HVAC': 'hvac',
    'Electrical': 'electrical',
    'Plumbing': 'plumbing',
    'Fire': 'fire',
    'Security': 'security'
  }
  return map[type] || 'hvac'
}

const updateStats = () => {
  stats.totalAssets = allAssets.value.length
  stats.localizedAssets = allAssets.value.filter(a => a.accuracy > 85).length
  const sevenDaysAgo = new Date()
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
  stats.recentlyUpdated = allAssets.value.filter(a => a.lastUpdated >= sevenDaysAgo).length
  const avgAccuracy = allAssets.value.reduce((sum, a) => sum + a.accuracy, 0) / allAssets.value.length
  stats.localizationAccuracy = Math.floor(avgAccuracy)
}

// ==================== 3D 场景绘制 ====================
const draw3DScene = () => {
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 400
  canvas.width = width
  canvas.height = height

  // Clear canvas
  ctx.fillStyle = '#1a1a2e'
  ctx.fillRect(0, 0, width, height)

  // Draw grid floor
  ctx.strokeStyle = 'rgba(100, 150, 255, 0.3)'
  ctx.lineWidth = 1
  const gridSize = 30
  const offsetX = width / 2
  const offsetY = height / 2 + 50

  for (let i = -10; i <= 10; i++) {
    ctx.beginPath()
    ctx.moveTo(offsetX + i * gridSize, offsetY - 100)
    ctx.lineTo(offsetX + i * gridSize, offsetY + 100)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(offsetX - 100, offsetY + i * gridSize)
    ctx.lineTo(offsetX + 100, offsetY + i * gridSize)
    ctx.stroke()
  }

  // Draw walls / room boundaries
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 2
  ctx.strokeRect(offsetX - 90, offsetY - 90, 180, 180)

  // Draw room labels
  ctx.fillStyle = 'rgba(255, 255, 255, 0.5)'
  ctx.font = '10px Arial'
  ctx.fillText('Server Room', offsetX - 85, offsetY - 75)
  ctx.fillText('Electrical', offsetX + 20, offsetY - 75)
  ctx.fillText('HVAC', offsetX - 85, offsetY + 40)
  ctx.fillText('Plumbing', offsetX + 30, offsetY + 40)

  // Draw assets as colored circles
  const filtered = filteredAssets.value.slice(0, 30)
  filtered.forEach(asset => {
    // Project 3D position to 2D (simplified)
    const x = offsetX + asset.position.x * 3
    const y = offsetY - asset.position.z * 2 - asset.position.y * 2

    // Skip if off canvas
    if (x < 0 || x > width || y < 0 || y > height) return

    // Color based on asset type
    let color = '#409eff'
    if (asset.type === 'HVAC') color = '#e6a23c'
    else if (asset.type === 'Electrical') color = '#f56c6c'
    else if (asset.type === 'Plumbing') color = '#67c23a'
    else if (asset.type === 'Fire') color = '#f56c6c'
    else if (asset.type === 'Security') color = '#8c9aab'

    // Highlight selected asset
    const isSelected = selectedAsset.value?.id === asset.id
    const radius = isSelected ? 10 : 7

    // Draw glow for selected
    if (isSelected) {
      ctx.shadowBlur = 15
      ctx.shadowColor = '#409eff'
    }

    ctx.beginPath()
    ctx.arc(x, y, radius, 0, Math.PI * 2)
    ctx.fillStyle = color
    ctx.fill()
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 2
    ctx.stroke()

    // Reset shadow
    ctx.shadowBlur = 0

    // Draw label
    ctx.fillStyle = 'white'
    ctx.font = '10px Arial'
    ctx.fillText(asset.name.substring(0, 10), x - 15, y - 8)

    // Draw pulsing effect for alert status
    if (asset.status === 'Alert') {
      ctx.beginPath()
      ctx.arc(x, y, radius + 5, 0, Math.PI * 2)
      ctx.strokeStyle = '#f56c6c'
      ctx.lineWidth = 2
      ctx.stroke()
    }
  })

  // Draw selected asset details
  if (selectedAsset.value) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
    ctx.fillRect(width - 220, 10, 210, 100)
    ctx.fillStyle = 'white'
    ctx.font = 'bold 12px Arial'
    ctx.fillText(selectedAsset.value.name, width - 210, 30)
    ctx.font = '10px Arial'
    ctx.fillText(`Type: ${selectedAsset.value.type}`, width - 210, 50)
    ctx.fillText(`Location: ${selectedAsset.value.location}`, width - 210, 65)
    ctx.fillText(`Status: ${selectedAsset.value.status}`, width - 210, 80)
    ctx.fillText(`Accuracy: ${selectedAsset.value.accuracy}%`, width - 210, 95)
  }
}

const start3DRenderLoop = () => {
  const render = () => {
    draw3DScene()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

const resetView = () => {
  cameraPosition.x = 10
  cameraPosition.y = 10
  cameraPosition.z = 8
  rotationAngle = 0
  draw3DScene()
  ElMessage.info('View reset to default position')
}

const toggleWireframe = () => {
  wireframeMode.value = !wireframeMode.value
  ElMessage.info(wireframeMode.value ? 'Wireframe mode enabled' : 'Wireframe mode disabled')
}

// ==================== 交互事件 ====================
const selectAsset = (asset: Asset) => {
  selectedAsset.value = asset
  // Calculate tooltip position (simulated)
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (canvas && container) {
    const offsetX = container.clientWidth / 2 + asset.position.x * 3
    const offsetY = 200 - asset.position.z * 2 - asset.position.y * 2
    tooltipStyle.value = {
      left: `${offsetX}px`,
      top: `${offsetY - 60}px`,
      position: 'absolute'
    }
    hoverPosition.value = true
    setTimeout(() => {
      hoverPosition.value = false
    }, 3000)
  }
  ElMessage.success(`Selected: ${asset.name}`)
}

const focusOnAsset = (asset: Asset) => {
  selectedAsset.value = asset
  // Simulate camera focus on asset
  ElMessage.success(`Camera focused on ${asset.name}`)
  draw3DScene()
}

const viewAssetDetails = (asset: Asset) => {
  detailDialog.asset = asset
  detailDialog.visible = true
}

const exportAsset = (asset: Asset) => {
  const data = JSON.stringify(asset, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `asset-${asset.id}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(`Exported ${asset.name}`)
}

const exportAssetData = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    assets: filteredAssets.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `asset-localization-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Asset data exported')
}

const refreshData = () => {
  allAssets.value = generateMockAssets()
  updateStats()
  draw3DScene()
  ElMessage.success('Data refreshed')
}

// ==================== 数据加载 ====================
const loadData = () => {
  allAssets.value = generateMockAssets()
  updateStats()

  nextTick(() => {
    start3DRenderLoop()
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  window.removeEventListener('resize', () => {
    draw3DScene()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      draw3DScene()
    })
  }
})

watch([viewMode, currentFloor, assetTypeFilter, assetSearch, selectedAsset], () => {
  draw3DScene()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
  animation-delay: 0.4s;
  width: 40%;
  height: 40%;
  top: 30%;
  left: 30%;
}

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

.loading-dots {
  display: inline-flex;
  gap: 2px;
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

/* ==================== Main Content Styles ==================== */
.asset-localization-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Viewer Card */
.viewer-card, .asset-list-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.viewer-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.viewer-container {
  position: relative;
  background-color: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
}

.viewer-canvas {
  width: 100%;
  height: 400px;
  display: block;
}

.asset-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  z-index: 100;
  min-width: 180px;
  pointer-events: none;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.viewer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.coordinates {
  display: flex;
  gap: 16px;
  font-family: monospace;
  font-size: 12px;
  color: #8c9aab;
}

.viewer-legend {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #8c9aab;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
}

.legend-dot.hvac { background-color: #e6a23c; }
.legend-dot.electrical { background-color: #f56c6c; }
.legend-dot.plumbing { background-color: #67c23a; }
.legend-dot.fire { background-color: #f56c6c; }
.legend-dot.security { background-color: #8c9aab; }

/* Asset List */
.search-input {
  width: 180px;
}

.filter-tabs {
  margin-bottom: 16px;
  overflow-x: auto;
  white-space: nowrap;
}

.asset-list {
  max-height: 420px;
  overflow-y: auto;
}

.asset-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.asset-item:hover {
  background-color: #f5f7fa;
}

.asset-item.selected {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.asset-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.asset-icon.hvac { background-color: #fff3e0; color: #e6a23c; }
.asset-icon.electrical { background-color: #fef0f0; color: #f56c6c; }
.asset-icon.plumbing { background-color: #f0f9eb; color: #67c23a; }
.asset-icon.fire { background-color: #fef0f0; color: #f56c6c; }
.asset-icon.security { background-color: #f5f7fa; color: #8c9aab; }

.asset-info {
  flex: 1;
}

.asset-name {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.asset-location {
  font-size: 11px;
  color: #8c9aab;
  margin-bottom: 4px;
}

.asset-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.asset-id {
  font-size: 10px;
  color: #c0c4cc;
  font-family: monospace;
}

.locate-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.asset-item:hover .locate-btn {
  opacity: 1;
}

.asset-list-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
  color: #8c9aab;
}

.no-assets {
  padding: 40px 0;
}

/* Asset Detail */
.asset-detail {
  padding: 8px 0;
}

.ifc-guid {
  font-family: monospace;
  font-size: 11px;
}

.detail-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-radio-button__inner) {
  padding: 6px 14px;
}
</style>