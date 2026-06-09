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
        <div class="loading-tip">Document Evidence Repository</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="documents-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Evidence Repository</el-breadcrumb-item>
            <el-breadcrumb-item>Documents</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Document Evidence Repository</h1>
        <p class="description">Manage and organize document evidence including reports, contracts, certificates, and technical documentation</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleUploadDocument">
          <el-icon><Plus /></el-icon>
          Upload Document
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

    <!-- Quick Access - Document Types -->
    <el-card class="quick-access-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Quick Access by Type</span>
        </div>
      </template>
      <div class="quick-access-grid">
        <div v-for="type in documentTypes" :key="type.name" class="quick-access-item" @click="filterByType(type.name)">
          <div class="type-icon" :style="{ background: type.color }">
            <el-icon :size="24"><component :is="type.icon" /></el-icon>
          </div>
          <div class="type-info">
            <div class="type-name">{{ type.name }}</div>
            <div class="type-count">{{ getDocumentCountByType(type.name) }} documents</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by title or description"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.documentType" placeholder="Document Type" clearable style="width: 150px">
            <el-option label="Report" value="Report" />
            <el-option label="Contract" value="Contract" />
            <el-option label="Certificate" value="Certificate" />
            <el-option label="Technical Spec" value="Technical Spec" />
            <el-option label="Manual" value="Manual" />
            <el-option label="Policy" value="Policy" />
            <el-option label="Invoice" value="Invoice" />
            <el-option label="Drawing" value="Drawing" />
          </el-select>
          <el-select v-model="filters.format" placeholder="Format" clearable style="width: 120px">
            <el-option label="PDF" value="PDF" />
            <el-option label="DOCX" value="DOCX" />
            <el-option label="XLSX" value="XLSX" />
            <el-option label="PPTX" value="PPTX" />
            <el-option label="TXT" value="TXT" />
          </el-select>
          <el-select v-model="filters.relatedDecision" placeholder="Related Decision" clearable style="width: 160px">
            <el-option label="Chiller Overhaul" value="Chiller Overhaul" />
            <el-option label="LED Retrofit" value="LED Retrofit" />
            <el-option label="UPS Replacement" value="UPS Replacement" />
            <el-option label="HVAC Optimization" value="HVAC Optimization" />
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
          <span>Documents Library ({{ filteredDocuments.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchDocuments" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedDocuments" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="File Type" width="70">
          <template #default="{ row }">
            <el-icon :size="28" :color="getFileIconColor(row.format)">
              <component :is="getFileIcon(row.format)" />
            </el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="documentType" label="Document Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getDocTypeTag(row.documentType)" size="small">{{ row.documentType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="format" label="Format" width="80" />
        <el-table-column prop="fileSize" label="Size" width="90" />
        <el-table-column prop="version" label="Version" width="80" />
        <el-table-column prop="uploader" label="Uploader" width="120" />
        <el-table-column prop="uploadDate" label="Upload Date" width="110" />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDocument(row)">View</el-button>
            <el-button link type="success" size="small" @click="downloadDocument(row)">Download</el-button>
            <el-button link type="info" size="small" @click="viewDecision(row)">Decision</el-button>
            <el-button link type="danger" size="small" @click="deleteDocument(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredDocuments.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload Document" width="600px" destroy-on-close>
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="110px">
        <el-form-item label="Title" prop="title">
          <el-input v-model="uploadForm.title" placeholder="Enter document title" />
        </el-form-item>
        <el-form-item label="Document Type" prop="documentType">
          <el-select v-model="uploadForm.documentType" placeholder="Select document type" style="width: 100%">
            <el-option label="Report" value="Report" />
            <el-option label="Contract" value="Contract" />
            <el-option label="Certificate" value="Certificate" />
            <el-option label="Technical Spec" value="Technical Spec" />
            <el-option label="Manual" value="Manual" />
            <el-option label="Policy" value="Policy" />
            <el-option label="Invoice" value="Invoice" />
            <el-option label="Drawing" value="Drawing" />
          </el-select>
        </el-form-item>
        <el-form-item label="Related Decision" prop="relatedDecision">
          <el-select v-model="uploadForm.relatedDecision" placeholder="Select related decision" clearable style="width: 100%">
            <el-option label="Chiller Overhaul Decision" value="Chiller Overhaul Decision" />
            <el-option label="LED Lighting Retrofit" value="LED Lighting Retrofit" />
            <el-option label="UPS Battery Replacement" value="UPS Battery Replacement" />
            <el-option label="HVAC Optimization Algorithm" value="HVAC Optimization Algorithm" />
            <el-option label="Solar Panel Installation" value="Solar Panel Installation" />
          </el-select>
        </el-form-item>
        <el-form-item label="Version" prop="version">
          <el-input v-model="uploadForm.version" placeholder="e.g., 1.0" />
        </el-form-item>
        <el-form-item label="Upload File" prop="file">
          <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT files up to 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" placeholder="Enter document description" />
        </el-form-item>
        <el-form-item label="Tags" prop="tags">
          <el-select v-model="uploadForm.tags" multiple filterable allow-create default-first-option placeholder="Enter tags" style="width: 100%">
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Inspection" value="Inspection" />
            <el-option label="Safety" value="Safety" />
            <el-option label="Energy" value="Energy" />
            <el-option label="Compliance" value="Compliance" />
            <el-option label="Technical" value="Technical" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitUpload">Upload</el-button>
      </template>
    </el-dialog>

    <!-- Document Preview Dialog -->
    <el-dialog v-model="previewDialogVisible" :title="currentDocument?.title" width="800px" destroy-on-close>
      <div class="preview-container">
        <div class="preview-notice">
          <el-icon :size="48" :color="getFileIconColor(currentDocument?.format || 'PDF')">
            <component :is="getFileIcon(currentDocument?.format || 'PDF')" />
          </el-icon>
          <p>Document preview is not available in the browser.</p>
          <p class="preview-hint">Click "Download" to view the document on your device.</p>
        </div>
        <div class="preview-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Title">{{ currentDocument?.title }}</el-descriptions-item>
            <el-descriptions-item label="Document Type">
              <el-tag :type="getDocTypeTag(currentDocument?.documentType || '')" size="small">{{ currentDocument?.documentType }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Format">{{ currentDocument?.format }}</el-descriptions-item>
            <el-descriptions-item label="File Size">{{ currentDocument?.fileSize }}</el-descriptions-item>
            <el-descriptions-item label="Version">{{ currentDocument?.version || '1.0' }}</el-descriptions-item>
            <el-descriptions-item label="Pages">{{ currentDocument?.pages || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Uploader">{{ currentDocument?.uploader }}</el-descriptions-item>
            <el-descriptions-item label="Upload Date">{{ currentDocument?.uploadDate }}</el-descriptions-item>
            <el-descriptions-item label="Downloads">{{ currentDocument?.downloads || 0 }}</el-descriptions-item>
            <el-descriptions-item label="Related Decision" :span="2">{{ currentDocument?.relatedDecision || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ currentDocument?.description || 'No description' }}</el-descriptions-item>
            <el-descriptions-item label="Tags" :span="2">
              <el-tag v-for="tag in currentDocument?.tags" :key="tag" size="small" style="margin-right: 4px">{{ tag }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadCurrentDocument">Download</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete document "{{ deleteTarget?.title }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
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
  Delete, ZoomIn, User, Grid, List, UploadFilled,
  Files, Tickets, Collection, Medal, Notebook,
  Aim, Money, EditPen
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading document repository...',
  'Indexing files...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Document {
  id: number
  title: string
  description: string
  documentType: string
  format: string
  fileSize: string
  version: string
  pages: number
  url: string
  relatedDecision: string
  relatedDecisionId: number
  uploader: string
  uploadDate: string
  downloads: number
  tags: string[]
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
  { title: 'Total Documents', value: 567, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'This Month', value: 28, trend: 8, icon: 'TrendCharts', bgColor: '#67c23a', key: 'monthly' },
  { title: 'Total Downloads', value: '2.4K', trend: 18, icon: 'Download', bgColor: '#e6a23c', key: 'downloads' },
  { title: 'Storage Used', value: '3.2 GB', trend: 10, icon: 'Clock', bgColor: '#f56c6c', key: 'storage' }
])

const documentTypes = [
  { name: 'Report', icon: 'Document', color: '#409eff', count: 0 },
  { name: 'Contract', icon: 'Files', color: '#67c23a', count: 0 },
  { name: 'Certificate', icon: 'Medal', color: '#e6a23c', count: 0 },
  { name: 'Technical Spec', icon: 'Tickets', color: '#909399', count: 0 },
  { name: 'Manual', icon: 'Notebook', color: '#9b59b6', count: 0 },
  { name: 'Policy', icon: 'Collection', color: '#3498db', count: 0 },
  { name: 'Invoice', icon: 'Money', color: '#2ecc71', count: 0 },
  { name: 'Drawing', icon: 'EditPen', color: '#e74c3c', count: 0 }
]

const documents = ref<Document[]>([
  {
    id: 1,
    title: 'Chiller Overhaul Technical Report',
    description: 'Comprehensive technical report on chiller overhaul including parts replaced and efficiency measurements',
    documentType: 'Report',
    format: 'PDF',
    fileSize: '2.4 MB',
    version: '1.0',
    pages: 24,
    url: '#',
    relatedDecision: 'Chiller Overhaul Decision',
    relatedDecisionId: 101,
    uploader: 'John Smith',
    uploadDate: '2024-01-05',
    downloads: 45,
    tags: ['Maintenance', 'Technical', 'Report']
  },
  {
    id: 2,
    title: 'LED Lighting Retrofit - Purchase Contract',
    description: 'Purchase agreement for LED lighting fixtures and installation services',
    documentType: 'Contract',
    format: 'PDF',
    fileSize: '1.8 MB',
    version: '2.1',
    pages: 12,
    url: '#',
    relatedDecision: 'LED Lighting Retrofit',
    relatedDecisionId: 102,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-08',
    downloads: 32,
    tags: ['Contract', 'Procurement']
  },
  {
    id: 3,
    title: 'UPS Battery Specification Sheet',
    description: 'Technical specifications for new lithium-ion UPS batteries',
    documentType: 'Technical Spec',
    format: 'PDF',
    fileSize: '1.2 MB',
    version: '1.0',
    pages: 8,
    url: '#',
    relatedDecision: 'UPS Battery Replacement',
    relatedDecisionId: 103,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-10',
    downloads: 28,
    tags: ['Technical', 'UPS', 'Battery']
  },
  {
    id: 4,
    title: 'Energy Audit Report - Q4 2023',
    description: 'Quarterly energy consumption audit and efficiency recommendations',
    documentType: 'Report',
    format: 'PDF',
    fileSize: '3.1 MB',
    version: '1.0',
    pages: 35,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-03',
    downloads: 67,
    tags: ['Energy', 'Audit', 'Report']
  },
  {
    id: 5,
    title: 'HVAC System User Manual',
    description: 'Complete user manual for the new HVAC control system',
    documentType: 'Manual',
    format: 'PDF',
    fileSize: '5.6 MB',
    version: '1.2',
    pages: 86,
    url: '#',
    relatedDecision: 'HVAC Optimization Algorithm',
    relatedDecisionId: 105,
    uploader: 'David Wang',
    uploadDate: '2024-01-12',
    downloads: 89,
    tags: ['Manual', 'HVAC', 'User Guide']
  },
  {
    id: 6,
    title: 'Safety Compliance Certificate',
    description: 'Annual safety inspection certificate for all facilities',
    documentType: 'Certificate',
    format: 'PDF',
    fileSize: '0.8 MB',
    version: '2024',
    pages: 2,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Robert Liu',
    uploadDate: '2024-01-06',
    downloads: 156,
    tags: ['Safety', 'Compliance', 'Certificate']
  },
  {
    id: 7,
    title: 'Solar Panel Installation Drawing',
    description: 'Engineering drawings for rooftop solar panel layout',
    documentType: 'Drawing',
    format: 'PDF',
    fileSize: '2.9 MB',
    version: '3.0',
    pages: 4,
    url: '#',
    relatedDecision: 'Solar Panel Installation',
    relatedDecisionId: 104,
    uploader: 'Emily Zhao',
    uploadDate: '2024-01-15',
    downloads: 34,
    tags: ['Drawing', 'Solar', 'Engineering']
  },
  {
    id: 8,
    title: 'Energy Saving Calculation Spreadsheet',
    description: 'Detailed calculations for projected energy savings from various initiatives',
    documentType: 'Report',
    format: 'XLSX',
    fileSize: '1.5 MB',
    version: '2.0',
    pages: 0,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-09',
    downloads: 123,
    tags: ['Energy', 'Calculation', 'Savings']
  },
  {
    id: 9,
    title: 'Fire Safety Policy - Updated',
    description: 'Updated fire safety policy and evacuation procedures',
    documentType: 'Policy',
    format: 'DOCX',
    fileSize: '0.6 MB',
    version: '3.0',
    pages: 15,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Robert Liu',
    uploadDate: '2024-01-02',
    downloads: 98,
    tags: ['Policy', 'Safety', 'Fire']
  },
  {
    id: 10,
    title: 'Cooling Tower Maintenance Invoice',
    description: 'Invoice for cooling tower maintenance service',
    documentType: 'Invoice',
    format: 'PDF',
    fileSize: '0.9 MB',
    version: '1.0',
    pages: 1,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Mike Johnson',
    uploadDate: '2024-01-14',
    downloads: 23,
    tags: ['Invoice', 'Maintenance']
  },
  {
    id: 11,
    title: 'BMS Programming Guide',
    description: 'Technical programming guide for Building Management System',
    documentType: 'Manual',
    format: 'PDF',
    fileSize: '4.2 MB',
    version: '1.5',
    pages: 112,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'David Wang',
    uploadDate: '2024-01-04',
    downloads: 67,
    tags: ['Manual', 'BMS', 'Programming']
  },
  {
    id: 12,
    title: 'LEED Certification Application',
    description: 'LEED certification application documents for building',
    documentType: 'Certificate',
    format: 'PDF',
    fileSize: '3.8 MB',
    version: '1.0',
    pages: 28,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Emily Zhao',
    uploadDate: '2024-01-11',
    downloads: 45,
    tags: ['Certificate', 'LEED', 'Sustainability']
  },
  {
    id: 13,
    title: 'Generator Maintenance Log',
    description: 'Monthly maintenance log for emergency generators',
    documentType: 'Report',
    format: 'XLSX',
    fileSize: '0.7 MB',
    version: 'Jan 2024',
    pages: 0,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-13',
    downloads: 34,
    tags: ['Maintenance', 'Generator', 'Log']
  },
  {
    id: 14,
    title: 'Vendor Service Agreement',
    description: 'Service level agreement with maintenance vendor',
    documentType: 'Contract',
    format: 'PDF',
    fileSize: '1.1 MB',
    version: '2.0',
    pages: 18,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'John Smith',
    uploadDate: '2024-01-07',
    downloads: 56,
    tags: ['Contract', 'Vendor', 'SLA']
  },
  {
    id: 15,
    title: 'Electrical System One-Line Diagram',
    description: 'Updated one-line diagram for main electrical distribution',
    documentType: 'Drawing',
    format: 'PDF',
    fileSize: '1.3 MB',
    version: '3.1',
    pages: 1,
    url: '#',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'David Wang',
    uploadDate: '2024-01-01',
    downloads: 78,
    tags: ['Drawing', 'Electrical', 'Diagram']
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const currentDocument = ref<Document | null>(null)
const deleteTarget = ref<Document | null>(null)
const uploadFormRef = ref()
const uploadRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)
const viewMode = ref<'grid' | 'list'>('list')

const filters = reactive({
  keyword: '',
  documentType: '',
  format: '',
  relatedDecision: '',
  dateRange: null as [Date, Date] | null
})

const uploadForm = reactive({
  title: '',
  documentType: '',
  relatedDecision: '',
  version: '1.0',
  description: '',
  tags: [] as string[],
  file: null as File | null
})

const uploadRules = {
  title: [{ required: true, message: 'Please enter document title', trigger: 'blur' }],
  documentType: [{ required: true, message: 'Please select document type', trigger: 'change' }],
  file: [{ required: true, message: 'Please select a file to upload', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredDocuments = computed(() => {
  let filtered = [...documents.value]

  if (filters.keyword) {
    filtered = filtered.filter(d =>
        d.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        d.tags.some(tag => tag.toLowerCase().includes(filters.keyword.toLowerCase()))
    )
  }

  if (filters.documentType) {
    filtered = filtered.filter(d => d.documentType === filters.documentType)
  }

  if (filters.format) {
    filtered = filtered.filter(d => d.format === filters.format)
  }

  if (filters.relatedDecision) {
    filtered = filtered.filter(d => d.relatedDecision === filters.relatedDecision)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(d => {
      const date = new Date(d.uploadDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedDocuments = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredDocuments.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getDocTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Report': 'primary',
    'Contract': 'danger',
    'Certificate': 'success',
    'Technical Spec': 'info',
    'Manual': 'warning',
    'Policy': 'info',
    'Invoice': 'success',
    'Drawing': 'warning'
  }
  return map[type] || 'info'
}

const getFileIcon = (format: string) => {
  const map: Record<string, any> = {
    'PDF': Document,
    'DOCX': Document,
    'XLSX': Files,
    'PPTX': Collection,
    'TXT': Notebook
  }
  return map[format] || Document
}

const getFileIconColor = (format: string): string => {
  const map: Record<string, string> = {
    'PDF': '#f56c6c',
    'DOCX': '#409eff',
    'XLSX': '#67c23a',
    'PPTX': '#e6a23c',
    'TXT': '#909399'
  }
  return map[format] || '#909399'
}

const getDocumentCountByType = (type: string): number => {
  return documents.value.filter(d => d.documentType === type).length
}

const filterByType = (type: string) => {
  filters.documentType = type
  handleSearch()
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
  filters.documentType = ''
  filters.format = ''
  filters.relatedDecision = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredDocuments.value.length} documents metadata...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchDocuments = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleUploadDocument = () => {
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
}

const submitUpload = async () => {
  if (!uploadFormRef.value) return
  await uploadFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const fileExt = uploadForm.file?.name.split('.').pop()?.toUpperCase() || 'PDF'
      const newDocument: Document = {
        id: Date.now(),
        title: uploadForm.title,
        description: uploadForm.description,
        documentType: uploadForm.documentType,
        format: fileExt,
        fileSize: uploadForm.file ? `${(uploadForm.file.size / 1024 / 1024).toFixed(1)} MB` : 'Unknown',
        version: uploadForm.version,
        pages: 0,
        url: '#',
        relatedDecision: uploadForm.relatedDecision,
        relatedDecisionId: 0,
        uploader: 'Current User',
        uploadDate: new Date().toISOString().split('T')[0],
        downloads: 0,
        tags: uploadForm.tags
      }
      documents.value.unshift(newDocument)
      ElMessage.success('Document uploaded successfully')
      uploadDialogVisible.value = false
      uploadFormRef.value?.resetFields()
      uploadForm.file = null
      uploadRef.value?.clearFiles()
    }
  })
}

const viewDocument = (document: Document) => {
  currentDocument.value = document
  previewDialogVisible.value = true
}

const downloadDocument = (document: Document) => {
  const index = documents.value.findIndex(d => d.id === document.id)
  if (index !== -1) {
    documents.value[index].downloads++
  }
  ElMessage.success(`Downloading: ${document.title}`)
}

const downloadCurrentDocument = () => {
  if (currentDocument.value) {
    downloadDocument(currentDocument.value)
  }
}

const deleteDocument = (document: Document) => {
  deleteTarget.value = document
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = documents.value.findIndex(d => d.id === deleteTarget.value!.id)
    if (index !== -1) {
      documents.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const viewDecision = (document: Document) => {
  if (document.relatedDecision) {
    ElMessage.info(`Viewing decision: ${document.relatedDecision}`)
  } else {
    ElMessage.info('No related decision found')
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
.documents-page {
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

.quick-access-card {
  margin-bottom: 20px;

  .card-header {
    font-weight: 600;
  }
}

.quick-access-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;

  .quick-access-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background: #ecf5ff;
      transform: translateY(-2px);
    }

    .type-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .type-info {
      .type-name {
        font-weight: 600;
        font-size: 14px;
        color: #303133;
      }

      .type-count {
        font-size: 11px;
        color: #909399;
        margin-top: 2px;
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

.preview-container {
  .preview-notice {
    text-align: center;
    padding: 40px;
    background: #f5f7fa;
    border-radius: 8px;
    margin-bottom: 20px;

    p {
      margin: 12px 0 0;
      color: #909399;
    }

    .preview-hint {
      font-size: 12px;
      color: #c0c4cc;
    }
  }

  .preview-info {
    margin-top: 16px;
  }
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-descriptions) {
  margin-top: 0;
}
</style>