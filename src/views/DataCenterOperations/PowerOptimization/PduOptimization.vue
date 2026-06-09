<template>
  <div class="pdu-optimization-container">
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
            <span class="loading-title">Loading PDU Optimization</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Power Distribution Unit Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">PDU Optimization</span>
          <el-tag type="primary" effect="dark" size="large">Power Distribution Optimization</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Total Power</span>
              </div>
              <div class="card-value">{{ totalPower }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="68" :stroke-width="8" status="warning" />
                <span class="status-text">of {{ totalCapacity }} kW capacity</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Connection /></el-icon>
                <span>Load Balance</span>
              </div>
              <div class="card-value">{{ loadBalance }}%</div>
              <div class="card-footer">
                <el-progress :percentage="loadBalance" :stroke-width="8" :color="balanceColor" />
                <span class="status-text">Unbalance: {{ unbalance }}%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Odometer /></el-icon>
                <span>Power Factor</span>
              </div>
              <div class="card-value">{{ powerFactor }}</div>
              <div class="card-footer">
                <el-progress :percentage="powerFactor * 100" :stroke-width="8" :color="pfColor" />
                <span class="status-text">Target: >0.95</span>
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
                <span class="status-text">Load balancing savings</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Real-Time Phase Monitoring -->
      <div class="phase-section">
        <el-card class="phase-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Connection /></el-icon>
            <span>Three-Phase Load Monitoring</span>
            <el-tag type="success" size="small">Real-Time</el-tag>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="phase-item phase-l1">
                <div class="phase-header">
                  <span class="phase-name">L1</span>
                  <el-tag :type="getPhaseTagType(phaseL1.load)" size="small">{{ phaseL1.load }}%</el-tag>
                </div>
                <div class="phase-value">{{ phaseL1.current }} A</div>
                <el-progress :percentage="phaseL1.load" :stroke-width="10" :color="getPhaseColor(phaseL1.load)" />
                <div class="phase-details">
                  <span>Voltage: {{ phaseL1.voltage }}V</span>
                  <span>Power: {{ phaseL1.power }} kW</span>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="phase-item phase-l2">
                <div class="phase-header">
                  <span class="phase-name">L2</span>
                  <el-tag :type="getPhaseTagType(phaseL2.load)" size="small">{{ phaseL2.load }}%</el-tag>
                </div>
                <div class="phase-value">{{ phaseL2.current }} A</div>
                <el-progress :percentage="phaseL2.load" :stroke-width="10" :color="getPhaseColor(phaseL2.load)" />
                <div class="phase-details">
                  <span>Voltage: {{ phaseL2.voltage }}V</span>
                  <span>Power: {{ phaseL2.power }} kW</span>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="phase-item phase-l3">
                <div class="phase-header">
                  <span class="phase-name">L3</span>
                  <el-tag :type="getPhaseTagType(phaseL3.load)" size="small">{{ phaseL3.load }}%</el-tag>
                </div>
                <div class="phase-value">{{ phaseL3.current }} A</div>
                <el-progress :percentage="phaseL3.load" :stroke-width="10" :color="getPhaseColor(phaseL3.load)" />
                <div class="phase-details">
                  <span>Voltage: {{ phaseL3.voltage }}V</span>
                  <span>Power: {{ phaseL3.power }} kW</span>
                </div>
              </div>
            </el-col>
          </el-row>
          <div class="balance-indicator">
            <span>Load Balance Status:</span>
            <el-tag :type="balanceStatusType" size="large">{{ balanceStatus }}</el-tag>
            <el-button size="small" type="primary" @click="rebalanceLoads">Suggest Rebalancing</el-button>
          </div>
        </el-card>
      </div>

      <!-- PDU Units Status -->
      <div class="pdu-units-section">
        <div class="section-header">
          <h3>PDU Units Status</h3>
          <div class="header-controls">
            <el-radio-group v-model="unitView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="6" v-for="pdu in pduUnits" :key="pdu.id">
            <el-card class="pdu-unit-card" :class="`status-${pdu.status}`" shadow="hover">
              <div class="pdu-header">
                <span class="pdu-name">{{ pdu.name }}</span>
                <el-tag :type="getPduTagType(pdu.status)" size="small">{{ pdu.status }}</el-tag>
              </div>
              <div class="pdu-metrics">
                <div class="metric-row">
                  <div class="metric">
                    <span>Load</span>
                    <strong>{{ pdu.load }}%</strong>
                    <el-progress :percentage="pdu.load" :stroke-width="4" :color="getLoadColor(pdu.load)" :show-text="false" />
                  </div>
                  <div class="metric">
                    <span>Power</span>
                    <strong>{{ pdu.power }} kW</strong>
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Ports Used</span>
                    <strong>{{ pdu.portsUsed }}/{{ pdu.totalPorts }}</strong>
                  </div>
                  <div class="metric">
                    <span>Temp</span>
                    <strong :class="{ warning: pdu.temp > 45 }">{{ pdu.temp }}°C</strong>
                  </div>
                </div>
              </div>
              <div class="pdu-footer">
                <el-button type="primary" size="small" @click="viewPduDetails(pdu)">Details</el-button>
                <el-button size="small" @click="configurePdu(pdu)">Configure</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="pduUnits" border v-else style="width: 100%">
          <el-table-column prop="name" label="Unit" width="120" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getPduTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="load" label="Load %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.load" :stroke-width="8" :color="getLoadColor(row.load)" />
            </template>
          </el-table-column>
          <el-table-column prop="power" label="Power (kW)" width="100" />
          <el-table-column prop="portsUsed" label="Ports Used" width="100" />
          <el-table-column prop="temp" label="Temp (°C)" width="100">
            <template #default="{ row }">
              <span :class="{ warning: row.temp > 45 }">{{ row.temp }}°C</span>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewPduDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="configurePdu(row)">Config</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Load Distribution Tab -->
          <el-tab-pane label="Load Distribution" name="distribution">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><PieChart /></el-icon>
                <span>Load Distribution Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="loadDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="distribution-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ maxPhaseLoad }} kW</div>
                      <div class="stat-label">Max Phase Load</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ minPhaseLoad }} kW</div>
                      <div class="stat-label">Min Phase Load</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ unbalance }}%</div>
                      <div class="stat-label">Unbalance Rate</div>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="optimizeLoadBalance">
                      Optimize Load Balance
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Port Monitoring Tab -->
          <el-tab-pane label="Port Monitoring" name="ports">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>Outlet Port Monitoring</span>
              </div>
              <el-table :data="portData" border style="width: 100%">
                <el-table-column prop="port" label="Port" width="80" />
                <el-table-column prop="device" label="Connected Device" />
                <el-table-column prop="power" label="Power (W)" width="120" />
                <el-table-column prop="current" label="Current (A)" width="100" />
                <el-table-column prop="voltage" label="Voltage (V)" width="100" />
                <el-table-column prop="status" label="Status" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'On' ? 'success' : 'danger'" size="small">
                      {{ row.status }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="Control" width="120">
                  <template #default="{ row }">
                    <el-switch v-model="row.status" active-value="On" inactive-value="Off" @change="togglePort(row)" />
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <!-- Power Quality Tab -->
          <el-tab-pane label="Power Quality" name="quality">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
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
                    <div class="quality-item">
                      <span>THD Voltage</span>
                      <el-progress :percentage="3.2" :stroke-width="8" :format="() => '3.2%'" status="success" />
                    </div>
                    <div class="quality-item">
                      <span>THD Current</span>
                      <el-progress :percentage="5.8" :stroke-width="8" :format="() => '5.8%'" status="success" />
                    </div>
                    <div class="quality-item">
                      <span>Power Factor</span>
                      <el-progress :percentage="94" :stroke-width="8" :format="() => '0.94'" status="success" />
                    </div>
                    <div class="quality-item">
                      <span>Frequency Stability</span>
                      <el-progress :percentage="98" :stroke-width="8" :format="() => '±0.1Hz'" status="success" />
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Energy Consumption Tab -->
          <el-tab-pane label="Energy Consumption" name="energy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Energy Consumption Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="energyTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="energy-stats">
                    <div class="stat-card energy">
                      <div class="stat-value">1,245,000 kWh</div>
                      <div class="stat-label">YTD Energy Consumption</div>
                    </div>
                    <div class="stat-card energy">
                      <div class="stat-value">$149,400</div>
                      <div class="stat-label">YTD Energy Cost</div>
                    </div>
                    <div class="stat-card energy">
                      <div class="stat-value">68.5 tCO₂e</div>
                      <div class="stat-label">Carbon Emissions</div>
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
                    <h4>Total Savings Potential</h4>
                    <div class="potential-value">12.5%</div>
                    <div class="potential-label">Energy Reduction</div>
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
                <span>PDU Alerts & Diagnostics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="pduAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="pdu" label="PDU" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>PDU Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Load Balance</span>
                        <el-progress :percentage="loadBalance" :stroke-width="6" :color="balanceColor" />
                      </div>
                      <div class="health-item">
                        <span>Temperature</span>
                        <el-progress :percentage="72" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Port Utilization</span>
                        <el-progress :percentage="portUtilization" :stroke-width="6" status="warning" />
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
          Export PDU Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </template>

    <!-- PDU Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`PDU ${selectedPdu?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedPdu">
        <el-descriptions-item label="Status">
          <el-tag :type="getPduTagType(selectedPdu.status)">{{ selectedPdu.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Model">APC AP8886</el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedPdu.load }}%</el-descriptions-item>
        <el-descriptions-item label="Power">{{ selectedPdu.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Voltage">220/380 V</el-descriptions-item>
        <el-descriptions-item label="Current">{{ selectedPdu.current || 185 }} A</el-descriptions-item>
        <el-descriptions-item label="Ports Used">{{ selectedPdu.portsUsed }}/{{ selectedPdu.totalPorts }}</el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedPdu.temp }}°C</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">2024-11-10</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">2025-02-10</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="remoteReboot">Remote Reboot</el-button>
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
const loadingMessage = ref('Initializing PDU systems...')

const loadingMessages = [
  'Initializing PDU systems...',
  'Loading power distribution data...',
  'Analyzing phase balance...',
  'Calculating port utilization...',
  'Detecting power quality issues...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('distribution')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const selectedPdu = ref<any>(null)

// Real-time metrics
const totalPower = ref(425)
const totalCapacity = ref(625)
const loadBalance = ref(78)
const unbalance = ref(12)
const powerFactor = ref(0.94)
const energySavings = ref(8.5)
const portUtilization = ref(65)
const healthScore = ref(84)

// Phase data
const phaseL1 = ref({ load: 65, current: 125, voltage: 221, power: 145 })
const phaseL2 = ref({ load: 72, current: 138, voltage: 219, power: 158 })
const phaseL3 = ref({ load: 58, current: 112, voltage: 222, power: 122 })

const maxPhaseLoad = ref(158)
const minPhaseLoad = ref(122)

// Computed
const balanceColor = computed(() => {
  if (loadBalance.value > 85) return '#67c23a'
  if (loadBalance.value > 70) return '#e6a23c'
  return '#f56c6c'
})

const pfColor = computed(() => {
  if (powerFactor.value > 0.95) return '#67c23a'
  if (powerFactor.value > 0.9) return '#e6a23c'
  return '#f56c6c'
})

const balanceStatus = computed(() => {
  if (unbalance.value < 5) return 'Excellent'
  if (unbalance.value < 10) return 'Good'
  if (unbalance.value < 15) return 'Moderate'
  return 'Poor'
})

const balanceStatusType = computed(() => {
  if (unbalance.value < 5) return 'success'
  if (unbalance.value < 10) return 'success'
  if (unbalance.value < 15) return 'warning'
  return 'danger'
})

const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

// PDU units data
const pduUnits = ref([
  { id: 1, name: 'PDU-A01', status: 'Online', load: 62, power: 52.5, portsUsed: 18, totalPorts: 24, temp: 38, current: 142 },
  { id: 2, name: 'PDU-A02', status: 'Online', load: 58, power: 48.2, portsUsed: 16, totalPorts: 24, temp: 36, current: 135 },
  { id: 3, name: 'PDU-B01', status: 'Online', load: 71, power: 59.8, portsUsed: 22, totalPorts: 24, temp: 42, current: 168 },
  { id: 4, name: 'PDU-B02', status: 'Warning', load: 85, power: 71.2, portsUsed: 24, totalPorts: 24, temp: 48, current: 195 },
  { id: 5, name: 'PDU-C01', status: 'Online', load: 45, power: 38.5, portsUsed: 14, totalPorts: 24, temp: 34, current: 108 },
  { id: 6, name: 'PDU-C02', status: 'Online', load: 52, power: 44.0, portsUsed: 15, totalPorts: 24, temp: 35, current: 118 }
])

// Port data
const portData = ref([
  { port: '01', device: 'Server Rack A01', power: 450, current: 2.0, voltage: 220, status: 'On' },
  { port: '02', device: 'Server Rack A02', power: 520, current: 2.3, voltage: 220, status: 'On' },
  { port: '03', device: 'Storage Array', power: 380, current: 1.7, voltage: 220, status: 'On' },
  { port: '04', device: 'Network Switch', power: 120, current: 0.5, voltage: 220, status: 'On' },
  { port: '05', device: 'Firewall', power: 85, current: 0.4, voltage: 220, status: 'On' },
  { port: '06', device: 'Server Rack A03', power: 490, current: 2.2, voltage: 220, status: 'Off' }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Re-balance phases L1/L2/L3 loads', impact: '+5% efficiency', priority: 'High' },
  { recommendation: 'Reduce PDU-B02 load (currently 85%)', impact: 'Improve reliability', priority: 'High' },
  { recommendation: 'Add additional PDU for high-density rack', impact: '+15% capacity', priority: 'Medium' },
  { recommendation: 'Enable port-level power scheduling', impact: '+8% energy savings', priority: 'Medium' }
])

// Alerts
const pduAlerts = ref([
  { severity: 'Warning', message: 'PDU-B02 load exceeds 80%', pdu: 'PDU-B02', timestamp: '2024-12-18 14:23' },
  { severity: 'Critical', message: 'Phase L2 unbalance detected', pdu: 'PDU-A01', timestamp: '2024-12-18 10:15' },
  { severity: 'Info', message: 'Port utilization reached 90% on PDU-B01', pdu: 'PDU-B01', timestamp: '2024-12-18 08:30' }
])

// Chart refs
const loadDistributionChartRef = ref<HTMLElement | null>(null)
const powerQualityChartRef = ref<HTMLElement | null>(null)
const energyTrendChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const getPhaseTagType = (load: number) => {
  if (load < 60) return 'success'
  if (load < 75) return 'warning'
  return 'danger'
}

const getPhaseColor = (load: number) => {
  if (load < 60) return '#67c23a'
  if (load < 75) return '#e6a23c'
  return '#f56c6c'
}

const getPduTagType = (status: string) => {
  if (status === 'Online') return 'success'
  if (status === 'Warning') return 'warning'
  return 'info'
}

const getLoadColor = (load: number) => {
  if (load < 60) return '#67c23a'
  if (load < 80) return '#e6a23c'
  return '#f56c6c'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const viewPduDetails = (pdu: any) => {
  selectedPdu.value = pdu
  detailsDialogVisible.value = true
}

const configurePdu = (pdu: any) => {
  ElMessage.info(`Configuring ${pdu.name}`)
}

const remoteReboot = () => {
  ElMessage.success(`Remote reboot initiated for ${selectedPdu.value.name}`)
  detailsDialogVisible.value = false
}

const togglePort = (port: any) => {
  ElMessage.success(`Port ${port.port} turned ${port.status.toLowerCase()}`)
}

const rebalanceLoads = () => {
  ElMessage.success('Load rebalancing suggestion generated. Moving 15A from L2 to L3.')
}

const optimizeLoadBalance = () => {
  ElMessage.success('Load balance optimization started. New configuration will be applied.')
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
  ElMessage.success('PDU report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

// Chart initialization
const initLoadDistributionChart = () => {
  if (loadDistributionChartRef.value) {
    const chart = echarts.init(loadDistributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['L1', 'L2', 'L3'] },
      xAxis: { type: 'category', data: ['PDU-A01', 'PDU-A02', 'PDU-B01', 'PDU-B02', 'PDU-C01', 'PDU-C02'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'L1', type: 'bar', data: [48, 42, 55, 68, 35, 40], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'L2', type: 'bar', data: [52, 46, 60, 72, 38, 42], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'L3', type: 'bar', data: [44, 38, 50, 65, 32, 36], itemStyle: { color: '#e6a23c', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
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
        { name: 'Voltage (V)', type: 'line', data: [220, 221, 220, 219, 220, 221], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'Current (A)', type: 'line', data: [125, 118, 135, 145, 138, 128], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Power Factor', type: 'line', yAxisIndex: 2, data: [0.94, 0.93, 0.95, 0.94, 0.93, 0.94], smooth: true, lineStyle: { color: '#f59e0b', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initEnergyTrendChart = () => {
  if (energyTrendChartRef.value) {
    const chart = echarts.init(energyTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Energy Consumption', 'Cost'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: [
        { type: 'value', name: 'Energy (kWh)' },
        { type: 'value', name: 'Cost ($)' }
      ],
      series: [
        { name: 'Energy Consumption', type: 'line', data: [105000, 102000, 108000, 112000, 115000, 118000, 120000, 118000, 115000, 110000, 106000, 103000], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Cost', type: 'line', yAxisIndex: 1, data: [12600, 12240, 12960, 13440, 13800, 14160, 14400, 14160, 13800, 13200, 12720, 12360], smooth: true, lineStyle: { color: '#f56c6c', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

// Simulate real-time updates
let realTimeInterval: ReturnType<typeof setInterval>

const startRealTimeUpdates = () => {
  realTimeInterval = setInterval(() => {
    // Simulate changing metrics
    phaseL1.value.current = 120 + Math.random() * 20
    phaseL2.value.current = 125 + Math.random() * 25
    phaseL3.value.current = 105 + Math.random() * 15

    phaseL1.value.load = Math.round((phaseL1.value.current / 200) * 100)
    phaseL2.value.load = Math.round((phaseL2.value.current / 200) * 100)
    phaseL3.value.load = Math.round((phaseL3.value.current / 200) * 100)

    totalPower.value = 400 + Math.random() * 50
    powerFactor.value = 0.92 + Math.random() * 0.04
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
        initLoadDistributionChart()
        initPowerQualityChart()
        initEnergyTrendChart()
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
.pdu-optimization-container {
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
.pdu-optimization-container {
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

/* Phase Section */
.phase-section {
  margin-bottom: 24px;
}

.phase-card {
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

.phase-item {
  padding: 16px;
  border-radius: 12px;
  background: #f5f7fa;
}

.phase-l1 .phase-name { color: #409eff; }
.phase-l2 .phase-name { color: #67c23a; }
.phase-l3 .phase-name { color: #e6a23c; }

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.phase-name {
  font-size: 18px;
  font-weight: 600;
}

.phase-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin: 12px 0;
}

.phase-details {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
}

.balance-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

/* PDU Units */
.pdu-units-section {
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

.pdu-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.pdu-unit-card:hover {
  transform: translateY(-2px);
}

.pdu-unit-card.status-Online {
  border-left: 4px solid #67c23a;
}

.pdu-unit-card.status-Warning {
  border-left: 4px solid #e6a23c;
}

.pdu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.pdu-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.pdu-metrics {
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

.pdu-footer {
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

/* Distribution Stats */
.distribution-stats {
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

.stat-card.energy {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #409eff;
}

.stat-card.energy .stat-value {
  color: #d97706;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

/* Quality Metrics */
.quality-metrics {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.quality-item {
  margin-bottom: 24px;
}

.quality-item span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

/* Energy Stats */
.energy-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
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