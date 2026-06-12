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
  <div v-else class="credential-anchor-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Credential Anchor</h1>
        <p>Anchor verifiable credential hashes to blockchain for tamper-proof verification</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAnchorDialog">
          <el-icon><Link /></el-icon>
          Anchor Credential
        </el-button>
        <el-button @click="verifyAnchor">
          <el-icon><Search /></el-icon>
          Verify Credential
        </el-button>
        <el-button @click="exportRegistry">
          <el-icon><Download /></el-icon>
          Export Registry
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
          placeholder="Search by credential ID, holder, or hash..."
          clearable
          style="width: 280px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All" value="" />
        <el-option label="Confirmed" value="confirmed" />
        <el-option label="Pending" value="pending" />
        <el-option label="Revoked" value="revoked" />
      </el-select>
      <el-select v-model="filters.type" placeholder="Type" clearable style="width: 140px">
        <el-option label="All Types" value="" />
        <el-option label="Employee Identity" value="employee" />
        <el-option label="Equipment Cert" value="equipment" />
        <el-option label="Compliance" value="compliance" />
        <el-option label="Access" value="access" />
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

    <!-- Credential Anchors Table -->
    <div class="anchors-table-wrapper">
      <el-table :data="filteredAnchors" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="credentialId" label="Credential ID" width="140" />
        <el-table-column prop="type" label="Type" width="140">
          <template #default="{ row }">
            <el-tag size="small">{{ formatCredentialType(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="holderDid" label="Holder DID" width="200" show-overflow-tooltip />
        <el-table-column prop="hash" label="Credential Hash" width="280" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="hash-code">{{ row.hash }}</code>
            <el-button link size="small" @click="copyHash(row.hash)">
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="txHash" label="Transaction Hash" width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <code class="tx-hash" v-if="row.txHash">{{ row.txHash }}</code>
            <span v-else class="pending-text">Pending</span>
            <el-button v-if="row.txHash" link size="small" @click="viewOnExplorer(row.txHash)">
              <el-icon><Link /></el-icon>
            </el-button>
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
            <el-button v-if="row.status === 'confirmed'" link type="success" size="small" @click="verifyCredential(row)">
              Verify
            </el-button>
            <el-button v-if="row.status === 'confirmed'" link type="danger" size="small" @click="revokeCredential(row)">
              Revoke
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

    <!-- Anchor Credential Dialog -->
    <el-dialog v-model="anchorDialog.visible" title="Anchor Credential to Blockchain" width="650px" class="anchor-dialog">
      <div class="anchor-steps">
        <el-steps :active="anchorStep" finish-status="success" align-center>
          <el-step title="Credential Info" />
          <el-step title="Generate Hash" />
          <el-step title="Confirm & Anchor" />
        </el-steps>
      </div>

      <div class="anchor-content">
        <!-- Step 1: Credential Info -->
        <div v-show="anchorStep === 0" class="step-panel">
          <el-form :model="credentialForm" label-width="130px">
            <el-form-item label="Credential ID" required>
              <el-input v-model="credentialForm.credentialId" placeholder="Enter credential ID" />
            </el-form-item>

            <el-form-item label="Credential Type" required>
              <el-select v-model="credentialForm.type" placeholder="Select credential type" style="width: 100%">
                <el-option label="Employee Identity" value="employee" />
                <el-option label="Equipment Certification" value="equipment" />
                <el-option label="Compliance Attestation" value="compliance" />
                <el-option label="Access Credential" value="access" />
              </el-select>
            </el-form-item>

            <el-form-item label="Holder DID" required>
              <el-input v-model="credentialForm.holderDid" placeholder="did:example:123456789abcdefghi" />
            </el-form-item>

            <el-form-item label="Issuer DID" required>
              <el-input v-model="credentialForm.issuerDid" placeholder="did:example:issuer.ibms" />
            </el-form-item>

            <el-form-item label="Valid From">
              <el-date-picker
                  v-model="credentialForm.validFrom"
                  type="datetime"
                  placeholder="Select start date"
                  style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="Valid Until">
              <el-date-picker
                  v-model="credentialForm.validUntil"
                  type="datetime"
                  placeholder="Select expiration date"
                  style="width: 100%"
              />
            </el-form-item>

            <el-form-item label="Credential JSON">
              <el-input
                  v-model="credentialForm.credentialJson"
                  type="textarea"
                  :rows="4"
                  placeholder='{"@context": ["https://www.w3.org/2018/credentials/v1"], "type": ["VerifiableCredential"]}'
              />
              <div class="form-hint">Paste the full verifiable credential JSON</div>
            </el-form-item>
          </el-form>
        </div>

        <!-- Step 2: Generate Hash -->
        <div v-show="anchorStep === 1" class="step-panel">
          <div class="credential-preview">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Credential ID">{{ credentialForm.credentialId || 'Not provided' }}</el-descriptions-item>
              <el-descriptions-item label="Type">{{ formatCredentialType(credentialForm.type) }}</el-descriptions-item>
              <el-descriptions-item label="Holder DID">{{ credentialForm.holderDid || 'Not provided' }}</el-descriptions-item>
              <el-descriptions-item label="Issuer DID">{{ credentialForm.issuerDid || 'Not provided' }}</el-descriptions-item>
              <el-descriptions-item label="Valid From">{{ formatDateTime(credentialForm.validFrom) }}</el-descriptions-item>
              <el-descriptions-item label="Valid Until">{{ formatDateTime(credentialForm.validUntil) }}</el-descriptions-item>
            </el-descriptions>
          </div>

          <div class="hash-generator">
            <div class="hash-label">SHA-256 Hash of Credential</div>
            <div class="hash-value">
              <code>{{ generatedHash || 'Click "Generate Hash" to compute' }}</code>
            </div>
            <el-button type="primary" @click="generateCredentialHash" :loading="isGeneratingHash">
              <el-icon><DataAnalysis /></el-icon>
              Generate Credential Hash
            </el-button>
          </div>

          <div class="hash-info">
            <el-alert
                title="What is being hashed?"
                type="info"
                description="The hash is computed from the full credential JSON. This creates a unique fingerprint that represents the credential on the blockchain."
                show-icon
                :closable="false"
            />
          </div>
        </div>

        <!-- Step 3: Confirm & Anchor -->
        <div v-show="anchorStep === 2" class="step-panel">
          <div class="confirm-info">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Credential Hash" :span="2">
                <code class="hash-code">{{ generatedHash }}</code>
              </el-descriptions-item>
              <el-descriptions-item label="Credential ID">{{ credentialForm.credentialId }}</el-descriptions-item>
              <el-descriptions-item label="Type">{{ formatCredentialType(credentialForm.type) }}</el-descriptions-item>
              <el-descriptions-item label="Holder">{{ credentialForm.holderDid }}</el-descriptions-item>
              <el-descriptions-item label="Valid Until">{{ formatDateTime(credentialForm.validUntil) }}</el-descriptions-item>
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
              <el-form-item label="Revocation Registry">
                <el-switch v-model="anchorParams.registerRevocation" />
                <span class="form-hint">Enable revocation support</span>
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
        <el-button v-if="anchorStep === 2" type="success" @click="anchorCredential" :loading="isAnchoring">
          <el-icon><Link /></el-icon>
          Anchor to Blockchain
        </el-button>
        <el-button @click="anchorDialog.visible = false">Cancel</el-button>
      </template>
    </el-dialog>

    <!-- Credential Details Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.anchor?.credentialId" width="700px">
      <div v-if="detailDialog.anchor" class="credential-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Credential ID">{{ detailDialog.anchor.credentialId }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ formatCredentialType(detailDialog.anchor.type) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTagType(detailDialog.anchor.status)">{{ detailDialog.anchor.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Holder DID">{{ detailDialog.anchor.holderDid }}</el-descriptions-item>
          <el-descriptions-item label="Issuer DID">{{ detailDialog.anchor.issuerDid }}</el-descriptions-item>
          <el-descriptions-item label="Valid From">{{ detailDialog.anchor.validFrom || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Valid Until">{{ detailDialog.anchor.validUntil || 'Never' }}</el-descriptions-item>
          <el-descriptions-item label="Credential Hash" :span="2">
            <code class="hash-code">{{ detailDialog.anchor.hash }}</code>
            <el-button link size="small" @click="copyHash(detailDialog.anchor.hash)">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Transaction Hash" :span="2" v-if="detailDialog.anchor.txHash">
            <code class="tx-hash">{{ detailDialog.anchor.txHash }}</code>
            <el-button link size="small" @click="viewOnExplorer(detailDialog.anchor.txHash)">View on Explorer</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Block Number">{{ detailDialog.anchor.blockNumber || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Network">{{ detailDialog.anchor.network }}</el-descriptions-item>
          <el-descriptions-item label="Anchored At">{{ detailDialog.anchor.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Anchored By">{{ detailDialog.anchor.anchoredBy }}</el-descriptions-item>
          <el-descriptions-item label="Revocation Status" v-if="detailDialog.anchor.revoked">
            <el-tag type="danger">Revoked on {{ detailDialog.anchor.revokedDate }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>

    <!-- Verification Dialog -->
    <el-dialog v-model="verifyDialog.visible" title="Verify Credential" width="550px">
      <div class="verify-content">
        <div class="verify-area" @click="triggerVerifyInput">
          <el-icon class="upload-icon"><Search /></el-icon>
          <div class="upload-text">Enter Credential ID or Transaction Hash to verify</div>
          <el-input
              v-model="verifyQuery"
              placeholder="Credential ID (e.g., VC-001) or Transaction Hash"
              style="margin-top: 16px"
          />
        </div>

        <div class="verify-option">
          <el-radio-group v-model="verifyOption">
            <el-radio value="credential">Verify by Credential JSON</el-radio>
            <el-radio value="hash">Verify by Hash Only</el-radio>
          </el-radio-group>
        </div>

        <div v-if="verifyOption === 'credential'" class="verify-json-area">
          <el-input
              v-model="verifyJson"
              type="textarea"
              :rows="4"
              placeholder="Paste credential JSON to verify..."
          />
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
            <h4>{{ verificationResult.isValid ? 'Credential Verified!' : 'Verification Failed' }}</h4>
            <p>{{ verificationResult.message }}</p>
            <div v-if="verificationResult.details" class="result-details">
              <div>Credential ID: {{ verificationResult.details.credentialId }}</div>
              <div>Status: {{ verificationResult.details.status }}</div>
              <div>Holder: {{ verificationResult.details.holderDid }}</div>
              <div>Block: {{ verificationResult.details.blockNumber }}</div>
              <div>Anchored At: {{ verificationResult.details.timestamp }}</div>
              <div v-if="verificationResult.details.revoked" class="revoked-warning">
                ⚠️ This credential has been revoked!
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- Revoke Dialog -->
    <el-dialog v-model="revokeDialog.visible" title="Revoke Credential" width="500px">
      <div class="revoke-content">
        <el-alert
            title="Warning: This action is irreversible"
            type="warning"
            description="Revoking a credential will mark it as invalid on the blockchain. The holder will no longer be able to use this credential."
            show-icon
            :closable="false"
        />

        <div class="credential-info">
          <p><strong>Credential ID:</strong> {{ revokeDialog.credential?.credentialId }}</p>
          <p><strong>Holder:</strong> {{ revokeDialog.credential?.holderDid }}</p>
        </div>

        <el-form :model="revokeForm" label-width="100px">
          <el-form-item label="Revocation Reason">
            <el-select v-model="revokeForm.reason" style="width: 100%">
              <el-option label="Credential Compromised" value="compromised" />
              <el-option label="Holder No Longer Authorized" value="unauthorized" />
              <el-option label="Information Incorrect" value="incorrect" />
              <el-option label="Credential Expired" value="expired" />
            </el-select>
          </el-form-item>
          <el-form-item label="Notify Holder">
            <el-switch v-model="revokeForm.notify" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="revokeDialog.visible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmRevoke" :loading="isRevoking">
          Revoke Credential
        </el-button>
      </template>
    </el-dialog>

    <!-- Success Dialog -->
    <el-dialog v-model="successDialog.visible" title="Credential Anchored Successfully" width="500px">
      <div class="success-content">
        <el-icon class="success-icon"><CircleCheck /></el-icon>
        <h3>Credential Successfully Anchored</h3>
        <p>The credential hash has been permanently recorded on the blockchain.</p>
        <div class="success-info">
          <div><strong>Credential ID:</strong> {{ lastAnchorResult?.credentialId }}</div>
          <div><strong>Transaction Hash:</strong> <code>{{ lastAnchorResult?.txHash }}</code></div>
          <div><strong>Block Number:</strong> {{ lastAnchorResult?.blockNumber }}</div>
          <div><strong>Network:</strong> {{ lastAnchorResult?.network }}</div>
        </div>
        <div class="success-actions">
          <el-button type="primary" @click="viewOnExplorer(lastAnchorResult?.txHash)">View on Explorer</el-button>
          <el-button @click="downloadCredentialProof">Download Proof</el-button>
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
  DataAnalysis,
  Loading,
  CircleClose,
  RefreshLeft,
  Download
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)

const loadingMessages = [
  'Preparing...',
  'Connecting to blockchain...',
  'Loading credential registry...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface CredentialAnchor {
  id: string
  credentialId: string
  type: string
  holderDid: string
  issuerDid: string
  hash: string
  txHash: string | null
  blockNumber: number | null
  network: string
  status: 'pending' | 'confirmed' | 'revoked'
  timestamp: string
  anchoredBy: string
  validFrom?: string
  validUntil?: string
  revoked?: boolean
  revokedDate?: string
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

const credentialAnchors = ref<CredentialAnchor[]>([
  {
    id: 'CA-001',
    credentialId: 'VC-EMP-001',
    type: 'employee',
    holderDid: 'did:example:john.smith',
    issuerDid: 'did:example:issuer.ibms',
    hash: '0x3a2b1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b',
    txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
    blockNumber: 18234567,
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-10 14:30:00',
    anchoredBy: 'admin@ibms.com',
    validFrom: '2024-06-10',
    validUntil: '2025-06-10'
  },
  {
    id: 'CA-002',
    credentialId: 'VC-EQP-001',
    type: 'equipment',
    holderDid: 'did:example:mike.chen',
    issuerDid: 'did:example:issuer.ibms',
    hash: '0x2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
    blockNumber: 18234123,
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-08 09:15:00',
    anchoredBy: 'admin@ibms.com',
    validFrom: '2024-06-08',
    validUntil: '2025-06-08'
  },
  {
    id: 'CA-003',
    credentialId: 'VC-COM-001',
    type: 'compliance',
    holderDid: 'did:example:audit.firm',
    issuerDid: 'did:example:issuer.ibms',
    hash: '0x3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    txHash: null,
    blockNumber: null,
    network: 'Polygon',
    status: 'pending',
    timestamp: '2024-06-12 11:20:00',
    anchoredBy: 'compliance@ibms.com'
  },
  {
    id: 'CA-004',
    credentialId: 'VC-ACC-001',
    type: 'access',
    holderDid: 'did:example:sarah.lee',
    issuerDid: 'did:example:issuer.ibms',
    hash: '0x4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5',
    txHash: '0x9c8b7a6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8c',
    blockNumber: 18234890,
    network: 'Ethereum',
    status: 'confirmed',
    timestamp: '2024-06-05 16:45:00',
    anchoredBy: 'security@ibms.com',
    validFrom: '2024-06-05',
    validUntil: '2024-12-05'
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
  anchor: null as CredentialAnchor | null
})

const verifyDialog = reactive({
  visible: false
})

const revokeDialog = reactive({
  visible: false,
  credential: null as CredentialAnchor | null
})

const successDialog = reactive({
  visible: false
})

const anchorStep = ref(0)
const generatedHash = ref('')
const isGeneratingHash = ref(false)
const isAnchoring = ref(false)
const isVerifying = ref(false)
const isRevoking = ref(false)
const verifyQuery = ref('')
const verifyOption = ref('credential')
const verifyJson = ref('')
const verificationResult = ref<any>(null)
const lastAnchorResult = ref<any>(null)

const credentialForm = reactive({
  credentialId: '',
  type: '',
  holderDid: '',
  issuerDid: '',
  validFrom: null as Date | null,
  validUntil: null as Date | null,
  credentialJson: ''
})

const revokeForm = reactive({
  reason: '',
  notify: true
})

const anchorParams = reactive({
  network: 'ethereum',
  gasLimit: 100000,
  registerRevocation: true
})

// ==================== 计算属性 ====================
const filteredAnchors = computed(() => {
  let filtered = [...credentialAnchors.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(a =>
        a.credentialId.toLowerCase().includes(searchLower) ||
        a.holderDid.toLowerCase().includes(searchLower) ||
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
    return credentialForm.credentialId.trim() !== '' &&
        credentialForm.type !== '' &&
        credentialForm.holderDid.trim() !== '' &&
        credentialForm.credentialJson.trim() !== ''
  }
  if (anchorStep.value === 1) {
    return generatedHash.value !== ''
  }
  return true
})

// ==================== 辅助函数 ====================
const formatCredentialType = (type: string) => {
  const map: Record<string, string> = {
    'employee': 'Employee Identity',
    'equipment': 'Equipment Certification',
    'compliance': 'Compliance Attestation',
    'access': 'Access Credential'
  }
  return map[type] || type
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'warning',
    'confirmed': 'success',
    'revoked': 'danger'
  }
  return map[status] || 'info'
}

const formatDateTime = (date: Date | null) => {
  if (!date) return 'Not specified'
  return new Date(date).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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

const generateCredentialHash = async () => {
  if (!credentialForm.credentialJson.trim()) {
    ElMessage.warning('Please enter credential JSON')
    return
  }

  isGeneratingHash.value = true

  await new Promise(resolve => setTimeout(resolve, 1500))

  const hash = Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')

  generatedHash.value = `0x${hash}`
  isGeneratingHash.value = false
  ElMessage.success('Credential hash generated successfully')
}

const anchorCredential = async () => {
  isAnchoring.value = true

  await new Promise(resolve => setTimeout(resolve, 3000))

  const txHash = `0x${Array.from({ length: 64 }, () =>
      '0123456789abcdef'[Math.floor(Math.random() * 16)]
  ).join('')}`

  const blockNumber = 18235000 + Math.floor(Math.random() * 1000)

  const newAnchor: CredentialAnchor = {
    id: `CA-${String(credentialAnchors.value.length + 1).padStart(3, '0')}`,
    credentialId: credentialForm.credentialId,
    type: credentialForm.type,
    holderDid: credentialForm.holderDid,
    issuerDid: credentialForm.issuerDid,
    hash: generatedHash.value,
    txHash: txHash,
    blockNumber: blockNumber,
    network: anchorParams.network,
    status: 'pending',
    timestamp: new Date().toLocaleString(),
    anchoredBy: 'admin@ibms.com',
    validFrom: credentialForm.validFrom ? credentialForm.validFrom.toISOString().slice(0, 10) : undefined,
    validUntil: credentialForm.validUntil ? credentialForm.validUntil.toISOString().slice(0, 10) : undefined
  }

  credentialAnchors.value.unshift(newAnchor)
  stats.totalAnchors++
  stats.pendingAnchors++

  lastAnchorResult.value = {
    credentialId: newAnchor.credentialId,
    txHash: txHash,
    blockNumber: blockNumber,
    network: anchorParams.network
  }

  isAnchoring.value = false
  anchorDialog.visible = false
  successDialog.visible = true

  // Simulate confirmation
  setTimeout(() => {
    const index = credentialAnchors.value.findIndex(a => a.id === newAnchor.id)
    if (index !== -1) {
      credentialAnchors.value[index].status = 'confirmed'
      stats.pendingAnchors--
      stats.confirmedAnchors++
    }
  }, 5000)

  // Reset form
  anchorStep.value = 0
  credentialForm.credentialId = ''
  credentialForm.type = ''
  credentialForm.holderDid = ''
  credentialForm.issuerDid = ''
  credentialForm.validFrom = null
  credentialForm.validUntil = null
  credentialForm.credentialJson = ''
  generatedHash.value = ''
}

const openAnchorDialog = () => {
  anchorStep.value = 0
  credentialForm.credentialId = ''
  credentialForm.type = ''
  credentialForm.holderDid = ''
  credentialForm.issuerDid = ''
  credentialForm.validFrom = null
  credentialForm.validUntil = null
  credentialForm.credentialJson = ''
  generatedHash.value = ''
  anchorDialog.visible = true
}

const viewDetails = (anchor: CredentialAnchor) => {
  detailDialog.anchor = anchor
  detailDialog.visible = true
}

const verifyAnchor = () => {
  verifyDialog.visible = true
  verifyQuery.value = ''
  verifyJson.value = ''
  verificationResult.value = null
}

const triggerVerifyInput = () => {
  // Focus on input
}

const performVerification = async () => {
  if (verifyOption.value === 'credential') {
    if (!verifyJson.value.trim()) {
      ElMessage.warning('Please enter credential JSON to verify')
      return
    }
  } else {
    if (!verifyQuery.value.trim()) {
      ElMessage.warning('Please enter Credential ID or Transaction Hash')
      return
    }
  }

  isVerifying.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  let anchor: CredentialAnchor | undefined

  if (verifyOption.value === 'credential') {
    // Simulate finding by JSON content
    anchor = credentialAnchors.value.find(a => a.status === 'confirmed')
  } else {
    anchor = credentialAnchors.value.find(a =>
        a.credentialId === verifyQuery.value || a.txHash === verifyQuery.value
    )
  }

  if (anchor && anchor.status === 'confirmed') {
    verificationResult.value = {
      isValid: true,
      message: 'Credential verified on blockchain. Hash matches on-chain record.',
      details: {
        credentialId: anchor.credentialId,
        status: anchor.status,
        holderDid: anchor.holderDid,
        blockNumber: anchor.blockNumber,
        timestamp: anchor.timestamp,
        revoked: anchor.revoked || false
      }
    }
  } else if (anchor && anchor.status === 'pending') {
    verificationResult.value = {
      isValid: false,
      message: 'Credential transaction is pending confirmation.',
      details: {
        credentialId: anchor.credentialId,
        status: anchor.status
      }
    }
  } else {
    verificationResult.value = {
      isValid: false,
      message: 'Credential not found on blockchain or verification failed.',
      details: null
    }
  }

  isVerifying.value = false
}

const verifyCredential = (anchor: CredentialAnchor) => {
  verifyDialog.visible = true
  verifyQuery.value = anchor.credentialId
  verifyOption.value = 'hash'
  performVerification()
}

const revokeCredential = (anchor: CredentialAnchor) => {
  revokeDialog.credential = anchor
  revokeForm.reason = ''
  revokeForm.notify = true
  revokeDialog.visible = true
}

const confirmRevoke = async () => {
  if (!revokeDialog.credential) return

  isRevoking.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  const index = credentialAnchors.value.findIndex(a => a.id === revokeDialog.credential!.id)
  if (index !== -1) {
    credentialAnchors.value[index].status = 'revoked'
    credentialAnchors.value[index].revoked = true
    credentialAnchors.value[index].revokedDate = new Date().toLocaleString()
    stats.confirmedAnchors--
  }

  if (revokeForm.notify) {
    ElMessage.success(`Revocation notification sent to ${revokeDialog.credential.holderDid}`)
  }

  isRevoking.value = false
  revokeDialog.visible = false
  ElMessage.success(`Credential ${revokeDialog.credential.credentialId} has been revoked`)
}

const downloadCredentialProof = () => {
  const proof = {
    anchoredAt: new Date().toISOString(),
    credentialId: lastAnchorResult.value?.credentialId,
    transactionHash: lastAnchorResult.value?.txHash,
    blockNumber: lastAnchorResult.value?.blockNumber,
    network: lastAnchorResult.value?.network,
    hash: generatedHash.value
  }
  const data = JSON.stringify(proof, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `credential-proof-${lastAnchorResult.value?.credentialId}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Credential proof downloaded')
}

const exportRegistry = () => {
  const registry = {
    generatedAt: new Date().toISOString(),
    totalAnchors: stats.totalAnchors,
    confirmedAnchors: stats.confirmedAnchors,
    anchors: credentialAnchors.value
  }
  const data = JSON.stringify(registry, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `credential-registry-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Credential registry exported')
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
.credential-anchor-page {
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

.credential-preview {
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

/* Credential Detail */
.credential-detail {
  padding: 8px 0;
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

.verify-option {
  margin-top: 20px;
  text-align: center;
}

.verify-json-area {
  margin-top: 16px;
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

.revoked-warning {
  margin-top: 8px;
  color: #f56c6c;
  font-weight: 500;
}

/* Revoke Dialog */
.revoke-content {
  padding: 8px 0;
}

.credential-info {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  margin: 16px 0;
}

.credential-info p {
  margin: 4px 0;
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