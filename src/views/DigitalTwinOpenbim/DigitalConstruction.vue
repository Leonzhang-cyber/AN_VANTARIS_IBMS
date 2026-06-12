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
        <div class="loading-tip">Digital Twin - Digital Construction</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="digital-construction-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Digital Construction</h1>
        <p>Real-time construction monitoring, progress tracking, and quality management</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="syncData">
          <el-icon><Refresh /></el-icon>
          Sync Data
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><DataLine /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.overallProgress }}<span class="stat-unit">%</span></div>
            <div class="stat-label">Overall Progress</div>
            <div class="stat-trend positive">↑ {{ stats.progressChange }}% vs plan</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.completedTasks }}</div>
            <div class="stat-label">Completed Tasks</div>
            <div class="stat-trend">/ {{ stats.totalTasks }} total</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.openIssues }}</div>
            <div class="stat-label">Open Issues</div>
            <div class="stat-trend negative">{{ stats.criticalIssues }} critical</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeWorkers }}</div>
            <div class="stat-label">Active Workers</div>
            <div class="stat-trend">On site today</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- 3D Construction Viewer -->
      <el-col :xs="24" :lg="14">
        <div class="viewer-card">
          <div class="card-header">
            <h3>Construction Site Overview</h3>
            <div class="view-controls">
              <el-radio-group v-model="viewLayer" size="small">
                <el-radio-button label="all">All</el-radio-button>
                <el-radio-button label="structure">Structure</el-radio-button>
                <el-radio-button label="mep">MEP</el-radio-button>
                <el-radio-button label="finishing">Finishing</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="resetView">
                <el-icon><RefreshRight /></el-icon>
                Reset
              </el-button>
            </div>
          </div>
          <div class="viewer-container" ref="viewerContainerRef">
            <canvas ref="viewerCanvasRef" class="viewer-canvas"></canvas>
            <div class="progress-overlay">
              <div class="progress-ring">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <circle cx="40" cy="40" r="35" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="5" />
                  <circle cx="40" cy="40" r="35" fill="none" stroke="#409eff" stroke-width="5" :stroke-dasharray="`${stats.overallProgress * 2.2}, 220`" stroke-linecap="round" transform="rotate(-90 40 40)" />
                </svg>
                <span class="progress-text">{{ stats.overallProgress }}%</span>
              </div>
            </div>
          </div>
          <div class="viewer-footer">
            <div class="legend">
              <span><span class="legend-dot completed"></span> Completed</span>
              <span><span class="legend-dot in-progress"></span> In Progress</span>
              <span><span class="legend-dot pending"></span> Pending</span>
              <span><span class="legend-dot issue"></span> Issue Detected</span>
            </div>
            <div class="last-sync">Last sync: {{ lastSyncTime }}</div>
          </div>
        </div>
      </el-col>

      <!-- Progress & Milestones -->
      <el-col :xs="24" :lg="10">
        <div class="progress-card">
          <div class="card-header">
            <h3>Project Milestones</h3>
            <el-button size="small" @click="viewAllMilestones">View All</el-button>
          </div>
          <div class="milestones-list">
            <div v-for="milestone in milestones" :key="milestone.id" class="milestone-item">
              <div class="milestone-status" :class="milestone.status">
                <el-icon v-if="milestone.status === 'completed'"><Check /></el-icon>
                <el-icon v-else-if="milestone.status === 'in-progress'"><Loading /></el-icon>
                <span v-else>{{ milestone.day }}</span>
              </div>
              <div class="milestone-content">
                <div class="milestone-title">{{ milestone.title }}</div>
                <div class="milestone-date">{{ milestone.date }}</div>
              </div>
              <div class="milestone-progress">
                <el-progress :percentage="milestone.progress" :stroke-width="6" :show-text="false" />
                <span class="progress-value">{{ milestone.progress }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Resource Utilization -->
        <div class="resources-card">
          <div class="card-header">
            <h3>Resource Utilization</h3>
          </div>
          <div class="resources-list">
            <div v-for="resource in resources" :key="resource.name" class="resource-item">
              <div class="resource-header">
                <span class="resource-name">{{ resource.name }}</span>
                <span class="resource-value">{{ resource.utilization }}%</span>
              </div>
              <el-progress :percentage="resource.utilization" :stroke-width="8" :color="resource.utilization > 90 ? '#f56c6c' : resource.utilization > 70 ? '#e6a23c' : '#67c23a'" />
              <div class="resource-detail">{{ resource.allocated }} / {{ resource.total }} units</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Construction Progress by Zone -->
    <div class="zones-card">
      <div class="card-header">
        <h3>Progress by Zone</h3>
        <el-select v-model="zoneFilter" placeholder="Filter by zone" size="small" style="width: 140px">
          <el-option label="All Zones" value="all" />
          <el-option label="Zone A" value="zoneA" />
          <el-option label="Zone B" value="zoneB" />
          <el-option label="Zone C" value="zoneC" />
        </el-select>
      </div>
      <div ref="zonesChartRef" class="zones-chart"></div>
    </div>

    <!-- Quality Inspection Points -->
    <div class="quality-card">
      <div class="card-header">
        <h3>Quality Inspection Points</h3>
        <el-button size="small" @click="addInspection">+ Add Inspection</el-button>
      </div>
      <el-table :data="inspections" stripe>
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="checkpoint" label="Checkpoint" min-width="200" />
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="inspector" label="Inspector" width="140" />
        <el-table-column prop="date" label="Date" width="120" />
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewInspection(row)">View</el-button>
            <el-button v-if="row.status === 'Pending'" link type="success" size="small" @click="completeInspection(row)">Complete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Daily Activity Log -->
    <div class="activity-card">
      <div class="card-header">
        <h3>Daily Activity Log</h3>
        <el-button size="small" @click="exportActivityLog">Export Log</el-button>
      </div>
      <div class="activity-timeline">
        <div v-for="activity in activityLog" :key="activity.id" class="activity-item">
          <div class="activity-time">{{ activity.time }}</div>
          <div class="activity-content">
            <span class="activity-user">{{ activity.user }}</span>
            <span class="activity-action">{{ activity.action }}</span>
            <span class="activity-location">{{ activity.location }}</span>
          </div>
          <div class="activity-status" :class="activity.status">
            {{ activity.status }}
          </div>
        </div>
      </div>
    </div>

    <!-- Inspection Detail Dialog -->
    <el-dialog v-model="inspectionDialog.visible" :title="inspectionDialog.inspection?.checkpoint" width="550px">
      <div v-if="inspectionDialog.inspection">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Location">{{ inspectionDialog.inspection.location }}</el-descriptions-item>
          <el-descriptions-item label="Inspector">{{ inspectionDialog.inspection.inspector }}</el-descriptions-item>
          <el-descriptions-item label="Date">{{ inspectionDialog.inspection.date }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(inspectionDialog.inspection.status)">{{ inspectionDialog.inspection.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Checklist" :span="2">
            <div v-for="item in inspectionDialog.inspection.checklist" :key="item.name" class="checklist-item">
              <el-checkbox v-model="item.checked" :disabled="inspectionDialog.inspection.status !== 'Pending'">
                {{ item.name }}
              </el-checkbox>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Notes" :span="2">
            <el-input v-model="inspectionDialog.inspection.notes" type="textarea" :rows="2" placeholder="Add inspection notes..." />
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="inspectionDialog.visible = false">Close</el-button>
        <el-button v-if="inspectionDialog.inspection?.status === 'Pending'" type="primary" @click="submitInspection">
          Submit Inspection
        </el-button>
      </template>
    </el-dialog>

    <!-- Add Inspection Dialog -->
    <el-dialog v-model="addInspectionDialog.visible" title="Add Inspection Point" width="450px">
      <el-form :model="newInspection" label-width="100px">
        <el-form-item label="Location">
          <el-select v-model="newInspection.location" style="width: 100%">
            <el-option label="Zone A - Foundation" value="Zone A - Foundation" />
            <el-option label="Zone B - Structural" value="Zone B - Structural" />
            <el-option label="Zone C - MEP" value="Zone C - MEP" />
            <el-option label="Zone D - Finishing" value="Zone D - Finishing" />
          </el-select>
        </el-form-item>
        <el-form-item label="Checkpoint">
          <el-input v-model="newInspection.checkpoint" placeholder="Enter checkpoint name" />
        </el-form-item>
        <el-form-item label="Inspector">
          <el-input v-model="newInspection.inspector" placeholder="Inspector name" />
        </el-form-item>
        <el-form-item label="Due Date">
          <el-date-picker v-model="newInspection.dueDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addInspectionDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="createInspection">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh,
  Download,
  DataLine,
  CircleCheck,
  Warning,
  User,
  RefreshRight,
  Check,
  Loading,
  Plus
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const lastSyncTime = ref('')
const viewLayer = ref('all')
const zoneFilter = ref('all')

const loadingMessages = [
  'Preparing...',
  'Loading BIM model...',
  'Syncing construction data...',
  'Almost ready...'
]

// ==================== 数据定义 ====================
const stats = reactive({
  overallProgress: 68,
  progressChange: 4,
  completedTasks: 142,
  totalTasks: 210,
  openIssues: 12,
  criticalIssues: 3,
  activeWorkers: 87
})

const milestones = ref([
  { id: 1, title: 'Foundation Complete', date: '2024-03-15', progress: 100, status: 'completed', day: '' },
  { id: 2, title: 'Structural Frame', date: '2024-05-20', progress: 85, status: 'in-progress', day: '' },
  { id: 3, title: 'MEP Rough-in', date: '2024-07-10', progress: 45, status: 'in-progress', day: '' },
  { id: 4, title: 'Interior Finishing', date: '2024-08-25', progress: 20, status: 'pending', day: 'Day 45' },
  { id: 5, title: 'Final Inspection', date: '2024-10-01', progress: 0, status: 'pending', day: 'Day 90' }
])

const resources = ref([
  { name: 'Crane Usage', utilization: 72, allocated: 18, total: 25 },
  { name: 'Concrete Pumps', utilization: 85, allocated: 17, total: 20 },
  { name: 'Labor Force', utilization: 78, allocated: 87, total: 112 },
  { name: 'Material Stock', utilization: 62, allocated: 310, total: 500 },
  { name: 'Safety Equipment', utilization: 95, allocated: 95, total: 100 }
])

const inspections = ref([
  { id: 1, location: 'Zone A', checkpoint: 'Foundation Reinforcement', status: 'Passed', inspector: 'John Smith', date: '2024-06-10', checklist: [{ name: 'Rebar spacing', checked: true }, { name: 'Concrete strength', checked: true }], notes: '' },
  { id: 2, location: 'Zone B', checkpoint: 'Steel Structure Alignment', status: 'Passed', inspector: 'Sarah Lee', date: '2024-06-08', checklist: [{ name: 'Column plumbness', checked: true }, { name: 'Beam alignment', checked: true }], notes: '' },
  { id: 3, location: 'Zone C', checkpoint: 'HVAC Duct Installation', status: 'Failed', inspector: 'Mike Chen', date: '2024-06-09', checklist: [{ name: 'Duct sealing', checked: false }, { name: 'Insulation thickness', checked: false }], notes: 'Air leakage detected' },
  { id: 4, location: 'Zone A', checkpoint: 'Electrical Conduit', status: 'Pending', inspector: 'David Wong', date: '2024-06-12', checklist: [{ name: 'Conduit routing', checked: false }, { name: 'Grounding check', checked: false }], notes: '' },
  { id: 5, location: 'Zone B', checkpoint: 'Fire Suppression', status: 'Pending', inspector: 'Anna Kim', date: '2024-06-13', checklist: [{ name: 'Sprinkler spacing', checked: false }, { name: 'Pipe pressure test', checked: false }], notes: '' }
])

const activityLog = ref([
  { id: 1, time: '08:30', user: 'John Smith', action: 'Started concrete pour - Zone A', location: 'Zone A', status: 'In Progress' },
  { id: 2, time: '09:15', user: 'Sarah Lee', action: 'Completed steel inspection', location: 'Zone B', status: 'Completed' },
  { id: 3, time: '10:00', user: 'Mike Chen', action: 'Reported HVAC issue', location: 'Zone C', status: 'Issue' },
  { id: 4, time: '11:30', user: 'David Wong', action: 'Electrical conduit installation', location: 'Zone A', status: 'In Progress' },
  { id: 5, time: '13:45', user: 'Anna Kim', action: 'Safety walkthrough', location: 'All Zones', status: 'Completed' },
  { id: 6, time: '14:30', user: 'John Smith', action: 'Material delivery arrived', location: 'Loading Dock', status: 'Info' }
])

const inspectionDialog = reactive({
  visible: false,
  inspection: null as any
})

const addInspectionDialog = reactive({
  visible: false
})

const newInspection = reactive({
  location: '',
  checkpoint: '',
  inspector: '',
  dueDate: null
})

// ==================== 图表引用 ====================
const viewerCanvasRef = ref<HTMLCanvasElement | null>(null)
const viewerContainerRef = ref<HTMLDivElement | null>(null)
const zonesChartRef = ref<HTMLElement | null>(null)

let zonesChart: echarts.ECharts | null = null
let animationFrameId: number | null = null

// ==================== 辅助函数 ====================
const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'Passed': 'success',
    'Failed': 'danger',
    'Pending': 'warning',
    'In Progress': 'info'
  }
  return map[status] || 'info'
}

const formatDate = (date: Date) => {
  return date.toISOString().slice(0, 10)
}

// ==================== 3D 场景绘制 ====================
const drawConstructionScene = () => {
  const canvas = viewerCanvasRef.value
  const container = viewerContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 400
  canvas.width = width
  canvas.height = height

  // Background
  ctx.fillStyle = '#1a1a2e'
  ctx.fillRect(0, 0, width, height)

  const centerX = width / 2
  const centerY = height / 2 + 20

  // Draw building outline based on layer
  ctx.fillStyle = 'rgba(64, 158, 255, 0.15)'
  ctx.fillRect(centerX - 160, centerY - 140, 320, 280)
  ctx.strokeStyle = '#409eff'
  ctx.lineWidth = 2
  ctx.strokeRect(centerX - 160, centerY - 140, 320, 280)

  // Draw different layers
  if (viewLayer.value === 'all' || viewLayer.value === 'structure') {
    // Structural frame
    ctx.fillStyle = 'rgba(103, 194, 58, 0.4)'
    for (let i = 0; i < 4; i++) {
      const y = centerY - 120 + i * 60
      ctx.fillRect(centerX - 150, y, 300, 8)
    }
    // Columns
    for (let i = 0; i < 5; i++) {
      const x = centerX - 140 + i * 70
      ctx.fillRect(x, centerY - 140, 8, 280)
    }
  }

  if (viewLayer.value === 'all' || viewLayer.value === 'mep') {
    // MEP systems
    ctx.beginPath()
    ctx.moveTo(centerX - 130, centerY - 100)
    ctx.lineTo(centerX - 80, centerY - 70)
    ctx.lineTo(centerX - 30, centerY - 100)
    ctx.lineTo(centerX + 20, centerY - 70)
    ctx.lineTo(centerX + 70, centerY - 100)
    ctx.strokeStyle = '#e6a23c'
    ctx.lineWidth = 3
    ctx.stroke()
  }

  if (viewLayer.value === 'all' || viewLayer.value === 'finishing') {
    // Finishing indicators
    ctx.fillStyle = 'rgba(64, 158, 255, 0.3)'
    for (let i = 0; i < 3; i++) {
      const x = centerX - 100 + i * 100
      ctx.fillRect(x, centerY + 20, 60, 40)
    }
  }

  // Draw zone labels
  ctx.fillStyle = 'white'
  ctx.font = '10px Arial'
  ctx.fillText('Zone A', centerX - 130, centerY - 150)
  ctx.fillText('Zone B', centerX - 30, centerY - 150)
  ctx.fillText('Zone C', centerX + 70, centerY - 150)

  // Draw progress colors on zones
  const zones = [
    { x: centerX - 140, y: centerY - 130, w: 90, h: 260, progress: 75 },
    { x: centerX - 40, y: centerY - 130, w: 90, h: 260, progress: 60 },
    { x: centerX + 60, y: centerY - 130, w: 90, h: 260, progress: 45 }
  ]

  zones.forEach(zone => {
    const fillHeight = zone.h * (zone.progress / 100)
    ctx.fillStyle = `rgba(103, 194, 58, ${0.3 + zone.progress / 200})`
    ctx.fillRect(zone.x, zone.y + zone.h - fillHeight, zone.w, fillHeight)
  })

  // Draw cranes
  ctx.fillStyle = '#8c9aab'
  ctx.fillRect(centerX - 180, centerY - 160, 10, 300)
  ctx.beginPath()
  ctx.moveTo(centerX - 180, centerY - 160)
  ctx.lineTo(centerX - 220, centerY - 180)
  ctx.lineTo(centerX - 180, centerY - 170)
  ctx.fill()

  // Animated construction lights
  const pulse = (Date.now() % 2000) / 2000
  ctx.fillStyle = `rgba(245, 158, 11, ${0.3 + pulse * 0.3})`
  for (let i = 0; i < 5; i++) {
    ctx.beginPath()
    ctx.arc(centerX - 150 + i * 75, centerY - 120, 5, 0, Math.PI * 2)
    ctx.fill()
  }
}

const startRenderLoop = () => {
  const render = () => {
    drawConstructionScene()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

const resetView = () => {
  viewLayer.value = 'all'
  drawConstructionScene()
}

// ==================== 图表渲染 ====================
const renderZonesChart = () => {
  if (!zonesChartRef.value) return
  if (zonesChart) zonesChart.dispose()

  zonesChart = echarts.init(zonesChartRef.value)

  const zones = ['Zone A', 'Zone B', 'Zone C', 'Zone D']
  const planned = [100, 85, 60, 30]
  const actual = [75, 60, 45, 20]

  zonesChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Planned', 'Actual'], top: 0 },
    xAxis: { type: 'category', data: zones },
    yAxis: { type: 'value', name: 'Progress (%)', max: 100 },
    series: [
      { name: 'Planned', type: 'bar', data: planned, itemStyle: { color: '#8c9aab', borderRadius: [4, 4, 0, 0] } },
      { name: 'Actual', type: 'bar', data: actual, itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

// ==================== 交互事件 ====================
const syncData = () => {
  lastSyncTime.value = new Date().toLocaleTimeString()
  ElMessage.success('Data synchronized with site')
}

const exportReport = () => {
  const report = {
    generatedAt: new Date().toISOString(),
    stats: stats,
    milestones: milestones.value,
    resources: resources.value,
    inspections: inspections.value,
    activityLog: activityLog.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `construction-report-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Report exported')
}

const exportActivityLog = () => {
  const data = JSON.stringify(activityLog.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `activity-log-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Activity log exported')
}

const viewInspection = (inspection: any) => {
  inspectionDialog.inspection = inspection
  inspectionDialog.visible = true
}

const completeInspection = (inspection: any) => {
  inspectionDialog.inspection = inspection
  inspectionDialog.visible = true
}

const submitInspection = () => {
  const inspection = inspectionDialog.inspection
  const allChecked = inspection.checklist.every((item: any) => item.checked)
  inspection.status = allChecked ? 'Passed' : 'Failed'
  inspection.date = formatDate(new Date())
  inspectionDialog.visible = false
  ElMessage.success(`Inspection ${inspection.status}`)
  // Refresh table
  inspections.value = [...inspections.value]
}

const addInspection = () => {
  addInspectionDialog.visible = true
}

const createInspection = () => {
  if (!newInspection.location || !newInspection.checkpoint || !newInspection.inspector) {
    ElMessage.warning('Please fill all fields')
    return
  }

  const newId = Math.max(...inspections.value.map(i => i.id)) + 1
  inspections.value.push({
    id: newId,
    location: newInspection.location,
    checkpoint: newInspection.checkpoint,
    status: 'Pending',
    inspector: newInspection.inspector,
    date: newInspection.dueDate ? formatDate(new Date(newInspection.dueDate)) : formatDate(new Date()),
    checklist: [],
    notes: ''
  })

  addInspectionDialog.visible = false
  newInspection.location = ''
  newInspection.checkpoint = ''
  newInspection.inspector = ''
  newInspection.dueDate = null
  ElMessage.success('Inspection point added')
}

const viewAllMilestones = () => {
  ElMessage.info('Opening full milestone view...')
}

// ==================== 数据加载 ====================
const loadData = () => {
  lastSyncTime.value = new Date().toLocaleTimeString()
  nextTick(() => {
    renderZonesChart()
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
  window.removeEventListener('resize', () => {
    zonesChart?.resize()
  })
})

watch([viewLayer, zoneFilter], () => {
  drawConstructionScene()
  if (zoneFilter.value !== 'all') {
    renderZonesChart()
  }
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      zonesChart?.resize()
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
.digital-construction-page {
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

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.positive { color: #67c23a; }
.stat-trend.negative { color: #f56c6c; }

/* Viewer Card */
.viewer-card, .progress-card, .resources-card, .zones-card, .quality-card, .activity-card {
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
  height: 400px;
  display: block;
}

.progress-overlay {
  position: absolute;
  top: 20px;
  right: 20px;
}

.progress-ring {
  position: relative;
  width: 80px;
  height: 80px;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 16px;
  font-weight: bold;
  color: white;
}

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

.legend-dot.completed { background-color: #67c23a; }
.legend-dot.in-progress { background-color: #409eff; }
.legend-dot.pending { background-color: #e6a23c; }
.legend-dot.issue { background-color: #f56c6c; }

.last-sync {
  font-size: 11px;
  color: #8c9aab;
}

/* Milestones */
.milestones-list {
  max-height: 280px;
  overflow-y: auto;
}

.milestone-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.milestone-status {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.milestone-status.completed {
  background-color: #f0f9eb;
  color: #67c23a;
}

.milestone-status.in-progress {
  background-color: #ecf5ff;
  color: #409eff;
}

.milestone-status.pending {
  background-color: #f5f7fa;
  color: #8c9aab;
}

.milestone-content {
  flex: 1;
}

.milestone-title {
  font-weight: 500;
  font-size: 13px;
  color: #1f2f3d;
}

.milestone-date {
  font-size: 10px;
  color: #8c9aab;
}

.milestone-progress {
  width: 100px;
  text-align: right;
}

.progress-value {
  font-size: 11px;
  color: #8c9aab;
  margin-left: 8px;
}

/* Resources */
.resources-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.resource-item {
  width: 100%;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 13px;
}

.resource-name {
  font-weight: 500;
}

.resource-value {
  color: #5e6e82;
}

.resource-detail {
  font-size: 10px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Zones Chart */
.zones-chart {
  height: 320px;
  width: 100%;
}

/* Activity Timeline */
.activity-timeline {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.activity-time {
  width: 50px;
  font-size: 11px;
  font-family: monospace;
  color: #8c9aab;
}

.activity-content {
  flex: 1;
  font-size: 12px;
}

.activity-user {
  font-weight: 600;
  color: #1f2f3d;
  margin-right: 8px;
}

.activity-action {
  color: #5e6e82;
}

.activity-location {
  font-size: 10px;
  color: #8c9aab;
  margin-left: 8px;
}

.activity-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 12px;
}

.activity-status.In\ Progress { background-color: #ecf5ff; color: #409eff; }
.activity-status.Completed { background-color: #f0f9eb; color: #67c23a; }
.activity-status.Issue { background-color: #fef0f0; color: #f56c6c; }
.activity-status.Info { background-color: #f5f7fa; color: #8c9aab; }

/* Checklist */
.checklist-item {
  margin: 8px 0;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}
</style>