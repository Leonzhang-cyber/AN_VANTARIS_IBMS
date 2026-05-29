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
        <div class="loading-tip">Evidence Link</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Evidence Link Page Content -->
  <div v-else class="evidence-link-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><Link /></el-icon>
          <span>FMS - Evidence Chain</span>
        </div>
        <h1>Evidence Link</h1>
        <p class="subtitle">Trace and link evidence from fault detection to root cause with blockchain-anchored proof</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportChain">
          <el-icon><Download /></el-icon>
          <span>Export Chain</span>
        </button>
        <button class="action-btn" @click="verifyBlockchain">
          <el-icon><Lock /></el-icon>
          <span>Verify on Blockchain</span>
        </button>
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><Document /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalEvidence }}</div>
          <div class="kpi-label">Total Evidence</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon linked">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ linkedEvidence }}%</div>
          <div class="kpi-label">Linked Rate</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon verified">
          <el-icon><CircleCheckFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ verifiedEvidence }}</div>
          <div class="kpi-label">Verified</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon blockchain">
          <el-icon><Connection /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ blockchainHeight }}</div>
          <div class="kpi-label">Blockchain Height</div>
        </div>
      </div>
    </div>

    <!-- Evidence Chain Visualization -->
    <div class="chain-card">
      <div class="card-header">
        <h3>Evidence Chain Visualization</h3>
        <div class="chain-controls">
          <el-radio-group v-model="chainView" size="small">
            <el-radio-button label="timeline">Timeline</el-radio-button>
            <el-radio-button label="graph">Graph View</el-radio-button>
          </el-radio-group>
        </div>
      </div>
      <div class="chain-container">
        <!-- Timeline View -->
        <div v-if="chainView === 'timeline'" class="timeline-view">
          <div v-for="(evidence, index) in evidenceChain" :key="evidence.id" class="timeline-item" :class="evidence.type">
            <div class="timeline-marker">
              <div class="marker-dot"></div>
              <div class="marker-line" v-if="index < evidenceChain.length - 1"></div>
            </div>
            <div class="timeline-card">
              <div class="card-header-row">
                <div class="evidence-type" :class="evidence.type">
                  <el-icon><component :is="getTypeIcon(evidence.type)" /></el-icon>
                  <span>{{ getTypeLabel(evidence.type) }}</span>
                </div>
                <div class="evidence-timestamp">{{ evidence.timestamp }}</div>
              </div>
              <div class="evidence-title">{{ evidence.title }}</div>
              <div class="evidence-description">{{ evidence.description }}</div>
              <div class="evidence-hash">
                <el-icon><Document /></el-icon>
                <span>Hash: {{ evidence.hash }}</span>
                <el-button link type="primary" size="small" @click="copyHash(evidence.hash)">Copy</el-button>
              </div>
              <div class="evidence-links">
                <div v-for="link in evidence.links" :key="link" class="link-tag">
                  <el-icon><Link /></el-icon>
                  <span>{{ link }}</span>
                </div>
              </div>
              <div class="card-footer">
                <button class="view-detail-btn" @click="viewEvidenceDetail(evidence)">View Details</button>
                <button class="verify-btn" @click="verifyEvidence(evidence)">Verify on Chain</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Graph View -->
        <div v-else class="graph-view" ref="graphChartRef"></div>
      </div>
    </div>

    <!-- Evidence Table -->
    <div class="table-card">
      <div class="card-header">
        <h3>All Evidence Records</h3>
        <div class="filter-group">
          <select v-model="filters.type" class="filter-select">
            <option value="all">All Types</option>
            <option value="fault">Fault Detection</option>
            <option value="sensor">Sensor Data</option>
            <option value="log">System Log</option>
            <option value="rca">RCA Result</option>
            <option value="action">Action Taken</option>
          </select>
          <input type="text" v-model="filters.search" placeholder="Search..." class="search-input" />
        </div>
      </div>
      <el-table :data="paginatedEvidence" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="type" label="Type" >
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)" size="small">{{ getTypeLabel(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Title"  show-overflow-tooltip />
        <el-table-column prop="timestamp" label="Timestamp"  sortable />
        <el-table-column prop="hash" label="Hash"  show-overflow-tooltip>
          <template #default="{ row }">
            <span class="hash-text">{{ row.hash.substring(0, 16) }}...</span>
          </template>
        </el-table-column>
        <el-table-column prop="verified" label="Verified" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.verified" color="#67c23a"><CircleCheckFilled /></el-icon>
            <el-icon v-else color="#f56c6c"><CircleCloseFilled /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewEvidenceDetail(row)">Details</el-button>
            <el-button link type="success" size="small" @click="verifyEvidence(row)">Verify</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="filteredEvidence.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Evidence Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" title="Evidence Details" width="650px">
      <div class="detail-content" v-if="selectedEvidence">
        <div class="detail-section">
          <div class="detail-title">Evidence Information</div>
          <div class="detail-grid">
            <div class="detail-item"><span class="label">ID:</span> #{{ selectedEvidence.id }}</div>
            <div class="detail-item"><span class="label">Type:</span> {{ getTypeLabel(selectedEvidence.type) }}</div>
            <div class="detail-item"><span class="label">Title:</span> {{ selectedEvidence.title }}</div>
            <div class="detail-item"><span class="label">Timestamp:</span> {{ selectedEvidence.timestamp }}</div>
          </div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Description</div>
          <div class="detail-text">{{ selectedEvidence.description }}</div>
        </div>
        <div class="detail-section">
          <div class="detail-title">Blockchain Data</div>
          <div class="detail-item"><span class="label">Hash:</span> <code>{{ selectedEvidence.hash }}</code></div>
          <div class="detail-item"><span class="label">Block Height:</span> {{ selectedEvidence.blockHeight || 'Pending' }}</div>
          <div class="detail-item"><span class="label">Anchored At:</span> {{ selectedEvidence.anchoredAt || 'Not anchored' }}</div>
        </div>
        <div class="detail-section" v-if="selectedEvidence.metadata">
          <div class="detail-title">Metadata</div>
          <div class="metadata-json">
            <pre>{{ JSON.stringify(selectedEvidence.metadata, null, 2) }}</pre>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="verifyEvidence(selectedEvidence)" v-if="selectedEvidence && !selectedEvidence.verified">Verify on Chain</el-button>
      </template>
    </el-dialog>

    <!-- Blockchain Verification Dialog -->
    <el-dialog v-model="verifyDialogVisible" title="Blockchain Verification" width="500px">
      <div class="verify-content">
        <div class="verify-icon" :class="verifyResult.status">
          <el-icon v-if="verifyResult.status === 'verified'"><CircleCheckFilled /></el-icon>
          <el-icon v-else-if="verifyResult.status === 'failed'"><CircleCloseFilled /></el-icon>
          <el-icon v-else><Loading /></el-icon>
        </div>
        <div class="verify-title">{{ verifyResult.title }}</div>
        <div class="verify-message">{{ verifyResult.message }}</div>
        <div class="verify-details" v-if="verifyResult.details">
          <div class="detail-row"><span>Block Hash:</span> {{ verifyResult.blockHash }}</div>
          <div class="detail-row"><span>Transaction ID:</span> {{ verifyResult.txId }}</div>
          <div class="detail-row"><span>Timestamp:</span> {{ verifyResult.timestamp }}</div>
          <div class="detail-row"><span>Confirmation:</span> {{ verifyResult.confirmations }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="verifyDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="openBlockExplorer" v-if="verifyResult.status === 'verified'">View on Explorer</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import {
  Refresh, Download, Link, Document, Connection, CircleCheckFilled,
  CircleCloseFilled, Lock, WarningFilled, DataLine, Clock,
  Loading, Warning, Setting, Position, Cpu
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading evidence chain...', 'Syncing blockchain data...', 'Almost ready...']

// Data Models
interface Evidence {
  id: number
  type: 'fault' | 'sensor' | 'log' | 'rca' | 'action'
  title: string
  description: string
  timestamp: string
  hash: string
  verified: boolean
  blockHeight?: number
  anchoredAt?: string
  metadata?: any
  links: string[]
}

// State
const chainView = ref('timeline')
const filters = ref({ type: 'all', search: '' })
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const verifyDialogVisible = ref(false)
const selectedEvidence = ref<Evidence | null>(null)
const verifyResult = ref({
  status: 'pending',
  title: '',
  message: '',
  details: false,
  blockHash: '',
  txId: '',
  timestamp: '',
  confirmations: 0
})

// Chart refs
const graphChartRef = ref<HTMLElement | null>(null)
let graphChart: echarts.ECharts | null = null

// Mock Data - Evidence Chain
const evidenceChain = ref<Evidence[]>([
  { id: 1, type: 'fault', title: 'Fault Detection: Chiller-02 High Pressure Trip', description: 'Chiller-02 tripped due to high pressure alarm at 08:23:15. System automatically logged the event.', timestamp: '2025-05-29 08:23:15', hash: '0x7f8a9c2b3e1d4f5a6b7c8d9e0f1a2b3c4d5e6f7a', verified: true, blockHeight: 1023456, anchoredAt: '2025-05-29 08:25:00', links: ['Sensor-001', 'Chiller-02', 'Event-Log-001'] },
  { id: 2, type: 'sensor', title: 'Sensor Data: Cooling Tower Fan Status', description: 'Cooling tower fan CT-01 reported NOT RUNNING status. Vibration sensor detected abnormal reading.', timestamp: '2025-05-29 08:21:30', hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c', verified: true, blockHeight: 1023454, anchoredAt: '2025-05-29 08:22:00', links: ['CT-01', 'Vibration-Sensor', 'Chiller-02'] },
  { id: 3, type: 'sensor', title: 'Sensor Data: Condenser Water Flow', description: 'Condenser water flow meter shows 45% below normal operating range (220 GPM vs 400 GPM).', timestamp: '2025-05-29 08:22:45', hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d', verified: true, blockHeight: 1023455, anchoredAt: '2025-05-29 08:23:30', links: ['Flow-Meter-02', 'Chiller-02'] },
  { id: 4, type: 'log', title: 'System Log: Chiller Alarm History', description: 'Chiller-02 high pressure alarm history shows 3 events in past 24 hours, trending upward.', timestamp: '2025-05-29 08:24:00', hash: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e', verified: true, blockHeight: 1023457, anchoredAt: '2025-05-29 08:24:30', links: ['Chiller-02', 'Event-History'] },
  { id: 5, type: 'rca', title: 'RCA Analysis: Cooling Tower Fan Bearing Failure', description: 'AI-driven root cause analysis identified cooling tower fan bearing failure as primary cause.', timestamp: '2025-05-29 08:30:00', hash: '0x5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f', verified: true, blockHeight: 1023460, anchoredAt: '2025-05-29 08:31:00', links: ['RCA-Engine', 'AI-Analysis'] },
  { id: 6, type: 'action', title: 'Action Taken: Replaced Fan Bearings', description: 'Maintenance team replaced cooling tower fan bearings. Vibration returned to normal levels.', timestamp: '2025-05-29 11:30:00', hash: '0x6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a', verified: true, blockHeight: 1023480, anchoredAt: '2025-05-29 11:35:00', links: ['Work-Order-1001', 'Maintenance-Log'] },
  { id: 7, type: 'sensor', title: 'Post-Repair Verification', description: 'Vibration sensor shows normal levels (0.08 mm/s). Chiller operating within parameters.', timestamp: '2025-05-29 11:45:00', hash: '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b', verified: true, blockHeight: 1023485, anchoredAt: '2025-05-29 11:50:00', links: ['Vibration-Sensor', 'Chiller-02'] }
])

const allEvidence = ref<Evidence[]>([...evidenceChain.value])

// Computed
const totalEvidence = computed(() => allEvidence.value.length)
const linkedEvidence = computed(() => Math.round((evidenceChain.value.length / allEvidence.value.length) * 100))
const verifiedEvidence = computed(() => allEvidence.value.filter(e => e.verified).length)
const blockchainHeight = computed(() => 1023485)

const filteredEvidence = computed(() => {
  let result = [...allEvidence.value]
  if (filters.value.type !== 'all') {
    result = result.filter(e => e.type === filters.value.type)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(e =>
        e.title.toLowerCase().includes(search) ||
        e.description.toLowerCase().includes(search) ||
        e.hash.toLowerCase().includes(search)
    )
  }
  return result
})

const paginatedEvidence = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvidence.value.slice(start, end)
})

// Helper Functions
const getTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    fault: 'Fault Detection',
    sensor: 'Sensor Data',
    log: 'System Log',
    rca: 'RCA Result',
    action: 'Action Taken'
  }
  return map[type] || type
}

const getTypeIcon = (type: string) => {
  const map: Record<string, any> = {
    fault: WarningFilled,
    sensor: DataLine,
    log: Document,
    rca: Position,
    action: Setting
  }
  return map[type] || Link
}

const getTypeTagType = (type: string) => {
  const map: Record<string, string> = {
    fault: 'danger',
    sensor: 'primary',
    log: 'info',
    rca: 'success',
    action: 'warning'
  }
  return map[type] || 'info'
}

// Copy hash
const copyHash = (hash: string) => {
  navigator.clipboard.writeText(hash)
  ElMessage.success('Hash copied to clipboard')
}

// View evidence detail
const viewEvidenceDetail = (evidence: Evidence) => {
  selectedEvidence.value = evidence
  detailDialogVisible.value = true
}

// Verify evidence on blockchain
const verifyEvidence = async (evidence: Evidence) => {
  verifyDialogVisible.value = true
  verifyResult.value = { status: 'pending', title: 'Verifying...', message: 'Connecting to blockchain network...', details: false, blockHash: '', txId: '', timestamp: '', confirmations: 0 }

  await new Promise(resolve => setTimeout(resolve, 1500))

  if (evidence.verified) {
    verifyResult.value = {
      status: 'verified',
      title: 'Verification Successful',
      message: `Evidence #${evidence.id} is anchored on blockchain and verified.`,
      details: true,
      blockHash: `0x${Array(64).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('')}`,
      txId: `0x${Array(64).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join('')}`,
      timestamp: evidence.anchoredAt || new Date().toISOString(),
      confirmations: Math.floor(Math.random() * 100) + 10
    }
  } else {
    verifyResult.value = {
      status: 'failed',
      title: 'Verification Failed',
      message: `Evidence #${evidence.id} not found on blockchain. Please check the evidence hash.`,
      details: false,
      blockHash: '',
      txId: '',
      timestamp: '',
      confirmations: 0
    }
  }
}

// Export chain
const exportChain = () => {
  const data = JSON.stringify(evidenceChain.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `evidence_chain_${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Evidence chain exported')
}

// Verify entire blockchain
const verifyBlockchain = () => {
  ElMessage.info('Connecting to blockchain network...')
  setTimeout(() => {
    ElMessage.success('Blockchain verification complete: All evidence verified')
  }, 2000)
}

// Open block explorer
const openBlockExplorer = () => {
  ElMessage.info('Opening block explorer...')
}

// Initialize graph chart
const initGraphChart = () => {
  if (!graphChartRef.value) return
  if (graphChart) graphChart.dispose()

  graphChart = echarts.init(graphChartRef.value)

  const nodes = [
    { name: 'Fault: Chiller Trip', category: 0, symbolSize: 40, itemStyle: { color: '#f56c6c' } },
    { name: 'Sensor: Fan Status', category: 1, symbolSize: 30, itemStyle: { color: '#409eff' } },
    { name: 'Sensor: Water Flow', category: 1, symbolSize: 30, itemStyle: { color: '#409eff' } },
    { name: 'Log: Alarm History', category: 2, symbolSize: 28, itemStyle: { color: '#e6a23c' } },
    { name: 'RCA: Bearing Failure', category: 3, symbolSize: 35, itemStyle: { color: '#67c23a' } },
    { name: 'Action: Replacement', category: 4, symbolSize: 32, itemStyle: { color: '#8b5cf6' } }
  ]

  const links = [
    { source: 'Sensor: Fan Status', target: 'Fault: Chiller Trip' },
    { source: 'Sensor: Water Flow', target: 'Fault: Chiller Trip' },
    { source: 'Log: Alarm History', target: 'Fault: Chiller Trip' },
    { source: 'Fault: Chiller Trip', target: 'RCA: Bearing Failure' },
    { source: 'RCA: Bearing Failure', target: 'Action: Replacement' }
  ]

  const categories = [
    { name: 'Fault', itemStyle: { color: '#f56c6c' } },
    { name: 'Sensor', itemStyle: { color: '#409eff' } },
    { name: 'Log', itemStyle: { color: '#e6a23c' } },
    { name: 'RCA', itemStyle: { color: '#67c23a' } },
    { name: 'Action', itemStyle: { color: '#8b5cf6' } }
  ]

  graphChart.setOption({
    title: { show: false },
    tooltip: { formatter: (params: any) => params.name },
    series: [{
      type: 'graph', layout: 'force', data: nodes, links: links, categories: categories,
      roam: true, draggable: true, force: { repulsion: 500, edgeLength: 150 },
      label: { show: true, position: 'right', fontSize: 11 },
      edgeSymbol: ['none', 'arrow'], edgeSymbolSize: [0, 8],
      lineStyle: { color: '#94a3b8', width: 2, curveness: 0.3 }
    }]
  })
}

// Actions
const refreshData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// Resize handler
const handleResize = () => {
  graphChart?.resize()
}

// Lifecycle
onMounted(() => {
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
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        initGraphChart()
      })
      window.addEventListener('resize', handleResize)
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  graphChart?.dispose()
})
</script>

<style scoped>
/* Loading Screen */
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
.evidence-link-page {
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
.kpi-icon.total { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.linked { background: #fef3c7; color: #d97706; }
.kpi-icon.verified { background: #d1fae5; color: #059669; }
.kpi-icon.blockchain { background: #f3e8ff; color: #8b5cf6; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }

/* Chain Card */
.chain-card {
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
.chain-container {
  min-height: 500px;
}

/* Timeline View */
.timeline-view {
  position: relative;
  padding-left: 30px;
}
.timeline-item {
  position: relative;
  margin-bottom: 24px;
}
.timeline-marker {
  position: absolute;
  left: -30px;
  top: 0;
  width: 30px;
  height: 100%;
}
.marker-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: #3b82f6;
  border: 2px solid white;
  box-shadow: 0 0 0 2px #3b82f6;
}
.timeline-item.fault .marker-dot { background: #f56c6c; box-shadow: 0 0 0 2px #f56c6c; }
.timeline-item.sensor .marker-dot { background: #409eff; box-shadow: 0 0 0 2px #409eff; }
.timeline-item.log .marker-dot { background: #e6a23c; box-shadow: 0 0 0 2px #e6a23c; }
.timeline-item.rca .marker-dot { background: #67c23a; box-shadow: 0 0 0 2px #67c23a; }
.timeline-item.action .marker-dot { background: #8b5cf6; box-shadow: 0 0 0 2px #8b5cf6; }
.marker-line {
  position: absolute;
  top: 14px;
  left: 6px;
  width: 2px;
  height: calc(100% + 10px);
  background: #e2e8f0;
}
.timeline-card {
  background: #f8fafc;
  border-radius: 14px;
  padding: 16px;
  margin-left: 16px;
  border-left: 3px solid;
}
.timeline-item.fault .timeline-card { border-left-color: #f56c6c; }
.timeline-item.sensor .timeline-card { border-left-color: #409eff; }
.timeline-item.log .timeline-card { border-left-color: #e6a23c; }
.timeline-item.rca .timeline-card { border-left-color: #67c23a; }
.timeline-item.action .timeline-card { border-left-color: #8b5cf6; }
.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 8px;
}
.evidence-type {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}
.evidence-type.fault { background: #fee2e2; color: #dc2626; }
.evidence-type.sensor { background: #dbeafe; color: #1d4ed8; }
.evidence-type.log { background: #fef3c7; color: #d97706; }
.evidence-type.rca { background: #d1fae5; color: #059669; }
.evidence-type.action { background: #ede9fe; color: #6d28d9; }
.evidence-timestamp { font-size: 11px; color: #94a3b8; }
.evidence-title { font-weight: 600; color: #1a1a2e; margin-bottom: 8px; }
.evidence-description { font-size: 13px; color: #475569; margin-bottom: 10px; }
.evidence-hash {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  color: #64748b;
  background: #f1f5f9;
  padding: 6px 10px;
  border-radius: 8px;
  margin-bottom: 10px;
}
.evidence-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.link-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  padding: 2px 8px;
  background: #e8f4ff;
  color: #3b82f6;
  border-radius: 12px;
}
.card-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.view-detail-btn, .verify-btn {
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.view-detail-btn {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
}
.view-detail-btn:hover { background: #f1f5f9; }
.verify-btn {
  background: #dbeafe;
  border: none;
  color: #1d4ed8;
}
.verify-btn:hover { background: #bfdbfe; }

/* Graph View */
.graph-view {
  height: 500px;
  width: 100%;
  background: #f8fafc;
  border-radius: 12px;
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
  flex-wrap: wrap;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
}
.search-input { width: 200px; }
.hash-text { font-family: monospace; }
.pagination-wrapper {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 16px;
}

/* Dialog Styles */
.detail-content { padding: 8px 0; }
.detail-section {
  margin-bottom: 24px;
}
.detail-title {
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
  font-size: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.detail-item {
  font-size: 13px;
}
.detail-item .label {
  color: #64748b;
  margin-right: 8px;
}
.detail-text {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
}
.metadata-json pre {
  background: #f1f5f9;
  padding: 12px;
  border-radius: 8px;
  font-size: 11px;
  overflow-x: auto;
}

/* Verify Dialog */
.verify-content {
  text-align: center;
  padding: 20px;
}
.verify-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  border-radius: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}
.verify-icon.verified { background: #d1fae5; color: #059669; }
.verify-icon.failed { background: #fee2e2; color: #dc2626; }
.verify-icon.pending { background: #e8f4ff; color: #3b82f6; animation: spin 1s linear infinite; }
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.verify-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}
.verify-message {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 20px;
}
.verify-details {
  text-align: left;
  background: #f8fafc;
  padding: 12px;
  border-radius: 12px;
}
.verify-details .detail-row {
  font-size: 12px;
  margin-bottom: 6px;
}
.verify-details .detail-row span {
  color: #64748b;
  width: 100px;
  display: inline-block;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
</style>