<template>
  <div class="crah-optimization-container">
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
            <span class="loading-title">Loading CRAH Optimization Dashboard</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Computer Room Air Handler Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header - 无返回按钮 -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">CRAH Optimization</span>
          <el-tag type="primary" effect="dark" size="large">Airflow Management</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><WindPower /></el-icon>
                <span>Airflow Efficiency</span>
              </div>
              <div class="card-value">86%</div>
              <div class="card-footer">
                <el-progress :percentage="86" :stroke-width="8" status="success" :format="() => 'Target: 90%'" />
                <span class="status-text">CFM per kW: 158</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>EC Fan Savings</span>
              </div>
              <div class="card-value">28%</div>
              <div class="card-footer">
                <el-progress :percentage="28" :stroke-width="8" status="success" />
                <span class="status-text">vs. AC Fans</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Coin /></el-icon>
                <span>Pressure Optimization</span>
              </div>
              <div class="card-value">22 Pa</div>
              <div class="card-footer">
                <el-progress :percentage="65" :stroke-width="8" status="warning" :format="() => 'Target: 15 Pa'" />
                <span class="status-text">Static Pressure</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Containment Leakage</span>
              </div>
              <div class="card-value">12%</div>
              <div class="card-footer">
                <el-progress :percentage="12" :stroke-width="8" status="exception" :format="() => 'Target: <5%'" />
                <span class="status-text">Hot Aisle Containment</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Airflow Visualization -->
      <div class="airflow-section">
        <el-card class="airflow-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Connection /></el-icon>
            <span>Airflow Simulation & CFD</span>
            <div class="header-actions">
              <el-button size="small" @click="playSimulation">Play Simulation</el-button>
              <el-button size="small" @click="resetSimulation">Reset</el-button>
              <el-button size="small" type="primary" @click="runCFD">Run CFD Analysis</el-button>
            </div>
          </div>
          <div class="airflow-container">
            <div ref="airflowChartRef" style="height: 450px"></div>
          </div>
        </el-card>
      </div>

      <!-- CRAH Units Status -->
      <div class="crah-units-section">
        <div class="section-header">
          <h3>CRAH Units Status</h3>
          <div class="header-controls">
            <el-radio-group v-model="unitView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="6" v-for="crah in crahUnits" :key="crah.id">
            <el-card class="crah-unit-card" :class="getCrahStatusClass(crah.status)" shadow="hover">
              <div class="crah-header">
                <span class="crah-name">{{ crah.name }}</span>
                <el-tag :type="getCrahTagType(crah.status)" size="small">{{ crah.status }}</el-tag>
              </div>
              <div class="crah-metrics">
                <div class="metric-row">
                  <div class="metric">
                    <span>Airflow</span>
                    <strong>{{ crah.airflow }} CFM</strong>
                  </div>
                  <div class="metric">
                    <span>Fan Speed</span>
                    <strong>{{ crah.fanSpeed }}%</strong>
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Static Pressure</span>
                    <strong>{{ crah.staticPressure }} Pa</strong>
                  </div>
                  <div class="metric">
                    <span>Power</span>
                    <strong>{{ crah.power }} kW</strong>
                  </div>
                </div>
                <div class="metric-progress">
                  <span>Efficiency</span>
                  <el-progress :percentage="crah.efficiency" :stroke-width="6" :color="getEfficiencyColor(crah.efficiency)" />
                </div>
              </div>
              <div class="crah-footer">
                <el-button type="primary" size="small" @click="viewCrahDetails(crah)">Details</el-button>
                <el-button size="small" @click="adjustCrahSettings(crah)">Adjust</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="crahUnits" border v-else style="width: 100%">
          <el-table-column prop="name" label="Unit" width="100" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getCrahTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="airflow" label="Airflow (CFM)" width="120" />
          <el-table-column prop="fanSpeed" label="Fan Speed %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.fanSpeed" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column prop="staticPressure" label="Static Pressure (Pa)" width="140" />
          <el-table-column prop="power" label="Power (kW)" width="100" />
          <el-table-column prop="efficiency" label="Efficiency %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.efficiency" :stroke-width="8" />
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewCrahDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="adjustCrahSettings(row)">Adjust</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Airflow Analytics Tab -->
          <el-tab-pane label="Airflow Analytics" name="analytics">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Airflow & Pressure Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="airflowTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="pressureDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Fan Wall Optimization Tab -->
          <el-tab-pane label="Fan Wall Optimization" name="fanWall">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Cpu /></el-icon>
                <span>EC Fan Wall Control</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="fanWallChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="fan-wall-control">
                    <h4>Fan Wall Configuration</h4>
                    <div class="fan-grid">
                      <div v-for="fan in fanArray" :key="fan.id" class="fan-cell" :class="{ active: fan.active }" @click="toggleFan(fan.id)">
                        <span>Fan {{ fan.id }}</span>
                        <span class="fan-speed">{{ fan.speed }}%</span>
                      </div>
                    </div>
                    <div class="fan-controls">
                      <el-button size="small" @click="setAllFans(60)">Set All to 60%</el-button>
                      <el-button size="small" @click="setAllFans(80)">Set All to 80%</el-button>
                      <el-button size="small" type="primary" @click="applyFanSettings">Apply</el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Containment Optimization Tab -->
          <el-tab-pane label="Containment Optimization" name="containment">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>Hot/Cold Aisle Containment</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="containment-diagram">
                    <div ref="containmentChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="containment-metrics">
                    <h4>Containment Performance</h4>
                    <div class="metric-card">
                      <span>Hot Aisle Containment</span>
                      <el-progress :percentage="88" :stroke-width="10" status="success" />
                    </div>
                    <div class="metric-card">
                      <span>Cold Aisle Containment</span>
                      <el-progress :percentage="92" :stroke-width="10" status="success" />
                    </div>
                    <div class="metric-card">
                      <span>Leakage Rate</span>
                      <el-progress :percentage="12" :stroke-width="10" status="exception" />
                    </div>
                    <div class="recommendations">
                      <h4>Containment Recommendations</h4>
                      <ul>
                        <li>Install brush seals at aisle ends</li>
                        <li>Add missing blanking panels (12 identified)</li>
                        <li>Seal cable cutouts under raised floor</li>
                        <li>Install pressure sensors for monitoring</li>
                      </ul>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Pressure Optimization Tab -->
          <el-tab-pane label="Pressure Optimization" name="pressure">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Gauge /></el-icon>
                <span>Static Pressure Management</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="pressure-card">
                    <h4>Underfloor Pressure</h4>
                    <div class="pressure-value">{{ underfloorPressure }} Pa</div>
                    <el-slider v-model="underfloorPressure" :min="10" :max="50" :step="1" show-input />
                    <div class="pressure-impact">
                      <span>Fan Power Impact: {{ calculateFanPowerImpact(underfloorPressure) }}</span>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="pressure-card">
                    <h4>Plenum Pressure</h4>
                    <div class="pressure-value">{{ plenumPressure }} Pa</div>
                    <el-slider v-model="plenumPressure" :min="5" :max="30" :step="1" show-input />
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="pressure-card">
                    <h4>Differential Pressure</h4>
                    <div class="pressure-value">{{ differentialPressure }} Pa</div>
                    <el-progress :percentage="70" :stroke-width="12" :format="() => `${differentialPressure} Pa`" />
                    <div class="pressure-note">Target: 10-15 Pa for optimal efficiency</div>
                  </div>
                </el-col>
              </el-row>
              <div class="action-buttons-inline">
                <el-button type="primary" @click="applyPressureSettings">Apply Pressure Settings</el-button>
                <el-button @click="optimizePressure">Auto-Optimize Pressure</el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- Energy Savings Tab -->
          <el-tab-pane label="Energy Savings" name="savings">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>CRAH Energy Savings Tracking</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="energySavingsChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="savings-summary">
                    <h4>Optimization Impact</h4>
                    <div class="impact-stat">
                      <span>Fan Energy Reduction</span>
                      <strong>124,000 kWh/year</strong>
                    </div>
                    <div class="impact-stat">
                      <span>Pressure Optimization Savings</span>
                      <strong>45,000 kWh/year</strong>
                    </div>
                    <div class="impact-stat">
                      <span>Containment Improvement</span>
                      <strong>38,000 kWh/year</strong>
                    </div>
                    <div class="impact-stat total">
                      <span>Total Annual Savings</span>
                      <strong>207,000 kWh/year</strong>
                    </div>
                    <div class="carbon-savings">
                      <el-icon><Leaf /></el-icon>
                      <span>Carbon Reduction: 95 tCO₂e/year</span>
                    </div>
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
                <span>System Alerts & Diagnostics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="crahAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="crah" label="CRAH Unit" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>CRAH Fleet Health</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Average Efficiency</span>
                        <el-progress :percentage="82" :stroke-width="6" />
                      </div>
                      <div class="health-item">
                        <span>Fan Bearing Health</span>
                        <el-progress :percentage="88" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Filter Pressure Drop</span>
                        <el-progress :percentage="75" :stroke-width="6" status="warning" />
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
        <el-button type="primary" size="large" @click="runAirflowOptimization">
          <el-icon><Cpu /></el-icon>
          Run AI Airflow Optimization
        </el-button>
        <el-button size="large" @click="exportCFDReport">
          <el-icon><Download /></el-icon>
          Export CFD Report
        </el-button>
        <el-button size="large" @click="scheduleContainmentAudit">
          <el-icon><Tools /></el-icon>
          Schedule Containment Audit
        </el-button>
      </div>
    </template>

    <!-- CRAH Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`CRAH ${selectedCrah?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedCrah">
        <el-descriptions-item label="Status">
          <el-tag :type="getCrahTagType(selectedCrah.status)">{{ selectedCrah.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Location">Row {{ Math.ceil(selectedCrah.id / 2) }}, Position {{ selectedCrah.id }}</el-descriptions-item>
        <el-descriptions-item label="Airflow">{{ selectedCrah.airflow }} CFM</el-descriptions-item>
        <el-descriptions-item label="Fan Speed">{{ selectedCrah.fanSpeed }}%</el-descriptions-item>
        <el-descriptions-item label="Static Pressure">{{ selectedCrah.staticPressure }} Pa</el-descriptions-item>
        <el-descriptions-item label="Power Consumption">{{ selectedCrah.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Efficiency">{{ selectedCrah.efficiency }}%</el-descriptions-item>
        <el-descriptions-item label="EC Fan Model">EC-315-4.0</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">2024-11-10</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">2025-02-10</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Adjust CRAH Settings Dialog -->
    <el-dialog v-model="adjustDialogVisible" title="Adjust CRAH Settings" width="500px">
      <el-form v-if="selectedCrah">
        <el-form-item label="Fan Speed Target">
          <el-slider v-model="adjustFanSpeed" :min="30" :max="100" :step="5" show-input />
        </el-form-item>
        <el-form-item label="Static Pressure Setpoint">
          <el-slider v-model="adjustPressure" :min="10" :max="40" :step="1" show-input />
        </el-form-item>
        <el-form-item label="Control Mode">
          <el-select v-model="adjustMode" placeholder="Select mode">
            <el-option label="Auto (Pressure-based)" value="auto" />
            <el-option label="Manual" value="manual" />
            <el-option label="Schedule-based" value="schedule" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reason for Adjustment">
          <el-input type="textarea" :rows="2" placeholder="Enter reason..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAdjustment">Apply Changes</el-button>
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
const loadingMessage = ref('Initializing CRAH systems...')

const loadingMessages = [
  'Initializing CRAH systems...',
  'Loading airflow simulation...',
  'Analyzing fan wall performance...',
  'Detecting containment issues...',
  'Calculating pressure optimization...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('analytics')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const selectedCrah = ref<any>(null)
const adjustFanSpeed = ref(65)
const adjustPressure = ref(22)
const adjustMode = ref('auto')

// Pressure values
const underfloorPressure = ref(22)
const plenumPressure = ref(18)
const differentialPressure = computed(() => underfloorPressure.value - plenumPressure.value)

// Health score
const healthScore = ref(84)
const healthColor = ref('#67c23a')

// Fan array for fan wall
const fanArray = ref([
  { id: 1, active: true, speed: 75 },
  { id: 2, active: true, speed: 72 },
  { id: 3, active: true, speed: 78 },
  { id: 4, active: true, speed: 70 },
  { id: 5, active: true, speed: 65 },
  { id: 6, active: true, speed: 68 },
  { id: 7, active: false, speed: 0 },
  { id: 8, active: false, speed: 0 },
  { id: 9, active: true, speed: 73 },
  { id: 10, active: true, speed: 71 },
  { id: 11, active: true, speed: 76 },
  { id: 12, active: true, speed: 69 }
])

// CRAH units data
const crahUnits = ref([
  { id: 1, name: 'CRAH-01', status: 'Running', airflow: 12500, fanSpeed: 72, staticPressure: 22, power: 8.5, efficiency: 84 },
  { id: 2, name: 'CRAH-02', status: 'Running', airflow: 11800, fanSpeed: 68, staticPressure: 21, power: 7.8, efficiency: 86 },
  { id: 3, name: 'CRAH-03', status: 'Running', airflow: 13200, fanSpeed: 78, staticPressure: 24, power: 9.2, efficiency: 81 },
  { id: 4, name: 'CRAH-04', status: 'Standby', airflow: 5000, fanSpeed: 35, staticPressure: 12, power: 2.5, efficiency: 0 },
  { id: 5, name: 'CRAH-05', status: 'Running', airflow: 11500, fanSpeed: 65, staticPressure: 20, power: 7.2, efficiency: 87 },
  { id: 6, name: 'CRAH-06', status: 'Running', airflow: 12800, fanSpeed: 75, staticPressure: 23, power: 8.8, efficiency: 83 }
])

// CRAH alerts
const crahAlerts = ref([
  { severity: 'Warning', message: 'High static pressure detected', crah: 'CRAH-03', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'Fan bearing vibration increasing', crah: 'CRAH-01', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'Containment leakage above threshold', crah: 'All', timestamp: '2024-12-17 22:30' },
  { severity: 'Info', message: 'Filter pressure drop nearing limit', crah: 'CRAH-05', timestamp: '2024-12-17 09:30' }
])

// Chart refs
const airflowChartRef = ref<HTMLElement | null>(null)
const airflowTrendChartRef = ref<HTMLElement | null>(null)
const pressureDistributionChartRef = ref<HTMLElement | null>(null)
const fanWallChartRef = ref<HTMLElement | null>(null)
const containmentChartRef = ref<HTMLElement | null>(null)
const energySavingsChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []
let simulationInterval: ReturnType<typeof setInterval>

// Methods
const getCrahStatusClass = (status: string) => {
  if (status === 'Running') return 'status-running'
  if (status === 'Standby') return 'status-standby'
  return ''
}

const getCrahTagType = (status: string) => {
  if (status === 'Running') return 'success'
  if (status === 'Standby') return 'warning'
  return 'info'
}

const getEfficiencyColor = (efficiency: number) => {
  if (efficiency >= 85) return '#67c23a'
  if (efficiency >= 75) return '#e6a23c'
  return '#f56c6c'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const calculateFanPowerImpact = (pressure: number) => {
  const basePower = 7.5
  const power = basePower * (pressure / 20)
  return `${power.toFixed(1)} kW (+${((power - basePower) / basePower * 100).toFixed(0)}%)`
}

const playSimulation = () => {
  ElMessage.success('Airflow simulation started')
  if (simulationInterval) clearInterval(simulationInterval)
  let step = 0
  simulationInterval = setInterval(() => {
    step++
    if (step > 20) {
      clearInterval(simulationInterval)
    }
  }, 200)
}

const resetSimulation = () => {
  if (simulationInterval) clearInterval(simulationInterval)
  ElMessage.info('Simulation reset')
}

const runCFD = () => {
  ElMessage.success('CFD analysis started. Results will be available in a few minutes.')
}

const toggleFan = (fanId: number) => {
  const fan = fanArray.value.find(f => f.id === fanId)
  if (fan) {
    fan.active = !fan.active
    fan.speed = fan.active ? 60 : 0
  }
}

const setAllFans = (speed: number) => {
  fanArray.value.forEach(fan => {
    fan.active = speed > 0
    fan.speed = speed
  })
}

const applyFanSettings = () => {
  ElMessage.success('Fan wall settings applied')
}

const viewCrahDetails = (crah: any) => {
  selectedCrah.value = crah
  detailsDialogVisible.value = true
}

const adjustCrahSettings = (crah: any) => {
  selectedCrah.value = crah
  adjustFanSpeed.value = crah.fanSpeed
  adjustPressure.value = crah.staticPressure
  adjustDialogVisible.value = true
}

const confirmAdjustment = () => {
  if (selectedCrah.value) {
    selectedCrah.value.fanSpeed = adjustFanSpeed.value
    selectedCrah.value.staticPressure = adjustPressure.value
    ElMessage.success(`CRAH ${selectedCrah.value.name} settings updated`)
  }
  adjustDialogVisible.value = false
}

const applyPressureSettings = () => {
  ElMessage.success(`Pressure settings applied: Underfloor ${underfloorPressure.value} Pa, Plenum ${plenumPressure.value} Pa`)
}

const optimizePressure = () => {
  underfloorPressure.value = 18
  plenumPressure.value = 14
  ElMessage.success('Pressure optimized to recommended values')
}

const runAirflowOptimization = () => {
  ElMessage.success('AI airflow optimization started. Results will be available shortly.')
}

const exportCFDReport = () => {
  ElMessage.success('CFD report export started')
}

const scheduleContainmentAudit = () => {
  ElMessage.info('Containment audit scheduling interface will open')
}

// Chart initialization
const initAirflowChart = () => {
  if (airflowChartRef.value) {
    const chart = echarts.init(airflowChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['CRAH-01', 'CRAH-02', 'CRAH-03', 'CRAH-04', 'CRAH-05', 'CRAH-06'] },
      yAxis: { type: 'value', name: 'Airflow (CFM)' },
      series: [{
        type: 'bar', data: [12500, 11800, 13200, 5000, 11500, 12800],
        itemStyle: { borderRadius: [8, 8, 0, 0], color: '#409eff' },
        label: { show: true, position: 'top', formatter: '{c} CFM' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initAirflowTrendChart = () => {
  if (airflowTrendChartRef.value) {
    const chart = echarts.init(airflowTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['CRAH-01', 'CRAH-02', 'CRAH-03', 'CRAH-05', 'CRAH-06'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: { type: 'value', name: 'Airflow (CFM)' },
      series: [
        { name: 'CRAH-01', type: 'line', data: [12500, 12400, 12600, 12500, 12650, 12550], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'CRAH-02', type: 'line', data: [11800, 11700, 11900, 11800, 11950, 11850], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'CRAH-03', type: 'line', data: [13200, 13100, 13300, 13200, 13350, 13250], smooth: true, lineStyle: { color: '#e6a23c', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPressureDistributionChart = () => {
  if (pressureDistributionChartRef.value) {
    const chart = echarts.init(pressureDistributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Row A', 'Row B', 'Row C', 'Row D', 'Row E'] },
      yAxis: { type: 'value', name: 'Static Pressure (Pa)' },
      series: [{
        type: 'bar', data: [22, 21, 25, 20, 23],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#3b82f6' },
              { offset: 0.5, color: '#10b981' },
              { offset: 1, color: '#f59e0b' }
            ]
          }
        },
        label: { show: true, position: 'top', formatter: '{c} Pa' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initFanWallChart = () => {
  if (fanWallChartRef.value) {
    const chart = echarts.init(fanWallChartRef.value)
    const fanSpeeds = fanArray.value.map(f => f.speed)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: fanArray.value.map(f => `Fan ${f.id}`) },
      yAxis: { type: 'value', name: 'Fan Speed (%)', max: 100 },
      series: [{
        type: 'bar', data: fanSpeeds,
        itemStyle: { borderRadius: [8, 8, 0, 0], color: (params: any) => fanSpeeds[params.dataIndex] > 0 ? '#409eff' : '#909399' },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initContainmentChart = () => {
  if (containmentChartRef.value) {
    const chart = echarts.init(containmentChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '60%',
        min: 0,
        max: 100,
        progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
        axisLine: { lineStyle: { width: 18, color: [[0.88, '#67c23a'], [1, '#e6a23c']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: false },
        title: { show: true, offsetCenter: [0, -30], fontSize: 14 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 24, formatter: '88%' },
        data: [{ value: 88, name: 'Hot Aisle Containment' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initEnergySavingsChart = () => {
  if (energySavingsChartRef.value) {
    const chart = echarts.init(energySavingsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Baseline', 'Optimized'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Energy (kWh)' },
      series: [
        { name: 'Baseline', type: 'line', data: [18500, 18200, 18600, 19000, 19500, 20000, 20500, 20300, 19800, 19200, 18600, 18200], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Optimized', type: 'line', data: [16800, 16500, 16900, 17200, 17600, 18000, 18400, 18200, 17800, 17200, 16800, 16500], lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } }
      ]
    })
    chartInstances.push(chart)
  }
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
        initAirflowChart()
        initAirflowTrendChart()
        initPressureDistributionChart()
        initFanWallChart()
        initContainmentChart()
        initEnergySavingsChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (simulationInterval) clearInterval(simulationInterval)
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.crah-optimization-container {
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
  border-top-color: #409eff;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #10b981;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #f59e0b;
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
  background: linear-gradient(90deg, #409eff, #10b981, #f59e0b);
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
/* Page Header - 无返回按钮 */
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

/* Airflow Section */
.airflow-section {
  margin-bottom: 24px;
}

.airflow-card {
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

.airflow-container {
  min-height: 450px;
}

/* CRAH Units */
.crah-units-section {
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

.crah-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.crah-unit-card:hover {
  transform: translateY(-2px);
}

.crah-unit-card.status-running {
  border-left: 4px solid #67c23a;
}

.crah-unit-card.status-standby {
  border-left: 4px solid #e6a23c;
}

.crah-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.crah-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.crah-metrics {
  margin-bottom: 16px;
}

.metric-row {
  display: flex;
  gap: 12px;
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

.metric-progress {
  margin-top: 8px;
}

.metric-progress span {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-bottom: 4px;
}

.crah-footer {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

/* Fan Wall Control */
.fan-wall-control {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.fan-wall-control h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.fan-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.fan-cell {
  background: white;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid #e4e7ed;
}

.fan-cell.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.fan-cell span:first-child {
  display: block;
  font-size: 12px;
  color: #606266;
}

.fan-speed {
  font-size: 14px;
  font-weight: 600;
  color: #409eff;
}

.fan-controls {
  display: flex;
  gap: 8px;
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

/* Containment Metrics */
.containment-metrics {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.containment-metrics h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.metric-card {
  margin-bottom: 20px;
}

.metric-card span {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.recommendations {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.recommendations ul {
  margin: 8px 0 0;
  padding-left: 20px;
}

.recommendations li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

/* Pressure Cards */
.pressure-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  text-align: center;
}

.pressure-card h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.pressure-value {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
  margin-bottom: 16px;
}

.pressure-impact {
  margin-top: 16px;
  font-size: 12px;
  color: #909399;
}

.pressure-note {
  margin-top: 16px;
  font-size: 12px;
  color: #909399;
}

/* Action Buttons */
.action-buttons-inline {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.action-buttons {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.action-buttons .el-button {
  border-radius: 8px;
}

/* Savings Summary */
.savings-summary {
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.savings-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.impact-stat {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.impact-stat.total {
  border-bottom: none;
  font-size: 16px;
  font-weight: 600;
  padding-top: 16px;
}

.impact-stat.total strong {
  font-size: 20px;
  color: #409eff;
}

.carbon-savings {
  margin-top: 20px;
  padding-top: 16px;
  text-align: center;
  border-top: 2px solid #e4e7ed;
}

.carbon-savings .el-icon {
  font-size: 20px;
  color: #67c23a;
  margin-right: 8px;
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

/* Deep Selectors */
:deep(.el-tabs--border-card) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-progress__text) {
  font-size: 12px;
}

:deep(.el-dialog__body) {
  padding-top: 0;
}
</style>