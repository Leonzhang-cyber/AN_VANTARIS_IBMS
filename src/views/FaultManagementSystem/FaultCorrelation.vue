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
        <div class="loading-tip">Fault Correlation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Fault Correlation Page Content -->
  <div v-else class="fault-correlation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Connection /></el-icon>
          <span>FMS - Correlation</span>
        </div>
        <h1>Fault Correlation</h1>
        <p class="subtitle">Intelligent fault correlation analysis to identify root causes and cascading failures</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="runCorrelationAnalysis" :loading="analysisRunning">
          <el-icon><TrendCharts /></el-icon>
          <span>{{ analysisRunning ? 'Analyzing...' : 'Run Analysis' }}</span>
        </button>
        <select v-model="selectedTimeRange" class="time-range-select" @change="onTimeRangeChange">
          <option value="today">Today</option>
          <option value="week">Last 7 Days</option>
          <option value="month">Last 30 Days</option>
        </select>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid" v-loading="kpiLoading">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentStats.totalFaults }}</div>
          <div class="kpi-label">Total Faults</div>
        </div>
        <div class="kpi-trend" :class="currentStats.totalTrend >= 0 ? 'up' : 'down'">
          {{ currentStats.totalTrend >= 0 ? '+' : '' }}{{ currentStats.totalTrend }}%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon correlated">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentStats.correlationRate }}%</div>
          <div class="kpi-label">Correlation Rate</div>
        </div>
        <div class="kpi-trend" :class="currentStats.correlationTrend >= 0 ? 'up' : 'down'">
          {{ currentStats.correlationTrend >= 0 ? '+' : '' }}{{ currentStats.correlationTrend }}%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon root">
          <el-icon><Position /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentStats.rootCauses }}</div>
          <div class="kpi-label">Root Causes</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon cascade">
          <el-icon><Share /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ currentStats.cascadeEvents }}</div>
          <div class="kpi-label">Cascade Events</div>
        </div>
      </div>
    </div>

    <!-- Vue Flow Correlation Graph - Draggable with Connections -->
    <div class="graph-card" v-loading="graphLoading">
      <div class="card-header">
        <h3>Fault Correlation Graph</h3>
        <div class="graph-legend">
          <span><span class="legend-dot root"></span>Root Cause</span>
          <span><span class="legend-dot secondary"></span>Secondary</span>
          <span><span class="legend-dot tertiary"></span>Tertiary</span>
          <span><span class="legend-dot cascade-edge"></span>Cascade</span>
        </div>
        <div class="graph-controls">
          <el-button size="small" circle @click="fitView">
            <el-icon><FullScreen /></el-icon>
          </el-button>
          <el-button size="small" circle @click="resetView">
            <el-icon><RefreshRight /></el-icon>
          </el-button>
        </div>
      </div>
      <div class="graph-container" ref="graphContainerRef">
        <VueFlow
            v-model="graphNodes"
            v-model:edges="graphEdges"
            class="vue-flow-wrapper"
            :default-viewport="{ zoom: 0.8, x: 100, y: 50 }"
            :fit-view-on-init="true"
            :nodes-draggable="true"
            :zoom-on-scroll="true"
            :pan-on-scroll="false"
            :min-zoom="0.3"
            :max-zoom="1.5"
            @node-click="onNodeClick"
            @node-drag-stop="onNodeDragStop"
        >
          <template #node-custom="nodeProps">
            <div class="fault-node" :class="nodeProps.data.type">
              <div class="node-header">
                <div class="node-icon" :class="nodeProps.data.severity">
                  <el-icon v-if="nodeProps.data.type === 'root'"><CircleCloseFilled /></el-icon>
                  <el-icon v-else-if="nodeProps.data.type === 'secondary'"><WarningFilled /></el-icon>
                  <el-icon v-else><InfoFilled /></el-icon>
                </div>
                <div class="node-title">{{ nodeProps.data.label }}</div>
              </div>
              <div class="node-details">
                <div class="node-asset">{{ nodeProps.data.asset }}</div>
                <div class="node-time">{{ nodeProps.data.time }}</div>
              </div>
              <div class="node-confidence-bar">
                <div class="node-confidence" :style="{ width: nodeProps.data.confidence + '%' }"></div>
              </div>
              <div class="node-confidence-label">{{ nodeProps.data.confidence }}% confidence</div>
            </div>
          </template>

          <Background pattern-color="#aaa" :gap="20" />
          <MiniMap position="bottom-right" :width="150" :height="100" />
          <Controls position="top-right" />
        </VueFlow>
      </div>
    </div>

    <!-- Correlation Groups -->
    <div class="correlation-groups" v-loading="groupsLoading">
      <div class="section-header">
        <h3>Correlation Groups</h3>
        <span class="group-count">{{ correlationGroups.length }} groups found</span>
      </div>
      <div class="groups-grid">
        <div v-for="group in correlationGroups" :key="group.id" class="group-card" @click="viewGroupDetails(group)">
          <div class="group-header">
            <div class="group-title">{{ group.title }}</div>
            <div class="group-severity" :class="group.severity">
              {{ group.severity.toUpperCase() }}
            </div>
          </div>
          <div class="group-stats">
            <div class="stat">
              <span class="stat-label">Faults</span>
              <span class="stat-value">{{ group.faultCount }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Impact</span>
              <span class="stat-value">{{ group.impactDuration }}</span>
            </div>
            <div class="stat">
              <span class="stat-label">Confidence</span>
              <span class="stat-value">{{ group.confidence }}%</span>
            </div>
          </div>
          <div class="group-faults">
            <div v-for="fault in group.faults.slice(0, 3)" :key="fault.id" class="fault-tag" :class="fault.severity">
              {{ fault.name }}
            </div>
            <div v-if="group.faults.length > 3" class="fault-tag more">
              +{{ group.faults.length - 3 }} more
            </div>
          </div>
          <div class="group-root">
            <el-icon><Position /></el-icon>
            <span>Root Cause: {{ group.rootCause }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Correlation Details Table -->
    <div class="table-card" v-loading="tableLoading">
      <div class="card-header">
        <h3>Correlation Analysis Details</h3>
        <div class="filter-group">
          <select v-model="filters.correlationType" class="filter-select">
            <option value="all">All Types</option>
            <option value="cascade">Cascade</option>
            <option value="dependency">Dependency</option>
            <option value="temporal">Temporal</option>
          </select>
          <input type="text" v-model="filters.search" placeholder="Search..." class="search-input" />
        </div>
      </div>
      <el-table :data="paginatedCorrelations" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="primaryFault" label="Primary Fault" min-width="200" show-overflow-tooltip />
        <el-table-column prop="correlatedFaults" label="Correlated Faults" min-width="200" show-overflow-tooltip />
        <el-table-column prop="relationship" label="Relationship" width="120">
          <template #default="{ row }">
            <el-tag :type="getRelationshipType(row.relationship)" size="small">
              {{ row.relationship }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="Confidence" width="100" align="center">
          <template #default="{ row }">
            <el-progress :percentage="row.confidence" :stroke-width="6" :show-text="true" />
          </template>
        </el-table-column>
        <el-table-column prop="timeDiff" label="Time Difference" width="120" sortable />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewCorrelation(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredCorrelations.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Correlation Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Correlation Details" width="600px">
      <div class="dialog-content" v-if="selectedCorrelation">
        <div class="detail-section">
          <div class="detail-title">Primary Fault</div>
          <div class="detail-item">{{ selectedCorrelation.primaryFault }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Correlated Faults</div>
          <div class="detail-item">{{ selectedCorrelation.correlatedFaults }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Relationship Type</div>
          <div class="detail-item">
            <el-tag :type="getRelationshipType(selectedCorrelation.relationship)" size="large">
              {{ selectedCorrelation.relationship }}
            </el-tag>
          </div>
        </div>
        <div class="detail-section">
          <div class="detail-title">AI Analysis</div>
          <div class="detail-item">{{ selectedCorrelation.analysis }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Recommended Action</div>
          <div class="detail-item">{{ selectedCorrelation.recommendedAction }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="investigateCorrelation">Start Investigation</el-button>
      </template>
    </el-dialog>

    <!-- Analysis Progress Dialog -->
    <el-dialog v-model="analysisDialogVisible" title="AI Correlation Analysis" width="500px" :close-on-click-modal="false">
      <div class="analysis-progress">
        <div class="analysis-icon">
          <el-icon v-if="analysisStep === 0"><Loading /></el-icon>
          <el-icon v-else-if="analysisStep === 1"><Document /></el-icon>
          <el-icon v-else-if="analysisStep === 2"><Connection /></el-icon>
          <el-icon v-else-if="analysisStep === 3"><TrendCharts /></el-icon>
          <el-icon v-else><CircleCheckFilled /></el-icon>
        </div>
        <div class="analysis-step">{{ analysisSteps[analysisStep] }}</div>
        <el-progress :percentage="analysisProgress" :stroke-width="8" :show-text="false" />
        <div class="analysis-result" v-if="analysisStep === 4">
          <p>✅ Analysis complete!</p>
          <p>📊 {{ analysisResult.summary }}</p>
        </div>
      </div>
      <template #footer>
        <el-button v-if="analysisStep === 4" type="primary" @click="analysisDialogVisible = false">View Results</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Refresh, Download, WarningFilled, Connection, Position, Share, TrendCharts,
  CircleCloseFilled, InfoFilled, FullScreen, RefreshRight, Loading, Document, CircleCheckFilled
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { VueFlow, useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

// Vue Flow setup
const { fitView, setViewport, zoomIn, zoomOut } = useVueFlow()

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Loading fault data...', 'Building correlation graph...', 'Almost ready...']

// UI States
const kpiLoading = ref(false)
const graphLoading = ref(false)
const groupsLoading = ref(false)
const tableLoading = ref(false)
const analysisRunning = ref(false)
const analysisDialogVisible = ref(false)
const analysisStep = ref(0)
const analysisProgress = ref(0)
const selectedTimeRange = ref('week')

// Vue Flow data
const graphNodes = ref<Node[]>([])
const graphEdges = ref<Edge[]>([])
const nodePositionsCache = ref<Map<string, { x: number; y: number }>>(new Map())

// Data States
const currentStats = ref({
  totalFaults: 0,
  totalTrend: 0,
  correlationRate: 0,
  correlationTrend: 0,
  rootCauses: 0,
  cascadeEvents: 0
})

const correlationGroups = ref<any[]>([])
const correlations = ref<any[]>([])
const lastAnalysisTime = ref('')
const analysisResult = ref({ summary: '' })
const analysisStepTexts = [
  'Connecting to AI Engine...',
  'Retrieving fault data...',
  'Analyzing correlation patterns...',
  'Generating correlation graph...',
  'Analysis Complete!'
]
const analysisSteps = analysisStepTexts

// Filters
const filters = ref({
  correlationType: 'all',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const selectedCorrelation = ref<any>(null)

// Helper Functions
const getRelationshipType = (relationship: string) => {
  const map: Record<string, string> = {
    Cascade: 'danger',
    Dependency: 'warning',
    Temporal: 'info'
  }
  return map[relationship] || 'info'
}

// 生成动态节点位置
const generateNodePositions = (rootCount: number, secondaryCount: number, tertiaryCount: number, canvasWidth: number, canvasHeight: number) => {
  const startX = 100
  const startY = 100
  const levelGap = 280
  const nodeGap = 120

  const positions: Map<string, { x: number; y: number }> = new Map()

  // 根节点位置 (左侧)
  for (let i = 0; i < rootCount; i++) {
    const y = startY + i * nodeGap
    positions.set(`root-${i + 1}`, { x: startX, y: Math.min(y, canvasHeight - 100) })
  }

  // 次级节点位置 (中间)
  for (let i = 0; i < secondaryCount; i++) {
    const y = startY + (i % rootCount) * nodeGap + Math.floor(i / rootCount) * 150
    positions.set(`secondary-${i + 1}`, { x: startX + levelGap, y: Math.min(y, canvasHeight - 100) })
  }

  // 三级节点位置 (右侧)
  for (let i = 0; i < tertiaryCount; i++) {
    const y = startY + (i % rootCount) * nodeGap + Math.floor(i / rootCount) * 150
    positions.set(`tertiary-${i + 1}`, { x: startX + levelGap * 2, y: Math.min(y, canvasHeight - 100) })
  }

  return positions
}

// 构建Vue Flow节点和边
const buildGraphData = (rootData: any[], secondaryData: any[], tertiaryData: any[]) => {
  const nodes: Node[] = []
  const edges: Edge[] = []

  // 创建根节点
  rootData.forEach((node, idx) => {
    nodes.push({
      id: `root-${idx + 1}`,
      type: 'custom',
      position: nodePositionsCache.value.get(`root-${idx + 1}`) || { x: 100, y: 100 + idx * 120 },
      data: {
        label: node.label,
        type: 'root',
        severity: node.severity,
        asset: node.asset,
        time: node.time,
        confidence: node.confidence
      }
    })
  })

  // 创建次级节点
  secondaryData.forEach((node, idx) => {
    nodes.push({
      id: `secondary-${idx + 1}`,
      type: 'custom',
      position: nodePositionsCache.value.get(`secondary-${idx + 1}`) || { x: 380, y: 120 + idx * 120 },
      data: {
        label: node.label,
        type: 'secondary',
        severity: node.severity,
        asset: node.asset,
        time: node.time,
        confidence: node.confidence
      }
    })
  })

  // 创建三级节点
  tertiaryData.forEach((node, idx) => {
    nodes.push({
      id: `tertiary-${idx + 1}`,
      type: 'custom',
      position: nodePositionsCache.value.get(`tertiary-${idx + 1}`) || { x: 660, y: 120 + idx * 120 },
      data: {
        label: node.label,
        type: 'tertiary',
        severity: node.severity,
        asset: node.asset,
        time: node.time,
        confidence: node.confidence
      }
    })
  })

  // 创建边 - 根节点到次级节点
  for (let i = 0; i < Math.min(rootData.length, secondaryData.length); i++) {
    edges.push({
      id: `edge-root-${i + 1}`,
      source: `root-${i + 1}`,
      target: `secondary-${i + 1}`,
      label: 'CASCADE',
      animated: true,
      style: { stroke: '#f59e0b', strokeWidth: 2 },
      labelStyle: { fill: '#f59e0b', fontSize: 10, fontWeight: 'bold' }
    })
  }

  // 创建边 - 次级节点到三级节点
  for (let i = 0; i < Math.min(secondaryData.length, tertiaryData.length); i++) {
    edges.push({
      id: `edge-secondary-${i + 1}`,
      source: `secondary-${i + 1}`,
      target: `tertiary-${i + 1}`,
      label: 'IMPACTS',
      animated: true,
      style: { stroke: '#f59e0b', strokeWidth: 2 },
      labelStyle: { fill: '#f59e0b', fontSize: 10, fontWeight: 'bold' }
    })
  }

  return { nodes, edges }
}

// 模拟后端API调用 - 根据时间范围获取数据
const fetchDataByTimeRange = async (range: string) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const multipliers = {
        today: { fault: 0.15, group: 0.2, node: 0.3 },
        week: { fault: 1, group: 1, node: 1 },
        month: { fault: 2.5, group: 1.5, node: 1.8 }
      }
      const m = multipliers[range as keyof typeof multipliers]

      // 统计数据
      const totalFaults = Math.floor(120 * m.fault)
      const correlationRate = Math.floor(65 + (range === 'today' ? 15 : range === 'week' ? 0 : -8))

      currentStats.value = {
        totalFaults,
        totalTrend: range === 'today' ? -12 : range === 'week' ? -5 : 8,
        correlationRate,
        correlationTrend: range === 'today' ? 8 : range === 'week' ? 3 : -2,
        rootCauses: Math.floor(12 * m.fault),
        cascadeEvents: Math.floor(8 * m.fault)
      }

      // 根节点数据
      const rootData = {
        today: [
          { id: 1, label: 'AHU-101\nVFD Overcurrent', asset: 'AHU-101', time: '14:23:15', confidence: 92, severity: 'critical' },
          { id: 2, label: 'Chiller-02\nHigh Pressure', asset: 'Chiller-02', time: '13:45:22', confidence: 88, severity: 'critical' },
          { id: 3, label: 'UPS-01\nBattery Low', asset: 'UPS-01', time: '11:30:05', confidence: 85, severity: 'major' }
        ],
        week: [
          { id: 1, label: 'Chiller-02\nHigh Pressure Trip', asset: 'Chiller-02', time: '08:23:15', confidence: 94, severity: 'critical' },
          { id: 2, label: 'UPS-01\nPower Loss', asset: 'UPS-01', time: '07:45:22', confidence: 92, severity: 'critical' },
          { id: 3, label: 'CRAC-03\nCompressor Failure', asset: 'CRAC-03', time: '06:30:05', confidence: 96, severity: 'critical' },
          { id: 4, label: 'AHU-201\nFilter Clogged', asset: 'AHU-201', time: '22:15:30', confidence: 88, severity: 'major' }
        ],
        month: [
          { id: 1, label: 'Chiller-02\nHigh Pressure Trip', asset: 'Chiller-02', time: '08:23:15', confidence: 94, severity: 'critical' },
          { id: 2, label: 'UPS-01\nPower Loss', asset: 'UPS-01', time: '07:45:22', confidence: 92, severity: 'critical' },
          { id: 3, label: 'CRAC-03\nCompressor Failure', asset: 'CRAC-03', time: '06:30:05', confidence: 96, severity: 'critical' },
          { id: 4, label: 'AHU-201\nFilter Clogged', asset: 'AHU-201', time: '22:15:30', confidence: 88, severity: 'major' },
          { id: 5, label: 'Cooling Tower\nFan Motor Fault', asset: 'CT-02', time: '19:20:00', confidence: 86, severity: 'major' },
          { id: 6, label: 'Generator\nFuel System Error', asset: 'GEN-01', time: '16:45:00', confidence: 91, severity: 'critical' }
        ]
      }

      // 次级节点
      const secondaryData = {
        today: [
          { id: 5, label: 'Building A\nTemp High', asset: 'Sensor-T-12', time: '14:25:30', confidence: 85, severity: 'major' },
          { id: 6, label: 'Cooling Tower\nFan Low Speed', asset: 'CT-01', time: '13:48:00', confidence: 82, severity: 'major' },
          { id: 7, label: 'PDU\nOverload Warning', asset: 'PDU-03', time: '11:32:10', confidence: 80, severity: 'warning' }
        ],
        week: [
          { id: 5, label: 'Cooling Tower\nFan Failure', asset: 'CT-01', time: '08:21:00', confidence: 88, severity: 'major' },
          { id: 6, label: 'PDU Overload', asset: 'PDU-03', time: '07:45:52', confidence: 86, severity: 'major' },
          { id: 7, label: 'Server Room\nTemp High', asset: 'Room Temp', time: '06:33:50', confidence: 90, severity: 'critical' },
          { id: 8, label: 'VFD-105\nOvercurrent', asset: 'VFD-105', time: '22:18:00', confidence: 83, severity: 'major' }
        ],
        month: [
          { id: 5, label: 'Cooling Tower\nFan Failure', asset: 'CT-01', time: '08:21:00', confidence: 88, severity: 'major' },
          { id: 6, label: 'PDU Overload', asset: 'PDU-03', time: '07:45:52', confidence: 86, severity: 'major' },
          { id: 7, label: 'Server Room\nTemp High', asset: 'Room Temp', time: '06:33:50', confidence: 90, severity: 'critical' },
          { id: 8, label: 'VFD-105\nOvercurrent', asset: 'VFD-105', time: '22:18:00', confidence: 83, severity: 'major' },
          { id: 9, label: 'Chilled Water\nFlow Low', asset: 'CWP-02', time: '19:25:00', confidence: 87, severity: 'major' },
          { id: 10, label: 'Fire Alarm\nZone 3 Fault', asset: 'FA-101', time: '16:50:00', confidence: 89, severity: 'critical' }
        ]
      }

      // 三级节点
      const tertiaryData = {
        today: [
          { id: 9, label: 'Office Zone\nComfort Loss', asset: 'Zone-3', time: '14:28:15', confidence: 78, severity: 'minor' },
          { id: 10, label: 'Server Room\nHotspot', asset: 'Rack A03', time: '11:35:20', confidence: 82, severity: 'warning' }
        ],
        week: [
          { id: 9, label: 'Building A\nTemp High', asset: 'Sensor-T-12', time: '08:25:30', confidence: 82, severity: 'minor' },
          { id: 10, label: 'Server Rack\nPower Loss', asset: 'Rack A03', time: '07:46:10', confidence: 84, severity: 'major' },
          { id: 11, label: 'Rack Inlet\nTemp Alarm', asset: 'Rack B01', time: '06:35:20', confidence: 85, severity: 'major' },
          { id: 12, label: 'Zone Temp\nDeviation', asset: 'Zone-3', time: '22:20:15', confidence: 78, severity: 'minor' }
        ],
        month: [
          { id: 9, label: 'Building A\nTemp High', asset: 'Sensor-T-12', time: '08:25:30', confidence: 82, severity: 'minor' },
          { id: 10, label: 'Server Rack\nPower Loss', asset: 'Rack A03', time: '07:46:10', confidence: 84, severity: 'major' },
          { id: 11, label: 'Rack Inlet\nTemp Alarm', asset: 'Rack B01', time: '06:35:20', confidence: 85, severity: 'major' },
          { id: 12, label: 'Zone Temp\nDeviation', asset: 'Zone-3', time: '22:20:15', confidence: 78, severity: 'minor' },
          { id: 13, label: 'UPS Output\nFluctuation', asset: 'UPS-02', time: '16:55:00', confidence: 83, severity: 'major' },
          { id: 14, label: 'Network Switch\nPoE Failure', asset: 'SW-05', time: '14:20:00', confidence: 76, severity: 'minor' }
        ]
      }

      // 相关性组
      const groupsData = {
        today: [
          { id: 1, title: 'AHU Failure Cascade', severity: 'critical', faultCount: 3, impactDuration: '45m', confidence: 92, faults: [{ id: 1, name: 'AHU-101 Overcurrent', severity: 'critical' }, { id: 2, name: 'Temp High', severity: 'major' }], rootCause: 'VFD capacitor failure' }
        ],
        week: [
          { id: 1, title: 'Chiller System Failure Cascade', severity: 'critical', faultCount: 8, impactDuration: '4h 30m', confidence: 94, faults: [{ id: 1001, name: 'Chiller-02 High Pressure Trip', severity: 'critical' }, { id: 1002, name: 'Cooling Tower Fan Failure', severity: 'major' }], rootCause: 'Condenser water flow reduced due to pump failure' },
          { id: 2, title: 'Power Distribution Cascade', severity: 'critical', faultCount: 6, impactDuration: '2h 15m', confidence: 92, faults: [{ id: 2001, name: 'UPS-01 Input Power Loss', severity: 'critical' }, { id: 2002, name: 'PDU Overload', severity: 'major' }], rootCause: 'Main switchboard breaker tripped' },
          { id: 3, title: 'Data Center Cooling Cascade', severity: 'critical', faultCount: 7, impactDuration: '5h', confidence: 96, faults: [{ id: 4001, name: 'CRAC-03 Compressor Failure', severity: 'critical' }, { id: 4002, name: 'Server Room Temperature High', severity: 'critical' }], rootCause: 'CRAC compressor capacitor failure' }
        ],
        month: [
          { id: 1, title: 'Chiller System Failure Cascade', severity: 'critical', faultCount: 12, impactDuration: '4h 30m', confidence: 94, faults: [{ id: 1001, name: 'Chiller-02 High Pressure Trip', severity: 'critical' }, { id: 1002, name: 'Cooling Tower Fan Failure', severity: 'major' }], rootCause: 'Condenser water flow reduced due to pump failure' },
          { id: 2, title: 'Power Distribution Cascade', severity: 'critical', faultCount: 9, impactDuration: '2h 15m', confidence: 92, faults: [{ id: 2001, name: 'UPS-01 Input Power Loss', severity: 'critical' }, { id: 2002, name: 'PDU Overload', severity: 'major' }], rootCause: 'Main switchboard breaker tripped' },
          { id: 3, title: 'Data Center Cooling Cascade', severity: 'critical', faultCount: 10, impactDuration: '5h', confidence: 96, faults: [{ id: 4001, name: 'CRAC-03 Compressor Failure', severity: 'critical' }, { id: 4002, name: 'Server Room Temperature High', severity: 'critical' }], rootCause: 'CRAC compressor capacitor failure' },
          { id: 4, title: 'Generator Fuel System Issue', severity: 'critical', faultCount: 5, impactDuration: '3h', confidence: 90, faults: [{ id: 5001, name: 'Generator Fuel Low', severity: 'critical' }, { id: 5002, name: 'Fuel Pump Error', severity: 'major' }], rootCause: 'Fuel delivery system failure' }
        ]
      }

      // 相关性记录
      const correlationsData = {
        today: [
          { id: 1, primaryFault: 'AHU-101 VFD Overcurrent', correlatedFaults: 'Building A Temp High', relationship: 'Cascade', confidence: 92, timeDiff: '2m 15s', analysis: 'VFD overcurrent caused by voltage spike, leading to temperature rise.', recommendedAction: 'Check VFD parameters and power quality' }
        ],
        week: [
          { id: 1, primaryFault: 'Chiller-02 High Pressure Trip', correlatedFaults: 'Cooling Tower Fan Failure, Building A Temperature High', relationship: 'Cascade', confidence: 94, timeDiff: '2m 15s', analysis: 'Chiller high pressure triggered by cooling tower fan failure, leading to temperature rise.', recommendedAction: 'Restore cooling tower fan operation and reset chiller' },
          { id: 2, primaryFault: 'UPS-01 Input Power Loss', correlatedFaults: 'PDU Overload, Server Rack Power Loss', relationship: 'Cascade', confidence: 92, timeDiff: '30s', analysis: 'UPS lost main input power, causing PDU to draw from battery and overload.', recommendedAction: 'Check main breaker and restore primary power' },
          { id: 3, primaryFault: 'CRAC-03 Compressor Failure', correlatedFaults: 'Server Room Temperature High, Rack Inlet Temperature Alarm', relationship: 'Cascade', confidence: 96, timeDiff: '3m 45s', analysis: 'CRAC compressor failure directly caused temperature rise in server room.', recommendedAction: 'Replace compressor and verify cooling capacity' }
        ],
        month: [
          { id: 1, primaryFault: 'Chiller-02 High Pressure Trip', correlatedFaults: 'Cooling Tower Fan Failure, Building A Temperature High', relationship: 'Cascade', confidence: 94, timeDiff: '2m 15s', analysis: 'Chiller high pressure triggered by cooling tower fan failure.', recommendedAction: 'Restore cooling tower fan operation and reset chiller' },
          { id: 2, primaryFault: 'UPS-01 Input Power Loss', correlatedFaults: 'PDU Overload, Server Rack Power Loss', relationship: 'Cascade', confidence: 92, timeDiff: '30s', analysis: 'UPS lost main input power, causing PDU overload.', recommendedAction: 'Check main breaker and restore primary power' },
          { id: 3, primaryFault: 'CRAC-03 Compressor Failure', correlatedFaults: 'Server Room Temperature High, Rack Inlet Temperature Alarm', relationship: 'Cascade', confidence: 96, timeDiff: '3m 45s', analysis: 'CRAC compressor failure directly caused temperature rise.', recommendedAction: 'Replace compressor and verify cooling capacity' },
          { id: 4, primaryFault: 'Generator Fuel Low', correlatedFaults: 'Fuel Pump Error, Emergency Power Loss', relationship: 'Dependency', confidence: 90, timeDiff: '1m', analysis: 'Fuel system failure detected, generator unable to start.', recommendedAction: 'Schedule fuel delivery and inspect fuel system' }
        ]
      }

      resolve({
        stats: currentStats.value,
        rootNodes: rootData[range as keyof typeof rootData] || rootData.week,
        secondaryNodes: secondaryData[range as keyof typeof secondaryData] || secondaryData.week,
        tertiaryNodes: tertiaryData[range as keyof typeof tertiaryData] || tertiaryData.week,
        groups: groupsData[range as keyof typeof groupsData] || groupsData.week,
        correlations: correlationsData[range as keyof typeof correlationsData] || correlationsData.week
      })
    }, 500)
  })
}

// 更新Vue Flow图形
const updateFlowGraph = async (rootData: any[], secondaryData: any[], tertiaryData: any[]) => {
  // 获取容器尺寸
  const container = document.querySelector('.graph-container')
  let width = 800, height = 500
  if (container) {
    const rect = container.getBoundingClientRect()
    width = rect.width - 40
    height = rect.height - 40
  }

  // 生成位置
  const positions = generateNodePositions(rootData.length, secondaryData.length, tertiaryData.length, width, height)
  nodePositionsCache.value = positions

  // 构建图形数据
  const { nodes, edges } = buildGraphData(rootData, secondaryData, tertiaryData)
  graphNodes.value = nodes
  graphEdges.value = edges

  // 延迟适应视图
  setTimeout(() => {
    fitView({ padding: 0.2, duration: 300 })
  }, 100)
}

// Load data for selected time range
const loadDataForTimeRange = async () => {
  kpiLoading.value = true
  graphLoading.value = true
  groupsLoading.value = true
  tableLoading.value = true

  const result = await fetchDataByTimeRange(selectedTimeRange.value) as any

  correlationGroups.value = result.groups
  correlations.value = result.correlations

  // 更新Vue Flow图形
  await updateFlowGraph(result.rootNodes, result.secondaryNodes, result.tertiaryNodes)

  kpiLoading.value = false
  graphLoading.value = false
  groupsLoading.value = false
  tableLoading.value = false
}

// Time range change handler
const onTimeRangeChange = async () => {
  await loadDataForTimeRange()
  ElMessage.success(`Switched to ${selectedTimeRange.value === 'today' ? 'Today' : selectedTimeRange.value === 'week' ? 'Last 7 Days' : 'Last 30 Days'} view`)
}

// Run correlation analysis
const runCorrelationAnalysis = async () => {
  analysisRunning.value = true
  analysisDialogVisible.value = true
  analysisStep.value = 0
  analysisProgress.value = 0

  for (let step = 0; step <= 4; step++) {
    analysisStep.value = step
    for (let p = 0; p <= 100; p += 20) {
      if (step === 4 && p > 0) break
      analysisProgress.value = step * 25 + p / 4
      await new Promise(resolve => setTimeout(resolve, 100))
    }
    if (step < 4) await new Promise(resolve => setTimeout(resolve, 500))
  }

  analysisProgress.value = 100
  analysisResult.value = {
    summary: `Identified ${correlationGroups.value.length} correlation groups with ${currentStats.value.rootCauses} root causes`
  }
  lastAnalysisTime.value = new Date().toLocaleString()

  setTimeout(() => {
    analysisRunning.value = false
  }, 500)
}

// Vue Flow actions
const resetView = () => {
  fitView({ padding: 0.2, duration: 300 })
}

// Node drag stop - save position to cache
const onNodeDragStop = (event: any) => {
  if (event.node) {
    nodePositionsCache.value.set(event.node.id, {
      x: event.node.position.x,
      y: event.node.position.y
    })
  }
}

// Node click
const onNodeClick = (event: any) => {
  const node = event.node
  const data = node.data
  ElMessage.info(`${data.label.replace('\n', ' ')} - Confidence: ${data.confidence}% - ${data.type === 'root' ? 'Root Cause' : data.type === 'secondary' ? 'Secondary Fault' : 'Tertiary Impact'}`)
}

// Other actions
const refreshData = async () => {
  await loadDataForTimeRange()
  ElMessage.success('Data refreshed')
}

const viewGroupDetails = (group: any) => {
  ElMessage.info(`Viewing group: ${group.title}`)
}

const viewCorrelation = (row: any) => {
  selectedCorrelation.value = row
  detailDialogVisible.value = true
}

const investigateCorrelation = () => {
  ElMessage.info('Starting investigation workflow...')
  detailDialogVisible.value = false
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// Computed
const filteredCorrelations = computed(() => {
  let result = [...correlations.value]
  if (filters.value.correlationType !== 'all') {
    result = result.filter(c => c.relationship.toLowerCase() === filters.value.correlationType)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(c =>
        c.primaryFault.toLowerCase().includes(search) ||
        c.correlatedFaults.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedCorrelations = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredCorrelations.value.slice(start, end)
})

// Window resize handler
const handleResize = () => {
  if (isLoaded.value) {
    // Refresh positions on resize
    const container = document.querySelector('.graph-container')
    if (container) {
      // Recalculate positions if needed
    }
  }
}

// Lifecycle
onMounted(async () => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(async () => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(async () => {
      isLoaded.value = true
      await loadDataForTimeRange()
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* Loading Screen - 保持原有样式 */
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
  font-size: 28px;
  font-weight: 700;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

/* Main Content */
.fault-correlation-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(139, 92, 246, 0.3);
}
.time-range-select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  font-size: 13px;
  cursor: pointer;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.kpi-icon.total { background: #fee2e2; color: #dc2626; }
.kpi-icon.correlated { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.root { background: #fef3c7; color: #d97706; }
.kpi-icon.cascade { background: #d1fae5; color: #059669; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }
.kpi-trend { font-size: 11px; font-weight: 600; padding: 2px 6px; border-radius: 12px; }
.kpi-trend.up { color: #10b981; background: #d1fae5; }
.kpi-trend.down { color: #dc2626; background: #fee2e2; }

/* Graph Card */
.graph-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}
.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1a1a2e;
}
.graph-legend {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #64748b;
}
.graph-controls {
  display: flex;
  gap: 8px;
}
.legend-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 6px;
}
.legend-dot.root { background: #f56c6c; }
.legend-dot.secondary { background: #e6a23c; }
.legend-dot.tertiary { background: #409eff; }
.legend-dot.cascade-edge { background: #f59e0b; }
.graph-container {
  height: 780px;
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  overflow: hidden;
}

/* Vue Flow Custom Node Styles */
.vue-flow-wrapper {
  width: 100%;
  height: 100%;
}
.fault-node {
  width: 200px;
  padding: 12px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
  border-left: 4px solid;
}
.fault-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}
.fault-node.root { border-left-color: #f56c6c; background: linear-gradient(135deg, #fff, #fff5f5); }
.fault-node.secondary { border-left-color: #e6a23c; background: linear-gradient(135deg, #fff, #fffaf0); }
.fault-node.tertiary { border-left-color: #409eff; background: linear-gradient(135deg, #fff, #f0f7ff); }
.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.node-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.node-icon.critical { background: #fee2e2; color: #dc2626; }
.node-icon.major { background: #fef3c7; color: #d97706; }
.node-icon.minor { background: #dbeafe; color: #2563eb; }
.node-title {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a2e;
  line-height: 1.3;
  white-space: pre-line;
  flex: 1;
}
.node-details {
  margin-bottom: 8px;
}
.node-asset {
  font-size: 10px;
  color: #64748b;
  margin-bottom: 2px;
}
.node-time {
  font-size: 9px;
  color: #94a3b8;
}
.node-confidence-bar {
  background: #e2e8f0;
  border-radius: 4px;
  height: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}
.node-confidence {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #10b981);
  border-radius: 4px;
}
.node-confidence-label {
  font-size: 9px;
  color: #64748b;
  text-align: right;
}

/* Vue Flow Styles */
:deep(.vue-flow__edge-path) { stroke: #f59e0b; stroke-width: 2; }
:deep(.vue-flow__edge-textbg) { fill: white; }
:deep(.vue-flow__edge-text) { fill: #f59e0b; font-size: 10px; font-weight: 600; }
:deep(.vue-flow__minimap) { background: #e2e8f0; border-radius: 8px; }
:deep(.vue-flow__controls) { bottom: 16px; right: 16px; }

/* Correlation Groups */
.correlation-groups {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
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
  margin: 0;
  color: #1a1a2e;
}
.group-count {
  font-size: 13px;
  color: #64748b;
  background: #f1f5f9;
  padding: 4px 12px;
  border-radius: 20px;
}
.groups-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}
.group-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}
.group-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #8b5cf6;
}
.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.group-title {
  font-weight: 600;
  color: #1a1a2e;
}
.group-severity {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 20px;
  font-weight: 600;
}
.group-severity.critical { background: #fee2e2; color: #dc2626; }
.group-severity.major { background: #fef3c7; color: #d97706; }
.group-severity.minor { background: #dbeafe; color: #2563eb; }
.group-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}
.stat {
  text-align: center;
}
.stat-label {
  display: block;
  font-size: 10px;
  color: #64748b;
}
.stat-value {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}
.group-faults {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.fault-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
}
.fault-tag.critical { background: #fee2e2; color: #dc2626; }
.fault-tag.major { background: #fef3c7; color: #d97706; }
.fault-tag.minor { background: #dbeafe; color: #2563eb; }
.fault-tag.more { background: #f1f5f9; color: #64748b; }
.group-root {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #8b5cf6;
  background: #f3e8ff;
  padding: 6px 10px;
  border-radius: 10px;
}

/* Table Card */
.table-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.filter-group {
  display: flex;
  gap: 12px;
  align-items: center;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
}
.search-input { width: 200px; }
.pagination-wrapper {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 16px;
}

/* Dialog */
.dialog-content { padding: 8px 0; }
.detail-section {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-section:last-child { border-bottom: none; margin-bottom: 0; }
.detail-title { font-weight: 600; color: #1a1a2e; margin-bottom: 8px; font-size: 14px; }
.detail-item { color: #475569; font-size: 13px; line-height: 1.5; }

/* Analysis Dialog */
.analysis-progress {
  text-align: center;
  padding: 20px;
}
.analysis-icon {
  font-size: 48px;
  color: #8b5cf6;
  margin-bottom: 20px;
}
.analysis-step {
  font-size: 16px;
  color: #1a1a2e;
  margin-bottom: 20px;
  font-weight: 500;
}
.analysis-result {
  margin-top: 20px;
  padding: 16px;
  background: #d1fae5;
  border-radius: 12px;
  color: #059669;
  font-size: 14px;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-progress__text) { font-size: 11px !important; }
</style>