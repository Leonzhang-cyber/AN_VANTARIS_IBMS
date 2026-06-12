<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Search, Refresh, Document, Download, Printer,
  Share, Star, Clock, Warning, CircleCheck,
  TrendCharts, DataLine, Calendar, Setting,
  Plus, Upload, Filter, ArrowUp, ArrowDown,
  View, User, Trophy, Medal, Edit, Delete,
  CopyDocument, Lock, Unlock, Key,
  Link, DataAnalysis
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading hash database...',
  'Verifying evidence integrity...',
  'Preparing blockchain records...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStatus = ref('all')
const selectedType = ref('all')
const hashDetailsVisible = ref(false)
const verifyDialogVisible = ref(false)
const chainVisible = ref(false)
const chartRef = ref(null)

let hashChart: echarts.ECharts | null = null

// Status filters
const statusOptions = [
  { value: 'all', label: 'All' },
  { value: 'verified', label: 'Verified', color: '#67C23A' },
  { value: 'pending', label: 'Pending', color: '#E6A23C' },
  { value: 'failed', label: 'Failed', color: '#F56C6C' },
  { value: 'expired', label: 'Expired', color: '#909399' }
]

// Type filters
const typeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'report', label: 'Report' },
  { value: 'dashboard', label: 'Dashboard' },
  { value: 'data', label: 'Data Export' },
  { value: 'attachment', label: 'Attachment' }
]

// Evidence hash data
const evidenceItems = ref([
  {
    id: 'HASH001', name: 'Executive Dashboard Q1', type: 'dashboard',
    hash: '0x8f4e2a1b3c5d7e9f0a1b2c3d4e5f6a7b8c9d0e1f',
    blockchainTx: '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7',
    createdBy: 'john.smith@system.com', createdAt: '2024-01-15 10:30:00',
    status: 'verified', size: '2.4 MB', pages: 12,
    blockHeight: 12548392, timestamp: '2024-01-15 10:35:22',
    verifications: 156, lastVerified: '2024-01-15 10:35:22'
  },
  {
    id: 'HASH002', name: 'Energy Consumption Report', type: 'report',
    hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c',
    blockchainTx: '0x8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8',
    createdBy: 'sarah.j@system.com', createdAt: '2024-01-14 14:20:00',
    status: 'verified', size: '3.1 MB', pages: 18,
    blockHeight: 12547832, timestamp: '2024-01-14 14:25:15',
    verifications: 89, lastVerified: '2024-01-14 14:25:15'
  },
  {
    id: 'HASH003', name: 'Financial Summary January', type: 'report',
    hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d',
    blockchainTx: '0x9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9',
    createdBy: 'mike.chen@system.com', createdAt: '2024-01-13 11:15:00',
    status: 'pending', size: '4.2 MB', pages: 24,
    blockHeight: null, timestamp: null,
    verifications: 0, lastVerified: null
  },
  {
    id: 'HASH004', name: 'Security Audit Log', type: 'data',
    hash: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e',
    blockchainTx: '0x0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0',
    createdBy: 'david.lee@system.com', createdAt: '2024-01-12 10:45:00',
    status: 'failed', size: '5.6 MB', pages: 45,
    blockHeight: null, timestamp: null,
    verifications: 0, lastVerified: null
  },
  {
    id: 'HASH005', name: 'Maintenance Dashboard', type: 'dashboard',
    hash: '0x5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f',
    blockchainTx: '0x1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1',
    createdBy: 'robert.w@system.com', createdAt: '2024-01-11 09:00:00',
    status: 'verified', size: '2.8 MB', pages: 10,
    blockHeight: 12546218, timestamp: '2024-01-11 09:08:42',
    verifications: 234, lastVerified: '2024-01-11 09:08:42'
  },
  {
    id: 'HASH006', name: 'Sustainability Report', type: 'report',
    hash: '0x6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a',
    blockchainTx: '0x2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
    createdBy: 'emily.w@system.com', createdAt: '2024-01-10 13:30:00',
    status: 'verified', size: '3.5 MB', pages: 20,
    blockHeight: 12545123, timestamp: '2024-01-10 13:38:05',
    verifications: 67, lastVerified: '2024-01-10 13:38:05'
  },
  {
    id: 'HASH007', name: 'Sales Performance Data', type: 'data',
    hash: '0x7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b',
    blockchainTx: '0x3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    createdBy: 'lisa.tan@system.com', createdAt: '2024-01-09 15:00:00',
    status: 'expired', size: '1.9 MB', pages: 8,
    blockHeight: 12544289, timestamp: '2024-01-09 15:05:30',
    verifications: 345, lastVerified: '2024-01-09 15:05:30'
  },
  {
    id: 'HASH008', name: 'Inventory Analysis', type: 'report',
    hash: '0x8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c',
    blockchainTx: '0x4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    createdBy: 'james.w@system.com', createdAt: '2024-01-08 11:00:00',
    status: 'pending', size: '2.2 MB', pages: 14,
    blockHeight: null, timestamp: null,
    verifications: 0, lastVerified: null
  }
])

// Hash statistics
const hashStats = reactive({
  total: 0,
  verified: 0,
  pending: 0,
  failed: 0,
  expired: 0,
  totalVerifications: 0,
  avgVerifications: 0,
  blockchainHeight: 12548392
})

// Verify form
const verifyForm = reactive({
  hash: '',
  file: null
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: evidenceItems.value.length
})

// Filtered items
const filteredItems = computed(() => {
  let filtered = evidenceItems.value
  if (searchKeyword.value) {
    filtered = filtered.filter(i =>
        i.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        i.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        i.hash.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(i => i.status === selectedStatus.value)
  }
  if (selectedType.value !== 'all') {
    filtered = filtered.filter(i => i.type === selectedType.value)
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

  hashChart = echarts.init(chartRef.value)
  hashChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Verifications', 'Block Height'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: evidenceItems.value.map(i => i.name.substring(0, 15)), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: [
      { type: 'value', name: 'Verifications' },
      { type: 'value', name: 'Block Height' }
    ],
    series: [
      { name: 'Verifications', type: 'bar', data: evidenceItems.value.map(i => i.verifications), itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Block Height', type: 'line', data: evidenceItems.value.map(i => i.blockHeight || 0), smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const updateStats = () => {
  hashStats.total = evidenceItems.value.length
  hashStats.verified = evidenceItems.value.filter(i => i.status === 'verified').length
  hashStats.pending = evidenceItems.value.filter(i => i.status === 'pending').length
  hashStats.failed = evidenceItems.value.filter(i => i.status === 'failed').length
  hashStats.expired = evidenceItems.value.filter(i => i.status === 'expired').length
  hashStats.totalVerifications = evidenceItems.value.reduce((sum, i) => sum + i.verifications, 0)
  hashStats.avgVerifications = Math.round(hashStats.totalVerifications / hashStats.verified)
}

const handleResize = () => {
  hashChart?.resize()
}

// ==================== Hash Functions ====================
const refreshHashes = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Hash records refreshed successfully')
}

const viewHashDetails = (item: any) => {
  selectedItem.value = item
  hashDetailsVisible.value = true
}

const openVerifyDialog = () => {
  verifyForm.hash = ''
  verifyForm.file = null
  verifyDialogVisible.value = true
}

const verifyHash = async () => {
  if (!verifyForm.hash && !verifyForm.file) {
    ElMessage.warning('Please enter a hash or upload a file')
    return
  }

  await new Promise(resolve => setTimeout(resolve, 1500))

  // Simulate verification
  const isVerified = Math.random() > 0.2
  if (isVerified) {
    ElMessage.success('Hash verified successfully! Evidence is authentic.')
  } else {
    ElMessage.error('Hash verification failed. Evidence may be tampered.')
  }

  verifyDialogVisible.value = false
}

const viewBlockchainChain = () => {
  chainVisible.value = true
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'verified': return '#67C23A'
    case 'pending': return '#E6A23C'
    case 'failed': return '#F56C6C'
    case 'expired': return '#909399'
    default: return '#909399'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'verified': return Warning
    case 'pending': return Clock
    case 'failed': return Warning
    case 'expired': return Warning
    default: return QuestionFilled
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'verified': return 'Pending'
    case 'pending': return 'Pending'
    case 'failed': return 'Failed'
    case 'expired': return 'Expired'
    default: return 'Unknown'
  }
}

const formatHash = (hash: string) => {
  if (!hash) return 'N/A'
  return hash.substring(0, 16) + '...' + hash.substring(hash.length - 8)
}

const formatTxHash = (tx: string) => {
  if (!tx) return 'N/A'
  return tx.substring(0, 16) + '...' + tx.substring(tx.length - 8)
}

const selectedItem = ref<any>(null)
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
          <span class="loading-title">Loading Report Evidence Hash</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Report Governance - Evidence Hash</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="evidence-hash-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Report Evidence Hash</h1>
        <p class="page-subtitle">Blockchain-anchored evidence for report integrity verification</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openVerifyDialog">
          <el-icon><ArrowDown /></el-icon>
          Verify Hash
        </el-button>
        <el-button size="large" @click="viewBlockchainChain">
          <el-icon><Link /></el-icon>
          Blockchain Explorer
        </el-button>
        <el-button size="large" @click="refreshHashes" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ hashStats.total }}</div>
          <div class="stat-label">Total Records</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ hashStats.verified }} Verified</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon verified-icon">
          <el-icon><Filter /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ hashStats.totalVerifications.toLocaleString() }}</div>
          <div class="stat-label">Total Verifications</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ hashStats.avgVerifications }} avg per record</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon blockchain-icon">
          <el-icon><Link /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ hashStats.blockchainHeight.toLocaleString() }}</div>
          <div class="stat-label">Block Height</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">Latest block</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon pending-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ hashStats.pending }}</div>
          <div class="stat-label">Pending</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">{{ hashStats.failed }} Failed</span>
        </div>
      </div>
    </div>

    <!-- Stats Breakdown Row -->
    <div class="stats-breakdown">
      <div class="breakdown-item">
        <span class="breakdown-label">Verified</span>
        <span class="breakdown-value">{{ hashStats.verified }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (hashStats.verified / hashStats.total) * 100 + '%', background: '#67C23A' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Pending</span>
        <span class="breakdown-value">{{ hashStats.pending }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (hashStats.pending / hashStats.total) * 100 + '%', background: '#E6A23C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Failed</span>
        <span class="breakdown-value">{{ hashStats.failed }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (hashStats.failed / hashStats.total) * 100 + '%', background: '#F56C6C' }"></div>
        </div>
      </div>
      <div class="breakdown-item">
        <span class="breakdown-label">Expired</span>
        <span class="breakdown-value">{{ hashStats.expired }}</span>
        <div class="breakdown-bar">
          <div class="bar-fill" :style="{ width: (hashStats.expired / hashStats.total) * 100 + '%', background: '#909399' }"></div>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Verification Statistics</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="verification-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search by name, ID, or hash..."
              :prefix-icon="Search"
              clearable
              style="width: 260px"
          />
        </div>
        <div class="status-filters">
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
      <div class="filters-right">
        <el-select v-model="selectedType" placeholder="Type" clearable style="width: 140px">
          <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
      </div>
    </div>

    <!-- Evidence Hash Grid - Card Style -->
    <div class="evidence-grid">
      <div
          v-for="item in filteredItems"
          :key="item.id"
          class="evidence-card"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="card-type">
            <span class="type-icon">{{ item.type === 'dashboard' ? '📊' : item.type === 'report' ? '📄' : item.type === 'data' ? '🗃️' : '📎' }}</span>
          </div>
          <div class="card-status">
            <el-tag :type="item.status === 'verified' ? 'success' : item.status === 'pending' ? 'warning' : item.status === 'failed' ? 'danger' : 'info'" size="small">
              <el-icon><component :is="getStatusIcon(item.status)" /></el-icon>
              {{ getStatusText(item.status) }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="card-title">{{ item.name }}</h4>

          <!-- Hash Info -->
          <div class="hash-info">
            <div class="info-row">
              <span class="info-label">Hash:</span>
              <span class="info-value hash-value" :title="item.hash">
                <el-icon><Trophy /></el-icon>
                {{ formatHash(item.hash) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">TX ID:</span>
              <span class="info-value tx-value" :title="item.blockchainTx">
                <el-icon><Link /></el-icon>
                {{ formatTxHash(item.blockchainTx) }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">Block:</span>
              <span class="info-value">{{ item.blockHeight || 'Pending' }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Size:</span>
              <span class="info-value">{{ item.size }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Pages:</span>
              <span class="info-value">{{ item.pages }}</span>
            </div>
          </div>

          <!-- Verification Stats -->
          <div class="verification-stats">
            <div class="stat-item">
              <span class="stat-label">Verifications:</span>
              <span class="stat-value">{{ item.verifications.toLocaleString() }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Created:</span>
              <span class="stat-value">{{ item.createdAt }}</span>
            </div>
            <div v-if="item.lastVerified" class="stat-item">
              <span class="stat-label">Last Verified:</span>
              <span class="stat-value">{{ item.lastVerified }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="footer-author">
            <el-icon><User /></el-icon>
            <span>{{ item.createdBy?.split('@')[0] }}</span>
          </div>
          <div class="card-actions">
            <el-button size="small" @click="viewHashDetails(item)">
              Details
            </el-button>
            <el-button size="small" type="primary" @click="openVerifyDialog">
              Verify
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredItems.length === 0" class="empty-state">
      <el-empty description="No evidence records found">
        <el-button type="primary">Generate Hash</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredItems.length > 0" class="pagination-wrapper">
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

    <!-- Hash Details Dialog -->
    <el-dialog v-model="hashDetailsVisible" :title="selectedItem?.name" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Record ID">{{ selectedItem?.id }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedItem?.type?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="selectedItem?.status === 'verified' ? 'success' : selectedItem?.status === 'pending' ? 'warning' : 'danger'" size="small">
            {{ getStatusText(selectedItem?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedItem?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedItem?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="File Size">{{ selectedItem?.size }}</el-descriptions-item>
        <el-descriptions-item label="Pages">{{ selectedItem?.pages }}</el-descriptions-item>
        <el-descriptions-item label="Hash" :span="2">
          <div class="full-hash">
            <code>{{ selectedItem?.hash }}</code>
            <el-button size="small" text @click="copyToClipboard(selectedItem?.hash)">
              Copy
            </el-button>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Transaction ID" :span="2">
          <div class="full-hash">
            <code>{{ selectedItem?.blockchainTx }}</code>
            <el-button size="small" text @click="copyToClipboard(selectedItem?.blockchainTx)">
              Copy
            </el-button>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="Block Height">{{ selectedItem?.blockHeight || 'Pending' }}</el-descriptions-item>
        <el-descriptions-item label="Timestamp">{{ selectedItem?.timestamp || 'Pending' }}</el-descriptions-item>
        <el-descriptions-item label="Verifications">{{ selectedItem?.verifications.toLocaleString() }}</el-descriptions-item>
        <el-descriptions-item label="Last Verified">{{ selectedItem?.lastVerified || 'Never' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="hashDetailsVisible = false">Close</el-button>
        <el-button type="primary" @click="openVerifyDialog">Verify Again</el-button>
      </template>
    </el-dialog>

    <!-- Verify Hash Dialog -->
    <el-dialog v-model="verifyDialogVisible" title="Verify Evidence Hash" width="500px">
      <div class="verify-info">
        <el-alert
            title="Verify evidence integrity using blockchain-anchored hash"
            type="info"
            show-icon
            :closable="false"
        />
      </div>

      <el-form :model="verifyForm" label-width="100px" style="margin-top: 20px">
        <el-form-item label="Enter Hash">
          <el-input
              v-model="verifyForm.hash"
              type="textarea"
              rows="2"
              placeholder="0x..."
          />
        </el-form-item>
        <el-form-item label="Or Upload File">
          <el-upload
              drag
              action="#"
              :auto-upload="false"
              :show-file-list="true"
              :on-change="(file) => verifyForm.file = file"
          >
            <el-icon class="upload-icon"><Upload /></el-icon>
            <div class="upload-text">Click or drag file to upload</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="verifyDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="verifyHash">Verify Hash</el-button>
      </template>
    </el-dialog>

    <!-- Blockchain Explorer Dialog -->
    <el-dialog v-model="chainVisible" title="Blockchain Explorer" width="800px">
      <div class="chain-info">
        <div class="chain-stats">
          <div class="chain-stat">
            <span class="stat-label">Current Block Height</span>
            <span class="stat-value">{{ hashStats.blockchainHeight.toLocaleString() }}</span>
          </div>
          <div class="chain-stat">
            <span class="stat-label">Network</span>
            <span class="stat-value">Ethereum Mainnet</span>
          </div>
          <div class="chain-stat">
            <span class="stat-label">Total Transactions</span>
            <span class="stat-value">{{ (hashStats.totalVerifications * 1.2).toLocaleString() }}</span>
          </div>
        </div>

        <el-divider />

        <div class="recent-blocks">
          <h4>Recent Blocks</h4>
          <el-table :data="evidenceItems.slice(0, 5)" stripe>
            <el-table-column prop="blockHeight" label="Block Height" width="120" />
            <el-table-column prop="name" label="Report" min-width="200" />
            <el-table-column prop="timestamp" label="Timestamp" width="180" />
            <el-table-column label="Hash" width="200">
              <template #default="{ row }">
                <span :title="row.hash">{{ formatHash(row.hash) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Action" width="100">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="viewHashDetails(row)">
                  View
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="chainVisible = false">Close</el-button>
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
.evidence-hash-container {
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
  margin-bottom: 20px;
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

.verified-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.blockchain-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.pending-icon {
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
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-neutral {
  font-size: 11px;
  color: #909399;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

/* Stats Breakdown */
.stats-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.breakdown-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.breakdown-label {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-bottom: 8px;
}

.breakdown-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  display: block;
  margin-bottom: 12px;
}

.breakdown-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
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

.verification-chart {
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

.status-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-chip {
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

.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

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

.filters-right {
  display: flex;
  gap: 12px;
}

/* Evidence Grid */
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.evidence-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.evidence-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.card-type {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.type-icon {
  font-size: 24px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
  line-height: 1.4;
}

.hash-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: #909399;
}

.info-value {
  color: #1e293b;
  font-weight: 500;
}

.hash-value, .tx-value {
  font-family: monospace;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.verification-stats {
  background: #f0f9ff;
  border-radius: 12px;
  padding: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-item .stat-label {
  color: #909399;
}

.stat-item .stat-value {
  color: #409eff;
  font-weight: 500;
}

/* Card Footer */
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.footer-author {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.card-actions {
  display: flex;
  gap: 8px;
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
.full-hash {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.full-hash code {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 4px;
  word-break: break-all;
  flex: 1;
}

.verify-info {
  margin-bottom: 15px;
}

.upload-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 12px;
}

.upload-text {
  font-size: 14px;
  color: #909399;
}

.chain-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.chain-stat {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
}

.chain-stat .stat-label {
  font-size: 12px;
  color: #909399;
  display: block;
  margin-bottom: 8px;
}

.chain-stat .stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.recent-blocks h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: #1e293b;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }

  .evidence-grid {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  }

  .chain-stats {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .evidence-hash-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stats-breakdown {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
  }

  .status-filters {
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

  .evidence-grid {
    grid-template-columns: 1fr;
  }

  .full-hash {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>