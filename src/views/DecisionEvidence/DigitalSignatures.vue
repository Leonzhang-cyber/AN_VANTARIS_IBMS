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
        <div class="loading-tip">Digital Signatures</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="signatures-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Digital Signatures</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Digital Signatures</h1>
        <p class="description">Manage and verify digital signatures for decisions, approvals, and compliance documentation</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Audit Log
        </el-button>
        <el-button type="primary" @click="handleSignDocument">
          <el-icon><Plus /></el-icon>
          Sign Document
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Certificate Status -->
    <el-card class="certificate-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Certificate Status</span>
          <el-button size="small" @click="handleRefreshCertificate">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6" v-for="cert in certificates" :key="cert.name">
          <div class="certificate-item">
            <div class="cert-icon" :style="{ background: cert.status === 'Valid' ? '#67c23a' : '#f56c6c' }">
              <el-icon :size="24"><component :is="cert.icon" /></el-icon>
            </div>
            <div class="cert-info">
              <div class="cert-name">{{ cert.name }}</div>
              <div class="cert-status">
                <el-tag :type="cert.status === 'Valid' ? 'success' : 'danger'" size="small">{{ cert.status }}</el-tag>
              </div>
              <div class="cert-expiry">Expires: {{ cert.expiryDate }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Signature Verification -->
    <el-card class="verification-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Verify Signature</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="16">
          <el-input
              v-model="verificationCode"
              placeholder="Enter signature ID or hash to verify"
              style="width: 100%"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="verifySignature">Verify</el-button>
        </el-col>
        <el-col :span="4">
          <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleFileUpload"
              :show-file-list="false"
          >
            <el-button>Upload Signed File</el-button>
          </el-upload>
        </el-col>
      </el-row>
      <div v-if="verificationResult" class="verification-result">
        <el-alert
            :title="verificationResult.message"
            :type="verificationResult.valid ? 'success' : 'error'"
            :closable="false"
            show-icon
        >
          <template v-if="verificationResult.valid">
            <div class="result-details">
              <p><strong>Signer:</strong> {{ verificationResult.signer }}</p>
              <p><strong>Signed At:</strong> {{ verificationResult.signedAt }}</p>
              <p><strong>Certificate ID:</strong> {{ verificationResult.certId }}</p>
              <p><strong>Hash:</strong> {{ verificationResult.hash }}</p>
            </div>
          </template>
        </el-alert>
      </div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by document or signer"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
            <el-option label="Valid" value="Valid" />
            <el-option label="Expired" value="Expired" />
            <el-option label="Revoked" value="Revoked" />
            <el-option label="Pending" value="Pending" />
          </el-select>
          <el-select v-model="filters.signatureType" placeholder="Signature Type" clearable style="width: 150px">
            <el-option label="Decision Approval" value="Decision Approval" />
            <el-option label="Contract" value="Contract" />
            <el-option label="Compliance" value="Compliance" />
            <el-option label="Financial" value="Financial" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 260px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Digital Signatures ({{ filteredSignatures.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchSignatures" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedSignatures" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="documentName" label="Document Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="documentType" label="Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getDocumentTypeTag(row.documentType)" size="small">{{ row.documentType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signer" label="Signer" width="150" />
        <el-table-column prop="signerRole" label="Role" width="130" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="signedAt" label="Signed At" width="160" />
        <el-table-column prop="expiresAt" label="Expires At" width="160" />
        <el-table-column label="Actions" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewSignature(row)">View</el-button>
            <el-button link type="success" size="small" @click="verifySignatureById(row)">Verify</el-button>
            <el-button link type="info" size="small" @click="downloadCertificate(row)">Certificate</el-button>
            <el-button v-if="row.status === 'Valid'" link type="danger" size="small" @click="revokeSignature(row)">Revoke</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredSignatures.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Sign Document Dialog -->
    <el-dialog v-model="signDialogVisible" title="Sign Document" width="600px" destroy-on-close>
      <el-form :model="signForm" :rules="signRules" ref="signFormRef" label-width="120px">
        <el-form-item label="Document" prop="document">
          <el-upload
              ref="signUploadRef"
              action="#"
              :auto-upload="false"
              :on-change="handleSignFileChange"
              :limit="1"
              accept=".pdf,.doc,.docx"
          >
            <el-button>Select Document</el-button>
            <template #tip>
              <div class="el-upload__tip">PDF, DOC, DOCX files only</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="Document Name" prop="documentName">
          <el-input v-model="signForm.documentName" placeholder="Enter document name" />
        </el-form-item>
        <el-form-item label="Document Type" prop="documentType">
          <el-select v-model="signForm.documentType" placeholder="Select type" style="width: 100%">
            <el-option label="Decision Approval" value="Decision Approval" />
            <el-option label="Contract" value="Contract" />
            <el-option label="Compliance" value="Compliance" />
            <el-option label="Financial" value="Financial" />
          </el-select>
        </el-form-item>
        <el-form-item label="Signer Name" prop="signerName">
          <el-input v-model="signForm.signerName" placeholder="Enter your name" />
        </el-form-item>
        <el-form-item label="Signer Role" prop="signerRole">
          <el-input v-model="signForm.signerRole" placeholder="Enter your role" />
        </el-form-item>
        <el-form-item label="Signer Email" prop="signerEmail">
          <el-input v-model="signForm.signerEmail" placeholder="Enter your email" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="signForm.password" type="password" placeholder="Enter your signing password" />
        </el-form-item>
        <el-form-item label="Reason for Signing" prop="reason">
          <el-input v-model="signForm.reason" type="textarea" :rows="2" placeholder="Enter reason for signing" />
        </el-form-item>
        <el-form-item label="Signature Position">
          <el-row>
            <el-col :span="12">
              <el-input v-model="signForm.positionX" placeholder="X position" />
            </el-col>
            <el-col :span="12">
              <el-input v-model="signForm.positionY" placeholder="Y position" />
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="signDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="signing" @click="submitSign">Sign Document</el-button>
      </template>
    </el-dialog>

    <!-- Signature Details Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="currentSignature?.documentName" width="700px" destroy-on-close>
      <div class="signature-detail">
        <div class="detail-header">
          <div class="signature-status">
            <el-tag :type="getStatusTag(currentSignature?.status || '')" size="large">{{ currentSignature?.status }}</el-tag>
          </div>
          <div class="signature-id">Signature ID: {{ currentSignature?.id }}</div>
        </div>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="Document Name">{{ currentSignature?.documentName }}</el-descriptions-item>
          <el-descriptions-item label="Document Type">{{ currentSignature?.documentType }}</el-descriptions-item>
          <el-descriptions-item label="Signer">{{ currentSignature?.signer }}</el-descriptions-item>
          <el-descriptions-item label="Signer Role">{{ currentSignature?.signerRole }}</el-descriptions-item>
          <el-descriptions-item label="Signer Email">{{ currentSignature?.signerEmail }}</el-descriptions-item>
          <el-descriptions-item label="Signed At">{{ currentSignature?.signedAt }}</el-descriptions-item>
          <el-descriptions-item label="Expires At">{{ currentSignature?.expiresAt }}</el-descriptions-item>
          <el-descriptions-item label="Signature Type">{{ currentSignature?.signatureType }}</el-descriptions-item>
          <el-descriptions-item label="Certificate ID" :span="2">{{ currentSignature?.certificateId }}</el-descriptions-item>
          <el-descriptions-item label="Hash Value" :span="2">
            <span class="hash-value">{{ currentSignature?.hash }}</span>
            <el-button link size="small" @click="copyHash">Copy</el-button>
          </el-descriptions-item>
          <el-descriptions-item label="Reason" :span="2">{{ currentSignature?.reason || 'No reason provided' }}</el-descriptions-item>
          <el-descriptions-item label="IP Address">{{ currentSignature?.ipAddress }}</el-descriptions-item>
          <el-descriptions-item label="Device Info">{{ currentSignature?.deviceInfo }}</el-descriptions-item>
        </el-descriptions>

        <div class="signature-timeline">
          <h4>Audit Trail</h4>
          <el-timeline>
            <el-timeline-item
                v-for="event in currentSignature?.auditTrail"
                :key="event.id"
                :timestamp="event.timestamp"
                :type="event.type"
            >
              {{ event.description }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadSignatureCertificate">Download Certificate</el-button>
        <el-button type="success" @click="verifySignatureById(currentSignature)">Verify Again</el-button>
      </template>
    </el-dialog>

    <!-- Revoke Confirmation Dialog -->
    <el-dialog v-model="revokeDialogVisible" title="Revoke Signature" width="450px">
      <p>Are you sure you want to revoke the signature for document:</p>
      <p><strong>{{ revokeTarget?.documentName }}</strong></p>
      <el-input
          v-model="revokeReason"
          type="textarea"
          :rows="3"
          placeholder="Enter revocation reason"
          style="margin-top: 16px"
      />
      <p style="color: #f56c6c; font-size: 12px; margin-top: 16px">This action cannot be undone and will invalidate the signature.</p>
      <template #footer>
        <el-button @click="revokeDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmRevoke">Revoke Signature</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, Key, Lock, Files, Medal
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading digital signatures...',
  'Verifying certificates...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface DigitalSignature {
  id: string
  documentName: string
  documentType: string
  signer: string
  signerRole: string
  signerEmail: string
  status: string
  signatureType: string
  signedAt: string
  expiresAt: string
  certificateId: string
  hash: string
  reason: string
  ipAddress: string
  deviceInfo: string
  auditTrail: Array<{ id: number; timestamp: string; description: string; type: string }>
}

interface Certificate {
  name: string
  icon: string
  status: string
  expiryDate: string
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Signatures', value: 342, trend: 15, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Valid Signatures', value: 298, trend: 12, icon: 'Checked', bgColor: '#67c23a', key: 'valid' },
  { title: 'Pending Signatures', value: 28, trend: -5, icon: 'Clock', bgColor: '#e6a23c', key: 'pending' },
  { title: 'Revoked', value: 16, trend: 8, icon: 'Delete', bgColor: '#f56c6c', key: 'revoked' }
])

const certificates = ref<Certificate[]>([
  { name: 'Root CA Certificate', icon: 'Key', status: 'Valid', expiryDate: '2026-12-31' },
  { name: 'Organization CA', icon: 'Lock', status: 'Valid', expiryDate: '2025-06-30' },
  { name: 'User Signing Cert', icon: 'Files', status: 'Valid', expiryDate: '2024-12-31' },
  { name: 'Document Signing', icon: 'Medal', status: 'Expiring Soon', expiryDate: '2024-03-15' }
])

const signatures = ref<DigitalSignature[]>([
  {
    id: 'SIG-2024-001',
    documentName: 'Chiller Overhaul Approval',
    documentType: 'Decision Approval',
    signer: 'John Smith',
    signerRole: 'Facility Manager',
    signerEmail: 'john.smith@ibms.com',
    status: 'Valid',
    signatureType: 'Digital Signature',
    signedAt: '2024-01-05 14:30:00',
    expiresAt: '2025-01-05 14:30:00',
    certificateId: 'CERT-A1B2C3D4',
    hash: '8f7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e',
    reason: 'Approval of chiller overhaul project',
    ipAddress: '192.168.1.105',
    deviceInfo: 'Chrome 120.0 / Windows 11',
    auditTrail: [
      { id: 1, timestamp: '2024-01-05 14:25:00', description: 'Document uploaded for signing', type: 'primary' },
      { id: 2, timestamp: '2024-01-05 14:28:00', description: 'Identity verified via certificate', type: 'primary' },
      { id: 3, timestamp: '2024-01-05 14:30:00', description: 'Document signed by John Smith', type: 'success' },
      { id: 4, timestamp: '2024-01-05 14:30:15', description: 'Signature recorded on blockchain', type: 'success' }
    ]
  },
  {
    id: 'SIG-2024-002',
    documentName: 'LED Retrofit Contract',
    documentType: 'Contract',
    signer: 'Lisa Zhang',
    signerRole: 'Energy Manager',
    signerEmail: 'lisa.zhang@ibms.com',
    status: 'Valid',
    signatureType: 'Digital Signature',
    signedAt: '2024-01-08 11:15:00',
    expiresAt: '2025-01-08 11:15:00',
    certificateId: 'CERT-E5F6G7H8',
    hash: '7e6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6',
    reason: 'Contract approval for LED lighting retrofit',
    ipAddress: '192.168.1.112',
    deviceInfo: 'Safari 17.0 / macOS',
    auditTrail: [
      { id: 1, timestamp: '2024-01-08 11:00:00', description: 'Document uploaded for signing', type: 'primary' },
      { id: 2, timestamp: '2024-01-08 11:10:00', description: 'Identity verified via certificate', type: 'primary' },
      { id: 3, timestamp: '2024-01-08 11:15:00', description: 'Document signed by Lisa Zhang', type: 'success' }
    ]
  },
  {
    id: 'SIG-2024-003',
    documentName: 'ESG Compliance Report 2023',
    documentType: 'Compliance',
    signer: 'Emily Zhao',
    signerRole: 'ESG Manager',
    signerEmail: 'emily.zhao@ibms.com',
    status: 'Valid',
    signatureType: 'Digital Signature',
    signedAt: '2024-01-03 09:45:00',
    expiresAt: '2025-01-03 09:45:00',
    certificateId: 'CERT-I9J0K1L2',
    hash: '6d5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5',
    reason: 'Approval of annual ESG compliance report',
    ipAddress: '192.168.1.98',
    deviceInfo: 'Chrome 120.0 / Windows 11',
    auditTrail: [
      { id: 1, timestamp: '2024-01-03 09:30:00', description: 'Document uploaded for signing', type: 'primary' },
      { id: 2, timestamp: '2024-01-03 09:40:00', description: 'Identity verified via certificate', type: 'primary' },
      { id: 3, timestamp: '2024-01-03 09:45:00', description: 'Document signed by Emily Zhao', type: 'success' }
    ]
  },
  {
    id: 'SIG-2024-004',
    documentName: 'Financial Audit Report Q4',
    documentType: 'Financial',
    signer: 'Anna Kim',
    signerRole: 'Finance Controller',
    signerEmail: 'anna.kim@ibms.com',
    status: 'Valid',
    signatureType: 'Digital Signature',
    signedAt: '2024-01-10 16:20:00',
    expiresAt: '2025-01-10 16:20:00',
    certificateId: 'CERT-M3N4O5P6',
    hash: '5c4b3a2f1e0d9c8b7a6f5e4d3c2b1a0f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4',
    reason: 'Approval of Q4 financial audit',
    ipAddress: '192.168.1.120',
    deviceInfo: 'Edge 120.0 / Windows 11',
    auditTrail: [
      { id: 1, timestamp: '2024-01-10 16:00:00', description: 'Document uploaded for signing', type: 'primary' },
      { id: 2, timestamp: '2024-01-10 16:15:00', description: 'Identity verified via certificate', type: 'primary' },
      { id: 3, timestamp: '2024-01-10 16:20:00', description: 'Document signed by Anna Kim', type: 'success' }
    ]
  },
  {
    id: 'SIG-2024-005',
    documentName: 'UPS Replacement Authorization',
    documentType: 'Decision Approval',
    signer: 'Tom Harris',
    signerRole: 'IT Director',
    signerEmail: 'tom.harris@ibms.com',
    status: 'Pending',
    signatureType: 'Digital Signature',
    signedAt: '',
    expiresAt: '2024-02-10 00:00:00',
    certificateId: 'PENDING',
    hash: '',
    reason: 'Awaiting approval',
    ipAddress: '',
    deviceInfo: '',
    auditTrail: [
      { id: 1, timestamp: '2024-01-20 10:00:00', description: 'Document uploaded for signing', type: 'primary' },
      { id: 2, timestamp: '2024-01-20 10:00:00', description: 'Signature request sent to Tom Harris', type: 'warning' }
    ]
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const signing = ref(false)
const signDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const revokeDialogVisible = ref(false)
const currentSignature = ref<DigitalSignature | null>(null)
const revokeTarget = ref<DigitalSignature | null>(null)
const revokeReason = ref('')
const verificationCode = ref('')
const verificationResult = ref<any>(null)
const signFormRef = ref()
const signUploadRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  status: '',
  signatureType: '',
  dateRange: null as [Date, Date] | null
})

const signForm = reactive({
  document: null as File | null,
  documentName: '',
  documentType: '',
  signerName: '',
  signerRole: '',
  signerEmail: '',
  password: '',
  reason: '',
  positionX: '100',
  positionY: '500'
})

const signRules = {
  documentName: [{ required: true, message: 'Please enter document name', trigger: 'blur' }],
  documentType: [{ required: true, message: 'Please select document type', trigger: 'change' }],
  signerName: [{ required: true, message: 'Please enter signer name', trigger: 'blur' }],
  signerRole: [{ required: true, message: 'Please enter signer role', trigger: 'blur' }],
  signerEmail: [{ required: true, message: 'Please enter signer email', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredSignatures = computed(() => {
  let filtered = [...signatures.value]

  if (filters.keyword) {
    filtered = filtered.filter(s =>
        s.documentName.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        s.signer.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.status) {
    filtered = filtered.filter(s => s.status === filters.status)
  }

  if (filters.signatureType) {
    filtered = filtered.filter(s => s.documentType === filters.signatureType)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(s => {
      const date = new Date(s.signedAt)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedSignatures = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSignatures.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getDocumentTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Decision Approval': 'primary',
    'Contract': 'success',
    'Compliance': 'warning',
    'Financial': 'danger'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Valid': 'success',
    'Expired': 'danger',
    'Revoked': 'danger',
    'Pending': 'warning'
  }
  return map[status] || 'info'
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.status = ''
  filters.signatureType = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting audit log for ${filteredSignatures.value.length} signatures...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchSignatures = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleRefreshCertificate = () => {
  ElMessage.success('Certificate status refreshed')
}

const handleSignDocument = () => {
  signDialogVisible.value = true
}

const handleSignFileChange = (file: any) => {
  signForm.document = file.raw
}

const submitSign = async () => {
  if (!signFormRef.value) return
  await signFormRef.value.validate((valid: boolean) => {
    if (valid) {
      signing.value = true
      setTimeout(() => {
        signing.value = false
        signDialogVisible.value = false
        ElMessage.success(`Document "${signForm.documentName}" signed successfully`)

        const newSignature: DigitalSignature = {
          id: `SIG-2024-${Math.floor(Math.random() * 900 + 100)}`,
          documentName: signForm.documentName,
          documentType: signForm.documentType,
          signer: signForm.signerName,
          signerRole: signForm.signerRole,
          signerEmail: signForm.signerEmail,
          status: 'Valid',
          signatureType: 'Digital Signature',
          signedAt: new Date().toLocaleString(),
          expiresAt: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toLocaleString(),
          certificateId: `CERT-${Math.random().toString(36).substring(2, 10).toUpperCase()}`,
          hash: Array.from({ length: 64 }, () => Math.random().toString(16)[2]).join(''),
          reason: signForm.reason,
          ipAddress: '192.168.1.1',
          deviceInfo: 'Chrome / Windows',
          auditTrail: [
            { id: 1, timestamp: new Date().toLocaleString(), description: 'Document signed', type: 'success' }
          ]
        }
        signatures.value.unshift(newSignature)

        signFormRef.value?.resetFields()
        signUploadRef.value?.clearFiles()
      }, 2000)
    }
  })
}

const viewSignature = (signature: DigitalSignature) => {
  currentSignature.value = signature
  detailDialogVisible.value = true
}

const verifySignature = () => {
  if (!verificationCode.value) {
    ElMessage.warning('Please enter a signature ID or hash')
    return
  }

  const found = signatures.value.find(s => s.id === verificationCode.value || s.hash === verificationCode.value)

  if (found) {
    verificationResult.value = {
      valid: found.status === 'Valid',
      message: found.status === 'Valid' ? 'Signature is valid' : 'Signature is invalid or expired',
      signer: found.signer,
      signedAt: found.signedAt,
      certId: found.certificateId,
      hash: found.hash.substring(0, 32) + '...'
    }
  } else {
    verificationResult.value = {
      valid: false,
      message: 'Signature not found or invalid'
    }
  }
}

const verifySignatureById = (signature: DigitalSignature | null) => {
  if (signature) {
    verificationResult.value = {
      valid: signature.status === 'Valid',
      message: signature.status === 'Valid' ? 'Signature is valid' : 'Signature is invalid or expired',
      signer: signature.signer,
      signedAt: signature.signedAt,
      certId: signature.certificateId,
      hash: signature.hash.substring(0, 32) + '...'
    }
    ElMessage.success('Verification completed')
  }
}

const handleFileUpload = (file: any) => {
  ElMessage.info(`File "${file.name}" uploaded. Simulating verification...`)
  setTimeout(() => {
    verificationResult.value = {
      valid: true,
      message: 'File signature verified successfully',
      signer: 'John Smith',
      signedAt: '2024-01-15 10:30:00',
      certId: 'CERT-TEST123',
      hash: '7f3e8d2c1b4a6f9e0d8c7b6a5f4e3d2c...'
    }
  }, 1000)
}

const downloadCertificate = (signature: DigitalSignature) => {
  ElMessage.success(`Downloading certificate for: ${signature.documentName}`)
}

const downloadSignatureCertificate = () => {
  if (currentSignature.value) {
    ElMessage.success(`Downloading certificate for: ${currentSignature.value.documentName}`)
  }
}

const revokeSignature = (signature: DigitalSignature) => {
  revokeTarget.value = signature
  revokeReason.value = ''
  revokeDialogVisible.value = true
}

const confirmRevoke = () => {
  if (revokeTarget.value && revokeReason.value) {
    const index = signatures.value.findIndex(s => s.id === revokeTarget.value!.id)
    if (index !== -1) {
      signatures.value[index].status = 'Revoked'
      signatures.value[index].auditTrail.push({
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        description: `Signature revoked. Reason: ${revokeReason.value}`,
        type: 'danger'
      })
      ElMessage.warning(`Revoked signature for: ${revokeTarget.value.documentName}`)
    }
  } else if (!revokeReason.value) {
    ElMessage.warning('Please enter a revocation reason')
    return
  }
  revokeDialogVisible.value = false
  revokeTarget.value = null
  revokeReason.value = ''
}

const copyHash = () => {
  if (currentSignature.value?.hash) {
    navigator.clipboard.writeText(currentSignature.value.hash)
    ElMessage.success('Hash copied to clipboard')
  }
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
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
      fetchSignatures()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

/* ==================== Main Page Styles ==================== */
.signatures-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.certificate-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.certificate-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;

  .cert-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .cert-info {
    flex: 1;

    .cert-name {
      font-weight: 600;
      font-size: 14px;
      color: #303133;
      margin-bottom: 4px;
    }

    .cert-status {
      margin-bottom: 4px;
    }

    .cert-expiry {
      font-size: 11px;
      color: #909399;
    }
  }
}

.verification-card {
  margin-bottom: 20px;

  .verification-result {
    margin-top: 20px;

    .result-details {
      margin-top: 12px;
      font-size: 13px;

      p {
        margin: 4px 0;
      }
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.signature-detail {
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;

    .signature-id {
      font-family: monospace;
      color: #909399;
    }
  }

  .hash-value {
    font-family: monospace;
    font-size: 12px;
    word-break: break-all;
  }

  .signature-timeline {
    margin-top: 24px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin-bottom: 16px;
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}

:deep(.el-descriptions) {
  margin-top: 0;
}
</style>