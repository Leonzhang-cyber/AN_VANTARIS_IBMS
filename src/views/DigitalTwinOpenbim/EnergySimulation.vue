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
        <div class="loading-tip">Digital Twin - Energy Simulation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="energy-simulation-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <h1>Energy Simulation</h1>
        <p>Predict and optimize building energy performance with AI-driven simulation models</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="runSimulation" :loading="isSimulating">
          <el-icon><VideoPlay /></el-icon>
          Run Simulation
        </el-button>
        <el-button @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button @click="resetParameters">
          <el-icon><RefreshLeft /></el-icon>
          Reset
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon primary-bg">
            <el-icon><Lightning /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.annualConsumption }}<span class="stat-unit">MWh</span></div>
            <div class="stat-label">Annual Consumption</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon success-bg">
            <el-icon><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">+{{ stats.potentialSavings }}%</div>
            <div class="stat-label">Potential Savings</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon warning-bg">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.simulationTime }}<span class="stat-unit">s</span></div>
            <div class="stat-label">Simulation Time</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <div class="stat-card">
          <div class="stat-icon info-bg">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.modelAccuracy }}%</div>
            <div class="stat-label">Model Accuracy</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Main Content Row -->
    <el-row :gutter="20">
      <!-- Simulation Parameters -->
      <el-col :xs="24" :lg="8">
        <div class="params-card">
          <div class="card-header">
            <h3>Simulation Parameters</h3>
            <el-tooltip content="Configure building and environmental parameters" placement="top">
              <el-icon><InfoFilled /></el-icon>
            </el-tooltip>
          </div>

          <el-tabs v-model="activeParamTab">
            <el-tab-pane label="Building" name="building">
              <el-form label-width="130px" class="param-form">
                <el-form-item label="Floor Area">
                  <el-input-number v-model="params.floorArea" :min="500" :max="50000" :step="500" style="width: 100%" />
                  <span class="param-unit">m²</span>
                </el-form-item>
                <el-form-item label="Building Height">
                  <el-input-number v-model="params.buildingHeight" :min="3" :max="50" :step="1" style="width: 100%" />
                  <span class="param-unit">m</span>
                </el-form-item>
                <el-form-item label="Window-to-Wall Ratio">
                  <el-slider v-model="params.windowRatio" :min="0" :max="60" :step="5" />
                  <span class="param-hint">{{ params.windowRatio }}%</span>
                </el-form-item>
                <el-form-item label="Insulation Level">
                  <el-select v-model="params.insulationLevel" style="width: 100%">
                    <el-option label="Poor" value="poor" />
                    <el-option label="Standard" value="standard" />
                    <el-option label="Good" value="good" />
                    <el-option label="Excellent" value="excellent" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Building Type">
                  <el-select v-model="params.buildingType" style="width: 100%">
                    <el-option label="Office" value="office" />
                    <el-option label="Commercial" value="commercial" />
                    <el-option label="Industrial" value="industrial" />
                    <el-option label="Data Center" value="datacenter" />
                    <el-option label="Hospital" value="hospital" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="HVAC" name="hvac">
              <el-form label-width="130px" class="param-form">
                <el-form-item label="Cooling Setpoint">
                  <el-slider v-model="params.coolingSetpoint" :min="18" :max="26" :step="0.5" />
                  <span class="param-hint">{{ params.coolingSetpoint }}°C</span>
                </el-form-item>
                <el-form-item label="Heating Setpoint">
                  <el-slider v-model="params.heatingSetpoint" :min="16" :max="24" :step="0.5" />
                  <span class="param-hint">{{ params.heatingSetpoint }}°C</span>
                </el-form-item>
                <el-form-item label="HVAC Efficiency">
                  <el-slider v-model="params.hvacEfficiency" :min="0.5" :max="1" :step="0.05" :format-tooltip="(val) => `${(val * 100).toFixed(0)}%`" />
                  <span class="param-hint">{{ (params.hvacEfficiency * 100).toFixed(0) }}%</span>
                </el-form-item>
                <el-form-item label="System Type">
                  <el-select v-model="params.hvacType" style="width: 100%">
                    <el-option label="VAV with Reheat" value="vav" />
                    <el-option label="Fan Coil Units" value="fcu" />
                    <el-option label="Chilled Water" value="chilled_water" />
                    <el-option label="Heat Pump" value="heat_pump" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Schedule">
                  <el-select v-model="params.schedule" style="width: 100%">
                    <el-option label="24/7 Operation" value="24_7" />
                    <el-option label="Weekdays Only" value="weekdays" />
                    <el-option label="Business Hours (8-18)" value="business" />
                    <el-option label="Optimized" value="optimized" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="Lighting" name="lighting">
              <el-form label-width="130px" class="param-form">
                <el-form-item label="Lighting Power Density">
                  <el-slider v-model="params.lightingDensity" :min="5" :max="20" :step="0.5" />
                  <span class="param-hint">{{ params.lightingDensity }} W/m²</span>
                </el-form-item>
                <el-form-item label="Occupancy Sensors">
                  <el-switch v-model="params.occupancySensors" />
                  <span class="param-hint">Enable motion-based control</span>
                </el-form-item>
                <el-form-item label="Daylight Harvesting">
                  <el-switch v-model="params.daylightHarvesting" />
                  <span class="param-hint">Reduce lighting near windows</span>
                </el-form-item>
                <el-form-item label="Lighting Schedule">
                  <el-select v-model="params.lightingSchedule" style="width: 100%">
                    <el-option label="Fixed Schedule" value="fixed" />
                    <el-option label="Occupancy-Based" value="occupancy" />
                    <el-option label="Time-Based Dimming" value="dimming" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="Climate" name="climate">
              <el-form label-width="130px" class="param-form">
                <el-form-item label="Climate Zone">
                  <el-select v-model="params.climateZone" style="width: 100%">
                    <el-option label="Tropical (Hot & Humid)" value="tropical" />
                    <el-option label="Temperate" value="temperate" />
                    <el-option label="Continental" value="continental" />
                    <el-option label="Mediterranean" value="mediterranean" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Annual Temp Avg">
                  <el-slider v-model="params.avgTemp" :min="0" :max="30" :step="1" />
                  <span class="param-hint">{{ params.avgTemp }}°C</span>
                </el-form-item>
                <el-form-item label="Cooling Degree Days">
                  <el-input-number v-model="params.cdd" :min="500" :max="5000" :step="100" style="width: 100%" />
                </el-form-item>
                <el-form-item label="Heating Degree Days">
                  <el-input-number v-model="params.hdd" :min="500" :max="5000" :step="100" style="width: 100%" />
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <el-divider />

          <div class="run-section">
            <el-button type="primary" size="large" @click="runSimulation" :loading="isSimulating" style="width: 100%">
              <el-icon><VideoPlay /></el-icon>
              Run Energy Simulation
            </el-button>
            <el-progress v-if="isSimulating" :percentage="simProgress" :status="simProgress === 100 ? 'success' : undefined" style="margin-top: 12px" />
          </div>
        </div>
      </el-col>

      <!-- Simulation Results -->
      <el-col :xs="24" :lg="16">
        <div class="results-card">
          <div class="card-header">
            <h3>Simulation Results</h3>
            <div class="result-tabs">
              <el-radio-group v-model="resultView" size="small">
                <el-radio-button value="overview">Overview</el-radio-button>
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="hourly">Hourly</el-radio-button>
                <el-radio-button value="breakdown">Breakdown</el-radio-button>
              </el-radio-group>
            </div>
          </div>

          <!-- Overview View -->
          <div v-if="resultView === 'overview'" class="overview-view">
            <el-row :gutter="16" class="kpi-row">
              <el-col :span="8">
                <div class="kpi-card">
                  <div class="kpi-value">{{ simulationResults.totalEnergy }}<span class="kpi-unit">MWh</span></div>
                  <div class="kpi-label">Total Energy</div>
                  <div class="kpi-trend" :class="simulationResults.energyTrend > 0 ? 'negative' : 'positive'">
                    {{ simulationResults.energyTrend > 0 ? '+' : '' }}{{ simulationResults.energyTrend }}% vs baseline
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="kpi-card">
                  <div class="kpi-value">{{ simulationResults.peakDemand }}<span class="kpi-unit">kW</span></div>
                  <div class="kpi-label">Peak Demand</div>
                  <div class="kpi-trend" :class="simulationResults.demandTrend > 0 ? 'negative' : 'positive'">
                    {{ simulationResults.demandTrend > 0 ? '+' : '' }}{{ simulationResults.demandTrend }}% vs baseline
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="kpi-card">
                  <div class="kpi-value">${{ simulationResults.annualCost }}<span class="kpi-unit">k</span></div>
                  <div class="kpi-label">Annual Cost</div>
                  <div class="kpi-trend" :class="simulationResults.costTrend > 0 ? 'negative' : 'positive'">
                    {{ simulationResults.costTrend > 0 ? '+' : '' }}{{ simulationResults.costTrend }}% vs baseline
                  </div>
                </div>
              </el-col>
            </el-row>

            <div class="chart-container">
              <div ref="overviewChartRef" class="chart"></div>
            </div>

            <div class="recommendations">
              <h4>AI Recommendations</h4>
              <div class="recommendation-list">
                <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
                  <el-icon :class="rec.type"><component :is="rec.icon" /></el-icon>
                  <div class="rec-content">
                    <div class="rec-title">{{ rec.title }}</div>
                    <div class="rec-description">{{ rec.description }}</div>
                  </div>
                  <div class="rec-savings">{{ rec.savings }}% savings</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Monthly View -->
          <div v-if="resultView === 'monthly'" class="monthly-view">
            <div ref="monthlyChartRef" class="chart"></div>
            <el-table :data="monthlyData" stripe size="small" class="monthly-table">
              <el-table-column prop="month" label="Month" width="80" />
              <el-table-column prop="cooling" label="Cooling (kWh)" sortable />
              <el-table-column prop="heating" label="Heating (kWh)" sortable />
              <el-table-column prop="lighting" label="Lighting (kWh)" sortable />
              <el-table-column prop="equipment" label="Equipment (kWh)" sortable />
              <el-table-column prop="total" label="Total (kWh)" sortable />
            </el-table>
          </div>

          <!-- Hourly View -->
          <div v-if="resultView === 'hourly'" class="hourly-view">
            <div class="hourly-controls">
              <el-select v-model="selectedMonth" placeholder="Select Month" size="small" style="width: 120px">
                <el-option v-for="(m, idx) in months" :key="idx" :label="m" :value="idx" />
              </el-select>
              <el-select v-model="selectedDayType" placeholder="Day Type" size="small" style="width: 120px">
                <el-option label="Weekday" value="weekday" />
                <el-option label="Weekend" value="weekend" />
              </el-select>
            </div>
            <div ref="hourlyChartRef" class="chart"></div>
          </div>

          <!-- Breakdown View -->
          <div v-if="resultView === 'breakdown'" class="breakdown-view">
            <el-row :gutter="16">
              <el-col :span="12">
                <div ref="breakdownChartRef" class="pie-chart"></div>
              </el-col>
              <el-col :span="12">
                <div class="breakdown-table">
                  <div v-for="item in breakdownData" :key="item.name" class="breakdown-item">
                    <div class="breakdown-label">
                      <span class="color-dot" :style="{ backgroundColor: item.color }"></span>
                      <span>{{ item.name }}</span>
                    </div>
                    <div class="breakdown-bar">
                      <el-progress :percentage="item.percentage" :color="item.color" :show-text="false" :stroke-width="8" />
                    </div>
                    <div class="breakdown-value">{{ item.value }} MWh</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- Scenario Comparison -->
    <div class="comparison-card">
      <div class="card-header">
        <h3>Scenario Comparison</h3>
        <el-button size="small" @click="addComparisonScenario">+ Add Scenario</el-button>
      </div>
      <div class="comparison-grid">
        <div v-for="(scenario, idx) in comparisonScenarios" :key="idx" class="comparison-item">
          <div class="comparison-header">
            <span class="scenario-name">{{ scenario.name }}</span>
            <el-button link type="danger" size="small" @click="removeComparisonScenario(idx)" v-if="idx > 0">×</el-button>
          </div>
          <div class="comparison-stats">
            <div>Energy: {{ scenario.energy }} MWh</div>
            <div>Cost: ${{ scenario.cost }}k</div>
            <div>Carbon: {{ scenario.carbon }} tons</div>
          </div>
          <div class="comparison-delta" v-if="idx > 0">
            <span :class="scenario.energy < comparisonScenarios[0].energy ? 'positive' : 'negative'">
              {{ ((scenario.energy - comparisonScenarios[0].energy) / comparisonScenarios[0].energy * 100).toFixed(1) }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Dialog -->
    <el-dialog v-model="exportDialog.visible" title="Export Simulation Report" width="500px">
      <el-form>
        <el-form-item label="Report Format">
          <el-radio-group v-model="exportFormat">
            <el-radio label="pdf">PDF Report</el-radio>
            <el-radio label="excel">Excel Data</el-radio>
            <el-radio label="json">JSON Export</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Include">
          <el-checkbox-group v-model="exportIncludes">
            <el-checkbox label="charts">Charts & Visualizations</el-checkbox>
            <el-checkbox label="rawData">Raw Simulation Data</el-checkbox>
            <el-checkbox label="recommendations">AI Recommendations</el-checkbox>
            <el-checkbox label="parameters">Parameter Settings</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportDialog.visible = false">Cancel</el-button>
        <el-button type="primary" @click="generateExport">Export</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  VideoPlay,
  Download,
  RefreshLeft,
  Lightning,
  TrendCharts,
  Timer,
  DataAnalysis,
  InfoFilled,
  Sunny,
  List,
  Check,
  WarningFilled
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const isSimulating = ref(false)
const simProgress = ref(0)
const resultView = ref('overview')
const activeParamTab = ref('building')
const selectedMonth = ref(6)
const selectedDayType = ref('weekday')
const exportFormat = ref('pdf')
const exportIncludes = ref(['charts', 'recommendations'])

const loadingMessages = [
  'Preparing...',
  'Loading energy models...',
  'Initializing simulation engine...',
  'Almost ready...'
]

// ==================== 参数定义 ====================
const params = reactive({
  // Building
  floorArea: 10000,
  buildingHeight: 12,
  windowRatio: 30,
  insulationLevel: 'standard',
  buildingType: 'office',
  // HVAC
  coolingSetpoint: 22,
  heatingSetpoint: 20,
  hvacEfficiency: 0.85,
  hvacType: 'vav',
  schedule: 'business',
  // Lighting
  lightingDensity: 10,
  occupancySensors: true,
  daylightHarvesting: true,
  lightingSchedule: 'occupancy',
  // Climate
  climateZone: 'temperate',
  avgTemp: 15,
  cdd: 1200,
  hdd: 2500
})

// ==================== 模拟结果 ====================
const simulationResults = reactive({
  totalEnergy: 1250,
  peakDemand: 450,
  annualCost: 187.5,
  energyTrend: -12.5,
  demandTrend: -8.3,
  costTrend: -12.5,
  carbonEmissions: 312,
  eui: 125
})

const monthlyData = ref([
  { month: 'Jan', cooling: 120, heating: 450, lighting: 85, equipment: 120, total: 775 },
  { month: 'Feb', cooling: 150, heating: 420, lighting: 80, equipment: 115, total: 765 },
  { month: 'Mar', cooling: 250, heating: 350, lighting: 75, equipment: 120, total: 795 },
  { month: 'Apr', cooling: 380, heating: 250, lighting: 70, equipment: 118, total: 818 },
  { month: 'May', cooling: 520, heating: 150, lighting: 65, equipment: 125, total: 860 },
  { month: 'Jun', cooling: 650, heating: 80, lighting: 60, equipment: 130, total: 920 },
  { month: 'Jul', cooling: 720, heating: 50, lighting: 58, equipment: 135, total: 963 },
  { month: 'Aug', cooling: 700, heating: 60, lighting: 60, equipment: 132, total: 952 },
  { month: 'Sep', cooling: 550, heating: 120, lighting: 65, equipment: 128, total: 863 },
  { month: 'Oct', cooling: 380, heating: 220, lighting: 70, equipment: 122, total: 792 },
  { month: 'Nov', cooling: 220, heating: 380, lighting: 78, equipment: 118, total: 796 },
  { month: 'Dec', cooling: 130, heating: 480, lighting: 82, equipment: 115, total: 807 }
])

const breakdownData = ref([
  { name: 'HVAC Cooling', value: 478, percentage: 38.2, color: '#409eff' },
  { name: 'HVAC Heating', value: 301, percentage: 24.1, color: '#f56c6c' },
  { name: 'Lighting', value: 165, percentage: 13.2, color: '#e6a23c' },
  { name: 'Equipment', value: 185, percentage: 14.8, color: '#67c23a' },
  { name: 'Other', value: 121, percentage: 9.7, color: '#8c9aab' }
])

const recommendations = ref([
  { id: 1, type: 'success', icon: 'Sunny', title: 'Upgrade to LED Lighting', description: 'Replace existing lighting with high-efficiency LEDs', savings: 18 },
  { id: 2, type: 'warning', icon: 'TrendCharts', title: 'Optimize HVAC Scheduling', description: 'Adjust setpoints during unoccupied hours', savings: 22 },
  { id: 3, type: 'primary', icon: 'DataAnalysis', title: 'Install Occupancy Sensors', description: 'Reduce lighting and HVAC in low-traffic areas', savings: 15 },
  { id: 4, type: 'success', icon: 'Check', title: 'Improve Building Envelope', description: 'Add insulation and seal air leaks', savings: 12 }
])

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

const comparisonScenarios = ref([
  { name: 'Baseline', energy: 1420, cost: 213, carbon: 355 },
  { name: 'Optimized', energy: 1250, cost: 187.5, carbon: 312 }
])

const stats = reactive({
  annualConsumption: 1250,
  potentialSavings: 18,
  simulationTime: 2.4,
  modelAccuracy: 94.7
})

const exportDialog = reactive({
  visible: false
})

// ==================== 图表引用 ====================
const overviewChartRef = ref<HTMLElement | null>(null)
const monthlyChartRef = ref<HTMLElement | null>(null)
const hourlyChartRef = ref<HTMLElement | null>(null)
const breakdownChartRef = ref<HTMLElement | null>(null)

let overviewChart: echarts.ECharts | null = null
let monthlyChart: echarts.ECharts | null = null
let hourlyChart: echarts.ECharts | null = null
let breakdownChart: echarts.ECharts | null = null

// ==================== 图表渲染 ====================
const renderOverviewChart = () => {
  if (!overviewChartRef.value) return
  if (overviewChart) overviewChart.dispose()

  overviewChart = echarts.init(overviewChartRef.value)

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const coolingData = Array.from({ length: 24 }, () => 40 + Math.random() * 60)
  const lightingData = Array.from({ length: 24 }, () => 15 + Math.random() * 25)
  const equipmentData = Array.from({ length: 24 }, () => 20 + Math.random() * 30)

  overviewChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Cooling', 'Lighting', 'Equipment'], bottom: 0 },
    xAxis: { type: 'category', data: hours, name: 'Hour' },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [
      { name: 'Cooling', type: 'line', smooth: true, data: coolingData, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Lighting', type: 'line', smooth: true, data: lightingData, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Equipment', type: 'line', smooth: true, data: equipmentData, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.1 } }
    ]
  })
}

const renderMonthlyChart = () => {
  if (!monthlyChartRef.value) return
  if (monthlyChart) monthlyChart.dispose()

  monthlyChart = echarts.init(monthlyChartRef.value)

  monthlyChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Cooling', 'Heating', 'Lighting', 'Equipment'], top: 0 },
    xAxis: { type: 'category', data: monthlyData.value.map(d => d.month) },
    yAxis: { type: 'value', name: 'Energy (kWh)' },
    series: [
      { name: 'Cooling', type: 'bar', data: monthlyData.value.map(d => d.cooling), stack: 'total', itemStyle: { color: '#409eff' } },
      { name: 'Heating', type: 'bar', data: monthlyData.value.map(d => d.heating), stack: 'total', itemStyle: { color: '#f56c6c' } },
      { name: 'Lighting', type: 'bar', data: monthlyData.value.map(d => d.lighting), stack: 'total', itemStyle: { color: '#e6a23c' } },
      { name: 'Equipment', type: 'bar', data: monthlyData.value.map(d => d.equipment), stack: 'total', itemStyle: { color: '#67c23a' } }
    ]
  })
}

const renderHourlyChart = () => {
  if (!hourlyChartRef.value) return
  if (hourlyChart) hourlyChart.dispose()

  hourlyChart = echarts.init(hourlyChartRef.value)

  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const data = Array.from({ length: 24 }, () => 30 + Math.random() * 70)

  hourlyChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: hours },
    yAxis: { type: 'value', name: 'Power (kW)' },
    series: [{ type: 'line', data: data, smooth: true, areaStyle: { opacity: 0.3 }, lineStyle: { color: '#409eff', width: 2 } }]
  })
}

const renderBreakdownChart = () => {
  if (!breakdownChartRef.value) return
  if (breakdownChart) breakdownChart.dispose()

  breakdownChart = echarts.init(breakdownChartRef.value)

  breakdownChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} MWh)' },
    legend: { orient: 'vertical', left: 'left', top: 'center' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '55%'],
      data: breakdownData.value.map(d => ({ name: d.name, value: d.value, itemStyle: { color: d.color } })),
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  })
}

// ==================== 模拟运行 ====================
const runSimulation = async () => {
  if (isSimulating.value) return

  isSimulating.value = true
  simProgress.value = 0

  const interval = setInterval(() => {
    if (simProgress.value < 100) {
      simProgress.value += Math.random() * 15 + 5
      if (simProgress.value > 100) simProgress.value = 100
    }
  }, 200)

  await new Promise(resolve => setTimeout(resolve, 2500))

  clearInterval(interval)
  simProgress.value = 100

  // Update results with random variations based on parameters
  const baseEnergy = 1250
  const hvacAdjust = (params.coolingSetpoint - 22) * -20 + (22 - params.heatingSetpoint) * -15
  const lightingAdjust = (10 - params.lightingDensity) * 15
  const efficiencyAdjust = (params.hvacEfficiency - 0.85) * -200
  const insulationAdjust = params.insulationLevel === 'excellent' ? -150 : params.insulationLevel === 'good' ? -80 : params.insulationLevel === 'poor' ? 100 : 0

  let totalAdjust = hvacAdjust + lightingAdjust + efficiencyAdjust + insulationAdjust
  totalAdjust = Math.min(300, Math.max(-300, totalAdjust))

  simulationResults.totalEnergy = Math.max(800, Math.min(2000, baseEnergy + totalAdjust))
  simulationResults.peakDemand = Math.floor(simulationResults.totalEnergy / 3.5)
  simulationResults.annualCost = parseFloat((simulationResults.totalEnergy * 0.15).toFixed(1))
  simulationResults.energyTrend = parseFloat(((simulationResults.totalEnergy - 1420) / 1420 * 100).toFixed(1))
  simulationResults.costTrend = simulationResults.energyTrend

  stats.annualConsumption = simulationResults.totalEnergy
  stats.potentialSavings = Math.floor(Math.random() * 25) + 10
  stats.simulationTime = parseFloat((Math.random() * 2 + 1.5).toFixed(1))

  ElMessage.success('Energy simulation completed successfully')

  // Refresh charts
  nextTick(() => {
    renderOverviewChart()
    renderMonthlyChart()
    renderHourlyChart()
    renderBreakdownChart()
  })
}

const resetParameters = () => {
  params.floorArea = 10000
  params.buildingHeight = 12
  params.windowRatio = 30
  params.insulationLevel = 'standard'
  params.buildingType = 'office'
  params.coolingSetpoint = 22
  params.heatingSetpoint = 20
  params.hvacEfficiency = 0.85
  params.hvacType = 'vav'
  params.schedule = 'business'
  params.lightingDensity = 10
  params.occupancySensors = true
  params.daylightHarvesting = true
  params.lightingSchedule = 'occupancy'
  params.climateZone = 'temperate'
  params.avgTemp = 15
  params.cdd = 1200
  params.hdd = 2500

  ElMessage.info('Parameters reset to default values')
}

const addComparisonScenario = () => {
  const newScenario = {
    name: `Scenario ${comparisonScenarios.value.length + 1}`,
    energy: Math.floor(1000 + Math.random() * 600),
    cost: parseFloat((Math.random() * 100 + 100).toFixed(1)),
    carbon: Math.floor(200 + Math.random() * 200)
  }
  comparisonScenarios.value.push(newScenario)
  ElMessage.success('Scenario added for comparison')
}

const removeComparisonScenario = (index: number) => {
  comparisonScenarios.value.splice(index, 1)
}

const exportReport = () => {
  exportDialog.visible = true
}

const generateExport = () => {
  const exportData = {
    generatedAt: new Date().toISOString(),
    parameters: params,
    results: simulationResults,
    monthlyData: monthlyData.value,
    breakdown: breakdownData.value,
    recommendations: recommendations.value
  }

  const data = JSON.stringify(exportData, null, 2)
  const blob = new Blob([data], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `energy-simulation-${new Date().toISOString().slice(0, 19)}.json`
  a.click()
  URL.revokeObjectURL(url)

  exportDialog.visible = false
  ElMessage.success('Report exported successfully')
}

// ==================== 数据加载 ====================
const loadData = () => {
  nextTick(() => {
    renderOverviewChart()
    renderMonthlyChart()
    renderHourlyChart()
    renderBreakdownChart()
  })
}

// ==================== 生命周期 ====================
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
      loadData()
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    overviewChart?.resize()
    monthlyChart?.resize()
    hourlyChart?.resize()
    breakdownChart?.resize()
  })
})

watch([resultView, selectedMonth, selectedDayType], () => {
  nextTick(() => {
    if (resultView.value === 'overview') renderOverviewChart()
    if (resultView.value === 'monthly') renderMonthlyChart()
    if (resultView.value === 'hourly') renderHourlyChart()
    if (resultView.value === 'breakdown') renderBreakdownChart()
  })
})

watch(isLoaded, (loaded) => {
  if (loaded) {
    window.addEventListener('resize', () => {
      overviewChart?.resize()
      monthlyChart?.resize()
      hourlyChart?.resize()
      breakdownChart?.resize()
    })
  }
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
  font-size: 28px;
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

/* ==================== Main Content Styles ==================== */
.energy-simulation-page {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.page-header p {
  margin: 0;
  color: #5e6e82;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.primary-bg { background-color: #ecf5ff; color: #409eff; }
.success-bg { background-color: #f0f9eb; color: #67c23a; }
.warning-bg { background-color: #fff3e0; color: #e6a23c; }
.info-bg { background-color: #f5f7fa; color: #8c9aab; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2f3d;
  line-height: 1.2;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #8c9aab;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 4px;
}

/* Parameters Card */
.params-card, .results-card, .comparison-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2f3d;
}

.param-form {
  margin-top: 8px;
}

.param-unit, .param-hint {
  margin-left: 8px;
  font-size: 12px;
  color: #8c9aab;
}

.run-section {
  margin-top: 8px;
}

/* Results */
.kpi-row {
  margin-bottom: 24px;
}

.kpi-card {
  text-align: center;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.kpi-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2f3d;
}

.kpi-unit {
  font-size: 14px;
  font-weight: normal;
  color: #8c9aab;
  margin-left: 4px;
}

.kpi-label {
  font-size: 13px;
  color: #8c9aab;
  margin-top: 8px;
}

.kpi-trend {
  font-size: 11px;
  margin-top: 4px;
}

.kpi-trend.positive { color: #67c23a; }
.kpi-trend.negative { color: #f56c6c; }

.chart-container, .chart {
  height: 320px;
  width: 100%;
  margin-bottom: 20px;
}

.pie-chart {
  height: 280px;
  width: 100%;
}

/* Recommendations */
.recommendations h4 {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: #1f2f3d;
}

.recommendation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.recommendation-item .el-icon {
  font-size: 20px;
}

.recommendation-item .el-icon.success { color: #67c23a; }
.recommendation-item .el-icon.warning { color: #e6a23c; }
.recommendation-item .el-icon.primary { color: #409eff; }

.rec-content {
  flex: 1;
}

.rec-title {
  font-weight: 500;
  font-size: 13px;
  color: #1f2f3d;
}

.rec-description {
  font-size: 11px;
  color: #8c9aab;
}

.rec-savings {
  font-size: 12px;
  font-weight: 600;
  color: #67c23a;
}

/* Monthly Table */
.monthly-table {
  margin-top: 16px;
}

/* Hourly Controls */
.hourly-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

/* Breakdown */
.breakdown-table {
  padding: 8px 0;
}

.breakdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.breakdown-label {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100px;
  font-size: 13px;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.breakdown-bar {
  flex: 1;
}

.breakdown-value {
  width: 70px;
  text-align: right;
  font-size: 12px;
  color: #5e6e82;
}

/* Comparison */
.comparison-grid {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.comparison-item {
  flex: 1;
  min-width: 180px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.scenario-name {
  font-weight: 600;
  font-size: 14px;
}

.comparison-stats {
  font-size: 12px;
  color: #5e6e82;
}

.comparison-stats div {
  margin-bottom: 4px;
}

.comparison-delta {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
  text-align: right;
  font-weight: 600;
}

.comparison-delta .positive { color: #67c23a; }
.comparison-delta .negative { color: #f56c6c; }

:deep(.el-table th) {
  background-color: #fafbfc;
  font-weight: 600;
}

:deep(.el-slider__runway) {
  margin: 8px 0;
}

:deep(.el-tabs__header) {
  margin-bottom: 16px;
}
</style>