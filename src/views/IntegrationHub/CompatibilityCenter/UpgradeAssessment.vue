<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Connection, Setting, DataLine,
  Document, CircleCheck, CircleClose, Loading,
  TrendCharts, Monitor, Aim, Clock, Timer,
  Warning, Upload, Download, Filter, Cpu,
  Link, Check, Close, QuestionFilled,
  Share, Expand, Fold, Tickets, Sunny
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing assessment engine...',
  'Analyzing current versions...',
  'Checking compatibility...',
  'Calculating upgrade paths...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedPriority = ref('all')
const selectedType = ref('all')
const detailsVisible = ref(false)
const batchUpgradeVisible = ref(false)
const chartRef = ref(null)
const radarChartRef = ref(null)

let impactChart: echarts.ECharts | null = null
let radarChart: echarts.ECharts | null = null

// Upgrade types
const upgradeTypes = [
  { value: 'all', label: 'All Upgrades' },
  { value: 'firmware', label: 'Firmware' },
  { value: 'driver', label: 'Driver' },
  { value: 'protocol', label: 'Protocol' }
]

// Priority levels
const priorityLevels = [
  { value: 'all', label: 'All Priorities' },
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' }
]

// Upgrade assessment data
const upgrades = ref([
  {
    id: 'UPG001', name: 'BACnet Controller Firmware', type: 'firmware', device: 'Building A - BMS Controller',
    currentVersion: '4.2.0', targetVersion: '4.3.0', priority: 'high',
    impact: 'moderate', downtime: '5-10 min', complexity: 'medium',
    compatibility: 'full', estimatedTime: '15 min', risk: 'low',
    benefits: ['Security improvements', 'Bug fixes', 'Performance boost'],
    prerequisites: ['Backup configuration', 'Test in lab first'], date: '2024-01-15'
  },
  {
    id: 'UPG002', name: 'Modbus TCP Driver', type: 'driver', device: 'Power Meter - Main',
    currentVersion: '2.1.0', targetVersion: '2.2.0', priority: 'medium',
    impact: 'low', downtime: '2-3 min', complexity: 'easy',
    compatibility: 'full', estimatedTime: '10 min', risk: 'very low',
    benefits: ['Improved performance', 'New features'], prerequisites: ['Stop data collection'], date: '2024-01-18'
  },
  {
    id: 'UPG003', name: 'OPC-UA Server', type: 'protocol', device: 'OPC-UA Gateway',
    currentVersion: '1.4.0', targetVersion: '1.5.0', priority: 'critical',
    impact: 'major', downtime: '30-45 min', complexity: 'complex',
    compatibility: 'partial', estimatedTime: '1 hour', risk: 'medium',
    benefits: ['Security patch', 'New encryption', 'Better stability'],
    prerequisites: ['Schedule maintenance window', 'Notify all clients', 'Test connectivity'], date: '2024-01-20'
  },
  {
    id: 'UPG004', name: 'MQTT Client Update', type: 'driver', device: 'Temperature Sensors Hub',
    currentVersion: '5.1.0', targetVersion: '5.2.0', priority: 'low',
    impact: 'low', downtime: '1-2 min', complexity: 'easy',
    compatibility: 'full', estimatedTime: '5 min', risk: 'very low',
    benefits: ['Minor improvements'], prerequisites: [], date: '2024-01-22'
  },
  {
    id: 'UPG005', name: 'KNX/IP Gateway Firmware', type: 'firmware', device: 'KNX Router',
    currentVersion: '1.8.0', targetVersion: '2.0.0', priority: 'high',
    impact: 'moderate', downtime: '15-20 min', complexity: 'medium',
    compatibility: 'full', estimatedTime: '30 min', risk: 'low',
    benefits: ['Major performance upgrade', 'New features', 'Better reliability'],
    prerequisites: ['Backup ETS project', 'Test with main devices'], date: '2024-01-25'
  },
  {
    id: 'UPG006', name: 'SNMP Agent Update', type: 'protocol', device: 'Network Switch - Core',
    currentVersion: '3.0.0', targetVersion: '3.1.0', priority: 'medium',
    impact: 'low', downtime: '5-10 min', complexity: 'easy',
    compatibility: 'full', estimatedTime: '15 min', risk: 'low',
    benefits: ['Security fixes', 'Better SNMPv3 support'], prerequisites: ['Backup config'], date: '2024-01-28'
  },
  {
    id: 'UPG007', name: 'Lighting Controller Firmware', type: 'firmware', device: 'Lighting Panel - L1',
    currentVersion: '4.5.0', targetVersion: '4.6.0', priority: 'critical',
    impact: 'major', downtime: '20-30 min', complexity: 'complex',
    compatibility: 'partial', estimatedTime: '45 min', risk: 'high',
    benefits: ['Critical bug fix', 'Energy savings'],
    prerequisites: ['Schedule after hours', 'Prepare rollback plan', 'Test on spare unit'], date: '2024-02-01'
  },
  {
    id: 'UPG008', name: 'BACnet Router Firmware', type: 'firmware', device: 'BACnet Router',
    currentVersion: '3.8.0', targetVersion: '4.0.0', priority: 'medium',
    impact: 'moderate', downtime: '10-15 min', complexity: 'medium',
    compatibility: 'full', estimatedTime: '20 min', risk: 'low',
    benefits: ['Performance improvements', 'New BACnet objects'], prerequisites: ['Verify network stability'], date: '2024-02-05'
  }
])

// Impact analysis data
const impactAnalysis = reactive({
  totalDevices: 156,
  devicesToUpgrade: 45,
  estimatedTotalDowntime: 185,
  averageRisk: 2.3,
  criticalCount: 2,
  highCount: 2,
  mediumCount: 2,
  lowCount: 2
})

// Radar chart data
const radarData = ref({
  indicators: [
    { name: 'Security Impact', max: 10 },
    { name: 'Performance Impact', max: 10 },
    { name: 'Compatibility Risk', max: 10 },
    { name: 'Implementation Complexity', max: 10 },
    { name: 'Downtime Impact', max: 10 },
    { name: 'Business Impact', max: 10 }
  ],
  series: [
    { value: [8, 6, 7, 5, 4, 7], name: 'Current State' },
    { value: [3, 2, 4, 3, 2, 3], name: 'After Upgrade' }
  ]
})

// Batch upgrade config
const batchConfig = reactive({
  priority: 'all',
  type: 'all',
  scheduledDate: '',
  scheduledTime: '02:00',
  notifyBefore: true,
  autoRollback: true
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: upgrades.value.length
})

// Filtered upgrades
const filteredUpgrades = computed(() => {
  let filtered = upgrades.value
  if (searchKeyword.value) {
    filtered = filtered.filter(u =>
        u.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        u.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        u.device.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        u.type.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedPriority.value !== 'all') {
    filtered = filtered.filter(u => u.priority === selectedPriority.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(u => u.type === selectedType.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initChart()
        initRadarChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  impactChart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  const priorityData = priorityLevels.filter(p => p.value !== 'all').map(priority => {
    const entries = upgrades.value.filter(u => u.priority === priority.value)
    return { priority: priority.label, count: entries.length }
  })

  impactChart?.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: priorityData.map(p => p.priority) },
    yAxis: { type: 'value', name: 'Number of Upgrades' },
    series: [{
      name: 'Upgrades by Priority',
      type: 'bar',
      data: priorityData.map(p => p.count),
      itemStyle: {
        color: (params: any) => {
          const priorities = ['Critical', 'High', 'Medium', 'Low']
          const colors = ['#F56C6C', '#E6A23C', '#409EFF', '#67C23A']
          return colors[priorities.indexOf(params.name)]
        },
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top' }
    }]
  })
}

const initRadarChart = () => {
  if (!radarChartRef.value) return

  radarChart = echarts.init(radarChartRef.value)
  radarChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { data: ['Current State', 'After Upgrade'], bottom: 0 },
    radar: {
      indicator: radarData.value.indicators,
      shape: 'circle',
      center: ['50%', '50%'],
      radius: '65%',
      name: { textStyle: { fontSize: 12, color: '#606266' } }
    },
    series: [{
      type: 'radar',
      data: radarData.value.series,
      areaStyle: { opacity: 0.2 },
      lineStyle: { width: 2 },
      symbolSize: 8,
      symbol: 'circle',
      itemStyle: { color: (params: any) => params.dataIndex === 0 ? '#F56C6C' : '#67C23A' }
    }]
  })
}

const handleResize = () => {
  impactChart?.resize()
  radarChart?.resize()
}

// ==================== Assessment Functions ====================
const refreshAssessment = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  updateChart()
  loading.value = false
  ElMessage.success('Upgrade assessment refreshed successfully')
}

const viewDetails = (upgrade: any) => {
  selectedUpgrade.value = upgrade
  detailsVisible.value = true
}

const scheduleUpgrade = (upgrade: any) => {
  ElMessage.info(`Schedule upgrade for ${upgrade.name}`)
}

const approveUpgrade = async (upgrade: any) => {
  await ElMessageBox.confirm(
      `Approve upgrade for ${upgrade.name}?`,
      'Confirm Approval',
      {
        confirmButtonText: 'Approve',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  )
  ElMessage.success(`Upgrade for ${upgrade.name} approved`)
}

const batchUpgrade = () => {
  const selected = upgrades.value.filter(u =>
      (batchConfig.priority === 'all' || u.priority === batchConfig.priority) &&
      (batchConfig.type === 'all' || u.type === batchConfig.type)
  )

  if (selected.length === 0) {
    ElMessage.warning('No upgrades match the selected criteria')
    return
  }

  batchUpgradeVisible.value = true
}

const executeBatchUpgrade = async () => {
  const selected = upgrades.value.filter(u =>
      (batchConfig.priority === 'all' || u.priority === batchConfig.priority) &&
      (batchConfig.type === 'all' || u.type === batchConfig.type)
  )

  await ElMessageBox.confirm(
      `Schedule batch upgrade for ${selected.length} items?`,
      'Confirm Batch Upgrade',
      {
        confirmButtonText: 'Schedule',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  const scheduledDateTime = batchConfig.scheduledDate
      ? `${batchConfig.scheduledDate} ${batchConfig.scheduledTime}`
      : `today at ${batchConfig.scheduledTime}`

  ElMessage.success(`Batch upgrade scheduled for ${scheduledDateTime}`)
  batchUpgradeVisible.value = false
}

const exportAssessment = () => {
  const data = upgrades.value.map(u => ({
    ID: u.id,
    Name: u.name,
    Type: u.type,
    Device: u.device,
    CurrentVersion: u.currentVersion,
    TargetVersion: u.targetVersion,
    Priority: u.priority,
    Impact: u.impact,
    Downtime: u.downtime,
    Complexity: u.complexity,
    Risk: u.risk,
    EstimatedTime: u.estimatedTime
  }))

  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `upgrade_assessment_${new Date().toISOString()}.csv`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Assessment exported successfully')
}

const convertToCSV = (data: any[]) => {
  const headers = Object.keys(data[0])
  const rows = data.map(obj => headers.map(header => JSON.stringify(obj[header])).join(','))
  return [headers.join(','), ...rows].join('\n')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getPriorityType = (priority: string) => {
  switch (priority) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getImpactType = (impact: string) => {
  switch (impact) {
    case 'major': return 'danger'
    case 'moderate': return 'warning'
    default: return 'success'
  }
}

const getRiskType = (risk: string) => {
  switch (risk) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    default: return 'success'
  }
}

const selectedUpgrade = ref<any>(null)
</script>

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
          <span class="loading-title">Loading Upgrade Assessment</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Compatibility Center - Upgrade Assessment</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="upgrade-assessment-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <h2>Upgrade Assessment</h2>
        <el-tag type="warning" effect="dark">Compatibility Center</el-tag>
      </div>
      <div class="header-stats">
        <el-tag type="info" effect="plain">Impact Analysis | Risk Assessment</el-tag>
      </div>
    </div>

    <!-- Control Panel -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="5">
          <el-select v-model="selectedPriority" placeholder="Priority" style="width: 100%" @change="updateChart">
            <el-option v-for="p in priorityLevels" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="selectedType" placeholder="Upgrade Type" clearable style="width: 100%">
            <el-option v-for="t in upgradeTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-col>
        <el-col :span="8">
          <el-input v-model="searchKeyword" placeholder="Search upgrades..." :prefix-icon="Search" clearable />
        </el-col>
        <el-col :span="6">
          <div class="control-buttons">
            <el-button type="primary" @click="refreshAssessment" :loading="loading">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button @click="batchUpgrade">
              <el-icon><Upload /></el-icon> Batch Upgrade
            </el-button>
            <el-button @click="exportAssessment">
              <el-icon><Download /></el-icon> Export
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Statistics Cards -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon devices-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ impactAnalysis.devicesToUpgrade }}/{{ impactAnalysis.totalDevices }}</div>
            <div class="stat-label">Devices to Upgrade</div>
            <el-progress :percentage="(impactAnalysis.devicesToUpgrade / impactAnalysis.totalDevices) * 100" :color="'#E6A23C'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon downtime-icon">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ impactAnalysis.estimatedTotalDowntime }} min</div>
            <div class="stat-label">Total Estimated Downtime</div>
            <div class="stat-sub-value">Across all upgrades</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon risk-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ impactAnalysis.averageRisk }}/5</div>
            <div class="stat-label">Average Risk Score</div>
            <el-progress :percentage="(impactAnalysis.averageRisk / 5) * 100" :color="impactAnalysis.averageRisk > 3 ? '#F56C6C' : '#67C23A'" :stroke-width="6" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon priority-icon">
            <el-icon><Flag /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ impactAnalysis.criticalCount }}</div>
            <div class="stat-label">Critical Upgrades</div>
            <div class="stat-sub-value">{{ impactAnalysis.highCount }} High | {{ impactAnalysis.mediumCount }} Medium</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Chart Section -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Upgrades by Priority</span>
              <el-button text type="primary" @click="updateChart">Refresh</el-button>
            </div>
          </template>
          <div ref="chartRef" class="chart" style="height: 300px"></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>Risk Impact Analysis</span>
              <el-button text type="primary" @click="initRadarChart">Refresh</el-button>
            </div>
          </template>
          <div ref="radarChartRef" class="radar-chart" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Upgrades Table -->
    <el-card shadow="never" class="upgrades-card">
      <template #header>
        <div class="table-header">
          <span>Upgrade Assessment Results</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredUpgrades.length }} upgrades found</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredUpgrades" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="Upgrade Name" min-width="200" />
        <el-table-column prop="device" label="Device" width="180" />
        <el-table-column label="Type" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.type === 'firmware' ? 'primary' : row.type === 'driver' ? 'success' : 'warning'">
              {{ row.type.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Version" width="130" align="center">
          <template #default="{ row }">
            <span class="version-old">{{ row.currentVersion }}</span>
            <el-icon><Right /></el-icon>
            <span class="version-new">{{ row.targetVersion }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Priority" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ row.priority.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Impact" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getImpactType(row.impact)" size="small">
              {{ row.impact }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Downtime" width="100" align="center">
          <template #default="{ row }">
            {{ row.downtime }}
          </template>
        </el-table-column>
        <el-table-column label="Risk" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getRiskType(row.risk)" size="small">
              {{ row.risk }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button link type="success" size="small" @click="approveUpgrade(row)">
              Approve
            </el-button>
            <el-button link type="warning" size="small" @click="scheduleUpgrade(row)">
              Schedule
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Upgrade Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="`Upgrade Assessment - ${selectedUpgrade?.name}`" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Upgrade ID">{{ selectedUpgrade?.id }}</el-descriptions-item>
        <el-descriptions-item label="Upgrade Name">{{ selectedUpgrade?.name }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedUpgrade?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Device">{{ selectedUpgrade?.device }}</el-descriptions-item>
        <el-descriptions-item label="Current Version">{{ selectedUpgrade?.currentVersion }}</el-descriptions-item>
        <el-descriptions-item label="Target Version">{{ selectedUpgrade?.targetVersion }}</el-descriptions-item>
        <el-descriptions-item label="Priority">
          <el-tag :type="getPriorityType(selectedUpgrade?.priority)" size="small">
            {{ selectedUpgrade?.priority?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Impact">
          <el-tag :type="getImpactType(selectedUpgrade?.impact)" size="small">
            {{ selectedUpgrade?.impact }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Estimated Downtime">{{ selectedUpgrade?.downtime }}</el-descriptions-item>
        <el-descriptions-item label="Implementation Time">{{ selectedUpgrade?.estimatedTime }}</el-descriptions-item>
        <el-descriptions-item label="Complexity">{{ selectedUpgrade?.complexity }}</el-descriptions-item>
        <el-descriptions-item label="Risk">
          <el-tag :type="getRiskType(selectedUpgrade?.risk)" size="small">
            {{ selectedUpgrade?.risk }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Compatibility">
          <el-tag :type="selectedUpgrade?.compatibility === 'full' ? 'success' : 'warning'" size="small">
            {{ selectedUpgrade?.compatibility === 'full' ? 'Full' : 'Partial' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Benefits" :span="2">
          <div class="benefits-list">
            <el-tag v-for="benefit in selectedUpgrade?.benefits" :key="benefit" type="success" size="small" style="margin: 2px">
              {{ benefit }}
            </el-tag>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Prerequisites" :span="2">
          <div class="prereqs-list">
            <el-tag v-for="prereq in selectedUpgrade?.prerequisites" :key="prereq" type="warning" size="small" style="margin: 2px">
              {{ prereq }}
            </el-tag>
            <span v-if="!selectedUpgrade?.prerequisites?.length" class="no-prereqs">No prerequisites</span>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="approveUpgrade(selectedUpgrade)">Approve Upgrade</el-button>
        <el-button type="warning" @click="scheduleUpgrade(selectedUpgrade)">Schedule</el-button>
      </template>
    </el-dialog>

    <!-- Batch Upgrade Dialog -->
    <el-dialog v-model="batchUpgradeVisible" title="Batch Upgrade Configuration" width="500px">
      <el-form :model="batchConfig" label-width="120px">
        <el-form-item label="Priority Filter">
          <el-select v-model="batchConfig.priority" style="width: 100%">
            <el-option v-for="p in priorityLevels" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Type Filter">
          <el-select v-model="batchConfig.type" style="width: 100%">
            <el-option v-for="t in upgradeTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule Date">
          <el-date-picker v-model="batchConfig.scheduledDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Schedule Time">
          <el-time-picker v-model="batchConfig.scheduledTime" format="HH:mm" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Notify Before">
          <el-switch v-model="batchConfig.notifyBefore" />
        </el-form-item>
        <el-form-item label="Auto Rollback">
          <el-switch v-model="batchConfig.autoRollback" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchUpgradeVisible = false">Cancel</el-button>
        <el-button type="primary" @click="executeBatchUpgrade">Schedule Batch Upgrade</el-button>
      </template>
    </el-dialog>
  </div>
</template>

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
.upgrade-assessment-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e4e7ed;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.control-card {
  margin-bottom: 20px;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
}

.devices-icon {
  background-color: #e6f7ff;
  color: #409eff;
}

.downtime-icon {
  background-color: #f0f9ff;
  color: #67c23a;
}

.risk-icon {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.priority-icon {
  background-color: #fef0f0;
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-sub-value {
  font-size: 12px;
  color: #67c23a;
  margin-top: 2px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  height: 370px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upgrades-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.chart,
.radar-chart {
  width: 100%;
}

.version-old {
  color: #909399;
  text-decoration: line-through;
  font-size: 12px;
  margin-right: 4px;
}

.version-new {
  color: #67c23a;
  font-weight: bold;
  margin-left: 4px;
}

.benefits-list,
.prereqs-list {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.no-prereqs {
  color: #909399;
  font-style: italic;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #ebeef5;
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}

@media (max-width: 1200px) {
  .table-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .control-buttons {
    justify-content: flex-start;
    margin-top: 10px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>