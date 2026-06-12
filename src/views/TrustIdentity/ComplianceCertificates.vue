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
        <div class="loading-tip">Trust & Identity - Compliance Certificates</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="compliance-certificates-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Compliance Certificates</h1>
        <p>Manage and verify compliance certificates with blockchain-anchored proof</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openUploadDialog">
          <el-icon><Plus /></el-icon>
          Upload Certificate
        </el-button>
        <el-button @click="openRenewalDialog">
          <el-icon><Refresh /></el-icon>
          Bulk Renewal
        </el-button>
        <el-button @click="exportCertificates">
          <el-icon><Download /></el-icon>
          Export Report
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
            <div class="stat-value">{{ stats.totalCertificates }}</div>
            <div class="stat-label">Total Certificates</div>
            <div class="stat-trend">+{{ stats.newThisMonth }} this month</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeCertificates }}</div>
            <div class="stat-label">Active</div>
            <div class="stat-trend">Valid certificates</div>
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
            <div class="stat-trend">Within 30 days</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.anchoredCertificates }}</div>
            <div class="stat-label">Blockchain Anchored</div>
            <div class="stat-trend">Immutable proof</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Certificate Standards Overview -->
    <div class="standards-card">
      <div class="card-header">
        <h3>Certificate Standards Coverage</h3>
      </div>
      <div class="standards-grid">
        <div v-for="standard in certificateStandards" :key="standard.name" class="standard-item">
          <div class="standard-icon" :class="standard.status">
            <el-icon><component :is="standard.icon" /></el-icon>
          </div>
          <div class="standard-info">
            <div class="standard-name">{{ standard.name }}</div>
            <div class="standard-count">{{ standard.count }} certificates</div>
          </div>
          <div class="standard-status">
            <el-tag :type="standard.status === 'compliant' ? 'success' : 'warning'" size="small">
              {{ standard.status === 'compliant' ? 'Compliant' : 'Partial' }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Search & Filter -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by certificate ID, name, or issuer..."
          clearable
          style="width: 260px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option label="All Status" value="" />
        <el-option label="Active" value="active" />
        <el-option label="Expired" value="expired" />
        <el-option label="Revoked" value="revoked" />
        <el-option label="Pending" value="pending" />
      </el-select>
      <el-select v-model="filters.type" placeholder="Standard" clearable style="width: 160px">
        <el-option label="All Standards" value="" />
        <el-option label="ISO 27001" value="iso27001" />
        <el-option label="ISO 9001" value="iso9001" />
        <el-option label="SOC 2" value="soc2" />
        <el-option label="GDPR" value="gdpr" />
        <el-option label="PCI DSS" value="pci" />
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

    <!-- Certificates Grid -->
    <div class="certificates-grid-wrapper">
      <div class="grid-header">
        <span class="grid-title">Certificate Inventory</span>
        <div class="grid-view-toggle">
          <el-button-group>
            <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" @click="viewMode = 'grid'">
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button :type="viewMode === 'list' ? 'primary' : 'default'" @click="viewMode = 'list'">
              <el-icon><List /></el-icon>
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="certificates-grid">
        <div
            v-for="cert in filteredCertificates"
            :key="cert.id"
            class="certificate-card"
            :class="{ 'status-expired': cert.status === 'expired', 'status-revoked': cert.status === 'revoked' }"
            @click="viewCertificate(cert)"
        >
          <div class="certificate-header">
            <div class="certificate-icon" :class="getStandardIconClass(cert.standard)">
              <el-icon><component :is="getStandardIcon(cert.standard)" /></el-icon>
            </div>
            <div class="certificate-status">
              <el-tag :type="getStatusTagType(cert.status)" size="small">
                {{ cert.status }}
              </el-tag>
            </div>
          </div>
          <div class="certificate-body">
            <div class="certificate-name">{{ cert.name }}</div>
            <div class="certificate-standard">{{ cert.standard }}</div>
            <div class="certificate-meta">
              <div class="meta-item">
                <el-icon><User /></el-icon>
                <span>{{ cert.issuer }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Calendar /></el-icon>
                <span>Issued: {{ cert.issuedDate }}</span>
              </div>
              <div class="meta-item" :class="{ 'expiring': isExpiringSoon(cert.expiryDate) }">
                <el-icon><Clock /></el-icon>
                <span>Expires: {{ cert.expiryDate }}</span>
              </div>
            </div>
            <div class="certificate-progress">
              <div class="progress-label">Validity Period</div>
              <el-progress :percentage="getValidityPercentage(cert)" :stroke-width="6" :color="getProgressColor(cert)" />
            </div>
          </div>
          <div class="certificate-footer">
            <el-button size="small" @click.stop="viewCertificate(cert)">
              <el-icon><View /></el-icon>
              Details
            </el-button>
            <el-button size="small" type="primary" @click.stop="verifyCertificate(cert)">
              <el-icon><Search /></el-icon>
              Verify
            </el-button>
            <el-dropdown trigger="click" @command="(cmd) => handleDropdown(cmd, cert)">
              <el-button size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="renew">Renew</el-dropdown-item>
                  <el-dropdown-item command="download">Download PDF</el-dropdown-item>
                  <el-dropdown-item command="anchor">Anchor to Blockchain</el-dropdown-item>
                  <el-dropdown-item command="revoke" divided>
                    <span style="color: #f56c6c">Revoke</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="certificates-list">
        <el-table :data="filteredCertificates" stripe style="width: 100%">
          <el-table-column prop="id" label="Certificate ID" width="120" />
          <el-table-column prop="name" label="Certificate Name" min-width="200" show-overflow-tooltip />
          <el-table-column prop="standard" label="Standard" width="120" />
          <el-table-column prop="issuer" label="Issuer" width="160" />
          <el-table-column prop="issuedDate" label="Issued Date" width="110" />
          <el-table-column prop="expiryDate" label="Expiry Date" width="110">
            <template #default="{ row }">
              <span :class="{ 'expiring-text': isExpiringSoon(row.expiryDate) }">
                {{ row.expiryDate }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Blockchain" width="80">
            <template #default="{ row }">
              <el-icon v-if="row.anchored" color="#67c23a"><CircleCheck /></el-icon>
              <el-button v-else link type="primary" size="small" @click.stop="anchorCertificate(row)">Anchor</el-button>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click.stop="viewCertificate(row)">
                Details
              </el-button>
              <el-button link type="success" size="small" @click.stop="verifyCertificate(row)">
                Verify
              </el-button>
              <el-dropdown trigger="click" @command="(cmd) => handleDropdown(cmd, row)">
                <el-button link size="small">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="renew">Renew</el-dropdown-item>
                    <el-dropdown-item command="download">Download PDF</el-dropdown-item>
                    <el-dropdown-item command="anchor">Anchor to Blockchain</el-dropdown-item>
                    <el-dropdown-item command="revoke" divided>Revoke</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[12, 24, 48]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Certificate Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.certificate?.name" width="750px" class="certificate-dialog">
      <div v-if="detailDialog.certificate" class="certificate-detail">
        <div class="detail-header">
          <div class="detail-icon" :class="getStandardIconClass(detailDialog.certificate.standard)">
            <el-icon><component :is="getStandardIcon(detailDialog.certificate.standard)" /></el-icon>
          </div>
          <div class="detail-title">
            <h2>{{ detailDialog.certificate.name }}</h2>
            <p>{{ detailDialog.certificate.standard }}</p>
          </div>
          <div class="detail-status">
            <el-tag :type="getStatusTagType(detailDialog.certificate.status)" size="large">
              {{ detailDialog.certificate.status }}
            </el-tag>
          </div>
        </div>

        <el-tabs v-model="detailTab">
          <el-tab-pane label="Certificate Details" name="details">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="Certificate ID">{{ detailDialog.certificate.id }}</el-descriptions-item>
              <el-descriptions-item label="Standard">{{ detailDialog.certificate.standard }}</el-descriptions-item>
              <el-descriptions-item label="Version">{{ detailDialog.certificate.version }}</el-descriptions-item>
              <el-descriptions-item label="Issuer">{{ detailDialog.certificate.issuer }}</el-descriptions-item>
              <el-descriptions-item label="Issued Date">{{ detailDialog.certificate.issuedDate }}</el-descriptions-item>
              <el-descriptions-item label="Expiry Date">{{ detailDialog.certificate.expiryDate }}</el-descriptions-item>
              <el-descriptions-item label="Scope" :span="2">{{ detailDialog.certificate.scope }}</el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">{{ detailDialog.certificate.description }}</el-descriptions-item>
            </el-descriptions>
          </el-tab-pane>

          <el-tab-pane label="Verification History" name="verification">
            <el-table :data="detailDialog.certificate.verificationHistory" stripe size="small">
              <el-table-column prop="date" label="Date" width="180" />
              <el-table-column prop="verifier" label="Verifier" width="180" />
              <el-table-column prop="result" label="Result" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.result === 'Valid' ? 'success' : 'danger'" size="small">
                    {{ row.result }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="method" label="Method" width="140" />
              <el-table-column prop="txHash" label="Transaction Hash" width="200" show-overflow-tooltip>
                <template #default="{ row }">
                  <code v-if="row.txHash">{{ row.txHash }}</code>
                  <span v-else>-</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="Blockchain Anchor" name="blockchain">
            <div v-if="detailDialog.certificate.blockchain" class="blockchain-info">
              <el-descriptions :column="2" border>
                <el-descriptions-item label="Transaction Hash">
                  <code>{{ detailDialog.certificate.blockchain.txHash }}</code>
                  <el-button link size="small" @click="viewOnExplorer(detailDialog.certificate.blockchain.txHash)">View</el-button>
                </el-descriptions-item>
                <el-descriptions-item label="Block Number">{{ detailDialog.certificate.blockchain.blockNumber }}</el-descriptions-item>
                <el-descriptions-item label="Network">{{ detailDialog.certificate.blockchain.network }}</el-descriptions-item>
                <el-descriptions-item label="Anchored At">{{ detailDialog.certificate.blockchain.timestamp }}</el-descriptions-item>
                <el-descriptions-item label="Anchor Type">SHA-256 Hash of Certificate</el-descriptions-item>
                <el-descriptions-item label="Status">
                  <el-tag type="success">Verified on Blockchain</el-tag>
                </el-descriptions-item>
              </el-descriptions>
            </div>
            <div v-else class="anchor-prompt">
              <el-empty description="Certificate not anchored to blockchain" />
              <el-button type="primary" @click="anchorCertificate(detailDialog.certificate)">Anchor Now</el-button>
            </div>
          </el-tab-pane>

          <el-tab-pane label="Audit Log" name="audit">
            <el-table :data="detailDialog.certificate.auditLog" stripe size="small">
              <el-table-column prop="timestamp" label="Timestamp" width="180" />
              <el-table-column prop="action" label="Action" width="140" />
              <el-table-column prop="user" label="User" width="160" />
              <el-table-column prop="details" label="Details" min-width="200" show-overflow-tooltip />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="detailDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="downloadCertificate(detailDialog.certificate)">
          <el-icon><Download /></el-icon>
          Download PDF
        </el-button>
      </template>
    </el-dialog>

    <!-- Upload Certificate Dialog -->
    <el-dialog v-model="uploadDialog.visible" title="Upload Certificate" width="550px">
      <el-form :model="uploadForm" label-width="110px">
        <el-form-item label="Certificate Name" required>
          <el-input v-model="uploadForm.name" placeholder="Enter certificate name" />
        </el-form-item>
        <el-form-item label="Standard" required>
          <el-select v-model="uploadForm.standard" style="width: 100%">
            <el-option label="ISO 27001 - Information Security" value="ISO 27001" />
            <el-option label="ISO 9001 - Quality Management" value="ISO 9001" />
            <el-option label="SOC 2 - Service Organization" value="SOC 2" />
            <el-option label="GDPR - Data Protection" value="GDPR" />
            <el-option label="PCI DSS - Payment Security" value="PCI DSS" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version">
          <el-input v-model="uploadForm.version" placeholder="e.g., 2022" />
        </el-form-item>
        <el-form-item label="Issuer" required>
          <el-input v-model="uploadForm.issuer" placeholder="Issuing authority" />
        </el-form-item>
        <el-form-item label="Issue Date" required>
          <el-date-picker v-model="uploadForm.issueDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Expiry Date" required>
          <el-date-picker v-model="uploadForm.expiryDate" type="date" placeholder="Select date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Scope">
          <el-input v-model="uploadForm.scope" type="textarea" :rows="2" placeholder="Certificate scope" />
        </el-form-item>
        <el-form-item label="Certificate File">
          <div class="upload-area" @click="triggerFileUpload">
            <el-icon><Upload /></el-icon>
            <span>Click to upload PDF</span>
            <input ref="pdfUploadRef" type="file" accept=".pdf" style="display: none" @change="handlePdfSelect" />
          </div>
          <div v-if="uploadFile" class="selected-file">
            <el-icon><Document /></el-icon>
            <span>{{ uploadFile.name }}</span>
            <el-button link type="danger" @click="uploadFile = null">Remove</el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="uploadCertificate" :loading="isUploading">Upload Certificate</el-button>
      </template>
    </el-dialog>

    <!-- Renewal Dialog -->
    <el-dialog v-model="renewalDialog.visible" title="Bulk Certificate Renewal" width="550px">
      <div class="renewal-info">
        <el-alert
            title="Certificates Pending Renewal"
            type="warning"
            :description="`${expiringCertificates.length} certificates expiring within 60 days`"
            show-icon
            :closable="false"
        />
      </div>
      <el-table :data="expiringCertificates" stripe size="small" max-height="300">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="name" label="Certificate Name" min-width="180" />
        <el-table-column prop="expiryDate" label="Expiry Date" width="110" />
        <el-table-column prop="standard" label="Standard" width="100" />
      </el-table>

      <el-form label-width="100px" style="margin-top: 20px">
        <el-form-item label="Renewal Period">
          <el-select v-model="renewalPeriod" style="width: 100%">
            <el-option label="1 Year" value="1" />
            <el-option label="2 Years" value="2" />
            <el-option label="3 Years" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Notify Stakeholders">
          <el-switch v-model="notifyStakeholders" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="renewalDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="processRenewal" :loading="isRenewing">Renew Selected</el-button>
      </template>
    </el-dialog>

    <!-- Verify Dialog -->
    <el-dialog v-model="verifyDialog.visible" title="Certificate Verification" width="500px">
      <div class="verify-content">
        <div class="verify-result" :class="verifyResult?.valid ? 'valid' : 'invalid'">
          <div class="result-icon">
            <el-icon v-if="verifyResult?.valid"><CircleCheck /></el-icon>
            <el-icon v-else><CircleClose /></el-icon>
          </div>
          <div class="result-text">
            <h3>{{ verifyResult?.valid ? 'Certificate Valid' : 'Certificate Invalid' }}</h3>
            <p>{{ verifyResult?.message }}</p>
          </div>
        </div>
        <div v-if="verifyResult?.details" class="verify-details">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Status">{{ verifyResult.details.status }}</el-descriptions-item>
            <el-descriptions-item label="Hash Match">{{ verifyResult.details.hashMatch ? 'Yes' : 'No' }}</el-descriptions-item>
            <el-descriptions-item label="Blockchain Verified">{{ verifyResult.details.blockchainVerified ? 'Yes' : 'No' }}</el-descriptions-item>
            <el-descriptions-item label="Valid Until">{{ verifyResult.details.validUntil }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Refresh,
  Download,
  Document,
  CircleCheck,
  Clock,
  Connection,
  Search,
  RefreshLeft,
  Grid,
  List,
  View,
  MoreFilled,
  User,
  Calendar,
  Upload,
  CircleClose,
  Warning,
  Check,
  Lock,
  Key,
  OfficeBuilding
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isUploading = ref(false)
const isRenewing = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading certificates...',
  'Verifying blockchain anchors...',
  'Almost ready...'
]

// ==================== 类型定义 ====================
interface ComplianceCertificate {
  id: string
  name: string
  standard: string
  version: string
  issuer: string
  issuedDate: string
  expiryDate: string
  status: 'active' | 'expired' | 'revoked' | 'pending'
  scope: string
  description: string
  anchored: boolean
  blockchain?: {
    txHash: string
    blockNumber: number
    network: string
    timestamp: string
  }
  verificationHistory: any[]
  auditLog: any[]
}

// ==================== 模拟数据 ====================
const stats = reactive({
  totalCertificates: 48,
  activeCertificates: 38,
  expiringSoon: 6,
  anchoredCertificates: 32,
  newThisMonth: 4
})

const certificateStandards = ref([
  { name: 'ISO 27001', icon: 'Lock', count: 12, status: 'compliant' },
  { name: 'ISO 9001', icon: 'Check', count: 8, status: 'compliant' },
  { name: 'SOC 2', icon: 'OfficeBuilding', count: 6, status: 'partial' },
  { name: 'GDPR', icon: 'Key', count: 10, status: 'compliant' },
  { name: 'PCI DSS', icon: 'Warning', count: 4, status: 'compliant' }
])

const certificates = ref<ComplianceCertificate[]>([
  {
    id: 'CERT-001',
    name: 'Information Security Management System',
    standard: 'ISO 27001',
    version: '2022',
    issuer: 'BSI Group',
    issuedDate: '2023-08-15',
    expiryDate: '2024-08-14',
    status: 'active',
    scope: 'All cloud infrastructure and data processing activities',
    description: 'Certification for information security management system compliance',
    anchored: true,
    blockchain: {
      txHash: '0x7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b',
      blockNumber: 18234567,
      network: 'Ethereum',
      timestamp: '2023-08-15 14:30:00'
    },
    verificationHistory: [
      { date: '2024-06-10 09:30:00', verifier: 'system', result: 'Valid', method: 'Blockchain' },
      { date: '2024-05-15 14:20:00', verifier: 'system', result: 'Valid', method: 'Auto-verify' }
    ],
    auditLog: [
      { timestamp: '2023-08-15 10:00:00', action: 'Upload', user: 'admin@ibms.com', details: 'Certificate uploaded' },
      { timestamp: '2023-08-15 10:05:00', action: 'Anchored', user: 'system', details: 'Hash anchored to blockchain' }
    ]
  },
  {
    id: 'CERT-002',
    name: 'Quality Management System',
    standard: 'ISO 9001',
    version: '2015',
    issuer: 'TÜV SÜD',
    issuedDate: '2023-06-01',
    expiryDate: '2024-05-31',
    status: 'active',
    scope: 'Product development and quality assurance processes',
    description: 'Quality management certification',
    anchored: true,
    blockchain: {
      txHash: '0x8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
      blockNumber: 18234123,
      network: 'Ethereum',
      timestamp: '2023-06-01 11:00:00'
    },
    verificationHistory: [],
    auditLog: []
  },
  {
    id: 'CERT-003',
    name: 'SOC 2 Type II Report',
    standard: 'SOC 2',
    version: '2023',
    issuer: 'Deloitte',
    issuedDate: '2024-01-15',
    expiryDate: '2024-07-14',
    status: 'active',
    scope: 'Security, Availability, and Confidentiality trust principles',
    description: 'Service organization controls report',
    anchored: true,
    blockchain: {
      txHash: '0x9c8b7a6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8c',
      blockNumber: 18235123,
      network: 'Polygon',
      timestamp: '2024-01-15 09:45:00'
    },
    verificationHistory: [],
    auditLog: []
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
  pageSize: 12,
  total: 0
})

const viewMode = ref<'grid' | 'list'>('grid')
const detailTab = ref('details')

const detailDialog = reactive({
  visible: false,
  certificate: null as ComplianceCertificate | null
})

const uploadDialog = reactive({
  visible: false
})

const renewalDialog = reactive({
  visible: false
})

const verifyDialog = reactive({
  visible: false
})

const verifyResult = ref<any>(null)

const uploadForm = reactive({
  name: '',
  standard: '',
  version: '',
  issuer: '',
  issueDate: null as Date | null,
  expiryDate: null as Date | null,
  scope: ''
})

const uploadFile = ref<File | null>(null)
const pdfUploadRef = ref<HTMLInputElement | null>(null)
const renewalPeriod = ref('1')
const notifyStakeholders = ref(true)

// ==================== 计算属性 ====================
const filteredCertificates = computed(() => {
  let filtered = [...certificates.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(c =>
        c.id.toLowerCase().includes(searchLower) ||
        c.name.toLowerCase().includes(searchLower) ||
        c.issuer.toLowerCase().includes(searchLower)
    )
  }

  if (filters.status) {
    filtered = filtered.filter(c => c.status === filters.status)
  }

  if (filters.type) {
    filtered = filtered.filter(c => c.standard === filters.type)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(c => {
      const date = new Date(c.issuedDate)
      return date >= start && date <= end
    })
  }

  pagination.total = filtered.length
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

const expiringCertificates = computed(() => {
  const sixtyDaysFromNow = new Date()
  sixtyDaysFromNow.setDate(sixtyDaysFromNow.getDate() + 60)
  return certificates.value.filter(c => {
    const expiry = new Date(c.expiryDate)
    return expiry <= sixtyDaysFromNow && c.status === 'active'
  })
})

// ==================== 辅助函数 ====================
const getStandardIcon = (standard: string) => {
  const map: Record<string, any> = {
    'ISO 27001': Lock,
    'ISO 9001': Check,
    'SOC 2': OfficeBuilding,
    'GDPR': Key,
    'PCI DSS': Warning
  }
  return map[standard] || Document
}

const getStandardIconClass = (standard: string) => {
  const map: Record<string, string> = {
    'ISO 27001': 'iso27001',
    'ISO 9001': 'iso9001',
    'SOC 2': 'soc2',
    'GDPR': 'gdpr',
    'PCI DSS': 'pci'
  }
  return map[standard] || 'default'
}

const getStatusTagType = (status: string) => {
  const map: Record<string, string> = {
    'active': 'success',
    'expired': 'danger',
    'revoked': 'info',
    'pending': 'warning'
  }
  return map[status] || 'info'
}

const isExpiringSoon = (expiryDate: string) => {
  const expiry = new Date(expiryDate)
  const thirtyDaysFromNow = new Date()
  thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30)
  return expiry <= thirtyDaysFromNow && expiry > new Date()
}

const getValidityPercentage = (cert: ComplianceCertificate) => {
  const issued = new Date(cert.issuedDate).getTime()
  const expiry = new Date(cert.expiryDate).getTime()
  const now = new Date().getTime()
  const total = expiry - issued
  const elapsed = now - issued
  const remaining = Math.max(0, total - elapsed)
  return Math.floor((remaining / total) * 100)
}

const getProgressColor = (cert: ComplianceCertificate) => {
  const percentage = getValidityPercentage(cert)
  if (percentage > 60) return '#67c23a'
  if (percentage > 30) return '#e6a23c'
  return '#f56c6c'
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

const viewCertificate = (cert: ComplianceCertificate) => {
  detailDialog.certificate = cert
  detailTab.value = 'details'
  detailDialog.visible = true
}

const verifyCertificate = (cert: ComplianceCertificate) => {
  verifyResult.value = {
    valid: cert.status === 'active',
    message: cert.status === 'active'
        ? 'Certificate is valid and has not been tampered with.'
        : 'Certificate is invalid or has expired.',
    details: {
      status: cert.status,
      hashMatch: true,
      blockchainVerified: cert.anchored,
      validUntil: cert.expiryDate
    }
  }
  verifyDialog.visible = true
}

const anchorCertificate = (cert: ComplianceCertificate) => {
  ElMessage.success(`Anchoring certificate ${cert.id} to blockchain...`)
  setTimeout(() => {
    cert.anchored = true
    cert.blockchain = {
      txHash: `0x${Math.random().toString(36).substring(2, 10)}...`,
      blockNumber: 18235000 + Math.floor(Math.random() * 1000),
      network: 'Ethereum',
      timestamp: new Date().toLocaleString()
    }
    stats.anchoredCertificates++
    ElMessage.success(`Certificate ${cert.id} anchored to blockchain`)
  }, 1500)
}

const downloadCertificate = (cert: ComplianceCertificate) => {
  ElMessage.success(`Downloading ${cert.name}.pdf`)
}

const handleDropdown = (command: string, cert: ComplianceCertificate) => {
  if (command === 'renew') {
    ElMessage.info(`Renewing certificate ${cert.id}`)
  } else if (command === 'download') {
    downloadCertificate(cert)
  } else if (command === 'anchor') {
    anchorCertificate(cert)
  } else if (command === 'revoke') {
    ElMessageBox.confirm(
        `Are you sure you want to revoke ${cert.name}? This action cannot be undone.`,
        'Confirm Revocation',
        { confirmButtonText: 'Revoke', type: 'warning' }
    ).then(() => {
      cert.status = 'revoked'
      stats.activeCertificates--
      ElMessage.success(`Certificate ${cert.id} revoked`)
    }).catch(() => {})
  }
}

const triggerFileUpload = () => {
  pdfUploadRef.value?.click()
}

const handlePdfSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    uploadFile.value = input.files[0]
  }
}

const uploadCertificate = async () => {
  if (!uploadForm.name || !uploadForm.standard || !uploadForm.issuer || !uploadForm.issueDate || !uploadForm.expiryDate) {
    ElMessage.warning('Please fill all required fields')
    return
  }

  isUploading.value = true
  await new Promise(resolve => setTimeout(resolve, 1500))

  const newCert: ComplianceCertificate = {
    id: `CERT-${String(certificates.value.length + 1).padStart(3, '0')}`,
    name: uploadForm.name,
    standard: uploadForm.standard,
    version: uploadForm.version || '1.0',
    issuer: uploadForm.issuer,
    issuedDate: uploadForm.issueDate.toISOString().slice(0, 10),
    expiryDate: uploadForm.expiryDate.toISOString().slice(0, 10),
    status: 'pending',
    scope: uploadForm.scope || 'Not specified',
    description: `Certificate for ${uploadForm.standard} compliance`,
    anchored: false,
    verificationHistory: [],
    auditLog: [
      { timestamp: new Date().toLocaleString(), action: 'Upload', user: 'admin@ibms.com', details: 'Certificate uploaded' }
    ]
  }

  certificates.value.unshift(newCert)
  stats.totalCertificates++
  stats.activeCertificates++

  isUploading.value = false
  uploadDialog.visible = false
  uploadForm.name = ''
  uploadForm.standard = ''
  uploadForm.version = ''
  uploadForm.issuer = ''
  uploadForm.issueDate = null
  uploadForm.expiryDate = null
  uploadForm.scope = ''
  uploadFile.value = null

  ElMessage.success('Certificate uploaded successfully')
}

const openUploadDialog = () => {
  uploadForm.name = ''
  uploadForm.standard = ''
  uploadForm.version = ''
  uploadForm.issuer = ''
  uploadForm.issueDate = null
  uploadForm.expiryDate = null
  uploadForm.scope = ''
  uploadFile.value = null
  uploadDialog.visible = true
}

const openRenewalDialog = () => {
  if (expiringCertificates.value.length === 0) {
    ElMessage.info('No certificates expiring soon')
    return
  }
  renewalDialog.visible = true
}

const processRenewal = async () => {
  isRenewing.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  expiringCertificates.value.forEach(cert => {
    const expiry = new Date(cert.expiryDate)
    expiry.setFullYear(expiry.getFullYear() + parseInt(renewalPeriod.value))
    cert.expiryDate = expiry.toISOString().slice(0, 10)
    cert.status = 'active'
    cert.auditLog.unshift({
      timestamp: new Date().toLocaleString(),
      action: 'Renewed',
      user: 'admin@ibms.com',
      details: `Renewed for ${renewalPeriod.value} year(s)`
    })
  })

  isRenewing.value = false
  renewalDialog.visible = false
  ElMessage.success(`${expiringCertificates.value.length} certificates renewed successfully`)
}

const exportCertificates = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    certificates: certificates.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `certificates-export-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Certificates exported')
}

const viewOnExplorer = (txHash: string) => {
  window.open(`https://etherscan.io/tx/${txHash}`, '_blank')
}

// ==================== 数据加载 ====================
const loadData = () => {
  // Data already loaded
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
.compliance-certificates-page {
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
  color: #8c9aab;
  margin-top: 2px;
}

/* Standards Card */
.standards-card {
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

.standards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.standard-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.standard-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.standard-icon.iso27001 { background-color: #ecf5ff; color: #409eff; }
.standard-icon.iso9001 { background-color: #f0f9eb; color: #67c23a; }
.standard-icon.soc2 { background-color: #fff3e0; color: #e6a23c; }
.standard-icon.gdpr { background-color: #fef0f0; color: #f56c6c; }
.standard-icon.pci { background-color: #f5f7fa; color: #8c9aab; }

.standard-info {
  flex: 1;
}

.standard-name {
  font-weight: 600;
  font-size: 13px;
}

.standard-count {
  font-size: 11px;
  color: #8c9aab;
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

/* Certificates Grid */
.certificates-grid-wrapper {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.grid-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.certificates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.certificate-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #ebeef5;
  overflow: hidden;
  transition: all 0.2s;
  cursor: pointer;
}

.certificate-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.certificate-card.status-expired {
  opacity: 0.7;
  border-left: 3px solid #f56c6c;
}

.certificate-card.status-revoked {
  opacity: 0.6;
  border-left: 3px solid #909399;
}

.certificate-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 0 16px;
}

.certificate-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.certificate-icon.iso27001 { background-color: #ecf5ff; color: #409eff; }
.certificate-icon.iso9001 { background-color: #f0f9eb; color: #67c23a; }
.certificate-icon.soc2 { background-color: #fff3e0; color: #e6a23c; }
.certificate-icon.gdpr { background-color: #fef0f0; color: #f56c6c; }

.certificate-body {
  padding: 16px;
}

.certificate-name {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
}

.certificate-standard {
  font-size: 12px;
  color: #8c9aab;
  margin-bottom: 12px;
}

.certificate-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #5e6e82;
}

.meta-item.expiring {
  color: #f56c6c;
}

.meta-item .el-icon {
  font-size: 12px;
}

.certificate-progress {
  margin-top: 8px;
}

.progress-label {
  font-size: 10px;
  color: #8c9aab;
  margin-bottom: 4px;
}

.certificate-footer {
  display: flex;
  gap: 8px;
  padding: 12px 16px 16px 16px;
  border-top: 1px solid #ebeef5;
  flex-wrap: wrap;
}

/* List View */
.certificates-list {
  width: 100%;
}

.expiring-text {
  color: #f56c6c;
  font-weight: 500;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* Certificate Detail Dialog */
.certificate-dialog :deep(.el-dialog__body) {
  max-height: 65vh;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.detail-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.detail-icon.iso27001 { background-color: #ecf5ff; color: #409eff; }
.detail-icon.iso9001 { background-color: #f0f9eb; color: #67c23a; }

.detail-title {
  flex: 1;
}

.detail-title h2 {
  margin: 0 0 4px 0;
  font-size: 18px;
}

.detail-title p {
  margin: 0;
  font-size: 13px;
  color: #8c9aab;
}

.blockchain-info {
  padding: 8px 0;
}

.anchor-prompt {
  text-align: center;
  padding: 40px;
}

/* Upload Dialog */
.upload-area {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  padding: 16px;
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
  margin-top: 8px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

/* Verify Dialog */
.verify-result {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
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

.result-text h3 {
  margin: 0 0 4px 0;
}

.result-text p {
  margin: 0;
  font-size: 13px;
}

.verify-details {
  padding: 8px 0;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}
</style>