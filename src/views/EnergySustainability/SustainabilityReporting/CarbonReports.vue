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
          <span class="loading-title">Carbon Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Carbon Emissions Reporting & Documentation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="carbon-reports-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          Carbon Reports
        </h1>
        <div class="page-subtitle">Carbon emissions reporting, inventories, and compliance documentation</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="createNewReport">
          <el-icon><Plus /></el-icon> Generate Report
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon> Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalReports }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.publishedReports }}</div>
          <div class="stat-label">Published</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Edit /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.draftReports }}</div>
          <div class="stat-label">In Progress</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalEmissions }}<span class="stat-unit">kt</span></div>
          <div class="stat-label">Total CO₂e (YTD)</div>
        </div>
      </div>
    </div>

    <!-- Section Header -->
    <div class="section-header">
      <h2 class="section-title">Report Library</h2>
      <div class="section-actions">
        <el-input
            v-model="searchText"
            placeholder="Search reports..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="reportTypeFilter" placeholder="Report Type" clearable style="width: 160px">
          <el-option label="Annual Carbon Report" value="annual" />
          <el-option label="Carbon Inventory" value="inventory" />
          <el-option label="CDP Disclosure" value="cdp" />
          <el-option label="TCFD Report" value="tcfd" />
          <el-option label="Offset Report" value="offset" />
        </el-select>
        <el-select v-model="yearFilter" placeholder="Year" clearable style="width: 100px">
          <el-option :label="currentYear.toString()" :value="currentYear.toString()" />
          <el-option :label="(currentYear - 1).toString()" :value="(currentYear - 1).toString()" />
          <el-option :label="(currentYear - 2).toString()" :value="(currentYear - 2).toString()" />
          <el-option :label="(currentYear - 3).toString()" :value="(currentYear - 3).toString()" />
        </el-select>
      </div>
    </div>

    <!-- Reports Grid -->
    <div class="reports-grid">
      <div
          v-for="report in paginatedReports"
          :key="report.id"
          class="report-card"
          @click="viewReport(report)"
      >
        <div class="report-cover" :style="{ backgroundImage: `linear-gradient(135deg, ${report.coverColor} 0%, ${report.coverColor2} 100%)` }">
          <div class="report-type-badge" :class="report.type">
            {{ getReportTypeLabel(report.type) }}
          </div>
          <div class="report-year">{{ report.year }}</div>
          <div class="report-icon">
            <el-icon><Document /></el-icon>
          </div>
        </div>
        <div class="report-content">
          <h3 class="report-title">{{ report.title }}</h3>
          <p class="report-description">{{ report.description }}</p>
          <div class="report-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>{{ report.publishDate }}</span>
            </div>
            <div class="meta-item">
              <el-icon><User /></el-icon>
              <span>{{ report.author }}</span>
            </div>
          </div>
          <div class="report-stats">
            <div class="stat-item">
              <span class="stat-label">Pages</span>
              <span class="stat-value">{{ report.pages }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Downloads</span>
              <span class="stat-value">{{ report.downloads }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Status</span>
              <el-tag :type="getStatusTagType(report.status)" size="small">{{ getStatusText(report.status) }}</el-tag>
            </div>
          </div>
          <div class="report-emissions">
            <div class="emissions-item">
              <span class="emissions-label">Scope 1</span>
              <span class="emissions-value">{{ report.scope1 }} t</span>
            </div>
            <div class="emissions-item">
              <span class="emissions-label">Scope 2</span>
              <span class="emissions-value">{{ report.scope2 }} t</span>
            </div>
            <div class="emissions-item">
              <span class="emissions-label">Scope 3</span>
              <span class="emissions-value">{{ report.scope3 }} t</span>
            </div>
          </div>
          <div class="report-actions">
            <el-button size="small" @click.stop="previewReport(report)">
              <el-icon><View /></el-icon> Preview
            </el-button>
            <el-button size="small" type="primary" @click.stop="downloadReport(report)">
              <el-icon><Download /></el-icon> Download
            </el-button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredReports.length === 0" class="empty-state">
        <el-empty description="No carbon reports found">
          <el-button type="primary" @click="createNewReport">Generate Report</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredReports.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 12, 18]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- Report Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedReport?.title" width="900px" class="report-dialog">
      <div v-if="selectedReport" class="report-detail">
        <!-- Report Header -->
        <div class="detail-header" :style="{ background: `linear-gradient(135deg, ${selectedReport.coverColor} 0%, ${selectedReport.coverColor2} 100%)` }">
          <div class="detail-header-content">
            <div class="report-badge" :class="selectedReport.type">{{ getReportTypeLabel(selectedReport.type) }}</div>
            <h2>{{ selectedReport.title }}</h2>
            <div class="detail-meta">
              <span><el-icon><Calendar /></el-icon> {{ selectedReport.publishDate }}</span>
              <span><el-icon><User /></el-icon> {{ selectedReport.author }}</span>
              <span><el-icon><Document /></el-icon> {{ selectedReport.pages }} pages</span>
              <span><el-icon><Download /></el-icon> {{ selectedReport.downloads }} downloads</span>
            </div>
          </div>
        </div>

        <!-- Report Content -->
        <div class="detail-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Report ID">{{ selectedReport.id }}</el-descriptions-item>
            <el-descriptions-item label="Version">{{ selectedReport.version }}</el-descriptions-item>
            <el-descriptions-item label="Reporting Period">{{ selectedReport.year }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusTagType(selectedReport.status)" size="small">{{ getStatusText(selectedReport.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Total Emissions">{{ selectedReport.totalEmissions }} tCO₂e</el-descriptions-item>
            <el-descriptions-item label="Verification Status">
              <el-tag :type="selectedReport.verified ? 'success' : 'warning'" size="small">
                {{ selectedReport.verified ? 'Verified' : 'Pending' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ selectedReport.description }}</el-descriptions-item>
          </el-descriptions>

          <!-- Emissions Breakdown -->
          <div class="detail-section">
            <div class="section-title">Emissions Breakdown</div>
            <div class="emissions-breakdown">
              <div class="breakdown-card">
                <div class="breakdown-value">{{ selectedReport.scope1.toLocaleString() }}</div>
                <div class="breakdown-label">Scope 1 (tCO₂e)</div>
                <div class="breakdown-change" :class="selectedReport.scope1Change < 0 ? 'positive' : 'negative'">
                  {{ selectedReport.scope1Change < 0 ? '↓' : '↑' }} {{ Math.abs(selectedReport.scope1Change) }}% vs last year
                </div>
              </div>
              <div class="breakdown-card">
                <div class="breakdown-value">{{ selectedReport.scope2.toLocaleString() }}</div>
                <div class="breakdown-label">Scope 2 (tCO₂e)</div>
                <div class="breakdown-change" :class="selectedReport.scope2Change < 0 ? 'positive' : 'negative'">
                  {{ selectedReport.scope2Change < 0 ? '↓' : '↑' }} {{ Math.abs(selectedReport.scope2Change) }}% vs last year
                </div>
              </div>
              <div class="breakdown-card">
                <div class="breakdown-value">{{ selectedReport.scope3.toLocaleString() }}</div>
                <div class="breakdown-label">Scope 3 (tCO₂e)</div>
                <div class="breakdown-change" :class="selectedReport.scope3Change < 0 ? 'positive' : 'negative'">
                  {{ selectedReport.scope3Change < 0 ? '↓' : '↑' }} {{ Math.abs(selectedReport.scope3Change) }}% vs last year
                </div>
              </div>
              <div class="breakdown-card total">
                <div class="breakdown-value">{{ selectedReport.totalEmissions.toLocaleString() }}</div>
                <div class="breakdown-label">Total CO₂e</div>
              </div>
            </div>
          </div>

          <!-- Emissions Trend Chart -->
          <div class="detail-section">
            <div class="section-title">Emissions Trend</div>
            <div class="trend-chart" ref="trendChartEl"></div>
          </div>

          <!-- Reduction Initiatives -->
          <div class="detail-section">
            <div class="section-title">Reduction Initiatives</div>
            <el-timeline>
              <el-timeline-item
                  v-for="init in selectedReport.initiatives"
                  :key="init.id"
                  :timestamp="init.status"
                  :type="init.status === 'Completed' ? 'success' : (init.status === 'In Progress' ? 'primary' : 'info')"
                  placement="top"
              >
                <div class="initiative-title">{{ init.title }}</div>
                <div class="initiative-impact">Expected reduction: {{ init.reduction }} tCO₂e/year</div>
              </el-timeline-item>
            </el-timeline>
          </div>

          <!-- Downloads -->
          <div class="detail-section">
            <div class="section-title">Available Formats</div>
            <div class="downloads-grid">
              <div class="download-card" @click="downloadReport(selectedReport, 'pdf')">
                <el-icon><Document /></el-icon>
                <span>PDF Report</span>
                <span class="file-size">{{ selectedReport.fileSize }} MB</span>
              </div>
              <div class="download-card" @click="downloadReport(selectedReport, 'excel')">
                <el-icon><DataAnalysis /></el-icon>
                <span>Excel Data</span>
                <span class="file-size">1.2 MB</span>
              </div>
              <div class="download-card" @click="downloadReport(selectedReport, 'csv')">
                <el-icon><DataLine /></el-icon>
                <span>CSV Raw Data</span>
                <span class="file-size">0.8 MB</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editReport(selectedReport)">Edit Report</el-button>
        <el-button type="success" @click="publishReport(selectedReport)">Publish</el-button>
      </template>
    </el-dialog>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateDialogVisible" title="Generate Carbon Report" width="600px">
      <el-form :model="reportForm" label-width="140px">
        <el-form-item label="Report Type" required>
          <el-select v-model="reportForm.type" placeholder="Select report type" style="width: 100%">
            <el-option label="Annual Carbon Report" value="annual" />
            <el-option label="Carbon Inventory" value="inventory" />
            <el-option label="CDP Disclosure" value="cdp" />
            <el-option label="TCFD Report" value="tcfd" />
            <el-option label="Offset Report" value="offset" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reporting Year" required>
          <el-select v-model="reportForm.year" placeholder="Select year" style="width: 100%">
            <el-option :label="currentYear.toString()" :value="currentYear.toString()" />
            <el-option :label="(currentYear - 1).toString()" :value="(currentYear - 1).toString()" />
            <el-option :label="(currentYear - 2).toString()" :value="(currentYear - 2).toString()" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reporting Period">
          <el-date-picker
              v-model="reportForm.period"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Include Scopes">
          <el-checkbox-group v-model="reportForm.scopes">
            <el-checkbox label="scope1">Scope 1 (Direct)</el-checkbox>
            <el-checkbox label="scope2">Scope 2 (Energy)</el-checkbox>
            <el-checkbox label="scope3">Scope 3 (Value Chain)</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Report Title">
          <el-input v-model="reportForm.title" placeholder="Enter report title" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveReport">Generate Report</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  TrendCharts, Plus, Refresh, CircleCheck, Edit, DataLine,
  Search, Calendar, User, View, Download, Document, DataAnalysis
} from '@element-plus/icons-vue'

// ==================== 获取当前日期 ====================
const currentDate = new Date()
const currentYear = currentDate.getFullYear()
const currentMonth = String(currentDate.getMonth() + 1).padStart(2, '0')
const currentDay = String(currentDate.getDate()).padStart(2, '0')
const formattedDate = `${currentYear}-${currentMonth}-${currentDay}`

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading carbon reports...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading carbon reports...',
  'Fetching emissions data...',
  'Loading compliance metrics...',
  'Almost ready...'
]

// ==================== Types ====================
interface CarbonReport {
  id: string
  title: string
  type: string
  year: string
  description: string
  publishDate: string
  author: string
  pages: number
  downloads: number
  status: string
  version: string
  coverColor: string
  coverColor2: string
  scope1: number
  scope2: number
  scope3: number
  totalEmissions: number
  scope1Change: number
  scope2Change: number
  scope3Change: number
  verified: boolean
  fileSize: number
  initiatives: { id: number; title: string; reduction: number; status: string }[]
}

// ==================== 生成模拟数据（使用当前年份） ====================
const generateReportsData = (): CarbonReport[] => {
  // 当前年份报告
  const currentYearStr = currentYear.toString()
  const lastYearStr = (currentYear - 1).toString()
  const twoYearsAgoStr = (currentYear - 2).toString()

  return [
    {
      id: `CAR-${currentYear}-001`, title: `Annual Carbon Report ${currentYear}`, type: 'annual', year: currentYearStr,
      description: `Comprehensive carbon emissions report for fiscal year ${currentYear}, including Scope 1, 2, and 3 emissions.`,
      publishDate: formattedDate, author: 'Carbon Management Team', pages: 86, downloads: 1247,
      status: 'published', version: 'v1.0',
      coverColor: '#059669', coverColor2: '#047857',
      scope1: 12500, scope2: 18500, scope3: 22500, totalEmissions: 53500,
      scope1Change: -5.2, scope2Change: -8.5, scope3Change: -3.2,
      verified: true, fileSize: 2.8,
      initiatives: [
        { id: 1, title: 'Solar PPA Implementation', reduction: 8500, status: 'In Progress' },
        { id: 2, title: 'HVAC Efficiency Upgrade', reduction: 3200, status: 'Completed' },
        { id: 3, title: 'EV Fleet Transition', reduction: 1800, status: 'In Progress' }
      ]
    },
    {
      id: `CAR-${currentYear}-002`, title: `Carbon Inventory ${currentYear}`, type: 'inventory', year: currentYearStr,
      description: `Detailed carbon inventory for ${currentYear} with facility-level breakdown and emission factors.`,
      publishDate: `${currentYear}-02-15`, author: 'Carbon Accounting', pages: 112, downloads: 856,
      status: 'published', version: 'v2.1',
      coverColor: '#0d9488', coverColor2: '#0f766e',
      scope1: 11800, scope2: 17200, scope3: 20800, totalEmissions: 49800,
      scope1Change: -6.8, scope2Change: -7.2, scope3Change: -4.5,
      verified: true, fileSize: 3.2,
      initiatives: [
        { id: 1, title: 'LED Lighting Retrofit', reduction: 2100, status: 'Completed' },
        { id: 2, title: 'Chiller Optimization', reduction: 2800, status: 'Completed' }
      ]
    },
    {
      id: `CAR-${currentYear}-003`, title: `CDP Climate Change Disclosure ${currentYear}`, type: 'cdp', year: currentYearStr,
      description: `CDP disclosure for ${currentYear}, scoring B in climate change management.`,
      publishDate: `${currentYear}-03-20`, author: 'ESG Team', pages: 64, downloads: 623,
      status: 'published', version: 'v1.0',
      coverColor: '#2563eb', coverColor2: '#1e3a8a',
      scope1: 12000, scope2: 17800, scope3: 21500, totalEmissions: 51300,
      scope1Change: -4.5, scope2Change: -6.2, scope3Change: -2.8,
      verified: true, fileSize: 1.8,
      initiatives: [
        { id: 1, title: 'Renewable Energy Certificates', reduction: 15000, status: 'Completed' },
        { id: 2, title: 'Energy Management System', reduction: 4200, status: 'In Progress' }
      ]
    },
    {
      id: `CAR-${currentYear}-004`, title: `TCFD Report ${currentYear}`, type: 'tcfd', year: currentYearStr,
      description: `Task Force on Climate-related Financial Disclosures report for ${currentYear}.`,
      publishDate: `${currentYear}-04-10`, author: 'Risk Committee', pages: 78, downloads: 432,
      status: 'draft', version: 'v0.9',
      coverColor: '#7c3aed', coverColor2: '#6d28d9',
      scope1: 13200, scope2: 19200, scope3: 23500, totalEmissions: 55900,
      scope1Change: -2.1, scope2Change: -3.5, scope3Change: -1.2,
      verified: false, fileSize: 2.1,
      initiatives: [
        { id: 1, title: 'Climate Risk Assessment', reduction: 0, status: 'In Progress' },
        { id: 2, title: 'Scenario Analysis', reduction: 0, status: 'Planned' }
      ]
    },
    {
      id: `CAR-${lastYearStr}-005`, title: `Annual Carbon Report ${lastYearStr}`, type: 'annual', year: lastYearStr,
      description: `Annual carbon report for ${lastYearStr} with verified emissions data.`,
      publishDate: `${lastYearStr}-03-15`, author: 'Carbon Management Team', pages: 82, downloads: 2156,
      status: 'published', version: 'v1.0',
      coverColor: '#059669', coverColor2: '#047857',
      scope1: 13200, scope2: 20200, scope3: 23200, totalEmissions: 56600,
      scope1Change: -3.2, scope2Change: -4.8, scope3Change: -2.1,
      verified: true, fileSize: 2.6,
      initiatives: [
        { id: 1, title: 'Solar PPA Initiation', reduction: 7500, status: 'Completed' },
        { id: 2, title: 'Building Automation Upgrade', reduction: 2800, status: 'Completed' }
      ]
    },
    {
      id: `OFF-${currentYear}-006`, title: `Carbon Offset Report ${currentYear}`, type: 'offset', year: currentYearStr,
      description: `Carbon offset portfolio and retirement certificates for ${currentYear}.`,
      publishDate: `${currentYear}-05-01`, author: 'Carbon Management', pages: 45, downloads: 312,
      status: 'draft', version: 'v0.8',
      coverColor: '#d97706', coverColor2: '#b45309',
      scope1: 0, scope2: 0, scope3: 0, totalEmissions: 0,
      scope1Change: 0, scope2Change: 0, scope3Change: 0,
      verified: false, fileSize: 1.5,
      initiatives: [
        { id: 1, title: 'Forest Conservation Project', reduction: 25000, status: 'Completed' },
        { id: 2, title: 'Solar Farm Investment', reduction: 18000, status: 'In Progress' }
      ]
    }
  ]
}

const reportsData = ref<CarbonReport[]>(generateReportsData())

// ==================== State ====================
const searchText = ref('')
const reportTypeFilter = ref('')
const yearFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const detailDialogVisible = ref(false)
const generateDialogVisible = ref(false)
const selectedReport = ref<CarbonReport | null>(null)

// Chart ref
let trendChart: echarts.ECharts | null = null
const trendChartEl = ref<HTMLElement | null>(null)

const reportForm = ref({
  type: 'annual',
  year: currentYear.toString(),
  period: null as string[] | null,
  scopes: ['scope1', 'scope2', 'scope3'],
  title: ''
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalReports = reportsData.value.length
  const publishedReports = reportsData.value.filter(r => r.status === 'published').length
  const draftReports = reportsData.value.filter(r => r.status === 'draft').length
  const currentYearReports = reportsData.value.filter(r => r.year === currentYear.toString())
  const totalEmissions = currentYearReports.reduce((sum, r) => sum + r.totalEmissions, 0)
  return { totalReports, publishedReports, draftReports, totalEmissions: Math.round(totalEmissions / 1000) }
})

const filteredReports = computed(() => {
  let filtered = [...reportsData.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(search) ||
        r.description.toLowerCase().includes(search) ||
        r.author.toLowerCase().includes(search)
    )
  }

  if (reportTypeFilter.value) {
    filtered = filtered.filter(r => r.type === reportTypeFilter.value)
  }

  if (yearFilter.value) {
    filtered = filtered.filter(r => r.year === yearFilter.value)
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
const getReportTypeLabel = (type: string): string => {
  const map: Record<string, string> = {
    annual: 'Annual Carbon', inventory: 'Carbon Inventory', cdp: 'CDP Disclosure',
    tcfd: 'TCFD Report', offset: 'Offset Report'
  }
  return map[type] || type
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { published: 'Published', draft: 'Draft' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { published: 'success', draft: 'warning' }
  return map[status] || 'info'
}

// ==================== Chart Functions ====================
const initTrendChart = () => {
  if (!trendChartEl.value || !selectedReport.value) return
  if (trendChart) {
    trendChart.dispose()
    trendChart = null
  }

  const years = [currentYear - 3, currentYear - 2, currentYear - 1, currentYear]
  const scope1Data = [14500, 13800, 13200, selectedReport.value.scope1]
  const scope2Data = [21500, 20800, 20200, selectedReport.value.scope2]
  const scope3Data = [24500, 23800, 23200, selectedReport.value.scope3]

  trendChart = echarts.init(trendChartEl.value)
  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Scope 1', 'Scope 2', 'Scope 3'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: years },
    yAxis: { type: 'value', name: 'Emissions (tCO₂e)' },
    series: [
      { name: 'Scope 1', type: 'line', data: scope1Data, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle' },
      { name: 'Scope 2', type: 'line', data: scope2Data, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle' },
      { name: 'Scope 3', type: 'line', data: scope3Data, lineStyle: { color: '#22c55e', width: 2 }, symbol: 'circle' }
    ]
  })
}

// ==================== Actions ====================
const viewReport = (report: CarbonReport) => {
  selectedReport.value = report
  detailDialogVisible.value = true
  nextTick(() => initTrendChart())
}

const previewReport = (report: CarbonReport) => {
  ElMessage.info(`Previewing ${report.title}`)
  setTimeout(() => {
    ElMessage.success('Preview ready')
  }, 500)
}

const downloadReport = (report: CarbonReport, format = 'pdf') => {
  ElMessage.success(`Downloading ${report.title} (${format.toUpperCase()})...`)
  setTimeout(() => {
    ElMessage.success('Download completed')
  }, 1000)
}

const editReport = (report: CarbonReport | null) => {
  if (report) {
    ElMessage.info(`Editing ${report.title}`)
  }
}

const publishReport = (report: CarbonReport | null) => {
  if (report) {
    ElMessage.success(`${report.title} published successfully`)
  }
}

const createNewReport = () => {
  reportForm.value = {
    type: 'annual',
    year: currentYear.toString(),
    period: null,
    scopes: ['scope1', 'scope2', 'scope3'],
    title: `Carbon Report ${currentYear}`
  }
  generateDialogVisible.value = true
}

const saveReport = () => {
  ElMessage.success('Report generation started. You will be notified when ready.')
  generateDialogVisible.value = false
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Watch ====================
watch([searchText, reportTypeFilter, yearFilter], () => {
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
  window.addEventListener('resize', () => {
    if (trendChart && !trendChart.isDisposed()) trendChart.resize()
  })
})

onUnmounted(() => {
  if (trendChart && !trendChart.isDisposed()) trendChart.dispose()
})
</script>

<style scoped>
.carbon-reports-page {
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

/* Loading Screen */
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

.stat-icon.green { background: #dcfce7; color: #22c55e; }
.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.orange { background: #fef3c7; color: #f59e0b; }
.stat-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
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

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.section-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.report-cover {
  height: 140px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px;
  color: white;
}

.report-type-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
  width: fit-content;
}

.report-year {
  font-size: 42px;
  font-weight: 700;
  opacity: 0.3;
  position: absolute;
  bottom: 12px;
  right: 16px;
  line-height: 1;
}

.report-icon {
  font-size: 28px;
  opacity: 0.4;
}

.report-content {
  padding: 20px;
}

.report-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.report-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 12px;
}

.report-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  font-size: 12px;
  color: #64748b;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.report-stats {
  display: flex;
  gap: 20px;
  padding: 10px 0;
  border-top: 1px solid #eef2f8;
  border-bottom: 1px solid #eef2f8;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-item .stat-label {
  font-size: 11px;
  color: #94a3b8;
}

.stat-item .stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.report-emissions {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.emissions-item {
  flex: 1;
  text-align: center;
}

.emissions-label {
  font-size: 11px;
  color: #94a3b8;
  display: block;
}

.emissions-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.report-actions {
  display: flex;
  gap: 12px;
}

/* Report Detail */
.report-detail {
  overflow: hidden;
}

.detail-header {
  color: white;
  padding: 28px;
  margin: -20px -20px 0 -20px;
  border-radius: 20px 20px 0 0;
}

.detail-header-content h2 {
  margin: 16px 0 12px 0;
  font-size: 22px;
}

.detail-meta {
  display: flex;
  gap: 24px;
  font-size: 12px;
  opacity: 0.9;
  flex-wrap: wrap;
}

.detail-meta span {
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-content {
  padding: 24px 0 0 0;
}

.emissions-breakdown {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.breakdown-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
}

.breakdown-card.total {
  background: linear-gradient(135deg, #059669, #047857);
  color: white;
}

.breakdown-card.total .breakdown-value {
  color: white;
}

.breakdown-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.breakdown-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.breakdown-card.total .breakdown-label {
  color: rgba(255, 255, 255, 0.8);
}

.breakdown-change {
  font-size: 11px;
  margin-top: 8px;
}

.breakdown-change.positive { color: #22c55e; }
.breakdown-change.negative { color: #ef4444; }

.detail-section {
  margin-top: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #059669;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

.initiative-title {
  font-weight: 500;
}

.initiative-impact {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.downloads-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.download-card {
  flex: 1;
  min-width: 120px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.download-card:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
}

.download-card .el-icon {
  font-size: 28px;
  margin-bottom: 8px;
  color: #059669;
}

.download-card span {
  display: block;
  font-size: 13px;
}

.file-size {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Pagination */
.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 60px;
  background: white;
  border-radius: 20px;
  text-align: center;
}

/* Responsive */
@media (max-width: 1000px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
  .emissions-breakdown {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .reports-grid {
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
  .section-actions .el-input,
  .section-actions .el-select {
    width: 100% !important;
  }
  .emissions-breakdown {
    grid-template-columns: 1fr;
  }
  .downloads-grid {
    flex-direction: column;
  }
  .detail-meta {
    gap: 12px;
  }
}

/* Element Plus Overrides */
:deep(.el-button--primary) {
  background: #059669;
  border-color: #059669;
}
:deep(.el-button--primary:hover) {
  background: #047857;
}
:deep(.el-dialog__body) {
  padding: 20px;
}
</style>