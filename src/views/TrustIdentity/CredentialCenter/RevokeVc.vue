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
        <div class="loading-tip">Trust & Identity - Revoke Verifiable Credential</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="revoke-vc-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Revoke Verifiable Credential</h1>
        <p>Revoke issued credentials and manage revocation registry</p>
      </div>
      <div class="header-actions">
        <el-button @click="viewRevocationRegistry">
          <el-icon><List /></el-icon>
          Revocation Registry
        </el-button>
        <el-button type="danger" @click="bulkRevoke" :disabled="selectedCredentials.length === 0">
          <el-icon><Delete /></el-icon>
          Bulk Revoke ({{ selectedCredentials.length }})
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
            <div class="stat-value">{{ stats.totalCredentials }}</div>
            <div class="stat-label">Total Issued</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeCredentials }}</div>
            <div class="stat-label">Active</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><CircleClose /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.revokedCredentials }}</div>
            <div class="stat-label">Revoked</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.revokedThisMonth }}</div>
            <div class="stat-label">Revoked This Month</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Search Section -->
    <div class="search-card">
      <div class="card-header">
        <h3>Find Credential</h3>
        <el-tag type="info" size="small">Enter credential ID or recipient information</el-tag>
      </div>
      <div class="search-area">
        <el-input
            v-model="searchQuery"
            placeholder="Search by Credential ID, Recipient DID, or Recipient Name..."
            size="large"
            clearable
            style="flex: 1"
            :prefix-icon="Search"
            @keyup.enter="searchCredential"
        />
        <el-button type="primary" size="large" @click="searchCredential">
          <el-icon><Search /></el-icon>
          Search
        </el-button>
        <el-button size="large" @click="resetSearch">
          <el-icon><RefreshLeft /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- Search Results -->
    <div class="results-card" v-if="searchPerformed">
      <div class="card-header">
        <h3>Search Results</h3>
        <span class="result-count">{{ searchResults.length }} credential(s) found</span>
      </div>

      <div v-if="searchResults.length === 0" class="no-results">
        <el-empty description="No credentials found matching your search" :image-size="80" />
      </div>

      <div v-else class="results-list">
        <div
            v-for="credential in searchResults"
            :key="credential.id"
            class="credential-card"
            :class="{ selected: selectedCredentials.includes(credential.id) }"
        >
          <div class="credential-select">
            <el-checkbox
                v-model="selectedCredentials"
                :value="credential.id"
                :disabled="credential.status === 'revoked'"
            />
          </div>
          <div class="credential-info">
            <div class="credential-header">
              <span class="credential-id">{{ credential.id }}</span>
              <el-tag :type="credential.status === 'active' ? 'success' : 'danger'" size="small">
                {{ credential.status === 'active' ? 'Active' : 'Revoked' }}
              </el-tag>
            </div>
            <div class="credential-details">
              <div class="detail-row">
                <el-icon><User /></el-icon>
                <span>{{ credential.recipientName }}</span>
                <el-icon><Message /></el-icon>
                <span>{{ credential.recipientDid }}</span>
              </div>
              <div class="detail-row">
                <el-icon><Document /></el-icon>
                <span>{{ credential.type }}</span>
                <el-icon><Calendar /></el-icon>
                <span>Issued: {{ credential.issuedDate }}</span>
                <span v-if="credential.expiryDate">Expires: {{ credential.expiryDate }}</span>
              </div>
            </div>
          </div>
          <div class="credential-actions">
            <el-button
                v-if="credential.status === 'active'"
                type="danger"
                size="small"
                @click="openRevokeDialog(credential)"
            >
              <el-icon><CircleClose /></el-icon>
              Revoke
            </el-button>
            <el-button
                v-else
                type="info"
                size="small"
                disabled
            >
              Revoked
            </el-button>
            <el-button size="small" @click="viewCredentialDetails(credential)">
              <el-icon><View /></el-icon>
              Details
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Active Credentials Table -->
    <div class="credentials-table-wrapper">
      <div class="table-header">
        <h3>Active Credentials</h3>
        <div class="table-filters">
          <el-select v-model="tableFilter.type" placeholder="Filter by type" clearable size="small" style="width: 140px">
            <el-option label="All Types" value="" />
            <el-option label="Employee Identity" value="Employee Identity" />
            <el-option label="Equipment Certification" value="Equipment Certification" />
            <el-option label="Compliance Attestation" value="Compliance Attestation" />
            <el-option label="Access Credential" value="Access Credential" />
          </el-select>
          <el-input
              v-model="tableFilter.search"
              placeholder="Search..."
              clearable
              size="small"
              style="width: 180px"
              :prefix-icon="Search"
          />
        </div>
      </div>
      <el-table :data="filteredCredentials" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column type="selection" width="55" :selectable="(row) => row.status === 'active'" />
        <el-table-column prop="id" label="Credential ID" width="180" />
        <el-table-column prop="type" label="Type" width="160" />
        <el-table-column prop="recipientName" label="Recipient" min-width="150" />
        <el-table-column prop="recipientDid" label="Recipient DID" width="200" show-overflow-tooltip />
        <el-table-column prop="issuedDate" label="Issued Date" width="110" />
        <el-table-column prop="expiryDate" label="Expiry Date" width="110">
          <template #default="{ row }">
            <span :class="{ 'expiring-soon': isExpiringSoon(row.expiryDate) }">
              {{ row.expiryDate || 'Never' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">
              {{ row.status === 'active' ? 'Active' : 'Revoked' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
                v-if="row.status === 'active'"
                link
                type="danger"
                size="small"
                @click="openRevokeDialog(row)"
            >
              Revoke
            </el-button>
            <el-button link type="primary" size="small" @click="viewCredentialDetails(row)">
              Details
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Revocation History -->
    <div class="history-card">
      <div class="card-header">
        <h3>Revocation History</h3>
        <el-button size="small" @click="refreshHistory">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
      <el-table :data="revocationHistory" stripe>
        <el-table-column prop="credentialId" label="Credential ID" width="200" />
        <el-table-column prop="credentialType" label="Type" width="160" />
        <el-table-column prop="recipient" label="Recipient" min-width="150" />
        <el-table-column prop="revokedDate" label="Revoked Date" width="160" />
        <el-table-column prop="reason" label="Reason" min-width="200" />
        <el-table-column prop="revokedBy" label="Revoked By" width="140" />
        <el-table-column label="Status" width="100">
          <template #default>
            <el-tag type="danger" size="small">Revoked</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="revocationHistory.length === 0" class="no-history">
        <el-empty description="No revocation history" :image-size="60" />
      </div>
    </div>

    <!-- Revoke Dialog -->
    <el-dialog v-model="revokeDialog.visible" title="Revoke Credential" width="550px">
      <div v-if="revokeDialog.credential" class="revoke-dialog-content">
        <el-alert
            title="Warning: This action cannot be undone"
            type="warning"
            description="Revoking a credential will immediately invalidate it. The holder will no longer be able to use this credential for verification."
            show-icon
            :closable="false"
        />

        <el-descriptions :column="2" border class="credential-info">
          <el-descriptions-item label="Credential ID">{{ revokeDialog.credential.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ revokeDialog.credential.type }}</el-descriptions-item>
          <el-descriptions-item label="Recipient">{{ revokeDialog.credential.recipientName }}</el-descriptions-item>
          <el-descriptions-item label="Recipient DID">{{ revokeDialog.credential.recipientDid }}</el-descriptions-item>
          <el-descriptions-item label="Issued Date">{{ revokeDialog.credential.issuedDate }}</el-descriptions-item>
          <el-descriptions-item label="Expiry Date">{{ revokeDialog.credential.expiryDate || 'Never' }}</el-descriptions-item>
        </el-descriptions>

        <el-form :model="revokeForm" label-width="100px" class="revoke-form">
          <el-form-item label="Revocation Reason" required>
            <el-select v-model="revokeForm.reason" placeholder="Select revocation reason" style="width: 100%">
              <el-option label="Credential Compromised" value="credential_compromised" />
              <el-option label="Recipient No Longer Authorized" value="unauthorized" />
              <el-option label="Information Incorrect" value="incorrect_info" />
              <el-option label="Credential Expired" value="expired" />
              <el-option label="Duplicate Issuance" value="duplicate" />
              <el-option label="Recipient Request" value="recipient_request" />
              <el-option label="Administrative Action" value="administrative" />
            </el-select>
          </el-form-item>

          <el-form-item label="Additional Notes">
            <el-input
                v-model="revokeForm.notes"
                type="textarea"
                :rows="3"
                placeholder="Provide additional context for this revocation..."
            />
          </el-form-item>

          <el-form-item label="Notify Recipient">
            <el-switch v-model="revokeForm.notifyRecipient" />
            <span class="form-hint">Send email notification to the credential holder</span>
          </el-form-item>
        </el-form>

        <div class="revoke-warning">
          <el-icon><WarningFilled /></el-icon>
          <span>This credential will be added to the revocation registry and will no longer be verifiable.</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="revokeDialog.visible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmRevoke" :loading="isRevoking">
          <el-icon><CircleClose /></el-icon>
          Revoke Credential
        </el-button>
      </template>
    </el-dialog>

    <!-- Bulk Revoke Dialog -->
    <el-dialog v-model="bulkRevokeDialog.visible" title="Bulk Revoke Credentials" width="550px">
      <div class="bulk-revoke-content">
        <el-alert
            title="Bulk Revocation"
            type="warning"
            :description="`You are about to revoke ${selectedCredentials.length} credential(s). This action cannot be undone.`"
            show-icon
            :closable="false"
        />

        <el-form :model="bulkRevokeForm" label-width="100px" class="revoke-form">
          <el-form-item label="Revocation Reason" required>
            <el-select v-model="bulkRevokeForm.reason" placeholder="Select revocation reason" style="width: 100%">
              <el-option label="Administrative Action" value="administrative" />
              <el-option label="System Migration" value="migration" />
              <el-option label="Policy Change" value="policy_change" />
              <el-option label="Security Incident" value="security_incident" />
            </el-select>
          </el-form-item>

          <el-form-item label="Additional Notes">
            <el-input v-model="bulkRevokeForm.notes" type="textarea" :rows="3" placeholder="Provide additional context..." />
          </el-form-item>

          <el-form-item label="Notify Recipients">
            <el-switch v-model="bulkRevokeForm.notifyRecipients" />
            <span class="form-hint">Send email notification to all affected holders</span>
          </el-form-item>
        </el-form>

        <div class="affected-credentials">
          <h4>Affected Credentials</h4>
          <div class="credential-list">
            <div v-for="id in selectedCredentials.slice(0, 10)" :key="id" class="affected-item">
              <el-icon><Document /></el-icon>
              <span>{{ id }}</span>
            </div>
            <div v-if="selectedCredentials.length > 10" class="more-items">
              ... and {{ selectedCredentials.length - 10 }} more
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="bulkRevokeDialog.visible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmBulkRevoke" :loading="isBulkRevoking">
          <el-icon><CircleClose /></el-icon>
          Revoke All ({{ selectedCredentials.length }})
        </el-button>
      </template>
    </el-dialog>

    <!-- Credential Details Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="`Credential Details - ${detailDialog.credential?.id}`" width="650px">
      <div v-if="detailDialog.credential" class="credential-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Credential ID">{{ detailDialog.credential.id }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="detailDialog.credential.status === 'active' ? 'success' : 'danger'" size="small">
              {{ detailDialog.credential.status === 'active' ? 'Active' : 'Revoked' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Type">{{ detailDialog.credential.type }}</el-descriptions-item>
          <el-descriptions-item label="Schema">{{ detailDialog.credential.schema }}</el-descriptions-item>
          <el-descriptions-item label="Recipient Name">{{ detailDialog.credential.recipientName }}</el-descriptions-item>
          <el-descriptions-item label="Recipient DID">{{ detailDialog.credential.recipientDid }}</el-descriptions-item>
          <el-descriptions-item label="Issued Date">{{ detailDialog.credential.issuedDate }}</el-descriptions-item>
          <el-descriptions-item label="Issued By">{{ detailDialog.credential.issuedBy }}</el-descriptions-item>
          <el-descriptions-item label="Expiry Date">{{ detailDialog.credential.expiryDate || 'Never' }}</el-descriptions-item>
          <el-descriptions-item label="Last Verified">{{ detailDialog.credential.lastVerified || 'Never' }}</el-descriptions-item>
          <el-descriptions-item label="Claims" :span="2">
            <div class="claims-detail">
              <div v-for="(value, key) in detailDialog.credential.claims" :key="key" class="claim-detail-item">
                <strong>{{ formatClaimLabel(key) }}:</strong> {{ value }}
              </div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Revocation Info" :span="2" v-if="detailDialog.credential.status === 'revoked'">
            <div class="revocation-info">
              <div>Revoked On: {{ detailDialog.credential.revokedDate }}</div>
              <div>Revoked By: {{ detailDialog.credential.revokedBy }}</div>
              <div>Reason: {{ detailDialog.credential.revokeReason }}</div>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  List,
  Delete,
  Document,
  CircleCheck,
  CircleClose,
  Clock,
  Search,
  RefreshLeft,
  User,
  Message,
  Calendar,
  View,
  Refresh,
  WarningFilled,
  Plus,
  Check
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const isRevoking = ref(false)
const isBulkRevoking = ref(false)
const searchPerformed = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading revocation registry...',
  'Initializing revocation service...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface Credential {
  id: string
  type: string
  schema: string
  recipientName: string
  recipientDid: string
  recipientEmail: string
  issuedDate: string
  expiryDate: string
  issuedBy: string
  status: 'active' | 'revoked'
  lastVerified?: string
  claims: Record<string, any>
  revokedDate?: string
  revokedBy?: string
  revokeReason?: string
}

interface RevocationRecord {
  credentialId: string
  credentialType: string
  recipient: string
  revokedDate: string
  reason: string
  revokedBy: string
  notes?: string
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalCredentials: 1248,
  activeCredentials: 892,
  revokedCredentials: 356,
  revokedThisMonth: 28
})

const activeCredentials = ref<Credential[]>([
  {
    id: 'cred_abc123def456',
    type: 'Employee Identity',
    schema: 'https://schema.org/EmployeeRole',
    recipientName: 'John Smith',
    recipientDid: 'did:example:john.smith',
    recipientEmail: 'john.smith@example.com',
    issuedDate: '2024-05-15',
    expiryDate: '2025-05-15',
    issuedBy: 'IBMS Trust Authority',
    status: 'active',
    claims: {
      employeeId: 'EMP-001',
      position: 'Senior Engineer',
      department: 'Engineering',
      hireDate: '2023-01-10',
      clearanceLevel: 'Level 3'
    }
  },
  {
    id: 'cred_xyz789012',
    type: 'Equipment Certification',
    schema: 'https://schema.org/Certification',
    recipientName: 'Mike Chen',
    recipientDid: 'did:example:mike.chen',
    recipientEmail: 'mike.chen@example.com',
    issuedDate: '2024-06-01',
    expiryDate: '2025-06-01',
    issuedBy: 'IBMS Trust Authority',
    status: 'active',
    claims: {
      equipmentId: 'CH-101',
      certificationType: 'Safety Compliance',
      inspectorName: 'Sarah Lee',
      complianceStatus: 'Compliant',
      remarks: 'Passed all tests'
    }
  },
  {
    id: 'cred_ghi345678',
    type: 'Access Credential',
    schema: 'https://schema.org/AccessCredential',
    recipientName: 'Sarah Lee',
    recipientDid: 'did:example:sarah.lee',
    recipientEmail: 'sarah.lee@example.com',
    issuedDate: '2024-05-20',
    expiryDate: '2024-11-20',
    issuedBy: 'IBMS Trust Authority',
    status: 'active',
    claims: {
      accessLevel: 'Restricted',
      zones: 'Server Room, Data Center',
      issuedBy: 'Security Department'
    }
  },
  {
    id: 'cred_mno901234',
    type: 'Compliance Attestation',
    schema: 'https://schema.org/Compliance',
    recipientName: 'David Kim',
    recipientDid: 'did:example:david.kim',
    recipientEmail: 'david.kim@example.com',
    issuedDate: '2024-04-10',
    expiryDate: '2025-04-10',
    issuedBy: 'IBMS Trust Authority',
    status: 'active',
    claims: {
      standard: 'ISO 27001',
      complianceScore: 98,
      auditorName: 'External Audit Firm',
      auditDate: '2024-03-15',
      recommendations: 'None'
    }
  }
])

const revocationHistory = ref<RevocationRecord[]>([
  {
    credentialId: 'cred_prev001',
    credentialType: 'Employee Identity',
    recipient: 'Jane Doe',
    revokedDate: '2024-06-05 14:30:00',
    reason: 'Employee terminated',
    revokedBy: 'admin@ibms.com'
  },
  {
    credentialId: 'cred_prev002',
    credentialType: 'Access Credential',
    recipient: 'Bob Wilson',
    revokedDate: '2024-06-01 09:15:00',
    reason: 'Credential compromised',
    revokedBy: 'security@ibms.com'
  },
  {
    credentialId: 'cred_prev003',
    credentialType: 'Equipment Certification',
    recipient: 'Alice Zhang',
    revokedDate: '2024-05-28 11:45:00',
    reason: 'Equipment decommissioned',
    revokedBy: 'admin@ibms.com'
  }
])

// ==================== 响应式状态 ====================
const searchQuery = ref('')
const searchResults = ref<Credential[]>([])
const selectedCredentials = ref<string[]>([])
const tableFilter = reactive({ type: '', search: '' })

const revokeDialog = reactive({
  visible: false,
  credential: null as Credential | null
})

const bulkRevokeDialog = reactive({
  visible: false
})

const detailDialog = reactive({
  visible: false,
  credential: null as Credential | null
})

const revokeForm = reactive({
  reason: '',
  notes: '',
  notifyRecipient: true
})

const bulkRevokeForm = reactive({
  reason: '',
  notes: '',
  notifyRecipients: true
})

// ==================== 计算属性 ====================
const filteredCredentials = computed(() => {
  let filtered = activeCredentials.value.filter(c => c.status === 'active')

  if (tableFilter.type) {
    filtered = filtered.filter(c => c.type === tableFilter.type)
  }

  if (tableFilter.search) {
    const searchLower = tableFilter.search.toLowerCase()
    filtered = filtered.filter(c =>
        c.id.toLowerCase().includes(searchLower) ||
        c.recipientName.toLowerCase().includes(searchLower) ||
        c.recipientDid.toLowerCase().includes(searchLower)
    )
  }

  return filtered
})

// ==================== 辅助函数 ====================
const formatClaimLabel = (key: string) => {
  const labels: Record<string, string> = {
    employeeId: 'Employee ID',
    position: 'Position',
    department: 'Department',
    hireDate: 'Hire Date',
    clearanceLevel: 'Clearance Level',
    equipmentId: 'Equipment ID',
    certificationType: 'Certification Type',
    inspectorName: 'Inspector Name',
    complianceStatus: 'Compliance Status',
    remarks: 'Remarks',
    standard: 'Standard',
    complianceScore: 'Compliance Score',
    auditorName: 'Auditor Name',
    auditDate: 'Audit Date',
    recommendations: 'Recommendations',
    accessLevel: 'Access Level',
    zones: 'Accessible Zones',
    issuedBy: 'Issuing Authority'
  }
  return labels[key] || key
}

const isExpiringSoon = (expiryDate: string) => {
  if (!expiryDate) return false
  const expiry = new Date(expiryDate)
  const now = new Date()
  const daysUntilExpiry = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
  return daysUntilExpiry <= 30 && daysUntilExpiry > 0
}

const searchCredential = () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('Please enter a search query')
    return
  }

  const query = searchQuery.value.toLowerCase()
  searchResults.value = activeCredentials.value.filter(c =>
      c.id.toLowerCase().includes(query) ||
      c.recipientName.toLowerCase().includes(query) ||
      c.recipientDid.toLowerCase().includes(query)
  )
  searchPerformed.value = true
}

const resetSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  searchPerformed.value = false
  selectedCredentials.value = []
}

const openRevokeDialog = (credential: Credential) => {
  revokeDialog.credential = credential
  revokeForm.reason = ''
  revokeForm.notes = ''
  revokeForm.notifyRecipient = true
  revokeDialog.visible = true
}

const confirmRevoke = async () => {
  if (!revokeForm.reason) {
    ElMessage.warning('Please select a revocation reason')
    return
  }

  isRevoking.value = true

  await new Promise(resolve => setTimeout(resolve, 1500))

  const credential = revokeDialog.credential!
  const index = activeCredentials.value.findIndex(c => c.id === credential.id)
  if (index !== -1) {
    activeCredentials.value[index].status = 'revoked'
    activeCredentials.value[index].revokedDate = new Date().toLocaleString()
    activeCredentials.value[index].revokedBy = 'admin@ibms.com'
    activeCredentials.value[index].revokeReason = revokeForm.reason
  }

  revocationHistory.value.unshift({
    credentialId: credential.id,
    credentialType: credential.type,
    recipient: credential.recipientName,
    revokedDate: new Date().toLocaleString(),
    reason: revokeForm.reason,
    revokedBy: 'admin@ibms.com',
    notes: revokeForm.notes
  })

  stats.activeCredentials--
  stats.revokedCredentials++
  stats.revokedThisMonth++

  if (revokeForm.notifyRecipient) {
    ElMessage.success(`Revocation notification sent to ${credential.recipientEmail}`)
  }

  isRevoking.value = false
  revokeDialog.visible = false
  ElMessage.success(`Credential ${credential.id} has been revoked`)

  // Remove from search results if present
  const resultIndex = searchResults.value.findIndex(r => r.id === credential.id)
  if (resultIndex !== -1) {
    searchResults.value.splice(resultIndex, 1)
  }
}

const bulkRevoke = () => {
  if (selectedCredentials.value.length === 0) return
  bulkRevokeForm.reason = ''
  bulkRevokeForm.notes = ''
  bulkRevokeForm.notifyRecipients = true
  bulkRevokeDialog.visible = true
}

const confirmBulkRevoke = async () => {
  if (!bulkRevokeForm.reason) {
    ElMessage.warning('Please select a revocation reason')
    return
  }

  isBulkRevoking.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  const revokedCount = selectedCredentials.value.length
  const revokedCredentialsList = [...selectedCredentials.value]

  activeCredentials.value = activeCredentials.value.filter(c => !revokedCredentialsList.includes(c.id))

  revokedCredentialsList.forEach(credId => {
    const credential = activeCredentials.value.find(c => c.id === credId)
    if (credential) {
      revocationHistory.value.unshift({
        credentialId: credential.id,
        credentialType: credential.type,
        recipient: credential.recipientName,
        revokedDate: new Date().toLocaleString(),
        reason: bulkRevokeForm.reason,
        revokedBy: 'admin@ibms.com',
        notes: bulkRevokeForm.notes
      })
    }
  })

  stats.activeCredentials -= revokedCount
  stats.revokedCredentials += revokedCount
  stats.revokedThisMonth += revokedCount

  if (bulkRevokeForm.notifyRecipients) {
    ElMessage.success(`Revocation notifications sent to ${revokedCount} recipients`)
  }

  isBulkRevoking.value = false
  bulkRevokeDialog.visible = false
  selectedCredentials.value = []
  ElMessage.success(`${revokedCount} credential(s) have been revoked`)
}

const viewCredentialDetails = (credential: Credential) => {
  detailDialog.credential = credential
  detailDialog.visible = true
}

const viewRevocationRegistry = () => {
  ElMessage.info('Viewing full revocation registry')
}

const refreshHistory = () => {
  ElMessage.success('Revocation history refreshed')
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
.revoke-vc-page {
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
.danger-bg { background-color: #fef0f0; color: #f56c6c; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }

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

/* Search Card */
.search-card, .results-card, .credentials-table-wrapper, .history-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
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

.search-area {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.result-count {
  font-size: 13px;
  color: #8c9aab;
}

/* Results List */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.credential-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  transition: all 0.2s;
}

.credential-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.credential-card.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.credential-select {
  flex-shrink: 0;
}

.credential-info {
  flex: 1;
}

.credential-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.credential-id {
  font-family: monospace;
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
}

.credential-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #5e6e82;
}

.detail-row .el-icon {
  font-size: 12px;
  color: #8c9aab;
}

.credential-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.no-results {
  padding: 40px 0;
}

/* Table */
.credentials-table-wrapper {
  overflow: hidden;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.table-filters {
  display: flex;
  gap: 12px;
}

.expiring-soon {
  color: #e6a23c;
  font-weight: 500;
}

/* History Card */
.no-history {
  padding: 20px 0;
}

/* Revoke Dialog */
.revoke-dialog-content {
  padding: 8px 0;
}

.credential-info {
  margin: 16px 0;
}

.revoke-form {
  margin-top: 16px;
}

.form-hint {
  margin-left: 12px;
  font-size: 12px;
  color: #8c9aab;
}

.revoke-warning {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background-color: #fef0f0;
  border-radius: 8px;
  margin-top: 16px;
  color: #f56c6c;
  font-size: 13px;
}

/* Bulk Revoke Dialog */
.bulk-revoke-content {
  padding: 8px 0;
}

.affected-credentials {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.affected-credentials h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
}

.credential-list {
  max-height: 200px;
  overflow-y: auto;
}

.affected-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  font-size: 12px;
  font-family: monospace;
}

.more-items {
  padding: 8px 0;
  color: #8c9aab;
  font-size: 12px;
}

/* Credential Detail */
.credential-detail {
  padding: 8px 0;
}

.claims-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.claim-detail-item {
  font-size: 13px;
  padding: 4px 0;
  border-bottom: 1px dashed #ebeef5;
}

.revocation-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}
</style>