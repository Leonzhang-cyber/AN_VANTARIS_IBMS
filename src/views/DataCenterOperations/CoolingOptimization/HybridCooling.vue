<template>
  <div class="hybrid-cooling-container">
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
            <span class="loading-title">Loading Hybrid Cooling System</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Free Cooling + Mechanical Cooling Integration</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>

      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Hybrid Cooling Optimization</span>
          <el-tag type="danger" effect="dark" size="large">Free Cooling Enabled</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Sunny /></el-icon>
                <span>Free Cooling Hours</span>
              </div>
              <div class="card-value">3,245 hrs</div>
              <div class="card-footer">
                <el-progress :percentage="74" :stroke-width="8" status="success" :format="() => 'YTD: 74%'" />
                <span class="status-text">Target: 4,380 hrs/year</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Free Cooling Savings</span>
              </div>
              <div class="card-value">38%</div>
              <div class="card-footer">
                <el-progress :percentage="38" :stroke-width="8" status="success" />
                <span class="status-text">vs. Mechanical Only</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Coin /></el-icon>
                <span>WUE Improvement</span>
              </div>
              <div class="card-value">28%</div>
              <div class="card-footer">
                <el-progress :percentage="28" :stroke-width="8" status="success" />
                <span class="status-text">Water Usage Effectiveness</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>PUE Reduction</span>
              </div>
              <div class="card-value">0.12</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" status="success" :format="() => 'From 1.45 to 1.33'" />
                <span class="status-text">Annual Improvement</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Cooling Mode Status -->
      <div class="mode-status-section">
        <el-card class="mode-card" shadow="hover">
          <div class="mode-header">
            <span class="mode-title">Current Cooling Mode</span>
            <el-tag :type="currentMode === 'Free Cooling' ? 'success' : currentMode === 'Hybrid' ? 'warning' : 'danger'" size="large">
              {{ currentMode }}
            </el-tag>
          </div>
          <div class="mode-details">
            <div class="weather-info">
              <div class="weather-item">
                <span>Outside Temp</span>
                <strong>{{ outsideTemp }}°C</strong>
              </div>
              <div class="weather-item">
                <span>Outside Humidity</span>
                <strong>{{ outsideHumidity }}%</strong>
              </div>
              <div class="weather-item">
                <span>Wet Bulb Temp</span>
                <strong>{{ wetBulbTemp }}°C</strong>
              </div>
              <div class="weather-item">
                <span>Setpoint</span>
                <strong>{{ setpointTemp }}°C</strong>
              </div>
            </div>
            <div class="mode-explanation">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ modeExplanation }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Cooling System Flow Diagram -->
      <div class="flow-diagram-section">
        <el-card class="flow-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Connection /></el-icon>
            <span>Hybrid Cooling System Flow</span>
            <div class="header-actions">
              <el-button size="small" @click="animateFlow">Animate Flow</el-button>
              <el-button size="small" type="primary" @click="resetFlow">Reset</el-button>
            </div>
          </div>
          <div class="flow-container">
            <div ref="flowDiagramChartRef" style="height: 400px"></div>
          </div>
        </el-card>
      </div>

      <!-- Cooling Mode Transition -->
      <div class="mode-transition-section">
        <div class="section-header">
          <h3>Free Cooling Availability</h3>
          <el-tag type="info">Based on ASHRAE Guidelines</el-tag>
        </div>
        <el-row :gutter="20">
          <el-col :span="16">
            <div class="chart-container">
              <div ref="freeCoolingChartRef" style="height: 350px"></div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="availability-stats">
              <div class="stat-circle">
                <el-progress type="dashboard" :percentage="74" :width="140" :stroke-width="10" color="#67c23a">
                  <template #default>
                    <span class="percentage-value">74%</span>
                    <span class="percentage-label">Free Cooling</span>
                  </template>
                </el-progress>
              </div>
              <div class="stat-breakdown">
                <div class="break-item">
                  <span class="color-dot full-free"></span>
                  <span>Full Free Cooling: 42%</span>
                </div>
                <div class="break-item">
                  <span class="color-dot partial-free"></span>
                  <span>Partial Free Cooling: 32%</span>
                </div>
                <div class="break-item">
                  <span class="color-dot mechanical"></span>
                  <span>Full Mechanical: 26%</span>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Cooling System Components -->
      <div class="components-section">
        <div class="section-header">
          <h3>Hybrid Cooling Components</h3>
          <el-radio-group v-model="componentView" size="small">
            <el-radio-button label="grid">Grid View</el-radio-button>
            <el-radio-button label="list">List View</el-radio-button>
          </el-radio-group>
        </div>
        <el-row :gutter="20" v-if="componentView === 'grid'">
          <el-col :span="6" v-for="component in coolingComponents" :key="component.id">
            <el-card class="component-card" :class="`status-${component.status.toLowerCase()}`" shadow="hover">
              <div class="component-icon">
                <el-icon :size="32"><component :is="component.icon" /></el-icon>
              </div>
              <div class="component-info">
                <h4>{{ component.name }}</h4>
                <div class="component-metrics">
                  <div v-for="(value, key) in component.metrics" :key="key" class="metric">
                    <span>{{ key }}</span>
                    <strong>{{ value }}</strong>
                  </div>
                </div>
                <div class="component-status">
                  <el-tag :type="component.status === 'Active' ? 'success' : component.status === 'Standby' ? 'warning' : 'info'" size="small">
                    {{ component.status }}
                  </el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="coolingComponents" border v-else style="width: 100%">
          <el-table-column prop="name" label="Component" width="180" />
          <el-table-column prop="status" label="Status" width="120">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Active' ? 'success' : row.status === 'Standby' ? 'warning' : 'info'">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="metrics" label="Metrics">
            <template #default="{ row }">
              <div class="table-metrics">
                <span v-for="(value, key) in row.metrics" :key="key">{{ key }}: {{ value }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="efficiency" label="Efficiency" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.efficiency" :stroke-width="8" />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Performance Analytics Tab -->
          <el-tab-pane label="Performance Analytics" name="analytics">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Hybrid Cooling Performance</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="pueTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="energyMixChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Free Cooling Optimization Tab -->
          <el-tab-pane label="Free Cooling Optimization" name="freeCooling">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Sunny /></el-icon>
                <span>Free Cooling Strategies</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="freeCoolingPotentialChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="strategies-list">
                    <h4>Optimization Strategies</h4>
                    <el-collapse v-model="strategiesCollapse">
                      <el-collapse-item title="Air-Side Economizer" name="air">
                        <p>Use outside air when temperature < 21°C</p>
                        <el-progress :percentage="85" :stroke-width="8" :format="() => '85% utilization'" />
                        <el-button type="primary" size="small" style="margin-top: 8px">Optimize Setpoints</el-button>
                      </el-collapse-item>
                      <el-collapse-item title="Water-Side Economizer" name="water">
                        <p>Use cooling tower when wet bulb < 15°C</p>
                        <el-progress :percentage="68" :stroke-width="8" :format="() => '68% utilization'" />
                        <el-button type="primary" size="small" style="margin-top: 8px">Adjust Thresholds</el-button>
                      </el-collapse-item>
                      <el-collapse-item title="Thermal Storage" name="thermal">
                        <p>Shift cooling load to off-peak hours</p>
                        <el-progress :percentage="45" :stroke-width="8" :format="() => '45% utilization'" />
                        <el-button type="primary" size="small" style="margin-top: 8px">Optimize Schedule</el-button>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Mode Transition Optimization Tab -->
          <el-tab-pane label="Mode Transition" name="transition">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Switch /></el-icon>
                <span>Smart Mode Transition Control</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="transitionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="transition-settings">
                    <h4>Transition Thresholds</h4>
                    <div class="setting-item">
                      <span>Free Cooling Enable Temp</span>
                      <el-slider v-model="freeCoolingTemp" :min="10" :max="25" :step="0.5" show-input />
                    </div>
                    <div class="setting-item">
                      <span>Hybrid Mode Temp Range</span>
                      <div class="range-slider">
                        <el-slider v-model="hybridRange" range :min="15" :max="30" show-input />
                      </div>
                    </div>
                    <div class="setting-item">
                      <span>Mechanical Only Threshold</span>
                      <el-slider v-model="mechanicalTemp" :min="25" :max="35" :step="0.5" show-input />
                    </div>
                    <div class="transition-prediction">
                      <h4>Next Transition Prediction</h4>
                      <div class="prediction-info">
                        <span>Expected Mode Change:</span>
                        <strong>Free Cooling → Hybrid</strong>
                      </div>
                      <div class="prediction-info">
                        <span>Predicted Time:</span>
                        <strong>2024-12-19 14:30</strong>
                      </div>
                      <div class="prediction-info">
                        <span>Trigger Condition:</span>
                        <strong>Outside temp rising to 22°C</strong>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Water Conservation Tab -->
          <el-tab-pane label="Water Conservation" name="water">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Water /></el-icon>
                <span>Water Usage & Conservation</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="waterUsageChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="water-metrics">
                    <div class="metric-card-water">
                      <div class="metric-value">{{ waterUsage }} m³/day</div>
                      <div class="metric-label">Current Water Usage</div>
                      <el-progress :percentage="75" :stroke-width="8" :format="() => 'vs. Baseline'" />
                    </div>
                    <div class="metric-card-water">
                      <div class="metric-value">{{ waterSavings }} m³/year</div>
                      <div class="metric-label">Annual Water Savings</div>
                      <el-tag type="success">28% reduction</el-tag>
                    </div>
                    <div class="conservation-tips">
                      <h4>Water Conservation Tips</h4>
                      <ul>
                        <li>Increase cycles of concentration to 5</li>
                        <li>Install drift eliminators on cooling towers</li>
                        <li>Use non-potable water for makeup</li>
                        <li>Implement automated blowdown control</li>
                      </ul>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Energy Savings Tab -->
          <el-tab-pane label="Energy Savings" name="savings">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>Hybrid Cooling Savings</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="hybridSavingsChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="savings-breakdown">
                    <h4>Savings Breakdown</h4>
                    <div class="savings-item">
                      <span>Compressor Savings</span>
                      <el-progress :percentage="65" :stroke-width="10" :format="() => '325,000 kWh'" />
                    </div>
                    <div class="savings-item">
                      <span>Fan Energy Reduction</span>
                      <el-progress :percentage="42" :stroke-width="10" :format="() => '85,000 kWh'" />
                    </div>
                    <div class="savings-item">
                      <span>Pump Optimization</span>
                      <el-progress :percentage="28" :stroke-width="10" :format="() => '45,000 kWh'" />
                    </div>
                    <div class="savings-total">
                      <span>Total Annual Savings</span>
                      <strong>455,000 kWh</strong>
                    </div>
                    <div class="carbon-savings">
                      <el-icon><Leaf /></el-icon>
                      <span>Carbon Reduction: 210 tCO₂e/year</span>
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
                  <el-table :data="coolingAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="component" label="Component" width="140" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>System Health</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Free Cooling Efficiency</span>
                        <el-progress :percentage="85" :stroke-width="6" />
                      </div>
                      <div class="health-item">
                        <span>Transition Smoothness</span>
                        <el-progress :percentage="78" :stroke-width="6" />
                      </div>
                      <div class="health-item">
                        <span>Water Conservation</span>
                        <el-progress :percentage="72" :stroke-width="6" />
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
        <el-button type="primary" size="large" @click="runOptimization">
          <el-icon><Cpu /></el-icon>
          Run Hybrid Cooling Optimization
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Performance Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing hybrid cooling system...')

const loadingMessages = [
  'Initializing hybrid cooling system...',
  'Loading free cooling analytics...',
  'Analyzing weather patterns...',
  'Calculating efficiency metrics...',
  'Optimizing mode transitions...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('analytics')
const componentView = ref('grid')
const strategiesCollapse = ref(['air'])

// Current mode and weather
const currentMode = ref('Free Cooling')
const outsideTemp = ref(18.5)
const outsideHumidity = ref(62)
const wetBulbTemp = ref(14.2)
const setpointTemp = ref(22)

// Transition thresholds
const freeCoolingTemp = ref(21)
const hybridRange = ref([21, 28])
const mechanicalTemp = ref(28)

// Water metrics
const waterUsage = ref(185)
const waterSavings = ref(38500)

// Health score
const healthScore = ref(86)
const healthColor = ref('#67c23a')

// Mode explanation
const modeExplanation = computed(() => {
  if (currentMode.value === 'Free Cooling') {
    return 'Outside conditions are optimal for free cooling. Mechanical compressors are bypassed, resulting in maximum energy savings.'
  } else if (currentMode.value === 'Hybrid') {
    return 'Partial free cooling with mechanical assistance. Economizer provides pre-cooling while compressors handle remaining load.'
  } else {
    return 'Outside conditions require full mechanical cooling. Economizer is bypassed, chillers operating at full capacity.'
  }
})

// Cooling components
const coolingComponents = ref([
  {
    id: 1, name: 'Air-Side Economizer', icon: 'WindPower', status: 'Active',
    metrics: { Airflow: '12,500 CFM', Damper: '85%' }, efficiency: 85
  },
  {
    id: 2, name: 'Water-Side Economizer', icon: 'Water', status: 'Active',
    metrics: { Flow: '850 GPM', Approach: '2.5°C' }, efficiency: 78
  },
  {
    id: 3, name: 'Cooling Towers', icon: 'OfficeBuilding', status: 'Active',
    metrics: { Fans: '2/4', Water: '35°C' }, efficiency: 82
  },
  {
    id: 4, name: 'Chillers', icon: 'Cpu', status: 'Standby',
    metrics: { Load: '15%', COP: '5.2' }, efficiency: 0
  },
  {
    id: 5, name: 'Dry Coolers', icon: 'Sunny', status: 'Standby',
    metrics: { Fans: '0/6', Approach: '0°C' }, efficiency: 0
  },
  {
    id: 6, name: 'Thermal Storage', icon: 'Clock', status: 'Standby',
    metrics: { Capacity: '45%', Charge: '8°C' }, efficiency: 0
  }
])

// Alerts
const coolingAlerts = ref([
  { severity: 'Info', message: 'Free cooling mode engaged', component: 'Economizer', timestamp: '2024-12-18 08:23' },
  { severity: 'Warning', message: 'Approach temperature increasing', component: 'Cooling Tower', timestamp: '2024-12-18 06:15' },
  { severity: 'Info', message: 'Mode transition predicted in 2 hours', component: 'Controller', timestamp: '2024-12-18 05:30' }
])

// Chart refs
const flowDiagramChartRef = ref<HTMLElement | null>(null)
const freeCoolingChartRef = ref<HTMLElement | null>(null)
const pueTrendChartRef = ref<HTMLElement | null>(null)
const energyMixChartRef = ref<HTMLElement | null>(null)
const freeCoolingPotentialChartRef = ref<HTMLElement | null>(null)
const transitionChartRef = ref<HTMLElement | null>(null)
const waterUsageChartRef = ref<HTMLElement | null>(null)
const hybridSavingsChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []
let animationInterval: ReturnType<typeof setInterval>

// Methods
const goBack = () => {
  router.back()
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const animateFlow = () => {
  ElMessage.success('Flow animation started')
  if (animationInterval) clearInterval(animationInterval)
  let step = 0
  animationInterval = setInterval(() => {
    step++
    if (step > 20) {
      clearInterval(animationInterval)
    }
  }, 300)
}

const resetFlow = () => {
  if (animationInterval) clearInterval(animationInterval)
  ElMessage.info('Flow diagram reset')
}

const runOptimization = () => {
  ElMessage.success('Hybrid cooling optimization started. Results will be available shortly.')
}

const exportReport = () => {
  ElMessage.success('Performance report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

// Chart initialization
const initFlowDiagramChart = () => {
  if (flowDiagramChartRef.value) {
    const chart = echarts.init(flowDiagramChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        data: [
          { name: 'Outside Air' }, { name: 'Economizer' },
          { name: 'Cooling Tower' }, { name: 'Heat Exchanger' },
          { name: 'Chiller' }, { name: 'CRAH Unit' }, { name: 'Data Hall' }
        ],
        links: [
          { source: 'Outside Air', target: 'Economizer', value: 80 },
          { source: 'Economizer', target: 'CRAH Unit', value: 60 },
          { source: 'Economizer', target: 'Chiller', value: 20 },
          { source: 'Cooling Tower', target: 'Heat Exchanger', value: 45 },
          { source: 'Heat Exchanger', target: 'CRAH Unit', value: 35 },
          { source: 'Chiller', target: 'CRAH Unit', value: 20 },
          { source: 'CRAH Unit', target: 'Data Hall', value: 100 }
        ],
        lineStyle: { color: 'gradient', curveness: 0.5 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initFreeCoolingChart = () => {
  if (freeCoolingChartRef.value) {
    const chart = echarts.init(freeCoolingChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Free Cooling Hours', 'Temperature'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: [{ type: 'value', name: 'Hours' }, { type: 'value', name: 'Temperature (°C)' }],
      series: [
        { name: 'Free Cooling Hours', type: 'bar', data: [320, 290, 310, 280, 250, 180, 150, 160, 220, 280, 310, 330], itemStyle: { color: '#67c23a' } },
        { name: 'Temperature', type: 'line', yAxisIndex: 1, data: [5, 6, 10, 15, 20, 25, 28, 27, 23, 18, 12, 7], lineStyle: { color: '#f59e0b', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPUETrendChart = () => {
  if (pueTrendChartRef.value) {
    const chart = echarts.init(pueTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Actual PUE', 'Baseline PUE', 'Target PUE'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.5 },
      series: [
        { name: 'Actual PUE', type: 'line', data: [1.42, 1.41, 1.40, 1.39, 1.38, 1.37, 1.36, 1.35, 1.34, 1.33, 1.33, 1.32], smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Baseline PUE', type: 'line', data: [1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45, 1.45], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Target PUE', type: 'line', data: [1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35, 1.35], lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initEnergyMixChart = () => {
  if (energyMixChartRef.value) {
    const chart = echarts.init(energyMixChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie',
        radius: '55%',
        data: [
          { value: 45, name: 'Free Cooling', itemStyle: { color: '#67c23a' } },
          { value: 35, name: 'Mechanical Cooling', itemStyle: { color: '#f59e0b' } },
          { value: 20, name: 'Hybrid Mode', itemStyle: { color: '#409eff' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initFreeCoolingPotentialChart = () => {
  if (freeCoolingPotentialChartRef.value) {
    const chart = echarts.init(freeCoolingPotentialChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Utilized', 'Available but Not Used', 'Not Available'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Hours', stack: 'total' },
      series: [
        { name: 'Utilized', type: 'bar', data: [280, 260, 280, 250, 220, 160, 130, 140, 190, 250, 280, 300], itemStyle: { color: '#67c23a' } },
        { name: 'Available but Not Used', type: 'bar', data: [40, 30, 30, 30, 30, 20, 20, 20, 30, 30, 30, 30], itemStyle: { color: '#f59e0b' } },
        { name: 'Not Available', type: 'bar', data: [45, 35, 31, 31, 31, 31, 31, 31, 31, 31, 31, 35], itemStyle: { color: '#909399' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initTransitionChart = () => {
  if (transitionChartRef.value) {
    const chart = echarts.init(transitionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Free Cooling', 'Hybrid', 'Mechanical'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: { type: 'value', name: 'Mode', min: 0, max: 3, axisLabel: { formatter: (value: number) => ['Free', 'Hybrid', 'Mechanical'][Math.floor(value)] } },
      series: [{
        type: 'line',
        data: [0, 0, 0.5, 1.5, 2, 1],
        smooth: true,
        lineStyle: { color: '#409eff', width: 2 },
        areaStyle: { opacity: 0.3 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initWaterUsageChart = () => {
  if (waterUsageChartRef.value) {
    const chart = echarts.init(waterUsageChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Baseline', 'Actual'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Water Usage (m³)' },
      series: [
        { name: 'Baseline', type: 'line', data: [220, 210, 230, 240, 260, 280, 290, 285, 270, 250, 230, 220], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Actual', type: 'bar', data: [185, 175, 190, 195, 210, 225, 235, 230, 215, 200, 185, 178], itemStyle: { color: '#409eff' }, label: { show: true, position: 'top', formatter: '{c} m³' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initHybridSavingsChart = () => {
  if (hybridSavingsChartRef.value) {
    const chart = echarts.init(hybridSavingsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['With Free Cooling', 'Without Free Cooling', 'Savings'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Energy (kWh)' },
      series: [
        { name: 'With Free Cooling', type: 'line', data: [38000, 35000, 37000, 39000, 42000, 45000, 47000, 46000, 43000, 40000, 37000, 35000], lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Without Free Cooling', type: 'line', data: [52000, 49000, 51000, 54000, 58000, 62000, 65000, 64000, 59000, 55000, 51000, 48000], lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Savings', type: 'bar', data: [14000, 14000, 14000, 15000, 16000, 17000, 18000, 18000, 16000, 15000, 14000, 13000], itemStyle: { color: '#409eff' }, label: { show: true, position: 'top', formatter: '{c} kWh' } }
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
        initFlowDiagramChart()
        initFreeCoolingChart()
        initPUETrendChart()
        initEnergyMixChart()
        initFreeCoolingPotentialChart()
        initTransitionChart()
        initWaterUsageChart()
        initHybridSavingsChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (animationInterval) clearInterval(animationInterval)
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.hybrid-cooling-container {
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
  border-top-color: #67c23a;
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
  border-bottom-color: #409eff;
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
  background: linear-gradient(90deg, #67c23a, #f59e0b, #409eff);
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
.hybrid-cooling-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
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

/* Mode Status Section */
.mode-status-section {
  margin-bottom: 24px;
}

.mode-card {
  border-radius: 12px;
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%);
}

.mode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.mode-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.mode-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.weather-info {
  display: flex;
  gap: 30px;
}

.weather-item {
  text-align: center;
}

.weather-item span {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.weather-item strong {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
}

.mode-explanation {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
  max-width: 400px;
}

.mode-explanation .el-icon {
  font-size: 20px;
  color: #409eff;
}

/* Flow Diagram */
.flow-diagram-section {
  margin-bottom: 24px;
}

.flow-card {
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

.flow-container {
  min-height: 400px;
}

/* Mode Transition Section */
.mode-transition-section {
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

.availability-stats {
  text-align: center;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.stat-circle {
  margin-bottom: 20px;
}

.percentage-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.percentage-label {
  font-size: 12px;
  color: #909399;
}

.stat-breakdown {
  text-align: left;
  width: 100%;
}

.break-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
  font-size: 13px;
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 4px;
}

.color-dot.full-free { background: #67c23a; }
.color-dot.partial-free { background: #f59e0b; }
.color-dot.mechanical { background: #909399; }

/* Components Section */
.components-section {
  margin-bottom: 24px;
}

.component-card {
  border-radius: 12px;
  transition: transform 0.2s;
  text-align: center;
  padding: 16px;
}

.component-card:hover {
  transform: translateY(-2px);
}

.component-card.status-active {
  border-left: 4px solid #67c23a;
}

.component-card.status-standby {
  border-left: 4px solid #f59e0b;
}

.component-icon {
  margin-bottom: 12px;
  color: #409eff;
}

.component-info h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
}

.component-metrics {
  margin: 12px 0;
}

.component-metrics .metric {
  display: inline-block;
  margin: 4px 8px;
  font-size: 12px;
}

.component-metrics .metric span {
  color: #909399;
}

.component-metrics .metric strong {
  color: #303133;
  margin-left: 4px;
}

.table-metrics {
  display: flex;
  gap: 16px;
  font-size: 12px;
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
  color: #67c23a;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Strategies List */
.strategies-list {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.strategies-list h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* Transition Settings */
.transition-settings {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.transition-settings h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.setting-item {
  margin-bottom: 20px;
}

.setting-item > span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.range-slider {
  padding: 0 8px;
}

.transition-prediction {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.prediction-info {
  display: flex;
  justify-content: space-between;
  margin: 12px 0;
  font-size: 13px;
}

.prediction-info strong {
  color: #409eff;
}

/* Water Metrics */
.water-metrics {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.metric-card-water {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.metric-value {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
}

.metric-label {
  font-size: 13px;
  color: #909399;
  margin: 8px 0;
}

.conservation-tips {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.conservation-tips h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.conservation-tips ul {
  margin: 0;
  padding-left: 20px;
}

.conservation-tips li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

/* Savings Breakdown */
.savings-breakdown {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.savings-breakdown h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.savings-item {
  margin-bottom: 20px;
}

.savings-item span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

.savings-total {
  margin: 20px 0;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 600;
}

.savings-total strong {
  color: #409eff;
  font-size: 20px;
}

.carbon-savings {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  background: #ecf5ff;
  border-radius: 8px;
}

.carbon-savings .el-icon {
  font-size: 20px;
  color: #67c23a;
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

:deep(.el-collapse-item__header) {
  font-weight: 500;
}
</style>