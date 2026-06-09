<template>
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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Reports Evidence Repository</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="reports-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Decision & Evidence</el-breadcrumb-item>
            <el-breadcrumb-item>Evidence Repository</el-breadcrumb-item>
            <el-breadcrumb-item>Reports</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Reports Evidence Repository</h1>
        <p class="description">Manage and organize reports including audit reports, analysis reports, and compliance documentation</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export
        </el-button>
        <el-button type="primary" @click="handleGenerateReport">
          <el-icon><Plus /></el-icon>
          Generate Report
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="6" v-for="stat in statsCards" :key="stat.title">
        <el-card class="stat-card" shadow="hover" @click="handleCardClick(stat)">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
                <el-icon><component :is="stat.trend > 0 ? 'ArrowUp' : 'ArrowDown'" /></el-icon>
                {{ Math.abs(stat.trend) }}%
                <span class="trend-label">vs last month</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Report Generation Trends Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="16">
        <el-card class="trend-chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Report Generation Trends</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="quarterly">Quarterly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card class="distribution-chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Reports by Type</span>
            </div>
          </template>
          <div ref="typeChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Quick Filters -->
    <el-card class="quick-filters-card" shadow="hover">
      <div class="quick-filters">
        <span class="filter-label">Quick Filters:</span>
        <el-radio-group v-model="quickFilter" @change="handleQuickFilter">
          <el-radio-button value="all">All Reports</el-radio-button>
          <el-radio-button value="recent">Last 30 Days</el-radio-button>
          <el-radio-button value="high">High Priority</el-radio-button>
          <el-radio-button value="executive">Executive Summary</el-radio-button>
          <el-radio-button value="pending">Pending Review</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by title or description"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.reportType" placeholder="Report Type" clearable style="width: 150px">
            <el-option label="Audit Report" value="Audit Report" />
            <el-option label="Energy Report" value="Energy Report" />
            <el-option label="Maintenance Report" value="Maintenance Report" />
            <el-option label="Compliance Report" value="Compliance Report" />
            <el-option label="Financial Report" value="Financial Report" />
            <el-option label="ESG Report" value="ESG Report" />
            <el-option label="Performance Report" value="Performance Report" />
            <el-option label="Incident Report" value="Incident Report" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Final" value="Final" />
            <el-option label="Draft" value="Draft" />
            <el-option label="Under Review" value="Under Review" />
            <el-option label="Approved" value="Approved" />
          </el-select>
          <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 120px">
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 260px"
          />
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Reports Library ({{ filteredReports.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchReports" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedReports" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="Report Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="reportType" label="Report Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getReportTypeTag(row.reportType)" size="small">{{ row.reportType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="Priority" width="90">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="generatedBy" label="Generated By" width="130" />
        <el-table-column prop="generatedDate" label="Date" width="110" />
        <el-table-column prop="pages" label="Pages" width="70" align="center" />
        <el-table-column prop="views" label="Views" width="80" align="center" />
        <el-table-column prop="downloads" label="Downloads" width="90" align="center" />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewReport(row)">View</el-button>
            <el-button link type="success" size="small" @click="downloadReport(row)">Download</el-button>
            <el-button link type="info" size="small" @click="previewReport(row)">Preview</el-button>
            <el-button link type="danger" size="small" @click="deleteReport(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredReports.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateDialogVisible" title="Generate Report" width="650px" destroy-on-close>
      <el-form :model="generateForm" :rules="generateRules" ref="generateFormRef" label-width="120px">
        <el-form-item label="Report Title" prop="title">
          <el-input v-model="generateForm.title" placeholder="Enter report title" />
        </el-form-item>
        <el-form-item label="Report Type" prop="reportType">
          <el-select v-model="generateForm.reportType" placeholder="Select report type" style="width: 100%">
            <el-option label="Audit Report" value="Audit Report" />
            <el-option label="Energy Report" value="Energy Report" />
            <el-option label="Maintenance Report" value="Maintenance Report" />
            <el-option label="Compliance Report" value="Compliance Report" />
            <el-option label="Financial Report" value="Financial Report" />
            <el-option label="ESG Report" value="ESG Report" />
            <el-option label="Performance Report" value="Performance Report" />
            <el-option label="Incident Report" value="Incident Report" />
          </el-select>
        </el-form-item>
        <el-form-item label="Priority" prop="priority">
          <el-select v-model="generateForm.priority" placeholder="Select priority" style="width: 100%">
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Range" prop="dataRange">
          <el-date-picker
              v-model="generateForm.dataRange"
              type="daterange"
              range-separator="to"
              start-placeholder="Start Date"
              end-placeholder="End Date"
              style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="Format" prop="format">
          <el-radio-group v-model="generateForm.format">
            <el-radio value="PDF">PDF</el-radio>
            <el-radio value="DOCX">DOCX</el-radio>
            <el-radio value="XLSX">XLSX</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Include Charts" prop="includeCharts">
          <el-switch v-model="generateForm.includeCharts" />
        </el-form-item>
        <el-form-item label="Include Executive Summary" prop="includeExecutive">
          <el-switch v-model="generateForm.includeExecutive" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="generateForm.description" type="textarea" :rows="2" placeholder="Enter report description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="generating" @click="submitGenerate">Generate Report</el-button>
      </template>
    </el-dialog>

    <!-- Report Preview Dialog -->
    <el-dialog v-model="previewDialogVisible" :title="currentReport?.title" width="800px" destroy-on-close>
      <div class="preview-container">
        <div class="report-header">
          <div class="report-meta">
            <el-tag :type="getReportTypeTag(currentReport?.reportType || '')" size="default">{{ currentReport?.reportType }}</el-tag>
            <el-tag :type="getStatusTag(currentReport?.status || '')" size="default">{{ currentReport?.status }}</el-tag>
            <el-tag :type="getPriorityTag(currentReport?.priority || '')" size="default">{{ currentReport?.priority }} Priority</el-tag>
          </div>
          <div class="report-date">Generated: {{ currentReport?.generatedDate }}</div>
        </div>
        <div class="report-content">
          <div class="report-section">
            <h3>Executive Summary</h3>
            <p>{{ currentReport?.executiveSummary || 'No executive summary available.' }}</p>
          </div>
          <div class="report-section">
            <h3>Key Findings</h3>
            <ul>
              <li v-for="(finding, idx) in currentReport?.keyFindings" :key="idx">{{ finding }}</li>
            </ul>
          </div>
          <div class="report-section">
            <h3>Recommendations</h3>
            <ul>
              <li v-for="(rec, idx) in currentReport?.recommendations" :key="idx">{{ rec }}</li>
            </ul>
          </div>
          <div class="report-section">
            <h3>Metrics Summary</h3>
            <el-table :data="currentReport?.metrics || []" size="small" border>
              <el-table-column prop="metric" label="Metric" />
              <el-table-column prop="value" label="Value" width="150" />
              <el-table-column prop="change" label="Change" width="100">
                <template #default="{ row }">
                  <span :style="{ color: row.change > 0 ? '#67c23a' : '#f56c6c' }">
                    {{ row.change > 0 ? '+' : '' }}{{ row.change }}%
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadCurrentReport">Download</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete report "{{ deleteTarget?.title }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone.</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmDelete">Delete</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, ZoomIn, User, DataAnalysis, PieChart
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading report repository...',
  'Analyzing data...',
  'Almost ready...'
]

// ==================== Interfaces ====================
interface Report {
  id: number
  title: string
  description: string
  reportType: string
  status: string
  priority: string
  format: string
  pages: number
  generatedBy: string
  generatedDate: string
  views: number
  downloads: number
  url: string
  executiveSummary: string
  keyFindings: string[]
  recommendations: string[]
  metrics: Array<{ metric: string; value: string; change: number }>
  relatedDecisions: string[]
}

interface StatCard {
  title: string
  value: string | number
  trend: number
  icon: string
  bgColor: string
  key: string
}

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

const trendPeriod = ref<'monthly' | 'quarterly'>('monthly')

// ==================== Mock Data ====================
const statsCards = ref<StatCard[]>([
  { title: 'Total Reports', value: 243, trend: 15, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'This Month', value: 18, trend: 20, icon: 'TrendCharts', bgColor: '#67c23a', key: 'monthly' },
  { title: 'Total Views', value: '5.2K', trend: 28, icon: 'View', bgColor: '#e6a23c', key: 'views' },
  { title: 'Avg. Rating', value: '4.6', trend: 8, icon: 'Checked', bgColor: '#f56c6c', key: 'rating' }
])

const reports = ref<Report[]>([
  {
    id: 1,
    title: 'Q4 2023 Energy Consumption Audit Report',
    description: 'Comprehensive energy audit report covering Q4 2023 consumption patterns and efficiency recommendations',
    reportType: 'Energy Report',
    status: 'Final',
    priority: 'High',
    format: 'PDF',
    pages: 42,
    generatedBy: 'Lisa Zhang',
    generatedDate: '2024-01-05',
    views: 156,
    downloads: 67,
    url: '#',
    executiveSummary: 'Q4 2023 showed a 12% reduction in energy consumption compared to Q3, primarily driven by LED retrofit and HVAC optimization initiatives. Total consumption was 1.2M kWh, with peak demand reduced by 8%.',
    keyFindings: [
      'Lighting efficiency improved by 35% after LED retrofit',
      'HVAC optimization resulted in 15% energy savings',
      'Weekend consumption reduced by 22%',
      'Peak demand charges decreased by $4,200'
    ],
    recommendations: [
      'Implement additional occupancy sensors in low-traffic areas',
      'Upgrade remaining T8 fixtures to LED by Q2',
      'Install sub-meters for better load tracking',
      'Consider solar PV installation for further savings'
    ],
    metrics: [
      { metric: 'Total Consumption (kWh)', value: '1,245,000', change: -12 },
      { metric: 'Peak Demand (kW)', value: '1,850', change: -8 },
      { metric: 'Energy Cost ($)', value: '148,500', change: -10 },
      { metric: 'Carbon Emissions (tCO₂e)', value: '425', change: -12 }
    ],
    relatedDecisions: ['LED Lighting Retrofit', 'HVAC Optimization Algorithm']
  },
  {
    id: 2,
    title: 'Annual Maintenance Performance Report 2023',
    description: 'Annual report on maintenance activities, response times, and equipment reliability',
    reportType: 'Maintenance Report',
    status: 'Final',
    priority: 'High',
    format: 'PDF',
    pages: 58,
    generatedBy: 'John Smith',
    generatedDate: '2024-01-10',
    views: 203,
    downloads: 89,
    url: '#',
    executiveSummary: '2023 maintenance performance exceeded targets with 97% uptime and average response time of 2.4 hours. Completed 1,245 work orders with 92% on-time completion rate.',
    keyFindings: [
      'Equipment uptime improved from 94% to 97%',
      'Average response time reduced by 28%',
      'Preventive maintenance completion rate reached 95%',
      'Emergency work orders decreased by 15%'
    ],
    recommendations: [
      'Implement predictive maintenance for critical assets',
      'Expand spare parts inventory for high-failure components',
      'Schedule additional technician training',
      'Upgrade CMMS system for better analytics'
    ],
    metrics: [
      { metric: 'Equipment Uptime (%)', value: '97', change: 3 },
      { metric: 'Avg Response Time (hrs)', value: '2.4', change: -28 },
      { metric: 'Work Orders Completed', value: '1,245', change: 12 },
      { metric: 'MTTR (hours)', value: '3.2', change: -15 }
    ],
    relatedDecisions: ['Chiller Overhaul Decision', 'UPS Battery Replacement']
  },
  {
    id: 3,
    title: 'ESG Compliance Report - 2023',
    description: 'Environmental, Social, and Governance compliance report for 2023 fiscal year',
    reportType: 'ESG Report',
    status: 'Final',
    priority: 'High',
    format: 'PDF',
    pages: 86,
    generatedBy: 'Emily Zhao',
    generatedDate: '2024-01-03',
    views: 312,
    downloads: 145,
    url: '#',
    executiveSummary: 'ESG score improved from 72 to 78 points in 2023, exceeding target. Carbon emissions reduced by 15%, water usage by 10%, and waste diversion rate reached 85%.',
    keyFindings: [
      'Scope 2 emissions reduced by 18% through renewable energy',
      'Water conservation initiatives saved 2.5M gallons',
      'Diversity hiring increased by 25%',
      'Supplier sustainability compliance reached 92%'
    ],
    recommendations: [
      'Set Science Based Targets for 2030',
      'Expand EV charging infrastructure',
      'Implement full waste audit and reduction program',
      'Enhance ESG data collection systems'
    ],
    metrics: [
      { metric: 'ESG Score', value: '78', change: 8 },
      { metric: 'Scope 2 Emissions (tCO₂e)', value: '3,200', change: -18 },
      { metric: 'Water Usage (gallons)', value: '2,250,000', change: -10 },
      { metric: 'Waste Diversion Rate (%)', value: '85', change: 12 }
    ],
    relatedDecisions: ['Solar Panel Installation']
  },
  {
    id: 4,
    title: 'Financial Audit Report - Operations',
    description: 'Internal audit report on operational expenditures and budget compliance',
    reportType: 'Financial Report',
    status: 'Approved',
    priority: 'Medium',
    format: 'PDF',
    pages: 34,
    generatedBy: 'Anna Kim',
    generatedDate: '2024-01-08',
    views: 98,
    downloads: 34,
    url: '#',
    executiveSummary: 'Operations budget 2.5% under target with 98% spend efficiency. Identified $125,000 in potential savings through process optimization.',
    keyFindings: [
      'Total spend: $4.2M vs budget $4.31M',
      'Maintenance costs 8% below forecast',
      'Energy costs 12% below budget due to efficiency',
      'Procurement savings of $85,000 identified'
    ],
    recommendations: [
      'Renegotiate vendor contracts for better rates',
      'Implement spend analytics dashboard',
      'Optimize inventory carrying costs',
      'Automate approval workflows'
    ],
    metrics: [
      { metric: 'Budget Variance (%)', value: '-2.5', change: -1.2 },
      { metric: 'Cost Savings ($)', value: '125,000', change: 15 },
      { metric: 'Spend Efficiency (%)', value: '98', change: 2 },
      { metric: 'PO Cycle Time (days)', value: '3.5', change: -0.8 }
    ],
    relatedDecisions: []
  },
  {
    id: 5,
    title: 'Safety Compliance Audit - January',
    description: 'Monthly safety compliance audit report covering all facilities',
    reportType: 'Compliance Report',
    status: 'Under Review',
    priority: 'High',
    format: 'PDF',
    pages: 28,
    generatedBy: 'Robert Liu',
    generatedDate: '2024-01-12',
    views: 67,
    downloads: 23,
    url: '#',
    executiveSummary: 'Monthly safety audit identified 8 minor findings, all resolved within 48 hours. No major violations. Overall compliance score: 96%.',
    keyFindings: [
      'Fire extinguisher inspections all current',
      'Emergency lighting tested and functional',
      '3 near-miss incidents reported and investigated',
      'PPE compliance rate at 98%'
    ],
    recommendations: [
      'Schedule additional safety training for new staff',
      'Update evacuation maps in common areas',
      'Conduct emergency drill next month'
    ],
    metrics: [
      { metric: 'Compliance Score (%)', value: '96', change: 2 },
      { metric: 'Open Findings', value: '0', change: -100 },
      { metric: 'Near Misses', value: '3', change: -25 },
      { metric: 'Training Completion (%)', value: '94', change: 5 }
    ],
    relatedDecisions: []
  },
  {
    id: 6,
    title: 'Incident Investigation Report - UPS Failure',
    description: 'Detailed investigation report on UPS battery failure incident',
    reportType: 'Incident Report',
    status: 'Final',
    priority: 'High',
    format: 'PDF',
    pages: 22,
    generatedBy: 'Tom Harris',
    generatedDate: '2024-01-09',
    views: 145,
    downloads: 78,
    url: '#',
    executiveSummary: 'UPS battery failure caused by thermal runaway in aging batteries. Immediate replacement prevented data loss. Root cause identified as exceeded lifecycle.',
    keyFindings: [
      'Batteries exceeded recommended lifecycle by 18 months',
      'Temperature monitoring detected anomalies 72 hours prior',
      'No critical load interruption due to redundant systems',
      'Maintenance logs showed overdue replacement'
    ],
    recommendations: [
      'Implement predictive battery monitoring',
      'Reduce battery replacement cycle from 5 to 4 years',
      'Add additional temperature sensors',
      'Schedule quarterly capacity testing'
    ],
    metrics: [
      { metric: 'Downtime (minutes)', value: '0', change: 0 },
      { metric: 'Impact Severity', value: 'Medium', change: 0 },
      { metric: 'Resolution Time (hours)', value: '6', change: 0 }
    ],
    relatedDecisions: ['UPS Battery Replacement']
  },
  {
    id: 7,
    title: 'Quarterly Performance Dashboard - Q4 2023',
    description: 'Executive dashboard summarizing key operational metrics for Q4 2023',
    reportType: 'Performance Report',
    status: 'Final',
    priority: 'Medium',
    format: 'PDF',
    pages: 16,
    generatedBy: 'Sarah Chen',
    generatedDate: '2024-01-02',
    views: 267,
    downloads: 123,
    url: '#',
    executiveSummary: 'Q4 performance exceeded targets across all key metrics. Operational efficiency improved by 8%, customer satisfaction at 94%.',
    keyFindings: [
      'Overall KPI achievement: 95%',
      'Energy efficiency exceeded target by 12%',
      'Maintenance response time improved by 22%',
      'Cost savings: $187,000 against target'
    ],
    recommendations: [
      'Maintain current improvement trajectory',
      'Invest in additional automation',
      'Expand AI-driven optimization'
    ],
    metrics: [
      { metric: 'KPI Achievement (%)', value: '95', change: 5 },
      { metric: 'Operational Efficiency (%)', value: '88', change: 8 },
      { metric: 'Customer Satisfaction', value: '94', change: 3 },
      { metric: 'Cost Savings ($)', value: '187,000', change: 25 }
    ],
    relatedDecisions: []
  },
  {
    id: 8,
    title: 'Draft: HVAC Upgrade Feasibility Study',
    description: 'Feasibility study for comprehensive HVAC system upgrade',
    reportType: 'Energy Report',
    status: 'Draft',
    priority: 'Medium',
    format: 'DOCX',
    pages: 45,
    generatedBy: 'David Wang',
    generatedDate: '2024-01-11',
    views: 34,
    downloads: 12,
    url: '#',
    executiveSummary: 'Preliminary analysis shows 30% energy savings potential with 4-year payback period for HVAC upgrade. Requires further validation.',
    keyFindings: [
      'Current system efficiency: 12-15 years old',
      'Potential savings: 850,000 kWh annually',
      'Estimated ROI: 25% over 10 years',
      'Available incentives: $50,000 from utility'
    ],
    recommendations: [
      'Conduct detailed engineering study',
      'Apply for incentive funding',
      'Develop phased implementation plan'
    ],
    metrics: [
      { metric: 'Potential Savings (kWh)', value: '850,000', change: 0 },
      { metric: 'Payback Period (years)', value: '4.2', change: 0 },
      { metric: 'ROI (%)', value: '25', change: 0 }
    ],
    relatedDecisions: []
  }
])

// ==================== Reactive Variables ====================
const loading = ref(false)
const generating = ref(false)
const generateDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const currentReport = ref<Report | null>(null)
const deleteTarget = ref<Report | null>(null)
const generateFormRef = ref()
const quickFilter = ref('all')
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  reportType: '',
  status: '',
  priority: '',
  dateRange: null as [Date, Date] | null
})

const generateForm = reactive({
  title: '',
  reportType: '',
  priority: 'Medium',
  dataRange: null as [Date, Date] | null,
  format: 'PDF',
  includeCharts: true,
  includeExecutive: true,
  description: ''
})

const generateRules = {
  title: [{ required: true, message: 'Please enter report title', trigger: 'blur' }],
  reportType: [{ required: true, message: 'Please select report type', trigger: 'change' }],
  dataRange: [{ required: true, message: 'Please select data range', trigger: 'change' }]
}

// ==================== Computed ====================
const filteredReports = computed(() => {
  let filtered = [...reports.value]

  // Apply quick filter
  if (quickFilter.value === 'recent') {
    const thirtyDaysAgo = new Date()
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
    filtered = filtered.filter(r => new Date(r.generatedDate) >= thirtyDaysAgo)
  } else if (quickFilter.value === 'high') {
    filtered = filtered.filter(r => r.priority === 'High')
  } else if (quickFilter.value === 'executive') {
    filtered = filtered.filter(r => r.reportType === 'Performance Report' || r.reportType === 'ESG Report')
  } else if (quickFilter.value === 'pending') {
    filtered = filtered.filter(r => r.status === 'Under Review' || r.status === 'Draft')
  }

  // Apply search filters
  if (filters.keyword) {
    filtered = filtered.filter(r =>
        r.title.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        r.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.reportType) {
    filtered = filtered.filter(r => r.reportType === filters.reportType)
  }

  if (filters.status) {
    filtered = filtered.filter(r => r.status === filters.status)
  }

  if (filters.priority) {
    filtered = filtered.filter(r => r.priority === filters.priority)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(r => {
      const date = new Date(r.generatedDate)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedReports = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredReports.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getReportTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Audit Report': 'danger',
    'Energy Report': 'success',
    'Maintenance Report': 'warning',
    'Compliance Report': 'primary',
    'Financial Report': 'info',
    'ESG Report': 'success',
    'Performance Report': 'primary',
    'Incident Report': 'danger'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Final': 'success',
    'Draft': 'info',
    'Under Review': 'warning',
    'Approved': 'success'
  }
  return map[status] || 'info'
}

const getPriorityTag = (priority: string): string => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[priority] || 'info'
}

// ==================== Chart Initialization ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Energy Reports', 'Maintenance Reports', 'Compliance Reports', 'ESG Reports', 'Other'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'Number of Reports' },
    series: [
      { name: 'Energy Reports', type: 'bar', data: [5, 6, 4, 7, 5, 8, 6, 7, 5, 8, 6, 9], stack: 'total' },
      { name: 'Maintenance Reports', type: 'bar', data: [3, 4, 5, 3, 6, 4, 5, 7, 4, 6, 5, 7], stack: 'total' },
      { name: 'Compliance Reports', type: 'bar', data: [4, 3, 5, 4, 3, 5, 4, 3, 5, 4, 3, 5], stack: 'total' },
      { name: 'ESG Reports', type: 'bar', data: [2, 2, 3, 2, 3, 2, 3, 4, 2, 3, 4, 3], stack: 'total' },
      { name: 'Other', type: 'bar', data: [3, 2, 3, 4, 2, 3, 3, 2, 4, 3, 2, 4], stack: 'total' }
    ]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()

  typeChart = echarts.init(typeChartRef.value)

  const typeCount = {
    'Energy Report': reports.value.filter(r => r.reportType === 'Energy Report').length,
    'Maintenance Report': reports.value.filter(r => r.reportType === 'Maintenance Report').length,
    'Compliance Report': reports.value.filter(r => r.reportType === 'Compliance Report').length,
    'ESG Report': reports.value.filter(r => r.reportType === 'ESG Report').length,
    'Financial Report': reports.value.filter(r => r.reportType === 'Financial Report').length,
    'Performance Report': reports.value.filter(r => r.reportType === 'Performance Report').length,
    'Incident Report': reports.value.filter(r => r.reportType === 'Incident Report').length
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} reports)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: typeCount['Energy Report'], name: 'Energy Report', itemStyle: { color: '#67c23a' } },
        { value: typeCount['Maintenance Report'], name: 'Maintenance Report', itemStyle: { color: '#e6a23c' } },
        { value: typeCount['Compliance Report'], name: 'Compliance Report', itemStyle: { color: '#409eff' } },
        { value: typeCount['ESG Report'], name: 'ESG Report', itemStyle: { color: '#67c23a' } },
        { value: typeCount['Financial Report'], name: 'Financial Report', itemStyle: { color: '#f56c6c' } },
        { value: typeCount['Performance Report'], name: 'Performance Report', itemStyle: { color: '#909399' } },
        { value: typeCount['Incident Report'], name: 'Incident Report', itemStyle: { color: '#f56c6c' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  typeChart.setOption(option)
  window.addEventListener('resize', () => typeChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: StatCard) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleQuickFilter = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.reportType = ''
  filters.status = ''
  filters.priority = ''
  filters.dateRange = null
  quickFilter.value = 'all'
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredReports.value.length} reports metadata...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchReports = () => {
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleGenerateReport = () => {
  generateDialogVisible.value = true
}

const submitGenerate = async () => {
  if (!generateFormRef.value) return
  await generateFormRef.value.validate((valid: boolean) => {
    if (valid) {
      generating.value = true
      setTimeout(() => {
        generating.value = false
        generateDialogVisible.value = false
        ElMessage.success(`Report "${generateForm.title}" generated successfully`)

        // Add new report to list
        const newReport: Report = {
          id: Date.now(),
          title: generateForm.title,
          description: generateForm.description,
          reportType: generateForm.reportType,
          status: 'Draft',
          priority: generateForm.priority,
          format: generateForm.format,
          pages: 0,
          generatedBy: 'Current User',
          generatedDate: new Date().toISOString().split('T')[0],
          views: 0,
          downloads: 0,
          url: '#',
          executiveSummary: 'Executive summary will be generated automatically.',
          keyFindings: ['Key finding 1', 'Key finding 2'],
          recommendations: ['Recommendation 1', 'Recommendation 2'],
          metrics: [],
          relatedDecisions: []
        }
        reports.value.unshift(newReport)

        generateFormRef.value?.resetFields()
        initTypeChart()
      }, 2000)
    }
  })
}

const viewReport = (report: Report) => {
  const index = reports.value.findIndex(r => r.id === report.id)
  if (index !== -1) {
    reports.value[index].views++
  }
  currentReport.value = report
  previewDialogVisible.value = true
}

const previewReport = (report: Report) => {
  viewReport(report)
}

const downloadReport = (report: Report) => {
  const index = reports.value.findIndex(r => r.id === report.id)
  if (index !== -1) {
    reports.value[index].downloads++
  }
  ElMessage.success(`Downloading: ${report.title}`)
}

const downloadCurrentReport = () => {
  if (currentReport.value) {
    downloadReport(currentReport.value)
  }
}

const deleteReport = (report: Report) => {
  deleteTarget.value = report
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = reports.value.findIndex(r => r.id === deleteTarget.value!.id)
    if (index !== -1) {
      reports.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.title}`)
      initTypeChart()
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
    initTypeChart()
  }, 100)
}

onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 400)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      initCharts()
      fetchReports()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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

.spinner-ring:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: 0s;
}

.spinner-ring:nth-child(2) {
  border-right-color: #f59e0b;
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

@keyframes pulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ==================== Main Page Styles ==================== */
.reports-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;

  .breadcrumb {
    margin-bottom: 8px;
  }

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .description {
    color: #909399;
    font-size: 14px;
    margin: 0;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
  }

  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stat-info {
    flex: 1;
  }

  .stat-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .stat-trend {
    font-size: 12px;
    display: flex;
    align-items: center;
    gap: 4px;

    &.up { color: #67c23a; }
    &.down { color: #f56c6c; }

    .trend-label {
      color: #909399;
      margin-left: 4px;
    }
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.chart-row {
  margin-bottom: 20px;
}

.trend-chart-card, .distribution-chart-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.chart-container {
  width: 100%;
  height: 320px;
}

.pie-chart-container {
  width: 100%;
  height: 300px;
}

.quick-filters-card {
  margin-bottom: 20px;

  .quick-filters {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;

    .filter-label {
      font-weight: 600;
      color: #303133;
    }
  }
}

.filter-card {
  margin-bottom: 20px;

  .filter-container {
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
    }
  }
}

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.preview-container {
  .report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #ebeef5;

    .report-meta {
      display: flex;
      gap: 8px;
    }

    .report-date {
      color: #909399;
      font-size: 13px;
    }
  }

  .report-content {
    .report-section {
      margin-bottom: 24px;

      h3 {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid #409eff;
        display: inline-block;
      }

      p {
        color: #606266;
        line-height: 1.6;
        margin: 0;
      }

      ul {
        margin: 0;
        padding-left: 20px;

        li {
          color: #606266;
          line-height: 1.8;
        }
      }
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>