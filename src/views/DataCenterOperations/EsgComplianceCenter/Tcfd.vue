<template>
  <div class="tcfd-container">
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
            <span class="loading-title">Loading TCFD Framework</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Task Force on Climate-related Financial Disclosures</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <el-page-header @back="goBack" content="Back">
        <template #content>
          <div class="page-header-content">
            <span class="page-title">TCFD - Climate-related Financial Disclosures</span>
            <el-tag type="warning" effect="dark" size="large">Recommendation Framework</el-tag>
          </div>
        </template>
      </el-page-header>

      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>Overall TCFD Alignment</span>
              </div>
              <div class="card-value">81%</div>
              <div class="card-footer">
                <el-progress :percentage="81" :stroke-width="8" />
                <span class="status-text">Fully Aligned</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Governance</span>
              </div>
              <div class="card-value">95%</div>
              <div class="card-footer">
                <el-progress :percentage="95" :stroke-width="8" status="success" />
                <span>Board Oversight</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Strategy</span>
              </div>
              <div class="card-value">78%</div>
              <div class="card-footer">
                <el-progress :percentage="78" :stroke-width="8" status="warning" />
                <span>Scenario Analysis</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Metrics & Targets</span>
              </div>
              <div class="card-value">72%</div>
              <div class="card-footer">
                <el-progress :percentage="72" :stroke-width="8" status="warning" />
                <span>Emissions Reduction</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Four Pillars Overview -->
      <div class="pillars-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="pillar-card governance" @click="activeTab = 'governance'">
              <div class="pillar-icon">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <h3>Governance</h3>
              <div class="pillar-progress">
                <el-progress :percentage="95" :stroke-width="6" status="success" />
              </div>
              <p>Board oversight & management role</p>
              <el-tag type="success" size="small">Completed</el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="pillar-card strategy" @click="activeTab = 'strategy'">
              <div class="pillar-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <h3>Strategy</h3>
              <div class="pillar-progress">
                <el-progress :percentage="78" :stroke-width="6" status="warning" />
              </div>
              <p>Risks, opportunities & scenarios</p>
              <el-tag type="warning" size="small">In Progress</el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="pillar-card risk" @click="activeTab = 'riskManagement'">
              <div class="pillar-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <h3>Risk Management</h3>
              <div class="pillar-progress">
                <el-progress :percentage="85" :stroke-width="6" status="success" />
              </div>
              <p>Identification & integration</p>
              <el-tag type="success" size="small">Good</el-tag>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="pillar-card metrics" @click="activeTab = 'metricsTargets'">
              <div class="pillar-icon">
                <el-icon><DataAnalysis /></el-icon>
              </div>
              <h3>Metrics & Targets</h3>
              <div class="pillar-progress">
                <el-progress :percentage="72" :stroke-width="6" status="warning" />
              </div>
              <p>GHG metrics & reduction targets</p>
              <el-tag type="warning" size="small">Partial</el-tag>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Governance Tab -->
          <el-tab-pane label="Governance" name="governance">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><OfficeBuilding /></el-icon>
                <span>Governance Disclosures</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="governance-table">
                    <el-table :data="governanceData" border style="width: 100%">
                      <el-table-column prop="disclosure" label="Disclosure Requirement" width="280" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="evidence" label="Evidence / Reference" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="info-panel">
                    <div class="panel-title">
                      <el-icon><InfoFilled /></el-icon>
                      <span>Governance Structure</span>
                    </div>
                    <div class="org-chart">
                      <div class="org-node board">
                        <el-icon><OfficeBuilding /></el-icon>
                        <span>Board of Directors</span>
                      </div>
                      <div class="org-line"></div>
                      <div class="org-children">
                        <div class="org-node committee">
                          <el-icon><User /></el-icon>
                          <span>Sustainability Committee</span>
                        </div>
                        <div class="org-node committee">
                          <el-icon><User /></el-icon>
                          <span>Risk Committee</span>
                        </div>
                      </div>
                      <div class="org-line"></div>
                      <div class="org-node management">
                        <el-icon><UserFilled /></el-icon>
                        <span>Chief Sustainability Officer</span>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Strategy Tab -->
          <el-tab-pane label="Strategy" name="strategy">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Strategy Disclosures</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="strategy-table">
                    <el-table :data="strategyData" border style="width: 100%">
                      <el-table-column prop="disclosure" label="Disclosure Requirement" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="scenarioChartRef" style="height: 380px"></div>
                  </div>
                  <div class="risk-opportunity-list">
                    <el-tabs>
                      <el-tab-pane label="Climate Risks">
                        <div v-for="risk in climateRisks" :key="risk.name" class="risk-item">
                          <div class="risk-header">
                            <span class="risk-name">{{ risk.name }}</span>
                            <el-tag :type="risk.level === 'High' ? 'danger' : 'warning'" size="small">
                              {{ risk.level }}
                            </el-tag>
                          </div>
                          <div class="risk-impact">{{ risk.impact }}</div>
                        </div>
                      </el-tab-pane>
                      <el-tab-pane label="Climate Opportunities">
                        <div v-for="opp in climateOpportunities" :key="opp.name" class="opportunity-item">
                          <div class="opportunity-name">{{ opp.name }}</div>
                          <div class="opportunity-benefit">{{ opp.benefit }}</div>
                        </div>
                      </el-tab-pane>
                    </el-tabs>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Risk Management Tab -->
          <el-tab-pane label="Risk Management" name="riskManagement">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Warning /></el-icon>
                <span>Risk Management Disclosures</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="risk-table">
                    <el-table :data="riskManagementData" border style="width: 100%">
                      <el-table-column prop="disclosure" label="Disclosure Requirement" width="280" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="description" label="Description" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="riskHeatmapChartRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Metrics & Targets Tab -->
          <el-tab-pane label="Metrics & Targets" name="metricsTargets">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><DataAnalysis /></el-icon>
                <span>Metrics & Targets Disclosures</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="metrics-table">
                    <el-table :data="metricsData" border style="width: 100%">
                      <el-table-column prop="metric" label="Metric" width="200" />
                      <el-table-column prop="value" label="Value" width="120" />
                      <el-table-column prop="unit" label="Unit" />
                    </el-table>
                  </div>
                  <div class="targets-section">
                    <h4>Emissions Reduction Targets</h4>
                    <div class="target-item">
                      <span>Scope 1 & 2 Reduction</span>
                      <el-progress :percentage="35" :format="() => '-25% by 2030'" status="success" />
                    </div>
                    <div class="target-item">
                      <span>Scope 3 Reduction</span>
                      <el-progress :percentage="20" :format="() => '-15% by 2030'" />
                    </div>
                    <div class="target-item">
                      <span>Renewable Energy</span>
                      <el-progress :percentage="68" :format="() => '100% by 2025'" status="success" />
                    </div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="emissionsChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Scenario Analysis Tab -->
          <el-tab-pane label="Scenario Analysis" name="scenario">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Connection /></el-icon>
                <span>Climate Scenario Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="scenarioComparisonChartRef" style="height: 400px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="scenario-descriptions">
                    <el-collapse v-model="scenarioCollapse">
                      <el-collapse-item title="1.5°C Scenario (Net Zero 2050)" name="1">
                        <p>Global warming limited to 1.5°C above pre-industrial levels. Requires rapid transition to net-zero by 2050.</p>
                        <el-tag type="danger">High Transition Risk</el-tag>
                        <el-tag type="info">Low Physical Risk</el-tag>
                      </el-collapse-item>
                      <el-collapse-item title="2°C Scenario (Moderate Transition)" name="2">
                        <p>Paris Agreement goals achieved with moderate transition pace. Balance of risks.</p>
                        <el-tag type="warning">Medium Transition Risk</el-tag>
                        <el-tag type="warning">Medium Physical Risk</el-tag>
                      </el-collapse-item>
                      <el-collapse-item title="3°C+ Scenario (Business as Usual)" name="3">
                        <p>Limited climate action, high physical impacts, delayed transition.</p>
                        <el-tag type="info">Low Transition Risk</el-tag>
                        <el-tag type="danger">High Physical Risk</el-tag>
                      </el-collapse-item>
                    </el-collapse>
                    <div class="financial-impact">
                      <h4>Financial Impact Assessment</h4>
                      <el-table :data="financialImpactData" border size="small">
                        <el-table-column prop="scenario" label="Scenario" />
                        <el-table-column prop="impact" label="Financial Impact" />
                        <el-table-column prop="timeframe" label="Timeframe" />
                      </el-table>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Gap Analysis Tab -->
          <el-tab-pane label="Gap Analysis" name="gap">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                <span>TCFD Gap Analysis</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="14">
                  <div class="gap-table">
                    <el-table :data="tcfdGapData" border style="width: 100%">
                      <el-table-column prop="pillar" label="Pillar" width="120" />
                      <el-table-column prop="disclosure" label="Disclosure" width="250" />
                      <el-table-column prop="status" label="Status" width="120">
                        <template #default="{ row }">
                          <el-tag :type="getGapStatusType(row.status)">
                            {{ row.status }}
                          </el-tag>
                        </template>
                      </el-table-column>
                      <el-table-column prop="action" label="Action Required" />
                    </el-table>
                  </div>
                </el-col>
                <el-col :span="10">
                  <div class="chart-container">
                    <div ref="gapChartRef" style="height: 280px"></div>
                  </div>
                  <div class="remediation-timeline">
                    <h4>Remediation Timeline</h4>
                    <el-timeline>
                      <el-timeline-item
                          v-for="(step, index) in remediationSteps"
                          :key="index"
                          :timestamp="step.date"
                          :type="step.type"
                      >
                        {{ step.description }}
                      </el-timeline-item>
                    </el-timeline>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-card>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="generateTCFDReport">
          <el-icon><Download /></el-icon>
          Generate TCFD Report
        </el-button>
        <el-button size="large" @click="exportData">
          <el-icon><Share /></el-icon>
          Export Recommendations
        </el-button>
        <el-button size="large" @click="runScenarioAnalysis">
          <el-icon><TrendCharts /></el-icon>
          Run Scenario Analysis
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading TCFD framework...')

const loadingMessages = [
  'Loading governance disclosures...',
  'Analyzing climate scenarios...',
  'Calculating risk metrics...',
  'Mapping strategic impacts...',
  'Assessing disclosure gaps...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('governance')
const scenarioCollapse = ref(['1'])

// Chart refs
const scenarioChartRef = ref<HTMLElement | null>(null)
const riskHeatmapChartRef = ref<HTMLElement | null>(null)
const emissionsChartRef = ref<HTMLElement | null>(null)
const scenarioComparisonChartRef = ref<HTMLElement | null>(null)
const gapChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Governance Data
const governanceData = ref([
  { disclosure: "Board's oversight of climate-related risks and opportunities", status: 'Disclosed', evidence: 'Board Charter, Q4 2024' },
  { disclosure: 'Management role in assessing climate-related issues', status: 'Disclosed', evidence: 'CSO Mandate' },
  { disclosure: 'Climate expertise within governance bodies', status: 'Partial', evidence: '2 of 5 members trained' },
  { disclosure: 'Integration into governance frameworks', status: 'Disclosed', evidence: 'Risk Committee Charter' }
])

// Strategy Data
const strategyData = ref([
  { disclosure: 'Climate-related risks and opportunities over short/medium/long term', status: 'Disclosed' },
  { disclosure: 'Impact of climate risks on business, strategy, and financial planning', status: 'Partial' },
  { disclosure: 'Resilience of strategy under different climate scenarios', status: 'Partial' }
])

// Risk Management Data
const riskManagementData = ref([
  { disclosure: 'Processes for identifying and assessing climate risks', status: 'Disclosed', description: 'Annual risk assessment' },
  { disclosure: 'Processes for managing climate risks', status: 'Disclosed', description: 'Integrated into ERM' },
  { disclosure: 'Integration into overall risk management', status: 'Partial', description: 'Under development' }
])

// Metrics Data
const metricsData = ref([
  { metric: 'Scope 1 GHG Emissions', value: '45,200', unit: 'tCO₂e' },
  { metric: 'Scope 2 GHG Emissions', value: '28,500', unit: 'tCO₂e' },
  { metric: 'Scope 3 GHG Emissions', value: '342,000', unit: 'tCO₂e' },
  { metric: 'Carbon Intensity', value: '125', unit: 'gCO₂e/kWh' },
  { metric: 'Energy Consumption', value: '425,000', unit: 'MWh' },
  { metric: 'Renewable Energy Ratio', value: '68', unit: '%' }
])

// Climate Risks
const climateRisks = ref([
  { name: 'Carbon Pricing / Regulation', level: 'High', impact: 'Increased operational costs by 15-20%' },
  { name: 'Physical Asset Damage', level: 'High', impact: 'Infrastructure damage from extreme weather' },
  { name: 'Technology Transition', level: 'Medium', impact: 'Investment in low-carbon tech required' },
  { name: 'Reputational Risk', level: 'Medium', impact: 'Stakeholder pressure for decarbonization' }
])

// Climate Opportunities
const climateOpportunities = ref([
  { name: 'Energy Efficiency', benefit: 'Cost savings of $5M annually' },
  { name: 'Renewable Energy Adoption', benefit: 'Reduced energy costs and emissions' },
  { name: 'Green Products/Services', benefit: 'New revenue streams from sustainable offerings' },
  { name: 'Resilience Planning', benefit: 'Reduced disruption from climate events' }
])

// Financial Impact Data
const financialImpactData = ref([
  { scenario: '1.5°C Scenario', impact: '-$15M (transition costs)', timeframe: '2025-2030' },
  { scenario: '2°C Scenario', impact: '-$8M (balanced)', timeframe: '2025-2030' },
  { scenario: '3°C+ Scenario', impact: '-$25M (physical damages)', timeframe: '2030-2040' }
])

// Gap Analysis Data
const tcfdGapData = ref([
  { pillar: 'Governance', disclosure: 'Board climate expertise disclosure', status: 'Partial', action: 'Document board climate competencies' },
  { pillar: 'Strategy', disclosure: 'Scenario analysis for 1.5°C pathway', status: 'Partial', action: 'Complete 1.5°C scenario analysis' },
  { pillar: 'Strategy', disclosure: 'Transition plan resilience', status: 'Missing', action: 'Develop transition plan' },
  { pillar: 'Risk Mgmt', disclosure: 'Risk process integration', status: 'Partial', action: 'Integrate with ERM fully' },
  { pillar: 'Metrics', disclosure: 'Scope 3 verification', status: 'Partial', action: 'Obtain third-party verification' }
])

// Remediation Steps
const remediationSteps = ref([
  { date: 'Q1 2025', description: 'Complete 1.5°C scenario analysis', type: 'primary' },
  { date: 'Q2 2025', description: 'Document board climate governance', type: 'primary' },
  { date: 'Q3 2025', description: 'Develop transition plan', type: 'warning' },
  { date: 'Q4 2025', description: 'Full TCFD alignment', type: 'success' }
])

// Methods
const goBack = () => {
  router.back()
}

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Disclosed': 'success',
    'Partial': 'warning',
    'Missing': 'danger'
  }
  return map[status] || 'info'
}

const getGapStatusType = (status: string) => {
  const map: Record<string, string> = {
    'Disclosed': 'success',
    'Partial': 'warning',
    'Missing': 'danger'
  }
  return map[status] || 'info'
}

const generateTCFDReport = () => {
  ElMessage.success('TCFD report generation started. You will receive a notification when ready.')
}

const exportData = () => {
  ElMessage.success('Recommendations export started. File will be downloaded shortly.')
}

const runScenarioAnalysis = () => {
  activeTab.value = 'scenario'
  ElMessage.info('Scenario analysis dashboard loaded.')
}

// Chart initialization
const initScenarioChart = () => {
  if (scenarioChartRef.value) {
    const chart = echarts.init(scenarioChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Physical Risk', 'Transition Risk', 'Net Opportunity'] },
      xAxis: { type: 'category', data: ['2025', '2030', '2035', '2040', '2050'] },
      yAxis: { type: 'value', name: 'Impact ($M)' },
      series: [
        { name: 'Physical Risk', type: 'line', data: [5, 10, 18, 28, 40], smooth: true, lineStyle: { color: '#f56c6c', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Transition Risk', type: 'line', data: [8, 15, 22, 25, 20], smooth: true, lineStyle: { color: '#e6a23c', width: 2 }, areaStyle: { opacity: 0.3 } },
        { name: 'Net Opportunity', type: 'line', data: [-2, -5, -8, -10, -15], smooth: true, lineStyle: { color: '#67c23a', width: 2, type: 'dashed' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initRiskHeatmapChart = () => {
  if (riskHeatmapChartRef.value) {
    const chart = echarts.init(riskHeatmapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      xAxis: { type: 'category', data: ['Physical', 'Transition', 'Liability', 'Reputational'] },
      yAxis: { type: 'category', data: ['Short-term', 'Medium-term', 'Long-term'] },
      visualMap: { min: 0, max: 5, calculable: true, inRange: { color: ['#90ed7d', '#f7a35c', '#f15c80'] } },
      series: [{
        type: 'heatmap',
        data: [
          [0, 0, 4], [1, 0, 3], [2, 0, 2], [3, 0, 3],
          [0, 1, 5], [1, 1, 4], [2, 1, 3], [3, 1, 4],
          [0, 2, 5], [1, 2, 3], [2, 2, 4], [3, 2, 3]
        ],
        label: { show: true, formatter: (params: any) => ['Low', 'Medium', 'High', 'Critical'][params.data[2] - 1] }
      }]
    })
    chartInstances.push(chart)
  }
}

const initEmissionsChart = () => {
  if (emissionsChartRef.value) {
    const chart = echarts.init(emissionsChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'] },
      xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024', '2025e'] },
      yAxis: { type: 'value', name: 'tCO₂e (thousands)' },
      series: [
        { name: 'Scope 1', type: 'bar', data: [52, 50, 48, 46, 45, 43], itemStyle: { color: '#5470c6' } },
        { name: 'Scope 2', type: 'bar', data: [35, 33, 31, 29, 28, 25], itemStyle: { color: '#91cc75' } },
        { name: 'Scope 3', type: 'bar', data: [380, 375, 365, 355, 342, 330], itemStyle: { color: '#fac858' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initScenarioComparisonChart = () => {
  if (scenarioComparisonChartRef.value) {
    const chart = echarts.init(scenarioComparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['1.5°C Scenario', '2°C Scenario', '3°C+ Scenario'] },
      xAxis: { type: 'category', data: ['2025', '2030', '2040', '2050'] },
      yAxis: { type: 'value', name: 'Revenue Impact ($M)' },
      series: [
        { name: '1.5°C Scenario', type: 'line', data: [-5, -15, -10, 5], smooth: true, lineStyle: { color: '#5470c6', width: 2 } },
        { name: '2°C Scenario', type: 'line', data: [-3, -8, -5, 10], smooth: true, lineStyle: { color: '#fac858', width: 2 } },
        { name: '3°C+ Scenario', type: 'line', data: [-2, -20, -35, -50], smooth: true, lineStyle: { color: '#ee6666', width: 2 } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initGapChart = () => {
  if (gapChartRef.value) {
    const chart = echarts.init(gapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      legend: { top: 'bottom' },
      series: [{
        name: 'Disclosure Status',
        type: 'pie',
        radius: '55%',
        data: [
          { value: 65, name: 'Disclosed', itemStyle: { color: '#67c23a' } },
          { value: 25, name: 'Partial', itemStyle: { color: '#e6a23c' } },
          { value: 10, name: 'Missing', itemStyle: { color: '#f56c6c' } }
        ],
        label: { show: true, formatter: '{b}: {d}%' }
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
        initScenarioChart()
        initRiskHeatmapChart()
        initEmissionsChart()
        initScenarioComparisonChart()
        initGapChart()
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
.tcfd-container {
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
  border: 1px solid rgba(245, 158, 11, 0.3);
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
  border-right-color: #ef4444;
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
  background: linear-gradient(90deg, #f59e0b, #ef4444, #10b981);
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
.tcfd-container {
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

.overview-section,
.pillars-section {
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

/* Pillar Cards */
.pillar-card {
  background: white;
  border-radius: 16px;
  padding: 24px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
  height: 100%;
}

.pillar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.1);
}

.pillar-card.governance:hover { border-color: #409eff; background: #ecf5ff; }
.pillar-card.strategy:hover { border-color: #f59e0b; background: #fffbeb; }
.pillar-card.risk:hover { border-color: #f56c6c; background: #fef0f0; }
.pillar-card.metrics:hover { border-color: #10b981; background: #ecfdf5; }

.pillar-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  border-radius: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.pillar-card.governance .pillar-icon { background: #ecf5ff; color: #409eff; }
.pillar-card.strategy .pillar-icon { background: #fffbeb; color: #f59e0b; }
.pillar-card.risk .pillar-icon { background: #fef0f0; color: #f56c6c; }
.pillar-card.metrics .pillar-icon { background: #ecfdf5; color: #10b981; }

.pillar-card h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
}

.pillar-card p {
  margin: 12px 0;
  font-size: 13px;
  color: #909399;
}

.pillar-progress {
  margin: 16px 0;
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

.info-panel {
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e4e7ed;
}

/* Organization Chart */
.org-chart {
  text-align: center;
  padding: 20px;
}

.org-node {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  font-weight: 500;
}

.org-node.board {
  background: #ecf5ff;
  color: #409eff;
  font-size: 16px;
}

.org-node.committee {
  background: #f5f7fa;
  color: #606266;
  margin: 0 10px;
}

.org-node.management {
  background: #ecfdf5;
  color: #10b981;
}

.org-line {
  width: 2px;
  height: 30px;
  background: #dcdfe6;
  margin: 0 auto;
}

.org-children {
  display: flex;
  justify-content: center;
  margin: 10px 0;
}

/* Risk & Opportunity Lists */
.risk-opportunity-list {
  margin-top: 16px;
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.risk-item, .opportunity-item {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.risk-name, .opportunity-name {
  font-weight: 500;
  color: #303133;
}

.risk-impact, .opportunity-benefit {
  font-size: 12px;
  color: #909399;
}

/* Targets Section */
.targets-section {
  margin-top: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.targets-section h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.target-item {
  margin-bottom: 16px;
}

.target-item span {
  display: block;
  margin-bottom: 8px;
  font-size: 13px;
  color: #606266;
}

/* Scenario Descriptions */
.scenario-descriptions {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
}

.financial-impact {
  margin-top: 16px;
}

.financial-impact h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

/* Remediation Timeline */
.remediation-timeline {
  margin-top: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.remediation-timeline h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

/* Tables */
.governance-table,
.strategy-table,
.risk-table,
.metrics-table,
.gap-table {
  border-radius: 8px;
  overflow: hidden;
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

:deep(.el-collapse-item__header) {
  font-weight: 500;
}

:deep(.el-table) {
  border-radius: 8px;
}
</style>