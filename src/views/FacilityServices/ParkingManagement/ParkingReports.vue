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
          <span class="loading-title">Parking Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Parking Analytics & Reporting Hub</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="parking-reports-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <div class="title-icon">
            <el-icon><DataAnalysis /></el-icon>
          </div>
          Parking Reports
        </h1>
        <div class="page-subtitle">Generate and analyze parking occupancy, revenue, and violation reports</div>
      </div>
      <div class="header-actions">
        <el-button class="primary-btn" @click="openGenerateDialog">
          <el-icon><Plus /></el-icon>
          <span>Generate Report</span>
        </el-button>
        <el-button class="secondary-btn" @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalReports }}</div>
          <div class="stat-label">Total Reports</div>
          <div class="stat-trend">+{{ stats.reportGrowth }}% this month</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.generatedReports }}</div>
          <div class="stat-label">Generated Reports</div>
          <div class="stat-trend">{{ stats.generatedPercent }}% of total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.scheduledReports }}</div>
          <div class="stat-label">Scheduled Reports</div>
          <div class="stat-trend">Next: Today 09:00</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.averageOccupancy }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Avg Occupancy</div>
          <div class="stat-trend up">↑ 5.2% vs last month</div>
        </div>
      </div>
    </div>

    <!-- Report Templates Section -->
    <div class="section-header">
      <div class="section-title-wrapper">
        <span class="section-icon">⚡</span>
        <h2 class="section-title">Quick Reports</h2>
      </div>
      <div class="section-actions">
        <div class="search-wrapper">
          <el-icon class="search-icon"><Search /></el-icon>
          <el-input
              v-model="searchText"
              placeholder="Search reports..."
              class="search-input"
              clearable
          />
        </div>
        <el-select v-model="typeFilter" placeholder="Report Type" clearable class="filter-select" popper-class="custom-select-dropdown">
          <el-option label="📊 Occupancy Report" value="occupancy" />
          <el-option label="💰 Revenue Report" value="revenue" />
          <el-option label="⚠️ Violation Report" value="violation" />
          <el-option label="📈 Utilization Report" value="utilization" />
        </el-select>
      </div>
    </div>

    <!-- Report Templates Grid -->
    <div class="templates-grid">
      <div class="template-card" @click="generateFromTemplate('occupancy')">
        <div class="template-icon occupancy">
          <el-icon><Place /></el-icon>
        </div>
        <h3 class="template-title">Occupancy Report</h3>
        <p class="template-desc">Daily, weekly, and monthly parking occupancy analysis with trend insights</p>
        <div class="template-metrics">
          <div class="metric-chip">
            <span class="metric-label">Peak</span>
            <span class="metric-value">92%</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Average</span>
            <span class="metric-value">68%</span>
          </div>
        </div>
        <div class="template-footer">
          <el-button class="generate-btn">Generate Report →</el-button>
        </div>
      </div>
      <div class="template-card" @click="generateFromTemplate('revenue')">
        <div class="template-icon revenue">
          <el-icon><Money /></el-icon>
        </div>
        <h3 class="template-title">Revenue Report</h3>
        <p class="template-desc">Parking fee collection, revenue analytics, and forecasting</p>
        <div class="template-metrics">
          <div class="metric-chip">
            <span class="metric-label">MTD</span>
            <span class="metric-value">$45.2K</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">YTD</span>
            <span class="metric-value">$156.8K</span>
          </div>
        </div>
        <div class="template-footer">
          <el-button class="generate-btn">Generate Report →</el-button>
        </div>
      </div>
      <div class="template-card" @click="generateFromTemplate('violation')">
        <div class="template-icon violation">
          <el-icon><Warning /></el-icon>
        </div>
        <h3 class="template-title">Violation Report</h3>
        <p class="template-desc">Parking violation statistics, trends, and hotspot analysis</p>
        <div class="template-metrics">
          <div class="metric-chip">
            <span class="metric-label">Total</span>
            <span class="metric-value">142</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">Pending</span>
            <span class="metric-value">38</span>
          </div>
        </div>
        <div class="template-footer">
          <el-button class="generate-btn">Generate Report →</el-button>
        </div>
      </div>
      <div class="template-card" @click="generateFromTemplate('utilization')">
        <div class="template-icon utilization">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <h3 class="template-title">Utilization Report</h3>
        <p class="template-desc">Space utilization, efficiency metrics, and optimization insights</p>
        <div class="template-metrics">
          <div class="metric-chip">
            <span class="metric-label">Turnover</span>
            <span class="metric-value">3.2/day</span>
          </div>
          <div class="metric-chip">
            <span class="metric-label">EV Usage</span>
            <span class="metric-value">45%</span>
          </div>
        </div>
        <div class="template-footer">
          <el-button class="generate-btn">Generate Report →</el-button>
        </div>
      </div>
    </div>

    <!-- Reports Library -->
    <div class="section-header">
      <div class="section-title-wrapper">
        <span class="section-icon">📚</span>
        <h2 class="section-title">Report Library</h2>
      </div>
      <div class="section-actions">
        <div class="date-range-wrapper">
          <el-icon><Calendar /></el-icon>
          <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="→"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              size="default"
              class="date-range-picker"
              :shortcuts="dateShortcuts"
          />
        </div>
      </div>
    </div>

    <div class="reports-grid">
      <div
          v-for="report in paginatedReports"
          :key="report.id"
          class="report-card"
          @click="viewReport(report)"
      >
        <div class="report-card-header">
          <div class="report-icon" :class="report.type">
            <el-icon><Document /></el-icon>
          </div>
          <div class="report-badge" :class="report.type">
            {{ getReportTypeLabel(report.type) }}
          </div>
        </div>
        <div class="report-info">
          <h3 class="report-title">{{ report.title }}</h3>
          <div class="report-meta">
            <span><el-icon><Calendar /></el-icon> {{ report.date }}</span>
            <span><el-icon><User /></el-icon> {{ report.author }}</span>
          </div>
          <div class="report-stats">
            <div class="stat-chip">
              <span>Format</span>
              <strong>{{ report.format.toUpperCase() }}</strong>
            </div>
            <div class="stat-chip">
              <span>Size</span>
              <strong>{{ report.fileSize }} MB</strong>
            </div>
            <div class="stat-chip">
              <span>Zones</span>
              <strong>{{ report.zones.length }}</strong>
            </div>
          </div>
        </div>
        <div class="report-actions" @click.stop>
          <el-tooltip content="View Report" placement="top">
            <el-button class="action-btn" @click="viewReport(report)">
              <el-icon><View /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="Download" placement="top">
            <el-button class="action-btn download" @click="downloadReport(report)">
              <el-icon><Download /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="Share" placement="top">
            <el-button class="action-btn share" @click="shareReport(report)">
              <el-icon><Share /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredReports.length === 0" class="empty-state">
        <div class="empty-icon">📄</div>
        <h3>No reports found</h3>
        <p>Try adjusting your search or filter criteria</p>
        <el-button class="primary-btn" @click="openGenerateDialog">Generate Report</el-button>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredReports.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 12, 18, 24]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateDialogVisible" title="Generate Report" width="580px" class="custom-dialog" destroy-on-close>
      <div class="dialog-header-icon">📊</div>
      <el-form :model="reportForm" label-width="130px" class="report-form">
        <el-form-item label="Report Type">
          <el-select v-model="reportForm.type" class="full-width-select" popper-class="custom-select-dropdown">
            <el-option label="📊 Occupancy Report" value="occupancy" />
            <el-option label="💰 Revenue Report" value="revenue" />
            <el-option label="⚠️ Violation Report" value="violation" />
            <el-option label="📈 Utilization Report" value="utilization" />
            <el-option label="🎨 Custom Report" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Period">
          <div class="period-buttons">
            <el-button
                :type="reportForm.period === 'daily' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.period = 'daily'"
                class="period-btn"
            >Daily</el-button>
            <el-button
                :type="reportForm.period === 'weekly' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.period = 'weekly'"
                class="period-btn"
            >Weekly</el-button>
            <el-button
                :type="reportForm.period === 'monthly' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.period = 'monthly'"
                class="period-btn"
            >Monthly</el-button>
            <el-button
                :type="reportForm.period === 'custom' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.period = 'custom'"
                class="period-btn"
            >Custom</el-button>
          </div>
        </el-form-item>
        <el-form-item label="Date Range" v-if="reportForm.period === 'custom'">
          <el-date-picker
              v-model="reportForm.dateRange"
              type="daterange"
              range-separator="→"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              class="full-width-date"
          />
        </el-form-item>
        <el-form-item label="Zones">
          <el-select v-model="reportForm.zones" multiple placeholder="Select zones" class="full-width-select">
            <el-option label="Zone A" value="Zone A" />
            <el-option label="Zone B" value="Zone B" />
            <el-option label="Zone C" value="Zone C" />
            <el-option label="Zone D" value="Zone D" />
            <el-option label="Zone E" value="Zone E" />
          </el-select>
        </el-form-item>
        <el-form-item label="Format">
          <div class="format-buttons">
            <el-button
                :type="reportForm.format === 'pdf' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.format = 'pdf'"
            >
              <el-icon><Document /></el-icon> PDF
            </el-button>
            <el-button
                :type="reportForm.format === 'excel' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.format = 'excel'"
            >
              <el-icon><DataLine /></el-icon> Excel
            </el-button>
            <el-button
                :type="reportForm.format === 'csv' ? 'primary' : 'default'"
                size="small"
                @click="reportForm.format = 'csv'"
            >
              <el-icon><DataAnalysis /></el-icon> CSV
            </el-button>
          </div>
        </el-form-item>
        <el-form-item label="Schedule">
          <el-switch v-model="reportForm.schedule" active-color="#22c55e" />
          <span v-if="reportForm.schedule" class="schedule-hint">
            Send every
            <el-select v-model="reportForm.scheduleFrequency" size="small" style="width: 100px; margin-left: 8px;">
              <el-option label="Day" value="daily" />
              <el-option label="Week" value="weekly" />
              <el-option label="Month" value="monthly" />
            </el-select>
          </span>
        </el-form-item>
        <el-form-item label="Report Title">
          <el-input v-model="reportForm.title" placeholder="Enter report title" class="full-width-input" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="generateDialogVisible = false">Cancel</el-button>
          <el-button class="generate-btn-dialog" @click="generateReport">
            <el-icon><Document /></el-icon> Generate Report
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- Report View Dialog -->
    <el-dialog v-model="viewDialogVisible" :title="selectedReport?.title" width="950px" class="report-view-dialog" destroy-on-close>
      <div v-if="selectedReport" class="report-view">
        <!-- Report Header -->
        <div class="report-header" :class="selectedReport.type">
          <div class="report-header-content">
            <div class="report-type-tag" :class="selectedReport.type">
              {{ getReportTypeLabel(selectedReport.type) }}
            </div>
            <h2>{{ selectedReport.title }}</h2>
            <div class="report-meta-info">
              <span><el-icon><Calendar /></el-icon> Generated: {{ selectedReport.date }}</span>
              <span><el-icon><User /></el-icon> Author: {{ selectedReport.author }}</span>
              <span><el-icon><Document /></el-icon> Format: {{ selectedReport.format.toUpperCase() }}</span>
            </div>
          </div>
        </div>

        <!-- Report Content Preview -->
        <div class="report-content">
          <div class="report-summary">
            <div class="summary-icon">📋</div>
            <div class="summary-text">
              <h3>Executive Summary</h3>
              <p>{{ getReportSummary(selectedReport) }}</p>
            </div>
          </div>

          <!-- Report Charts -->
          <div class="report-charts">
            <div class="chart-container" :ref="el => setChartRef(el, selectedReport.type)"></div>
          </div>

          <!-- Key Findings -->
          <div class="key-findings">
            <div class="findings-header">
              <span>🔍</span>
              <h3>Key Findings</h3>
            </div>
            <ul>
              <li v-for="finding in getKeyFindings(selectedReport)" :key="finding">
                <span class="bullet">•</span> {{ finding }}
              </li>
            </ul>
          </div>

          <!-- Recommendations -->
          <div class="recommendations">
            <div class="rec-header">
              <span>💡</span>
              <h3>Recommendations</h3>
            </div>
            <ul>
              <li v-for="rec in getRecommendations(selectedReport)" :key="rec">
                <span class="bullet">→</span> {{ rec }}
              </li>
            </ul>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button class="cancel-btn" @click="viewDialogVisible = false">Close</el-button>
          <el-button class="download-btn" @click="downloadReport(selectedReport)">
            <el-icon><Download /></el-icon> Download
          </el-button>
          <el-button class="share-btn" @click="shareReport(selectedReport)">
            <el-icon><Share /></el-icon> Share
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  DataAnalysis, Plus, Refresh, Document, CircleCheck, Clock, DataLine,
  Place, Money, Warning, TrendCharts, Calendar, User, View, Download, Share, Search
} from '@element-plus/icons-vue'

// ==================== Helper Functions ====================
const getReportTypeLabel = (type: string): string => {
  const map: Record<string, string> = {
    occupancy: 'Occupancy', revenue: 'Revenue', violation: 'Violation', utilization: 'Utilization', custom: 'Custom'
  }
  return map[type] || type
}

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading parking reports...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading parking reports...',
  'Fetching report data...',
  'Loading analytics...',
  'Almost ready...'
]

// ==================== Types ====================
interface ParkingReport {
  id: string
  title: string
  type: string
  date: string
  author: string
  fileSize: number
  format: string
  period: string
  zones: string[]
}

// ==================== Mock Data ====================
const currentDate = new Date()
const formattedDate = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`

const generateReports = (): ParkingReport[] => {
  const reports: ParkingReport[] = []
  const authors = ['System Auto-Generated', 'John Tan', 'Mike Chen', 'Sarah Koh']
  const types = ['occupancy', 'revenue', 'violation', 'utilization']
  const formats = ['pdf', 'excel', 'csv']

  for (let i = 0; i < 12; i++) {
    const date = new Date()
    date.setDate(date.getDate() - i * 7)
    const dateStr = date.toISOString().slice(0, 10)
    const type = types[Math.floor(Math.random() * types.length)]

    reports.push({
      id: `RPT-${String(i + 1).padStart(6, '0')}`,
      title: `${getReportTypeLabel(type)} Report - ${dateStr}`,
      type: type,
      date: dateStr,
      author: authors[Math.floor(Math.random() * authors.length)],
      fileSize: parseFloat((1.5 + Math.random() * 3).toFixed(1)),
      format: formats[Math.floor(Math.random() * formats.length)],
      period: 'monthly',
      zones: ['Zone A', 'Zone B', 'Zone C', 'Zone D', 'Zone E']
    })
  }

  return reports.sort((a, b) => b.date.localeCompare(a.date))
}

const reportsData = ref<ParkingReport[]>(generateReports())

// ==================== State ====================
const searchText = ref('')
const typeFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const currentPage = ref(1)
const pageSize = ref(6)
const generateDialogVisible = ref(false)
const viewDialogVisible = ref(false)
const selectedReport = ref<ParkingReport | null>(null)

// Chart refs
let previewChart: echarts.ECharts | null = null
const chartRefs: Record<string, HTMLElement | null> = {
  occupancy: null,
  revenue: null,
  violation: null,
  utilization: null
}

const reportForm = ref({
  type: 'occupancy',
  period: 'monthly',
  dateRange: null as string[] | null,
  zones: [] as string[],
  format: 'pdf',
  schedule: false,
  scheduleFrequency: 'weekly',
  title: `Occupancy Report - ${formattedDate}`
})

const dateShortcuts = [
  { text: 'Last 7 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 7 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 30 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 30 * 24 * 60 * 60 * 1000)
      return [start, end]
    }},
  { text: 'Last 90 days', value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 90 * 24 * 60 * 60 * 1000)
      return [start, end]
    }}
]

// ==================== Computed ====================
const stats = computed(() => {
  const totalReports = reportsData.value.length
  const generatedReports = reportsData.value.filter(r => r.author !== 'System Auto-Generated').length
  const scheduledReports = 3
  const averageOccupancy = 68
  const reportGrowth = 12
  const generatedPercent = Math.round((generatedReports / totalReports) * 100)

  return { totalReports, generatedReports, scheduledReports, averageOccupancy, reportGrowth, generatedPercent }
})

const filteredReports = computed(() => {
  let filtered = [...reportsData.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(search) ||
        r.author.toLowerCase().includes(search)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(r => r.type === typeFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(r => {
      const reportDate = new Date(r.date)
      return reportDate >= start && reportDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredReports.value.length)

const paginatedReports = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredReports.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getReportSummary = (report: ParkingReport): string => {
  const summaries: Record<string, string> = {
    occupancy: `This report analyzes parking occupancy across ${report.zones.length} zones. Average occupancy rate is 68% with peak occupancy of 92% during weekday mornings. Overall, occupancy has increased by 5.2% compared to the previous period.`,
    revenue: `Total parking revenue for the period is $45,200. Monthly season pass holders contribute 42% of total revenue. Credit card payments account for 65% of all transactions.`,
    violation: `A total of 142 violations were recorded during this period. The most common violation type is "No Parking Zone" accounting for 28% of all violations. Repeat offenders represent 15% of total violations.`,
    utilization: `Overall parking utilization is 65%. EV charging spots show 45% utilization rate, representing a 10% increase from last year. Turnover rate averages 3.2 vehicles per spot per day.`
  }
  return summaries[report.type] || 'Report generated successfully with comprehensive data analysis.'
}

const getKeyFindings = (report: ParkingReport): string[] => {
  const findings: Record<string, string[]> = {
    occupancy: [
      'Peak occupancy occurs between 10:00 AM - 11:00 AM reaching 92% capacity',
      'Zone A has the highest average occupancy at 78%, while Zone E is lowest at 52%',
      'Weekend occupancy is 45% lower than weekdays, indicating significant demand variation',
      'Occupancy has increased 5.2% compared to the same period last year'
    ],
    revenue: [
      'Monthly revenue increased by 8.5% compared to previous period, exceeding targets',
      'Credit card payments account for 65% of transactions, mobile payments growing 22% YoY',
      'Season pass renewals at 92% retention rate, showing strong customer loyalty',
      'Revenue per available spot (RevPAS) increased 6.3% due to dynamic pricing'
    ],
    violation: [
      'Repeat offenders account for 15% of total violations, down 3% from last quarter',
      'Zone B has the highest violation rate with 32% of all violations occurring there',
      'Peak violation time is between 2:00 PM - 4:00 PM, coinciding with afternoon rush',
      '"No Parking Zone" violations increased 12%, requiring additional signage'
    ],
    utilization: [
      'EV charging spots utilization is 45%, up from 35% last year due to increased EV adoption',
      'Turnover rate averages 3.2 vehicles per spot per day, higher than industry average of 2.8',
      'Disabled spots utilization rate is 28%, indicating potential over-provisioning',
      'Morning hours (8-10 AM) show highest utilization at 85%'
    ]
  }
  return findings[report.type] || ['Data analysis complete.']
}

const getRecommendations = (report: ParkingReport): string[] => {
  const recs: Record<string, string[]> = {
    occupancy: [
      'Consider dynamic pricing during peak hours (10 AM - 11 AM) to manage demand',
      'Launch a promotion to increase weekend occupancy, targeting retail and entertainment visitors',
      'Consider expanding capacity in Zone A with multi-level parking structure',
      'Implement real-time occupancy notifications via mobile app to guide drivers'
    ],
    revenue: [
      'Increase rates during peak hours by 15-20% to optimize revenue',
      'Launch digital marketing campaign for season passes targeting monthly commuters',
      'Implement loyalty program offering free parking after 10 visits',
      'Introduce premium reserved parking at higher rates for guaranteed spots'
    ],
    violation: [
      'Increase enforcement patrols in Zone B during peak afternoon hours',
      'Install additional signage in high-violation areas with clear penalty warnings',
      'Launch education campaign highlighting EV/disabled spot rules and fines',
      'Implement automated license plate recognition for instant violation detection'
    ],
    utilization: [
      'Convert underutilized regular spots to EV charging to meet growing demand',
      'Implement reservation system for high-demand spots during peak hours',
      'Consider valet service during peak morning hours to maximize turnover',
      'Install smart sensors for real-time availability tracking to improve utilization'
    ]
  }
  return recs[report.type] || ['Continue monitoring performance and adjust strategies accordingly.']
}

const setChartRef = (el: any, type: string) => {
  if (el) {
    chartRefs[type] = el
    nextTick(() => initPreviewChart(type))
  }
}

const initPreviewChart = (type: string) => {
  const el = chartRefs[type]
  if (!el) return

  if (previewChart) {
    previewChart.dispose()
    previewChart = null
  }

  previewChart = echarts.init(el)

  let option = {}

  if (type === 'occupancy') {
    option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 40, left: 60, right: 30, bottom: 30, containLabel: true },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], axisLabel: { fontSize: 12, fontWeight: 500 } },
      yAxis: { type: 'value', name: 'Occupancy (%)', max: 100, nameLocation: 'middle', nameGap: 40 },
      series: [{
        type: 'line',
        data: [85, 82, 88, 86, 90, 55, 48],
        smooth: true,
        lineStyle: { color: '#3b82f6', width: 3 },
        symbol: 'circle',
        symbolSize: 8,
        areaStyle: { opacity: 0.1, color: '#3b82f6' },
        label: { show: true, position: 'top', formatter: '{c}%' }
      }]
    }
  } else if (type === 'revenue') {
    option = {
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { top: 40, left: 60, right: 30, bottom: 30 },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { type: 'value', name: 'Revenue ($K)' },
      series: [{
        type: 'bar',
        data: [5.2, 4.8, 5.5, 5.8, 6.2, 3.5, 2.8],
        itemStyle: { borderRadius: [8, 8, 0, 0], color: '#22c55e' },
        label: { show: true, position: 'top', formatter: '${c}K' }
      }]
    }
  } else if (type === 'violation') {
    option = {
      tooltip: { trigger: 'axis' },
      grid: { top: 40, left: 60, right: 30, bottom: 30 },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
      yAxis: { type: 'value', name: 'Violations' },
      series: [{
        type: 'line',
        data: [12, 15, 18, 20, 25, 8, 6],
        smooth: true,
        lineStyle: { color: '#ef4444', width: 3 },
        symbol: 'circle',
        symbolSize: 8,
        areaStyle: { opacity: 0.1, color: '#ef4444' },
        label: { show: true, position: 'top' }
      }]
    }
  } else if (type === 'utilization') {
    option = {
      tooltip: { trigger: 'item', formatter: '{b}: {d}%' },
      legend: { orient: 'vertical', left: 'left', textStyle: { fontSize: 12 } },
      series: [{
        type: 'pie',
        radius: '55%',
        center: ['50%', '50%'],
        data: [
          { value: 65, name: 'Regular', itemStyle: { color: '#3b82f6' } },
          { value: 15, name: 'EV Charging', itemStyle: { color: '#22c55e' } },
          { value: 10, name: 'Disabled', itemStyle: { color: '#8b5cf6' } },
          { value: 10, name: 'Reserved', itemStyle: { color: '#f59e0b' } }
        ],
        label: { show: true, formatter: '{b}: {d}%', fontSize: 12 },
        emphasis: { scale: true }
      }]
    }
  }

  previewChart.setOption(option)
}

const resetFilters = () => {
  searchText.value = ''
  typeFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Actions ====================
const viewReport = (report: ParkingReport) => {
  selectedReport.value = report
  viewDialogVisible.value = true
}

const downloadReport = (report: ParkingReport | null) => {
  if (report) {
    ElMessage.success(`Downloading ${report.title}...`)
    setTimeout(() => {
      ElMessage.success('Download completed')
    }, 1000)
  }
}

const shareReport = (report: ParkingReport | null) => {
  if (report) {
    ElMessage.success(`Share link created for ${report.title}`)
  }
}

const generateFromTemplate = (type: string) => {
  reportForm.value = {
    type: type,
    period: 'monthly',
    dateRange: null,
    zones: [],
    format: 'pdf',
    schedule: false,
    scheduleFrequency: 'weekly',
    title: `${getReportTypeLabel(type)} Report - ${formattedDate}`
  }
  generateDialogVisible.value = true
}

const openGenerateDialog = () => {
  reportForm.value = {
    type: 'occupancy',
    period: 'monthly',
    dateRange: null,
    zones: [],
    format: 'pdf',
    schedule: false,
    scheduleFrequency: 'weekly',
    title: `Occupancy Report - ${formattedDate}`
  }
  generateDialogVisible.value = true
}

const generateReport = () => {
  ElMessage.success('Report generation started. You will be notified when ready.')
  generateDialogVisible.value = false
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  reportsData.value = generateReports()
  ElMessage.success('Data refreshed')
}

// ==================== Watch ====================
watch([searchText, typeFilter, dateRange], () => {
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
    }, 500)
  }, 2200)
}

onMounted(() => {
  startLoading()
})

onUnmounted(() => {
  if (previewChart && !previewChart.isDisposed()) previewChart.dispose()
})
</script>

<style scoped>
/* ==================== 全局样式 ==================== */
.parking-reports-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f9ff 0%, #e8f0fe 100%);
  padding: 28px;
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
  border-radius: 10px;
}
*::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 10px;
}
*::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* ==================== Loading Screen ==================== */
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
  padding: 48px;
  border-radius: 40px;
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

/* ==================== Header ==================== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.title-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin-left: 62px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.primary-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s;
}

.primary-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.secondary-btn {
  background: white;
  border: 1px solid #e2e8f0;
  color: #475569;
  padding: 10px 20px;
  border-radius: 12px;
  transition: all 0.3s;
}

.secondary-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  transform: translateY(-2px);
}

/* ==================== Stats Grid ==================== */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 28px;
}

.stat-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
}

.stat-icon.blue { background: linear-gradient(135deg, #eef2ff, #dbeafe); color: #3b82f6; }
.stat-icon.green { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #22c55e; }
.stat-icon.orange { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }
.stat-icon.purple { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #8b5cf6; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-unit {
  font-size: 14px;
  font-weight: normal;
  color: #64748b;
  margin-left: 4px;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  font-size: 11px;
  margin-top: 6px;
  color: #94a3b8;
}

.stat-trend.up { color: #22c55e; }

/* ==================== Section Header ==================== */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  font-size: 24px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 14px;
  color: #94a3b8;
  font-size: 16px;
}

.search-input {
  width: 260px;
}
.search-input :deep(.el-input__wrapper) {
  padding-left: 36px;
  border-radius: 40px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}
.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.search-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}

.filter-select {
  width: 180px;
}
.filter-select :deep(.el-input__wrapper) {
  border-radius: 40px;
}

.date-range-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 4px 12px;
  border-radius: 40px;
  border: 1px solid #e2e8f0;
}

.date-range-picker {
  width: 260px;
}
.date-range-picker :deep(.el-input__wrapper) {
  box-shadow: none;
  background: transparent;
}

/* ==================== Templates Grid ==================== */
.templates-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.template-card {
  background: white;
  border-radius: 24px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.template-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #3b82f6, #22c55e, #f59e0b, #ef4444);
  opacity: 0;
  transition: opacity 0.3s;
}

.template-card:hover::before {
  opacity: 1;
}

.template-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.15);
}

.template-icon {
  width: 72px;
  height: 72px;
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto 16px;
}

.template-icon.occupancy { background: linear-gradient(135deg, #eef2ff, #dbeafe); color: #3b82f6; }
.template-icon.revenue { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #22c55e; }
.template-icon.violation { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #ef4444; }
.template-icon.utilization { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }

.template-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.template-desc {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin-bottom: 16px;
}

.template-metrics {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
}

.metric-chip {
  background: #f8fafc;
  padding: 6px 12px;
  border-radius: 20px;
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.metric-chip .metric-label {
  color: #94a3b8;
}

.metric-chip .metric-value {
  font-weight: 600;
  color: #1e293b;
}

.template-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.generate-btn {
  background: transparent;
  border: none;
  color: #3b82f6;
  font-weight: 500;
  transition: all 0.3s;
}

.generate-btn:hover {
  color: #2563eb;
  transform: translateX(4px);
}

/* ==================== Reports Grid ==================== */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(390px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.report-card {
  background: white;
  border-radius: 24px;
  padding: 20px;
  display: flex;
  gap: 16px;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  cursor: pointer;
  position: relative;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 28px -8px rgba(0, 0, 0, 0.12);
}

.report-card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.report-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.report-icon.occupancy { background: linear-gradient(135deg, #eef2ff, #dbeafe); color: #3b82f6; }
.report-icon.revenue { background: linear-gradient(135deg, #dcfce7, #bbf7d0); color: #22c55e; }
.report-icon.violation { background: linear-gradient(135deg, #fee2e2, #fecaca); color: #ef4444; }
.report-icon.utilization { background: linear-gradient(135deg, #fef3c7, #fde68a); color: #f59e0b; }

.report-badge {
  font-size: 10px;
  padding: 4px 8px;
  border-radius: 20px;
  font-weight: 600;
}

.report-badge.occupancy { background: #eef2ff; color: #3b82f6; }
.report-badge.revenue { background: #dcfce7; color: #22c55e; }
.report-badge.violation { background: #fee2e2; color: #ef4444; }
.report-badge.utilization { background: #fef3c7; color: #f59e0b; }

.report-info {
  flex: 1;
}

.report-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.report-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
}

.report-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.report-stats {
  display: flex;
  gap: 12px;
}

.stat-chip {
  background: #f8fafc;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  display: flex;
  gap: 4px;
}

.stat-chip span {
  color: #94a3b8;
}

.stat-chip strong {
  color: #1e293b;
}

.report-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border: none;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #eef2ff;
  transform: scale(1.05);
}

.action-btn.download:hover { background: #dcfce7; color: #22c55e; }
.action-btn.share:hover { background: #fef3c7; color: #f59e0b; }

/* ==================== Report View Dialog ==================== */
.report-view-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.report-view {
  max-height: 70vh;
  overflow-y: auto;
}

.report-header {
  padding: 28px;
  margin: -20px -20px 0 -20px;
  border-radius: 20px 20px 0 0;
}

.report-header.occupancy { background: linear-gradient(135deg, #3b82f6, #1e3a8a); color: white; }
.report-header.revenue { background: linear-gradient(135deg, #22c55e, #166534); color: white; }
.report-header.violation { background: linear-gradient(135deg, #ef4444, #991b1b); color: white; }
.report-header.utilization { background: linear-gradient(135deg, #f59e0b, #b45309); color: white; }

.report-type-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  width: fit-content;
}

.report-header-content h2 {
  margin: 16px 0 12px 0;
  font-size: 24px;
}

.report-meta-info {
  display: flex;
  gap: 24px;
  font-size: 13px;
  opacity: 0.9;
  flex-wrap: wrap;
}

.report-meta-info span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.report-content {
  padding: 24px;
}

.report-summary {
  display: flex;
  gap: 16px;
  background: #f8fafc;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
}

.summary-icon {
  font-size: 32px;
}

.summary-text h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.summary-text p {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
}

.report-charts {
  margin-bottom: 24px;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.key-findings, .recommendations {
  background: #f8fafc;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 20px;
}

.findings-header, .rec-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.findings-header span, .rec-header span {
  font-size: 24px;
}

.findings-header h3, .rec-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.key-findings ul, .recommendations ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.key-findings li, .recommendations li {
  font-size: 14px;
  color: #64748b;
  margin: 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.bullet {
  color: #3b82f6;
  font-weight: 600;
}

/* ==================== Pagination ==================== */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

/* ==================== Empty State ==================== */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 24px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 20px;
}

/* ==================== Dialog Styles ==================== */
.custom-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #eef2f8;
  padding: 20px 24px;
}

.custom-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.dialog-header-icon {
  text-align: center;
  font-size: 48px;
  margin-bottom: 16px;
}

.report-form {
  padding: 0 8px;
}

.full-width-select, .full-width-date, .full-width-input {
  width: 100%;
}

.period-buttons, .format-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.period-btn, .format-buttons .el-button {
  border-radius: 20px;
}

.schedule-hint {
  margin-left: 12px;
  font-size: 13px;
  color: #64748b;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
}

.cancel-btn {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 40px;
  padding: 8px 20px;
}

.generate-btn-dialog, .download-btn, .share-btn {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
  color: white;
  border-radius: 40px;
  padding: 8px 20px;
}

.generate-btn-dialog:hover, .download-btn:hover, .share-btn:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  transform: translateY(-2px);
}

/* ==================== Responsive ==================== */
@media (max-width: 1000px) {
  .stats-grid, .templates-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .reports-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid, .templates-grid {
    grid-template-columns: 1fr;
  }
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .section-actions {
    width: 100%;
    flex-direction: column;
  }
  .search-wrapper, .search-input, .filter-select, .date-range-wrapper, .date-range-picker {
    width: 100%;
  }
  .report-card {
    flex-direction: column;
  }
  .report-actions {
    flex-direction: row;
    justify-content: flex-end;
  }
  .report-meta-info {
    flex-wrap: wrap;
  }
}

/* ==================== Element Plus Overrides ==================== */
:deep(.el-button--primary) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border: none;
}
:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}
:deep(.el-pagination.is-background .el-pager li.is-active) {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
:deep(.el-pagination .btn-prev, :deep(.el-pagination .btn-next)) {
  border-radius: 12px;
}
:deep(.el-select-dropdown__item.selected) {
  color: #3b82f6;
}
:deep(.el-progress-bar__inner) {
  border-radius: 8px;
}
</style>