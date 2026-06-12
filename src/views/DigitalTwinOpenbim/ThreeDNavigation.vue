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
        <div class="loading-tip">Digital Twin - 3D Navigation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="threed-navigation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>3D Navigation</h1>
        <p>Immersive navigation through the digital twin environment with interactive controls</p>
      </div>
      <div class="header-actions">
        <el-button-group>
          <el-button :type="navMode === 'orbit' ? 'primary' : 'default'" @click="navMode = 'orbit'" size="small">
            <el-icon><Expand /></el-icon>
            Orbit
          </el-button>
          <el-button :type="navMode === 'fly' ? 'primary' : 'default'" @click="navMode = 'fly'" size="small">
            <el-icon><Aim /></el-icon>
            Fly
          </el-button>
          <el-button :type="navMode === 'walk' ? 'primary' : 'default'" @click="navMode = 'walk'" size="small">
            <el-icon><User /></el-icon>
            Walk
          </el-button>
        </el-button-group>
        <el-button type="primary" @click="resetCamera">
          <el-icon><RefreshRight /></el-icon>
          Reset View
        </el-button>
        <el-button @click="toggleFullscreen">
          <el-icon><FullScreen /></el-icon>
          Fullscreen
        </el-button>
      </div>
    </div>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- 3D Viewer -->
      <el-col :xs="24" :lg="16">
        <div class="viewer-card">
          <div class="viewer-toolbar">
            <div class="toolbar-group">
              <el-tooltip content="Zoom In" placement="bottom">
                <el-button size="small" @click="zoomIn">
                  <el-icon><ZoomIn /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Zoom Out" placement="bottom">
                <el-button size="small" @click="zoomOut">
                  <el-icon><ZoomOut /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
            <div class="toolbar-group">
              <el-tooltip content="Rotate Left" placement="bottom">
                <el-button size="small" @click="rotateLeft">
                  <el-icon><RefreshLeft /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Rotate Right" placement="bottom">
                <el-button size="small" @click="rotateRight">
                  <el-icon><RefreshRight /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
            <div class="toolbar-group">
              <el-tooltip content="Pan Up" placement="bottom">
                <el-button size="small" @click="panUp">
                  <el-icon><ArrowUp /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Pan Down" placement="bottom">
                <el-button size="small" @click="panDown">
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Pan Left" placement="bottom">
                <el-button size="small" @click="panLeft">
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Pan Right" placement="bottom">
                <el-button size="small" @click="panRight">
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
            <div class="toolbar-group">
              <el-tooltip content="Toggle Grid" placement="bottom">
                <el-button size="small" @click="toggleGrid" :type="showGrid ? 'primary' : 'default'">
                  <el-icon><Grid /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Toggle Labels" placement="bottom">
                <el-button size="small" @click="toggleLabels" :type="showLabels ? 'primary' : 'default'">
                  <el-icon><Document /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Toggle Wireframe" placement="bottom">
                <el-button size="small" @click="toggleWireframe" :type="wireframeMode ? 'primary' : 'default'">
                  <el-icon><Grid /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
            <div class="toolbar-group">
              <el-tooltip content="First Person View" placement="bottom">
                <el-button size="small" @click="firstPersonView">
                  <el-icon><UserFilled /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="Top Down View" placement="bottom">
                <el-button size="small" @click="topDownView">
                  <el-icon><View /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
          <div class="viewer-container" ref="viewerContainerRef">
            <canvas ref="viewerCanvasRef" class="viewer-canvas"></canvas>
            <!-- Navigation Compass -->
            <div class="navigation-compass">
              <div class="compass-ring">
                <div class="compass-direction north" @click="rotateToNorth">N</div>
                <div class="compass-direction east" @click="rotateToEast">E</div>
                <div class="compass-direction south" @click="rotateToSouth">S</div>
                <div class="compass-direction west" @click="rotateToWest">W</div>
                <div class="compass-center" @click="resetCamera"></div>
              </div>
            </div>
            <!-- Minimap -->
            <div class="minimap">
              <canvas ref="minimapCanvasRef" class="minimap-canvas"></canvas>
              <div class="minimap-label">Floor Plan</div>
            </div>
            <!-- Info Panel -->
            <div class="info-panel">
              <div class="info-row">
                <span class="info-label">Position:</span>
                <span class="info-value">{{ formatPosition(cameraPosition) }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">Floor:</span>
                <span class="info-value">{{ currentFloorLabel }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">FPS:</span>
                <span class="info-value">{{ fps }} fps</span>
              </div>
            </div>
          </div>
          <div class="viewer-footer">
            <div class="floor-selector">
              <span>Floor:</span>
              <el-radio-group v-model="currentFloor" size="small" @change="onFloorChange">
                <el-radio-button value="ground">Ground</el-radio-button>
                <el-radio-button value="second">2nd</el-radio-button>
                <el-radio-button value="third">3rd</el-radio-button>
                <el-radio-button value="basement">Basement</el-radio-button>
              </el-radio-group>
            </div>
            <div class="navigation-instructions">
              <span><el-icon><Mouse /></el-icon> Drag to rotate</span>
              <span><el-icon><Pointer /></el-icon> Right-click to pan</span>
              <span><el-icon><ZoomIn /></el-icon> Scroll to zoom</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- Navigation Controls & Bookmarks -->
      <el-col :xs="24" :lg="8">
        <!-- Bookmarked Locations -->
        <div class="bookmarks-card">
          <div class="card-header">
            <h3>Saved Views</h3>
            <el-button size="small" type="primary" @click="addBookmark">
              <el-icon><Plus /></el-icon>
              Save Current View
            </el-button>
          </div>
          <div class="bookmarks-list">
            <div
                v-for="bookmark in bookmarks"
                :key="bookmark.id"
                class="bookmark-item"
                @click="gotoBookmark(bookmark)"
            >
              <div class="bookmark-icon" :style="{ backgroundColor: bookmark.color }">
                <el-icon><Location /></el-icon>
              </div>
              <div class="bookmark-info">
                <div class="bookmark-name">{{ bookmark.name }}</div>
                <div class="bookmark-location">{{ bookmark.location }}</div>
              </div>
              <el-button
                  link
                  type="danger"
                  size="small"
                  class="delete-btn"
                  @click.stop="deleteBookmark(bookmark)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <div v-if="bookmarks.length === 0" class="no-bookmarks">
              <el-empty description="No saved views" :image-size="80" />
              <p class="hint-text">Save your current view to quickly navigate back</p>
            </div>
          </div>
        </div>

        <!-- Scene Objects / Assets -->
        <div class="objects-card">
          <div class="card-header">
            <h3>Scene Objects</h3>
            <el-input
                v-model="objectSearch"
                placeholder="Search objects..."
                clearable
                size="small"
                :prefix-icon="Search"
                style="width: 160px"
            />
          </div>
          <div class="objects-list">
            <div
                v-for="obj in filteredObjects"
                :key="obj.id"
                class="object-item"
                :class="{ selected: selectedObject?.id === obj.id }"
                @click="focusOnObject(obj)"
            >
              <div class="object-icon" :class="getObjectIconClass(obj.category)">
                <el-icon><component :is="getObjectIcon(obj.category)" /></el-icon>
              </div>
              <div class="object-info">
                <div class="object-name">{{ obj.name }}</div>
                <div class="object-location">{{ obj.location }}</div>
              </div>
              <el-tooltip content="Navigate to" placement="left">
                <el-button link type="primary" size="small" @click.stop="flyToObject(obj)">
                  <el-icon><Aim /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
            <div v-if="filteredObjects.length === 0" class="no-objects">
              <span>No objects found</span>
            </div>
          </div>
        </div>

        <!-- Navigation History -->
        <div class="history-card">
          <div class="card-header">
            <h3>Navigation History</h3>
            <el-button size="small" @click="clearHistory" :disabled="history.length === 0">
              Clear
            </el-button>
          </div>
          <div class="history-list">
            <div
                v-for="(item, idx) in history.slice(0, 8)"
                :key="idx"
                class="history-item"
                @click="goToHistoryItem(item)"
            >
              <el-icon><Expand /></el-icon>
              <span>{{ item.name }}</span>
              <span class="history-time">{{ formatTime(item.timestamp) }}</span>
            </div>
            <div v-if="history.length === 0" class="no-history">
              <span>No navigation history</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Object Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.object?.name" width="500px">
      <div v-if="detailDialog.object" class="object-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Object ID">{{ detailDialog.object.id }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ detailDialog.object.category }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ detailDialog.object.location }}</el-descriptions-item>
          <el-descriptions-item label="Floor">{{ detailDialog.object.floor }}</el-descriptions-item>
          <el-descriptions-item label="Coordinates" :span="2">
            X: {{ detailDialog.object.position.x }}, Y: {{ detailDialog.object.position.y }}, Z: {{ detailDialog.object.position.z }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.object.description || 'No description available' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="flyToObject(detailDialog.object); detailDialog.visible = false">
          Navigate To
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Expand,
  Aim,
  User,
  FullScreen,
  ZoomIn,
  ZoomOut,
  RefreshLeft,
  RefreshRight,
  ArrowUp,
  ArrowDown,
  ArrowLeft,
  ArrowRight,
  Grid,
  Document,
  UserFilled,
  View,
  Mouse,
  Pointer,
  Plus,
  Location,
  Delete,
  Search,
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
  'Loading 3D environment...',
  'Building scene graph...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface SceneObject {
  id: string
  name: string
  category: 'HVAC' | 'Electrical' | 'Plumbing' | 'Fire' | 'Security' | 'Structure'
  location: string
  floor: string
  position: { x: number; y: number; z: number }
  description?: string
}

interface Bookmark {
  id: string
  name: string
  location: string
  position: { x: number; y: number; z: number }
  target: { x: number; y: number; z: number }
  color: string
}

interface HistoryItem {
  name: string
  position: { x: number; y: number; z: number }
  target: { x: number; y: number; z: number }
  timestamp: Date
}

// ==================== 模拟数据生成 ====================
const generateSceneObjects = (): SceneObject[] => {
  const categories = ['HVAC', 'Electrical', 'Plumbing', 'Fire', 'Security', 'Structure'] as const
  const locations = [
    'Main Equipment Room', 'Server Room A', 'Server Room B', 'Electrical Closet',
    'HVAC Mechanical Room', 'Plumbing Riser', 'Fire Pump Room', 'Security Control Room',
    'Data Hall', 'Battery Room', 'Generator Room', 'Cooling Tower', 'Chiller Plant'
  ]
  const floors = ['ground', 'second', 'third', 'basement']

  const objects: SceneObject[] = []

  // Generate building structure elements
  const structureObjects = [
    { name: 'Main Entrance', location: 'North Side', position: { x: 0, y: 12, z: 0 } },
    { name: 'Emergency Exit', location: 'East Side', position: { x: 15, y: 5, z: 0 } },
    { name: 'Stairwell A', location: 'North-East Corner', position: { x: 12, y: 12, z: 0 } },
    { name: 'Stairwell B', location: 'South-West Corner', position: { x: -12, y: -10, z: 0 } },
    { name: 'Elevator Bank', location: 'Central Core', position: { x: 0, y: 0, z: 0 } },
    { name: 'Loading Dock', location: 'West Side', position: { x: -18, y: 5, z: 0 } }
  ]

  structureObjects.forEach((obj, idx) => {
    objects.push({
      id: `STR-${String(idx + 1).padStart(3, '0')}`,
      name: obj.name,
      category: 'Structure',
      location: obj.location,
      floor: 'ground',
      position: obj.position,
      description: 'Building structural element'
    })
  })

  // Generate MEP assets
  for (let i = 1; i <= 40; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const floor = floors[Math.floor(Math.random() * floors.length)]
    const zOffset = floor === 'ground' ? 0 : floor === 'second' ? 3 : floor === 'third' ? 6 : -3

    objects.push({
      id: `${category.substring(0, 3).toUpperCase()}-${String(i).padStart(3, '0')}`,
      name: `${category} Asset ${i}`,
      category: category as any,
      location: locations[Math.floor(Math.random() * locations.length)],
      floor: floor,
      position: {
        x: (Math.random() - 0.5) * 30,
        y: (Math.random() - 0.5) * 24,
        z: zOffset + (Math.random() - 0.5) * 1.5
      },
      description: `${category} equipment installed in ${locations[Math.floor(Math.random() * locations.length)]}`
    })
  }

  return objects
}

const getRandomColor = () => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#9b59b6']
  return colors[Math.floor(Math.random() * colors.length)]
}

// ==================== 响应式状态 ====================
const sceneObjects = ref<SceneObject[]>([])
const bookmarks = ref<Bookmark[]>([])
const history = ref<HistoryItem[]>([])
const navMode = ref<'orbit' | 'fly' | 'walk'>('orbit')
const currentFloor = ref('ground')
const showGrid = ref(true)
const showLabels = ref(true)
const wireframeMode = ref(false)
const objectSearch = ref('')
const selectedObject = ref<SceneObject | null>(null)
const fps = ref(60)

const viewerCanvasRef = ref<HTMLCanvasElement | null>(null)
const minimapCanvasRef = ref<HTMLCanvasElement | null>(null)
const viewerContainerRef = ref<HTMLDivElement | null>(null)

let animationFrameId: number | null = null
let lastFrameTime = 0
let frameCount = 0

// Camera state
const cameraPosition = reactive({ x: 15, y: 15, z: 12 })
const cameraTarget = reactive({ x: 0, y: 0, z: 0 })
const cameraZoom = ref(1)

const detailDialog = reactive({
  visible: false,
  object: null as SceneObject | null
})

// ==================== 计算属性 ====================
const currentFloorLabel = computed(() => {
  const map: Record<string, string> = {
    'ground': 'Ground Floor',
    'second': 'Second Floor',
    'third': 'Third Floor',
    'basement': 'Basement'
  }
  return map[currentFloor.value] || currentFloor.value
})

const filteredObjects = computed(() => {
  let filtered = [...sceneObjects.value]

  if (objectSearch.value) {
    const searchLower = objectSearch.value.toLowerCase()
    filtered = filtered.filter(obj =>
        obj.name.toLowerCase().includes(searchLower) ||
        obj.id.toLowerCase().includes(searchLower) ||
        obj.location.toLowerCase().includes(searchLower)
    )
  }

  if (currentFloor.value) {
    filtered = filtered.filter(obj => obj.floor === currentFloor.value)
  }

  return filtered.slice(0, 30)
})

// ==================== 辅助函数 ====================
const formatPosition = (pos: { x: number; y: number; z: number }) => {
  return `(${pos.x.toFixed(1)}, ${pos.y.toFixed(1)}, ${pos.z.toFixed(1)})`
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

const getObjectIcon = (category: string) => {
  const map: Record<string, any> = {
    'HVAC': Tools,
    'Electrical': Connection,
    'Plumbing': Plus,
    'Fire': Warning,
    'Security': Lock,
    'Structure': House
  }
  return map[category] || House
}

const getObjectIconClass = (category: string) => {
  const map: Record<string, string> = {
    'HVAC': 'hvac',
    'Electrical': 'electrical',
    'Plumbing': 'plumbing',
    'Fire': 'fire',
    'Security': 'security',
    'Structure': 'structure'
  }
  return map[category] || 'structure'
}

// ==================== 3D 场景绘制 ====================
const draw3DScene = () => {
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 500
  canvas.width = width
  canvas.height = height

  // Clear canvas
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, '#1a1a2e')
  gradient.addColorStop(1, '#16213e')
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, width, height)

  // Calculate projection (simplified isometric-like projection)
  const centerX = width / 2
  const centerY = height / 2 - 50
  const scale = 8 * cameraZoom.value

  const project = (x: number, y: number, z: number) => {
    // Simple isometric projection with camera rotation
    const angle = rotationAngle
    const cos = Math.cos(angle)
    const sin = Math.sin(angle)
    const rx = x * cos - y * sin
    const ry = x * sin + y * cos
    const px = centerX + (rx - z * 0.5) * scale
    const py = centerY - (ry + z * 1.2) * scale + (cameraPosition.z - 8) * 5
    return { x: px, y: py }
  }

  // Draw grid floor if enabled
  if (showGrid.value) {
    ctx.strokeStyle = 'rgba(100, 150, 255, 0.3)'
    ctx.lineWidth = 1
    const gridSize = 2
    for (let i = -15; i <= 15; i += gridSize) {
      const p1 = project(i, -15, 0)
      const p2 = project(i, 15, 0)
      ctx.beginPath()
      ctx.moveTo(p1.x, p1.y)
      ctx.lineTo(p2.x, p2.y)
      ctx.stroke()

      const p3 = project(-15, i, 0)
      const p4 = project(15, i, 0)
      ctx.beginPath()
      ctx.moveTo(p3.x, p3.y)
      ctx.lineTo(p4.x, p4.y)
      ctx.stroke()
    }
  }

  // Draw room boundaries
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)'
  ctx.lineWidth = 2
  const rooms = [
    { name: 'Server Room', x1: -12, y1: -8, x2: -2, y2: 2 },
    { name: 'Electrical', x1: 2, y1: -8, x2: 12, y2: -2 },
    { name: 'HVAC', x1: -12, y1: 3, x2: -2, y2: 10 },
    { name: 'Plumbing', x1: 2, y1: 3, x2: 12, y2: 10 },
    { name: 'Security', x1: -8, y1: -12, x2: 0, y2: -8 }
  ]

  rooms.forEach(room => {
    const p1 = project(room.x1, room.y1, 0)
    const p2 = project(room.x2, room.y2, 0)
    ctx.strokeRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y)

    if (showLabels.value) {
      ctx.fillStyle = 'rgba(255, 255, 255, 0.4)'
      ctx.font = '10px Arial'
      const center = project((room.x1 + room.x2) / 2, (room.y1 + room.y2) / 2, 0)
      ctx.fillText(room.name, center.x - 20, center.y)
    }
  })

  // Draw objects
  const visibleObjects = filteredObjects.value
  visibleObjects.forEach(obj => {
    let color = '#409eff'
    if (obj.category === 'HVAC') color = '#e6a23c'
    else if (obj.category === 'Electrical') color = '#f56c6c'
    else if (obj.category === 'Plumbing') color = '#67c23a'
    else if (obj.category === 'Fire') color = '#f56c6c'
    else if (obj.category === 'Security') color = '#8c9aab'
    else if (obj.category === 'Structure') color = '#909399'

    const pos = project(obj.position.x, obj.position.y, obj.position.z)
    const isSelected = selectedObject.value?.id === obj.id
    const radius = isSelected ? 8 : 5

    // Draw glow for selected
    if (isSelected) {
      ctx.shadowBlur = 15
      ctx.shadowColor = '#409eff'
    }

    ctx.beginPath()
    ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2)
    ctx.fillStyle = color
    ctx.fill()
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 1.5
    ctx.stroke()

    ctx.shadowBlur = 0

    if (showLabels.value) {
      ctx.fillStyle = 'white'
      ctx.font = '10px Arial'
      ctx.fillText(obj.name.substring(0, 12), pos.x - 20, pos.y - 8)
    }
  })

  // Draw camera target indicator
  const targetPos = project(cameraTarget.x, cameraTarget.y, cameraTarget.z)
  ctx.beginPath()
  ctx.arc(targetPos.x, targetPos.y, 4, 0, Math.PI * 2)
  ctx.strokeStyle = '#ffaa00'
  ctx.lineWidth = 2
  ctx.stroke()

  // Update FPS counter
  frameCount++
  const now = performance.now()
  if (now - lastFrameTime >= 1000) {
    fps.value = frameCount
    frameCount = 0
    lastFrameTime = now
  }
}

// Draw minimap
const drawMinimap = () => {
  const canvas = minimapCanvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width = 150
  canvas.height = 150

  ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
  ctx.fillRect(0, 0, 150, 150)

  // Draw floor outline
  ctx.strokeStyle = 'rgba(100, 150, 255, 0.8)'
  ctx.lineWidth = 1
  ctx.strokeRect(15, 15, 120, 120)

  // Draw rooms on minimap
  ctx.fillStyle = 'rgba(64, 158, 255, 0.3)'
  ctx.fillRect(20, 20, 40, 40)
  ctx.fillStyle = 'rgba(230, 162, 60, 0.3)'
  ctx.fillRect(70, 20, 40, 30)
  ctx.fillStyle = 'rgba(103, 194, 58, 0.3)'
  ctx.fillRect(20, 70, 40, 40)
  ctx.fillStyle = 'rgba(245, 108, 108, 0.3)'
  ctx.fillRect(70, 70, 40, 40)

  // Draw camera position on minimap
  const mapX = 15 + (cameraPosition.x + 15) * 4
  const mapY = 15 + (cameraPosition.y + 12) * 4.8
  ctx.beginPath()
  ctx.arc(Math.min(Math.max(mapX, 20), 135), Math.min(Math.max(mapY, 20), 135), 4, 0, Math.PI * 2)
  ctx.fillStyle = '#ffaa00'
  ctx.fill()
}

// Rotation angle for camera
let rotationAngle = 0
let isDragging = false
let lastMouseX = 0
let lastMouseY = 0

// Mouse interaction handlers
const handleMouseDown = (e: MouseEvent) => {
  isDragging = true
  lastMouseX = e.clientX
  lastMouseY = e.clientY
  viewerCanvasRef.value?.setPointerCapture(e.pointerId)
}

const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging) return

  const deltaX = e.clientX - lastMouseX
  const deltaY = e.clientY - lastMouseY

  if (navMode.value === 'orbit') {
    rotationAngle += deltaX * 0.01
    cameraPosition.x += deltaX * 0.1
    cameraPosition.y -= deltaY * 0.1
  } else if (navMode.value === 'walk') {
    cameraPosition.x += deltaX * 0.05
    cameraPosition.y -= deltaY * 0.05
  }

  lastMouseX = e.clientX
  lastMouseY = e.clientY

  draw3DScene()
  drawMinimap()
}

const handleMouseUp = () => {
  isDragging = false
  viewerCanvasRef.value?.releasePointerCapture()
}

const handleWheel = (e: WheelEvent) => {
  cameraZoom.value = Math.max(0.5, Math.min(2, cameraZoom.value - e.deltaY * 0.005))
  draw3DScene()
  drawMinimap()
}

// ==================== 导航控制 ====================
const zoomIn = () => {
  cameraZoom.value = Math.min(2, cameraZoom.value + 0.1)
  draw3DScene()
}

const zoomOut = () => {
  cameraZoom.value = Math.max(0.5, cameraZoom.value - 0.1)
  draw3DScene()
}

const rotateLeft = () => {
  rotationAngle -= 0.1
  draw3DScene()
}

const rotateRight = () => {
  rotationAngle += 0.1
  draw3DScene()
}

const panUp = () => {
  cameraPosition.y += 1
  draw3DScene()
  drawMinimap()
}

const panDown = () => {
  cameraPosition.y -= 1
  draw3DScene()
  drawMinimap()
}

const panLeft = () => {
  cameraPosition.x -= 1
  draw3DScene()
  drawMinimap()
}

const panRight = () => {
  cameraPosition.x += 1
  draw3DScene()
  drawMinimap()
}

const resetCamera = () => {
  cameraPosition.x = 15
  cameraPosition.y = 15
  cameraPosition.z = 12
  cameraTarget.x = 0
  cameraTarget.y = 0
  cameraTarget.z = 0
  cameraZoom.value = 1
  rotationAngle = 0
  draw3DScene()
  drawMinimap()
  ElMessage.info('Camera view reset')
}

const rotateToNorth = () => {
  rotationAngle = 0
  draw3DScene()
}

const rotateToEast = () => {
  rotationAngle = Math.PI / 2
  draw3DScene()
}

const rotateToSouth = () => {
  rotationAngle = Math.PI
  draw3DScene()
}

const rotateToWest = () => {
  rotationAngle = -Math.PI / 2
  draw3DScene()
}

const firstPersonView = () => {
  navMode.value = 'walk'
  cameraPosition.z = 1.5
  cameraPosition.x = 0
  cameraPosition.y = -5
  draw3DScene()
  ElMessage.info('Switched to First Person View')
}

const topDownView = () => {
  cameraPosition.x = 0
  cameraPosition.y = 0
  cameraPosition.z = 20
  rotationAngle = 0
  draw3DScene()
  ElMessage.info('Switched to Top Down View')
}

const toggleGrid = () => {
  showGrid.value = !showGrid.value
  draw3DScene()
}

const toggleLabels = () => {
  showLabels.value = !showLabels.value
  draw3DScene()
}

const toggleWireframe = () => {
  wireframeMode.value = !wireframeMode.value
  draw3DScene()
}

const toggleFullscreen = () => {
  const container = viewerContainerRef.value
  if (container) {
    if (!document.fullscreenElement) {
      container.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }
}

const onFloorChange = () => {
  const floorHeights: Record<string, number> = {
    'basement': -3,
    'ground': 0,
    'second': 3,
    'third': 6
  }
  cameraPosition.z = floorHeights[currentFloor.value] + 8
  draw3DScene()
  drawMinimap()
  ElMessage.info(`Switched to ${currentFloorLabel.value}`)
}

const focusOnObject = (obj: SceneObject) => {
  selectedObject.value = obj
  cameraTarget.x = obj.position.x
  cameraTarget.y = obj.position.y
  cameraTarget.z = obj.position.z
  cameraPosition.x = obj.position.x + 5
  cameraPosition.y = obj.position.y + 5
  cameraPosition.z = obj.position.z + 3
  draw3DScene()
  drawMinimap()
}

const flyToObject = (obj: SceneObject) => {
  selectedObject.value = obj
  cameraTarget.x = obj.position.x
  cameraTarget.y = obj.position.y
  cameraTarget.z = obj.position.z
  cameraPosition.x = obj.position.x + 4
  cameraPosition.y = obj.position.y + 4
  cameraPosition.z = obj.position.z + 5
  draw3DScene()
  drawMinimap()
  ElMessage.success(`Navigating to ${obj.name}`)

  // Add to history
  history.value.unshift({
    name: obj.name,
    position: { ...cameraPosition },
    target: { ...cameraTarget },
    timestamp: new Date()
  })
  if (history.value.length > 20) history.value.pop()
}

const addBookmark = () => {
  const newBookmark: Bookmark = {
    id: `bm-${Date.now()}`,
    name: `View ${bookmarks.value.length + 1}`,
    location: currentFloorLabel.value,
    position: { ...cameraPosition },
    target: { ...cameraTarget },
    color: getRandomColor()
  }
  bookmarks.value.push(newBookmark)
  ElMessage.success('Current view saved to bookmarks')
}

const gotoBookmark = (bookmark: Bookmark) => {
  cameraPosition.x = bookmark.position.x
  cameraPosition.y = bookmark.position.y
  cameraPosition.z = bookmark.position.z
  cameraTarget.x = bookmark.target.x
  cameraTarget.y = bookmark.target.y
  cameraTarget.z = bookmark.target.z
  draw3DScene()
  drawMinimap()
  ElMessage.info(`Navigated to ${bookmark.name}`)
}

const deleteBookmark = (bookmark: Bookmark) => {
  const index = bookmarks.value.findIndex(b => b.id === bookmark.id)
  if (index !== -1) {
    bookmarks.value.splice(index, 1)
    ElMessage.success('Bookmark deleted')
  }
}

const goToHistoryItem = (item: HistoryItem) => {
  cameraPosition.x = item.position.x
  cameraPosition.y = item.position.y
  cameraPosition.z = item.position.z
  cameraTarget.x = item.target.x
  cameraTarget.y = item.target.y
  cameraTarget.z = item.target.z
  draw3DScene()
  drawMinimap()
}

const clearHistory = () => {
  history.value = []
  ElMessage.info('Navigation history cleared')
}

// ==================== 渲染循环 ====================
const startRenderLoop = () => {
  const render = () => {
    draw3DScene()
    drawMinimap()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

// ==================== 数据加载 ====================
const loadData = () => {
  sceneObjects.value = generateSceneObjects()

  // Add some default bookmarks
  bookmarks.value = [
    {
      id: 'bm-1',
      name: 'Server Room View',
      location: 'Ground Floor',
      position: { x: -5, y: -3, z: 10 },
      target: { x: -7, y: -3, z: 0 },
      color: '#409eff'
    },
    {
      id: 'bm-2',
      name: 'HVAC Overview',
      location: 'Ground Floor',
      position: { x: -8, y: 8, z: 12 },
      target: { x: -7, y: 6, z: 0 },
      color: '#e6a23c'
    },
    {
      id: 'bm-3',
      name: 'Data Center View',
      location: 'Second Floor',
      position: { x: 5, y: 5, z: 15 },
      target: { x: 3, y: 3, z: 3 },
      color: '#67c23a'
    }
  ]
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
      startRenderLoop()

      // Add event listeners
      const canvas = viewerCanvasRef.value
      if (canvas) {
        canvas.addEventListener('mousedown', handleMouseDown)
        canvas.addEventListener('mousemove', handleMouseMove)
        canvas.addEventListener('mouseup', handleMouseUp)
        canvas.addEventListener('wheel', handleWheel)
      }
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  const canvas = viewerCanvasRef.value
  if (canvas) {
    canvas.removeEventListener('mousedown', handleMouseDown)
    canvas.removeEventListener('mousemove', handleMouseMove)
    canvas.removeEventListener('mouseup', handleMouseUp)
    canvas.removeEventListener('wheel', handleWheel)
  }
})

watch([currentFloor, selectedObject], () => {
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
.threed-navigation-page {
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
  flex-wrap: wrap;
}

/* Viewer Card */
.viewer-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.viewer-toolbar {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #2c3e50;
  border-bottom: 1px solid #34495e;
  flex-wrap: wrap;
}

.toolbar-group {
  display: flex;
  gap: 4px;
  padding-right: 12px;
  border-right: 1px solid #445566;
}

.toolbar-group:last-child {
  border-right: none;
}

.viewer-container {
  position: relative;
  background-color: #1a1a2e;
}

.viewer-canvas {
  width: 100%;
  height: 500px;
  display: block;
  cursor: grab;
}

.viewer-canvas:active {
  cursor: grabbing;
}

/* Navigation Compass */
.navigation-compass {
  position: absolute;
  bottom: 80px;
  right: 20px;
  width: 100px;
  height: 100px;
}

.compass-ring {
  position: relative;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.compass-direction {
  position: absolute;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  color: white;
  transition: all 0.2s;
}

.compass-direction:hover {
  background: #409eff;
}

.north { top: -10px; left: 35px; }
.east { top: 35px; right: -10px; }
.south { bottom: -10px; left: 35px; }
.west { top: 35px; left: -10px; }

.compass-center {
  position: absolute;
  top: 35px;
  left: 35px;
  width: 30px;
  height: 30px;
  background: rgba(64, 158, 255, 0.8);
  border-radius: 50%;
  cursor: pointer;
}

/* Minimap */
.minimap {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 8px;
  padding: 8px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.minimap-canvas {
  width: 150px;
  height: 150px;
  border-radius: 4px;
}

.minimap-label {
  text-align: center;
  font-size: 10px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Info Panel */
.info-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 11px;
  color: white;
  font-family: monospace;
}

.info-row {
  margin-bottom: 4px;
}

.info-label {
  color: #8c9aab;
  margin-right: 8px;
}

.info-value {
  color: #409eff;
}

.viewer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #2c3e50;
  border-top: 1px solid #34495e;
}

.floor-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 13px;
}

.navigation-instructions {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #8c9aab;
}

.navigation-instructions .el-icon {
  font-size: 12px;
  margin-right: 4px;
}

/* Cards */
.bookmarks-card, .objects-card, .history-card {
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

/* Bookmarks List */
.bookmarks-list, .objects-list, .history-list {
  max-height: 280px;
  overflow-y: auto;
}

.bookmark-item, .history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.bookmark-item:hover, .history-item:hover {
  background-color: #f5f7fa;
}

.bookmark-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.bookmark-info {
  flex: 1;
}

.bookmark-name {
  font-weight: 600;
  font-size: 13px;
  color: #1f2f3d;
}

.bookmark-location {
  font-size: 11px;
  color: #8c9aab;
}

.delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.bookmark-item:hover .delete-btn {
  opacity: 1;
}

.no-bookmarks, .no-history {
  text-align: center;
  padding: 20px;
}

.hint-text {
  font-size: 12px;
  color: #8c9aab;
  margin-top: 8px;
}

/* Objects List */
.object-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.2s;
}

.object-item:hover {
  background-color: #f5f7fa;
}

.object-item.selected {
  background-color: #ecf5ff;
  border-left: 3px solid #409eff;
}

.object-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.object-icon.hvac { background-color: #fff3e0; color: #e6a23c; }
.object-icon.electrical { background-color: #fef0f0; color: #f56c6c; }
.object-icon.plumbing { background-color: #f0f9eb; color: #67c23a; }
.object-icon.fire { background-color: #fef0f0; color: #f56c6c; }
.object-icon.security { background-color: #f5f7fa; color: #8c9aab; }
.object-icon.structure { background-color: #ecf5ff; color: #409eff; }

.object-info {
  flex: 1;
}

.object-name {
  font-weight: 500;
  font-size: 13px;
  color: #1f2f3d;
}

.object-location {
  font-size: 10px;
  color: #8c9aab;
}

.no-objects {
  text-align: center;
  padding: 20px;
  color: #8c9aab;
}

/* History List */
.history-item {
  cursor: pointer;
}

.history-item .el-icon {
  color: #8c9aab;
}

.history-time {
  font-size: 10px;
  color: #c0c4cc;
  margin-left: auto;
}

/* Object Detail Dialog */
.object-detail {
  padding: 8px 0;
}

:deep(.el-radio-button__inner) {
  padding: 6px 14px;
}

:deep(.el-button-group .el-button) {
  padding: 8px 12px;
}
</style>