<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete, Monitor, Connection,
  User, Warning, Clock, Cpu, DataLine, Message, Upload, Download,
  Setting, Document, Checked, Bell, TrendCharts,
  List, Odometer, Location, Link, Share, VideoCamera, Lock,
  CopyDocument, Switch, Filter, MagicStick, Tickets, Right,
  Sort, FolderOpened, Files, DocumentAdd, Timer, Aim, DataAnalysis,
  Key, Grid, Collection, Platform, Service,
  Notification, Guide, Star, StarFilled, ShoppingCart,
  Shop, OfficeBuilding, Box, Files as FilesIcon
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing marketplace...',
  'Fetching connectors...',
  'Almost ready...'
]

// ==================== Chart Refs ====================
const categoryChart = ref<HTMLElement | null>(null)
const downloadsChart = ref<HTMLElement | null>(null)
const ratingChart = ref<HTMLElement | null>(null)

// ==================== State ====================
const activeTab = ref('marketplace')
const searchKeyword = ref('')
const categoryFilter = ref('')
const sortBy = ref('downloads')
const currentPage = ref(1)
const pageSize = ref(12)
const connectorDialogVisible = ref(false)
const installDialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const reviewDialogVisible = ref(false)
const selectedConnector = ref<any>(null)
const myConnectorsPage = ref(1)
const myConnectorsPageSize = ref(8)

// ==================== Statistics ====================
const statistics = reactive({
  totalConnectors: 48,
  officialConnectors: 32,
  communityConnectors: 16,
  totalDownloads: 12580,
  activeUsers: 342,
  avgRating: 4.6
})

// ==================== Connector Data ====================
interface Connector {
  id: number
  name: string
  version: string
  type: 'official' | 'community' | 'partner'
  category: string
  description: string
  publisher: string
  downloads: number
  rating: number
  reviews: number
  installed: boolean
  compatible: string[]
  features: string[]
  price: 'free' | 'paid'
  priceAmount?: number
  icon: string
  lastUpdated: string
  documentationUrl: string
  supportUrl: string
  requirements: string[]
}

const connectors = ref<Connector[]>([
  {
    id: 1,
    name: 'MQTT Connector',
    version: '2.1.0',
    type: 'official',
    category: 'IoT Protocols',
    description: 'High-performance MQTT connector for bidirectional communication with IoT devices',
    publisher: 'IBMS Core Team',
    downloads: 12500,
    rating: 4.8,
    reviews: 234,
    installed: true,
    compatible: ['MQTT 3.1.1', 'MQTT 5.0'],
    features: ['TLS/SSL Support', 'Last Will Testament', 'Shared Subscriptions', 'Retained Messages'],
    price: 'free',
    icon: 'Connection',
    lastUpdated: '2024-01-15',
    documentationUrl: '/docs/mqtt-connector',
    supportUrl: '/support/mqtt',
    requirements: ['Node.js 18+', 'Network access to MQTT broker']
  },
  {
    id: 2,
    name: 'BACnet Connector',
    version: '1.8.0',
    type: 'official',
    category: 'Building Automation',
    description: 'BACnet/IP and BACnet/MSTP connector for building automation systems',
    publisher: 'IBMS Core Team',
    downloads: 8900,
    rating: 4.7,
    reviews: 156,
    installed: true,
    compatible: ['BACnet/IP', 'BACnet/MSTP', 'BACnet/SC'],
    features: ['Device Discovery', 'Object Subscription', 'Trend Logs', 'Schedule Management'],
    price: 'free',
    icon: 'OfficeBuilding',
    lastUpdated: '2024-01-10',
    documentationUrl: '/docs/bacnet-connector',
    supportUrl: '/support/bacnet',
    requirements: ['BACnet network access', 'BBMD configuration for routing']
  },
  {
    id: 3,
    name: 'Modbus Connector',
    version: '3.0.1',
    type: 'official',
    category: 'Industrial Protocols',
    description: 'Modbus RTU and TCP connector for industrial equipment integration',
    publisher: 'IBMS Core Team',
    downloads: 7500,
    rating: 4.6,
    reviews: 189,
    installed: false,
    compatible: ['Modbus RTU', 'Modbus TCP', 'Modbus ASCII'],
    features: ['RTU over TCP', 'Function Code 1-16', 'Automatic retry', 'Data type conversion'],
    price: 'free',
    icon: 'Cpu',
    lastUpdated: '2024-01-12',
    documentationUrl: '/docs/modbus-connector',
    supportUrl: '/support/modbus',
    requirements: ['Serial port or network access', 'Modbus device addresses']
  },
  {
    id: 4,
    name: 'OPC-UA Connector',
    version: '2.2.0',
    type: 'official',
    category: 'Industrial Protocols',
    description: 'OPC Unified Architecture connector for industrial automation',
    publisher: 'IBMS Core Team',
    downloads: 4300,
    rating: 4.5,
    reviews: 98,
    installed: false,
    compatible: ['OPC-UA 1.04', 'OPC-UA 1.05'],
    features: ['Certificate authentication', 'Subscription model', 'Historical access', 'Method calls'],
    price: 'free',
    icon: 'Connection',
    lastUpdated: '2024-01-08',
    documentationUrl: '/docs/opcua-connector',
    supportUrl: '/support/opcua',
    requirements: ['OPC-UA server access', 'Certificate for secure connection']
  },
  {
    id: 5,
    name: 'LoRaWAN Connector',
    version: '1.5.0',
    type: 'community',
    category: 'IoT Protocols',
    description: 'LoRaWAN network server connector for LPWAN devices',
    publisher: 'Community Contributors',
    downloads: 3200,
    rating: 4.3,
    reviews: 67,
    installed: false,
    compatible: ['LoRaWAN 1.0.2', 'LoRaWAN 1.0.4'],
    features: ['Join handling', 'MAC commands', 'Class A/B/C support', 'FOTA support'],
    price: 'free',
    icon: 'Share',
    lastUpdated: '2024-01-05',
    documentationUrl: '/docs/lorawan-connector',
    supportUrl: '/support/lorawan',
    requirements: ['LoRaWAN network server API key']
  },
  {
    id: 6,
    name: 'KNX Connector',
    version: '1.3.0',
    type: 'official',
    category: 'Building Automation',
    description: 'KNX TP and IP connector for building control systems',
    publisher: 'IBMS Core Team',
    downloads: 2800,
    rating: 4.4,
    reviews: 45,
    installed: false,
    compatible: ['KNX TP1', 'KNX IP'],
    features: ['Group address mapping', 'Device management', 'Diagnostic tools', 'ETS project import'],
    price: 'free',
    icon: 'OfficeBuilding',
    lastUpdated: '2024-01-03',
    documentationUrl: '/docs/knx-connector',
    supportUrl: '/support/knx',
    requirements: ['KNX interface (USB/IP)', 'KNX project file']
  },
  {
    id: 7,
    name: 'AWS IoT Core Connector',
    version: '1.2.0',
    type: 'official',
    category: 'Cloud Services',
    description: 'Connect to AWS IoT Core for cloud-based device management',
    publisher: 'IBMS Core Team',
    downloads: 2100,
    rating: 4.7,
    reviews: 56,
    installed: false,
    compatible: ['AWS IoT Core'],
    features: ['Thing registry', 'Device shadows', 'Rules engine', 'IoT Analytics integration'],
    price: 'free',
    icon: 'Connection',
    lastUpdated: '2024-01-14',
    documentationUrl: '/docs/aws-iot',
    supportUrl: '/support/aws-iot',
    requirements: ['AWS account', 'IAM permissions']
  },
  {
    id: 8,
    name: 'Azure IoT Hub Connector',
    version: '1.1.0',
    type: 'official',
    category: 'Cloud Services',
    description: 'Azure IoT Hub integration for enterprise IoT solutions',
    publisher: 'IBMS Core Team',
    downloads: 1900,
    rating: 4.6,
    reviews: 43,
    installed: false,
    compatible: ['Azure IoT Hub'],
    features: ['Device twin', 'Direct methods', 'Cloud-to-device messaging', 'File upload'],
    price: 'free',
    icon: 'Connection',
    lastUpdated: '2024-01-09',
    documentationUrl: '/docs/azure-iot',
    supportUrl: '/support/azure-iot',
    requirements: ['Azure subscription', 'IoT Hub connection string']
  },
  {
    id: 9,
    name: 'Google Cloud IoT Connector',
    version: '1.0.0',
    type: 'official',
    category: 'Cloud Services',
    description: 'Google Cloud IoT Core connector for GCP integration',
    publisher: 'IBMS Core Team',
    downloads: 1200,
    rating: 4.4,
    reviews: 28,
    installed: false,
    compatible: ['Google Cloud IoT Core'],
    features: ['Device registry', 'Telemetry pipeline', 'Cloud Functions triggers', 'BigQuery export'],
    price: 'free',
    icon: 'Connection',
    lastUpdated: '2024-01-02',
    documentationUrl: '/docs/google-iot',
    supportUrl: '/support/google-iot',
    requirements: ['Google Cloud project', 'Service account key']
  },
  {
    id: 10,
    name: 'REST API Gateway',
    version: '2.0.0',
    type: 'official',
    category: 'Web Services',
    description: 'Universal REST API connector with customizable endpoints',
    publisher: 'IBMS Core Team',
    downloads: 5600,
    rating: 4.9,
    reviews: 178,
    installed: true,
    compatible: ['RESTful APIs', 'OpenAPI 3.0'],
    features: ['OAuth2 support', 'Rate limiting', 'Response transformation', 'Batch requests'],
    price: 'free',
    icon: 'Link',
    lastUpdated: '2024-01-15',
    documentationUrl: '/docs/rest-connector',
    supportUrl: '/support/rest',
    requirements: ['API endpoint URL', 'Authentication credentials']
  },
  {
    id: 11,
    name: 'WebSocket Connector',
    version: '1.4.0',
    type: 'community',
    category: 'Web Services',
    description: 'Real-time WebSocket connector for streaming data',
    publisher: 'Community Contributors',
    downloads: 3400,
    rating: 4.5,
    reviews: 67,
    installed: false,
    compatible: ['WebSocket (RFC 6455)'],
    features: ['Binary frames', 'Ping/Pong', 'Reconnection', 'Message queuing'],
    price: 'free',
    icon: 'Connection',
    lastUpdated: '2024-01-07',
    documentationUrl: '/docs/websocket-connector',
    supportUrl: '/support/websocket',
    requirements: ['WebSocket server URL']
  },
  {
    id: 12,
    name: 'Siemens S7 Connector',
    version: '1.2.0',
    type: 'partner',
    category: 'Industrial Protocols',
    description: 'Siemens S7 PLC connector for industrial automation (Partner Edition)',
    publisher: 'Siemens Integration',
    downloads: 1800,
    rating: 4.8,
    reviews: 42,
    installed: false,
    compatible: ['S7-1200', 'S7-1500', 'S7-300', 'S7-400'],
    features: ['Data block access', 'ISO-on-TCP', 'Multi-variable reads', 'Write operations'],
    price: 'paid',
    priceAmount: 999,
    icon: 'Cpu',
    lastUpdated: '2024-01-10',
    documentationUrl: '/docs/siemens-connector',
    supportUrl: '/support/siemens',
    requirements: ['Siemens PLC network access', 'License key']
  }
])

// ==================== User Installed Connectors ====================
const userConnectors = ref([
  { id: 1, connectorId: 1, name: 'MQTT Connector', version: '2.1.0', installedAt: '2024-01-10', status: 'active', lastUpdated: '2024-01-15' },
  { id: 2, connectorId: 2, name: 'BACnet Connector', version: '1.8.0', installedAt: '2024-01-05', status: 'active', lastUpdated: '2024-01-10' },
  { id: 3, connectorId: 10, name: 'REST API Gateway', version: '2.0.0', installedAt: '2024-01-12', status: 'active', lastUpdated: '2024-01-15' }
])

// ==================== Reviews Data ====================
const reviews = ref([
  { id: 1, connectorId: 1, user: 'john_doe', rating: 5, comment: 'Excellent MQTT connector, very reliable!', date: '2024-01-14' },
  { id: 2, connectorId: 1, user: 'jane_smith', rating: 4, comment: 'Works great, documentation could be better.', date: '2024-01-12' },
  { id: 3, connectorId: 2, user: 'bob_wilson', rating: 5, comment: 'BACnet discovery works perfectly!', date: '2024-01-10' },
  { id: 4, connectorId: 10, user: 'alice_brown', rating: 5, comment: 'Best REST API connector out there', date: '2024-01-08' }
])

// ==================== Categories ====================
const categories = [
  'All Categories',
  'IoT Protocols',
  'Building Automation',
  'Industrial Protocols',
  'Cloud Services',
  'Web Services',
  'Database Connectors',
  'Analytics Tools',
  'Security & Compliance'
]

// ==================== Computed ====================
const filteredConnectors = computed(() => {
  let filtered = connectors.value
  if (searchKeyword.value) {
    filtered = filtered.filter(c =>
        c.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.description.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        c.publisher.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (categoryFilter.value && categoryFilter.value !== 'All Categories') {
    filtered = filtered.filter(c => c.category === categoryFilter.value)
  }

  // Sort
  if (sortBy.value === 'downloads') {
    filtered = [...filtered].sort((a, b) => b.downloads - a.downloads)
  } else if (sortBy.value === 'rating') {
    filtered = [...filtered].sort((a, b) => b.rating - a.rating)
  } else if (sortBy.value === 'newest') {
    filtered = [...filtered].sort((a, b) => new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime())
  } else if (sortBy.value === 'name') {
    filtered = [...filtered].sort((a, b) => a.name.localeCompare(b.name))
  }

  return filtered
})

const paginatedConnectors = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredConnectors.value.slice(start, end)
})

const installedConnectorIds = computed(() => new Set(userConnectors.value.map(uc => uc.connectorId)))

// ==================== Methods ====================
const getConnectorIcon = (iconName: string) => {
  const icons: Record<string, any> = {
    Connection: Connection,
    OfficeBuilding: OfficeBuilding,
    Cpu: Cpu,
    Share: Share,
    Link: Link,
    Box: Box,
    FilesIcon: FilesIcon
  }
  return icons[iconName] || Connection
}

const getTypeTag = (type: string) => {
  const types: Record<string, string> = {
    official: 'primary',
    community: 'info',
    partner: 'warning'
  }
  return types[type] || 'info'
}

const getTypeText = (type: string) => {
  const texts: Record<string, string> = {
    official: 'Official',
    community: 'Community',
    partner: 'Partner'
  }
  return texts[type] || type
}

const getRatingStars = (rating: number) => {
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 >= 0.5
  const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
  return { fullStars, hasHalfStar, emptyStars }
}

const formatNumber = (num: number) => {
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

const handleInstall = (connector: Connector) => {
  selectedConnector.value = connector
  installDialogVisible.value = true
}

const handleConfirmInstall = () => {
  if (selectedConnector.value) {
    if (!installedConnectorIds.value.has(selectedConnector.value.id)) {
      userConnectors.value.push({
        id: userConnectors.value.length + 1,
        connectorId: selectedConnector.value.id,
        name: selectedConnector.value.name,
        version: selectedConnector.value.version,
        installedAt: new Date().toISOString().split('T')[0],
        status: 'active',
        lastUpdated: selectedConnector.value.lastUpdated
      })
      const index = connectors.value.findIndex(c => c.id === selectedConnector.value.id)
      if (index !== -1) {
        connectors.value[index].installed = true
      }
      ElMessage.success(`${selectedConnector.value.name} installed successfully`)
    }
    installDialogVisible.value = false
  }
}

const handleUninstall = (connector: Connector) => {
  ElMessageBox.confirm(
      `Are you sure you want to uninstall "${connector.name}"?`,
      'Confirm Uninstall',
      { type: 'warning' }
  ).then(() => {
    const index = userConnectors.value.findIndex(uc => uc.connectorId === connector.id)
    if (index !== -1) {
      userConnectors.value.splice(index, 1)
      const connIndex = connectors.value.findIndex(c => c.id === connector.id)
      if (connIndex !== -1) {
        connectors.value[connIndex].installed = false
      }
      ElMessage.success(`${connector.name} uninstalled successfully`)
    }
  }).catch(() => {})
}

const handleViewDetails = (connector: Connector) => {
  selectedConnector.value = connector
  detailsDialogVisible.value = true
}

const handleWriteReview = (connector: Connector) => {
  selectedConnector.value = connector
  reviewDialogVisible.value = true
}

const handleSubmitReview = () => {
  ElMessage.success('Review submitted successfully')
  reviewDialogVisible.value = false
}

const handleUpdateConnector = (connector: any) => {
  ElMessage.info(`Checking for updates for ${connector.name}...`)
  setTimeout(() => {
    ElMessage.success(`${connector.name} is up to date`)
  }, 1500)
}

const handleRefresh = () => {
  ElMessage.info('Refreshing marketplace...')
  setTimeout(() => {
    ElMessage.success('Marketplace refreshed')
  }, 1000)
}

const handleGetSupport = (connector: Connector) => {
  ElMessage.info(`Opening support for ${connector.name}`)
}

const handleViewDocumentation = (connector: Connector) => {
  ElMessage.info(`Opening documentation for ${connector.name}`)
}

// ==================== Initialize Charts ====================
const initCharts = () => {
  if (!categoryChart.value) return

  // Category Distribution Chart (Pie)
  const categoryDist = echarts.init(categoryChart.value)
  const categoryData: Record<string, number> = {}
  connectors.value.forEach(c => {
    categoryData[c.category] = (categoryData[c.category] || 0) + 1
  })
  categoryDist.setOption({
    tooltip: { trigger: 'item' },
    legend: { top: 'bottom', orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: Object.entries(categoryData).map(([name, value]) => ({ name, value })),
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })

  // Downloads Chart (Bar)
  const downloads = echarts.init(downloadsChart.value)
  downloads.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: connectors.value.slice(0, 8).map(c => c.name.substring(0, 15)), axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Downloads' },
    series: [{
      data: connectors.value.slice(0, 8).map(c => c.downloads),
      type: 'bar',
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#1890ff' }
    }]
  })

  // Rating Distribution Chart (Line)
  const rating = echarts.init(ratingChart.value)
  rating.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['5 Star', '4 Star', '3 Star', '2 Star', '1 Star'] },
    yAxis: { type: 'value', name: 'Number of Reviews' },
    series: [{
      data: [156, 89, 34, 12, 8],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 },
      lineStyle: { color: '#faad14', width: 2 },
      itemStyle: { color: '#faad14' }
    }]
  })

  // Handle resize
  window.addEventListener('resize', () => {
    categoryDist.resize()
    downloads.resize()
    rating.resize()
  })
}

// ==================== Watch for Tab Changes ====================
watch(activeTab, (newTab) => {
  if (newTab === 'analytics') {
    nextTick(() => {
      initCharts()
    })
  }
})

// ==================== Loading on Mount ====================
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
      if (activeTab.value === 'analytics') {
        initCharts()
      }
    }, 400)
  }, 2000)
})
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
          <span class="loading-title">Loading Connector Marketplace</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="connector-marketplace">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>Connector Marketplace</h2>
        <p>Discover, install, and manage connectors for integrating with various IoT protocols, cloud services, and third-party systems</p>
      </div>
      <div class="header-right">
        <el-button @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e8f4ff">
            <el-icon color="#1890ff" size="28"><Collection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalConnectors }}</div>
            <div class="stat-label">Total Connectors</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #e6f7e6">
            <el-icon color="#52c41a" size="28"><Checked /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.officialConnectors }}</div>
            <div class="stat-label">Official Connectors</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fff7e6">
            <el-icon color="#faad14" size="28"><Download /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ (statistics.totalDownloads / 1000).toFixed(1) }}k</div>
            <div class="stat-label">Total Downloads</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon" style="background: #fdf0e8">
            <el-icon color="#ff7a45" size="28"><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.avgRating }}</div>
            <div class="stat-label">Avg Rating</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Tabs -->
    <el-tabs v-model="activeTab" class="marketplace-tabs">
      <!-- Marketplace Tab -->
      <el-tab-pane label="Marketplace" name="marketplace">
        <div class="toolbar">
          <div class="toolbar-left">
            <el-input
                v-model="searchKeyword"
                placeholder="Search connectors..."
                clearable
                style="width: 260px"
                :prefix-icon="Search"
            />
            <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 160px">
              <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
            </el-select>
            <el-select v-model="sortBy" placeholder="Sort by" style="width: 140px">
              <el-option label="Most Downloads" value="downloads" />
              <el-option label="Highest Rated" value="rating" />
              <el-option label="Newest" value="newest" />
              <el-option label="Name A-Z" value="name" />
            </el-select>
          </div>
          <div class="toolbar-right">
            <span class="results-count">{{ filteredConnectors.length }} connectors found</span>
          </div>
        </div>

        <!-- Connectors Grid -->
        <div class="connectors-grid">
          <el-card
              v-for="connector in paginatedConnectors"
              :key="connector.id"
              class="connector-card"
              shadow="hover"
          >
            <div class="connector-header">
              <div class="connector-icon">
                <el-icon :size="32" color="#1890ff">
                  <component :is="getConnectorIcon(connector.icon)" />
                </el-icon>
              </div>
              <div class="connector-info">
                <div class="connector-name">{{ connector.name }}</div>
                <div class="connector-publisher">{{ connector.publisher }}</div>
              </div>
              <el-tag :type="getTypeTag(connector.type)" size="small">{{ getTypeText(connector.type) }}</el-tag>
            </div>

            <div class="connector-description">{{ connector.description }}</div>

            <div class="connector-meta">
              <div class="meta-item">
                <el-icon><Download /></el-icon>
                <span>{{ formatNumber(connector.downloads) }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Star /></el-icon>
                <span>{{ connector.rating }} ({{ connector.reviews }})</span>
              </div>
              <div class="meta-item">
                <el-icon><Timer /></el-icon>
                <span>{{ connector.version }}</span>
              </div>
            </div>

            <div class="connector-tags">
              <el-tag v-for="feature in connector.features.slice(0, 2)" :key="feature" size="small" effect="plain">
                {{ feature }}
              </el-tag>
              <el-tag v-if="connector.features.length > 2" size="small" effect="plain">
                +{{ connector.features.length - 2 }}
              </el-tag>
            </div>

            <div class="connector-footer">
              <div class="price-badge">
                <span v-if="connector.price === 'free'" class="free">Free</span>
                <span v-else class="paid">${{ connector.priceAmount }}</span>
              </div>
              <div class="connector-actions">
                <el-button size="small" @click="handleViewDetails(connector)">
                  Details
                </el-button>
                <el-button
                    v-if="installedConnectorIds.has(connector.id)"
                    type="danger"
                    size="small"
                    plain
                    @click="handleUninstall(connector)"
                >
                  Uninstall
                </el-button>
                <el-button
                    v-else
                    type="primary"
                    size="small"
                    @click="handleInstall(connector)"
                >
                  Install
                </el-button>
              </div>
            </div>
          </el-card>
        </div>

        <!-- Pagination -->
        <div class="pagination-wrapper">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[12, 24, 48, 96]"
              :total="filteredConnectors.length"
              layout="total, sizes, prev, pager, next, jumper"
          />
        </div>
      </el-tab-pane>

      <!-- My Connectors Tab -->
      <el-tab-pane label="My Connectors" name="my-connectors">
        <div class="my-connectors-container">
          <div v-if="userConnectors.length === 0" class="empty-state">
            <el-empty description="No connectors installed yet">
              <el-button type="primary" @click="activeTab = 'marketplace'">
                Browse Marketplace
              </el-button>
            </el-empty>
          </div>

          <div v-else class="installed-grid">
            <el-card
                v-for="uc in userConnectors"
                :key="uc.id"
                class="installed-card"
                shadow="hover"
            >
              <div class="installed-header">
                <div class="connector-icon-small">
                  <el-icon :size="24" color="#1890ff">
                    <component :is="getConnectorIcon(connectors.find(c => c.id === uc.connectorId)?.icon || 'Connection')" />
                  </el-icon>
                </div>
                <div class="installed-info">
                  <div class="installed-name">{{ uc.name }}</div>
                  <div class="installed-version">v{{ uc.version }}</div>
                </div>
                <el-tag :type="uc.status === 'active' ? 'success' : 'danger'" size="small">
                  {{ uc.status.toUpperCase() }}
                </el-tag>
              </div>

              <div class="installed-meta">
                <div class="meta-row">
                  <span class="label">Installed:</span>
                  <span class="value">{{ uc.installedAt }}</span>
                </div>
                <div class="meta-row">
                  <span class="label">Last Updated:</span>
                  <span class="value">{{ uc.lastUpdated }}</span>
                </div>
              </div>

              <div class="installed-actions">
                <el-button size="small" @click="handleViewDetails(connectors.find(c => c.id === uc.connectorId)!)">
                  Configure
                </el-button>
                <el-button size="small" @click="handleUpdateConnector(uc)">
                  Check Updates
                </el-button>
                <el-button size="small" type="danger" plain @click="handleUninstall(connectors.find(c => c.id === uc.connectorId)!)">
                  Uninstall
                </el-button>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>

      <!-- Analytics Tab -->
      <el-tab-pane label="Analytics" name="analytics">
        <div class="analytics-container">
          <el-row :gutter="16">
            <el-col :xs="24" :lg="12">
              <el-card class="analytics-card" header="Connectors by Category">
                <div ref="categoryChart" style="height: 350px"></div>
              </el-card>
            </el-col>
            <el-col :xs="24" :lg="12">
              <el-card class="analytics-card" header="Top Connectors by Downloads">
                <div ref="downloadsChart" style="height: 350px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Rating Distribution">
                <div ref="ratingChart" style="height: 300px"></div>
              </el-card>
            </el-col>
          </el-row>

          <el-row :gutter="16" style="margin-top: 16px">
            <el-col :span="24">
              <el-card class="analytics-card" header="Popular Connectors">
                <el-table :data="connectors.slice(0, 10)" style="width: 100%" stripe>
                  <el-table-column prop="name" label="Connector Name" min-width="200" />
                  <el-table-column prop="category" label="Category" width="150" />
                  <el-table-column prop="downloads" label="Downloads" width="120" align="right">
                    <template #default="{ row }">
                      {{ formatNumber(row.downloads) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="rating" label="Rating" width="120" align="center">
                    <template #default="{ row }">
                      <div class="rating-cell">
                        <el-rate v-model="row.rating" disabled show-score text-color="#ff9900" :allow-half="true" />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="type" label="Type" width="100">
                    <template #default="{ row }">
                      <el-tag :type="getTypeTag(row.type)" size="small">{{ getTypeText(row.type) }}</el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- Connector Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="selectedConnector?.name" width="800px">
      <div v-if="selectedConnector" class="connector-details">
        <div class="details-header">
          <div class="details-icon">
            <el-icon :size="48" color="#1890ff">
              <component :is="getConnectorIcon(selectedConnector.icon)" />
            </el-icon>
          </div>
          <div class="details-info">
            <h3>{{ selectedConnector.name }}</h3>
            <div class="details-meta">
              <el-tag :type="getTypeTag(selectedConnector.type)" size="small">{{ getTypeText(selectedConnector.type) }}</el-tag>
              <span class="version">v{{ selectedConnector.version }}</span>
              <span class="publisher">by {{ selectedConnector.publisher }}</span>
            </div>
            <div class="details-rating">
              <el-rate v-model="selectedConnector.rating" disabled show-score text-color="#ff9900" :allow-half="true" />
              <span class="reviews">({{ selectedConnector.reviews }} reviews)</span>
            </div>
          </div>
        </div>

        <el-divider />

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Category">{{ selectedConnector.category }}</el-descriptions-item>
          <el-descriptions-item label="Last Updated">{{ selectedConnector.lastUpdated }}</el-descriptions-item>
          <el-descriptions-item label="Downloads">{{ formatNumber(selectedConnector.downloads) }}</el-descriptions-item>
          <el-descriptions-item label="Price">
            <span v-if="selectedConnector.price === 'free'" class="free">Free</span>
            <span v-else class="paid">${{ selectedConnector.priceAmount }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Compatible Versions" :span="2">
            <el-tag v-for="comp in selectedConnector.compatible" :key="comp" size="small" style="margin-right: 4px">
              {{ comp }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Requirements" :span="2">
            <ul class="requirements-list">
              <li v-for="req in selectedConnector.requirements" :key="req">{{ req }}</li>
            </ul>
          </el-descriptions-item>
          <el-descriptions-item label="Features" :span="2">
            <ul class="features-list">
              <li v-for="feature in selectedConnector.features" :key="feature">{{ feature }}</li>
            </ul>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>Reviews</el-divider>

        <div class="reviews-section">
          <div v-for="review in reviews.filter(r => r.connectorId === selectedConnector.id)" :key="review.id" class="review-item">
            <div class="review-header">
              <strong>{{ review.user }}</strong>
              <el-rate v-model="review.rating" disabled :allow-half="true" />
              <span class="review-date">{{ review.date }}</span>
            </div>
            <div class="review-comment">{{ review.comment }}</div>
          </div>
          <div class="write-review">
            <el-button type="primary" plain @click="handleWriteReview(selectedConnector)">
              Write a Review
            </el-button>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button @click="handleViewDocumentation(selectedConnector)">
          Documentation
        </el-button>
        <el-button @click="handleGetSupport(selectedConnector)">
          Support
        </el-button>
        <el-button
            v-if="selectedConnector && !installedConnectorIds.has(selectedConnector.id)"
            type="primary"
            @click="handleInstall(selectedConnector)"
        >
          Install
        </el-button>
        <el-button
            v-else-if="selectedConnector && installedConnectorIds.has(selectedConnector.id)"
            type="danger"
            @click="handleUninstall(selectedConnector)"
        >
          Uninstall
        </el-button>
      </template>
    </el-dialog>

    <!-- Install Confirmation Dialog -->
    <el-dialog v-model="installDialogVisible" :title="`Install ${selectedConnector?.name}`" width="450px">
      <div class="install-container">
        <el-alert
            title="Installation Confirmation"
            type="info"
            :closable="false"
            show-icon
        >
          <template #default>
            <p>You are about to install {{ selectedConnector?.name }} v{{ selectedConnector?.version }}</p>
            <p>This connector will be added to your installed connectors list and will be available for use in your integrations.</p>
          </template>
        </el-alert>

        <div class="install-details" v-if="selectedConnector">
          <div class="detail-row">
            <span class="label">Publisher:</span>
            <span>{{ selectedConnector.publisher }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Type:</span>
            <span>{{ getTypeText(selectedConnector.type) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Downloads:</span>
            <span>{{ formatNumber(selectedConnector.downloads) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Rating:</span>
            <span>{{ selectedConnector.rating }}/5</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="installDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleConfirmInstall">Confirm Install</el-button>
      </template>
    </el-dialog>

    <!-- Write Review Dialog -->
    <el-dialog v-model="reviewDialogVisible" :title="`Write Review - ${selectedConnector?.name}`" width="500px">
      <el-form label-width="100px">
        <el-form-item label="Rating">
          <el-rate v-model="newReview.rating" :allow-half="true" />
        </el-form-item>
        <el-form-item label="Comment">
          <el-input
              v-model="newReview.comment"
              type="textarea"
              :rows="4"
              placeholder="Share your experience with this connector..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmitReview">Submit Review</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts">
// Helper for new review
const newReview = ref({
  rating: 5,
  comment: ''
})

export default {
  setup() {
    return {
      newReview
    }
  }
}
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
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 4px;
}

.loading-title {
  font-size: 20px;
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
  font-weight: 500;
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
.connector-marketplace {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.header-left p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a1a;
}

.stat-label {
  font-size: 14px;
  color: #8c8c8c;
  margin-top: 4px;
}

.marketplace-tabs {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.results-count {
  font-size: 13px;
  color: #666;
}

/* Connectors Grid */
.connectors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.connector-card {
  transition: all 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.connector-card:hover {
  transform: translateY(-4px);
}

.connector-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.connector-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f4ff 0%, #d4e8ff 100%);
  border-radius: 12px;
}

.connector-info {
  flex: 1;
}

.connector-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.connector-publisher {
  font-size: 12px;
  color: #999;
}

.connector-description {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.connector-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding: 8px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.connector-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 16px;
}

.connector-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.price-badge .free {
  color: #52c41a;
  font-weight: 600;
}

.price-badge .paid {
  color: #faad14;
  font-weight: 600;
}

.connector-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* My Connectors */
.my-connectors-container {
  padding: 16px 0;
}

.empty-state {
  padding: 40px 0;
}

.installed-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.installed-card {
  transition: all 0.3s ease;
}

.installed-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.connector-icon-small {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f4ff 0%, #d4e8ff 100%);
  border-radius: 10px;
}

.installed-info {
  flex: 1;
}

.installed-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.installed-version {
  font-size: 12px;
  color: #999;
}

.installed-meta {
  margin-bottom: 16px;
  padding: 8px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.meta-row .label {
  color: #999;
}

.meta-row .value {
  color: #1a1a1a;
}

.installed-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

/* Analytics */
.analytics-container {
  padding: 16px 0;
}

.analytics-card {
  height: 100%;
}

.rating-cell {
  display: flex;
  justify-content: center;
}

/* Connector Details */
.connector-details {
  padding: 8px 0;
}

.details-header {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.details-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f4ff 0%, #d4e8ff 100%);
  border-radius: 16px;
}

.details-info h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.details-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.details-meta .version {
  font-size: 13px;
  color: #666;
}

.details-meta .publisher {
  font-size: 13px;
  color: #999;
}

.details-rating {
  display: flex;
  align-items: center;
  gap: 8px;
}

.details-rating .reviews {
  font-size: 13px;
  color: #666;
}

.requirements-list, .features-list {
  margin: 0;
  padding-left: 20px;
}

.requirements-list li, .features-list li {
  margin: 4px 0;
}

.reviews-section {
  margin-top: 16px;
}

.review-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.review-date {
  font-size: 12px;
  color: #999;
}

.review-comment {
  font-size: 13px;
  color: #666;
}

.write-review {
  margin-top: 16px;
  text-align: center;
}

/* Install Dialog */
.install-container {
  padding: 8px 0;
}

.install-details {
  margin-top: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 13px;
}

.detail-row .label {
  color: #999;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }

  .connectors-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-right {
    margin-top: 16px;
  }

  .toolbar {
    flex-direction: column;
  }

  .toolbar-left {
    width: 100%;
  }

  .toolbar-left .el-input,
  .toolbar-left .el-select {
    width: 100% !important;
  }

  .connectors-grid {
    grid-template-columns: 1fr;
  }

  .installed-grid {
    grid-template-columns: 1fr;
  }

  .details-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .details-rating {
    justify-content: center;
  }

  .details-meta {
    justify-content: center;
  }
}

:deep(.el-card__header) {
  font-weight: 600;
  background-color: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-rate) {
  height: auto;
}
</style>