<template>
  <div class="rack-capacity-container">
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
            <span class="loading-title">Loading Rack Capacity</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Rack Space & Power Capacity Management</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Rack Capacity</span>
          <el-tag type="primary" effect="dark" size="large">Capacity Management</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Grid /></el-icon>
                <span>Total Racks</span>
              </div>
              <div class="card-value">{{ totalRacks }}</div>
              <div class="card-footer">
                <el-progress :percentage="(usedRacks / totalRacks) * 100" :stroke-width="8" status="success" />
                <span class="status-text">{{ usedRacks }} Used / {{ freeRacks }} Free</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Menu /></el-icon>
                <span>U Space Utilization</span>
              </div>
              <div class="card-value">{{ uUtilization }}%</div>
              <div class="card-footer">
                <el-progress :percentage="uUtilization" :stroke-width="8" :color="uColor" />
                <span class="status-text">{{ usedU }} / {{ totalU }} U used</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Power Capacity</span>
              </div>
              <div class="card-value">{{ powerUtilization }}%</div>
              <div class="card-footer">
                <el-progress :percentage="powerUtilization" :stroke-width="8" :color="powerColor" />
                <span class="status-text">{{ usedPower }} / {{ totalPower }} kW</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Temperature /></el-icon>
                <span>Cooling Capacity</span>
              </div>
              <div class="card-value">{{ coolingUtilization }}%</div>
              <div class="card-footer">
                <el-progress :percentage="coolingUtilization" :stroke-width="8" :color="coolingColor" />
                <span class="status-text">Heat Load: {{ heatLoad }} kW</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Rack Visualization -->
      <div class="rack-viz-section">
        <el-card class="viz-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Grid /></el-icon>
            <span>Rack View - Row {{ selectedRow }}</span>
            <div class="header-actions">
              <el-select v-model="selectedRow" size="small" style="width: 100px">
                <el-option label="Row A" value="A" />
                <el-option label="Row B" value="B" />
                <el-option label="Row C" value="C" />
                <el-option label="Row D" value="D" />
              </el-select>
              <el-button size="small" @click="prevRow" :disabled="selectedRow === 'A'">◀</el-button>
              <el-button size="small" @click="nextRow" :disabled="selectedRow === 'D'">▶</el-button>
              <el-button size="small" type="primary" @click="toggle3DView">3D View</el-button>
            </div>
          </div>
          <div class="rack-viz-container">
            <div class="rack-viz-grid">
              <div
                  v-for="rack in currentRowRacks"
                  :key="rack.id"
                  class="rack-viz-item"
                  :class="{ selected: selectedRack?.id === rack.id }"
                  @click="selectRack(rack)"
              >
                <div class="rack-header">
                  <span class="rack-name">{{ rack.name }}</span>
                  <el-tag :type="getRackStatusType(rack)" size="small">
                    {{ rack.heatLoad }}%
                  </el-tag>
                </div>
                <div class="rack-u-viz">
                  <div
                      v-for="u in 42"
                      :key="u"
                      class="u-unit"
                      :class="{
                      'occupied': rack.occupiedU.includes(u),
                      'available': !rack.occupiedU.includes(u) && u <= rack.deviceCount,
                      'planned': rack.plannedU.includes(u)
                    }"
                      :style="{ height: (380 / 42) + 'px' }"
                  ></div>
                </div>
                <div class="rack-footer">
                  <span>{{ rack.usedU }}/42 U</span>
                  <span>{{ rack.power }} kW</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Capacity Dashboard -->
      <div class="capacity-dashboard-section">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="capacity-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Menu /></el-icon>
                <span>Space Capacity</span>
              </div>
              <div class="gauge-container">
                <div ref="spaceGaugeRef" style="height: 200px"></div>
              </div>
              <div class="capacity-stats">
                <div class="stat-row">
                  <span>Used U Space</span>
                  <strong>{{ usedU }} U</strong>
                </div>
                <div class="stat-row">
                  <span>Free U Space</span>
                  <strong>{{ freeU }} U</strong>
                </div>
                <div class="stat-row">
                  <span>Planned U</span>
                  <strong>{{ plannedU }} U</strong>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="capacity-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Cpu /></el-icon>
                <span>Power Capacity</span>
              </div>
              <div class="gauge-container">
                <div ref="powerGaugeRef" style="height: 200px"></div>
              </div>
              <div class="capacity-stats">
                <div class="stat-row">
                  <span>Current Power</span>
                  <strong>{{ usedPower }} kW</strong>
                </div>
                <div class="stat-row">
                  <span>Available Power</span>
                  <strong>{{ totalPower - usedPower }} kW</strong>
                </div>
                <div class="stat-row">
                  <span>Peak Power</span>
                  <strong>{{ peakPower }} kW</strong>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card class="capacity-card" shadow="hover">
              <div class="card-header-simple">
                <el-icon><Temperature /></el-icon>
                <span>Cooling Capacity</span>
              </div>
              <div class="gauge-container">
                <div ref="coolingGaugeRef" style="height: 200px"></div>
              </div>
              <div class="capacity-stats">
                <div class="stat-row">
                  <span>Current Heat Load</span>
                  <strong>{{ heatLoad }} kW</strong>
                </div>
                <div class="stat-row">
                  <span>Available Cooling</span>
                  <strong>{{ totalCooling - heatLoad }} kW</strong>
                </div>
                <div class="stat-row">
                  <span>PUE Impact</span>
                  <strong>{{ pueImpact }}</strong>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Rack Capacity Table -->
      <div class="rack-table-section">
        <div class="section-header">
          <h3>Rack Capacity Details</h3>
          <div class="header-controls">
            <el-input v-model="searchQuery" placeholder="Search rack..." prefix-icon="Search" style="width: 200px" clearable />
            <el-button type="primary" @click="exportCapacityReport">Export Report</el-button>
          </div>
        </div>
        <el-table :data="filteredRacks" border style="width: 100%">
          <el-table-column prop="name" label="Rack"  />
          <el-table-column prop="row" label="Row"  />
          <el-table-column label="U Space" >
            <template #default="{ row }">
              <el-progress :percentage="(row.usedU / 42) * 100" :stroke-width="12" :color="getUColor(row.usedU / 42)" />
              <span class="progress-text">{{ row.usedU }}/42 U</span>
            </template>
          </el-table-column>
          <el-table-column label="Power" >
            <template #default="{ row }">
              <el-progress :percentage="(row.power / row.maxPower) * 100" :stroke-width="12" :color="getPowerColor(row.power / row.maxPower)" />
              <span class="progress-text">{{ row.power }}/{{ row.maxPower }} kW</span>
            </template>
          </el-table-column>
          <el-table-column label="Cooling" >
            <template #default="{ row }">
              <el-progress :percentage="(row.heatLoad / row.maxCooling) * 100" :stroke-width="12" :color="getCoolingColor(row.heatLoad / row.maxCooling)" />
              <span class="progress-text">{{ row.heatLoad }}/{{ row.maxCooling }} kW</span>
            </template>
          </el-table-column>
          <el-table-column prop="deviceCount" label="Devices"  />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row)" size="small">{{ getStatusText(row) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="120">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewRackDetail(row)">Details</el-button>
              <el-button type="success" link size="small" @click="planDevice(row)">Plan</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Capacity Trends Tab -->
          <el-tab-pane label="Capacity Trends" name="trends">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Capacity Utilization Trends</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="capacityTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="powerTrendChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Utilization Heatmap Tab -->
          <el-tab-pane label="Utilization Heatmap" name="heatmap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>Rack Utilization Heatmap</span>
              </div>
              <div class="chart-container">
                <div ref="heatmapChartRef" style="height: 450px"></div>
              </div>
            </div>
          </el-tab-pane>

          <!-- Capacity Planning Tab -->
          <el-tab-pane label="Capacity Planning" name="planning">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                <span>Capacity Planning & Forecasting</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="forecastChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="planning-stats">
                    <div class="stat-card">
                      <div class="stat-value">{{ monthsUntilFull }} months</div>
                      <div class="stat-label">Until Space Full</div>
                    </div>
                    <div class="stat-card">
                      <div class="stat-value">{{ powerMonthsUntilFull }} months</div>
                      <div class="stat-label">Until Power Full</div>
                    </div>
                    <div class="recommendation-box">
                      <h4>Recommendation</h4>
                      <p>Based on current growth rate, additional racks will be needed in {{ monthsUntilFull }} months. Consider row expansion.</p>
                      <el-button type="primary" size="small" @click="generatePlan">Generate Expansion Plan</el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Device Placement Suggestions Tab -->
          <el-tab-pane label="Placement Suggestions" name="placement">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Location /></el-icon>
                <span>Device Placement Suggestions</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="placementSuggestions" border style="width: 100%">
                    <el-table-column prop="device" label="Device" />
                    <el-table-column prop="requirements" label="Requirements" />
                    <el-table-column prop="suggestedRack" label="Suggested Rack" />
                    <el-table-column prop="availableU" label="Available U" />
                    <el-table-column prop="availablePower" label="Available Power" />
                    <el-table-column label="Action" width="100">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="placeDevice(row)">Place</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="placement-summary">
                    <h4>Placement Rules</h4>
                    <ul>
                      <li>High power devices → Bottom of rack</li>
                      <li>Network devices → Top of rack</li>
                      <li>Storage devices → Middle of rack</li>
                      <li>Keep hot/cold aisle alignment</li>
                      <li>Balance power across phases</li>
                    </ul>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="autoPlaceDevices">
                      Auto-Place Pending Devices
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Alerts & Recommendations Tab -->
          <el-tab-pane label="Alerts & Recommendations" name="alerts">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Bell /></el-icon>
                <span>Capacity Alerts</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <el-table :data="capacityAlerts" border style="width: 100%">
                    <el-table-column prop="severity" label="Severity" width="100">
                      <template #default="{ row }">
                        <el-tag :type="getAlertSeverityType(row.severity)" size="small">
                          {{ row.severity }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="message" label="Message" />
                    <el-table-column prop="rack" label="Rack" width="100" />
                    <el-table-column prop="timestamp" label="Time" width="160" />
                  </el-table>
                </el-col>
                <el-col :span="10">
                  <div class="recommendation-panel">
                    <h4>Recommendations</h4>
                    <div class="rec-item" v-for="(rec, idx) in recommendations" :key="idx">
                      <el-icon><Setting /></el-icon>
                      <span>{{ rec }}</span>
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
        <el-button type="primary" size="large" @click="optimizeCapacity">
          <el-icon><Cpu /></el-icon>
          Optimize Capacity
        </el-button>
        <el-button size="large" @click="exportFullReport">
          <el-icon><Download /></el-icon>
          Export Full Report
        </el-button>
        <el-button size="large" @click="scheduleAudit">
          <el-icon><Calendar /></el-icon>
          Schedule Capacity Audit
        </el-button>
      </div>
    </template>

    <!-- Rack Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Rack ${selectedRack?.name} Details`" width="700px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Location">Row {{ selectedRack?.row }}, Position {{ selectedRack?.position }}</el-descriptions-item>
            <el-descriptions-item label="U Space">{{ selectedRack?.usedU }}/42 U used</el-descriptions-item>
            <el-descriptions-item label="Power">{{ selectedRack?.power }}/{{ selectedRack?.maxPower }} kW</el-descriptions-item>
            <el-descriptions-item label="Heat Load">{{ selectedRack?.heatLoad }}/{{ selectedRack?.maxCooling }} kW</el-descriptions-item>
            <el-descriptions-item label="Devices">{{ selectedRack?.deviceCount }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusType(selectedRack)">{{ getStatusText(selectedRack) }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
        <el-col :span="12">
          <div class="rack-u-detail">
            <h4>U Space Utilization</h4>
            <div class="u-bars">
              <div v-for="u in 42" :key="u" class="u-bar" :class="{ occupied: selectedRack?.occupiedU.includes(u) }">
                <span class="u-number">{{ u }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editRack">Edit Capacity</el-button>
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
const loadingMessage = ref('Loading rack capacity data...')

const loadingMessages = [
  'Loading rack capacity data...',
  'Mapping U space utilization...',
  'Analyzing power distribution...',
  'Calculating cooling capacity...',
  'Generating heatmap...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('trends')
const selectedRow = ref('A')
const selectedRack = ref<any>(null)
const searchQuery = ref('')
const detailDialogVisible = ref(false)

// Capacity metrics
const totalRacks = ref(48)
const usedRacks = ref(38)
const freeRacks = ref(10)
const totalU = ref(2016)
const usedU = ref(1450)
const freeU = ref(566)
const plannedU = ref(85)
const uUtilization = computed(() => Math.round((usedU.value / totalU.value) * 100))

const totalPower = ref(750)
const usedPower = ref(485)
const peakPower = ref(520)
const powerUtilization = computed(() => Math.round((usedPower.value / totalPower.value) * 100))

const totalCooling = ref(800)
const heatLoad = ref(465)
const coolingUtilization = computed(() => Math.round((heatLoad.value / totalCooling.value) * 100))
const pueImpact = ref(1.42)

const monthsUntilFull = ref(8)
const powerMonthsUntilFull = ref(12)

// Colors
const uColor = computed(() => {
  if (uUtilization.value < 70) return '#67c23a'
  if (uUtilization.value < 85) return '#e6a23c'
  return '#f56c6c'
})

const powerColor = computed(() => {
  if (powerUtilization.value < 70) return '#67c23a'
  if (powerUtilization.value < 85) return '#e6a23c'
  return '#f56c6c'
})

const coolingColor = computed(() => {
  if (coolingUtilization.value < 70) return '#67c23a'
  if (coolingUtilization.value < 85) return '#e6a23c'
  return '#f56c6c'
})

// Rack data
const racks = ref([
  { id: 1, name: 'A01', row: 'A', position: 1, usedU: 38, occupiedU: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38], plannedU: [], power: 8.5, maxPower: 15, heatLoad: 8.2, maxCooling: 15, deviceCount: 12, status: 'Normal' },
  { id: 2, name: 'A02', row: 'A', position: 2, usedU: 35, occupiedU: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35], plannedU: [], power: 7.8, maxPower: 15, heatLoad: 7.5, maxCooling: 15, deviceCount: 11, status: 'Normal' },
  { id: 3, name: 'A03', row: 'A', position: 3, usedU: 40, occupiedU: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40], plannedU: [], power: 12.5, maxPower: 15, heatLoad: 12.0, maxCooling: 15, deviceCount: 14, status: 'Warning' },
  { id: 4, name: 'A04', row: 'A', position: 4, usedU: 28, occupiedU: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28], plannedU: [29,30,31], power: 6.2, maxPower: 15, heatLoad: 5.8, maxCooling: 15, deviceCount: 9, status: 'Normal' },
  { id: 5, name: 'B01', row: 'B', position: 1, usedU: 42, occupiedU: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42], plannedU: [], power: 14.2, maxPower: 15, heatLoad: 13.8, maxCooling: 15, deviceCount: 16, status: 'Critical' },
  { id: 6, name: 'B02', row: 'B', position: 2, usedU: 32, occupiedU: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32], plannedU: [], power: 7.2, maxPower: 15, heatLoad: 6.8, maxCooling: 15, deviceCount: 10, status: 'Normal' }
])

// Current row racks
const currentRowRacks = computed(() => racks.value.filter(r => r.row === selectedRow.value))

// Filtered racks for table
const filteredRacks = computed(() => {
  if (!searchQuery.value) return racks.value
  return racks.value.filter(r => r.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

// Placement suggestions
const placementSuggestions = ref([
  { device: 'New Server - High Density', requirements: '4U, 2.5kW, 45°C max', suggestedRack: 'C03', availableU: '6U', availablePower: '3.2kW' },
  { device: 'Storage Array', requirements: '3U, 1.8kW, 40°C max', suggestedRack: 'B04', availableU: '8U', availablePower: '4.5kW' },
  { device: 'Network Switch', requirements: '1U, 0.5kW, 50°C max', suggestedRack: 'A02', availableU: '7U', availablePower: '7.2kW' }
])

// Capacity alerts
const capacityAlerts = ref([
  { severity: 'Critical', message: 'Rack B01 at 100% U space capacity', rack: 'B01', timestamp: '2024-12-18 14:23' },
  { severity: 'Warning', message: 'Rack A03 power at 83% of capacity', rack: 'A03', timestamp: '2024-12-18 10:15' },
  { severity: 'Info', message: 'Row D has 8 free racks available', rack: 'Row D', timestamp: '2024-12-18 08:30' }
])

// Recommendations
const recommendations = ref([
  'Add 2 new racks to Row D (space available)',
  'Consolidate partially filled racks to free up space',
  'Upgrade power feed to Row B for additional capacity',
  'Consider high-density cooling for Row A'
])

// Helper functions
const getRackStatusType = (rack: any) => {
  if (rack.status === 'Critical') return 'danger'
  if (rack.status === 'Warning') return 'warning'
  return 'success'
}

const getUColor = (ratio: number) => {
  if (ratio < 0.7) return '#67c23a'
  if (ratio < 0.85) return '#e6a23c'
  return '#f56c6c'
}

const getPowerColor = (ratio: number) => {
  if (ratio < 0.7) return '#67c23a'
  if (ratio < 0.85) return '#e6a23c'
  return '#f56c6c'
}

const getCoolingColor = (ratio: number) => {
  if (ratio < 0.7) return '#67c23a'
  if (ratio < 0.85) return '#e6a23c'
  return '#f56c6c'
}

const getStatusType = (rack: any) => {
  if (rack.status === 'Critical') return 'danger'
  if (rack.status === 'Warning') return 'warning'
  return 'success'
}

const getStatusText = (rack: any) => {
  if (rack.status === 'Critical') return 'Critical'
  if (rack.status === 'Warning') return 'Warning'
  return 'Normal'
}

const getAlertSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'Warning') return 'warning'
  return 'info'
}

const selectRack = (rack: any) => {
  selectedRack.value = rack
}

const viewRackDetail = (rack: any) => {
  selectedRack.value = rack
  detailDialogVisible.value = true
}

const planDevice = (rack: any) => {
  ElMessage.info(`Planning device placement in ${rack.name}`)
}

const editRack = () => {
  ElMessage.info(`Editing capacity for ${selectedRack.value.name}`)
  detailDialogVisible.value = false
}

const prevRow = () => {
  const rows = ['A', 'B', 'C', 'D']
  const idx = rows.indexOf(selectedRow.value)
  if (idx > 0) selectedRow.value = rows[idx - 1]
}

const nextRow = () => {
  const rows = ['A', 'B', 'C', 'D']
  const idx = rows.indexOf(selectedRow.value)
  if (idx < rows.length - 1) selectedRow.value = rows[idx + 1]
}

const toggle3DView = () => {
  ElMessage.info('3D view mode coming soon')
}

const exportCapacityReport = () => {
  ElMessage.success('Capacity report export started')
}

const exportFullReport = () => {
  ElMessage.success('Full capacity report export started')
}

const optimizeCapacity = () => {
  ElMessage.success('Capacity optimization started')
}

const scheduleAudit = () => {
  ElMessage.info('Capacity audit scheduling interface will open')
}

const generatePlan = () => {
  ElMessage.success('Expansion plan generated')
}

const placeDevice = (suggestion: any) => {
  ElMessage.success(`Device placed in ${suggestion.suggestedRack}`)
}

const autoPlaceDevices = () => {
  ElMessage.success('Auto-placement completed. 3 devices placed.')
}

// Chart refs
const spaceGaugeRef = ref<HTMLElement | null>(null)
const powerGaugeRef = ref<HTMLElement | null>(null)
const coolingGaugeRef = ref<HTMLElement | null>(null)
const capacityTrendChartRef = ref<HTMLElement | null>(null)
const powerTrendChartRef = ref<HTMLElement | null>(null)
const heatmapChartRef = ref<HTMLElement | null>(null)
const forecastChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Chart initialization
const initSpaceGauge = () => {
  if (spaceGaugeRef.value) {
    const chart = echarts.init(spaceGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 0,
        max: 100,
        splitNumber: 5,
        progress: { show: true, width: 18, itemStyle: { color: uColor.value } },
        axisLine: { lineStyle: { width: 18, color: [[0.7, '#67c23a'], [0.85, '#e6a23c'], [1, '#f56c6c']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}%' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12 },
        data: [{ value: uUtilization.value, name: 'Space' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initPowerGauge = () => {
  if (powerGaugeRef.value) {
    const chart = echarts.init(powerGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 0,
        max: 100,
        splitNumber: 5,
        progress: { show: true, width: 18, itemStyle: { color: powerColor.value } },
        axisLine: { lineStyle: { width: 18, color: [[0.7, '#67c23a'], [0.85, '#e6a23c'], [1, '#f56c6c']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}%' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12 },
        data: [{ value: powerUtilization.value, name: 'Power' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initCoolingGauge = () => {
  if (coolingGaugeRef.value) {
    const chart = echarts.init(coolingGaugeRef.value)
    chart.setOption({
      series: [{
        type: 'gauge',
        center: ['50%', '50%'],
        radius: '70%',
        min: 0,
        max: 100,
        splitNumber: 5,
        progress: { show: true, width: 18, itemStyle: { color: coolingColor.value } },
        axisLine: { lineStyle: { width: 18, color: [[0.7, '#67c23a'], [0.85, '#e6a23c'], [1, '#f56c6c']] } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        pointer: { show: true, length: '60%', width: 8 },
        detail: { show: true, offsetCenter: [0, 20], fontSize: 16, formatter: '{value}%' },
        title: { show: true, offsetCenter: [0, -20], fontSize: 12 },
        data: [{ value: coolingUtilization.value, name: 'Cooling' }]
      }]
    })
    chartInstances.push(chart)
  }
}

const initCapacityTrendChart = () => {
  if (capacityTrendChartRef.value) {
    const chart = echarts.init(capacityTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['U Space Used', 'Available U', 'Planned U'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'U Space' },
      series: [
        { name: 'U Space Used', type: 'area', data: [1250, 1280, 1320, 1350, 1380, 1410, 1430, 1450, 1470, 1490, 1510, 1530], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Available U', type: 'area', data: [766, 736, 696, 666, 636, 606, 586, 566, 546, 526, 506, 486], smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Planned U', type: 'bar', data: [0, 0, 0, 0, 0, 0, 20, 30, 45, 55, 70, 85], itemStyle: { color: '#f59e0b' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPowerTrendChart = () => {
  if (powerTrendChartRef.value) {
    const chart = echarts.init(powerTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Power Usage', 'Capacity Limit'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Power (kW)' },
      series: [
        { name: 'Power Usage', type: 'line', data: [420, 435, 445, 455, 465, 470, 478, 485, 492, 498, 505, 512], smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Capacity Limit', type: 'line', data: [750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750, 750], lineStyle: { color: '#909399', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initHeatmapChart = () => {
  if (heatmapChartRef.value) {
    const chart = echarts.init(heatmapChartRef.value)
    const data: any[] = []
    const rows = ['A', 'B', 'C', 'D', 'E', 'F']
    const cols = Array.from({ length: 12 }, (_, i) => i + 1)

    for (let i = 0; i < rows.length; i++) {
      for (let j = 0; j < cols.length; j++) {
        let value = 30 + Math.random() * 60
        if (i === 1 && j === 2) value = 95
        if (i === 0 && j === 4) value = 85
        data.push([j, i, value])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Rack ${rows[params.data[1]]}${cols[params.data[0]]}<br/>Utilization: ${params.data[2].toFixed(0)}%` },
      xAxis: { type: 'category', data: cols, name: 'Position' },
      yAxis: { type: 'category', data: rows, name: 'Row' },
      visualMap: { min: 0, max: 100, calculable: true, inRange: { color: ['#10b981', '#84cc16', '#f59e0b', '#ef4444', '#7c2d12'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false }, emphasis: { scale: true } }]
    })
    chartInstances.push(chart)
  }
}

const initForecastChart = () => {
  if (forecastChartRef.value) {
    const chart = echarts.init(forecastChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Historical', 'Forecast', 'Capacity Limit'] },
      xAxis: { type: 'category', data: ['2024 Q1', '2024 Q2', '2024 Q3', '2024 Q4', '2025 Q1', '2025 Q2', '2025 Q3', '2025 Q4'] },
      yAxis: { type: 'value', name: 'U Space Usage' },
      series: [
        { name: 'Historical', type: 'line', data: [1250, 1320, 1380, 1450, null, null, null, null], smooth: true, lineStyle: { color: '#409eff', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Forecast', type: 'line', data: [null, null, null, 1450, 1520, 1580, 1650, 1720], smooth: true, lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } },
        { name: 'Capacity Limit', type: 'line', data: [2016, 2016, 2016, 2016, 2016, 2016, 2016, 2016], lineStyle: { color: '#f56c6c', width: 2, type: 'dotted' } }
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
    usedPower.value = 480 + Math.random() * 10
    heatLoad.value = 460 + Math.random() * 10
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
        initSpaceGauge()
        initPowerGauge()
        initCoolingGauge()
        initCapacityTrendChart()
        initPowerTrendChart()
        initHeatmapChart()
        initForecastChart()
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
.rack-capacity-container {
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
.rack-capacity-container {
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

/* Rack Visualization */
.rack-viz-section {
  margin-bottom: 24px;
}

.viz-card {
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

.rack-viz-container {
  overflow-x: auto;
}

.rack-viz-grid {
  display: flex;
  gap: 16px;
  min-width: 600px;
}

.rack-viz-item {
  flex: 1;
  min-width: 120px;
  background: #f5f7fa;
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.rack-viz-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rack-viz-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.rack-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rack-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.rack-u-viz {
  display: flex;
  flex-direction: column;
  height: 380px;
  overflow: hidden;
  border-radius: 8px;
  background: #e4e7ed;
}

.u-unit {
  flex: 1;
  min-height: 8px;
  border: 0.5px solid rgba(255, 255, 255, 0.2);
}

.u-unit.occupied {
  background: #409eff;
}

.u-unit.available {
  background: #67c23a;
}

.u-unit.planned {
  background: #f59e0b;
}

.rack-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 11px;
  color: #909399;
}

/* Capacity Dashboard */
.capacity-dashboard-section {
  margin-bottom: 24px;
}

.capacity-card {
  height: 100%;
}

.gauge-container {
  padding: 8px;
}

.capacity-stats {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 13px;
}

.stat-row strong {
  color: #409eff;
}

/* Rack Table Section */
.rack-table-section {
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

.header-controls {
  display: flex;
  gap: 12px;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 11px;
  margin-top: 4px;
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

/* Planning Stats */
.planning-stats {
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
  margin-top: 8px;
}

.recommendation-box {
  background: #ecf5ff;
  border-radius: 8px;
  padding: 16px;
}

.recommendation-box h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.recommendation-box p {
  font-size: 13px;
  color: #606266;
  margin-bottom: 12px;
}

/* Placement Summary */
.placement-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.placement-summary h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.placement-summary ul {
  margin: 0;
  padding-left: 20px;
}

.placement-summary li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

/* Recommendation Panel */
.recommendation-panel {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.recommendation-panel h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.rec-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.rec-item .el-icon {
  color: #f59e0b;
  font-size: 18px;
}

.rec-item span {
  flex: 1;
  font-size: 13px;
  color: #606266;
}

/* Rack U Detail */
.rack-u-detail {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.rack-u-detail h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.u-bars {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  max-height: 300px;
  overflow-y: auto;
}

.u-bar {
  width: 30px;
  height: 20px;
  background: #e4e7ed;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #909399;
  cursor: pointer;
}

.u-bar.occupied {
  background: #409eff;
  color: white;
}

.u-bar .u-number {
  font-size: 9px;
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