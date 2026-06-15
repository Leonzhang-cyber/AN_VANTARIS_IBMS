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
          <span class="loading-title">Loading Driver Marketplace</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Discover, Download, and Deploy Device Drivers</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="driver-marketplace-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Driver Marketplace</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Developer Center</el-breadcrumb-item>
          <el-breadcrumb-item>Driver Marketplace</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="uploadDriver">
          <el-icon><Upload /></el-icon>
          Upload Driver
        </el-button>
        <el-button type="success" plain @click="createDriver">
          <el-icon><MagicStick /></el-icon>
          Create Driver
        </el-button>
        <el-button type="info" plain @click="viewMyDrivers">
          <el-icon><User /></el-icon>
          My Drivers
        </el-button>
      </div>
    </div>

    <!-- Search and Filter Section -->
    <el-card class="search-card" shadow="hover">
      <div class="search-section">
        <el-input v-model="searchKeyword" placeholder="Search drivers by name, protocol, or vendor..." size="large" class="search-input" clearable>
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="selectedProtocol" placeholder="Protocol" size="large" style="width: 150px" clearable>
          <el-option label="BACnet" value="bacnet" />
          <el-option label="Modbus" value="modbus" />
          <el-option label="MQTT" value="mqtt" />
          <el-option label="OPC-UA" value="opcua" />
          <el-option label="SNMP" value="snmp" />
          <el-option label="KNX" value="knx" />
        </el-select>
        <el-select v-model="selectedCategory" placeholder="Category" size="large" style="width: 150px" clearable>
          <el-option label="HVAC" value="hvac" />
          <el-option label="Lighting" value="lighting" />
          <el-option label="Security" value="security" />
          <el-option label="Power" value="power" />
          <el-option label="Data Center" value="datacenter" />
        </el-select>
        <el-button type="primary" size="large" @click="handleSearch">
          <el-icon><Search /></el-icon>
          Search
        </el-button>
        <el-button size="large" @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          Reset
        </el-button>
      </div>
    </el-card>

    <!-- Featured Drivers Banner -->
    <el-card class="featured-banner" shadow="hover">
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon :size="48"><Medal /></el-icon>
        </div>
        <div class="banner-info">
          <div class="banner-title">Featured Driver of the Week</div>
          <div class="banner-name">{{ featuredDriver.name }}</div>
          <div class="banner-description">{{ featuredDriver.description }}</div>
          <div class="banner-stats">
            <span><el-icon><Download /></el-icon> {{ featuredDriver.downloads }} downloads</span>
            <span><el-icon><Star /></el-icon> {{ featuredDriver.rating }} ({{ featuredDriver.reviews }} reviews)</span>
            <span><el-icon><SuccessFilled /></el-icon> {{ featuredDriver.compatibility }}</span>
          </div>
        </div>
        <el-button type="primary" size="large" @click="downloadDriver(featuredDriver)">
          <el-icon><Download /></el-icon>
          Download Now
        </el-button>
      </div>
    </el-card>

    <!-- Driver Statistics -->
    <div class="stats-section">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Service /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalDrivers }}</div>
            <div class="stat-label">Total Drivers</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Download /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalDownloads }}</div>
            <div class="stat-label">Total Downloads</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Connection /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ supportedProtocols }}</div>
            <div class="stat-label">Protocols Supported</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><User /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ activeDevelopers }}</div>
            <div class="stat-label">Active Developers</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Driver Categories -->
    <div class="categories-section">
      <h3 class="section-title">Browse by Category</h3>
      <div class="categories-grid">
        <div v-for="cat in categories" :key="cat.name" class="category-card" @click="filterByCategory(cat.name)">
          <div class="category-icon" :style="{ backgroundColor: cat.color }">
            <el-icon :size="28"><component :is="cat.icon" /></el-icon>
          </div>
          <div class="category-info">
            <h4>{{ cat.name }}</h4>
            <p>{{ cat.count }} drivers</p>
          </div>
          <el-icon class="category-arrow"><Share /></el-icon>
        </div>
      </div>
    </div>

    <!-- Popular Drivers Grid -->
    <div class="drivers-section">
      <div class="section-header">
        <h3 class="section-title">Popular Drivers</h3>
        <el-button text type="primary" @click="viewAllDrivers">View All Drivers <el-icon><Share /></el-icon></el-button>
      </div>
      <div class="drivers-grid">
        <el-card v-for="driver in displayedDrivers" :key="driver.id" class="driver-card" shadow="hover">
          <div class="driver-header">
            <div class="driver-icon" :style="{ backgroundColor: driver.color }">
              <el-icon :size="32"><component :is="driver.icon" /></el-icon>
            </div>
            <el-tag :type="getDriverTagType(driver.certified)" size="small">
              {{ driver.certified ? 'Certified' : 'Community' }}
            </el-tag>
          </div>
          <div class="driver-info">
            <h4 class="driver-name">{{ driver.name }}</h4>
            <p class="driver-description">{{ driver.description }}</p>
            <div class="driver-meta">
              <span><el-icon><User /></el-icon> {{ driver.author }}</span>
              <span><el-icon><Download /></el-icon> {{ driver.downloads }}</span>
              <span><el-icon><Star /></el-icon> {{ driver.rating }}</span>
            </div>
            <div class="driver-tags">
              <el-tag v-for="tag in driver.tags.slice(0, 3)" :key="tag" size="small" type="info">{{ tag }}</el-tag>
            </div>
            <div class="driver-version">
              <span>Version: {{ driver.version }}</span>
              <span>Updated: {{ driver.updated }}</span>
            </div>
          </div>
          <div class="driver-actions">
            <el-button type="primary" size="small" @click="downloadDriver(driver)">
              <el-icon><Download /></el-icon> Download
            </el-button>
            <el-button size="small" @click="viewDriverDetails(driver)">
              <el-icon><Search /></el-icon> Details
            </el-button>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Recently Updated Drivers -->
    <div class="recent-section">
      <div class="section-header">
        <h3 class="section-title">Recently Updated</h3>
        <el-button text type="primary" @click="viewRecentDrivers">View All <el-icon><Share /></el-icon></el-button>
      </div>
      <el-table :data="recentDrivers" stripe style="width: 100%">
        <el-table-column prop="name" label="Driver Name" min-width="200" />
        <el-table-column prop="author" label="Author" width="150" />
        <el-table-column prop="version" label="Version" width="100" />
        <el-table-column prop="protocol" label="Protocol" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.protocol }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated" label="Updated" width="140" />
        <el-table-column prop="downloads" label="Downloads" width="100" sortable />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="downloadDriver(row)">
              <el-icon><Download /></el-icon> Download
            </el-button>
            <el-button size="small" plain @click="viewDriverDetails(row)">
              <el-icon><Search /></el-icon> Info
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Driver Development Resources -->
    <div class="resources-section">
      <el-card class="resources-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><MagicStick /></el-icon> Driver Development Resources</span>
            <el-button text type="primary" @click="viewAllResources">Browse Resources</el-button>
          </div>
        </template>
        <div class="resources-grid">
          <div v-for="resource in resources" :key="resource.id" class="resource-item">
            <div class="resource-icon">
              <el-icon :size="24"><component :is="resource.icon" /></el-icon>
            </div>
            <div class="resource-info">
              <div class="resource-title">{{ resource.title }}</div>
              <div class="resource-description">{{ resource.description }}</div>
            </div>
            <el-button size="small" text type="primary" @click="viewResource(resource)">
              <el-icon><Search /></el-icon> Learn More
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Top Contributors -->
    <div class="contributors-section">
      <el-card class="contributors-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Medal /></el-icon> Top Contributors</span>
            <el-button text type="primary" @click="viewLeaderboard">View Leaderboard</el-button>
          </div>
        </template>
        <div class="contributors-grid">
          <div v-for="contributor in topContributors" :key="contributor.id" class="contributor-item">
            <div class="contributor-rank" :class="{ 'top': contributor.rank <= 3 }">#{{ contributor.rank }}</div>
            <div class="contributor-avatar">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="contributor-info">
              <div class="contributor-name">{{ contributor.name }}</div>
              <div class="contributor-stats">{{ contributor.drivers }} drivers · {{ contributor.downloads }}K downloads</div>
            </div>
            <el-button size="small" text type="primary" @click="viewContributor(contributor)">
              <el-icon><Search /></el-icon> View
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="requestDriver">
          <el-icon><Message /></el-icon>
          Request Driver
        </el-button>
        <el-button type="success" plain @click="reportIssue">
          <el-icon><Warning /></el-icon>
          Report Issue
        </el-button>
        <el-button type="warning" plain @click="viewDocumentation">
          <el-icon><Document /></el-icon>
          Documentation
        </el-button>
        <el-button type="info" plain @click="joinCommunity">
          <el-icon><ChatDotRound /></el-icon>
          Join Community
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Setting, User, Clock, Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic, Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service, Search, Edit, Plus, VideoPlay,
  VideoPause, Operation, Headset, Monitor, Cpu, Connection, Lock, Key, Medal,
  Flag, DataAnalysis, EditPen, Tickets, Filter, SuccessFilled, List
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Driver Marketplace...')

const loadingMessages = [
  'Loading Driver Marketplace...',
  'Fetching available drivers...',
  'Loading vendor certifications...',
  'Marketplace ready!'
]

// Search filters
const searchKeyword = ref('')
const selectedProtocol = ref('')
const selectedCategory = ref('')

// Statistics
const totalDrivers = ref(347)
const totalDownloads = ref(28500)
const supportedProtocols = ref(12)
const activeDevelopers = ref(156)

// Featured driver
const featuredDriver = ref({
  id: 1,
  name: 'Siemens BACnet Driver Suite',
  description: 'Complete BACnet driver for Siemens building automation systems. Supports BACnet/IP, BACnet/MSTP with full device discovery and point management.',
  downloads: 12450,
  rating: 4.9,
  reviews: 342,
  compatibility: 'BACnet/IP, BACnet/MSTP',
  icon: 'Connection'
})

// Categories
const categories = ref([
  { name: 'HVAC', icon: 'Operation', count: 86, color: '#3b82f6' },
  { name: 'Lighting', icon: 'EditPen', count: 54, color: '#10b981' },
  { name: 'Security', icon: 'Lock', count: 42, color: '#ef4444' },
  { name: 'Power', icon: 'DataLine', count: 38, color: '#f59e0b' },
  { name: 'Data Center', icon: 'Monitor', count: 67, color: '#8b5cf6' },
  { name: 'Fire Safety', icon: 'Warning', count: 23, color: '#ec489a' },
  { name: 'Access Control', icon: 'Key', count: 31, color: '#06b6d4' },
  { name: 'IoT Sensors', icon: 'Connection', count: 45, color: '#84cc16' }
])

// Popular drivers
const popularDrivers = ref([
  { id: 1, name: 'Siemens BACnet Driver', description: 'Full BACnet protocol support for Siemens controllers', author: 'Siemens AG', downloads: 12450, rating: 4.9, version: '3.2.1', updated: '2024-01-10', certified: true, tags: ['BACnet', 'HVAC', 'Building Automation'], color: '#3b82f6', icon: 'Connection', protocol: 'bacnet' },
  { id: 2, name: 'Modbus TCP/IP Driver', description: 'High-performance Modbus driver for PLCs and RTUs', author: 'Modbus.org', downloads: 9870, rating: 4.8, version: '2.5.0', updated: '2024-01-08', certified: true, tags: ['Modbus', 'PLC', 'Industrial'], color: '#10b981', icon: 'DataLine', protocol: 'modbus' },
  { id: 3, name: 'Schneider Electric MQTT', description: 'MQTT connector for Schneider IoT devices', author: 'Schneider Electric', downloads: 7650, rating: 4.7, version: '1.8.3', updated: '2024-01-05', certified: true, tags: ['MQTT', 'IoT', 'Schneider'], color: '#f59e0b', icon: 'Connection', protocol: 'mqtt' },
  { id: 4, name: 'Honeywell Spyder Driver', description: 'Driver for Honeywell Spyder controllers', author: 'Honeywell', downloads: 5430, rating: 4.6, version: '2.1.0', updated: '2024-01-03', certified: true, tags: ['Honeywell', 'HVAC', 'Controller'], color: '#ef4444', icon: 'Cpu', protocol: 'bacnet' },
  { id: 5, name: 'ONVIF Camera Driver', description: 'Video surveillance driver for IP cameras', author: 'Security Labs', downloads: 4320, rating: 4.5, version: '1.4.2', updated: '2024-01-01', certified: false, tags: ['ONVIF', 'Camera', 'Security'], color: '#8b5cf6', icon: 'VideoPlay', protocol: 'onvif' },
  { id: 6, name: 'Johnson Controls N2', description: 'Legacy N2 protocol driver for JCI controllers', author: 'JCI Integration', downloads: 3210, rating: 4.4, version: '1.9.1', updated: '2023-12-28', certified: false, tags: ['N2', 'JCI', 'Legacy'], color: '#ec489a', icon: 'Operation', protocol: 'n2' }
])

// Recent drivers
const recentDrivers = ref([
  { id: 101, name: 'ABB ACS880 Drive Driver', author: 'ABB Robotics', version: '1.0.0', protocol: 'Modbus', updated: '2024-01-14', downloads: 234 },
  { id: 102, name: 'Daikin VRV Controller', author: 'Daikin HVAC', version: '2.0.1', protocol: 'BACnet', updated: '2024-01-13', downloads: 567 },
  { id: 103, name: 'Hikvision NVR Driver', author: 'Hikvision', version: '3.1.0', protocol: 'ONVIF', updated: '2024-01-12', downloads: 890 },
  { id: 104, name: 'Tridium Niagara Driver', author: 'Tridium', version: '4.5.0', protocol: 'BACnet', updated: '2024-01-11', downloads: 1243 },
  { id: 105, name: 'OpenWeather API Driver', author: 'Community', version: '1.2.0', protocol: 'REST', updated: '2024-01-10', downloads: 456 }
])

// Resources
const resources = ref([
  { id: 1, title: 'Driver Development Guide', description: 'Step-by-step guide to creating custom drivers for IBMS', icon: 'Document' },
  { id: 2, title: 'SDK Documentation', description: 'Complete SDK reference for driver development', icon: 'MagicStick' },
  { id: 3, title: 'Driver Certification Program', description: 'Get your driver certified for enterprise use', icon: 'Medal' },
  { id: 4, title: 'API Integration Examples', description: 'Code samples for common integration patterns', icon: 'DataAnalysis' }
])

// Top contributors
const topContributors = ref([
  { id: 1, rank: 1, name: 'John Smith', drivers: 24, downloads: 125, icon: 'User' },
  { id: 2, rank: 2, name: 'Sarah Chen', drivers: 18, downloads: 89, icon: 'User' },
  { id: 3, rank: 3, name: 'Mike Johnson', drivers: 15, downloads: 76, icon: 'User' },
  { id: 4, rank: 4, name: 'Emma Wilson', drivers: 12, downloads: 54, icon: 'User' },
  { id: 5, rank: 5, name: 'David Kim', drivers: 10, downloads: 42, icon: 'User' }
])

// Filtered drivers
const displayedDrivers = computed(() => {
  let result = popularDrivers.value
  if (searchKeyword.value) {
    const search = searchKeyword.value.toLowerCase()
    result = result.filter(d => d.name.toLowerCase().includes(search) || d.description.toLowerCase().includes(search))
  }
  if (selectedProtocol.value) {
    result = result.filter(d => d.protocol === selectedProtocol.value)
  }
  return result
})

// Helper functions
const getDriverTagType = (certified: boolean) => {
  return certified ? 'success' : 'info'
}

const filterByCategory = (category: string) => {
  selectedCategory.value = category
  ElMessage.info(`Filtering by category: ${category}`)
}

const handleSearch = () => {
  ElMessage.info(`Searching for: ${searchKeyword.value || 'all drivers'}`)
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedProtocol.value = ''
  selectedCategory.value = ''
  ElMessage.success('Filters reset')
}

const downloadDriver = (driver: any) => {
  ElMessageBox.confirm(`Download ${driver.name}?`, 'Confirm Download', {
    confirmButtonText: 'Download',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    ElMessage.success(`Downloading ${driver.name}...`)
  }).catch(() => {})
}

const viewDriverDetails = (driver: any) => {
  ElMessageBox.alert(
      `Driver: ${driver.name}\nAuthor: ${driver.author}\nVersion: ${driver.version}\nUpdated: ${driver.updated}\nDownloads: ${driver.downloads}\nRating: ${driver.rating}\n\nDescription: ${driver.description}\n\nCompatibility: ${driver.tags?.join(', ') || 'N/A'}\n\nRequirements: IBMS v2.0 or higher`,
      'Driver Details',
      { confirmButtonText: 'OK', type: 'info' }
  )
}

const uploadDriver = () => {
  ElMessage.info('Upload driver dialog opened')
}

const createDriver = () => {
  ElMessage.info('Create driver wizard started')
}

const viewMyDrivers = () => {
  ElMessage.info('Viewing my drivers')
}

const viewAllDrivers = () => {
  ElMessage.info('Viewing all drivers catalog')
}

const viewRecentDrivers = () => {
  ElMessage.info('Viewing all recently updated drivers')
}

const viewAllResources = () => {
  ElMessage.info('Viewing all development resources')
}

const viewResource = (resource: any) => {
  ElMessage.info(`Opening resource: ${resource.title}`)
}

const viewLeaderboard = () => {
  ElMessage.info('Viewing contributor leaderboard')
}

const viewContributor = (contributor: any) => {
  ElMessage.info(`Viewing contributor: ${contributor.name}`)
}

const requestDriver = () => {
  ElMessageBox.prompt('Enter driver name and protocol you need', 'Request Driver', {
    confirmButtonText: 'Submit Request',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'e.g., Mitsubishi PLC - Modbus TCP'
  }).then(({ value }) => {
    ElMessage.success(`Driver request submitted: ${value}`)
  }).catch(() => {})
}

const reportIssue = () => {
  ElMessage.info('Report issue form opened')
}

const viewDocumentation = () => {
  ElMessage.info('Opening driver documentation')
}

const joinCommunity = () => {
  ElMessage.info('Join developer community')
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
  }, 2500)
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
  font-size: 24px;
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

/* ==================== Main Content ==================== */
.driver-marketplace-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Search Card */
.search-card {
  margin-bottom: 24px;
  border-radius: 12px;
  background: white;
}

.search-section {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
}

/* Featured Banner */
.featured-banner {
  margin-bottom: 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
  border-color: #bae6fd;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px;
}

.banner-icon {
  color: #3b82f6;
}

.banner-info {
  flex: 1;
}

.banner-title {
  font-size: 12px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.banner-name {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.banner-description {
  font-size: 13px;
  color: #475569;
  margin-bottom: 12px;
  line-height: 1.4;
}

.banner-stats {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #64748b;
}

.banner-stats span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  background: white;
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

/* Categories Section */
.categories-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 16px;
}

.category-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.category-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.category-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.category-info h4 {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 2px 0;
}

.category-info p {
  font-size: 11px;
  color: #64748b;
  margin: 0;
}

.category-arrow {
  color: #cbd5e1;
  margin-left: auto;
}

/* Drivers Section */
.drivers-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.drivers-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.driver-card {
  border-radius: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.driver-card:hover {
  transform: translateY(-2px);
}

.driver-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.driver-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.driver-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.driver-description {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.4;
}

.driver-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 10px;
}

.driver-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.driver-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.driver-version {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #94a3b8;
  margin-bottom: 16px;
}

.driver-actions {
  display: flex;
  gap: 10px;
}

/* Recent Section */
.recent-section {
  margin-bottom: 32px;
}

/* Resources Section */
.resources-section {
  margin-bottom: 32px;
}

.resources-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.resource-icon {
  width: 44px;
  height: 44px;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.resource-info {
  flex: 1;
}

.resource-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.resource-description {
  font-size: 12px;
  color: #64748b;
}

/* Contributors Section */
.contributors-section {
  margin-bottom: 24px;
}

.contributors-card {
  border-radius: 12px;
  background: white;
}

.contributors-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contributor-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.contributor-rank {
  width: 32px;
  font-weight: 700;
  color: #64748b;
}

.contributor-rank.top {
  color: #f59e0b;
  font-size: 18px;
}

.contributor-avatar {
  width: 44px;
  height: 44px;
  background: #e2e8f0;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.contributor-info {
  flex: 1;
}

.contributor-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.contributor-stats {
  font-size: 11px;
  color: #64748b;
}

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .categories-grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .drivers-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .resources-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .drivers-grid {
    grid-template-columns: 1fr;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .search-section {
    flex-direction: column;
  }

  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .banner-stats {
    justify-content: center;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>