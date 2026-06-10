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
        <div class="loading-tip">GIS Integration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="gis-integration-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Third-Party Systems</el-breadcrumb-item>
            <el-breadcrumb-item>GIS</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>GIS Integration</h1>
        <p class="description">Integrate with ArcGIS, QGIS, Google Maps, and other geospatial platforms for location-based services</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Map Data
        </el-button>
        <el-button type="primary" @click="openAddLayerDialog">
          <el-icon><Plus /></el-icon>
          Add Map Layer
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

    <!-- GIS Platform Cards -->
    <el-row :gutter="20" class="gis-cards-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="gis in gisPlatforms" :key="gis.name">
        <el-card class="gis-card" shadow="hover" @click="selectGISPlatform(gis)">
          <div class="gis-card-content">
            <div class="gis-icon" :style="{ background: gis.color }">
              <el-icon :size="32"><component :is="gis.icon" /></el-icon>
            </div>
            <div class="gis-info">
              <div class="gis-name">{{ gis.name }}</div>
              <div class="gis-status">
                <el-tag :type="gis.status === 'Connected' ? 'success' : 'danger'" size="small">
                  {{ gis.status }}
                </el-tag>
              </div>
              <div class="gis-version">{{ gis.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Interactive Map -->
    <el-card class="map-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Interactive Map</span>
          <div class="map-controls">
            <el-button-group size="small">
              <el-button @click="zoomIn">+</el-button>
              <el-button @click="zoomOut">-</el-button>
              <el-button @click="resetMap">Reset</el-button>
            </el-button-group>
            <el-select v-model="baseMap" size="small" style="width: 120px; margin-left: 8px">
              <el-option label="Street Map" value="street" />
              <el-option label="Satellite" value="satellite" />
              <el-option label="Terrain" value="terrain" />
            </el-select>
          </div>
        </div>
      </template>
      <div ref="mapContainer" class="map-container"></div>
      <div class="map-legend">
        <div class="legend-item">
          <span class="legend-color" style="background: #409eff;"></span>
          <span>Buildings</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #67c23a;"></span>
          <span>Green Spaces</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #f56c6c;"></span>
          <span>Critical Assets</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #e6a23c;"></span>
          <span>Utility Lines</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #f39c12;"></span>
          <span>Alert Zone</span>
        </div>
      </div>
    </el-card>

    <!-- GIS Layers Table -->
    <el-card class="layers-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>GIS Layers</span>
          <div class="layers-actions">
            <el-input
                v-model="layerSearch"
                placeholder="Search layers"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="layerTypeFilter" placeholder="Type" clearable style="width: 120px">
              <el-option label="Base Map" value="Base Map" />
              <el-option label="Feature Layer" value="Feature Layer" />
              <el-option label="WMS" value="WMS" />
              <el-option label="Tile Layer" value="Tile Layer" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchLayers" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedLayers" stripe style="width: 100%" v-loading="layersLoading">
        <el-table-column prop="name" label="Layer Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getLayerTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="200" show-overflow-tooltip />
        <el-table-column prop="featureCount" label="Features" width="100" align="center" />
        <el-table-column prop="lastUpdated" label="Last Updated" width="150" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewLayer(row)">View</el-button>
            <el-button link type="success" size="small" @click="syncLayer(row)">Sync</el-button>
            <el-button link type="danger" size="small" @click="deleteLayer(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="layersPage"
            v-model:page-size="layersPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredLayers.length"
            @size-change="layersPage = 1"
        />
      </div>
    </el-card>

    <!-- Spatial Data Table -->
    <el-card class="spatial-data-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Spatial Data</span>
          <div class="spatial-actions">
            <el-input
                v-model="spatialSearch"
                placeholder="Search by name"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="spatialTypeFilter" placeholder="Geometry Type" clearable style="width: 140px">
              <el-option label="Point" value="Point" />
              <el-option label="LineString" value="LineString" />
              <el-option label="Polygon" value="Polygon" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchSpatialData" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedSpatialData" stripe style="width: 100%" v-loading="spatialLoading">
        <el-table-column prop="name" label="Feature Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="geometryType" label="Geometry Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getGeometryTag(row.geometryType)" size="small">{{ row.geometryType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="coordinates" label="Coordinates" min-width="200" show-overflow-tooltip />
        <el-table-column prop="area" label="Area (m²)" width="110" align="right" />
        <el-table-column prop="assetId" label="Asset ID" width="120" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewFeature(row)">View</el-button>
            <el-button link type="success" size="small" @click="locateFeature(row)">Locate</el-button>
            <el-button link type="info" size="small" @click="editFeature(row)">Edit</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="spatialPage"
            v-model:page-size="spatialPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredSpatialData.length"
            @size-change="spatialPage = 1"
        />
      </div>
    </el-card>

    <!-- Sync History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>GIS Sync History</span>
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
        <el-table-column prop="layerName" label="Layer Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="featuresProcessed" label="Features" width="100" align="right" />
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

    <!-- Add GIS Layer Dialog -->
    <el-dialog v-model="layerDialogVisible" title="Add GIS Layer" width="600px" destroy-on-close>
      <el-form :model="layerForm" :rules="layerRules" ref="layerFormRef" label-width="130px">
        <el-form-item label="Layer Name" prop="name">
          <el-input v-model="layerForm.name" placeholder="Enter layer name" />
        </el-form-item>
        <el-form-item label="Layer Type" prop="type">
          <el-select v-model="layerForm.type" style="width: 100%">
            <el-option label="Base Map" value="Base Map" />
            <el-option label="Feature Layer" value="Feature Layer" />
            <el-option label="WMS" value="WMS" />
            <el-option label="Tile Layer" value="Tile Layer" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Source" prop="source">
          <el-input v-model="layerForm.source" placeholder="URL or file path" />
        </el-form-item>
        <el-form-item label="CRS" prop="crs">
          <el-select v-model="layerForm.crs" style="width: 100%">
            <el-option label="EPSG:4326 - WGS 84" value="EPSG:4326" />
            <el-option label="EPSG:3857 - Web Mercator" value="EPSG:3857" />
            <el-option label="EPSG:27700 - British National Grid" value="EPSG:27700" />
          </el-select>
        </el-form-item>
        <el-form-item label="Style" prop="style">
          <el-select v-model="layerForm.style" style="width: 100%">
            <el-option label="Default" value="default" />
            <el-option label="Satellite" value="satellite" />
            <el-option label="Terrain" value="terrain" />
            <el-option label="Dark" value="dark" />
          </el-select>
        </el-form-item>
        <el-form-item label="Opacity" prop="opacity">
          <el-slider v-model="layerForm.opacity" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="layerForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="layerDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testLayer">Test Connection</el-button>
        <el-button type="success" @click="saveLayer">Add Layer</el-button>
      </template>
    </el-dialog>

    <!-- Feature Detail Dialog -->
    <el-dialog v-model="featureDetailVisible" :title="`Feature Detail - ${currentFeature?.name}`" width="600px" destroy-on-close>
      <div class="feature-detail" v-if="currentFeature">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Feature ID">{{ currentFeature.id }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ currentFeature.name }}</el-descriptions-item>
          <el-descriptions-item label="Geometry Type">
            <el-tag :type="getGeometryTag(currentFeature.geometryType)" size="small">{{ currentFeature.geometryType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Coordinates" :span="2">
            <code class="coordinates-code">{{ currentFeature.coordinates }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="Area">{{ currentFeature.area }} m²</el-descriptions-item>
          <el-descriptions-item label="Perimeter">{{ currentFeature.perimeter }} m</el-descriptions-item>
          <el-descriptions-item label="Asset ID">{{ currentFeature.assetId || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Asset Name">{{ currentFeature.assetName || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Created At">{{ currentFeature.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="Updated At">{{ currentFeature.updatedAt }}</el-descriptions-item>
          <el-descriptions-item label="Properties" :span="2">
            <pre class="props-preview">{{ JSON.stringify(currentFeature.properties, null, 2) }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="featureDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="locateFeature(currentFeature)">Locate on Map</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Server:</strong> {{ testResult.details.server }}</p>
          <p><strong>Version:</strong> {{ testResult.details.version }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
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
  Location, Grid
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing GIS integration...', 'Loading map layers...', 'Almost ready...']

// ==================== Map References ====================
const mapContainer = ref<HTMLElement>()

// ==================== State ====================
const layersLoading = ref(false)
const spatialLoading = ref(false)
const historyLoading = ref(false)
const layerDialogVisible = ref(false)
const featureDetailVisible = ref(false)
const testDialogVisible = ref(false)
const currentFeature = ref<any>(null)
const layerSearch = ref('')
const spatialSearch = ref('')
const layerTypeFilter = ref('')
const spatialTypeFilter = ref('')
const baseMap = ref('street')
const layersPage = ref(1)
const layersPageSize = ref(10)
const spatialPage = ref(1)
const spatialPageSize = ref(10)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyDateRange = ref<[Date, Date] | null>(null)

const layerFormRef = ref()
const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'GIS Layers', value: '12', trend: 3, icon: 'Grid', bgColor: '#409eff', key: 'layers', subTitle: 'Active: 10' },
  { title: 'Spatial Features', value: '2,456', trend: 15, icon: 'Location', bgColor: '#67c23a', key: 'features', subTitle: 'Points: 1,234' },
  { title: 'Map Tiles', value: '45.2K', trend: 8, icon: 'Document', bgColor: '#e6a23c', key: 'tiles', subTitle: 'Cached' },
  { title: 'Geocoding', value: '98.5%', trend: 1.2, icon: 'Checked', bgColor: '#f56c6c', key: 'success', subTitle: 'Success rate' }
])

const gisPlatforms = ref([
  { name: 'ArcGIS', icon: 'DataAnalysis', color: '#409eff', status: 'Connected', version: '10.8.1' },
  { name: 'QGIS', icon: 'Monitor', color: '#67c23a', status: 'Connected', version: '3.28' },
  { name: 'Google Maps', icon: 'Location', color: '#f56c6c', status: 'Connected', version: 'API v3' }
])

const gisLayers = ref([
  { id: 1, name: 'Building Footprints', type: 'Feature Layer', source: 'ArcGIS REST Service', featureCount: 1250, lastUpdated: '2024-01-20 10:30:00', status: 'Active' },
  { id: 2, name: 'Road Network', type: 'Feature Layer', source: 'OpenStreetMap', featureCount: 890, lastUpdated: '2024-01-20 09:00:00', status: 'Active' },
  { id: 3, name: 'Satellite Base Map', type: 'Base Map', source: 'Google Maps', featureCount: 0, lastUpdated: '2024-01-19 15:00:00', status: 'Active' },
  { id: 4, name: 'Utility Lines', type: 'WMS', source: 'City GIS Server', featureCount: 2340, lastUpdated: '2024-01-18 12:00:00', status: 'Active' }
])

const spatialData = ref([
  { id: 1, name: 'Main Building', geometryType: 'Polygon', coordinates: 'POLYGON((120.1 30.2, 120.2 30.2, 120.2 30.3, 120.1 30.3, 120.1 30.2))', area: 12500, perimeter: 450, assetId: 'BLD-001', properties: { floors: 5, built_year: 2010 }, createdAt: '2023-01-01', updatedAt: '2024-01-20' },
  { id: 2, name: 'Chiller Plant', geometryType: 'Point', coordinates: 'POINT(120.15 30.25)', area: 0, perimeter: 0, assetId: 'AST-001', properties: { type: 'HVAC', capacity: '500 tons' }, createdAt: '2023-06-01', updatedAt: '2024-01-19' },
  { id: 3, name: 'Power Line Route', geometryType: 'LineString', coordinates: 'LINESTRING(120.1 30.2, 120.15 30.25, 120.2 30.3)', area: 0, perimeter: 0, assetId: 'UTL-001', properties: { voltage: '11kV', length: '2.5km' }, createdAt: '2023-03-01', updatedAt: '2024-01-18' }
])

const syncHistory = ref([
  { id: 1, timestamp: '2024-01-20 10:30:00', layerName: 'Building Footprints', featuresProcessed: 1250, duration: '2 min 34 sec', status: 'Success', message: 'Layer synced successfully' },
  { id: 2, timestamp: '2024-01-20 09:00:00', layerName: 'Road Network', featuresProcessed: 890, duration: '1 min 45 sec', status: 'Success', message: 'Layer synced successfully' },
  { id: 3, timestamp: '2024-01-19 15:00:00', layerName: 'Utility Lines', featuresProcessed: 2340, duration: '3 min 22 sec', status: 'Running', message: 'Processing features' }
])

// ==================== Computed ====================
const filteredLayers = computed(() => {
  let filtered = [...gisLayers.value]
  if (layerSearch.value) filtered = filtered.filter(l => l.name.toLowerCase().includes(layerSearch.value.toLowerCase()))
  if (layerTypeFilter.value) filtered = filtered.filter(l => l.type === layerTypeFilter.value)
  return filtered
})

const paginatedLayers = computed(() => {
  const start = (layersPage.value - 1) * layersPageSize.value
  const end = start + layersPageSize.value
  return filteredLayers.value.slice(start, end)
})

const filteredSpatialData = computed(() => {
  let filtered = [...spatialData.value]
  if (spatialSearch.value) filtered = filtered.filter(f => f.name.toLowerCase().includes(spatialSearch.value.toLowerCase()))
  if (spatialTypeFilter.value) filtered = filtered.filter(f => f.geometryType === spatialTypeFilter.value)
  return filtered
})

const paginatedSpatialData = computed(() => {
  const start = (spatialPage.value - 1) * spatialPageSize.value
  const end = start + spatialPageSize.value
  return filteredSpatialData.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getLayerTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Base Map': 'success',
    'Feature Layer': 'primary',
    'WMS': 'warning',
    'Tile Layer': 'info'
  }
  return map[type] || 'info'
}

const getGeometryTag = (type: string) => {
  const map: Record<string, string> = {
    'Point': 'success',
    'LineString': 'warning',
    'Polygon': 'primary'
  }
  return map[type] || 'info'
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting GIS map data...')
}

const selectGISPlatform = (gis: any) => {
  ElMessage.info(`Selected ${gis.name} - ${gis.status}`)
}

const fetchLayers = () => {
  layersLoading.value = true
  setTimeout(() => {
    layersLoading.value = false
    ElMessage.success('Layers refreshed')
  }, 500)
}

const fetchSpatialData = () => {
  spatialLoading.value = true
  setTimeout(() => {
    spatialLoading.value = false
    ElMessage.success('Spatial data refreshed')
  }, 500)
}

const filterHistory = () => {
  ElMessage.success('History filtered')
}

const openAddLayerDialog = () => {
  layerDialogVisible.value = true
}

const testLayer = () => {
  ElMessage.info('Testing layer connection...')
  setTimeout(() => {
    testResult.success = true
    testResult.message = 'Successfully connected to GIS server'
    testResult.details = {
      server: layerForm.source,
      version: '2.0',
      responseTime: 234
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveLayer = async () => {
  if (!layerFormRef.value) return
  await layerFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(`Layer "${layerForm.name}" added successfully`)
      layerDialogVisible.value = false
      layerFormRef.value?.resetFields()
    }
  })
}

const viewLayer = (layer: any) => {
  ElMessage.info(`Viewing layer: ${layer.name}`)
}

const syncLayer = (layer: any) => {
  ElMessage.info(`Syncing layer "${layer.name}"...`)
  setTimeout(() => {
    ElMessage.success(`Layer "${layer.name}" synced successfully`)
  }, 2000)
}

const deleteLayer = (layer: any) => {
  ElMessageBox.confirm(`Delete layer "${layer.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = gisLayers.value.findIndex(l => l.id === layer.id)
    if (index !== -1) {
      gisLayers.value.splice(index, 1)
      ElMessage.success(`Deleted: ${layer.name}`)
    }
  }).catch(() => {})
}

const viewFeature = (feature: any) => {
  currentFeature.value = feature
  featureDetailVisible.value = true
}

const locateFeature = (feature: any) => {
  ElMessage.info(`Locating ${feature.name} on map...`)
}

const editFeature = (feature: any) => {
  ElMessage.info(`Editing feature: ${feature.name}`)
}

// Map controls
const zoomIn = () => {
  ElMessage.info('Zooming in')
}

const zoomOut = () => {
  ElMessage.info('Zooming out')
}

const resetMap = () => {
  ElMessage.info('Map view reset')
}

// ==================== Forms ====================
const layerForm = reactive({
  name: '',
  type: '',
  source: '',
  crs: 'EPSG:4326',
  style: 'default',
  opacity: 70,
  description: ''
})

const layerRules = {
  name: [{ required: true, message: 'Please enter layer name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select layer type', trigger: 'change' }],
  source: [{ required: true, message: 'Please enter data source', trigger: 'blur' }]
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
      fetchLayers()
      fetchSpatialData()
    }, 400)
  }, 2000)
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

.gis-integration-page {
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

.gis-cards-row { margin-bottom: 20px; }
.gis-card { cursor: pointer; transition: all 0.3s; }
.gis-card:hover { transform: translateY(-4px); }
.gis-card .gis-card-content { display: flex; gap: 16px; align-items: center; }
.gis-card .gis-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.gis-card .gis-info { flex: 1; }
.gis-card .gis-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.gis-card .gis-version { font-size: 12px; color: #909399; margin-top: 4px; }

.map-card { margin-bottom: 20px; }
.map-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.map-container { height: 450px; background: #e8eef3; border-radius: 8px; display: flex; align-items: center; justify-content: center; background-image: radial-gradient(circle, #c0c4cc 1px, transparent 1px); background-size: 20px 20px; position: relative; }
.map-legend { display: flex; gap: 20px; margin-top: 12px; padding: 8px 16px; background: #f5f7fa; border-radius: 8px; justify-content: center; }
.map-legend .legend-item { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.map-legend .legend-color { width: 16px; height: 16px; border-radius: 4px; }

.layers-card, .spatial-data-card, .history-card { margin-bottom: 20px; }
.layers-card .card-header, .spatial-data-card .card-header, .history-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.layers-card .layers-actions, .spatial-data-card .spatial-actions, .history-card .history-controls { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.coordinates-code, .props-preview { background: #f5f7fa; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; margin: 0; overflow-x: auto; }

.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>