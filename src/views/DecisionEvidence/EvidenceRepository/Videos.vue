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
        <div class="loading-tip">Video Evidence Repository</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="videos-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Evidence Repository</el-breadcrumb-item>
            <el-breadcrumb-item>Videos</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Video Evidence Repository</h1>
        <p class="description">Manage and organize video evidence for inspections, maintenance procedures, and incident documentation</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleUploadVideo">
          <el-icon><Plus /></el-icon>
          Upload Video
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
          <el-select v-model="filters.category" placeholder="Category" clearable style="width: 140px">
            <el-option label="Inspection" value="Inspection" />
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Training" value="Training" />
            <el-option label="Incident" value="Incident" />
            <el-option label="Procedure" value="Procedure" />
            <el-option label="Demonstration" value="Demonstration" />
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

    <!-- Video Grid -->
    <el-card class="video-grid-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Video Gallery ({{ filteredVideos.length }} items)</span>
          <div class="view-toggle">
            <el-button-group>
              <el-button :type="viewMode === 'grid' ? 'primary' : 'default'" size="small" @click="viewMode = 'grid'">
                <el-icon><Grid /></el-icon>
              </el-button>
              <el-button :type="viewMode === 'list' ? 'primary' : 'default'" size="small" @click="viewMode = 'list'">
                <el-icon><List /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <!-- Grid View -->
      <div v-if="viewMode === 'grid'" class="video-grid" v-loading="loading">
        <el-card
            v-for="video in paginatedVideos"
            :key="video.id"
            class="video-card"
            shadow="hover"
            body-style="{ padding: '0px' }"
        >
          <div class="video-thumbnail-container" @click="playVideo(video)">
            <img :src="video.thumbnail" :alt="video.title" class="video-thumbnail" />
            <div class="video-play-overlay">
              <el-icon class="play-icon"><VideoPlay /></el-icon>
            </div>
            <div class="video-duration">{{ video.duration }}</div>
          </div>
          <div class="video-info">
            <div class="video-title">{{ video.title }}</div>
            <div class="video-meta">
              <el-tag :type="getCategoryTag(video.category)" size="small">{{ video.category }}</el-tag>
              <span class="video-date">{{ video.uploadDate }}</span>
            </div>
            <div class="video-description" v-if="video.description">{{ video.description }}</div>
            <div class="video-footer">
              <span class="video-uploader">
                <el-icon><User /></el-icon>
                {{ video.uploader }}
              </span>
              <div class="video-stats">
                <span><el-icon><View /></el-icon> {{ video.views }}</span>
                <span><el-icon><Download /></el-icon> {{ video.downloads }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- List View -->
      <el-table v-else :data="paginatedVideos" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="Thumbnail" width="120">
          <template #default="{ row }">
            <div class="thumbnail-cell" @click="playVideo(row)">
              <img :src="row.thumbnail" class="thumbnail-img" />
              <el-icon class="thumbnail-play"><VideoPlay /></el-icon>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="130">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="Duration" width="100" />
        <el-table-column prop="fileSize" label="File Size" width="100" />
        <el-table-column prop="uploader" label="Uploader" width="120" />
        <el-table-column prop="uploadDate" label="Upload Date" width="110" />
        <el-table-column prop="views" label="Views" width="80" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="playVideo(row)">Play</el-button>
            <el-button link type="success" size="small" @click="viewDecision(row)">Decision</el-button>
            <el-button link type="danger" size="small" @click="deleteVideo(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 48, 96]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredVideos.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload Video" width="600px" destroy-on-close>
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="Title" prop="title">
          <el-input v-model="uploadForm.title" placeholder="Enter video title" />
        </el-form-item>
        <el-form-item label="Category" prop="category">
          <el-select v-model="uploadForm.category" placeholder="Select category" style="width: 100%">
            <el-option label="Inspection" value="Inspection" />
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Training" value="Training" />
            <el-option label="Incident" value="Incident" />
            <el-option label="Procedure" value="Procedure" />
            <el-option label="Demonstration" value="Demonstration" />
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
        <el-form-item label="Upload Video" prop="file">
          <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept="video/mp4,video/avi,video/mov,video/wmv,video/webm"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop video file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                MP4, AVI, MOV, WMV, WEBM files up to 500MB
              </div>
            </template>
          </el-upload>
          <div v-if="uploadPreview" class="upload-preview">
            <video :src="uploadPreview" controls class="preview-video"></video>
          </div>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="uploadForm.description" type="textarea" :rows="3" placeholder="Enter video description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitUpload">Upload</el-button>
      </template>
    </el-dialog>

    <!-- Video Player Dialog -->
    <el-dialog v-model="playerDialogVisible" :title="currentVideo?.title" width="900px" destroy-on-close>
      <div class="player-container">
        <video :src="currentVideo?.url" controls class="video-player" autoplay></video>
        <div class="player-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Category">
              <el-tag :type="getCategoryTag(currentVideo?.category || '')" size="small">{{ currentVideo?.category }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Duration">{{ currentVideo?.duration }}</el-descriptions-item>
            <el-descriptions-item label="Uploader">{{ currentVideo?.uploader }}</el-descriptions-item>
            <el-descriptions-item label="Upload Date">{{ currentVideo?.uploadDate }}</el-descriptions-item>
            <el-descriptions-item label="File Size">{{ currentVideo?.fileSize }}</el-descriptions-item>
            <el-descriptions-item label="Views">{{ currentVideo?.views }}</el-descriptions-item>
            <el-descriptions-item label="Downloads">{{ currentVideo?.downloads }}</el-descriptions-item>
            <el-descriptions-item label="Related Decision" :span="2">{{ currentVideo?.relatedDecision || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ currentVideo?.description || 'No description' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="playerDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadVideo">Download</el-button>
        <el-button type="success" @click="shareVideo">Share</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete video "{{ deleteTarget?.title }}"?</p>
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
  VideoPlay, View
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading video repository...',
  'Processing video data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Video {
  id: number
  title: string
  description: string
  category: string
  url: string
  thumbnail: string
  duration: string
  fileSize: string
  relatedDecision: string
  relatedDecisionId: number
  uploader: string
  uploadDate: string
  views: number
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
  { title: 'Total Videos', value: 86, trend: 18, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'This Month', value: 12, trend: 25, icon: 'TrendCharts', bgColor: '#67c23a', key: 'monthly' },
  { title: 'Total Views', value: '4.2K', trend: 32, icon: 'View', bgColor: '#e6a23c', key: 'views' },
  { title: 'Storage Used', value: '12.8 GB', trend: 15, icon: 'Clock', bgColor: '#f56c6c', key: 'storage' }
])

// Generate placeholder thumbnails
const generateThumbnail = (index: number, category: string): string => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#9b59b6', '#3498db', '#2ecc71']
  const color = colors[index % colors.length]
  return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='320' height='180' viewBox='0 0 320 180'%3E%3Crect width='320' height='180' fill='${color.replace('#', '%23')}'/%3E%3Cpolygon points='140,70 140,110 180,90' fill='white' /%3E%3Ctext x='160' y='140' text-anchor='middle' fill='white' font-size='12'%3E${category}%3C/text%3E%3C/svg%3E`
}

const videos = ref<Video[]>([
  {
    id: 1,
    title: 'Chiller Compressor Replacement Procedure',
    description: 'Step-by-step video guide for replacing chiller compressor showing safety protocols and installation techniques',
    category: 'Procedure',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(1, 'Procedure'),
    duration: '12:34',
    fileSize: '156 MB',
    relatedDecision: 'Chiller Overhaul Decision',
    relatedDecisionId: 101,
    uploader: 'John Smith',
    uploadDate: '2024-01-05',
    views: 156,
    downloads: 42,
    tags: ['chiller', 'procedure', 'maintenance']
  },
  {
    id: 2,
    title: 'LED Retrofit Time-lapse',
    description: 'Time-lapse video showing complete LED lighting retrofit across office floor',
    category: 'Demonstration',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(2, 'Demonstration'),
    duration: '03:45',
    fileSize: '89 MB',
    relatedDecision: 'LED Lighting Retrofit',
    relatedDecisionId: 102,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-08',
    views: 342,
    downloads: 87,
    tags: ['lighting', 'LED', 'timelapse']
  },
  {
    id: 3,
    title: 'UPS Battery Failure Analysis',
    description: 'Technical analysis of failed UPS batteries showing swelling and thermal damage',
    category: 'Inspection',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(3, 'Inspection'),
    duration: '08:22',
    fileSize: '203 MB',
    relatedDecision: 'UPS Battery Replacement',
    relatedDecisionId: 103,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-10',
    views: 98,
    downloads: 23,
    tags: ['UPS', 'battery', 'failure']
  },
  {
    id: 4,
    title: 'HVAC System Optimization Tutorial',
    description: 'Training video on HVAC optimization techniques using AI algorithms',
    category: 'Training',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(4, 'Training'),
    duration: '25:18',
    fileSize: '412 MB',
    relatedDecision: 'HVAC Optimization Algorithm',
    relatedDecisionId: 105,
    uploader: 'David Wang',
    uploadDate: '2024-01-12',
    views: 267,
    downloads: 56,
    tags: ['HVAC', 'training', 'optimization']
  },
  {
    id: 5,
    title: 'Drone Inspection - Building Exterior',
    description: 'Drone footage showing building exterior conditions including roof, facade, and cooling towers',
    category: 'Inspection',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(5, 'Inspection'),
    duration: '15:42',
    fileSize: '345 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Sarah Chen',
    uploadDate: '2024-01-07',
    views: 423,
    downloads: 89,
    tags: ['drone', 'inspection', 'building']
  },
  {
    id: 6,
    title: 'Fire Safety Training Video',
    description: 'Annual fire safety training covering evacuation procedures and equipment usage',
    category: 'Training',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(6, 'Training'),
    duration: '18:30',
    fileSize: '278 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Robert Liu',
    uploadDate: '2024-01-03',
    views: 534,
    downloads: 124,
    tags: ['safety', 'training', 'fire']
  },
  {
    id: 7,
    title: 'Solar Panel Installation Process',
    description: 'Complete installation process for rooftop solar panel system',
    category: 'Procedure',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(7, 'Procedure'),
    duration: '22:15',
    fileSize: '389 MB',
    relatedDecision: 'Solar Panel Installation',
    relatedDecisionId: 104,
    uploader: 'Emily Zhao',
    uploadDate: '2024-01-15',
    views: 187,
    downloads: 45,
    tags: ['solar', 'installation', 'renewable']
  },
  {
    id: 8,
    title: 'Cooling Tower Maintenance Walkthrough',
    description: 'Monthly maintenance checklist walkthrough for cooling towers',
    category: 'Maintenance',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(8, 'Maintenance'),
    duration: '14:08',
    fileSize: '198 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Mike Johnson',
    uploadDate: '2024-01-14',
    views: 124,
    downloads: 31,
    tags: ['cooling', 'maintenance', 'walkthrough']
  },
  {
    id: 9,
    title: 'Emergency Generator Test',
    description: 'Monthly load bank test and emergency generator operation',
    category: 'Demonstration',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(9, 'Demonstration'),
    duration: '06:52',
    fileSize: '112 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-11',
    views: 89,
    downloads: 18,
    tags: ['generator', 'test', 'emergency']
  },
  {
    id: 10,
    title: 'Water Leak Detection & Repair',
    description: 'Video documentation of water leak detection using thermal imaging and repair process',
    category: 'Incident',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(10, 'Incident'),
    duration: '09:33',
    fileSize: '167 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Chris Lee',
    uploadDate: '2024-01-06',
    views: 156,
    downloads: 42,
    tags: ['leak', 'water', 'repair']
  },
  {
    id: 11,
    title: 'Energy Management System Overview',
    description: 'Overview of new energy management system features and capabilities',
    category: 'Training',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(11, 'Training'),
    duration: '20:00',
    fileSize: '312 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-09',
    views: 203,
    downloads: 67,
    tags: ['energy', 'EMS', 'training']
  },
  {
    id: 12,
    title: 'BMS Control Panel Programming',
    description: 'Advanced programming tutorial for building management system',
    category: 'Training',
    url: 'https://www.w3schools.com/html/mov_bbb.mp4',
    thumbnail: generateThumbnail(12, 'Training'),
    duration: '35:22',
    fileSize: '528 MB',
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'David Wang',
    uploadDate: '2024-01-04',
    views: 78,
    downloads: 19,
    tags: ['BMS', 'programming', 'training']
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')
const uploadDialogVisible = ref(false)
const playerDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const currentVideo = ref<Video | null>(null)
const deleteTarget = ref<Video | null>(null)
const uploadFormRef = ref()
const uploadRef = ref()
const currentPage = ref(1)
const pageSize = ref(12)
const uploadPreview = ref('')

const filters = reactive({
  keyword: '',
  category: '',
  relatedDecision: '',
  dateRange: null as [Date, Date] | null
})

const uploadForm = reactive({
  title: '',
  category: '',
  relatedDecision: '',
  description: '',
  file: null as File | null
})

const uploadRules = {
  title: [{ required: true, message: 'Please enter video title', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  file: [{ required: true, message: 'Please select a video to upload', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredVideos = computed(() => {
  let filtered = [...videos.value]

  if (filters.keyword) {
    filtered = filtered.filter(v =>
        v.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        v.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        v.tags.some(tag => tag.toLowerCase().includes(filters.keyword.toLowerCase()))
    )
  }

  if (filters.category) {
    filtered = filtered.filter(v => v.category === filters.category)
  }

  if (filters.relatedDecision) {
    filtered = filtered.filter(v => v.relatedDecision === filters.relatedDecision)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(v => {
      const date = new Date(v.uploadDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedVideos = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredVideos.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCategoryTag = (category: string): string => {
  const map: Record<string, string> = {
    'Inspection': 'primary',
    'Maintenance': 'warning',
    'Training': 'success',
    'Incident': 'danger',
    'Procedure': 'info',
    'Demonstration': 'success'
  }
  return map[category] || 'info'
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
  filters.category = ''
  filters.relatedDecision = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredVideos.value.length} videos metadata...`)
}

const handleUploadVideo = () => {
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  if (file.raw) {
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadPreview.value = e.target?.result as string
    }
    reader.readAsDataURL(file.raw)
  }
}

const submitUpload = async () => {
  if (!uploadFormRef.value) return
  await uploadFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const newVideo: Video = {
        id: Date.now(),
        title: uploadForm.title,
        description: uploadForm.description,
        category: uploadForm.category,
        url: uploadPreview.value,
        thumbnail: generateThumbnail(videos.value.length + 1, uploadForm.category),
        duration: '00:00',
        fileSize: uploadForm.file ? `${(uploadForm.file.size / 1024 / 1024).toFixed(1)} MB` : 'Unknown',
        relatedDecision: uploadForm.relatedDecision,
        relatedDecisionId: 0,
        uploader: 'Current User',
        uploadDate: new Date().toISOString().split('T')[0],
        views: 0,
        downloads: 0,
        tags: []
      }
      videos.value.unshift(newVideo)
      ElMessage.success('Video uploaded successfully')
      uploadDialogVisible.value = false
      uploadFormRef.value?.resetFields()
      uploadPreview.value = ''
      uploadForm.file = null
      uploadRef.value?.clearFiles()
    }
  })
}

const playVideo = (video: Video) => {
  currentVideo.value = video
  // Increment view count
  const index = videos.value.findIndex(v => v.id === video.id)
  if (index !== -1) {
    videos.value[index].views++
  }
  playerDialogVisible.value = true
}

const deleteVideo = (video: Video) => {
  deleteTarget.value = video
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = videos.value.findIndex(v => v.id === deleteTarget.value!.id)
    if (index !== -1) {
      videos.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const viewDecision = (video: Video) => {
  if (video.relatedDecision) {
    ElMessage.info(`Viewing decision: ${video.relatedDecision}`)
  } else {
    ElMessage.info('No related decision found')
  }
}

const downloadVideo = () => {
  if (currentVideo.value) {
    // Increment download count
    const index = videos.value.findIndex(v => v.id === currentVideo.value!.id)
    if (index !== -1) {
      videos.value[index].downloads++
    }
    ElMessage.success(`Downloading: ${currentVideo.value.title}`)
  }
}

const shareVideo = () => {
  ElMessage.success('Share link copied to clipboard')
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
.videos-page {
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

.video-grid-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .view-toggle {
    display: flex;
    gap: 8px;
  }
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 20px 0;

  .video-card {
    overflow: hidden;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
    }

    .video-thumbnail-container {
      position: relative;
      height: 180px;
      overflow: hidden;
      cursor: pointer;
      background: #000;

      .video-thumbnail {
        width: 100%;
        height: 100%;
        object-fit: cover;
        opacity: 0.8;
      }

      .video-play-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.3s;

        .play-icon {
          width: 48px;
          height: 48px;
          color: white;
          opacity: 0.9;
        }
      }

      .video-duration {
        position: absolute;
        bottom: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
      }

      &:hover {
        .video-play-overlay {
          background: rgba(0, 0, 0, 0.2);

          .play-icon {
            transform: scale(1.1);
          }
        }
      }
    }

    .video-info {
      padding: 12px;

      .video-title {
        font-weight: 600;
        font-size: 14px;
        color: #303133;
        margin-bottom: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .video-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .video-date {
          font-size: 11px;
          color: #909399;
        }
      }

      .video-description {
        font-size: 12px;
        color: #606266;
        margin-bottom: 12px;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .video-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 8px;
        border-top: 1px solid #ebeef5;

        .video-uploader {
          font-size: 11px;
          color: #909399;
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .video-stats {
          display: flex;
          gap: 12px;
          font-size: 11px;
          color: #909399;

          span {
            display: flex;
            align-items: center;
            gap: 4px;
          }
        }
      }
    }
  }
}

.thumbnail-cell {
  position: relative;
  width: 100px;
  height: 56px;
  cursor: pointer;

  .thumbnail-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
  }

  .thumbnail-play {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
    font-size: 20px;
    text-shadow: 0 0 4px rgba(0,0,0,0.5);
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.upload-preview {
  margin-top: 12px;
  text-align: center;

  .preview-video {
    max-width: 100%;
    max-height: 200px;
    border-radius: 8px;
  }
}

.player-container {
  .video-player {
    width: 100%;
    max-height: 450px;
    border-radius: 8px;
  }

  .player-info {
    margin-top: 16px;
  }
}

:deep(.el-upload-dragger) {
  width: 100%;
}

:deep(.el-table) {
  font-size: 13px;
}
</style>