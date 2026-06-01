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
        <div class="loading-tip">Multi-Site Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="multi-site-management">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h2>Multi-Site Management</h2>
        <p class="subtitle">Manage and monitor multiple sites across different locations</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openAddSiteDialog">
          <el-icon><Plus /></el-icon> Add Site
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData">
          <el-icon><RefreshRight /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🌍</div>
        <div class="stat-info">
          <div class="stat-value">{{ sites.length }}</div>
          <div class="stat-label">Total Sites</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🏢</div>
        <div class="stat-info">
          <div class="stat-value">{{ totalBuildings }}</div>
          <div class="stat-label">Total Buildings</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📐</div>
        <div class="stat-info">
          <div class="stat-value">{{ formatNumber(totalArea) }}</div>
          <div class="stat-label">Total Area (sqm)</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgHealth }}%</div>
          <div class="stat-label">Avg Site Health</div>
        </div>
      </div>
    </div>

    <!-- Search and Filter Bar -->
    <div class="filter-section">
      <div class="search-wrapper">
        <el-input v-model="searchText" placeholder="Search by site name, location or region..." clearable :prefix-icon="Search" />
      </div>
      <div class="filter-wrapper">
        <el-select v-model="filterRegion" placeholder="Region" clearable style="width: 160px">
          <el-option label="All Regions" value="all" />
          <el-option label="Asia Pacific" value="asia" />
          <el-option label="Europe" value="europe" />
          <el-option label="North America" value="na" />
          <el-option label="Middle East" value="me" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="Status" clearable style="width: 140px">
          <el-option label="All Status" value="all" />
          <el-option label="Operational" value="operational" />
          <el-option label="Maintenance" value="maintenance" />
          <el-option label="Offline" value="offline" />
        </el-select>
      </div>
    </div>

    <!-- Map Overview -->
    <div class="map-overview">
      <div class="map-header">
        <span class="map-title">📍 Site Locations Map</span>
        <el-button size="small" @click="openGlobalMap">View Full Map</el-button>
      </div>
      <div class="map-placeholder">
        <div class="map-markers">
          <div v-for="site in sites" :key="site.id" class="map-marker" :style="{ left: site.mapX + '%', top: site.mapY + '%' }">
            <div class="marker-dot" :class="site.status"></div>
            <div class="marker-label">{{ site.code }}</div>
          </div>
        </div>
        <div class="world-map-bg"></div>
      </div>
    </div>

    <!-- Sites Grid -->
    <div class="sites-grid">
      <div v-for="site in filteredSites" :key="site.id" class="site-card" :class="site.status">
        <div class="site-header">
          <div class="site-icon">{{ getSiteIcon(site.type) }}</div>
          <div class="site-info">
            <div class="site-name">{{ site.name }}</div>
            <div class="site-code">{{ site.code }}</div>
          </div>
          <div class="site-status">
            <span class="status-badge" :class="site.status">{{ getStatusText(site.status) }}</span>
          </div>
        </div>

        <div class="site-location">
          <el-icon><Location /></el-icon>
          <span>{{ site.city }}, {{ site.country }}</span>
        </div>

        <div class="site-stats">
          <div class="stat-item">
            <div class="stat-number">{{ site.buildings }}</div>
            <div class="stat-label-sm">Buildings</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ site.campuses }}</div>
            <div class="stat-label-sm">Campuses</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ formatNumber(site.area) }}</div>
            <div class="stat-label-sm">sqm</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ site.health }}%</div>
            <div class="stat-label-sm">Health</div>
          </div>
        </div>

        <div class="site-details">
          <div class="detail-row">
            <span class="detail-label">Region</span>
            <span class="detail-value">{{ getRegionLabel(site.region) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Site Manager</span>
            <span class="detail-value">{{ site.manager }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Active Alerts</span>
            <span class="detail-value" :class="{ 'alert-count': site.activeAlerts > 0 }">{{ site.activeAlerts }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Last Sync</span>
            <span class="detail-value">{{ site.lastSync }}</span>
          </div>
        </div>

        <div class="site-actions">
          <el-button size="small" type="primary" plain @click="viewSite(site)">
            <el-icon><View /></el-icon> Details
          </el-button>
          <el-button size="small" type="info" plain @click="editSite(site)">
            <el-icon><Edit /></el-icon> Edit
          </el-button>
          <el-button size="small" type="danger" plain @click="deleteSite(site)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredSites.length === 0" class="empty-state">
      <div class="empty-icon">🌍</div>
      <div class="empty-title">No sites found</div>
      <div class="empty-desc">Add a site to start multi-site management</div>
      <el-button type="primary" @click="openAddSiteDialog">Add Site</el-button>
    </div>

    <!-- Add/Edit Site Dialog -->
    <el-dialog v-model="showSiteDialog" :title="dialogTitle" width="650px">
      <el-form :model="siteForm" label-width="130px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Site Name" required>
              <el-input v-model="siteForm.name" placeholder="Enter site name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Site Code">
              <el-input v-model="siteForm.code" placeholder="e.g., SGP-01" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Country">
              <el-select v-model="siteForm.country" style="width: 100%">
                <el-option label="Singapore" value="Singapore" />
                <el-option label="Malaysia" value="Malaysia" />
                <el-option label="China" value="China" />
                <el-option label="Japan" value="Japan" />
                <el-option label="USA" value="USA" />
                <el-option label="UK" value="UK" />
                <el-option label="Germany" value="Germany" />
                <el-option label="UAE" value="UAE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="City">
              <el-input v-model="siteForm.city" placeholder="City" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Region">
              <el-select v-model="siteForm.region" style="width: 100%">
                <el-option label="Asia Pacific" value="asia" />
                <el-option label="Europe" value="europe" />
                <el-option label="North America" value="na" />
                <el-option label="Middle East" value="me" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Address">
          <el-input v-model="siteForm.address" placeholder="Street address" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Area (sqm)">
              <el-input-number v-model="siteForm.area" :min="0" :step="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Number of Buildings">
              <el-input-number v-model="siteForm.buildings" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Number of Campuses">
              <el-input-number v-model="siteForm.campuses" :min="0" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="Site Type">
              <el-select v-model="siteForm.type" style="width: 100%">
                <el-option label="Corporate" value="corporate" />
                <el-option label="Industrial" value="industrial" />
                <el-option label="Data Center" value="datacenter" />
                <el-option label="Mixed Use" value="mixed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Site Manager">
              <el-input v-model="siteForm.manager" placeholder="Manager name" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="Status">
              <el-select v-model="siteForm.status" style="width: 100%">
                <el-option label="Operational" value="operational" />
                <el-option label="Maintenance" value="maintenance" />
                <el-option label="Offline" value="offline" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Map X Position">
              <el-input-number v-model="siteForm.mapX" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Map Y Position">
              <el-input-number v-model="siteForm.mapY" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="Description">
          <el-input v-model="siteForm.description" type="textarea" :rows="2" placeholder="Additional notes" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSiteDialog = false">Cancel</el-button>
        <el-button type="primary" @click="saveSite">Save Site</el-button>
      </template>
    </el-dialog>

    <!-- Site Detail Dialog -->
    <el-dialog v-model="showDetailDialog" :title="selectedSite?.name" width="750px">
      <div v-if="selectedSite">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Site ID">{{ selectedSite.id }}</el-descriptions-item>
          <el-descriptions-item label="Site Code">{{ selectedSite.code }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ getSiteTypeLabel(selectedSite.type) }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <span :class="['status-badge', selectedSite.status]">{{ getStatusText(selectedSite.status) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Location" :span="2">{{ selectedSite.address }}, {{ selectedSite.city }}, {{ selectedSite.country }}</el-descriptions-item>
          <el-descriptions-item label="Region">{{ getRegionLabel(selectedSite.region) }}</el-descriptions-item>
          <el-descriptions-item label="Total Area">{{ formatNumber(selectedSite.area) }} sqm</el-descriptions-item>
          <el-descriptions-item label="Buildings">{{ selectedSite.buildings }}</el-descriptions-item>
          <el-descriptions-item label="Campuses">{{ selectedSite.campuses }}</el-descriptions-item>
          <el-descriptions-item label="Site Health">{{ selectedSite.health }}%</el-descriptions-item>
          <el-descriptions-item label="Site Manager">{{ selectedSite.manager }}</el-descriptions-item>
          <el-descriptions-item label="Active Alerts">{{ selectedSite.activeAlerts }}</el-descriptions-item>
          <el-descriptions-item label="Last Sync">{{ selectedSite.lastSync }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ selectedSite.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">Close</el-button>
        <el-button type="primary" @click="editSite(selectedSite); showDetailDialog = false">Edit</el-button>
      </template>
    </el-dialog>

    <!-- Global Map Dialog -->
    <el-dialog v-model="showGlobalMap" title="Global Site Locations" width="900px">
      <div class="global-map-container">
        <div class="global-map-placeholder">
          <div class="map-markers-global">
            <div v-for="site in sites" :key="site.id" class="map-marker-global" :style="{ left: site.mapX + '%', top: site.mapY + '%' }">
              <div class="marker-dot" :class="site.status" @click="viewSite(site)"></div>
              <div class="marker-tooltip">{{ site.name }}</div>
            </div>
          </div>
          <div class="world-map-full"></div>
        </div>
        <div class="global-map-legend">
          <div class="legend-item"><span class="legend-dot operational"></span> Operational</div>
          <div class="legend-item"><span class="legend-dot maintenance"></span> Maintenance</div>
          <div class="legend-item"><span class="legend-dot offline"></span> Offline</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showGlobalMap = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Plus, RefreshRight, Search, Download, View, Edit, Delete, Location } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Loading multi-site data...',
  'Fetching site information...',
  'Loading map data...',
  'Almost ready...'
]

// Site interface
interface Site {
  id: number
  name: string
  code: string
  type: string
  status: string
  region: string
  country: string
  city: string
  address: string
  area: number
  buildings: number
  campuses: number
  health: number
  manager: string
  activeAlerts: number
  lastSync: string
  description: string
  mapX: number
  mapY: number
}

// Sample sites data
const sites = ref<Site[]>([
  {
    id: 1,
    name: 'Singapore Headquarters',
    code: 'SGP-01',
    type: 'corporate',
    status: 'operational',
    region: 'asia',
    country: 'Singapore',
    city: 'Singapore',
    address: '8 Marina Boulevard',
    area: 125000,
    buildings: 4,
    campuses: 2,
    health: 98,
    manager: 'Johnathan Lee',
    activeAlerts: 2,
    lastSync: '2025-01-16 08:30:00',
    description: 'Main corporate headquarters',
    mapX: 55,
    mapY: 45
  },
  {
    id: 2,
    name: 'Jurong Industrial Hub',
    code: 'SGP-02',
    type: 'industrial',
    status: 'operational',
    region: 'asia',
    country: 'Singapore',
    city: 'Singapore',
    address: '15 Jurong West Street',
    area: 85000,
    buildings: 6,
    campuses: 1,
    health: 92,
    manager: 'Michael Tan',
    activeAlerts: 5,
    lastSync: '2025-01-16 08:25:00',
    description: 'Industrial and logistics hub',
    mapX: 50,
    mapY: 48
  },
  {
    id: 3,
    name: 'Shanghai Tech Park',
    code: 'SHA-01',
    type: 'datacenter',
    status: 'operational',
    region: 'asia',
    country: 'China',
    city: 'Shanghai',
    address: '999 Pudong New Area',
    area: 45000,
    buildings: 3,
    campuses: 1,
    health: 96,
    manager: 'Wei Zhang',
    activeAlerts: 1,
    lastSync: '2025-01-16 08:20:00',
    description: 'Technology and data center campus',
    mapX: 70,
    mapY: 42
  },
  {
    id: 4,
    name: 'Tokyo Data Center',
    code: 'TYO-01',
    type: 'datacenter',
    status: 'maintenance',
    region: 'asia',
    country: 'Japan',
    city: 'Tokyo',
    address: '2-1-1 Otsuka, Bunkyo-ku',
    area: 32000,
    buildings: 2,
    campuses: 1,
    health: 78,
    manager: 'Kenji Sato',
    activeAlerts: 8,
    lastSync: '2025-01-16 08:15:00',
    description: 'Primary data center - scheduled maintenance',
    mapX: 75,
    mapY: 38
  },
  {
    id: 5,
    name: 'London Corporate Park',
    code: 'LON-01',
    type: 'corporate',
    status: 'operational',
    region: 'europe',
    country: 'UK',
    city: 'London',
    address: '1 Canada Square, Canary Wharf',
    area: 68000,
    buildings: 3,
    campuses: 2,
    health: 95,
    manager: 'James Wilson',
    activeAlerts: 3,
    lastSync: '2025-01-16 08:10:00',
    description: 'European headquarters',
    mapX: 35,
    mapY: 35
  },
  {
    id: 6,
    name: 'Frankfurt Data Hub',
    code: 'FRA-01',
    type: 'datacenter',
    status: 'operational',
    region: 'europe',
    country: 'Germany',
    city: 'Frankfurt',
    address: 'Hanauer Landstrasse 120',
    area: 28000,
    buildings: 2,
    campuses: 1,
    health: 97,
    manager: 'Hans Mueller',
    activeAlerts: 0,
    lastSync: '2025-01-16 08:05:00',
    description: 'Cloud data center',
    mapX: 30,
    mapY: 32
  },
  {
    id: 7,
    name: 'New York Innovation Hub',
    code: 'NYC-01',
    type: 'mixed',
    status: 'operational',
    region: 'na',
    country: 'USA',
    city: 'New York',
    address: '300 Hudson Street',
    area: 52000,
    buildings: 2,
    campuses: 1,
    health: 94,
    manager: 'Sarah Johnson',
    activeAlerts: 4,
    lastSync: '2025-01-16 08:00:00',
    description: 'Mixed-use innovation center',
    mapX: 25,
    mapY: 40
  },
  {
    id: 8,
    name: 'Dubai Smart City',
    code: 'DXB-01',
    type: 'mixed',
    status: 'operational',
    region: 'me',
    country: 'UAE',
    city: 'Dubai',
    address: 'Dubai Internet City',
    area: 75000,
    buildings: 5,
    campuses: 2,
    health: 93,
    manager: 'Ahmed Al Mansouri',
    activeAlerts: 2,
    lastSync: '2025-01-16 07:55:00',
    description: 'Smart city campus',
    mapX: 65,
    mapY: 55
  }
])

// UI State
const searchText = ref('')
const filterRegion = ref('all')
const filterStatus = ref('all')
const showSiteDialog = ref(false)
const showDetailDialog = ref(false)
const showGlobalMap = ref(false)
const isEditing = ref(false)
const selectedSite = ref<Site | null>(null)

const siteForm = ref({
  name: '',
  code: '',
  type: 'corporate',
  status: 'operational',
  region: 'asia',
  country: 'Singapore',
  city: '',
  address: '',
  area: 0,
  buildings: 1,
  campuses: 1,
  manager: '',
  description: '',
  mapX: 50,
  mapY: 50
})

// Computed
const dialogTitle = computed(() => isEditing.value ? 'Edit Site' : 'Add Site')

const totalBuildings = computed(() => sites.value.reduce((sum, s) => sum + s.buildings, 0))
const totalArea = computed(() => sites.value.reduce((sum, s) => sum + s.area, 0))
const avgHealth = computed(() => Math.round(sites.value.reduce((sum, s) => sum + s.health, 0) / sites.value.length))

const filteredSites = computed(() => {
  let filtered = [...sites.value]

  if (searchText.value) {
    const keyword = searchText.value.toLowerCase()
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(keyword) ||
        s.code.toLowerCase().includes(keyword) ||
        s.city.toLowerCase().includes(keyword) ||
        s.country.toLowerCase().includes(keyword)
    )
  }

  if (filterRegion.value !== 'all') {
    filtered = filtered.filter(s => s.region === filterRegion.value)
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(s => s.status === filterStatus.value)
  }

  return filtered
})

// Helper functions
const formatNumber = (num: number) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(0) + 'k'
  return num.toLocaleString()
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    operational: 'Operational',
    maintenance: 'Maintenance',
    offline: 'Offline'
  }
  return map[status] || status
}

const getRegionLabel = (region: string) => {
  const map: Record<string, string> = {
    asia: 'Asia Pacific',
    europe: 'Europe',
    na: 'North America',
    me: 'Middle East'
  }
  return map[region] || region
}

const getSiteIcon = (type: string) => {
  const map: Record<string, string> = {
    corporate: '🏢',
    industrial: '🏭',
    datacenter: '💿',
    mixed: '🏙️'
  }
  return map[type] || '📍'
}

const getSiteTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    corporate: 'Corporate',
    industrial: 'Industrial',
    datacenter: 'Data Center',
    mixed: 'Mixed Use'
  }
  return map[type] || type
}

const openGlobalMap = () => {
  showGlobalMap.value = true
}

// Site CRUD operations
const openAddSiteDialog = () => {
  isEditing.value = false
  siteForm.value = {
    name: '',
    code: '',
    type: 'corporate',
    status: 'operational',
    region: 'asia',
    country: 'Singapore',
    city: '',
    address: '',
    area: 0,
    buildings: 1,
    campuses: 1,
    manager: '',
    description: '',
    mapX: 50,
    mapY: 50
  }
  showSiteDialog.value = true
}

const editSite = (site: Site) => {
  isEditing.value = true
  selectedSite.value = site
  siteForm.value = {
    name: site.name,
    code: site.code,
    type: site.type,
    status: site.status,
    region: site.region,
    country: site.country,
    city: site.city,
    address: site.address,
    area: site.area,
    buildings: site.buildings,
    campuses: site.campuses,
    manager: site.manager,
    description: site.description || '',
    mapX: site.mapX,
    mapY: site.mapY
  }
  showSiteDialog.value = true
}

const saveSite = () => {
  if (!siteForm.value.name.trim()) {
    ElMessage.warning('Please enter site name')
    return
  }
  if (!siteForm.value.city.trim()) {
    ElMessage.warning('Please enter city')
    return
  }

  if (isEditing.value && selectedSite.value) {
    const index = sites.value.findIndex(s => s.id === selectedSite.value!.id)
    if (index !== -1) {
      sites.value[index] = {
        ...sites.value[index],
        name: siteForm.value.name,
        code: siteForm.value.code,
        type: siteForm.value.type,
        status: siteForm.value.status,
        region: siteForm.value.region,
        country: siteForm.value.country,
        city: siteForm.value.city,
        address: siteForm.value.address,
        area: siteForm.value.area,
        buildings: siteForm.value.buildings,
        campuses: siteForm.value.campuses,
        manager: siteForm.value.manager,
        description: siteForm.value.description,
        mapX: siteForm.value.mapX,
        mapY: siteForm.value.mapY
      }
      ElMessage.success('Site updated successfully')
    }
  } else {
    const newSite: Site = {
      id: Date.now(),
      name: siteForm.value.name,
      code: siteForm.value.code || `SITE-${sites.value.length + 1}`,
      type: siteForm.value.type,
      status: siteForm.value.status,
      region: siteForm.value.region,
      country: siteForm.value.country,
      city: siteForm.value.city,
      address: siteForm.value.address,
      area: siteForm.value.area,
      buildings: siteForm.value.buildings,
      campuses: siteForm.value.campuses,
      health: 85,
      manager: siteForm.value.manager,
      activeAlerts: 0,
      lastSync: new Date().toLocaleString(),
      description: siteForm.value.description,
      mapX: siteForm.value.mapX,
      mapY: siteForm.value.mapY
    }
    sites.value.push(newSite)
    ElMessage.success('Site added successfully')
  }

  showSiteDialog.value = false
}

const viewSite = (site: Site) => {
  selectedSite.value = site
  showDetailDialog.value = true
}

const deleteSite = (site: Site) => {
  ElMessageBox.confirm(
      `Delete site "${site.name}"? This will also remove all associated campuses, buildings, and devices.`,
      'Delete Site',
      {
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  ).then(() => {
    const index = sites.value.findIndex(s => s.id === site.id)
    if (index !== -1) {
      sites.value.splice(index, 1)
      ElMessage.success('Site deleted successfully')
    }
  }).catch(() => {})
}

const exportData = () => {
  const data = JSON.stringify(filteredSites.value, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `sites_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Export completed')
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
.multi-site-management {
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

/* Filter Section */
.filter-section {
  background: white;
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.search-wrapper {
  flex: 1;
  min-width: 250px;
}

.filter-wrapper {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* Map Overview */
.map-overview {
  background: white;
  border-radius: 20px;
  margin-bottom: 24px;
  overflow: hidden;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.map-title {
  font-size: 16px;
  font-weight: 600;
}

.map-placeholder {
  position: relative;
  height: 250px;
  background: linear-gradient(135deg, #1a237e, #0d47a1);
  overflow: hidden;
}

.world-map-bg {
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" fill="none"><path d="M100,200 C150,150 200,180 250,160 C300,140 350,170 400,150 C450,130 500,160 550,140 C600,120 650,150 700,130" stroke="rgba(255,255,255,0.1)" stroke-width="2" fill="none"/><ellipse cx="200" cy="200" rx="80" ry="60" stroke="rgba(255,255,255,0.05)" stroke-width="1"/><ellipse cx="600" cy="180" rx="100" ry="70" stroke="rgba(255,255,255,0.05)" stroke-width="1"/><ellipse cx="400" cy="220" rx="120" ry="80" stroke="rgba(255,255,255,0.05)" stroke-width="1"/></svg>');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
}

.map-markers {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.map-marker {
  position: absolute;
  cursor: pointer;
  transform: translate(-50%, -50%);
}

.marker-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.marker-dot.operational { background: #67c23a; }
.marker-dot.maintenance { background: #e6a23c; }
.marker-dot.offline { background: #f56c6c; }

.marker-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 9px;
  color: white;
  white-space: nowrap;
  background: rgba(0,0,0,0.5);
  padding: 2px 6px;
  border-radius: 10px;
}

/* Sites Grid */
.sites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.site-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border-left: 4px solid #67c23a;
}

.site-card.maintenance { border-left-color: #e6a23c; }
.site-card.offline { border-left-color: #f56c6c; }
.site-card.operational { border-left-color: #67c23a; }

.site-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.site-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.site-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.site-info {
  flex: 1;
}

.site-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.site-code {
  font-size: 11px;
  color: #909399;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
}

.status-badge.operational { background: #e8f5e9; color: #67c23a; }
.status-badge.maintenance { background: #fff7e6; color: #e6a23c; }
.status-badge.offline { background: #ffefef; color: #f56c6c; }

.site-location {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.site-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #409eff;
}

.stat-label-sm {
  font-size: 10px;
  color: #909399;
  margin-top: 2px;
}

.site-details {
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 12px;
}

.detail-label {
  color: #909399;
}

.detail-value {
  color: #303133;
  font-weight: 500;
}

.alert-count {
  color: #f56c6c;
  font-weight: 700;
}

.site-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 20px;
  margin-top: 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: #909399;
  margin-bottom: 24px;
}

/* Global Map Dialog */
.global-map-container {
  position: relative;
}

.global-map-placeholder {
  position: relative;
  height: 400px;
  background: linear-gradient(135deg, #1a237e, #0d47a1);
  border-radius: 12px;
  overflow: hidden;
}

.world-map-full {
  width: 100%;
  height: 100%;
  background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400" fill="none"><path d="M100,200 C150,150 200,180 250,160 C300,140 350,170 400,150 C450,130 500,160 550,140 C600,120 650,150 700,130" stroke="rgba(255,255,255,0.15)" stroke-width="2" fill="none"/><ellipse cx="200" cy="200" rx="80" ry="60" stroke="rgba(255,255,255,0.08)" stroke-width="1"/><ellipse cx="600" cy="180" rx="100" ry="70" stroke="rgba(255,255,255,0.08)" stroke-width="1"/><ellipse cx="400" cy="220" rx="120" ry="80" stroke="rgba(255,255,255,0.08)" stroke-width="1"/></svg>');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
}

.map-markers-global {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.map-marker-global {
  position: absolute;
  cursor: pointer;
  transform: translate(-50%, -50%);
}

.map-marker-global .marker-dot {
  width: 14px;
  height: 14px;
}

.marker-tooltip {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 10px;
  color: white;
  white-space: nowrap;
  background: rgba(0,0,0,0.7);
  padding: 2px 8px;
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

.map-marker-global:hover .marker-tooltip {
  opacity: 1;
}

.global-map-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.operational { background: #67c23a; }
.legend-dot.maintenance { background: #e6a23c; }
.legend-dot.offline { background: #f56c6c; }

/* Dialog */
:deep(.el-dialog__body) {
  padding: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .multi-site-management { padding: 16px; }
  .page-header { flex-direction: column; align-items: stretch; }
  .header-actions { flex-direction: column; }
  .header-actions .el-button { width: 100%; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .filter-section { flex-direction: column; }
  .search-wrapper { width: 100%; }
  .filter-wrapper { width: 100%; justify-content: space-between; }
  .sites-grid { grid-template-columns: 1fr; }
  .map-placeholder { height: 200px; }
  .site-stats { grid-template-columns: repeat(2, 1fr); }
}
</style>