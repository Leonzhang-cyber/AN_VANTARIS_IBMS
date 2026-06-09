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
        <div class="loading-tip">Data Lake Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="data-lake-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Lake</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Lake</h1>
        <p class="description">Centralized repository for raw, processed, and curated data assets</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Metadata
        </el-button>
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>
          Upload File
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

    <!-- Storage Overview Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card class="storage-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Storage Usage by Zone</span>
              <el-radio-group v-model="storagePeriod" size="small">
                <el-radio-button value="daily">Daily</el-radio-button>
                <el-radio-button value="weekly">Weekly</el-radio-button>
                <el-radio-button value="monthly">Monthly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="storageChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="zone-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Storage by Zone</span>
            </div>
          </template>
          <div ref="zoneChartRef" class="pie-chart-container"></div>
          <div class="zone-legend">
            <div class="legend-item" v-for="zone in zones" :key="zone.name">
              <span class="legend-color" :style="{ background: zone.color }"></span>
              <span class="legend-name">{{ zone.name }}</span>
              <span class="legend-size">{{ zone.size }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Zone Tabs & File Browser -->
    <el-card class="browser-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Data Lake Browser</span>
          <div class="browser-actions">
            <el-button size="small" @click="refreshBrowser">
              <el-icon><Refresh /></el-icon>
            </el-button>
            <el-button size="small" @click="createFolder">
              <el-icon><FolderAdd /></el-icon>
              New Folder
            </el-button>
          </div>
        </div>
      </template>

      <!-- Zone Tabs -->
      <el-tabs v-model="activeZone" @tab-click="handleZoneChange">
        <el-tab-pane label="Raw Zone" name="raw">
          <template #label>
            <span><el-icon><Document /></el-icon> Raw Zone</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Processed Zone" name="processed">
          <template #label>
            <span><el-icon><DataAnalysis /></el-icon> Processed Zone</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Curated Zone" name="curated">
          <template #label>
            <span><el-icon><Checked /></el-icon> Curated Zone</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Temp Zone" name="temp">
          <template #label>
            <span><el-icon><Clock /></el-icon> Temp Zone</span>
          </template>
        </el-tab-pane>
      </el-tabs>

      <!-- File Browser Breadcrumb -->
      <div class="file-browser">
        <div class="breadcrumb-bar">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>
              <el-link @click="navigateToRoot">data-lake</el-link>
            </el-breadcrumb-item>
            <el-breadcrumb-item v-for="(part, idx) in currentPath" :key="idx">
              <el-link @click="navigateToPath(idx)">{{ part }}</el-link>
            </el-breadcrumb-item>
          </el-breadcrumb>
          <div class="path-actions">
            <el-input
                v-model="searchFile"
                placeholder="Search files"
                prefix-icon="Search"
                size="small"
                style="width: 200px"
                clearable
            />
          </div>
        </div>

        <!-- File/ Folder Table -->
        <el-table :data="filteredItems" stripe style="width: 100%" v-loading="tableLoading">
          <el-table-column label="Name" min-width="250">
            <template #default="{ row }">
              <div class="file-name" @click="row.type === 'folder' ? navigateToFolder(row) : previewFileMap(row)">
                <el-icon :color="row.type === 'folder' ? '#e6a23c' : '#409eff'" :size="20">
                  <component :is="row.type === 'folder' ? 'Folder' : 'Document'" />
                </el-icon>
                <span>{{ row.name }}</span>
                <el-tag v-if="row.partitioned" type="info" size="small" class="file-tag">Partitioned</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="size" label="Size" width="120">
            <template #default="{ row }">
              <span v-if="row.type === 'file'">{{ row.size }}</span>
              <span v-else class="folder-size">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="format" label="Format" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.format" :type="getFormatTag(row.format)" size="small">{{ row.format }}</el-tag>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column prop="records" label="Records" width="120" align="right">
            <template #default="{ row }">
              <span v-if="row.records">{{ row.records.toLocaleString() }}</span>
              <span v-else>—</span>
            </template>
          </el-table-column>
          <el-table-column prop="modified" label="Last Modified" width="160" />
          <el-table-column label="Actions" width="200" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.type === 'file'" link type="primary" size="small" @click="previewFileMap(row)">Preview</el-button>
              <el-button v-if="row.type === 'file'" link type="success" size="small" @click="downloadFile(row)">Download</el-button>
              <el-button link type="danger" size="small" @click="deleteItem(row)">Delete</el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
        <div class="pagination-container">
          <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[15, 30, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="filteredItems.length"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </el-card>

    <!-- File Preview Dialog -->
    <el-dialog v-model="previewDialogVisible" :title="previewFile?.name" width="800px" destroy-on-close>
      <div class="preview-container" v-loading="previewLoading">
        <div class="preview-header">
          <el-descriptions :column="3" border size="small">
            <el-descriptions-item label="Path">{{ previewFile?.path }}</el-descriptions-item>
            <el-descriptions-item label="Size">{{ previewFile?.size }}</el-descriptions-item>
            <el-descriptions-item label="Format">{{ previewFile?.format }}</el-descriptions-item>
            <el-descriptions-item label="Records">{{ previewFile?.records?.toLocaleString() || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Last Modified">{{ previewFile?.modified }}</el-descriptions-item>
            <el-descriptions-item label="Partitioned">{{ previewFile?.partitioned ? 'Yes' : 'No' }}</el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="preview-data" v-if="previewData">
          <h4>Data Preview (First 10 rows)</h4>
          <el-table :data="previewData" size="small" border>
            <el-table-column v-for="col in previewColumns" :key="col" :prop="col" :label="col" min-width="120" />
          </el-table>
        </div>
        <div class="preview-schema" v-if="previewSchema">
          <h4>Schema</h4>
          <el-table :data="previewSchema" size="small" border>
            <el-table-column prop="column" label="Column Name" width="200" />
            <el-table-column prop="type" label="Data Type" width="150" />
            <el-table-column prop="nullable" label="Nullable" width="100">
              <template #default="{ row }">
                <el-tag :type="row.nullable ? 'success' : 'danger'" size="small">{{ row.nullable ? 'Yes' : 'No' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadCurrentFile">Download</el-button>
      </template>
    </el-dialog>

    <!-- Upload Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload File" width="500px" destroy-on-close>
      <el-form :model="uploadForm" :rules="uploadRules" ref="uploadFormRef" label-width="100px">
        <el-form-item label="Upload to" prop="targetPath">
          <el-input v-model="uploadForm.targetPath" placeholder="/data-lake/raw/" disabled />
        </el-form-item>
        <el-form-item label="File" prop="file">
          <el-upload
              ref="uploadRef"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              :file-list="fileList"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Parquet, CSV, JSON, Avro files up to 5GB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" placeholder="Enter file description" />
        </el-form-item>
        <el-form-item label="Tags" prop="tags">
          <el-select v-model="uploadForm.tags" multiple filterable allow-create default-first-option placeholder="Enter tags" style="width: 100%">
            <el-option label="Raw" value="Raw" />
            <el-option label="Processed" value="Processed" />
            <el-option label="Curated" value="Curated" />
            <el-option label="Temporary" value="Temporary" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitUpload">Upload</el-button>
      </template>
    </el-dialog>

    <!-- Create Folder Dialog -->
    <el-dialog v-model="folderDialogVisible" title="Create Folder" width="400px" destroy-on-close>
      <el-form :model="folderForm" :rules="folderRules" ref="folderFormRef" label-width="100px">
        <el-form-item label="Folder Name" prop="name">
          <el-input v-model="folderForm.name" placeholder="Enter folder name" />
        </el-form-item>
        <el-form-item label="Zone" prop="zone">
          <el-select v-model="folderForm.zone" placeholder="Select zone" style="width: 100%">
            <el-option label="Raw Zone" value="raw" />
            <el-option label="Processed Zone" value="processed" />
            <el-option label="Curated Zone" value="curated" />
            <el-option label="Temp Zone" value="temp" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="folderForm.description" type="textarea" :rows="2" placeholder="Enter folder description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="folderDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitCreateFolder">Create</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Upload, Folder, FolderAdd, DataAnalysis
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading data lake...',
  'Scanning storage...',
  'Almost ready...'
]

// ==================== Chart References ====================
const storageChartRef = ref<HTMLElement>()
const zoneChartRef = ref<HTMLElement>()
let storageChart: echarts.ECharts | null = null
let zoneChart: echarts.ECharts | null = null

// ==================== State ====================
const activeZone = ref('raw')
const currentPath = ref<string[]>([])
const searchFile = ref('')
const tableLoading = ref(false)
const previewDialogVisible = ref(false)
const uploadDialogVisible = ref(false)
const folderDialogVisible = ref(false)
const previewLoading = ref(false)
const previewData = ref<any[]>([])
const previewColumns = ref<string[]>([])
const previewSchema = ref<any[]>([])
const previewFile = ref<any>(null)
const uploadFormRef = ref()
const folderFormRef = ref()
const uploadRef = ref()
const fileList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(15)
const storagePeriod = ref('daily')

const zones = ref([
  { name: 'Raw Zone', color: '#409eff', size: '124.5 TB' },
  { name: 'Processed Zone', color: '#67c23a', size: '87.2 TB' },
  { name: 'Curated Zone', color: '#e6a23c', size: '42.8 TB' },
  { name: 'Temp Zone', color: '#909399', size: '18.5 TB' }
])

// Mock file system data
const fileSystem = ref({
  raw: {
    name: 'raw',
    type: 'zone',
    children: [
      {
        name: 'device_data',
        type: 'folder',
        children: [
          { name: '2024-01-15.parquet', type: 'file', size: '245 MB', format: 'Parquet', records: 1250000, modified: '2024-01-15 10:30:00', partitioned: false, path: '/raw/device_data/2024-01-15.parquet' },
          { name: '2024-01-16.parquet', type: 'file', size: '256 MB', format: 'Parquet', records: 1320000, modified: '2024-01-16 10:30:00', partitioned: false, path: '/raw/device_data/2024-01-16.parquet' },
          { name: '2024-01-17.parquet', type: 'file', size: '248 MB', format: 'Parquet', records: 1280000, modified: '2024-01-17 10:30:00', partitioned: false, path: '/raw/device_data/2024-01-17.parquet' }
        ]
      },
      {
        name: 'sensor_readings',
        type: 'folder',
        children: [
          { name: 'readings_jan.csv', type: 'file', size: '512 MB', format: 'CSV', records: 3450000, modified: '2024-01-20 08:00:00', partitioned: false, path: '/raw/sensor_readings/readings_jan.csv' },
          { name: 'readings_dec.csv', type: 'file', size: '498 MB', format: 'CSV', records: 3320000, modified: '2024-01-01 08:00:00', partitioned: false, path: '/raw/sensor_readings/readings_dec.csv' }
        ]
      },
      {
        name: 'logs',
        type: 'folder',
        children: [
          { name: 'application_logs.json', type: 'file', size: '1.2 GB', format: 'JSON', records: 8900000, modified: '2024-01-20 09:00:00', partitioned: true, path: '/raw/logs/application_logs.json' }
        ]
      }
    ]
  },
  processed: {
    name: 'processed',
    type: 'zone',
    children: [
      {
        name: 'daily_aggregates',
        type: 'folder',
        children: [
          { name: 'agg_2024_01.parquet', type: 'file', size: '89 MB', format: 'Parquet', records: 310000, modified: '2024-01-20 12:00:00', partitioned: false, path: '/processed/daily_aggregates/agg_2024_01.parquet' }
        ]
      },
      {
        name: 'cleaned_sensors',
        type: 'folder',
        children: [
          { name: 'sensors_clean.parquet', type: 'file', size: '156 MB', format: 'Parquet', records: 2450000, modified: '2024-01-19 14:30:00', partitioned: false, path: '/processed/cleaned_sensors/sensors_clean.parquet' }
        ]
      }
    ]
  },
  curated: {
    name: 'curated',
    type: 'zone',
    children: [
      {
        name: 'dim_devices',
        type: 'folder',
        children: [
          { name: 'dim_devices.parquet', type: 'file', size: '12 MB', format: 'Parquet', records: 12500, modified: '2024-01-18 16:00:00', partitioned: false, path: '/curated/dim_devices/dim_devices.parquet' }
        ]
      },
      {
        name: 'fact_readings',
        type: 'folder',
        children: [
          { name: 'fact_readings_2024.parquet', type: 'file', size: '234 MB', format: 'Parquet', records: 5678000, modified: '2024-01-20 11:00:00', partitioned: true, path: '/curated/fact_readings/fact_readings_2024.parquet' }
        ]
      }
    ]
  },
  temp: {
    name: 'temp',
    type: 'zone',
    children: [
      { name: 'temp_export_2024-01-15.csv', type: 'file', size: '45 MB', format: 'CSV', records: 234000, modified: '2024-01-15 09:00:00', partitioned: false, path: '/temp/temp_export_2024-01-15.csv' },
      { name: 'staging_data.parquet', type: 'file', size: '67 MB', format: 'Parquet', records: 456000, modified: '2024-01-19 15:00:00', partitioned: false, path: '/temp/staging_data.parquet' }
    ]
  }
})

const currentItems = computed(() => {
  let items = getCurrentItems()

  // Filter by search
  if (searchFile.value) {
    items = items.filter(item =>
        item.name.toLowerCase().includes(searchFile.value.toLowerCase())
    )
  }

  return items
})

const filteredItems = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return currentItems.value.slice(start, end)
})

const uploadForm = reactive({
  targetPath: '',
  description: '',
  tags: [] as string[],
  file: null as File | null
})

const folderForm = reactive({
  name: '',
  zone: 'raw',
  description: ''
})

const uploadRules = {
  file: [{ required: true, message: 'Please select a file', trigger: 'change' }]
}

const folderRules = {
  name: [{ required: true, message: 'Please enter folder name', trigger: 'blur' }]
}

// ==================== Stats Cards ====================
const statsCards = ref([
  { title: 'Total Storage', value: '273 TB', trend: 12, icon: 'Document', bgColor: '#409eff', key: 'storage' },
  { title: 'Total Files', value: '12,456', trend: 8, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'files' },
  { title: 'Total Records', value: '2.45B', trend: 15, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'records' },
  { title: 'Active Users', value: '34', trend: 5, icon: 'User', bgColor: '#f56c6c', key: 'users' }
])

// ==================== Helper Methods ====================
const getFormatTag = (format: string) => {
  const map: Record<string, string> = {
    'Parquet': 'success',
    'CSV': 'primary',
    'JSON': 'warning',
    'Avro': 'info'
  }
  return map[format] || 'info'
}

const getCurrentItems = () => {
  const zoneData = fileSystem.value[activeZone as keyof typeof fileSystem.value]
  if (!zoneData) return []

  let items = [...zoneData.children]

  for (const pathPart of currentPath.value) {
    const folder = items.find(i => i.type === 'folder' && i.name === pathPart)
    if (folder && folder.children) {
      items = folder.children
    }
  }

  return items
}

const navigateToRoot = () => {
  currentPath.value = []
}

const navigateToPath = (idx: number) => {
  currentPath.value = currentPath.value.slice(0, idx + 1)
}

const navigateToFolder = (folder: any) => {
  currentPath.value.push(folder.name)
}

const handleZoneChange = () => {
  currentPath.value = []
  searchFile.value = ''
}

const refreshBrowser = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Browser refreshed')
  }, 500)
}

const createFolder = () => {
  folderDialogVisible.value = true
}

const previewFileMap = (file: any) => {
  previewFile.value = file
  previewDialogVisible.value = true
  previewLoading.value = true

  // Mock preview data
  setTimeout(() => {
    if (file.name.includes('devices')) {
      previewColumns.value = ['device_id', 'device_name', 'device_type', 'location', 'status']
      previewData.value = [
        { device_id: 'DEV-001', device_name: 'Temperature Sensor', device_type: 'sensor', location: 'Building A', status: 'active' },
        { device_id: 'DEV-002', device_name: 'Pressure Sensor', device_type: 'sensor', location: 'Building B', status: 'active' }
      ]
      previewSchema.value = [
        { column: 'device_id', type: 'string', nullable: false },
        { column: 'device_name', type: 'string', nullable: false },
        { column: 'device_type', type: 'string', nullable: false },
        { column: 'location', type: 'string', nullable: true },
        { column: 'status', type: 'string', nullable: false }
      ]
    } else if (file.name.includes('readings')) {
      previewColumns.value = ['reading_id', 'device_id', 'timestamp', 'value', 'unit']
      previewData.value = [
        { reading_id: 1, device_id: 'DEV-001', timestamp: '2024-01-20 10:00:00', value: 22.5, unit: '°C' },
        { reading_id: 2, device_id: 'DEV-001', timestamp: '2024-01-20 10:05:00', value: 22.6, unit: '°C' }
      ]
      previewSchema.value = [
        { column: 'reading_id', type: 'bigint', nullable: false },
        { column: 'device_id', type: 'string', nullable: false },
        { column: 'timestamp', type: 'timestamp', nullable: false },
        { column: 'value', type: 'double', nullable: false },
        { column: 'unit', type: 'string', nullable: true }
      ]
    } else {
      previewColumns.value = ['id', 'name', 'value', 'timestamp']
      previewData.value = [
        { id: 1, name: 'sample', value: 100, timestamp: '2024-01-20 10:00:00' }
      ]
      previewSchema.value = [
        { column: 'id', type: 'int', nullable: false },
        { column: 'name', type: 'string', nullable: false },
        { column: 'value', type: 'double', nullable: false },
        { column: 'timestamp', type: 'timestamp', nullable: false }
      ]
    }
    previewLoading.value = false
  }, 1000)
}

const downloadFile = (file: any) => {
  ElMessage.success(`Downloading: ${file.name}`)
}

const downloadCurrentFile = () => {
  if (previewFile.value) {
    downloadFile(previewFile.value)
  }
}

const deleteItem = (item: any) => {
  ElMessageBox.confirm(`Delete "${item.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.success(`Deleted: ${item.name}`)
  }).catch(() => {})
}

const handleUpload = () => {
  uploadForm.targetPath = `/data-lake/${activeZone.value}${currentPath.value.length ? '/' + currentPath.value.join('/') : ''}`
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadForm.file = file.raw
  fileList.value = [file]
}

const submitUpload = async () => {
  if (!uploadFormRef.value) return
  await uploadFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('File uploaded successfully')
      uploadDialogVisible.value = false
      uploadFormRef.value?.resetFields()
      fileList.value = []
      uploadForm.file = null
    }
  })
}

const submitCreateFolder = async () => {
  if (!folderFormRef.value) return
  await folderFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(`Folder "${folderForm.name}" created successfully`)
      folderDialogVisible.value = false
      folderFormRef.value?.resetFields()
    }
  })
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting data lake metadata...')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Chart Initializations ====================
const initStorageChart = () => {
  if (!storageChartRef.value) return
  if (storageChart) storageChart.dispose()

  storageChart = echarts.init(storageChartRef.value)

  const dailyData = [45, 48, 52, 55, 58, 62, 65, 68, 72, 75, 78, 82, 85, 88, 92, 95, 98, 102, 105, 108, 112, 115, 118, 122, 125, 128, 132, 135, 138, 142]
  const weeklyData = [320, 345, 368, 392, 415, 438, 462, 485, 508, 532, 555, 578]
  const monthlyData = [1250, 1320, 1380, 1450, 1520, 1580, 1650, 1720, 1780, 1850, 1920, 1980]

  let data, xAxisData
  if (storagePeriod.value === 'daily') {
    data = dailyData
    xAxisData = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
  } else if (storagePeriod.value === 'weekly') {
    data = weeklyData
    xAxisData = Array.from({ length: 12 }, (_, i) => `Week ${i + 1}`)
  } else {
    data = monthlyData
    xAxisData = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Storage (TB)' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 6
    }]
  }

  storageChart.setOption(option)
  window.addEventListener('resize', () => storageChart?.resize())
}

const initZoneChart = () => {
  if (!zoneChartRef.value) return
  if (zoneChart) zoneChart.dispose()

  zoneChart = echarts.init(zoneChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} TB)' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: zones.value.map(z => ({ name: z.name, value: parseFloat(z.size) })),
      label: { show: true, formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }

  zoneChart.setOption(option)
  window.addEventListener('resize', () => zoneChart?.resize())
}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initStorageChart()
    initZoneChart()
  }, 100)
}

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
      initCharts()
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
.data-lake-page {
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

.chart-row {
  margin-bottom: 20px;
}

.storage-card, .zone-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.pie-chart-container {
  width: 100%;
  height: 280px;
}

.zone-legend {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;

    .legend-color {
      width: 12px;
      height: 12px;
      border-radius: 2px;
    }

    .legend-name {
      flex: 1;
      font-size: 13px;
      color: #606266;
    }

    .legend-size {
      font-weight: 600;
      color: #303133;
    }
  }
}

.browser-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .browser-actions {
    display: flex;
    gap: 8px;
  }
}

.file-browser {
  .breadcrumb-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #ebeef5;
  }

  .file-name {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;

    &:hover {
      color: #409eff;
    }

    .file-tag {
      margin-left: 8px;
    }
  }

  .folder-size {
    color: #c0c4cc;
  }
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.preview-container {
  .preview-header {
    margin-bottom: 20px;
  }

  .preview-data, .preview-schema {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-tabs__header) {
  margin-bottom: 16px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>