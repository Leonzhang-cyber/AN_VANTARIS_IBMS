<template>
  <div class="dynamic-setpoint-container">
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
            <span class="loading-title">Loading Dynamic Setpoint Control</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">AI-Powered Temperature Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->

      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Dynamic Setpoint Control</span>
          <el-tag type="danger" effect="dark" size="large">AI-Powered Optimization</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Energy Savings</span>
              </div>
              <div class="card-value">18.5%</div>
              <div class="card-footer">
                <el-progress :percentage="18.5" :stroke-width="8" status="success" />
                <span class="status-text">vs. Static Setpoint</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Temperature /></el-icon>
                <span>Temp Stability</span>
              </div>
              <div class="card-value">±0.8°C</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" status="success" :format="() => 'Target: ±1.0°C'" />
                <span class="status-text">Improved by 32%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Setpoint Adjustments</span>
              </div>
              <div class="card-value">1,248</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" status="success" :format="() => 'This Month'" />
                <span class="status-text">24/day average</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>AI Prediction Accuracy</span>
              </div>
              <div class="card-value">94%</div>
              <div class="card-footer">
                <el-progress :percentage="94" :stroke-width="8" status="success" />
                <span class="status-text">±0.3°C margin</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Real-Time Setpoint Control -->
      <div class="real-time-section">
        <el-card class="control-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Monitor /></el-icon>
            <span>Real-Time Setpoint Control</span>
            <div class="header-actions">
              <el-switch v-model="autoMode" active-text="AI Auto" inactive-text="Manual" @change="toggleMode" />
              <el-button type="primary" size="small" @click="applySetpoint" :disabled="autoMode">Apply</el-button>
            </div>
          </div>
          <el-row :gutter="30">
            <el-col :span="8">
              <div class="setpoint-gauge">
                <div ref="supplyGaugeRef" style="height: 200px"></div>
                <div class="gauge-label">
                  <span>Supply Air Setpoint</span>
                  <strong :class="{ 'auto-value': autoMode }">{{ supplySetpoint }}°C</strong>
                </div>
                <el-slider v-model="supplySetpoint" :min="18" :max="26" :step="0.5" :disabled="autoMode" />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="setpoint-gauge">
                <div ref="returnGaugeRef" style="height: 200px"></div>
                <div class="gauge-label">
                  <span>Return Air Setpoint</span>
                  <strong :class="{ 'auto-value': autoMode }">{{ returnSetpoint }}°C</strong>
                </div>
                <el-slider v-model="returnSetpoint" :min="24" :max="32" :step="0.5" :disabled="autoMode" />
              </div>
            </el-col>
            <el-col :span="8">
              <div class="setpoint-gauge">
                <div ref="humidityGaugeRef" style="height: 200px"></div>
                <div class="gauge-label">
                  <span>Humidity Setpoint</span>
                  <strong :class="{ 'auto-value': autoMode }">{{ humiditySetpoint }}%</strong>
                </div>
                <el-slider v-model="humiditySetpoint" :min="40" :max="60" :step="5" :disabled="autoMode" />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- AI Prediction & Optimization -->
      <div class="ai-prediction-section">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="prediction-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Cpu /></el-icon>
                <span>AI Temperature Prediction</span>
                <el-tag type="success" size="small">Live Forecast</el-tag>
              </div>
              <div class="chart-container">
                <div ref="predictionChartRef" style="height: 350px"></div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="recommendation-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Setting /></el-icon>
                <span>AI Recommendations</span>
              </div>
              <div class="recommendations-list">
                <div v-for="(rec, index) in recommendations" :key="index" class="rec-item" :class="{ active: rec.active }">
                  <div class="rec-header">
                    <el-icon><Check v-if="rec.active" /><Clock v-else /></el-icon>
                    <span class="rec-title">{{ rec.title }}</span>
                  </div>
                  <div class="rec-details">
                    <span>Current: {{ rec.current }}</span>
                    <span>Recommended: {{ rec.recommended }}</span>
                  </div>
                  <div class="rec-impact">
                    <span>Savings: {{ rec.savings }}</span>
                    <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Dynamic Optimization Strategies -->
      <div class="strategies-section">
        <div class="section-header">
          <h3>Dynamic Optimization Strategies</h3>
          <el-button type="primary" link @click="showAllStrategies">View All →</el-button>
        </div>
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="strategy-card" @click="activateStrategy('load')">
              <el-icon><DataLine /></el-icon>
              <h4>Load-Based Control</h4>
              <p>Adjust setpoints based on IT load</p>
              <div class="strategy-status">
                <el-tag :type="activeStrategy === 'load' ? 'success' : 'info'" size="small">
                  {{ activeStrategy === 'load' ? 'Active' : 'Available' }}
                </el-tag>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="strategy-card" @click="activateStrategy('weather')">
              <el-icon><Sunny /></el-icon>
              <h4>Weather-Adaptive</h4>
              <p>Optimize using outside conditions</p>
              <div class="strategy-status">
                <el-tag :type="activeStrategy === 'weather' ? 'success' : 'info'" size="small">
                  {{ activeStrategy === 'weather' ? 'Active' : 'Available' }}
                </el-tag>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="strategy-card" @click="activateStrategy('time')">
              <el-icon><Clock /></el-icon>
              <h4>Time-of-Day</h4>
              <p>Schedule-based optimization</p>
              <div class="strategy-status">
                <el-tag :type="activeStrategy === 'time' ? 'success' : 'info'" size="small">
                  {{ activeStrategy === 'time' ? 'Active' : 'Available' }}
                </el-tag>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="strategy-card" @click="activateStrategy('ml')">
              <el-icon><Cpu /></el-icon>
              <h4>ML Predictive</h4>
              <p>Machine learning forecast</p>
              <div class="strategy-status">
                <el-tag :type="activeStrategy === 'ml' ? 'success' : 'info'" size="small">
                  {{ activeStrategy === 'ml' ? 'Active' : 'Available' }}
                </el-tag>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Setpoint Trends Tab -->
          <el-tab-pane label="Setpoint Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Historical Setpoint Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="setpointTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="setpointHeatmapRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Energy Impact Tab -->
          <el-tab-pane label="Energy Impact" name="energy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>Energy Savings from Dynamic Control</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="energyImpactChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="savings-summary">
                    <h4>Optimization Impact</h4>
                    <div class="impact-metrics">
                      <div class="impact-item">
                        <span>Cooling Energy Reduction</span>
                        <strong>285,000 kWh/year</strong>
                        <el-progress :percentage="18.5" :stroke-width="8" :format="() => '18.5%'" />
                      </div>
                      <div class="impact-item">
                        <span>Fan Energy Reduction</span>
                        <strong>95,000 kWh/year</strong>
                        <el-progress :percentage="12" :stroke-width="8" :format="() => '12%'" />
                      </div>
                      <div class="impact-item">
                        <span>PUE Improvement</span>
                        <strong>0.08 reduction</strong>
                        <el-progress :percentage="100" :stroke-width="8" :format="() => 'From 1.45 to 1.37'" />
                      </div>
                    </div>
                    <div class="carbon-savings">
                      <el-icon><Leaf /></el-icon>
                      <span>Carbon Reduction: 165 tCO₂e/year</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Optimization Rules Tab -->
          <el-tab-pane label="Optimization Rules" name="rules">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>Dynamic Setpoint Rules Engine</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-table :data="optimizationRules" border style="width: 100%">
                    <el-table-column prop="condition" label="Condition" width="200" />
                    <el-table-column prop="action" label="Action" />
                    <el-table-column prop="status" label="Status" width="100">
                      <template #default="{ row }">
                        <el-switch v-model="row.enabled" />
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="12">
                  <div class="rule-builder">
                    <h4>Create Custom Rule</h4>
                    <el-form label-width="100px">
                      <el-form-item label="Condition">
                        <el-select v-model="newRule.condition" placeholder="Select condition">
                          <el-option label="IT Load >" value="load_high" />
                          <el-option label="Outside Temp >" value="temp_high" />
                          <el-option label="Time between" value="time_range" />
                          <el-option label="Day of week" value="day_week" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="Value">
                        <el-input v-model="newRule.value" placeholder="Threshold value" />
                      </el-form-item>
                      <el-form-item label="Action">
                        <el-select v-model="newRule.action" placeholder="Select action">
                          <el-option label="Increase setpoint by" value="increase" />
                          <el-option label="Decrease setpoint by" value="decrease" />
                          <el-option label="Set setpoint to" value="set" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="Setpoint Value">
                        <el-input-number v-model="newRule.setpoint" :min="18" :max="26" :step="0.5" />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="addRule">Add Rule</el-button>
                      </el-form-item>
                    </el-form>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Performance Dashboard Tab -->
          <el-tab-pane label="Performance Dashboard" name="performance">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Control Performance Metrics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="metric-card-dashboard">
                    <div class="metric-icon"><el-icon><TrendCharts /></el-icon></div>
                    <div class="metric-info">
                      <span class="metric-label">Setpoint Compliance</span>
                      <span class="metric-value">96.2%</span>
                      <el-progress :percentage="96.2" :stroke-width="6" status="success" />
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="metric-card-dashboard">
                    <div class="metric-icon"><el-icon><Clock /></el-icon></div>
                    <div class="metric-info">
                      <span class="metric-label">Response Time</span>
                      <span class="metric-value">2.4 min</span>
                      <el-progress :percentage="85" :stroke-width="6" :format="() => 'Target: 5 min'" />
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="metric-card-dashboard">
                    <div class="metric-icon"><el-icon><Cpu /></el-icon></div>
                    <div class="metric-info">
                      <span class="metric-label">Oscillation Count</span>
                      <span class="metric-value">3/day</span>
                      <el-progress :percentage="70" :stroke-width="6" :format="() => 'Reduced by 45%'" />
                    </div>
                  </div>
                </el-col>
              </el-row>
              <div class="chart-container" style="margin-top: 20px">
                <div ref="performanceChartRef" style="height: 350px"></div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Alerts & Logs Tab -->
          <el-tab-pane label="Alerts & Logs" name="alerts">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Bell /></el-icon>
                <span>Setpoint Change Log & Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="setpointLogs" border style="width: 100%" max-height="400">
                    <el-table-column prop="timestamp" label="Time" width="180" />
                    <el-table-column prop="action" label="Action" width="150" />
                    <el-table-column prop="from" label="From" width="80" />
                    <el-table-column prop="to" label="To" width="80" />
                    <el-table-column prop="reason" label="Reason" />
                    <el-table-column prop="source" label="Source" width="100" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="alert-summary">
                    <h4>Recent Alerts</h4>
                    <div v-for="alert in setpointAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
                      <el-icon><WarningFilled /></el-icon>
                      <div class="alert-content">
                        <div class="alert-message">{{ alert.message }}</div>
                        <div class="alert-time">{{ alert.timestamp }}</div>
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
          Run AI Optimization
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Performance Report
        </el-button>
        <el-button size="large" @click="viewAnalytics">
          <el-icon><DataAnalysis /></el-icon>
          View Advanced Analytics
        </el-button>
      </div>
    </template>
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
const loadingMessage = ref('Initializing dynamic setpoint control...')

const loadingMessages = [
  'Initializing dynamic setpoint control...',
  'Loading AI prediction models...',
  'Analyzing historical data...',
  'Calibrating optimization rules...',
  'Starting real-time monitoring...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('trends')
const autoMode = ref(true)
const activeStrategy = ref('load')

// Setpoint values
const supplySetpoint = ref(22.5)
const returnSetpoint = ref(28.5)
const humiditySetpoint = ref(50)

// Recommendations
const recommendations = ref([
  { title: 'Increase Supply Temp', current: '22.5°C', recommended: '23.5°C', savings: '+8% energy', active: true },
  { title: 'Widen Deadband', current: '2°C', recommended: '3°C', savings: '+5% energy', active: false },
  { title: 'Enable Night Setback', current: '22.5°C', recommended: '24°C', savings: '+12% energy', active: false }
])

// Optimization rules
const optimizationRules = ref([
  { condition: 'IT Load > 80%', action: 'Decrease setpoint by 1°C', enabled: true },
  { condition: 'IT Load < 30%', action: 'Increase setpoint by 2°C', enabled: true },
  { condition: 'Outside Temp > 30°C', action: 'Decrease setpoint by 1°C', enabled: true },
  { condition: 'Outside Temp < 15°C', action: 'Increase setpoint by 2°C', enabled: false },
  { condition: 'Time 00:00-06:00', action: 'Increase setpoint by 1.5°C', enabled: true }
])

// New rule
const newRule = ref({
  condition: '',
  value: '',
  action: '',
  setpoint: 22
})

// Setpoint logs
const setpointLogs = ref([
  { timestamp: '2024-12-18 14:23:15', action: 'Supply Temp Change', from: '22.5°C', to: '23.0°C', reason: 'Low IT Load', source: 'AI Auto' },
  { timestamp: '2024-12-18 12:05:22', action: 'Supply Temp Change', from: '22.0°C', to: '22.5°C', reason: 'Load Increase', source: 'AI Auto' },
  { timestamp: '2024-12-18 09:30:45', action: 'Return Temp Change', from: '28.0°C', to: '28.5°C', reason: 'Optimization', source: 'AI Auto' },
  { timestamp: '2024-12-18 06:15:33', action: 'Supply Temp Change', from: '23.0°C', to: '22.0°C', reason: 'Morning Ramp-up', source: 'Schedule' },
  { timestamp: '2024-12-17 23:45:12', action: 'Supply Temp Change', from: '22.5°C', to: '23.5°C', reason: 'Night Setback', source: 'AI Auto' }
])

// Setpoint alerts
const setpointAlerts = ref([
  { id: 1, message: 'Rapid temperature fluctuation detected', severity: 'warning', timestamp: '2 min ago' },
  { id: 2, message: 'Setpoint change frequency exceeded threshold', severity: 'info', timestamp: '15 min ago' },
  { id: 3, message: 'AI model retraining completed', severity: 'success', timestamp: '1 hour ago' }
])

// Chart refs
const supplyGaugeRef = ref<HTMLElement | null>(null)
const returnGaugeRef = ref<HTMLElement | null>(null)
const humidityGaugeRef = ref<HTMLElement | null>(null)
const predictionChartRef = ref<HTMLElement | null>(null)
const setpointTrendChartRef = ref<HTMLElement | null>(null)
const setpointHeatmapRef = ref<HTMLElement | null>(null)
const energyImpactChartRef = ref<HTMLElement | null>(null)
const performanceChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const toggleMode = () => {
  if (autoMode.value) {
    ElMessage.success('AI Auto mode enabled - setpoints will be dynamically optimized')
  } else {
    ElMessage.info('Manual mode enabled - setpoints can be adjusted manually')
  }
}

const applySetpoint = () => {
  ElMessage.success(`Setpoints applied: Supply ${supplySetpoint.value}°C, Return ${returnSetpoint.value}°C, Humidity ${humiditySetpoint.value}%`)
}

const applyRecommendation = (rec: any) => {
  if (rec.title === 'Increase Supply Temp') {
    supplySetpoint.value = 23.5
  }
  ElMessage.success(`Applied: ${rec.title}`)
  rec.active = true
}

const activateStrategy = (strategy: string) => {
  activeStrategy.value = strategy
  ElMessage.success(`${strategy === 'load' ? 'Load-Based' : strategy === 'weather' ? 'Weather-Adaptive' : strategy === 'time' ? 'Time-of-Day' : 'ML Predictive'} control activated`)
}

const showAllStrategies = () => {
  ElMessage.info('All optimization strategies will be displayed in a new window')
}

const addRule = () => {
  if (newRule.value.condition && newRule.value.action) {
    optimizationRules.value.push({
      condition: `${newRule.value.condition} ${newRule.value.value}`,
      action: `${newRule.value.action} to ${newRule.value.setpoint}°C`,
      enabled: true
    })
    ElMessage.success('Rule added successfully')
    newRule.value = { condition: '', value: '', action: '', setpoint: 22 }
  } else {
    ElMessage.warning('Please fill in all fields')
  }
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const exportReport = () => {
  ElMessage.success('Performance report export started')
}

const viewAnalytics = () => {
  ElMessage.info('Advanced analytics dashboard will open')
}

// Chart initialization
const initSupplyGauge = () => {
  if (supplyGaugeRef.value) {
    const chart = echarts.init(supplyGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 18,
        max: 26,
        splitNumber: 8,
        progress: { show: true, width: 18, itemStyle: { color: '#409eff' } },
        axisLine: { lineStyle: { width: 18, color: [[0.75, '#67c23a'], [1, '#f59e0b']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8, itemStyle: { color: 'auto' } },
        detail: { show: false },
        title: { show: false },
        data: [{ value: supplySetpoint.value, name: 'Supply' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initReturnGauge = () => {
  if (returnGaugeRef.value) {
    const chart = echarts.init(returnGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 24,
        max: 32,
        splitNumber: 8,
        progress: { show: true, width: 18, itemStyle: { color: '#409eff' } },
        axisLine: { lineStyle: { width: 18, color: [[0.625, '#67c23a'], [1, '#f59e0b']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8, itemStyle: { color: 'auto' } },
        detail: { show: false },
        title: { show: false },
        data: [{ value: returnSetpoint.value, name: 'Return' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initHumidityGauge = () => {
  if (humidityGaugeRef.value) {
    const chart = echarts.init(humidityGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 30,
        max: 70,
        splitNumber: 8,
        progress: { show: true, width: 18, itemStyle: { color: '#409eff' } },
        axisLine: { lineStyle: { width: 18, color: [[0.5, '#67c23a'], [1, '#f59e0b']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8, itemStyle: { color: 'auto' } },
        detail: { show: false },
        title: { show: false },
        data: [{ value: humiditySetpoint.value, name: 'Humidity' }]
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
      legend: { data: ['Actual Temp', 'AI Predicted', 'Upper Bound', 'Lower Bound'] },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [
        { name: 'Actual Temp', type: 'line', data: [22.1, 22.0, 21.8, 22.2, 22.5, 22.8, 23.0, 23.2, 23.1, 22.9, 22.6, 22.3], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'AI Predicted', type: 'line', data: [22.0, 21.9, 21.7, 22.1, 22.4, 22.7, 22.9, 23.1, 23.0, 22.8, 22.5, 22.2], smooth: true, lineStyle: { color: '#67c23a', width: 2, type: 'dashed' } },
        { name: 'Upper Bound', type: 'line', data: [22.5, 22.4, 22.2, 22.6, 22.9, 23.2, 23.4, 23.6, 23.5, 23.3, 23.0, 22.7], lineStyle: { color: '#f59e0b', width: 1, type: 'dotted' } },
        { name: 'Lower Bound', type: 'line', data: [21.5, 21.4, 21.2, 21.6, 21.9, 22.2, 22.4, 22.6, 22.5, 22.3, 22.0, 21.7], lineStyle: { color: '#f59e0b', width: 1, type: 'dotted' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initSetpointTrendChart = () => {
  if (setpointTrendChartRef.value) {
    const chart = echarts.init(setpointTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Supply Setpoint', 'Actual Supply', 'Return Setpoint', 'Actual Return'] },
      xAxis: { type: 'category', data: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [
        { name: 'Supply Setpoint', type: 'line', data: [23.5, 23.5, 23.0, 22.5, 22.5, 23.0, 23.0, 23.5], lineStyle: { color: '#409eff', width: 2, type: 'dashed' } },
        { name: 'Actual Supply', type: 'line', data: [23.3, 23.4, 22.8, 22.4, 22.6, 22.9, 23.1, 23.4], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Return Setpoint', type: 'line', data: [29.5, 29.5, 29.0, 28.5, 28.5, 29.0, 29.0, 29.5], lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Actual Return', type: 'line', data: [29.2, 29.3, 28.7, 28.3, 28.5, 28.8, 29.0, 29.3], smooth: true, lineStyle: { color: '#ef4444', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initSetpointHeatmap = () => {
  if (setpointHeatmapRef.value) {
    const chart = echarts.init(setpointHeatmapRef.value)
    const hours = ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22']
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    const data: any[] = []

    for (let i = 0; i < days.length; i++) {
      for (let j = 0; j < hours.length; j++) {
        data.push([j, i, 22 + Math.sin(i) * 1.5 + Math.cos(j / 4) * 1])
      }
    }

    chart.setOption({
      tooltip: { position: 'top' },
      xAxis: { type: 'category', data: hours, name: 'Hour' },
      yAxis: { type: 'category', data: days, name: 'Day' },
      visualMap: { min: 20, max: 25, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false } }]
    })
    chartInstances.push(chart)
  }
}

const initEnergyImpactChart = () => {
  if (energyImpactChartRef.value) {
    const chart = echarts.init(energyImpactChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Static Setpoint', 'Dynamic Setpoint', 'Savings'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Energy (kWh)' },
      series: [
        { name: 'Static Setpoint', type: 'line', data: [42000, 41000, 43000, 45000, 48000, 52000, 55000, 54000, 50000, 46000, 43000, 41000], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Dynamic Setpoint', type: 'line', data: [38000, 37000, 38500, 40000, 42500, 46000, 48500, 47500, 44500, 41000, 38500, 37000], lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Savings', type: 'bar', data: [4000, 4000, 4500, 5000, 5500, 6000, 6500, 6500, 5500, 5000, 4500, 4000], itemStyle: { color: '#409eff' }, label: { show: true, position: 'top', formatter: '{c} kWh' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPerformanceChart = () => {
  if (performanceChartRef.value) {
    const chart = echarts.init(performanceChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Temp Stability', 'Response Time', 'Energy Efficiency'] },
      xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'] },
      yAxis: { type: 'value', name: 'Score (%)', max: 100 },
      series: [
        { name: 'Temp Stability', type: 'line', data: [82, 85, 87, 89], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Response Time', type: 'line', data: [78, 82, 85, 88], smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Energy Efficiency', type: 'line', data: [85, 87, 90, 92], smooth: true, lineStyle: { color: '#f59e0b', width: 2 }, areaStyle: { opacity: 0.3 } }
      ]
    })
    chartInstances.push(chart)
  }
}

// Watch for setpoint changes to update gauges
watch([supplySetpoint, returnSetpoint, humiditySetpoint], () => {
  if (isLoaded.value) {
    initSupplyGauge()
    initReturnGauge()
    initHumidityGauge()
  }
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
        initSupplyGauge()
        initReturnGauge()
        initHumidityGauge()
        initPredictionChart()
        initSetpointTrendChart()
        initSetpointHeatmap()
        initEnergyImpactChart()
        initPerformanceChart()
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
.dynamic-setpoint-container {
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
  border-right-color: #67c23a;
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
.dynamic-setpoint-container {
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

/* Real-Time Control Section */
.real-time-section {
  margin-bottom: 24px;
}

.control-card {
  border-radius: 12px;
}

.card-header-simple {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.card-header-simple .header-actions {
  margin-left: auto;
  display: flex;
  gap: 16px;
  align-items: center;
}

.setpoint-gauge {
  text-align: center;
}

.gauge-label {
  margin-top: 16px;
}

.gauge-label span {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.gauge-label strong {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.gauge-label strong.auto-value {
  color: #409eff;
}

/* AI Prediction Section */
.ai-prediction-section {
  margin-bottom: 24px;
}

.prediction-card,
.recommendation-card {
  border-radius: 12px;
  height: 100%;
}

.recommendations-list {
  padding: 8px 0;
}

.rec-item {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
}

.rec-item:hover {
  background: #f5f7fa;
}

.rec-item.active {
  background: #ecf5ff;
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rec-title {
  font-weight: 600;
  color: #303133;
}

.rec-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.rec-impact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.rec-impact span {
  color: #67c23a;
  font-weight: 500;
}

/* Strategies Section */
.strategies-section {
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

.strategy-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
  border: 2px solid transparent;
}

.strategy-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.strategy-card .el-icon {
  font-size: 32px;
  color: #409eff;
  margin-bottom: 12px;
}

.strategy-card h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.strategy-card p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #909399;
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

/* Savings Summary */
.savings-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.savings-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.impact-item {
  margin-bottom: 20px;
}

.impact-item span {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
  color: #606266;
}

.impact-item strong {
  display: block;
  margin-bottom: 8px;
  font-size: 18px;
  color: #409eff;
}

.carbon-savings {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  padding: 12px;
  background: #ecf5ff;
  border-radius: 8px;
}

.carbon-savings .el-icon {
  font-size: 20px;
  color: #67c23a;
}

/* Rule Builder */
.rule-builder {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.rule-builder h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* Metric Cards */
.metric-card-dashboard {
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  height: 100%;
}

.metric-icon .el-icon {
  font-size: 40px;
  color: #409eff;
}

.metric-info {
  flex: 1;
}

.metric-label {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

/* Alert Summary */
.alert-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
}

.alert-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.alert-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: white;
}

.alert-item.warning {
  border-left: 4px solid #f59e0b;
}

.alert-item.success {
  border-left: 4px solid #67c23a;
}

.alert-item.info {
  border-left: 4px solid #409eff;
}

.alert-item .el-icon {
  font-size: 18px;
  color: #f59e0b;
}

.alert-content {
  flex: 1;
}

.alert-message {
  font-size: 13px;
  font-weight: 500;
  color: #303133;
}

.alert-time {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
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

:deep(.el-slider__runway) {
  margin-top: 8px;
}
</style>