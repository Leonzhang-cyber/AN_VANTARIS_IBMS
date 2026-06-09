<template>
  <div class="airflow-analysis-container">
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
            <span class="loading-title">Loading Airflow Analysis</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">CFD Airflow Simulation & Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Airflow Analysis</span>
          <el-tag type="info" effect="dark" size="large">CFD Simulation</el-tag>
        </div>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><WindPower /></el-icon>
                <span>Total Airflow</span>
              </div>
              <div class="card-value">185,000 CFM</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" status="success" :format="() => 'Capacity: 220k CFM'" />
                <span class="status-text">CRAC + CRAH</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Airflow Efficiency</span>
              </div>
              <div class="card-value">78%</div>
              <div class="card-footer">
                <el-progress :percentage="78" :stroke-width="8" status="warning" :format="() => 'Target: 85%'" />
                <span class="status-text">CFM/kW Ratio</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Connection /></el-icon>
                <span>Airflow Distribution</span>
              </div>
              <div class="card-value">±15%</div>
              <div class="card-footer">
                <el-progress :percentage="70" :stroke-width="8" status="warning" :format="() => 'Target: ±10%'" />
                <span class="status-text">Uniformity Index</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Recirculation</span>
              </div>
              <div class="card-value">12%</div>
              <div class="card-footer">
                <el-progress :percentage="12" :stroke-width="8" status="exception" :format="() => 'Target: <5%'" />
                <span class="status-text">Hot Air Recirculation</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Main Airflow Visualization -->
      <div class="airflow-viz-section">
        <el-card class="viz-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Grid /></el-icon>
            <span>Airflow Vector Field</span>
            <div class="header-actions">
              <el-radio-group v-model="vizType" size="small">
                <el-radio-button label="vectors">Vector Field</el-radio-button>
                <el-radio-button label="streamlines">Streamlines</el-radio-button>
                <el-radio-button label="contour">Velocity Contour</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="playAnimation">Play Animation</el-button>
              <el-button size="small" @click="stopAnimation">Stop</el-button>
              <el-button size="small" type="primary" @click="runSimulation">Run CFD</el-button>
            </div>
          </div>
          <div class="viz-container">
            <div ref="airflowVectorChartRef" style="height: 500px"></div>
          </div>
          <div class="viz-legend">
            <span>Airflow Velocity:</span>
            <span class="legend-color" style="background: #3b82f6"></span>
            <span>0-0.5 m/s</span>
            <span class="legend-color" style="background: #10b981"></span>
            <span>0.5-1.0 m/s</span>
            <span class="legend-color" style="background: #f59e0b"></span>
            <span>1.0-2.0 m/s</span>
            <span class="legend-color" style="background: #ef4444"></span>
            <span>2.0-3.0 m/s</span>
            <span class="legend-color" style="background: #7c2d12"></span>
            <span>&gt;3.0 m/s</span>
          </div>
        </el-card>
      </div>

      <!-- Underfloor Airflow Distribution -->
      <div class="underfloor-section">
        <el-card class="underfloor-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Menu /></el-icon>
            <span>Underfloor Airflow Distribution</span>
            <div class="header-actions">
              <el-button size="small" @click="viewPressureMap">View Pressure Map</el-button>
              <el-button size="small" type="primary" @click="optimizeFloorTiles">Optimize Tiles</el-button>
            </div>
          </div>
          <div class="underfloor-container">
            <div ref="underfloorChartRef" style="height: 400px"></div>
          </div>
        </el-card>
      </div>

      <!-- Rack Airflow Metrics -->
      <div class="rack-airflow-section">
        <div class="section-header">
          <h3>Rack Airflow Metrics</h3>
          <div class="header-controls">
            <el-radio-group v-model="rackView" size="small">
              <el-radio-button label="grid">Grid View</el-radio-button>
              <el-radio-button label="list">List View</el-radio-button>
            </el-radio-group>
            <el-select v-model="rackFilter" placeholder="Filter by row" clearable size="small" style="width: 120px">
              <el-option label="Row A" value="A" />
              <el-option label="Row B" value="B" />
              <el-option label="Row C" value="C" />
              <el-option label="Row D" value="D" />
            </el-select>
          </div>
        </div>
        <div v-if="rackView === 'grid'">
          <div class="rack-airflow-grid">
            <div v-for="rack in filteredRackAirflow" :key="rack.id" class="rack-airflow-card" :class="getAirflowClass(rack.airflowEfficiency)">
              <div class="rack-header">
                <span class="rack-id">{{ rack.id }}</span>
                <el-tag :type="getAirflowTagType(rack.airflowEfficiency)" size="small">
                  {{ getAirflowStatus(rack.airflowEfficiency) }}
                </el-tag>
              </div>
              <div class="rack-metrics">
                <div class="metric">
                  <span>Intake CFM</span>
                  <strong>{{ rack.intakeCFM }}</strong>
                </div>
                <div class="metric">
                  <span>Exhaust CFM</span>
                  <strong>{{ rack.exhaustCFM }}</strong>
                </div>
                <div class="metric">
                  <span>ΔCFM</span>
                  <strong :style="{ color: rack.deltaCFM > 0 ? '#ef4444' : '#10b981' }">
                    {{ rack.deltaCFM > 0 ? '+' : '' }}{{ rack.deltaCFM }}
                  </strong>
                </div>
              </div>
              <div class="airflow-bar">
                <div class="bar-intake" :style="{ width: (rack.intakeCFM / 800) * 100 + '%' }"></div>
                <div class="bar-exhaust" :style="{ width: (rack.exhaustCFM / 800) * 100 + '%' }"></div>
              </div>
              <div class="rack-footer">
                <el-progress :percentage="rack.airflowEfficiency" :stroke-width="6" :color="getAirflowColor(rack.airflowEfficiency)" />
              </div>
            </div>
          </div>
        </div>
        <el-table :data="filteredRackAirflow" border v-else style="width: 100%">
          <el-table-column prop="id" label="Rack ID" width="100" />
          <el-table-column prop="row" label="Row" width="80" />
          <el-table-column prop="intakeCFM" label="Intake CFM" width="120" />
          <el-table-column prop="exhaustCFM" label="Exhaust CFM" width="120" />
          <el-table-column prop="deltaCFM" label="ΔCFM" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.deltaCFM > 0 ? '#ef4444' : '#10b981' }">
                {{ row.deltaCFM > 0 ? '+' : '' }}{{ row.deltaCFM }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="airflowEfficiency" label="Efficiency" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.airflowEfficiency" :stroke-width="8" :color="getAirflowColor(row.airflowEfficiency)" />
            </template>
          </el-table-column>
          <el-table-column label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="getAirflowTagType(row.airflowEfficiency)" size="small">
                {{ getAirflowStatus(row.airflowEfficiency) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Airflow Distribution Tab -->
          <el-tab-pane label="Airflow Distribution" name="distribution">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><PieChart /></el-icon>
                <span>Airflow Distribution Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="distributionChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="velocityProfileChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Bypass/Recirculation Tab -->
          <el-tab-pane label="Bypass & Recirculation" name="bypass">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Refresh /></el-icon>
                <span>Air Bypass & Recirculation Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="bypassChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="bypass-stats">
                    <div class="stat-card">
                      <div class="stat-title">Air Bypass</div>
                      <div class="stat-value-large">8.5%</div>
                      <el-progress :percentage="8.5" :stroke-width="12" status="exception" :format="() => 'Target: <5%'" />
                      <p>Air that bypasses IT equipment</p>
                    </div>
                    <div class="stat-card">
                      <div class="stat-title">Hot Air Recirculation</div>
                      <div class="stat-value-large">12%</div>
                      <el-progress :percentage="12" :stroke-width="12" status="exception" :format="() => 'Target: <5%'" />
                      <p>Hot exhaust mixing with cold supply</p>
                    </div>
                    <div class="recommendation-box">
                      <h4>Recommendations</h4>
                      <ul>
                        <li>Install blanking panels in empty U spaces</li>
                        <li>Seal cable cutouts under raised floor</li>
                        <li>Add brush seals at aisle ends</li>
                        <li>Implement hot aisle containment</li>
                      </ul>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Perforated Tile Analysis Tab -->
          <el-tab-pane label="Perforated Tiles" name="tiles">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Grid /></el-icon>
                <span>Perforated Tile Airflow Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="chart-container">
                    <div ref="tileChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="tile-stats">
                    <el-table :data="tileData" border size="small">
                      <el-table-column prop="location" label="Location" width="100" />
                      <el-table-column prop="cfm" label="CFM" width="80" />
                      <el-table-column prop="status" label="Status" width="100">
                        <template #default="{ row }">
                          <el-tag :type="row.cfm < 400 ? 'danger' : row.cfm > 700 ? 'warning' : 'success'" size="small">
                            {{ row.cfm < 400 ? 'Low' : row.cfm > 700 ? 'High' : 'Normal' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column label="Action" width="80">
                        <template #default="{ row }">
                          <el-button type="primary" link size="small" @click="adjustTile(row)">Adjust</el-button>
                        </template>
                      </el-table-column>
                    </el-table>
                    <div class="tile-recommendation">
                      <h4>Tile Optimization</h4>
                      <p>Recommended: Replace 25% open tiles with 35% open tiles in high-density areas</p>
                      <el-button type="primary" size="small" @click="optimizeTiles">Optimize Now</el-button>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- CFD Simulation Tab -->
          <el-tab-pane label="CFD Simulation" name="cfd">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Cpu /></el-icon>
                <span>CFD Simulation Results</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="cfdTempChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="cfdVelocityChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
              <div class="cfd-controls">
                <el-button type="primary" @click="runNewCFD">Run New CFD Simulation</el-button>
                <el-button @click="exportCFDResults">Export Results</el-button>
              </div>
            </div>
          </el-tab-pane>

          <!-- Improvement Opportunities Tab -->
          <el-tab-pane label="Improvements" name="improvements">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>Airflow Improvement Opportunities</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="improvements" border style="width: 100%">
                    <el-table-column prop="area" label="Area" width="150" />
                    <el-table-column prop="issue" label="Issue" />
                    <el-table-column prop="recommendation" label="Recommendation" />
                    <el-table-column prop="impact" label="Expected Impact" width="120" />
                    <el-table-column prop="priority" label="Priority" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.priority === 'High' ? 'danger' : row.priority === 'Medium' ? 'warning' : 'info'" size="small">
                          {{ row.priority }}
                        </el-tag>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="8">
                  <div class="improvement-summary">
                    <h4>Total Improvement Potential</h4>
                    <div class="potential-value">15.5%</div>
                    <div class="potential-label">Airflow Efficiency Gain</div>
                    <el-progress :percentage="15.5" :stroke-width="12" status="success" />
                    <div class="potential-details">
                      <div class="detail-item">
                        <span>Energy Savings:</span>
                        <strong>185,000 kWh/year</strong>
                      </div>
                      <div class="detail-item">
                        <span>PUE Reduction:</span>
                        <strong>0.06</strong>
                      </div>
                      <div class="detail-item">
                        <span>Cost Savings:</span>
                        <strong>$22,000/year</strong>
                      </div>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="generateActionPlan">
                      Generate Action Plan
                    </el-button>
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
          Run Full Airflow Analysis
        </el-button>
        <el-button size="large" @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Analysis Report
        </el-button>
        <el-button size="large" @click="scheduleAudit">
          <el-icon><Calendar /></el-icon>
          Schedule Airflow Audit
        </el-button>
      </div>
    </template>

    <!-- Tile Adjustment Dialog -->
    <el-dialog v-model="tileDialogVisible" title="Adjust Perforated Tile" width="450px">
      <el-form>
        <el-form-item label="Tile Location">
          <span>{{ selectedTile?.location }}</span>
        </el-form-item>
        <el-form-item label="Current CFM">
          <span>{{ selectedTile?.cfm }} CFM</span>
        </el-form-item>
        <el-form-item label="New CFM Target">
          <el-slider v-model="targetCFM" :min="300" :max="800" :step="10" show-input />
        </el-form-item>
        <el-form-item label="Tile Type">
          <el-select v-model="tileType" placeholder="Select tile type">
            <el-option label="25% Open" value="25" />
            <el-option label="35% Open" value="35" />
            <el-option label="45% Open" value="45" />
            <el-option label="56% Open" value="56" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tileDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTileAdjustment">Apply</el-button>
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
const loadingMessage = ref('Initializing airflow analysis...')

const loadingMessages = [
  'Initializing airflow analysis...',
  'Loading CFD simulation data...',
  'Processing airflow vectors...',
  'Analyzing distribution patterns...',
  'Detecting recirculation zones...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('distribution')
const vizType = ref('vectors')
const rackView = ref('grid')
const rackFilter = ref('')
const tileDialogVisible = ref(false)
const selectedTile = ref<any>(null)
const targetCFM = ref(500)
const tileType = ref('35')

// Animation state
let animationInterval: ReturnType<typeof setInterval>
let isAnimating = ref(false)

// Rack airflow data
const rackAirflow = ref([
  { id: 'A01', row: 'A', intakeCFM: 520, exhaustCFM: 540, deltaCFM: 20, airflowEfficiency: 85 },
  { id: 'A02', row: 'A', intakeCFM: 480, exhaustCFM: 510, deltaCFM: 30, airflowEfficiency: 78 },
  { id: 'A03', row: 'A', intakeCFM: 650, exhaustCFM: 680, deltaCFM: 30, airflowEfficiency: 72 },
  { id: 'A04', row: 'A', intakeCFM: 720, exhaustCFM: 750, deltaCFM: 30, airflowEfficiency: 65 },
  { id: 'B01', row: 'B', intakeCFM: 500, exhaustCFM: 520, deltaCFM: 20, airflowEfficiency: 82 },
  { id: 'B02', row: 'B', intakeCFM: 490, exhaustCFM: 515, deltaCFM: 25, airflowEfficiency: 80 },
  { id: 'B03', row: 'B', intakeCFM: 780, exhaustCFM: 820, deltaCFM: 40, airflowEfficiency: 58 },
  { id: 'B04', row: 'B', intakeCFM: 550, exhaustCFM: 570, deltaCFM: 20, airflowEfficiency: 75 },
  { id: 'C01', row: 'C', intakeCFM: 510, exhaustCFM: 530, deltaCFM: 20, airflowEfficiency: 84 },
  { id: 'C02', row: 'C', intakeCFM: 470, exhaustCFM: 495, deltaCFM: 25, airflowEfficiency: 79 },
  { id: 'D01', row: 'D', intakeCFM: 530, exhaustCFM: 550, deltaCFM: 20, airflowEfficiency: 83 },
  { id: 'D02', row: 'D', intakeCFM: 490, exhaustCFM: 515, deltaCFM: 25, airflowEfficiency: 76 }
])

// Filtered rack airflow
const filteredRackAirflow = computed(() => {
  if (!rackFilter.value) return rackAirflow.value
  return rackAirflow.value.filter(r => r.row === rackFilter.value)
})

// Tile data
const tileData = ref([
  { location: 'A01', cfm: 450, status: 'Normal' },
  { location: 'A02', cfm: 380, status: 'Low' },
  { location: 'A03', cfm: 620, status: 'High' },
  { location: 'B01', cfm: 480, status: 'Normal' },
  { location: 'B02', cfm: 350, status: 'Low' },
  { location: 'B03', cfm: 720, status: 'High' }
])

// Improvements data
const improvements = ref([
  { area: 'Row A', issue: 'Uneven airflow distribution', recommendation: 'Replace perforated tiles with higher open area', impact: '+8% efficiency', priority: 'High' },
  { area: 'Row B', issue: 'Hot air recirculation', recommendation: 'Install hot aisle containment', impact: '-3°C hotspot', priority: 'High' },
  { area: 'Underfloor', issue: 'Cable cutouts causing bypass', recommendation: 'Seal all cable openings', impact: '+5% airflow', priority: 'Medium' },
  { area: 'Rack A04', issue: 'High density causing local heating', recommendation: 'Add spot cooling', impact: '-2°C', priority: 'Medium' }
])

// Chart refs
const airflowVectorChartRef = ref<HTMLElement | null>(null)
const underfloorChartRef = ref<HTMLElement | null>(null)
const distributionChartRef = ref<HTMLElement | null>(null)
const velocityProfileChartRef = ref<HTMLElement | null>(null)
const bypassChartRef = ref<HTMLElement | null>(null)
const tileChartRef = ref<HTMLElement | null>(null)
const cfdTempChartRef = ref<HTMLElement | null>(null)
const cfdVelocityChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Helper functions
const getAirflowClass = (efficiency: number) => {
  if (efficiency >= 80) return 'efficiency-good'
  if (efficiency >= 70) return 'efficiency-warning'
  return 'efficiency-critical'
}

const getAirflowTagType = (efficiency: number) => {
  if (efficiency >= 80) return 'success'
  if (efficiency >= 70) return 'warning'
  return 'danger'
}

const getAirflowStatus = (efficiency: number) => {
  if (efficiency >= 80) return 'Optimal'
  if (efficiency >= 70) return 'Warning'
  return 'Critical'
}

const getAirflowColor = (efficiency: number) => {
  if (efficiency >= 80) return '#67c23a'
  if (efficiency >= 70) return '#f59e0b'
  return '#ef4444'
}

const playAnimation = () => {
  if (isAnimating.value) return
  isAnimating.value = true
  ElMessage.success('Airflow animation started')

  let step = 0
  animationInterval = setInterval(() => {
    step++
    if (step > 20) {
      stopAnimation()
    }
  }, 200)
}

const stopAnimation = () => {
  if (animationInterval) {
    clearInterval(animationInterval)
    isAnimating.value = false
    ElMessage.info('Animation stopped')
  }
}

const runSimulation = () => {
  ElMessage.success('CFD simulation started. Results will be available in 2-3 minutes.')
}

const viewPressureMap = () => {
  ElMessage.info('Underfloor pressure map view coming soon')
}

const optimizeFloorTiles = () => {
  ElMessage.success('Floor tile optimization analysis completed. 12 tiles recommended for replacement.')
}

const adjustTile = (tile: any) => {
  selectedTile.value = tile
  targetCFM.value = tile.cfm
  tileDialogVisible.value = true
}

const saveTileAdjustment = () => {
  if (selectedTile.value) {
    selectedTile.value.cfm = targetCFM.value
    ElMessage.success(`Tile ${selectedTile.value.location} adjusted to ${targetCFM.value} CFM`)
  }
  tileDialogVisible.value = false
}

const optimizeTiles = () => {
  ElMessage.success('Tile optimization plan generated. 8 tiles recommended for replacement.')
}

const runNewCFD = () => {
  ElMessage.success('New CFD simulation started')
}

const exportCFDResults = () => {
  ElMessage.success('CFD results export started')
}

const runFullAnalysis = () => {
  ElMessage.success('Full airflow analysis started')
}

const exportReport = () => {
  ElMessage.success('Airflow analysis report export started')
}

const scheduleAudit = () => {
  ElMessage.info('Airflow audit scheduling interface will open')
}

const generateActionPlan = () => {
  ElMessage.success('Action plan generated')
}

// Chart initialization
const initAirflowVectorChart = () => {
  if (airflowVectorChartRef.value) {
    const chart = echarts.init(airflowVectorChartRef.value)

    // Generate vector field data
    const vectorData: any[] = []
    for (let i = 0; i < 20; i++) {
      for (let j = 0; j < 30; j++) {
        const x = j / 30
        const y = i / 20
        let u = Math.sin(x * Math.PI * 2) * 0.5
        let v = Math.cos(y * Math.PI) * 0.3
        // Add vortex effect in center
        const cx = 0.5, cy = 0.5
        const dx = x - cx, dy = y - cy
        const r = Math.sqrt(dx * dx + dy * dy)
        if (r < 0.3) {
          u += -dy * 0.8
          v += dx * 0.8
        }
        vectorData.push([j, i, u, v])
      }
    }

    chart.setOption({
      tooltip: { trigger: 'item' },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => i + 1), name: 'Rack Position', axisLabel: { interval: 5 } },
      yAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String.fromCharCode(65 + i)), name: 'Row' },
      visualMap: { min: 0, max: 2, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] } },
      series: [{
        type: 'scatter', data: vectorData.map(d => [d[0], d[1]]),
        symbolSize: 8,
        itemStyle: { color: (params: any) => {
            const idx = params.dataIndex
            const speed = Math.sqrt(vectorData[idx][2] ** 2 + vectorData[idx][3] ** 2)
            if (speed < 0.5) return '#3b82f6'
            if (speed < 1.0) return '#10b981'
            if (speed < 1.5) return '#f59e0b'
            return '#ef4444'
          } }
      }]
    })
    chartInstances.push(chart)
  }
}

const initUnderfloorChart = () => {
  if (underfloorChartRef.value) {
    const chart = echarts.init(underfloorChartRef.value)
    const data: any[] = []
    for (let i = 0; i < 15; i++) {
      for (let j = 0; j < 20; j++) {
        let pressure = 50 + Math.random() * 30
        // Create pressure variations
        if ((i === 5 && j === 8) || (i === 6 && j === 9)) pressure = 35
        if ((i === 10 && j === 12) || (i === 11 && j === 11)) pressure = 75
        data.push([j, i, pressure])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Pressure: ${params.data[2].toFixed(0)} Pa` },
      xAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => i + 1), name: 'Tile Position' },
      yAxis: { type: 'category', data: Array.from({ length: 15 }, (_, i) => String.fromCharCode(65 + i)), name: 'Row' },
      visualMap: { min: 30, max: 80, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false } }]
    })
    chartInstances.push(chart)
  }
}

const initDistributionChart = () => {
  if (distributionChartRef.value) {
    const chart = echarts.init(distributionChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Cold Aisle', 'Hot Aisle'] },
      xAxis: { type: 'category', data: ['Row A', 'Row B', 'Row C', 'Row D'] },
      yAxis: { type: 'value', name: 'Airflow (CFM)' },
      series: [
        { name: 'Cold Aisle', type: 'bar', data: [1850, 1920, 1780, 1900], itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Hot Aisle', type: 'bar', data: [1650, 1720, 1580, 1700], itemStyle: { color: '#ef4444', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initVelocityProfileChart = () => {
  if (velocityProfileChartRef.value) {
    const chart = echarts.init(velocityProfileChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Bottom', '1/4 Height', '1/2 Height', '3/4 Height', 'Top'] },
      yAxis: { type: 'value', name: 'Velocity (m/s)' },
      series: [{
        type: 'line', data: [0.8, 1.2, 1.5, 1.4, 1.1],
        smooth: true, lineStyle: { color: '#409eff', width: 3 }, areaStyle: { opacity: 0.3 },
        label: { show: true, position: 'top' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initBypassChart = () => {
  if (bypassChartRef.value) {
    const chart = echarts.init(bypassChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        type: 'pie', radius: '55%',
        data: [
          { value: 65.5, name: 'IT Equipment', itemStyle: { color: '#67c23a' } },
          { value: 12, name: 'Hot Recirculation', itemStyle: { color: '#ef4444' } },
          { value: 8.5, name: 'Air Bypass', itemStyle: { color: '#f59e0b' } },
          { value: 14, name: 'Other Losses', itemStyle: { color: '#909399' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initTileChart = () => {
  if (tileChartRef.value) {
    const chart = echarts.init(tileChartRef.value)
    const tilePositions = ['A01', 'A02', 'A03', 'B01', 'B02', 'B03', 'C01', 'C02', 'D01', 'D02']
    const tileCFMs = [450, 380, 620, 480, 350, 720, 520, 410, 490, 380]

    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: tilePositions, axisLabel: { rotate: 45 } },
      yAxis: { type: 'value', name: 'CFM', min: 300, max: 800 },
      series: [{
        type: 'bar', data: tileCFMs,
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => {
            const val = tileCFMs[params.dataIndex]
            if (val < 400) return '#ef4444'
            if (val > 700) return '#f59e0b'
            return '#67c23a'
          }
        },
        label: { show: true, position: 'top', formatter: '{c} CFM' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initCFDTempChart = () => {
  if (cfdTempChartRef.value) {
    const chart = echarts.init(cfdTempChartRef.value)
    const data: any[] = []
    for (let i = 0; i < 20; i++) {
      for (let j = 0; j < 30; j++) {
        let temp = 22 + Math.random() * 4
        if ((i === 5 && j === 8) || (i === 6 && j === 9)) temp = 26
        data.push([j, i, temp])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Temperature: ${params.data[2].toFixed(1)}°C` },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => i + 1), axisLabel: { interval: 5 } },
      yAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String.fromCharCode(65 + i)) },
      visualMap: { min: 20, max: 28, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false } }]
    })
    chartInstances.push(chart)
  }
}

const initCFDVelocityChart = () => {
  if (cfdVelocityChartRef.value) {
    const chart = echarts.init(cfdVelocityChartRef.value)
    const data: any[] = []
    for (let i = 0; i < 20; i++) {
      for (let j = 0; j < 30; j++) {
        let velocity = 0.5 + Math.random() * 2
        data.push([j, i, velocity])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Velocity: ${params.data[2].toFixed(2)} m/s` },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => i + 1), axisLabel: { interval: 5 } },
      yAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String.fromCharCode(65 + i)) },
      visualMap: { min: 0, max: 3, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false } }]
    })
    chartInstances.push(chart)
  }
}

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

// Watch for viz type changes
const refreshViz = () => {
  initAirflowVectorChart()
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
        initAirflowVectorChart()
        initUnderfloorChart()
        initDistributionChart()
        initVelocityProfileChart()
        initBypassChart()
        initTileChart()
        initCFDTempChart()
        initCFDVelocityChart()
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
.airflow-analysis-container {
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
  border-top-color: #3b82f6;
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
  background: linear-gradient(90deg, #3b82f6, #10b981, #f59e0b);
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
.airflow-analysis-container {
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

/* Airflow Visualization */
.airflow-viz-section {
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
  flex-wrap: wrap;
}

.viz-container {
  min-height: 500px;
}

.viz-legend {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 12px;
  color: #909399;
  flex-wrap: wrap;
}

.legend-color {
  width: 20px;
  height: 12px;
  border-radius: 4px;
  display: inline-block;
}

/* Underfloor Section */
.underfloor-section {
  margin-bottom: 24px;
}

.underfloor-card {
  border-radius: 12px;
}

.underfloor-container {
  min-height: 400px;
}

/* Rack Airflow Section */
.rack-airflow-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
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
  align-items: center;
  flex-wrap: wrap;
}

.rack-airflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.rack-airflow-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  transition: transform 0.2s;
  border-left: 4px solid;
}

.rack-airflow-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.rack-airflow-card.efficiency-good {
  border-left-color: #67c23a;
}

.rack-airflow-card.efficiency-warning {
  border-left-color: #f59e0b;
}

.rack-airflow-card.efficiency-critical {
  border-left-color: #ef4444;
}

.rack-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rack-id {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.rack-metrics {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.metric {
  text-align: center;
}

.metric span {
  display: block;
  font-size: 11px;
  color: #909399;
}

.metric strong {
  font-size: 14px;
  color: #303133;
}

.airflow-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
  background: #e4e7ed;
}

.bar-intake {
  background: #3b82f6;
  transition: width 0.3s;
}

.bar-exhaust {
  background: #ef4444;
  transition: width 0.3s;
}

.rack-footer {
  margin-top: 8px;
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
  color: #3b82f6;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Bypass Stats */
.bypass-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value-large {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 12px;
}

.recommendation-box {
  background: #ecf5ff;
  border-radius: 8px;
  padding: 16px;
}

.recommendation-box h4 {
  margin: 0 0 12px 0;
  color: #303133;
}

.recommendation-box ul {
  margin: 0;
  padding-left: 20px;
}

.recommendation-box li {
  margin: 8px 0;
  font-size: 13px;
  color: #606266;
}

/* Tile Stats */
.tile-stats {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
}

.tile-recommendation {
  margin-top: 20px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  text-align: center;
}

.tile-recommendation h4 {
  margin: 0 0 8px 0;
  color: #303133;
}

.tile-recommendation p {
  font-size: 12px;
  color: #909399;
  margin-bottom: 12px;
}

/* CFD Controls */
.cfd-controls {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Improvement Summary */
.improvement-summary {
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  height: 100%;
}

.improvement-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.potential-value {
  font-size: 48px;
  font-weight: 700;
  color: #409eff;
  margin: 16px 0;
}

.potential-label {
  font-size: 13px;
  color: #909399;
  margin-bottom: 16px;
}

.potential-details {
  margin: 20px 0;
  text-align: left;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e4e7ed;
}

.detail-item strong {
  color: #409eff;
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