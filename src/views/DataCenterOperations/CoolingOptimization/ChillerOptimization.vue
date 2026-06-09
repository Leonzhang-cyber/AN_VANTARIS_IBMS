<template>
  <div class="chiller-optimization-container">
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
            <span class="loading-title">Loading Chiller Optimization Dashboard</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">HVAC Cooling System Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->

      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Chiller Optimization</span>
          <el-tag type="danger" effect="dark" size="large">Cooling Efficiency Management</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Current COP</span>
              </div>
              <div class="card-value">5.8</div>
              <div class="card-footer">
                <el-progress :percentage="82" :stroke-width="8" status="success" :format="() => 'Target: 7.0'" />
                <span class="status-text">Above Average</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Energy Savings</span>
              </div>
              <div class="card-value">18.5%</div>
              <div class="card-footer">
                <el-progress :percentage="18.5" :stroke-width="8" status="success" />
                <span class="status-text">Since Optimization</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Coin /></el-icon>
                <span>Cost Reduction</span>
              </div>
              <div class="card-value">$142K</div>
              <div class="card-footer">
                <el-progress :percentage="65" :stroke-width="8" status="warning" />
                <span class="status-text">Annual Savings</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Carbon Reduction</span>
              </div>
              <div class="card-value">285 tCO₂e</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" status="success" :format="() => 'Annual'" />
                <span class="status-text">Scope 2 Emissions</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Chiller Plant Overview -->
      <div class="plant-overview">
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="plant-diagram-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Connection /></el-icon>
                <span>Chiller Plant Schematic</span>
                <div class="header-actions">
                  <el-button size="small" @click="refreshData">Refresh</el-button>
                  <el-button size="small" type="primary" @click="viewDetails">View Details</el-button>
                </div>
              </div>
              <div class="plant-diagram">
                <div ref="chillerPlantChartRef" style="height: 400px"></div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="performance-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Monitor /></el-icon>
                <span>Real-Time Performance</span>
              </div>
              <div class="live-metrics">
                <div class="metric-big">
                  <span class="metric-label">Total Cooling Load</span>
                  <span class="metric-value">{{ currentLoad }} kW</span>
                  <el-progress :percentage="currentLoadPercent" :stroke-width="8" :color="loadColor" />
                </div>
                <div class="metric-grid">
                  <div class="metric-item">
                    <span class="label">Supply Temp</span>
                    <span class="value">{{ supplyTemp }}°C</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">Return Temp</span>
                    <span class="value">{{ returnTemp }}°C</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">Delta T</span>
                    <span class="value">{{ deltaT }}°C</span>
                  </div>
                  <div class="metric-item">
                    <span class="label">Flow Rate</span>
                    <span class="value">{{ flowRate }} L/s</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Chiller Units Status -->
      <div class="chiller-units-section">
        <div class="section-header">
          <h3>Chiller Units Status</h3>
          <el-radio-group v-model="unitView" size="small">
            <el-radio-button label="grid">Grid View</el-radio-button>
            <el-radio-button label="list">List View</el-radio-button>
          </el-radio-group>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="8" v-for="chiller in chillers" :key="chiller.id">
            <el-card class="chiller-unit-card" :class="getChillerStatusClass(chiller.status)" shadow="hover">
              <div class="chiller-header">
                <span class="chiller-name">{{ chiller.name }}</span>
                <el-tag :type="getChillerTagType(chiller.status)" size="small">{{ chiller.status }}</el-tag>
              </div>
              <div class="chiller-metrics">
                <div class="metric">
                  <span>Load</span>
                  <strong>{{ chiller.load }}%</strong>
                  <el-progress :percentage="chiller.load" :stroke-width="6" :color="getLoadColor(chiller.load)" />
                </div>
                <div class="metric">
                  <span>Efficiency (COP)</span>
                  <strong>{{ chiller.cop }}</strong>
                </div>
                <div class="metric-row">
                  <div class="metric-small">
                    <span>Supply</span>
                    <strong>{{ chiller.supplyTemp }}°C</strong>
                  </div>
                  <div class="metric-small">
                    <span>Return</span>
                    <strong>{{ chiller.returnTemp }}°C</strong>
                  </div>
                  <div class="metric-small">
                    <span>Power</span>
                    <strong>{{ chiller.power }} kW</strong>
                  </div>
                </div>
              </div>
              <div class="chiller-footer">
                <el-button type="primary" size="small" @click="viewChillerDetails(chiller)">Details</el-button>
                <el-button size="small" @click="adjustSetpoint(chiller)">Adjust</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="chillers" border v-else style="width: 100%">
          <el-table-column prop="name" label="Unit" width="120" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getChillerTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="load" label="Load %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.load" :stroke-width="8" :color="getLoadColor(row.load)" />
            </template>
          </el-table-column>
          <el-table-column prop="cop" label="COP" width="100" />
          <el-table-column prop="supplyTemp" label="Supply °C" width="100" />
          <el-table-column prop="returnTemp" label="Return °C" width="100" />
          <el-table-column prop="power" label="Power (kW)" width="100" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewChillerDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="adjustSetpoint(row)">Adjust</el-button>
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
                <span>Chiller Performance Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="copTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="loadDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Optimization Strategies Tab -->
          <el-tab-pane label="Optimization Strategies" name="strategies">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>AI-Powered Optimization Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="recommendations-list">
                    <div v-for="(rec, index) in recommendations" :key="index" class="recommendation-card">
                      <div class="rec-header">
                        <el-icon :color="rec.priority === 'High' ? '#f56c6c' : '#e6a23c'">
                          <Warning v-if="rec.priority === 'High'" />
                          <InfoFilled v-else />
                        </el-icon>
                        <span class="rec-title">{{ rec.title }}</span>
                        <el-tag :type="rec.priority === 'High' ? 'danger' : 'warning'" size="small">{{ rec.priority }} Priority</el-tag>
                      </div>
                      <p class="rec-description">{{ rec.description }}</p>
                      <div class="rec-impact">
                        <span>Expected Savings: <strong>{{ rec.savings }}</strong></span>
                        <span>ROI: <strong>{{ rec.roi }}</strong></span>
                      </div>
                      <el-button type="primary" size="small" @click="applyRecommendation(rec)">Apply</el-button>
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="optimizationChartRef" style="height: 350px"></div>
                  </div>
                  <div class="strategy-impact">
                    <h4>Impact Summary</h4>
                    <el-table :data="strategyImpacts" border size="small">
                      <el-table-column prop="strategy" label="Strategy" />
                      <el-table-column prop="savings" label="Annual Savings" />
                      <el-table-column prop="status" label="Status">
                        <template #default="{ row }">
                          <el-tag :type="row.status === 'Applied' ? 'success' : 'info'" size="small">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Setpoint Optimization Tab -->
          <el-tab-pane label="Setpoint Optimization" name="setpoints">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Control /></el-icon>
                <span>Dynamic Setpoint Control</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="setpoint-card">
                    <h4>Supply Temperature Setpoint</h4>
                    <div class="setpoint-control">
                      <span class="current-value">{{ supplySetpoint }}°C</span>
                      <el-slider v-model="supplySetpoint" :min="6" :max="12" :step="0.5" show-input />
                    </div>
                    <div class="setpoint-impact">
                      <span>Impact on COP: <strong>{{ calculateCOPImpact(supplySetpoint) }}</strong></span>
                      <span>Energy Impact: <strong>{{ calculateEnergyImpact(supplySetpoint) }}</strong></span>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="setpoint-card">
                    <h4>Condenser Water Setpoint</h4>
                    <div class="setpoint-control">
                      <span class="current-value">{{ condenserSetpoint }}°C</span>
                      <el-slider v-model="condenserSetpoint" :min="20" :max="32" :step="0.5" show-input />
                    </div>
                    <div class="setpoint-impact">
                      <span>Impact on COP: <strong>{{ calculateCondenserImpact(condenserSetpoint) }}</strong></span>
                      <span>Energy Impact: <strong>{{ calculateCondenserEnergyImpact(condenserSetpoint) }}</strong></span>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="setpoint-card">
                    <h4>Chiller Sequencing</h4>
                    <div class="sequencing-control">
                      <div class="sequence-item">
                        <span>Primary Chillers</span>
                        <el-switch v-model="primaryChillers" active-text="2" inactive-text="1" />
                      </div>
                      <div class="sequence-item">
                        <span>Standby Chillers</span>
                        <el-switch v-model="standbyChillers" active-text="1" inactive-text="0" />
                      </div>
                      <div class="sequence-item">
                        <span>Load Balancing</span>
                        <el-select v-model="loadBalanceMode" size="small" style="width: 120px">
                          <el-option label="Equal" value="equal" />
                          <el-option label="Priority" value="priority" />
                          <el-option label="Efficiency" value="efficiency" />
                        </el-select>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
              <div class="action-buttons-inline">
                <el-button type="primary" @click="applySetpoints">Apply Setpoints</el-button>
                <el-button @click="resetSetpoints">Reset to Optimal</el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- Energy Savings Tab -->
          <el-tab-pane label="Energy Savings" name="savings">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>Energy Savings Tracking</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="savingsChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="carbonChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
              <div class="savings-summary">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="savings-stat">
                      <span class="stat-label">Total Energy Saved</span>
                      <span class="stat-value">1,245,000 kWh</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="savings-stat">
                      <span class="stat-label">Cost Savings</span>
                      <span class="stat-value">$142,000</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="savings-stat">
                      <span class="stat-label">Carbon Reduction</span>
                      <span class="stat-value">285 tCO₂e</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="savings-stat">
                      <span class="stat-label">PUE Improvement</span>
                      <span class="stat-value">-0.08</span>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </div>
          </el-tab-pane>

          <!-- Alerts & Diagnostics Tab -->
          <el-tab-pane label="Alerts & Diagnostics" name="alerts">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Bell /></el-icon>
                <span>Active Alerts & Diagnostics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="alerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                    <el-table-column prop="status" label="Status" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'Active' ? 'danger' : 'success'" size="small">
                          {{ row.status }}
                        </el-tag>
                      </template>
                    </el-table-column>
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
                        <span>COP Efficiency</span>
                        <el-progress :percentage="82" :stroke-width="6" />
                      </div>
                      <div class="health-item">
                        <span>Setpoint Optimization</span>
                        <el-progress :percentage="75" :stroke-width="6" />
                      </div>
                      <div class="health-item">
                        <span>Maintenance Status</span>
                        <el-progress :percentage="90" :stroke-width="6" status="success" />
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
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </template>

    <!-- Chiller Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Chiller ${selectedChiller?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedChiller">
        <el-descriptions-item label="Status">
          <el-tag :type="getChillerTagType(selectedChiller.status)">{{ selectedChiller.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Load">{{ selectedChiller.load }}%</el-descriptions-item>
        <el-descriptions-item label="COP">{{ selectedChiller.cop }}</el-descriptions-item>
        <el-descriptions-item label="Power Consumption">{{ selectedChiller.power }} kW</el-descriptions-item>
        <el-descriptions-item label="Supply Temp">{{ selectedChiller.supplyTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Return Temp">{{ selectedChiller.returnTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Flow Rate">{{ selectedChiller.flowRate || 45 }} L/s</el-descriptions-item>
        <el-descriptions-item label="Refrigerant">R-134a</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">2024-11-15</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">2025-02-15</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Adjust Setpoint Dialog -->
    <el-dialog v-model="adjustDialogVisible" title="Adjust Chiller Setpoint" width="450px">
      <el-form>
        <el-form-item label="Supply Temperature Setpoint">
          <el-slider v-model="adjustSetpointTemp" :min="5" :max="15" :step="0.5" show-input />
        </el-form-item>
        <el-form-item label="Chilled Water Flow">
          <el-slider v-model="adjustFlowRate" :min="30" :max="80" :step="1" show-input />
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
const loadingMessage = ref('Initializing chiller systems...')

const loadingMessages = [
  'Initializing chiller systems...',
  'Loading performance metrics...',
  'Analyzing efficiency data...',
  'Calculating optimization potential...',
  'Loading real-time telemetry...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('analytics')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const selectedChiller = ref<any>(null)
const adjustSetpointTemp = ref(7)
const adjustFlowRate = ref(45)

// Real-time metrics
const currentLoad = ref(1850)
const currentLoadPercent = computed(() => (currentLoad.value / 2500) * 100)
const loadColor = computed(() => {
  if (currentLoadPercent.value < 50) return '#67c23a'
  if (currentLoadPercent.value < 80) return '#e6a23c'
  return '#f56c6c'
})
const supplyTemp = ref(7.2)
const returnTemp = ref(12.8)
const deltaT = computed(() => (returnTemp.value - supplyTemp.value).toFixed(1))
const flowRate = ref(42.5)

// Setpoint values
const supplySetpoint = ref(7)
const condenserSetpoint = ref(26)
const primaryChillers = ref(true)
const standbyChillers = ref(false)
const loadBalanceMode = ref('efficiency')

// Health score
const healthScore = ref(82)
const healthColor = ref('#67c23a')

// Chiller units data
const chillers = ref([
  { id: 1, name: 'Chiller 1', status: 'Running', load: 78, cop: 5.9, supplyTemp: 7.1, returnTemp: 12.5, power: 245, flowRate: 42 },
  { id: 2, name: 'Chiller 2', status: 'Running', load: 72, cop: 6.1, supplyTemp: 7.0, returnTemp: 12.6, power: 218, flowRate: 40 },
  { id: 3, name: 'Chiller 3', status: 'Standby', load: 0, cop: 0, supplyTemp: 8.0, returnTemp: 0, power: 12, flowRate: 0 },
  { id: 4, name: 'Chiller 4', status: 'Maintenance', load: 0, cop: 0, supplyTemp: 0, returnTemp: 0, power: 0, flowRate: 0 }
])

// Recommendations
const recommendations = ref([
  { title: 'Increase Supply Temp Setpoint', description: 'Current setpoint can be raised from 7°C to 7.5°C without impacting IT equipment', savings: '~8% energy', roi: '3 months', priority: 'High' },
  { title: 'Enable Load Balancing', description: 'Distribute load evenly between Chiller 1 and 2 for optimal efficiency', savings: '~5% energy', roi: '2 months', priority: 'High' },
  { title: 'Reduce Condenser Water Setpoint', description: 'Lower condenser setpoint to 24°C when ambient permits', savings: '~6% energy', roi: '4 months', priority: 'Medium' },
  { title: 'Schedule Chiller 4 Maintenance', description: 'Unit requires overdue maintenance to restore efficiency', savings: '~10% recovery', roi: '1 month', priority: 'High' }
])

// Strategy impacts
const strategyImpacts = ref([
  { strategy: 'Supply Temp Optimization', savings: '35,000 kWh/year', status: 'Applied' },
  { strategy: 'Load Balancing', savings: '22,000 kWh/year', status: 'Applied' },
  { strategy: 'Condenser Optimization', savings: '18,000 kWh/year', status: 'Pending' },
  { strategy: 'Sequencing Optimization', savings: '15,000 kWh/year', status: 'Planned' }
])

// Alerts
const alerts = ref([
  { severity: 'Warning', message: 'Chiller 3 - Low flow detected', timestamp: '2024-12-18 14:23', status: 'Active' },
  { severity: 'Info', message: 'Chiller 1 efficiency dropped 2%', timestamp: '2024-12-18 10:15', status: 'Active' },
  { severity: 'Critical', message: 'Chiller 4 - Compressor alarm', timestamp: '2024-12-17 09:30', status: 'Acknowledged' }
])

// Chart refs
const chillerPlantChartRef = ref<HTMLElement | null>(null)
const copTrendChartRef = ref<HTMLElement | null>(null)
const loadDistributionChartRef = ref<HTMLElement | null>(null)
const optimizationChartRef = ref<HTMLElement | null>(null)
const savingsChartRef = ref<HTMLElement | null>(null)
const carbonChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const getChillerStatusClass = (status: string) => {
  if (status === 'Running') return 'status-running'
  if (status === 'Standby') return 'status-standby'
  if (status === 'Maintenance') return 'status-maintenance'
  return ''
}

const getChillerTagType = (status: string) => {
  if (status === 'Running') return 'success'
  if (status === 'Standby') return 'warning'
  if (status === 'Maintenance') return 'danger'
  return 'info'
}

const getLoadColor = (load: number) => {
  if (load < 50) return '#67c23a'
  if (load < 80) return '#e6a23c'
  return '#f56c6c'
}

const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const calculateCOPImpact = (temp: number) => {
  const baseCOP = 6.0
  const impact = ((temp - 7) * 0.15).toFixed(2)
  return `${(baseCOP + parseFloat(impact)).toFixed(1)} (+${impact > 0 ? '+' : ''}${impact})`
}

const calculateEnergyImpact = (temp: number) => {
  const impact = ((temp - 7) * 8).toFixed(0)
  return `${Math.abs(parseInt(impact))} ${parseInt(impact) >= 0 ? 'reduction' : 'increase'} kWh/day`
}

const calculateCondenserImpact = (temp: number) => {
  const baseCOP = 6.0
  const impact = ((26 - temp) * 0.1).toFixed(2)
  return `${(baseCOP + parseFloat(impact)).toFixed(1)} (+${impact})`
}

const calculateCondenserEnergyImpact = (temp: number) => {
  const impact = ((26 - temp) * 5).toFixed(0)
  return `${Math.abs(parseInt(impact))} kWh/day ${parseInt(impact) >= 0 ? 'saved' : 'additional'}`
}

const refreshData = () => {
  ElMessage.success('Data refreshed')
}

const viewDetails = () => {
  ElMessage.info('Detailed plant view coming soon')
}

const viewChillerDetails = (chiller: any) => {
  selectedChiller.value = chiller
  detailsDialogVisible.value = true
}

const adjustSetpoint = (chiller: any) => {
  selectedChiller.value = chiller
  adjustSetpointTemp.value = chiller.supplyTemp
  adjustDialogVisible.value = true
}

const confirmAdjustment = () => {
  ElMessage.success(`Setpoint adjusted to ${adjustSetpointTemp.value}°C`)
  adjustDialogVisible.value = false
}

const applyRecommendation = (rec: any) => {
  ElMessage.success(`Applied: ${rec.title}`)
}

const applySetpoints = () => {
  ElMessage.success(`Setpoints applied: Supply ${supplySetpoint.value}°C, Condenser ${condenserSetpoint.value}°C`)
}

const resetSetpoints = () => {
  supplySetpoint.value = 7
  condenserSetpoint.value = 26
  ElMessage.success('Setpoints reset to optimal values')
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const exportReport = () => {
  ElMessage.success('Performance report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

// Chart initialization
const initChillerPlantChart = () => {
  if (chillerPlantChartRef.value) {
    const chart = echarts.init(chillerPlantChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'sankey',
        layout: 'none',
        emphasis: { focus: 'adjacency' },
        data: [
          { name: 'Chiller 1' }, { name: 'Chiller 2' }, { name: 'Chiller 3' },
          { name: 'Primary Pump' }, { name: 'Secondary Pump' },
          { name: 'Cooling Tower 1' }, { name: 'Cooling Tower 2' },
          { name: 'Data Hall' }
        ],
        links: [
          { source: 'Chiller 1', target: 'Primary Pump', value: 245 },
          { source: 'Chiller 2', target: 'Primary Pump', value: 218 },
          { source: 'Chiller 3', target: 'Primary Pump', value: 12 },
          { source: 'Primary Pump', target: 'Secondary Pump', value: 475 },
          { source: 'Secondary Pump', target: 'Data Hall', value: 475 },
          { source: 'Data Hall', target: 'Cooling Tower 1', value: 280 },
          { source: 'Data Hall', target: 'Cooling Tower 2', value: 195 }
        ],
        lineStyle: { color: 'gradient', curveness: 0.5 }
      }]
    })
    chartInstances.push(chart)
  }
}

const initCOPTrendChart = () => {
  if (copTrendChartRef.value) {
    const chart = echarts.init(copTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Chiller 1', 'Chiller 2', 'Target COP'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'COP', min: 4, max: 8 },
      series: [
        { name: 'Chiller 1', type: 'line', data: [5.2, 5.4, 5.6, 5.8, 5.9, 5.9, 5.8, 5.7, 5.9, 6.0, 6.1, 6.1], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'Chiller 2', type: 'line', data: [5.1, 5.3, 5.5, 5.7, 5.8, 5.9, 5.9, 5.8, 6.0, 6.1, 6.2, 6.2], smooth: true, lineStyle: { color: '#67c23a', width: 2 } },
        { name: 'Target COP', type: 'line', data: [5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5], lineStyle: { color: '#e6a23c', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initLoadDistributionChart = () => {
  if (loadDistributionChartRef.value) {
    const chart = echarts.init(loadDistributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie',
        radius: '55%',
        data: [
          { value: 78, name: 'Chiller 1', itemStyle: { color: '#409eff' } },
          { value: 72, name: 'Chiller 2', itemStyle: { color: '#67c23a' } },
          { value: 0, name: 'Chiller 3', itemStyle: { color: '#e6a23c' } },
          { value: 0, name: 'Chiller 4', itemStyle: { color: '#909399' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initOptimizationChart = () => {
  if (optimizationChartRef.value) {
    const chart = echarts.init(optimizationChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Current', 'Optimized'] },
      xAxis: { type: 'category', data: ['Chiller 1', 'Chiller 2', 'Total'] },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        { name: 'Current', type: 'bar', data: [245, 218, 463], itemStyle: { color: '#e6a23c' } },
        { name: 'Optimized', type: 'bar', data: [220, 210, 430], itemStyle: { color: '#67c23a' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initSavingsChart = () => {
  if (savingsChartRef.value) {
    const chart = echarts.init(savingsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Energy Savings (kWh)' },
      series: [{
        type: 'bar',
        data: [8500, 9200, 10100, 10800, 11500, 11800, 11200, 10900, 11400, 12100, 12800, 13200],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#67c23a' },
              { offset: 1, color: '#409eff' }
            ]
          }
        },
        label: { show: true, position: 'top', formatter: '{c} kWh' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initCarbonChart = () => {
  if (carbonChartRef.value) {
    const chart = echarts.init(carbonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Baseline', 'Actual'] },
      xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
      yAxis: { type: 'value', name: 'Carbon (tCO₂e)' },
      series: [
        { name: 'Baseline', type: 'line', data: [95, 100, 105, 110], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Actual', type: 'bar', data: [85, 88, 82, 80], itemStyle: { color: '#67c23a' } }
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
    // Simulate changing real-time metrics
    currentLoad.value = 1800 + Math.random() * 300
    supplyTemp.value = 7 + (Math.random() - 0.5) * 0.5
    returnTemp.value = 12.5 + (Math.random() - 0.5) * 0.8
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
        initChillerPlantChart()
        initCOPTrendChart()
        initLoadDistributionChart()
        initOptimizationChart()
        initSavingsChart()
        initCarbonChart()
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
.chiller-optimization-container {
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
  border-bottom-color: #e6a23c;
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
  background: linear-gradient(90deg, #409eff, #67c23a, #e6a23c);
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
.chiller-optimization-container {
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

/* Plant Overview */
.plant-overview {
  margin-bottom: 24px;
}

.plant-diagram-card,
.performance-card {
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

.plant-diagram {
  min-height: 400px;
}

.live-metrics {
  text-align: center;
}

.metric-big {
  margin-bottom: 24px;
}

.metric-big .metric-label {
  display: block;
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.metric-big .metric-value {
  font-size: 36px;
  font-weight: 700;
  color: #303133;
  display: block;
  margin-bottom: 12px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.metric-item .label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-item .value {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

/* Chiller Units */
.chiller-units-section {
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

.chiller-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.chiller-unit-card:hover {
  transform: translateY(-2px);
}

.chiller-unit-card.status-running {
  border-left: 4px solid #67c23a;
}

.chiller-unit-card.status-standby {
  border-left: 4px solid #e6a23c;
}

.chiller-unit-card.status-maintenance {
  border-left: 4px solid #f56c6c;
}

.chiller-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chiller-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chiller-metrics {
  margin-bottom: 16px;
}

.chiller-metrics .metric {
  margin-bottom: 12px;
}

.chiller-metrics .metric span {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.chiller-metrics .metric strong {
  font-size: 14px;
  color: #303133;
}

.metric-row {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.metric-small {
  flex: 1;
  text-align: center;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

.metric-small span {
  display: block;
  font-size: 10px;
  color: #909399;
}

.metric-small strong {
  font-size: 14px;
  color: #303133;
}

.chiller-footer {
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

/* Recommendations */
.recommendations-list {
  max-height: 500px;
  overflow-y: auto;
}

.recommendation-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
}

.rec-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rec-title {
  flex: 1;
  font-weight: 600;
  color: #303133;
}

.rec-description {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

.rec-impact {
  display: flex;
  gap: 16px;
  margin: 12px 0;
  font-size: 12px;
  color: #909399;
}

/* Setpoint Cards */
.setpoint-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.setpoint-card h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.setpoint-control {
  margin-bottom: 16px;
}

.current-value {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  display: block;
  margin-bottom: 12px;
}

.setpoint-impact {
  margin-top: 16px;
  font-size: 12px;
  color: #909399;
}

.setpoint-impact strong {
  color: #303133;
}

.sequencing-control {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sequence-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons-inline {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Savings Summary */
.savings-summary {
  margin-top: 24px;
  padding: 20px;
  background: linear-gradient(135deg, #ecf5ff 0%, #f0f9ff 100%);
  border-radius: 12px;
}

.savings-stat {
  text-align: center;
}

.savings-stat .stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.savings-stat .stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
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

/* Strategy Impact */
.strategy-impact {
  margin-top: 20px;
}

.strategy-impact h4 {
  margin: 0 0 12px 0;
  color: #303133;
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