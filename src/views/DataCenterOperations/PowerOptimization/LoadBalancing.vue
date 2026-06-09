<template>
  <div class="load-balancing-container">
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
            <span class="loading-title">Loading Load Balancing</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Power Load Distribution Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Load Balancing</span>
          <el-tag type="primary" effect="dark" size="large">Power Distribution Optimization</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="unbalanceAlert" class="alert-banner warning">
        <el-icon><Warning /></el-icon>
        <span>Phase L2 load is {{ unbalanceLevel }}% above average. Load balancing recommended.</span>
        <el-button size="small" type="warning" @click="optimizeNow">Optimize Now</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Total Load</span>
              </div>
              <div class="card-value">{{ totalLoad }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="(totalLoad / totalCapacity) * 100" :stroke-width="8" status="warning" />
                <span class="status-text">Capacity: {{ totalCapacity }} kW</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Connection /></el-icon>
                <span>Balance Index</span>
              </div>
              <div class="card-value">{{ balanceIndex }}%</div>
              <div class="card-footer">
                <el-progress :percentage="balanceIndex" :stroke-width="8" :color="balanceColor" />
                <span class="status-text">Target: >90%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Peak Load</span>
              </div>
              <div class="card-value">{{ peakLoad }} kW</div>
              <div class="card-footer">
                <el-progress :percentage="(peakLoad / totalCapacity) * 100" :stroke-width="8" status="exception" />
                <span class="status-text">Peak at {{ peakTime }}</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Coin /></el-icon>
                <span>Demand Savings</span>
              </div>
              <div class="card-value">${{ demandSavings }}K</div>
              <div class="card-footer">
                <el-progress :percentage="75" :stroke-width="8" status="success" />
                <span class="status-text">Since load balancing</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Three-Phase Load Balance -->
      <div class="phase-section">
        <el-card class="phase-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Connection /></el-icon>
            <span>Three-Phase Load Balance</span>
            <el-tag type="success" size="small">Real-Time</el-tag>
          </div>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="phase-bar phase-l1">
                <div class="phase-header">
                  <span class="phase-name">L1</span>
                  <span class="phase-value">{{ phaseL1.load }} kW</span>
                </div>
                <el-progress :percentage="phaseL1.percentage" :stroke-width="20" :color="getPhaseColor(phaseL1.percentage)" />
                <div class="phase-details">
                  <span>Current: {{ phaseL1.current }} A</span>
                  <span>Deviation: {{ phaseL1.deviation }}%</span>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="phase-bar phase-l2">
                <div class="phase-header">
                  <span class="phase-name">L2</span>
                  <span class="phase-value">{{ phaseL2.load }} kW</span>
                </div>
                <el-progress :percentage="phaseL2.percentage" :stroke-width="20" :color="getPhaseColor(phaseL2.percentage)" />
                <div class="phase-details">
                  <span>Current: {{ phaseL2.current }} A</span>
                  <span>Deviation: {{ phaseL2.deviation }}%</span>
                </div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="phase-bar phase-l3">
                <div class="phase-header">
                  <span class="phase-name">L3</span>
                  <span class="phase-value">{{ phaseL3.load }} kW</span>
                </div>
                <el-progress :percentage="phaseL3.percentage" :stroke-width="20" :color="getPhaseColor(phaseL3.percentage)" />
                <div class="phase-details">
                  <span>Current: {{ phaseL3.current }} A</span>
                  <span>Deviation: {{ phaseL3.deviation }}%</span>
                </div>
              </div>
            </el-col>
          </el-row>
          <div class="balance-stats">
            <div class="stat">
              <span>Max Phase Load</span>
              <strong>{{ maxPhaseLoad }} kW</strong>
            </div>
            <div class="stat">
              <span>Min Phase Load</span>
              <strong>{{ minPhaseLoad }} kW</strong>
            </div>
            <div class="stat">
              <span>Unbalance Rate</span>
              <strong :class="{ warning: unbalanceRate > 10 }">{{ unbalanceRate }}%</strong>
            </div>
            <div class="stat">
              <span>Balance Improvement</span>
              <strong class="success">+{{ balanceImprovement }}%</strong>
            </div>
          </div>
        </el-card>
      </div>

      <!-- PDU Load Distribution -->
      <div class="pdu-section">
        <div class="section-header">
          <h3>PDU Load Distribution</h3>
          <div class="header-controls">
            <el-radio-group v-model="pduView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="pduView === 'grid'">
          <el-col :span="6" v-for="pdu in pduLoads" :key="pdu.id">
            <el-card class="pdu-load-card" :class="`load-${pdu.status}`" shadow="hover">
              <div class="pdu-header">
                <span class="pdu-name">{{ pdu.name }}</span>
                <el-tag :type="getLoadTagType(pdu.loadPercentage)" size="small">
                  {{ pdu.loadPercentage }}%
                </el-tag>
              </div>
              <div class="pdu-load">
                <el-progress :percentage="pdu.loadPercentage" :stroke-width="12" :color="getLoadColor(pdu.loadPercentage)" />
              </div>
              <div class="pdu-metrics">
                <div class="metric">
                  <span>Current Load</span>
                  <strong>{{ pdu.currentLoad }} kW</strong>
                </div>
                <div class="metric">
                  <span>Rated Capacity</span>
                  <strong>{{ pdu.ratedCapacity }} kW</strong>
                </div>
              </div>
              <div class="pdu-phases">
                <div class="phase-mini">
                  <span class="phase-l1-mini">L1: {{ pdu.l1 }} kW</span>
                  <span class="phase-l2-mini">L2: {{ pdu.l2 }} kW</span>
                  <span class="phase-l3-mini">L3: {{ pdu.l3 }} kW</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="pduLoads" border v-else style="width: 100%">
          <el-table-column prop="name" label="PDU" width="100" />
          <el-table-column prop="loadPercentage" label="Load %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.loadPercentage" :stroke-width="8" :color="getLoadColor(row.loadPercentage)" />
            </template>
          </el-table-column>
          <el-table-column prop="currentLoad" label="Current Load (kW)" width="120" />
          <el-table-column prop="ratedCapacity" label="Capacity (kW)" width="120" />
          <el-table-column prop="l1" label="L1 (kW)" width="80" />
          <el-table-column prop="l2" label="L2 (kW)" width="80" />
          <el-table-column prop="l3" label="L3 (kW)" width="80" />
          <el-table-column label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getLoadTagType(row.loadPercentage)" size="small">
                {{ row.status }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Rack Level Load Distribution -->
      <div class="rack-section">
        <div class="section-header">
          <h3>Rack Level Load Distribution</h3>
          <el-button size="small" type="primary" @click="viewHeatmap">View Heatmap</el-button>
        </div>
        <div class="rack-grid">
          <div v-for="row in rackRows" :key="row.name" class="rack-row">
            <div class="row-label">{{ row.name }}</div>
            <div class="row-racks">
              <div
                  v-for="rack in row.racks"
                  :key="rack.id"
                  class="rack-load-cell"
                  :style="{ backgroundColor: getRackLoadColor(rack.load) }"
                  @click="showRackDetails(rack)"
              >
                <div class="rack-id">{{ rack.id }}</div>
                <div class="rack-load">{{ rack.load }} kW</div>
                <div class="rack-percent">{{ rack.loadPercentage }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Load Trends Tab -->
          <el-tab-pane label="Load Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Load History & Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="loadTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="phaseComparisonChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Load Migration Suggestions Tab -->
          <el-tab-pane label="Load Migration" name="migration">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Switch /></el-icon>
                <span>Load Migration Suggestions</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="migrationSuggestions" border style="width: 100%">
                    <el-table-column prop="from" label="From" width="120" />
                    <el-table-column prop="to" label="To" width="120" />
                    <el-table-column prop="load" label="Load to Move" width="100" />
                    <el-table-column prop="impact" label="Expected Impact" />
                    <el-table-column prop="priority" label="Priority" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.priority === 'High' ? 'danger' : 'warning'" size="small">
                          {{ row.priority }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="Action" width="100">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="applyMigration(row)">Apply</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="migration-summary">
                    <h4>Potential Benefits</h4>
                    <div class="benefit-item">
                      <span>Balance Improvement</span>
                      <strong>+{{ balanceImprovementPotential }}%</strong>
                    </div>
                    <div class="benefit-item">
                      <span>Peak Reduction</span>
                      <strong>{{ peakReductionPotential }} kW</strong>
                    </div>
                    <div class="benefit-item">
                      <span>Cost Savings</span>
                      <strong>${{ costSavingsPotential }}K/year</strong>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="applyAllMigrations">
                      Apply All Recommended
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Capacity Planning Tab -->
          <el-tab-pane label="Capacity Planning" name="capacity">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Capacity Planning & Forecasting</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="capacityForecastChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="capacity-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ usedCapacity }} kW</div>
                      <div class="stat-label">Current Used Capacity</div>
                      <el-progress :percentage="capacityUtilization" :stroke-width="10" :color="utilizationColor" />
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ availableCapacity }} kW</div>
                      <div class="stat-label">Available Capacity</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ monthsUntilFull }} months</div>
                      <div class="stat-label">Until Full Capacity</div>
                    </div>
                    <el-button type="primary" size="small" @click="viewCapacityReport">View Capacity Report</el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Peak Load Management Tab -->
          <el-tab-pane label="Peak Management" name="peak">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Peak Load Management</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="peakLoadChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="peak-strategies">
                    <h4>Peak Shaving Strategies</h4>
                    <div class="strategy-item">
                      <el-switch v-model="peakShavingEnabled" />
                      <span>Enable Peak Shaving</span>
                    </div>
                    <div class="strategy-item">
                      <span>Threshold</span>
                      <el-slider v-model="peakThreshold" :min="80" :max="100" :step="1" show-input style="width: 150px" />
                    </div>
                    <div class="strategy-item">
                      <span>Action</span>
                      <el-select v-model="peakAction" size="small">
                        <el-option label="Load Shedding" value="shedding" />
                        <el-option label="Battery Support" value="battery" />
                        <el-option label="Generator Support" value="generator" />
                      </el-select>
                    </div>
                    <div class="peak-savings">
                      <span>Estimated Savings:</span>
                      <strong>${{ peakSavings }}/month</strong>
                    </div>
                    <el-button type="primary" size="small" style="margin-top: 16px" @click="applyPeakStrategy">
                      Apply Strategy
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
                    <h4>Total Optimization Potential</h4>
                    <div class="potential-value">{{ totalPotential }}%</div>
                    <div class="potential-label">Load Balance Improvement</div>
                    <el-progress :percentage="totalPotential" :stroke-width="12" status="success" />
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
                <span>Load Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="loadAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
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
                    <h4>System Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Load Balance</span>
                        <el-progress :percentage="balanceIndex" :stroke-width="6" :color="balanceColor" />
                      </div>
                      <div class="health-item">
                        <span>Capacity Utilization</span>
                        <el-progress :percentage="capacityUtilization" :stroke-width="6" status="warning" />
                      </div>
                      <div class="health-item">
                        <span>Peak Management</span>
                        <el-progress :percentage="75" :stroke-width="6" status="success" />
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
        <el-button type="primary" size="large" @click="runAutoBalance">
          <el-icon><Cpu /></el-icon>
          Run Auto-Balance
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Load Report
        </el-button>
        <el-button size="large" @click="scheduleBalancing">
          <el-icon><Calendar /></el-icon>
          Schedule Balancing
        </el-button>
      </div>
    </template>

    <!-- Rack Details Dialog -->
    <el-dialog v-model="rackDialogVisible" :title="`Rack ${selectedRack?.id} Details`" width="500px">
      <el-descriptions :column="2" border v-if="selectedRack">
        <el-descriptions-item label="Location">Row {{ selectedRack.row }}</el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedRack.load }} kW</el-descriptions-item>
        <el-descriptions-item label="Load %">{{ selectedRack.loadPercentage }}%</el-descriptions-item>
        <el-descriptions-item label="Connected PDU">PDU-{{ selectedRack.row }}01</el-descriptions-item>
        <el-descriptions-item label="Phase">L{{ ((selectedRack.id.charCodeAt(2) % 3) + 1) }}</el-descriptions-item>
        <el-descriptions-item label="Devices">{{ selectedRack.deviceCount || 12 }}</el-descriptions-item>
        <el-descriptions-item label="Temperature">{{ selectedRack.temp || 24 }}°C</el-descriptions-item>
        <el-descriptions-item label="Recommended Action" :span="2">{{ selectedRack.recommendation || 'Monitor' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="rackDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="rebalanceRack">Rebalance</el-button>
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
const loadingMessage = ref('Initializing load balancing system...')

const loadingMessages = [
  'Initializing load balancing system...',
  'Analyzing phase distribution...',
  'Calculating balance metrics...',
  'Identifying migration opportunities...',
  'Forecasting capacity needs...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('trends')
const pduView = ref('grid')
const rackDialogVisible = ref(false)
const selectedRack = ref<any>(null)

// Peak management settings
const peakShavingEnabled = ref(true)
const peakThreshold = ref(85)
const peakAction = ref('battery')
const peakSavings = ref(1250)

// Alert state
const unbalanceAlert = ref(true)
const unbalanceLevel = ref(18)

// Load metrics
const totalLoad = ref(425)
const totalCapacity = ref(625)
const balanceIndex = ref(82)
const peakLoad = ref(485)
const peakTime = ref('14:30')
const demandSavings = ref(28.5)
const usedCapacity = ref(425)
const availableCapacity = ref(200)
const monthsUntilFull = ref(8)
const capacityUtilization = computed(() => (totalLoad.value / totalCapacity.value) * 100)
const balanceImprovement = ref(12)
const balanceImprovementPotential = ref(8)
const peakReductionPotential = ref(35)
const costSavingsPotential = ref(15.2)
const totalPotential = ref(12.5)
const healthScore = ref(86)

// Phase data
const phaseL1 = ref({ load: 138, percentage: 65, current: 185, deviation: -8 })
const phaseL2 = ref({ load: 158, percentage: 75, current: 212, deviation: +5 })
const phaseL3 = ref({ load: 129, percentage: 61, current: 172, deviation: -12 })

const maxPhaseLoad = computed(() => Math.max(phaseL1.value.load, phaseL2.value.load, phaseL3.value.load))
const minPhaseLoad = computed(() => Math.min(phaseL1.value.load, phaseL2.value.load, phaseL3.value.load))
const unbalanceRate = computed(() => ((maxPhaseLoad.value - minPhaseLoad.value) / (totalLoad.value / 3)) * 100)

// Colors
const balanceColor = computed(() => {
  if (balanceIndex.value > 90) return '#67c23a'
  if (balanceIndex.value > 75) return '#e6a23c'
  return '#f56c6c'
})

const utilizationColor = computed(() => {
  if (capacityUtilization.value < 70) return '#67c23a'
  if (capacityUtilization.value < 85) return '#e6a23c'
  return '#f56c6c'
})

const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

const getPhaseColor = (percentage: number) => {
  if (percentage < 70) return '#67c23a'
  if (percentage < 85) return '#e6a23c'
  return '#f56c6c'
}

const getLoadColor = (percentage: number) => {
  if (percentage < 60) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getLoadTagType = (percentage: number) => {
  if (percentage < 60) return 'success'
  if (percentage < 80) return 'warning'
  return 'danger'
}

const getRackLoadColor = (load: number) => {
  if (load < 5) return '#10b981'
  if (load < 8) return '#84cc16'
  if (load < 11) return '#f59e0b'
  if (load < 14) return '#ef4444'
  return '#7c2d12'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

// PDU load data
const pduLoads = ref([
  { id: 1, name: 'PDU-A01', loadPercentage: 68, currentLoad: 42.5, ratedCapacity: 62.5, status: 'Normal', l1: 14.2, l2: 15.8, l3: 12.5 },
  { id: 2, name: 'PDU-A02', loadPercentage: 72, currentLoad: 45.0, ratedCapacity: 62.5, status: 'Normal', l1: 15.0, l2: 16.5, l3: 13.5 },
  { id: 3, name: 'PDU-B01', loadPercentage: 85, currentLoad: 53.1, ratedCapacity: 62.5, status: 'Warning', l1: 18.5, l2: 19.2, l3: 15.4 },
  { id: 4, name: 'PDU-B02', loadPercentage: 58, currentLoad: 36.3, ratedCapacity: 62.5, status: 'Normal', l1: 12.0, l2: 13.5, l3: 10.8 },
  { id: 5, name: 'PDU-C01', loadPercentage: 62, currentLoad: 38.8, ratedCapacity: 62.5, status: 'Normal', l1: 13.2, l2: 14.0, l3: 11.6 },
  { id: 6, name: 'PDU-C02', loadPercentage: 55, currentLoad: 34.4, ratedCapacity: 62.5, status: 'Normal', l1: 11.5, l2: 12.8, l3: 10.1 }
])

// Rack load data
const rackRows = ref([
  { name: 'Row A', racks: [
      { id: 'A01', load: 4.2, loadPercentage: 35, temp: 22.5 },
      { id: 'A02', load: 5.8, loadPercentage: 48, temp: 23.1 },
      { id: 'A03', load: 8.5, loadPercentage: 71, temp: 24.5 },
      { id: 'A04', load: 10.2, loadPercentage: 85, temp: 25.2 },
      { id: 'A05', load: 6.5, loadPercentage: 54, temp: 23.8 }
    ]},
  { name: 'Row B', racks: [
      { id: 'B01', load: 3.8, loadPercentage: 32, temp: 21.8 },
      { id: 'B02', load: 5.2, loadPercentage: 43, temp: 22.2 },
      { id: 'B03', load: 12.5, loadPercentage: 104, temp: 27.5, overload: true },
      { id: 'B04', load: 7.8, loadPercentage: 65, temp: 24.8 },
      { id: 'B05', load: 6.2, loadPercentage: 52, temp: 23.2 }
    ]},
  { name: 'Row C', racks: [
      { id: 'C01', load: 3.5, loadPercentage: 29, temp: 20.5 },
      { id: 'C02', load: 4.8, loadPercentage: 40, temp: 21.2 },
      { id: 'C03', load: 6.5, loadPercentage: 54, temp: 22.5 },
      { id: 'C04', load: 7.2, loadPercentage: 60, temp: 23.1 },
      { id: 'C05', load: 5.5, loadPercentage: 46, temp: 22.8 }
    ]}
])

// Migration suggestions
const migrationSuggestions = ref([
  { from: 'PDU-B01 (L2)', to: 'PDU-C02 (L1)', load: '8.5 kW', impact: 'Reduce L2 load by 12%', priority: 'High' },
  { from: 'Rack B03', to: 'Rack C03', load: '4.2 kW', impact: 'Eliminate overload', priority: 'High' },
  { from: 'PDU-A02 (L2)', to: 'PDU-B02 (L3)', load: '5.0 kW', impact: 'Improve balance by 8%', priority: 'Medium' },
  { from: 'Rack A04', to: 'Rack A05', load: '2.5 kW', impact: 'Reduce peak load', priority: 'Medium' }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Migrate 8.5kW from PDU-B01 L2 to PDU-C02 L1', impact: '+12% balance improvement', priority: 'High' },
  { recommendation: 'Add capacity to Row B (currently at 85% utilization)', impact: 'Prevent future overload', priority: 'High' },
  { recommendation: 'Enable peak shaving at 85% threshold', impact: 'Reduce demand charges by $1.2K/month', priority: 'Medium' },
  { recommendation: 'Re-balance single-phase loads across phases', impact: '+8% balance index', priority: 'Medium' }
])

// Alerts
const loadAlerts = ref([
  { severity: 'Warning', message: 'Rack B03 load exceeds 100% capacity', location: 'Row B, Rack 03', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'Phase L3 deviation exceeds 10%', location: 'Main PDU', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'PDU-B01 load approaching 85%', location: 'Row B PDU', timestamp: '2024-12-18 08:30' }
])

// Chart refs
const loadTrendChartRef = ref<HTMLElement | null>(null)
const phaseComparisonChartRef = ref<HTMLElement | null>(null)
const capacityForecastChartRef = ref<HTMLElement | null>(null)
const peakLoadChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const optimizeNow = () => {
  ElMessage.success('Load balancing optimization started')
}

const viewHeatmap = () => {
  ElMessage.info('Load heatmap view will open')
}

const showRackDetails = (rack: any) => {
  selectedRack.value = rack
  rackDialogVisible.value = true
}

const rebalanceRack = () => {
  ElMessage.success(`Rebalancing ${selectedRack.value.id}...`)
  rackDialogVisible.value = false
}

const applyMigration = (migration: any) => {
  ElMessage.success(`Applied migration: ${migration.from} → ${migration.to}`)
}

const applyAllMigrations = () => {
  ElMessage.success('All recommended migrations applied')
}

const viewCapacityReport = () => {
  ElMessage.info('Capacity report will be generated')
}

const applyPeakStrategy = () => {
  ElMessage.success(`Peak shaving strategy applied (threshold: ${peakThreshold.value}%)`)
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const runAutoBalance = () => {
  ElMessage.success('Auto-balance sequence initiated. Estimated completion: 2 minutes.')
}

const exportReport = () => {
  ElMessage.success('Load report export started')
}

const scheduleBalancing = () => {
  ElMessage.info('Balancing scheduling interface will open')
}

// Chart initialization
const initLoadTrendChart = () => {
  if (loadTrendChartRef.value) {
    const chart = echarts.init(loadTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['L1', 'L2', 'L3', 'Total'] },
      xAxis: { type: 'category', data: ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'L1', type: 'line', data: [120, 115, 110, 118, 135, 142, 138, 145, 140, 132, 125, 122], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'L2', type: 'line', data: [135, 128, 122, 130, 148, 155, 152, 158, 150, 142, 138, 132], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'L3', type: 'line', data: [115, 108, 105, 112, 128, 135, 132, 138, 130, 125, 118, 115], smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
        { name: 'Total', type: 'line', data: [370, 351, 337, 360, 411, 432, 422, 441, 420, 399, 381, 369], smooth: true, lineStyle: { color: '#f56c6c', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPhaseComparisonChart = () => {
  if (phaseComparisonChartRef.value) {
    const chart = echarts.init(phaseComparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['PDU-A01', 'PDU-A02', 'PDU-B01', 'PDU-B02', 'PDU-C01', 'PDU-C02'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'L1', type: 'bar', data: [14.2, 15.0, 18.5, 12.0, 13.2, 11.5], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'L2', type: 'bar', data: [15.8, 16.5, 19.2, 13.5, 14.0, 12.8], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'L3', type: 'bar', data: [12.5, 13.5, 15.4, 10.8, 11.6, 10.1], itemStyle: { color: '#e6a23c', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initCapacityForecastChart = () => {
  if (capacityForecastChartRef.value) {
    const chart = echarts.init(capacityForecastChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Actual Load', 'Forecast Load', 'Capacity Limit'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan 2025'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'Actual Load', type: 'line', data: [385, 392, 398, 405, 412, 418, 425, 430, 435, 440, 445, 450, null], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Forecast Load', type: 'line', data: [null, null, null, null, null, null, null, null, null, null, 448, 455, 462], smooth: true, lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Capacity Limit', type: 'line', data: [625, 625, 625, 625, 625, 625, 625, 625, 625, 625, 625, 625, 625], lineStyle: { color: '#f56c6c', width: 2, type: 'dotted' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPeakLoadChart = () => {
  if (peakLoadChartRef.value) {
    const chart = echarts.init(peakLoadChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['With Shaving', 'Without Shaving', 'Threshold'] },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'With Shaving', type: 'line', data: [445, 452, 448, 455, 458, 425, 418], smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Without Shaving', type: 'line', data: [465, 478, 472, 485, 492, 438, 425], smooth: true, lineStyle: { color: '#f56c6c', width: 2, type: 'dashed' } },
        { name: 'Threshold', type: 'line', data: [450, 450, 450, 450, 450, 450, 450], lineStyle: { color: '#f59e0b', width: 2, type: 'dotted' } }
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
    phaseL1.value.load = 135 + Math.random() * 6
    phaseL2.value.load = 155 + Math.random() * 8
    phaseL3.value.load = 125 + Math.random() * 5
    totalLoad.value = phaseL1.value.load + phaseL2.value.load + phaseL3.value.load
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
        initLoadTrendChart()
        initPhaseComparisonChart()
        initCapacityForecastChart()
        initPeakLoadChart()
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
.load-balancing-container {
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
.load-balancing-container {
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

.phase-bar {
  padding: 16px;
  border-radius: 12px;
  background: #f5f7fa;
}

.phase-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.phase-name {
  font-size: 18px;
  font-weight: 600;
}

.phase-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.phase-details {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
}

.balance-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.balance-stats .stat {
  text-align: center;
}

.balance-stats .stat span {
  display: block;
  font-size: 12px;
  color: #909399;
}

.balance-stats .stat strong {
  font-size: 20px;
  color: #303133;
}

.balance-stats .stat strong.warning {
  color: #f56c6c;
}

.balance-stats .stat strong.success {
  color: #67c23a;
}

/* PDU Section */
.pdu-section,
.rack-section {
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

.pdu-load-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.pdu-load-card:hover {
  transform: translateY(-2px);
}

.pdu-load-card.load-Warning {
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

.pdu-load {
  margin-bottom: 16px;
}

.pdu-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.pdu-metrics .metric {
  text-align: center;
}

.pdu-metrics .metric span {
  display: block;
  font-size: 11px;
  color: #909399;
}

.pdu-metrics .metric strong {
  font-size: 14px;
  color: #303133;
}

.pdu-phases {
  text-align: center;
  font-size: 11px;
}

.phase-mini span {
  margin: 0 4px;
}

.phase-l1-mini { color: #409eff; }
.phase-l2-mini { color: #67c23a; }
.phase-l3-mini { color: #e6a23c; }

/* Rack Grid */
.rack-grid {
  background: white;
  border-radius: 12px;
  padding: 20px;
  overflow-x: auto;
}

.rack-row {
  display: flex;
  margin-bottom: 8px;
}

.row-label {
  width: 50px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 8px;
  margin-right: 8px;
}

.row-racks {
  display: flex;
  flex: 1;
  gap: 8px;
}

.rack-load-cell {
  flex: 1;
  min-width: 80px;
  padding: 12px;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
  color: white;
}

.rack-load-cell:hover {
  transform: scale(1.05);
}

.rack-id {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 4px;
}

.rack-load {
  font-size: 14px;
  font-weight: 700;
}

.rack-percent {
  font-size: 10px;
  opacity: 0.8;
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

/* Migration Summary */
.migration-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.migration-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.benefit-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.benefit-item strong {
  color: #409eff;
}

/* Capacity Stats */
.capacity-stats {
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

/* Peak Strategies */
.peak-strategies {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.peak-strategies h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.strategy-item {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.peak-savings {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
}

.peak-savings strong {
  color: #67c23a;
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