<template>
  <div class="containment-analysis-container">
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
            <span class="loading-title">Loading Containment Analysis</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Hot/Cold Aisle Containment Analysis</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">Containment Analysis</span>
          <el-tag type="warning" effect="dark" size="large">Hot/Cold Aisle Containment</el-tag>
        </div>
      </div>

      <!-- Alert Banner -->
      <div v-if="leakageRate > 15" class="alert-banner critical">
        <el-icon><WarningFilled /></el-icon>
        <span>High containment leakage detected ({{ leakageRate }}%)! Immediate action required.</span>
        <el-button size="small" type="danger" @click="viewLeakagePoints">View Leak Points</el-button>
      </div>
      <div v-else-if="leakageRate > 8" class="alert-banner warning">
        <el-icon><Warning /></el-icon>
        <span>Moderate containment leakage ({{ leakageRate }}%). Optimization recommended.</span>
        <el-button size="small" type="warning" @click="viewLeakagePoints">Review Leaks</el-button>
      </div>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Containment Type</span>
              </div>
              <div class="card-value">Hot Aisle</div>
              <div class="card-footer">
                <el-progress :percentage="100" :stroke-width="8" status="success" />
                <span class="status-text">Fully Enclosed</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Containment Efficiency</span>
              </div>
              <div class="card-value">{{ containmentEfficiency }}%</div>
              <div class="card-footer">
                <el-progress :percentage="containmentEfficiency" :stroke-width="8" :color="efficiencyColor" />
                <span class="status-text">Target: >95%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Warning /></el-icon>
                <span>Leakage Rate</span>
              </div>
              <div class="card-value">{{ leakageRate }}%</div>
              <div class="card-footer">
                <el-progress :percentage="leakageRate" :stroke-width="8" :color="leakageColor" :format="() => `${leakageRate}%`" />
                <span class="status-text">Target: <5%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Temperature Delta</span>
              </div>
              <div class="card-value">{{ tempDelta }}°C</div>
              <div class="card-footer">
                <el-progress :percentage="75" :stroke-width="8" status="success" :format="() => 'Cold-Hot Delta'" />
                <span class="status-text">Improved by 4°C</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Containment 3D Visualization -->
      <div class="containment-viz-section">
        <el-card class="viz-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Grid /></el-icon>
            <span>Containment 3D Visualization</span>
            <div class="header-actions">
              <el-radio-group v-model="vizLayer" size="small">
                <el-radio-button label="3d">3D View</el-radio-button>
                <el-radio-button label="top">Top View</el-radio-button>
                <el-radio-button label="side">Side View</el-radio-button>
              </el-radio-group>
              <el-button size="small" @click="rotateView">Rotate</el-button>
              <el-button size="small" @click="resetView">Reset</el-button>
              <el-button size="small" type="primary" @click="exportModel">Export Model</el-button>
            </div>
          </div>
          <div class="viz-container">
            <div ref="containment3DChartRef" style="height: 500px"></div>
          </div>
        </el-card>
      </div>

      <!-- Leakage Detection Map -->
      <div class="leakage-section">
        <el-card class="leakage-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><Warning /></el-icon>
            <span>Leakage Detection Map</span>
            <div class="header-actions">
              <el-button size="small" @click="refreshLeakMap">Refresh</el-button>
              <el-button size="small" type="primary" @click="runLeakDetection">Run Leak Detection</el-button>
            </div>
          </div>
          <div class="leakage-container">
            <div ref="leakageMapChartRef" style="height: 400px"></div>
          </div>
        </el-card>
      </div>

      <!-- Leak Points List -->
      <div class="leakpoints-section">
        <div class="section-header">
          <h3>Identified Leak Points</h3>
          <div class="header-controls">
            <el-input v-model="leakSearch" placeholder="Search leaks..." prefix-icon="Search" style="width: 250px" clearable />
            <el-select v-model="leakSeverityFilter" placeholder="Severity" clearable style="width: 120px">
              <el-option label="Critical" value="Critical" />
              <el-option label="High" value="High" />
              <el-option label="Medium" value="Medium" />
              <el-option label="Low" value="Low" />
            </el-select>
            <el-button type="primary" @click="exportLeakReport">Export Report</el-button>
          </div>
        </div>
        <el-table :data="filteredLeakPoints" border style="width: 100%">
          <el-table-column prop="location" label="Location" width="120" />
          <el-table-column prop="type" label="Leak Type" width="140" />
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">
                {{ row.severity }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="leakageRate" label="Leakage Rate" width="120">
            <template #default="{ row }">
              <span :style="{ color: getLeakageColor(row.leakageRate) }">{{ row.leakageRate }}%</span>
            </template>
          </el-table-column>
          <el-table-column prop="tempImpact" label="Temp Impact" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.tempImpact > 2 ? '#ef4444' : '#f59e0b' }">+{{ row.tempImpact }}°C</span>
            </template>
          </el-table-column>
          <el-table-column prop="recommendation" label="Recommendation" />
          <el-table-column label="Actions" width="120">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewLeakDetails(row)">Details</el-button>
              <el-button type="success" link size="small" @click="fixLeak(row)">Fix</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Performance Metrics Tab -->
          <el-tab-pane label="Performance Metrics" name="metrics">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Containment Performance Metrics</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="efficiencyTrendChartRef" style="height: 350px"></div>
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

          <!-- Pressure Differential Tab -->
          <el-tab-pane label="Pressure Differential" name="pressure">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Gauge /></el-icon>
                <span>Pressure Differential Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="pressureDiffChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="pressure-stats">
                    <div class="stat-card">
                      <div class="stat-title">Hot Aisle Pressure</div>
                      <div class="stat-value">{{ hotAislePressure }} Pa</div>
                      <el-progress :percentage="65" :stroke-width="8" :format="() => 'Target: 5-10 Pa'" />
                    </div>
                    <div class="stat-card">
                      <div class="stat-title">Cold Aisle Pressure</div>
                      <div class="stat-value">{{ coldAislePressure }} Pa</div>
                      <el-progress :percentage="40" :stroke-width="8" :format="() => 'Target: 2-5 Pa'" />
                    </div>
                    <div class="stat-card">
                      <div class="stat-title">Pressure Differential</div>
                      <div class="stat-value">{{ pressureDiff }} Pa</div>
                      <el-progress :percentage="70" :stroke-width="8" :format="() => 'Ideal: 3-8 Pa'" />
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Airflow Bypass Tab -->
          <el-tab-pane label="Airflow Bypass" name="bypass">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Refresh /></el-icon>
                <span>Airflow Bypass Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="bypassChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="bypass-summary">
                    <h4>Bypass Sources</h4>
                    <div class="bypass-item">
                      <span>Missing Blanking Panels</span>
                      <el-progress :percentage="35" :stroke-width="8" :format="() => '35%'" />
                    </div>
                    <div class="bypass-item">
                      <span>Cable Cutouts</span>
                      <el-progress :percentage="28" :stroke-width="8" :format="() => '28%'" />
                    </div>
                    <div class="bypass-item">
                      <span>Aisle End Gaps</span>
                      <el-progress :percentage="22" :stroke-width="8" :format="() => '22%'" />
                    </div>
                    <div class="bypass-item">
                      <span>Underfloor Leaks</span>
                      <el-progress :percentage="15" :stroke-width="8" :format="() => '15%'" />
                    </div>
                    <div class="bypass-total">
                      <span>Total Bypass Airflow</span>
                      <strong>{{ totalBypass }} CFM ({{ bypassPercentage }}%)</strong>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Retrofit Recommendations Tab -->
          <el-tab-pane label="Retrofit Recommendations" name="retrofit">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Setting /></el-icon>
                <span>Containment Retrofit Recommendations</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="retrofitRecommendations" border style="width: 100%">
                    <el-table-column prop="area" label="Area" width="120" />
                    <el-table-column prop="recommendation" label="Recommendation" />
                    <el-table-column prop="cost" label="Cost Estimate" width="120" />
                    <el-table-column prop="savings" label="Expected Savings" width="120" />
                    <el-table-column prop="roi" label="ROI" width="100" />
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
                  <div class="retrofit-summary">
                    <h4>Investment Summary</h4>
                    <div class="investment-item">
                      <span>Total Estimated Cost</span>
                      <strong>${{ totalCost }}K</strong>
                    </div>
                    <div class="investment-item">
                      <span>Annual Energy Savings</span>
                      <strong>{{ annualSavings }} kWh</strong>
                    </div>
                    <div class="investment-item">
                      <span>Payback Period</span>
                      <strong>{{ paybackPeriod }} months</strong>
                    </div>
                    <div class="investment-item">
                      <span>PUE Improvement</span>
                      <strong>-{{ pueImprovement }}</strong>
                    </div>
                    <el-button type="primary" style="width: 100%; margin-top: 16px" @click="generateRetrofitPlan">
                      Generate Retrofit Plan
                    </el-button>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Before/After Comparison Tab -->
          <el-tab-pane label="Before/After Comparison" name="comparison">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Containment Before vs After</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="beforeAfterChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="comparison-stats">
                    <div class="comparison-item">
                      <span>Containment Efficiency</span>
                      <div class="comparison-bars">
                        <span class="before">Before: 78%</span>
                        <el-progress :percentage="78" :stroke-width="8" status="exception" />
                        <span class="after">After: 94%</span>
                        <el-progress :percentage="94" :stroke-width="8" status="success" />
                      </div>
                    </div>
                    <div class="comparison-item">
                      <span>Leakage Rate</span>
                      <div class="comparison-bars">
                        <span class="before">Before: 22%</span>
                        <el-progress :percentage="22" :stroke-width="8" status="exception" />
                        <span class="after">After: 6%</span>
                        <el-progress :percentage="6" :stroke-width="8" status="success" />
                      </div>
                    </div>
                    <div class="comparison-item">
                      <span>Max Hotspot Temp</span>
                      <div class="comparison-bars">
                        <span class="before">Before: 28.5°C</span>
                        <el-progress :percentage="95" :stroke-width="8" status="exception" :format="() => '28.5°C'" />
                        <span class="after">After: 24.2°C</span>
                        <el-progress :percentage="80" :stroke-width="8" status="success" :format="() => '24.2°C'" />
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Reports Tab -->
          <el-tab-pane label="Reports" name="reports">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>Containment Reports</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8" v-for="report in containmentReports" :key="report.id">
                  <div class="report-card" @click="downloadReport(report)">
                    <el-icon :size="40"><component :is="report.icon" /></el-icon>
                    <h4>{{ report.title }}</h4>
                    <p>{{ report.description }}</p>
                    <div class="report-meta">
                      <span>{{ report.date }}</span>
                      <el-tag size="small">{{ report.format }}</el-tag>
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
          Run Full Containment Analysis
        </el-button>
        <el-button size="large" @click="scheduleRetrofit">
          <el-icon><Tools /></el-icon>
          Schedule Retrofit
        </el-button>
        <el-button size="large" @click="generateAuditReport">
          <el-icon><Document /></el-icon>
          Generate Audit Report
        </el-button>
      </div>
    </template>

    <!-- Leak Details Dialog -->
    <el-dialog v-model="leakDialogVisible" :title="`Leak Details - ${selectedLeak?.location}`" width="500px">
      <el-descriptions :column="2" border v-if="selectedLeak">
        <el-descriptions-item label="Location">{{ selectedLeak.location }}</el-descriptions-item>
        <el-descriptions-item label="Leak Type">{{ selectedLeak.type }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityType(selectedLeak.severity)">{{ selectedLeak.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Leakage Rate">{{ selectedLeak.leakageRate }}%</el-descriptions-item>
        <el-descriptions-item label="Temp Impact">+{{ selectedLeak.tempImpact }}°C</el-descriptions-item>
        <el-descriptions-item label="Detected At">{{ selectedLeak.detectedAt || '2024-12-18 10:30:00' }}</el-descriptions-item>
        <el-descriptions-item label="Recommendation" :span="2">{{ selectedLeak.recommendation }}</el-descriptions-item>
        <el-descriptions-item label="Materials Needed" :span="2">{{ selectedLeak.materials || 'Brush seals, foam tape' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="leakDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="fixLeak(selectedLeak)">Mark as Fixed</el-button>
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
const loadingMessage = ref('Loading containment analysis...')

const loadingMessages = [
  'Loading containment analysis...',
  'Scanning for air leaks...',
  'Analyzing containment efficiency...',
  'Calculating pressure differentials...',
  'Generating retrofit recommendations...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('metrics')
const vizLayer = ref('3d')
const leakSearch = ref('')
const leakSeverityFilter = ref('')
const leakDialogVisible = ref(false)
const selectedLeak = ref<any>(null)

// Metrics
const containmentEfficiency = ref(86)
const leakageRate = ref(14)
const tempDelta = ref(8.5)
const hotAislePressure = ref(7.2)
const coldAislePressure = ref(3.5)
const pressureDiff = computed(() => (hotAislePressure.value - coldAislePressure.value).toFixed(1))
const totalBypass = ref(18500)
const bypassPercentage = ref(12.5)

// Colors
const efficiencyColor = computed(() => {
  if (containmentEfficiency.value >= 90) return '#67c23a'
  if (containmentEfficiency.value >= 80) return '#f59e0b'
  return '#ef4444'
})

const leakageColor = computed(() => {
  if (leakageRate.value <= 5) return '#67c23a'
  if (leakageRate.value <= 10) return '#f59e0b'
  return '#ef4444'
})

// Leak points data
const leakPoints = ref([
  { id: 1, location: 'Aisle A - North End', type: 'Aisle End Gap', severity: 'Critical', leakageRate: 18, tempImpact: 3.5, recommendation: 'Install brush seals on both ends', materials: 'Brush seals, mounting hardware', detectedAt: '2024-12-18 08:30' },
  { id: 2, location: 'Rack A04', type: 'Missing Blanking Panel', severity: 'High', leakageRate: 12, tempImpact: 2.8, recommendation: 'Install blanking panels in empty U spaces', materials: '1U blanking panels (8 pcs)', detectedAt: '2024-12-18 09:15' },
  { id: 3, location: 'Rack B03', type: 'Cable Cutout', severity: 'High', leakageRate: 10, tempImpact: 2.2, recommendation: 'Seal cable openings with brush strips', materials: 'Brush grommets', detectedAt: '2024-12-18 10:00' },
  { id: 4, location: 'Rack C07', type: 'Missing Blanking Panel', severity: 'Medium', leakageRate: 8, tempImpact: 1.8, recommendation: 'Install blanking panels', materials: '2U blanking panels (4 pcs)', detectedAt: '2024-12-18 10:45' },
  { id: 5, location: 'Aisle B - South End', type: 'Aisle End Gap', severity: 'Medium', leakageRate: 7, tempImpact: 1.5, recommendation: 'Install door seals', materials: 'Door seals, adhesive', detectedAt: '2024-12-18 11:30' },
  { id: 6, location: 'Underfloor - Zone A', type: 'Cable Cutout', severity: 'Low', leakageRate: 4, tempImpact: 0.8, recommendation: 'Seal floor openings', materials: 'Grommets, firestop putty', detectedAt: '2024-12-18 12:15' }
])

// Filtered leak points
const filteredLeakPoints = computed(() => {
  let data = leakPoints.value
  if (leakSearch.value) {
    data = data.filter(l => l.location.toLowerCase().includes(leakSearch.value.toLowerCase()))
  }
  if (leakSeverityFilter.value) {
    data = data.filter(l => l.severity === leakSeverityFilter.value)
  }
  return data
})

// Retrofit recommendations
const retrofitRecommendations = ref([
  { area: 'Aisle Ends', recommendation: 'Install brush seals on all aisle ends', cost: '$2,500', savings: '45,000 kWh/year', roi: '4 months', priority: 'High' },
  { area: 'Rack Gaps', recommendation: 'Add missing blanking panels', cost: '$1,200', savings: '28,000 kWh/year', roi: '3 months', priority: 'High' },
  { area: 'Cable Cutouts', recommendation: 'Seal all cable openings', cost: '$800', savings: '18,000 kWh/year', roi: '5 months', priority: 'Medium' },
  { area: 'Underfloor', recommendation: 'Seal raised floor leaks', cost: '$1,500', savings: '15,000 kWh/year', roi: '6 months', priority: 'Medium' }
])

// Financial summary
const totalCost = ref(6.0)
const annualSavings = ref(106000)
const paybackPeriod = ref(4.2)
const pueImprovement = ref(0.08)

// Containment reports
const containmentReports = ref([
  { id: 1, title: 'Containment Audit Report', description: 'Complete containment efficiency analysis', icon: 'DataAnalysis', format: 'PDF', date: '2024-12-01' },
  { id: 2, title: 'Leak Detection Summary', description: 'Identified leak points and recommendations', icon: 'Warning', format: 'PDF', date: '2024-12-01' },
  { id: 3, title: 'Retrofit ROI Analysis', description: 'Cost-benefit analysis for containment upgrades', icon: 'TrendCharts', format: 'Excel', date: '2024-12-01' }
])

// Chart refs
const containment3DChartRef = ref<HTMLElement | null>(null)
const leakageMapChartRef = ref<HTMLElement | null>(null)
const efficiencyTrendChartRef = ref<HTMLElement | null>(null)
const tempDistributionChartRef = ref<HTMLElement | null>(null)
const pressureDiffChartRef = ref<HTMLElement | null>(null)
const bypassChartRef = ref<HTMLElement | null>(null)
const beforeAfterChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Helper functions
const getSeverityType = (severity: string) => {
  if (severity === 'Critical') return 'danger'
  if (severity === 'High') return 'danger'
  if (severity === 'Medium') return 'warning'
  return 'info'
}

const getLeakageColor = (rate: number) => {
  if (rate >= 15) return '#ef4444'
  if (rate >= 8) return '#f59e0b'
  return '#67c23a'
}

const viewLeakagePoints = () => {
  activeTab.value = 'metrics'
  ElMessage.info('Opening leakage detection map')
}

const refreshLeakMap = () => {
  initLeakageMapChart()
  ElMessage.success('Leak map refreshed')
}

const runLeakDetection = () => {
  ElMessage.success('Leak detection scan started. Results will be available in 2 minutes.')
}

const viewLeakDetails = (leak: any) => {
  selectedLeak.value = leak
  leakDialogVisible.value = true
}

const fixLeak = (leak: any) => {
  ElMessage.success(`Leak at ${leak.location} marked as fixed`)
  const index = leakPoints.value.findIndex(l => l.id === leak.id)
  if (index !== -1) {
    leakPoints.value.splice(index, 1)
    // Update metrics
    containmentEfficiency.value = Math.min(containmentEfficiency.value + 2, 98)
    leakageRate.value = Math.max(leakageRate.value - 1, 2)
  }
  leakDialogVisible.value = false
}

const exportLeakReport = () => {
  ElMessage.success('Leak report export started')
}

const rotateView = () => {
  ElMessage.info('Rotating view...')
}

const resetView = () => {
  ElMessage.info('View reset')
}

const exportModel = () => {
  ElMessage.success('3D model export started')
}

const runFullAnalysis = () => {
  ElMessage.success('Full containment analysis started')
}

const scheduleRetrofit = () => {
  ElMessage.info('Retrofit scheduling interface will open')
}

const generateAuditReport = () => {
  ElMessage.success('Audit report generation started')
}

const generateRetrofitPlan = () => {
  ElMessage.success('Retrofit plan generated')
}

const downloadReport = (report: any) => {
  ElMessage.success(`Downloading ${report.title}...`)
}

// Chart initialization
const initContainment3DChart = () => {
  if (containment3DChartRef.value) {
    const chart = echarts.init(containment3DChartRef.value)

    // Generate 3D surface data for containment visualization
    const data: any[] = []
    for (let i = 0; i < 30; i++) {
      for (let j = 0; j < 50; j++) {
        let z = 0
        // Hot aisle area (center)
        if (j > 15 && j < 35 && i > 5 && i < 25) {
          z = 2.5 + Math.sin(i / 5) * 0.5
        }
        // Cold aisle areas
        else if ((j < 15 || j > 35) && i > 5 && i < 25) {
          z = 1.0
        }
        // Containment walls
        if ((i === 5 || i === 25) && j > 15 && j < 35) {
          z = 3.0
        }
        data.push([j, i, z])
      }
    }

    chart.setOption({
      tooltip: { trigger: 'item' },
      xAxis: { type: 'category', data: Array.from({ length: 50 }, (_, i) => i + 1), show: false },
      yAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => String.fromCharCode(65 + i)), show: false },
      visualMap: { min: 0, max: 3.5, calculable: true, inRange: { color: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false } }]
    })
    chartInstances.push(chart)
  }
}

const initLeakageMapChart = () => {
  if (leakageMapChartRef.value) {
    const chart = echarts.init(leakageMapChartRef.value)
    const data: any[] = []

    for (let i = 0; i < 20; i++) {
      for (let j = 0; j < 30; j++) {
        let leakIntensity = Math.random() * 10
        // Create leak hotspots
        if ((i === 5 && j === 8) || (i === 6 && j === 9)) leakIntensity = 18
        if ((i === 12 && j === 15) || (i === 13 && j === 14)) leakIntensity = 12
        data.push([j, i, leakIntensity])
      }
    }

    chart.setOption({
      tooltip: { position: 'top', formatter: (params: any) => `Leak Intensity: ${params.data[2].toFixed(0)}%` },
      xAxis: { type: 'category', data: Array.from({ length: 30 }, (_, i) => i + 1), name: 'Rack Position', axisLabel: { interval: 5 } },
      yAxis: { type: 'category', data: Array.from({ length: 20 }, (_, i) => String.fromCharCode(65 + i)), name: 'Row' },
      visualMap: { min: 0, max: 20, calculable: true, inRange: { color: ['#10b981', '#84cc16', '#f59e0b', '#ef4444', '#7c2d12'] } },
      series: [{ type: 'heatmap', data: data, label: { show: false } }]
    })
    chartInstances.push(chart)
  }
}

const initEfficiencyTrendChart = () => {
  if (efficiencyTrendChartRef.value) {
    const chart = echarts.init(efficiencyTrendChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Containment Efficiency', 'Target'] },
      xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
      yAxis: { type: 'value', name: 'Efficiency (%)', min: 60, max: 100 },
      series: [
        { name: 'Containment Efficiency', type: 'line', data: [72, 74, 76, 78, 80, 82, 84, 85, 86, 87, 88, 89], smooth: true, lineStyle: { color: '#409eff', width: 3 }, areaStyle: { opacity: 0.3 } },
        { name: 'Target', type: 'line', data: [95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95, 95], lineStyle: { color: '#f59e0b', width: 2, type: 'dashed' } }
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
      legend: { data: ['Cold Aisle', 'Hot Aisle'] },
      xAxis: { type: 'category', data: ['Row A', 'Row B', 'Row C', 'Row D'] },
      yAxis: { type: 'value', name: 'Temperature (°C)' },
      series: [
        { name: 'Cold Aisle', type: 'bar', data: [22.5, 23.0, 22.8, 23.2], itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'Hot Aisle', type: 'bar', data: [31.5, 32.0, 31.8, 32.2], itemStyle: { color: '#ef4444', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initPressureDiffChart = () => {
  if (pressureDiffChartRef.value) {
    const chart = echarts.init(pressureDiffChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5', 'Zone 6'] },
      yAxis: { type: 'value', name: 'Pressure (Pa)' },
      series: [
        { name: 'Hot Aisle', type: 'line', data: [7.2, 6.8, 7.5, 7.0, 6.5, 7.3], lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', symbolSize: 8, label: { show: true } },
        { name: 'Cold Aisle', type: 'line', data: [3.5, 3.2, 3.8, 3.3, 3.0, 3.6], lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', symbolSize: 8, label: { show: true } }
      ]
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
          { value: 35, name: 'Missing Blanking Panels', itemStyle: { color: '#ef4444' } },
          { value: 28, name: 'Cable Cutouts', itemStyle: { color: '#f59e0b' } },
          { value: 22, name: 'Aisle End Gaps', itemStyle: { color: '#10b981' } },
          { value: 15, name: 'Underfloor Leaks', itemStyle: { color: '#3b82f6' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initBeforeAfterChart = () => {
  if (beforeAfterChartRef.value) {
    const chart = echarts.init(beforeAfterChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Before Retrofit', 'After Retrofit'] },
      xAxis: { type: 'category', data: ['Containment Efficiency', 'Leakage Rate', 'PUE', 'Energy (MWh)'] },
      yAxis: { type: 'value' },
      series: [
        { name: 'Before Retrofit', type: 'bar', data: [78, 22, 1.45, 3200], itemStyle: { color: '#f59e0b', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } },
        { name: 'After Retrofit', type: 'bar', data: [94, 6, 1.37, 2800], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const handleResize = () => {
  chartInstances.forEach(chart => chart.resize())
}

// Watch for viz layer changes
const refreshViz = () => {
  initContainment3DChart()
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
        initContainment3DChart()
        initLeakageMapChart()
        initEfficiencyTrendChart()
        initTempDistributionChart()
        initPressureDiffChart()
        initBypassChart()
        initBeforeAfterChart()
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
.containment-analysis-container {
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
  border-top-color: #f59e0b;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #3b82f6;
  animation-delay: 0.2s;
  width: 70%;
  height: 70%;
  top: 15%;
  left: 15%;
}

.spinner-ring:nth-child(3) {
  border-bottom-color: #10b981;
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
  background: linear-gradient(90deg, #f59e0b, #3b82f6, #10b981);
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
.containment-analysis-container {
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

.alert-banner.critical {
  background: #fef2f2;
  border-left: 4px solid #ef4444;
  color: #dc2626;
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

/* Containment Visualization */
.containment-viz-section {
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

/* Leakage Section */
.leakage-section {
  margin-bottom: 24px;
}

.leakage-card {
  border-radius: 12px;
}

.leakage-container {
  min-height: 400px;
}

/* Leak Points Section */
.leakpoints-section {
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
  color: #f59e0b;
}

.chart-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

/* Pressure Stats */
.pressure-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
}

.stat-card {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 12px;
}

/* Bypass Summary */
.bypass-summary {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.bypass-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.bypass-item {
  margin-bottom: 16px;
}

.bypass-item span {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
  color: #606266;
}

.bypass-total {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
}

.bypass-total strong {
  color: #409eff;
  font-size: 18px;
}

/* Retrofit Summary */
.retrofit-summary {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  height: 100%;
}

.retrofit-summary h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.investment-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.investment-item strong {
  color: #d97706;
}

/* Comparison Stats */
.comparison-stats {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.comparison-item {
  margin-bottom: 24px;
}

.comparison-item > span {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #303133;
}

.comparison-bars {
  padding-left: 8px;
}

.comparison-bars .before {
  font-size: 12px;
  color: #f59e0b;
}

.comparison-bars .after {
  font-size: 12px;
  color: #67c23a;
  margin-top: 8px;
  display: block;
}

/* Report Cards */
.report-card {
  background: #fafafa;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.report-card .el-icon {
  color: #409eff;
  margin-bottom: 12px;
}

.report-card h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.report-card p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: #909399;
}

.report-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #c0c4cc;
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