<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Search as SearchIcon, Link, Aim, SuccessFilled
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing diagnostic engine...',
  'Analyzing fault patterns...',
  'Tracing root causes...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedSeverity = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const chartRef = ref(null)
const treeRef = ref(null)

let causeChart: echarts.ECharts | null = null
let treeChart: echarts.ECharts | null = null

// Severity filters
const severityOptions = [
  { value: 'all', label: 'All Severities' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'investigating', label: 'Investigating' },
  { value: 'identified', label: 'Root Cause Identified' },
  { value: 'resolved', label: 'Resolved' }
]

// Root cause analysis data
const incidents = ref([
  {
    id: 'INC001', fault: 'Chiller-1 High Temperature Alarm', severity: 'critical',
    timestamp: '2024-01-15 10:23:45', status: 'identified',
    rootCause: 'Compressor failure due to refrigerant leak',
    symptoms: ['Temperature spike to 35°C', 'Increased vibration', 'Unusual noise'],
    contributingFactors: ['Age of equipment (8 years)', 'Missed maintenance cycle', 'Low refrigerant levels'],
    solution: 'Replace compressor and repair leak',
    confidence: 92, resolvedBy: 'HVAC Team', resolvedAt: null,
    affectedSystems: ['HVAC', 'Building Automation']
  },
  {
    id: 'INC002', fault: 'AHU-2 Airflow Low', severity: 'high',
    timestamp: '2024-01-14 14:30:00', status: 'investigating',
    rootCause: null,
    symptoms: ['Airflow reduced by 40%', 'Filter pressure high', 'Fan speed increased'],
    contributingFactors: ['Duct blockage suspected', 'Filter clogging'],
    solution: null,
    confidence: 65, resolvedBy: null, resolvedAt: null,
    affectedSystems: ['HVAC', 'Air Distribution']
  },
  {
    id: 'INC003', fault: 'Main Switchboard Overheat', severity: 'high',
    timestamp: '2024-01-14 09:15:22', status: 'identified',
    rootCause: 'Loose connection at main breaker',
    symptoms: ['Temperature 78°C', 'Voltage fluctuation', 'Burning smell reported'],
    contributingFactors: ['Thermal expansion', 'Vibration from nearby equipment'],
    solution: 'Tighten connections and thermal scan',
    confidence: 88, resolvedBy: 'Electrical Team', resolvedAt: null,
    affectedSystems: ['Electrical', 'Power Distribution']
  },
  {
    id: 'INC004', fault: 'VFD Pump Vibration High', severity: 'medium',
    timestamp: '2024-01-13 11:20:15', status: 'resolved',
    rootCause: 'Bearing wear and misalignment',
    symptoms: ['Vibration 4.2 mm/s', 'Unusual noise', 'Temperature elevated'],
    contributingFactors: ['Normal wear', 'Lack of lubrication'],
    solution: 'Replace bearings and realign shaft',
    confidence: 94, resolvedBy: 'Mechanical Team', resolvedAt: '2024-01-14',
    affectedSystems: ['Pump', 'Water Distribution']
  },
  {
    id: 'INC005', fault: 'Cooling Tower Fan Failure', severity: 'critical',
    timestamp: '2024-01-12 16:45:33', status: 'identified',
    rootCause: 'Motor winding failure',
    symptoms: ['Fan not spinning', 'Burning smell', 'Breaker tripped'],
    contributingFactors: ['Age (10 years)', 'Overload condition'],
    solution: 'Replace fan motor',
    confidence: 96, resolvedBy: 'HVAC Team', resolvedAt: null,
    affectedSystems: ['HVAC', 'Cooling']
  },
  {
    id: 'INC006', fault: 'Network Switch Intermittent', severity: 'medium',
    timestamp: '2024-01-12 08:30:00', status: 'resolved',
    rootCause: 'Faulty power supply',
    symptoms: ['Random reboots', 'Packet loss 15%', 'Error logs'],
    contributingFactors: ['Power surge', 'Age of equipment'],
    solution: 'Replace power supply unit',
    confidence: 91, resolvedBy: 'IT Team', resolvedAt: '2024-01-13',
    affectedSystems: ['Network', 'Building Automation']
  },
  {
    id: 'INC007', fault: 'Lighting Panel Communication Loss', severity: 'low',
    timestamp: '2024-01-11 10:00:00', status: 'investigating',
    rootCause: null,
    symptoms: ['No response from controller', 'LED error indicator'],
    contributingFactors: ['Possible firmware issue', 'Network configuration'],
    solution: null,
    confidence: 45, resolvedBy: null, resolvedAt: null,
    affectedSystems: ['Lighting', 'Control System']
  },
  {
    id: 'INC008', fault: 'Chiller-2 Low Efficiency', severity: 'medium',
    timestamp: '2024-01-10 13:20:00', status: 'identified',
    rootCause: 'Refrigerant undercharge',
    symptoms: ['Efficiency drop 25%', 'Longer run times', 'Higher energy consumption'],
    contributingFactors: ['Slow leak over time', 'Previous repairs'],
    solution: 'Locate and repair leak, recharge system',
    confidence: 86, resolvedBy: 'HVAC Team', resolvedAt: null,
    affectedSystems: ['HVAC', 'Chiller Plant']
  }
])

// Analysis statistics
const analysisStats = reactive({
  total: 0,
  critical: 0,
  high: 0,
  medium: 0,
  low: 0,
  identified: 0,
  investigating: 0,
  resolved: 0,
  avgConfidence: 0,
  topCause: ''
})

// Cause distribution data for pie chart
const causeDistribution = ref([
  { name: 'Mechanical Wear', value: 3, color: '#F56C6C' },
  { name: 'Electrical Issues', value: 2, color: '#E6A23C' },
  { name: 'Refrigerant Problems', value: 2, color: '#67C23A' },
  { name: 'Maintenance Neglect', value: 1, color: '#409EFF' }
])

// Tree data for root cause tree
const treeData = ref({
  name: 'Fault: Chiller High Temperature',
  children: [
    { name: 'Primary Causes', children: [
        { name: 'Compressor Issues', children: [
            { name: 'Worn Bearings', status: 'confirmed' },
            { name: 'Motor Failure', status: 'suspected' }
          ] },
        { name: 'Refrigerant Problems', children: [
            { name: 'Low Charge', status: 'confirmed' },
            { name: 'Contamination', status: 'excluded' }
          ] }
      ] },
    { name: 'Secondary Factors', children: [
        { name: 'Cooling Issues', children: [
            { name: 'Condenser Fouling', status: 'suspected' },
            { name: 'Fan Speed Low', status: 'excluded' }
          ] },
        { name: 'Electrical', children: [
            { name: 'Voltage Fluctuation', status: 'confirmed' },
            { name: 'Phase Imbalance', status: 'excluded' }
          ] }
      ] }
  ]
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: incidents.value.length
})

// Filtered incidents
const filteredIncidents = computed(() => {
  let filtered = incidents.value
  if (searchKeyword.value) {
    filtered = filtered.filter(i =>
        i.fault.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        i.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(i => i.severity === selectedSeverity.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(i => i.status === selectedStatus.value)
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
        initTreeChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  causeChart = echarts.init(chartRef.value)
  causeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c})' },
    legend: { orient: 'vertical', left: 'left', data: causeDistribution.value.map(c => c.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: causeDistribution.value.map(c => ({ name: c.name, value: c.value })),
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' },
      itemStyle: { color: (params: any) => causeDistribution.value[params.dataIndex].color }
    }]
  })
}

const initTreeChart = () => {
  if (!treeRef.value) return

  // Convert tree data for echarts
  const convertToEchartsTree = (node: any) => {
    return {
      name: node.name,
      children: node.children?.map((child: any) => convertToEchartsTree(child)),
      itemStyle: node.status ? {
        color: node.status === 'confirmed' ? '#F56C6C' : node.status === 'suspected' ? '#E6A23C' : '#67C23A'
      } : undefined
    }
  }

  treeChart = echarts.init(treeRef.value)
  treeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}' },
    series: [{
      type: 'tree',
      data: [convertToEchartsTree(treeData.value)],
      left: '2%',
      right: '2%',
      top: '8%',
      bottom: '8%',
      symbol: 'emptyCircle',
      symbolSize: 15,
      orient: 'LR',
      expandAndCollapse: true,
      initialTreeDepth: 2,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 11,
        offset: [5, 0]
      },
      leaves: { label: { position: 'right', align: 'left' } },
      lineStyle: { color: '#ccc', width: 1.5, curveness: 0.5 },
      itemStyle: {
        borderColor: '#409EFF',
        borderWidth: 1.5
      }
    }]
  })
}

const updateStats = () => {
  analysisStats.total = incidents.value.length
  analysisStats.critical = incidents.value.filter(i => i.severity === 'critical').length
  analysisStats.high = incidents.value.filter(i => i.severity === 'high').length
  analysisStats.medium = incidents.value.filter(i => i.severity === 'medium').length
  analysisStats.low = incidents.value.filter(i => i.severity === 'low').length
  analysisStats.identified = incidents.value.filter(i => i.status === 'identified').length
  analysisStats.investigating = incidents.value.filter(i => i.status === 'investigating').length
  analysisStats.resolved = incidents.value.filter(i => i.status === 'resolved').length

  const confidences = incidents.value.filter(i => i.confidence).map(i => i.confidence)
  if (confidences.length > 0) {
    analysisStats.avgConfidence = Math.round(confidences.reduce((a, b) => a + b, 0) / confidences.length)
  }

  // Most common root cause
  const causes = incidents.value.filter(i => i.rootCause).map(i => i.rootCause.split(' ')[0])
  if (causes.length > 0) {
    const causeCount = new Map()
    causes.forEach(c => causeCount.set(c, (causeCount.get(c) || 0) + 1))
    analysisStats.topCause = Array.from(causeCount.entries()).reduce((a, b) => a[1] > b[1] ? a : b)[0]
  }
}

const handleResize = () => {
  causeChart?.resize()
  treeChart?.resize()
}

// ==================== Analysis Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Analysis data refreshed successfully')
}

const viewDetails = (incident: any) => {
  selectedIncident.value = incident
  detailsVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical': return '#F56C6C'
    case 'high': return '#F56C6C'
    case 'medium': return '#E6A23C'
    case 'low': return '#67C23A'
    default: return '#909399'
  }
}

const getSeverityIcon = (severity: string) => {
  switch (severity) {
    case 'critical': return '🔴'
    case 'high': return '🟠'
    case 'medium': return '🟡'
    case 'low': return '🟢'
    default: return '⚪'
  }
}

const getStatusTag = (status: string) => {
  switch (status) {
    case 'identified': return { type: 'success', text: 'Root Cause Identified' }
    case 'investigating': return { type: 'warning', text: 'Investigating' }
    case 'resolved': return { type: 'info', text: 'Resolved' }
    default: return { type: 'info', text: status }
  }
}

const selectedIncident = ref<any>(null)
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
          <span class="loading-title">Loading Root Cause Analysis</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Fault Diagnostics - Root Cause Analysis</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="root-cause-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Root Cause Analysis</h1>
        <p class="page-subtitle">AI-powered fault diagnosis and root cause identification</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshData" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ analysisStats.total }}</div>
          <div class="stat-label">Total Incidents</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ analysisStats.critical }} Critical</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon identified-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ analysisStats.identified }}</div>
          <div class="stat-label">Root Cause Identified</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="(analysisStats.identified / analysisStats.total) * 100" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon confidence-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ analysisStats.avgConfidence }}%</div>
          <div class="stat-label">Avg Diagnosis Confidence</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+8% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon resolved-icon">
          <el-icon><SuccessFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ analysisStats.resolved }}</div>
          <div class="stat-label">Resolved</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ analysisStats.investigating }} Investigating</span>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-section">
        <div class="section-header">
          <h3>Root Cause Distribution</h3>
          <el-button text type="primary" @click="initChart">Refresh</el-button>
        </div>
        <div ref="chartRef" class="cause-chart" style="height: 300px"></div>
      </div>

      <div class="chart-section">
        <div class="section-header">
          <h3>Root Cause Tree (Example: Chiller High Temperature)</h3>
          <el-button text type="primary" @click="initTreeChart">Refresh</el-button>
        </div>
        <div ref="treeRef" class="tree-chart" style="height: 300px"></div>
      </div>
    </div>

    <!-- Legend -->
    <div class="severity-legend">
      <div class="legend-item">
        <span class="legend-dot critical"></span>
        <span>Critical</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot high"></span>
        <span>High</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot medium"></span>
        <span>Medium</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot low"></span>
        <span>Low</span>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search incidents..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="severity-filters">
          <button
              v-for="s in severityOptions"
              :key="s.value"
              class="severity-chip"
              :class="{ active: selectedSeverity === s.value }"
              @click="selectedSeverity = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
      </div>
      <div class="filters-right">
        <el-select v-model="selectedStatus" placeholder="Status" clearable style="width: 160px">
          <el-option v-for="s in statusOptions.slice(1)" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </div>
    </div>

    <!-- Incidents Table -->
    <el-card shadow="never" class="incidents-card">
      <template #header>
        <div class="table-header">
          <span>Fault Incidents & Root Cause Analysis</span>
          <div class="table-actions">
            <el-tag type="info" size="small">{{ filteredIncidents.length }} incidents</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="filteredIncidents" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="fault" label="Fault Description" min-width="250" />
        <el-table-column label="Severity" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.severity === 'critical' || row.severity === 'high' ? 'danger' : row.severity === 'medium' ? 'warning' : 'success'" size="small">
              {{ getSeverityIcon(row.severity) }} {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="150" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status).type" size="small">
              {{ getStatusTag(row.status).text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column label="Root Cause" min-width="200">
          <template #default="{ row }">
            <span v-if="row.rootCause" class="root-cause-text">{{ row.rootCause }}</span>
            <span v-else class="no-cause">-- Investigating --</span>
          </template>
        </el-table-column>
        <el-table-column label="Confidence" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.confidence">
              <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="false" />
              <span style="font-size: 12px">{{ row.confidence }}%</span>
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
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
            :page-sizes="[8, 12, 16, 24]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- Incident Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedIncident?.fault" width="700px">
      <div class="dialog-content">
        <div class="incident-summary" :class="selectedIncident?.severity">
          <div class="severity-badge">
            {{ getSeverityIcon(selectedIncident?.severity) }} {{ selectedIncident?.severity?.toUpperCase() }}
          </div>
          <div class="incident-id">{{ selectedIncident?.id }}</div>
          <div class="incident-time">{{ selectedIncident?.timestamp }}</div>
        </div>

        <el-divider />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(selectedIncident?.status).type" size="small">
              {{ getStatusTag(selectedIncident?.status).text }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Confidence" v-if="selectedIncident?.confidence">
            {{ selectedIncident?.confidence }}%
          </el-descriptions-item>
          <el-descriptions-item label="Root Cause" :span="2" v-if="selectedIncident?.rootCause">
            <strong>{{ selectedIncident?.rootCause }}</strong>
          </el-descriptions-item>
          <el-descriptions-item label="Symptoms" :span="2">
            <div class="symptoms-list">
              <el-tag v-for="symptom in selectedIncident?.symptoms" :key="symptom" size="small" style="margin: 2px">
                {{ symptom }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Contributing Factors" :span="2">
            <div class="factors-list">
              <el-tag v-for="factor in selectedIncident?.contributingFactors" :key="factor" type="warning" size="small" style="margin: 2px">
                {{ factor }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Affected Systems" :span="2">
            <div class="systems-list">
              <el-tag v-for="system in selectedIncident?.affectedSystems" :key="system" type="primary" size="small" style="margin: 2px">
                {{ system }}
              </el-tag>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Solution" :span="2" v-if="selectedIncident?.solution">
            {{ selectedIncident?.solution }}
          </el-descriptions-item>
          <el-descriptions-item label="Resolved By" v-if="selectedIncident?.resolvedBy">
            {{ selectedIncident?.resolvedBy }}
          </el-descriptions-item>
          <el-descriptions-item label="Resolved At" v-if="selectedIncident?.resolvedAt">
            {{ selectedIncident?.resolvedAt }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="!selectedIncident?.rootCause" class="investigating-alert">
          <el-alert
              title="Investigation in Progress"
              type="warning"
              show-icon
              :closable="false"
          >
            <template #default>
              <p>Root cause analysis is ongoing. Check back for updates.</p>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button v-if="selectedIncident?.status !== 'resolved'" type="primary">Mark Resolved</el-button>
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
.root-cause-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.identified-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.confidence-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.resolved-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.cause-chart,
.tree-chart {
  width: 100%;
}

/* Severity Legend */
.severity-legend {
  display: flex;
  justify-content: center;
  gap: 32px;
  margin-bottom: 24px;
  padding: 12px 20px;
  background: white;
  border-radius: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.critical { background: #F56C6C; }
.legend-dot.high { background: #F56C6C; }
.legend-dot.medium { background: #E6A23C; }
.legend-dot.low { background: #67C23A; }

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.severity-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.severity-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 40px;
  font-size: 13px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.severity-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.severity-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.filters-right {
  display: flex;
  gap: 12px;
}

/* Incidents Card */
.incidents-card {
  margin-top: 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

/* Table Cell Styles */
.root-cause-text {
  color: #67c23a;
  font-weight: 500;
}

.no-cause {
  color: #e6a23c;
  font-style: italic;
}

/* Dialog Styles */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.incident-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: 12px;
}

.incident-summary.critical {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
}

.incident-summary.high {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
}

.incident-summary.medium {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
}

.incident-summary.low {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
}

.severity-badge {
  font-size: 14px;
  font-weight: 600;
}

.incident-summary.critical .severity-badge { color: #f56c6c; }
.incident-summary.high .severity-badge { color: #f56c6c; }
.incident-summary.medium .severity-badge { color: #e6a23c; }
.incident-summary.low .severity-badge { color: #67c23a; }

.incident-id, .incident-time {
  font-size: 13px;
  color: #606266;
}

.symptoms-list,
.factors-list,
.systems-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.investigating-alert {
  margin-top: 10px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .root-cause-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .severity-filters {
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .incident-summary {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }

  .severity-legend {
    flex-direction: column;
    align-items: center;
  }
}
</style>