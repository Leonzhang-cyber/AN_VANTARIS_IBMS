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
  Link, Aim, SuccessFilled, Connection as ConnectionIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing correlation engine...',
  'Analyzing fault patterns...',
  'Building correlation graph...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedSeverity = ref('all')
const detailsVisible = ref(false)
const graphRef = ref(null)
const chartRef = ref(null)

let correlationGraph: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null

// Severity filters
const severityOptions = [
  { value: 'all', label: 'All Severities' },
  { value: 'critical', label: 'Critical', color: '#F56C6C' },
  { value: 'high', label: 'High', color: '#F56C6C' },
  { value: 'medium', label: 'Medium', color: '#E6A23C' },
  { value: 'low', label: 'Low', color: '#67C23A' }
]

// Fault correlation data
const faultClusters = ref([
  {
    id: 'CLUSTER001', rootFault: 'Chiller High Temperature',
    severity: 'critical', confidence: 92,
    relatedFaults: [
      { name: 'Cooling Tower Fan Failure', relationship: 'causes', severity: 'critical' },
      { name: 'High Pressure Alarm', relationship: 'triggered_by', severity: 'high' },
      { name: 'Compressor Cycling', relationship: 'symptom_of', severity: 'medium' },
      { name: 'Low Refrigerant Level', relationship: 'root_cause', severity: 'high' }
    ],
    timestamp: '2024-01-15 10:23:45', resolved: false
  },
  {
    id: 'CLUSTER002', rootFault: 'AHU Low Airflow',
    severity: 'high', confidence: 88,
    relatedFaults: [
      { name: 'Clogged Filters', relationship: 'root_cause', severity: 'low' },
      { name: 'Duct Blockage', relationship: 'root_cause', severity: 'medium' },
      { name: 'Fan Motor Overload', relationship: 'caused_by', severity: 'high' },
      { name: 'Poor Indoor Air Quality', relationship: 'results_in', severity: 'medium' }
    ],
    timestamp: '2024-01-14 14:30:00', resolved: true
  },
  {
    id: 'CLUSTER003', rootFault: 'Switchboard Overheating',
    severity: 'critical', confidence: 91,
    relatedFaults: [
      { name: 'Loose Connections', relationship: 'root_cause', severity: 'high' },
      { name: 'Phase Imbalance', relationship: 'contributing_factor', severity: 'medium' },
      { name: 'Voltage Fluctuation', relationship: 'symptom_of', severity: 'high' },
      { name: 'Breaker Tripping', relationship: 'results_in', severity: 'critical' }
    ],
    timestamp: '2024-01-14 09:15:22', resolved: false
  },
  {
    id: 'CLUSTER004', rootFault: 'VFD Pump Vibration',
    severity: 'medium', confidence: 94,
    relatedFaults: [
      { name: 'Bearing Wear', relationship: 'root_cause', severity: 'medium' },
      { name: 'Shaft Misalignment', relationship: 'root_cause', severity: 'medium' },
      { name: 'Cavitation', relationship: 'contributing_factor', severity: 'low' },
      { name: 'Seal Leakage', relationship: 'related_to', severity: 'low' }
    ],
    timestamp: '2024-01-13 11:20:15', resolved: true
  }
])

// Graph data for visualization
const graphData = ref({
  nodes: [
    { name: 'Chiller High Temperature', category: 'root', symbolSize: 40, itemStyle: { color: '#F56C6C' } },
    { name: 'Cooling Tower Fan Failure', category: 'related', symbolSize: 30, itemStyle: { color: '#F56C6C' } },
    { name: 'High Pressure Alarm', category: 'related', symbolSize: 25, itemStyle: { color: '#E6A23C' } },
    { name: 'Compressor Cycling', category: 'related', symbolSize: 25, itemStyle: { color: '#E6A23C' } },
    { name: 'Low Refrigerant Level', category: 'related', symbolSize: 28, itemStyle: { color: '#F56C6C' } },
    { name: 'AHU Low Airflow', category: 'root', symbolSize: 40, itemStyle: { color: '#E6A23C' } },
    { name: 'Clogged Filters', category: 'related', symbolSize: 22, itemStyle: { color: '#67C23A' } },
    { name: 'Fan Motor Overload', category: 'related', symbolSize: 28, itemStyle: { color: '#E6A23C' } },
    { name: 'Switchboard Overheating', category: 'root', symbolSize: 40, itemStyle: { color: '#F56C6C' } },
    { name: 'Loose Connections', category: 'related', symbolSize: 28, itemStyle: { color: '#E6A23C' } },
    { name: 'Breaker Tripping', category: 'related', symbolSize: 30, itemStyle: { color: '#F56C6C' } }
  ],
  links: [
    { source: 'Chiller High Temperature', target: 'Cooling Tower Fan Failure' },
    { source: 'Chiller High Temperature', target: 'High Pressure Alarm' },
    { source: 'Chiller High Temperature', target: 'Compressor Cycling' },
    { source: 'Chiller High Temperature', target: 'Low Refrigerant Level' },
    { source: 'AHU Low Airflow', target: 'Clogged Filters' },
    { source: 'AHU Low Airflow', target: 'Fan Motor Overload' },
    { source: 'Switchboard Overheating', target: 'Loose Connections' },
    { source: 'Switchboard Overheating', target: 'Breaker Tripping' }
  ],
  categories: [
    { name: 'Root Fault', itemStyle: { color: '#F56C6C' } },
    { name: 'Related Fault', itemStyle: { color: '#E6A23C' } }
  ]
})

// Timeline data
const timelineData = ref([
  { time: '00:00', faults: 2, correlations: 1 },
  { time: '02:00', faults: 3, correlations: 2 },
  { time: '04:00', faults: 4, correlations: 3 },
  { time: '06:00', faults: 6, correlations: 4 },
  { time: '08:00', faults: 12, correlations: 8 },
  { time: '10:00', faults: 15, correlations: 10 },
  { time: '12:00', faults: 18, correlations: 12 },
  { time: '14:00', faults: 14, correlations: 9 },
  { time: '16:00', faults: 10, correlations: 7 },
  { time: '18:00', faults: 8, correlations: 5 },
  { time: '20:00', faults: 5, correlations: 3 },
  { time: '22:00', faults: 3, correlations: 2 }
])

// Correlation statistics
const correlationStats = reactive({
  totalClusters: 0,
  activeClusters: 0,
  resolvedClusters: 0,
  totalCorrelations: 0,
  avgConfidence: 0,
  criticalCount: 0
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 6,
  total: faultClusters.value.length
})

// Filtered clusters
const filteredClusters = computed(() => {
  let filtered = faultClusters.value
  if (searchKeyword.value) {
    filtered = filtered.filter(c =>
        c.rootFault.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.id.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedSeverity.value !== 'all') {
    filtered = filtered.filter(c => c.severity === selectedSeverity.value)
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
        initGraph()
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initGraph = () => {
  if (!graphRef.value) return

  correlationGraph = echarts.init(graphRef.value)
  correlationGraph.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<strong>${params.name}</strong><br/>Type: ${params.data.category === 'root' ? 'Root Fault' : 'Related Fault'}`
        }
        return `${params.data.source} → ${params.data.target}`
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      data: graphData.value.nodes,
      links: graphData.value.links,
      categories: graphData.value.categories,
      roam: true,
      draggable: true,
      focusNodeAdjacency: true,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 8],
      label: {
        show: true,
        position: 'right',
        fontSize: 11,
        formatter: (params: any) => params.name,
        offset: [5, 0]
      },
      force: {
        repulsion: 500,
        edgeLength: 150,
        gravity: 0.1,
        friction: 0.1,
        layoutAnimation: true
      },
      lineStyle: {
        color: '#ccc',
        curveness: 0.3,
        width: 1.5
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 2,
          color: '#409EFF'
        }
      },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2,
        shadowBlur: 10,
        shadowColor: 'rgba(0,0,0,0.3)'
      }
    }]
  })
}

const initChart = () => {
  if (!chartRef.value) return

  timelineChart = echarts.init(chartRef.value)
  timelineChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Faults', 'Correlations'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: timelineData.value.map(t => t.time) },
    yAxis: { type: 'value', name: 'Count' },
    series: [
      { name: 'Faults', type: 'line', data: timelineData.value.map(t => t.faults), smooth: true, lineStyle: { color: '#F56C6C', width: 2 }, areaStyle: { opacity: 0.1, color: '#F56C6C' }, symbol: 'circle', symbolSize: 8 },
      { name: 'Correlations', type: 'bar', data: timelineData.value.map(t => t.correlations), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  correlationStats.totalClusters = faultClusters.value.length
  correlationStats.activeClusters = faultClusters.value.filter(c => !c.resolved).length
  correlationStats.resolvedClusters = faultClusters.value.filter(c => c.resolved).length
  correlationStats.totalCorrelations = faultClusters.value.reduce((sum, c) => sum + c.relatedFaults.length, 0)
  correlationStats.avgConfidence = Math.round(faultClusters.value.reduce((sum, c) => sum + c.confidence, 0) / faultClusters.value.length)
  correlationStats.criticalCount = faultClusters.value.filter(c => c.severity === 'critical').length
}

const handleResize = () => {
  correlationGraph?.resize()
  timelineChart?.resize()
}

// ==================== Correlation Functions ====================
const refreshData = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Correlation data refreshed successfully')
}

const viewDetails = (cluster: any) => {
  selectedCluster.value = cluster
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

const getRelationshipText = (relationship: string) => {
  const map: Record<string, string> = {
    'causes': 'Causes',
    'triggered_by': 'Triggered By',
    'symptom_of': 'Symptom Of',
    'root_cause': 'Root Cause',
    'caused_by': 'Caused By',
    'results_in': 'Results In',
    'contributing_factor': 'Contributing Factor',
    'related_to': 'Related To'
  }
  return map[relationship] || relationship
}

const selectedCluster = ref<any>(null)
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
          <span class="loading-title">Loading Fault Correlation</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Fault Diagnostics - Fault Correlation</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="fault-correlation-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Fault Correlation</h1>
        <p class="page-subtitle">Intelligent fault correlation and root cause analysis</p>
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
        <div class="stat-icon clusters-icon">
          <el-icon><ConnectionIcon /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ correlationStats.totalClusters }}</div>
          <div class="stat-label">Fault Clusters</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ correlationStats.activeClusters }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon correlations-icon">
          <el-icon><Link /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ correlationStats.totalCorrelations }}</div>
          <div class="stat-label">Total Correlations</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+5 this week</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon confidence-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ correlationStats.avgConfidence }}%</div>
          <div class="stat-label">Avg Confidence</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="correlationStats.avgConfidence" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon resolved-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ correlationStats.resolvedClusters }}</div>
          <div class="stat-label">Resolved</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ correlationStats.criticalCount }} Critical</span>
        </div>
      </div>
    </div>

    <!-- Correlation Graph Section -->
    <div class="graph-section">
      <div class="section-header">
        <h3>Fault Correlation Graph</h3>
        <div class="graph-legend">
          <span class="legend-dot root"></span>
          <span>Root Fault</span>
          <span class="legend-dot related"></span>
          <span>Related Fault</span>
        </div>
        <el-button text type="primary" @click="initGraph">Refresh Graph</el-button>
      </div>
      <div ref="graphRef" class="correlation-graph" style="height: 450px"></div>
    </div>

    <!-- Timeline Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Fault & Correlation Timeline (24 Hours)</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="timeline-chart" style="height: 300px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search fault clusters..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="severity-filters">
          <span class="filter-label">Severity:</span>
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
    </div>

    <!-- Fault Clusters Grid -->
    <div class="clusters-grid">
      <div
          v-for="cluster in filteredClusters"
          :key="cluster.id"
          class="cluster-card"
          :class="cluster.severity"
          @click="viewDetails(cluster)"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="cluster-severity">
            <span class="severity-icon">{{ getSeverityIcon(cluster.severity) }}</span>
            <span class="severity-text">{{ cluster.severity.toUpperCase() }}</span>
          </div>
          <div class="cluster-confidence">
            {{ cluster.confidence }}% confidence
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="root-fault">{{ cluster.rootFault }}</h4>
          <div class="related-count">
            <el-icon><Link /></el-icon>
            {{ cluster.relatedFaults.length }} related faults
          </div>
          <div class="related-preview">
            <div
                v-for="fault in cluster.relatedFaults.slice(0, 3)"
                :key="fault.name"
                class="related-item"
            >
              <span class="rel-icon">↳</span>
              <span class="rel-name">{{ fault.name }}</span>
              <span class="rel-relationship">{{ getRelationshipText(fault.relationship) }}</span>
            </div>
            <div v-if="cluster.relatedFaults.length > 3" class="more-related">
              +{{ cluster.relatedFaults.length - 3 }} more
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="timestamp">
            <el-icon><Clock /></el-icon>
            {{ cluster.timestamp }}
          </div>
          <div class="status-badge" :class="{ resolved: cluster.resolved }">
            {{ cluster.resolved ? 'Resolved' : 'Active' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredClusters.length === 0" class="empty-state">
      <el-empty description="No fault clusters found">
        <el-button type="primary">Reset Filters</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredClusters.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[6, 9, 12, 18]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Fault Cluster Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedCluster?.rootFault" width="650px">
      <div class="dialog-content">
        <div class="cluster-summary" :class="selectedCluster?.severity">
          <div class="summary-header">
            <span class="severity-badge">{{ getSeverityIcon(selectedCluster?.severity) }} {{ selectedCluster?.severity?.toUpperCase() }}</span>
            <span class="confidence-badge">{{ selectedCluster?.confidence }}% Confidence</span>
          </div>
          <div class="summary-id">Cluster ID: {{ selectedCluster?.id }}</div>
          <div class="summary-time">{{ selectedCluster?.timestamp }}</div>
        </div>

        <el-divider />

        <h4>Related Faults</h4>
        <el-table :data="selectedCluster?.relatedFaults" stripe style="width: 100%">
          <el-table-column prop="name" label="Fault Name" min-width="200" />
          <el-table-column label="Relationship" width="150">
            <template #default="{ row }">
              {{ getRelationshipText(row.relationship) }}
            </template>
          </el-table-column>
          <el-table-column label="Severity" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.severity === 'critical' || row.severity === 'high' ? 'danger' : row.severity === 'medium' ? 'warning' : 'success'" size="small">
                {{ row.severity.toUpperCase() }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="recommendation-section">
          <h4>Recommendation</h4>
          <el-alert
              :title="selectedCluster?.resolved ? 'This fault cluster has been resolved' : 'Investigate root cause and related faults'"
              :type="selectedCluster?.resolved ? 'success' : 'warning'"
              show-icon
              :closable="false"
          >
            <template #default>
              <p v-if="!selectedCluster?.resolved">
                Priority: {{ selectedCluster?.severity === 'critical' ? 'Immediate action required' : 'Schedule investigation within 7 days' }}
              </p>
            </template>
          </el-alert>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button v-if="!selectedCluster?.resolved" type="primary">Mark Resolved</el-button>
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
.fault-correlation-container {
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

.clusters-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.correlations-icon {
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

/* Graph Section */
.graph-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.graph-legend {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}

.legend-dot.root {
  background: #f56c6c;
}

.legend-dot.related {
  background: #e6a23c;
}

.correlation-graph {
  width: 100%;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.timeline-chart {
  width: 100%;
}

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

.filter-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-right: 8px;
}

.severity-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.severity-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  font-size: 12px;
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

/* Clusters Grid */
.clusters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.cluster-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.cluster-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.cluster-card.critical {
  border-left: 4px solid #f56c6c;
}

.cluster-card.high {
  border-left: 4px solid #f56c6c;
}

.cluster-card.medium {
  border-left: 4px solid #e6a23c;
}

.cluster-card.low {
  border-left: 4px solid #67c23a;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 8px 20px;
}

.cluster-severity {
  display: flex;
  align-items: center;
  gap: 6px;
}

.severity-icon {
  font-size: 14px;
}

.severity-text {
  font-size: 12px;
  font-weight: 600;
}

.cluster-card.critical .severity-text { color: #f56c6c; }
.cluster-card.high .severity-text { color: #f56c6c; }
.cluster-card.medium .severity-text { color: #e6a23c; }
.cluster-card.low .severity-text { color: #67c23a; }

.cluster-confidence {
  font-size: 11px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 12px;
}

/* Card Body */
.card-body {
  padding: 0 20px 12px 20px;
}

.root-fault {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.related-count {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.related-preview {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 8px;
}

.related-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  margin-bottom: 6px;
}

.related-item:last-child {
  margin-bottom: 0;
}

.rel-icon {
  color: #909399;
}

.rel-name {
  color: #1e293b;
  flex: 1;
}

.rel-relationship {
  font-size: 10px;
  color: #909399;
  background: #eef2f6;
  padding: 2px 6px;
  border-radius: 10px;
}

.more-related {
  font-size: 11px;
  color: #409eff;
  margin-top: 6px;
  padding-left: 16px;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: #fafbfc;
  border-top: 1px solid #f0f0f0;
}

.timestamp {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
}

.status-badge {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
  background: #fef0f0;
  color: #f56c6c;
}

.status-badge.resolved {
  background: #f0f9ff;
  color: #67c23a;
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Dialog Styles */
.dialog-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cluster-summary {
  padding: 16px;
  border-radius: 12px;
}

.cluster-summary.critical {
  background: #fef0f0;
}

.cluster-summary.high {
  background: #fef0f0;
}

.cluster-summary.medium {
  background: #fdf6ec;
}

.cluster-summary.low {
  background: #f0f9ff;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.severity-badge {
  font-size: 14px;
  font-weight: 600;
}

.cluster-summary.critical .severity-badge { color: #f56c6c; }
.cluster-summary.high .severity-badge { color: #f56c6c; }
.cluster-summary.medium .severity-badge { color: #e6a23c; }
.cluster-summary.low .severity-badge { color: #67c23a; }

.confidence-badge {
  font-size: 12px;
  background: white;
  padding: 2px 8px;
  border-radius: 12px;
  color: #606266;
}

.summary-id, .summary-time {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}

.recommendation-section {
  margin-top: 10px;
}

.recommendation-section h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 10px 0;
  color: #1e293b;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .clusters-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .fault-correlation-container {
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
    align-items: stretch;
  }

  .severity-filters {
    flex-wrap: wrap;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .graph-legend {
    order: 2;
  }

  .clusters-grid {
    grid-template-columns: 1fr;
  }
}
</style>