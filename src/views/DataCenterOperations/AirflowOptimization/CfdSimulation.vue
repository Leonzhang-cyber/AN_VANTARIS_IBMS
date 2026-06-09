<template>
  <div class="hotspot-detection-container">
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
            <span class="loading-title">Loading Hotspot Detection</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Real-Time Hotspot Monitoring & Alerting</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Hotspot Detection</span>
          <el-tag type="danger" effect="dark" size="large">Real-Time Monitoring</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="criticalHotspots > 0" class="alert-banner critical">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ criticalHotspots }} critical hotspot(s) detected! Immediate action required.</span>
        <el-button size="small" type="danger" @click="viewCriticalHotspots">View Now</el-button>
      </div>
      <div v-else-if="warningHotspots > 0" class="alert-banner warning">
        <el-icon><Warning /></el-icon>
        <span>{{ warningHotspots }} warning hotspot(s) detected. Review recommended.</span>
        <el-button size="small" type="warning" @click="viewWarningHotspots">Review</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Warning /></el-icon>
                <span>Active Hotspots</span>
              </div>
              <div class="card-value">{{ activeHotspots }}</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" :color="hotspotProgressColor" :format="() => `${criticalHotspots} Critical`" />
                <span class="status-text">{{ resolvedHotspots }} Resolved Today</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Temperature /></el-icon>
                <span>Max Temperature</span>
              </div>
              <div class="card-value">28.5°C</div>
              <div class="card-footer">
                <el-progress :percentage="95" :stroke-width="8" status="exception" :format="() => 'Threshold: 27°C'" />
                <span class="status-text">Location: Rack B03</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Avg Resolution Time</span>
              </div>
              <div class="card-value">2.4 hrs</div>
              <div class="card-footer">
                <el-progress :percentage="65" :stroke-width="8" status="warning" :format="() => 'Target: 1.5 hrs'" />
                <span class="status-text">Improved by 32%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Detection Accuracy</span>
              </div>
              <div class="card-value">96%</div>
              <div class="card-footer">
                <el-progress :percentage="96" :stroke-width="8" status="success" />
                <span class="status-text">AI-Powered Detection</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Hotspot Heatmap -->
      <div class="heatmap-section">
        <el-card class="heatmap-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Grid /></el-icon>
            <span>Hotspot Heatmap</span>
            <div class="header-actions">
              <el-radio-group v-model="heatmapType" size="small">
                <el-radio-button label="temperature">Temperature</el-radio-button>
                <el-radio-button label="risk">Risk Level</el-radio-button>
                <el-radio-button label="density">Hotspot Density</el-radio-button>
              </el-radio-group>
              <el-button size="small" type="primary" @click="refreshHeatmap">Refresh</el-button>
            </div>
          </div>
          <div class="heatmap-container">
            <div ref="hotspotHeatmapRef" style="height: 450px"></div>
          </div>
        </el-card>
      </div>

      <!-- Active Hotspots List -->
      <div class="hotspots-section">
        <div class="section-header">
          <h3>Active Hotspots</h3>
          <div class="header-controls">
            <el-input v-model="searchQuery" placeholder="Search hotspots..." prefix-icon="Search" style="width: 250px" clearable />
            <el-select v-model="severityFilter" placeholder="Severity" clearable style="width: 120px">
              <el-option label="Critical" value="Critical" />
              <el-option label="Warning" value="Warning" />
              <el-option label="Info" value="Info" />
            </el-select>
            <el-button type="primary" @click="exportHotspotData">Export Data</el-button>
          </div>
        </div>
        <el-table :data="filteredHotspots" border style="width: 100%">
          <el-table-column prop="location" label="Location" width="120" />
          <el-table-column prop="rack" label="Rack ID" width="100" />
          <el-table-column prop="temperature" label="Temperature" width="120">
            <template #default="{ row }">
              <span :style="{ color: getTemperatureColor(row.temperature), fontWeight: 'bold' }">
                {{ row.temperature }}°C
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="Duration" width="120" />
          <el-table-column prop="cause" label="Detected Cause" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Active' ? 'danger' : 'success'" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewHotspotDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="startInvestigation(row)">Investigate</el-button>
              <el-button type="warning" link size="small" @click="resolveHotspot(row)">Resolve</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Hotspot Trends Tab -->
          <el-tab-pane label="Hotspot Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Hotspot Detection Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="hotspotTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="severityDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Root Cause Analysis Tab -->
          <el-tab-pane label="Root Cause Analysis" name="rca">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Root Cause Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="rootCauseChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="rootcause-list">
                    <h4>Common Root Causes</h4>
                    <div v-for="cause in rootCauses" :key="cause.name" class="cause-item">
                      <div class="cause-header">
                        <span class="cause-name">{{ cause.name }}</span>
                        <el-tag :type="cause.severity === 'High' ? 'danger' : 'warning'" size="small">
                          {{ cause.percentage }}%
                        </el-tag>
                      </div>
                      <el-progress :percentage="cause.percentage" :stroke-width="8" :color="cause.severity === 'High' ? '#ef4444' : '#f59e0b'" />
                      <div class="cause-recommendation">{{ cause.recommendation }}</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Resolution History Tab -->
          <el-tab-pane label="Resolution History" name="history">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Clock /></el-icon>
                <span>Hotspot Resolution History</span>
              </div>
              <el-table :data="resolutionHistory" border style="width: 100%">
                <el-table-column prop="timestamp" label="Time" width="180" />
                <el-table-column prop="location" label="Location" width="120" />
                <el-table-column prop="rack" label="Rack" width="100" />
                <el-table-column prop="temperature" label="Temp" width="100" />
                <el-table-column prop="resolution" label="Resolution Action" />
                <el-table-column prop="resolvedBy" label="Resolved By" width="120" />
                <el-table-column prop="duration" label="Duration" width="100" />
              </el-table>
            </div>
          </el-tab-pane>

          <!-- AI Predictions Tab -->
          <el-tab-pane label="AI Predictions" name="predictions">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Cpu /></el-icon>
                <span>AI-Powered Hotspot Predictions</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="predictionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="predictions-list">
                    <h4>Predicted Hotspots (Next 24 Hours)</h4>
                    <div v-for="pred in predictions" :key="pred.location" class="prediction-item" :class="pred.risk">
                      <div class="prediction-header">
                        <span class="prediction-location">{{ pred.location }} - {{ pred.rack }}</span>
                        <el-tag :type="pred.risk === 'High' ? 'danger' : 'warning'" size="small">
                          {{ pred.risk }} Risk
                        </el-tag>
                      </div>
                      <div class="prediction-details">
                        <span>Expected Temp: {{ pred.expectedTemp }}°C</span>
                        <span>Probability: {{ pred.probability }}%</span>
                      </div>
                      <div class="prediction-action">
                        <el-button type="primary" size="small" @click="preventHotspot(pred)">Preventive Action</el-button>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Resolution Recommendations Tab -->
          <el-tab-pane label="Recommendations" name="recommendations">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>Resolution Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="recommendations" border style="width: 100%">
                    <el-table-column prop="hotspot" label="Hotspot Location" width="150" />
                    <el-table-column prop="recommendation" label="Recommended Action" />
                    <el-table-column prop="impact" label="Expected Impact" width="120" />
                    <el-table-column prop="priority" label="Priority" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.priority === 'High' ? 'danger' : row.priority === 'Medium' ? 'warning' : 'info'" size="small">
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
                    <h4>Automated Actions</h4>
                    <div class="auto-action-item">
                      <el-switch v-model="autoRemediation" />
                      <span>Auto-Remediation Enabled</span>
                    </div>
                    <div class="auto-action-settings">
                      <p>When enabled, the system will automatically:</p>
                      <ul>
                        <li>Adjust CRAC/CRAH setpoints</li>
                        <li>Increase local fan speeds</li>
                        <li>Send alerts to maintenance team</li>
                        <li>Log all actions for audit</li>
                      </ul>
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
        <el-button type="primary" size="large" @click="runFullDetection">
          <el-icon><Cpu /></el-icon>
          Run Full Detection Scan
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Hotspot Report
        </el-button>
        <el-button size="large" @click="schedulePreventiveMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Preventive Maintenance
        </el-button>
      </div>
    </template>

    <!-- Hotspot Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Hotspot Details - ${selectedHotspot?.rack}`" width="600px">
      <el-descriptions :column="2" border v-if="selectedHotspot">
        <el-descriptions-item label="Location">{{ selectedHotspot.location }}</el-descriptions-item>
        <el-descriptions-item label="Rack ID">{{ selectedHotspot.rack }}</el-descriptions-item>
        <el-descriptions-item label="Temperature">
          <span :style="{ color: getTemperatureColor(selectedHotspot.temperature), fontWeight: 'bold' }">
            {{ selectedHotspot.temperature }}°C
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityType(selectedHotspot.severity)">{{ selectedHotspot.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Duration">{{ selectedHotspot.duration }}</el-descriptions-item>
        <el-descriptions-item label="Detected At">{{ selectedHotspot.detectedAt || '2024-12-18 10:30:00' }}</el-descriptions-item>
        <el-descriptions-item label="Detected Cause">{{ selectedHotspot.cause }}</el-descriptions-item>
        <el-descriptions-item label="Affected Equipment">{{ selectedHotspot.affectedEquipment || 'Server Rack' }}</el-descriptions-item>
        <el-descriptions-item label="Recommended Action" :span="2">{{ selectedHotspot.recommendation || 'Increase airflow, check for blockage' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="startInvestigation(selectedHotspot)">Start Investigation</el-button>
        <el-button type="success" @click="resolveHotspot(selectedHotspot)">Mark Resolved</el-button>
      </template>
    </el-dialog>
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
const loadingMessage = ref('Initializing hotspot detection...')

const loadingMessages = [
  'Initializing hotspot detection...',
  'Scanning temperature sensors...',
  'Analyzing thermal patterns...',
  'Detecting anomalies...',
  'Generating heatmap...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('trends')
const heatmapType = ref('temperature')
const severityFilter = ref('')
const searchQuery = ref('')
const detailsDialogVisible = ref(false)
const selectedHotspot = ref<any>(null)
const autoRemediation = ref(false)

// Hotspot counts
const activeHotspots = ref(5)
const criticalHotspots = ref(2)
const warningHotspots = ref(3)
const resolvedHotspots = ref(8)

const hotspotProgressColor = computed(() => {
  if (criticalHotspots.value > 0) return '#ef4444'
  if (warningHotspots.value > 0) return '#f59e0b'
  return '#10b981'
})

// Active hotspots data
const hotspots = ref([
  { id: 1, location: 'Row A', rack: 'A04', temperature: 27.2, severity: 'Critical', duration: '45 min', cause: 'High server load + blocked airflow', status: 'Active', recommendation: 'Install blanking panels, increase airflow' },
  { id: 2, location: 'Row B', rack: 'B03', temperature: 28.5, severity: 'Critical', duration: '30 min', cause: 'Failed CRAC unit in zone', status: 'Active', recommendation: 'Redirect airflow, schedule maintenance' },
  { id: 3, location: 'Row A', rack: 'A03', temperature: 25.8, severity: 'Warning', duration: '2 hours', cause: 'Partial air blockage', status: 'Active', recommendation: 'Clear obstructions' },
  { id: 4, location: 'Row D', rack: 'D04', temperature: 25.2, severity: 'Warning', duration: '1 hour', cause: 'High density compute cluster', status: 'Active', recommendation: 'Add local cooling' },
  { id: 5, location: 'Row C', rack: 'C07', temperature: 24.5, severity: 'Info', duration: '3 hours', cause: 'Seasonal ambient increase', status: 'Active', recommendation: 'Monitor trend' }
])

// Filtered hotspots
const filteredHotspots = computed(() => {
  let data = hotspots.value
  if (searchQuery.value) {
    data = data.filter(h => h.location.includes(searchQuery.value) || h.rack.includes(searchQuery.value))
  }
  if (severityFilter.value) {
    data = data.filter(h => h.severity === severityFilter.value)
  }
  return data
})

// Root causes data
const rootCauses = ref([
  { name: 'Airflow Blockage', percentage: 35, severity: 'High', recommendation: 'Install blanking panels, check perforated tiles' },
  { name: 'Equipment Overload', percentage: 28, severity: 'High', recommendation: 'Redistribute load, upgrade cooling' },
  { name: 'CRAC/CRAH Failure', percentage: 18, severity: 'Medium', recommendation: 'Schedule maintenance, activate redundancy' },
  { name: 'Containment Leakage', percentage: 12, severity: 'Medium', recommendation: 'Seal gaps, add brush strips' },
  { name: 'Sensor Calibration', percentage: 7, severity: 'Low', recommendation: 'Recalibrate sensors' }
])

// Resolution history
const resolutionHistory = ref([
  { timestamp: '2024-12-18 09:30:00', location: 'Row B', rack: 'B02', temperature: 26.5, resolution: 'Increased fan speed, cleared blockage', resolvedBy: 'System Auto', duration: '25 min' },
  { timestamp: '2024-12-17 14:20:00', location: 'Row A', rack: 'A01', temperature: 27.1, resolution: 'Redirected airflow, added blanking panel', resolvedBy: 'John Smith', duration: '1.2 hrs' },
  { timestamp: '2024-12-17 11:15:00', location: 'Row D', rack: 'D05', temperature: 25.8, resolution: 'Balanced cooling distribution', resolvedBy: 'System Auto', duration: '35 min' }
])

// AI Predictions
const predictions = ref([
  { location: 'Row B', rack: 'B05', expectedTemp: 26.2, probability: 85, risk: 'High' },
  { location: 'Row A', rack: 'A06', expectedTemp: 25.5, probability: 72, risk: 'Medium' },
  { location: 'Row D', rack: 'D02', expectedTemp: 25.1, probability: 68, risk: 'Medium' }
])

// Recommendations
const recommendations = ref([
  { hotspot: 'Rack A04', recommendation: 'Install blanking panels and increase CRAC setpoint', impact: '-2.5°C', priority: 'High' },
  { hotspot: 'Rack B03', recommendation: 'Activate standby CRAC unit', impact: '-3.0°C', priority: 'High' },
  { hotspot: 'Rack A03', recommendation: 'Clear airflow obstructions', impact: '-1.5°C', priority: 'Medium' },
  { hotspot: 'Rack D04', recommendation: 'Add spot cooling', impact: '-2.0°C', priority: 'Medium' }
])

// Chart refs
const hotspotHeatmapRef = ref<HTMLElement | null>(null)
const hotspotTrendChartRef = ref<HTMLElement | null>(null)
const severityDistributionChartRef = ref<HTMLElement | null>(null)
const rootCauseChartRef = ref<HTMLElement | null>(null)
const predictionChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Helper functions
const getTemperatureColor = (temp: number) => {
  if (temp < 24) return '#10b981'
  if (temp < 26) return '#f59e0b'
  return '#ef4444'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const viewCriticalHotspots = () => {
  severityFilter.value = 'Critical'
  ElMessage.info('Showing critical hotspots')
}

const viewWarningHotspots = () => {
  severityFilter.value = 'Warning'
  ElMessage.info('Showing warning hotspots')
}

const viewHotspotDetails = (hotspot: any) => {
  selectedHotspot.value = hotspot
  detailsDialogVisible.value = true
}

const startInvestigation = (hotspot: any) => {
  ElMessage.info(`Starting investigation for ${hotspot.rack}`)
  detailsDialogVisible.value = false
}

const resolveHotspot = (hotspot: any) => {
  ElMessage.success(`Hotspot ${hotspot.rack} marked as resolved`)
  const index = hotspots.value.findIndex(h => h.id === hotspot.id)
  if (index !== -1) {
    hotspots.value.splice(index, 1)
    activeHotspots.value = hotspots.value.length
    criticalHotspots.value = hotspots.value.filter(h => h.severity === 'Critical').length
    warningHotspots.value = hotspots.value.filter(h => h.severity === 'Warning').length
  }
  detailsDialogVisible.value = false
}

const refreshHeatmap = () => {
  ElMessage.success('Heatmap refreshed')
  initHotspotHeatmap()
}

const exportHotspotData = () => {
  ElMessage.success('Hotspot data export started')
}

const runFullDetection = () => {
  ElMessage.success('Full detection scan started. Results will be available in 2 minutes.')
}

const exportReport = () => {
  ElMessage.success('Hotspot report export started')
}

const schedulePreventiveMaintenance = () => {
  ElMessage.info('Preventive maintenance scheduling interface will open')
}

const preventHotspot = (pred: any) => {
  ElMessage.info(`Preventive action scheduled for ${pred.rack}`)
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied recommendation for ${rec.hotspot}`)
}

// Chart initialization
const initHotspotHeatmap = () => {
  if (hotspotHeatmapRef.value) {
    const chart = echarts.init(hotspotHeatmapRef.value)
    const data: any[] = []

    // Generate heatmap data with hotspot concentrations
    for (let i = 0; i < 20; i++) {
      for (let j = 0; j < 30; j++) {
        let value = 20 + Math.random() * 8
        // Create hotspot concentrations at specific locations
        if ((i === 3 && j === 4) || (i === 4 && j === 3)) value = 28 + Math.random() * 2
        if ((i === 6 && j === 8) || (i === 7 && j === 8)) value = 27 + Math.random() * 2
        if ((i === 12 && j === 15) || (i === 13 && j === 14)) value = 26.5 + Math.random() * 1.5
        data.push([j, i, value])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Temperature: ${params.data[2].toFixed(1)}°C` },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => String(i + 1)), name: 'Rack Position', axisLabel: { rotate: 45, interval: 5 } },
      yAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String.fromCharCode(65 + i)), name: 'Row' },
      visualMap: { min: 20, max: 30, calculable: true, inRange: { color: ['#10b981', '#84cc16', '#f59e0b', '#ef4444', '#7c2d12'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false }, emphasis: { scale: true } }]
    })
    chartInstances.push(chart)
  }
}

const initHotspotTrendChart = () => {
  if (hotspotTrendChartRef.value) {
    const chart = echarts.init(hotspotTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Critical', 'Warning', 'Info'] },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: { type: 'value', name: 'Number of Hotspots' },
      series: [
        { name: 'Critical', type: 'line', data: [3, 2, 2, 1, 2, 3, 4, 5, 4, 3, 2, 2], smooth: true, lineStyle: { color: '#ef4444', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Warning', type: 'line', data: [5, 4, 4, 3, 4, 5, 6, 7, 6, 5, 4, 4], smooth: true, lineStyle: { color: '#f59e0b', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Info', type: 'line', data: [8, 7, 7, 6, 7, 8, 9, 10, 9, 8, 7, 7], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initSeverityDistributionChart = () => {
  if (severityDistributionChartRef.value) {
    const chart = echarts.init(severityDistributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie',
        radius: '55%',
        data: [
          { value: criticalHotspots.value, name: 'Critical', itemStyle: { color: '#ef4444' } },
          { value: warningHotspots.value, name: 'Warning', itemStyle: { color: '#f59e0b' } },
          { value: activeHotspots.value - criticalHotspots.value - warningHotspots.value, name: 'Info', itemStyle: { color: '#409eff' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initRootCauseChart = () => {
  if (rootCauseChartRef.value) {
    const chart = echarts.init(rootCauseChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: rootCauses.value.map(r => r.name), axisLabel: { rotate: 30 } },
      yAxis: { type: 'value', name: 'Percentage (%)' },
      series: [{
        type: 'bar', data: rootCauses.value.map(r => r.percentage),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => rootCauses.value[params.dataIndex].severity === 'High' ? '#ef4444' : '#f59e0b'
        },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initPredictionChart = () => {
  if (predictionChartRef.value) {
    const chart = echarts.init(predictionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Rack B05', 'Rack A06', 'Rack D02', 'Rack C03', 'Rack E01'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [
        { name: 'Current', type: 'bar', data: [24.2, 23.8, 24.0, 23.5, 23.2], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Predicted (24h)', type: 'bar', data: [26.2, 25.5, 25.1, 24.8, 24.5], itemStyle: { color: '#ef4444', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

// Watch for heatmap type changes
const refreshCharts = () => {
  initHotspotHeatmap()
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
        initHotspotHeatmap()
        initHotspotTrendChart()
        initSeverityDistributionChart()
        initRootCauseChart()
        initPredictionChart()
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
.hotspot-detection-container {
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
  border: 1px solid rgba(239, 68, 68, 0.3);
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
.hotspot-detection-container {
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

.alert-banner.critical {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #dc2626;
}

.alert-banner.warning {
  background: #fffbeb;
  border-left: 4px solid #f59e0b;
  color: #d97706;
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

/* Heatmap Section */
.heatmap-section {
  margin-bottom: 24px;
}

.heatmap-card {
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

.heatmap-container {
  min-height: 450px;
}

/* Hotspots Section */
.hotspots-section {
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
  align-items: center;
  flex-wrap: wrap;
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

/* Root Cause List */
.rootcause-list {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.rootcause-list h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.cause-item {
  margin-bottom: 20px;
}

.cause-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.cause-name {
  font-weight: 500;
  color: #303133;
}

.cause-recommendation {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* Predictions List */
.predictions-list {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.predictions-list h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.prediction-item {
  background: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  border-left: 3px solid;
}

.prediction-item.High {
  border-left-color: #ef4444;
}

.prediction-item.Medium {
  border-left-color: #f59e0b;
}

.prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.prediction-location {
  font-weight: 600;
  color: #303133;
}

.prediction-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

.prediction-action {
  text-align: right;
}

/* Recommendation Summary */
.recommendation-summary {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.recommendation-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.auto-action-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.auto-action-settings {
  font-size: 13px;
  color: #606266;
}

.auto-action-settings ul {
  margin: 8px 0 0;
  padding-left: 20px;
}

.auto-action-settings li {
  margin: 4px 0;
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