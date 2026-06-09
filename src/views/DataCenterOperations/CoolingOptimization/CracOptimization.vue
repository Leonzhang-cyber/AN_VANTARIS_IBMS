<template>
  <div class="crac-optimization-container">
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
            <span class="loading-title">Loading CRAC Optimization Dashboard</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Computer Room Air Conditioner Optimization</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->

      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">CRAC Optimization</span>
          <el-tag type="danger" effect="dark" size="large">Precision Cooling Management</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Temperature /></el-icon>
                <span>Average Rack Inlet Temp</span>
              </div>
              <div class="card-value">22.4°C</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" status="success" :format="() => 'Target: 24°C'" />
                <span class="status-text">ASHRAE Compliant</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Cooling Efficiency (SCOP)</span>
              </div>
              <div class="card-value">3.8</div>
              <div class="card-footer">
                <el-progress :percentage="76" :stroke-width="8" status="warning" :format="() => 'Target: 5.0'" />
                <span class="status-text">Optimization Needed</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Fan Energy Reduction</span>
              </div>
              <div class="card-value">22%</div>
              <div class="card-footer">
                <el-progress :percentage="22" :stroke-width="8" status="success" />
                <span class="status-text">VFD Optimization</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Hotspots Eliminated</span>
              </div>
              <div class="card-value">12</div>
              <div class="card-footer">
                <el-progress :percentage="80" :stroke-width="8" status="success" />
                <span class="status-text">15 Total Identified</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Data Hall Heat Map -->
      <div class="heatmap-section">
        <el-card class="heatmap-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Grid /></el-icon>
            <span>Data Hall Thermal Map</span>
            <div class="header-actions">
              <el-button size="small" @click="zoomIn">Zoom In</el-button>
              <el-button size="small" @click="zoomOut">Zoom Out</el-button>
              <el-button size="small" type="primary" @click="refreshHeatmap">Refresh</el-button>
            </div>
          </div>
          <div class="heatmap-container">
            <div ref="heatmapChartRef" style="height: 450px"></div>
          </div>
          <div class="heatmap-legend">
            <span>Temperature Range:</span>
            <span class="legend-color" style="background: #3b82f6"></span>
            <span>18-20°C</span>
            <span class="legend-color" style="background: #10b981"></span>
            <span>20-22°C</span>
            <span class="legend-color" style="background: #f59e0b"></span>
            <span>22-24°C</span>
            <span class="legend-color" style="background: #ef4444"></span>
            <span>24-26°C+</span>
          </div>
        </el-card>
      </div>

      <!-- CRAC Units Status -->
      <div class="crac-units-section">
        <div class="section-header">
          <h3>CRAC Units Status</h3>
          <div class="header-controls">
            <el-radio-group v-model="unitView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
          </div>
        </div>
        <el-row :gutter="20" v-if="unitView === 'grid'">
          <el-col :span="6" v-for="crac in cracUnits" :key="crac.id">
            <el-card class="crac-unit-card" :class="getCracStatusClass(crac.status)" shadow="hover">
              <div class="crac-header">
                <span class="crac-name">{{ crac.name }}</span>
                <el-tag :type="getCracTagType(crac.status)" size="small">{{ crac.status }}</el-tag>
              </div>
              <div class="crac-metrics">
                <div class="metric-row">
                  <div class="metric">
                    <span>Supply Temp</span>
                    <strong>{{ crac.supplyTemp }}°C</strong>
                  </div>
                  <div class="metric">
                    <span>Return Temp</span>
                    <strong>{{ crac.returnTemp }}°C</strong>
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Fan Speed</span>
                    <el-progress :percentage="crac.fanSpeed" :stroke-width="6" :color="getFanSpeedColor(crac.fanSpeed)" />
                  </div>
                  <div class="metric">
                    <span>Cooling Load</span>
                    <el-progress :percentage="crac.load" :stroke-width="6" :color="getLoadColor(crac.load)" />
                  </div>
                </div>
                <div class="metric-row">
                  <div class="metric">
                    <span>Power</span>
                    <strong>{{ crac.power }} kW</strong>
                  </div>
                  <div class="metric">
                    <span>COP</span>
                    <strong>{{ crac.cop }}</strong>
                  </div>
                </div>
              </div>
              <div class="crac-footer">
                <el-button type="primary" size="small" @click="viewCracDetails(crac)">Details</el-button>
                <el-button size="small" @click="adjustCracSettings(crac)">Adjust</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-table :data="cracUnits" border v-else style="width: 100%">
          <el-table-column prop="name" label="Unit" width="100" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getCracTagType(row.status)">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="supplyTemp" label="Supply °C" width="100" />
          <el-table-column prop="returnTemp" label="Return °C" width="100" />
          <el-table-column prop="fanSpeed" label="Fan Speed %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.fanSpeed" :stroke-width="8" :color="getFanSpeedColor(row.fanSpeed)" />
            </template>
          </el-table-column>
          <el-table-column prop="load" label="Load %" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.load" :stroke-width="8" :color="getLoadColor(row.load)" />
            </template>
          </el-table-column>
          <el-table-column prop="power" label="Power (kW)" width="100" />
          <el-table-column prop="cop" label="COP" width="80" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewCracDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="adjustCracSettings(row)">Adjust</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Temperature Analytics Tab -->
          <el-tab-pane label="Temperature Analytics" name="analytics">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Temperature Trends & Distribution</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="tempTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="tempDistributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Fan Optimization Tab -->
          <el-tab-pane label="Fan Optimization" name="fan">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><WindPower /></el-icon>
                <span>VFD Fan Speed Optimization</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="fanSpeedChartRef" style="height: 350px"></div>
                  </div>
                  <div class="optimization-tips">
                    <h4>Fan Optimization Recommendations</h4>
                    <ul>
                      <li>Reduce fan speed by 5% during low load periods (2 AM - 6 AM)</li>
                      <li>Implement demand-based control instead of fixed speed</li>
                      <li>Stagger fan startup to reduce peak demand</li>
                      <li>Enable auto-standby for redundant units during partial load</li>
                    </ul>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="fan-control-panel">
                    <h4>Manual Fan Control</h4>
                    <div v-for="crac in cracUnits.filter(c => c.status === 'Running')" :key="crac.id" class="fan-control-item">
                      <span>{{ crac.name }}</span>
                      <el-slider v-model="crac.fanSpeed" :min="30" :max="100" :step="5" style="width: 200px" />
                      <span class="fan-power">{{ calculateFanPower(crac.fanSpeed) }} kW</span>
                    </div>
                    <el-button type="primary" style="margin-top: 16px" @click="applyFanSettings">Apply Fan Settings</el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Hotspot Management Tab -->
          <el-tab-pane label="Hotspot Management" name="hotspots">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Hotspot Detection & Resolution</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="hotspots" border style="width: 100%">
                    <el-table-column prop="location" label="Location" width="150" />
                    <el-table-column prop="temperature" label="Temperature" width="100">
                      <template #default="{ row }">
                        <span :style="{ color: row.temperature > 27 ? '#f56c6c' : '#e6a23c' }">
                          {{ row.temperature }}°C
                        </span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.severity === 'Critical' ? 'danger' : 'warning'">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="status" label="Status" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.status === 'Resolved' ? 'success' : 'danger'">{{ row.status }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="action" label="Action Taken" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="hotspot-summary">
                    <h4>Hotspot Resolution Progress</h4>
                    <el-progress :percentage="80" :stroke-width="12" status="success" />
                    <div class="resolution-stats">
                      <div class="stat">Resolved: 12</div>
                      <div class="stat">In Progress: 3</div>
                      <div class="stat">Total: 15</div>
                    </div>
                    <h4 style="margin-top: 20px">Recommended Actions</h4>
                    <el-timeline>
                      <el-timeline-item timestamp="Immediate" type="danger">Increase fan speed on CRAC-03</el-timeline-item>
                      <el-timeline-item timestamp="Short-term" type="warning">Install blanking panels in Rack A12</el-timeline-item>
                      <el-timeline-item timestamp="Long-term" type="primary">Consider local cooling for high-density racks</el-timeline-item>
                    </el-timeline>
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
                <span>Temperature & Humidity Setpoints</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8">
                  <div class="setpoint-card">
                    <h4>Supply Temperature Setpoint</h4>
                    <div class="setpoint-control">
                      <span class="current-value">{{ supplyTempSetpoint }}°C</span>
                      <el-slider v-model="supplyTempSetpoint" :min="18" :max="26" :step="0.5" show-input />
                    </div>
                    <div class="ashrae-range">
                      <span>ASHRAE Recommended Range: 18-27°C</span>
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="setpoint-card">
                    <h4>Return Temperature Setpoint</h4>
                    <div class="setpoint-control">
                      <span class="current-value">{{ returnTempSetpoint }}°C</span>
                      <el-slider v-model="returnTempSetpoint" :min="22" :max="32" :step="0.5" show-input />
                    </div>
                  </div>
                </el-col>
                <el-col :span="8">
                  <div class="setpoint-card">
                    <h4>Humidity Setpoint</h4>
                    <div class="setpoint-control">
                      <span class="current-value">{{ humiditySetpoint }}%</span>
                      <el-slider v-model="humiditySetpoint" :min="40" :max="60" :step="5" show-input />
                    </div>
                    <div class="ashrae-range">
                      <span>ASHRAE Recommended: 40-60% RH</span>
                    </div>
                  </div>
                </el-col>
              </el-row>
              <div class="action-buttons-inline">
                <el-button type="primary" @click="applySetpoints">Apply Setpoints</el-button>
                <el-button @click="resetSetpoints">Reset to ASHRAE Recommended</el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- Energy Savings Tab -->
          <el-tab-pane label="Energy Savings" name="savings">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                <span>CRAC Energy Savings Tracking</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="energySavingsChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="savings-breakdown">
                    <h4>Savings Breakdown</h4>
                    <el-table :data="savingsBreakdown" border size="small">
                      <el-table-column prop="measure" label="Optimization Measure" />
                      <el-table-column prop="savings" label="Energy Savings" />
                      <el-table-column prop="status" label="Status">
                        <template #default="{ row }">
                          <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                    <div class="total-savings">
                      <span>Total Annual Savings:</span>
                      <strong>285,000 kWh</strong>
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
                <span>Active Alerts & Diagnostics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="cracAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Alert Message" />
                    <el-table-column prop="crac" label="CRAC Unit" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="diagnostics-panel">
                    <h4>CRAC Fleet Health</h4>
                    <div class="health-score">
                      <el-progress type="dashboard" :percentage="healthScore" :color="healthColor" :width="150" />
                    </div>
                    <div class="health-metrics">
                      <div class="health-item">
                        <span>Average COP</span>
                        <el-progress :percentage="76" :stroke-width="6" :format="() => '3.8/5.0'" />
                      </div>
                      <div class="health-item">
                        <span>Fan Efficiency</span>
                        <el-progress :percentage="72" :stroke-width="6" />
                      </div>
                      <div class="health-item">
                        <span>Filter Status</span>
                        <el-progress :percentage="85" :stroke-width="6" status="success" />
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
          Export Cooling Report
        </el-button>
        <el-button size="large" @click="scheduleMaintenance">
          <el-icon><Tools /></el-icon>
          Schedule Maintenance
        </el-button>
      </div>
    </template>

    <!-- CRAC Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`CRAC ${selectedCrac?.name} Details`" width="600px">
      <el-descriptions :column="2" border v-if="selectedCrac">
        <el-descriptions-item label="Status">
          <el-tag :type="getCracTagType(selectedCrac.status)">{{ selectedCrac.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Location">Row A, Position {{ selectedCrac.id }}</el-descriptions-item>
        <el-descriptions-item label="Supply Temp">{{ selectedCrac.supplyTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Return Temp">{{ selectedCrac.returnTemp }}°C</el-descriptions-item>
        <el-descriptions-item label="Delta T">{{ (selectedCrac.returnTemp - selectedCrac.supplyTemp).toFixed(1) }}°C</el-descriptions-item>
        <el-descriptions-item label="Fan Speed">{{ selectedCrac.fanSpeed }}%</el-descriptions-item>
        <el-descriptions-item label="Cooling Load">{{ selectedCrac.load }}%</el-descriptions-item>
        <el-descriptions-item label="Power Consumption">{{ selectedCrac.power }} kW</el-descriptions-item>
        <el-descriptions-item label="COP">{{ selectedCrac.cop }}</el-descriptions-item>
        <el-descriptions-item label="Filter Status">Good (85% life remaining)</el-descriptions-item>
        <el-descriptions-item label="Last Maintenance">2024-11-01</el-descriptions-item>
        <el-descriptions-item label="Next Maintenance">2025-02-01</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <!-- Adjust CRAC Settings Dialog -->
    <el-dialog v-model="adjustDialogVisible" title="Adjust CRAC Settings" width="500px">
      <el-form v-if="selectedCrac">
        <el-form-item label="Supply Temperature Setpoint">
          <el-slider v-model="adjustSupplyTemp" :min="18" :max="26" :step="0.5" show-input />
        </el-form-item>
        <el-form-item label="Fan Speed">
          <el-slider v-model="adjustFanSpeed" :min="30" :max="100" :step="5" show-input />
        </el-form-item>
        <el-form-item label="Cooling Mode">
          <el-select v-model="adjustMode" placeholder="Select mode">
            <el-option label="Auto" value="auto" />
            <el-option label="Manual" value="manual" />
            <el-option label="Eco" value="eco" />
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
const loadingMessage = ref('Initializing CRAC systems...')

const loadingMessages = [
  'Initializing CRAC systems...',
  'Loading thermal mapping data...',
  'Analyzing fan performance...',
  'Detecting hotspots...',
  'Calculating optimization potential...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('analytics')
const unitView = ref('grid')
const detailsDialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const selectedCrac = ref<any>(null)
const adjustSupplyTemp = ref(22)
const adjustFanSpeed = ref(60)
const adjustMode = ref('auto')

// Setpoint values
const supplyTempSetpoint = ref(22)
const returnTempSetpoint = ref(28)
const humiditySetpoint = ref(50)

// Health score
const healthScore = ref(78)
const healthColor = ref('#e6a23c')

// CRAC units data
const cracUnits = ref([
  { id: 1, name: 'CRAC-01', status: 'Running', supplyTemp: 22.5, returnTemp: 28.2, fanSpeed: 65, load: 72, power: 18.5, cop: 3.9 },
  { id: 2, name: 'CRAC-02', status: 'Running', supplyTemp: 22.3, returnTemp: 28.0, fanSpeed: 62, load: 68, power: 17.2, cop: 4.0 },
  { id: 3, name: 'CRAC-03', status: 'Running', supplyTemp: 23.0, returnTemp: 29.5, fanSpeed: 78, load: 85, power: 22.1, cop: 3.5 },
  { id: 4, name: 'CRAC-04', status: 'Standby', supplyTemp: 23.5, returnTemp: 27.5, fanSpeed: 30, load: 25, power: 5.2, cop: 0 },
  { id: 5, name: 'CRAC-05', status: 'Running', supplyTemp: 22.1, returnTemp: 27.8, fanSpeed: 58, load: 62, power: 16.8, cop: 4.1 },
  { id: 6, name: 'CRAC-06', status: 'Maintenance', supplyTemp: 24.0, returnTemp: 30.0, fanSpeed: 0, load: 0, power: 0.8, cop: 0 }
])

// Hotspots data
const hotspots = ref([
  { location: 'Rack A12', temperature: 28.5, severity: 'Critical', status: 'In Progress', action: 'Increase CRAC-03 fan speed' },
  { location: 'Rack B08', temperature: 27.2, severity: 'Warning', status: 'In Progress', action: 'Install blanking panels' },
  { location: 'Rack C15', temperature: 26.8, severity: 'Warning', status: 'Resolved', action: 'Relocated equipment' },
  { location: 'Rack D03', temperature: 27.5, severity: 'Warning', status: 'Resolved', action: 'Adjusted airflow' },
  { location: 'Rack A05', temperature: 26.5, severity: 'Warning', status: 'Resolved', action: 'Cleaned filters' }
])

// Savings breakdown
const savingsBreakdown = ref([
  { measure: 'VFD Fan Optimization', savings: '125,000 kWh/year', status: 'Active' },
  { measure: 'Setpoint Adjustment', savings: '85,000 kWh/year', status: 'Active' },
  { measure: 'Hotspot Resolution', savings: '45,000 kWh/year', status: 'Active' },
  { measure: 'Filter Maintenance', savings: '30,000 kWh/year', status: 'Planned' }
])

// CRAC alerts
const cracAlerts = ref([
  { severity: 'Warning', message: 'High return temperature detected', crac: 'CRAC-03', timestamp: '2024-12-18 14:23' },
  { severity: 'Info', message: 'Filter cleaning recommended', crac: 'CRAC-01', timestamp: '2024-12-18 10:15' },
  { severity: 'Warning', message: 'Fan speed above optimal range', crac: 'CRAC-03', timestamp: '2024-12-17 22:30' },
  { severity: 'Critical', message: 'Hotspot detected at Rack A12', crac: 'Multiple', timestamp: '2024-12-17 09:30' }
])

// Chart refs
const heatmapChartRef = ref<HTMLElement | null>(null)
const tempTrendChartRef = ref<HTMLElement | null>(null)
const tempDistributionChartRef = ref<HTMLElement | null>(null)
const fanSpeedChartRef = ref<HTMLElement | null>(null)
const energySavingsChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const getCracStatusClass = (status: string) => {
  if (status === 'Running') return 'status-running'
  if (status === 'Standby') return 'status-standby'
  if (status === 'Maintenance') return 'status-maintenance'
  return ''
}

const getCracTagType = (status: string) => {
  if (status === 'Running') return 'success'
  if (status === 'Standby') return 'warning'
  if (status === 'Maintenance') return 'danger'
  return 'info'
}

const getFanSpeedColor = (speed: number) => {
  if (speed < 50) return '#67c23a'
  if (speed < 75) return '#e6a23c'
  return '#f56c6c'
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

const calculateFanPower = (speed: number) => {
  return (speed / 100 * 15).toFixed(1)
}

const zoomIn = () => {
  ElMessage.info('Zoom feature coming soon')
}

const zoomOut = () => {
  ElMessage.info('Zoom feature coming soon')
}

const refreshHeatmap = () => {
  ElMessage.success('Heatmap refreshed')
}

const viewCracDetails = (crac: any) => {
  selectedCrac.value = crac
  detailsDialogVisible.value = true
}

const adjustCracSettings = (crac: any) => {
  selectedCrac.value = crac
  adjustSupplyTemp.value = crac.supplyTemp
  adjustFanSpeed.value = crac.fanSpeed
  adjustDialogVisible.value = true
}

const confirmAdjustment = () => {
  if (selectedCrac.value) {
    selectedCrac.value.supplyTemp = adjustSupplyTemp.value
    selectedCrac.value.fanSpeed = adjustFanSpeed.value
    ElMessage.success(`CRAC ${selectedCrac.value.name} settings updated`)
  }
  adjustDialogVisible.value = false
}

const applyFanSettings = () => {
  ElMessage.success('Fan settings applied to all running CRAC units')
}

const applySetpoints = () => {
  ElMessage.success(`Setpoints applied: Supply ${supplyTempSetpoint.value}°C, Return ${returnTempSetpoint.value}°C, Humidity ${humiditySetpoint.value}%`)
}

const resetSetpoints = () => {
  supplyTempSetpoint.value = 22
  returnTempSetpoint.value = 28
  humiditySetpoint.value = 50
  ElMessage.success('Setpoints reset to ASHRAE recommended values')
}

const runOptimization = () => {
  ElMessage.success('AI optimization started. Results will be available shortly.')
}

const exportReport = () => {
  ElMessage.success('Cooling performance report export started')
}

const scheduleMaintenance = () => {
  ElMessage.info('Maintenance scheduling interface will open')
}

// Chart initialization
const initHeatmapChart = () => {
  if (heatmapChartRef.value) {
    const chart = echarts.init(heatmapChartRef.value)
    const hours = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    const data: any[] = []

    for (let i = 0; i < days.length; i++) {
      for (let j = 0; j < hours.length; j++) {
        data.push([j, i, 20 + Math.random() * 8])
      }
    }

    chart.setOption({
      tooltip: { position: 'top' },
      xAxis: { type: 'category', data: hours, name: 'Time' },
      yAxis: { type: 'category', data: days, name: 'Day' },
      visualMap: { min: 20, max: 30, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false }, emphasis: { scale: true } }]
    })
    chartInstances.push(chart)
  }
}

const initTempTrendChart = () => {
  if (tempTrendChartRef.value) {
    const chart = echarts.init(tempTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Supply Temp', 'Return Temp', 'Rack Inlet Avg'] },
      xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'] },
      yAxis: { type: 'value', name: 'Temperature (°C)', min: 18, max: 32 },
      series: [
        { name: 'Supply Temp', type: 'line', data: [22.1, 22.0, 22.3, 22.5, 22.4, 22.2], smooth: true, lineStyle: { color: '#409eff', width: 2 } },
        { name: 'Return Temp', type: 'line', data: [27.8, 27.6, 28.0, 28.2, 28.1, 27.9], smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
        { name: 'Rack Inlet Avg', type: 'line', data: [23.5, 23.2, 23.8, 24.0, 23.9, 23.6], smooth: true, lineStyle: { color: '#67c23a', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initTempDistributionChart = () => {
  if (tempDistributionChartRef.value) {
    const chart = echarts.init(tempDistributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['<20°C', '20-22°C', '22-24°C', '24-26°C', '>26°C'] },
      yAxis: { type: 'value', name: 'Number of Sensors' },
      series: [{
        type: 'bar', data: [8, 45, 68, 32, 12],
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: '#3b82f6' },
              { offset: 0.5, color: '#10b981' },
              { offset: 0.75, color: '#f59e0b' },
              { offset: 1, color: '#ef4444' }
            ]
          }
        },
        label: { show: true, position: 'top' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initFanSpeedChart = () => {
  if (fanSpeedChartRef.value) {
    const chart = echarts.init(fanSpeedChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Fan Speed', 'Power Consumption'] },
      xAxis: { type: 'category', data: cracUnits.value.filter(c => c.status === 'Running').map(c => c.name) },
      yAxis: [{ type: 'value', name: 'Fan Speed (%)' }, { type: 'value', name: 'Power (kW)' }],
      series: [
        { name: 'Fan Speed', type: 'bar', data: cracUnits.value.filter(c => c.status === 'Running').map(c => c.fanSpeed), itemStyle: { color: '#409eff' }, label: { show: true, position: 'top', formatter: '{c}%' } },
        { name: 'Power Consumption', type: 'line', yAxisIndex: 1, data: cracUnits.value.filter(c => c.status === 'Running').map(c => c.power), lineStyle: { color: '#f56c6c', width: 2 }, symbol: 'circle', symbolSize: 8 }
      ]
    })
    chartInstances.push(chart)
  }
}

const initEnergySavingsChart = () => {
  if (energySavingsChartRef.value) {
    const chart = echarts.init(energySavingsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Baseline', 'Optimized', 'Savings'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Energy (kWh)' },
      series: [
        { name: 'Baseline', type: 'line', data: [8200, 8100, 8300, 8500, 8800, 9000, 9200, 9100, 8800, 8500, 8200, 8000], lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Optimized', type: 'line', data: [7500, 7400, 7600, 7700, 7900, 8100, 8300, 8200, 7900, 7600, 7400, 7200], lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Savings', type: 'bar', data: [700, 700, 700, 800, 900, 900, 900, 900, 900, 900, 800, 800], itemStyle: { color: '#409eff' }, label: { show: true, position: 'top', formatter: '{c} kWh' } }
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
        initHeatmapChart()
        initTempTrendChart()
        initTempDistributionChart()
        initFanSpeedChart()
        initEnergySavingsChart()
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
.crac-optimization-container {
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
.crac-optimization-container {
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

/* Heatmap Section */
.heatmap-section {
  margin-bottom: 24px;
}

.heatmap-card {
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

.heatmap-container {
  min-height: 450px;
}

.heatmap-legend {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #909399;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 4px;
  display: inline-block;
}

/* CRAC Units */
.crac-units-section {
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

.crac-unit-card {
  border-radius: 12px;
  transition: transform 0.2s;
  height: 100%;
}

.crac-unit-card:hover {
  transform: translateY(-2px);
}

.crac-unit-card.status-running {
  border-left: 4px solid #67c23a;
}

.crac-unit-card.status-standby {
  border-left: 4px solid #e6a23c;
}

.crac-unit-card.status-maintenance {
  border-left: 4px solid #f56c6c;
}

.crac-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.crac-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.crac-metrics {
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

.crac-footer {
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

/* Optimization Tips */
.optimization-tips {
  margin-top: 20px;
  padding: 16px;
  background: #ecf5ff;
  border-radius: 8px;
}

.optimization-tips h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.optimization-tips ul {
  margin: 0;
  padding-left: 20px;
}

.optimization-tips li {
  margin: 8px 0;
  color: #606266;
}

/* Fan Control Panel */
.fan-control-panel {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
}

.fan-control-panel h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.fan-control-item {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.fan-control-item span:first-child {
  width: 80px;
  font-weight: 500;
}

.fan-power {
  width: 60px;
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

.ashrae-range {
  margin-top: 16px;
  font-size: 12px;
  color: #909399;
}

.action-buttons-inline {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Savings Breakdown */
.savings-breakdown {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 350px;
  display: flex;
  flex-direction: column;
}

.savings-breakdown h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.total-savings {
  margin-top: auto;
  padding-top: 16px;
  text-align: center;
  font-size: 14px;
}

.total-savings strong {
  font-size: 20px;
  color: #409eff;
  margin-left: 8px;
}

/* Hotspot Summary */
.hotspot-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.hotspot-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.resolution-stats {
  display: flex;
  gap: 20px;
  margin-top: 16px;
}

.stat {
  font-size: 14px;
  font-weight: 500;
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