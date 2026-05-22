<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VueFlow } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import {
  Plus, Search, RefreshRight, Setting, Connection, Warning,
  Document, Download, Delete, Cpu, ArrowDown, Edit, User,
  Check, Close, Refresh, Upload, Monitor
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing edge infrastructure...',
  'Loading node topology...',
  'Initializing gateway connections...',
  'Syncing blockchain status...',
  'Almost ready...'
]

// ==================== Statistics ====================
const stats = ref({
  totalNodes: 6,
  onlineNodes: 6,
  totalDevices: 347,
  todaySyncData: '2.34 GB'
})

// ==================== Edge Nodes Data - All Online ====================
interface EdgeNode {
  id: number
  name: string
  site: string
  siteType: 'Factory' | 'Building' | 'Warehouse' | 'Office'
  ipAddress: string
  deviceCount: number
  onlineStatus: 'online' | 'offline' | 'warning'
  lastHeartbeat: string
  softwareVersion: string
  cpuUsage: number
  memoryUsage: number
  diskUsage: number
  blockchainHeight: number
  localStorage: string
  publicKey: string
  did: string
  latitude?: number
  longitude?: number
}

const edgeNodes = ref<EdgeNode[]>([
  {
    id: 1, name: 'Edge-Gateway-SG-01', site: 'Singapore Data Center', siteType: 'Factory',
    ipAddress: '10.0.1.101', deviceCount: 45, onlineStatus: 'online',
    lastHeartbeat: '2025-04-17 14:32:15', softwareVersion: 'v2.1.0',
    cpuUsage: 42, memoryUsage: 56, diskUsage: 38, blockchainHeight: 1024,
    localStorage: '128 GB', publicKey: '0x8a7b9c...3f2e1d',
    did: 'did:edge:0x8a7b9c...3f2e1d', latitude: 1.3521, longitude: 103.8198
  },
  {
    id: 2, name: 'Edge-Gateway-SG-02', site: 'Singapore Office Tower', siteType: 'Office',
    ipAddress: '10.0.1.102', deviceCount: 28, onlineStatus: 'online',
    lastHeartbeat: '2025-04-17 14:31:42', softwareVersion: 'v2.1.0',
    cpuUsage: 23, memoryUsage: 34, diskUsage: 25, blockchainHeight: 1020,
    localStorage: '64 GB', publicKey: '0x2c4d5e...7a8b9c',
    did: 'did:edge:0x2c4d5e...7a8b9c', latitude: 1.2801, longitude: 103.8500
  },
  {
    id: 3, name: 'Edge-Gateway-HK-01', site: 'Hong Kong Warehouse', siteType: 'Warehouse',
    ipAddress: '10.0.2.103', deviceCount: 62, onlineStatus: 'online',
    lastHeartbeat: '2025-04-17 14:32:08', softwareVersion: 'v2.1.0',
    cpuUsage: 67, memoryUsage: 78, diskUsage: 52, blockchainHeight: 1018,
    localStorage: '256 GB', publicKey: '0x5e6f7g...8h9i0j',
    did: 'did:edge:0x5e6f7g...8h9i0j', latitude: 22.3193, longitude: 114.1694
  },
  {
    id: 4, name: 'Edge-Gateway-HK-02', site: 'Hong Kong Factory', siteType: 'Factory',
    ipAddress: '10.0.2.104', deviceCount: 38, onlineStatus: 'online',
    lastHeartbeat: '2025-04-17 14:20:33', softwareVersion: 'v2.1.0',
    cpuUsage: 45, memoryUsage: 52, diskUsage: 41, blockchainHeight: 1022,
    localStorage: '128 GB', publicKey: '0x9i0j1k...2l3m4n',
    did: 'did:edge:0x9i0j1k...2l3m4n', latitude: 22.3964, longitude: 114.1095
  },
  {
    id: 5, name: 'Edge-Gateway-SG-03', site: 'Singapore R&D Center', siteType: 'Office',
    ipAddress: '10.0.1.105', deviceCount: 15, onlineStatus: 'online',
    lastHeartbeat: '2025-04-17 14:30:21', softwareVersion: 'v2.1.0',
    cpuUsage: 34, memoryUsage: 45, diskUsage: 38, blockchainHeight: 1023,
    localStorage: '64 GB', publicKey: '0x3m4n5o...6p7q8r',
    did: 'did:edge:0x3m4n5o...6p7q8r', latitude: 1.2900, longitude: 103.7800
  },
  {
    id: 6, name: 'Edge-Gateway-HK-03', site: 'Hong Kong Office', siteType: 'Office',
    ipAddress: '10.0.2.106', deviceCount: 54, onlineStatus: 'online',
    lastHeartbeat: '2025-04-17 14:32:01', softwareVersion: 'v2.1.0',
    cpuUsage: 34, memoryUsage: 45, diskUsage: 41, blockchainHeight: 1023,
    localStorage: '128 GB', publicKey: '0x7q8r9s...0t1u2v',
    did: 'did:edge:0x7q8r9s...0t1u2v', latitude: 22.2793, longitude: 114.1628
  }
])

// ==================== Topology Related ====================
const topologyRef = ref<HTMLElement | null>(null)
const flowNodes = ref<Node[]>([])
const flowEdges = ref<Edge[]>([])
const nodePositionsCache = ref<Map<string, { x: number; y: number }>>(new Map())

// Fixed node positions - 2 rows, 3 columns grid layout
const getFixedNodePositions = (canvasWidth: number, canvasHeight: number) => {
  const cols = 3
  const rows = 2
  const cellWidth = canvasWidth / cols
  const cellHeight = canvasHeight / rows

  const nodeWidth = 170
  const nodeHeight = 140

  return edgeNodes.value.map((node, index) => {
    const col = index % cols
    const row = Math.floor(index / cols)
    return {
      x: col * cellWidth + (cellWidth - nodeWidth) / 2,
      y: row * cellHeight + (cellHeight - nodeHeight) / 2
    }
  })
}

// Convert geo coordinates to canvas positions
const convertGeoToCanvas = (longitude: number, latitude: number, width: number, height: number) => {
  const minLng = 100, maxLng = 125
  const minLat = 1, maxLat = 25

  const x = ((longitude - minLng) / (maxLng - minLng)) * width
  const y = ((maxLat - latitude) / (maxLat - minLat)) * height
  return { x: Math.max(60, Math.min(width - 60, x)), y: Math.max(60, Math.min(height - 60, y)) }
}

// Update topology
const updateTopology = () => {
  if (!topologyRef.value || edgeNodes.value.length === 0) return
  const rect = topologyRef.value.getBoundingClientRect()
  const width = rect.width - 80
  const height = rect.height - 80

  const positions = getFixedNodePositions(width, height)

  flowNodes.value = edgeNodes.value.map((node, idx) => {
    const cachedPos = nodePositionsCache.value.get(node.id.toString())
    return {
      id: node.id.toString(),
      type: 'custom',
      position: cachedPos || positions[idx],
      data: {
        id: node.id,
        name: node.name,
        site: node.site,
        status: node.onlineStatus,
        deviceCount: node.deviceCount,
        cpuUsage: node.cpuUsage
      }
    }
  })

  const edges: Edge[] = []
  for (let i = 0; i < edgeNodes.value.length; i++) {
    for (let j = i + 1; j < edgeNodes.value.length; j++) {
      edges.push({
        id: `edge-${i}-${j}`,
        source: edgeNodes.value[i].id.toString(),
        target: edgeNodes.value[j].id.toString(),
        animated: true,
        style: {
          stroke: '#52c41a',
          strokeWidth: 2
        },
        label: 'P2P Connected',
        labelStyle: {
          fill: '#52c41a',
          fontSize: 10,
          background: '#fff',
          padding: '2px 6px',
          borderRadius: '12px'
        }
      })
    }
  }
  flowEdges.value = edges
}

const resetTopologyView = () => {
  nodePositionsCache.value.clear()
  updateTopology()
}

const handleNodeDragStop = (event: any) => {
  if (event.node) {
    nodePositionsCache.value.set(event.node.id, {
      x: event.node.position.x,
      y: event.node.position.y
    })
  }
}

const handleResize = () => {
  if (isLoaded.value) {
    updateTopology()
  }
}

// ==================== Node Details ====================
const showDetailDialog = ref(false)
const currentNode = ref<EdgeNode | null>(null)

const nodeLogs = ref([
  { timestamp: '2025-04-17 14:32:15', level: 'INFO', message: 'Device data sync completed' },
  { timestamp: '2025-04-17 14:30:22', level: 'INFO', message: 'Blockchain height updated to #1024' },
  { timestamp: '2025-04-17 14:28:10', level: 'INFO', message: 'Network latency: 56ms' },
  { timestamp: '2025-04-17 14:25:33', level: 'INFO', message: 'Merkle tree root hash generated' },
  { timestamp: '2025-04-17 14:20:05', level: 'INFO', message: 'Data sync completed successfully' }
])

// ==================== Add Node ====================
const showAddDialog = ref(false)
const addForm = ref({ name: '', site: '', gatewayType: '', serialNumber: '', publicKey: '' })

const siteOptions = [
  { label: 'Singapore Data Center', value: 'Singapore Data Center', type: 'Factory', lat: 1.3521, lng: 103.8198 },
  { label: 'Singapore Office Tower', value: 'Singapore Office Tower', type: 'Office', lat: 1.2801, lng: 103.8500 },
  { label: 'Hong Kong Warehouse', value: 'Hong Kong Warehouse', type: 'Warehouse', lat: 22.3193, lng: 114.1694 },
  { label: 'Hong Kong Factory', value: 'Hong Kong Factory', type: 'Factory', lat: 22.3964, lng: 114.1095 },
  { label: 'Singapore R&D Center', value: 'Singapore R&D Center', type: 'Office', lat: 1.2900, lng: 103.7800 },
  { label: 'Hong Kong Office', value: 'Hong Kong Office', type: 'Office', lat: 22.2793, lng: 114.1628 }
]

const gatewayTypeOptions = ['Industrial Gateway', 'Edge AI Box', 'IoT Gateway', 'Lightweight Edge']

const generatePublicKey = () => {
  const chars = '0123456789abcdef'
  let result = '0x'
  for (let i = 0; i < 40; i++) result += chars[Math.floor(Math.random() * 16)]
  addForm.value.publicKey = result
}

const downloadScript = () => {
  const script = `#!/bin/bash\n# Edge Node Installation Script\n# Node Name: ${addForm.value.name}\n# DID: did:edge:${addForm.value.publicKey.substring(0, 16)}...\n\ndocker run -d --name edge-agent-${addForm.value.name} -e NODE_NAME="${addForm.value.name}" -e SITE="${addForm.value.site}" -e PUBLIC_KEY="${addForm.value.publicKey}" registry.blockchain.com/edge-agent:latest`
  const blob = new Blob([script], { type: 'text/plain' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `install-${addForm.value.name || 'edge-node'}.sh`
  link.click()
  URL.revokeObjectURL(link.href)
  ElMessage.success('Installation script downloaded')
}

// ==================== Firmware Management ====================
const showFirmwareDialog = ref(false)
const firmwares = ref([
  { version: 'v2.1.0', releaseDate: '2025-04-01', size: '245 MB', changelog: 'Added edge caching, improved sync performance' },
  { version: 'v2.0.5', releaseDate: '2025-03-15', size: '238 MB', changelog: 'Bug fixes, security updates' }
])

const upgradeProgress = ref<Map<number, number>>(new Map())

const startUpgrade = async (node: EdgeNode, version: string) => {
  await ElMessageBox.confirm(`Upgrade ${node.name} to ${version}?`, 'Confirm', { type: 'warning' })
  upgradeProgress.value.set(node.id, 0)
  for (let i = 0; i <= 100; i += 20) {
    await new Promise(resolve => setTimeout(resolve, 300))
    upgradeProgress.value.set(node.id, i)
  }
  node.softwareVersion = version
  ElMessage.success(`${node.name} upgraded successfully`)
  setTimeout(() => upgradeProgress.value.delete(node.id), 2000)
}

// ==================== Data Sync Strategy ====================
const showSyncStrategyDialog = ref(false)
const syncStrategy = ref({
  frequency: '30',
  frequencyUnit: 'seconds',
  dataTypes: ['device-status', 'sensor-data', 'events'],
  localStorage: true,
  blockchainSync: true,
  offlineCache: true,
  retryCount: 3,
  batchSize: 100
})

// ==================== Edge Attestation ====================
const showAttestationDialog = ref(false)
const attestationRecords = ref([
  { timestamp: '2025-04-17 14:00:00', rootHash: '0x7d8f9a...3e2b1c', blockHeight: 1024, verified: true },
  { timestamp: '2025-04-17 13:00:00', rootHash: '0x5c6d7e...8f9a0b', blockHeight: 1015, verified: true },
  { timestamp: '2025-04-17 12:00:00', rootHash: '0x3a4b5c...6d7e8f', blockHeight: 1008, verified: true }
])

// ==================== Search and Filter ====================
const searchKeyword = ref('')
const statusFilter = ref('all')

const filteredNodes = computed(() => {
  let filtered = edgeNodes.value
  if (searchKeyword.value) {
    filtered = filtered.filter(n =>
        n.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        n.site.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(n => n.onlineStatus === statusFilter.value)
  }
  return filtered
})

// ==================== Node Operations ====================
const viewDeviceList = (node: EdgeNode) => ElMessage.info(`View devices for ${node.name}`)
const syncLogs = (node: EdgeNode) => ElMessage.info(`Syncing logs for ${node.name}`)

const restartGateway = async (node: EdgeNode) => {
  await ElMessageBox.confirm(`Restart ${node.name}?`, 'Confirm', { type: 'warning' })
  ElMessage.success(`${node.name} restarting...`)
}

const resetData = async (node: EdgeNode) => {
  await ElMessageBox.confirm(`Reset data for ${node.name}?`, 'Confirm', { type: 'warning' })
  ElMessage.success(`${node.name} data reset initiated`)
}

const editNode = (node: EdgeNode) => {
  currentNode.value = node
  showDetailDialog.value = true
}

const deleteNode = async (node: EdgeNode) => {
  await ElMessageBox.confirm(`Delete ${node.name}?`, 'Confirm', { type: 'error' })
  const index = edgeNodes.value.findIndex(n => n.id === node.id)
  if (index !== -1) {
    edgeNodes.value.splice(index, 1)
    stats.value.totalNodes--
    stats.value.onlineNodes--
    updateTopology()
    ElMessage.success('Node deleted')
  }
}

const addNewNode = () => {
  const newId = Math.max(...edgeNodes.value.map(n => n.id)) + 1
  const selectedSite = siteOptions.find(s => s.value === addForm.value.site)
  edgeNodes.value.push({
    id: newId,
    name: addForm.value.name,
    site: addForm.value.site,
    siteType: selectedSite?.type || 'Factory',
    ipAddress: `10.0.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
    deviceCount: 0,
    onlineStatus: 'online',
    lastHeartbeat: new Date().toLocaleString(),
    softwareVersion: 'v2.1.0',
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
    blockchainHeight: 1024,
    localStorage: '64 GB',
    publicKey: addForm.value.publicKey,
    did: `did:edge:${addForm.value.publicKey.substring(0, 16)}...`,
    latitude: selectedSite?.lat,
    longitude: selectedSite?.lng
  })
  stats.value.totalNodes++
  stats.value.onlineNodes++
  showAddDialog.value = false
  addForm.value = { name: '', site: '', gatewayType: '', serialNumber: '', publicKey: '' }
  updateTopology()
  ElMessage.success('Edge node registered successfully')
}

const verifyAttestation = (record: any) => {
  if (record.verified) {
    ElMessage.success('Attestation verified: Consistent with cloud')
  } else {
    ElMessage.error('Attestation mismatch detected!')
  }
}

const onNodeClick = (event: any) => {
  const node = edgeNodes.value.find(n => n.id === parseInt(event.node.id))
  if (node) {
    currentNode.value = node
    showDetailDialog.value = true
  }
}

// ==================== Initialization ====================
onMounted(() => {
  let progress = 0, msgIndex = 0
  const msgInterval = setInterval(() => {
    if (msgIndex < loadingMessages.length - 1) {
      msgIndex++
      loadingMessage.value = loadingMessages[msgIndex]
    }
  }, 500)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 15 + 5
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 200)

  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        updateTopology()
      })
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner"><div class="spinner-ring"></div><div class="spinner-ring"></div><div class="spinner-ring"></div></div>
        <div class="loading-text"><span class="loading-title">Loading</span><span class="loading-dots"><span>.</span><span>.</span><span>.</span></span></div>
        <div class="loading-progress"><div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div></div>
        <div class="loading-tip">Edge Nodes Management</div><div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <div v-else class="edge-nodes-page">
    <div class="page-header">
      <h2>🔌 Edge Nodes Management</h2>
      <el-button type="primary" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon> Register New Edge Node
      </el-button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">📡</div>
        <div class="stat-value">{{ stats.totalNodes }}</div>
        <div class="stat-label">Total Edge Nodes</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon online">🟢</div>
        <div class="stat-value">{{ stats.onlineNodes }}</div>
        <div class="stat-label">Online Nodes</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon devices">🔌</div>
        <div class="stat-value">{{ stats.totalDevices }}</div>
        <div class="stat-label">Total Devices</div>
      </div>
      <div class="stat-card">
        <div class="stat-icon sync">📤</div>
        <div class="stat-value">{{ stats.todaySyncData }}</div>
        <div class="stat-label">Today's Data Sync</div>
      </div>
    </div>

    <div class="topology-card">
      <div class="topology-header">
        <span>🗺️ Edge Nodes Geographic Distribution</span>
        <div class="topology-legend">
          <span class="legend-dot online"></span>Online
          <span class="legend-dot offline"></span>Offline
          <span class="legend-dot warning"></span>Warning
          <span class="legend-dot edge"></span>Data Sync
        </div>
        <el-button size="small" text @click="resetTopologyView">
          <el-icon><RefreshRight /></el-icon> Reset View
        </el-button>
      </div>
      <div class="topology-canvas" ref="topologyRef">
        <VueFlow
            v-model="flowNodes"
            v-model:edges="flowEdges"
            class="vue-flow-wrapper"
            :default-viewport="{ zoom: 0.8, x: 50, y: 50 }"
            :fit-view-on-init="true"
            :nodes-draggable="true"
            :zoom-on-scroll="true"
            :min-zoom="0.5"
            :max-zoom="1.5"
            @node-drag-stop="handleNodeDragStop"
            @node-click="onNodeClick"
        >
          <template #node-custom="nodeProps">
            <div class="topology-node" :class="nodeProps.data.status">
              <div class="node-icon">🖥️</div>
              <div class="node-name">{{ nodeProps.data.name }}</div>
              <div class="node-site">{{ nodeProps.data.site }}</div>
              <div class="node-stats">
                <span>{{ nodeProps.data.deviceCount }} devices</span>
                <span>{{ nodeProps.data.cpuUsage }}% CPU</span>
              </div>
              <div class="node-status-badge" :class="nodeProps.data.status">
                {{ nodeProps.data.status === 'online' ? '● Online' : nodeProps.data.status === 'warning' ? '⚠ Warning' : '○ Offline' }}
              </div>
            </div>
          </template>
        </VueFlow>
      </div>
    </div>

    <div class="action-bar">
      <el-input v-model="searchKeyword" placeholder="Search by name or site" :prefix-icon="Search" clearable class="search-input" />
      <el-select v-model="statusFilter" placeholder="Status" class="status-filter">
        <el-option label="All" value="all" />
        <el-option label="Online" value="online" />
        <el-option label="Offline" value="offline" />
        <el-option label="Warning" value="warning" />
      </el-select>
      <el-button @click="showSyncStrategyDialog = true">
        <el-icon><Connection /></el-icon> Sync Strategy
      </el-button>
    </div>

    <div class="table-card">
      <el-table :data="filteredNodes" stripe :default-sort="{ prop: 'lastHeartbeat', order: 'descending' }">
        <el-table-column prop="name" label="Node Name" min-width="180"  align="center">
          <template #default="{ row }">
            <el-link type="primary" @click="currentNode = row; showDetailDialog = true">{{ row.name }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="site" label="Site" min-width="180"  align="center" />
        <el-table-column prop="ipAddress" label="IP Address" min-width="130"  align="center" />
        <el-table-column prop="deviceCount" label="Devices" width="80" align="center" />
        <el-table-column prop="onlineStatus" label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.onlineStatus === 'online' ? 'success' : row.onlineStatus === 'warning' ? 'warning' : 'danger'" size="small">
              {{ row.onlineStatus === 'online' ? 'Online' : row.onlineStatus === 'warning' ? 'Warning' : 'Offline' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastHeartbeat" label="Last Heartbeat" width="170" sortable  align="center" />
        <el-table-column prop="softwareVersion" label="Version" width="90"  align="center" />
        <el-table-column label="Upgrade" width="120"  align="center">
          <template #default="{ row }">
            <div v-if="upgradeProgress.has(row.id)" class="upgrade-progress">
              <el-progress :percentage="upgradeProgress.get(row.id) || 0" :stroke-width="6" />
            </div>
            <span v-else class="version-text">{{ row.softwareVersion }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="260" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" @click="viewDeviceList(row)">
              <el-icon><Cpu /></el-icon>Devices
            </el-button>
            <el-button size="small" type="primary" @click="syncLogs(row)" style="margin-right: 20px">
              <el-icon><RefreshRight /></el-icon>Sync
            </el-button>
            <el-dropdown @command="(cmd) => { if (cmd === 'edit') editNode(row); else if (cmd === 'restart') restartGateway(row); else if (cmd === 'reset') resetData(row); else if (cmd === 'delete') deleteNode(row) }">
              <el-button size="small">
                More<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">Edit</el-dropdown-item>
                  <el-dropdown-item command="restart">Restart Gateway</el-dropdown-item>
                  <el-dropdown-item command="reset">Reset Data</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Node Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="currentNode?.name" width="900px" class="detail-dialog">
      <div v-if="currentNode" class="node-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Node Name">{{ currentNode.name }}</el-descriptions-item>
          <el-descriptions-item label="Site">{{ currentNode.site }}</el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ currentNode.ipAddress }}</el-descriptions-item>
          <el-descriptions-item label="DID">{{ currentNode.did }}</el-descriptions-item>
          <el-descriptions-item label="Software Version">{{ currentNode.softwareVersion }}</el-descriptions-item>
          <el-descriptions-item label="Local Storage">{{ currentNode.localStorage }}</el-descriptions-item>
        </el-descriptions>

        <div class="monitoring-section">
          <h4>📊 Real-time Monitoring</h4>
          <div class="metrics-grid">
            <div class="metric">
              <div class="metric-label">CPU Usage</div>
              <el-progress :percentage="currentNode.cpuUsage" :color="currentNode.cpuUsage > 80 ? '#f56c6c' : '#67c23a'" />
            </div>
            <div class="metric">
              <div class="metric-label">Memory Usage</div>
              <el-progress :percentage="currentNode.memoryUsage" :color="currentNode.memoryUsage > 80 ? '#f56c6c' : '#67c23a'" />
            </div>
            <div class="metric">
              <div class="metric-label">Disk Usage</div>
              <el-progress :percentage="currentNode.diskUsage" :color="currentNode.diskUsage > 80 ? '#f56c6c' : '#67c23a'" />
            </div>
          </div>
          <div class="info-row">
            <span>Blockchain Sync Height:</span>
            <strong>#{{ currentNode.blockchainHeight }}</strong>
          </div>
        </div>

        <div class="logs-section">
          <h4>📋 Recent Node Logs</h4>
          <div class="logs-list">
            <div v-for="(log, idx) in nodeLogs.slice(0, 8)" :key="idx" class="log-item" :class="log.level.toLowerCase()">
              <span class="log-time">{{ log.timestamp }}</span>
              <span class="log-level">[{{ log.level }}]</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </div>

        <div class="action-buttons">
          <el-button type="danger" @click="restartGateway(currentNode)">
            <el-icon><RefreshRight /></el-icon> Restart Gateway
          </el-button>
          <el-button @click="resetData(currentNode)">
            <el-icon><Delete /></el-icon> Reset Data
          </el-button>
          <el-button type="primary" @click="showAttestationDialog = true">
            <el-icon><Document /></el-icon> View Attestations
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- Add Node Dialog -->
    <el-dialog v-model="showAddDialog" title="Register New Edge Node" width="600px">
      <el-form :model="addForm" label-width="100px">
        <el-form-item label="Node Name" required>
          <el-input v-model="addForm.name" placeholder="e.g., Edge-Gateway-SG-01" />
        </el-form-item>
        <el-form-item label="Site" required>
          <el-select v-model="addForm.site" placeholder="Select site" style="width: 100%">
            <el-option v-for="opt in siteOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Gateway Type" required>
          <el-select v-model="addForm.gatewayType" placeholder="Select type" style="width: 100%">
            <el-option v-for="type in gatewayTypeOptions" :key="type" :label="type" :value="type" />
          </el-select>
        </el-form-item>
        <el-form-item label="Serial Number" required>
          <el-input v-model="addForm.serialNumber" placeholder="Enter serial number" />
        </el-form-item>
        <el-form-item label="Public Key">
          <el-input v-model="addForm.publicKey" placeholder="Click generate" />
          <el-button size="small" @click="generatePublicKey" style="margin-top: 8px">Generate Public Key</el-button>
        </el-form-item>
      </el-form>
      <div v-if="addForm.publicKey" class="config-script">
        <el-divider>Installation Configuration</el-divider>
        <div class="did-info">
          <strong>Node DID:</strong> did:edge:{{ addForm.publicKey.substring(0, 16) }}...
        </div>
        <el-button type="primary" size="small" @click="downloadScript">
          <el-icon><Download /></el-icon> Download Install Script
        </el-button>
      </div>
      <template #footer>
        <el-button @click="showAddDialog = false">Cancel</el-button>
        <el-button type="primary" @click="addNewNode" :disabled="!addForm.name || !addForm.site || !addForm.publicKey">Register</el-button>
      </template>
    </el-dialog>

    <!-- Attestation Dialog -->
    <el-dialog v-model="showAttestationDialog" title="Edge Attestation Records" width="800px">
      <el-table :data="attestationRecords" stripe>
        <el-table-column prop="timestamp" label="Timestamp" width="180" />
        <el-table-column prop="rootHash" label="Merkle Root Hash" />
        <el-table-column prop="blockHeight" label="Block Height" width="120" align="center" />
        <el-table-column label="Verification" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.verified ? 'success' : 'danger'" size="small">
              {{ row.verified ? 'Verified' : 'Mismatch' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="verifyAttestation(row)">Verify</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="attestation-tip">
        <el-icon><Warning /></el-icon> Merkle tree root hashes anchored to blockchain
      </div>
    </el-dialog>

    <!-- Firmware Management Dialog -->
    <el-dialog v-model="showFirmwareDialog" title="Firmware Management" width="800px">
      <el-table :data="firmwares" stripe>
        <el-table-column prop="version" label="Version" width="100">
          <template #default="{ row }">
            <el-tag>{{ row.version }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="releaseDate" label="Release Date" width="120" />
        <el-table-column prop="size" label="Size" width="80" />
        <el-table-column prop="changelog" label="Changelog" />
        <el-table-column label="Actions" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="() => { edgeNodes.forEach(node => { if (node.onlineStatus === 'online') startUpgrade(node, row.version) }); ElMessage.info('Batch upgrade started') }">
              Upgrade All
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-divider>Upgrade Progress</el-divider>
      <div v-for="node in edgeNodes" :key="node.id" v-if="upgradeProgress.has(node.id)" class="upgrade-item">
        <span>{{ node.name }}</span>
        <el-progress :percentage="upgradeProgress.get(node.id) || 0" :stroke-width="8" style="flex:1;margin:0 12px" />
      </div>
      <div v-if="!upgradeProgress.size" class="no-upgrade">
        <el-empty description="No ongoing upgrades" :image-size="80" />
      </div>
    </el-dialog>

    <!-- Sync Strategy Dialog -->
    <el-dialog v-model="showSyncStrategyDialog" title="Data Sync Strategy" width="550px">
      <el-form :model="syncStrategy" label-width="130px">
        <el-form-item label="Sync Frequency">
          <el-input-number v-model="syncStrategy.frequency" :min="1" :max="3600" />
          <el-select v-model="syncStrategy.frequencyUnit" style="width: 100px; margin-left: 8px">
            <el-option label="Seconds" value="seconds" />
            <el-option label="Minutes" value="minutes" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Types">
          <el-select v-model="syncStrategy.dataTypes" multiple placeholder="Select" style="width: 100%">
            <el-option label="Device Status" value="device-status" />
            <el-option label="Sensor Data" value="sensor-data" />
            <el-option label="Events" value="events" />
          </el-select>
        </el-form-item>
        <el-form-item label="Local Storage">
          <el-switch v-model="syncStrategy.localStorage" />
          <span class="form-tip">Store data locally before sync</span>
        </el-form-item>
        <el-form-item label="Offline Cache">
          <el-switch v-model="syncStrategy.offlineCache" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSyncStrategyDialog = false">Cancel</el-button>
        <el-button type="primary" @click="showSyncStrategyDialog = false">Save Strategy</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
* { margin: 0; padding: 0; box-sizing: border-box; }

.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-overlay { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(2px); }
.loading-content { text-align: center; padding: 40px; border-radius: 32px; background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59, 130, 246, 0.3); box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5); animation: fadeInUp 0.6s ease-out; }
.loading-spinner { position: relative; width: 80px; height: 80px; margin: 0 auto 24px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; width: 70%; height: 70%; top: 15%; left: 15%; animation-delay: 0.2s; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; width: 40%; height: 40%; top: 30%; left: 30%; animation-delay: 0.4s; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { margin-bottom: 24px; font-size: 28px; font-weight: 700; color: #e2e8f0; display: flex; justify-content: center; align-items: baseline; gap: 4px; }
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
.loading-progress { width: 280px; height: 4px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden; margin: 0 auto 16px; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a); border-radius: 4px; transition: width 0.3s ease; background-size: 200% auto; animation: shimmer 2s linear infinite; }
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.edge-nodes-page { padding: 24px; min-height: 100vh; background: #f0f2f6; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 16px; }
.page-header h2 { font-size: 24px; font-weight: 600; color: #1a1a2e; margin: 0; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
.stat-card { background: #ffffff; border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform 0.2s, box-shadow 0.2s; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.1); }
.stat-icon { width: 52px; height: 52px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 28px; }
.stat-icon.total { background: #e8f4ff; }
.stat-icon.online { background: #e8f9ef; }
.stat-icon.devices { background: #fff7e6; }
.stat-icon.sync { background: #f4f0ff; }
.stat-value { font-size: 32px; font-weight: 700; color: #1a1a2e; line-height: 1.2; }
.stat-label { font-size: 13px; color: #8c8c8c; margin-top: 4px; }

.topology-card { background: #ffffff; border-radius: 16px; margin-bottom: 24px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.topology-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #fafafa; border-bottom: 1px solid #f0f0f0; flex-wrap: wrap; gap: 12px; font-weight: 500; }
.topology-legend { display: flex; gap: 20px; font-size: 12px; font-weight: normal; }
.legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }
.legend-dot.online { background: #52c41a; box-shadow: 0 0 4px #52c41a; }
.legend-dot.offline { background: #ff4d4f; }
.legend-dot.warning { background: #faad14; animation: warningPulse 1.5s infinite; }
.legend-dot.edge { background: #1890ff; }
@keyframes warningPulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.topology-canvas { height: 680px; width: 100%; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); border-radius: 0; overflow: hidden; }
.vue-flow-wrapper { width: 100%; height: 100%; }

.topology-node { width: 170px; padding: 14px 12px; background: #ffffff; border-radius: 14px; text-align: center; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-left: 4px solid #d9d9d9; }
.topology-node:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.topology-node.online { border-left-color: #52c41a; background: linear-gradient(135deg, #fff 0%, #f6ffed 100%); }
.topology-node.offline { border-left-color: #ff4d4f; background: linear-gradient(135deg, #fff 0%, #fff1f0 100%); opacity: 0.7; }
.topology-node.warning { border-left-color: #faad14; background: linear-gradient(135deg, #fff 0%, #fff7e6 100%); animation: warningBorder 1s infinite; }
@keyframes warningBorder { 0%, 100% { border-left-color: #faad14; } 50% { border-left-color: #ff7a45; } }
.node-icon { font-size: 32px; margin-bottom: 8px; }
.node-name { font-size: 14px; font-weight: 700; color: #1a1a2e; margin-bottom: 4px; }
.node-site { font-size: 11px; color: #8c8c8c; margin-bottom: 8px; }
.node-stats { display: flex; justify-content: center; gap: 12px; font-size: 10px; color: #666; margin-bottom: 8px; }
.node-stats span { background: #f5f5f5; padding: 2px 8px; border-radius: 12px; }
.node-status-badge { font-size: 10px; font-weight: 600; padding: 3px 10px; border-radius: 20px; display: inline-block; }
.node-status-badge.online { color: #52c41a; background: #f6ffed; }
.node-status-badge.offline { color: #ff4d4f; background: #fff1f0; }
.node-status-badge.warning { color: #faad14; background: #fff7e6; }

.action-bar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; align-items: center; }
.search-input { width: 280px; }
.status-filter { width: 130px; }

.table-card { background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.upgrade-progress { width: 100px; }
.version-text { font-size: 13px; color: #666; }
:deep(.el-table th) { background: #fafafa; font-weight: 600; color: #262626; }
:deep(.el-table .cell) { padding: 12px 8px; }
:deep(.el-table__body tr:hover > td) { background: #f5f7fa; }

.detail-dialog :deep(.el-dialog__header) { border-bottom: 1px solid #f0f0f0; padding: 20px 24px; }
.detail-dialog :deep(.el-dialog__body) { padding: 24px; }
.node-detail { max-height: 70vh; overflow-y: auto; }
.monitoring-section { margin-top: 20px; padding: 20px; background: #f8f9fc; border-radius: 12px; }
.monitoring-section h4 { margin: 0 0 16px 0; font-size: 16px; display: flex; align-items: center; gap: 8px; }
.metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }
.metric { background: white; padding: 12px; border-radius: 10px; }
.metric-label { font-size: 12px; color: #666; margin-bottom: 8px; }
.info-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e8e8e8; }
.logs-section { margin-top: 20px; }
.logs-section h4 { margin: 0 0 12px 0; font-size: 16px; display: flex; align-items: center; gap: 8px; }
.logs-list { background: #1e1e2e; color: #e0e0e0; border-radius: 12px; padding: 12px; font-family: monospace; font-size: 12px; max-height: 280px; overflow-y: auto; }
.log-item { padding: 6px 0; border-bottom: 1px solid #2a2a3a; display: flex; gap: 16px; align-items: baseline; flex-wrap: wrap; }
.log-time { color: #888; min-width: 140px; font-size: 11px; }
.log-level { min-width: 70px; font-weight: 600; }
.log-item.info .log-level { color: #4fc3f7; }
.log-item.warn .log-level { color: #ffb74d; }
.log-item.error .log-level { color: #e57373; }
.action-buttons { margin-top: 24px; display: flex; gap: 12px; justify-content: flex-end; }

.config-script { margin-top: 20px; padding: 16px; background: #f8f9fc; border-radius: 12px; }
.did-info { padding: 10px; background: white; border-radius: 8px; font-family: monospace; font-size: 12px; margin-bottom: 12px; word-break: break-all; }

.attestation-tip { margin-top: 16px; padding: 12px 16px; background: #e8f4ff; border-radius: 10px; display: flex; align-items: center; gap: 10px; font-size: 12px; color: #1890ff; }

.upgrade-item { display: flex; align-items: center; padding: 10px 0; gap: 16px; }
.no-upgrade { padding: 30px; text-align: center; }

.form-tip { margin-left: 12px; font-size: 12px; color: #8c8c8c; }

:deep(.vue-flow__edge-path) { stroke-dasharray: 6; }
:deep(.vue-flow__edge-label) { font-size: 10px; fill: #fff; background: #1890ff; padding: 2px 10px; border-radius: 20px; }
:deep(.vue-flow__minimap) { background: rgba(0,0,0,0.3); border-radius: 8px; }
:deep(.vue-flow__controls) { bottom: 16px; right: 16px; }

@media (max-width: 1024px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 768px) { .edge-nodes-page { padding: 16px; } .stats-grid { grid-template-columns: 1fr; } .metrics-grid { grid-template-columns: 1fr; } .topology-canvas { height: 350px; } .topology-node { width: 140px; padding: 10px; } .action-bar { flex-direction: column; align-items: stretch; } .search-input { width: 100%; } .status-filter { width: 100%; } }
</style>