<template>
  <div class="gis-map-container">
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
            <span class="loading-title">Loading GIS Map</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Geographic Information System - Command Center</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="gis-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">GIS Map</h1>
          <p class="page-subtitle">Geographic visualization of sites, assets, and real-time incidents</p>
        </div>
        <div class="header-actions">
          <div class="time-display">
            <el-icon><Clock /></el-icon>
            <span>{{ currentTime }}</span>
          </div>
          <el-button-group>
            <el-button @click="toggleLayer('satellite')" :type="mapLayer === 'satellite' ? 'primary' : 'default'">
              Satellite
            </el-button>
            <el-button @click="toggleLayer('street')" :type="mapLayer === 'street' ? 'primary' : 'default'">
              Street
            </el-button>
            <el-button @click="toggleLayer('terrain')" :type="mapLayer === 'terrain' ? 'primary' : 'default'">
              Terrain
            </el-button>
          </el-button-group>
          <el-button @click="refreshMapData">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button @click="exportMapView">
            <el-icon><Download /></el-icon>
            Export
          </el-button>
        </div>
      </div>

      <!-- Main Map Area -->
      <div class="map-layout">
        <!-- Left Sidebar - Layers & Filters -->
        <div class="map-sidebar">
          <div class="sidebar-section">
            <div class="section-title">
              <el-icon><Search /></el-icon>
              <span>Location Search</span>
            </div>
            <el-input v-model="searchLocation" placeholder="Search address or site name..." @keyup.enter="searchMapLocation">
              <template #append>
                <el-button @click="searchMapLocation">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>

          <div class="sidebar-section">
            <div class="section-title">
              <el-icon><Filter /></el-icon>
              <span>Map Layers</span>
            </div>
            <div class="layer-list">
              <div class="layer-item">
                <el-checkbox v-model="layers.sites" @change="refreshMap">Sites & Facilities</el-checkbox>
                <span class="layer-count">{{ sitesData.length }}</span>
              </div>
              <div class="layer-item">
                <el-checkbox v-model="layers.alerts" @change="refreshMap">Active Alerts</el-checkbox>
                <span class="layer-count alert">{{ activeAlertsCount }}</span>
              </div>
              <div class="layer-item">
                <el-checkbox v-model="layers.assets" @change="refreshMap">Critical Assets</el-checkbox>
                <span class="layer-count">{{ criticalAssetsCount }}</span>
              </div>
              <div class="layer-item">
                <el-checkbox v-model="layers.incidents" @change="refreshMap">Incidents</el-checkbox>
                <span class="layer-count incident">{{ activeIncidents.length }}</span>
              </div>
              <div class="layer-item">
                <el-checkbox v-model="layers.powerGrid" @change="refreshMap">Power Grid</el-checkbox>
              </div>
              <div class="layer-item">
                <el-checkbox v-model="layers.weather" @change="refreshMap">Weather Overlay</el-checkbox>
              </div>
            </div>
          </div>

          <div class="sidebar-section">
            <div class="section-title">
              <el-icon><Filter /></el-icon>
              <span>Filter by Status</span>
            </div>
            <div class="filter-list">
              <el-radio-group v-model="statusFilter" @change="refreshMap">
                <el-radio label="all">All Sites</el-radio>
                <el-radio label="healthy">Healthy</el-radio>
                <el-radio label="warning">Warning</el-radio>
                <el-radio label="critical">Critical</el-radio>
              </el-radio-group>
            </div>
          </div>

          <div class="sidebar-section">
            <div class="section-title">
              <el-icon><DataLine /></el-icon>
              <span>Regional Summary</span>
            </div>
            <div class="regional-stats">
              <div class="region-item" v-for="region in regionStats" :key="region.name" @click="focusRegion(region)">
                <div class="region-name">{{ region.name }}</div>
                <div class="region-status">
                  <span class="status-dot" :class="region.status"></span>
                  <span>{{ region.status }}</span>
                </div>
                <div class="region-count">{{ region.count }} sites</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Center - Map View -->
        <div class="map-container">
          <div ref="mapCanvas" class="map-canvas">
            <!-- Interactive Map Simulation -->
            <div class="map-toolbar">
              <div class="zoom-controls">
                <el-button size="small" @click="zoomIn">
                  <el-icon><ZoomIn /></el-icon>
                </el-button>
                <el-button size="small" @click="zoomOut">
                  <el-icon><ZoomOut /></el-icon>
                </el-button>
                <el-button size="small" @click="resetView">
                  <el-icon><RefreshLeft /></el-icon>
                </el-button>
              </div>
              <div class="locate-btn">
                <el-button size="small" @click="locateUser">
                  <el-icon><Location /></el-icon>
                  My Location
                </el-button>
              </div>
            </div>

            <!-- Map Grid (模拟地图) -->
            <div class="map-grid" :style="{ transform: `scale(${zoom}) translate(${panX}px, ${panY}px)` }">
              <!-- 经纬度网格线 -->
              <div class="grid-lines">
                <div v-for="i in 20" :key="'h-' + i" class="grid-line horizontal" :style="{ top: (i * 5) + '%' }"></div>
                <div v-for="i in 20" :key="'v-' + i" class="grid-line vertical" :style="{ left: (i * 5) + '%' }"></div>
              </div>

              <!-- 大陆轮廓（简化） -->
              <div class="continent-outline"></div>

              <!-- 地图标记 -->
              <div v-for="site in filteredSites" :key="site.id" class="map-marker"
                   :style="{ left: site.x + '%', top: site.y + '%' }"
                   @click="selectSite(site)">
                <div class="marker-pulse" :class="site.status"></div>
                <div class="marker-icon" :class="site.status">
                  <el-icon><component :is="getSiteIcon(site.type)" /></el-icon>
                </div>
                <div class="marker-popup" v-show="selectedSiteId === site.id" @click.stop>
                  <div class="popup-header">
                    <span class="popup-title">{{ site.name }}</span>
                    <el-button link @click="closePopup">
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                  <div class="popup-content">
                    <div class="popup-row">
                      <span class="label">Location:</span>
                      <span>{{ site.location }}</span>
                    </div>
                    <div class="popup-row">
                      <span class="label">Status:</span>
                      <el-tag :type="getStatusTagType(site.status)" size="small">{{ site.status }}</el-tag>
                    </div>
                    <div class="popup-row">
                      <span class="label">Temperature:</span>
                      <span :style="{ color: getTempColor(site.temperature) }">{{ site.temperature }}°C</span>
                    </div>
                    <div class="popup-row">
                      <span class="label">Power:</span>
                      <span>{{ site.power }} kW</span>
                    </div>
                    <div class="popup-row">
                      <span class="label">Last Update:</span>
                      <span>{{ site.lastUpdate }}</span>
                    </div>
                  </div>
                  <div class="popup-actions">
                    <el-button size="small" @click="viewSiteDetails(site)">Details</el-button>
                    <el-button size="small" type="primary" @click="navigateToSite(site)">Navigate</el-button>
                  </div>
                </div>
              </div>

              <!-- 告警标记 -->
              <div v-for="alert in activeAlerts" :key="alert.id" class="alert-marker"
                   :style="{ left: alert.x + '%', top: alert.y + '%' }"
                   @click="selectAlert(alert)">
                <div class="alert-pulse" :class="alert.severity"></div>
                <div class="alert-icon" :class="alert.severity">
                  <el-icon><WarningFilled /></el-icon>
                </div>
              </div>

              <!-- 天气覆盖层 -->
              <div v-if="layers.weather" class="weather-overlay">
                <div class="weather-cell" v-for="i in 12" :key="i" :style="{ left: ((i-1)*8.33)+'%', top: '0' }">
                  <div class="weather-icon" :class="getWeatherClass(i)"></div>
                </div>
              </div>
            </div>

            <!-- Map Coordinates Display -->
            <div class="map-coordinates">
              <span>Lat: {{ currentLat.toFixed(4) }}°</span>
              <span>Lon: {{ currentLon.toFixed(4) }}°</span>
              <span>Zoom: {{ ((zoom - 0.5) * 20).toFixed(0) }}%</span>
            </div>
          </div>

          <!-- Incident Panel (右侧浮窗) -->
          <div class="incident-panel" v-if="showIncidentPanel">
            <div class="panel-header">
              <span class="panel-title">
                <el-icon><Warning /></el-icon>
                Active Incidents
              </span>
              <el-button link @click="showIncidentPanel = false">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <div class="panel-content">
              <div v-for="incident in activeIncidents" :key="incident.id" class="incident-item" @click="focusIncident(incident)">
                <div class="incident-priority" :class="incident.priority">{{ incident.priority }}</div>
                <div class="incident-info">
                  <div class="incident-title">{{ incident.title }}</div>
                  <div class="incident-location">{{ incident.location }}</div>
                </div>
                <div class="incident-time">{{ incident.time }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Sidebar - Site Details & Analytics -->
        <div class="map-sidebar-right">
          <el-tabs v-model="rightPanelTab" class="right-tabs">
            <el-tab-pane label="Site Details" name="details">
              <div v-if="selectedSite" class="site-details">
                <div class="detail-header">
                  <div class="site-status-badge" :class="selectedSite.status">
                    {{ selectedSite.status.toUpperCase() }}
                  </div>
                  <h3>{{ selectedSite.name }}</h3>
                  <p class="site-address">
                    <el-icon><Location /></el-icon>
                    {{ selectedSite.location }}
                  </p>
                </div>
                <div class="detail-section">
                  <div class="detail-title">Key Metrics</div>
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <div class="metric-mini">
                        <span class="label">Temperature</span>
                        <span class="value" :style="{ color: getTempColor(selectedSite.temperature) }">
                          {{ selectedSite.temperature }}°C
                        </span>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div class="metric-mini">
                        <span class="label">Humidity</span>
                        <span class="value">{{ selectedSite.humidity }}%</span>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div class="metric-mini">
                        <span class="label">Power Usage</span>
                        <span class="value">{{ selectedSite.power }} kW</span>
                      </div>
                    </el-col>
                    <el-col :span="12">
                      <div class="metric-mini">
                        <span class="label">Health Score</span>
                        <span class="value">{{ selectedSite.health }}%</span>
                      </div>
                    </el-col>
                  </el-row>
                </div>
                <div class="detail-section">
                  <div class="detail-title">Asset Summary</div>
                  <div class="asset-summary">
                    <div class="asset-type">
                      <span>HVAC Units</span>
                      <span>{{ selectedSite.assets?.hvac || 12 }}</span>
                    </div>
                    <div class="asset-type">
                      <span>Power Systems</span>
                      <span>{{ selectedSite.assets?.power || 8 }}</span>
                    </div>
                    <div class="asset-type">
                      <span>IT Equipment</span>
                      <span>{{ selectedSite.assets?.it || 45 }}</span>
                    </div>
                    <div class="asset-type">
                      <span>Security Devices</span>
                      <span>{{ selectedSite.assets?.security || 24 }}</span>
                    </div>
                  </div>
                </div>
                <div class="detail-section">
                  <div class="detail-title">Recent Alerts</div>
                  <div class="recent-alerts">
                    <div v-for="alert in selectedSite.recentAlerts" :key="alert.id" class="recent-alert">
                      <span class="alert-time">{{ alert.time }}</span>
                      <span class="alert-msg">{{ alert.message }}</span>
                    </div>
                  </div>
                </div>
                <div class="detail-actions">
                  <el-button type="primary" size="small" @click="viewSiteDashboard(selectedSite)">View Dashboard</el-button>
                  <el-button size="small" @click="scheduleSiteVisit(selectedSite)">Schedule Visit</el-button>
                </div>
              </div>
              <div v-else class="no-selection">
                <el-icon><Location /></el-icon>
                <p>Select a site on the map to view details</p>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Route Planning" name="route">
              <div class="route-planning">
                <div class="route-input">
                  <el-input v-model="routeOrigin" placeholder="Origin" prefix-icon="Location">
                    <template #append>
                      <el-button @click="useCurrentLocation">Use My Location</el-button>
                    </template>
                  </el-input>
                  <el-input v-model="routeDestination" placeholder="Destination" prefix-icon="Flag">
                    <template #append>
                      <el-button @click="useSelectedSite">Use Selected Site</el-button>
                    </template>
                  </el-input>
                  <el-button type="primary" style="width: 100%" @click="planRoute">
                    <el-icon><Van /></el-icon>
                    Plan Route
                  </el-button>
                </div>
                <div v-if="routeInfo" class="route-info">
                  <div class="route-summary">
                    <div class="route-stat">
                      <span class="stat-label">Distance</span>
                      <span class="stat-value">{{ routeInfo.distance }}</span>
                    </div>
                    <div class="route-stat">
                      <span class="stat-label">Duration</span>
                      <span class="stat-value">{{ routeInfo.duration }}</span>
                    </div>
                    <div class="route-stat">
                      <span class="stat-label">Traffic</span>
                      <span class="stat-value" :class="routeInfo.trafficClass">{{ routeInfo.traffic }}</span>
                    </div>
                  </div>
                  <div class="route-steps">
                    <div v-for="(step, idx) in routeInfo.steps" :key="idx" class="route-step">
                      <div class="step-icon">{{ idx + 1 }}</div>
                      <div class="step-text">{{ step }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Heat Map" name="heatmap">
              <div class="heatmap-container">
                <div ref="heatmapChartRef" class="heatmap-chart"></div>
                <div class="heatmap-legend">
                  <div class="legend-item">
                    <span class="legend-color" style="background: #10b981"></span>
                    <span>Low Activity</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background: #f59e0b"></span>
                    <span>Medium Activity</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background: #ef4444"></span>
                    <span>High Activity</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Resources" name="resources">
              <div class="resource-list">
                <div v-for="resource in nearbyResources" :key="resource.id" class="resource-item">
                  <div class="resource-icon" :style="{ background: resource.color }">
                    <el-icon><component :is="resource.icon" /></el-icon>
                  </div>
                  <div class="resource-info">
                    <div class="resource-name">{{ resource.name }}</div>
                    <div class="resource-location">{{ resource.distance }} away</div>
                  </div>
                  <div class="resource-status" :class="resource.status">{{ resource.status }}</div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>

    <!-- Site Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="detailSite?.name" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Location">{{ detailSite?.location }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(detailSite?.status)">{{ detailSite?.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Coordinates">{{ detailSite?.coordinates }}</el-descriptions-item>
        <el-descriptions-item label="Timezone">{{ detailSite?.timezone }}</el-descriptions-item>
        <el-descriptions-item label="Contact Person">{{ detailSite?.contact }}</el-descriptions-item>
        <el-descriptions-item label="Phone">{{ detailSite?.phone }}</el-descriptions-item>
        <el-descriptions-item label="Emergency Plan" :span="2">
          <el-button link>View Emergency Response Plan</el-button>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="navigateToSite(detailSite)">Navigate</el-button>
        <el-button @click="callSiteContact(detailSite)">Call Contact</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Clock, Refresh, Download, Search, Filter, DataLine,
  ZoomIn, ZoomOut, RefreshLeft, Location, Close, WarningFilled,
  Warning, Van, Flag, User, Phone, HomeFilled, OfficeBuilding, ShoppingCart, School, Check, Bell, Setting
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading GIS data...')

// ==================== Time ====================
const currentTime = ref('')
let timeInterval: ReturnType<typeof setInterval> | null = null

// ==================== Map State ====================
const mapLayer = ref('satellite')
const zoom = ref(1)
const panX = ref(0)
const panY = ref(0)
const currentLat = ref(1.3521)
const currentLon = ref(103.8198)
const searchLocation = ref('')
const statusFilter = ref('all')
const selectedSiteId = ref<number | null>(null)
const showIncidentPanel = ref(true)
const rightPanelTab = ref('details')
const selectedSite = ref<any>(null)
const detailDialogVisible = ref(false)
const detailSite = ref<any>(null)

// Route Planning
const routeOrigin = ref('')
const routeDestination = ref('')
const routeInfo = ref<any>(null)

// Map Layers
const layers = ref({
  sites: true,
  alerts: true,
  assets: true,
  incidents: true,
  powerGrid: false,
  weather: false
})

// ==================== Data ====================
// Sites Data with map coordinates (percentage positions)
const sitesData = ref([
  { id: 1, name: 'Singapore DC East', location: 'Singapore, SG', type: 'datacenter', status: 'healthy', temperature: 24.2, humidity: 48, power: 1250, health: 96, x: 35, y: 55, lastUpdate: '2 min ago', coordinates: '1.3521° N, 103.8198° E', timezone: 'UTC+8', contact: 'John Tan', phone: '+65 9123 4567', assets: { hvac: 12, power: 8, it: 120, security: 24 }, recentAlerts: [{ id: 1, time: '1h ago', message: 'Temperature stable' }] },
  { id: 2, name: 'Singapore DC West', location: 'Singapore, SG', type: 'datacenter', status: 'warning', temperature: 26.8, humidity: 52, power: 980, health: 82, x: 28, y: 52, lastUpdate: '5 min ago', coordinates: '1.3120° N, 103.7650° E', timezone: 'UTC+8', contact: 'Mary Lim', phone: '+65 9234 5678', assets: { hvac: 8, power: 6, it: 85, security: 18 }, recentAlerts: [{ id: 1, time: '30m ago', message: 'High temperature warning' }] },
  { id: 3, name: 'Kuala Lumpur HQ', location: 'Kuala Lumpur, MY', type: 'office', status: 'healthy', temperature: 25.1, humidity: 55, power: 450, health: 94, x: 45, y: 68, lastUpdate: '3 min ago', coordinates: '3.1390° N, 101.6869° E', timezone: 'UTC+8', contact: 'Ahmad Razak', phone: '+60 12 345 6789', assets: { hvac: 6, power: 4, it: 45, security: 12 }, recentAlerts: [] },
  { id: 4, name: 'Bangkok Facility', location: 'Bangkok, TH', type: 'factory', status: 'critical', temperature: 29.5, humidity: 65, power: 320, health: 68, x: 58, y: 75, lastUpdate: '10 min ago', coordinates: '13.7367° N, 100.5231° E', timezone: 'UTC+7', contact: 'Somchai Thong', phone: '+66 81 234 5678', assets: { hvac: 4, power: 3, it: 12, security: 8 }, recentAlerts: [{ id: 1, time: '15m ago', message: 'Critical temperature alert' }] },
  { id: 5, name: 'Jakarta Data Center', location: 'Jakarta, ID', type: 'datacenter', status: 'warning', temperature: 27.3, humidity: 58, power: 1100, health: 78, x: 52, y: 82, lastUpdate: '7 min ago', coordinates: '6.2088° S, 106.8456° E', timezone: 'UTC+7', contact: 'Budi Santoso', phone: '+62 812 3456 7890', assets: { hvac: 10, power: 7, it: 95, security: 20 }, recentAlerts: [{ id: 1, time: '1h ago', message: 'Power fluctuation detected' }] },
  { id: 6, name: 'Manila Office', location: 'Manila, PH', type: 'office', status: 'healthy', temperature: 26.0, humidity: 62, power: 280, health: 92, x: 62, y: 78, lastUpdate: '4 min ago', coordinates: '14.5995° N, 120.9842° E', timezone: 'UTC+8', contact: 'Maria Santos', phone: '+63 912 345 6789', assets: { hvac: 3, power: 2, it: 28, security: 6 }, recentAlerts: [] },
  { id: 7, name: 'Ho Chi Minh Site', location: 'Ho Chi Minh City, VN', type: 'factory', status: 'warning', temperature: 28.1, humidity: 70, power: 380, health: 74, x: 55, y: 85, lastUpdate: '8 min ago', coordinates: '10.8231° N, 106.6297° E', timezone: 'UTC+7', contact: 'Nguyen Van An', phone: '+84 912 345 678', assets: { hvac: 5, power: 3, it: 18, security: 10 }, recentAlerts: [{ id: 1, time: '2h ago', message: 'High humidity alert' }] },
  { id: 8, name: 'Taipei Data Center', location: 'Taipei, TW', type: 'datacenter', status: 'healthy', temperature: 23.5, humidity: 45, power: 890, health: 95, x: 68, y: 62, lastUpdate: '6 min ago', coordinates: '25.0330° N, 121.5654° E', timezone: 'UTC+8', contact: 'Wei Chen', phone: '+886 912 345 678', assets: { hvac: 7, power: 5, it: 72, security: 16 }, recentAlerts: [] },
  { id: 9, name: 'Hong Kong DR Site', location: 'Hong Kong, HK', type: 'datacenter', status: 'critical', temperature: 30.2, humidity: 72, power: 560, health: 58, x: 62, y: 58, lastUpdate: '12 min ago', coordinates: '22.3193° N, 114.1694° E', timezone: 'UTC+8', contact: 'Eric Wong', phone: '+852 9123 4567', assets: { hvac: 4, power: 3, it: 35, security: 8 }, recentAlerts: [{ id: 1, time: '5m ago', message: 'Cooling system failure' }] }
])

// Active Alerts
const activeAlerts = ref([
  { id: 1, title: 'Cooling Failure', location: 'Hong Kong DR Site', severity: 'critical', x: 62, y: 58, time: '5 min ago' },
  { id: 2, title: 'High Temperature', location: 'Bangkok Facility', severity: 'critical', x: 58, y: 75, time: '15 min ago' },
  { id: 3, title: 'Power Fluctuation', location: 'Jakarta Data Center', severity: 'warning', x: 52, y: 82, time: '1 hour ago' },
  { id: 4, title: 'Humidity Alert', location: 'Ho Chi Minh Site', severity: 'warning', x: 55, y: 85, time: '2 hours ago' }
])

// Active Incidents
const activeIncidents = ref([
  { id: 1, title: 'Cooling System Failure', location: 'Hong Kong DR Site', priority: 'critical', time: '5 min ago', x: 62, y: 58 },
  { id: 2, title: 'High Temperature Alert', location: 'Bangkok Facility', priority: 'critical', time: '15 min ago', x: 58, y: 75 },
  { id: 3, title: 'Power Quality Issue', location: 'Jakarta Data Center', priority: 'high', time: '1 hour ago', x: 52, y: 82 }
])

// Region Stats
const regionStats = ref([
  { name: 'Southeast Asia', status: 'warning', count: 7 },
  { name: 'East Asia', status: 'critical', count: 2 },
  { name: 'South Asia', status: 'healthy', count: 1 }
])

// Nearby Resources
const nearbyResources = ref([
  { id: 1, name: 'Emergency Response Team', distance: '2 km', status: 'available', color: '#10b981', icon: 'User' },
  { id: 2, name: 'Mobile Generator', distance: '5 km', status: 'dispatched', color: '#f59e0b', icon: 'Setting' },
  { id: 3, name: 'HVAC Specialist', distance: '8 km', status: 'available', color: '#10b981', icon: 'User' },
  { id: 4, name: 'Fire Rescue Unit', distance: '12 km', status: 'en-route', color: '#3b82f6', icon: 'Van' }
])

// Computed
const filteredSites = computed(() => {
  let result = sitesData.value
  if (statusFilter.value !== 'all') {
    result = result.filter(s => s.status === statusFilter.value)
  }
  if (!layers.value.sites) return []
  return result
})

const activeAlertsCount = computed(() => activeAlerts.value.length)
const criticalAssetsCount = computed(() => sitesData.value.filter(s => s.status === 'critical').length)

// Helper Functions
const getSiteIcon = (type: string) => {
  const icons: Record<string, any> = {
    datacenter: 'Monitor',
    office: 'OfficeBuilding',
    factory: 'Factory',
    hospital: 'Hospital',
    school: 'School',
    shopping: 'ShoppingCart'
  }
  return icons[type] || 'HomeFilled'
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    healthy: 'success',
    warning: 'warning',
    critical: 'danger'
  }
  return types[status] || 'info'
}

const getTempColor = (temp: number) => {
  if (temp < 25) return '#10b981'
  if (temp < 28) return '#f59e0b'
  return '#ef4444'
}

const getWeatherClass = (i: number) => {
  const weathers = ['sunny', 'cloudy', 'rainy', 'storm']
  return weathers[i % 4]
}

// Map Actions
const toggleLayer = (layer: string) => {
  mapLayer.value = layer
  ElMessage.info(`${layer} map view enabled`)
}

const refreshMapData = () => {
  ElMessage.success('Map data refreshed')
}

const exportMapView = () => {
  ElMessage.success('Map view exported')
}

const searchMapLocation = () => {
  if (searchLocation.value) {
    ElMessage.info(`Searching for: ${searchLocation.value}`)
    // Simulate search - move map to random location
    currentLat.value = 1.3521 + (Math.random() - 0.5) * 10
    currentLon.value = 103.8198 + (Math.random() - 0.5) * 10
  }
}

const refreshMap = () => {
  // Refresh map layers
  ElMessage.info('Map layers updated')
}

const zoomIn = () => {
  zoom.value = Math.min(zoom.value + 0.1, 2)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value - 0.1, 0.5)
}

const resetView = () => {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
  currentLat.value = 1.3521
  currentLon.value = 103.8198
}

const locateUser = () => {
  ElMessage.info('Locating your position...')
  setTimeout(() => {
    ElMessage.success('Location found')
  }, 1000)
}

const selectSite = (site: any) => {
  selectedSiteId.value = site.id
  selectedSite.value = site
  rightPanelTab.value = 'details'
}

const closePopup = () => {
  selectedSiteId.value = null
}

const selectAlert = (alert: any) => {
  ElMessage.warning(`Alert: ${alert.title} at ${alert.location}`)
}

const focusRegion = (region: any) => {
  ElMessage.info(`Focusing on ${region.name}`)
}

const focusIncident = (incident: any) => {
  ElMessage.warning(`Focusing on incident: ${incident.title}`)
}

const viewSiteDetails = (site: any) => {
  detailSite.value = site
  detailDialogVisible.value = true
}

const navigateToSite = (site: any) => {
  ElMessage.info(`Navigation started to ${site.name}`)
  routeOrigin.value = 'Current Location'
  routeDestination.value = site.name
  planRoute()
}

const viewSiteDashboard = (site: any) => {
  ElMessage.info(`Opening dashboard for ${site.name}`)
}

const scheduleSiteVisit = (site: any) => {
  ElMessage.info(`Scheduling visit to ${site.name}`)
}

const callSiteContact = (site: any) => {
  ElMessage.info(`Calling ${site.contact} at ${site.phone}`)
}

// Route Planning
const useCurrentLocation = () => {
  routeOrigin.value = 'Current Location'
}

const useSelectedSite = () => {
  if (selectedSite.value) {
    routeDestination.value = selectedSite.value.name
  } else {
    ElMessage.warning('Please select a site first')
  }
}

const planRoute = () => {
  if (!routeOrigin.value || !routeDestination.value) {
    ElMessage.warning('Please enter origin and destination')
    return
  }
  routeInfo.value = {
    distance: `${(Math.random() * 50 + 5).toFixed(1)} km`,
    duration: `${Math.floor(Math.random() * 60 + 15)} min`,
    traffic: ['Light', 'Moderate', 'Heavy'][Math.floor(Math.random() * 3)],
    trafficClass: ['light', 'moderate', 'heavy'][Math.floor(Math.random() * 3)],
    steps: [
      'Start from ' + routeOrigin.value,
      'Take AYE towards city center',
      'Exit at junction 15',
      'Continue straight for 2 km',
      'Arrive at ' + routeDestination.value
    ]
  }
  ElMessage.success('Route planned successfully')
}

// ==================== Chart ====================
let heatmapChart: echarts.ECharts | null = null
const heatmapChartRef = ref<HTMLElement | null>(null)

const initHeatmapChart = () => {
  if (!heatmapChartRef.value) return
  if (heatmapChart) heatmapChart.dispose()
  heatmapChart = echarts.init(heatmapChartRef.value)

  const hours = ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const data: number[][] = []

  for (let i = 0; i < days.length; i++) {
    for (let j = 0; j < hours.length; j++) {
      data.push([j, i, Math.floor(Math.random() * 100)])
    }
  }

  heatmapChart.setOption({
    tooltip: { position: 'top' },
    xAxis: { type: 'category', data: hours, name: 'Time', axisLabel: { rotate: 45 } },
    yAxis: { type: 'category', data: days, name: 'Day' },
    visualMap: { min: 0, max: 100, calculable: true, inRange: { color: ['#10b981', '#f59e0b', '#ef4444'] } },
    series: [{ type: 'heatmap', data: data, label: { show: false }, emphasis: { scale: true } }]
  })
}

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Simulate real-time updates
let dataInterval: ReturnType<typeof setInterval> | null = null

const startDataSimulation = () => {
  dataInterval = setInterval(() => {
    // Randomly update site data
    sitesData.value.forEach(site => {
      if (Math.random() > 0.8) {
        site.temperature = +(site.temperature + (Math.random() - 0.5) * 0.5).toFixed(1)
        site.humidity = Math.min(100, Math.max(30, site.humidity + (Math.random() - 0.5) * 2))
        site.lastUpdate = 'Just now'
      }
    })
  }, 10000)
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (heatmapChart) heatmapChart.resize()
  }, 200)
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)

  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initHeatmapChart()
          startDataSimulation()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  if (heatmapChart) heatmapChart.dispose()
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.gis-map-container {
  min-height: 100vh;
  background: #f0f2f6;
}

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

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
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
  width: 320px;
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
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
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
.gis-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 12px;
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

/* Map Layout */
.map-layout {
  display: flex;
  gap: 20px;
}

/* Left Sidebar */
.map-sidebar {
  width: 280px;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
  max-height: calc(100vh - 140px);
}

.sidebar-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-section:last-child {
  border-bottom: none;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.layer-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.layer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.layer-count {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  background: #f1f5f9;
  color: #64748b;
}

.layer-count.alert { background: #fef2f2; color: #ef4444; }
.layer-count.incident { background: #fef2f2; color: #ef4444; }

.filter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.regional-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.region-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.region-item:hover {
  background: #f1f5f9;
}

.region-name {
  font-weight: 500;
  font-size: 14px;
  color: #1e293b;
}

.region-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.healthy { background: #10b981; }
.status-dot.warning { background: #f59e0b; }
.status-dot.critical { background: #ef4444; }

.region-count {
  font-size: 12px;
  color: #64748b;
}

/* Map Container */
.map-container {
  flex: 1;
  position: relative;
}

.map-canvas {
  background: #1a1a2e;
  border-radius: 20px;
  overflow: hidden;
  position: relative;
  height: calc(100vh - 140px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.map-toolbar {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  display: flex;
  gap: 8px;
}

.zoom-controls {
  display: flex;
  gap: 4px;
  background: white;
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.locate-btn {
  background: white;
  border-radius: 12px;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.map-grid {
  width: 100%;
  height: 100%;
  position: relative;
  transition: transform 0.2s ease;
}

.grid-lines {
  position: absolute;
  width: 100%;
  height: 100%;
}

.grid-line {
  position: absolute;
  background: rgba(59, 130, 246, 0.1);
}

.grid-line.horizontal {
  width: 100%;
  height: 1px;
}

.grid-line.vertical {
  height: 100%;
  width: 1px;
}

.continent-outline {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at 50% 60%, rgba(16, 185, 129, 0.05) 0%, transparent 70%);
}

/* Map Markers */
.map-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 5;
}

.marker-pulse {
  position: absolute;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: markerPulse 1.5s infinite;
  z-index: 1;
}

.marker-pulse.healthy { background: rgba(16, 185, 129, 0.3); }
.marker-pulse.warning { background: rgba(245, 158, 11, 0.3); }
.marker-pulse.critical { background: rgba(239, 68, 68, 0.3); }

@keyframes markerPulse {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.marker-icon {
  position: relative;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.marker-icon.healthy { background: #10b981; }
.marker-icon.warning { background: #f59e0b; }
.marker-icon.critical { background: #ef4444; }

.marker-popup {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  width: 240px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
  z-index: 20;
  animation: popupFadeIn 0.2s ease;
}

@keyframes popupFadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(10px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.popup-title {
  font-weight: 600;
  color: #1e293b;
}

.popup-content {
  padding: 12px 16px;
}

.popup-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.popup-row .label {
  color: #64748b;
}

.popup-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e2e8f0;
}

/* Alert Markers */
.alert-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 6;
}

.alert-pulse {
  position: absolute;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: alertPulse 1s infinite;
}

.alert-pulse.critical { background: rgba(239, 68, 68, 0.4); }
.alert-pulse.warning { background: rgba(245, 158, 11, 0.4); }

@keyframes alertPulse {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.8); opacity: 0; }
}

.alert-icon {
  position: relative;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  z-index: 2;
  animation: alertShake 0.5s infinite;
}

.alert-icon.critical { background: #ef4444; }
.alert-icon.warning { background: #f59e0b; }

@keyframes alertShake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

/* Weather Overlay */
.weather-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 3;
}

.weather-cell {
  position: absolute;
  width: 8.33%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.weather-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  opacity: 0.3;
}

.weather-icon.sunny { background: #f59e0b; box-shadow: 0 0 10px #f59e0b; }
.weather-icon.cloudy { background: #94a3b8; }
.weather-icon.rainy { background: #3b82f6; }
.weather-icon.storm { background: #8b5cf6; }

/* Map Coordinates */
.map-coordinates {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  color: white;
  display: flex;
  gap: 12px;
  z-index: 10;
}

/* Incident Panel */
.incident-panel {
  position: absolute;
  top: 16px;
  left: 16px;
  width: 280px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
  z-index: 10;
  overflow: hidden;
}

.incident-panel .panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fef2f2;
  border-bottom: 1px solid #fee2e2;
}

.incident-panel .panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #dc2626;
}

.panel-content {
  max-height: 300px;
  overflow-y: auto;
}

.incident-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.incident-item:hover {
  background: #f8fafc;
}

.incident-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.incident-priority.critical { background: #fef2f2; color: #ef4444; }
.incident-priority.high { background: #fffbeb; color: #f59e0b; }

.incident-info {
  flex: 1;
}

.incident-title {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.incident-location {
  font-size: 11px;
  color: #64748b;
}

.incident-time {
  font-size: 10px;
  color: #94a3b8;
}

/* Right Sidebar */
.map-sidebar-right {
  width: 320px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 140px);
}

.right-tabs {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.right-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 16px;
  border-bottom: 1px solid #e2e8f0;
}

.right-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

/* Site Details */
.site-details {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-header {
  text-align: center;
}

.site-status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 12px;
}

.site-status-badge.healthy { background: #ecfdf5; color: #10b981; }
.site-status-badge.warning { background: #fffbeb; color: #f59e0b; }
.site-status-badge.critical { background: #fef2f2; color: #ef4444; }

.detail-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1e293b;
}

.site-address {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  font-size: 12px;
  color: #64748b;
}

.detail-section {
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
}

.detail-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.metric-mini {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  text-align: center;
  margin-bottom: 12px;
}

.metric-mini .label {
  display: block;
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-mini .value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.asset-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.asset-type {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.recent-alerts {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-alert {
  display: flex;
  gap: 8px;
  font-size: 12px;
  padding: 8px;
  background: #f8fafc;
  border-radius: 8px;
}

.recent-alert .alert-time {
  color: #64748b;
}

.recent-alert .alert-msg {
  color: #1e293b;
}

.detail-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
}

.no-selection {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
}

.no-selection .el-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

/* Route Planning */
.route-planning {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.route-input {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-info {
  border-top: 1px solid #e2e8f0;
  padding-top: 16px;
}

.route-summary {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.route-stat {
  text-align: center;
}

.route-stat .stat-label {
  display: block;
  font-size: 11px;
  color: #64748b;
}

.route-stat .stat-value {
  display: block;
  font-size: 16px;
  font-weight: 700;
  color: #1e293b;
}

.route-stat .stat-value.light { color: #10b981; }
.route-stat .stat-value.moderate { color: #f59e0b; }
.route-stat .stat-value.heavy { color: #ef4444; }

.route-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.route-step {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.step-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
}

.step-text {
  flex: 1;
  color: #475569;
}

/* Heatmap */
.heatmap-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.heatmap-chart {
  height: 300px;
  width: 100%;
}

.heatmap-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
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

/* Resources */
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.resource-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.resource-info {
  flex: 1;
}

.resource-name {
  font-weight: 500;
  font-size: 14px;
  color: #1e293b;
}

.resource-location {
  font-size: 11px;
  color: #64748b;
}

.resource-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
}

.resource-status.available { background: #d1fae5; color: #10b981; }
.resource-status.dispatched { background: #fef3c7; color: #f59e0b; }
.resource-status.en-route { background: #dbeafe; color: #3b82f6; }

/* Responsive */
@media (max-width: 1200px) {
  .gis-main { padding: 16px; }
  .map-sidebar { width: 240px; }
  .map-sidebar-right { width: 280px; }
}

@media (max-width: 900px) {
  .map-layout { flex-direction: column; }
  .map-sidebar, .map-sidebar-right { width: 100%; max-height: none; }
  .map-canvas { height: 500px; }
}
</style>