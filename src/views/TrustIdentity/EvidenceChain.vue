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
        <div class="loading-tip">Trust & Identity - Evidence Chain</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="evidence-chain-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Evidence Chain</h1>
        <p>Cryptographically linked evidence chain for immutable audit trail and verification</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddEvidenceDialog">
          <el-icon><Plus /></el-icon>
          Add Evidence
        </el-button>
        <el-button @click="verifyChain">
          <el-icon><Search /></el-icon>
          Verify Chain
        </el-button>
        <el-button @click="exportChain">
          <el-icon><Download /></el-icon>
          Export Chain
        </el-button>
      </div>
    </div>

    <!-- Chain Overview Stats -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Link /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEvidence }}</div>
            <div class="stat-label">Total Evidence</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.verifiedCount }}</div>
            <div class="stat-label">Verified</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.chainIntegrity }}%</div>
            <div class="stat-label">Chain Integrity</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.anchoredCount }}</div>
            <div class="stat-label">Blockchain Anchored</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Chain Visualization -->
    <div class="chain-visualization-card">
      <div class="card-header">
        <h3>Evidence Chain Visualization</h3>
        <div class="chain-legend">
          <span><span class="legend-dot verified"></span> Verified</span>
          <span><span class="legend-dot pending"></span> Pending</span>
          <span><span class="legend-dot anchored"></span> Blockchain Anchored</span>
          <span><span class="legend-dot broken"></span> Broken Link</span>
        </div>
      </div>
      <div class="chain-container" ref="chainContainerRef">
        <canvas ref="chainCanvasRef" class="chain-canvas"></canvas>
        <div v-if="selectedEvidence" class="chain-tooltip" :style="tooltipStyle">
          <div class="tooltip-header">
            <strong>{{ selectedEvidence.title }}</strong>
            <el-button link @click="selectedEvidence = null">✕</el-button>
          </div>
          <div>ID: {{ selectedEvidence.id }}</div>
          <div>Hash: <code>{{ selectedEvidence.hash.substring(0, 16) }}...</code></div>
          <div>Status: {{ selectedEvidence.status }}</div>
          <el-button size="small" type="primary" @click="viewEvidenceDetail(selectedEvidence)">View Details</el-button>
        </div>
      </div>
    </div>

    <!-- Evidence Chain Table -->
    <div class="evidence-table-wrapper">
      <div class="table-header">
        <h3>Evidence Chain Records</h3>
        <div class="table-filters">
          <el-input
              v-model="filters.search"
              placeholder="Search by ID, title, or hash..."
              clearable
              style="width: 200px"
              :prefix-icon="Search"
          />
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="All" value="" />
            <el-option label="Verified" value="verified" />
            <el-option label="Pending" value="pending" />
            <el-option label="Tampered" value="tampered" />
          </el-select>
        </div>
      </div>
      <el-table :data="filteredEvidence" stripe v-loading="tableLoading" style="width: 100%" @row-click="viewEvidenceDetail">
        <el-table-column prop="index" label="#" width="60" />
        <el-table-column prop="id" label="Evidence ID" width="120" />
        <el-table-column prop="title" label="Title" min-width="180" show-overflow-tooltip />
        <el-table-column prop="hash" label="Hash" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="hash-code">{{ row.hash.substring(0, 16) }}...</code>
            <el-button link size="small" @click.stop="copyHash(row.hash)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="previousHash" label="Previous Hash" width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <code v-if="row.previousHash" class="hash-code">{{ row.previousHash.substring(0, 12) }}...</code>
            <span v-else class="root-text">Genesis</span>
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="anchored" label="Blockchain" width="100">
          <template #default="{ row }">
            <el-icon v-if="row.anchored" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-else color="#909399"><Clock /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewEvidenceDetail(row)">
              Details
            </el-button>
            <el-button v-if="row.status === 'verified'" link type="success" size="small" @click.stop="verifyEvidence(row)">
              Verify
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Add Evidence Dialog -->
    <el-dialog v-model="addDialog.visible" title="Add Evidence to Chain" width="600px">
      <el-steps :active="addStep" finish-status="success" align-center style="margin-bottom: 24px">
        <el-step title="Evidence Details" />
        <el-step title="Generate Hash" />
        <el-step title="Confirm" />
      </el-steps>

      <div class="add-content">
        <!-- Step 1: Evidence Details -->
        <div v-show="addStep === 0" class="step-panel">
          <el-form :model="evidenceForm" label-width="120px">
            <el-form-item label="Evidence Title" required>
              <el-input v-model="evidenceForm.title" placeholder="Enter descriptive title" />
            </el-form-item>
            <el-form-item label="Description" required>
              <el-input v-model="evidenceForm.description" type="textarea" :rows="3" placeholder="Detailed description" />
            </el-form-item>
            <el-form-item label="Evidence Type">
              <el-select v-model="evidenceForm.type" style="width: 100%">
                <el-option label="Document" value="document" />
                <el-option label="Image" value="image" />
                <el-option label="Video" value="video" />
                <el-option label="Audio" value="audio" />
                <el-option label="Log" value="log" />
                <el-option label="Credential" value="credential" />
              </el-select>
            </el-form-item>
            <el-form-item label="Upload File">
              <div class="upload-area" @click="triggerFileUpload">
                <el-icon><Upload /></el-icon>
                <span>Click to upload file</span>
                <input ref="fileUploadRef" type="file" style="display: none" @change="handleFileSelect" />
              </div>
              <div v-if="selectedFile" class="selected-file">
                <el-icon><Document /></el-icon>
                <span>{{ selectedFile.name }}</span>
                <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
                <el-button link type="danger" @click="selectedFile = null">Remove</el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: Generate Hash -->
        <div v-show="addStep === 1" class="step-panel">
          <div class="hash-preview">
            <div class="hash-label">SHA-256 Hash</div>
            <div class="hash-value">
              <code>{{ generatedHash || 'Click "Generate Hash" to compute' }}</code>
            </div>
            <el-button type="primary" @click="generateEvidenceHash" :loading="isGenerating">
              <el-icon><DataAnalysis /></el-icon>
              Generate Hash
            </el-button>
          </div>
          <div class="chain-info">
            <el-alert
                title="Chain Integrity"
                type="info"
                :description="`Previous evidence hash will be linked to maintain chain integrity. Current chain length: ${evidenceChain.length} records.`"
                show-icon
                :closable="false"
            />
          </div>
        </div>

        <!-- Step 3: Confirm -->
        <div v-show="addStep === 2" class="step-panel">
          <div class="confirm-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Title">{{ evidenceForm.title }}</el-descriptions-item>
              <el-descriptions-item label="Type">{{ evidenceForm.type || 'Not specified' }}</el-descriptions-item>
              <el-descriptions-item label="File">{{ selectedFile?.name || 'No file' }}</el-descriptions-item>
              <el-descriptions-item label="File Size">{{ formatFileSize(selectedFile?.size || 0) }}</el-descriptions-item>
              <el-descriptions-item label="Hash" :span="2">
                <code class="hash-code">{{ generatedHash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Previous Hash" :span="2">
                <code class="hash-code">{{ previousHash || 'Genesis (First evidence)' }}</code>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <div class="anchor-option">
            <el-checkbox v-model="anchorToBlockchain">Anchor to Blockchain</el-checkbox>
            <span class="form-hint">Permanently record evidence hash on blockchain</span>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="addStep > 0" @click="addStep--">Back</el-button>
        <el-button v-if="addStep < 2" type="primary" @click="addStep++" :disabled="!canProceedAdd">
          Next
        </el-button>
        <el-button v-if="addStep === 2" type="success" @click="addToChain" :loading="isAdding">
          <el-icon><Link /></el-icon>
          Add to Evidence Chain
        </el-button>
        <el-button @click="addDialog.visible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Evidence Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.evidence?.title" width="700px">
      <div v-if="detailDialog.evidence" class="evidence-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Evidence ID">{{ detailDialog.evidence.id }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.evidence.status)">{{ detailDialog.evidence.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Type">{{ detailDialog.evidence.type || 'Document' }}</el-descriptions-item>
          <el-descriptions-item label="Index">{{ detailDialog.evidence.index }}</el-descriptions-item>
          <el-descriptions-item label="Created By">{{ detailDialog.evidence.createdBy }}</el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ detailDialog.evidence.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.evidence.description }}</el-descriptions-item>
          <el-descriptions-item label="Hash" :span="2">
            <code class="hash-code">{{ detailDialog.evidence.hash }}</code>
            <el-button link size="small" @click="copyHash(detailDialog.evidence.hash)">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Previous Hash" :span="2">
            <code class="hash-code">{{ detailDialog.evidence.previousHash || 'Genesis' }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="Blockchain" :span="2" v-if="detailDialog.evidence.blockchain">
            <div class="blockchain-info">
              <div>Tx Hash: <code>{{ detailDialog.evidence.blockchain.txHash }}</code></div>
              <div>Block: {{ detailDialog.evidence.blockchain.blockNumber }}</div>
              <div>Network: {{ detailDialog.evidence.blockchain.network }}</div>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <div class="verification-section" v-if="detailDialog.evidence.verification">
          <h4>Verification Record</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Verified At">{{ detailDialog.evidence.verification.timestamp }}</el-descriptions-item>
            <el-descriptions-item label="Verified By">{{ detailDialog.evidence.verification.verifiedBy }}</el-descriptions-item>
            <el-descriptions-item label="Chain Valid">{{ detailDialog.evidence.verification.chainValid ? 'Yes' : 'No' }}</el-descriptions-item>
            <el-descriptions-item label="Hash Match">{{ detailDialog.evidence.verification.hashMatch ? 'Yes' : 'No' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>

    <!-- Verify Chain Dialog -->
    <el-dialog v-model="verifyDialog.visible" title="Chain Verification Result" width="550px">
      <div class="verify-result" :class="verificationResult?.valid ? 'valid' : 'invalid'">
        <div class="result-icon">
          <el-icon v-if="verificationResult?.valid"><CircleCheck /></el-icon>
          <el-icon v-else><CircleClose /></el-icon>
        </div>
        <div class="result-content">
          <h3>{{ verificationResult?.valid ? 'Chain Integrity Verified' : 'Chain Integrity Compromised' }}</h3>
          <p>{{ verificationResult?.message }}</p>
          <div class="result-stats">
            <div>Total Records: {{ verificationResult?.totalRecords }}</div>
            <div>Verified Records: {{ verificationResult?.verifiedCount }}</div>
            <div>Tampered Records: {{ verificationResult?.tamperedCount }}</div>
            <div>Blockchain Anchored: {{ verificationResult?.anchoredCount }}</div>
          </div>
          <div v-if="verificationResult?.brokenLinks?.length" class="broken-links">
            <h4>Broken Links Detected</h4>
            <div v-for="link in verificationResult.brokenLinks" :key="link.index" class="broken-link">
              Link between #{{ link.prevIndex }} and #{{ link.currIndex }} is broken
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="verifyDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="exportVerificationReport">Export Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Search,
  Download,
  Link,
  CircleCheck,
  Clock,
  DataAnalysis,
  CopyDocument,
  Upload,
  Document,
  CircleClose,
  RefreshLeft,
  Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading evidence chain...',
  'Verifying chain integrity...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface Evidence {
  id: string
  index: number
  title: string
  description: string
  type: string
  hash: string
  previousHash: string | null
  timestamp: string
  createdBy: string
  status: 'verified' | 'pending' | 'tampered'
  anchored: boolean
  blockchain?: {
    txHash: string
    blockNumber: number
    network: string
    timestamp: string
  }
  verification?: {
    timestamp: string
    verifiedBy: string
    chainValid: boolean
    hashMatch: boolean
  }
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalEvidence: 24,
  verifiedCount: 22,
  chainIntegrity: 100,
  anchoredCount: 18
})

const evidenceChain = ref<Evidence[]>([
  {
    id: 'EVD-001',
    index: 1,
    title: 'Security Audit Report - Q1 2024',
    description: 'Comprehensive security audit report for Q1 2024',
    type: 'document',
    hash: '0x3a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    previousHash: null,
    timestamp: '2024-06-01 10:00:00',
    createdBy: 'security@ibms.com',
    status: 'verified',
    anchored: true,
    blockchain: {
      txHash: '0x7a6b5c4d3e2f1a0b',
      blockNumber: 18234567,
      network: 'Ethereum',
      timestamp: '2024-06-01 14:30:00'
    },
    verification: {
      timestamp: '2024-06-01 15:00:00',
      verifiedBy: 'system',
      chainValid: true,
      hashMatch: true
    }
  },
  {
    id: 'EVD-002',
    index: 2,
    title: 'Compliance Certificate - ISO 27001',
    description: 'ISO 27001:2022 compliance certification',
    type: 'credential',
    hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    previousHash: '0x3a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    timestamp: '2024-06-05 14:30:00',
    createdBy: 'compliance@ibms.com',
    status: 'verified',
    anchored: true,
    blockchain: {
      txHash: '0x8b7a6c5d4e3f2a1b',
      blockNumber: 18234890,
      network: 'Ethereum',
      timestamp: '2024-06-05 16:00:00'
    },
    verification: {
      timestamp: '2024-06-05 16:30:00',
      verifiedBy: 'system',
      chainValid: true,
      hashMatch: true
    }
  },
  {
    id: 'EVD-003',
    index: 3,
    title: 'AI Model Validation Report',
    description: 'Validation results for Energy Optimization AI model',
    type: 'document',
    hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    previousHash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    timestamp: '2024-06-10 09:15:00',
    createdBy: 'ai-team@ibms.com',
    status: 'verified',
    anchored: true,
    blockchain: {
      txHash: '0x9c8b7a6d5e4f3a2c',
      blockNumber: 18235123,
      network: 'Polygon',
      timestamp: '2024-06-10 11:00:00'
    },
    verification: {
      timestamp: '2024-06-10 11:30:00',
      verifiedBy: 'system',
      chainValid: true,
      hashMatch: true
    }
  },
  {
    id: 'EVD-004',
    index: 4,
    title: 'Incident Response Log',
    description: 'Security incident response documentation',
    type: 'log',
    hash: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5',
    previousHash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    timestamp: '2024-06-12 16:45:00',
    createdBy: 'soc@ibms.com',
    status: 'pending',
    anchored: false,
    verification: null
  }
])

const filters = reactive({
  search: '',
  status: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const addDialog = reactive({
  visible: false
})

const detailDialog = reactive({
  visible: false,
  evidence: null as Evidence | null
})

const verifyDialog = reactive({
  visible: false
})

const verificationResult = ref<any>(null)

const addStep = ref(0)
const isGenerating = ref(false)
const isAdding = ref(false)
const generatedHash = ref('')
const selectedFile = ref<File | null>(null)
const anchorToBlockchain = ref(true)

const chainCanvasRef = ref<HTMLCanvasElement | null>(null)
const chainContainerRef = ref<HTMLDivElement | null>(null)
const fileUploadRef = ref<HTMLInputElement | null>(null)
const selectedEvidence = ref<Evidence | null>(null)
const tooltipStyle = ref({})

let animationFrameId: number | null = null

const evidenceForm = reactive({
  title: '',
  description: '',
  type: ''
})

// ==================== 计算属性 ====================
const filteredEvidence = computed(() => {
  let filtered = [...evidenceChain.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(e =>
        e.id.toLowerCase().includes(searchLower) ||
        e.title.toLowerCase().includes(searchLower) ||
        e.hash.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(e => e.status === filters.status)
  }

  pagination.total = filtered.length
  return filtered
})

const previousHash = computed(() => {
  if (evidenceChain.value.length > 0) {
    return evidenceChain.value[evidenceChain.value.length - 1].hash
  }
  return null
})

const canProceedAdd = computed(() => {
  if (addStep.value === 0) {
    return evidenceForm.title.trim() !== '' && evidenceForm.description.trim() !== ''
  }
  if (addStep.value === 1) {
    return generatedHash.value !== ''
  }
  return true
})

// ==================== 辅助函数 ====================
const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'verified': 'success',
    'pending': 'warning',
    'tampered': 'danger'
  }
  return map[status] || 'info'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toDouble(2)) + ' ' + sizes[i]
}

const copyHash = async (hash: string) => {
  try {
    await navigator.clipboard.writeText(hash)
    ElMessage.success('Hash copied to clipboard')
  } catch {
    ElMessage.error('Failed to copy')
  }
}

const triggerFileUpload = () => {
  fileUploadRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
  }
}

const generateEvidenceHash = async () => {
  isGenerating.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))

  const hash = Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')
  generatedHash.value = `0x${hash}`

  isGenerating.value = false
  ElMessage.success('Hash generated successfully')
}

const addToChain = async () => {
  isAdding.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const newId = `EVD-${String(evidenceChain.value.length + 1).padStart(3, '0')}`
  const newEvidence: Evidence = {
    id: newId,
    index: evidenceChain.value.length + 1,
    title: evidenceForm.title,
    description: evidenceForm.description,
    type: evidenceForm.type || 'document',
    hash: generatedHash.value,
    previousHash: previousHash.value,
    timestamp: new Date().toLocaleString(),
    createdBy: 'admin@ibms.com',
    status: 'pending',
    anchored: anchorToBlockchain.value,
    blockchain: anchorToBlockchain.value ? {
      txHash: `0x${Array.from({ length: 32 }, () => Math.random().toString(16)[2]).join('')}`,
      blockNumber: 18235000 + Math.floor(Math.random() * 1000),
      network: 'Ethereum',
      timestamp: new Date().toISOString()
    } : undefined
  }

  evidenceChain.value.push(newEvidence)
  stats.totalEvidence++
  if (anchorToBlockchain.value) stats.anchoredCount++

  isAdding.value = false
  addDialog.visible = false
  ElMessage.success('Evidence added to chain')

  // Reset form
  addStep.value = 0
  evidenceForm.title = ''
  evidenceForm.description = ''
  evidenceForm.type = ''
  generatedHash.value = ''
  selectedFile.value = null
  anchorToBlockchain.value = true
}

const openAddEvidenceDialog = () => {
  addStep.value = 0
  evidenceForm.title = ''
  evidenceForm.description = ''
  evidenceForm.type = ''
  generatedHash.value = ''
  selectedFile.value = null
  anchorToBlockchain.value = true
  addDialog.visible = true
}

const viewEvidenceDetail = (evidence: Evidence) => {
  detailDialog.evidence = evidence
  detailDialog.visible = true
}

const verifyEvidence = (evidence: Evidence) => {
  ElMessage.success(`Verifying evidence ${evidence.id}...`)
  setTimeout(() => {
    evidence.status = 'verified'
    evidence.verification = {
      timestamp: new Date().toLocaleString(),
      verifiedBy: 'admin@ibms.com',
      chainValid: true,
      hashMatch: true
    }
    stats.verifiedCount++
    ElMessage.success(`Evidence ${evidence.id} verified successfully`)
  }, 1000)
}

const verifyChain = async () => {
  await new Promise(resolve => setTimeout(resolve, 1500))

  let valid = true
  let verifiedCount = 0
  let tamperedCount = 0
  let brokenLinks: any[] = []

  for (let i = 0; i < evidenceChain.value.length; i++) {
    const current = evidenceChain.value[i]
    if (current.status === 'verified') verifiedCount++
    if (current.status === 'tampered') tamperedCount++

    if (i > 0) {
      const previous = evidenceChain.value[i - 1]
      if (current.previousHash !== previous.hash) {
        valid = false
        brokenLinks.push({ prevIndex: i, currIndex: i + 1 })
      }
    }
  }

  verificationResult.value = {
    valid: valid,
    message: valid
        ? 'The evidence chain is intact and all records are properly linked.'
        : 'Chain integrity compromised. Broken links detected.',
    totalRecords: evidenceChain.value.length,
    verifiedCount: verifiedCount,
    tamperedCount: tamperedCount,
    anchoredCount: evidenceChain.value.filter(e => e.anchored).length,
    brokenLinks: brokenLinks
  }

  stats.chainIntegrity = valid ? 100 : Math.floor((1 - brokenLinks.length / evidenceChain.value.length) * 100)
  verifyDialog.visible = true
}

const exportChain = () => {
  const exportData = {
    exportedAt: new Date().toISOString(),
    chain: evidenceChain.value,
    stats: stats
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `evidence-chain-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Evidence chain exported')
}

const exportVerificationReport = () => {
  const report = {
    verifiedAt: new Date().toISOString(),
    result: verificationResult.value
  }
  const data = JSON.stringify(report, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `chain-verification-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Verification report exported')
}

// ==================== 链可视化绘制 ====================
const drawChain = () => {
  const canvas = chainCanvasRef.value
  const container = chainContainerRef.value
  if (!canvas || !container) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const width = container.clientWidth
  const height = 400
  canvas.width = width
  canvas.height = height

  ctx.fillStyle = '#1a1a2e'
  ctx.fillRect(0, 0, width, height)

  const chain = evidenceChain.value
  const nodeRadius = 30
  const startY = height / 2
  const spacing = Math.min(120, (width - 100) / Math.max(chain.length, 1))
  const startX = 60

  chain.forEach((evidence, idx) => {
    const x = startX + idx * spacing
    const y = startY

    // Draw connecting line
    if (idx > 0) {
      const prevX = startX + (idx - 1) * spacing
      ctx.beginPath()
      ctx.moveTo(prevX + nodeRadius, y)
      ctx.lineTo(x - nodeRadius, y)

      const isBroken = evidence.previousHash !== chain[idx - 1].hash
      ctx.strokeStyle = isBroken ? '#f56c6c' : '#67c23a'
      ctx.lineWidth = 2
      ctx.stroke()
    }

    // Draw node
    ctx.beginPath()
    ctx.arc(x, y, nodeRadius, 0, Math.PI * 2)

    let color = '#8c9aab'
    if (evidence.status === 'verified') color = '#67c23a'
    else if (evidence.status === 'pending') color = '#e6a23c'
    else if (evidence.status === 'tampered') color = '#f56c6c'

    ctx.fillStyle = color + '40'
    ctx.fill()
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.stroke()

    // Draw index
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(evidence.index.toString(), x, y)

    // Draw anchor icon for blockchain anchored
    if (evidence.anchored) {
      ctx.beginPath()
      ctx.arc(x + 20, y - 20, 8, 0, Math.PI * 2)
      ctx.fillStyle = '#409eff'
      ctx.fill()
      ctx.fillStyle = '#ffffff'
      ctx.font = '10px Arial'
      ctx.fillText('⛓️', x + 18, y - 22)
    }

    // Draw hash preview on hover
    if (selectedEvidence.value?.id === evidence.id) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
      ctx.fillRect(x - 80, y - 60, 160, 50)
      ctx.fillStyle = '#ffffff'
      ctx.font = '10px monospace'
      ctx.fillText(evidence.hash.substring(0, 12) + '...', x - 70, y - 40)
    }
  })

  // Draw legend
  ctx.fillStyle = '#ffffff'
  ctx.font = '12px Arial'
  ctx.fillText('Evidence Chain Visualization', width - 200, 30)
}

const startRenderLoop = () => {
  const render = () => {
    drawChain()
    animationFrameId = requestAnimationFrame(render)
  }
  render()
}

// ==================== 生命周期 ====================
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
      startRenderLoop()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
})
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

/* ==================== Main Content Styles ==================== */
.evidence-chain-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Cards */
.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Chain Visualization */
.chain-visualization-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.chain-legend {
  display: flex;
  gap: 20px;
  font-size: 12px;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 6px;
}

.legend-dot.verified { background-color: #67c23a; }
.legend-dot.pending { background-color: #e6a23c; }
.legend-dot.anchored { background-color: #409eff; }
.legend-dot.broken { background-color: #f56c6c; }

.chain-container {
  position: relative;
}

.chain-canvas {
  width: 100%;
  height: 400px;
  display: block;
  background: #1a1a2e;
  border-radius: 8px;
}

.chain-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px;
  border-radius: 8px;
  font-size: 12px;
  z-index: 100;
  min-width: 200px;
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

/* Evidence Table */
.evidence-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.hash-code {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.root-text {
  color: #8c9aab;
  font-style: italic;
}

/* Add Dialog */
.add-content {
  min-height: 350px;
}

.step-panel {
  padding: 8px 0;
}

.upload-area {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

.file-size {
  margin-left: auto;
  font-size: 11px;
  color: #8c9aab;
}

.hash-preview {
  text-align: center;
  padding: 20px;
}

.hash-value {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  word-break: break-all;
}

.chain-info {
  margin-top: 20px;
}

.confirm-info {
  margin-bottom: 20px;
}

.anchor-option {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.form-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #8c9aab;
}

/* Evidence Detail */
.evidence-detail {
  padding: 8px 0;
}

.blockchain-info {
  font-size: 12px;
}

.blockchain-info code {
  font-size: 11px;
}

.verification-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.verification-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

/* Verify Dialog */
.verify-result {
  padding: 20px;
  border-radius: 12px;
  display: flex;
  gap: 20px;
}

.verify-result.valid {
  background-color: #f0f9eb;
  border: 1px solid #67c23a;
}

.verify-result.invalid {
  background-color: #fef0f0;
  border: 1px solid #f56c6c;
}

.result-icon {
  font-size: 48px;
}

.verify-result.valid .result-icon { color: #67c23a; }
.verify-result.invalid .result-icon { color: #f56c6c; }

.result-content {
  flex: 1;
}

.result-content h3 {
  margin: 0 0 8px 0;
}

.result-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin: 16px 0;
  padding: 12px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.broken-links {
  margin-top: 16px;
}

.broken-links h4 {
  margin: 0 0 8px 0;
  font-size: 13px;
}

.broken-link {
  padding: 4px 0;
  color: #f56c6c;
  font-size: 12px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-step__title) {
  font-size: 12px;
}
</style>