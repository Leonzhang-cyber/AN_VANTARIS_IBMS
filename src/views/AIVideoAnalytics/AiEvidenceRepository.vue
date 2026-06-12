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
        <div class="loading-tip">AI Video Analytics - AI Evidence Repository</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-evidence-repository-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>AI Evidence Repository</h1>
        <p>Centralized storage for all AI-detected video evidence with chain-of-custody tracking</p>
      </div>
      <div class="header-actions">
        <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileUpload"
            accept="image/jpeg,image/png,video/mp4"
        >
          <el-button type="primary">
            <el-icon><Upload /></el-icon>
            Upload Evidence
          </el-button>
        </el-upload>
        <el-button @click="exportAll">
          <el-icon><Download /></el-icon>
          Export All
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Folder /></el-icon>
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
            <el-icon><VideoCamera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.videoCount }}</div>
            <div class="stat-label">Video Files</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Picture /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.imageCount }}</div>
            <div class="stat-label">Image Files</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon danger-bg">
            <el-icon><Lock /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.chainOfCustody }}%</div>
            <div class="stat-label">Chain of Custody</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <el-input
          v-model="filters.search"
          placeholder="Search by event ID, description, or location..."
          clearable
          style="width: 260px"
          :prefix-icon="Search"
      />
      <el-select v-model="filters.type" placeholder="Media Type" clearable style="width: 140px">
        <el-option label="All Types" value="" />
        <el-option label="Video" value="VIDEO" />
        <el-option label="Image" value="IMAGE" />
      </el-select>
      <el-select v-model="filters.eventType" placeholder="Event Type" clearable style="width: 160px">
        <el-option label="All Events" value="" />
        <el-option label="PPE Violation" value="PPE_VIOLATION" />
        <el-option label="Intrusion" value="INTRUSION" />
        <el-option label="Fighting" value="FIGHTING" />
        <el-option label="Falling" value="FALLING" />
        <el-option label="Smoke/Fire" value="SMOKE_FIRE" />
      </el-select>
      <el-select v-model="filters.verified" placeholder="Verification" clearable style="width: 140px">
        <el-option label="All" value="" />
        <el-option label="Verified" value="VERIFIED" />
        <el-option label="Pending" value="PENDING" />
        <el-option label="Disputed" value="DISPUTED" />
      </el-select>
      <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start Date"
          end-placeholder="End Date"
          style="width: 280px"
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

    <!-- Evidence Grid -->
    <div class="evidence-grid-wrapper">
      <div class="grid-header">
        <span class="grid-title">Evidence Files</span>
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
      <div v-if="viewMode === 'grid'" class="evidence-grid">
        <div
            v-for="item in paginatedEvidence"
            :key="item.id"
            class="evidence-card"
            @click="openDetail(item)"
        >
          <div class="evidence-thumbnail">
            <el-image v-if="item.type === 'IMAGE'" :src="item.thumbnail" fit="cover">
              <template #error>
                <div class="thumbnail-placeholder">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
            <div v-else class="video-thumbnail">
              <el-icon><VideoCamera /></el-icon>
              <span class="duration-badge">{{ item.duration }}</span>
            </div>
            <div class="event-badge" :class="getSeverityClass(item.severity)">
              {{ item.eventType }}
            </div>
            <div v-if="item.verified === 'VERIFIED'" class="verified-badge">
              <el-icon><Check /></el-icon> Verified
            </div>
          </div>
          <div class="evidence-info">
            <div class="evidence-title">{{ item.title }}</div>
            <div class="evidence-meta">
              <span><el-icon><Calendar /></el-icon> {{ formatDate(item.timestamp) }}</span>
              <span><el-icon><Location /></el-icon> {{ item.location }}</span>
            </div>
            <div class="evidence-footer">
              <el-tag :type="getEventTagType(item.eventType)" size="small">
                {{ formatEventType(item.eventType) }}
              </el-tag>
              <div class="evidence-actions" @click.stop>
                <el-button link type="primary" size="small" @click="downloadEvidence(item)">
                  <el-icon><Download /></el-icon>
                </el-button>
                <el-button link type="danger" size="small" @click="confirmDelete(item)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="evidence-list">
        <el-table :data="paginatedEvidence" stripe @row-click="openDetail">
          <el-table-column prop="thumbnail" label="" width="60">
            <template #default="{ row }">
              <div class="list-thumbnail">
                <el-icon v-if="row.type === 'VIDEO'"><VideoCamera /></el-icon>
                <el-icon v-else><Picture /></el-icon>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="Title" min-width="200" />
          <el-table-column prop="eventType" label="Event Type" width="140">
            <template #default="{ row }">
              <el-tag :type="getEventTagType(row.eventType)" size="small">
                {{ formatEventType(row.eventType) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="location" label="Location" width="150" />
          <el-table-column prop="timestamp" label="Date" width="160">
            <template #default="{ row }">
              {{ formatDate(row.timestamp) }}
            </template>
          </el-table-column>
          <el-table-column prop="verified" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getVerificationTagType(row.verified)" size="small">
                {{ row.verified }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click.stop="downloadEvidence(row)">
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button link type="danger" size="small" @click.stop="confirmDelete(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Pagination -->
      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[12, 24, 48, 96]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Evidence Detail Dialog -->
    <el-dialog v-model="detailDialog.visible" :title="detailDialog.evidence?.title" width="800px" class="evidence-dialog">
      <div v-if="detailDialog.evidence" class="evidence-detail">
        <!-- Media Preview -->
        <div class="detail-preview">
          <el-image v-if="detailDialog.evidence.type === 'IMAGE'" :src="detailDialog.evidence.url" fit="contain">
            <template #error>
              <div class="preview-placeholder">
                <el-icon><Picture /></el-icon>
                <span>Image preview not available</span>
              </div>
            </template>
          </el-image>
          <div v-else class="video-preview">
            <video controls class="video-player">
              <source :src="detailDialog.evidence.url" type="video/mp4" />
              Your browser does not support video playback.
            </video>
          </div>
        </div>

        <!-- Evidence Details -->
        <el-descriptions :column="2" border class="detail-descriptions">
          <el-descriptions-item label="Evidence ID">{{ detailDialog.evidence.id }}</el-descriptions-item>
          <el-descriptions-item label="Event Type">
            <el-tag :type="getEventTagType(detailDialog.evidence.eventType)" size="small">
              {{ formatEventType(detailDialog.evidence.eventType) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Timestamp">{{ formatFullTimestamp(detailDialog.evidence.timestamp) }}</el-descriptions-item>
          <el-descriptions-item label="Camera">{{ detailDialog.evidence.camera }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ detailDialog.evidence.location }}</el-descriptions-item>
          <el-descriptions-item label="Confidence">{{ (detailDialog.evidence.confidence * 100).toFixed(0) }}%</el-descriptions-item>
          <el-descriptions-item label="File Size">{{ detailDialog.evidence.fileSize }}</el-descriptions-item>
          <el-descriptions-item label="Format">{{ detailDialog.evidence.format }}</el-descriptions-item>
          <el-descriptions-item label="Verification Status" :span="2">
            <el-radio-group v-model="detailDialog.evidence.verified" @change="updateVerification">
              <el-radio value="VERIFIED">Verified</el-radio>
              <el-radio value="PENDING">Pending</el-radio>
              <el-radio value="DISPUTED">Disputed</el-radio>
            </el-radio-group>
          </el-descriptions-item>
          <el-descriptions-item label="AI Analysis" :span="2">
            <div class="ai-analysis">
              <el-icon><MagicStick /></el-icon>
              <span>{{ detailDialog.evidence.aiAnalysis }}</span>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Chain of Custody" :span="2">
            <div class="chain-of-custody">
              <el-timeline>
                <el-timeline-item
                    v-for="(entry, idx) in detailDialog.evidence.custodyChain"
                    :key="idx"
                    :timestamp="entry.timestamp"
                    placement="top"
                    :type="entry.type"
                >
                  {{ entry.action }} - {{ entry.user }}
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Add Note -->
        <div class="add-note">
          <el-input
              v-model="newNote"
              type="textarea"
              :rows="2"
              placeholder="Add a note to this evidence..."
          />
          <el-button type="primary" @click="addNote" style="margin-top: 12px">
            Add Note
          </el-button>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialog.visible = false">Close</el-button>
        <el-button type="primary" @click="downloadEvidence(detailDialog.evidence)">
          <el-icon><Download /></el-icon>
          Download Evidence
        </el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation -->
    <el-dialog v-model="deleteDialog.visible" title="Delete Evidence" width="400px">
      <p>Are you sure you want to delete <strong>{{ deleteDialog.evidence?.title }}</strong>?</p>
      <p class="delete-warning">This action cannot be undone and will remove the evidence from the repository.</p>
      <template #footer>
        <el-button @click="deleteDialog.visible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDeleteEvidence">Delete</el-button>
      </template>
    </el-dialog>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadDialog.visible" title="Upload Evidence" width="500px">
      <el-upload
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="uploadFileList"
          multiple
          accept="image/jpeg,image/png,video/mp4"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          Drop files here or <em>click to upload</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            Supported formats: JPEG, PNG, MP4 (max 500MB)
          </div>
        </template>
      </el-upload>
      <el-form :model="uploadForm" label-width="100px" style="margin-top: 20px">
        <el-form-item label="Event Type">
          <el-select v-model="uploadForm.eventType" placeholder="Select event type">
            <el-option label="PPE Violation" value="PPE_VIOLATION" />
            <el-option label="Intrusion" value="INTRUSION" />
            <el-option label="Fighting" value="FIGHTING" />
            <el-option label="Falling" value="FALLING" />
            <el-option label="Smoke/Fire" value="SMOKE_FIRE" />
          </el-select>
        </el-form-item>
        <el-form-item label="Location">
          <el-input v-model="uploadForm.location" placeholder="Enter location" />
        </el-form-item>
        <el-form-item label="Camera">
          <el-input v-model="uploadForm.camera" placeholder="Enter camera name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="uploadEvidence">Upload</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile, UploadFiles } from 'element-plus'
import {
  Refresh,
  Download,
  Upload,
  Folder,
  VideoCamera,
  Picture,
  Lock,
  Search,
  RefreshLeft,
  Grid,
  List,
  Calendar,
  Location,
  Delete,
  Check,
  UploadFilled,
  MagicStick
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading evidence repository...',
  'Indexing media files...',
  'Almost ready...'
]

// ==================== Type Definitions ====================
interface EvidenceItem {
  id: string
  title: string
  type: 'VIDEO' | 'IMAGE'
  eventType: string
  description: string
  location: string
  camera: string
  timestamp: Date
  confidence: number
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  verified: 'VERIFIED' | 'PENDING' | 'DISPUTED'
  url: string
  thumbnail: string
  duration?: string
  fileSize: string
  format: string
  aiAnalysis: string
  custodyChain: Array<{
    action: string
    user: string
    timestamp: string
    type: string
  }>
}

// ==================== 模拟数据生成 ====================
const generateMockEvidence = (): EvidenceItem[] => {
  const eventTypes = [
    { code: 'PPE_VIOLATION', name: 'PPE Violation', severity: 'HIGH', desc: 'Missing safety equipment detected' },
    { code: 'INTRUSION', name: 'Intrusion', severity: 'CRITICAL', desc: 'Unauthorized access detected' },
    { code: 'FIGHTING', name: 'Fighting', severity: 'CRITICAL', desc: 'Physical altercation detected' },
    { code: 'FALLING', name: 'Falling', severity: 'CRITICAL', desc: 'Person fallen to ground' },
    { code: 'SMOKE_FIRE', name: 'Smoke/Fire', severity: 'CRITICAL', desc: 'Smoke or fire detected' }
  ]

  const cameras = [
    'Main Entrance', 'Lobby East', 'Corridor North', 'Parking Area',
    'Loading Dock', 'Server Room', 'Cafeteria', 'West Gate'
  ]

  const locations = [
    'Building A - Ground Floor', 'Building A - Lobby', 'Building B - 2nd Floor',
    'West Parking', 'South Building', 'Data Center', 'Building A - 1st Floor'
  ]

  const evidence: EvidenceItem[] = []
  const now = new Date()

  for (let i = 0; i < 36; i++) {
    const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
    const isVideo = Math.random() > 0.6
    const timestamp = new Date(now.getTime() - Math.random() * 30 * 24 * 60 * 60 * 1000)
    const verified = ['VERIFIED', 'PENDING', 'DISPUTED'][Math.floor(Math.random() * 3)] as any
    const confidence = 0.7 + Math.random() * 0.28

    evidence.push({
      id: `EVD-${String(i + 1).padStart(6, '0')}`,
      title: `${eventType.name} - ${cameras[Math.floor(Math.random() * cameras.length)]}`,
      type: isVideo ? 'VIDEO' : 'IMAGE',
      eventType: eventType.code,
      description: eventType.desc,
      location: locations[Math.floor(Math.random() * locations.length)],
      camera: cameras[Math.floor(Math.random() * cameras.length)],
      timestamp: timestamp,
      confidence: confidence,
      severity: eventType.severity as any,
      verified: verified,
      url: `#`,
      thumbnail: `https://picsum.photos/id/${i + 100}/300/200`,
      duration: isVideo ? `${Math.floor(Math.random() * 60) + 10} sec` : undefined,
      fileSize: isVideo
          ? `${(Math.random() * 50 + 5).toFixed(1)} MB`
          : `${(Math.random() * 2 + 0.5).toFixed(1)} MB`,
      format: isVideo ? 'MP4' : 'JPEG',
      aiAnalysis: `${eventType.name} detected with ${Math.floor(confidence * 100)}% confidence. ${getAIAnalysisNote(eventType.name)}`,
      custodyChain: [
        { action: 'Evidence captured', user: 'AI System', timestamp: timestamp.toLocaleString(), type: 'primary' },
        { action: 'Added to repository', user: 'AI System', timestamp: new Date(timestamp.getTime() + 5000).toLocaleString(), type: 'primary' }
      ]
    })
  }

  return evidence.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
}

const getAIAnalysisNote = (eventType: string): string => {
  const notes: Record<string, string> = {
    'PPE Violation': 'Missing hard hat and safety vest identified.',
    'Intrusion': 'Subject entered restricted area without authorization.',
    'Fighting': 'Aggressive posture and high motion intensity detected.',
    'Falling': 'Sudden vertical movement followed by stationary position.',
    'Smoke/Fire': 'Abnormal heat signature and smoke plume confirmed.'
  }
  return notes[eventType] || 'Standard AI analysis completed.'
}

// ==================== 响应式状态 ====================
const allEvidence = ref<EvidenceItem[]>([])
const viewMode = ref<'grid' | 'list'>('grid')

const filters = reactive({
  search: '',
  type: '',
  eventType: '',
  verified: '',
  dateRange: null as Date[] | null
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 12,
  total: 0
})

const stats = reactive({
  totalEvidence: 0,
  videoCount: 0,
  imageCount: 0,
  chainOfCustody: 98
})

const detailDialog = reactive({
  visible: false,
  evidence: null as EvidenceItem | null
})

const deleteDialog = reactive({
  visible: false,
  evidence: null as EvidenceItem | null
})

const uploadDialog = reactive({
  visible: false,
  files: [] as File[]
})

const uploadForm = reactive({
  eventType: '',
  location: '',
  camera: ''
})

const uploadFileList = ref<UploadFile[]>([])
const newNote = ref('')

// ==================== 计算属性 ====================
const filteredEvidence = computed(() => {
  let filtered = [...allEvidence.value]

  if (filters.search) {
    const searchLower = filters.search.toLowerCase()
    filtered = filtered.filter(e =>
        e.id.toLowerCase().includes(searchLower) ||
        e.title.toLowerCase().includes(searchLower) ||
        e.description.toLowerCase().includes(searchLower) ||
        e.location.toLowerCase().includes(searchLower)
    )
  }

  if (filters.type) {
    filtered = filtered.filter(e => e.type === filters.type)
  }

  if (filters.eventType) {
    filtered = filtered.filter(e => e.eventType === filters.eventType)
  }

  if (filters.verified) {
    filtered = filtered.filter(e => e.verified === filters.verified)
  }

  if (filters.dateRange && filters.dateRange.length === 2) {
    const [start, end] = filters.dateRange
    filtered = filtered.filter(e => e.timestamp >= start && e.timestamp <= end)
  }

  pagination.total = filtered.length
  return filtered
})

const paginatedEvidence = computed(() => {
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filteredEvidence.value.slice(start, end)
})

// ==================== 辅助函数 ====================
const formatDate = (date: Date) => {
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatFullTimestamp = (date: Date) => {
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatEventType = (code: string) => {
  const map: Record<string, string> = {
    'PPE_VIOLATION': 'PPE Violation',
    'INTRUSION': 'Intrusion',
    'FIGHTING': 'Fighting',
    'FALLING': 'Falling',
    'SMOKE_FIRE': 'Smoke/Fire'
  }
  return map[code] || code
}

const getEventTagType = (code: string) => {
  const map: Record<string, string> = {
    'PPE_VIOLATION': 'warning',
    'INTRUSION': 'danger',
    'FIGHTING': 'danger',
    'FALLING': 'danger',
    'SMOKE_FIRE': 'danger'
  }
  return map[code] || 'info'
}

const getVerificationTagType = (verified: string) => {
  const map: Record<string, string> = {
    'VERIFIED': 'success',
    'PENDING': 'warning',
    'DISPUTED': 'danger'
  }
  return map[verified] || 'info'
}

const getSeverityClass = (severity: string) => {
  const map: Record<string, string> = {
    'CRITICAL': 'critical',
    'HIGH': 'high',
    'MEDIUM': 'medium',
    'LOW': 'low'
  }
  return map[severity] || 'medium'
}

const updateStats = () => {
  stats.totalEvidence = allEvidence.value.length
  stats.videoCount = allEvidence.value.filter(e => e.type === 'VIDEO').length
  stats.imageCount = allEvidence.value.filter(e => e.type === 'IMAGE').length
}

// ==================== 交互事件 ====================
const handleSearch = () => {
  pagination.currentPage = 1
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  filters.search = ''
  filters.type = ''
  filters.eventType = ''
  filters.verified = ''
  filters.dateRange = null
  pagination.currentPage = 1
  ElMessage.info('Filters reset')
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
}

const openDetail = (evidence: EvidenceItem) => {
  detailDialog.evidence = evidence
  detailDialog.visible = true
  newNote.value = ''
}

const downloadEvidence = (evidence: EvidenceItem) => {
  // Simulate download
  const data = JSON.stringify(evidence, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${evidence.id}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success(`Downloading ${evidence.title}`)
}

const confirmDelete = (evidence: EvidenceItem) => {
  deleteDialog.evidence = evidence
  deleteDialog.visible = true
}

const confirmDeleteEvidence = () => {
  if (deleteDialog.evidence) {
    const index = allEvidence.value.findIndex(e => e.id === deleteDialog.evidence!.id)
    if (index !== -1) {
      allEvidence.value.splice(index, 1)
      updateStats()
      ElMessage.success(`Deleted ${deleteDialog.evidence.title}`)
    }
  }
  deleteDialog.visible = false
  deleteDialog.evidence = null
}

const updateVerification = () => {
  if (detailDialog.evidence) {
    ElMessage.success(`Verification status updated to ${detailDialog.evidence.verified}`)
  }
}

const addNote = () => {
  if (newNote.value.trim() && detailDialog.evidence) {
    detailDialog.evidence.custodyChain.push({
      action: `Note added: ${newNote.value}`,
      user: 'Current User',
      timestamp: new Date().toLocaleString(),
      type: 'info'
    })
    ElMessage.success('Note added to chain of custody')
    newNote.value = ''
  }
}

const handleFileUpload = (file: UploadFile) => {
  uploadDialog.visible = true
  uploadFileList.value = [file]
}

const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  uploadFileList.value = files
}

const handleFileRemove = (file: UploadFile, files: UploadFiles) => {
  uploadFileList.value = files
}

const uploadEvidence = () => {
  if (uploadFileList.value.length === 0) {
    ElMessage.warning('Please select files to upload')
    return
  }

  if (!uploadForm.eventType) {
    ElMessage.warning('Please select event type')
    return
  }

  // Simulate upload
  const newEvidence: EvidenceItem[] = uploadFileList.value.map((file, idx) => {
    const isVideo = file.raw?.type.startsWith('video/') || false
    const now = new Date()
    return {
      id: `EVD-${String(allEvidence.value.length + idx + 1).padStart(6, '0')}`,
      title: file.name,
      type: isVideo ? 'VIDEO' : 'IMAGE',
      eventType: uploadForm.eventType,
      description: `Uploaded evidence: ${file.name}`,
      location: uploadForm.location || 'Unknown',
      camera: uploadForm.camera || 'External Camera',
      timestamp: now,
      confidence: 1.0,
      severity: 'MEDIUM',
      verified: 'PENDING',
      url: '#',
      thumbnail: `https://picsum.photos/id/${Math.floor(Math.random() * 100)}/300/200`,
      duration: isVideo ? '30 sec' : undefined,
      fileSize: file.raw ? `${(file.raw.size / (1024 * 1024)).toFixed(1)} MB` : '1 MB',
      format: isVideo ? 'MP4' : 'JPEG',
      aiAnalysis: 'Manually uploaded evidence. AI analysis pending.',
      custodyChain: [
        { action: 'Evidence uploaded', user: 'Current User', timestamp: now.toLocaleString(), type: 'primary' }
      ]
    }
  })

  allEvidence.value.unshift(...newEvidence)
  updateStats()
  ElMessage.success(`${newEvidence.length} file(s) uploaded successfully`)
  uploadDialog.visible = false
  uploadFileList.value = []
  uploadForm.eventType = ''
  uploadForm.location = ''
  uploadForm.camera = ''
}

const exportAll = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    summary: stats,
    evidence: filteredEvidence.value
  }
  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `evidence-repository-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Evidence exported successfully')
}

// ==================== 数据加载 ====================
const loadData = () => {
  allEvidence.value = generateMockEvidence()
  updateStats()
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
.ai-evidence-repository-page {
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
.danger-bg { background-color: #fef0f0; color: #f56c6c; }

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

/* Evidence Grid */
.evidence-grid-wrapper {
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

.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.evidence-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid #ebeef5;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
}

.evidence-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.evidence-thumbnail {
  position: relative;
  height: 160px;
  background-color: #f5f7fa;
  overflow: hidden;
}

.evidence-thumbnail .el-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder,
.video-thumbnail {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.thumbnail-placeholder .el-icon,
.video-thumbnail .el-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.duration-badge {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  color: white;
}

.event-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  color: white;
}

.event-badge.critical { background-color: #f56c6c; }
.event-badge.high { background-color: #f56c6c; }
.event-badge.medium { background-color: #e6a23c; }
.event-badge.low { background-color: #409eff; }

.verified-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: #67c23a;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  color: white;
  display: flex;
  align-items: center;
  gap: 4px;
}

.evidence-info {
  padding: 12px;
}

.evidence-title {
  font-weight: 600;
  font-size: 14px;
  color: #1f2f3d;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.evidence-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #8c9aab;
  margin-bottom: 12px;
}

.evidence-meta .el-icon {
  font-size: 11px;
}

.evidence-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.evidence-actions {
  display: flex;
  gap: 4px;
}

/* List View */
.evidence-list {
  width: 100%;
}

.list-thumbnail {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #8c9aab;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* Evidence Detail Dialog */
.evidence-dialog :deep(.el-dialog__body) {
  padding-top: 0;
  max-height: 70vh;
  overflow-y: auto;
}

.detail-preview {
  margin-bottom: 20px;
  background: #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-preview .el-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px;
  color: #8c9aab;
}

.preview-placeholder .el-icon {
  font-size: 48px;
}

.video-player {
  width: 100%;
  max-height: 400px;
}

.detail-descriptions {
  margin-bottom: 20px;
}

.ai-analysis {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #67c23a;
}

.chain-of-custody {
  max-height: 200px;
  overflow-y: auto;
}

.add-note {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.delete-warning {
  color: #f56c6c;
  font-size: 13px;
  margin-top: 8px;
}

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>