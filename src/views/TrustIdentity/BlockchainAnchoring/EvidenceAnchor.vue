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
        <div class="loading-tip">Trust & Identity - Blockchain Anchoring</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="evidence-anchor-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Evidence Anchor</h1>
        <p>Anchor digital evidence to blockchain for immutable proof of existence and integrity</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAnchorDialog">
          <el-icon><Link /></el-icon>
          Anchor New Evidence
        </el-button>
        <el-button @click="verifyAnchor">
          <el-icon><Search /></el-icon>
          Verify Anchor
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalAnchors }}</div>
            <div class="stat-label">Total Anchors</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.confirmedAnchors }}</div>
            <div class="stat-label">Confirmed</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.pendingAnchors }}</div>
            <div class="stat-label">Pending</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.networkStatus }}</div>
            <div class="stat-label">Network</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Blockchain Status Bar -->
    <div class="blockchain-status">
      <div class="status-left">
        <div class="status-indicator" :class="blockchainStatus"></div>
        <span class="status-text">Blockchain: {{ blockchainStatus === 'connected' ? 'Connected' : 'Disconnected' }}</span>
        <span class="network-name">{{ networkName }}</span>
      </div>
      <div class="status-right">
        <span>Block Height: {{ blockHeight }}</span>
        <span>Gas Price: {{ gasPrice }} Gwei</span>
        <span>Last Block: {{ lastBlockTime }}</span>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by evidence ID, hash, or description..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Confirmed" value="confirmed" />
        <el-option label="Pending" value="pending" />
        <el-option label="Failed" value="failed" />
      </el-select>
      <el-select v-model="filters.type" placeholder="Type" clearable style="width: 140px">
        <el-option label="All Types" value="" />
        <el-option label="Document" value="document" />
        <el-option label="Image" value="image" />
        <el-option label="Video" value="video" />
        <el-option label="Credential" value="credential" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 260px"
      />
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        Apply
      </el-button>
      <el-button @click="resetFilters">
        <el-icon><RefreshLeft /></el-icon>
        Reset
      </el-button>
    </div>

    <!-- Evidence Anchors Table -->
    <div class="anchors-table-wrapper">
      <el-table :data="filteredAnchors" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="Evidence ID" width="120" />
        <el-table-column prop="name" label="Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hash" label="SHA-256 Hash" width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="hash-code">{{ row.hash }}</code>
            <el-button link size="small" @click="copyHash(row.hash)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="txHash" label="Transaction Hash" width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="tx-hash" v-if="row.txHash">{{ row.txHash }}</code>
            <span v-else class="pending-text">Pending</span>
            <el-button v-if="row.txHash" link size="small" @click="viewOnExplorer(row.txHash)">
              <el-icon><Link /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="blockNumber" label="Block" width="100">
          <template #default="{ row }">
            {{ row.blockNumber || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="Anchored At" width="160" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button v-if="row.status === 'confirmed'" link type="success" size="small" @click="verifyEvidence(row)">
              Verify
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Anchor Evidence Dialog -->
    <el-dialog v-model="anchorDialog.visible" title="Anchor Evidence to Blockchain" width="650px" class="anchor-dialog">
      <div class="anchor-steps">
        <el-steps :active="anchorStep" finish-status="success" align-center>
          <el-step title="Select File" />
          <el-step title="Generate Hash" />
          <el-step title="Confirm & Anchor" />
        </el-steps>
      </div>

      <div class="anchor-content">
        <!-- Step 1: Select File -->
        <div v-show="anchorStep === 0" class="step-panel">
          <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop" @click="triggerFileInput">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">Drag & drop file here or click to browse</div>
            <div class="upload-hint">Supports any file type (Max 100MB)</div>
            <input ref="fileInputRef" type="file" style="display: none" @change="handleFileSelect" />
          </div>
          <div v-if="selectedFile" class="selected-file">
            <el-icon><Document /></el-icon>
            <span>{{ selectedFile.name }}</span>
            <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
            <el-button link type="danger" @click="selectedFile = null">Remove</el-button>
          </div>

          <el-form :model="evidenceForm" label-width="100px" style="margin-top: 20px">
            <el-form-item label="Evidence Name">
              <el-input v-model="evidenceForm.name" placeholder="Enter a descriptive name" />
            </el-form-item>
            <el-form-item label="Description">
              <el-input v-model="evidenceForm.description" type="textarea" :rows="2" placeholder="Optional description" />
            </el-form-item>
            <el-form-item label="Evidence Type">
              <el-select v-model="evidenceForm.type" placeholder="Select type">
                <el-option label="Document" value="document" />
                <el-option label="Image" value="image" />
                <el-option label="Video" value="video" />
                <el-option label="Credential" value="credential" />
                <el-option label="Report" value="report" />
                <el-option label="Other" value="other" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: Generate Hash -->
        <div v-show="anchorStep === 1" class="step-panel">
          <div class="hash-preview">
            <div class="hash-label">SHA-256 Hash</div>
            <div class="hash-value">
              <code>{{ generatedHash || 'Click "Generate Hash" to compute' }}</code>
            </div>
            <el-button type="primary" @click="generateHash" :loading="isGeneratingHash">
              <el-icon><DataAnalysis /></el-icon>
              Generate Hash
            </el-button>
          </div>
          <div class="hash-info">
            <el-alert
                title="What is this?"
                type="info"
                description="The SHA-256 hash is a unique fingerprint of your file. Even a tiny change in the file produces a completely different hash."
                show-icon
                :closable="false"
            />
          </div>
        </div>

        <!-- Step 3: Confirm & Anchor -->
        <div v-show="anchorStep === 2" class="step-panel">
          <div class="confirm-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Evidence Name">{{ evidenceForm.name || 'Untitled' }}</el-descriptions-item>
              <el-descriptions-item label="Evidence Type">{{ evidenceForm.type || 'Not specified' }}</el-descriptions-item>
              <el-descriptions-item label="File Name">{{ selectedFile?.name }}</el-descriptions-item>
              <el-descriptions-item label="File Size">{{ formatFileSize(selectedFile?.size || 0) }}</el-descriptions-item>
              <el-descriptions-item label="SHA-256 Hash" :span="2">
                <code class="hash-code">{{ generatedHash }}</code>
              </el-descriptions-item>
            </el-descriptions>
          </div>
          <div class="anchor-params">
            <el-form label-width="120px">
              <el-form-item label="Network">
                <el-select v-model="anchorParams.network" style="width: 100%">
                  <el-option label="Ethereum Mainnet" value="ethereum" />
                  <el-option label="Polygon" value="polygon" />
                  <el-option label="Binance Smart Chain" value="bsc" />
                  <el-option label="Hyperledger Fabric" value="fabric" />
                </el-select>
              </el-form-item>
              <el-form-item label="Gas Limit">
                <el-input-number v-model="anchorParams.gasLimit" :min="50000" :max="500000" :step="10000" />
              </el-form-item>
              <el-form-item label="Include Metadata">
                <el-switch v-model="anchorParams.includeMetadata" />
                <span class="form-hint">Store additional metadata on-chain</span>
              </el-form-item>
            </el-form>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button v-if="anchorStep > 0" @click="anchorStep--">Back</el-button>
        <el-button v-if="anchorStep < 2" type="primary" @click="anchorStep++" :disabled="!canProceedToNext">
          Next
        </el-button>
        <el-button v-if="anchorStep === 2" type="success" @click="anchorToBlockchain" :loading="isAnchoring">
          <el-icon><Link /></el-icon>
          Anchor to Blockchain
        </el-button>
        <el-button @click="anchorDialog.visible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Evidence Details Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.evidence?.name" width="700px">
      <div v-if="detailDialog.evidence" class="evidence-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Evidence ID">{{ detailDialog.evidence.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ detailDialog.evidence.type }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.evidence.status)">{{ detailDialog.evidence.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="File Size">{{ detailDialog.evidence.fileSize }}</el-descriptions-item>
          <el-descriptions-item label="SHA-256 Hash" :span="2">
            <code class="hash-code">{{ detailDialog.evidence.hash }}</code>
            <el-button link size="small" @click="copyHash(detailDialog.evidence.hash)">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Transaction Hash" :span="2" v-if="detailDialog.evidence.txHash">
            <code class="tx-hash">{{ detailDialog.evidence.txHash }}</code>
            <el-button link size="small" @click="viewOnExplorer(detailDialog.evidence.txHash)">View on Explorer</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Block Number">{{ detailDialog.evidence.blockNumber || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Block Hash">{{ detailDialog.evidence.blockHash || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Network">{{ detailDialog.evidence.network }}</el-descriptions-item>
          <el-descriptions-item label="Anchored At">{{ detailDialog.evidence.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Anchored By">{{ detailDialog.evidence.anchoredBy }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ detailDialog.evidence.description || 'No description' }}</el-descriptions-item>
          <el-descriptions-item label="Verification Proof" :span="2" v-if="detailDialog.evidence.proof">
            <div class="proof-data">
              <pre>{{ JSON.stringify(detailDialog.evidence.proof, null, 2) }}</pre>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Verification Dialog -->
    <el-dialog v-model="verifyDialog.visible" title="Verify Evidence" width="550px">
      <div class="verify-content">
        <div class="verify-area" @dragover.prevent @drop.prevent="handleVerifyDrop" @click="triggerVerifyFileInput">
          <el-icon class="upload-icon"><Search /></el-icon>
          <div class="upload-text">Drop file to verify or click to browse</div>
          <input ref="verifyFileInputRef" type="file" style="display: none" @change="handleVerifyFileSelect" />
        </div>
        <div v-if="verifyFile" class="selected-file">
          <el-icon><Document /></el-icon>
          <span>{{ verifyFile.name }}</span>
          <el-button link type="danger" @click="verifyFile = null">Remove</el-button>
        </div>

        <div v-if="verificationResult" class="verification-result" :class="verificationResult.isValid ? 'valid' : 'invalid'">
          <div class="result-icon">
            <el-icon v-if="verificationResult.isValid"><CircleCheck /></el-icon>
            <el-icon v-else><CircleClose /></el-icon>
          </div>
          <div class="result-content">
            <h4>{{ verificationResult.isValid ? 'Evidence Verified!' : 'Verification Failed' }}</h4>
            <p>{{ verificationResult.message }}</p>
            <div v-if="verificationResult.details" class="result-details">
              <div>Hash Match: {{ verificationResult.details.hashMatch ? 'Yes' : 'No' }}</div>
              <div>On-chain Hash: <code>{{ verificationResult.details.onChainHash }}</code></div>
              <div>Local Hash: <code>{{ verificationResult.details.localHash }}</code></div>
              <div>Block: {{ verificationResult.details.blockNumber }}</div>
              <div>Timestamp: {{ verificationResult.details.timestamp }}</div>
            </div>
          </div>
        </div>

        <div v-if="isVerifying" class="verifying">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>Verifying on blockchain...</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="verifyDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="resetVerification">New Verification</el-button>
      </template>
    </el-dialog>

    <!-- Success Dialog -->
    <el-dialog v-model="successDialog.visible" title="Anchor Successful" width="450px">
      <div class="success-content">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <h3>Evidence Successfully Anchored</h3>
        <p>Your evidence has been permanently recorded on the blockchain.</p>
        <div class="success-info">
          <div><strong>Transaction Hash:</strong> <code>{{ lastAnchorResult?.txHash }}</code></div>
          <div><strong>Block Number:</strong> {{ lastAnchorResult?.blockNumber }}</div>
          <div><strong>Network:</strong> {{ lastAnchorResult?.network }}</div>
        </div>
        <div class="success-actions">
          <el-button type="primary" @click="viewOnExplorer(lastAnchorResult?.txHash)">View on Explorer</el-button>
          <el-button @click="downloadProof">Download Proof</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Link,
  Search,
  Document,
  CircleCheck,
  Clock,
  Connection,
  CopyDocument,
  UploadFilled,
  DataAnalysis,
  Loading,
  CircleClose,
  RefreshLeft
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to blockchain...',
  'Loading anchor registry...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface EvidenceAnchor {
  id: string
  name: string
  description: string
  type: string
  hash: string
  txHash: string | null
  blockNumber: number | null
  blockHash: string | null
  network: string
  status: 'pending' | 'confirmed' | 'failed'
  timestamp: string
  anchoredBy: string
  fileSize: string
  proof?: any
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalAnchors: 156,
  confirmedAnchors: 148,
  pendingAnchors: 5,
  networkStatus: 'Ethereum'
})

const blockchainStatus = ref('connected')
const networkName = ref('Ethereum Mainnet')
const blockHeight = ref('18,234,567')
const gasPrice = ref('28')
const lastBlockTime = ref('12s ago')

const anchors = ref<EvidenceAnchor[]>([
  {
    id: 'EVD-001',
    name: 'Building Inspection Report',
    description: 'Structural integrity inspection report for Building A',
    type: 'document',
    hash: '0x3a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
    blockNumber: 18234567,
    blockHash: '0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8',
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-10 14:30:00',
    anchoredBy: 'admin@ibms.com',
    fileSize: '2.4 MB'
  },
  {
    id: 'EVD-002',
    name: 'Equipment Calibration Record',
    description: 'Annual calibration for HVAC equipment',
    type: 'document',
    hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
    blockNumber: 18234123,
    blockHash: '0x8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7',
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-08 09:15:00',
    anchoredBy: 'engineering@ibms.com',
    fileSize: '856 KB'
  },
  {
    id: 'EVD-003',
    name: 'Security Audit Log',
    description: 'Q2 2024 security audit findings',
    type: 'document',
    hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    txHash: null,
    blockNumber: null,
    blockHash: null,
    network: 'Polygon',
    status: 'pending',
    timestamp: '2024-06-12 11:20:00',
    anchoredBy: 'security@ibms.com',
    fileSize: '5.2 MB'
  },
  {
    id: 'EVD-004',
    name: 'Maintenance Certificate',
    description: 'Certified maintenance record for UPS systems',
    type: 'credential',
    hash: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5',
    txHash: '0x9c8b7a6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8c',
    blockNumber: 18234890,
    blockHash: '0x7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6',
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-05 16:45:00',
    anchoredBy: 'admin@ibms.com',
    fileSize: '1.1 MB'
  }
])

const filters = reactive({
  search: '',
  status: '',
  type: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

const anchorDialog = reactive({
  visible: false
})

const detailDialog = reactive({
  visible: false,
  evidence: null as EvidenceAnchor | null
})

const verifyDialog = reactive({
  visible: false
})

const successDialog = reactive({
  visible: false
})

const anchorStep = ref(0)
const selectedFile = ref<File | null>(null)
const generatedHash = ref('')
const isGeneratingHash = ref(false)
const isAnchoring = ref(false)
const isVerifying = ref(false)
const verifyFile = ref<File | null>(null)
const verificationResult = ref<any>(null)
const lastAnchorResult = ref<any>(null)

const fileInputRef = ref<HTMLInputElement | null>(null)
const verifyFileInputRef = ref<HTMLInputElement | null>(null)

const evidenceForm = reactive({
  name: '',
  description: '',
  type: ''
})

const anchorParams = reactive({
  network: 'ethereum',
  gasLimit: 100000,
  includeMetadata: true
})

// ==================== 计算属性 ====================
const filteredAnchors = computed(() => {
  let filtered = [...anchors.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(a =>
        a.id.toLowerCase().includes(searchLower) ||
        a.name.toLowerCase().includes(searchLower) ||
        a.hash.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(a => a.status === filters.status)
  }

  if (filters.type) {
    filtered = filtered.filter(a => a.type === filters.type)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(a => {
      const date = new Date(a.timestamp)
      return date >= start && date <= end
    })
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

const canProceedToNext = computed(() => {
  if (anchorStep.value === 0) {
    return selectedFile.value !== null && evidenceForm.name.trim() !== ''
  }
  if (anchorStep.value === 1) {
    return generatedHash.value !== ''
  }
  return true
})

// ==================== 辅助函数 ====================
const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'warning',
    'confirmed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const copyHash = async (hash: string) => {
  try {
    await navigator.clipboard.writeText(hash)
    ElMessage.success('Hash copied to clipboard')
  } catch {
    ElMessage.error('Failed to copy')
  }
}

const viewOnExplorer = (hash: string) => {
  if (hash) {
    window.open(`https://etherscan.io/tx/${hash}`, '_blank')
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.type = ''
  filters.dateRange = null
  pagination.currentPage = 1
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const triggerFileInput = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0]
    evidenceForm.name = selectedFile.value.name
  }
}

const handleDrop = (e: DragEvent) => {
  const files = e.dataTransfer?.files
  if (files && files[0]) {
    selectedFile.value = files[0]
    evidenceForm.name = selectedFile.value.name
  }
}

const generateHash = async () => {
  if (!selectedFile.value) return

  isGeneratingHash.value = true

  await new Promise(resolve => setTimeout(resolve, 1000))

  // Simulate SHA-256 hash generation
  const hash = Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')

  generatedHash.value = `0x${hash}`
  isGeneratingHash.value = false
  ElMessage.success('Hash generated successfully')
}

const anchorToBlockchain = async () => {
  isAnchoring.value = true

  await new Promise(resolve => setTimeout(resolve, 3000))

  const txHash = `0x${Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')}`

  const blockNumber = 18235000 + Math.floor(Math.random() * 1000)

  const newAnchor: EvidenceAnchor = {
    id: `EVD-${String(anchors.value.length + 1).padStart(3, '0')}`,
    name: evidenceForm.name,
    description: evidenceForm.description,
    type: evidenceForm.type || 'document',
    hash: generatedHash.value,
    txHash: txHash,
    blockNumber: blockNumber,
    blockHash: `0x${Array.from({ length: 64 }, () =>
        '0123456789abcdef'[Math.floor(Math.random() * 16)]
    ).join('')}`,
    network: anchorParams.network,
    status: 'pending',
    timestamp: new Date().toLocaleString(),
    anchoredBy: 'admin@ibms.com',
    fileSize: formatFileSize(selectedFile.value!.size),
    proof: {
      hash: generatedHash.value,
      txHash: txHash,
      blockNumber: blockNumber,
      timestamp: new Date().toISOString(),
      anchorType: 'evidential'
    }
  }

  anchors.value.unshift(newAnchor)
  stats.totalAnchors++
  stats.pendingAnchors++

  lastAnchorResult.value = {
    txHash: txHash,
    blockNumber: blockNumber,
    network: anchorParams.network
  }

  isAnchoring.value = false
  anchorDialog.visible = false
  successDialog.visible = true

  // Simulate confirmation after a few seconds
  setTimeout(() => {
    const index = anchors.value.findIndex(a => a.id === newAnchor.id)
    if (index !== -1) {
      anchors.value[index].status = 'confirmed'
      stats.pendingAnchors--
      stats.confirmedAnchors++
    }
  }, 5000)

  resetAnchorForm()
}

const resetAnchorForm = () => {
  anchorStep.value = 0
  selectedFile.value = null
  generatedHash.value = ''
  evidenceForm.name = ''
  evidenceForm.description = ''
  evidenceForm.type = ''
  anchorParams.network = 'ethereum'
  anchorParams.gasLimit = 100000
}

const openAnchorDialog = () => {
  resetAnchorForm()
  anchorDialog.visible = true
}

const viewDetails = (evidence: EvidenceAnchor) => {
  detailDialog.evidence = evidence
  detailDialog.visible = true
}

const verifyAnchor = () => {
  verifyDialog.visible = true
  verifyFile.value = null
  verificationResult.value = null
}

const triggerVerifyFileInput = () => {
  verifyFileInputRef.value?.click()
}

const handleVerifyFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    verifyFile.value = input.files[0]
    performVerification()
  }
}

const handleVerifyDrop = (e: DragEvent) => {
  const files = e.dataTransfer?.files
  if (files && files[0]) {
    verifyFile.value = files[0]
    performVerification()
  }
}

const performVerification = async () => {
  if (!verifyFile.value) return

  isVerifying.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  // Simulate verification
  const success = Math.random() > 0.2
  verificationResult.value = {
    isValid: success,
    message: success
        ? 'The file matches the on-chain record. Evidence is authentic and untampered.'
        : 'Hash mismatch. The file may have been altered or never anchored.',
    details: success ? {
      hashMatch: true,
      onChainHash: '0x3a2b...f1a2b',
      localHash: '0x3a2b...f1a2b',
      blockNumber: 18234567,
      timestamp: '2024-06-10 14:30:00 UTC'
    } : {
      hashMatch: false,
      onChainHash: '0x7a6b...c9d8e',
      localHash: generateRandomHash(),
      blockNumber: null,
      timestamp: null
    }
  }

  isVerifying.value = false
}

const generateRandomHash = () => {
  return `0x${Array.from({ length: 32 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')}`
}

const resetVerification = () => {
  verifyFile.value = null
  verificationResult.value = null
}

const verifyEvidence = (evidence: EvidenceAnchor) => {
  verifyDialog.visible = true
  verifyFile.value = null
  verificationResult.value = {
    isValid: true,
    message: 'Evidence verified on blockchain. Hash matches on-chain record.',
    details: {
      hashMatch: true,
      onChainHash: evidence.hash,
      localHash: evidence.hash,
      blockNumber: evidence.blockNumber,
      timestamp: evidence.timestamp
    }
  }
}

const downloadProof = () => {
  const proof = {
    anchoredAt: new Date().toISOString(),
    transactionHash: lastAnchorResult.value?.txHash,
    blockNumber: lastAnchorResult.value?.blockNumber,
    network: lastAnchorResult.value?.network,
    evidence: {
      name: evidenceForm.name,
      type: evidenceForm.type,
      hash: generatedHash.value
    }
  }
  const data = JSON.stringify(proof, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `anchor-proof-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Proof downloaded')
}

// ==================== 数据加载 ====================
const loadData = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
  }, 500)
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  // Cleanup
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
.evidence-anchor-page {
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

/* Blockchain Status */
.blockchain-status {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.status-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-indicator.connected {
  background-color: #67c23a;
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.status-indicator.disconnected {
  background-color: #f56c6c;
}

.network-name {
  color: #409eff;
  font-weight: 500;
}

.status-right {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: #5e6e82;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Anchors Table */
.anchors-table-wrapper {
  background: white;
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.hash-code, .tx-hash {
  font-family: monospace;
  font-size: 12px;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.pending-text {
  color: #e6a23c;
  font-style: italic;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
}

/* Anchor Dialog */
.anchor-dialog :deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

.anchor-steps {
  margin-bottom: 30px;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.upload-icon {
  font-size: 48px;
  color: #8c9aab;
  margin-bottom: 16px;
}

.selected-file {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 8px;
}

.file-size {
  margin-left: auto;
  color: #8c9aab;
  font-size: 12px;
}

.hash-preview {
  text-align: center;
  padding: 20px;
}

.hash-label {
  font-weight: 500;
  margin-bottom: 12px;
}

.hash-value {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  word-break: break-all;
}

.hash-info {
  margin-top: 20px;
}

.confirm-info {
  margin-bottom: 20px;
}

.anchor-params {
  margin-top: 20px;
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

.proof-data {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  max-height: 200px;
}

.proof-data pre {
  margin: 0;
  font-size: 11px;
}

/* Verification Dialog */
.verify-content {
  padding: 8px 0;
}

.verify-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.verify-area:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.verification-result {
  margin-top: 20px;
  padding: 20px;
  border-radius: 8px;
  display: flex;
  gap: 16px;
}

.verification-result.valid {
  background-color: #f0f9eb;
  border: 1px solid #67c23a;
}

.verification-result.invalid {
  background-color: #fef0f0;
  border: 1px solid #f56c6c;
}

.result-icon {
  font-size: 32px;
}

.verification-result.valid .result-icon { color: #67c23a; }
.verification-result.invalid .result-icon { color: #f56c6c; }

.result-content {
  flex: 1;
}

.result-content h4 {
  margin: 0 0 8px 0;
}

.result-details {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 12px;
}

.verifying {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: #409eff;
}

/* Success Dialog */
.success-content {
  text-align: center;
  padding: 20px;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
  margin-bottom: 20px;
}

.success-info {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  margin: 20px 0;
  text-align: left;
}

.success-info div {
  margin-bottom: 8px;
  word-break: break-all;
}

.success-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-step__title) {
  font-size: 12px;
}
</style>