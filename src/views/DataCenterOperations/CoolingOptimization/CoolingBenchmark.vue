<template>
  <div class="cooling-benchmark-container">
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
            <span class="loading-title">Loading Cooling Benchmark</span>
            <span class="loading-dots">
              <span>.</span><span>.</span><span>.</span>
            </span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Performance Comparison & Industry Standards</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <template v-else>
      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-content">
          <span class="page-title">IFRS S2 - Climate-related Disclosures</span>
          <el-tag type="danger" effect="dark" size="large">Compliance Center</el-tag>
        </div>
      </div>
      <!-- Overview Cards -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>Cooling PUE</span>
              </div>
              <div class="card-value">1.33</div>
              <div class="card-footer">
                <el-progress :percentage="85" :stroke-width="8" status="success" :format="() => 'vs. Industry: 1.45'" />
                <span class="status-text">Top 15%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Cpu /></el-icon>
                <span>Cooling COP</span>
              </div>
              <div class="card-value">5.8</div>
              <div class="card-footer">
                <el-progress :percentage="82" :stroke-width="8" status="success" :format="() => 'Industry Avg: 5.2'" />
                <span class="status-text">Above Average</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><Water /></el-icon>
                <span>WUE</span>
              </div>
              <div class="card-value">1.65</div>
              <div class="card-footer">
                <el-progress :percentage="68" :stroke-width="8" status="warning" :format="() => 'L/kWh'" />
                <span class="status-text">Industry Avg: 1.8</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" class="overview-card">
              <div class="card-header">
                <el-icon><DataLine /></el-icon>
                <span>Free Cooling %</span>
              </div>
              <div class="card-value">38%</div>
              <div class="card-footer">
                <el-progress :percentage="76" :stroke-width="8" status="success" :format="() => 'of Total Hours'" />
                <span class="status-text">Top Quartile</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Benchmark Comparison Charts -->
      <div class="benchmark-section">
        <el-card class="benchmark-card" shadow="hover">
          <div class="card-header-simple">
            <el-icon><DataAnalysis /></el-icon>
            <span>Cooling Efficiency Benchmark</span>
            <div class="header-actions">
              <el-radio-group v-model="benchmarkMetric" size="small">
                <el-radio-button label="pue">PUE</el-radio-button>
                <el-radio-button label="cop">COP</el-radio-button>
                <el-radio-button label="wue">WUE</el-radio-button>
              </el-radio-group>
            </div>
          </div>
          <div class="chart-container">
            <div ref="benchmarkChartRef" style="height: 400px"></div>
          </div>
        </el-card>
      </div>

      <!-- Industry Standards Comparison -->
      <div class="standards-section">
        <div class="section-header">
          <h3>Industry Standards Comparison</h3>
          <el-select v-model="selectedStandard" placeholder="Select Standard" size="small" style="width: 200px">
            <el-option label="ASHRAE Class A1" value="ashrae_a1" />
            <el-option label="ASHRAE Class A2" value="ashrae_a2" />
            <el-option label="EU Code of Conduct" value="eu_code" />
            <el-option label="Green Grid" value="green_grid" />
          </el-select>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="standards-table">
              <el-table :data="standardsComparison" border style="width: 100%">
                <el-table-column prop="metric" label="Metric" width="180" />
                <el-table-column prop="ourValue" label="Our Value" width="120">
                  <template #default="{ row }">
                    <span :class="{ 'excellent': row.excellent, 'good': row.good }">{{ row.ourValue }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="industryAvg" label="Industry Avg" width="120" />
                <el-table-column prop="bestPractice" label="Best Practice" width="120" />
                <el-table-column prop="rating" label="Rating" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.rating === 'Excellent' ? 'success' : row.rating === 'Good' ? 'warning' : 'info'" size="small">
                      {{ row.rating }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="radar-container">
              <div ref="radarChartRef" style="height: 380px"></div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Peer Comparison -->
      <div class="peer-section">
        <div class="section-header">
          <h3>Peer Data Center Comparison</h3>
          <el-button type="primary" link @click="refreshPeerData">Refresh Data →</el-button>
        </div>
        <el-row :gutter="20">
          <el-col :span="16">
            <div class="chart-container">
              <div ref="peerComparisonChartRef" style="height: 400px"></div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="peer-rankings">
              <h4>Ranking Among Peers</h4>
              <div class="ranking-item">
                <span class="rank">1st</span>
                <span>Cooling Efficiency</span>
                <el-tag type="success">Top 5%</el-tag>
              </div>
              <div class="ranking-item">
                <span class="rank">2nd</span>
                <span>PUE Performance</span>
                <el-tag type="success">Top 10%</el-tag>
              </div>
              <div class="ranking-item">
                <span class="rank">3rd</span>
                <span>Free Cooling Usage</span>
                <el-tag type="warning">Top 20%</el-tag>
              </div>
              <div class="ranking-item">
                <span class="rank">5th</span>
                <span>Water Efficiency</span>
                <el-tag type="warning">Top 25%</el-tag>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Main Content Tabs -->
      <el-card class="main-content-card" shadow="never">
        <el-tabs v-model="activeTab" type="border-card">
          <!-- Historical Benchmark Tab -->
          <el-tab-pane label="Historical Benchmark" name="historical">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                <span>Historical Performance vs. Benchmarks</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="historicalPUETrendRef" style="height: 350px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="historicalCOPTrendRef" style="height: 350px"></div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Regional Benchmark Tab -->
          <el-tab-pane label="Regional Benchmark" name="regional">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Location /></el-icon>
                <span>Regional Performance Comparison</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="regionalMapChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="regional-stats">
                    <el-table :data="regionalData" border>
                      <el-table-column prop="region" label="Region" />
                      <el-table-column prop="avgPUE" label="Avg PUE" />
                      <el-table-column prop="ourPUE" label="Our PUE" />
                      <el-table-column prop="comparison" label="Comparison">
                        <template #default="{ row }">
                          <el-tag :type="row.ourPUE < row.avgPUE ? 'success' : 'danger'" size="small">
                            {{ row.ourPUE < row.avgPUE ? 'Better' : 'Worse' }}
                          </el-tag>
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Technology Benchmark Tab -->
          <el-tab-pane label="Technology Benchmark" name="technology">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Cpu /></el-icon>
                <span>Cooling Technology Benchmark</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <div ref="techComparisonChartRef" style="height: 380px"></div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="tech-recommendations">
                    <h4>Technology Gap Analysis</h4>
                    <div v-for="tech in techGaps" :key="tech.name" class="tech-gap-item">
                      <div class="tech-header">
                        <span class="tech-name">{{ tech.name }}</span>
                        <el-tag :type="tech.status === 'Implemented' ? 'success' : 'warning'" size="small">
                          {{ tech.status }}
                        </el-tag>
                      </div>
                      <div class="tech-progress">
                        <el-progress :percentage="tech.progress" :stroke-width="8" :color="tech.color" />
                      </div>
                      <div class="tech-impact">
                        <span>Potential Savings: {{ tech.savings }}</span>
                        <el-button type="primary" link size="small" @click="viewTechDetails(tech)">Details</el-button>
                      </div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>

          <!-- Improvement Opportunities Tab -->
          <el-tab-pane label="Improvement Opportunities" name="opportunities">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Goal /></el-icon>
                <span>Improvement Opportunities</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="16">
                  <el-table :data="improvementOpportunities" border style="width: 100%">
                    <el-table-column prop="opportunity" label="Opportunity" width="250" />
                    <el-table-column prop="currentGap" label="Current Gap" />
                    <el-table-column prop="potentialSavings" label="Potential Savings" />
                    <el-table-column prop="priority" label="Priority" width="100">
                      <template #default="{ row }">
                        <el-tag :type="row.priority === 'High' ? 'danger' : row.priority === 'Medium' ? 'warning' : 'info'" size="small">
                          {{ row.priority }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column label="Action" width="100">
                      <template #default="{ row }">
                        <el-button type="primary" link size="small" @click="viewOpportunity(row)">View</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </el-col>
                <el-col :span="8">
                  <div class="opportunity-summary">
                    <h4>Total Improvement Potential</h4>
                    <div class="potential-value">15.5%</div>
                    <div class="potential-label">Cooling Energy Reduction</div>
                    <el-progress :percentage="15.5" :stroke-width="12" status="success" />
                    <div class="potential-details">
                      <div class="detail-item">
                        <span>Annual Savings:</span>
                        <strong>245,000 kWh</strong>
                      </div>
                      <div class="detail-item">
                        <span>Carbon Reduction:</span>
                        <strong>112 tCO₂e</strong>
                      </div>
                      <div class="detail-item">
                        <span>Cost Savings:</span>
                        <strong>$28,000/year</strong>
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

          <!-- Reports Tab -->
          <el-tab-pane label="Reports" name="reports">
            <div class="tab-content">
              <div class="section-title">
                <el-icon><Document /></el-icon>
                <span>Benchmark Reports</span>
              </div>
              <el-row :gutter="20">
                <el-col :span="8" v-for="report in benchmarkReports" :key="report.id">
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
        <el-button type="primary" size="large" @click="runBenchmarkAnalysis">
          <el-icon><DataAnalysis /></el-icon>
          Run Full Benchmark Analysis
        </el-button>
        <el-button size="large" @click="exportBenchmarkData">
          <el-icon><Download /></el-icon>
          Export Benchmark Data
        </el-button>
        <el-button size="large" @click="scheduleReview">
          <el-icon><Calendar /></el-icon>
          Schedule Review Meeting
        </el-button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const router = useRouter()

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading benchmark data...')

const loadingMessages = [
  'Loading benchmark data...',
  'Comparing industry standards...',
  'Analyzing peer performance...',
  'Calculating improvement opportunities...',
  'Generating comparison charts...',
  'Ready to display dashboard...'
]

// Reactive data
const activeTab = ref('historical')
const benchmarkMetric = ref('pue')
const selectedStandard = ref('ashrae_a1')

// Standards comparison data
const standardsComparison = ref([
  { metric: 'PUE (Cooling)', ourValue: '1.33', industryAvg: '1.45', bestPractice: '1.20', rating: 'Excellent', excellent: true, good: false },
  { metric: 'Cooling COP', ourValue: '5.8', industryAvg: '5.2', bestPractice: '7.0', rating: 'Good', excellent: false, good: true },
  { metric: 'WUE (L/kWh)', ourValue: '1.65', industryAvg: '1.80', bestPractice: '1.20', rating: 'Good', excellent: false, good: true },
  { metric: 'Free Cooling %', ourValue: '38%', industryAvg: '32%', bestPractice: '60%', rating: 'Good', excellent: false, good: true },
  { metric: 'EC Fan Adoption', ourValue: '85%', industryAvg: '70%', bestPractice: '100%', rating: 'Excellent', excellent: true, good: false }
])

// Regional data
const regionalData = ref([
  { region: 'North America', avgPUE: '1.42', ourPUE: '1.33' },
  { region: 'Europe', avgPUE: '1.38', ourPUE: '1.33' },
  { region: 'Asia-Pacific', avgPUE: '1.48', ourPUE: '1.33' },
  { region: 'Middle East', avgPUE: '1.55', ourPUE: '1.33' }
])

// Technology gaps
const techGaps = ref([
  { name: 'Liquid Cooling', status: 'Partial', progress: 45, savings: '15-25%', color: '#e6a23c' },
  { name: 'EC Fan Upgrades', status: 'Implemented', progress: 85, savings: '8-12%', color: '#67c23a' },
  { name: 'AI Dynamic Control', status: 'In Progress', progress: 60, savings: '10-18%', color: '#409eff' },
  { name: 'Free Cooling Enhancement', status: 'Partial', progress: 55, savings: '12-20%', color: '#e6a23c' }
])

// Improvement opportunities
const improvementOpportunities = ref([
  { opportunity: 'Increase free cooling usage by 15%', currentGap: '15% below target', potentialSavings: '85,000 kWh/year', priority: 'High' },
  { opportunity: 'Deploy liquid cooling for high-density racks', currentGap: 'Not implemented', potentialSavings: '65,000 kWh/year', priority: 'Medium' },
  { opportunity: 'Optimize fan speeds with AI', currentGap: 'Partial deployment', potentialSavings: '45,000 kWh/year', priority: 'High' },
  { opportunity: 'Implement containment sealing', currentGap: '12% leakage', potentialSavings: '35,000 kWh/year', priority: 'Medium' },
  { opportunity: 'Upgrade to next-gen EC fans', currentGap: '15% legacy units', potentialSavings: '25,000 kWh/year', priority: 'Low' }
])

// Benchmark reports
const benchmarkReports = ref([
  { id: 1, title: 'Annual Cooling Benchmark', description: 'Comprehensive cooling efficiency report', icon: 'DataAnalysis', format: 'PDF', date: '2024-12-01' },
  { id: 2, title: 'Peer Comparison Report', description: 'Comparison with industry peers', icon: 'TrendCharts', format: 'Excel', date: '2024-12-01' },
  { id: 3, title: 'Improvement Roadmap', description: 'Action plan for benchmark improvements', icon: 'Goal', format: 'PDF', date: '2024-12-01' },
  { id: 4, title: 'Technology Assessment', description: 'Cooling technology gap analysis', icon: 'Cpu', format: 'PPT', date: '2024-12-01' }
])

// Chart refs
const benchmarkChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)
const peerComparisonChartRef = ref<HTMLElement | null>(null)
const historicalPUETrendRef = ref<HTMLElement | null>(null)
const historicalCOPTrendRef = ref<HTMLElement | null>(null)
const regionalMapChartRef = ref<HTMLElement | null>(null)
const techComparisonChartRef = ref<HTMLElement | null>(null)

// Chart instances
let chartInstances: echarts.ECharts[] = []

// Methods
const goBack = () => {
  router.back()
}

const refreshPeerData = () => {
  ElMessage.success('Peer data refreshed')
}

const viewTechDetails = (tech: any) => {
  ElMessage.info(`Viewing details for ${tech.name}`)
}

const viewOpportunity = (opp: any) => {
  ElMessage.info(`Viewing opportunity: ${opp.opportunity}`)
}

const generateActionPlan = () => {
  ElMessage.success('Action plan generation started')
}

const runBenchmarkAnalysis = () => {
  ElMessage.success('Full benchmark analysis started')
}

const exportBenchmarkData = () => {
  ElMessage.success('Benchmark data export started')
}

const scheduleReview = () => {
  ElMessage.info('Review meeting scheduling interface will open')
}

const downloadReport = (report: any) => {
  ElMessage.success(`Downloading ${report.title}...`)
}

// Chart initialization
const initBenchmarkChart = () => {
  if (benchmarkChartRef.value) {
    const chart = echarts.init(benchmarkChartRef.value)
    let data = []
    if (benchmarkMetric.value === 'pue') {
      data = [
        { name: 'Our Facility', value: 1.33, category: 'Our' },
        { name: 'Industry Avg', value: 1.45, category: 'Industry' },
        { name: 'Best Practice', value: 1.20, category: 'Best' },
        { name: 'Top Quartile', value: 1.35, category: 'Top' }
      ]
    } else if (benchmarkMetric.value === 'cop') {
      data = [
        { name: 'Our Facility', value: 5.8, category: 'Our' },
        { name: 'Industry Avg', value: 5.2, category: 'Industry' },
        { name: 'Best Practice', value: 7.0, category: 'Best' },
        { name: 'Top Quartile', value: 6.2, category: 'Top' }
      ]
    } else {
      data = [
        { name: 'Our Facility', value: 1.65, category: 'Our' },
        { name: 'Industry Avg', value: 1.80, category: 'Industry' },
        { name: 'Best Practice', value: 1.20, category: 'Best' },
        { name: 'Top Quartile', value: 1.55, category: 'Top' }
      ]
    }

    chart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { rotate: 15 } },
      yAxis: { type: 'value', name: benchmarkMetric.value === 'pue' ? 'PUE' : benchmarkMetric.value === 'cop' ? 'COP' : 'WUE (L/kWh)' },
      series: [{
        type: 'bar',
        data: data.map(d => d.value),
        itemStyle: {
          borderRadius: [8, 8, 0, 0],
          color: (params: any) => {
            const colors = { Our: '#409eff', Industry: '#909399', Best: '#67c23a', Top: '#e6a23c' }
            return colors[data[params.dataIndex].category as keyof typeof colors] || '#409eff'
          }
        },
        label: { show: true, position: 'top', formatter: '{c}' }
      }]
    })
    chartInstances.push(chart)
  }
}

const initRadarChart = () => {
  if (radarChartRef.value) {
    const chart = echarts.init(radarChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      radar: {
        indicator: [
          { name: 'PUE', max: 2.0 },
          { name: 'COP', max: 8 },
          { name: 'WUE', max: 3.0 },
          { name: 'Free Cooling %', max: 100 },
          { name: 'EC Fan %', max: 100 },
          { name: 'Setpoint Optimization', max: 100 }
        ],
        shape: 'circle',
        center: ['50%', '50%'],
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: [
          { value: [1.33, 5.8, 1.65, 38, 85, 75], name: 'Our Facility', areaStyle: { color: 'rgba(64, 158, 255, 0.3)' }, lineStyle: { color: '#409eff', width: 2 } },
          { value: [1.45, 5.2, 1.80, 32, 70, 60], name: 'Industry Average', areaStyle: { color: 'rgba(144, 147, 153, 0.2)' }, lineStyle: { color: '#909399', width: 2 } }
        ]
      }]
    })
    chartInstances.push(chart)
  }
}

const initPeerComparisonChart = () => {
  if (peerComparisonChartRef.value) {
    const chart = echarts.init(peerComparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Our PUE', 'Peer Avg', 'Best Peer'] },
      xAxis: { type: 'category', data: ['Facility A', 'Facility B', 'Facility C', 'Facility D', 'Facility E', 'Our Facility'] },
      yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
      series: [
        { name: 'Our PUE', type: 'bar', data: [null, null, null, null, null, 1.33], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}' } },
        { name: 'Peer Avg', type: 'bar', data: [1.42, 1.38, 1.45, 1.40, 1.44, null], itemStyle: { color: '#909399', borderRadius: [8, 8, 0, 0] } },
        { name: 'Best Peer', type: 'bar', data: [1.35, 1.32, 1.38, 1.34, 1.36, null], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initHistoricalPUETrend = () => {
  if (historicalPUETrendRef.value) {
    const chart = echarts.init(historicalPUETrendRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Our PUE', 'Industry Average', 'Best Practice'] },
      xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
      yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
      series: [
        { name: 'Our PUE', type: 'line', data: [1.52, 1.48, 1.42, 1.38, 1.33], smooth: true, lineStyle: { color: '#409eff', width: 3 }, areaStyle: { opacity: 0.3 } },
        { name: 'Industry Average', type: 'line', data: [1.55, 1.52, 1.50, 1.48, 1.45], smooth: true, lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Best Practice', type: 'line', data: [1.45, 1.42, 1.38, 1.35, 1.32], smooth: true, lineStyle: { color: '#67c23a', width: 2, type: 'dotted' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initHistoricalCOPTrend = () => {
  if (historicalCOPTrendRef.value) {
    const chart = echarts.init(historicalCOPTrendRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Our COP', 'Industry Average', 'Best Practice'] },
      xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
      yAxis: { type: 'value', name: 'COP', min: 4, max: 7 },
      series: [
        { name: 'Our COP', type: 'line', data: [4.8, 5.1, 5.4, 5.6, 5.8], smooth: true, lineStyle: { color: '#409eff', width: 3 }, areaStyle: { opacity: 0.3 } },
        { name: 'Industry Average', type: 'line', data: [4.6, 4.8, 5.0, 5.1, 5.2], smooth: true, lineStyle: { color: '#909399', width: 2, type: 'dashed' } },
        { name: 'Best Practice', type: 'line', data: [5.2, 5.5, 5.8, 6.1, 6.4], smooth: true, lineStyle: { color: '#67c23a', width: 2, type: 'dotted' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initRegionalMapChart = () => {
  if (regionalMapChartRef.value) {
    const chart = echarts.init(regionalMapChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Our PUE', 'Regional Avg'] },
      xAxis: { type: 'category', data: regionalData.value.map(r => r.region) },
      yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
      series: [
        { name: 'Our PUE', type: 'line', data: [1.33, 1.33, 1.33, 1.33], lineStyle: { color: '#409eff', width: 3 }, symbol: 'circle', symbolSize: 10 },
        { name: 'Regional Avg', type: 'bar', data: [1.42, 1.38, 1.48, 1.55], itemStyle: { color: '#909399', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}' } }
      ]
    })
    chartInstances.push(chart)
  }
}

const initTechComparisonChart = () => {
  if (techComparisonChartRef.value) {
    const chart = echarts.init(techComparisonChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['Current', 'Potential'] },
      xAxis: { type: 'category', data: ['Air Cooling', 'Liquid Cooling', 'Free Cooling', 'AI Control', 'EC Fans'] },
      yAxis: { type: 'value', name: 'Efficiency Score' },
      series: [
        { name: 'Current', type: 'bar', data: [85, 45, 55, 60, 85], itemStyle: { color: '#409eff', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } },
        { name: 'Potential', type: 'bar', data: [90, 85, 80, 90, 95], itemStyle: { color: '#67c23a', borderRadius: [8, 8, 0, 0] }, label: { show: true, position: 'top', formatter: '{c}%' } }
      ]
    })
    chartInstances.push(chart)
  }
}

// Watch for metric changes
watch(benchmarkMetric, () => {
  initBenchmarkChart()
})

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
        initBenchmarkChart()
        initRadarChart()
        initPeerComparisonChart()
        initHistoricalPUETrend()
        initHistoricalCOPTrend()
        initRegionalMapChart()
        initTechComparisonChart()
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
.cooling-benchmark-container {
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
.cooling-benchmark-container {
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

/* Benchmark Section */
.benchmark-section {
  margin-bottom: 24px;
}

.benchmark-card {
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

/* Standards Section */
.standards-section {
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

.standards-table {
  border-radius: 8px;
  overflow: hidden;
}

.excellent {
  color: #67c23a;
  font-weight: 600;
}

.good {
  color: #409eff;
}

.radar-container {
  background: #fafafa;
  border-radius: 8px;
  padding: 12px;
  height: 100%;
}

/* Peer Section */
.peer-section {
  margin-bottom: 24px;
}

.peer-rankings {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.peer-rankings h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.ranking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.ranking-item .rank {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
  width: 50px;
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

/* Regional Stats */
.regional-stats {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
  height: 100%;
}

/* Technology Recommendations */
.tech-recommendations {
  background: #fafafa;
  border-radius: 8px;
  padding: 20px;
  height: 100%;
}

.tech-recommendations h4 {
  margin: 0 0 16px 0;
  color: #303133;
}

.tech-gap-item {
  margin-bottom: 20px;
  padding: 12px;
  background: white;
  border-radius: 8px;
}

.tech-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tech-name {
  font-weight: 600;
  color: #303133;
}

.tech-progress {
  margin: 12px 0;
}

.tech-impact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

/* Opportunity Summary */
.opportunity-summary {
  background: linear-gradient(135deg, #f0f9ff 0%, #ecfdf5 100%);
  border-radius: 12px;
  padding: 20px;
  height: 100%;
  text-align: center;
}

.opportunity-summary h4 {
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