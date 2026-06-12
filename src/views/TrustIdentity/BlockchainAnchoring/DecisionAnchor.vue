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
  <div v-else class="decision-anchor-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Decision Anchor</h1>
        <p>Anchor governance decisions to blockchain for immutable audit trail and transparency</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAnchorDialog">
          <el-icon><Link /></el-icon>
          Anchor Decision
        </el-button>
        <el-button @click="verifyAnchor">
          <el-icon><Search /></el-icon>
          Verify Decision
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
            <div class="stat-value">{{ stats.totalDecisions }}</div>
            <div class="stat-label">Total Decisions</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.confirmedDecisions }}</div>
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
            <div class="stat-value">{{ stats.pendingDecisions }}</div>
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
          placeholder="Search by decision ID, title, or hash..."
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
        <el-option label="Policy Change" value="policy" />
        <el-option label="Approval" value="approval" />
        <el-option label="Rejection" value="rejection" />
        <el-option label="Escalation" value="escalation" />
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

    <!-- Decision Anchors Table -->
    <div class="anchors-table-wrapper">
      <el-table :data="filteredDecisions" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="Decision ID" width="120" />
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ formatDecisionType(row.type) }}</el-tag>
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
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">
              Details
            </el-button>
            <el-button v-if="row.status === 'confirmed'" link type="success" size="small" @click="verifyDecision(row)">
              Verify
            </el-button>
            <el-button v-if="row.status !== 'confirmed'" link type="info" size="small" @click="viewOnChainStatus(row)">
              Check Status
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

    <!-- Anchor Decision Dialog -->
    <el-dialog v-model="anchorDialog.visible" title="Anchor Decision to Blockchain" width="700px" class="anchor-dialog">
      <div class="anchor-steps">
        <el-steps :active="anchorStep" finish-status="success" align-center>
          <el-step title="Decision Details" />
          <el-step title="Generate Hash" />
          <el-step title="Confirm & Anchor" />
        </el-steps>
      </div>

      <div class="anchor-content">
        <!-- Step 1: Decision Details -->
        <div v-show="anchorStep === 0" class="step-panel">
          <el-form :model="decisionForm" label-width="120px">
            <el-form-item label="Decision Title" required>
              <el-input v-model="decisionForm.title" placeholder="Enter decision title" size="large" />
            </el-form-item>

            <el-form-item label="Decision Type" required>
              <el-select v-model="decisionForm.type" placeholder="Select decision type" style="width: 100%">
                <el-option label="Policy Change" value="policy" />
                <el-option label="Approval" value="approval" />
                <el-option label="Rejection" value="rejection" />
                <el-option label="Escalation" value="escalation" />
              </el-select>
            </el-form-item>

            <el-form-item label="Decision Description" required>
              <el-input
                  v-model="decisionForm.description"
                  type="textarea"
                  :rows="3"
                  placeholder="Detailed description of the decision..."
              />
            </el-form-item>

            <el-form-item label="Decision Makers">
              <el-select
                  v-model="decisionForm.makers"
                  multiple
                  filterable
                  allow-create
                  placeholder="Select or enter decision makers"
                  style="width: 100%"
              >
                <el-option label="John Smith (CEO)" value="john.smith@ibms.com" />
                <el-option label="Sarah Lee (CTO)" value="sarah.lee@ibms.com" />
                <el-option label="Mike Chen (COO)" value="mike.chen@ibms.com" />
                <el-option label="Anna Zhang (Legal)" value="anna.zhang@ibms.com" />
              </el-select>
            </el-form-item>

            <el-form-item label="Effective Date">
              <el-date-picker
                  v-model="decisionForm.effectiveDate"
                  type="datetime"
                  placeholder="Select effective date"
                  style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="Supporting Documents">
              <div class="upload-area-small" @click="triggerDocUpload">
                <el-icon><Upload /></el-icon>
                <span>Click to upload supporting documents</span>
                <input ref="docInputRef" type="file" multiple style="display: none" @change="handleDocsSelect" />
              </div>
              <div v-if="supportingDocs.length > 0" class="docs-list">
                <div v-for="(doc, idx) in supportingDocs" :key="idx" class="doc-item">
                  <el-icon><Document /></el-icon>
                  <span>{{ doc.name }}</span>
                  <el-button link type="danger" @click="removeDoc(idx)">Remove</el-button>
                </div>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: Generate Hash -->
        <div v-show="anchorStep === 1" class="step-panel">
          <div class="decision-preview">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Decision Title">{{ decisionForm.title || 'Not provided' }}</el-descriptions-item>
              <el-descriptions-item label="Decision Type">{{ formatDecisionType(decisionForm.type) }}</el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">{{ decisionForm.description || 'Not provided' }}</el-descriptions-item>
              <el-descriptions-item label="Decision Makers">{{ decisionForm.makers.join(', ') || 'None' }}</el-descriptions-item>
              <el-descriptions-item label="Effective Date">{{ decisionForm.effectiveDate ? new Date(decisionForm.effectiveDate).toLocaleString() : 'Not specified' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="hash-generator">
            <div class="hash-label">SHA-256 Hash of Decision Data</div>
            <div class="hash-value">
              <code>{{ generatedHash || 'Click "Generate Hash" to compute' }}</code>
            </div>
            <el-button type="primary" @click="generateDecisionHash" :loading="isGeneratingHash">
              <el-icon><DataAnalysis /></el-icon>
              Generate Decision Hash
            </el-button>
          </div>

          <div class="hash-info">
            <el-alert
                title="What is being hashed?"
                type="info"
                description="The hash is computed from the decision title, description, type, makers, and effective date. This creates a unique fingerprint that represents the decision."
                show-icon
                :closable="false"
            />
          </div>
        </div>

        <!-- Step 3: Confirm & Anchor -->
        <div v-show="anchorStep === 2" class="step-panel">
          <div class="confirm-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Decision Hash" :span="2">
                <code class="hash-code">{{ generatedHash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Decision Type">{{ formatDecisionType(decisionForm.type) }}</el-descriptions-item>
              <el-descriptions-item label="Decision Title">{{ decisionForm.title }}</el-descriptions-item>
              <el-descriptions-item label="Number of Makers">{{ decisionForm.makers.length }}</el-descriptions-item>
              <el-descriptions-item label="Effective Date">{{ decisionForm.effectiveDate ? new Date(decisionForm.effectiveDate).toLocaleString() : 'Immediate' }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="anchor-params">
            <el-form label-width="120px">
              <el-form-item label="Network">
                <el-select v-model="anchorParams.network" style="width: 100%">
                  <el-option label="Ethereum Mainnet" value="ethereum" />
                  <el-option label="Polygon" value="polygon" />
                  <el-option label="Binance Smart Chain" value="bsc" />
                </el-select>
              </el-form-item>
              <el-form-item label="Gas Limit">
                <el-input-number v-model="anchorParams.gasLimit" :min="50000" :max="500000" :step="10000" />
              </el-form-item>
              <el-form-item label="Include Metadata">
                <el-switch v-model="anchorParams.includeMetadata" />
                <span class="form-hint">Store decision metadata on-chain</span>
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
        <el-button v-if="anchorStep === 2" type="success" @click="anchorDecision" :loading="isAnchoring">
          <el-icon><Link /></el-icon>
          Anchor to Blockchain
        </el-button>
        <el-button @click="anchorDialog.visible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Decision Details Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.decision?.title" width="700px">
      <div v-if="detailDialog.decision" class="decision-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Decision ID">{{ detailDialog.decision.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ formatDecisionType(detailDialog.decision.type) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.decision.status)">{{ detailDialog.decision.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Decision Makers" :span="2">
            {{ detailDialog.decision.makers?.join(', ') || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="Effective Date" :span="2">
            {{ detailDialog.decision.effectiveDate || 'Immediate' }}
          </el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">
            {{ detailDialog.decision.description }}
          </el-descriptions-item>
          <el-descriptions-item label="SHA-256 Hash" :span="2">
            <code class="hash-code">{{ detailDialog.decision.hash }}</code>
            <el-button link size="small" @click="copyHash(detailDialog.decision.hash)">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Transaction Hash" :span="2" v-if="detailDialog.decision.txHash">
            <code class="tx-hash">{{ detailDialog.decision.txHash }}</code>
            <el-button link size="small" @click="viewOnExplorer(detailDialog.decision.txHash)">View on Explorer</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Block Number">{{ detailDialog.decision.blockNumber || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Block Hash">{{ detailDialog.decision.blockHash || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Network">{{ detailDialog.decision.network }}</el-descriptions-item>
          <el-descriptions-item label="Anchored At">{{ detailDialog.decision.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Anchored By">{{ detailDialog.decision.anchoredBy }}</el-descriptions-item>
        </el-descriptions>

        <div class="supporting-docs" v-if="detailDialog.decision.documents?.length">
          <h4>Supporting Documents</h4>
          <div class="docs-list">
            <div v-for="doc in detailDialog.decision.documents" :key="doc.name" class="doc-item">
              <el-icon><Document /></el-icon>
              <span>{{ doc.name }}</span>
              <el-button link size="small" @click="downloadDocument(doc)">Download</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Verification Dialog -->
    <el-dialog v-model="verifyDialog.visible" title="Verify Decision on Blockchain" width="550px">
      <div class="verify-content">
        <div class="verify-area" @click="triggerVerifyInput">
          <el-icon class="upload-icon"><Search /></el-icon>
          <div class="upload-text">Enter Decision ID or Transaction Hash to verify</div>
          <el-input
              v-model="verifyQuery"
              placeholder="Decision ID (e.g., DEC-001) or Transaction Hash"
              style="margin-top: 16px"
          />
          <input ref="verifyFileInputRef" type="text" style="display: none" />
        </div>

        <el-button type="primary" @click="performVerification" :loading="isVerifying" style="margin-top: 16px; width: 100%">
          Verify on Blockchain
        </el-button>

        <div v-if="verificationResult" class="verification-result" :class="verificationResult.isValid ? 'valid' : 'invalid'">
          <div class="result-icon">
            <el-icon v-if="verificationResult.isValid"><CircleCheck /></el-icon>
            <el-icon v-else><CircleClose /></el-icon>
          </div>
          <div class="result-content">
            <h4>{{ verificationResult.isValid ? 'Decision Verified!' : 'Verification Failed' }}</h4>
            <p>{{ verificationResult.message }}</p>
            <div v-if="verificationResult.details" class="result-details">
              <div>Decision ID: {{ verificationResult.details.decisionId }}</div>
              <div>On-chain Hash: <code>{{ verificationResult.details.onChainHash }}</code></div>
              <div>Block: {{ verificationResult.details.blockNumber }}</div>
              <div>Timestamp: {{ verificationResult.details.timestamp }}</div>
              <div>Status: {{ verificationResult.details.status }}</div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Success Dialog -->
    <el-dialog v-model="successDialog.visible" title="Decision Anchored Successfully" width="450px">
      <div class="success-content">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <h3>Decision Successfully Anchored</h3>
        <p>The decision has been permanently recorded on the blockchain.</p>
        <div class="success-info">
          <div><strong>Decision ID:</strong> {{ lastAnchorResult?.decisionId }}</div>
          <div><strong>Transaction Hash:</strong> <code>{{ lastAnchorResult?.txHash }}</code></div>
          <div><strong>Block Number:</strong> {{ lastAnchorResult?.blockNumber }}</div>
          <div><strong>Network:</strong> {{ lastAnchorResult?.network }}</div>
        </div>
        <div class="success-actions">
          <el-button type="primary" @click="viewOnExplorer(lastAnchorResult?.txHash)">View on Explorer</el-button>
          <el-button @click="downloadDecisionProof">Download Proof</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Link,
  Search,
  Document,
  CircleCheck,
  Clock,
  Connection,
  CopyDocument,
  Upload,
  DataAnalysis,
  Loading,
  CircleClose,
  RefreshLeft,
  Plus
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to blockchain...',
  'Loading decision registry...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface DecisionAnchor {
  id: string
  title: string
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
  makers: string[]
  effectiveDate: string | null
  documents?: Array<{ name: string; size: string }>
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalDecisions: 89,
  confirmedDecisions: 84,
  pendingDecisions: 3,
  networkStatus: 'Ethereum'
})

const blockchainStatus = ref('connected')
const networkName = ref('Ethereum Mainnet')
const blockHeight = ref('18,234,567')
const gasPrice = ref('28')
const lastBlockTime = ref('12s ago')

const decisions = ref<DecisionAnchor[]>([
  {
    id: 'DEC-001',
    title: 'AI Model Approval - Energy Optimization v2',
    description: 'Approval to deploy the Energy Optimization AI model v2.0 to production environment',
    type: 'approval',
    hash: '0x3a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
    blockNumber: 18234567,
    blockHash: '0x9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8',
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-10 14:30:00',
    anchoredBy: 'john.smith@ibms.com',
    makers: ['john.smith@ibms.com', 'sarah.lee@ibms.com'],
    effectiveDate: '2024-06-15',
    documents: [{ name: 'Model_Validation_Report.pdf', size: '2.4 MB' }]
  },
  {
    id: 'DEC-002',
    title: 'Budget Approval - AI Infrastructure Upgrade',
    description: 'Approval of $500,000 budget for AI compute infrastructure upgrade',
    type: 'approval',
    hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
    blockNumber: 18234123,
    blockHash: '0x8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7',
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-08 09:15:00',
    anchoredBy: 'mike.chen@ibms.com',
    makers: ['mike.chen@ibms.com', 'john.smith@ibms.com'],
    effectiveDate: '2024-07-01',
    documents: [{ name: 'Budget_Proposal.pdf', size: '1.2 MB' }]
  },
  {
    id: 'DEC-003',
    title: 'Policy Change - Data Retention',
    description: 'Update data retention policy from 90 days to 180 days for audit logs',
    type: 'policy',
    hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    txHash: null,
    blockNumber: null,
    blockHash: null,
    network: 'Polygon',
    status: 'pending',
    timestamp: '2024-06-12 11:20:00',
    anchoredBy: 'anna.zhang@ibms.com',
    makers: ['anna.zhang@ibms.com', 'sarah.lee@ibms.com'],
    effectiveDate: '2024-06-20',
    documents: []
  },
  {
    id: 'DEC-004',
    title: 'Vendor Contract Rejection',
    description: 'Rejection of vendor proposal for cloud services due to non-compliance',
    type: 'rejection',
    hash: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5',
    txHash: '0x9c8b7a6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8c',
    blockNumber: 18234890,
    blockHash: '0x7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6',
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-05 16:45:00',
    anchoredBy: 'john.smith@ibms.com',
    makers: ['john.smith@ibms.com', 'mike.chen@ibms.com'],
    effectiveDate: '2024-06-05',
    documents: []
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
  decision: null as DecisionAnchor | null
})

const verifyDialog = reactive({
  visible: false
})

const successDialog = reactive({
  visible: false
})

const anchorStep = ref(0)
const generatedHash = ref('')
const isGeneratingHash = ref(false)
const isAnchoring = ref(false)
const isVerifying = ref(false)
const verifyQuery = ref('')
const verificationResult = ref<any>(null)
const lastAnchorResult = ref<any>(null)
const supportingDocs = ref<File[]>([])

const docInputRef = ref<HTMLInputElement | null>(null)
const verifyFileInputRef = ref<HTMLInputElement | null>(null)

const decisionForm = reactive({
  title: '',
  description: '',
  type: '',
  makers: [] as string[],
  effectiveDate: null as Date | null
})

const anchorParams = reactive({
  network: 'ethereum',
  gasLimit: 100000,
  includeMetadata: true
})

// ==================== 计算属性 ====================
const filteredDecisions = computed(() => {
  let filtered = [...decisions.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(d =>
        d.id.toLowerCase().includes(searchLower) ||
        d.title.toLowerCase().includes(searchLower) ||
        d.hash.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(d => d.status === filters.status)
  }

  if (filters.type) {
    filtered = filtered.filter(d => d.type === filters.type)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(d => {
      const date = new Date(d.timestamp)
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
    return decisionForm.title.trim() !== '' &&
        decisionForm.description.trim() !== '' &&
        decisionForm.type !== ''
  }
  if (anchorStep.value === 1) {
    return generatedHash.value !== ''
  }
  return true
})

// ==================== 辅助函数 ====================
const formatDecisionType = (type: string) => {
  const map: Record<string, string> = {
    'policy': 'Policy Change',
    'approval': 'Approval',
    'rejection': 'Rejection',
    'escalation': 'Escalation'
  }
  return map[type] || type
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'warning',
    'confirmed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
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

const triggerDocUpload = () => {
  docInputRef.value?.click()
}

const handleDocsSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) {
    supportingDocs.value.push(...Array.from(input.files))
  }
}

const removeDoc = (index: number) => {
  supportingDocs.value.splice(index, 1)
}

const generateDecisionHash = async () => {
  isGeneratingHash.value = true

  await new Promise(resolve => setTimeout(resolve, 1500))

  // Simulate hash generation from decision data
  const dataToHash = JSON.stringify({
    title: decisionForm.title,
    description: decisionForm.description,
    type: decisionForm.type,
    makers: decisionForm.makers,
    effectiveDate: decisionForm.effectiveDate,
    supportingDocs: supportingDocs.value.map(d => d.name)
  })

  const hash = Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')

  generatedHash.value = `0x${hash}`
  isGeneratingHash.value = false
  ElMessage.success('Decision hash generated successfully')
}

const anchorDecision = async () => {
  isAnchoring.value = true

  await new Promise(resolve => setTimeout(resolve, 3000))

  const txHash = `0x${Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')}`

  const blockNumber = 18235000 + Math.floor(Math.random() * 1000)

  const newDecision: DecisionAnchor = {
    id: `DEC-${String(decisions.value.length + 1).padStart(3, '0')}`,
    title: decisionForm.title,
    description: decisionForm.description,
    type: decisionForm.type,
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
    makers: decisionForm.makers,
    effectiveDate: decisionForm.effectiveDate ? decisionForm.effectiveDate.toISOString().slice(0, 10) : null,
    documents: supportingDocs.value.map(d => ({ name: d.name, size: `${(d.size / 1024).toFixed(1)} KB` }))
  }

  decisions.value.unshift(newDecision)
  stats.totalDecisions++
  stats.pendingDecisions++

  lastAnchorResult.value = {
    decisionId: newDecision.id,
    txHash: txHash,
    blockNumber: blockNumber,
    network: anchorParams.network
  }

  isAnchoring.value = false
  anchorDialog.visible = false
  successDialog.visible = true

  // Simulate confirmation
  setTimeout(() => {
    const index = decisions.value.findIndex(d => d.id === newDecision.id)
    if (index !== -1) {
      decisions.value[index].status = 'confirmed'
      stats.pendingDecisions--
      stats.confirmedDecisions++
    }
  }, 5000)

  // Reset form
  anchorStep.value = 0
  decisionForm.title = ''
  decisionForm.description = ''
  decisionForm.type = ''
  decisionForm.makers = []
  decisionForm.effectiveDate = null
  generatedHash.value = ''
  supportingDocs.value = []
}

const openAnchorDialog = () => {
  anchorStep.value = 0
  decisionForm.title = ''
  decisionForm.description = ''
  decisionForm.type = ''
  decisionForm.makers = []
  decisionForm.effectiveDate = null
  generatedHash.value = ''
  supportingDocs.value = []
  anchorDialog.visible = true
}

const viewDetails = (decision: DecisionAnchor) => {
  detailDialog.decision = decision
  detailDialog.visible = true
}

const verifyAnchor = () => {
  verifyDialog.visible = true
  verifyQuery.value = ''
  verificationResult.value = null
}

const triggerVerifyInput = () => {
  verifyFileInputRef.value?.click()
}

const performVerification = async () => {
  if (!verifyQuery.value.trim()) {
    ElMessage.warning('Please enter a Decision ID or Transaction Hash')
    return
  }

  isVerifying.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  const decision = decisions.value.find(d =>
      d.id === verifyQuery.value || d.txHash === verifyQuery.value
  )

  if (decision && decision.status === 'confirmed') {
    verificationResult.value = {
      isValid: true,
      message: 'Decision verified on blockchain. Hash matches on-chain record.',
      details: {
        decisionId: decision.id,
        onChainHash: decision.hash,
        blockNumber: decision.blockNumber,
        timestamp: decision.timestamp,
        status: decision.status
      }
    }
  } else if (decision && decision.status === 'pending') {
    verificationResult.value = {
      isValid: false,
      message: 'Decision transaction is pending confirmation. Please check again later.',
      details: {
        decisionId: decision.id,
        status: decision.status,
        timestamp: decision.timestamp
      }
    }
  } else {
    verificationResult.value = {
      isValid: false,
      message: 'Decision not found on blockchain or verification failed.',
      details: null
    }
  }

  isVerifying.value = false
}

const verifyDecision = (decision: DecisionAnchor) => {
  verifyDialog.visible = true
  verifyQuery.value = decision.id
  performVerification()
}

const viewOnChainStatus = (decision: DecisionAnchor) => {
  ElMessage.info(`Checking status of decision ${decision.id} on blockchain...`)
}

const downloadDecisionProof = () => {
  const proof = {
    anchoredAt: new Date().toISOString(),
    decisionId: lastAnchorResult.value?.decisionId,
    transactionHash: lastAnchorResult.value?.txHash,
    blockNumber: lastAnchorResult.value?.blockNumber,
    network: lastAnchorResult.value?.network,
    decision: {
      title: decisionForm.title,
      type: decisionForm.type,
      description: decisionForm.description,
      makers: decisionForm.makers,
      hash: generatedHash.value
    }
  }
  const data = JSON.stringify(proof, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `decision-proof-${lastAnchorResult.value?.decisionId}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Decision proof downloaded')
}

const downloadDocument = (doc: any) => {
  ElMessage.success(`Downloading ${doc.name}`)
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
.decision-anchor-page {
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

.upload-area-small {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.upload-area-small:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.docs-list {
  margin-top: 8px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  background: #f5f7fa;
  border-radius: 4px;
  margin-top: 4px;
}

.decision-preview {
  margin-bottom: 24px;
}

.hash-generator {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.hash-label {
  font-weight: 500;
  margin-bottom: 12px;
}

.hash-value {
  background: white;
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

/* Decision Detail */
.decision-detail {
  padding: 8px 0;
}

.supporting-docs {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.supporting-docs h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

/* Verification Dialog */
.verify-content {
  padding: 8px 0;
}

.verify-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 30px 20px;
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

.result-details code {
  font-size: 11px;
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

.success-info code {
  font-size: 11px;
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