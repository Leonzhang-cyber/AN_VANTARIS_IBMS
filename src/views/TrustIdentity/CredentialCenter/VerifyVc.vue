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
        <div class="loading-tip">Trust & Identity - Issue Verifiable Credential</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="issue-vc-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Issue Verifiable Credential</h1>
        <p>Create and issue W3C-compliant verifiable credentials to trusted entities</p>
      </div>
      <div class="header-actions">
        <el-button @click="viewIssuanceHistory">
          <el-icon><List /></el-icon>
          Issuance History
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
            <div class="stat-value">{{ stats.totalIssued }}</div>
            <div class="stat-label">Total Issued</div>
            <div class="stat-trend positive">↑ {{ stats.monthlyIssued }} this month</div>
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
            <div class="stat-label">Active Credentials</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Clock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.expiringSoon }}</div>
            <div class="stat-label">Expiring Soon</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.avgVerificationTime }}s</div>
            <div class="stat-label">Avg Verification</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Credential Form -->
      <el-col :xs="24" :lg="14">
        <div class="form-card">
          <div class="card-header">
            <h3>Credential Details</h3>
            <el-steps :active="currentStep" finish-status="success" align-center style="width: 300px">
              <el-step title="Template" />
              <el-step title="Data" />
              <el-step title="Review" />
            </el-steps>
          </div>

          <!-- Step 1: Select Template -->
          <div v-show="currentStep === 0" class="step-content">
            <div class="template-grid">
              <div
                  v-for="template in credentialTemplates"
                  :key="template.id"
                  class="template-card"
                  :class="{ selected: selectedTemplate === template.id }"
                  @click="selectedTemplate = template.id"
              >
                <div class="template-icon" :class="getTemplateIconClass(template.name)">
                  <el-icon><component :is="getTemplateIcon(template.name)" /></el-icon>
                </div>
                <div class="template-info">
                  <div class="template-name">{{ template.name }}</div>
                  <div class="template-desc">{{ template.description }}</div>
                  <div class="template-meta">
                    <el-tag size="small" type="info">{{ template.fields.length }} fields</el-tag>
                  </div>
                </div>
                <el-icon v-if="selectedTemplate === template.id" class="selected-icon"><CircleCheck /></el-icon>
              </div>
            </div>

            <div v-if="selectedTemplateData" class="schema-preview">
              <div class="preview-header">
                <span>Schema Information</span>
                <el-tag size="small" type="primary">{{ selectedTemplateData.schema }}</el-tag>
              </div>
              <div class="preview-fields">
                <div v-for="field in selectedTemplateData.fields" :key="field.name" class="preview-field">
                  <span class="field-name">{{ field.label }}</span>
                  <span class="field-type">{{ field.type }}</span>
                  <span v-if="field.required" class="field-required">Required</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 2: Credential Data -->
          <div v-show="currentStep === 1" class="step-content">
            <el-form :model="credentialData" label-width="140px" class="data-form">
              <el-divider content-position="left">Recipient Information</el-divider>

              <el-form-item label="Recipient DID" required>
                <el-input
                    v-model="credentialData.recipientDid"
                    placeholder="did:example:123456789abcdefghi"
                    size="large"
                />
                <div class="form-hint">The decentralized identifier of the credential recipient</div>
              </el-form-item>

              <el-form-item label="Recipient Name">
                <el-input v-model="credentialData.recipientName" placeholder="Full name of the recipient" size="large" />
              </el-form-item>

              <el-form-item label="Recipient Email">
                <el-input v-model="credentialData.recipientEmail" placeholder="recipient@example.com" size="large" />
              </el-form-item>

              <el-divider content-position="left">Credential Claims</el-divider>

              <div class="claims-grid">
                <div v-for="field in credentialFields" :key="field.name" class="claim-field">
                  <el-form-item :label="field.label" :required="field.required">
                    <el-input
                        v-if="field.type === 'string'"
                        v-model="credentialData.claims[field.name]"
                        :placeholder="`Enter ${field.label.toLowerCase()}`"
                        size="large"
                    />
                    <el-input-number
                        v-else-if="field.type === 'number'"
                        v-model="credentialData.claims[field.name]"
                        style="width: 100%"
                        :controls-position="'right'"
                    />
                    <el-date-picker
                        v-else-if="field.type === 'date'"
                        v-model="credentialData.claims[field.name]"
                        type="date"
                        placeholder="Select date"
                        style="width: 100%"
                        format="YYYY-MM-DD"
                    />
                    <el-select
                        v-else-if="field.type === 'select'"
                        v-model="credentialData.claims[field.name]"
                        placeholder="Select option"
                        style="width: 100%"
                        size="large"
                    >
                      <el-option v-for="opt in field.options" :key="opt" :label="opt" :value="opt" />
                    </el-select>
                  </el-form-item>
                </div>
              </div>

              <el-divider content-position="left">Validity Period</el-divider>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="Valid From">
                    <el-date-picker
                        v-model="credentialData.validFrom"
                        type="datetime"
                        placeholder="Select start date"
                        style="width: 100%"
                        format="YYYY-MM-DD HH:mm"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="Valid Until">
                    <el-date-picker
                        v-model="credentialData.validUntil"
                        type="datetime"
                        placeholder="Select expiration date"
                        style="width: 100%"
                        format="YYYY-MM-DD HH:mm"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>

          <!-- Step 3: Review & Issue -->
          <div v-show="currentStep === 2" class="step-content">
            <div class="review-container">
              <div class="review-section">
                <h4>Credential Overview</h4>
                <el-descriptions :column="2" border size="large">
                  <el-descriptions-item label="Credential Type">
                    <el-tag type="primary" size="large">{{ selectedTemplateData?.name }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Schema">{{ selectedTemplateData?.schema }}</el-descriptions-item>
                  <el-descriptions-item label="Recipient DID">
                    <code>{{ credentialData.recipientDid || 'Not specified' }}</code>
                  </el-descriptions-item>
                  <el-descriptions-item label="Recipient Name">{{ credentialData.recipientName || 'Not specified' }}</el-descriptions-item>
                  <el-descriptions-item label="Valid From">{{ formatDateTime(credentialData.validFrom) }}</el-descriptions-item>
                  <el-descriptions-item label="Valid Until">{{ formatDateTime(credentialData.validUntil) }}</el-descriptions-item>
                </el-descriptions>
              </div>

              <div class="review-section">
                <h4>Credential Claims</h4>
                <div class="claims-preview">
                  <div v-for="(value, key) in credentialData.claims" :key="key" class="claim-preview-item">
                    <span class="claim-label">{{ formatClaimLabel(key) }}:</span>
                    <span class="claim-value">{{ value || 'Not provided' }}</span>
                  </div>
                  <div v-if="Object.keys(credentialData.claims).length === 0" class="no-claims">
                    No claims added
                  </div>
                </div>
              </div>

              <div class="review-section signature-info">
                <el-alert
                    title="Digital Signature"
                    type="info"
                    description="This credential will be digitally signed using your organization's private key. The signature ensures authenticity and integrity of the credential."
                    show-icon
                    :closable="false"
                />
              </div>
            </div>
          </div>

          <!-- Navigation Buttons -->
          <div class="step-buttons">
            <el-button v-if="currentStep > 0" size="large" @click="prevStep">
              <el-icon><ArrowLeft /></el-icon>
              Back
            </el-button>
            <el-button v-if="currentStep < 2" type="primary" size="large" @click="nextStep">
              Next
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <el-button v-if="currentStep === 2" type="success" size="large" @click="issueCredential" :loading="isIssuing">
              <el-icon><Check /></el-icon>
              Issue Credential
            </el-button>
          </div>
        </div>
      </el-col>

      <!-- Right Sidebar -->
      <el-col :xs="24" :lg="10">
        <!-- Issuer Information -->
        <div class="info-card">
          <div class="card-header">
            <h3>Issuer Information</h3>
            <el-tag type="success" size="small">Verified</el-tag>
          </div>
          <div class="issuer-details">
            <div class="issuer-did">
              <span class="label">Issuer DID</span>
              <code class="did-value">did:example:issuer.{{ issuerDid }}</code>
              <el-button link size="small" @click="copyToClipboard(issuerDid)">Copy</el-button>
            </div>
            <div class="issuer-row">
              <span class="label">Organization</span>
              <span class="value">{{ issuerInfo.organization }}</span>
            </div>
            <div class="issuer-row">
              <span class="label">Key Type</span>
              <span class="value">{{ issuerInfo.keyType }}</span>
            </div>
            <div class="issuer-row">
              <span class="label">Key ID</span>
              <span class="value">{{ issuerInfo.keyId }}</span>
            </div>
            <div class="issuer-row">
              <span class="label">Status</span>
              <el-tag type="success" size="small">Active</el-tag>
            </div>
          </div>
        </div>

        <!-- Help Section -->
        <div class="help-card">
          <div class="card-header">
            <h3>What is a Verifiable Credential?</h3>
          </div>
          <div class="help-content">
            <p>A verifiable credential is a W3C standard data model for digital credentials with these properties:</p>
            <ul>
              <li><el-icon><Lock /></el-icon> <strong>Tamper-evident</strong> - Cryptographically secured</li>
              <li><el-icon><User /></el-icon> <strong>Privacy-preserving</strong> - Selective disclosure support</li>
              <li><el-icon><Connection /></el-icon> <strong>Interoperable</strong> - Works across platforms</li>
              <li><el-icon><Monitor /></el-icon> <strong>Machine-verifiable</strong> - Instant verification</li>
            </ul>
            <el-divider />
            <h4>Common Use Cases</h4>
            <div class="use-cases">
              <el-tag>Employee Identity</el-tag>
              <el-tag>Equipment Certification</el-tag>
              <el-tag>Compliance Attestation</el-tag>
              <el-tag>Access Control</el-tag>
              <el-tag>Training Records</el-tag>
              <el-tag>Maintenance Logs</el-tag>
            </div>
          </div>
        </div>

        <!-- Recent Issuances -->
        <div class="recent-card">
          <div class="card-header">
            <h3>Recent Issuances</h3>
            <el-button size="small" @click="refreshRecent">
              <el-icon><Refresh /></el-icon>
              Refresh
            </el-button>
          </div>
          <div class="recent-list">
            <div v-for="item in recentIssuances" :key="item.id" class="recent-item">
              <div class="recent-icon" :class="item.status">
                <el-icon><component :is="item.status === 'issued' ? 'CircleCheck' : 'Clock'" /></el-icon>
              </div>
              <div class="recent-info">
                <div class="recent-title">{{ item.credentialType }}</div>
                <div class="recent-meta">
                  <el-icon><User /></el-icon>
                  {{ item.recipient }}
                  <el-icon><Calendar /></el-icon>
                  {{ item.date }}
                </div>
              </div>
              <el-button link size="small" @click="viewCredential(item)">View</el-button>
            </div>
            <div v-if="recentIssuances.length === 0" class="no-recent">
              <el-empty description="No recent issuances" :image-size="60" />
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Success Dialog -->
    <el-dialog v-model="successDialog.visible" title="Credential Issued Successfully" width="550px" class="success-dialog">
      <div class="success-content">
        <div class="success-icon-wrapper">
          <el-icon class="success-icon"><CircleCheck /></el-icon>
        </div>
        <h3>Verifiable Credential Issued</h3>
        <p>The credential has been successfully issued and cryptographically signed.</p>

        <div class="credential-summary">
          <div class="summary-row">
            <span class="summary-label">Credential ID:</span>
            <code class="summary-value">{{ issuedCredential?.id }}</code>
          </div>
          <div class="summary-row">
            <span class="summary-label">Recipient:</span>
            <span class="summary-value">{{ issuedCredential?.recipient }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Type:</span>
            <span class="summary-value">{{ issuedCredential?.type }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Issued At:</span>
            <span class="summary-value">{{ issuedCredential?.issuedAt }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">Valid Until:</span>
            <span class="summary-value">{{ issuedCredential?.validUntil }}</span>
          </div>
        </div>

        <div class="success-actions">
          <el-button type="primary" @click="downloadCredential">
            <el-icon><Download /></el-icon>
            Download JSON
          </el-button>
          <el-button @click="copyCredential">
            <el-icon><CopyDocument /></el-icon>
            Copy to Clipboard
          </el-button>
          <el-button @click="sendToRecipient">
            <el-icon><Message /></el-icon>
            Send to Recipient
          </el-button>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeSuccessDialog">Close</el-button>
        <el-button type="primary" @click="issueAnother">Issue Another Credential</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  List,
  Check,
  CircleCheck,
  Clock,
  Document,
  DataAnalysis,
  Refresh,
  User,
  Calendar,
  Lock,
  Connection,
  Monitor,
  Download,
  CopyDocument,
  Message,
  ArrowLeft,
  ArrowRight,
  Plus,
  Tools,
  OfficeBuilding,
  Key,
  UserFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isIssuing = ref(false)
const currentStep = ref(0)

const loadingMessages = [
  'Preparing...',
  'Loading credential templates...',
  'Initializing signing service...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface CredentialTemplate {
  id: string
  name: string
  description: string
  schema: string
  version: string
  fields: Array<{ name: string; label: string; type: string; required: boolean; options?: string[] }>
}

interface IssuedCredential {
  id: string
  recipient: string
  recipientDid: string
  type: string
  issuedAt: string
  validFrom: string
  validUntil: string
  claims: Record<string, any>
  proof: {
    type: string
    created: string
    proofPurpose: string
    verificationMethod: string
    signature: string
  }
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalIssued: 1248,
  monthlyIssued: 156,
  activeCredentials: 892,
  expiringSoon: 23,
  avgVerificationTime: 1.2
})

const credentialTemplates = ref<CredentialTemplate[]>([
  {
    id: 'temp-001',
    name: 'Employee Identity',
    description: 'Verifiable credential for employee identity and role verification',
    schema: 'https://schema.org/EmployeeRole',
    version: '1.0.0',
    fields: [
      { name: 'employeeId', label: 'Employee ID', type: 'string', required: true },
      { name: 'position', label: 'Position', type: 'string', required: true },
      { name: 'department', label: 'Department', type: 'string', required: true },
      { name: 'hireDate', label: 'Hire Date', type: 'date', required: true },
      { name: 'clearanceLevel', label: 'Clearance Level', type: 'select', required: true, options: ['Level 1', 'Level 2', 'Level 3', 'Level 4'] }
    ]
  },
  {
    id: 'temp-002',
    name: 'Equipment Certification',
    description: 'Certification for equipment inspection and maintenance',
    schema: 'https://schema.org/Certification',
    version: '1.0.0',
    fields: [
      { name: 'equipmentId', label: 'Equipment ID', type: 'string', required: true },
      { name: 'certificationType', label: 'Certification Type', type: 'string', required: true },
      { name: 'inspectorName', label: 'Inspector Name', type: 'string', required: true },
      { name: 'complianceStatus', label: 'Compliance Status', type: 'select', required: true, options: ['Compliant', 'Non-Compliant', 'Partial'] },
      { name: 'remarks', label: 'Remarks', type: 'string', required: false }
    ]
  },
  {
    id: 'temp-003',
    name: 'Compliance Attestation',
    description: 'Regulatory compliance and standards attestation',
    schema: 'https://schema.org/Compliance',
    version: '1.0.0',
    fields: [
      { name: 'standard', label: 'Standard', type: 'string', required: true },
      { name: 'complianceScore', label: 'Compliance Score', type: 'number', required: true },
      { name: 'auditorName', label: 'Auditor Name', type: 'string', required: true },
      { name: 'auditDate', label: 'Audit Date', type: 'date', required: true },
      { name: 'recommendations', label: 'Recommendations', type: 'string', required: false }
    ]
  },
  {
    id: 'temp-004',
    name: 'Access Credential',
    description: 'Access rights and permissions credential',
    schema: 'https://schema.org/AccessCredential',
    version: '1.0.0',
    fields: [
      { name: 'accessLevel', label: 'Access Level', type: 'select', required: true, options: ['Public', 'Restricted', 'Confidential', 'Secret'] },
      { name: 'zones', label: 'Accessible Zones', type: 'string', required: true },
      { name: 'issuedBy', label: 'Issuing Authority', type: 'string', required: true }
    ]
  }
])

const selectedTemplate = ref('')
const credentialData = reactive({
  recipientDid: '',
  recipientName: '',
  recipientEmail: '',
  validFrom: new Date(),
  validUntil: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000),
  claims: {} as Record<string, any>
})

const issuerInfo = {
  organization: 'IBMS Trust Authority',
  keyType: 'Ed25519 Signature 2020',
  keyId: 'key-abc123def456'
}

const issuerDid = ref('ibms-trust-authority')

const recentIssuances = ref([
  { id: 'vc-001', credentialType: 'Employee Identity', recipient: 'john.doe@example.com', date: '2024-06-10', status: 'issued' },
  { id: 'vc-002', credentialType: 'Equipment Certification', recipient: 'mike.chen@example.com', date: '2024-06-08', status: 'issued' },
  { id: 'vc-003', credentialType: 'Access Credential', recipient: 'sarah.lee@example.com', date: '2024-06-05', status: 'issued' },
  { id: 'vc-004', credentialType: 'Compliance Attestation', recipient: 'david.kim@example.com', date: '2024-06-03', status: 'issued' }
])

const successDialog = reactive({
  visible: false
})

const issuedCredential = ref<IssuedCredential | null>(null)

// ==================== 计算属性 ====================
const selectedTemplateData = computed(() => {
  return credentialTemplates.value.find(t => t.id === selectedTemplate.value)
})

const credentialFields = computed(() => {
  return selectedTemplateData.value?.fields || []
})

// ==================== 辅助函数 ====================
const getTemplateIcon = (name: string) => {
  const map: Record<string, any> = {
    'Employee Identity': UserFilled,
    'Equipment Certification': Tools,
    'Compliance Attestation': Document,
    'Access Credential': Key
  }
  return map[name] || Document
}

const getTemplateIconClass = (name: string) => {
  const map: Record<string, string> = {
    'Employee Identity': 'employee',
    'Equipment Certification': 'equipment',
    'Compliance Attestation': 'compliance',
    'Access Credential': 'access'
  }
  return map[name] || 'default'
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

const formatDateOnly = (date: Date | null) => {
  if (!date) return 'Not specified'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

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

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('Copied to clipboard')
  } catch {
    ElMessage.error('Failed to copy')
  }
}

const resetCredentialForm = () => {
  currentStep.value = 0
  selectedTemplate.value = ''
  credentialData.recipientDid = ''
  credentialData.recipientName = ''
  credentialData.recipientEmail = ''
  credentialData.validFrom = new Date()
  credentialData.validUntil = new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)
  credentialData.claims = {}
}

const nextStep = () => {
  if (currentStep.value === 0 && !selectedTemplate.value) {
    ElMessage.warning('Please select a credential template')
    return
  }
  if (currentStep.value === 1) {
    if (!credentialData.recipientDid) {
      ElMessage.warning('Please enter recipient DID')
      return
    }
    const missingFields = credentialFields.value
        .filter(f => f.required && !credentialData.claims[f.name])
        .map(f => f.label)
    if (missingFields.length > 0) {
      ElMessage.warning(`Please fill required fields: ${missingFields.join(', ')}`)
      return
    }
  }
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const issueCredential = async () => {
  isIssuing.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  const credentialId = `urn:uuid:${Math.random().toString(36).substring(2, 15)}`

  issuedCredential.value = {
    id: credentialId,
    recipient: credentialData.recipientName || credentialData.recipientDid,
    recipientDid: credentialData.recipientDid,
    type: selectedTemplateData.value!.name,
    issuedAt: new Date().toISOString(),
    validFrom: formatDateTime(credentialData.validFrom),
    validUntil: formatDateTime(credentialData.validUntil),
    claims: { ...credentialData.claims },
    proof: {
      type: 'Ed25519Signature2020',
      created: new Date().toISOString(),
      proofPurpose: 'assertionMethod',
      verificationMethod: `did:example:issuer.${issuerDid.value}#${issuerInfo.keyId}`,
      signature: `sig_${Math.random().toString(36).substring(2, 20)}`
    }
  }

  recentIssuances.value.unshift({
    id: credentialId,
    credentialType: selectedTemplateData.value!.name,
    recipient: credentialData.recipientName || credentialData.recipientDid.substring(0, 20),
    date: new Date().toISOString().slice(0, 10),
    status: 'issued'
  })

  stats.totalIssued++
  stats.monthlyIssued++

  isIssuing.value = false
  successDialog.visible = true
}

const downloadCredential = () => {
  if (!issuedCredential.value) return
  const data = JSON.stringify(issuedCredential.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `credential-${issuedCredential.value.id.split(':').pop()}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Credential downloaded')
}

const copyCredential = () => {
  if (!issuedCredential.value) return
  copyToClipboard(JSON.stringify(issuedCredential.value, null, 2))
}

const sendToRecipient = () => {
  ElMessage.success(`Credential sent to ${issuedCredential.value?.recipient}`)
}

const issueAnother = () => {
  successDialog.visible = false
  resetCredentialForm()
}

const closeSuccessDialog = () => {
  successDialog.visible = false
}

const viewIssuanceHistory = () => {
  ElMessage.info('View issuance history')
}

const refreshRecent = () => {
  ElMessage.success('Recent issuances refreshed')
}

const viewCredential = (item: any) => {
  ElMessage.info(`Viewing credential: ${item.credentialType}`)
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
.issue-vc-page {
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

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.positive { color: #67c23a; }

/* Form Card */
.form-card, .info-card, .help-card, .recent-card {
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
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

/* Template Grid */
.template-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.template-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.template-card:hover {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.template-card.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.template-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.template-icon.employee { background-color: #ecf5ff; color: #409eff; }
.template-icon.equipment { background-color: #f0f9eb; color: #67c23a; }
.template-icon.compliance { background-color: #fff3e0; color: #e6a23c; }
.template-icon.access { background-color: #fef0f0; color: #f56c6c; }

.template-info {
  flex: 1;
}

.template-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 11px;
  color: #8c9aab;
  margin-bottom: 8px;
}

.selected-icon {
  position: absolute;
  top: 8px;
  right: 8px;
  color: #409eff;
  font-size: 18px;
}

/* Schema Preview */
.schema-preview {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
  font-weight: 500;
}

.preview-fields {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-field {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 12px;
}

.field-name {
  width: 100px;
  font-weight: 500;
}

.field-type {
  color: #8c9aab;
  font-size: 11px;
}

.field-required {
  color: #f56c6c;
  font-size: 10px;
}

/* Data Form */
.data-form {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.form-hint {
  font-size: 11px;
  color: #8c9aab;
  margin-top: 4px;
}

.claims-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Review Container */
.review-container {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.review-section {
  margin-bottom: 24px;
}

.review-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2f3d;
}

.claims-preview {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
}

.claim-preview-item {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.claim-preview-item:last-child {
  border-bottom: none;
}

.claim-label {
  width: 140px;
  font-weight: 500;
  font-size: 13px;
}

.claim-value {
  flex: 1;
  font-size: 13px;
  color: #5e6e82;
}

.no-claims {
  text-align: center;
  color: #8c9aab;
  padding: 20px;
}

/* Step Buttons */
.step-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* Issuer Details */
.issuer-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.issuer-did {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
}

.issuer-did .label {
  display: block;
  font-size: 11px;
  color: #8c9aab;
  margin-bottom: 4px;
}

.did-value {
  font-size: 12px;
  font-family: monospace;
  word-break: break-all;
}

.issuer-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.issuer-row .label {
  color: #8c9aab;
  font-size: 13px;
}

.issuer-row .value {
  font-weight: 500;
  font-size: 13px;
}

/* Help Card */
.help-content {
  font-size: 13px;
  line-height: 1.5;
  color: #5e6e82;
}

.help-content ul {
  margin: 12px 0;
  padding-left: 0;
  list-style: none;
}

.help-content li {
  margin: 8px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.help-content li .el-icon {
  color: #409eff;
}

.use-cases {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

/* Recent List */
.recent-list {
  max-height: 320px;
  overflow-y: auto;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
}

.recent-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.recent-icon.issued {
  background-color: #f0f9eb;
  color: #67c23a;
}

.recent-info {
  flex: 1;
}

.recent-title {
  font-weight: 500;
  font-size: 13px;
  margin-bottom: 4px;
}

.recent-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 11px;
  color: #8c9aab;
}

.recent-meta .el-icon {
  font-size: 11px;
}

.no-recent {
  padding: 20px;
}

/* Success Dialog */
.success-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.success-content {
  text-align: center;
  padding: 24px;
}

.success-icon-wrapper {
  margin-bottom: 20px;
}

.success-icon {
  font-size: 64px;
  color: #67c23a;
}

.success-content h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.success-content p {
  color: #8c9aab;
  margin-bottom: 24px;
}

.credential-summary {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  text-align: left;
}

.summary-row {
  display: flex;
  padding: 6px 0;
  font-size: 13px;
}

.summary-label {
  width: 100px;
  color: #8c9aab;
}

.summary-value {
  flex: 1;
  font-family: monospace;
  word-break: break-all;
}

.success-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

:deep(.el-divider__text) {
  font-weight: 500;
  color: #409eff;
}
</style>