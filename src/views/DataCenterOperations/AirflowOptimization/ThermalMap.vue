<template>
  <div class="thermal-map-container">
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
            <span class="loading-title">Loading Thermal Map</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Data Center Temperature Visualization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Thermal Map</span>
          <el-tag type="danger" effect="dark" size="large">Real-Time Temperature Visualization</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Temperature /></el-icon>
                <span>Average Temperature</span>
              </div>
              <div class="card-value">22.8°C</div>
              <div class="card-footer">
                <el-progress :percentage="75" :stroke-width="8" status="success" :format="() => 'Target: 24°C'" />
                <span class="status-text">ASHRAE Compliant</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Warning /></el-icon>
                <span>Hotspots Detected</span>
              </div>
              <div class="card-value">3</div>
              <div class="card-footer">
                <el-progress :percentage="80" :stroke-width="8" status="warning" :format="() => 'Resolved: 12'" />
                <span class="status-text">Active Monitoring</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Temp Range</span>
              </div>
              <div class="card-value">18-26°C</div>
              <div class="card-footer">
                <el-progress :percentage="88" :stroke-width="8" status="success" />
                <span class="status-text">Within Spec</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Sensor Network</span>
              </div>
              <div class="card-value">156</div>
              <div class="card-footer">
                <el-progress :percentage="98" :stroke-width="8" status="success" />
                <span class="status-text">Active Sensors</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Main Thermal Map -->
      <div class="thermal-map-section">
        <el-card class="map-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Grid /></el-icon>
            <span>Data Hall Thermal Map</span>
            <div class="header-actions">
              <el-radio-group v-model="mapLayer" size="small">
                <el-radio-button label="temperature">Temperature</el-radio-button>
                <el-radio-button label="humidity">Humidity</el-radio-button>
                <el-radio-button label="airflow">Airflow</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="zoomInMap">Zoom In</el-button>
              <el-button size="small" @click="zoomOutMap">Zoom Out</el-button>
              <el-button size="small" type="primary" @click="refreshMap">Refresh</el-button>
            </div>
          </div>
          <div class="map-container">
            <div ref="thermalMapChartRef" style="height: 550px"></div>
          </div>
          <div class="map-legend">
            <span class="legend-title">Temperature Scale:</span>
            <span class="legend-color" style="background: #3b82f6"></span>
            <span>&lt;18°C</span>
            <span class="legend-color" style="background: #10b981"></span>
            <span>18-20°C</span>
            <span class="legend-color" style="background: #84cc16"></span>
            <span>20-22°C</span>
            <span class="legend-color" style="background: #f59e0b"></span>
            <span>22-24°C</span>
            <span class="legend-color" style="background: #ef4444"></span>
            <span>24-26°C</span>
            <span class="legend-color" style="background: #7c2d12"></span>
            <span>&gt;26°C</span>
          </div>
        </el-card>
      </div>

      <!-- Rack Temperature Grid -->
      <div class="rack-grid-section">
        <div class="section-header">
          <h3>Rack Temperature Grid</h3>
          <div class="header-controls">
            <el-radio-group v-model="rackView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <div v-if="rackView === 'grid'">
          <div class="rack-grid">
            <div v-for="row in rackRows" :key="row.name" class="rack-row">
              <div class="row-label">{{ row.name }}</div>
              <div class="row-racks">
                <div
                    v-for="rack in row.racks"
                    :key="rack.id"
                    class="rack-cell"
                    :style="{ backgroundColor: getTemperatureColor(rack.temperature) }"
                    @click="showRackDetails(rack)"
                >
                  <div class="rack-id">{{ rack.id }}</div>
                  <div class="rack-temp">{{ rack.temperature }}°C</div>
                  <div class="rack-status" :class="getStatusClass(rack.temperature)"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <el-table :data="rackTableData" border v-else style="width: 100%">
          <el-table-column prop="id" label="Rack ID" width="100" />
          <el-table-column prop="row" label="Row" width="80" />
          <el-table-column prop="temperature" label="Temperature (°C)" width="150">
            <template #default="{ row }">
              <span :style="{ color: getTemperatureTextColor(row.temperature) }">
                {{ row.temperature }}°C
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.temperature)" size="small">
                {{ getStatusText(row.temperature) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="load" label="IT Load (kW)" width="120" />
          <el-table-column prop="airflow" label="Airflow (CFM)" width="120" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="showRackDetails(row)">Details</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Temperature Trends Tab -->
          <el-tab-pane label="Temperature Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Temperature History & Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="tempTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="tempDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Hotspot Analysis Tab -->
          <el-tab-pane label="Hotspot Analysis" name="hotspots">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Hotspot Detection & Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="hotspotData" border style="width: 100%">
                    <el-table-column prop="location" label="Location" width="120" />
                    <el-table-column prop="rack" label="Rack" width="80" />
                    <el-table-column prop="temperature" label="Temperature" width="100">
                      <template #default="{ row }">
                        <span style="color: #ef4444; font-weight: 600;">{{ row.temperature }}°C</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.severity === 'Critical' ? 'danger' : 'warning'" size="small">
                          {{ row.severity }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="duration" label="Duration" width="100" />
                    <el-table-column prop="status" label="Status" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'Resolved' ? 'success' : 'danger'" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="hotspot-summary">
                    <h4>Hotspot Statistics</h4>
                    <div class="stat-circle">
                      <el-progress type="dashboard" :percentage="80" :width="140" :stroke-width="10" color="#ef4444">
                        <template #default>
                          <span class="percentage-value">3</span>
                          <span class="percentage-label">Active</span>
                        </template>
                      </el-progress>
                    </div>
                    <div class="stat-details">
                      <div class="stat-item">
                        <span>Total Detected:</span>
                        <strong>15</strong>
                      </div>
                      <div class="stat-item">
                        <span>Resolved:</span>
                        <strong>12</strong>
                      </div>
                      <div class="stat-item">
                        <span>Avg Resolution Time:</span>
                        <strong>2.5 hours</strong>
                      </div>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="runHotspotAnalysis">
                      Run Hotspot Analysis
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Sensor Network Tab -->
          <el-tab-pane label="Sensor Network" name="sensors">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Connection /></el-icon>
                <span>Sensor Network Status</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="sensorMapChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <el-table :data="sensorData" border>
                    <el-table-column prop="zone" label="Zone" width="100" />
                    <el-table-column prop="total" label="Total Sensors" width="100" />
                    <el-table-column prop="active" label="Active" width="80">
                      <template #default="{ row }">
                        <el-tag type="success" size="small">{{ row.active }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="warning" label="Warning" width="80">
                      <template #default="{ row }">
                        <el-tag type="warning" size="small">{{ row.warning }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="offline" label="Offline" width="80">
                      <template #default="{ row }">
                        <el-tag type="info" size="small">{{ row.offline }}</el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Cross-Section Analysis Tab -->
          <el-tab-pane label="Cross-Section Analysis" name="crosssection">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Menu /></el-icon>
                <span>Vertical Temperature Profile</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="verticalProfileChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="horizontalProfileChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Historical Comparison Tab -->
          <el-tab-pane label="Historical Comparison" name="historical">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>Historical Temperature Comparison</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="monthlyComparisonChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="yearlyTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Reports Tab -->
          <el-tab-pane label="Reports" name="reports">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>Thermal Reports</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8" v-for="report in thermalReports" :key="report.id">
                  <div class="report-card" @click="downloadReport(report)">
                    <el-icon :size="40"><component :is="report.icon" /></el-icon>
                    <h4>{{ report.title }}</h4>
                    <p>{{ report.description }}</p>
                    <div class="report-meta">
                      <span>{{ report.date }}</span>
                      <el-tag size="small">{{ report.format }}</el-tag>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="exportThermalMap">
          <el-icon><Download /></el-icon>
          Export Thermal Map
        </el-button>
        <el-button size="large" @click="scheduleAnalysis">
          <el-icon><Calendar /></el-icon>
          Schedule Analysis
        </el-button>
        <el-button size="large" @click="generateReport">
          <el-icon><Document /></el-icon>
          Generate Report
        </el-button>
      </div>
    </template>

    <!-- Rack Details Dialog -->
    <el-dialog v-model="rackDialogVisible" :title="`Rack ${selectedRack?.id} Details`" width="500px">
      <el-descriptions :column="2" border v-if="selectedRack">
        <el-descriptions-item label="Location">Row {{ selectedRack.row }}, Position {{ selectedRack.id }}</el-descriptions-item>
        <el-descriptions-item label="Temperature">
          <span :style="{ color: getTemperatureTextColor(selectedRack.temperature), fontWeight: 'bold' }">
            {{ selectedRack.temperature }}°C
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusTagType(selectedRack.temperature)" size="small">
            {{ getStatusText(selectedRack.temperature) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="IT Load">{{ selectedRack.load || 'N/A' }} kW</el-descriptions-item>
        <el-descriptions-item label="Airflow">{{ selectedRack.airflow || 'N/A' }} CFM</el-descriptions-item>
        <el-descriptions-item label="Sensor ID">T-{{ selectedRack.id }}-001</el-descriptions-item>
        <el-descriptions-item label="Last Updated">2024-12-18 14:30:00</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="rackDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="investigateRack">Investigate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading thermal map data...')

const loadingMessages = [
  'Loading thermal map data...',
  'Processing sensor readings...',
  'Analyzing temperature distribution...',
  'Detecting hotspots...',
  'Rendering heat map...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('trends')
const mapLayer = ref('temperature')
const rackView = ref('grid')
const rackDialogVisible = ref(false)
const selectedRack = ref<any>(null)

// Rack rows data
const rackRows = ref([
  { name: 'Row A', racks: [
      { id: 'A01', temperature: 22.5, row: 'A', load: 8.5, airflow: 850 },
      { id: 'A02', temperature: 23.1, row: 'A', load: 9.2, airflow: 820 },
      { id: 'A03', temperature: 24.5, row: 'A', load: 10.5, airflow: 780 },
      { id: 'A04', temperature: 25.2, row: 'A', load: 11.2, airflow: 750 },
      { id: 'A05', temperature: 23.8, row: 'A', load: 9.8, airflow: 800 }
    ]},
  { name: 'Row B', racks: [
      { id: 'B01', temperature: 21.8, row: 'B', load: 7.5, airflow: 900 },
      { id: 'B02', temperature: 22.2, row: 'B', load: 8.2, airflow: 880 },
      { id: 'B03', temperature: 26.5, row: 'B', load: 12.5, airflow: 700 },
      { id: 'B04', temperature: 24.8, row: 'B', load: 10.8, airflow: 760 },
      { id: 'B05', temperature: 23.2, row: 'B', load: 9.2, airflow: 810 }
    ]},
  { name: 'Row C', racks: [
      { id: 'C01', temperature: 20.5, row: 'C', load: 6.5, airflow: 950 },
      { id: 'C02', temperature: 21.2, row: 'C', load: 7.2, airflow: 920 },
      { id: 'C03', temperature: 22.5, row: 'C', load: 8.5, airflow: 880 },
      { id: 'C04', temperature: 23.1, row: 'C', load: 9.0, airflow: 850 },
      { id: 'C05', temperature: 22.8, row: 'C', load: 8.8, airflow: 860 }
    ]},
  { name: 'Row D', racks: [
      { id: 'D01', temperature: 21.5, row: 'D', load: 7.0, airflow: 910 },
      { id: 'D02', temperature: 22.0, row: 'D', load: 7.8, airflow: 890 },
      { id: 'D03', temperature: 23.5, row: 'D', load: 9.2, airflow: 840 },
      { id: 'D04', temperature: 24.2, row: 'D', load: 10.2, airflow: 790 },
      { id: 'D05', temperature: 23.8, row: 'D', load: 9.5, airflow: 820 }
    ]}
])

// Rack table data
const rackTableData = ref([
  { id: 'A01', row: 'A', temperature: 22.5, status: 'Normal', load: 8.5, airflow: 850 },
  { id: 'A02', row: 'A', temperature: 23.1, status: 'Normal', load: 9.2, airflow: 820 },
  { id: 'A03', row: 'A', temperature: 24.5, status: 'Warning', load: 10.5, airflow: 780 },
  { id: 'A04', row: 'A', temperature: 25.2, status: 'Critical', load: 11.2, airflow: 750 },
  { id: 'B03', row: 'B', temperature: 26.5, status: 'Critical', load: 12.5, airflow: 700 }
])

// Hotspot data
const hotspotData = ref([
  { location: 'Row B', rack: 'B03', temperature: 26.5, severity: 'Critical', duration: '45 min', status: 'Active' },
  { location: 'Row A', rack: 'A04', temperature: 25.2, severity: 'Critical', duration: '30 min', status: 'Active' },
  { location: 'Row A', rack: 'A03', temperature: 24.5, severity: 'Warning', duration: '2 hours', status: 'Active' },
  { location: 'Row D', rack: 'D04', temperature: 24.2, severity: 'Warning', duration: '1 hour', status: 'Resolved' }
])

// Sensor data
const sensorData = ref([
  { zone: 'Zone 1', total: 32, active: 30, warning: 2, offline: 0 },
  { zone: 'Zone 2', total: 28, active: 27, warning: 1, offline: 0 },
  { zone: 'Zone 3', total: 35, active: 33, warning: 1, offline: 1 },
  { zone: 'Zone 4', total: 30, active: 28, warning: 2, offline: 0 }
])

// Thermal reports
const thermalReports = ref([
  { id: 1, title: 'Thermal Map Report', description: 'Complete temperature distribution analysis', icon: 'Grid', format: 'PDF', date: '2024-12-01' },
  { id: 2, title: 'Hotspot Analysis', description: 'Detailed hotspot detection and resolution', icon: 'Warning', format: 'PDF', date: '2024-12-01' },
  { id: 3, title: 'Sensor Health Report', description: 'Sensor network status and maintenance', icon: 'Connection', format: 'Excel', date: '2024-12-01' }
])

// Chart refs
const thermalMapChartRef = ref<HTMLElement | null>(null)
const tempTrendChartRef = ref<HTMLElement | null>(null)
const tempDistributionChartRef = ref<HTMLElement | null>(null)
const sensorMapChartRef = ref<HTMLElement | null>(null)
const verticalProfileChartRef = ref<HTMLElement | null>(null)
const horizontalProfileChartRef = ref<HTMLElement | null>(null)
const monthlyComparisonChartRef = ref<HTMLElement | null>(null)
const yearlyTrendChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Helper functions
const getTemperatureColor = (temp: number) => {
  if (temp < 20) return '#10b981'
  if (temp < 22) return '#84cc16'
  if (temp < 24) return '#f59e0b'
  if (temp < 26) return '#ef4444'
  return '#7c2d12'
}

const getTemperatureTextColor = (temp: number) => {
  if (temp < 22) return '#10b981'
  if (temp < 24) return '#f59e0b'
  return '#ef4444'
}

const getStatusClass = (temp: number) => {
  if (temp < 22) return 'status-good'
  if (temp < 24) return 'status-warning'
  return 'status-critical'
}

const getStatusTagType = (temp: number) => {
  if (temp < 22) return 'success'
  if (temp < 24) return 'warning'
  return 'danger'
}

const getStatusText = (temp: number) => {
  if (temp < 22) return 'Optimal'
  if (temp < 24) return 'Warning'
  return 'Critical'
}

const showRackDetails = (rack: any) => {
  selectedRack.value = rack
  rackDialogVisible.value = true
}

const investigateRack = () => {
  ElMessage.info(`Investigating rack ${selectedRack.value.id}`)
  rackDialogVisible.value = false
}

const zoomInMap = () => {
  ElMessage.info('Zoom in feature coming soon')
}

const zoomOutMap = () => {
  ElMessage.info('Zoom out feature coming soon')
}

const refreshMap = () => {
  ElMessage.success('Thermal map refreshed')
  initThermalMapChart()
}

const runHotspotAnalysis = () => {
  ElMessage.success('Hotspot analysis started. Results will be available shortly.')
}

const exportThermalMap = () => {
  ElMessage.success('Thermal map export started')
}

const scheduleAnalysis = () => {
  ElMessage.info('Analysis scheduling interface will open')
}

const generateReport = () => {
  ElMessage.success('Report generation started')
}

const downloadReport = (report: any) => {
  ElMessage.success(`Downloading ${report.title}...`)
}

// Chart initialization
const initThermalMapChart = () => {
  if (thermalMapChartRef.value) {
    const chart = echarts.init(thermalMapChartRef.value)
    const data: any[] = []
    for (let i = 0; i < 20; i++) {
      for (let j = 0; j < 30; j++) {
        data.push([j, i, 20 + Math.random() * 8 + Math.sin(i / 3) * 2 + Math.cos(j / 4) * 1.5])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Temperature: ${params.data[2].toFixed(1)}°C` },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => String(i + 1)), name: 'Rack Position', axisLabel: { rotate: 45, interval: 5 } },
      yAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String.fromCharCode(65 + i)), name: 'Row' },
      visualMap: { min: 18, max: 30, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#84cc16', '#f59e0b', '#ef4444', '#7c2d12'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false }, emphasis: { scale: true } }]
    })
    chartInstances.push(chart)
  }
}

const initTempTrendChart = () => {
  if (tempTrendChartRef.value) {
    const chart = echarts.init(tempTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Average Temp', 'Max Temp', 'Min Temp'] },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [
        { name: 'Average Temp', type: 'line', data: [22.1, 22.0, 21.8, 22.2, 22.5, 22.8, 23.0, 23.2, 23.1, 22.9, 22.6, 22.3], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Max Temp', type: 'line', data: [24.2, 24.0, 23.8, 24.5, 25.0, 25.5, 25.8, 26.0, 25.9, 25.6, 25.2, 24.8], smooth: true, lineStyle: { color: '#ef4444', width: 2 } },
        { name: 'Min Temp', type: 'line', data: [20.5, 20.3, 20.1, 20.4, 20.6, 20.8, 21.0, 21.2, 21.1, 20.9, 20.7, 20.4], smooth: true, lineStyle: { color: '#10b981', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initTempDistributionChart = () => {
  if (tempDistributionChartRef.value) {
    const chart = echarts.init(tempDistributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['<18°C', '18-20°C', '20-22°C', '22-24°C', '24-26°C', '>26°C'] },
      yAxis: { type: 'value', name: 'Number of Sensors' },
      series: [{
        type: 'bar', data: [8, 32, 65, 42, 8, 1],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => {
            const colors = ['#3b82f6', '#10b981', '#84cc16', '#f59e0b', '#ef4444', '#7c2d12']
            return colors[params.dataIndex]
          }
        },
        label: { show: true, position: 'top' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initSensorMapChart = () => {
  if (sensorMapChartRef.value) {
    const chart = echarts.init(sensorMapChartRef.value)
    const positions: any[] = []
    for (let i = 0; i < 50; i++) {
      positions.push([Math.random() * 100, Math.random() * 80, Math.random() > 0.9 ? 2 : Math.random() > 0.7 ? 1 : 0])
    }

    chart.setOption({
      tooltip: { formatter: (params: any) => `Sensor at (${params.data[0].toFixed(0)}, ${params.data[1].toFixed(0)})\nStatus: ${params.data[2] === 0 ? 'Normal' : params.data[2] === 1 ? 'Warning' : 'Critical'}` },
      xAxis: { show: false, min: 0, max: 100 },
      yAxis: { show: false, min: 0, max: 80 },
      series: [{
        type: 'scatter', data: positions,
        symbolSize: 10,
        itemStyle: { color: (params: any) => params.data[2] === 0 ? '#67c23a' : params.data[2] === 1 ? '#f59e0b' : '#ef4444' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initVerticalProfileChart = () => {
  if (verticalProfileChartRef.value) {
    const chart = echarts.init(verticalProfileChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Bottom', 'Middle', 'Top'] },
      xAxis: { type: 'category', data: ['Rack A', 'Rack B', 'Rack C', 'Rack D', 'Rack E', 'Rack F'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [
        { name: 'Bottom', type: 'line', data: [21.5, 22.0, 23.5, 22.5, 21.8, 22.2], lineStyle: { color: '#10b981' } },
        { name: 'Middle', type: 'line', data: [22.5, 23.0, 24.5, 23.5, 22.8, 23.2], lineStyle: { color: '#f59e0b' } },
        { name: 'Top', type: 'line', data: [23.5, 24.0, 25.5, 24.5, 23.8, 24.2], lineStyle: { color: '#ef4444' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initHorizontalProfileChart = () => {
  if (horizontalProfileChartRef.value) {
    const chart = echarts.init(horizontalProfileChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Front', 'Middle Front', 'Center', 'Middle Rear', 'Rear'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [{
        type: 'line', data: [22.0, 22.8, 23.5, 23.2, 22.5],
        smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 },
        label: { show: true, position: 'top' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initMonthlyComparisonChart = () => {
  if (monthlyComparisonChartRef.value) {
    const chart = echarts.init(monthlyComparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['This Year', 'Last Year'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Average Temperature (°C)' },
      series: [
        { name: 'This Year', type: 'line', data: [22.1, 22.0, 22.3, 22.5, 22.8, 23.0, 23.2, 23.1, 22.9, 22.6, 22.4, 22.2], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Last Year', type: 'line', data: [22.5, 22.4, 22.7, 22.9, 23.2, 23.5, 23.7, 23.6, 23.4, 23.1, 22.8, 22.6], smooth: true, lineStyle: { color: '#909399', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initYearlyTrendChart = () => {
  if (yearlyTrendChartRef.value) {
    const chart = echarts.init(yearlyTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
      yAxis: { type: 'value', name: 'Average Temperature (°C)' },
      series: [{
        type: 'line', data: [23.5, 23.2, 22.8, 22.5, 22.2],
        smooth: true, lineStyle: { color: '#409eff', width: 3 }, areaStyle: { opacity: 0.3 },
        label: { show: true, position: 'top', formatter: '{c}°C' }
      }]
    })
    chartInstances.push(chart)
  }
}

// Watch for map layer changes
watch(mapLayer, () => {
  initThermalMapChart()
})

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

onMounted(() => {
  let messageIndex = 0
  let progressInterval: ReturnType<typeof setInterval>
  let messageInterval: ReturnType<typeof setInterval>

  messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      const increment = Math.random() * 12 + 3
      loadingProgress.value = Math.min(loadingProgress.value + increment, 100)
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      setTimeout(() => {
        initThermalMapChart()
        initTempTrendChart()
        initTempDistributionChart()
        initSensorMapChart()
        initVerticalProfileChart()
        initHorizontalProfileChart()
        initMonthlyComparisonChart()
        initYearlyTrendChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.thermal-map-container {
  min-height: 100vh;
  background-color: #f5f7fa;
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
  border: 1px solid rgba(64, 158, 255, 0.3);
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
  border-top-color: #ef4444;
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
  width: 320px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #ef4444, #f59e0b, #10b981);
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

/* ==================== Main Content Styles ==================== */
.thermal-map-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.page-header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.overview-section {
  margin: 24px 0;
}

.overview-card {
  border-radius: 12px;
  transition: transform 0.2s;
}

.overview-card:hover {
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
}

.card-header .el-icon {
  font-size: 18px;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 16px;
}

.card-footer {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.status-text {
  font-size: 12px;
  color: #909399;
}

/* Thermal Map Section */
.thermal-map-section {
  margin-bottom: 24px;
}

.map-card {
  border-radius: 12px;
}

.card-header-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.card-header-simple .header-actions {
  margin-left: auto;
  display: flex;
  gap: 12px;
  align-items: center;
}

.map-container {
  min-height: 550px;
}

.map-legend {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
}

.legend-title {
  font-weight: 600;
  color: #606266;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 4px;
  display: inline-block;
}

/* Rack Grid Section */
.rack-grid-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.rack-grid {
  background: white;
  border-radius: 12px;
  padding: 20px;
  overflow-x: auto;
}

.rack-row {
  display: flex;
  margin-bottom: 8px;
}

.row-label {
  width: 50px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
  margin-right: 8px;
}

.row-racks {
  display: flex;
  flex: 1;
  gap: 8px;
}

.rack-cell {
  flex: 1;
  min-width: 80px;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
  color: white;
}

.rack-cell:hover {
  transform: scale(1.05);
}

.rack-id {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
}

.rack-temp {
  font-size: 14px;
  font-weight: 700;
}

.rack-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin: 4px auto 0;
}

.rack-status.status-good {
  background: #10b981;
  box-shadow: 0 0 4px #10b981;
}

.rack-status.status-warning {
  background: #f59e0b;
  box-shadow: 0 0 4px #f59e0b;
}

.rack-status.status-critical {
  background: #ef4444;
  box-shadow: 0 0 4px #ef4444;
}

/* Main Content */
.main-content-card {
  margin-top: 20px;
  border-radius: 12px;
}

.tab-content {
  padding: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e4e7ed;
}

.section-title .el-icon {
  font-size: 22px;
  color: #ef4444;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Hotspot Summary */
.hotspot-summary {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  height: 100%;
}

.hotspot-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.stat-circle {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.percentage-value {
  font-size: 28px;
  font-weight: 700;
  color: #ef4444;
}

.percentage-label {
  font-size: 12px;
  color: #909399;
}

.stat-details {
  text-align: left;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item strong {
  color: #303133;
}

/* Report Cards */
.report-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.report-card .el-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.report-card h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.report-card p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #909399;
}

.report-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #c0c4cc;
}

/* Action Buttons */
.action-buttons {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.action-buttons .el-button {
  border-radius: 8px;
}

/* Deep Selectors */
:deep(.el-tabs--border-card) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-progress__text) {
  font-size: 12px;
}
</style>