<template>
  <div class="generator-strategy-container">
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
            <span class="loading-title">Loading Generator Strategy</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Backup Power Strategy Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Generator Strategy</span>
          <el-tag type="danger" effect="dark" size="large">Backup Power Optimization</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="upcomingMaintenance" class="alert-banner warning">
        <el-icon><Warning /></el-icon>
        <span>Generator G002 scheduled maintenance in {{ daysUntilMaintenance }} days. Please schedule service.</span>
        <el-button size="small" type="warning" @click="scheduleMaintenance">Schedule Now</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Generator Status</span>
              </div>
              <div class="card-value">{{ onlineGenerators }}/{{ totalGenerators }}</div>
              <div class="card-footer">
                <el-progress :percentage="(onlineGenerators / totalGenerators) * 100" :stroke-width="8" status="success" />
                <span class="status-text">{{ standbyGenerators }} Standby</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Fuel Remaining</span>
              </div>
              <div class="card-value">{{ fuelRemaining }}%</div>
              <div class="card-footer">
                <el-progress :percentage="fuelRemaining" :stroke-width="8" :color="fuelColor" />
                <span class="status-text">{{ fuelDays }} days runtime</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Load Level</span>
              </div>
              <div class="card-value">{{ avgLoad }}%</div>
              <div class="card-footer">
                <el-progress :percentage="avgLoad" :stroke-width="8" :color="loadColor" />
                <span class="status-text">Optimal: 40-80%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Calendar /></el-icon>
                <span>Test Frequency</span>
              </div>
              <div class="card-value">{{ testFrequency }}</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" status="success" :format="() => 'Compliance: 95%'" />
                <span class="status-text">Last test: {{ lastTestDate }}</span>
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
                <span>Generator Real-Time Status</span>
                <el-tag type="success" size="small">Live Data</el-tag>
              </div>
              <div class="generator-stats">
                <div class="stat-big">
                  <span class="stat-label">Total Output Power</span>
                  <span class="stat-value">{{ totalOutputPower }} kW</span>
                  <el-progress :percentage="(totalOutputPower / totalCapacity) * 100" :stroke-width="10" :color="loadColor" />
                </div>
                <div class="stat-grid">
                  <div class="stat-item">
                    <span>Frequency</span>
                    <strong>{{ frequency }} Hz</strong>
                    <el-progress :percentage="((frequency - 49) / 2) * 100" :stroke-width="4" :show-text="false" />
                  </div>
                  <div class="stat-item">
                    <span>Voltage</span>
                    <strong>{{ voltage }} V</strong>
                    <el-progress :percentage="(voltage / 480) * 100" :stroke-width="4" :show-text="false" />
                  </div>
                  <div class="stat-item">
                    <span>Fuel Consumption</span>
                    <strong>{{ fuelConsumption }} L/h</strong>
                  </div>
                  <div class="stat-item">
                    <span>Engine Temp</span>
                    <strong :class="{ warning: engineTemp > 95 }">{{ engineTemp }}°C</strong>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="fuel-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Drop /></el-icon>
                <span>Fuel Level</span>
              </div>
              <div class="fuel-gauge">
                <div ref="fuelGaugeRef" style="height: 180px"></div>
              </div>
              <div class="fuel-details">
                <div class="fuel-item">
                  <span>Main Tank</span>
                  <el-progress :percentage="82" :stroke-width="6" status="success" :format="() => '8,200 L'" />
                </div>
                <div class="fuel-item">
                  <span>Day Tank</span>
                  <el-progress :percentage="65" :stroke-width="6" status="warning" :format="() => '650 L'" />
                </div>
                <div class="fuel-item">
                  <span>Consumption Rate</span>
                  <span class="value">{{ fuelConsumption }} L/h</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Generator Units Status -->
      <div class="generator-units-section">
        <div class="section-header">
          <h3>Generator Units Status</h3>
          <div class="header-controls">
            <el-radio-group v-model="unitView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="6" v-for="gen in generators" :key="gen.id">
            <el-card class="generator-unit-card" :class="`status-${gen.status}`" shadow="hover">
              <div class="gen-header">
                <span class="gen-name">{{ gen.name }}</span>
                <el-tag :type="getGenTagType(gen.status)" size="small">{{ gen.status }}</el-tag>
              </div>
              <div class="gen-metrics">
                <div class="metric-row">
                  <div class="metric">
                    <span>Load</span>
                    <strong>{{ gen.load }}%</strong>
                    <el-progress :percentage="gen.load" :stroke-width="4" :color="getLoadColor(gen.load)" :show-text="false" />
                  </div>
                  <div class="metric">
                    <span>Output</span>
                    <strong>{{ gen.power }} kW</strong>
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Fuel Level</span>
                    <strong>{{ gen.fuelLevel }}%</strong>
                  </div>
                  <div class="metric">
                    <span>Runtime</span>
                    <strong>{{ gen.runtime }} h</strong>
                  </div>
                </div>
              </div>
              <div class="gen-footer">
                <el-button type="primary" size="small" @click="viewGenDetails(gen)">Details</el-button>
                <el-button size="small" @click="manualTest(gen)">Test</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="generators" border v-else style="width: 100%">
          <el-table-column prop="name" label="Unit" width="100" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getGenTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="load" label="Load %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.load" :stroke-width="8" :color="getLoadColor(row.load)" />
            </template>
          </el-table-column>
          <el-table-column prop="power" label="Power (kW)" width="100" />
          <el-table-column prop="fuelLevel" label="Fuel %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.fuelLevel" :stroke-width="8" :color="getFuelColor(row.fuelLevel)" />
            </template>
          </el-table-column>
          <el-table-column prop="runtime" label="Runtime (h)" width="100" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewGenDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="manualTest(row)">Test</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Load Strategy Tab -->
          <el-tab-pane label="Load Strategy" name="loadStrategy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Generator Load Strategy</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="loadStrategyChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="strategy-config">
                    <h4>Staged Load Shedding</h4>
                    <el-table :data="loadSheddingStages" border size="small">
                      <el-table-column prop="stage" label="Stage" width="80" />
                      <el-table-column prop="threshold" label="Load Threshold" />
                      <el-table-column prop="action" label="Action" />
                      <el-table-column prop="priority" label="Priority" width="100" />
                    </el-table>
                    <el-button type="primary" size="small" style="margin-top: 16px" @click="configureLoadShedding">
                      Configure Strategy
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Fuel Management Tab -->
          <el-tab-pane label="Fuel Management" name="fuel">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Drop /></el-icon>
                <span>Fuel Management & Analytics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="fuelTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="fuel-management">
                    <div class="fuel-order">
                      <h4>Fuel Order Recommendation</h4>
                      <div class="order-info">
                        <span>Current Level: <strong>{{ fuelRemaining }}%</strong></span>
                        <span>Reorder Point: <strong>30%</strong></span>
                        <span>Estimated Order Date: <strong>{{ orderDate }}</strong></span>
                      </div>
                      <el-button type="primary" size="small" @click="placeFuelOrder">Place Order</el-button>
                    </div>
                    <div class="fuel-quality">
                      <h4>Fuel Quality Test</h4>
                      <el-table :data="fuelQualityTests" border size="small">
                        <el-table-column prop="date" label="Date" width="100" />
                        <el-table-column prop="result" label="Result" />
                        <el-table-column prop="status" label="Status" width="80">
                          <template #default="{ row }">
                            <el-tag :type="row.status === 'Pass' ? 'success' : 'danger'" size="small">
                              {{ row.status }}
                            </el-tag>
                          </template>
                        </el-table-column>
                      </el-table>
                      <el-button size="small" style="margin-top: 8px" @click="scheduleFuelTest">Schedule Test</el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Test Strategy Tab -->
          <el-tab-pane label="Test Strategy" name="testStrategy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>Generator Test Schedule</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="testHistory" border style="width: 100%">
                    <el-table-column prop="date" label="Date" width="120" />
                    <el-table-column prop="generator" label="Generator" width="100" />
                    <el-table-column prop="type" label="Test Type" width="120" />
                    <el-table-column prop="duration" label="Duration" width="100" />
                    <el-table-column prop="result" label="Result" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.result === 'Pass' ? 'success' : 'danger'" size="small">
                          {{ row.result }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="notes" label="Notes" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="test-config">
                    <h4>Test Schedule Configuration</h4>
                    <div class="config-item">
                      <span>Weekly No-Load Test</span>
                      <el-switch v-model="weeklyTest" />
                    </div>
                    <div class="config-item">
                      <span>Monthly Load Bank Test</span>
                      <el-switch v-model="monthlyTest" />
                    </div>
                    <div class="config-item">
                      <span>Quarterly Full Load Test</span>
                      <el-switch v-model="quarterlyTest" />
                    </div>
                    <div class="config-item">
                      <span>Next Scheduled Test</span>
                      <strong>{{ nextTestDate }}</strong>
                    </div>
                    <el-button type="primary" size="small" style="margin-top: 16px" @click="runManualTest">
                      Run Manual Test
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Maintenance Strategy Tab -->
          <el-tab-pane label="Maintenance" name="maintenance">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Tools /></el-icon>
                <span>Maintenance Schedule</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="maintenanceSchedule" border style="width: 100%">
                    <el-table-column prop="date" label="Date" width="120" />
                    <el-table-column prop="generator" label="Generator" width="100" />
                    <el-table-column prop="type" label="Maintenance Type" />
                    <el-table-column prop="status" label="Status" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getMaintenanceStatusType(row.status)" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="Actions" width="100">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="viewMaintenanceDetails(row)">Details</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="maintenance-stats">
                    <h4>Maintenance Metrics</h4>
                    <div class="metric-item">
                      <span>Oil Change Due</span>
                      <el-progress :percentage="85" :stroke-width="8" :format="() => 'G002 (85%)'" />
                    </div>
                    <div class="metric-item">
                      <span>Filter Replacement</span>
                      <el-progress :percentage="72" :stroke-width="8" :format="() => 'G001, G003'" />
                    </div>
                    <div class="metric-item">
                      <span>Battery Health</span>
                      <el-progress :percentage="78" :stroke-width="8" status="warning" />
                    </div>
                    <div class="metric-item">
                      <span>Coolant Condition</span>
                      <el-progress :percentage="88" :stroke-width="8" status="success" />
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
                    <div class="potential-value">15.5%</div>
                    <div class="potential-label">Fuel Efficiency Gain</div>
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
                <span>Generator Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="generatorAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="generator" label="Generator" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>Fleet Health Score</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Engine Health</span>
                        <el-progress :percentage="88" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Alternator Health</span>
                        <el-progress :percentage="92" :stroke-width="6" status="success" />
                      </div>
                      <div class="health-item">
                        <span>Fuel System</span>
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
        <el-button type="primary" size="large" @click="runStrategyOptimization">
          <el-icon><Cpu /></el-icon>
          Optimize Strategy
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button size="large" @click="emergencyStart">
          <el-icon><WarningFilled /></el-icon>
          Emergency Start
        </el-button>
      </div>
    </template>

    <!-- Generator Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Generator ${selectedGen?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedGen">
        <el-descriptions-item label="Status">
          <el-tag :type="getGenTagType(selectedGen.status)">{{ selectedGen.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Model">Caterpillar 3516C</el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedGen.load }}%</el-descriptions-item>
        <el-descriptions-item label="Output Power">{{ selectedGen.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Voltage">480 V</el-descriptions-item>
        <el-descriptions-item label="Frequency">50 Hz</el-descriptions-item>
        <el-descriptions-item label="Fuel Level">{{ selectedGen.fuelLevel }}%</el-descriptions-item>
        <el-descriptions-item label="Runtime">{{ selectedGen.runtime }} hours</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">2024-11-01</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">2025-02-01</el-descriptions-item>
        <el-descriptions-item label="Last Test">2024-12-15</el-descriptions-item>
        <el-descriptions-item label="Test Result">Pass</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="runDiagnosticTest">Run Diagnostic</el-button>
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
const loadingMessage = ref('Initializing generator systems...')

const loadingMessages = [
  'Initializing generator systems...',
  'Loading fuel level data...',
  'Analyzing test history...',
  'Calculating maintenance schedules...',
  'Optimizing load strategies...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('loadStrategy')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const selectedGen = ref<any>(null)
const upcomingMaintenance = ref(true)
const daysUntilMaintenance = ref(12)

// Generator metrics
const onlineGenerators = ref(3)
const totalGenerators = ref(4)
const standbyGenerators = ref(1)
const fuelRemaining = ref(68)
const fuelDays = ref(72)
const avgLoad = ref(58)
const testFrequency = ref('Weekly')
const lastTestDate = ref('2024-12-15')
const totalOutputPower = ref(1250)
const totalCapacity = ref(2000)
const frequency = ref(50.02)
const voltage = ref(478)
const fuelConsumption = ref(185)
const engineTemp = ref(88)
const healthScore = ref(84)

// Order date
const orderDate = ref('2024-01-15')

// Test switches
const weeklyTest = ref(true)
const monthlyTest = ref(true)
const quarterlyTest = ref(false)
const nextTestDate = ref('2024-12-22')

// Colors
const fuelColor = computed(() => {
  if (fuelRemaining.value > 60) return '#67c23a'
  if (fuelRemaining.value > 30) return '#e6a23c'
  return '#f56c6c'
})

const loadColor = computed(() => {
  if (avgLoad.value < 40) return '#909399'
  if (avgLoad.value < 80) return '#67c23a'
  return '#f56c6c'
})

const healthColor = computed(() => {
  if (healthScore.value > 80) return '#67c23a'
  if (healthScore.value > 60) return '#e6a23c'
  return '#f56c6c'
})

// Generator units
const generators = ref([
  { id: 1, name: 'G001', status: 'Online', load: 62, power: 620, fuelLevel: 75, runtime: 1250 },
  { id: 2, name: 'G002', status: 'Online', load: 58, power: 580, fuelLevel: 68, runtime: 980 },
  { id: 3, name: 'G003', status: 'Online', load: 55, power: 550, fuelLevel: 82, runtime: 2100 },
  { id: 4, name: 'G004', status: 'Standby', load: 0, power: 0, fuelLevel: 95, runtime: 350 }
])

// Load shedding stages
const loadSheddingStages = ref([
  { stage: 'Stage 1', threshold: '>80% load', action: 'Non-critical lighting', priority: 'Low' },
  { stage: 'Stage 2', threshold: '>85% load', action: 'HVAC non-essential', priority: 'Medium' },
  { stage: 'Stage 3', threshold: '>90% load', action: 'Office equipment', priority: 'High' },
  { stage: 'Stage 4', threshold: '>95% load', action: 'Non-essential servers', priority: 'Critical' }
])

// Fuel quality tests
const fuelQualityTests = ref([
  { date: '2024-12-01', result: 'Pass', status: 'Pass' },
  { date: '2024-11-01', result: 'Pass', status: 'Pass' },
  { date: '2024-10-01', result: 'Warning - Water detected', status: 'Warning' }
])

// Test history
const testHistory = ref([
  { date: '2024-12-15', generator: 'G001', type: 'Weekly No-Load', duration: '30 min', result: 'Pass', notes: 'Normal' },
  { date: '2024-12-15', generator: 'G002', type: 'Weekly No-Load', duration: '30 min', result: 'Pass', notes: 'Normal' },
  { date: '2024-12-08', generator: 'G003', type: 'Monthly Load Bank', duration: '60 min', result: 'Pass', notes: 'Load at 75%' },
  { date: '2024-12-01', generator: 'G001', type: 'Weekly No-Load', duration: '30 min', result: 'Warning', notes: 'Low coolant' }
])

// Maintenance schedule
const maintenanceSchedule = ref([
  { date: '2025-02-01', generator: 'G001', type: 'Oil Change + Filter', status: 'Scheduled' },
  { date: '2025-02-15', generator: 'G002', type: 'Full Service', status: 'Planned' },
  { date: '2025-01-20', generator: 'G003', type: 'Battery Replacement', status: 'Scheduled' },
  { date: '2025-03-01', generator: 'G004', type: 'Annual Inspection', status: 'Planned' }
])

// Recommendations
const recommendations = ref([
  { recommendation: 'Schedule fuel delivery (current level 68%)', impact: 'Ensure 72hr runtime', priority: 'High' },
  { recommendation: 'Run load bank test on G002', impact: 'Verify capacity', priority: 'Medium' },
  { recommendation: 'Optimize load sharing between units', impact: '+5% fuel efficiency', priority: 'High' },
  { recommendation: 'Replace G003 batteries (health 72%)', impact: 'Improve reliability', priority: 'Medium' }
])

// Alerts
const generatorAlerts = ref([
  { severity: 'Warning', message: 'G002 coolant level low', generator: 'G002', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'Fuel level below 70% on G002', generator: 'G002', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'G003 battery health critical', generator: 'G003', timestamp: '2024-12-17 22:30' }
])

// Chart refs
const fuelGaugeRef = ref<HTMLElement | null>(null)
const loadStrategyChartRef = ref<HTMLElement | null>(null)
const fuelTrendChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const getGenTagType = (status: string) => {
  if (status === 'Online') return 'success'
  if (status === 'Standby') return 'warning'
  return 'info'
}

const getLoadColor = (load: number) => {
  if (load < 40) return '#909399'
  if (load < 80) return '#67c23a'
  return '#f56c6c'
}

const getFuelColor = (fuel: number) => {
  if (fuel > 60) return '#67c23a'
  if (fuel > 30) return '#e6a23c'
  return '#f56c6c'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const getMaintenanceStatusType = (status: string) => {
  if (status === 'Scheduled') return 'warning'
  if (status === 'Completed') return 'success'
  return 'info'
}

const viewGenDetails = (gen: any) => {
  selectedGen.value = gen
  detailsDialogVisible.value = true
}

const manualTest = (gen: any) => {
  ElMessage.info(`Starting manual test for ${gen.name}`)
}

const runDiagnosticTest = () => {
  ElMessage.success('Diagnostic test initiated')
  detailsDialogVisible.value = false
}

const configureLoadShedding = () => {
  ElMessage.info('Load shedding configuration interface will open')
}

const placeFuelOrder = () => {
  ElMessage.success('Fuel order placed. Estimated delivery: 3 days')
}

const scheduleFuelTest = () => {
  ElMessage.info('Fuel test scheduling interface will open')
}

const runManualTest = () => {
  ElMessage.success('Manual test started. Results in 30 minutes.')
}

const viewMaintenanceDetails = (item: any) => {
  ElMessage.info(`Viewing maintenance details for ${item.generator}`)
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.recommendation}`)
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const runStrategyOptimization = () => {
  ElMessage.success('Strategy optimization started')
}

const exportReport = () => {
  ElMessage.success('Generator report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

const emergencyStart = () => {
  ElMessage.warning('Emergency start sequence initiated. All units starting...')
}

// Chart initialization
const initFuelGauge = () => {
  if (fuelGaugeRef.value) {
    const chart = echarts.init(fuelGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 0,
        max: 100,
        splitNumber: 5,
        progress: { show: true, width: 18, itemStyle: { color: '#67c23a' } },
        axisLine: { lineStyle: { width: 18, color: [[0.6, '#f56c6c'], [0.8, '#e6a23c'], [1, '#67c23a']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}%' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12 },
        data: [{ value: fuelRemaining.value, name: 'Fuel Level' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initLoadStrategyChart = () => {
  if (loadStrategyChartRef.value) {
    const chart = echarts.init(loadStrategyChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['G001', 'G002', 'G003', 'Total Load'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: { type: 'value', name: 'Load (kW)' },
      series: [
        { name: 'G001', type: 'line', data: [580, 560, 620, 650, 640, 610], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'G002', type: 'line', data: [540, 520, 580, 610, 600, 570], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'G003', type: 'line', data: [510, 490, 550, 580, 570, 540], smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
        { name: 'Total Load', type: 'line', data: [1630, 1570, 1750, 1840, 1810, 1720], smooth: true, lineStyle: { color: '#f56c6c', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initFuelTrendChart = () => {
  if (fuelTrendChartRef.value) {
    const chart = echarts.init(fuelTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Main Tank', 'Day Tank'] },
      xAxis: { type: 'category', data: ['Dec 10', 'Dec 11', 'Dec 12', 'Dec 13', 'Dec 14', 'Dec 15', 'Dec 16', 'Dec 17', 'Dec 18'] },
      yAxis: { type: 'value', name: 'Fuel Level (L)' },
      series: [
        { name: 'Main Tank', type: 'line', data: [8500, 8420, 8350, 8280, 8200, 8130, 8050, 7980, 7900], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Day Tank', type: 'line', data: [680, 670, 660, 655, 650, 645, 640, 635, 630], smooth: true, lineStyle: { color: '#67c23a', width: 2 } }
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
    totalOutputPower.value = 1200 + Math.random() * 100
    frequency.value = 49.98 + Math.random() * 0.05
    engineTemp.value = 85 + Math.random() * 8
    fuelConsumption.value = 180 + Math.random() * 10
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
        initFuelGauge()
        initLoadStrategyChart()
        initFuelTrendChart()
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
.generator-strategy-container {
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
.generator-strategy-container {
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

/* Monitoring Section */
.monitoring-section {
  margin-bottom: 24px;
}

.monitoring-card,
.fuel-card {
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

.generator-stats {
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

.fuel-details {
  margin-top: 16px;
}

.fuel-item {
  margin-bottom: 16px;
}

.fuel-item span {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.fuel-item .value {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

/* Generator Units */
.generator-units-section {
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

.generator-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.generator-unit-card:hover {
  transform: translateY(-2px);
}

.generator-unit-card.status-Online {
  border-left: 4px solid #67c23a;
}

.generator-unit-card.status-Standby {
  border-left: 4px solid #e6a23c;
}

.gen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.gen-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.gen-metrics {
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

.gen-footer {
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

/* Fuel Management */
.fuel-management {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.fuel-order,
.fuel-quality {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.fuel-order h4,
.fuel-quality h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 13px;
}

/* Test Config */
.test-config {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.test-config h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

/* Maintenance Stats */
.maintenance-stats {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.maintenance-stats h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.metric-item {
  margin-bottom: 20px;
}

.metric-item span {
  display: block;
  margin-bottom: 8px;
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