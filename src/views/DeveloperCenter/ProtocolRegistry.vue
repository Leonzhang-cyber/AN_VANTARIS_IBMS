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
  Lock, Key, Medal, Flag, DataAnalysis,
  EditPen, Tickets, Filter, SuccessFilled,
  List, Download as DownloadIcon
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing protocol registry...',
  'Loading protocol definitions...',
  'Checking compatibility...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedType = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const createProtocolVisible = ref(false)
const editProtocolVisible = ref(false)
const chartRef = ref(null)

let usageChart: echarts.ECharts | null = null

// Protocol type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'building', label: 'Building Automation', color: '#409EFF' },
  { value: 'industrial', label: 'Industrial', color: '#67C23A' },
  { value: 'iot', label: 'IoT', color: '#E6A23C' },
  { value: 'it', label: 'IT/Network', color: '#F56C6C' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'active', label: 'Active', color: '#67C23A' },
  { value: 'deprecated', label: 'Deprecated', color: '#909399' },
  { value: 'experimental', label: 'Experimental', color: '#E6A23C' }
]

// Protocol registry data
const protocols = ref([
  {
    id: 'PROT001', name: 'BACnet', type: 'building', version: 'BACnet/IP',
    status: 'active', port: 47808, vendor: 'ASHRAE',
    description: 'Building Automation and Control networking protocol',
    features: ['Object-oriented', 'Interoperable', 'Scalable'],
    implementations: ['Siemens', 'Schneider', 'Honeywell'],
    lastUpdated: '2024-01-15', usageCount: 12450, popularity: 98
  },
  {
    id: 'PROT002', name: 'BACnet MS/TP', type: 'building', version: 'MS/TP',
    status: 'active', port: null, vendor: 'ASHRAE',
    description: 'BACnet Master-Slave/Token Passing for serial communication',
    features: ['Serial communication', 'Cost-effective', 'Legacy support'],
    implementations: ['Siemens', 'Johnson Controls'],
    lastUpdated: '2024-01-14', usageCount: 8920, popularity: 85
  },
  {
    id: 'PROT003', name: 'Modbus TCP', type: 'industrial', version: 'TCP/IP',
    status: 'active', port: 502, vendor: 'Modbus Organization',
    description: 'Modbus protocol over TCP/IP for industrial automation',
    features: ['Simple', 'Widely adopted', 'Open standard'],
    implementations: ['Schneider', 'ABB', 'Siemens'],
    lastUpdated: '2024-01-13', usageCount: 15670, popularity: 95
  },
  {
    id: 'PROT004', name: 'Modbus RTU', type: 'industrial', version: 'RTU/ASCII',
    status: 'active', port: null, vendor: 'Modbus Organization',
    description: 'Modbus serial protocol for industrial devices',
    features: ['Serial communication', 'CRC error checking', 'Legacy compatible'],
    implementations: ['Schneider', 'ABB'],
    lastUpdated: '2024-01-12', usageCount: 11340, popularity: 88
  },
  {
    id: 'PROT005', name: 'MQTT', type: 'iot', version: '5.0',
    status: 'active', port: 1883, vendor: 'OASIS',
    description: 'Lightweight IoT messaging protocol',
    features: ['Publish/Subscribe', 'Low bandwidth', 'Quality of Service'],
    implementations: ['HiveMQ', 'EMQX', 'Mosquitto'],
    lastUpdated: '2024-01-11', usageCount: 23450, popularity: 99
  },
  {
    id: 'PROT006', name: 'OPC-UA', type: 'industrial', version: '1.05',
    status: 'active', port: 4840, vendor: 'OPC Foundation',
    description: 'Open Platform Communications Unified Architecture',
    features: ['Secure', 'Platform independent', 'Rich data modeling'],
    implementations: ['Siemens', 'ABB', 'Rockwell'],
    lastUpdated: '2024-01-10', usageCount: 9870, popularity: 92
  },
  {
    id: 'PROT007', name: 'SNMP', type: 'it', version: 'v3',
    status: 'active', port: 161, vendor: 'IETF',
    description: 'Simple Network Management Protocol',
    features: ['Network monitoring', 'Trap notifications', 'MIB support'],
    implementations: ['Cisco', 'Juniper', 'HP'],
    lastUpdated: '2024-01-09', usageCount: 17890, popularity: 94
  },
  {
    id: 'PROT008', name: 'KNX', type: 'building', version: 'TP/IP',
    status: 'active', port: 3671, vendor: 'KNX Association',
    description: 'Standard for building control',
    features: ['Multi-vendor', 'Decentralized', 'Energy efficient'],
    implementations: ['Siemens', 'ABB', 'Schneider'],
    lastUpdated: '2024-01-08', usageCount: 6780, popularity: 82
  },
  {
    id: 'PROT009', name: 'CoAP', type: 'iot', version: 'RFC 7252',
    status: 'experimental', port: 5683, vendor: 'IETF',
    description: 'Constrained Application Protocol for IoT',
    features: ['UDP-based', 'RESTful', 'Low overhead'],
    implementations: ['Eclipse', 'Californium'],
    lastUpdated: '2024-01-07', usageCount: 2340, popularity: 65
  },
  {
    id: 'PROT010', name: 'LonWorks', type: 'building', version: 'FT-10',
    status: 'deprecated', port: null, vendor: 'Echelon',
    description: 'Legacy building automation protocol',
    features: ['Peer-to-peer', 'Legacy systems'],
    implementations: ['Echelon', 'Loytec'],
    lastUpdated: '2024-01-06', usageCount: 890, popularity: 35
  }
])

// Protocol statistics
const protocolStats = reactive({
  total: 0,
  active: 0,
  deprecated: 0,
  experimental: 0,
  building: 0,
  industrial: 0,
  iot: 0,
  it: 0,
  totalUsage: 0,
  avgPopularity: 0
})

// Create protocol form
const createProtocolForm = reactive({
  name: '',
  type: 'building',
  version: '',
  port: null,
  vendor: '',
  description: '',
  features: [''],
  implementations: ['']
})

// Edit protocol form
const editProtocolForm = reactive({
  id: '',
  name: '',
  type: '',
  version: '',
  status: '',
  port: null,
  vendor: '',
  description: '',
  features: [] as string[],
  implementations: [] as string[]
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: protocols.value.length
})

// Filtered protocols
const filteredProtocols = computed(() => {
  let filtered = protocols.value
  if (searchKeyword.value) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        p.description.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(p => p.type === selectedType.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(p => p.status === selectedStatus.value)
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
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  usageChart = echarts.init(chartRef.value)
  usageChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Usage Count (K)', 'Popularity Score'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: protocols.value.map(p => p.name), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: [
      { type: 'value', name: 'Usage (K)' },
      { type: 'value', name: 'Popularity Score', min: 0, max: 100 }
    ],
    series: [
      { name: 'Usage Count (K)', type: 'bar', data: protocols.value.map(p => p.usageCount / 1000), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}K' } },
      { name: 'Popularity Score', type: 'line', data: protocols.value.map(p => p.popularity), smooth: true, lineStyle: { color: '#E6A23C', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  protocolStats.total = protocols.value.length
  protocolStats.active = protocols.value.filter(p => p.status === 'active').length
  protocolStats.deprecated = protocols.value.filter(p => p.status === 'deprecated').length
  protocolStats.experimental = protocols.value.filter(p => p.status === 'experimental').length
  protocolStats.building = protocols.value.filter(p => p.type === 'building').length
  protocolStats.industrial = protocols.value.filter(p => p.type === 'industrial').length
  protocolStats.iot = protocols.value.filter(p => p.type === 'iot').length
  protocolStats.it = protocols.value.filter(p => p.type === 'it').length
  protocolStats.totalUsage = protocols.value.reduce((sum, p) => sum + p.usageCount, 0)
  protocolStats.avgPopularity = Math.round(protocols.value.reduce((sum, p) => sum + p.popularity, 0) / protocols.value.length)
}

const handleResize = () => {
  usageChart?.resize()
}

// ==================== Protocol Functions ====================
const refreshProtocols = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Protocol registry refreshed successfully')
}

const viewProtocolDetails = (protocol: any) => {
  selectedProtocol.value = protocol
  detailsVisible.value = true
}

const editProtocol = (protocol: any) => {
  editProtocolForm.id = protocol.id
  editProtocolForm.name = protocol.name
  editProtocolForm.type = protocol.type
  editProtocolForm.version = protocol.version
  editProtocolForm.status = protocol.status
  editProtocolForm.port = protocol.port
  editProtocolForm.vendor = protocol.vendor
  editProtocolForm.description = protocol.description
  editProtocolForm.features = [...protocol.features]
  editProtocolForm.implementations = [...protocol.implementations]
  editProtocolVisible.value = true
}

const saveProtocolEdit = async () => {
  if (!editProtocolForm.name) {
    ElMessage.warning('Please enter a protocol name')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1000))

  const index = protocols.value.findIndex(p => p.id === editProtocolForm.id)
  if (index !== -1) {
    protocols.value[index] = {
      ...protocols.value[index],
      name: editProtocolForm.name,
      type: editProtocolForm.type,
      version: editProtocolForm.version,
      status: editProtocolForm.status,
      port: editProtocolForm.port,
      vendor: editProtocolForm.vendor,
      description: editProtocolForm.description,
      features: editProtocolForm.features.filter(f => f.trim()),
      implementations: editProtocolForm.implementations.filter(i => i.trim()),
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  }

  updateStats()
  initChart()
  editProtocolVisible.value = false
  ElMessage.success('Protocol updated successfully')
}

const deleteProtocol = async (protocol: any) => {
  await ElMessageBox.confirm(
      `Delete protocol "${protocol.name}"? This action cannot be undone.`,
      'Confirm Delete',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'danger'
      }
  )

  const index = protocols.value.findIndex(p => p.id === protocol.id)
  if (index !== -1) {
    protocols.value.splice(index, 1)
  }

  updateStats()
  initChart()
  ElMessage.success('Protocol deleted successfully')
}

const openCreateProtocol = () => {
  createProtocolForm.name = ''
  createProtocolForm.type = 'building'
  createProtocolForm.version = ''
  createProtocolForm.port = null
  createProtocolForm.vendor = ''
  createProtocolForm.description = ''
  createProtocolForm.features = ['']
  createProtocolForm.implementations = ['']
  createProtocolVisible.value = true
}

const addArrayItem = (array: string[]) => {
  array.push('')
}

const removeArrayItem = (array: string[], index: number) => {
  if (array.length > 1) {
    array.splice(index, 1)
  }
}

const createProtocol = async () => {
  if (!createProtocolForm.name) {
    ElMessage.warning('Please enter a protocol name')
    return
  }

  if (!createProtocolForm.version) {
    ElMessage.warning('Please enter a protocol version')
    return
  }

  const features = createProtocolForm.features.filter(f => f.trim())
  const implementations = createProtocolForm.implementations.filter(i => i.trim())

  await new Promise(resolve => setTimeout(resolve, 1000))

  const newProtocol = {
    id: `PROT${String(protocols.value.length + 1).padStart(3, '0')}`,
    name: createProtocolForm.name,
    type: createProtocolForm.type,
    version: createProtocolForm.version,
    status: 'experimental',
    port: createProtocolForm.port || null,
    vendor: createProtocolForm.vendor || 'Unknown',
    description: createProtocolForm.description || 'New protocol',
    features,
    implementations,
    lastUpdated: new Date().toISOString().split('T')[0],
    usageCount: 0,
    popularity: 0
  }

  protocols.value.unshift(newProtocol)
  updateStats()
  initChart()
  createProtocolVisible.value = false
  ElMessage.success('Protocol created successfully')
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getTypeColor = (type: string) => {
  switch (type) {
    case 'building': return '#409EFF'
    case 'industrial': return '#67C23A'
    case 'iot': return '#E6A23C'
    case 'it': return '#F56C6C'
    default: return '#909399'
  }
}

const getTypeIcon = (type: string) => {
  switch (type) {
    case 'building': return '🏢'
    case 'industrial': return '🏭'
    case 'iot': return '📡'
    case 'it': return '🖧'
    default: return '🔌'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'deprecated': return 'info'
    case 'experimental': return 'warning'
    default: return 'info'
  }
}

const getPopularityClass = (score: number) => {
  if (score >= 90) return 'popularity-high'
  if (score >= 70) return 'popularity-medium'
  return 'popularity-low'
}

const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const selectedProtocol = ref<any>(null)
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
          <span class="loading-title">Loading Protocol Registry</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Developer Center - Protocol Registry</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="protocol-registry-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Protocol Registry</h1>
        <p class="page-subtitle">Central registry of supported communication protocols</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openCreateProtocol">
          <el-icon><Plus /></el-icon>
          Register Protocol
        </el-button>
        <el-button size="large" @click="refreshProtocols" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ protocolStats.total }}</div>
          <div class="stat-label">Total Protocols</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ protocolStats.active }} Active</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon usage-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(protocolStats.totalUsage) }}</div>
          <div class="stat-label">Total Usage</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+18% this month</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon popularity-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ protocolStats.avgPopularity }}%</div>
          <div class="stat-label">Avg Popularity</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="protocolStats.avgPopularity" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon types-icon">
          <el-icon><Tickets /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ protocolStats.building }}+</div>
          <div class="stat-label">Protocol Types</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ protocolStats.experimental }} Experimental</span>
        </div>
      </div>
    </div>

    <!-- Usage Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Protocol Usage & Popularity</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="usage-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search protocols..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="type-filters">
          <span class="filter-label">Type:</span>
          <button
              v-for="t in typeOptions"
              :key="t.value"
              class="type-chip"
              :class="{ active: selectedType === t.value }"
              @click="selectedType = t.value"
          >
            <span class="chip-dot" :style="{ background: t.color }"></span>
            <span>{{ t.label }}</span>
          </button>
        </div>
        <div class="status-filters">
          <span class="filter-label">Status:</span>
          <button
              v-for="s in statusOptions"
              :key="s.value"
              class="status-chip"
              :class="{ active: selectedStatus === s.value }"
              @click="selectedStatus = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Protocols Grid -->
    <div class="protocols-grid">
      <div
          v-for="protocol in filteredProtocols"
          :key="protocol.id"
          class="protocol-card"
          :class="protocol.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="protocol-type">
            <span class="type-icon">{{ getTypeIcon(protocol.type) }}</span>
            <span class="type-name" :style="{ background: getTypeColor(protocol.type) + '20', color: getTypeColor(protocol.type) }">
              {{ protocol.type.toUpperCase() }}
            </span>
          </div>
          <div class="protocol-status">
            <el-tag :type="getStatusType(protocol.status)" size="small" effect="light">
              {{ protocol.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="protocol-name">{{ protocol.name }}</h4>
          <p class="protocol-description">{{ protocol.description }}</p>

          <!-- Version and Port -->
          <div class="protocol-meta">
            <div class="meta-item">
              <span class="meta-label">Version:</span>
              <span class="meta-value">{{ protocol.version }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Port:</span>
              <span class="meta-value">{{ protocol.port || 'N/A' }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Vendor:</span>
              <span class="meta-value">{{ protocol.vendor }}</span>
            </div>
          </div>

          <!-- Features Preview -->
          <div class="features-preview">
            <div class="features-label">Features:</div>
            <div class="features-list">
              <span v-for="feature in protocol.features.slice(0, 2)" :key="feature" class="feature-tag">
                {{ feature }}
              </span>
              <span v-if="protocol.features.length > 2" class="more">+{{ protocol.features.length - 2 }}</span>
            </div>
          </div>

          <!-- Implementations -->
          <div class="implementations-preview">
            <div class="impl-label">Implementations:</div>
            <div class="impl-list">
              <span v-for="impl in protocol.implementations.slice(0, 2)" :key="impl" class="impl-tag">
                {{ impl }}
              </span>
              <span v-if="protocol.implementations.length > 2" class="more">+{{ protocol.implementations.length - 2 }}</span>
            </div>
          </div>

          <!-- Stats -->
          <div class="protocol-stats">
            <div class="stat">
              <el-icon><DataLine /></el-icon>
              <span>{{ formatNumber(protocol.usageCount) }}</span>
            </div>
            <div class="stat">
              <el-icon><Star /></el-icon>
              <span :class="getPopularityClass(protocol.popularity)">{{ protocol.popularity }}%</span>
            </div>
            <div class="stat">
              <el-icon><Clock /></el-icon>
              <span>{{ protocol.lastUpdated }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewProtocolDetails(protocol)">
              <el-icon><Eye /></el-icon> Details
            </el-button>
            <el-button size="small" type="primary" @click="editProtocol(protocol)">
              <el-icon><Edit /></el-icon> Edit
            </el-button>
            <el-button size="small" type="danger" @click="deleteProtocol(protocol)">
              <el-icon><Delete /></el-icon> Delete
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredProtocols.length === 0" class="empty-state">
      <el-empty description="No protocols found">
        <el-button type="primary" @click="openCreateProtocol">Register Protocol</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredProtocols.length > 0" class="pagination-wrapper">
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

    <!-- Protocol Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedProtocol?.name" width="650px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Protocol ID">{{ selectedProtocol?.id }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedProtocol?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Version">{{ selectedProtocol?.version }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedProtocol?.status)" size="small">
            {{ selectedProtocol?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Port">{{ selectedProtocol?.port || 'N/A' }}</el-descriptions-item>
        <el-descriptions-item label="Vendor">{{ selectedProtocol?.vendor }}</el-descriptions-item>
        <el-descriptions-item label="Usage Count">{{ formatNumber(selectedProtocol?.usageCount) }}</el-descriptions-item>
        <el-descriptions-item label="Popularity">{{ selectedProtocol?.popularity }}%</el-descriptions-item>
        <el-descriptions-item label="Last Updated">{{ selectedProtocol?.lastUpdated }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedProtocol?.description }}</el-descriptions-item>
        <el-descriptions-item label="Features" :span="2">
          <div class="features-list-detail">
            <div v-for="f in selectedProtocol?.features" :key="f" class="feature-item">• {{ f }}</div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Implementations" :span="2">
          <div class="implementations-list">
            <el-tag v-for="i in selectedProtocol?.implementations" :key="i" size="small" style="margin: 2px">
              {{ i }}
            </el-tag>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Create Protocol Dialog -->
    <el-dialog v-model="createProtocolVisible" title="Register New Protocol" width="600px">
      <el-form :model="createProtocolForm" label-width="100px">
        <el-form-item label="Protocol Name" required>
          <el-input v-model="createProtocolForm.name" placeholder="Enter protocol name" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="createProtocolForm.type" style="width: 100%">
            <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version" required>
          <el-input v-model="createProtocolForm.version" placeholder="e.g., 1.0, TCP/IP" />
        </el-form-item>
        <el-form-item label="Port">
          <el-input-number v-model="createProtocolForm.port" :min="1" :max="65535" placeholder="Optional" />
        </el-form-item>
        <el-form-item label="Vendor">
          <el-input v-model="createProtocolForm.vendor" placeholder="Standards organization" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="createProtocolForm.description" type="textarea" rows="2" placeholder="Protocol description" />
        </el-form-item>
        <el-form-item label="Features">
          <div v-for="(feature, idx) in createProtocolForm.features" :key="idx" class="array-item">
            <el-input v-model="createProtocolForm.features[idx]" placeholder="Feature description" />
            <el-button type="danger" link @click="removeArrayItem(createProtocolForm.features, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(createProtocolForm.features)">
            <el-icon><Plus /></el-icon> Add Feature
          </el-button>
        </el-form-item>
        <el-form-item label="Implementations">
          <div v-for="(impl, idx) in createProtocolForm.implementations" :key="idx" class="array-item">
            <el-input v-model="createProtocolForm.implementations[idx]" placeholder="Vendor name" />
            <el-button type="danger" link @click="removeArrayItem(createProtocolForm.implementations, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(createProtocolForm.implementations)">
            <el-icon><Plus /></el-icon> Add Implementation
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createProtocolVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createProtocol">Register Protocol</el-button>
      </template>
    </el-dialog>

    <!-- Edit Protocol Dialog -->
    <el-dialog v-model="editProtocolVisible" title="Edit Protocol" width="600px">
      <el-form :model="editProtocolForm" label-width="100px">
        <el-form-item label="Protocol Name" required>
          <el-input v-model="editProtocolForm.name" placeholder="Enter protocol name" />
        </el-form-item>
        <el-form-item label="Type">
          <el-select v-model="editProtocolForm.type" style="width: 100%">
            <el-option v-for="t in typeOptions.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="editProtocolForm.version" placeholder="e.g., 1.0, TCP/IP" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="editProtocolForm.status" style="width: 100%">
            <el-option label="Active" value="active" />
            <el-option label="Deprecated" value="deprecated" />
            <el-option label="Experimental" value="experimental" />
          </el-select>
        </el-form-item>
        <el-form-item label="Port">
          <el-input-number v-model="editProtocolForm.port" :min="1" :max="65535" placeholder="Optional" />
        </el-form-item>
        <el-form-item label="Vendor">
          <el-input v-model="editProtocolForm.vendor" placeholder="Standards organization" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="editProtocolForm.description" type="textarea" rows="2" placeholder="Protocol description" />
        </el-form-item>
        <el-form-item label="Features">
          <div v-for="(feature, idx) in editProtocolForm.features" :key="idx" class="array-item">
            <el-input v-model="editProtocolForm.features[idx]" placeholder="Feature description" />
            <el-button type="danger" link @click="removeArrayItem(editProtocolForm.features, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(editProtocolForm.features)">
            <el-icon><Plus /></el-icon> Add Feature
          </el-button>
        </el-form-item>
        <el-form-item label="Implementations">
          <div v-for="(impl, idx) in editProtocolForm.implementations" :key="idx" class="array-item">
            <el-input v-model="editProtocolForm.implementations[idx]" placeholder="Vendor name" />
            <el-button type="danger" link @click="removeArrayItem(editProtocolForm.implementations, idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          <el-button type="primary" link @click="addArrayItem(editProtocolForm.implementations)">
            <el-icon><Plus /></el-icon> Add Implementation
          </el-button>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editProtocolVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveProtocolEdit">Save Changes</el-button>
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
.protocol-registry-container {
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

.usage-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.popularity-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.types-icon {
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

.trend-neutral {
  color: #909399;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
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

.usage-chart {
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

.type-filters,
.status-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.type-chip,
.status-chip {
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

.type-chip:hover,
.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.type-chip.active,
.status-chip.active {
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

/* Protocols Grid */
.protocols-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.protocol-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.protocol-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.protocol-card.active {
  border-left: 4px solid #67c23a;
}

.protocol-card.deprecated {
  border-left: 4px solid #909399;
}

.protocol-card.experimental {
  border-left: 4px solid #e6a23c;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.protocol-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
}

.type-name {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.protocol-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.protocol-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.protocol-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  gap: 4px;
  font-size: 12px;
}

.meta-label {
  color: #909399;
}

.meta-value {
  color: #1e293b;
  font-weight: 500;
}

.features-preview,
.implementations-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.features-label,
.impl-label {
  font-size: 11px;
  color: #909399;
}

.features-list,
.impl-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.feature-tag,
.impl-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 12px;
}

.more {
  font-size: 11px;
  color: #909399;
}

.protocol-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}

.popularity-high {
  color: #67c23a;
  font-weight: 600;
}

.popularity-medium {
  color: #e6a23c;
  font-weight: 600;
}

.popularity-low {
  color: #f56c6c;
  font-weight: 600;
}

/* Card Footer */
.card-footer {
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
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
.array-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.array-item .el-input {
  flex: 1;
}

.features-list-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-item {
  font-size: 13px;
  color: #606266;
}

.implementations-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .protocols-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .protocol-registry-container {
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

  .type-filters,
  .status-filters {
    flex-wrap: wrap;
    justify-content: center;
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

  .protocols-grid {
    grid-template-columns: 1fr;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }

  .protocol-meta {
    flex-direction: column;
    gap: 4px;
  }
}
</style>