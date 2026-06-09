<template>
  <div class="battery-strategy-container">
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
            <span class="loading-title">Loading Battery Strategy</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Battery Energy Storage Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Battery Strategy</span>
          <el-tag type="success" effect="dark" size="large">Energy Storage Optimization</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="batteryAlert" class="alert-banner" :class="alertType">
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
                <el-icon><Battery /></el-icon>
                <span>State of Health (SOH)</span>
              </div>
              <div class="card-value">{{ soh }}%</div>
              <div class="card-footer">
                <el-progress :percentage="soh" :stroke-width="8" :color="sohColor" />
                <span class="status-text">Remaining Life: {{ remainingLife }} cycles</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>State of Charge (SOC)</span>
              </div>
              <div class="card-value">{{ soc }}%</div>
              <div class="card-footer">
                <el-progress :percentage="soc" :stroke-width="8" :color="socColor" />
                <span class="status-text">Target: 40-80%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Round Trip Efficiency</span>
              </div>
              <div class="card-value">{{ efficiency }}%</div>
              <div class="card-footer">
                <el-progress :percentage="efficiency" :stroke-width="8" status="success" />
                <span class="status-text">Target: >90%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Coin /></el-icon>
                <span>Cost Savings (YTD)</span>
              </div>
              <div class="card-value">${{ costSavings }}K</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" status="success" />
                <span class="status-text">Peak Shaving + TOU</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Real-Time Monitoring -->
      <div class="monitoring-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="monitoring-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Monitor /></el-icon>
                <span>Battery Real-Time Status</span>
                <el-tag type="success" size="small">Live Data</el-tag>
              </div>
              <div class="battery-stats">
                <div class="stat-big">
                  <span class="stat-label">Total Power</span>
                  <span class="stat-value">{{ totalPower }} kW</span>
                  <el-progress :percentage="(totalPower / maxPower) * 100" :stroke-width="10" :color="powerColor" />
                </div>
                <div class="stat-grid">
                  <div class="stat-item">
                    <span>Voltage</span>
                    <strong>{{ voltage }} V</strong>
                    <el-progress :percentage="(voltage / 800) * 100" :stroke-width="4" :show-text="false" />
                  </div>
                  <div class="stat-item">
                    <span>Current</span>
                    <strong :class="{ warning: Math.abs(current) > 200 }">{{ current }} A</strong>
                    <el-progress :percentage="(Math.abs(current) / 300) * 100" :stroke-width="4" :show-text="false" />
                  </div>
                  <div class="stat-item">
                    <span>Temperature</span>
                    <strong :class="{ warning: temp > 40 }">{{ temp }}°C</strong>
                    <el-progress :percentage="(temp / 60) * 100" :stroke-width="4" :color="tempColor" :show-text="false" />
                  </div>
                  <div class="stat-item">
                    <span>Cell Variance</span>
                    <strong :class="{ warning: cellVariance > 50 }">{{ cellVariance }} mV</strong>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="soc-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Battery /></el-icon>
                <span>State of Charge</span>
              </div>
              <div class="soc-gauge">
                <div ref="socGaugeRef" style="height: 200px"></div>
              </div>
              <div class="soc-details">
                <div class="soc-item">
                  <span>Usable Capacity</span>
                  <strong>{{ usableCapacity }} kWh</strong>
                </div>
                <div class="soc-item">
                  <span>Total Capacity</span>
                  <strong>{{ totalCapacity }} kWh</strong>
                </div>
                <div class="soc-item">
                  <span>Cycle Count</span>
                  <strong>{{ cycleCount }}</strong>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Battery Units Status -->
      <div class="battery-units-section">
        <div class="section-header">
          <h3>Battery Strings Status</h3>
          <div class="header-controls">
            <el-radio-group v-model="unitView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="6" v-for="battery in batteryStrings" :key="battery.id">
            <el-card class="battery-unit-card" :class="`status-${battery.status}`" shadow="hover">
              <div class="battery-header">
                <span class="battery-name">{{ battery.name }}</span>
                <el-tag :type="getBatteryTagType(battery.status)" size="small">{{ battery.status }}</el-tag>
              </div>
              <div class="battery-metrics">
                <div class="metric-row">
                  <div class="metric">
                    <span>SOH</span>
                    <strong>{{ battery.soh }}%</strong>
                    <el-progress :percentage="battery.soh" :stroke-width="4" :color="getSohColor(battery.soh)" :show-text="false" />
                  </div>
                  <div class="metric">
                    <span>SOC</span>
                    <strong>{{ battery.soc }}%</strong>
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Temp</span>
                    <strong :class="{ warning: battery.temp > 40 }">{{ battery.temp }}°C</strong>
                  </div>
                  <div class="metric">
                    <span>Cycles</span>
                    <strong>{{ battery.cycles }}</strong>
                  </div>
                </div>
              </div>
              <div class="battery-footer">
                <el-button type="primary" size="small" @click="viewBatteryDetails(battery)">Details</el-button>
                <el-button size="small" @click="runDiagnostics(battery)">Diagnostics</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="batteryStrings" border v-else style="width: 100%">
          <el-table-column prop="name" label="String" width="100" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getBatteryTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="soh" label="SOH %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.soh" :stroke-width="8" :color="getSohColor(row.soh)" />
            </template>
          </el-table-column>
          <el-table-column prop="soc" label="SOC %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.soc" :stroke-width="8" :color="getSocColor(row.soc)" />
            </template>
          </el-table-column>
          <el-table-column prop="temp" label="Temp (°C)" width="100">
            <template #default="{ row }">
              <span :class="{ warning: row.temp > 40 }">{{ row.temp }}°C</span>
            </template>
          </el-table-column>
          <el-table-column prop="cycles" label="Cycles" width="100" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewBatteryDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="runDiagnostics(row)">Diag</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Charge/Discharge Strategy Tab -->
          <el-tab-pane label="Charge/Discharge Strategy" name="chargeStrategy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Smart Charge/Discharge Strategy</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="chargeStrategyChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="strategy-config">
                    <h4>Time-of-Use Strategy</h4>
                    <el-table :data="touSchedule" border size="small">
                      <el-table-column prop="period" label="Period" width="100" />
                      <el-table-column prop="time" label="Time" />
                      <el-table-column prop="action" label="Action" />
                      <el-table-column prop="rate" label="Rate" width="100" />
                    </el-table>
                    <div class="config-controls">
                      <el-button type="primary" size="small" @click="configureTOU">Edit Schedule</el-button>
                      <el-button size="small" @click="optimizeStrategy">Optimize</el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Health Analysis Tab -->
          <el-tab-pane label="Health Analysis" name="health">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Battery Health & Degradation Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="sohTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="health-metrics">
                    <div class="metric-card">
                      <div class="metric-value">{{ soh }}%</div>
                      <div class="metric-label">Current SOH</div>
                      <el-progress :percentage="soh" :stroke-width="8" :color="sohColor" />
                    </div>
                    <div class="metric-card">
                      <div class="metric-value">{{ degradationRate }}%/year</div>
                      <div class="metric-label">Degradation Rate</div>
                    </div>
                    <div class="metric-card">
                      <div class="metric-value">{{ remainingLife }} months</div>
                      <div class="metric-label">Estimated Remaining Life</div>
                    </div>
                    <div class="prediction-note">
                      <el-icon><InfoFilled /></el-icon>
                      <span>Based on current usage patterns, battery replacement recommended at 70% SOH</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Thermal Management Tab -->
          <el-tab-pane label="Thermal Management" name="thermal">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Sunny /></el-icon>
                <span>Battery Temperature Monitoring</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="tempDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="thermal-stats">
                    <div class="temp-summary">
                      <div class="temp-item">
                        <span>Average Temp</span>
                        <strong :class="{ warning: avgTemp > 35 }">{{ avgTemp }}°C</strong>
                      </div>
                      <div class="temp-item">
                        <span>Max Temp</span>
                        <strong :class="{ warning: maxTemp > 45 }">{{ maxTemp }}°C</strong>
                      </div>
                      <div class="temp-item">
                        <span>Min Temp</span>
                        <strong>{{ minTemp }}°C</strong>
                      </div>
                      <div class="temp-item">
                        <span>Delta Temp</span>
                        <strong :class="{ warning: deltaTemp > 10 }">{{ deltaTemp }}°C</strong>
                      </div>
                    </div>
                    <div class="cooling-status">
                      <h4>Cooling System</h4>
                      <div class="cooling-item">
                        <span>Fan Speed</span>
                        <el-progress :percentage="65" :stroke-width="8" status="success" />
                      </div>
                      <div class="cooling-item">
                        <span>Coolant Temp</span>
                        <el-progress :percentage="70" :stroke-width="8" status="warning" />
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Cycle Life Tab -->
          <el-tab-pane label="Cycle Life" name="cycleLife">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Cycle Life Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="cycleLifeChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="cycle-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ cycleCount }}</div>
                      <div class="stat-label">Total Cycles Completed</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ expectedCycles }}</div>
                      <div class="stat-label">Expected Cycles (to 70% SOH)</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ cyclesRemaining }}</div>
                      <div class="stat-label">Remaining Cycles</div>
                    </div>
                    <div class="cycle-recommendation">
                      <el-progress :percentage="cyclePercentage" :stroke-width="12" :color="cycleProgressColor" />
                      <p>Depth of Discharge (DoD): {{ avgDoD }}%</p>
                      <el-button size="small" type="primary" @click="optimizeCycling">Optimize Cycling</el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Optimization Recommendations Tab -->
          <el-tab-pane label="Recommendations" name="recommendations">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>AI-Powered Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="recommendations" border style="width: 100%">
                    <el-table-column prop="recommendation" label="Recommendation" width="280" />
                    <el-table-column prop="impact" label="Expected Impact" width="140" />
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
                    <div class="potential-value">12.5%</div>
                    <div class="potential-label">Battery Life Extension</div>
                    <el-progress :percentage="12.5" :stroke-width="12" status="success" />
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="runOptimization">
                      Run Full Optimization
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Alerts & Diagnostics Tab -->
          <el-tab-pane label="Alerts & Diagnostics" name="alerts">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Bell /></el-icon>
                <span>Battery Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="batteryAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="string" label="String" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>System Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Cell Balance</span>
                        <el-progress :percentage="85" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Thermal Management</span>
                        <el-progress :percentage="78" :stroke-width="6" status="warning" />
                      </div>
                      <div class="health-item">
                        <span>Charge Efficiency</span>
                        <el-progress :percentage="92" :stroke-width="6" status="success" />
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
        <el-button type="primary" size="large" @click="runDiagnostics">
          <el-icon><Cpu /></el-icon>
          Run Full Diagnostics
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Battery Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Balancing
        </el-button>
      </div>
    </template>

    <!-- Battery Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Battery ${selectedBattery?.name} Details`" width="650px">
      <el-descriptions :column="2" border v-if="selectedBattery">
        <el-descriptions-item label="Status">
          <el-tag :type="getBatteryTagType(selectedBattery.status)">{{ selectedBattery.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Type">Li-ion NMC</el-descriptions-item>
        <el-descriptions-item label="SOH">{{ selectedBattery.soh }}%</el-descriptions-item>
        <el-descriptions-item label="SOC">{{ selectedBattery.soc }}%</el-descriptions-item>
        <el-descriptions-item label="Voltage">{{ selectedBattery.voltage || 720 }} V</el-descriptions-item>
        <el-descriptions-item label="Current">{{ selectedBattery.current || 150 }} A</el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedBattery.temp }}°C</el-descriptions-item>
        <el-descriptions-item label="Cycles">{{ selectedBattery.cycles }}</el-descriptions-item>
        <el-descriptions-item label="Cell Variance">{{ selectedBattery.cellVariance || 35 }} mV</el-descriptions-item>
        <el-descriptions-item label="Internal Resistance">{{ selectedBattery.resistance || 2.5 }} mΩ</el-descriptions-item>
        <el-descriptions-item label="Last Balancing">2024-12-01</el-descriptions-item>
        <el-descriptions-item label="Next Balancing">2025-01-01</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="startBalancing">Start Balancing</el-button>
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
const loadingMessage = ref('Initializing battery systems...')

const loadingMessages = [
  'Initializing battery systems...',
  'Loading health metrics...',
  'Analyzing cell balance...',
  'Calculating cycle life...',
  'Optimizing charge strategy...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('chargeStrategy')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const selectedBattery = ref<any>(null)

// Alert state
const batteryAlert = ref(true)
const alertType = ref('warning')
const alertMessage = ref('Battery String 3 cell voltage imbalance detected (45mV variance)')

// Battery metrics
const soh = ref(86)
const soc = ref(65)
const efficiency = ref(92)
const costSavings = ref(185)
const totalPower = ref(350)
const maxPower = ref(500)
const voltage = ref(725)
const current = ref(-125)
const temp = ref(35)
const cellVariance = ref(38)
const usableCapacity = ref(385)
const totalCapacity = ref(450)
const cycleCount = ref(1850)
const expectedCycles = ref(3500)
const cyclesRemaining = ref(1650)
const avgDoD = ref(65)
const degradationRate = ref(3.2)
const remainingLife = ref(28)
const healthScore = ref(84)

// Temperature metrics
const avgTemp = ref(36.5)
const maxTemp = ref(42)
const minTemp = ref(31)
const deltaTemp = ref(11)

// Computed
const sohColor = computed(() => {
  if (soh.value > 80) return '#67c23a'
  if (soh.value > 70) return '#e6a23c'
  return '#f56c6c'
})

const socColor = computed(() => {
  if (soc.value >= 40 && soc.value <= 80) return '#67c23a'
  return '#e6a23c'
})

const powerColor = computed(() => {
  if (totalPower.value > 0) return '#67c23a'
  return '#409eff'
})

const tempColor = computed(() => {
  if (temp.value < 35) return '#67c23a'
  if (temp.value < 45) return '#e6a23c'
  return '#f56c6c'
})

const cyclePercentage = computed(() => (cycleCount.value / expectedCycles.value) * 100)
const cycleProgressColor = computed(() => {
  if (cyclePercentage.value < 50) return '#67c23a'
  if (cyclePercentage.value < 75) return '#e6a23c'
  return '#f56c6c'
})

const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

// Battery strings data
const batteryStrings = ref([
  { id: 1, name: 'String 1', status: 'Normal', soh: 88, soc: 68, temp: 34, cycles: 1650, voltage: 728, current: 130, cellVariance: 28 },
  { id: 2, name: 'String 2', status: 'Normal', soh: 85, soc: 62, temp: 36, cycles: 1920, voltage: 722, current: 118, cellVariance: 32 },
  { id: 3, name: 'String 3', status: 'Warning', soh: 78, soc: 55, temp: 42, cycles: 2200, voltage: 715, current: 145, cellVariance: 52 },
  { id: 4, name: 'String 4', status: 'Normal', soh: 90, soc: 72, temp: 32, cycles: 1420, voltage: 732, current: 108, cellVariance: 22 }
])

// TOU schedule
const touSchedule = ref([
  { period: 'Peak', time: '09:00-12:00, 18:00-21:00', action: 'Discharge', rate: '$0.25/kWh' },
  { period: 'Shoulder', time: '07:00-09:00, 12:00-18:00', action: 'Standby', rate: '$0.15/kWh' },
  { period: 'Off-Peak', time: '21:00-07:00', action: 'Charge', rate: '$0.08/kWh' }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Perform cell balancing on String 3', impact: '+5% capacity', priority: 'High' },
  { recommendation: 'Adjust charge voltage to reduce degradation', impact: '+15% cycle life', priority: 'High' },
  { recommendation: 'Optimize discharge depth to 50% DoD', impact: '+20% cycle life', priority: 'Medium' },
  { recommendation: 'Improve cooling for String 3', impact: '-5°C temperature', priority: 'Medium' }
])

// Alerts
const batteryAlerts = ref([
  { severity: 'Warning', message: 'Cell voltage imbalance on String 3', string: 'String 3', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'String 1 temperature rising', string: 'String 1', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'SOH below 80% on String 3', string: 'String 3', timestamp: '2024-12-17 22:30' }
])

// Chart refs
const socGaugeRef = ref<HTMLElement | null>(null)
const chargeStrategyChartRef = ref<HTMLElement | null>(null)
const sohTrendChartRef = ref<HTMLElement | null>(null)
const tempDistributionChartRef = ref<HTMLElement | null>(null)
const cycleLifeChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const viewAlertDetails = () => {
  activeTab.value = 'alerts'
  ElMessage.info('Viewing alert details')
}

const getBatteryTagType = (status: string) => {
  if (status === 'Normal') return 'success'
  if (status === 'Warning') return 'warning'
  return 'info'
}

const getSohColor = (sohValue: number) => {
  if (sohValue > 80) return '#67c23a'
  if (sohValue > 70) return '#e6a23c'
  return '#f56c6c'
}

const getSocColor = (socValue: number) => {
  if (socValue >= 40 && socValue <= 80) return '#67c23a'
  return '#e6a23c'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const viewBatteryDetails = (battery: any) => {
  selectedBattery.value = battery
  detailsDialogVisible.value = true
}

const runDiagnostics = (battery: any) => {
  ElMessage.info(`Running diagnostics on ${battery.name}`)
}

const startBalancing = () => {
  ElMessage.success('Cell balancing started. Estimated completion: 2 hours')
  detailsDialogVisible.value = false
}

const configureTOU = () => {
  ElMessage.info('TOU schedule configuration interface will open')
}

const optimizeStrategy = () => {
  ElMessage.success('Charge/discharge strategy optimized based on price signals')
}

const optimizeCycling = () => {
  ElMessage.success('Cycling strategy optimized. Target DoD set to 50%')
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const runDiagnosticsFull = () => {
  ElMessage.success('Full system diagnostics started')
}

const exportReport = () => {
  ElMessage.success('Battery report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Balancing scheduling interface will open')
}

// Chart initialization
const initSocGauge = () => {
  if (socGaugeRef.value) {
    const chart = echarts.init(socGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 0,
        max: 100,
        splitNumber: 5,
        progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
        axisLine: { lineStyle: { width: 18, color: [[0.4, '#f56c6c'], [0.8, '#e6a23c'], [1, '#67c23a']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}%' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12 },
        data: [{ value: soc.value, name: 'SOC' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initChargeStrategyChart = () => {
  if (chargeStrategyChartRef.value) {
    const chart = echarts.init(chargeStrategyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Power (kW)', 'SOC (%)', 'Price ($/kWh)'] },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: [
        { type: 'value', name: 'Power (kW)' },
        { type: 'value', name: 'SOC (%)', min: 0, max: 100 },
        { type: 'value', name: 'Price ($/kWh)', min: 0, max: 0.3 }
      ],
      series: [
        { name: 'Power (kW)', type: 'line', data: [0, 0, 350, 350, 0, -250, -250, -250, -250, 0, 0, 0], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'SOC (%)', type: 'line', yAxisIndex: 1, data: [40, 42, 65, 80, 78, 65, 52, 40, 38, 40, 42, 40], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Price ($/kWh)', type: 'line', yAxisIndex: 2, data: [0.08, 0.08, 0.08, 0.08, 0.15, 0.25, 0.25, 0.25, 0.25, 0.15, 0.08, 0.08], smooth: true, lineStyle: { color: '#f56c6c', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initSohTrendChart = () => {
  if (sohTrendChartRef.value) {
    const chart = echarts.init(sohTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['String 1', 'String 2', 'String 3', 'String 4'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'SOH (%)', min: 70, max: 100 },
      series: [
        { name: 'String 1', type: 'line', data: [96, 95, 94, 93, 92, 91, 90, 90, 89, 89, 88, 88], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'String 2', type: 'line', data: [94, 93, 92, 91, 90, 89, 88, 87, 86, 86, 85, 85], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'String 3', type: 'line', data: [90, 89, 88, 87, 85, 84, 82, 81, 80, 79, 78, 78], smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
        { name: 'String 4', type: 'line', data: [97, 97, 96, 96, 95, 95, 94, 93, 92, 91, 91, 90], smooth: true, lineStyle: { color: '#f56c6c', width: 2 } }
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
      xAxis: { type: 'category', data: ['Cell 1', 'Cell 5', 'Cell 9', 'Cell 13', 'Cell 17', 'Cell 21', 'Cell 25', 'Cell 29', 'Cell 33', 'Cell 37'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [{
        type: 'bar', data: [34, 35, 36, 38, 42, 40, 37, 35, 34, 33],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => {
            const val = params.data
            if (val < 35) return '#67c23a'
            if (val < 40) return '#e6a23c'
            return '#f56c6c'
          }
        },
        label: { show: true, position: 'top', formatter: '{c}°C' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initCycleLifeChart = () => {
  if (cycleLifeChartRef.value) {
    const chart = echarts.init(cycleLifeChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Capacity Retention', 'DoD Impact'] },
      xAxis: { type: 'category', data: ['0', '500', '1000', '1500', '2000', '2500', '3000', '3500', '4000'] },
      yAxis: [
        { type: 'value', name: 'Capacity (%)', min: 60, max: 105 },
        { type: 'value', name: 'DoD (%)', min: 0, max: 100 }
      ],
      series: [
        { name: 'Capacity Retention', type: 'line', data: [100, 96, 92, 88, 84, 80, 76, 72, 68], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'DoD Impact', type: 'line', yAxisIndex: 1, data: [20, 30, 40, 50, 60, 65, 65, 65, 65], smooth: true, lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

// Simulate real-time updates
let realTimeInterval: ReturnType<typeof setInterval>

const startRealTimeUpdates = () => {
  realTimeInterval = setInterval(() => {
    // Simulate changing metrics
    soc.value = Math.max(30, Math.min(90, soc.value + (Math.random() - 0.5) * 2))
    totalPower.value = 300 + Math.random() * 150
    voltage.value = 720 + (Math.random() - 0.5) * 10
    temp.value = 34 + Math.random() * 6
    if (temp.value > 40) batteryAlert.value = true
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
      setTimeout(() => {
        initSocGauge()
        initChargeStrategyChart()
        initSohTrendChart()
        initTempDistributionChart()
        initCycleLifeChart()
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
.battery-strategy-container {
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
.battery-strategy-container {
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

/* Monitoring Section */
.monitoring-section {
  margin-bottom: 24px;
}

.monitoring-card,
.soc-card {
  border-radius: 12px;
  height: 100%;
}

.card-header-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.battery-stats {
  padding: 8px 0;
}

.stat-big {
  text-align: center;
  margin-bottom: 20px;
}

.stat-big .stat-label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-big .stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 12px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-item span {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-item strong {
  font-size: 18px;
  color: #303133;
}

.stat-item strong.warning {
  color: #f56c6c;
}

.soc-details {
  margin-top: 16px;
}

.soc-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #e4e7ed;
}

.soc-item strong {
  color: #409eff;
}

/* Battery Units */
.battery-units-section {
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

.battery-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.battery-unit-card:hover {
  transform: translateY(-2px);
}

.battery-unit-card.status-Normal {
  border-left: 4px solid #67c23a;
}

.battery-unit-card.status-Warning {
  border-left: 4px solid #e6a23c;
}

.battery-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.battery-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.battery-metrics {
  margin-bottom: 16px;
}

.metric-row {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.metric {
  flex: 1;
}

.metric span {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.metric strong {
  font-size: 14px;
  color: #303133;
}

.metric strong.warning {
  color: #f56c6c;
}

.battery-footer {
  display: flex;
  gap: 8px;
  margin-top: 12px;
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

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Strategy Config */
.strategy-config {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.strategy-config h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.config-controls {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

/* Health Metrics */
.health-metrics {
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
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin: 8px 0;
}

.prediction-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #ecf5ff;
  border-radius: 8px;
  font-size: 12px;
  color: #606266;
}

/* Thermal Stats */
.thermal-stats {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.temp-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.temp-item {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
}

.temp-item span {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.temp-item strong {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.temp-item strong.warning {
  color: #f56c6c;
}

.cooling-status h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.cooling-item {
  margin-bottom: 16px;
}

.cooling-item span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

/* Cycle Stats */
.cycle-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.stat-card {
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
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
  margin-top: 4px;
}

.cycle-recommendation {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.cycle-recommendation p {
  margin: 12px 0 0;
  font-size: 13px;
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

/* Diagnostics Panel */
.diagnostics-panel {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  text-align: center;
}

.diagnostics-panel h4 {
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