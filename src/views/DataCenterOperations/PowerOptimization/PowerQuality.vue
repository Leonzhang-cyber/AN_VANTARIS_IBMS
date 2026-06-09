<template>
  <div class="power-quality-container">
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
            <span class="loading-title">Loading Power Quality</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Power Quality Monitoring & Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Power Quality</span>
          <el-tag type="primary" effect="dark" size="large">PQ Monitoring & Analysis</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="pqAlert" class="alert-banner" :class="alertType">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ alertMessage }}</span>
        <el-button size="small" :type="alertType === 'critical' ? 'danger' : 'warning'" @click="viewEventDetails">
          View Events
        </el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
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
                <span>THD Voltage</span>
              </div>
              <div class="card-value">{{ thdVoltage }}%</div>
              <div class="card-footer">
                <el-progress :percentage="thdVoltage * 2" :stroke-width="8" :color="thdColor" />
                <span class="status-text">IEC 61000: &lt;5%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Connection /></el-icon>
                <span>Voltage Unbalance</span>
              </div>
              <div class="card-value">{{ voltageUnbalance }}%</div>
              <div class="card-footer">
                <el-progress :percentage="voltageUnbalance * 4" :stroke-width="8" :color="unbalanceColor" />
                <span class="status-text">Target: &lt;2%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>Frequency Stability</span>
              </div>
              <div class="card-value">{{ frequencyStability }}%</div>
              <div class="card-footer">
                <el-progress :percentage="frequencyStability" :stroke-width="8" status="success" />
                <span class="status-text">±0.1Hz tolerance</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Real-Time Waveform -->
      <div class="waveform-section">
        <el-card class="waveform-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Monitor /></el-icon>
            <span>Real-Time Waveform</span>
            <div class="header-actions">
              <el-radio-group v-model="waveformType" size="small">
                <el-radio-button label="voltage">Voltage</el-radio-button>
                <el-radio-button label="current">Current</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="toggleLive">Live</el-button>
              <el-button size="small" type="primary" @click="captureWaveform">Capture</el-button>
            </div>
          </div>
          <div class="waveform-container">
            <div ref="waveformChartRef" style="height: 300px"></div>
          </div>
          <div class="waveform-stats">
            <div class="stat">
              <span>Vrms</span>
              <strong>{{ vrms }} V</strong>
            </div>
            <div class="stat">
              <span>Irms</span>
              <strong>{{ irms }} A</strong>
            </div>
            <div class="stat">
              <span>Crest Factor</span>
              <strong>{{ crestFactor }}</strong>
            </div>
            <div class="stat">
              <span>Frequency</span>
              <strong>{{ frequency }} Hz</strong>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Harmonic Analysis -->
      <div class="harmonic-section">
        <el-row :gutter="20">
          <el-col :span="14">
            <el-card class="harmonic-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><DataAnalysis /></el-icon>
                <span>Harmonic Spectrum</span>
                <el-tag size="small">FFT Analysis</el-tag>
              </div>
              <div class="chart-container">
                <div ref="harmonicSpectrumChartRef" style="height: 350px"></div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="10">
            <el-card class="thd-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><TrendCharts /></el-icon>
                <span>THD Trend</span>
              </div>
              <div class="chart-container">
                <div ref="thdTrendChartRef" style="height: 250px"></div>
              </div>
              <div class="thd-summary">
                <div class="thd-item">
                  <span>THD-V</span>
                  <strong :class="{ warning: thdVoltage > 5 }">{{ thdVoltage }}%</strong>
                </div>
                <div class="thd-item">
                  <span>THD-I</span>
                  <strong :class="{ warning: thdCurrent > 10 }">{{ thdCurrent }}%</strong>
                </div>
                <div class="thd-item">
                  <span>Dominant Harmonic</span>
                  <strong>{{ dominantHarmonic }}</strong>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Power Factor & Compensation -->
      <div class="pf-section">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="pf-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Setting /></el-icon>
                <span>Power Factor & Compensation</span>
              </div>
              <div class="pf-metrics">
                <div class="pf-gauge">
                  <div ref="pfGaugeRef" style="height: 200px"></div>
                </div>
                <div class="pf-details">
                  <div class="detail-item">
                    <span>Active Power (P)</span>
                    <strong>{{ activePower }} kW</strong>
                  </div>
                  <div class="detail-item">
                    <span>Reactive Power (Q)</span>
                    <strong :class="{ warning: reactivePower > 200 }">{{ reactivePower }} kVAR</strong>
                  </div>
                  <div class="detail-item">
                    <span>Apparent Power (S)</span>
                    <strong>{{ apparentPower }} kVA</strong>
                  </div>
                </div>
              </div>
              <div class="capacitor-status">
                <h4>Capacitor Bank</h4>
                <div class="cap-steps">
                  <div class="step" :class="{ active: capStep1 }">Step 1 (50kVAR)</div>
                  <div class="step" :class="{ active: capStep2 }">Step 2 (50kVAR)</div>
                  <div class="step" :class="{ active: capStep3 }">Step 3 (50kVAR)</div>
                  <div class="step" :class="{ active: capStep4 }">Step 4 (50kVAR)</div>
                </div>
                <el-button type="primary" size="small" @click="configureCapacitor">Configure</el-button>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="event-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Bell /></el-icon>
                <span>Recent Power Quality Events</span>
              </div>
              <el-table :data="pqEvents" border size="small" style="width: 100%">
                <el-table-column prop="time" label="Time" width="140" />
                <el-table-column prop="type" label="Type" width="120">
                  <template #default="{ row }">
                    <el-tag :type="getEventTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="magnitude" label="Magnitude"  />
                <el-table-column prop="duration" label="Duration"  />
                <el-table-column label="Severity" width="80">
                  <template #default="{ row }">
                    <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
              <div class="event-footer">
                <el-button type="primary" link size="small" @click="viewAllEvents">View All Events</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Three-Phase Quality Tab -->
          <el-tab-pane label="Three-Phase Quality" name="threePhase">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Connection /></el-icon>
                <span>Three-Phase Power Quality</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="threePhaseChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="phase-quality-table">
                    <el-table :data="phaseQualityData" border>
                      <el-table-column prop="phase" label="Phase" width="80" />
                      <el-table-column prop="voltage" label="Voltage (V)"  />
                      <el-table-column prop="current" label="Current (A)"  />
                      <el-table-column prop="pf" label="PF" width="80" />
                      <el-table-column prop="thd" label="THD %" width="80">
                        <template #default="{ row }">
                          <span :class="{ warning: row.thd > 5 }">{{ row.thd }}%</span>
                        </template>
                      </el-table-column>
                      <el-table-column label="Status" width="80">
                        <template #default="{ row }">
                          <el-tag :type="row.thd > 5 ? 'warning' : 'success'" size="small">
                            {{ row.thd > 5 ? 'Poor' : 'Good' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Flicker & Transients Tab -->
          <el-tab-pane label="Flicker & Transients" name="flicker">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Flicker & Transient Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="flickerChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="flicker-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ pst }}%</div>
                      <div class="stat-label">Short-term Flicker (Pst)</div>
                      <el-progress :percentage="pst * 10" :stroke-width="8" :color="pst > 1 ? '#f56c6c' : '#67c23a'" />
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ plt }}%</div>
                      <div class="stat-label">Long-term Flicker (Plt)</div>
                      <el-progress :percentage="plt * 10" :stroke-width="8" :color="plt > 0.8 ? '#f56c6c' : '#67c23a'" />
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ transientCount }}</div>
                      <div class="stat-label">Transient Events (24h)</div>
                    </div>
                    <el-button type="primary" size="small" @click="analyzeTransients">Analyze Transients</el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Sag/Swell Analysis Tab -->
          <el-tab-pane label="Sag/Swell Analysis" name="sagSwell">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Voltage Sag/Swell Events</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="sagSwellEvents" border style="width: 100%">
                    <el-table-column prop="date" label="Date" width="120" />
                    <el-table-column prop="type" label="Type" >
                      <template #default="{ row }">
                        <el-tag :type="row.type === 'Sag' ? 'warning' : 'danger'" size="small">
                          {{ row.type }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="magnitude" label="Magnitude"  />
                    <el-table-column prop="duration" label="Duration"  />
                    <el-table-column prop="affectedPhase" label="Phase" width="80" />
                    <el-table-column prop="status" label="Status" >
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'Resolved' ? 'success' : 'warning'" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="sag-summary">
                    <h4>Summary</h4>
                    <div class="summary-item">
                      <span>Total Sags</span>
                      <strong>{{ totalSags }}</strong>
                    </div>
                    <div class="summary-item">
                      <span>Total Swells</span>
                      <strong>{{ totalSwells }}</strong>
                    </div>
                    <div class="summary-item">
                      <span>Average Duration</span>
                      <strong>{{ avgDuration }} ms</strong>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="configureSagRideThrough">
                      Configure Ride-Through
                    </el-button>
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
                <span>PQ Improvement Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="recommendations" border style="width: 100%">
                    <el-table-column prop="recommendation" label="Recommendation" width="280" />
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
                    <h4>PQ Improvement Potential</h4>
                    <div class="potential-value">15.5%</div>
                    <div class="potential-label">Power Quality Score</div>
                    <el-progress :percentage="15.5" :stroke-width="12" status="success" />
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="runOptimization">
                      Run Full Analysis
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Compliance Report Tab -->
          <el-tab-pane label="Compliance" name="compliance">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>Standard Compliance Report</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="complianceData" border style="width: 100%">
                    <el-table-column prop="standard" label="Standard" width="180" />
                    <el-table-column prop="parameter" label="Parameter" />
                    <el-table-column prop="limit" label="Limit"  />
                    <el-table-column prop="current" label="Current"  />
                    <el-table-column prop="status" label="Status" >
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'Compliant' ? 'success' : 'danger'" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="compliance-summary">
                    <div class="overall-score">
                      <span>Overall Compliance Score</span>
                      <strong>{{ complianceScore }}%</strong>
                      <el-progress :percentage="complianceScore" :stroke-width="12" :color="complianceColor" />
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="generateComplianceReport">
                      Generate Report
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
                <span>PQ Alerts & Diagnostics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="pqAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" >
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="location" label="Location" width="120" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>PQ Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="pqHealthScore" :color="pqHealthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Harmonic Performance</span>
                        <el-progress :percentage="85" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Power Factor</span>
                        <el-progress :percentage="94" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Event Frequency</span>
                        <el-progress :percentage="78" :stroke-width="6" status="warning" />
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
        <el-button type="primary" size="large" @click="runFullAnalysis">
          <el-icon><Cpu /></el-icon>
          Run Full PQ Analysis
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export PQ Report
        </el-button>
        <el-button size="large" @click="scheduleAudit">
          <el-icon><Calendar /></el-icon>
          Schedule PQ Audit
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
const loadingMessage = ref('Initializing power quality analysis...')

const loadingMessages = [
  'Initializing power quality analysis...',
  'Loading waveform data...',
  'Analyzing harmonic spectrum...',
  'Processing PQ events...',
  'Calculating compliance metrics...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('threePhase')
const waveformType = ref('voltage')
const pqAlert = ref(true)
const alertType = ref('warning')
const alertMessage = ref('THD voltage exceeds 5% on Phase B. Harmonic filter recommended.')

// Power Quality metrics
const powerFactor = ref(0.94)
const thdVoltage = ref(4.8)
const thdCurrent = ref(8.5)
const voltageUnbalance = ref(1.2)
const frequencyStability = ref(98.5)
const vrms = ref(220.5)
const irms = ref(185)
const crestFactor = ref(1.42)
const frequency = ref(50.02)
const activePower = ref(385)
const reactivePower = ref(142)
const apparentPower = ref(410)
const dominantHarmonic = ref('5th')
const pst = ref(0.85)
const plt = ref(0.62)
const transientCount = ref(8)
const totalSags = ref(12)
const totalSwells = ref(3)
const avgDuration = ref(85)
const complianceScore = ref(86)
const pqHealthScore = ref(84)

// Capacitor steps
const capStep1 = ref(true)
const capStep2 = ref(true)
const capStep3 = ref(false)
const capStep4 = ref(false)

// Colors
const pfColor = computed(() => {
  if (powerFactor.value > 0.95) return '#67c23a'
  if (powerFactor.value > 0.9) return '#e6a23c'
  return '#f56c6c'
})

const thdColor = computed(() => {
  if (thdVoltage.value <= 3) return '#67c23a'
  if (thdVoltage.value <= 5) return '#e6a23c'
  return '#f56c6c'
})

const unbalanceColor = computed(() => {
  if (voltageUnbalance.value <= 1) return '#67c23a'
  if (voltageUnbalance.value <= 2) return '#e6a23c'
  return '#f56c6c'
})

const complianceColor = computed(() => {
  if (complianceScore.value >= 90) return '#67c23a'
  if (complianceScore.value >= 75) return '#e6a23c'
  return '#f56c6c'
})

const pqHealthColor = computed(() => {
  if (pqHealthScore.value >= 85) return '#67c23a'
  if (pqHealthScore.value >= 70) return '#e6a23c'
  return '#f56c6c'
})

// Phase quality data
const phaseQualityData = ref([
  { phase: 'L1', voltage: 220.5, current: 185, pf: 0.95, thd: 3.2 },
  { phase: 'L2', voltage: 219.8, current: 192, pf: 0.93, thd: 5.8 },
  { phase: 'L3', voltage: 221.2, current: 178, pf: 0.94, thd: 4.5 }
])

// PQ Events
const pqEvents = ref([
  { time: '14:23:15', type: 'Voltage Sag', magnitude: '88%', duration: '120ms', severity: 'Moderate' },
  { time: '13:45:22', type: 'Harmonic', magnitude: '5.8% THD', duration: '-', severity: 'Warning' },
  { time: '11:30:08', type: 'Transient', magnitude: '850V', duration: '50μs', severity: 'High' },
  { time: '09:15:33', type: 'Voltage Swell', magnitude: '108%', duration: '180ms', severity: 'Moderate' }
])

// Sag/Swell events
const sagSwellEvents = ref([
  { date: '2024-12-18 14:23:15', type: 'Sag', magnitude: '88%', duration: '120ms', affectedPhase: 'L2', status: 'Resolved' },
  { date: '2024-12-18 11:30:08', type: 'Swell', magnitude: '108%', duration: '180ms', affectedPhase: 'L1', status: 'Resolved' },
  { date: '2024-12-17 16:45:22', type: 'Sag', magnitude: '85%', duration: '95ms', affectedPhase: 'L3', status: 'Under Investigation' },
  { date: '2024-12-17 09:12:30', type: 'Sag', magnitude: '92%', duration: '65ms', affectedPhase: 'L1', status: 'Resolved' }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Install active harmonic filter (5th/7th/11th)', impact: 'Reduce THD to <3%', priority: 'High' },
  { recommendation: 'Add capacitor bank step for power factor correction', impact: 'Improve PF to 0.98', priority: 'High' },
  { recommendation: 'Install surge protection on main feed', impact: 'Reduce transient events', priority: 'Medium' },
  { recommendation: 'Balance phase loads to reduce unbalance', impact: 'Reduce unbalance to <1%', priority: 'Medium' }
])

// Compliance data
const complianceData = ref([
  { standard: 'IEC 61000-2-4', parameter: 'THD Voltage', limit: '≤5%', current: '4.8%', status: 'Compliant' },
  { standard: 'IEC 61000-2-4', parameter: 'Power Factor', limit: '≥0.90', current: '0.94', status: 'Compliant' },
  { standard: 'IEEE 519', parameter: 'THD Current', limit: '≤8%', current: '8.5%', status: 'Non-Compliant' },
  { standard: 'IEC 61000-2-4', parameter: 'Voltage Unbalance', limit: '≤2%', current: '1.2%', status: 'Compliant' }
])

// Alerts
const pqAlerts = ref([
  { severity: 'Warning', message: 'THD voltage exceeded 5% on Phase B', location: 'Main Feed', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'Power factor dropped below 0.92', location: 'PDU-A01', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'Voltage sag detected on Phase L2', location: 'UPS Input', timestamp: '2024-12-18 08:30' }
])

// Chart refs
const waveformChartRef = ref<HTMLElement | null>(null)
const harmonicSpectrumChartRef = ref<HTMLElement | null>(null)
const thdTrendChartRef = ref<HTMLElement | null>(null)
const pfGaugeRef = ref<HTMLElement | null>(null)
const threePhaseChartRef = ref<HTMLElement | null>(null)
const flickerChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []
let waveformInterval: ReturnType<typeof setInterval>

// Methods
const goBack = () => {
  router.back()
}

const viewEventDetails = () => {
  activeTab.value = 'sagSwell'
  ElMessage.info('Viewing event details')
}

const getEventTypeTag = (type: string) => {
  if (type.includes('Sag')) return 'warning'
  if (type.includes('Swell')) return 'danger'
  if (type === 'Harmonic') return 'warning'
  return 'info'
}

const getSeverityType = (severity: string) => {
  if (severity === 'High') return 'danger'
  if (severity === 'Moderate') return 'warning'
  return 'info'
}

const toggleLive = () => {
  if (waveformInterval) {
    clearInterval(waveformInterval)
    waveformInterval = null as any
    ElMessage.info('Live waveform stopped')
  } else {
    startWaveformSimulation()
    ElMessage.success('Live waveform started')
  }
}

const captureWaveform = () => {
  ElMessage.success('Waveform captured and saved')
}

const configureCapacitor = () => {
  ElMessage.info('Capacitor bank configuration interface will open')
}

const viewAllEvents = () => {
  activeTab.value = 'sagSwell'
}

const analyzeTransients = () => {
  ElMessage.success('Transient analysis started')
}

const configureSagRideThrough = () => {
  ElMessage.info('Ride-through configuration interface will open')
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('Power quality optimization started')
}

const runFullAnalysis = () => {
  ElMessage.success('Full power quality analysis started')
}

const exportReport = () => {
  ElMessage.success('Power quality report export started')
}

const scheduleAudit = () => {
  ElMessage.info('PQ audit scheduling interface will open')
}

const generateComplianceReport = () => {
  ElMessage.success('Compliance report generated')
}

// Waveform simulation
const startWaveformSimulation = () => {
  let time = 0
  waveformInterval = setInterval(() => {
    time += 0.02
    if (waveformChartRef.value) {
      initWaveformChart(time)
    }
  }, 100)
}

// Chart initialization
const initWaveformChart = (offset = 0) => {
  if (waveformChartRef.value) {
    const chart = echarts.getInstanceByDom(waveformChartRef.value) || echarts.init(waveformChartRef.value)
    const data = []
    for (let i = 0; i < 200; i++) {
      let value
      if (waveformType.value === 'voltage') {
        value = 311 * Math.sin(i * 0.1 + offset)
      } else {
        value = 260 * Math.sin(i * 0.1 + offset)
      }
      data.push(value)
    }
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', show: false },
      yAxis: { type: 'value', name: waveformType.value === 'voltage' ? 'Voltage (V)' : 'Current (A)' },
      series: [{
        type: 'line', data: data, smooth: false,
        lineStyle: { color: waveformType.value === 'voltage' ? '#409eff' : '#67c23a', width: 1.5 },
        areaStyle: { opacity: 0.1 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initHarmonicSpectrumChart = () => {
  if (harmonicSpectrumChartRef.value) {
    const chart = echarts.init(harmonicSpectrumChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['1st', '3rd', '5th', '7th', '9th', '11th', '13th', '15th'] },
      yAxis: { type: 'value', name: 'Harmonic Content (%)' },
      series: [
        { name: 'Voltage', type: 'bar', data: [100, 2.5, 4.8, 3.2, 1.8, 2.1, 1.2, 0.8], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } },
        { name: 'Current', type: 'bar', data: [100, 4.2, 8.5, 5.6, 3.2, 3.8, 2.1, 1.5], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initThdTrendChart = () => {
  if (thdTrendChartRef.value) {
    const chart = echarts.init(thdTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['THD-V', 'THD-I', 'Limit'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: { type: 'value', name: 'THD (%)' },
      series: [
        { name: 'THD-V', type: 'line', data: [4.2, 3.8, 4.5, 5.2, 4.8, 4.3], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'THD-I', type: 'line', data: [7.5, 6.8, 8.2, 9.5, 8.8, 7.2], smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Limit', type: 'line', data: [5, 5, 5, 5, 5, 5], lineStyle: { color: '#f56c6c', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPfGauge = () => {
  if (pfGaugeRef.value) {
    const chart = echarts.init(pfGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 0,
        max: 1,
        splitNumber: 5,
        progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
        axisLine: { lineStyle: { width: 18, color: [[0.9, '#f56c6c'], [0.95, '#e6a23c'], [1, '#67c23a']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12, formatter: 'Power Factor' },
        data: [{ value: powerFactor.value, name: 'PF' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initThreePhaseChart = () => {
  if (threePhaseChartRef.value) {
    const chart = echarts.init(threePhaseChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Voltage (V)', 'Current (A)', 'THD (%)'] },
      xAxis: { type: 'category', data: ['L1', 'L2', 'L3'] },
      yAxis: [
        { type: 'value', name: 'Voltage (V)' },
        { type: 'value', name: 'Current (A)' },
        { type: 'value', name: 'THD (%)' }
      ],
      series: [
        { name: 'Voltage (V)', type: 'bar', data: [220.5, 219.8, 221.2], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Current (A)', type: 'bar', yAxisIndex: 1, data: [185, 192, 178], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'THD (%)', type: 'line', yAxisIndex: 2, data: [3.2, 5.8, 4.5], lineStyle: { color: '#f56c6c', width: 2 }, symbol: 'circle', symbolSize: 8, label: { show: true, formatter: '{c}%' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initFlickerChart = () => {
  if (flickerChartRef.value) {
    const chart = echarts.init(flickerChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: { type: 'value', name: 'Flicker (Pst)' },
      series: [{
        type: 'line', data: [0.45, 0.42, 0.38, 0.41, 0.68, 0.85, 0.92, 0.88, 0.75, 0.62, 0.55, 0.48],
        smooth: true, lineStyle: { color: '#f59e0b', width: 2 }, areaStyle: { opacity: 0.3 },
        markLine: { data: [{ yAxis: 1, label: { formatter: 'Limit Pst=1' }, lineStyle: { color: '#f56c6c', type: 'dashed' } }] }
      }]
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
        initWaveformChart()
        initHarmonicSpectrumChart()
        initThdTrendChart()
        initPfGauge()
        initThreePhaseChart()
        initFlickerChart()
        startWaveformSimulation()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (waveformInterval) clearInterval(waveformInterval)
  chartInstances.forEach(chart => chart.dispose())
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.power-quality-container {
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
.power-quality-container {
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

/* Waveform Section */
.waveform-section {
  margin-bottom: 24px;
}

.waveform-card {
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

.waveform-container {
  min-height: 300px;
}

.waveform-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.waveform-stats .stat {
  text-align: center;
}

.waveform-stats .stat span {
  display: block;
  font-size: 11px;
  color: #909399;
}

.waveform-stats .stat strong {
  font-size: 18px;
  color: #303133;
}

/* Harmonic Section */
.harmonic-section {
  margin-bottom: 24px;
}

.harmonic-card,
.thd-card {
  height: 100%;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.thd-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.thd-item {
  text-align: center;
}

.thd-item span {
  display: block;
  font-size: 11px;
  color: #909399;
}

.thd-item strong {
  font-size: 18px;
  color: #303133;
}

.thd-item strong.warning {
  color: #f56c6c;
}

/* PF Section */
.pf-section {
  margin-bottom: 24px;
}

.pf-card,
.event-card {
  height: 100%;
}

.pf-metrics {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.pf-gauge {
  width: 100%;
}

.pf-details {
  display: flex;
  justify-content: space-around;
  width: 100%;
  margin-top: 16px;
}

.detail-item {
  text-align: center;
}

.detail-item span {
  display: block;
  font-size: 11px;
  color: #909399;
}

.detail-item strong {
  font-size: 14px;
  color: #303133;
}

.detail-item strong.warning {
  color: #f56c6c;
}

.capacitor-status {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.capacitor-status h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.cap-steps {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.step {
  flex: 1;
  text-align: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 11px;
  color: #909399;
}

.step.active {
  background: #ecf5ff;
  color: #409eff;
  border: 1px solid #409eff;
}

.event-footer {
  margin-top: 12px;
  text-align: center;
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

/* Phase Quality Table */
.phase-quality-table {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
  height: 100%;
}

.phase-quality-table .warning {
  color: #f56c6c;
}

/* Flicker Stats */
.flicker-stats {
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
  margin: 8px 0;
}

/* Sag Summary */
.sag-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.sag-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.summary-item strong {
  color: #409eff;
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

/* Compliance Summary */
.compliance-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  height: 100%;
}

.overall-score {
  margin-bottom: 16px;
}

.overall-score span {
  display: block;
  font-size: 13px;
  color: #909399;
  margin-bottom: 8px;
}

.overall-score strong {
  font-size: 36px;
  color: #409eff;
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