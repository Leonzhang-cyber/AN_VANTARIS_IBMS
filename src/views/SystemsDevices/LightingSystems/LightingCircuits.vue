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
        <div class="loading-tip">Lighting Circuits Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="lighting-circuits-container">
    <!-- Page Header -->
    <div class="page-header">
      <h2>Lighting Circuits</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddCircuit">
          <el-icon><Plus /></el-icon>
          Add Circuit
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Total Circuits</div>
              <div class="stat-value">{{ stats.total }}</div>
            </div>
            <div class="stat-icon total">
              <el-icon><Grid /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Active</div>
              <div class="stat-value active">{{ stats.active }}</div>
            </div>
            <div class="stat-icon active-bg">
              <el-icon><Link /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Inactive</div>
              <div class="stat-value inactive">{{ stats.inactive }}</div>
            </div>
            <div class="stat-icon inactive-bg">
              <el-icon><Link /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">Total Power (kW)</div>
              <div class="stat-value power">{{ stats.totalPower }}</div>
            </div>
            <div class="stat-icon power-bg">
              <el-icon><Lightning /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Row -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :md="16">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Circuit Load Trend (Last 7 Days)</span>
              <el-button text @click="refreshChart">Refresh</el-button>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="8">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Circuit Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Circuit Name">
          <el-input v-model="filters.circuitName" placeholder="Search by name" clearable />
        </el-form-item>
        <el-form-item label="Panel">
          <el-select v-model="filters.panel" placeholder="All Panels" clearable>
            <el-option v-for="panel in panelOptions" :key="panel" :label="panel" :value="panel" />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="filters.status" placeholder="All Status" clearable>
            <el-option label="Active" value="active" />
            <el-option label="Inactive" value="inactive" />
            <el-option label="Overload" value="overload" />
            <el-option label="Fault" value="fault" />
          </el-select>
        </el-form-item>
        <el-form-item label="Circuit Type">
          <el-select v-model="filters.circuitType" placeholder="All Types" clearable>
            <el-option label="Lighting" value="Lighting" />
            <el-option label="Emergency" value="Emergency" />
            <el-option label="Control" value="Control" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            Search
          </el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Data Table -->
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <span>Lighting Circuits List</span>
          <el-button text @click="toggleFullscreen">
            <el-icon><FullScreen /></el-icon>
          </el-button>
        </div>
      </template>

      <el-table :data="paginatedCircuits" stripe border style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Circuit Name" min-width="150" />
        <el-table-column prop="panel" label="Panel" min-width="120" />
        <el-table-column prop="zone" label="Zone" min-width="100" />
        <el-table-column prop="circuitType" label="Circuit Type" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getCircuitTypeTag(row.circuitType)">{{ row.circuitType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" min-width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              <el-icon v-if="row.status === 'active'"><Link /></el-icon>
              <el-icon v-else-if="row.status === 'inactive'"><Link /></el-icon>
              <el-icon v-else-if="row.status === 'fault'"><WarningFilled /></el-icon>
              <el-icon v-else><WarningFilled /></el-icon>
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="load" label="Load (kW)" min-width="140" sortable>
          <template #default="{ row }">
            <span>{{ row.load.toFixed(1) }} kW</span>
            <el-progress :percentage="Math.round(getLoadPercentage(row.load, row.capacity))" :stroke-width="6" />
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="Capacity (kW)" min-width="120" sortable>
          <template #default="{ row }">{{ row.capacity.toFixed(1) }} kW</template>
        </el-table-column>
        <el-table-column prop="current" label="Current (A)" min-width="110" sortable>
          <template #default="{ row }">{{ row.current.toFixed(1) }} A</template>
        </el-table-column>
        <el-table-column prop="voltage" label="Voltage (V)" min-width="110" sortable>
          <template #default="{ row }">
            <span :class="{ warning: row.voltage < 210 || row.voltage > 230 }">
              {{ row.voltage.toFixed(1) }} V
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="lastUpdated" label="Last Updated" min-width="170" sortable />
        <el-table-column label="Actions" fixed="right" min-width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetails(row)">
              <el-icon><View /></el-icon>
              View
            </el-button>
            <el-button type="success" link @click="controlCircuit(row)">
              <el-icon><Operation /></el-icon>
              Control
            </el-button>
            <el-button type="danger" link @click="confirmDelete(row)">
              <el-icon><Delete /></el-icon>
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredCircuits.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit Circuit Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Circuit Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter circuit name" />
        </el-form-item>
        <el-form-item label="Panel" prop="panel">
          <el-select v-model="formData.panel" placeholder="Select panel" style="width: 100%">
            <el-option v-for="panel in panelOptions" :key="panel" :label="panel" :value="panel" />
          </el-select>
        </el-form-item>
        <el-form-item label="Zone" prop="zone">
          <el-input v-model="formData.zone" placeholder="Enter zone" />
        </el-form-item>
        <el-form-item label="Circuit Type" prop="circuitType">
          <el-select v-model="formData.circuitType" placeholder="Select type" style="width: 100%">
            <el-option label="Lighting" value="Lighting" />
            <el-option label="Emergency" value="Emergency" />
            <el-option label="Control" value="Control" />
          </el-select>
        </el-form-item>
        <el-form-item label="Capacity (kW)" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1" :max="50" :step="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Confirm</el-button>
      </template>
    </el-dialog>

    <!-- Control Dialog -->
    <el-dialog v-model="controlDialogVisible" title="Circuit Control" width="450px">
      <div class="control-content" v-if="selectedCircuit">
        <div class="current-status">
          <span>Current Status:</span>
          <el-tag :type="getStatusTag(selectedCircuit.status)" size="large">
            {{ getStatusText(selectedCircuit.status) }}
          </el-tag>
        </div>
        <el-divider />
        <div class="control-buttons">
          <el-button type="success" @click="sendCommand('activate')" :disabled="selectedCircuit.status === 'active'">
            <el-icon><VideoPlay /></el-icon>
            Activate
          </el-button>
          <el-button type="danger" @click="sendCommand('deactivate')" :disabled="selectedCircuit.status === 'inactive'">
            <el-icon><VideoPause /></el-icon>
            Deactivate
          </el-button>
          <el-button type="warning" @click="sendCommand('reset')">
            <el-icon><RefreshRight /></el-icon>
            Reset
          </el-button>
        </div>
        <el-divider />
        <div class="load-control">
          <span>Load Control:</span>
          <el-slider v-model="loadLevel" :min="0" :max="100" @change="sendLoadCommand" />
          <span class="load-value">{{ loadLevel }}%</span>
        </div>
      </div>
    </el-dialog>

    <!-- Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Circuit Details" width="650px">
      <el-descriptions :column="2" border v-if="selectedCircuit">
        <el-descriptions-item label="Circuit Name">{{ selectedCircuit.name }}</el-descriptions-item>
        <el-descriptions-item label="Panel">{{ selectedCircuit.panel }}</el-descriptions-item>
        <el-descriptions-item label="Zone">{{ selectedCircuit.zone }}</el-descriptions-item>
        <el-descriptions-item label="Circuit Type">{{ selectedCircuit.circuitType }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTag(selectedCircuit.status)">{{ getStatusText(selectedCircuit.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedCircuit.load.toFixed(1) }} kW</el-descriptions-item>
        <el-descriptions-item label="Capacity">{{ selectedCircuit.capacity.toFixed(1) }} kW</el-descriptions-item>
        <el-descriptions-item label="Current">{{ selectedCircuit.current.toFixed(1) }} A</el-descriptions-item>
        <el-descriptions-item label="Voltage">{{ selectedCircuit.voltage.toFixed(1) }} V</el-descriptions-item>
        <el-descriptions-item label="Power Factor">{{ selectedCircuit.powerFactor }}</el-descriptions-item>
        <el-descriptions-item label="Energy Today">{{ selectedCircuit.energyToday }} kWh</el-descriptions-item>
        <el-descriptions-item label="Energy Month">{{ selectedCircuit.energyMonth }} kWh</el-descriptions-item>
        <el-descriptions-item label="Last Updated" :span="2">{{ selectedCircuit.lastUpdated }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus,
  Download,
  Refresh,
  Grid,
  Link,
  Lightning,
  Search,
  FullScreen,
  View,
  Operation,
  Delete,
  WarningFilled,
  VideoPlay,
  VideoPause,
  RefreshRight
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing...',
  'Almost ready...'
]

// ==================== Data State ====================
const tableLoading = ref(false)
const stats = ref({
  total: 0,
  active: 0,
  inactive: 0,
  totalPower: 0
})

// Mock Circuit Data
interface LightingCircuit {
  id: number
  name: string
  panel: string
  zone: string
  circuitType: string
  status: 'active' | 'inactive' | 'overload' | 'fault'
  load: number
  capacity: number
  current: number
  voltage: number
  powerFactor: number
  energyToday: number
  energyMonth: number
  lastUpdated: string
}

const circuits = ref<LightingCircuit[]>([])

// Panel options for filter
const panelOptions = ref<string[]>([])

// Generate mock data
const generateMockData = (): LightingCircuit[] => {
  const panels = ['LP-001', 'LP-002', 'LP-003', 'LP-004', 'LP-005', 'LP-006']
  const zones = ['Floor 1', 'Floor 2', 'Floor 3', 'Ground Floor', 'Basement', 'Mezzanine', 'East Wing', 'West Wing']
  const circuitTypes = ['Lighting', 'Emergency', 'Control']
  const statuses: ('active' | 'inactive' | 'overload' | 'fault')[] = ['active', 'active', 'active', 'inactive', 'overload', 'fault']

  const data: LightingCircuit[] = []
  for (let i = 1; i <= 36; i++) {
    const capacity = parseFloat((Math.random() * 10 + 2).toFixed(1))
    const loadPercent = Math.random()
    let load: number
    let status: 'active' | 'inactive' | 'overload' | 'fault'

    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)]
    if (randomStatus === 'inactive') {
      load = 0
      status = 'inactive'
    } else if (randomStatus === 'overload') {
      load = parseFloat((capacity * (0.95 + Math.random() * 0.1)).toFixed(1))
      status = 'overload'
    } else if (randomStatus === 'fault') {
      load = 0
      status = 'fault'
    } else {
      load = parseFloat((capacity * (0.3 + Math.random() * 0.5)).toFixed(1))
      status = 'active'
    }

    const voltage = 215 + Math.random() * 20
    const current = load * 1000 / voltage / 0.95

    data.push({
      id: i,
      name: `CIRC-${String(i).padStart(3, '0')}`,
      panel: panels[Math.floor(Math.random() * panels.length)],
      zone: zones[Math.floor(Math.random() * zones.length)],
      circuitType: circuitTypes[Math.floor(Math.random() * circuitTypes.length)],
      status: status,
      load: load,
      capacity: capacity,
      current: parseFloat(current.toFixed(1)),
      voltage: parseFloat(voltage.toFixed(1)),
      powerFactor: parseFloat((0.85 + Math.random() * 0.1).toFixed(2)),
      energyToday: parseFloat((Math.random() * 50).toFixed(1)),
      energyMonth: parseFloat((Math.random() * 1500).toFixed(1)),
      lastUpdated: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleString()
    })
  }
  return data
}

// Update panel options
const updatePanelOptions = () => {
  const panels = new Set(circuits.value.map(c => c.panel))
  panelOptions.value = Array.from(panels).sort()
}

// Filters
const filters = ref({
  circuitName: '',
  panel: '',
  status: '',
  circuitType: ''
})

// Pagination
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// Filtered circuits
const filteredCircuits = computed(() => {
  let filtered = circuits.value

  if (filters.value.circuitName) {
    filtered = filtered.filter(c => c.name.toLowerCase().includes(filters.value.circuitName.toLowerCase()))
  }
  if (filters.value.panel) {
    filtered = filtered.filter(c => c.panel === filters.value.panel)
  }
  if (filters.value.status) {
    filtered = filtered.filter(c => c.status === filters.value.status)
  }
  if (filters.value.circuitType) {
    filtered = filtered.filter(c => c.circuitType === filters.value.circuitType)
  }

  return filtered
})

// Paginated circuits
const paginatedCircuits = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.pageSize
  const end = start + pagination.value.pageSize
  return filteredCircuits.value.slice(start, end)
})

// Update stats
const updateStats = () => {
  stats.value.total = circuits.value.length
  stats.value.active = circuits.value.filter(c => c.status === 'active').length
  stats.value.inactive = circuits.value.filter(c => c.status === 'inactive').length
  stats.value.totalPower = parseFloat(circuits.value.reduce((sum, c) => sum + c.load, 0).toFixed(1))
}

// ==================== Chart Functions ====================
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

const initCharts = () => {
  nextTick(() => {
    if (trendChartRef.value) {
      if (trendChart) trendChart.dispose()
      trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['Total Load (kW)', 'Average Load %'] },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: [{ type: 'value', name: 'Load (kW)' }, { type: 'value', name: 'Load %' }],
        series: [
          {
            name: 'Total Load (kW)',
            type: 'line',
            data: [156.5, 162.3, 158.7, 165.2, 170.8, 163.5, 155.2],
            smooth: true,
            lineStyle: { color: '#409EFF', width: 3 },
            areaStyle: { opacity: 0.1 }
          },
          {
            name: 'Average Load %',
            type: 'line',
            data: [48.2, 50.1, 49.5, 51.3, 53.6, 50.8, 47.5],
            smooth: true,
            lineStyle: { color: '#67C23A', width: 3 },
            yAxisIndex: 1
          }
        ]
      })
    }

    if (statusChartRef.value) {
      if (statusChart) statusChart.dispose()
      statusChart = echarts.init(statusChartRef.value)
      statusChart.setOption({
        tooltip: { trigger: 'item' },
        legend: { orient: 'vertical', left: 'left' },
        series: [{
          type: 'pie',
          radius: '55%',
          data: [
            { value: stats.value.active, name: 'Active', itemStyle: { color: '#67C23A' } },
            { value: stats.value.inactive, name: 'Inactive', itemStyle: { color: '#909399' } },
            { value: circuits.value.filter(c => c.status === 'overload').length, name: 'Overload', itemStyle: { color: '#E6A23C' } },
            { value: circuits.value.filter(c => c.status === 'fault').length, name: 'Fault', itemStyle: { color: '#F56C6C' } }
          ],
          emphasis: { scale: true },
          label: { show: true, formatter: '{b}: {d}%' }
        }]
      })
    }
  })
}

const refreshChart = () => {
  if (trendChart) {
    trendChart.setOption({
      series: [
        { data: [156.5 + Math.random() * 20, 162.3 + Math.random() * 20, 158.7 + Math.random() * 20, 165.2 + Math.random() * 20, 170.8 + Math.random() * 20, 163.5 + Math.random() * 20, 155.2 + Math.random() * 20] },
        { data: [48.2 + Math.random() * 5, 50.1 + Math.random() * 5, 49.5 + Math.random() * 5, 51.3 + Math.random() * 5, 53.6 + Math.random() * 5, 50.8 + Math.random() * 5, 47.5 + Math.random() * 5] }
      ]
    })
  }
  ElMessage.success('Chart data refreshed')
}

// ==================== CRUD Operations ====================
const dialogVisible = ref(false)
const dialogTitle = ref('Add Circuit')
const formRef = ref()
const formData = ref({
  name: '',
  panel: '',
  zone: '',
  circuitType: '',
  capacity: 10
})

const formRules = {
  name: [{ required: true, message: 'Please enter circuit name', trigger: 'blur' }],
  panel: [{ required: true, message: 'Please select panel', trigger: 'change' }],
  zone: [{ required: true, message: 'Please enter zone', trigger: 'blur' }],
  circuitType: [{ required: true, message: 'Please select circuit type', trigger: 'change' }]
}

const handleAddCircuit = () => {
  dialogTitle.value = 'Add Circuit'
  formData.value = { name: '', panel: '', zone: '', circuitType: '', capacity: 10 }
  dialogVisible.value = true
}

const submitForm = async () => {
  try {
    await formRef.value?.validate()

    const newCircuit: LightingCircuit = {
      id: circuits.value.length + 1,
      name: formData.value.name,
      panel: formData.value.panel,
      zone: formData.value.zone,
      circuitType: formData.value.circuitType,
      status: 'inactive',
      load: 0,
      capacity: formData.value.capacity,
      current: 0,
      voltage: 220,
      powerFactor: 0.95,
      energyToday: 0,
      energyMonth: 0,
      lastUpdated: new Date().toLocaleString()
    }

    circuits.value.push(newCircuit)
    updateStats()
    updatePanelOptions()
    initCharts()
    dialogVisible.value = false
    ElMessage.success('Circuit added successfully')
  } catch (error) {
    ElMessage.error('Please fill in all required fields')
  }
}

const confirmDelete = (row: LightingCircuit) => {
  ElMessageBox.confirm(`Are you sure to delete circuit "${row.name}"?`, 'Warning', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = circuits.value.findIndex(c => c.id === row.id)
    if (index > -1) {
      circuits.value.splice(index, 1)
      updateStats()
      updatePanelOptions()
      initCharts()
      ElMessage.success('Circuit deleted successfully')
    }
  }).catch(() => {})
}

// ==================== Circuit Control ====================
const controlDialogVisible = ref(false)
const selectedCircuit = ref<LightingCircuit | null>(null)
const loadLevel = ref(0)

const controlCircuit = (row: LightingCircuit) => {
  selectedCircuit.value = row
  loadLevel.value = row.capacity > 0 ? Math.round((row.load / row.capacity) * 100) : 0
  controlDialogVisible.value = true
}

const sendCommand = (command: string) => {
  if (!selectedCircuit.value) return

  tableLoading.value = true
  setTimeout(() => {
    if (command === 'activate') {
      selectedCircuit.value!.status = 'active'
      selectedCircuit.value!.load = parseFloat((selectedCircuit.value!.capacity * 0.6).toFixed(1))
      selectedCircuit.value!.current = parseFloat((selectedCircuit.value!.load * 1000 / selectedCircuit.value!.voltage / 0.95).toFixed(1))
    } else if (command === 'deactivate') {
      selectedCircuit.value!.status = 'inactive'
      selectedCircuit.value!.load = 0
      selectedCircuit.value!.current = 0
    } else if (command === 'reset') {
      if (selectedCircuit.value!.status === 'fault' || selectedCircuit.value!.status === 'overload') {
        selectedCircuit.value!.status = 'active'
        selectedCircuit.value!.load = parseFloat((selectedCircuit.value!.capacity * 0.5).toFixed(1))
        selectedCircuit.value!.current = parseFloat((selectedCircuit.value!.load * 1000 / selectedCircuit.value!.voltage / 0.95).toFixed(1))
      }
    }
    selectedCircuit.value!.lastUpdated = new Date().toLocaleString()
    updateStats()
    tableLoading.value = false
    ElMessage.success(`Command "${command}" executed successfully`)
    controlDialogVisible.value = false
  }, 500)
}

const sendLoadCommand = (value: number) => {
  if (!selectedCircuit.value) return
  if (selectedCircuit.value.status !== 'active') {
    selectedCircuit.value.status = 'active'
  }
  const newLoad = selectedCircuit.value.capacity * (value / 100)
  selectedCircuit.value.load = parseFloat(newLoad.toFixed(1))
  selectedCircuit.value.current = parseFloat((newLoad * 1000 / selectedCircuit.value.voltage / 0.95).toFixed(1))
  selectedCircuit.value.lastUpdated = new Date().toLocaleString()
  ElMessage.info(`Load set to ${value}%`)
}

// ==================== Detail View ====================
const detailDialogVisible = ref(false)

const viewDetails = (row: LightingCircuit) => {
  selectedCircuit.value = row
  detailDialogVisible.value = true
}

// ==================== Helper Functions ====================
const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    active: 'success',
    inactive: 'info',
    overload: 'warning',
    fault: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    active: 'Active',
    inactive: 'Inactive',
    overload: 'Overload',
    fault: 'Fault'
  }
  return map[status] || status
}

const getCircuitTypeTag = (type: string) => {
  const map: Record<string, string> = {
    Lighting: 'primary',
    Emergency: 'danger',
    Control: 'success'
  }
  return map[type] || 'info'
}

const getLoadPercentage = (load: number, capacity: number) => {
  if (capacity === 0) return 0
  return parseFloat(((load / capacity) * 100).toFixed(1))
}

// ==================== Actions ====================
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    circuits.value = generateMockData()
    updateStats()
    updatePanelOptions()
    initCharts()
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 800)
}

const handleExport = () => {
  ElMessage.success('Export started')
}

const handleSearch = () => {
  pagination.value.currentPage = 1
  ElMessage.success(`Found ${filteredCircuits.value.length} circuits`)
}

const resetFilters = () => {
  filters.value = { circuitName: '', panel: '', status: '', circuitType: '' }
  pagination.value.currentPage = 1
  ElMessage.success('Filters reset')
}

const handleSizeChange = () => {
  pagination.value.currentPage = 1
}

const handleCurrentChange = () => {}

const toggleFullscreen = () => {
  ElMessage.info('Fullscreen mode')
}

// Watch for window resize
watch([trendChartRef, statusChartRef], () => {
  window.addEventListener('resize', () => {
    trendChart?.resize()
    statusChart?.resize()
  })
})

// ==================== Lifecycle ====================
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
      circuits.value = generateMockData()
      updateStats()
      updatePanelOptions()
      initCharts()
    }, 400)
  }, 2000)
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

/* ==================== Main Content ==================== */
.lighting-circuits-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 12px;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-value.active {
  color: #67C23A;
}

.stat-value.inactive {
  color: #909399;
}

.stat-value.power {
  color: #409EFF;
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

.stat-icon.total {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.stat-icon.active-bg {
  background: rgba(103, 194, 58, 0.1);
  color: #67C23A;
}

.stat-icon.inactive-bg {
  background: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.stat-icon.power-bg {
  background: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.charts-row {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.table-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.warning {
  color: #f56c6c;
  font-weight: bold;
}

.control-content {
  padding: 10px;
}

.current-status {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
}

.control-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 20px 0;
}

.load-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

.load-control .el-slider {
  flex: 1;
}

.load-value {
  min-width: 45px;
  font-size: 14px;
  color: #409EFF;
}
</style>