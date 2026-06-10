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
        <div class="loading-tip">BIM Integration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="bim-integration-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Third-Party Systems</el-breadcrumb-item>
            <el-breadcrumb-item>BIM</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>BIM Integration</h1>
        <p class="description">Integrate with Revit, Navisworks, IFC models for digital twin and asset lifecycle management</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Models
        </el-button>
        <el-button type="primary" @click="openAddModelDialog">
          <el-icon><Plus /></el-icon>
          Import BIM Model
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
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span>{{ stat.subTitle }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- BIM Systems Cards -->
    <el-row :gutter="20" class="bim-cards-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="bim in bimSystems" :key="bim.name">
        <el-card class="bim-card" shadow="hover" @click="selectBIMSystem(bim)">
          <div class="bim-card-content">
            <div class="bim-icon" :style="{ background: bim.color }">
              <el-icon :size="32"><component :is="bim.icon" /></el-icon>
            </div>
            <div class="bim-info">
              <div class="bim-name">{{ bim.name }}</div>
              <div class="bim-status">
                <el-tag :type="bim.status === 'Connected' ? 'success' : 'danger'" size="small">
                  {{ bim.status }}
                </el-tag>
              </div>
              <div class="bim-version">{{ bim.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Model Viewer & Info -->
    <el-row :gutter="20" class="model-row">
      <el-col :xs="24" :lg="16">
        <el-card class="model-viewer-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>3D Model Viewer</span>
              <div class="viewer-controls">
                <el-button-group size="small">
                  <el-button @click="rotateModel">Rotate</el-button>
                  <el-button @click="panModel">Pan</el-button>
                  <el-button @click="zoomModel">Zoom</el-button>
                  <el-button @click="resetView">Reset</el-button>
                </el-button-group>
              </div>
            </div>
          </template>
          <div class="model-viewer-container">
            <div class="model-placeholder">
              <el-icon :size="64"><Monitor /></el-icon>
              <p>3D Model Preview Area</p>
              <p class="model-hint">Click on any element to view asset information</p>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="asset-info-card" shadow="hover" v-if="selectedAsset">
          <template #header>
            <div class="card-header">
              <span>Asset Information</span>
              <el-button link type="primary" size="small" @click="syncToIBMS">Sync to IBMS</el-button>
            </div>
          </template>
          <div class="asset-details">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="GUID">{{ selectedAsset.guid }}</el-descriptions-item>
              <el-descriptions-item label="Name">{{ selectedAsset.name }}</el-descriptions-item>
              <el-descriptions-item label="Type">{{ selectedAsset.type }}</el-descriptions-item>
              <el-descriptions-item label="Family">{{ selectedAsset.family }}</el-descriptions-item>
              <el-descriptions-item label="Category">{{ selectedAsset.category }}</el-descriptions-item>
              <el-descriptions-item label="Location">{{ selectedAsset.location }}</el-descriptions-item>
              <el-descriptions-item label="Level">{{ selectedAsset.level }}</el-descriptions-item>
              <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
              <el-descriptions-item label="Model">{{ selectedAsset.modelNumber }}</el-descriptions-item>
              <el-descriptions-item label="Installation Date">{{ selectedAsset.installationDate }}</el-descriptions-item>
              <el-descriptions-item label="Status">{{ selectedAsset.status }}</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
        <el-card class="asset-info-card" shadow="hover" v-else>
          <div class="empty-asset">
            <el-empty description="Select an asset from the 3D model" :image-size="80" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- BIM Models Table -->
    <el-card class="models-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>BIM Models</span>
          <div class="models-actions">
            <el-input
                v-model="modelSearch"
                placeholder="Search models"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="fileFormatFilter" placeholder="Format" clearable style="width: 120px">
              <el-option label="IFC" value="IFC" />
              <el-option label="RVT" value="RVT" />
              <el-option label="NWD" value="NWD" />
              <el-option label="DWG" value="DWG" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchModels" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedModels" stripe style="width: 100%" v-loading="modelsLoading">
        <el-table-column prop="name" label="Model Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="project" label="Project" width="180" show-overflow-tooltip />
        <el-table-column prop="format" label="Format" width="80">
          <template #default="{ row }">
            <el-tag :type="getFormatTag(row.format)" size="small">{{ row.format }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fileSize" label="Size" width="100" />
        <el-table-column prop="assetCount" label="Assets" width="80" align="center" />
        <el-table-column prop="version" label="Version" width="100" />
        <el-table-column prop="lastSync" label="Last Sync" width="150" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewModel(row)">View</el-button>
            <el-button link type="success" size="small" @click="syncModel(row)">Sync Assets</el-button>
            <el-button link type="info" size="small" @click="viewAssetList(row)">Assets</el-button>
            <el-button link type="danger" size="small" @click="deleteModel(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="modelsPage"
            v-model:page-size="modelsPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredModels.length"
            @size-change="modelsPage = 1"
        />
      </div>
    </el-card>

    <!-- Asset List Table -->
    <el-card class="assets-card" shadow="hover" v-if="showAssetList">
      <template #header>
        <div class="card-header">
          <span>Assets from {{ currentModel?.name }}</span>
          <div class="assets-actions">
            <el-input
                v-model="assetSearch"
                placeholder="Search assets"
                prefix-icon="Search"
                clearable
                size="small"
                style="width: 200px"
            />
            <el-button size="small" @click="syncAllAssets">Sync All Assets</el-button>
            <el-button size="small" @click="showAssetList = false">Close</el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredAssets" stripe size="small" v-loading="assetsLoading">
        <el-table-column prop="guid" label="GUID" width="200" show-overflow-tooltip />
        <el-table-column prop="name" label="Asset Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="140" />
        <el-table-column prop="category" label="Category" width="120" />
        <el-table-column prop="location" label="Location" width="150" />
        <el-table-column prop="syncStatus" label="Sync Status" width="110">
          <template #default="{ row }">
            <el-tag :type="row.syncStatus === 'Synced' ? 'success' : 'warning'" size="small">
              {{ row.syncStatus }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="100">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewAsset(row)">View</el-button>
            <el-button link type="success" size="small" @click="syncAsset(row)">Sync</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="assetsPage"
            v-model:page-size="assetsPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredAssets.length"
            @size-change="assetsPage = 1"
        />
      </div>
    </el-card>

    <!-- Sync History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>BIM Sync History</span>
          <div class="history-controls">
            <el-date-picker
                v-model="historyDateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start Date"
                end-placeholder="End Date"
                size="small"
                style="width: 240px"
            />
            <el-button size="small" @click="filterHistory">Filter</el-button>
          </div>
        </div>
      </template>

      <el-table :data="syncHistory" stripe style="width: 100%" v-loading="historyLoading">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="modelName" label="Model Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="format" label="Format" width="80" />
        <el-table-column prop="assetsProcessed" label="Assets" width="100" align="right" />
        <el-table-column prop="duration" label="Duration" width="100" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Success' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" min-width="250" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="historyPage"
            v-model:page-size="historyPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="syncHistory.length"
            @size-change="historyPage = 1"
        />
      </div>
    </el-card>

    <!-- Import BIM Model Dialog -->
    <el-dialog v-model="importDialogVisible" title="Import BIM Model" width="600px" destroy-on-close>
      <el-form :model="importForm" :rules="importRules" ref="importFormRef" label-width="120px">
        <el-form-item label="Model Name" prop="name">
          <el-input v-model="importForm.name" placeholder="Enter model name" />
        </el-form-item>
        <el-form-item label="Project" prop="project">
          <el-input v-model="importForm.project" placeholder="Project name" />
        </el-form-item>
        <el-form-item label="File" prop="file">
          <el-upload
              ref="uploadRef"
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".ifc,.rvt,.nwd,.dwg"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                IFC, RVT, NWD, DWG files up to 500MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="IFC Version" prop="ifcVersion">
          <el-select v-model="importForm.ifcVersion" style="width: 100%">
            <el-option label="IFC 2x3" value="IFC2x3" />
            <el-option label="IFC 4" value="IFC4" />
            <el-option label="IFC 4x3" value="IFC4x3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Coordinate System" prop="coordinateSystem">
          <el-select v-model="importForm.coordinateSystem" style="width: 100%">
            <el-option label="WGS 84" value="WGS84" />
            <el-option label="UTM" value="UTM" />
            <el-option label="Local Grid" value="Local" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="importForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="uploadModel">Upload & Import</el-button>
      </template>
    </el-dialog>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="assetDetailVisible" :title="`Asset Detail - ${currentAsset?.name}`" width="600px" destroy-on-close>
      <div class="asset-detail" v-if="currentAsset">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="GUID">{{ currentAsset.guid }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ currentAsset.name }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ currentAsset.type }}</el-descriptions-item>
          <el-descriptions-item label="Family">{{ currentAsset.family }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ currentAsset.category }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ currentAsset.location }}</el-descriptions-item>
          <el-descriptions-item label="Level">{{ currentAsset.level }}</el-descriptions-item>
          <el-descriptions-item label="Elevation">{{ currentAsset.elevation }} m</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ currentAsset.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ currentAsset.modelNumber }}</el-descriptions-item>
          <el-descriptions-item label="Serial Number">{{ currentAsset.serialNumber || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Installation Date">{{ currentAsset.installationDate }}</el-descriptions-item>
          <el-descriptions-item label="Warranty Expiry">{{ currentAsset.warrantyExpiry || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Status">{{ currentAsset.status }}</el-descriptions-item>
          <el-descriptions-item label="Parameters" :span="2">
            <pre class="params-preview">{{ JSON.stringify(currentAsset.parameters, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="assetDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="syncAsset(currentAsset)">Sync to IBMS</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, Connection, Edit, DataAnalysis, Monitor, Share,
  UploadFilled, Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing BIM integration...', 'Loading models...', 'Almost ready...']

// ==================== State ====================
const modelsLoading = ref(false)
const assetsLoading = ref(false)
const historyLoading = ref(false)
const importDialogVisible = ref(false)
const assetDetailVisible = ref(false)
const showAssetList = ref(false)
const currentModel = ref<any>(null)
const currentAsset = ref<any>(null)
const selectedAsset = ref<any>(null)
const modelSearch = ref('')
const assetSearch = ref('')
const fileFormatFilter = ref('')
const modelsPage = ref(1)
const modelsPageSize = ref(10)
const assetsPage = ref(1)
const assetsPageSize = ref(10)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyDateRange = ref<[Date, Date] | null>(null)

const importFormRef = ref()
const uploadRef = ref()

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'BIM Models', value: '8', trend: 2, icon: 'Building', bgColor: '#409eff', key: 'models', subTitle: 'Active: 7' },
  { title: 'Assets Mapped', value: '2,456', trend: 15, icon: 'Grid', bgColor: '#67c23a', key: 'assets', subTitle: 'Synced: 2,234' },
  { title: 'File Size', value: '2.4 GB', trend: 8, icon: 'Document', bgColor: '#e6a23c', key: 'size', subTitle: 'Total storage' },
  { title: 'Sync Success', value: '98.2%', trend: 1.5, icon: 'Checked', bgColor: '#f56c6c', key: 'success', subTitle: 'Last 30 days' }
])

const bimSystems = ref([
  { name: 'Autodesk Revit', icon: 'DataAnalysis', color: '#409eff', status: 'Connected', version: '2024' },
  { name: 'Navisworks', icon: 'Monitor', color: '#f56c6c', status: 'Connected', version: '2024' },
  { name: 'BIM 360', icon: 'Share', color: '#67c23a', status: 'Connected', version: 'Enterprise' }
])

const bimModels = ref([
  { id: 1, name: 'Building A - Architectural Model', project: 'Main Campus', format: 'RVT', fileSize: '245 MB', assetCount: 1250, version: '2.1', lastSync: '2024-01-20 10:30:00', status: 'Active' },
  { id: 2, name: 'Building A - MEP Model', project: 'Main Campus', format: 'RVT', fileSize: '189 MB', assetCount: 890, version: '2.1', lastSync: '2024-01-20 09:00:00', status: 'Active' },
  { id: 3, name: 'IFC Coordination Model', project: 'Phase 2', format: 'IFC', fileSize: '156 MB', assetCount: 2340, version: '1.0', lastSync: '2024-01-19 15:00:00', status: 'Active' },
  { id: 4, name: 'Structural Model', project: 'Main Campus', format: 'NWD', fileSize: '98 MB', assetCount: 560, version: '1.2', lastSync: '2024-01-18 12:00:00', status: 'Inactive' }
])

const assetsList = ref([
  { guid: '3d2e1f0a-9b8c-7d6e-5f4a-3b2c1d0e9f8a', name: 'AHU-01', type: 'Air Handling Unit', category: 'HVAC', location: 'Floor 2, Room 201', level: 'Level 2', family: 'Air Terminal', manufacturer: 'Carrier', modelNumber: '39C-06', installationDate: '2022-03-15', status: 'Operational', syncStatus: 'Synced', elevation: 8.5, parameters: { airflow: '2000 CFM', power: '5.5 kW', static_pressure: '2.5 in.wg' } },
  { guid: '4e3f2a1b-0c9d-8e7f-6a5b-4c3d2e1f0a9b', name: 'Chiller-01', type: 'Chiller', category: 'HVAC', location: 'Basement Mechanical Room', level: 'B1', family: 'Centrifugal Chiller', manufacturer: 'Trane', modelNumber: 'CVHF-570', installationDate: '2021-06-10', status: 'Operational', syncStatus: 'Synced', elevation: -2.0, parameters: { capacity: '500 tons', power: '350 kW', cop: '6.2' } },
  { guid: '5a4b3c2d-1e0f-9a8b-7c6d-5e4f3a2b1c0d', name: 'VAV-101', type: 'VAV Box', category: 'HVAC', location: 'Floor 1, Zone A', level: 'Level 1', family: 'VAV Terminal', manufacturer: 'Johnson Controls', modelNumber: 'VMA1630', installationDate: '2023-01-20', status: 'Operational', syncStatus: 'Pending', elevation: 4.2, parameters: { max_flow: '1200 CFM', min_flow: '300 CFM', reheat: '2.5 kW' } }
])

const syncHistory = ref([
  { id: 1, timestamp: '2024-01-20 10:30:00', modelName: 'Building A - Architectural Model', format: 'RVT', assetsProcessed: 1250, duration: '3 min 45 sec', status: 'Success', message: 'Model synced successfully' },
  { id: 2, timestamp: '2024-01-20 09:00:00', modelName: 'Building A - MEP Model', format: 'RVT', assetsProcessed: 890, duration: '2 min 30 sec', status: 'Success', message: 'Model synced successfully' },
  { id: 3, timestamp: '2024-01-19 15:00:00', modelName: 'IFC Coordination Model', format: 'IFC', assetsProcessed: 2340, duration: '5 min 12 sec', status: 'Running', message: 'Processing IFC elements' },
  { id: 4, timestamp: '2024-01-18 12:00:00', modelName: 'Structural Model', format: 'NWD', assetsProcessed: 560, duration: '1 min 48 sec', status: 'Failed', message: 'File format not supported' }
])

// ==================== Computed ====================
const filteredModels = computed(() => {
  let filtered = [...bimModels.value]
  if (modelSearch.value) filtered = filtered.filter(m => m.name.toLowerCase().includes(modelSearch.value.toLowerCase()))
  if (fileFormatFilter.value) filtered = filtered.filter(m => m.format === fileFormatFilter.value)
  return filtered
})

const paginatedModels = computed(() => {
  const start = (modelsPage.value - 1) * modelsPageSize.value
  const end = start + modelsPageSize.value
  return filteredModels.value.slice(start, end)
})

const filteredAssets = computed(() => {
  let filtered = [...assetsList.value]
  if (assetSearch.value) filtered = filtered.filter(a => a.name.toLowerCase().includes(assetSearch.value.toLowerCase()) || a.type.toLowerCase().includes(assetSearch.value.toLowerCase()))
  return filtered
})

// ==================== Helper Methods ====================
const getFormatTag = (format: string) => {
  const map: Record<string, string> = {
    'IFC': 'primary',
    'RVT': 'success',
    'NWD': 'warning',
    'DWG': 'danger'
  }
  return map[format] || 'info'
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting BIM model data...')
}

const selectBIMSystem = (bim: any) => {
  ElMessage.info(`Selected ${bim.name} - ${bim.status}`)
}

const fetchModels = () => {
  modelsLoading.value = true
  setTimeout(() => {
    modelsLoading.value = false
    ElMessage.success('Models refreshed')
  }, 500)
}

const filterHistory = () => {
  ElMessage.success('History filtered')
}

const openAddModelDialog = () => {
  importDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  importForm.file = file.raw
}

const uploadModel = async () => {
  if (!importFormRef.value) return
  await importFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(`Model "${importForm.name}" imported successfully`)
      importDialogVisible.value = false
      importFormRef.value?.resetFields()
      uploadRef.value?.clearFiles()
    }
  })
}

const viewModel = (model: any) => {
  ElMessage.info(`Viewing model: ${model.name}`)
}

const syncModel = (model: any) => {
  ElMessage.info(`Syncing model "${model.name}"...`)
  setTimeout(() => {
    ElMessage.success(`Model "${model.name}" synced successfully`)
  }, 2000)
}

const viewAssetList = (model: any) => {
  currentModel.value = model
  showAssetList.value = true
}

const deleteModel = (model: any) => {
  ElMessageBox.confirm(`Delete model "${model.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = bimModels.value.findIndex(m => m.id === model.id)
    if (index !== -1) {
      bimModels.value.splice(index, 1)
      ElMessage.success(`Deleted: ${model.name}`)
    }
  }).catch(() => {})
}

const viewAsset = (asset: any) => {
  currentAsset.value = asset
  assetDetailVisible.value = true
}

const syncAsset = (asset: any) => {
  ElMessage.success(`Asset "${asset.name}" synchronized to IBMS`)
  asset.syncStatus = 'Synced'
}

const syncAllAssets = () => {
  ElMessage.info('Syncing all assets to IBMS...')
  setTimeout(() => {
    assetsList.value.forEach(a => a.syncStatus = 'Synced')
    ElMessage.success('All assets synced successfully')
  }, 2000)
}

const syncToIBMS = () => {
  if (selectedAsset.value) {
    ElMessage.success(`Asset "${selectedAsset.value.name}" synced to IBMS`)
    selectedAsset.value.syncStatus = 'Synced'
  }
}

// Model viewer controls
const rotateModel = () => {
  ElMessage.info('Rotate mode enabled')
}

const panModel = () => {
  ElMessage.info('Pan mode enabled')
}

const zoomModel = () => {
  ElMessage.info('Zoom mode enabled')
}

const resetView = () => {
  ElMessage.info('View reset to default')
}

// Simulate asset selection from model
const selectAssetFromModel = (asset: any) => {
  selectedAsset.value = asset
}

// ==================== Forms ====================
const importForm = reactive({
  name: '',
  project: '',
  file: null,
  ifcVersion: 'IFC4',
  coordinateSystem: 'WGS84',
  description: ''
})

const importRules = {
  name: [{ required: true, message: 'Please enter model name', trigger: 'blur' }],
  project: [{ required: true, message: 'Please enter project name', trigger: 'blur' }],
  file: [{ required: true, message: 'Please select a file', trigger: 'change' }]
}

// ==================== Mounted ====================
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
      fetchModels()
    }, 400)
  }, 2000)

  // Simulate clicking on an asset in the 3D model after load
  setTimeout(() => {
    selectAssetFromModel(assetsList.value[0])
  }, 3000)
})
</script>

<style scoped lang="scss">
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
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
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
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
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
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.bim-integration-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header .breadcrumb { margin-bottom: 8px; }
.page-header h1 { font-size: 28px; font-weight: 600; color: #303133; margin: 0 0 8px 0; }
.page-header .description { color: #909399; font-size: 14px; margin: 0; }
.page-header .header-actions { display: flex; gap: 12px; }

.stats-row { margin-bottom: 20px; }
.stat-card { cursor: pointer; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card .stat-content { display: flex; justify-content: space-between; align-items: center; }
.stat-card .stat-info { flex: 1; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.stat-card .stat-trend { font-size: 12px; display: flex; align-items: center; gap: 4px; }
.stat-card .stat-trend.up { color: #67c23a; }
.stat-card .stat-trend.down { color: #f56c6c; }
.stat-card .stat-trend .trend-label { color: #909399; margin-left: 4px; }
.stat-card .stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-card .stat-footer { margin-top: 12px; padding-top: 8px; border-top: 1px solid #ebeef5; font-size: 12px; color: #909399; }

.bim-cards-row { margin-bottom: 20px; }
.bim-card { cursor: pointer; transition: all 0.3s; }
.bim-card:hover { transform: translateY(-4px); }
.bim-card .bim-card-content { display: flex; gap: 16px; align-items: center; }
.bim-card .bim-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.bim-card .bim-info { flex: 1; }
.bim-card .bim-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.bim-card .bim-version { font-size: 12px; color: #909399; margin-top: 4px; }

.model-row { margin-bottom: 20px; }
.model-viewer-card .card-header, .asset-info-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.model-viewer-container { height: 400px; background: #1a1a2e; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.model-placeholder { text-align: center; color: #666; }
.model-placeholder .el-icon { color: #409eff; margin-bottom: 16px; }
.model-placeholder p { margin: 8px 0; color: #909399; }
.model-placeholder .model-hint { font-size: 12px; color: #666; }

.asset-details { max-height: 500px; overflow-y: auto; }
.empty-asset { padding: 40px; text-align: center; }

.models-card, .assets-card, .history-card { margin-bottom: 20px; }
.models-card .card-header, .assets-card .card-header, .history-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.models-card .models-actions, .assets-card .assets-actions, .history-card .history-controls { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.params-preview { background: #f5f7fa; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; margin: 0; overflow-x: auto; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>