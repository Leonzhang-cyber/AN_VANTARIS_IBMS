<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
          <span class="loading-title">Asset Analytics</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Advanced Asset Performance Analytics & Insights</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="asset-analytics-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><DataAnalysis /></el-icon>
          Asset Analytics
        </h1>
        <div class="page-subtitle">Advanced analytics, performance insights, and predictive intelligence</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="openInsightsDialog">
          <el-icon><Cpu /></el-icon> AI Insights
        </el-button>
        <el-button @click="exportData">
          <el-icon><Download /></el-icon> Export
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalAssets }}</div>
          <div class="stat-label">Total Assets</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.anomaliesDetected }}</div>
          <div class="stat-label">Anomalies Detected</div>
          <div class="stat-trend up">↑ {{ stats.anomalyTrend }}% vs last month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.predictiveAlerts }}</div>
          <div class="stat-label">Predictive Alerts</div>
          <div class="stat-trend down">Action required</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Opportunity /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.optimizationPotential }}%</div>
          <div class="stat-label">Optimization Potential</div>
          <div class="stat-trend up">{{ stats.potentialValue }}M potential savings</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Overall Asset Health</div>
        <div class="metric-value">{{ metrics.overallHealth }}<span class="metric-unit">%</span></div>
        <div class="metric-trend" :class="metrics.healthTrend > 0 ? 'positive' : 'negative'">
          {{ metrics.healthTrend > 0 ? '↑' : '↓' }} {{ Math.abs(metrics.healthTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Operational Efficiency</div>
        <div class="metric-value">{{ metrics.operationalEfficiency }}<span class="metric-unit">%</span></div>
        <el-progress :percentage="metrics.operationalEfficiency" :stroke-width="8" :color="getEfficiencyColor(metrics.operationalEfficiency)" />
      </div>
      <div class="metric-card">
        <div class="metric-title">Asset Utilization</div>
        <div class="metric-value">{{ metrics.utilization }}<span class="metric-unit">%</span></div>
        <div class="metric-sub">Peak: {{ metrics.peakUtilization }}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Failure Prediction Rate</div>
        <div class="metric-value">{{ metrics.predictionAccuracy }}<span class="metric-unit">%</span></div>
        <div class="metric-trend positive">↑ {{ metrics.accuracyGrowth }}% improvement</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Asset Performance Trends</span>
          <span class="chart-subtitle">Health score evolution</span>
        </div>
        <div class="chart-container" ref="performanceTrendChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Anomaly Detection Heatmap</span>
          <span class="chart-subtitle">Recent anomalies by asset</span>
        </div>
        <div class="chart-container" ref="heatmapChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Predictive Failure Analysis</span>
          <span class="chart-subtitle">Failure probability by asset category</span>
        </div>
        <div class="chart-container" ref="predictiveChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cost & Performance Correlation</span>
          <span class="chart-subtitle">Maintenance cost vs performance</span>
        </div>
        <div class="chart-container" ref="correlationChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Top Performing Assets</span>
          <span class="chart-subtitle">Health score leaderboard</span>
        </div>
        <div class="chart-container" ref="topAssetsChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Degradation Rate Analysis</span>
          <span class="chart-subtitle">Accelerating degradation alerts</span>
        </div>
        <div class="chart-container" ref="degradationChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
            v-model="searchText"
            placeholder="Search by asset name or tag..."
            style="width: 220px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="categoryFilter" placeholder="Category" clearable style="width: 140px">
          <el-option v-for="c in uniqueCategories" :key="c" :label="c" :value="c" />
        </el-select>
        <el-select v-model="healthFilter" placeholder="Health Status" clearable style="width: 140px">
          <el-option label="Critical (<50%)" value="critical" />
          <el-option label="Warning (50-70%)" value="warning" />
          <el-option label="Normal (70-85%)" value="normal" />
          <el-option label="Optimal (>85%)" value="optimal" />
        </el-select>
        <el-select v-model="anomalyFilter" placeholder="Anomaly Status" clearable style="width: 130px">
          <el-option label="Has Anomalies" value="has" />
          <el-option label="No Anomalies" value="none" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Analytics Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Asset Analytics Dashboard</span>
        <el-button size="small" @click="viewAllAssets">View All →</el-button>
      </div>
      <el-table :data="paginatedAssets" stripe style="width: 100%" v-loading="tableLoading"
                @row-click="viewAssetDetail">
        <el-table-column prop="tag" label="Asset Tag" width="120" />
        <el-table-column prop="name" label="Asset Name" min-width="180" />
        <el-table-column prop="category" label="Category" width="120">
          <template #default="{ row }">
            <el-tag :type="getCategoryTagType(row.category)" size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="healthScore" label="Health Score" width="140">
          <template #default="{ row }">
            <el-progress :percentage="row.healthScore" :stroke-width="8" :color="getHealthColor(row.healthScore)" />
          </template>
        </el-table-column>
        <el-table-column prop="performance" label="Performance" width="120">
          <template #default="{ row }">
            <el-rate v-model="row.performance" disabled show-score text-color="#ff9900" score-template="{value} pts" />
          </template>
        </el-table-column>
        <el-table-column prop="anomalies" label="Anomalies" width="100">
          <template #default="{ row }">
            <el-tag :type="row.anomalies > 0 ? 'danger' : 'success'" size="small">
              {{ row.anomalies }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="failureProbability" label="Failure Risk" width="130">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.failureProbability)" size="small">
              {{ row.failureProbability }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nextMaintenance" label="Next Maintenance" width="120" />
        <el-table-column prop="trend" label="Trend" width="100">
          <template #default="{ row }">
            <el-tag :type="row.trend === 'improving' ? 'success' : (row.trend === 'declining' ? 'danger' : 'info')" size="small">
              {{ row.trend === 'improving' ? '↑ Improving' : (row.trend === 'declining' ? '↓ Declining' : '→ Stable') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="viewAssetDetail(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="totalRecords"
            layout="total, sizes, prev, pager, next"
            background
        />
      </div>
    </div>

    <!-- Asset Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedAsset?.name" width="1000px" class="analytics-dialog">
      <div v-if="selectedAsset" class="asset-analytics-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getHealthColor(selectedAsset.healthScore) }">
              {{ selectedAsset.healthScore }}%
            </div>
            <div class="detail-stat-label">Health Score</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.performance }}%</div>
            <div class="detail-stat-label">Performance</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.failureProbability }}%</div>
            <div class="detail-stat-label">Failure Risk</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedAsset.mttr }} hrs</div>
            <div class="detail-stat-label">MTTR</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Asset Tag">{{ selectedAsset.tag }}</el-descriptions-item>
          <el-descriptions-item label="Category">{{ selectedAsset.category }}</el-descriptions-item>
          <el-descriptions-item label="Manufacturer">{{ selectedAsset.manufacturer }}</el-descriptions-item>
          <el-descriptions-item label="Model">{{ selectedAsset.model }}</el-descriptions-item>
          <el-descriptions-item label="Location">{{ selectedAsset.location }}</el-descriptions-item>
          <el-descriptions-item label="Install Date">{{ selectedAsset.installDate }}</el-descriptions-item>
          <el-descriptions-item label="Last Maintenance">{{ selectedAsset.lastMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Next Maintenance">{{ selectedAsset.nextMaintenance }}</el-descriptions-item>
          <el-descriptions-item label="Trend">
            <el-tag :type="selectedAsset.trend === 'improving' ? 'success' : (selectedAsset.trend === 'declining' ? 'danger' : 'info')" size="small">
              {{ selectedAsset.trend }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- Performance Metrics -->
        <div class="detail-section">
          <div class="section-title">Performance Metrics</div>
          <el-table :data="selectedAsset.performanceMetrics" border stripe>
            <el-table-column prop="metric" label="Metric" width="200" />
            <el-table-column prop="value" label="Value" width="120" />
            <el-table-column prop="unit" label="Unit" width="80" />
            <el-table-column prop="target" label="Target" width="120" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'Good' ? 'success' : (row.status === 'Warning' ? 'warning' : 'danger')" size="small">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="trend" label="Trend" width="100">
              <template #default="{ row }">
                <el-tag :type="row.trend === 'up' ? 'success' : (row.trend === 'down' ? 'danger' : 'info')" size="small">
                  {{ row.trend === 'up' ? '↑ Improving' : (row.trend === 'down' ? '↓ Declining' : '→ Stable') }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Anomaly History -->
        <div class="detail-section" v-if="selectedAsset.anomalyHistory.length > 0">
          <div class="section-title">Anomaly Detection History</div>
          <el-table :data="selectedAsset.anomalyHistory" border stripe>
            <el-table-column prop="date" label="Date" width="150" />
            <el-table-column prop="type" label="Type" width="150" />
            <el-table-column prop="description" label="Description" min-width="250" />
            <el-table-column prop="severity" label="Severity" width="100">
              <template #default="{ row }">
                <el-tag :type="row.severity === 'High' ? 'danger' : (row.severity === 'Medium' ? 'warning' : 'info')" size="small">
                  {{ row.severity }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="resolved" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="row.resolved ? 'success' : 'danger'" size="small">
                  {{ row.resolved ? 'Resolved' : 'Open' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- AI Insights -->
        <div class="detail-section">
          <div class="section-title">AI-Powered Insights</div>
          <el-alert
              :title="selectedAsset.aiInsights.title"
              :type="selectedAsset.aiInsights.type"
              :closable="false"
              show-icon
          >
            <template #default>
              <div class="insights-content">
                <p>{{ selectedAsset.aiInsights.description }}</p>
                <div class="insights-recommendations">
                  <strong>Recommendations:</strong>
                  <ul>
                    <li v-for="rec in selectedAsset.aiInsights.recommendations" :key="rec">{{ rec }}</li>
                  </ul>
                </div>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- Performance Trend Chart -->
        <div class="detail-section">
          <div class="section-title">Performance Trend (Last 12 Months)</div>
          <div class="trend-chart" ref="assetTrendChartEl"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="scheduleMaintenance(selectedAsset)">Schedule Maintenance</el-button>
        <el-button type="warning" @click="runDiagnostics(selectedAsset)">Run Diagnostics</el-button>
      </template>
    </el-dialog>

    <!-- AI Insights Dialog -->
    <el-dialog v-model="insightsDialogVisible" title="AI-Powered Insights" width="800px">
      <div class="insights-container">
        <div class="insights-summary">
          <h3>Executive Summary</h3>
          <p>Based on analysis of {{ stats.totalAssets }} assets across {{ uniqueCategories.length }} categories, the system has identified key opportunities for optimization and risk mitigation.</p>
        </div>

        <div class="insights-grid">
          <div class="insight-card">
            <div class="insight-icon red">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="insight-content">
              <div class="insight-title">Critical Alerts</div>
              <div class="insight-value">{{ stats.predictiveAlerts }}</div>
              <div class="insight-desc">Assets requiring immediate attention</div>
            </div>
          </div>
          <div class="insight-card">
            <div class="insight-icon orange">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="insight-content">
              <div class="insight-title">Optimization Potential</div>
              <div class="insight-value">{{ stats.optimizationPotential }}%</div>
              <div class="insight-desc">Potential efficiency improvement</div>
            </div>
          </div>
          <div class="insight-card">
            <div class="insight-icon green">
              <el-icon><Money /></el-icon>
            </div>
            <div class="insight-content">
              <div class="insight-title">Cost Savings</div>
              <div class="insight-value">$2.5M</div>
              <div class="insight-desc">Annual potential savings</div>
            </div>
          </div>
          <div class="insight-card">
            <div class="insight-icon blue">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="insight-content">
              <div class="insight-title">Lifetime Extension</div>
              <div class="insight-value">3.5 yrs</div>
              <div class="insight-desc">Average asset life extension</div>
            </div>
          </div>
        </div>

        <el-divider />

        <div class="recommendations-list">
          <h3>Top Recommendations</h3>
          <el-timeline>
            <el-timeline-item
                v-for="rec in recommendations"
                :key="rec.id"
                :timestamp="rec.priority"
                :type="rec.type"
                placement="top"
            >
              <div class="recommendation-item">
                <div class="recommendation-title">{{ rec.title }}</div>
                <div class="recommendation-description">{{ rec.description }}</div>
                <div class="recommendation-impact">Expected Impact: {{ rec.impact }}</div>
              </div>
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="insightsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportInsights">Export Insights</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, TrendCharts, DataLine, Timer, Opportunity, Cpu, Download, Refresh,
  Search, RefreshLeft, Warning, Money, Clock
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading asset analytics data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading asset data...',
  'Analyzing performance metrics...',
  'Detecting anomalies...',
  'Generating AI insights...',
  'Almost ready...'
]

// ==================== Types ====================
interface PerformanceMetric {
  metric: string
  value: number
  unit: string
  target: number
  status: string
  trend: string
}

interface AnomalyHistory {
  date: string
  type: string
  description: string
  severity: string
  resolved: boolean
}

interface AIInsights {
  title: string
  type: 'success' | 'warning' | 'info' | 'error'
  description: string
  recommendations: string[]
}

interface AnalyticsAsset {
  id: number
  tag: string
  name: string
  category: string
  manufacturer: string
  model: string
  location: string
  healthScore: number
  performance: number
  anomalies: number
  failureProbability: number
  mttr: number
  installDate: string
  lastMaintenance: string
  nextMaintenance: string
  trend: string
  performanceMetrics: PerformanceMetric[]
  anomalyHistory: AnomalyHistory[]
  aiInsights: AIInsights
}

// ==================== Mock Data (65 assets) ====================
const generateAnalyticsData = (): AnalyticsAsset[] => {
  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Switchgear', 'Server', 'Storage', 'Network']
  const manufacturers = {
    'UPS': ['Schneider Electric', 'Eaton', 'Vertiv', 'ABB'],
    'Generator': ['Caterpillar', 'Cummins', 'MTU', 'Kohler'],
    'CRAC': ['Stulz', 'Vertiv', 'Schneider Electric', 'Daikin'],
    'Chiller': ['Trane', 'Carrier', 'York', 'Daikin'],
    'Switchgear': ['ABB', 'Siemens', 'Schneider Electric', 'Eaton'],
    'Server': ['Dell', 'HP', 'Cisco', 'Lenovo'],
    'Storage': ['Dell EMC', 'NetApp', 'Pure Storage', 'HPE'],
    'Network': ['Cisco', 'Juniper', 'Arista', 'Huawei']
  }
  const locations = ['Data Center A', 'Data Center B', 'Server Room 1', 'Server Room 2', 'Generator Room', 'UPS Room', 'Chiller Plant']

  const assets: AnalyticsAsset[] = []

  for (let i = 1; i <= 65; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)]
    const manufacturerList = manufacturers[category as keyof typeof manufacturers] || ['Generic']
    const manufacturer = manufacturerList[Math.floor(Math.random() * manufacturerList.length)]

    const installDate = new Date()
    installDate.setMonth(installDate.getMonth() - Math.random() * 120)
    const installDateStr = installDate.toISOString().slice(0, 10)

    const ageYears = (new Date().getTime() - installDate.getTime()) / (1000 * 60 * 60 * 24 * 365)
    let healthScore = Math.max(40, Math.min(98, 100 - ageYears * 6 + (Math.random() * 15 - 7.5)))
    healthScore = Math.round(healthScore)

    const performance = Math.min(100, Math.max(60, healthScore + (Math.random() * 10 - 5)))
    const anomalies = Math.floor(Math.random() * 5)
    const failureProbability = Math.min(95, Math.max(5, Math.round(100 - healthScore + (Math.random() * 15 - 7.5))))
    const mttr = parseFloat((2 + Math.random() * 8).toFixed(1))

    let trend = 'stable'
    if (healthScore > 75 && Math.random() > 0.7) trend = 'improving'
    else if (healthScore < 65 && Math.random() > 0.6) trend = 'declining'

    // Performance metrics
    const performanceMetrics: PerformanceMetric[] = [
      { metric: 'Operational Efficiency', value: Math.round(65 + Math.random() * 30), unit: '%', target: 85, status: '', trend: Math.random() > 0.6 ? 'up' : (Math.random() > 0.5 ? 'stable' : 'down') },
      { metric: 'Energy Consumption', value: Math.round(100 + Math.random() * 200), unit: 'kWh', target: 200, status: '', trend: Math.random() > 0.6 ? 'down' : (Math.random() > 0.5 ? 'stable' : 'up') },
      { metric: 'Downtime', value: Math.round(Math.random() * 10) / 10, unit: 'hrs/month', target: 0.5, status: '', trend: Math.random() > 0.7 ? 'down' : (Math.random() > 0.5 ? 'stable' : 'up') },
      { metric: 'Maintenance Cost', value: Math.round(500 + Math.random() * 2000), unit: '$/month', target: 1500, status: '', trend: Math.random() > 0.6 ? 'down' : (Math.random() > 0.5 ? 'stable' : 'up') }
    ]

    performanceMetrics.forEach(m => {
      if (m.metric === 'Operational Efficiency') {
        m.status = m.value >= 85 ? 'Good' : (m.value >= 70 ? 'Warning' : 'Critical')
      } else if (m.metric === 'Energy Consumption') {
        m.status = m.value <= 200 ? 'Good' : (m.value <= 300 ? 'Warning' : 'Critical')
      } else if (m.metric === 'Downtime') {
        m.status = m.value <= 0.5 ? 'Good' : (m.value <= 1 ? 'Warning' : 'Critical')
      } else {
        m.status = m.value <= 1500 ? 'Good' : (m.value <= 2500 ? 'Warning' : 'Critical')
      }
    })

    // Anomaly history
    const anomalyHistory: AnomalyHistory[] = []
    for (let a = 0; a < anomalies; a++) {
      anomalyHistory.push({
        date: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        type: Math.random() > 0.5 ? 'Temperature' : 'Vibration',
        description: `Abnormal ${Math.random() > 0.5 ? 'temperature' : 'vibration'} detected beyond threshold`,
        severity: Math.random() > 0.7 ? 'High' : (Math.random() > 0.5 ? 'Medium' : 'Low'),
        resolved: Math.random() > 0.3
      })
    }

    // AI Insights
    let aiInsights: AIInsights
    if (healthScore < 60) {
      aiInsights = {
        title: 'Critical Health Alert',
        type: 'error',
        description: `Asset health has deteriorated to ${healthScore}%, significantly below optimal range. Predictive models indicate high risk of failure within next 90 days.`,
        recommendations: [
          'Schedule immediate comprehensive maintenance',
          'Review operating conditions and environmental factors',
          'Prepare replacement budget for next fiscal year',
          'Increase monitoring frequency to daily'
        ]
      }
    } else if (healthScore < 75) {
      aiInsights = {
        title: 'Performance Degradation Detected',
        type: 'warning',
        description: `Asset health has declined ${100 - healthScore}% since installation. Degradation rate is ${(100 - healthScore) / Math.max(1, ageYears)}% per year, which is above industry average.`,
        recommendations: [
          'Schedule preventive maintenance within 30 days',
          'Analyze root cause of accelerated degradation',
          'Review maintenance logs for missed activities',
          'Consider part replacement for critical components'
        ]
      }
    } else {
      aiInsights = {
        title: 'Optimal Performance',
        type: 'success',
        description: `Asset is performing at ${healthScore}% health, above industry average. Maintenance practices are effective and degradation rate is controlled.`,
        recommendations: [
          'Continue current maintenance schedule',
          'Document best practices for knowledge sharing',
          'Monitor trend for early detection of changes',
          'Consider extending maintenance intervals if trend continues'
        ]
      }
    }

    assets.push({
      id: i,
      tag: `${category.substring(0, 3).toUpperCase()}-${String(i).padStart(4, '0')}`,
      name: `${category} ${String.fromCharCode(64 + Math.ceil(i / 8))}${((i - 1) % 8) + 1}`,
      category: category,
      manufacturer: manufacturer,
      model: `${category}-${Math.floor(Math.random() * 1000)}`,
      location: locations[Math.floor(Math.random() * locations.length)],
      healthScore: healthScore,
      performance: Math.round(performance),
      anomalies: anomalies,
      failureProbability: failureProbability,
      mttr: mttr,
      installDate: installDateStr,
      lastMaintenance: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      nextMaintenance: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
      trend: trend,
      performanceMetrics: performanceMetrics,
      anomalyHistory: anomalyHistory,
      aiInsights: aiInsights
    })
  }

  return assets
}

const assets = ref<AnalyticsAsset[]>(generateAnalyticsData())

// ==================== State ====================
const searchText = ref('')
const categoryFilter = ref('')
const healthFilter = ref('')
const anomalyFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const insightsDialogVisible = ref(false)
const selectedAsset = ref<AnalyticsAsset | null>(null)

// Chart refs
let performanceTrendChart: echarts.ECharts | null = null
let heatmapChart: echarts.ECharts | null = null
let predictiveChart: echarts.ECharts | null = null
let correlationChart: echarts.ECharts | null = null
let topAssetsChart: echarts.ECharts | null = null
let degradationChart: echarts.ECharts | null = null
let assetTrendChart: echarts.ECharts | null = null

const performanceTrendChartEl = ref<HTMLElement | null>(null)
const heatmapChartEl = ref<HTMLElement | null>(null)
const predictiveChartEl = ref<HTMLElement | null>(null)
const correlationChartEl = ref<HTMLElement | null>(null)
const topAssetsChartEl = ref<HTMLElement | null>(null)
const degradationChartEl = ref<HTMLElement | null>(null)
const assetTrendChartEl = ref<HTMLElement | null>(null)

// ==================== Computed ====================
const stats = computed(() => {
  const totalAssets = assets.value.length
  const anomaliesDetected = assets.value.reduce((sum, a) => sum + a.anomalies, 0)
  const predictiveAlerts = assets.value.filter(a => a.failureProbability > 70).length
  const optimizationPotential = Math.round(100 - assets.value.reduce((sum, a) => sum + a.healthScore, 0) / totalAssets)
  const anomalyTrend = 12.5

  return {
    totalAssets,
    anomaliesDetected,
    anomalyTrend,
    predictiveAlerts,
    optimizationPotential,
    potentialValue: 3.2
  }
})

const metrics = computed(() => {
  const overallHealth = Math.round(assets.value.reduce((sum, a) => sum + a.healthScore, 0) / assets.value.length)
  const operationalEfficiency = Math.round(assets.value.reduce((sum, a) => sum + a.performance, 0) / assets.value.length)
  const utilization = Math.round(65 + Math.random() * 20)
  const peakUtilization = utilization + Math.round(Math.random() * 15)
  const predictionAccuracy = 85 + Math.random() * 10

  return {
    overallHealth,
    healthTrend: -1.5,
    operationalEfficiency,
    utilization,
    peakUtilization,
    predictionAccuracy: Math.round(predictionAccuracy),
    accuracyGrowth: 4.2
  }
})

const uniqueCategories = computed(() => {
  return [...new Set(assets.value.map(a => a.category))]
})

const filteredAssets = computed(() => {
  let filtered = [...assets.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(a =>
        a.name.toLowerCase().includes(search) ||
        a.tag.toLowerCase().includes(search) ||
        a.location.toLowerCase().includes(search)
    )
  }

  if (categoryFilter.value) {
    filtered = filtered.filter(a => a.category === categoryFilter.value)
  }

  if (healthFilter.value) {
    if (healthFilter.value === 'optimal') filtered = filtered.filter(a => a.healthScore > 85)
    else if (healthFilter.value === 'normal') filtered = filtered.filter(a => a.healthScore >= 70 && a.healthScore <= 85)
    else if (healthFilter.value === 'warning') filtered = filtered.filter(a => a.healthScore >= 50 && a.healthScore < 70)
    else if (healthFilter.value === 'critical') filtered = filtered.filter(a => a.healthScore < 50)
  }

  if (anomalyFilter.value === 'has') {
    filtered = filtered.filter(a => a.anomalies > 0)
  } else if (anomalyFilter.value === 'none') {
    filtered = filtered.filter(a => a.anomalies === 0)
  }

  return filtered
})

const totalRecords = computed(() => filteredAssets.value.length)

const paginatedAssets = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredAssets.value.slice(start, end)
})

const recommendations = computed(() => {
  return [
    { id: 1, priority: 'High', type: 'danger', title: 'Critical Assets Requiring Immediate Attention', description: '5 assets have health score below 50% and failure probability > 80%', impact: 'Prevent potential $500K downtime cost' },
    { id: 2, priority: 'Medium', type: 'warning', title: 'Predictive Maintenance Opportunity', description: '12 assets show accelerated degradation patterns', impact: 'Extend asset life by 3-5 years' },
    { id: 3, priority: 'Medium', type: 'warning', title: 'Energy Efficiency Improvement', description: 'Older CRAC units consuming 25% more energy than newer models', impact: 'Save $120K annually in energy costs' },
    { id: 4, priority: 'Low', type: 'info', title: 'Spare Parts Optimization', description: 'Critical spares inventory can be optimized based on failure predictions', impact: 'Reduce inventory holding cost by 15%' }
  ]
})

// ==================== Helper Functions ====================
const getHealthColor = (health: number): string => {
  if (health >= 85) return '#22c55e'
  if (health >= 70) return '#3b82f6'
  if (health >= 50) return '#f59e0b'
  return '#ef4444'
}

const getEfficiencyColor = (efficiency: number): string => {
  if (efficiency >= 85) return '#22c55e'
  if (efficiency >= 70) return '#3b82f6'
  if (efficiency >= 50) return '#f59e0b'
  return '#ef4444'
}

const getRiskTagType = (risk: number): string => {
  if (risk > 70) return 'danger'
  if (risk > 40) return 'warning'
  return 'info'
}

const getCategoryTagType = (category: string): string => {
  const map: Record<string, string> = {
    'UPS': 'primary', 'Generator': 'warning', 'CRAC': 'info', 'Chiller': 'danger',
    'Switchgear': 'success', 'Server': '', 'Storage': '', 'Network': ''
  }
  return map[category] || 'info'
}

const resetFilters = () => {
  searchText.value = ''
  categoryFilter.value = ''
  healthFilter.value = ''
  anomalyFilter.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initPerformanceTrendChart = () => {
  if (!performanceTrendChartEl.value) return
  if (performanceTrendChart) {
    performanceTrendChart.dispose()
    performanceTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const healthTrend = [85, 84, 83, 82, 81, 80, 79, 78, 77, 76, 75, 74]

  performanceTrendChart = echarts.init(performanceTrendChartEl.value)
  performanceTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 60, max: 100 },
    series: [{
      type: 'line',
      data: healthTrend,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1, color: '#3b82f6' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initHeatmapChart = () => {
  if (!heatmapChartEl.value) return
  if (heatmapChart) {
    heatmapChart.dispose()
    heatmapChart = null
  }

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
  const data = []

  for (let i = 0; i < weeks.length; i++) {
    for (let j = 0; j < days.length; j++) {
      data.push([j, i, Math.floor(Math.random() * 100)])
    }
  }

  heatmapChart = echarts.init(heatmapChartEl.value)
  heatmapChart.setOption({
    tooltip: { position: 'top' },
    grid: { height: '70%', top: 30, left: 60, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: days, splitArea: { show: true } },
    yAxis: { type: 'category', data: weeks, splitArea: { show: true } },
    visualMap: { min: 0, max: 100, calculable: true, orient: 'horizontal', left: 'center', bottom: 0,
      inRange: { color: ['#22c55e', '#f59e0b', '#ef4444'] } },
    series: [{
      name: 'Anomaly Score',
      type: 'heatmap',
      data: data,
      label: { show: true },
      emphasis: { itemStyle: { shadowBlur: 10 } }
    }]
  })
}

const initPredictiveChart = () => {
  if (!predictiveChartEl.value) return
  if (predictiveChart) {
    predictiveChart.dispose()
    predictiveChart = null
  }

  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Switchgear', 'Server']
  const probabilities = [25, 35, 20, 45, 30, 15]

  predictiveChart = echarts.init(predictiveChartEl.value)
  predictiveChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Failure Probability (%)', max: 100 },
    series: [{
      type: 'bar',
      data: probabilities,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 40) return '#ef4444'
          if (value > 25) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initCorrelationChart = () => {
  if (!correlationChartEl.value) return
  if (correlationChart) {
    correlationChart.dispose()
    correlationChart = null
  }

  // Scatter plot data: [maintenance cost, performance score]
  const data = assets.value.slice(0, 30).map(a => [a.healthScore, a.mttr * 1000])

  correlationChart = echarts.init(correlationChartEl.value)
  correlationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'value', name: 'Health Score (%)' },
    yAxis: { type: 'value', name: 'Maintenance Cost ($)' },
    series: [{
      type: 'scatter',
      data: data,
      symbolSize: 10,
      itemStyle: { color: '#3b82f6' },
      label: { show: false }
    }]
  })
}

const initTopAssetsChart = () => {
  if (!topAssetsChartEl.value) return
  if (topAssetsChart) {
    topAssetsChart.dispose()
    topAssetsChart = null
  }

  const topAssets = assets.value.sort((a, b) => b.healthScore - a.healthScore).slice(0, 8)
  const names = topAssets.map(a => a.name.length > 10 ? a.name.slice(0, 10) + '...' : a.name)
  const scores = topAssets.map(a => a.healthScore)

  topAssetsChart = echarts.init(topAssetsChartEl.value)
  topAssetsChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 80, max: 100 },
    series: [{
      type: 'bar',
      data: scores,
      itemStyle: { borderRadius: [4, 4, 0, 0], color: '#22c55e' },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initDegradationChart = () => {
  if (!degradationChartEl.value) return
  if (degradationChart) {
    degradationChart.dispose()
    degradationChart = null
  }

  const categories = ['UPS', 'Generator', 'CRAC', 'Chiller', 'Switchgear']
  const rates = [8.5, 12.3, 6.8, 15.2, 7.5]

  degradationChart = echarts.init(degradationChartEl.value)
  degradationChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: categories },
    yAxis: { type: 'value', name: 'Degradation Rate (%/year)' },
    series: [{
      type: 'bar',
      data: rates,
      itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: (params: any) => {
          const value = params.value
          if (value > 10) return '#ef4444'
          if (value > 7) return '#f59e0b'
          return '#22c55e'
        }
      },
      label: { show: true, position: 'top', formatter: '{c}%/yr' }
    }]
  })
}

const initAssetTrendChart = () => {
  if (!assetTrendChartEl.value || !selectedAsset.value) return
  if (assetTrendChart) {
    assetTrendChart.dispose()
    assetTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const scores = [85, 84, 83, 82, 81, selectedAsset.value.healthScore - 2, selectedAsset.value.healthScore - 1, selectedAsset.value.healthScore, selectedAsset.value.healthScore]

  assetTrendChart = echarts.init(assetTrendChartEl.value)
  assetTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months.slice(0, scores.length) },
    yAxis: { type: 'value', name: 'Health Score (%)', min: 40, max: 100 },
    series: [{
      type: 'line',
      data: scores,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initPerformanceTrendChart()
    initHeatmapChart()
    initPredictiveChart()
    initCorrelationChart()
    initTopAssetsChart()
    initDegradationChart()
  })
}

// ==================== Actions ====================
const viewAssetDetail = (asset: AnalyticsAsset) => {
  selectedAsset.value = asset
  detailDialogVisible.value = true
  nextTick(() => initAssetTrendChart())
}

const viewAllAssets = () => {
  ElMessage.info('Viewing all assets')
}

const scheduleMaintenance = (asset: AnalyticsAsset | null) => {
  if (asset) {
    ElMessage.success(`Maintenance scheduled for ${asset.name}`)
  }
}

const runDiagnostics = (asset: AnalyticsAsset | null) => {
  if (asset) {
    ElMessage.success(`Running diagnostics for ${asset.name}...`)
    setTimeout(() => {
      ElMessage.success('Diagnostics completed')
    }, 2000)
  }
}

const openInsightsDialog = () => {
  insightsDialogVisible.value = true
}

const exportInsights = () => {
  ElMessage.success('Exporting AI insights...')
  setTimeout(() => {
    ElMessage.success('Insights exported successfully')
  }, 1500)
}

const exportData = () => {
  ElMessage.success('Exporting analytics data...')
  setTimeout(() => {
    ElMessage.success('Data exported successfully')
  }, 1000)
}

const refreshData = async () => {
  refreshing.value = true
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  tableLoading.value = false
  refreshCharts()
  ElMessage.success('Data refreshed')
}

// 窗口缩放处理
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    const charts = [performanceTrendChart, heatmapChart, predictiveChart, correlationChart, topAssetsChart, degradationChart, assetTrendChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([searchText, categoryFilter, healthFilter, anomalyFilter], () => {
  currentPage.value = 1
})

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => refreshCharts())
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (resizeTimer) clearTimeout(resizeTimer)
  window.removeEventListener('resize', handleResize)
  const charts = [performanceTrendChart, heatmapChart, predictiveChart, correlationChart, topAssetsChart, degradationChart, assetTrendChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.asset-analytics-page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 24px;
}

* {
  scrollbar-width: thin;
}
*::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
*::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

/* Loading Screen - reuse from previous pages */
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
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 28px;
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
  width: 280px;
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 0 auto 16px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec489a);
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

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.red { background: #fee2e2; color: #ef4444; }

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 4px;
}

.stat-trend.up { color: #ef4444; }
.stat-trend.down { color: #22c55e; }

/* Metrics Row */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.metric-title {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.metric-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
}

.metric-trend {
  font-size: 12px;
  margin: 8px 0 4px;
}

.metric-trend.positive { color: #22c55e; }
.metric-trend.negative { color: #ef4444; }

.metric-sub {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

/* Charts Row */
.charts-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  flex: 1;
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.chart-subtitle {
  font-size: 12px;
  color: #64748b;
}

.chart-container {
  height: 280px;
  width: 100%;
}

/* Filter Bar */
.filter-bar {
  background: white;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.filter-left {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Table Container */
.table-container {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* Asset Analytics Detail */
.asset-analytics-detail {
  padding: 8px;
}

.detail-header-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 16px;
}

.detail-stat {
  text-align: center;
}

.detail-stat-value {
  font-size: 24px;
  font-weight: 700;
}

.detail-stat-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #3b82f6;
}

.insights-content {
  margin-top: 8px;
}

.insights-recommendations {
  margin-top: 12px;
}

.insights-recommendations ul {
  margin: 8px 0 0 20px;
  padding: 0;
}

.insights-recommendations li {
  margin: 4px 0;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

/* Insights Dialog */
.insights-container {
  padding: 8px;
}

.insights-summary {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.insights-summary h3 {
  margin: 0 0 8px 0;
  color: #1e293b;
}

.insights-summary p {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.insight-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.insight-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.insight-icon.red { background: #fee2e2; color: #ef4444; }
.insight-icon.orange { background: #fef3c7; color: #f59e0b; }
.insight-icon.green { background: #dcfce7; color: #22c55e; }
.insight-icon.blue { background: #eef2ff; color: #3b82f6; }

.insight-content {
  flex: 1;
}

.insight-title {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.insight-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.insight-desc {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

.recommendations-list {
  margin-top: 16px;
}

.recommendations-list h3 {
  margin: 0 0 16px 0;
  color: #1e293b;
}

.recommendation-item {
  padding: 8px 0;
}

.recommendation-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.recommendation-description {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.recommendation-impact {
  font-size: 12px;
  color: #22c55e;
  margin-top: 4px;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid, .metrics-row {
    grid-template-columns: repeat(2, 1fr);
  }
  .charts-row {
    flex-direction: column;
  }
  .detail-header-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .insights-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid, .metrics-row {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-left {
    flex-direction: column;
    width: 100%;
  }
  .filter-left .el-input,
  .filter-left .el-select {
    width: 100% !important;
  }
  .insights-grid {
    grid-template-columns: 1fr;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
}
:deep(.el-table th.el-table__cell) {
  background-color: #f8fafc !important;
  color: #334155;
}
:deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background-color: #f0f7ff;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #3b82f6;
}
:deep(.el-dialog__body) {
  max-height: 600px;
  overflow-y: auto;
}
:deep(.el-progress-bar__inner) {
  border-radius: 4px;
}
:deep(.el-rate) {
  display: inline-flex;
  align-items: center;
}
:deep(.el-rate__text) {
  margin-left: 8px;
  font-size: 12px;
}
</style>