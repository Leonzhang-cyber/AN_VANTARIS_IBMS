<template>
  <div class="asset-lifecycle-container">
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
            <span class="loading-title">Loading Asset Lifecycle</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Asset Lifecycle Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="asset-lifecycle-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Asset Lifecycle</h1>
          <p class="page-subtitle">Track and manage assets from procurement to disposal</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="addAsset">
            <el-icon><Plus /></el-icon>
            Add Asset
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="scheduleAudit">
            <el-icon><Calendar /></el-icon>
            Schedule Audit
          </el-button>
        </div>
      </div>

      <!-- Lifecycle Stages Overview -->
      <div class="lifecycle-overview">
        <el-card class="lifecycle-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Connection /></el-icon>
              <span>Asset Lifecycle Stages</span>
            </div>
          </div>
          <div class="lifecycle-stages">
            <div class="stage" v-for="stage in lifecycleStages" :key="stage.name">
              <div class="stage-icon" :style="{ background: stage.color }">
                <el-icon><component :is="stage.icon" /></el-icon>
              </div>
              <div class="stage-info">
                <span class="stage-name">{{ stage.name }}</span>
                <span class="stage-count">{{ stage.count }} assets</span>
              </div>
              <div class="stage-progress">
                <el-progress :percentage="stage.percentage" :stroke-width="4" :color="stage.color" :show-text="false" />
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Key Metrics -->
      <div class="metrics-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon blue">
                <el-icon><Grid /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Total Assets</span>
                <span class="metric-value">{{ totalAssets }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon green">
                <el-icon><Check /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Active Assets</span>
                <span class="metric-value">{{ activeAssets }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon orange">
                <el-icon><Tools /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">Under Maintenance</span>
                <span class="metric-value">{{ maintenanceAssets }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-icon purple">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="metric-info">
                <span class="metric-label">End of Life (6 months)</span>
                <span class="metric-value">{{ eolAssets }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Asset Lifecycle Gantt -->
      <div class="gantt-section">
        <el-card class="gantt-card" shadow="hover">
          <div class="card-header">
            <div class="card-title">
              <el-icon><TrendCharts /></el-icon>
              <span>Asset Lifecycle Timeline</span>
            </div>
            <el-select v-model="ganttCategory" size="small" style="width: 120px">
              <el-option label="All Assets" value="all" />
              <el-option label="Cooling" value="cooling" />
              <el-option label="Power" value="power" />
              <el-option label="IT" value="it" />
            </el-select>
          </div>
          <div class="chart-container">
            <canvas id="lifecycleGanttChart"></canvas>
          </div>
        </el-card>
      </div>

      <!-- Assets Table -->
      <div class="assets-section">
        <div class="section-header">
          <h3>Asset Inventory</h3>
          <div class="header-controls">
            <el-input v-model="searchQuery" placeholder="Search assets..." prefix-icon="Search" style="width: 200px" clearable />
            <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 120px">
              <el-option label="Cooling" value="cooling" />
              <el-option label="Power" value="power" />
              <el-option label="IT" value="it" />
              <el-option label="Lighting" value="lighting" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Active" value="active" />
              <el-option label="Maintenance" value="maintenance" />
              <el-option label="EOL" value="eol" />
              <el-option label="Retired" value="retired" />
            </el-select>
          </div>
        </div>
        <el-table :data="filteredAssets" stripe class="assets-table">
          <el-table-column prop="name" label="Asset Name" />
          <el-table-column prop="category" label="Category" >
            <template #default="{ row }">
              <el-tag size="small">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="model" label="Model" width="140" />
          <el-table-column prop="manufacturer" label="Manufacturer" />
          <el-table-column prop="installationDate" label="Installation Date" />
          <el-table-column prop="expectedLife" label="Expected Life" >
            <template #default="{ row }">
              {{ row.expectedLife }} years
            </template>
          </el-table-column>
          <el-table-column label="Age" >
            <template #default="{ row }">
              <span :style="{ color: getAgeColor(row.age) }">{{ row.age }} years</span>
            </template>
          </el-table-column>
          <el-table-column label="Health" >
            <template #default="{ row }">
              <el-progress :percentage="row.health" :stroke-width="8" :color="getHealthColor(row.health)" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" >
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewAssetDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="scheduleMaintenance(row)">Maintenance</el-button>
              <el-button type="warning" link size="small" @click="retireAsset(row)">Retire</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Replacement Planning -->
      <div class="replacement-section">
        <div class="section-header">
          <h3>Replacement Planning</h3>
          <el-button type="primary" link @click="generateReplacementPlan">Generate Plan →</el-button>
        </div>
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="replacement-card">
              <div class="replacement-header">
                <el-icon><Warning /></el-icon>
                <span>Critical (Replace within 3 months)</span>
              </div>
              <div class="replacement-list">
                <div v-for="asset in criticalAssets" :key="asset.id" class="replacement-item">
                  <span class="asset-name">{{ asset.name }}</span>
                  <span class="asset-age">{{ asset.age }} years</span>
                  <el-button size="small" @click="planReplacement(asset)">Plan</el-button>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="replacement-card">
              <div class="replacement-header warning">
                <el-icon><Warning /></el-icon>
                <span>Warning (Replace within 6-12 months)</span>
              </div>
              <div class="replacement-list">
                <div v-for="asset in warningAssets" :key="asset.id" class="replacement-item">
                  <span class="asset-name">{{ asset.name }}</span>
                  <span class="asset-age">{{ asset.age }} years</span>
                  <el-button size="small" type="warning" @click="planReplacement(asset)">Plan</el-button>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="replacement-card">
              <div class="replacement-header success">
                <el-icon><Success /></el-icon>
                <span>Good (Replace >12 months)</span>
              </div>
              <div class="replacement-list">
                <div v-for="asset in goodAssets" :key="asset.id" class="replacement-item">
                  <span class="asset-name">{{ asset.name }}</span>
                  <span class="asset-age">{{ asset.age }} years</span>
                  <el-button size="small" type="primary" @click="planReplacement(asset)">Monitor</el-button>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Cost Analysis -->
      <div class="cost-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="cost-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Coin /></el-icon>
                  <span>Lifecycle Cost Analysis</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="costAnalysisChart"></canvas>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="cost-card" shadow="hover">
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DataLine /></el-icon>
                  <span>Asset Value Depreciation</span>
                </div>
              </div>
              <div class="chart-container">
                <canvas id="depreciationChart"></canvas>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="runLifecycleAnalysis">
          <el-icon><Cpu /></el-icon>
          Run Lifecycle Analysis
        </el-button>
        <el-button size="large" @click="generateLifecycleReport">
          <el-icon><Document /></el-icon>
          Generate Lifecycle Report
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
        </el-button>
      </div>
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Category">{{ selectedAsset?.category }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(selectedAsset?.status)">{{ selectedAsset?.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Model">{{ selectedAsset?.model }}</el-descriptions-item>
        <el-descriptions-item label="Manufacturer">{{ selectedAsset?.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="Serial Number">{{ selectedAsset?.serialNumber }}</el-descriptions-item>
        <el-descriptions-item label="Installation Date">{{ selectedAsset?.installationDate }}</el-descriptions-item>
        <el-descriptions-item label="Expected Life">{{ selectedAsset?.expectedLife }} years</el-descriptions-item>
        <el-descriptions-item label="Current Age">{{ selectedAsset?.age }} years</el-descriptions-item>
        <el-descriptions-item label="Health Score">
          <el-progress :percentage="selectedAsset?.health" :stroke-width="10" :color="getHealthColor(selectedAsset?.health)" />
        </el-descriptions-item>
        <el-descriptions-item label="Maintenance History" :span="2">
          <ul>
            <li>2024-05-15: Quarterly inspection</li>
            <li>2024-02-10: Filter replacement</li>
            <li>2023-11-20: Firmware update</li>
          </ul>
        </el-descriptions-item>
        <el-descriptions-item label="Total Cost of Ownership" :span="2">
          <strong>${{ formatNumber(selectedAsset?.tco) }}</strong>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedAsset)">Schedule Maintenance</el-button>
        <el-button type="danger" @click="retireAsset(selectedAsset)">Retire Asset</el-button>
      </template>
    </el-dialog>

    <!-- Maintenance Dialog -->
    <el-dialog v-model="maintenanceDialogVisible" title="Schedule Maintenance" width="500px">
      <el-form>
        <el-form-item label="Asset">
          <span>{{ selectedAsset?.name }}</span>
        </el-form-item>
        <el-form-item label="Maintenance Type">
          <el-select v-model="maintenanceType" placeholder="Select type">
            <el-option label="Preventive" value="preventive" />
            <el-option label="Corrective" value="corrective" />
            <el-option label="Predictive" value="predictive" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule Date">
          <el-date-picker v-model="maintenanceDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Priority">
          <el-select v-model="maintenancePriority" placeholder="Select priority">
            <el-option label="High" value="high" />
            <el-option label="Medium" value="medium" />
            <el-option label="Low" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input type="textarea" :rows="3" placeholder="Add maintenance notes..." v-model="maintenanceNotes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="maintenanceDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveMaintenance">Schedule</el-button>
      </template>
    </el-dialog>

    <!-- Retire Dialog -->
    <el-dialog v-model="retireDialogVisible" title="Retire Asset" width="450px">
      <el-form>
        <el-form-item label="Asset">
          <span>{{ selectedAsset?.name }}</span>
        </el-form-item>
        <el-form-item label="Retirement Date">
          <el-date-picker v-model="retirementDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Reason">
          <el-select v-model="retirementReason" placeholder="Select reason">
            <el-option label="End of Life" value="eol" />
            <el-option label="Technology Upgrade" value="upgrade" />
            <el-option label="Performance Degradation" value="degradation" />
            <el-option label="Energy Efficiency" value="efficiency" />
          </el-select>
        </el-form-item>
        <el-form-item label="Disposal Method">
          <el-select v-model="disposalMethod" placeholder="Select method">
            <el-option label="Recycle" value="recycle" />
            <el-option label="Resell" value="resell" />
            <el-option label="Donate" value="donate" />
            <el-option label="Landfill" value="landfill" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="retireDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmRetire">Retire Asset</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, Download, Calendar, Connection, Grid, Check, Tools, Clock,
  TrendCharts, Search, Coin, DataLine, Cpu, Document, Warning, SuccessFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading asset lifecycle data...')

// ==================== Reactive Data ====================
const searchQuery = ref('')
const categoryFilter = ref('')
const statusFilter = ref('')
const ganttCategory = ref('all')
const detailDialogVisible = ref(false)
const maintenanceDialogVisible = ref(false)
const retireDialogVisible = ref(false)
const selectedAsset = ref<any>(null)

// Maintenance form
const maintenanceType = ref('preventive')
const maintenanceDate = ref('')
const maintenancePriority = ref('medium')
const maintenanceNotes = ref('')

// Retirement form
const retirementDate = ref('')
const retirementReason = ref('eol')
const disposalMethod = ref('recycle')

// Lifecycle stages
const lifecycleStages = ref([
  { name: 'Procurement', icon: 'ShoppingCart', color: '#3b82f6', count: 12, percentage: 15 },
  { name: 'Installation', icon: 'Tools', color: '#10b981', count: 8, percentage: 10 },
  { name: 'Operation', icon: 'Cpu', color: '#8b5cf6', count: 45, percentage: 56 },
  { name: 'Maintenance', icon: 'Setting', color: '#f59e0b', count: 8, percentage: 10 },
  { name: 'EOL Planning', icon: 'Clock', color: '#ef4444', count: 5, percentage: 6 },
  { name: 'Retired', icon: 'Delete', color: '#909399', count: 2, percentage: 3 }
])

// Assets data
const assets = ref([
  { id: 1, name: 'Chiller-01', category: 'cooling', model: 'Carrier AquaEdge', manufacturer: 'Carrier', installationDate: '2020-03-15', expectedLife: 15, age: 4, health: 92, status: 'active', serialNumber: 'CH-2020-001', tco: 125000 },
  { id: 2, name: 'Chiller-02', category: 'cooling', model: 'Carrier AquaEdge', manufacturer: 'Carrier', installationDate: '2018-06-20', expectedLife: 15, age: 6, health: 85, status: 'active', serialNumber: 'CH-2018-045', tco: 128000 },
  { id: 3, name: 'CRAC-01', category: 'cooling', model: 'Stulz CyberAir', manufacturer: 'Stulz', installationDate: '2015-04-10', expectedLife: 12, age: 9, health: 68, status: 'warning', serialNumber: 'CR-2015-023', tco: 85000 },
  { id: 4, name: 'UPS-01', category: 'power', model: 'Galaxy VX', manufacturer: 'Schneider', installationDate: '2017-11-05', expectedLife: 12, age: 7, health: 78, status: 'maintenance', serialNumber: 'UP-2017-089', tco: 150000 },
  { id: 5, name: 'UPS-02', category: 'power', model: 'Galaxy VX', manufacturer: 'Schneider', installationDate: '2021-08-15', expectedLife: 12, age: 3, health: 96, status: 'active', serialNumber: 'UP-2021-156', tco: 152000 },
  { id: 6, name: 'Server Rack A01', category: 'it', model: 'PowerEdge R750', manufacturer: 'Dell', installationDate: '2022-02-28', expectedLife: 5, age: 2, health: 94, status: 'active', serialNumber: 'SR-2022-078', tco: 45000 },
  { id: 7, name: 'Cooling Tower-01', category: 'cooling', model: 'BAC 3000', manufacturer: 'Baltimore', installationDate: '2014-03-20', expectedLife: 12, age: 10, health: 55, status: 'eol', serialNumber: 'CT-2014-012', tco: 95000 },
  { id: 8, name: 'LED Lighting Controller', category: 'lighting', model: 'Dynalite', manufacturer: 'Philips', installationDate: '2023-01-10', expectedLife: 10, age: 1, health: 98, status: 'active', serialNumber: 'LT-2023-034', tco: 12000 }
])

// Computed
const totalAssets = computed(() => assets.value.length)
const activeAssets = computed(() => assets.value.filter(a => a.status === 'active').length)
const maintenanceAssets = computed(() => assets.value.filter(a => a.status === 'maintenance').length)
const eolAssets = computed(() => assets.value.filter(a => a.status === 'eol' || a.health < 60).length)

const filteredAssets = computed(() => {
  let result = assets.value
  if (searchQuery.value) {
    result = result.filter(a => a.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
  }
  if (categoryFilter.value) {
    result = result.filter(a => a.category === categoryFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(a => a.status === statusFilter.value)
  }
  return result
})

const criticalAssets = computed(() => assets.value.filter(a => a.health < 60 && a.status !== 'retired').slice(0, 3))
const warningAssets = computed(() => assets.value.filter(a => a.health >= 60 && a.health < 75 && a.status !== 'retired').slice(0, 3))
const goodAssets = computed(() => assets.value.filter(a => a.health >= 75 && a.status !== 'retired').slice(0, 3))

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return num.toString()
}

const getAgeColor = (age: number) => {
  if (age < 3) return '#10b981'
  if (age < 6) return '#3b82f6'
  if (age < 9) return '#f59e0b'
  return '#ef4444'
}

const getHealthColor = (health: number) => {
  if (health >= 80) return '#10b981'
  if (health >= 60) return '#f59e0b'
  return '#ef4444'
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    'active': 'success',
    'maintenance': 'warning',
    'eol': 'danger',
    'retired': 'info'
  }
  return types[status] || 'info'
}

// Actions
const addAsset = () => {
  ElMessage.info('Add asset interface will open')
}

const exportReport = () => {
  ElMessage.success('Asset report export started')
}

const scheduleAudit = () => {
  ElMessage.info('Audit scheduling interface will open')
}

const viewAssetDetails = (asset: any) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
}

const scheduleMaintenance = (asset: any) => {
  selectedAsset.value = asset
  maintenanceType.value = 'preventive'
  maintenanceDate.value = ''
  maintenancePriority.value = 'medium'
  maintenanceNotes.value = ''
  maintenanceDialogVisible.value = true
}

const saveMaintenance = () => {
  ElMessage.success(`Maintenance scheduled for ${selectedAsset.value.name}`)
  maintenanceDialogVisible.value = false
}

const retireAsset = (asset: any) => {
  selectedAsset.value = asset
  retirementDate.value = ''
  retirementReason.value = 'eol'
  disposalMethod.value = 'recycle'
  retireDialogVisible.value = true
}

const confirmRetire = () => {
  ElMessage.success(`${selectedAsset.value.name} has been retired`)
  retireDialogVisible.value = false
}

const planReplacement = (asset: any) => {
  ElMessage.info(`Replacement planning for ${asset.name}`)
}

const generateReplacementPlan = () => {
  ElMessage.success('Replacement plan generated')
}

const runLifecycleAnalysis = () => {
  ElMessage.success('Lifecycle analysis started')
}

const generateLifecycleReport = () => {
  ElMessage.success('Lifecycle report generation started')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling will open')
}

// Chart instances
let lifecycleGanttChart: echarts.ECharts | null = null
let costAnalysisChart: echarts.ECharts | null = null
let depreciationChart: echarts.ECharts | null = null

// Chart initialization
const initLifecycleGanttChart = () => {
  const canvas = document.getElementById('lifecycleGanttChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 350

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (lifecycleGanttChart) lifecycleGanttChart.dispose()
  lifecycleGanttChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  const assetsData = assets.value.map(a => ({
    name: a.name,
    start: new Date(a.installationDate).getFullYear(),
    end: new Date(a.installationDate).getFullYear() + a.expectedLife,
    value: a.expectedLife,
    category: a.category
  }))

  lifecycleGanttChart.setOption({
    tooltip: { trigger: 'axis', formatter: (params: any) => `${params[0].name}: ${params[0].value} years life` },
    xAxis: { type: 'value', name: 'Year' },
    yAxis: { type: 'category', data: assetsData.map(a => a.name) },
    series: [{
      type: 'bar', data: assetsData.map(a => a.value),
      itemStyle: { borderRadius: [0, 8, 8, 0], color: (params: any) => {
          const colors: Record<string, string> = { cooling: '#3b82f6', power: '#f59e0b', it: '#10b981', lighting: '#8b5cf6' }
          return colors[assetsData[params.dataIndex].category] || '#909399'
        } },
      label: { show: true, position: 'right', formatter: '{c} years' }
    }]
  })
}

const initCostAnalysisChart = () => {
  const canvas = document.getElementById('costAnalysisChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 320

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (costAnalysisChart) costAnalysisChart.dispose()
  costAnalysisChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  costAnalysisChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Acquisition Cost', 'Maintenance Cost', 'Energy Cost', 'Total'], bottom: 0, left: 'center' },
    xAxis: { type: 'category', data: ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5', 'Year 6', 'Year 7', 'Year 8', 'Year 9', 'Year 10'] },
    yAxis: { type: 'value', name: 'Cost ($k)' },
    series: [
      { name: 'Acquisition Cost', type: 'bar', data: [100, 0, 0, 0, 0, 0, 0, 0, 0, 0], itemStyle: { color: '#3b82f6' } },
      { name: 'Maintenance Cost', type: 'bar', data: [5, 8, 10, 12, 15, 18, 22, 25, 28, 32], itemStyle: { color: '#f59e0b' } },
      { name: 'Energy Cost', type: 'bar', data: [20, 22, 24, 26, 28, 30, 32, 34, 36, 38], itemStyle: { color: '#10b981' } },
      { name: 'Total', type: 'line', data: [125, 30, 34, 38, 43, 48, 54, 59, 64, 70], lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', symbolSize: 6 }
    ]
  })
}

const initDepreciationChart = () => {
  const canvas = document.getElementById('depreciationChart') as HTMLCanvasElement
  if (!canvas) return

  const container = canvas.parentElement
  if (!container) return

  const width = container.clientWidth
  const height = 320

  const pixelRatio = window.devicePixelRatio || 1
  canvas.width = width * pixelRatio
  canvas.height = height * pixelRatio
  canvas.style.width = `${width}px`
  canvas.style.height = `${height}px`

  if (depreciationChart) depreciationChart.dispose()
  depreciationChart = echarts.init(canvas, null, { width: width, height: height, devicePixelRatio: pixelRatio })

  depreciationChart.setOption({
    tooltip: { trigger: 'axis', formatter: '{b}: ${c}k' },
    xAxis: { type: 'category', data: ['Chiller', 'UPS', 'CRAC', 'Server', 'Cooling Tower'] },
    yAxis: { type: 'value', name: 'Value ($k)' },
    series: [
      { name: 'Initial Value', type: 'bar', data: [125, 150, 85, 45, 95], itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}k' } },
      { name: 'Current Value', type: 'bar', data: [85, 95, 35, 40, 25], itemStyle: { color: '#f59e0b', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}k' } }
    ]
  })
}

const refreshAllCharts = () => {
  setTimeout(() => {
    initLifecycleGanttChart()
    initCostAnalysisChart()
    initDepreciationChart()
  }, 100)
}

// Window resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (lifecycleGanttChart) lifecycleGanttChart.resize()
    if (costAnalysisChart) costAnalysisChart.resize()
    if (depreciationChart) depreciationChart.resize()
  }, 200)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          refreshAllCharts()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  if (lifecycleGanttChart) lifecycleGanttChart.dispose()
  if (costAnalysisChart) costAnalysisChart.dispose()
  if (depreciationChart) depreciationChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.asset-lifecycle-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
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
  font-size: 24px;
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

/* ==================== Main Content ==================== */
.asset-lifecycle-main {
  padding: 24px 32px;
  min-height: 100vh;
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
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Lifecycle Overview */
.lifecycle-overview {
  margin-bottom: 24px;
}

.lifecycle-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.card-title .el-icon {
  font-size: 18px;
  color: #3b82f6;
}

.lifecycle-stages {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.stage {
  flex: 1;
  text-align: center;
}

.stage-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: white;
}

.stage-info {
  margin-bottom: 8px;
}

.stage-name {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #1e293b;
}

.stage-count {
  display: block;
  font-size: 11px;
  color: #64748b;
}

/* Metrics Section */
.metrics-section {
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.metric-icon.blue { background: #eff6ff; color: #3b82f6; }
.metric-icon.green { background: #ecfdf5; color: #10b981; }
.metric-icon.orange { background: #fffbeb; color: #f59e0b; }
.metric-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.metric-info {
  flex: 1;
}

.metric-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

/* Gantt Section */
.gantt-section {
  margin-bottom: 24px;
}

.gantt-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container {
  width: 100%;
  min-height: 350px;
  position: relative;
}

/* Assets Section */
.assets-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.assets-table {
  border-radius: 16px;
  overflow: hidden;
}

/* Replacement Section */
.replacement-section {
  margin-bottom: 24px;
}

.replacement-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.replacement-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 12px;
  margin-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  color: #1e293b;
}

.replacement-header.warning { color: #f59e0b; }
.replacement-header.success { color: #10b981; }

.replacement-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.replacement-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.asset-name {
  font-weight: 500;
  color: #1e293b;
}

.asset-age {
  font-size: 12px;
  color: #64748b;
}

/* Cost Section */
.cost-section {
  margin-bottom: 24px;
}

.cost-card {
  border-radius: 20px;
  background: white;
  padding: 20px;
  height: 100%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 20px;
}

/* Responsive */
@media (max-width: 1200px) {
  .asset-lifecycle-main { padding: 16px; }
  .lifecycle-stages { flex-wrap: wrap; }
  .stage { min-width: 100px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .lifecycle-stages { flex-direction: column; }
  .section-header { flex-direction: column; align-items: flex-start; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>