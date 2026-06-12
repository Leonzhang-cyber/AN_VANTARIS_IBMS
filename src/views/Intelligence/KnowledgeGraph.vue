<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading knowledge graph...',
  'Building semantic relationships...',
  'Preparing graph visualization...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedNodeType = ref('all')
const detailsVisible = ref(false)
const graphRef = ref<HTMLElement | null>(null)

let knowledgeGraph: echarts.ECharts | null = null

// Node type filters
const nodeTypeOptions = [
  { value: 'all', label: 'All Nodes', color: '#409EFF' },
  { value: 'device', label: 'Devices', color: '#67C23A' },
  { value: 'system', label: 'Systems', color: '#E6A23C' },
  { value: 'location', label: 'Locations', color: '#F56C6C' },
  { value: 'metric', label: 'Metrics', color: '#9B59B6' },
  { value: 'alert', label: 'Alerts', color: '#1ABC9C' }
]

// Knowledge graph data
const graphData = ref({
  nodes: [
    { name: 'Building A', category: 'location', symbolSize: 40, itemStyle: { color: '#F56C6C' }, description: 'Main office building, 5 floors' },
    { name: 'Building B', category: 'location', symbolSize: 35, itemStyle: { color: '#F56C6C' }, description: 'Annex building, 3 floors' },
    { name: 'AHU-1', category: 'device', symbolSize: 30, itemStyle: { color: '#67C23A' }, description: 'Air Handling Unit 1' },
    { name: 'AHU-2', category: 'device', symbolSize: 30, itemStyle: { color: '#67C23A' }, description: 'Air Handling Unit 2' },
    { name: 'Chiller-1', category: 'device', symbolSize: 32, itemStyle: { color: '#67C23A' }, description: 'Chiller Unit 1' },
    { name: 'HVAC System', category: 'system', symbolSize: 35, itemStyle: { color: '#E6A23C' }, description: 'Heating, Ventilation, Air Conditioning' },
    { name: 'BMS', category: 'system', symbolSize: 38, itemStyle: { color: '#E6A23C' }, description: 'Building Management System' },
    { name: 'Temperature', category: 'metric', symbolSize: 25, itemStyle: { color: '#9B59B6' }, description: 'Temperature readings' },
    { name: 'Humidity', category: 'metric', symbolSize: 25, itemStyle: { color: '#9B59B6' }, description: 'Humidity readings' },
    { name: 'Energy', category: 'metric', symbolSize: 25, itemStyle: { color: '#9B59B6' }, description: 'Energy consumption' },
    { name: 'Alert: High Temp', category: 'alert', symbolSize: 28, itemStyle: { color: '#1ABC9C' }, description: 'Temperature exceeds threshold' },
    { name: 'Alert: Low Flow', category: 'alert', symbolSize: 28, itemStyle: { color: '#1ABC9C' }, description: 'Water flow low' },
    { name: 'Floor 1', category: 'location', symbolSize: 30, itemStyle: { color: '#F56C6C' }, description: 'First floor' },
    { name: 'Floor 2', category: 'location', symbolSize: 30, itemStyle: { color: '#F56C6C' }, description: 'Second floor' },
    { name: 'Floor 3', category: 'location', symbolSize: 30, itemStyle: { color: '#F56C6C' }, description: 'Third floor' }
  ],
  links: [
    { source: 'Building A', target: 'Floor 1', category: 'contains' },
    { source: 'Building A', target: 'Floor 2', category: 'contains' },
    { source: 'Building A', target: 'Floor 3', category: 'contains' },
    { source: 'Floor 1', target: 'AHU-1', category: 'houses' },
    { source: 'Floor 2', target: 'AHU-2', category: 'houses' },
    { source: 'Floor 3', target: 'Chiller-1', category: 'houses' },
    { source: 'AHU-1', target: 'HVAC System', category: 'belongs_to' },
    { source: 'AHU-2', target: 'HVAC System', category: 'belongs_to' },
    { source: 'Chiller-1', target: 'HVAC System', category: 'belongs_to' },
    { source: 'HVAC System', target: 'BMS', category: 'connected_to' },
    { source: 'AHU-1', target: 'Temperature', category: 'measures' },
    { source: 'AHU-1', target: 'Humidity', category: 'measures' },
    { source: 'AHU-2', target: 'Temperature', category: 'measures' },
    { source: 'Chiller-1', target: 'Energy', category: 'consumes' },
    { source: 'Temperature', target: 'Alert: High Temp', category: 'triggers' },
    { source: 'Chiller-1', target: 'Alert: Low Flow', category: 'triggers' }
  ]
})

// Node categories for legend
const categories = [
  { name: 'location', itemStyle: { color: '#F56C6C' } },
  { name: 'device', itemStyle: { color: '#67C23A' } },
  { name: 'system', itemStyle: { color: '#E6A23C' } },
  { name: 'metric', itemStyle: { color: '#9B59B6' } },
  { name: 'alert', itemStyle: { color: '#1ABC9C' } }
]

// Knowledge graph statistics
const graphStats = reactive({
  totalNodes: 0,
  totalEdges: 0,
  deviceCount: 0,
  systemCount: 0,
  locationCount: 0,
  metricCount: 0,
  alertCount: 0,
  relationships: 0
})

// Related content for selected node
const relatedContent = ref<any>(null)

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: 0
})

// Filtered graph data
const filteredGraphData = computed(() => {
  if (selectedNodeType.value === 'all') {
    return graphData.value
  }

  const filteredNodes = graphData.value.nodes.filter(node => node.category === selectedNodeType.value)
  const filteredNodeNames = new Set(filteredNodes.map(n => n.name))
  const filteredLinks = graphData.value.links.filter(link =>
      filteredNodeNames.has(link.source) && filteredNodeNames.has(link.target)
  )

  return { nodes: filteredNodes, links: filteredLinks }
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
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Graph Functions ====================
const initGraph = () => {
  if (!graphRef.value) return

  // Create node categories mapping
  const nodeCategories: Record<string, any> = {
    location: { name: 'location', itemStyle: { color: '#F56C6C' } },
    device: { name: 'device', itemStyle: { color: '#67C23A' } },
    system: { name: 'system', itemStyle: { color: '#E6A23C' } },
    metric: { name: 'metric', itemStyle: { color: '#9B59B6' } },
    alert: { name: 'alert', itemStyle: { color: '#1ABC9C' } }
  }

  const nodes = graphData.value.nodes.map(node => ({
    name: node.name,
    category: node.category,
    symbolSize: node.symbolSize,
    itemStyle: { color: nodeCategories[node.category]?.itemStyle.color || '#409EFF' },
    description: node.description
  }))

  const links = graphData.value.links.map(link => ({
    source: link.source,
    target: link.target,
    lineStyle: { color: '#ccc', curveness: 0.3, width: 1.5 }
  }))

  knowledgeGraph = echarts.init(graphRef.value)
  knowledgeGraph.setOption({
    title: { show: false },
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<strong>${params.name}</strong><br/>Type: ${params.data.category}<br/>${params.data.description || ''}`
        }
        return `${params.data.source} → ${params.data.target}`
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: links,
      categories: categories,
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

  // Add click handler
  knowledgeGraph.off('click')
  knowledgeGraph.on('click', (params: any) => {
    if (params.dataType === 'node') {
      showNodeDetails(params.data)
    }
  })
}

const showNodeDetails = (node: any) => {
  selectedNode.value = node
  findRelatedContent(node.name)
  detailsVisible.value = true
}

const findRelatedContent = (nodeName: string) => {
  const incoming = graphData.value.links.filter(l => l.target === nodeName).map(l => l.source)
  const outgoing = graphData.value.links.filter(l => l.source === nodeName).map(l => l.target)
  const related = [...new Set([...incoming, ...outgoing])]

  relatedContent.value = {
    name: nodeName,
    incoming,
    outgoing,
    total: incoming.length + outgoing.length
  }
}

const updateStats = () => {
  graphStats.totalNodes = graphData.value.nodes.length
  graphStats.totalEdges = graphData.value.links.length
  graphStats.deviceCount = graphData.value.nodes.filter(n => n.category === 'device').length
  graphStats.systemCount = graphData.value.nodes.filter(n => n.category === 'system').length
  graphStats.locationCount = graphData.value.nodes.filter(n => n.category === 'location').length
  graphStats.metricCount = graphData.value.nodes.filter(n => n.category === 'metric').length
  graphStats.alertCount = graphData.value.nodes.filter(n => n.category === 'alert').length
  graphStats.relationships = graphData.value.links.length
}

const handleResize = () => {
  knowledgeGraph?.resize()
}

// ==================== Graph Functions ====================
const refreshGraph = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  initGraph()
  updateStats()
  loading.value = false
  ElMessage.success('Knowledge graph refreshed successfully')
}

const resetView = () => {
  if (knowledgeGraph) {
    knowledgeGraph.setOption({
      series: [{
        force: {
          layoutAnimation: true
        }
      }]
    })
    ElMessage.info('View reset')
  }
}

const exportGraph = () => {
  const data = {
    nodes: graphData.value.nodes,
    edges: graphData.value.links,
    exportedAt: new Date().toISOString()
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `knowledge_graph_${new Date().toISOString()}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Graph exported successfully')
}

const searchNode = () => {
  if (!searchKeyword.value) return

  const node = graphData.value.nodes.find(n => n.name.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  if (node && knowledgeGraph) {
    knowledgeGraph.dispatchAction({
      type: 'highlight',
      seriesIndex: 0,
      name: node.name
    })
    showNodeDetails(node)
    setTimeout(() => {
      knowledgeGraph?.dispatchAction({ type: 'downplay', seriesIndex: 0 })
    }, 3000)
  } else {
    ElMessage.warning('Node not found')
  }
}

const getNodeColor = (category: string) => {
  switch (category) {
    case 'location': return '#F56C6C'
    case 'device': return '#67C23A'
    case 'system': return '#E6A23C'
    case 'metric': return '#9B59B6'
    case 'alert': return '#1ABC9C'
    default: return '#409EFF'
  }
}

const selectedNode = ref<any>(null)
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
          <span class="loading-title">Loading Knowledge Graph</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Intelligence - Knowledge Graph</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="knowledge-graph-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Knowledge Graph</h1>
        <p class="page-subtitle">Visualize relationships between devices, systems, and metrics</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="refreshGraph" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
        <el-button size="large" @click="exportGraph">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button size="large" @click="resetView">
          <el-icon><MagicStick /></el-icon>
          Reset View
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon nodes-icon">
          <el-icon><Share /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ graphStats.totalNodes }}</div>
          <div class="stat-label">Total Nodes</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ graphStats.totalEdges }} Connections</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon devices-icon">
          <el-icon><Monitor /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ graphStats.deviceCount }}</div>
          <div class="stat-label">Devices</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ graphStats.systemCount }} Systems</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon locations-icon">
          <el-icon><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ graphStats.locationCount }}</div>
          <div class="stat-label">Locations</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ graphStats.metricCount }} Metrics</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon alerts-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ graphStats.alertCount }}</div>
          <div class="stat-label">Alerts</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ graphStats.relationships }} Relationships</span>
        </div>
      </div>
    </div>

    <!-- Legend -->
    <div class="legend-container">
      <div class="legend-title">Node Types:</div>
      <div class="legend-items">
        <div v-for="type in nodeTypeOptions.slice(1)" :key="type.value" class="legend-item">
          <span class="legend-color" :style="{ background: getNodeColor(type.value) }"></span>
          <span class="legend-label">{{ type.label }}</span>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="search-bar">
      <el-input
          v-model="searchKeyword"
          placeholder="Search for a node in the graph..."
          :prefix-icon="Search"
          clearable
          style="width: 300px"
          @keyup.enter="searchNode"
      />
      <el-button type="primary" @click="searchNode">Search</el-button>
    </div>

    <!-- Graph Visualization -->
    <div class="graph-container">
      <div ref="graphRef" class="knowledge-graph" style="height: 550px"></div>
    </div>

    <!-- Node Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedNode?.name" width="550px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Node Type">
          <el-tag :type="selectedNode?.category === 'device' ? 'success' : selectedNode?.category === 'system' ? 'warning' : 'danger'" size="small">
            {{ selectedNode?.category?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Description">{{ selectedNode?.description || 'No description available' }}</el-descriptions-item>
        <el-descriptions-item label="Connections" :span="2">
          <div class="connections-info">
            <div class="connection-group">
              <strong>Incoming ({{ relatedContent?.incoming?.length || 0 }}):</strong>
              <div class="connection-tags">
                <el-tag v-for="item in relatedContent?.incoming" :key="item" size="small" style="margin: 2px">
                  {{ item }}
                </el-tag>
                <span v-if="!relatedContent?.incoming?.length" class="no-data">None</span>
              </div>
            </div>
            <div class="connection-group">
              <strong>Outgoing ({{ relatedContent?.outgoing?.length || 0 }}):</strong>
              <div class="connection-tags">
                <el-tag v-for="item in relatedContent?.outgoing" :key="item" size="small" style="margin: 2px" type="primary">
                  {{ item }}
                </el-tag>
                <span v-if="!relatedContent?.outgoing?.length" class="no-data">None</span>
              </div>
            </div>
            <div class="connection-total">
              <strong>Total Connections:</strong> {{ relatedContent?.total || 0 }}
            </div>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="searchNode">View Details</el-button>
      </template>
    </el-dialog>

    <!-- Tips -->
    <div class="tips-container">
      <div class="tip-item">
        <span class="tip-icon">💡</span>
        <span class="tip-text">Click on any node to see details</span>
      </div>
      <div class="tip-item">
        <span class="tip-icon">🖱️</span>
        <span class="tip-text">Drag nodes to rearrange the graph</span>
      </div>
      <div class="tip-item">
        <span class="tip-icon">🔍</span>
        <span class="tip-text">Use mouse wheel to zoom in/out</span>
      </div>
      <div class="tip-item">
        <span class="tip-icon">🎯</span>
        <span class="tip-text">Hover over nodes to highlight connections</span>
      </div>
    </div>
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
.knowledge-graph-container {
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

.nodes-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.devices-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.locations-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.alerts-icon {
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
  color: #67c23a;
}

.trend-up {
  color: #67c23a;
}

/* Legend Container */
.legend-container {
  background: white;
  border-radius: 16px;
  padding: 16px 20px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.legend-items {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}

.legend-label {
  font-size: 13px;
  color: #606266;
}

/* Search Bar */
.search-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  justify-content: center;
}

/* Graph Container */
.graph-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.knowledge-graph {
  width: 100%;
  min-height: 550px;
  border-radius: 12px;
}

/* Tips Container */
.tips-container {
  display: flex;
  justify-content: center;
  gap: 32px;
  flex-wrap: wrap;
  padding: 16px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.tip-icon {
  font-size: 16px;
}

/* Dialog Styles */
.connections-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.connection-group {
  padding: 8px 0;
}

.connection-tags {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
}

.connection-total {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
  font-size: 14px;
}

.no-data {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .knowledge-graph-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .legend-container {
    flex-direction: column;
    align-items: flex-start;
  }

  .search-bar {
    flex-direction: column;
  }

  .search-bar .el-input {
    width: 100% !important;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .tips-container {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
}
</style>