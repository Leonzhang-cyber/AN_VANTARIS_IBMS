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
        <div class="loading-tip">Site Boundary Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="site-boundary">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Site Boundary</h2>
        <p class="subtitle">Define property boundaries, zoning areas, and site perimeters</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="editMode = !editMode">
          <el-icon><Edit /></el-icon> {{ editMode ? 'Cancel Edit' : 'Edit Boundary' }}
        </el-button>
        <el-button v-if="editMode" type="success" @click="saveChanges">
          <el-icon><Check /></el-icon> Save Changes
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Boundary Overview Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">📐</div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(siteBoundary.totalArea) }}</div>
          <div class="stat-label">Total Area (sqm)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📏</div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(siteBoundary.perimeter) }}</div>
          <div class="stat-label">Perimeter (m)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏗️</div>
        <div class="stat-info">
          <div class="stat-value">{{ siteBoundary.buildableArea }}%</div>
          <div class="stat-label">Buildable Area</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🌳</div>
        <div class="stat-info">
          <div class="stat-value">{{ siteBoundary.greenSpace }}%</div>
          <div class="stat-label">Green Space</div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Property Details -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><OfficeBuilding /></el-icon> Property Details</span>
            </div>
          </template>
          <div class="info-content">
            <div class="info-row">
              <span class="info-label">Property ID</span>
              <span class="info-value">{{ siteBoundary.propertyId }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Title Deed</span>
              <span v-if="!editMode" class="info-value">{{ siteBoundary.titleDeed }}</span>
              <el-input v-else v-model="editData.titleDeed" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Land Use</span>
              <span v-if="!editMode" class="info-value">{{ siteBoundary.landUse }}</span>
              <el-select v-else v-model="editData.landUse" class="info-input">
                <el-option label="Commercial" value="Commercial" />
                <el-option label="Industrial" value="Industrial" />
                <el-option label="Mixed Use" value="Mixed Use" />
                <el-option label="Residential" value="Residential" />
              </el-select>
            </div>
            <div class="info-row">
              <span class="info-label">Zoning Category</span>
              <span v-if="!editMode" class="info-value">{{ siteBoundary.zoning }}</span>
              <el-select v-else v-model="editData.zoning" class="info-input">
                <el-option label="Business District" value="Business District" />
                <el-option label="Light Industrial" value="Light Industrial" />
                <el-option label="Heavy Industrial" value="Heavy Industrial" />
                <el-option label="Special Use" value="Special Use" />
              </el-select>
            </div>
            <div class="info-row">
              <span class="info-label">Region/District</span>
              <span v-if="!editMode" class="info-value">{{ siteBoundary.district }}</span>
              <el-input v-else v-model="editData.district" class="info-input" />
            </div>
          </div>
        </el-card>

        <!-- Area Breakdown -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> Area Distribution</span>
            </div>
          </template>
          <div class="breakdown-chart">
            <div class="breakdown-legend">
              <div class="legend-item">
                <span class="legend-color building"></span>
                <span>Building Footprint: {{ siteBoundary.buildingFootprint }}%</span>
              </div>
              <div class="legend-item">
                <span class="legend-color green"></span>
                <span>Green Space: {{ siteBoundary.greenSpace }}%</span>
              </div>
              <div class="legend-item">
                <span class="legend-color parking"></span>
                <span>Parking Area: {{ siteBoundary.parkingArea }}%</span>
              </div>
              <div class="legend-item">
                <span class="legend-color roads"></span>
                <span>Roads & Pathways: {{ siteBoundary.roads }}%</span>
              </div>
            </div>
            <div class="breakdown-bars">
              <div class="bar building" :style="{ width: siteBoundary.buildingFootprint + '%' }"></div>
              <div class="bar green" :style="{ width: siteBoundary.greenSpace + '%' }"></div>
              <div class="bar parking" :style="{ width: siteBoundary.parkingArea + '%' }"></div>
              <div class="bar roads" :style="{ width: siteBoundary.roads + '%' }"></div>
            </div>
            <div class="breakdown-numbers">
              <div class="number-item">
                <span class="number-label">Building:</span>
                <span class="number-value">{{ (siteBoundary.totalArea * siteBoundary.buildingFootprint / 100).toLocaleString() }} sqm</span>
              </div>
              <div class="number-item">
                <span class="number-label">Green Space:</span>
                <span class="number-value">{{ (siteBoundary.totalArea * siteBoundary.greenSpace / 100).toLocaleString() }} sqm</span>
              </div>
              <div class="number-item">
                <span class="number-label">Parking:</span>
                <span class="number-value">{{ (siteBoundary.totalArea * siteBoundary.parkingArea / 100).toLocaleString() }} sqm</span>
              </div>
              <div class="number-item">
                <span class="number-label">Roads:</span>
                <span class="number-value">{{ (siteBoundary.totalArea * siteBoundary.roads / 100).toLocaleString() }} sqm</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Boundary Points Summary -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Location /></el-icon> Boundary Points</span>
              <el-tag type="info" size="small">{{ siteBoundary.boundaryPoints.length }} Points</el-tag>
            </div>
          </template>
          <div class="boundary-points-table">
            <el-table :data="siteBoundary.boundaryPoints" size="small" stripe>
              <el-table-column type="index" label="#"  />
              <el-table-column prop="name" label="Point"  />
              <el-table-column prop="lat" label="Latitude" />
              <el-table-column prop="lng" label="Longitude" />
              <el-table-column v-if="editMode" label="Actions" >
                <template #default="{ $index }">
                  <el-button type="danger" link size="small" @click="removeBoundaryPoint($index)">Remove</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div v-if="editMode" class="add-point-section">
            <el-button type="primary" size="small" @click="showAddPointDialog = true">
              <el-icon><Plus /></el-icon> Add Boundary Point
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Adjacent Properties -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Share /></el-icon> Adjacent Properties</span>
            </div>
          </template>
          <div class="adjacent-list">
            <div v-for="prop in siteBoundary.adjacentProperties" :key="prop.id" class="adjacent-item">
              <div class="adjacent-info">
                <div class="adjacent-name">{{ prop.name }}</div>
                <div class="adjacent-type">{{ prop.type }}</div>
              </div>
              <div class="adjacent-boundary">{{ prop.boundarySide }}</div>
            </div>
          </div>
        </el-card>

        <!-- Utility Easements -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Connection /></el-icon> Utility Easements</span>
            </div>
          </template>
          <div class="easements-list">
            <div v-for="easement in siteBoundary.easements" :key="easement.id" class="easement-item">
              <div class="easement-type">{{ easement.type }}</div>
              <div class="easement-details">
                <span>{{ easement.width }}m width</span>
                <span>{{ easement.length }}m length</span>
              </div>
              <div class="easement-location">{{ easement.location }}</div>
            </div>
          </div>
        </el-card>

        <!-- Setback Requirements -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Setting /></el-icon> Setback Requirements</span>
            </div>
          </template>
          <div class="setbacks-grid">
            <div class="setback-item">
              <span class="setback-side">Front</span>
              <span class="setback-value">{{ siteBoundary.setbacks.front }} m</span>
            </div>
            <div class="setback-item">
              <span class="setback-side">Rear</span>
              <span class="setback-value">{{ siteBoundary.setbacks.rear }} m</span>
            </div>
            <div class="setback-item">
              <span class="setback-side">Left Side</span>
              <span class="setback-value">{{ siteBoundary.setbacks.left }} m</span>
            </div>
            <div class="setback-item">
              <span class="setback-side">Right Side</span>
              <span class="setback-value">{{ siteBoundary.setbacks.right }} m</span>
            </div>
          </div>
        </el-card>

        <!-- Regulatory Information -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Document /></el-icon> Regulatory Information</span>
            </div>
          </template>
          <div class="info-content">
            <div class="info-row">
              <span class="info-label">Max Building Height</span>
              <span class="info-value">{{ siteBoundary.maxBuildingHeight }} m</span>
            </div>
            <div class="info-row">
              <span class="info-label">Floor Area Ratio</span>
              <span class="info-value">{{ siteBoundary.far }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Plot Ratio</span>
              <span class="info-value">{{ siteBoundary.plotRatio }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Heritage Status</span>
              <span class="info-value">{{ siteBoundary.heritageStatus }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">Flood Zone</span>
              <span class="info-value">{{ siteBoundary.floodZone }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Add Boundary Point Dialog -->
    <el-dialog v-model="showAddPointDialog" title="Add Boundary Point" width="450px">
      <el-form :model="newPoint" label-width="100px">
        <el-form-item label="Point Name">
          <el-input v-model="newPoint.name" placeholder="e.g., NW Corner" />
        </el-form-item>
        <el-form-item label="Latitude" required>
          <el-input-number v-model="newPoint.lat" :step="0.0001" :precision="6" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Longitude" required>
          <el-input-number v-model="newPoint.lng" :step="0.0001" :precision="6" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPointDialog = false">Cancel</el-button>
        <el-button type="primary" @click="addBoundaryPoint">Add Point</el-button>
      </template>
    </el-dialog>

    <!-- Edit Mode Notice -->
    <div v-if="editMode" class="edit-notice">
      <el-alert
          title="Edit Mode Active"
          description="You are currently editing site boundary. Add, remove, or modify boundary points and property details. Click 'Save Changes' to apply updates."
          type="info"
          show-icon
          :closable="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Edit, Check, RefreshRight, Location, OfficeBuilding, DataAnalysis, Share, Connection, Setting, Document, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading site boundary data...',
  'Fetching property details...',
  'Loading regulatory information...',
  'Almost ready...'
]

// Site boundary data
const siteBoundary = reactive({
  propertyId: 'PROP-SGP-001',
  titleDeed: 'LOT-2345-6789-ABCD',
  landUse: 'Commercial',
  zoning: 'Business District',
  district: 'Marina Bay',
  totalArea: 45280,
  perimeter: 865,
  buildableArea: 65,
  greenSpace: 20,
  buildingFootprint: 45,
  parkingArea: 25,
  roads: 10,
  maxBuildingHeight: 45,
  far: 3.5,
  plotRatio: 4.2,
  heritageStatus: 'None',
  floodZone: 'Zone B (Low Risk)',
  setbacks: {
    front: 8,
    rear: 6,
    left: 4,
    right: 4
  },
  boundaryPoints: [
    { name: 'NW Corner', lat: 1.2852, lng: 103.8585 },
    { name: 'NE Corner', lat: 1.2852, lng: 103.8615 },
    { name: 'SE Corner', lat: 1.2826, lng: 103.8615 },
    { name: 'SW Corner', lat: 1.2826, lng: 103.8585 },
    { name: 'Gate Entrance', lat: 1.2840, lng: 103.8595 }
  ],
  adjacentProperties: [
    { id: 1, name: 'Marina Square Mall', type: 'Commercial', boundarySide: 'East' },
    { id: 2, name: 'Central Boulevard', type: 'Public Road', boundarySide: 'North' },
    { id: 3, name: 'Sheares Avenue', type: 'Public Road', boundarySide: 'South' },
    { id: 4, name: 'Bayfront Park', type: 'Public Park', boundarySide: 'West' }
  ],
  easements: [
    { id: 1, type: 'Power Cable', width: 3, length: 280, location: 'Eastern boundary' },
    { id: 2, type: 'Water Main', width: 2, length: 320, location: 'Northern boundary' },
    { id: 3, type: 'Telecom Fiber', width: 1.5, length: 200, location: 'Western boundary' }
  ]
})

// Edit data copy
const editData = reactive({ ...siteBoundary })
const editMode = ref(false)
const showAddPointDialog = ref(false)
const newPoint = ref({ name: '', lat: 0, lng: 0 })

// Helper functions
const formatNumber = (num: number) => {
  return num.toLocaleString()
}

// Boundary point management
const addBoundaryPoint = () => {
  if (!newPoint.value.lat || !newPoint.value.lng) {
    ElMessage.warning('Please enter both latitude and longitude')
    return
  }
  const pointName = newPoint.value.name || `Point ${editData.boundaryPoints.length + 1}`
  editData.boundaryPoints.push({
    name: pointName,
    lat: newPoint.value.lat,
    lng: newPoint.value.lng
  })
  showAddPointDialog.value = false
  newPoint.value = { name: '', lat: 0, lng: 0 }
  ElMessage.success('Boundary point added')
}

const removeBoundaryPoint = (index: number) => {
  editData.boundaryPoints.splice(index, 1)
  ElMessage.success('Boundary point removed')
}

// Save changes
const saveChanges = () => {
  ElMessageBox.confirm(
      'Save all changes to site boundary?',
      'Confirm Changes',
      {
        confirmButtonText: 'Save',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    Object.assign(siteBoundary, editData)
    editMode.value = false
    ElMessage.success('Site boundary updated successfully')
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

// Loading animation
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

.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

.loading-tip { font-size: 13px; color: #94a3b8; letter-spacing: 1px; margin-bottom: 8px; font-weight: 500; }
.loading-subtip { font-size: 11px; color: #64748b; letter-spacing: 0.5px; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* Main Content */
.site-boundary {
  padding: 24px;
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h2 {
  margin: 0 0 4px 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1565c0, #1976d2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #1565c0;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  font-size: 36px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Info Cards */
.info-card {
  border-radius: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: #909399;
  min-width: 140px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  text-align: right;
  flex: 1;
}

.info-input {
  width: 200px;
}

/* Breakdown Chart */
.breakdown-chart {
  padding: 8px 0;
}

.breakdown-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.building { background: #409eff; }
.legend-color.green { background: #67c23a; }
.legend-color.parking { background: #e6a23c; }
.legend-color.roads { background: #909399; }

.breakdown-bars {
  display: flex;
  height: 24px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.bar {
  height: 100%;
}

.bar.building { background: #409eff; }
.bar.green { background: #67c23a; }
.bar.parking { background: #e6a23c; }
.bar.roads { background: #909399; }

.breakdown-numbers {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.number-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.number-label {
  color: #909399;
}

.number-value {
  font-weight: 500;
  color: #303133;
}

/* Boundary Points Table */
.boundary-points-table {
  max-height: 250px;
  overflow-y: auto;
}

.add-point-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  text-align: right;
}

/* Adjacent Properties */
.adjacent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.adjacent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
}

.adjacent-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.adjacent-type {
  font-size: 11px;
  color: #909399;
}

.adjacent-boundary {
  font-size: 12px;
  color: #409eff;
  font-weight: 500;
}

/* Easements List */
.easements-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.easement-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
}

.easement-type {
  font-weight: 600;
  margin-bottom: 8px;
  color: #e6a23c;
}

.easement-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.easement-location {
  font-size: 11px;
  color: #909399;
}

/* Setbacks Grid */
.setbacks-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.setback-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.setback-side {
  font-size: 13px;
  color: #606266;
}

.setback-value {
  font-weight: 600;
  color: #303133;
}

/* Edit Notice */
.edit-notice {
  margin-top: 24px;
}

/* Responsive */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .site-boundary { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .info-row { flex-direction: column; align-items: flex-start; }
  .info-value { text-align: left; }
  .info-input { width: 100%; }
  .breakdown-numbers { grid-template-columns: 1fr; }
  .adjacent-item { flex-direction: column; text-align: center; gap: 8px; }
  .setbacks-grid { grid-template-columns: 1fr; }
}
</style>