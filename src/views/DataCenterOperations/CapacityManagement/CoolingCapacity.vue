<template>
  <div class="cooling-capacity-container">
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
            <span class="loading-title">Loading Cooling Capacity</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Cooling Capacity Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Cooling Capacity</span>
          <el-tag type="info" effect="dark" size="large">Thermal Management</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="coolingAlert" class="alert-banner" :class="alertType">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ alertMessage }}</span>
        <el-button size="small" :type="alertType === 'critical' ? 'danger' : 'warning'" @click="viewAlertDetails">
          View Details
        </el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Sunny /></el-icon>
                <span>Total Cooling Capacity</span>
              </div>
              <div class="card-value">{{ totalCooling }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="coolingUtilization" :stroke-width="8" :color="coolingColor" />
                <span class="status-text">Utilization: {{ coolingUtilization }}%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Sunny /></el-icon>
                <span>Current Heat Load</span>
              </div>
              <div class="card-value">{{ currentHeatLoad }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="(currentHeatLoad / totalCooling) * 100" :stroke-width="8" :color="heatColor" />
                <span class="status-text">Peak: {{ peakHeatLoad }} kW</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Share /></el-icon>
                <span>Redundant Cooling</span>
              </div>
              <div class="card-value">{{ redundantCooling }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="(redundantCooling / totalCooling) * 100" :stroke-width="8" :color="redundantColor" />
                <span class="status-text">N+1 Redundancy</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Cooling PUE</span>
              </div>
              <div class="card-value">{{ coolingPue }}</div>
              <div class="card-footer">
                <el-progress :percentage="(1 - (coolingPue - 1)) * 100" :stroke-width="8" status="success" :format="() => `Target: 1.20`" />
                <span class="status-text">IT Load: {{ itLoad }} kW</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Cooling Distribution Chart -->
      <div class="distribution-section">
        <el-card class="distribution-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Connection /></el-icon>
            <span>Cooling Distribution by Row</span>
            <el-radio-group v-model="distributionType" size="small">
              <el-radio-button label="heatLoad">Heat Load</el-radio-button>
              <el-radio-button label="coolingCapacity">Cooling Capacity</el-radio-button>
              <el-radio-button label="utilization">Utilization</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-container">
            <div ref="distributionChartRef" style="height: 350px"></div>
          </div>
        </el-card>
      </div>

      <!-- Cooling Topology -->
      <div class="topology-section">
        <el-card class="topology-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Share /></el-icon>
            <span>Cooling System Topology</span>
            <div class="header-actions">
              <el-button size="small" @click="zoomInTopology">Zoom In</el-button>
              <el-button size="small" @click="zoomOutTopology">Zoom Out</el-button>
              <el-button size="small" type="primary" @click="exportTopology">Export</el-button>
            </div>
          </div>
          <div class="topology-container">
            <div ref="topologyChartRef" style="height: 400px"></div>
          </div>
        </el-card>
      </div>

      <!-- CRAC/CRAH Units Status -->
      <div class="crac-section">
        <div class="section-header">
          <h3>Cooling Units Status</h3>
          <div class="header-controls">
            <el-input v-model="searchQuery" placeholder="Search unit..." prefix-icon="Search" style="width: 200px" clearable />
            <el-button type="primary" @click="exportUnitData">Export Data</el-button>
          </div>
        </div>
        <el-table :data="filteredCracUnits" border style="width: 100%">
          <el-table-column prop="name" label="Unit"  />
          <el-table-column prop="row" label="Row"  />
          <el-table-column label="Cooling Capacity">
            <template #default="{ row }">
              <el-progress :percentage="(row.currentLoad / row.capacity) * 100" :stroke-width="10" :color="getUtilColor(row.currentLoad / row.capacity)" />
              <span class="progress-text">{{ row.currentLoad }}/{{ row.capacity }} kW</span>
            </template>
          </el-table-column>
          <el-table-column prop="supplyTemp" label="Supply Temp">
            <template #default="{ row }">
              <span :class="{ warning: row.supplyTemp > 24 }">{{ row.supplyTemp }}°C</span>
            </template>
          </el-table-column>
          <el-table-column prop="returnTemp" label="Return Temp">
            <template #default="{ row }">
              <span :class="{ warning: row.returnTemp > 32 }">{{ row.returnTemp }}°C</span>
            </template>
          </el-table-column>
          <el-table-column prop="fanSpeed" label="Fan Speed" >
            <template #default="{ row }">
              <el-progress :percentage="row.fanSpeed" :stroke-width="8" :color="getFanColor(row.fanSpeed)" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" >
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" >
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewUnitDetail(row)">Details</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Temperature Heatmap Tab -->
          <el-tab-pane label="Temperature Heatmap" name="heatmap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>Data Hall Temperature Heatmap</span>
              </div>
              <div class="chart-container">
                <div ref="heatmapChartRef" style="height: 450px"></div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Cooling Trends Tab -->
          <el-tab-pane label="Cooling Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Cooling & Temperature Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="coolingTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="pueTrendChartRef" style="height: 350px"></div>
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
                <span>Cooling Demand Forecast</span>
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
                      <div class="stat-label">Required Cooling Upgrade</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ growthRate }}%</div>
                      <div class="stat-label">Annual Heat Load Growth</div>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="generateUpgradePlan">
                      Generate Upgrade Plan
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Efficiency Analysis Tab -->
          <el-tab-pane label="Efficiency Analysis" name="efficiency">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>Cooling Efficiency Metrics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="efficiencyChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="efficiency-metrics">
                    <div class="metric-card">
                      <div class="metric-value">{{ cop }} COP</div>
                      <div class="metric-label">Chiller COP</div>
                      <el-progress :percentage="(cop / 6) * 100" :stroke-width="8" :color="copColor" />
                    </div>
                    <div class="metric-card">
                      <div class="metric-value">{{ eer }} EER</div>
                      <div class="metric-label">CRAC EER</div>
                      <el-progress :percentage="(eer / 15) * 100" :stroke-width="8" :color="eerColor" />
                    </div>
                    <div class="metric-card">
                      <div class="metric-value">{{ freeCoolingHours }} hrs</div>
                      <div class="metric-label">Free Cooling Hours (YTD)</div>
                    </div>
                    <el-button type="primary" size="small" style="margin-top: 16px" @click="optimizeEfficiency">
                      Optimize Efficiency
                    </el-button>
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
                <span>Cooling Optimization Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="recommendations" border style="width: 100%">
                    <el-table-column prop="recommendation" label="Recommendation" width="300" />
                    <el-table-column prop="impact" label="Expected Impact" width="140" />
                    <el-table-column prop="priority" label="Priority" >
                      <template #default="{ row }">
                        <el-tag :type="row.priority === 'High' ? 'danger' : 'warning'" size="small">
                          {{ row.priority }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="Action" >
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="applyRecommendation(row)">Apply</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="8">
                  <div class="recommendation-summary">
                    <h4>Total Improvement Potential</h4>
                    <div class="potential-value">{{ totalPotential }}%</div>
                    <div class="potential-label">Cooling Efficiency Gain</div>
                    <el-progress :percentage="totalPotential" :stroke-width="12" status="success" />
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
                <span>Cooling Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="coolingAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" >
                      <template #default="{ row }">
                        <el-tag :type="getAlertSeverityType(row.severity)" size="small">
                          {{ row.severity }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Message" />
                    <el-table-column prop="location" label="Location"  />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="health-panel">
                    <h4>Cooling Health Score</h4>
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
                        <el-progress :percentage="90" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Efficiency Health</span>
                        <el-progress :percentage="82" :stroke-width="6" status="warning" />
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
        <el-button type="primary" size="large" @click="runCoolingAnalysis">
          <el-icon><Cpu /></el-icon>
          Run Cooling Analysis
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Calendar /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </template>

    <!-- Unit Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Cooling Unit ${selectedUnit?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedUnit">
        <el-descriptions-item label="Location">Row {{ selectedUnit.row }}, Position {{ selectedUnit.position }}</el-descriptions-item>
        <el-descriptions-item label="Capacity">{{ selectedUnit.capacity }} kW</el-descriptions-item>
        <el-descriptions-item label="Current Load">{{ selectedUnit.currentLoad }} kW</el-descriptions-item>
        <el-descriptions-item label="Utilization">{{ ((selectedUnit.currentLoad / selectedUnit.capacity) * 100).toFixed(0) }}%</el-descriptions-item>
        <el-descriptions-item label="Supply Temp">{{ selectedUnit.supplyTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Return Temp">{{ selectedUnit.returnTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Fan Speed">{{ selectedUnit.fanSpeed }}%</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedUnit.status)">{{ selectedUnit.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">{{ selectedUnit.lastMaintenance || '2024-11-15' }}</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">{{ selectedUnit.nextMaintenance || '2025-02-15' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="adjustSettings">Adjust Settings</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Sunny, Share, Cpu, Connection, Grid,
  TrendCharts, DataAnalysis, Setting, Bell, WarningFilled,
  Search, Download, Calendar, Tools, Monitor, Location
} from '@element-plus/icons-vue'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading cooling capacity data...')

const loadingMessages = [
  'Loading cooling capacity data...',
  'Analyzing heat distribution...',
  'Calculating efficiency metrics...',
  'Generating heatmap...',
  'Forecasting cooling demand...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('heatmap')
const distributionType = ref('heatLoad')
const searchQuery = ref('')
const detailDialogVisible = ref(false)
const selectedUnit = ref<any>(null)
const coolingAlert = ref(true)
const alertType = ref('warning')
const alertMessage = ref('Row B cooling capacity at 85% utilization. Consider adding supplemental cooling.')

// Cooling metrics
const totalCooling = ref(1200)
const currentHeatLoad = ref(785)
const peakHeatLoad = ref(850)
const redundantCooling = ref(415)
const coolingUtilization = computed(() => Math.round((currentHeatLoad.value / totalCooling.value) * 100))
const coolingPue = ref(1.42)
const itLoad = ref(550)
const monthsUntilFull = ref(8)
const requiredUpgrade = ref(200)
const growthRate = ref(6.5)
const cop = ref(5.2)
const eer = ref(11.5)
const freeCoolingHours = ref(2850)
const totalPotential = ref(12.5)
const healthScore = ref(86)
const capacityHealth = ref(78)

// Colors
const coolingColor = computed(() => {
  if (coolingUtilization.value < 70) return '#67c23a'
  if (coolingUtilization.value < 85) return '#e6a23c'
  return '#f56c6c'
})

const heatColor = computed(() => {
  const pct = (currentHeatLoad.value / totalCooling.value) * 100
  if (pct < 70) return '#67c23a'
  if (pct < 85) return '#e6a23c'
  return '#f56c6c'
})

const redundantColor = computed(() => {
  const pct = (redundantCooling.value / totalCooling.value) * 100
  if (pct > 30) return '#67c23a'
  if (pct > 15) return '#e6a23c'
  return '#f56c6c'
})

const copColor = computed(() => {
  if (cop.value > 5.5) return '#67c23a'
  if (cop.value > 4.5) return '#e6a23c'
  return '#f56c6c'
})

const eerColor = computed(() => {
  if (eer.value > 12) return '#67c23a'
  if (eer.value > 10) return '#e6a23c'
  return '#f56c6c'
})

const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

// Row data for distribution
const rowHeatData = ref([
  { row: 'Row A', heatLoad: 165, coolingCapacity: 200, utilization: 82.5 },
  { row: 'Row B', heatLoad: 185, coolingCapacity: 200, utilization: 92.5 },
  { row: 'Row C', heatLoad: 145, coolingCapacity: 200, utilization: 72.5 },
  { row: 'Row D', heatLoad: 125, coolingCapacity: 200, utilization: 62.5 },
  { row: 'Row E', heatLoad: 155, coolingCapacity: 200, utilization: 77.5 }
])

// CRAC/CRAH units
const cracUnits = ref([
  { id: 1, name: 'CRAC-01', row: 'A', position: 1, capacity: 100, currentLoad: 82, supplyTemp: 22.5, returnTemp: 28.5, fanSpeed: 68, status: 'Normal', lastMaintenance: '2024-11-15', nextMaintenance: '2025-02-15' },
  { id: 2, name: 'CRAC-02', row: 'A', position: 2, capacity: 100, currentLoad: 83, supplyTemp: 22.8, returnTemp: 29.0, fanSpeed: 70, status: 'Normal', lastMaintenance: '2024-11-15', nextMaintenance: '2025-02-15' },
  { id: 3, name: 'CRAC-03', row: 'B', position: 1, capacity: 100, currentLoad: 92, supplyTemp: 23.5, returnTemp: 30.5, fanSpeed: 85, status: 'Warning', lastMaintenance: '2024-11-10', nextMaintenance: '2025-02-10' },
  { id: 4, name: 'CRAC-04', row: 'B', position: 2, capacity: 100, currentLoad: 93, supplyTemp: 23.8, returnTemp: 31.0, fanSpeed: 88, status: 'Warning', lastMaintenance: '2024-11-10', nextMaintenance: '2025-02-10' },
  { id: 5, name: 'CRAH-01', row: 'C', position: 1, capacity: 100, currentLoad: 72, supplyTemp: 22.0, returnTemp: 27.5, fanSpeed: 60, status: 'Normal', lastMaintenance: '2024-11-20', nextMaintenance: '2025-02-20' },
  { id: 6, name: 'CRAH-02', row: 'C', position: 2, capacity: 100, currentLoad: 73, supplyTemp: 22.2, returnTemp: 27.8, fanSpeed: 62, status: 'Normal', lastMaintenance: '2024-11-20', nextMaintenance: '2025-02-20' },
  { id: 7, name: 'CRAH-03', row: 'D', position: 1, capacity: 100, currentLoad: 62, supplyTemp: 21.5, returnTemp: 26.5, fanSpeed: 52, status: 'Normal', lastMaintenance: '2024-11-25', nextMaintenance: '2025-02-25' },
  { id: 8, name: 'CRAH-04', row: 'D', position: 2, capacity: 100, currentLoad: 63, supplyTemp: 21.8, returnTemp: 26.8, fanSpeed: 54, status: 'Normal', lastMaintenance: '2024-11-25', nextMaintenance: '2025-02-25' }
])

const filteredCracUnits = computed(() => {
  if (!searchQuery.value) return cracUnits.value
  return cracUnits.value.filter(u => u.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

// Recommendations
const recommendations = ref([
  { recommendation: 'Add supplemental cooling to Row B (current utilization 92.5%)', impact: '+50kW capacity', priority: 'High' },
  { recommendation: 'Increase free cooling usage during night hours', impact: 'Reduce PUE by 0.05', priority: 'High' },
  { recommendation: 'Optimize CRAC setpoints based on IT load', impact: 'Save 8% energy', priority: 'Medium' },
  { recommendation: 'Schedule maintenance for CRAC-03 and CRAC-04', impact: 'Improve efficiency by 5%', priority: 'Medium' }
])

// Cooling alerts
const coolingAlerts = ref([
  { severity: 'Warning', message: 'Row B cooling capacity at 92.5% utilization', location: 'Row B', timestamp: '2024-12-18 14:23' },
  { severity: 'Warning', message: 'CRAC-03 return temperature high (30.5°C)', location: 'CRAC-03', timestamp: '2024-12-18 10:15' },
  { severity: 'Info', message: 'Free cooling available for next 6 hours', location: 'Economizer', timestamp: '2024-12-18 08:30' }
])

// Helper functions
const getUtilColor = (ratio: number) => {
  if (ratio < 0.7) return '#67c23a'
  if (ratio < 0.85) return '#e6a23c'
  return '#f56c6c'
}

const getFanColor = (speed: number) => {
  if (speed < 60) return '#67c23a'
  if (speed < 80) return '#e6a23c'
  return '#f56c6c'
}

const getStatusType = (status: string) => {
  if (status === 'Normal') return 'success'
  if (status === 'Warning') return 'warning'
  return 'danger'
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

const viewAlertDetails = () => {
  activeTab.value = 'alerts'
}

const exportUnitData = () => {
  ElMessage.success('Unit data export started')
}

const exportTopology = () => {
  ElMessage.success('Topology export started')
}

const zoomInTopology = () => {
  ElMessage.info('Zoom in feature')
}

const zoomOutTopology = () => {
  ElMessage.info('Zoom out feature')
}

const viewUnitDetail = (unit: any) => {
  selectedUnit.value = unit
  detailDialogVisible.value = true
}

const adjustSettings = () => {
  ElMessage.info(`Adjusting settings for ${selectedUnit.value.name}`)
  detailDialogVisible.value = false
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('Cooling optimization started')
}

const runCoolingAnalysis = () => {
  ElMessage.success('Full cooling analysis started')
}

const exportReport = () => {
  ElMessage.success('Cooling report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

const generateUpgradePlan = () => {
  ElMessage.success('Upgrade plan generated')
}

const optimizeEfficiency = () => {
  ElMessage.success('Efficiency optimization started')
}

// Chart refs
const distributionChartRef = ref<HTMLElement | null>(null)
const topologyChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)
const coolingTrendChartRef = ref<HTMLElement | null>(null)
const pueTrendChartRef = ref<HTMLElement | null>(null)
const forecastChartRef = ref<HTMLElement | null>(null)
const efficiencyChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Chart initialization
const initDistributionChart = () => {
  if (distributionChartRef.value) {
    const chart = echarts.init(distributionChartRef.value)
    let data: any = {}
    if (distributionType.value === 'heatLoad') {
      data = {
        xAxis: { type: 'category', data: rowHeatData.value.map(r => r.row) },
        yAxis: { type: 'value', name: 'Heat Load (kW)' },
        series: [{ type: 'bar', data: rowHeatData.value.map(r => r.heatLoad), itemStyle: { color: '#f56c6c', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} kW' } }]
      }
    } else if (distributionType.value === 'coolingCapacity') {
      data = {
        xAxis: { type: 'category', data: rowHeatData.value.map(r => r.row) },
        yAxis: { type: 'value', name: 'Cooling Capacity (kW)' },
        series: [{ type: 'bar', data: rowHeatData.value.map(r => r.coolingCapacity), itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c} kW' } }]
      }
    } else {
      data = {
        xAxis: { type: 'category', data: rowHeatData.value.map(r => r.row) },
        yAxis: { type: 'value', name: 'Utilization (%)', max: 100 },
        series: [{ type: 'bar', data: rowHeatData.value.map(r => r.utilization), itemStyle: { color: (params: any) => getUtilColor(params.data / 100), borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } }]
      }
    }
    chart.setOption(data)
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
          { name: 'Chillers' }, { name: 'Cooling Towers' }, { name: 'Primary Pumps' },
          { name: 'Secondary Pumps' }, { name: 'CRAC Row A' }, { name: 'CRAC Row B' },
          { name: 'CRAH Row C' }, { name: 'CRAH Row D' }, { name: 'Data Hall' }
        ],
        links: [
          { source: 'Chillers', target: 'Primary Pumps', value: 1200 },
          { source: 'Cooling Towers', target: 'Chillers', value: 1200 },
          { source: 'Primary Pumps', target: 'Secondary Pumps', value: 1200 },
          { source: 'Secondary Pumps', target: 'CRAC Row A', value: 300 },
          { source: 'Secondary Pumps', target: 'CRAC Row B', value: 300 },
          { source: 'Secondary Pumps', target: 'CRAH Row C', value: 300 },
          { source: 'Secondary Pumps', target: 'CRAH Row D', value: 300 },
          { source: 'CRAC Row A', target: 'Data Hall', value: 165 },
          { source: 'CRAC Row B', target: 'Data Hall', value: 185 },
          { source: 'CRAH Row C', target: 'Data Hall', value: 145 },
          { source: 'CRAH Row D', target: 'Data Hall', value: 125 }
        ],
        lineStyle: { color: 'gradient', curveness: 0.5 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initHeatmapChart = () => {
  if (heatmapChartRef.value) {
    const chart = echarts.init(heatmapChartRef.value)
    const data: any[] = []
    const rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    const cols = Array.from({ length: 12 }, (_, i) => i + 1)

    for (let i = 0; i < rows.length; i++) {
      for (let j = 0; j < cols.length; j++) {
        let value = 22 + Math.random() * 6
        if (i === 1 && j === 3) value = 28.5
        if (i === 1 && j === 4) value = 27.5
        if (i === 3 && j === 7) value = 26.0
        if (i === 5 && j === 2) value = 25.5
        data.push([j, i, value])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Rack ${rows[params.data[1]]}${cols[params.data[0]]}<br/>Temperature: ${params.data[2].toFixed(1)}°C` },
      xAxis: { type: 'category', data: cols, name: 'Position' },
      yAxis: { type: 'category', data: rows, name: 'Row' },
      visualMap: { min: 20, max: 30, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#84cc16', '#f59e0b', '#ef4444', '#7c2d12'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false }, emphasis: { scale: true } }]
    })
    chartInstances.push(chart)
  }
}

const initCoolingTrendChart = () => {
  if (coolingTrendChartRef.value) {
    const chart = echarts.init(coolingTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Cooling Capacity', 'Heat Load', 'Redundant Capacity'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        { name: 'Cooling Capacity', type: 'line', data: [1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Heat Load', type: 'area', data: [650, 670, 690, 710, 730, 750, 770, 785, 800, 810, 820, 830], smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Redundant Capacity', type: 'area', data: [550, 530, 510, 490, 470, 450, 430, 415, 400, 390, 380, 370], smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPueTrendChart = () => {
  if (pueTrendChartRef.value) {
    const chart = echarts.init(pueTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Actual PUE', 'Target PUE', 'Cooling PUE Component'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
      series: [
        { name: 'Actual PUE', type: 'line', data: [1.48, 1.47, 1.46, 1.45, 1.44, 1.43, 1.42, 1.41, 1.40, 1.39, 1.38, 1.37], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Target PUE', type: 'line', data: [1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35], lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Cooling PUE Component', type: 'line', data: [0.42, 0.41, 0.40, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31], smooth: true, lineStyle: { color: '#67c23a', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initForecastChart = () => {
  if (forecastChartRef.value) {
    const chart = echarts.init(forecastChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Historical Heat Load', 'Forecast Heat Load', 'Cooling Capacity'] },
      xAxis: { type: 'category', data: ['2024 Q1', '2024 Q2', '2024 Q3', '2024 Q4', '2025 Q1', '2025 Q2', '2025 Q3', '2025 Q4'] },
      yAxis: { type: 'value', name: 'Cooling Load (kW)' },
      series: [
        { name: 'Historical Heat Load', type: 'line', data: [650, 690, 730, 770, null, null, null, null], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Forecast Heat Load', type: 'line', data: [null, null, null, 770, 800, 830, 860, 890], smooth: true, lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Cooling Capacity', type: 'line', data: [1200, 1200, 1200, 1200, 1200, 1200, 1200, 1200], lineStyle: { color: '#f56c6c', width: 2, type: 'dotted' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initEfficiencyChart = () => {
  if (efficiencyChartRef.value) {
    const chart = echarts.init(efficiencyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['CRAC Efficiency', 'Chiller COP', 'Free Cooling %'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: [
        { type: 'value', name: 'Efficiency (%)', min: 60, max: 100 },
        { type: 'value', name: 'COP', min: 4, max: 6 },
        { type: 'value', name: 'Free Cooling %', min: 0, max: 100 }
      ],
      series: [
        { name: 'CRAC Efficiency', type: 'line', data: [85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'Chiller COP', type: 'line', yAxisIndex: 1, data: [4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Free Cooling %', type: 'line', yAxisIndex: 2, data: [45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 98], smooth: true, lineStyle: { color: '#f59e0b', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initAllCharts = () => {
  initDistributionChart()
  initTopologyChart()
  initHeatmapChart()
  initCoolingTrendChart()
  initPueTrendChart()
  initForecastChart()
  initEfficiencyChart()
}

const handleResize = () => {
  chartInstances.forEach(chart => {
    try { chart.resize() } catch (e) {}
  })
}

// Watch for distribution type changes
watch(distributionType, () => {
  initDistributionChart()
})

// Watch for tab changes to resize charts
watch(activeTab, () => {
  nextTick(() => {
    setTimeout(() => {
      chartInstances.forEach(chart => {
        try { chart.resize() } catch (e) {}
      })
    }, 100)
  })
})

// Simulate real-time updates
let realTimeInterval: ReturnType<typeof setInterval>

const startRealTimeUpdates = () => {
  realTimeInterval = setInterval(() => {
    currentHeatLoad.value = 780 + Math.random() * 10
    const idx = Math.floor(Math.random() * cracUnits.value.length)
    cracUnits.value[idx].currentLoad = 70 + Math.random() * 25
  }, 5000)
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
      nextTick(() => {
        setTimeout(() => {
          initAllCharts()
          startRealTimeUpdates()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (realTimeInterval) clearInterval(realTimeInterval)
  chartInstances.forEach(chart => {
    try { chart.dispose() } catch (e) {}
  })
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.cooling-capacity-container {
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
.cooling-capacity-container {
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

/* CRAC Section */
.crac-section {
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

.progress-text {
  display: block;
  text-align: center;
  font-size: 11px;
  margin-top: 4px;
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

/* Efficiency Metrics */
.efficiency-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.metric-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.metric-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin: 8px 0;
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

/* Warning text */
.warning {
  color: #f56c6c;
}
</style>