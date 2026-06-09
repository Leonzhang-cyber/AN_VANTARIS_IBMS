<template>
  <div class="ups-optimization-container">
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
            <span class="loading-title">Loading UPS Optimization</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Uninterruptible Power Supply Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">UPS Optimization</span>
          <el-tag type="warning" effect="dark" size="large">Power Protection Optimization</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>UPS Load</span>
              </div>
              <div class="card-value">{{ upsLoad }}%</div>
              <div class="card-footer">
                <el-progress :percentage="upsLoad" :stroke-width="8" :color="loadColor" />
                <span class="status-text">Optimal: 40-70%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>UPS Efficiency</span>
              </div>
              <div class="card-value">{{ upsEfficiency }}%</div>
              <div class="card-footer">
                <el-progress :percentage="upsEfficiency" :stroke-width="8" status="success" />
                <span class="status-text">Target: >95%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Battery /></el-icon>
                <span>Battery Health</span>
              </div>
              <div class="card-value">{{ batteryHealth }}%</div>
              <div class="card-footer">
                <el-progress :percentage="batteryHealth" :stroke-width="8" :color="batteryColor" />
                <span class="status-text">Replace at &lt;60%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Energy Savings</span>
              </div>
              <div class="card-value">{{ energySavings }}%</div>
              <div class="card-footer">
                <el-progress :percentage="energySavings" :stroke-width="8" status="success" />
                <span class="status-text">Eco Mode Savings</span>
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
                <span>Real-Time Power Monitoring</span>
                <el-tag type="success" size="small">Live Data</el-tag>
              </div>
              <div class="monitoring-grid">
                <div class="monitor-item">
                  <span class="monitor-label">Input Voltage</span>
                  <span class="monitor-value">{{ inputVoltage }} V</span>
                  <el-progress :percentage="(inputVoltage / 240) * 100" :stroke-width="4" :show-text="false" />
                </div>
                <div class="monitor-item">
                  <span class="monitor-label">Output Voltage</span>
                  <span class="monitor-value">{{ outputVoltage }} V</span>
                  <el-progress :percentage="(outputVoltage / 240) * 100" :stroke-width="4" :show-text="false" />
                </div>
                <div class="monitor-item">
                  <span class="monitor-label">Input Current</span>
                  <span class="monitor-value">{{ inputCurrent }} A</span>
                  <el-progress :percentage="(inputCurrent / 200) * 100" :stroke-width="4" :show-text="false" />
                </div>
                <div class="monitor-item">
                  <span class="monitor-label">Output Current</span>
                  <span class="monitor-value">{{ outputCurrent }} A</span>
                  <el-progress :percentage="(outputCurrent / 200) * 100" :stroke-width="4" :show-text="false" />
                </div>
                <div class="monitor-item">
                  <span class="monitor-label">Frequency</span>
                  <span class="monitor-value">{{ frequency }} Hz</span>
                  <el-progress :percentage="((frequency - 49) / 2) * 100" :stroke-width="4" :show-text="false" />
                </div>
                <div class="monitor-item">
                  <span class="monitor-label">Temperature</span>
                  <span class="monitor-value" :class="{ warning: upsTemp > 35 }">{{ upsTemp }}°C</span>
                  <el-progress :percentage="(upsTemp / 50) * 100" :stroke-width="4" :color="tempColor" :show-text="false" />
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="efficiency-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><TrendCharts /></el-icon>
                <span>Efficiency Curve</span>
              </div>
              <div ref="efficiencyGaugeRef" style="height: 200px"></div>
              <div class="efficiency-stats">
                <div class="stat-item">
                  <span>Current Efficiency</span>
                  <strong>{{ upsEfficiency }}%</strong>
                </div>
                <div class="stat-item">
                  <span>Eco Mode Efficiency</span>
                  <strong>98.5%</strong>
                </div>
                <div class="stat-item">
                  <span>Loss Reduction</span>
                  <strong>+12%</strong>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- UPS Units Status -->
      <div class="ups-units-section">
        <div class="section-header">
          <h3>UPS Units Status</h3>
          <div class="header-controls">
            <el-radio-group v-model="unitView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="6" v-for="ups in upsUnits" :key="ups.id">
            <el-card class="ups-unit-card" :class="`status-${ups.status}`" shadow="hover">
              <div class="ups-header">
                <span class="ups-name">{{ ups.name }}</span>
                <el-tag :type="getUpsTagType(ups.status)" size="small">{{ ups.status }}</el-tag>
              </div>
              <div class="ups-metrics">
                <div class="metric-row">
                  <div class="metric">
                    <span>Load</span>
                    <strong>{{ ups.load }}%</strong>
                    <el-progress :percentage="ups.load" :stroke-width="4" :color="getLoadColor(ups.load)" :show-text="false" />
                  </div>
                  <div class="metric">
                    <span>Efficiency</span>
                    <strong>{{ ups.efficiency }}%</strong>
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Output</span>
                    <strong>{{ ups.outputVoltage }} V</strong>
                  </div>
                  <div class="metric">
                    <span>Battery</span>
                    <strong>{{ ups.batteryHealth }}%</strong>
                  </div>
                </div>
              </div>
              <div class="ups-footer">
                <el-button type="primary" size="small" @click="viewUpsDetails(ups)">Details</el-button>
                <el-button size="small" @click="configureUps(ups)">Configure</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="upsUnits" border v-else style="width: 100%">
          <el-table-column prop="name" label="Unit" width="120" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getUpsTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="load" label="Load %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.load" :stroke-width="8" :color="getLoadColor(row.load)" />
            </template>
          </el-table-column>
          <el-table-column prop="efficiency" label="Efficiency %" width="120" />
          <el-table-column prop="outputVoltage" label="Output (V)" width="100" />
          <el-table-column prop="batteryHealth" label="Battery %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.batteryHealth" :stroke-width="8" :color="getBatteryColor(row.batteryHealth)" />
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewUpsDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="configureUps(row)">Config</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Load Analysis Tab -->
          <el-tab-pane label="Load Analysis" name="load">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>UPS Load & Capacity Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="loadTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="load-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ totalCapacity }} kW</div>
                      <div class="stat-label">Total Capacity</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ currentLoad }} kW</div>
                      <div class="stat-label">Current Load</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ availableCapacity }} kW</div>
                      <div class="stat-label">Available Capacity</div>
                    </div>
                    <div class="warning-message" v-if="upsLoad > 70">
                      <el-icon><WarningFilled /></el-icon>
                      <span>Load is above 70%. Consider redistributing or upgrading capacity.</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Battery Management Tab -->
          <el-tab-pane label="Battery Management" name="battery">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Battery /></el-icon>
                <span>Battery Health & Management</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="batteryData" border style="width: 100%">
                    <el-table-column prop="string" label="Battery String" width="120" />
                    <el-table-column prop="health" label="Health %" width="150">
                      <template #default="{ row }">
                        <el-progress :percentage="row.health" :stroke-width="8" :color="getBatteryColor(row.health)" />
                      </template>
                    </el-table-column>
                    <el-table-column prop="temperature" label="Temperature" width="120">
                      <template #default="{ row }">
                        <span :class="{ warning: row.temperature > 35 }">{{ row.temperature }}°C</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="internalResistance" label="Internal Resistance" width="140" />
                    <el-table-column prop="status" label="Status" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'Good' ? 'success' : 'warning'" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="battery-summary">
                    <h4>Battery Replacement Forecast</h4>
                    <div class="forecast-item">
                      <span>String 1</span>
                      <el-progress :percentage="85" :stroke-width="8" :format="() => '12 months'" />
                    </div>
                    <div class="forecast-item">
                      <span>String 2</span>
                      <el-progress :percentage="65" :stroke-width="8" :format="() => '8 months'" />
                    </div>
                    <div class="forecast-item">
                      <span>String 3</span>
                      <el-progress :percentage="40" :stroke-width="8" :format="() => '5 months'" />
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="scheduleBatteryTest">
                      Schedule Battery Test
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Harmonic Analysis Tab -->
          <el-tab-pane label="Harmonic Analysis" name="harmonics">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Connection /></el-icon>
                <span>Harmonic Distortion Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="harmonicChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="harmonic-stats">
                    <div class="thd-card">
                      <span class="thd-label">Total Harmonic Distortion (THD)</span>
                      <span class="thd-value" :class="{ warning: thd > 5 }">{{ thd }}%</span>
                      <el-progress :percentage="thd * 10" :stroke-width="10" :color="thd > 5 ? '#f56c6c' : '#67c23a'" />
                      <span class="thd-target">Target: &lt;5%</span>
                    </div>
                    <div class="harmonic-recommendations">
                      <h4>Recommendations</h4>
                      <ul>
                        <li>Install active harmonic filter for THD reduction</li>
                        <li>Balance single-phase loads across phases</li>
                        <li>Consider 12-pulse rectifier upgrade</li>
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
                <el-icon><TrendCharts /></el-icon>
                <span>UPS Energy Savings Tracking</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="savingsChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="savings-summary">
                    <h4>Eco Mode Savings</h4>
                    <div class="savings-item">
                      <span>Energy Saved (YTD)</span>
                      <strong>185,000 kWh</strong>
                    </div>
                    <div class="savings-item">
                      <span>Cost Savings</span>
                      <strong>$22,200</strong>
                    </div>
                    <div class="savings-item">
                      <span>Carbon Reduction</span>
                      <strong>85 tCO₂e</strong>
                    </div>
                    <div class="eco-mode-toggle">
                      <span>Eco Mode</span>
                      <el-switch v-model="ecoModeEnabled" @change="toggleEcoMode" />
                    </div>
                    <el-alert
                        title="Eco Mode Active"
                        description="UPS is operating in high-efficiency mode. Automatic transfer to double conversion if input power quality degrades."
                        type="success"
                        show-icon
                        :closable="false"
                        v-if="ecoModeEnabled"
                    />
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
                <span>AI-Powered Optimization Recommendations</span>
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
                    <h4>Total Savings Potential</h4>
                    <div class="potential-value">15.5%</div>
                    <div class="potential-label">Energy Reduction</div>
                    <el-progress :percentage="15.5" :stroke-width="12" status="success" />
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
                <span>UPS Alerts & Diagnostics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="upsAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="ups" label="UPS" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>UPS Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Inverter Health</span>
                        <el-progress :percentage="92" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Rectifier Health</span>
                        <el-progress :percentage="88" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Battery Health</span>
                        <el-progress :percentage="batteryHealth" :stroke-width="6" :color="batteryColor" />
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
          Export UPS Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </template>

    <!-- UPS Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`UPS ${selectedUps?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedUps">
        <el-descriptions-item label="Status">
          <el-tag :type="getUpsTagType(selectedUps.status)">{{ selectedUps.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Model">Galaxy VX 500kW</el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedUps.load }}%</el-descriptions-item>
        <el-descriptions-item label="Efficiency">{{ selectedUps.efficiency }}%</el-descriptions-item>
        <el-descriptions-item label="Output Voltage">{{ selectedUps.outputVoltage }} V</el-descriptions-item>
        <el-descriptions-item label="Output Current">{{ selectedUps.outputCurrent || 185 }} A</el-descriptions-item>
        <el-descriptions-item label="Battery Health">{{ selectedUps.batteryHealth }}%</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">2024-11-15</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">2025-02-15</el-descriptions-item>
        <el-descriptions-item label="Runtime Remaining">{{ selectedUps.runtime || 18 }} min</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="runSelfTest">Run Self-Test</el-button>
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
const loadingMessage = ref('Initializing UPS systems...')

const loadingMessages = [
  'Initializing UPS systems...',
  'Loading power metrics...',
  'Analyzing battery health...',
  'Calculating efficiency data...',
  'Detecting harmonic distortion...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('load')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const selectedUps = ref<any>(null)
const ecoModeEnabled = ref(true)

// Real-time metrics
const upsLoad = ref(52)
const upsEfficiency = ref(94.5)
const batteryHealth = ref(82)
const energySavings = ref(18.5)
const inputVoltage = ref(220.5)
const outputVoltage = ref(220.2)
const inputCurrent = ref(118)
const outputCurrent = ref(115)
const frequency = ref(50.02)
const upsTemp = ref(32.5)
const totalCapacity = ref(1500)
const currentLoad = ref(780)
const availableCapacity = ref(720)
const thd = ref(3.8)

// Colors
const loadColor = computed(() => {
  if (upsLoad.value < 40) return '#909399'
  if (upsLoad.value < 70) return '#67c23a'
  return '#f56c6c'
})

const batteryColor = computed(() => {
  if (batteryHealth.value > 70) return '#67c23a'
  if (batteryHealth.value > 50) return '#e6a23c'
  return '#f56c6c'
})

const tempColor = computed(() => {
  if (upsTemp.value < 30) return '#67c23a'
  if (upsTemp.value < 38) return '#e6a23c'
  return '#f56c6c'
})

const healthScore = ref(86)
const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

// UPS units data
const upsUnits = ref([
  { id: 1, name: 'UPS-01', status: 'Online', load: 48, efficiency: 95.2, outputVoltage: 220.1, batteryHealth: 85, runtime: 22 },
  { id: 2, name: 'UPS-02', status: 'Online', load: 52, efficiency: 94.8, outputVoltage: 220.3, batteryHealth: 82, runtime: 18 },
  { id: 3, name: 'UPS-03', status: 'Online', load: 45, efficiency: 95.5, outputVoltage: 220.0, batteryHealth: 88, runtime: 25 },
  { id: 4, name: 'UPS-04', status: 'Standby', load: 12, efficiency: 88.0, outputVoltage: 219.8, batteryHealth: 75, runtime: 30 }
])

// Battery data
const batteryData = ref([
  { string: 'String 1', health: 85, temperature: 28, internalResistance: '2.1 mΩ', status: 'Good' },
  { string: 'String 2', health: 78, temperature: 32, internalResistance: '2.5 mΩ', status: 'Good' },
  { string: 'String 3', health: 65, temperature: 35, internalResistance: '3.2 mΩ', status: 'Warning' },
  { string: 'String 4', health: 88, temperature: 27, internalResistance: '1.9 mΩ', status: 'Good' }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Enable Eco Mode for light load conditions', impact: '+8% efficiency', priority: 'High' },
  { recommendation: 'Balance load across UPS units', impact: '+5% efficiency', priority: 'Medium' },
  { recommendation: 'Replace String 3 batteries (health below 70%)', impact: 'Improve reliability', priority: 'High' },
  { recommendation: 'Install harmonic filter for THD reduction', impact: '-2% THD', priority: 'Medium' }
])

// Alerts
const upsAlerts = ref([
  { severity: 'Warning', message: 'String 3 battery health below 70%', ups: 'UPS-02', timestamp: '2024-12-18 10:23' },
  { severity: 'Info', message: 'Load increased by 5% in last hour', ups: 'UPS-01', timestamp: '2024-12-18 09:15' },
  { severity: 'Warning', message: 'Temperature elevated on UPS-02', ups: 'UPS-02', timestamp: '2024-12-18 08:30' }
])

// Chart refs
const efficiencyGaugeRef = ref<HTMLElement | null>(null)
const loadTrendChartRef = ref<HTMLElement | null>(null)
const harmonicChartRef = ref<HTMLElement | null>(null)
const savingsChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const getUpsTagType = (status: string) => {
  if (status === 'Online') return 'success'
  if (status === 'Standby') return 'warning'
  return 'info'
}

const getLoadColor = (load: number) => {
  if (load < 40) return '#909399'
  if (load < 70) return '#67c23a'
  return '#f56c6c'
}

const getBatteryColor = (health: number) => {
  if (health > 70) return '#67c23a'
  if (health > 50) return '#e6a23c'
  return '#f56c6c'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const viewUpsDetails = (ups: any) => {
  selectedUps.value = ups
  detailsDialogVisible.value = true
}

const configureUps = (ups: any) => {
  ElMessage.info(`Configuring ${ups.name}`)
}

const runSelfTest = () => {
  ElMessage.success('UPS self-test initiated. Results in 2 minutes.')
  detailsDialogVisible.value = false
}

const scheduleBatteryTest = () => {
  ElMessage.info('Battery test scheduling interface will open')
}

const toggleEcoMode = () => {
  ElMessage.success(`Eco Mode ${ecoModeEnabled.value ? 'enabled' : 'disabled'}`)
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const runDiagnostics = () => {
  ElMessage.success('Full system diagnostics started')
}

const exportReport = () => {
  ElMessage.success('UPS report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

// Chart initialization
const initEfficiencyGauge = () => {
  if (efficiencyGaugeRef.value) {
    const chart = echarts.init(efficiencyGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 70,
        max: 100,
        splitNumber: 6,
        progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
        axisLine: { lineStyle: { width: 18, color: [[0.6, '#f56c6c'], [0.85, '#e6a23c'], [1, '#67c23a']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}%' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12 },
        data: [{ value: upsEfficiency.value, name: 'Efficiency' }]
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
      legend: { data: ['UPS-01', 'UPS-02', 'UPS-03', 'Total Load'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'UPS-01', type: 'line', data: [180, 175, 190, 210, 205, 195], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'UPS-02', type: 'line', data: [195, 190, 205, 225, 220, 210], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'UPS-03', type: 'line', data: [170, 165, 180, 200, 195, 185], smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
        { name: 'Total Load', type: 'line', data: [545, 530, 575, 635, 620, 590], smooth: true, lineStyle: { color: '#f56c6c', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initHarmonicChart = () => {
  if (harmonicChartRef.value) {
    const chart = echarts.init(harmonicChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['1st', '3rd', '5th', '7th', '9th', '11th', '13th'] },
      yAxis: { type: 'value', name: 'Harmonic Content (%)' },
      series: [{
        type: 'bar', data: [100, 12.5, 8.2, 5.6, 3.8, 2.1, 1.2],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => {
            const val = params.data
            if (val > 10) return '#f56c6c'
            if (val > 5) return '#e6a23c'
            return '#67c23a'
          }
        },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initSavingsChart = () => {
  if (savingsChartRef.value) {
    const chart = echarts.init(savingsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Standard Mode', 'Eco Mode', 'Savings'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Energy (kWh)' },
      series: [
        { name: 'Standard Mode', type: 'line', data: [18500, 18200, 18600, 19000, 19500, 20000, 20500, 20300, 19800, 19200, 18600, 18200], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Eco Mode', type: 'line', data: [16800, 16500, 16900, 17200, 17600, 18000, 18400, 18200, 17800, 17200, 16800, 16500], lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Savings', type: 'bar', data: [1700, 1700, 1700, 1800, 1900, 2000, 2100, 2100, 2000, 2000, 1800, 1700], itemStyle: { color: '#409eff' }, label: { show: true, position: 'top', formatter: '{c} kWh' } }
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
    upsLoad.value = 48 + Math.random() * 8
    upsEfficiency.value = 94 + Math.random() * 2
    inputVoltage.value = 220 + (Math.random() - 0.5) * 3
    outputVoltage.value = 220 + (Math.random() - 0.5) * 2
    upsTemp.value = 32 + Math.random() * 4
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
        initEfficiencyGauge()
        initLoadTrendChart()
        initHarmonicChart()
        initSavingsChart()
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
.ups-optimization-container {
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
  border-right-color: #f59e0b;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #67c23a;
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
.ups-optimization-container {
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

/* Monitoring Section */
.monitoring-section {
  margin-bottom: 24px;
}

.monitoring-card,
.efficiency-card {
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

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.monitor-item {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.monitor-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.monitor-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 8px;
}

.monitor-value.warning {
  color: #f56c6c;
}

.efficiency-stats {
  margin-top: 16px;
  display: flex;
  justify-content: space-around;
}

.efficiency-stats .stat-item {
  text-align: center;
}

.efficiency-stats .stat-item span {
  display: block;
  font-size: 11px;
  color: #909399;
}

.efficiency-stats .stat-item strong {
  font-size: 16px;
  color: #303133;
}

/* UPS Units */
.ups-units-section {
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

.ups-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.ups-unit-card:hover {
  transform: translateY(-2px);
}

.ups-unit-card.status-Online {
  border-left: 4px solid #67c23a;
}

.ups-unit-card.status-Standby {
  border-left: 4px solid #e6a23c;
}

.ups-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ups-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.ups-metrics {
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

.ups-footer {
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

/* Load Stats */
.load-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.warning-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #fef0f0;
  border-radius: 8px;
  color: #f56c6c;
  font-size: 13px;
}

/* Battery Summary */
.battery-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.battery-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.forecast-item {
  margin-bottom: 16px;
}

.forecast-item span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

/* Harmonic Stats */
.harmonic-stats {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.thd-card {
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.thd-label {
  display: block;
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.thd-value {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 12px;
}

.thd-value.warning {
  color: #f56c6c;
}

.thd-target {
  display: block;
  font-size: 11px;
  color: #909399;
  margin-top: 8px;
}

.harmonic-recommendations {
  margin-top: 20px;
}

.harmonic-recommendations h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.harmonic-recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.harmonic-recommendations li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
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

.savings-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.savings-item strong {
  color: #409eff;
  font-size: 18px;
}

.eco-mode-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-top: 16px;
  border-top: 1px solid #e4e7ed;
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