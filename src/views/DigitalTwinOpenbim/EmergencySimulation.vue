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
        <div class="loading-tip">Digital Twin - Emergency Simulation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="emergency-simulation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Emergency Simulation</h1>
        <p>Simulate emergency scenarios to optimize evacuation routes and response strategies</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runSimulation" :loading="isSimulating">
          <el-icon><VideoPlay /></el-icon>
          Run Simulation
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="resetSimulation">
          <el-icon><RefreshLeft /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><WarningFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEvacuated }}</div>
            <div class="stat-label">Total Evacuated</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgEvacTime }}<span class="stat-unit">min</span></div>
            <div class="stat-label">Avg Evacuation Time</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.evacuationRate }}%</div>
            <div class="stat-label">Evacuation Rate</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.responseTime }}<span class="stat-unit">s</span></div>
            <div class="stat-label">Response Time</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Simulation Configuration -->
      <el-col :xs="24" :lg="8">
        <div class="config-card">
          <div class="card-header">
            <h3>Emergency Configuration</h3>
            <el-tag :type="simulationStatus === 'running' ? 'warning' : simulationStatus === 'completed' ? 'success' : 'info'">
              {{ simulationStatus === 'idle' ? 'Ready' : simulationStatus === 'running' ? 'Simulating...' : 'Completed' }}
            </el-tag>
          </div>

          <!-- Emergency Type Selection -->
          <div class="config-section">
            <label>Emergency Type</label>
            <div class="emergency-types">
              <div
                  v-for="type in emergencyTypes"
                  :key="type.id"
                  class="emergency-type-card"
                  :class="{ active: selectedEmergencyType === type.id, [type.id]: true }"
                  @click="selectedEmergencyType = type.id"
              >
                <el-icon><component :is="type.icon" /></el-icon>
                <span>{{ type.name }}</span>
              </div>
            </div>
          </div>

          <el-divider />

          <!-- Simulation Parameters -->
          <el-form label-width="120px" class="param-form">
            <el-form-item label="Fire Location">
              <el-select v-model="params.fireLocation" placeholder="Select location" style="width: 100%">
                <el-option label="Server Room A" value="server_a" />
                <el-option label="Server Room B" value="server_b" />
                <el-option label="Electrical Room" value="electrical" />
                <el-option label="Data Hall" value="data_hall" />
                <el-option label="Battery Room" value="battery" />
              </el-select>
            </el-form-item>

            <el-form-item label="Fire Severity">
              <el-slider v-model="params.fireSeverity" :min="1" :max="5" :step="1" />
              <span class="param-hint">{{ getSeverityLabel(params.fireSeverity) }}</span>
            </el-form-item>

            <el-form-item label="Smoke Density">
              <el-slider v-model="params.smokeDensity" :min="0" :max="100" :step="5" />
              <span class="param-hint">{{ params.smokeDensity }}%</span>
            </el-form-item>

            <el-form-item label="Occupancy">
              <el-slider v-model="params.occupancy" :min="0" :max="100" :step="5" />
              <span class="param-hint">{{ params.occupancy }}% of capacity</span>
            </el-form-item>

            <el-form-item label="Evacuation Speed">
              <el-slider v-model="params.evacuationSpeed" :min="0.5" :max="2" :step="0.1" />
              <span class="param-hint">{{ params.evacuationSpeed }}x normal</span>
            </el-form-item>

            <el-form-item label="Staff Training Level">
              <el-select v-model="params.trainingLevel" style="width: 100%">
                <el-option label="Basic" value="basic" />
                <el-option label="Intermediate" value="intermediate" />
                <el-option label="Advanced" value="advanced" />
                <el-option label="Expert" value="expert" />
              </el-select>
            </el-form-item>
          </el-form>

          <el-divider />

          <div class="run-section">
            <el-button type="primary" size="large" @click="runSimulation" :loading="isSimulating" style="width: 100%">
              <el-icon><VideoPlay /></el-icon>
              Start Emergency Simulation
            </el-button>
            <el-progress v-if="isSimulating" :percentage="simProgress" :status="simProgress === 100 ? 'success' : undefined" style="margin-top: 12px" />
          </div>
        </div>
      </el-col>

      <!-- Simulation Visualization -->
      <el-col :xs="24" :lg="16">
        <div class="visualization-card">
          <div class="card-header">
            <h3>Building Evacuation Simulation</h3>
            <div class="view-controls">
              <el-radio-group v-model="viewMode" size="small">
                <el-radio-button value="floorplan">Floor Plan</el-radio-button>
                <el-radio-button value="heatmap">Heat Map</el-radio-button>
                <el-radio-button value="evacuation">Evacuation Path</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="resetView">
                <el-icon><RefreshRight /></el-icon>
                Reset
              </el-button>
            </div>
          </div>

          <div class="viewer-container" ref="viewerContainerRef">
            <canvas ref="viewerCanvasRef" class="viewer-canvas"></canvas>
            <div v-if="isSimulating" class="simulation-overlay">
              <div class="simulation-status">
                <el-icon class="is-loading"><Loading /></el-icon>
                Simulating Emergency Scenario...
              </div>
            </div>
            <div v-if="simulationStatus === 'completed'" class="results-overlay">
              <div class="results-summary">
                <div class="result-item">
                  <span class="result-label">Total Evacuated:</span>
                  <span class="result-value">{{ simulationResults.totalEvacuated }}</span>
                </div>
                <div class="result-item">
                  <span class="result-label">Evacuation Time:</span>
                  <span class="result-value">{{ simulationResults.evacuationTime }} min</span>
                </div>
                <div class="result-item">
                  <span class="result-label">Casualties:</span>
                  <span class="result-value" :class="simulationResults.casualties > 0 ? 'danger' : 'success'">
                    {{ simulationResults.casualties }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="viewer-footer">
            <div class="legend">
              <span><span class="legend-dot exit"></span> Exit</span>
              <span><span class="legend-dot fire"></span> Fire Source</span>
              <span><span class="legend-dot safe"></span> Safe Zone</span>
              <span><span class="legend-dot crowd"></span> Crowd Density</span>
            </div>
            <div class="simulation-time" v-if="isSimulating || simulationStatus === 'completed'">
              Time: {{ simTime }}:{{ simSeconds.toString().padStart(2, '0') }}
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Evacuation Analysis -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <div class="analysis-card">
          <div class="card-header">
            <h3>Evacuation Path Analysis</h3>
          </div>
          <div ref="pathChartRef" class="path-chart"></div>
          <div class="path-recommendations">
            <div v-for="rec in pathRecommendations" :key="rec.id" class="rec-item">
              <el-icon :class="rec.type"><Check /></el-icon>
              <span>{{ rec.message }}</span>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :lg="12">
        <div class="analysis-card">
          <div class="card-header">
            <h3>Evacuation Timeline</h3>
          </div>
          <div ref="timelineChartRef" class="timeline-chart"></div>
          <div class="timeline-stats">
            <div class="stat">
              <span class="stat-label">Critical Point:</span>
              <span class="stat-value">{{ criticalPoint }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Max Congestion:</span>
              <span class="stat-value">{{ maxCongestion }} people/min</span>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Evacuation Routes Table -->
    <div class="routes-card">
      <div class="card-header">
        <h3>Recommended Evacuation Routes</h3>
        <el-button size="small" @click="exportRoutes">
          <el-icon><Download /></el-icon>
          Export Routes
        </el-button>
      </div>
      <el-table :data="evacuationRoutes" stripe style="width: 100%">
        <el-table-column prop="name" label="Route Name" min-width="150" />
        <el-table-column prop="from" label="Starting Point" width="150" />
        <el-table-column prop="to" label="Destination" width="120" />
        <el-table-column prop="distance" label="Distance (m)" width="100" />
        <el-table-column prop="time" label="Est. Time (min)" width="120" />
        <el-table-column prop="capacity" label="Capacity (ppl/min)" width="130" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Recommended' ? 'success' : row.status === 'Alternative' ? 'warning' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewRouteOnMap(row)">
              View
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Historical Simulations -->
    <div class="history-card">
      <div class="card-header">
        <h3>Simulation History</h3>
        <el-button size="small" @click="clearHistory">Clear History</el-button>
      </div>
      <el-table :data="simulationHistory" stripe size="small">
        <el-table-column prop="timestamp" label="Date & Time" width="180">
          <template #default="{ row }">
            {{ formatTimestamp(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="emergencyType" label="Emergency Type" width="120" />
        <el-table-column prop="evacuationTime" label="Evac Time (min)" width="120" />
        <el-table-column prop="totalEvacuated" label="Evacuated" width="100" />
        <el-table-column prop="casualties" label="Casualties" width="100" />
        <el-table-column prop="effectiveness" label="Effectiveness" width="120">
          <template #default="{ row }">
            <el-progress :percentage="row.effectiveness" :stroke-width="6" :show-text="false" />
            <span>{{ row.effectiveness }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="replaySimulation(row)">
              Replay
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="simulationHistory.length === 0" class="no-history">
        <el-empty description="No simulation history" :image-size="80" />
      </div>
    </div>

    <!-- Export Dialog -->
    <el-dialog v-model="exportDialog.visible" title="Export Simulation Report" width="500px">
      <el-form>
        <el-form-item label="Report Format">
          <el-radio-group v-model="exportFormat">
            <el-radio label="pdf">PDF Report</el-radio>
            <el-radio label="excel">Excel Data</el-radio>
            <el-radio label="json">JSON Export</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Include">
          <el-checkbox-group v-model="exportIncludes">
            <el-checkbox label="floorplan">Floor Plan</el-checkbox>
            <el-checkbox label="evacuationPaths">Evacuation Paths</el-checkbox>
            <el-checkbox label="timeline">Timeline Analysis</el-checkbox>
            <el-checkbox label="recommendations">Recommendations</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="generateExport">Export</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  VideoPlay,
  Download,
  RefreshLeft,
  WarningFilled,
  Timer,
  CircleCheck,
  DataAnalysis,
  RefreshRight,
  Loading,
  Check,
  Grid,
  Location,
  User,
  House
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isSimulating = ref(false)
const simProgress = ref(0)
const simulationStatus = ref<'idle' | 'running' | 'completed'>('idle')
const viewMode = ref('floorplan')
const selectedEmergencyType = ref('fire')
const simTime = ref(0)
const simSeconds = ref(0)
let simulationInterval: number | null = null

const loadingMessages = [
  'Preparing...',
  'Loading building model...',
  'Initializing evacuation simulation...',
  'Almost ready...'
]

// ==================== 参数定义 ====================
const emergencyTypes = [
  { id: 'fire', name: 'Fire', icon: 'Grid', color: '#f56c6c' },
  { id: 'earthquake', name: 'Earthquake', icon: 'Grid', color: '#e6a23c' },
  { id: 'flood', name: 'Flood', icon: 'Location', color: '#409eff' },
  { id: 'active_shooter', name: 'Active Shooter', icon: 'User', color: '#f56c6c' },
  { id: 'power_outage', name: 'Power Outage', icon: 'House', color: '#909399' }
]

const params = reactive({
  fireLocation: 'server_a',
  fireSeverity: 3,
  smokeDensity: 60,
  occupancy: 75,
  evacuationSpeed: 1,
  trainingLevel: 'intermediate'
})

const simulationResults = reactive({
  totalEvacuated: 248,
  evacuationTime: 12.5,
  casualties: 2,
  effectiveness: 92
})

const stats = reactive({
  totalEvacuated: 248,
  avgEvacTime: 12.5,
  evacuationRate: 92,
  responseTime: 45
})

const pathRecommendations = ref([
  { id: 1, type: 'success', message: 'Clear East exit corridor - minimal congestion detected' },
  { id: 2, type: 'warning', message: 'West stairwell congestion - consider rerouting' },
  { id: 3, type: 'primary', message: 'South exit recommended as primary evacuation route' }
])

const evacuationRoutes = ref([
  { name: 'Primary Route A', from: 'Data Hall', to: 'East Exit', distance: 85, time: 2.5, capacity: 45, status: 'Recommended' },
  { name: 'Secondary Route B', from: 'Data Hall', to: 'South Exit', distance: 120, time: 3.5, capacity: 35, status: 'Alternative' },
  { name: 'Emergency Route C', from: 'Server Room', to: 'North Exit', distance: 65, time: 2.0, capacity: 25, status: 'Restricted' },
  { name: 'Staff Route D', from: 'Office Area', to: 'West Exit', distance: 95, time: 2.8, capacity: 30, status: 'Alternative' }
])

const simulationHistory = ref<any[]>([])
const criticalPoint = ref('East Stairwell (min 3-5)')
const maxCongestion = ref(28)

const exportDialog = reactive({
  visible: false
})
const exportFormat = ref('pdf')
const exportIncludes = ref(['floorplan', 'evacuationPaths'])

// ==================== 图表引用 ====================
const viewerCanvasRef = ref<HTMLCanvasElement | null>(null)
const viewerContainerRef = ref<HTMLDivElement | null>(null)
const pathChartRef = ref<HTMLElement | null>(null)
const timelineChartRef = ref<HTMLElement | null>(null)

let pathChart: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null
let animationFrameId: number | null = null

// ==================== 辅助函数 ====================
const getSeverityLabel = (severity: number) => {
  const labels: Record<number, string> = { 1: 'Low', 2: 'Moderate', 3: 'High', 4: 'Severe', 5: 'Critical' }
  return labels[severity] || 'Moderate'
}

const formatTimestamp = (date: Date) => {
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ==================== 3D 场景绘制 ====================
const drawFloorPlan = () => {
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 450
  canvas.width = width
  canvas.height = height

  // Background
  ctx.fillStyle = '#1a1a2e'
  ctx.fillRect(0, 0, width, height)

  const centerX = width / 2
  const centerY = height / 2 - 20

  // Draw building outline
  ctx.fillStyle = 'rgba(64, 158, 255, 0.1)'
  ctx.fillRect(centerX - 160, centerY - 120, 320, 240)
  ctx.strokeStyle = '#409eff'
  ctx.lineWidth = 2
  ctx.strokeRect(centerX - 160, centerY - 120, 320, 240)

  // Draw rooms
  const rooms = [
    { name: 'Server Room', x: centerX - 150, y: centerY - 110, w: 70, h: 50, color: '#f56c6c' },
    { name: 'Data Hall', x: centerX - 70, y: centerY - 110, w: 60, h: 50, color: '#409eff' },
    { name: 'Office', x: centerX - 150, y: centerY - 50, w: 70, h: 50, color: '#67c23a' },
    { name: 'HVAC Room', x: centerX - 70, y: centerY - 50, w: 60, h: 50, color: '#e6a23c' },
    { name: 'Electrical', x: centerX + 10, y: centerY - 110, w: 70, h: 50, color: '#f56c6c' },
    { name: 'Battery', x: centerX + 10, y: centerY - 50, w: 70, h: 50, color: '#909399' }
  ]

  rooms.forEach(room => {
    ctx.fillStyle = room.color + '20'
    ctx.fillRect(room.x, room.y, room.w, room.h)
    ctx.strokeStyle = room.color
    ctx.strokeRect(room.x, room.y, room.w, room.h)
    ctx.fillStyle = 'white'
    ctx.font = '10px Arial'
    ctx.fillText(room.name, room.x + 5, room.y + 15)
  })

  // Draw exits
  const exits = [
    { x: centerX - 160, y: centerY - 40, label: 'North Exit' },
    { x: centerX + 160, y: centerY - 40, label: 'East Exit' },
    { x: centerX - 160, y: centerY + 80, label: 'West Exit' },
    { x: centerX + 160, y: centerY + 80, label: 'South Exit' }
  ]

  exits.forEach(exit => {
    ctx.fillStyle = '#67c23a'
    ctx.fillRect(exit.x - 5, exit.y - 10, 10, 20)
    ctx.fillStyle = '#67c23a'
    ctx.font = '9px Arial'
    ctx.fillText(exit.label, exit.x - 20, exit.y - 15)
  })

  // Draw fire source if fire emergency
  if (selectedEmergencyType.value === 'fire') {
    let fireX = centerX - 115, fireY = centerY - 85
    if (params.fireLocation === 'server_a') { fireX = centerX - 115; fireY = centerY - 85 }
    else if (params.fireLocation === 'server_b') { fireX = centerX - 100; fireY = centerY - 85 }
    else if (params.fireLocation === 'electrical') { fireX = centerX + 45; fireY = centerY - 85 }
    else if (params.fireLocation === 'data_hall') { fireX = centerX - 40; fireY = centerY - 85 }
    else if (params.fireLocation === 'battery') { fireX = centerX + 45; fireY = centerY - 25 }

    // Animated fire effect
    const pulse = (Date.now() % 1000) / 1000
    ctx.beginPath()
    ctx.arc(fireX + 35, fireY + 25, 15 + pulse * 3, 0, Math.PI * 2)
    ctx.fillStyle = `rgba(245, 108, 108, ${0.6 + pulse * 0.3})`
    ctx.fill()
    ctx.beginPath()
    ctx.arc(fireX + 35, fireY + 25, 8, 0, Math.PI * 2)
    ctx.fillStyle = '#f56c6c'
    ctx.fill()
    ctx.fillStyle = 'white'
    ctx.font = 'bold 10px Arial'
    ctx.fillText('FIRE', fireX + 30, fireY + 20)
  }

  // Draw evacuation paths if in path mode
  if (viewMode.value === 'evacuation') {
    ctx.beginPath()
    ctx.moveTo(centerX - 40, centerY - 85)
    ctx.lineTo(centerX + 155, centerY - 40)
    ctx.strokeStyle = '#67c23a'
    ctx.lineWidth = 3
    ctx.setLineDash([10, 5])
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(centerX - 40, centerY - 85)
    ctx.lineTo(centerX - 155, centerY + 80)
    ctx.stroke()
    ctx.setLineDash([])
  }

  // Draw crowd density heatmap
  if (viewMode.value === 'heatmap') {
    const gradient = ctx.createLinearGradient(centerX - 100, centerY - 80, centerX + 100, centerY + 80)
    gradient.addColorStop(0, 'rgba(103, 194, 58, 0.3)')
    gradient.addColorStop(0.5, 'rgba(230, 162, 60, 0.4)')
    gradient.addColorStop(1, 'rgba(245, 108, 108, 0.5)')
    ctx.fillStyle = gradient
    ctx.fillRect(centerX - 150, centerY - 110, 300, 220)
  }

  // Draw evacuation dots
  if (isSimulating.value || simulationStatus.value === 'completed') {
    const time = Date.now() / 1000
    for (let i = 0; i < 20; i++) {
      const progress = (simTime.value * 60 + simSeconds.value) / (simulationResults.evacuationTime * 60)
      const x = centerX - 100 + (progress * 300 + Math.sin(time + i) * 5)
      const y = centerY - 50 + Math.cos(time * 2 + i) * 15
      ctx.beginPath()
      ctx.arc(Math.min(Math.max(x, centerX - 150), centerX + 150), y, 3, 0, Math.PI * 2)
      ctx.fillStyle = '#67c23a'
      ctx.fill()
    }
  }
}

const startRenderLoop = () => {
  const render = () => {
    drawFloorPlan()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

const resetView = () => {
  drawFloorPlan()
}

// ==================== 图表渲染 ====================
const renderPathChart = () => {
  if (!pathChartRef.value) return
  if (pathChart) pathChart.dispose()

  pathChart = echarts.init(pathChartRef.value)

  const routes = ['East Exit', 'South Exit', 'North Exit', 'West Exit']
  const capacities = [45, 35, 25, 30]
  const congestions = [28, 22, 15, 18]

  pathChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Capacity', 'Current Load'], top: 0 },
    xAxis: { type: 'category', data: routes, name: 'Exit' },
    yAxis: { type: 'value', name: 'People per minute' },
    series: [
      { name: 'Capacity', type: 'bar', data: capacities, itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] } },
      { name: 'Current Load', type: 'bar', data: congestions, itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const renderTimelineChart = () => {
  if (!timelineChartRef.value) return
  if (timelineChart) timelineChart.dispose()

  timelineChart = echarts.init(timelineChartRef.value)

  const times = Array.from({ length: 15 }, (_, i) => `${i + 1} min`)
  const evacuated = [15, 35, 62, 85, 112, 138, 162, 185, 205, 222, 235, 242, 247, 248, 248]
  const rate = [15, 20, 27, 23, 27, 26, 24, 23, 20, 17, 13, 7, 5, 1, 0]

  timelineChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Cumulative Evacuated', 'Evacuation Rate'], top: 0 },
    xAxis: { type: 'category', data: times, name: 'Time' },
    yAxis: [{ type: 'value', name: 'People Evacuated' }, { type: 'value', name: 'Rate (ppl/min)' }],
    series: [
      { name: 'Cumulative Evacuated', type: 'line', data: evacuated, smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Evacuation Rate', type: 'bar', data: rate, yAxisIndex: 1, itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

// ==================== 模拟运行 ====================
const runSimulation = async () => {
  if (isSimulating.value) return

  isSimulating.value = true
  simulationStatus.value = 'running'
  simProgress.value = 0
  simTime.value = 0
  simSeconds.value = 0

  const interval = setInterval(() => {
    if (simProgress.value < 100) {
      simProgress.value += Math.random() * 10 + 5
      if (simProgress.value > 100) simProgress.value = 100
    }
  }, 200)

  // Simulate evacuation countdown
  let elapsed = 0
  const duration = simulationResults.evacuationTime * 60
  if (simulationInterval) clearInterval(simulationInterval)
  simulationInterval = window.setInterval(() => {
    elapsed++
    simTime.value = Math.floor(elapsed / 60)
    simSeconds.value = elapsed % 60
    if (elapsed >= duration) {
      clearInterval(simulationInterval!)
      simulationInterval = null
    }
  }, 1000)

  await new Promise(resolve => setTimeout(resolve, 3000))

  clearInterval(interval)
  simProgress.value = 100

  // Update results based on parameters
  const severityFactor = params.fireSeverity * 2
  const occupancyFactor = params.occupancy / 100
  const speedFactor = params.evacuationSpeed
  const trainingFactor = params.trainingLevel === 'expert' ? 1.2 : params.trainingLevel === 'advanced' ? 1.1 : params.trainingLevel === 'basic' ? 0.9 : 1

  const efficiency = (speedFactor * trainingFactor) / (severityFactor / 10 + occupancyFactor)
  const evacuated = Math.floor(250 * Math.min(1, efficiency))
  const casualties = Math.floor(250 - evacuated)

  simulationResults.totalEvacuated = evacuated
  simulationResults.casualties = casualties
  simulationResults.evacuationTime = parseFloat((12.5 / efficiency).toFixed(1))
  simulationResults.effectiveness = Math.floor(efficiency * 100)

  stats.totalEvacuated = evacuated
  stats.avgEvacTime = simulationResults.evacuationTime
  stats.evacuationRate = Math.floor((evacuated / 250) * 100)

  // Add to history
  simulationHistory.value.unshift({
    id: Date.now(),
    timestamp: new Date(),
    emergencyType: emergencyTypes.find(t => t.id === selectedEmergencyType.value)?.name,
    evacuationTime: simulationResults.evacuationTime,
    totalEvacuated: evacuated,
    casualties: casualties,
    effectiveness: simulationResults.effectiveness
  })

  simulationStatus.value = 'completed'
  isSimulating.value = false

  ElMessage.success('Emergency simulation completed')

  nextTick(() => {
    renderPathChart()
    renderTimelineChart()
  })
}

const resetSimulation = () => {
  if (simulationInterval) {
    clearInterval(simulationInterval)
    simulationInterval = null
  }
  isSimulating.value = false
  simulationStatus.value = 'idle'
  simProgress.value = 0
  simTime.value = 0
  simSeconds.value = 0
  params.fireSeverity = 3
  params.smokeDensity = 60
  params.occupancy = 75
  params.evacuationSpeed = 1
  params.trainingLevel = 'intermediate'
  ElMessage.info('Simulation reset')
}

const replaySimulation = (history: any) => {
  simulationResults.totalEvacuated = history.totalEvacuated
  simulationResults.evacuationTime = history.evacuationTime
  simulationResults.casualties = history.casualties
  simulationResults.effectiveness = history.effectiveness
  simulationStatus.value = 'completed'
  ElMessage.success(`Replaying simulation from ${formatTimestamp(history.timestamp)}`)
}

const viewRouteOnMap = (route: any) => {
  viewMode.value = 'evacuation'
  ElMessage.info(`Highlighting ${route.name}`)
}

const exportReport = () => {
  exportDialog.visible = true
}

const exportRoutes = () => {
  const data = JSON.stringify(evacuationRoutes.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `evacuation-routes-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Routes exported')
}

const generateExport = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    emergencyType: selectedEmergencyType.value,
    parameters: params,
    results: simulationResults,
    routes: evacuationRoutes.value,
    recommendations: pathRecommendations.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `emergency-simulation-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  exportDialog.visible = false
  ElMessage.success('Report exported')
}

const clearHistory = () => {
  simulationHistory.value = []
  ElMessage.info('Simulation history cleared')
}

// ==================== 数据加载 ====================
const loadData = () => {
  nextTick(() => {
    renderPathChart()
    renderTimelineChart()
    startRenderLoop()
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
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (simulationInterval) clearInterval(simulationInterval)
  window.removeEventListener('resize', () => {
    pathChart?.resize()
    timelineChart?.resize()
  })
})

watch([viewMode, selectedEmergencyType, params.fireLocation, params.fireSeverity], () => {
  drawFloorPlan()
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      pathChart?.resize()
      timelineChart?.resize()
    })
  }
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
.emergency-simulation-page {
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

.danger-bg { background-color: #fef0f0; color: #f56c6c; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
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

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #8c9aab;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Configuration Card */
.config-card, .visualization-card, .analysis-card, .routes-card, .history-card {
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

.config-section {
  margin-bottom: 16px;
}

.config-section label {
  font-size: 13px;
  font-weight: 500;
  color: #5e6e82;
  display: block;
  margin-bottom: 8px;
}

.emergency-types {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.emergency-type-card {
  flex: 1;
  min-width: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.emergency-type-card:hover {
  transform: translateY(-2px);
}

.emergency-type-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.emergency-type-card.fire.active { border-color: #f56c6c; background: #fef0f0; }
.emergency-type-card.earthquake.active { border-color: #e6a23c; background: #fff3e0; }
.emergency-type-card.flood.active { border-color: #409eff; background: #ecf5ff; }

.emergency-type-card .el-icon {
  font-size: 28px;
}

.emergency-type-card.fire .el-icon { color: #f56c6c; }
.emergency-type-card.earthquake .el-icon { color: #e6a23c; }
.emergency-type-card.flood .el-icon { color: #409eff; }

.param-form .param-hint {
  margin-left: 8px;
  font-size: 12px;
  color: #8c9aab;
}

.run-section {
  margin-top: 8px;
}

/* Visualization */
.view-controls {
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
  height: 450px;
  display: block;
}

.simulation-overlay, .results-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.simulation-status {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.8);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
}

.results-summary {
  background: rgba(0, 0, 0, 0.85);
  padding: 16px 24px;
  border-radius: 12px;
  min-width: 250px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: white;
}

.result-item .result-label {
  color: #8c9aab;
}

.result-item .result-value {
  font-weight: 600;
}

.result-item .result-value.danger { color: #f56c6c; }
.result-item .result-value.success { color: #67c23a; }

.viewer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.legend {
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

.legend-dot.exit { background-color: #67c23a; }
.legend-dot.fire { background-color: #f56c6c; }
.legend-dot.safe { background-color: #409eff; }
.legend-dot.crowd { background-color: #e6a23c; }

.simulation-time {
  font-family: monospace;
  font-size: 14px;
  color: #409eff;
}

/* Charts */
.path-chart, .timeline-chart {
  height: 280px;
  width: 100%;
}

.path-recommendations {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.rec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 13px;
}

.rec-item .el-icon.success { color: #67c23a; }
.rec-item .el-icon.warning { color: #e6a23c; }
.rec-item .el-icon.primary { color: #409eff; }

.timeline-stats {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.timeline-stats .stat {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.timeline-stats .stat-label {
  color: #8c9aab;
}

.timeline-stats .stat-value {
  font-weight: 600;
  color: #1f2f3d;
}

/* Routes Table */
.routes-card, .history-card {
  overflow: hidden;
}

.no-history {
  padding: 20px 0;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-slider__runway) {
  margin: 8px 0;
}
</style>