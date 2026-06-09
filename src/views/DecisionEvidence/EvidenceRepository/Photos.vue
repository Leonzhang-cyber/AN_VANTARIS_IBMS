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
        <div class="loading-tip">Photo Evidence Repository</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="photos-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Evidence Repository</el-breadcrumb-item>
            <el-breadcrumb-item>Photos</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Photo Evidence Repository</h1>
        <p class="description">Manage and organize photo evidence for maintenance, fault diagnosis, and inspection records</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleUploadPhoto">
          <el-icon><Plus /></el-icon>
          Upload Photo
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
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Fault Diagnosis" value="Fault Diagnosis" />
            <el-option label="Inspection" value="Inspection" />
            <el-option label="Before/After" value="Before/After" />
            <el-option label="Safety" value="Safety" />
            <el-option label="Equipment" value="Equipment" />
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

    <!-- Photo Grid -->
    <el-card class="photo-grid-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Photo Gallery ({{ filteredPhotos.length }} items)</span>
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
      <div v-if="viewMode === 'grid'" class="photo-grid" v-loading="loading">
        <el-card
            v-for="photo in paginatedPhotos"
            :key="photo.id"
            class="photo-card"
            shadow="hover"
            body-style="{ padding: '0px' }"
        >
          <div class="photo-image-container" @click="viewPhoto(photo)">
            <img :src="photo.thumbnail || photo.url" :alt="photo.title" class="photo-image" />
            <div class="photo-overlay">
              <div class="overlay-actions">
                <el-button circle size="small" type="primary" @click.stop="viewPhoto(photo)">
                  <el-icon><ZoomIn /></el-icon>
                </el-button>
                <el-button circle size="small" type="danger" @click.stop="deletePhoto(photo)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
          <div class="photo-info">
            <div class="photo-title">{{ photo.title }}</div>
            <div class="photo-meta">
              <el-tag :type="getCategoryTag(photo.category)" size="small">{{ photo.category }}</el-tag>
              <span class="photo-date">{{ photo.uploadDate }}</span>
            </div>
            <div class="photo-description" v-if="photo.description">{{ photo.description }}</div>
            <div class="photo-footer">
              <span class="photo-uploader">
                <el-icon><User /></el-icon>
                {{ photo.uploader }}
              </span>
              <el-button link type="primary" size="small" @click="viewDecision(photo)">View Decision</el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- List View -->
      <el-table v-else :data="paginatedPhotos" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="Thumbnail" width="80">
          <template #default="{ row }">
            <el-image :src="row.thumbnail || row.url" :preview-src-list="[row.url]" fit="cover" style="width: 50px; height: 50px; border-radius: 4px" />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="Title" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="130">
          <template #default="{ row }">
            <el-tag :type="getCategoryTag(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="relatedDecision" label="Related Decision" width="160" show-overflow-tooltip />
        <el-table-column prop="uploader" label="Uploader" width="120" />
        <el-table-column prop="uploadDate" label="Upload Date" width="110" />
        <el-table-column prop="fileSize" label="File Size" width="100" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewPhoto(row)">View</el-button>
            <el-button link type="danger" size="small" @click="deletePhoto(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[12, 24, 48, 96]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredPhotos.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload Photo" width="600px" destroy-on-close>
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="Title" prop="title">
          <el-input v-model="uploadForm.title" placeholder="Enter photo title" />
        </el-form-item>
        <el-form-item label="Category" prop="category">
          <el-select v-model="uploadForm.category" placeholder="Select category" style="width: 100%">
            <el-option label="Maintenance" value="Maintenance" />
            <el-option label="Fault Diagnosis" value="Fault Diagnosis" />
            <el-option label="Inspection" value="Inspection" />
            <el-option label="Before/After" value="Before/After" />
            <el-option label="Safety" value="Safety" />
            <el-option label="Equipment" value="Equipment" />
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
        <el-form-item label="Upload Photo" prop="file">
          <el-upload
              ref="uploadRef"
              class="upload-demo"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept="image/jpeg,image/png,image/jpg,image/gif,image/webp"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                JPG, PNG, GIF, WEBP files up to 10MB
              </div>
            </template>
          </el-upload>
          <div v-if="uploadPreview" class="upload-preview">
            <img :src="uploadPreview" alt="Preview" class="preview-image" />
          </div>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="uploadForm.description" type="textarea" :rows="3" placeholder="Enter photo description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitUpload">Upload</el-button>
      </template>
    </el-dialog>

    <!-- Photo Preview Dialog -->
    <el-dialog v-model="previewDialogVisible" :title="previewPhoto?.title" width="800px" destroy-on-close>
      <div class="preview-container">
        <img :src="previewPhoto?.url" :alt="previewPhoto?.title" class="preview-image-full" />
        <div class="preview-info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Category">
              <el-tag :type="getCategoryTag(previewPhoto?.category || '')" size="small">{{ previewPhoto?.category }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Uploader">{{ previewPhoto?.uploader }}</el-descriptions-item>
            <el-descriptions-item label="Upload Date">{{ previewPhoto?.uploadDate }}</el-descriptions-item>
            <el-descriptions-item label="File Size">{{ previewPhoto?.fileSize }}</el-descriptions-item>
            <el-descriptions-item label="Related Decision" :span="2">{{ previewPhoto?.relatedDecision || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ previewPhoto?.description || 'No description' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadPhoto">Download</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete photo "{{ deleteTarget?.title }}"?</p>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, ZoomIn, User, Grid, List, UploadFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading photo repository...',
  'Fetching images...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Photo {
  id: number
  title: string
  description: string
  category: string
  url: string
  thumbnail: string
  relatedDecision: string
  relatedDecisionId: number
  uploader: string
  uploadDate: string
  fileSize: string
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
  { title: 'Total Photos', value: 1248, trend: 15, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'This Month', value: 86, trend: 22, icon: 'TrendCharts', bgColor: '#67c23a', key: 'monthly' },
  { title: 'Categories', value: 6, trend: 0, icon: 'Grid', bgColor: '#e6a23c', key: 'categories' },
  { title: 'Storage Used', value: '2.4 GB', trend: 8, icon: 'Clock', bgColor: '#f56c6c', key: 'storage' }
])

// Generate placeholder images using data URLs
const generatePlaceholderImage = (index: number, category: string): string => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#9b59b6', '#3498db', '#2ecc71']
  const color = colors[index % colors.length]
  return `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='200' viewBox='0 0 300 200'%3E%3Crect width='300' height='200' fill='${color.replace('#', '%23')}'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' dy='.3em' fill='white' font-size='14'%3E${category}%3C/text%3E%3C/svg%3E`
}

const photos = ref<Photo[]>([
  {
    id: 1,
    title: 'Chiller Compressor Failure - Before',
    description: 'Close-up view of failed compressor showing bearing damage and oil leakage',
    category: 'Fault Diagnosis',
    url: generatePlaceholderImage(1, 'Chiller Failure'),
    thumbnail: generatePlaceholderImage(1, 'Chiller Failure'),
    relatedDecision: 'Chiller Overhaul Decision',
    relatedDecisionId: 101,
    uploader: 'John Smith',
    uploadDate: '2024-01-05',
    fileSize: '2.4 MB',
    tags: ['chiller', 'compressor', 'failure']
  },
  {
    id: 2,
    title: 'Chiller Overhaul - After',
    description: 'New compressor installed and system operational',
    category: 'Before/After',
    url: generatePlaceholderImage(2, 'After Repair'),
    thumbnail: generatePlaceholderImage(2, 'After Repair'),
    relatedDecision: 'Chiller Overhaul Decision',
    relatedDecisionId: 101,
    uploader: 'Mike Johnson',
    uploadDate: '2024-01-12',
    fileSize: '1.8 MB',
    tags: ['chiller', 'repair', 'completed']
  },
  {
    id: 3,
    title: 'LED Lighting Installation - Office Area',
    description: 'New LED fixtures installed in main office area showing improved lighting',
    category: 'Maintenance',
    url: generatePlaceholderImage(3, 'LED Installation'),
    thumbnail: generatePlaceholderImage(3, 'LED Installation'),
    relatedDecision: 'LED Lighting Retrofit',
    relatedDecisionId: 102,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-10',
    fileSize: '3.1 MB',
    tags: ['lighting', 'LED', 'energy']
  },
  {
    id: 4,
    title: 'Old Fluorescent vs New LED Comparison',
    description: 'Side by side comparison of old fluorescent and new LED lighting',
    category: 'Before/After',
    url: generatePlaceholderImage(4, 'Lighting Compare'),
    thumbnail: generatePlaceholderImage(4, 'Lighting Compare'),
    relatedDecision: 'LED Lighting Retrofit',
    relatedDecisionId: 102,
    uploader: 'Lisa Zhang',
    uploadDate: '2024-01-08',
    fileSize: '2.9 MB',
    tags: ['comparison', 'lighting']
  },
  {
    id: 5,
    title: 'UPS Battery Swelling',
    description: 'Battery bank showing visible swelling and deformation',
    category: 'Fault Diagnosis',
    url: generatePlaceholderImage(5, 'UPS Battery'),
    thumbnail: generatePlaceholderImage(5, 'UPS Battery'),
    relatedDecision: 'UPS Battery Replacement',
    relatedDecisionId: 103,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-10',
    fileSize: '2.1 MB',
    tags: ['UPS', 'battery', 'fault']
  },
  {
    id: 6,
    title: 'New UPS Battery Installation',
    description: 'New lithium-ion battery bank installed and operational',
    category: 'Maintenance',
    url: generatePlaceholderImage(6, 'New UPS'),
    thumbnail: generatePlaceholderImage(6, 'New UPS'),
    relatedDecision: 'UPS Battery Replacement',
    relatedDecisionId: 103,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-12',
    fileSize: '2.3 MB',
    tags: ['UPS', 'battery', 'installation']
  },
  {
    id: 7,
    title: 'Solar Panel Roof Installation - Day 1',
    description: 'Racking system installation on main building roof',
    category: 'Inspection',
    url: generatePlaceholderImage(7, 'Solar Install'),
    thumbnail: generatePlaceholderImage(7, 'Solar Install'),
    relatedDecision: 'Solar Panel Installation',
    relatedDecisionId: 104,
    uploader: 'Emily Zhao',
    uploadDate: '2024-01-15',
    fileSize: '3.5 MB',
    tags: ['solar', 'renewable', 'roof']
  },
  {
    id: 8,
    title: 'HVAC Control Panel - Before',
    description: 'Old control panel showing outdated components',
    category: 'Equipment',
    url: generatePlaceholderImage(8, 'Old Panel'),
    thumbnail: generatePlaceholderImage(8, 'Old Panel'),
    relatedDecision: 'HVAC Optimization Algorithm',
    relatedDecisionId: 105,
    uploader: 'David Wang',
    uploadDate: '2024-01-09',
    fileSize: '1.9 MB',
    tags: ['HVAC', 'controls', 'before']
  },
  {
    id: 9,
    title: 'New Smart Thermostat Installation',
    description: 'Smart thermostats installed across all zones',
    category: 'Maintenance',
    url: generatePlaceholderImage(9, 'Smart Thermostat'),
    thumbnail: generatePlaceholderImage(9, 'Smart Thermostat'),
    relatedDecision: 'HVAC Optimization Algorithm',
    relatedDecisionId: 105,
    uploader: 'David Wang',
    uploadDate: '2024-01-11',
    fileSize: '2.6 MB',
    tags: ['HVAC', 'thermostat', 'smart']
  },
  {
    id: 10,
    title: 'Safety Inspection - Fire Extinguisher',
    description: 'Monthly safety inspection of fire extinguisher stations',
    category: 'Safety',
    url: generatePlaceholderImage(10, 'Safety'),
    thumbnail: generatePlaceholderImage(10, 'Safety'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Robert Liu',
    uploadDate: '2024-01-14',
    fileSize: '1.5 MB',
    tags: ['safety', 'inspection', 'fire']
  },
  {
    id: 11,
    title: 'Cooling Tower Fan Blade Damage',
    description: 'Cracked fan blade discovered during routine inspection',
    category: 'Fault Diagnosis',
    url: generatePlaceholderImage(11, 'Fan Damage'),
    thumbnail: generatePlaceholderImage(11, 'Fan Damage'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Mike Johnson',
    uploadDate: '2024-01-13',
    fileSize: '2.8 MB',
    tags: ['cooling', 'fan', 'damage']
  },
  {
    id: 12,
    title: 'Building Exterior - Drone Inspection',
    description: 'Thermal imaging showing heat loss areas',
    category: 'Inspection',
    url: generatePlaceholderImage(12, 'Drone'),
    thumbnail: generatePlaceholderImage(12, 'Drone'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Sarah Chen',
    uploadDate: '2024-01-07',
    fileSize: '4.2 MB',
    tags: ['drone', 'thermal', 'inspection']
  },
  {
    id: 13,
    title: 'Water Leak Detection',
    description: 'Moisture detected near pipe joint',
    category: 'Fault Diagnosis',
    url: generatePlaceholderImage(13, 'Water Leak'),
    thumbnail: generatePlaceholderImage(13, 'Water Leak'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Chris Lee',
    uploadDate: '2024-01-06',
    fileSize: '2.2 MB',
    tags: ['plumbing', 'leak', 'water']
  },
  {
    id: 14,
    title: 'Server Room Temperature Monitoring',
    description: 'Temperature sensors installed in server racks',
    category: 'Equipment',
    url: generatePlaceholderImage(14, 'Server'),
    thumbnail: generatePlaceholderImage(14, 'Server'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'Tom Harris',
    uploadDate: '2024-01-04',
    fileSize: '1.7 MB',
    tags: ['server', 'temperature', 'monitoring']
  },
  {
    id: 15,
    title: 'Before: Old Boiler System',
    description: 'Outdated boiler with efficiency issues',
    category: 'Before/After',
    url: generatePlaceholderImage(15, 'Old Boiler'),
    thumbnail: generatePlaceholderImage(15, 'Old Boiler'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'John Smith',
    uploadDate: '2024-01-03',
    fileSize: '3.0 MB',
    tags: ['boiler', 'before', 'efficiency']
  },
  {
    id: 16,
    title: 'After: New High-Efficiency Boiler',
    description: 'New condensing boiler installation completed',
    category: 'Before/After',
    url: generatePlaceholderImage(16, 'New Boiler'),
    thumbnail: generatePlaceholderImage(16, 'New Boiler'),
    relatedDecision: '',
    relatedDecisionId: 0,
    uploader: 'John Smith',
    uploadDate: '2024-01-18',
    fileSize: '3.2 MB',
    tags: ['boiler', 'after', 'efficiency']
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const previewPhoto = ref<Photo | null>(null)
const deleteTarget = ref<Photo | null>(null)
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
  title: [{ required: true, message: 'Please enter photo title', trigger: 'blur' }],
  category: [{ required: true, message: 'Please select category', trigger: 'change' }],
  file: [{ required: true, message: 'Please select a photo to upload', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredPhotos = computed(() => {
  let filtered = [...photos.value]

  if (filters.keyword) {
    filtered = filtered.filter(p =>
        p.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        p.description.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        p.tags.some(tag => tag.toLowerCase().includes(filters.keyword.toLowerCase()))
    )
  }

  if (filters.category) {
    filtered = filtered.filter(p => p.category === filters.category)
  }

  if (filters.relatedDecision) {
    filtered = filtered.filter(p => p.relatedDecision === filters.relatedDecision)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(p => {
      const date = new Date(p.uploadDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedPhotos = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPhotos.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCategoryTag = (category: string): string => {
  const map: Record<string, string> = {
    'Maintenance': 'primary',
    'Fault Diagnosis': 'danger',
    'Inspection': 'warning',
    'Before/After': 'success',
    'Safety': 'info',
    'Equipment': 'success'
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
  ElMessage.success(`Exporting ${filteredPhotos.value.length} photos...`)
}

const handleUploadPhoto = () => {
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
      const newPhoto: Photo = {
        id: Date.now(),
        title: uploadForm.title,
        description: uploadForm.description,
        category: uploadForm.category,
        url: uploadPreview.value,
        thumbnail: uploadPreview.value,
        relatedDecision: uploadForm.relatedDecision,
        relatedDecisionId: 0,
        uploader: 'Current User',
        uploadDate: new Date().toISOString().split('T')[0],
        fileSize: uploadForm.file ? `${(uploadForm.file.size / 1024 / 1024).toFixed(1)} MB` : 'Unknown',
        tags: []
      }
      photos.value.unshift(newPhoto)
      ElMessage.success('Photo uploaded successfully')
      uploadDialogVisible.value = false
      uploadFormRef.value?.resetFields()
      uploadPreview.value = ''
      uploadForm.file = null
      uploadRef.value?.clearFiles()
    }
  })
}

const viewPhoto = (photo: Photo) => {
  previewPhoto.value = photo
  previewDialogVisible.value = true
}

const deletePhoto = (photo: Photo) => {
  deleteTarget.value = photo
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = photos.value.findIndex(p => p.id === deleteTarget.value!.id)
    if (index !== -1) {
      photos.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const viewDecision = (photo: Photo) => {
  if (photo.relatedDecision) {
    ElMessage.info(`Viewing decision: ${photo.relatedDecision}`)
  } else {
    ElMessage.info('No related decision found')
  }
}

const downloadPhoto = () => {
  if (previewPhoto.value) {
    ElMessage.success(`Downloading: ${previewPhoto.value.title}`)
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
.photos-page {
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

.photo-grid-card {
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

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 20px 0;

  .photo-card {
    overflow: hidden;
    transition: all 0.3s;

    &:hover {
      transform: translateY(-4px);
    }

    .photo-image-container {
      position: relative;
      height: 200px;
      overflow: hidden;
      cursor: pointer;

      .photo-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s;
      }

      .photo-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;

        .overlay-actions {
          display: flex;
          gap: 12px;
        }
      }

      &:hover {
        .photo-image {
          transform: scale(1.05);
        }

        .photo-overlay {
          opacity: 1;
        }
      }
    }

    .photo-info {
      padding: 12px;

      .photo-title {
        font-weight: 600;
        font-size: 14px;
        color: #303133;
        margin-bottom: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .photo-meta {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        .photo-date {
          font-size: 11px;
          color: #909399;
        }
      }

      .photo-description {
        font-size: 12px;
        color: #606266;
        margin-bottom: 12px;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .photo-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 8px;
        border-top: 1px solid #ebeef5;

        .photo-uploader {
          font-size: 11px;
          color: #909399;
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }
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

  .preview-image {
    max-width: 200px;
    max-height: 150px;
    border-radius: 8px;
    object-fit: cover;
  }
}

.preview-container {
  .preview-image-full {
    width: 100%;
    max-height: 400px;
    object-fit: contain;
    margin-bottom: 20px;
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
</style>