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
        <div class="loading-tip">Site Profile Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="site-profile">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Site Profile</h2>
        <p class="subtitle">View and manage site information, location details, and operational settings</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="editMode = !editMode">
          <el-icon><Edit /></el-icon> {{ editMode ? 'Cancel Edit' : 'Edit Profile' }}
        </el-button>
        <el-button v-if="editMode" type="success" @click="saveChanges">
          <el-icon><Check /></el-icon> Save Changes
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Site Overview Card -->
    <div class="overview-card">
      <div class="overview-header">
        <div class="site-avatar">
          <span class="avatar-icon">🏢</span>
        </div>
        <div class="site-info">
          <h1 class="site-name">{{ siteData.name }}</h1>
          <p class="site-code">Site Code: {{ siteData.code }}</p>
          <div class="site-status">
            <span class="status-badge" :class="siteData.status">● {{ siteData.status === 'active' ? 'Active' : 'Inactive' }}</span>
            <span class="since-date">Since {{ siteData.established }}</span>
          </div>
        </div>
        <div class="site-stats">
          <div class="stat-item">
            <div class="stat-value">{{ siteData.totalBuildings }}</div>
            <div class="stat-label">Buildings</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ siteData.totalArea }}k</div>
            <div class="stat-label">sqm Area</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ siteData.departments }}</div>
            <div class="stat-label">Departments</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ siteData.employees }}</div>
            <div class="stat-label">Employees</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Left Column -->
      <div class="left-column">
        <!-- Location Information -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Location /></el-icon> Location Information</span>
            </div>
          </template>
          <div class="info-content">
            <div class="info-row">
              <span class="info-label">Address</span>
              <span v-if="!editMode" class="info-value">{{ siteData.address }}</span>
              <el-input v-else v-model="editData.address" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">City</span>
              <span v-if="!editMode" class="info-value">{{ siteData.city }}</span>
              <el-input v-else v-model="editData.city" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">State/Province</span>
              <span v-if="!editMode" class="info-value">{{ siteData.state }}</span>
              <el-input v-else v-model="editData.state" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Country</span>
              <span v-if="!editMode" class="info-value">{{ siteData.country }}</span>
              <el-input v-else v-model="editData.country" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Postal Code</span>
              <span v-if="!editMode" class="info-value">{{ siteData.postalCode }}</span>
              <el-input v-else v-model="editData.postalCode" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Time Zone</span>
              <span v-if="!editMode" class="info-value">{{ siteData.timezone }}</span>
              <el-select v-else v-model="editData.timezone" class="info-input">
                <el-option label="UTC-8 (Pacific Time)" value="UTC-8" />
                <el-option label="UTC-7 (Mountain Time)" value="UTC-7" />
                <el-option label="UTC-6 (Central Time)" value="UTC-6" />
                <el-option label="UTC-5 (Eastern Time)" value="UTC-5" />
                <el-option label="UTC+0 (GMT)" value="UTC+0" />
                <el-option label="UTC+8 (Singapore/Beijing)" value="UTC+8" />
              </el-select>
            </div>
            <div class="info-row">
              <span class="info-label">Coordinates</span>
              <span class="info-value">{{ siteData.latitude }}, {{ siteData.longitude }}</span>
            </div>
          </div>
        </el-card>

        <!-- Contact Information -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Phone /></el-icon> Contact Information</span>
            </div>
          </template>
          <div class="info-content">
            <div class="info-row">
              <span class="info-label">Site Manager</span>
              <span v-if="!editMode" class="info-value">{{ siteData.siteManager }}</span>
              <el-input v-else v-model="editData.siteManager" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Phone Number</span>
              <span v-if="!editMode" class="info-value">{{ siteData.phone }}</span>
              <el-input v-else v-model="editData.phone" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Email</span>
              <span v-if="!editMode" class="info-value">{{ siteData.email }}</span>
              <el-input v-else v-model="editData.email" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Emergency Contact</span>
              <span v-if="!editMode" class="info-value">{{ siteData.emergencyContact }}</span>
              <el-input v-else v-model="editData.emergencyContact" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Emergency Phone</span>
              <span v-if="!editMode" class="info-value">{{ siteData.emergencyPhone }}</span>
              <el-input v-else v-model="editData.emergencyPhone" class="info-input" />
            </div>
          </div>
        </el-card>
      </div>

      <!-- Right Column -->
      <div class="right-column">
        <!-- Operational Settings -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Setting /></el-icon> Operational Settings</span>
            </div>
          </template>
          <div class="info-content">
            <div class="info-row">
              <span class="info-label">Business Hours</span>
              <span v-if="!editMode" class="info-value">{{ siteData.businessHours }}</span>
              <el-input v-else v-model="editData.businessHours" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Weekend Hours</span>
              <span v-if="!editMode" class="info-value">{{ siteData.weekendHours }}</span>
              <el-input v-else v-model="editData.weekendHours" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Energy Target</span>
              <span v-if="!editMode" class="info-value">{{ siteData.energyTarget }} kWh/sqm/year</span>
              <el-input-number v-else v-model="editData.energyTarget" :min="0" :max="500" class="info-input" />
            </div>
            <div class="info-row">
              <span class="info-label">Carbon Target</span>
              <span v-if="!editMode" class="info-value">{{ siteData.carbonTarget }} tons CO2/year</span>
              <el-input-number v-else v-model="editData.carbonTarget" :min="0" :max="10000" class="info-input" />
            </div>
          </div>
        </el-card>

        <!-- Site Map with Google Maps -->
        <el-card class="info-card map-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Location /></el-icon> Site Location Map</span>
              <div class="map-controls">
                <el-button size="small" @click="openGoogleMaps">
                  <el-icon><Location /></el-icon> Open in Maps
                </el-button>
                <el-button size="small" @click="reloadMap">
                  <el-icon><RefreshRight /></el-icon> Reload Map
                </el-button>
              </div>
            </div>
          </template>
          <div class="site-map-container">
            <iframe
                ref="mapIframe"
                :src="googleMapsUrl"
                class="map-iframe"
                frameborder="0"
                allowfullscreen
                loading="lazy"
                @load="onMapLoaded"
            ></iframe>
            <div v-if="mapLoading" class="map-loading-overlay">
              <div class="map-loader">
                <div class="map-spinner"></div>
                <span>Loading Google Maps...</span>
              </div>
            </div>
          </div>
          <div class="map-attribution">
            <span>📍 Location: {{ siteData.city }}, {{ siteData.country }}</span>
            <span>📐 Coordinates: {{ siteData.latitude }}, {{ siteData.longitude }}</span>
            <span>© Google Maps</span>
          </div>
        </el-card>

        <!-- Quick Stats -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> Quick Statistics</span>
            </div>
          </template>
          <div class="stats-row">
            <div class="quick-stat">
              <div class="quick-stat-value">{{ siteData.activeDevices }}</div>
              <div class="quick-stat-label">Active Devices</div>
            </div>
            <div class="quick-stat">
              <div class="quick-stat-value">{{ siteData.alertsCount }}</div>
              <div class="quick-stat-label">Active Alerts</div>
            </div>
            <div class="quick-stat">
              <div class="quick-stat-value">{{ siteData.maintenanceTasks }}</div>
              <div class="quick-stat-label">Maintenance</div>
            </div>
            <div class="quick-stat">
              <div class="quick-stat-value">{{ siteData.occupancyRate }}%</div>
              <div class="quick-stat-label">Occupancy</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Edit Mode Notice -->
    <div v-if="editMode" class="edit-notice">
      <el-alert
          title="Edit Mode Active"
          description="You are currently editing site information. Click 'Save Changes' to apply updates or 'Cancel Edit' to discard changes."
          type="info"
          show-icon
          :closable="false"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Edit, Check, RefreshRight, Location, Phone, Setting, DataAnalysis } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const mapLoading = ref(true)

const loadingMessages = [
  'Loading site profile...',
  'Fetching site data...',
  'Loading location details...',
  'Loading Google Maps...',
  'Almost ready...'
]

// Site data - Singapore Marina Bay Sands location
const siteData = reactive({
  id: 'SITE-001',
  code: 'SGP-MAIN',
  name: 'Singapore Marina Bay HQ',
  status: 'active',
  established: '2018',
  totalBuildings: 3,
  totalArea: 45,
  departments: 12,
  employees: 450,
  address: '10 Bayfront Avenue, Marina Bay, Singapore',
  city: 'Singapore',
  state: 'Central Region',
  country: 'Singapore',
  postalCode: '018956',
  timezone: 'UTC+8',
  siteManager: 'Johnathan Lee',
  phone: '+65 6789 0123',
  email: 'facility@company.com',
  emergencyContact: 'Security Control Room',
  emergencyPhone: '+65 6789 0999',
  businessHours: 'Mon-Fri: 8:00 AM - 6:00 PM',
  weekendHours: 'Sat: 9:00 AM - 1:00 PM, Sun: Closed',
  energyTarget: 185,
  carbonTarget: 1250,
  latitude: 1.2839,
  longitude: 103.8600,
  activeDevices: 1248,
  alertsCount: 3,
  maintenanceTasks: 8,
  occupancyRate: 87
})

// Edit data copy
const editData = reactive({ ...siteData })
const editMode = ref(false)
const mapIframe = ref<HTMLIFrameElement | null>(null)

// Google Maps Embed URL (English language)
const googleMapsUrl = computed(() => {
  const query = encodeURIComponent(`${siteData.latitude},${siteData.longitude}`)
  return `https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q=${query}&zoom=16&maptype=roadmap&language=en`
})

// Map load event handler
const onMapLoaded = () => {
  mapLoading.value = false
  checkAllLoaded()
}

// Reload map
const reloadMap = () => {
  mapLoading.value = true
  if (mapIframe.value) {
    const src = mapIframe.value.src
    mapIframe.value.src = ''
    setTimeout(() => {
      if (mapIframe.value) {
        mapIframe.value.src = src
      }
    }, 100)
  }
}

// Open in Google Maps
const openGoogleMaps = () => {
  window.open(`https://www.google.com/maps/search/?api=1&query=${siteData.latitude},${siteData.longitude}`, '_blank')
}

// Check if everything is loaded
const checkAllLoaded = () => {
  if (!mapLoading.value && loadingProgress.value >= 100) {
    setTimeout(() => {
      isLoaded.value = true
    }, 300)
  }
}

// Methods
const saveChanges = () => {
  ElMessageBox.confirm(
      'Save all changes to site profile?',
      'Confirm Changes',
      {
        confirmButtonText: 'Save',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
  ).then(() => {
    const coordsChanged = editData.latitude !== siteData.latitude || editData.longitude !== siteData.longitude
    Object.assign(siteData, editData)
    editMode.value = false
    ElMessage.success('Site profile updated successfully')

    if (coordsChanged) {
      reloadMap()
    }
  }).catch(() => {})
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
  reloadMap()
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
    checkAllLoaded()
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    if (loadingProgress.value < 100) loadingProgress.value = 100
    mapLoading.value = false
    isLoaded.value = true
  }, 8000)
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
.site-profile {
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

/* Overview Card */
.overview-card {
  background: white;
  border-radius: 24px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.overview-header {
  display: flex;
  align-items: center;
  gap: 24px;
  flex-wrap: wrap;
}

.site-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #1565c0, #1976d2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 40px;
}

.site-info {
  flex: 1;
}

.site-name {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin: 0 0 4px 0;
}

.site-code {
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.site-status {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.status-badge {
  font-size: 13px;
  font-weight: 500;
}

.status-badge.active { color: #67c23a; }
.status-badge.inactive { color: #f56c6c; }

.since-date {
  font-size: 12px;
  color: #909399;
}

.site-stats {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 12px;
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
  min-width: 130px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  text-align: right;
  flex: 1;
}

.info-input {
  width: 250px;
}

/* Map Card */
.map-card :deep(.el-card__body) {
  padding: 0;
  overflow: hidden;
}

.site-map-container {
  height: 380px;
  width: 100%;
  background: #e8eef4;
  position: relative;
}

.map-iframe {
  width: 100%;
  height: 100%;
  border: none;
}

.map-loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.map-loader {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #409eff;
}

.map-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #e4e7ed;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.map-controls {
  display: flex;
  gap: 8px;
}

.map-attribution {
  padding: 10px 16px;
  font-size: 11px;
  color: #909399;
  background: #f8f9fa;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

/* Quick Stats */
.stats-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-stat {
  text-align: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
}

.quick-stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.quick-stat-label {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
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
  .site-profile { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .overview-header { flex-direction: column; text-align: center; }
  .site-info { text-align: center; }
  .site-status { justify-content: center; }
  .info-row { flex-direction: column; align-items: flex-start; }
  .info-value { text-align: left; }
  .info-input { width: 100%; }
  .stats-row { grid-template-columns: 1fr; }
  .site-map-container { height: 280px; }
  .map-attribution { flex-direction: column; text-align: center; }
  .map-controls { justify-content: center; }
}
</style>