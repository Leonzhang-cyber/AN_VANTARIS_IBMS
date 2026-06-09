<template>
  <div class="power-capacity-container">
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
            <span class="loading-title">Loading Power Capacity</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Power Capacity Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Power Capacity</span>
          <el-tag type="danger" effect="dark" size="large">Power Management</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="capacityAlert" class="alert-banner" :class="alertType">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ alertMessage }}</span>
        <el-button size="small" :type="alertType === 'critical' ? 'danger' : 'warning'" @click="viewCapacityDetails">
          View Details
        </el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Total Capacity</span>
              </div>
              <div class="card-value">{{ totalCapacity }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="capacityUtilization" :stroke-width="8" :color="capacityColor" />
                <span class="status-text">Utilization: {{ capacityUtilization }}%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Current Load</span>
              </div>
              <div class="card-value">{{ currentLoad }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="(currentLoad / totalCapacity) * 100" :stroke-width="8" :color="loadColor" />
                <span class="status-text">Peak: {{ peakLoad }} kW</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Battery /></el-icon>
                <span>Reserve Capacity</span>
              </div>
              <div class="card-value">{{ reserveCapacity }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="reservePercentage" :stroke-width="8" :color="reserveColor" />
                <span class="status-text">N+1 Redundancy</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>PUE</span>
              </div>
              <div class="card-value">{{ pue }}</div>
              <div class="card-footer">
                <el-progress :percentage="100 - (pue - 1) * 100" :stroke-width="8" status="success" :format="() => `Target: 1.35`" />
                <span class="status-text">Cooling: {{ coolingPower }} kW</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Main Power Distribution Chart -->
      <div class="distribution-section">
        <el-card class="distribution-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Connection /></el-icon>
            <span>Power Distribution by Area</span>
            <el-radio-group v-model="distributionType" size="small">
              <el-radio-button label="byRow">By Row</el-radio-button>
              <el-radio-button label="byZone">By Zone</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <div ref="distributionChartRef" style="height: 350px"></div>
          </div>
        </el-card>
      </div>

      <!-- Power Topology -->
      <div class="topology-section">
        <el-card class="topology-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Share /></el-icon>
            <span>Power Distribution Topology</span>
            <div class="header-actions">
              <el-button size="small" @click="zoomIn">Zoom In</el-button>
              <el-button size="small" @click="zoomOut">Zoom Out</el-button>
              <el-button size="small" type="primary" @click="exportTopology">Export</el-button>
            </div>
          </div>
          <div class="topology-container">
            <div ref="topologyChartRef" style="height: 400px"></div>
          </div>
        </el-card>
      </div>

      <!-- Area Power Details -->
      <div class="area-section">
        <div class="section-header">
          <h3>Area Power Details</h3>
          <div class="header-controls">
            <el-input v-model="searchQuery" placeholder="Search area..." prefix-icon="Search" style="width: 200px" clearable />
            <el-button type="primary" @click="exportAreaData">Export Data</el-button>
          </div>
        </div>
        <el-table :data="filteredAreaData" border style="width: 100%">
          <el-table-column prop="area" label="Area" align="center" />
          <el-table-column prop="capacity" label="Capacity (kW)" align="center" />
          <el-table-column prop="currentLoad" label="Current Load (kW)" align="center" />
          <el-table-column label="Utilization" align="center">
            <template #default="{ row }">
              <el-progress :percentage="(row.currentLoad / row.capacity) * 100" :stroke-width="10" :color="getUtilColor(row.currentLoad / row.capacity)" />
            </template>
          </el-table-column>
          <el-table-column prop="peakLoad" label="Peak Load (kW)" align="center" />
          <el-table-column prop="reserve" label="Reserve (kW)" align="center" />
          <el-table-column prop="status" label="Status" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.currentLoad / row.capacity)" size="small">
                {{ getStatusText(row.currentLoad / row.capacity) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Load Trends Tab -->
          <el-tab-pane label="Load Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Power Load Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="loadTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="dailyPeakChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Capacity Forecast Tab -->
          <el-tab-pane label="Capacity Forecast" name="forecast">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Power Capacity Forecast</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="forecastChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="forecast-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ monthsUntilFull }} months</div>
                      <div class="stat-label">Until Capacity Full</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ requiredUpgrade }} kW</div>
                      <div class="stat-label">Required Upgrade by 2025</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ growthRate }}%</div>
                      <div class="stat-label">Annual Growth Rate</div>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="generateUpgradePlan">
                      Generate Upgrade Plan
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Power Quality Tab -->
          <el-tab-pane label="Power Quality" name="quality">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Monitor /></el-icon>
                <span>Power Quality Metrics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="powerQualityChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="quality-metrics">
                    <div class="metric-item">
                      <span>Power Factor</span>
                      <el-progress :percentage="94" :stroke-width="8" :format="() => '0.94'" status="success" />
                    </div>
                    <div class="metric-item">
                      <span>THD Voltage</span>
                      <el-progress :percentage="4.8" :stroke-width="8" :format="() => '4.8%'" status="warning" />
                    </div>
                    <div class="metric-item">
                      <span>Voltage Stability</span>
                      <el-progress :percentage="98" :stroke-width="8" :format="() => '±2.2%'" status="success" />
                    </div>
                    <div class="metric-item">
                      <span>Frequency Stability</span>
                      <el-progress :percentage="99" :stroke-width="8" :format="() => '±0.1Hz'" status="success" />
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Redundancy Analysis Tab -->
          <el-tab-pane label="Redundancy" name="redundancy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Lock /></el-icon>
                <span>Redundancy Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="redundancyChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="redundancy-stats">
                    <div class="stat-card">
                      <div class="stat-value">N+1</div>
                      <div class="stat-label">Redundancy Level</div>
                      <el-tag type="success">Compliant</el-tag>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ redundantCapacity }} kW</div>
                      <div class="stat-label">Redundant Capacity</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ failureTolerance }} kW</div>
                      <div class="stat-label">Single Failure Tolerance</div>
                    </div>
                    <div class="redundancy-note">
                      <el-icon><InfoFilled /></el-icon>
                      <span>N+1 redundancy maintained. Can withstand single UPS/feeder failure.</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Recommendations Tab -->
          <el-tab-pane label="Recommendations" name="recommendations">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>Capacity Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="recommendations" border style="width: 100%">
                    <el-table-column prop="recommendation" label="Recommendation" width="300" />
                    <el-table-column prop="impact" label="Impact" />
                    <el-table-column prop="priority" label="Priority" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.priority === 'High' ? 'danger' : 'warning'" size="small">
                          {{ row.priority }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="Action" width="100">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="applyRecommendation(row)">Apply</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="8">
                  <div class="recommendation-summary">
                    <h4>Total Improvement Potential</h4>
                    <div class="potential-value">15%</div>
                    <div class="potential-label">Capacity Efficiency Gain</div>
                    <el-progress :percentage="15" :stroke-width="12" status="success" />
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="runOptimization">
                      Run Optimization
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Alerts Tab -->
          <el-tab-pane label="Alerts" name="alerts">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Bell /></el-icon>
                <span>Power Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="powerAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getAlertSeverityType(row.severity)" size="small">
                          {{ row.severity }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Message" />
                    <el-table-column prop="location" label="Location" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="health-panel">
                    <h4>Power Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Capacity Health</span>
                        <el-progress :percentage="capacityHealth" :stroke-width="6" :color="getHealthColor(capacityHealth)" />
                      </div>
                      <div class="health-item">
                        <span>Redundancy Health</span>
                        <el-progress :percentage="95" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Power Quality</span>
                        <el-progress :percentage="88" :stroke-width="6" status="success" />
                      </div>
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
        <el-button type="primary" size="large" @click="runCapacityAnalysis">
          <el-icon><Cpu /></el-icon>
          Run Capacity Analysis
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button size="large" @click="scheduleUpgrade">
          <el-icon><Calendar /></el-icon>
          Schedule Upgrade
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading power capacity data...')

const loadingMessages = [
  'Loading power capacity data...',
  'Analyzing distribution topology...',
  'Calculating redundancy metrics...',
  'Forecasting capacity needs...',
  'Generating recommendations...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('trends')
const distributionType = ref('byRow')
const searchQuery = ref('')
const capacityAlert = ref(true)
const alertType = ref('warning')
const alertMessage = ref('Row B capacity utilization at 85%. Planning recommended.')

// Power capacity metrics
const totalCapacity = ref(1500)
const currentLoad = ref(985)
const peakLoad = ref(1050)
const reserveCapacity = ref(515)
const reservePercentage = computed(() => (reserveCapacity.value / totalCapacity.value) * 100)
const capacityUtilization = computed(() => Math.round((currentLoad.value / totalCapacity.value) * 100))
const pue = ref(1.42)
const coolingPower = ref(285)

const monthsUntilFull = ref(6)
const requiredUpgrade = ref(250)
const growthRate = ref(8.5)
const redundantCapacity = ref(250)
const failureTolerance = ref(200)
const healthScore = ref(84)
const capacityHealth = ref(72)

// Colors
const capacityColor = computed(() => {
  if (capacityUtilization.value < 70) return '#67c23a'
  if (capacityUtilization.value < 85) return '#e6a23c'
  return '#f56c6c'
})

const loadColor = computed(() => {
  const pct = (currentLoad.value / totalCapacity.value) * 100
  if (pct < 70) return '#67c23a'
  if (pct < 85) return '#e6a23c'
  return '#f56c6c'
})

const reserveColor = computed(() => {
  if (reservePercentage.value > 30) return '#67c23a'
  if (reservePercentage.value > 15) return '#e6a23c'
  return '#f56c6c'
})

const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

// Area data
const areaData = ref([
  { area: 'Row A', capacity: 250, currentLoad: 185, peakLoad: 195, reserve: 65, status: 'Normal' },
  { area: 'Row B', capacity: 250, currentLoad: 212, peakLoad: 225, reserve: 38, status: 'Warning' },
  { area: 'Row C', capacity: 250, currentLoad: 168, peakLoad: 178, reserve: 82, status: 'Normal' },
  { area: 'Row D', capacity: 250, currentLoad: 145, peakLoad: 155, reserve: 105, status: 'Normal' },
  { area: 'Row E', capacity: 250, currentLoad: 195, peakLoad: 205, reserve: 55, status: 'Warning' },
  { area: 'Storage', capacity: 250, currentLoad: 80, peakLoad: 90, reserve: 170, status: 'Normal' }
])

const filteredAreaData = computed(() => {
  if (!searchQuery.value) return areaData.value
  return areaData.value.filter(a => a.area.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

// Zone data for chart
const zoneData = ref([
  { name: 'Zone A', value: 185, capacity: 250 },
  { name: 'Zone B', value: 212, capacity: 250 },
  { name: 'Zone C', value: 168, capacity: 250 },
  { name: 'Zone D', value: 145, capacity: 250 },
  { name: 'Zone E', value: 195, capacity: 250 }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Upgrade Row B power feed (currently at 85% capacity)', impact: '+50kW capacity', priority: 'High' },
  { recommendation: 'Implement load balancing between Row A and Row B', impact: 'Reduce peak by 15kW', priority: 'High' },
  { recommendation: 'Add redundant UPS module for N+2 configuration', impact: 'Improve fault tolerance', priority: 'Medium' },
  { recommendation: 'Optimize cooling setpoints to reduce PUE', impact: 'Save 8% energy', priority: 'Medium' }
])

// Power alerts
const powerAlerts = ref([
  { severity: 'Warning', message: 'Row B power utilization exceeds 85%', location: 'Row B', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'UPS load balancing in progress', location: 'Main UPS', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'Peak load approaching capacity limit', location: 'Main Feed', timestamp: '2024-12-18 08:30' }
])

// Helper functions
const getUtilColor = (ratio: number) => {
  if (ratio < 0.7) return '#67c23a'
  if (ratio < 0.85) return '#e6a23c'
  return '#f56c6c'
}

const getStatusType = (ratio: number) => {
  if (ratio < 0.7) return 'success'
  if (ratio < 0.85) return 'warning'
  return 'danger'
}

const getStatusText = (ratio: number) => {
  if (ratio < 0.7) return 'Normal'
  if (ratio < 0.85) return 'Warning'
  return 'Critical'
}

const getAlertSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const getHealthColor = (score: number) => {
  if (score > 80) return '#67c23a'
  if (score > 60) return '#e6a23c'
  return '#f56c6c'
}

const viewCapacityDetails = () => {
  activeTab.value = 'forecast'
}

const exportAreaData = () => {
  ElMessage.success('Area data export started')
}

const exportTopology = () => {
  ElMessage.success('Topology export started')
}

const zoomIn = () => {
  ElMessage.info('Zoom in feature')
}

const zoomOut = () => {
  ElMessage.info('Zoom out feature')
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('Capacity optimization started')
}

const runCapacityAnalysis = () => {
  ElMessage.success('Full capacity analysis started')
}

const exportReport = () => {
  ElMessage.success('Capacity report export started')
}

const scheduleUpgrade = () => {
  ElMessage.info('Upgrade scheduling interface will open')
}

const generateUpgradePlan = () => {
  ElMessage.success('Upgrade plan generated')
}

// Chart refs
const distributionChartRef = ref<HTMLElement | null>(null)
const topologyChartRef = ref<HTMLElement | null>(null)
const loadTrendChartRef = ref<HTMLElement | null>(null)
const dailyPeakChartRef = ref<HTMLElement | null>(null)
const forecastChartRef = ref<HTMLElement | null>(null)
const powerQualityChartRef = ref<HTMLElement | null>(null)
const redundancyChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Chart initialization
const initDistributionChart = () => {
  if (distributionChartRef.value) {
    const chart = echarts.init(distributionChartRef.value)
    if (distributionType.value === 'byRow') {
      chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        legend: { data: ['Current Load', 'Capacity', 'Reserve'] },
        xAxis: { type: 'category', data: areaData.value.map(a => a.area) },
        yAxis: { type: 'value', name: 'Power (kW)' },
        series: [
          { name: 'Current Load', type: 'bar', data: areaData.value.map(a => a.currentLoad), itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} kW' } },
          { name: 'Capacity', type: 'bar', data: areaData.value.map(a => a.capacity), itemStyle: { color: '#e4e7ed', borderRadius: [8, 8, 0, 0] } },
          { name: 'Reserve', type: 'bar', data: areaData.value.map(a => a.reserve), itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] } }
        ]
      })
    } else {
      chart.setOption({
        tooltip: { trigger: 'item' },
        legend: { top: 'bottom' },
        series: [{
          type: 'pie', radius: '55%',
          data: zoneData.value.map(z => ({ name: z.name, value: z.value, itemStyle: { color: z.value / z.capacity > 0.85 ? '#f56c6c' : z.value / z.capacity > 0.7 ? '#e6a23c' : '#67c23a' } })),
          label: { show: true, formatter: '{b}: {d}%' }
        }]
      })
    }
    chartInstances.push(chart)
  }
}

const initTopologyChart = () => {
  if (topologyChartRef.value) {
    const chart = echarts.init(topologyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        data: [
          { name: 'Utility Feed' }, { name: 'Transformer' }, { name: 'Main Switchgear' },
          { name: 'UPS 1' }, { name: 'UPS 2' }, { name: 'UPS 3' },
          { name: 'PDU A' }, { name: 'PDU B' }, { name: 'PDU C' },
          { name: 'Row A' }, { name: 'Row B' }, { name: 'Row C' }
        ],
        links: [
          { source: 'Utility Feed', target: 'Transformer', value: 1500 },
          { source: 'Transformer', target: 'Main Switchgear', value: 1500 },
          { source: 'Main Switchgear', target: 'UPS 1', value: 500 },
          { source: 'Main Switchgear', target: 'UPS 2', value: 500 },
          { source: 'Main Switchgear', target: 'UPS 3', value: 500 },
          { source: 'UPS 1', target: 'PDU A', value: 450 },
          { source: 'UPS 2', target: 'PDU B', value: 450 },
          { source: 'UPS 3', target: 'PDU C', value: 450 },
          { source: 'PDU A', target: 'Row A', value: 185 },
          { source: 'PDU A', target: 'Row B', value: 212 },
          { source: 'PDU B', target: 'Row C', value: 168 },
          { source: 'PDU B', target: 'Row D', value: 145 },
          { source: 'PDU C', target: 'Row E', value: 195 }
        ],
        lineStyle: { color: 'gradient', curveness: 0.5 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initLoadTrendChart = () => {
  if (loadTrendChartRef.value) {
    const chart = echarts.init(loadTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Total Load', 'IT Load', 'Cooling Load', 'Other Load'] },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        { name: 'Total Load', type: 'line', data: [850, 820, 800, 810, 880, 950, 985, 1020, 1000, 960, 910, 870], smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'IT Load', type: 'line', data: [620, 600, 590, 600, 650, 700, 720, 740, 730, 700, 670, 640], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'Cooling Load', type: 'line', data: [180, 175, 170, 172, 185, 195, 200, 210, 205, 195, 185, 180], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Other Load', type: 'line', data: [50, 45, 40, 38, 45, 55, 65, 70, 65, 65, 55, 50], smooth: true, lineStyle: { color: '#f59e0b', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initDailyPeakChart = () => {
  if (dailyPeakChartRef.value) {
    const chart = echarts.init(dailyPeakChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { type: 'value', name: 'Peak Power (kW)' },
      series: [{
        type: 'bar', data: [1020, 1015, 1030, 1045, 1050, 980, 920],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => {
            const val = params.data
            if (val > 1000) return '#f56c6c'
            if (val > 950) return '#e6a23c'
            return '#67c23a'
          }
        },
        label: { show: true, position: 'top', formatter: '{c} kW' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initForecastChart = () => {
  if (forecastChartRef.value) {
    const chart = echarts.init(forecastChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Historical Load', 'Forecast Load', 'Capacity Limit'] },
      xAxis: { type: 'category', data: ['2024 Q1', '2024 Q2', '2024 Q3', '2024 Q4', '2025 Q1', '2025 Q2', '2025 Q3', '2025 Q4'] },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        { name: 'Historical Load', type: 'line', data: [850, 880, 920, 960, null, null, null, null], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Forecast Load', type: 'line', data: [null, null, null, 960, 1000, 1040, 1080, 1120], smooth: true, lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Capacity Limit', type: 'line', data: [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500], lineStyle: { color: '#f56c6c', width: 2, type: 'dotted' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPowerQualityChart = () => {
  if (powerQualityChartRef.value) {
    const chart = echarts.init(powerQualityChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Voltage (V)', 'Current (A)', 'Power Factor'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: [
        { type: 'value', name: 'Voltage (V)' },
        { type: 'value', name: 'Current (A)' },
        { type: 'value', name: 'Power Factor', min: 0.8, max: 1.0 }
      ],
      series: [
        { name: 'Voltage (V)', type: 'line', data: [415, 414, 416, 413, 415, 414], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'Current (A)', type: 'line', data: [1250, 1200, 1280, 1320, 1300, 1260], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Power Factor', type: 'line', yAxisIndex: 2, data: [0.94, 0.93, 0.95, 0.94, 0.93, 0.94], smooth: true, lineStyle: { color: '#f59e0b', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initRedundancyChart = () => {
  if (redundancyChartRef.value) {
    const chart = echarts.init(redundancyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['UPS 1', 'UPS 2', 'UPS 3'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'Current Load', type: 'bar', data: [330, 340, 315], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} kW' } },
        { name: 'Capacity', type: 'bar', data: [500, 500, 500], itemStyle: { color: '#e4e7ed', borderRadius: [8, 8, 0, 0] } }
      ]
    })
    chartInstances.push(chart)
  }
}

// Watch for distribution type changes
const refreshDistribution = () => {
  initDistributionChart()
}

// Real-time updates
let realTimeInterval: ReturnType<typeof setInterval>

const startRealTimeUpdates = () => {
  realTimeInterval = setInterval(() => {
    currentLoad.value = 980 + Math.random() * 20
    const idx = Math.floor(Math.random() * areaData.value.length)
    areaData.value[idx].currentLoad = 180 + Math.random() * 50
  }, 5000)
}

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
        initDistributionChart()
        initTopologyChart()
        initLoadTrendChart()
        initDailyPeakChart()
        initForecastChart()
        initPowerQualityChart()
        initRedundancyChart()
        startRealTimeUpdates()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (realTimeInterval) clearInterval(realTimeInterval)
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.power-capacity-container {
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

.spinner-ring:nth-child(1) { border-top-color: #409eff; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #67c23a; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

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
  background: linear-gradient(90deg, #409eff, #67c23a, #f59e0b);
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
.power-capacity-container {
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

/* Alert Banner */
.alert-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.alert-banner.warning {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
  color: #d97706;
}

.alert-banner.critical {
  background: #fef2f2;
  border-left: 4px solid #f56c6c;
  color: #dc2626;
}

.alert-banner .el-icon {
  font-size: 20px;
}

.alert-banner span {
  flex: 1;
  font-weight: 500;
}

/* Overview Section */
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

/* Distribution Section */
.distribution-section {
  margin-bottom: 24px;
}

.distribution-card {
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
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Topology Section */
.topology-section {
  margin-bottom: 24px;
}

.topology-card {
  border-radius: 12px;
}

.topology-container {
  min-height: 400px;
}

/* Area Section */
.area-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-controls {
  display: flex;
  gap: 12px;
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
  color: #409eff;
}

/* Forecast Stats */
.forecast-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.stat-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 8px;
}

/* Quality Metrics */
.quality-metrics {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.metric-item {
  margin-bottom: 24px;
}

.metric-item span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

/* Redundancy Stats */
.redundancy-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.redundancy-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #ecf5ff;
  border-radius: 8px;
  font-size: 12px;
  color: #606266;
}

/* Recommendation Summary */
.recommendation-summary {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  height: 100%;
}

.recommendation-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.potential-value {
  font-size: 48px;
  font-weight: 700;
  color: #d97706;
  margin: 16px 0;
}

.potential-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 16px;
}

/* Health Panel */
.health-panel {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  text-align: center;
}

.health-panel h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.health-score {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.health-metrics {
  text-align: left;
}

.health-item {
  margin-bottom: 16px;
}

.health-item span {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
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