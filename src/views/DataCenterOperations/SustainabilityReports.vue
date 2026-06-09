<template>
  <div class="sustainability-reports-container">
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
            <span class="loading-title">Loading Sustainability Reports</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">ESG Reporting & Compliance Platform</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="reports-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Sustainability Reports</h1>
          <p class="page-subtitle">ESG reporting, carbon analytics, and compliance documentation</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="generateNewReport">
            <el-icon><Plus /></el-icon>
            Generate Report
          </el-button>
          <el-button @click="scheduleReport">
            <el-icon><Timer /></el-icon>
            Schedule
          </el-button>
          <el-button @click="openComplianceCenter">
            <el-icon><DocumentChecked /></el-icon>
            Compliance Center
          </el-button>
        </div>
      </div>

      <!-- Key Metrics Banner -->
      <div class="metrics-banner">
        <el-row :gutter="20">
          <el-col :span="6">
            <div class="metric-banner-item">
              <div class="metric-icon green"><el-icon><TrendCharts /></el-icon></div>
              <div class="metric-info">
                <span class="metric-label">Total Reports</span>
                <span class="metric-value">{{ totalReports }}</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-banner-item">
              <div class="metric-icon blue"><el-icon><DataLine /></el-icon></div>
              <div class="metric-info">
                <span class="metric-label">Carbon Reduction</span>
                <span class="metric-value">{{ carbonReduction }}%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-banner-item">
              <div class="metric-icon orange"><el-icon><Connection /></el-icon></div>
              <div class="metric-info">
                <span class="metric-label">Compliance Score</span>
                <span class="metric-value">{{ complianceScore }}%</span>
              </div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-banner-item">
              <div class="metric-icon purple"><el-icon><Calendar /></el-icon></div>
              <div class="metric-info">
                <span class="metric-label">Next Deadline</span>
                <span class="metric-value">{{ nextDeadline }}</span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Main Tabs -->
      <el-tabs v-model="activeTab" class="reports-tabs" @tab-click="handleTabChange">
        <!-- ESG Reports Tab -->
        <el-tab-pane label="ESG Reports" name="esg">
          <div class="tab-content">
            <div class="section-header">
              <h3>ESG Reports Library</h3>
              <div class="header-controls">
                <el-input v-model="esgSearch" placeholder="Search reports..." prefix-icon="Search" style="width: 200px" clearable />
                <el-select v-model="esgYear" placeholder="Year" style="width: 100px">
                  <el-option label="2024" value="2024" />
                  <el-option label="2023" value="2023" />
                  <el-option label="2022" value="2022" />
                  <el-option label="2021" value="2021" />
                </el-select>
                <el-select v-model="esgFramework" placeholder="Framework" style="width: 120px">
                  <el-option label="All" value="all" />
                  <el-option label="GRI" value="gri" />
                  <el-option label="SASB" value="sasb" />
                  <el-option label="TCFD" value="tcfd" />
                  <el-option label="CSRD" value="csrd" />
                </el-select>
              </div>
            </div>
            <el-row :gutter="20">
              <el-col :span="8" v-for="report in filteredEsgReports" :key="report.id">
                <el-card class="report-card" shadow="hover" @click="viewReport(report)">
                  <div class="report-icon" :style="{ background: report.color }">
                    <el-icon><component :is="report.icon" /></el-icon>
                  </div>
                  <div class="report-info">
                    <h4>{{ report.title }}</h4>
                    <p>{{ report.description }}</p>
                    <div class="report-meta">
                      <span><el-icon><Calendar /></el-icon> {{ report.date }}</span>
                      <span><el-icon><Document /></el-icon> {{ report.framework }}</span>
                    </div>
                  </div>
                  <div class="report-actions">
                    <el-button link type="primary" @click.stop="downloadReport(report)">Download</el-button>
                    <el-button link @click.stop="shareReport(report)">Share</el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- Carbon Reports Tab -->
        <el-tab-pane label="Carbon Reports" name="carbon">
          <div class="tab-content">
            <div class="section-header">
              <h3>Carbon Emissions Reports</h3>
              <div class="header-controls">
                <el-select v-model="carbonScope" placeholder="Scope" style="width: 120px">
                  <el-option label="All Scopes" value="all" />
                  <el-option label="Scope 1" value="scope1" />
                  <el-option label="Scope 2" value="scope2" />
                  <el-option label="Scope 3" value="scope3" />
                </el-select>
                <el-date-picker v-model="carbonDateRange" type="daterange" range-separator="To" start-placeholder="Start" end-placeholder="End" style="width: 240px" />
              </div>
            </div>

            <!-- Carbon Overview Charts -->
            <el-row :gutter="20" style="margin-bottom: 24px">
              <el-col :span="12">
                <el-card class="chart-card">
                  <div class="card-header">
                    <span>Carbon Emissions Trend</span>
                    <el-tag type="success" size="small">-12.5% YoY</el-tag>
                  </div>
                  <div ref="carbonTrendChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <div class="card-header">
                    <span>Emissions by Scope</span>
                    <el-tooltip content="Scope 1: Direct, Scope 2: Energy indirect, Scope 3: Other indirect" placement="top">
                      <el-icon><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <div ref="scopeChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
            </el-row>

            <!-- Carbon Reports List -->
            <div class="reports-list">
              <div v-for="report in filteredCarbonReports" :key="report.id" class="report-list-item">
                <div class="item-icon" :style="{ background: getCarbonColor(report.scope) }">
                  <el-icon><Cloudy /></el-icon>
                </div>
                <div class="item-info">
                  <div class="item-title">{{ report.title }}</div>
                  <div class="item-meta">
                    <span>{{ report.date }}</span>
                    <span>{{ report.scope }}</span>
                    <span>{{ report.total }} tCO₂e</span>
                  </div>
                </div>
                <div class="item-progress">
                  <el-progress :percentage="report.progress" :stroke-width="8" :color="getProgressColor(report.progress)" />
                </div>
                <div class="item-actions">
                  <el-button type="primary" link @click="viewReport(report)">View</el-button>
                  <el-button link @click="downloadReport(report)">Download</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Energy Reports Tab -->
        <el-tab-pane label="Energy Reports" name="energy">
          <div class="tab-content">
            <div class="section-header">
              <h3>Energy Consumption Reports</h3>
              <div class="header-controls">
                <el-select v-model="energyType" placeholder="Energy Type" style="width: 120px">
                  <el-option label="All" value="all" />
                  <el-option label="Electricity" value="electricity" />
                  <el-option label="Gas" value="gas" />
                  <el-option label="Water" value="water" />
                  <el-option label="Renewable" value="renewable" />
                </el-select>
                <el-select v-model="energyPeriod" placeholder="Period" style="width: 100px">
                  <el-option label="Monthly" value="monthly" />
                  <el-option label="Quarterly" value="quarterly" />
                  <el-option label="Yearly" value="yearly" />
                </el-select>
              </div>
            </div>

            <!-- Energy Charts -->
            <el-row :gutter="20" style="margin-bottom: 24px">
              <el-col :span="12">
                <el-card class="chart-card">
                  <div class="card-header">
                    <span>Energy Consumption by Source</span>
                  </div>
                  <div ref="energyMixChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card class="chart-card">
                  <div class="card-header">
                    <span>Renewable Energy Ratio</span>
                  </div>
                  <div ref="renewableChartRef" class="chart-container"></div>
                </el-card>
              </el-col>
            </el-row>

            <!-- PUE Analysis -->
            <el-card class="pue-card">
              <div class="card-header">
                <span>Data Center PUE Analysis</span>
                <el-tag type="primary">Target: 1.35</el-tag>
              </div>
              <div ref="pueChartRef" class="pue-chart-container"></div>
              <div class="pue-stats">
                <div class="pue-stat-item">
                  <span class="stat-label">Current PUE</span>
                  <span class="stat-value">1.42</span>
                  <span class="stat-trend down">-0.03</span>
                </div>
                <div class="pue-stat-item">
                  <span class="stat-label">Best PUE</span>
                  <span class="stat-value">1.38</span>
                  <span class="stat-trend">Jan 2024</span>
                </div>
                <div class="pue-stat-item">
                  <span class="stat-label">Industry Average</span>
                  <span class="stat-value">1.58</span>
                  <span class="stat-trend">-0.16</span>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>

        <!-- Green Finance Tab -->
        <el-tab-pane label="Green Finance" name="finance">
          <div class="tab-content">
            <div class="section-header">
              <h3>Green Finance & Sustainability-Linked Loans</h3>
              <el-button type="primary" @click="applyGreenLoan">Apply for Green Loan</el-button>
            </div>

            <!-- Finance Metrics -->
            <el-row :gutter="20" style="margin-bottom: 24px">
              <el-col :span="8">
                <div class="finance-metric-card">
                  <div class="metric-title">Green Bond Issued</div>
                  <div class="metric-amount">$250M</div>
                  <div class="metric-rate">Interest Rate: 3.2%</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="finance-metric-card">
                  <div class="metric-title">Sustainability-Linked Loan</div>
                  <div class="metric-amount">$500M</div>
                  <div class="metric-rate">KPI: Carbon Reduction</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="finance-metric-card">
                  <div class="metric-title">Green Investment</div>
                  <div class="metric-amount">$180M</div>
                  <div class="metric-rate">ROI: 12.5%</div>
                </div>
              </el-col>
            </el-row>

            <!-- Finance Reports -->
            <el-row :gutter="20">
              <el-col :span="12" v-for="report in financeReports" :key="report.id">
                <el-card class="finance-report-card" shadow="hover">
                  <div class="report-header">
                    <div class="report-type">{{ report.type }}</div>
                    <el-tag :type="getFinanceTagType(report.status)">{{ report.status }}</el-tag>
                  </div>
                  <h4>{{ report.title }}</h4>
                  <p>{{ report.description }}</p>
                  <div class="report-footer">
                    <span>{{ report.date }}</span>
                    <el-button type="primary" link @click="viewFinanceReport(report)">View Details →</el-button>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>

        <!-- Compliance Reports Tab -->
        <el-tab-pane label="Compliance" name="compliance">
          <div class="tab-content">
            <div class="section-header">
              <h3>Regulatory Compliance Reports</h3>
              <el-button type="primary" @click="runComplianceCheck">Run Compliance Check</el-button>
            </div>

            <!-- Compliance Score Dashboard -->
            <el-row :gutter="20" style="margin-bottom: 24px">
              <el-col :span="16">
                <el-card class="compliance-card">
                  <div ref="complianceChartRef" class="compliance-chart-container"></div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <div class="compliance-summary">
                  <div class="summary-score">
                    <div class="score-value">94<span>%</span></div>
                    <div class="score-label">Overall Compliance</div>
                  </div>
                  <div class="summary-stats">
                    <div class="stat-row">
                      <span>GRI Standards</span>
                      <el-progress :percentage="98" :stroke-width="6" color="#10b981" />
                    </div>
                    <div class="stat-row">
                      <span>SASB</span>
                      <el-progress :percentage="92" :stroke-width="6" color="#10b981" />
                    </div>
                    <div class="stat-row">
                      <span>TCFD</span>
                      <el-progress :percentage="88" :stroke-width="6" color="#f59e0b" />
                    </div>
                    <div class="stat-row">
                      <span>CSRD</span>
                      <el-progress :percentage="85" :stroke-width="6" color="#f59e0b" />
                    </div>
                  </div>
                </div>
              </el-col>
            </el-row>

            <!-- Compliance Reports List -->
            <div class="compliance-reports">
              <div v-for="report in complianceReports" :key="report.id" class="compliance-report-item">
                <div class="report-status" :class="report.status">
                  <el-icon><CircleCheck v-if="report.status === 'compliant'" /><WarningFilled v-else /></el-icon>
                </div>
                <div class="report-details">
                  <div class="report-name">{{ report.name }}</div>
                  <div class="report-reg">{{ report.regulation }}</div>
                </div>
                <div class="report-date">{{ report.date }}</div>
                <div class="report-actions">
                  <el-button size="small" @click="viewComplianceReport(report)">View</el-button>
                  <el-button size="small" type="primary" @click="downloadComplianceReport(report)">Download</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="exportAllReports">
          <el-icon><Download /></el-icon>
          Export All Reports
        </el-button>
        <el-button size="large" @click="scheduleAutoReports">
          <el-icon><Setting /></el-icon>
          Auto-Report Settings
        </el-button>
        <el-button size="large" @click="openDataVerification">
          <el-icon><Lock /></el-icon>
          Data Verification
        </el-button>
      </div>
    </div>

    <!-- Report Preview Dialog -->
    <el-dialog v-model="previewDialogVisible" :title="previewReport?.title" width="800px" class="report-preview-dialog">
      <div class="report-preview-content">
        <div class="preview-header">
          <div class="preview-meta">
            <span><el-icon><Calendar /></el-icon> {{ previewReport?.date }}</span>
            <span><el-icon><Document /></el-icon> {{ previewReport?.framework || previewReport?.scope }}</span>
          </div>
          <el-tag :type="getReportTagType(previewReport?.status)">{{ previewReport?.status || 'Published' }}</el-tag>
        </div>
        <div class="preview-stats" v-if="previewReport?.stats">
          <div v-for="stat in previewReport.stats" :key="stat.label" class="preview-stat">
            <span class="stat-label">{{ stat.label }}</span>
            <span class="stat-value">{{ stat.value }}</span>
          </div>
        </div>
        <div class="preview-chart" ref="previewChartRef"></div>
        <div class="preview-summary">
          <h4>Executive Summary</h4>
          <p>{{ previewReport?.summary || 'This report provides comprehensive sustainability performance data including carbon emissions, energy consumption, and ESG metrics aligned with international standards.' }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadReport(previewReport)">Download PDF</el-button>
        <el-button @click="shareReport(previewReport)">Share</el-button>
      </template>
    </el-dialog>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateDialogVisible" title="Generate New Report" width="500px">
      <el-form :model="newReportForm" label-width="120px">
        <el-form-item label="Report Type" required>
          <el-select v-model="newReportForm.type" placeholder="Select type" style="width: 100%">
            <el-option label="ESG Report" value="esg" />
            <el-option label="Carbon Report" value="carbon" />
            <el-option label="Energy Report" value="energy" />
            <el-option label="Compliance Report" value="compliance" />
            <el-option label="Green Finance Report" value="finance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reporting Period">
          <el-date-picker v-model="newReportForm.period" type="daterange" range-separator="To" start-placeholder="Start" end-placeholder="End" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Framework">
          <el-select v-model="newReportForm.framework" placeholder="Select framework" style="width: 100%">
            <el-option label="GRI Standards" value="gri" />
            <el-option label="SASB" value="sasb" />
            <el-option label="TCFD" value="tcfd" />
            <el-option label="CSRD" value="csrd" />
            <el-option label="IFRS S2" value="ifrs" />
          </el-select>
        </el-form-item>
        <el-form-item label="Format">
          <el-radio-group v-model="newReportForm.format">
            <el-radio label="pdf">PDF</el-radio>
            <el-radio label="excel">Excel</el-radio>
            <el-radio label="both">Both</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmGenerateReport">Generate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, Timer, DocumentChecked, TrendCharts, DataLine, Connection,
  Calendar, Document, Search, InfoFilled, Cloudy, Download, Setting,
  Lock, CircleCheck, WarningFilled, Share, Edit, Link, Star
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading sustainability data...')

// ==================== Reactive Data ====================
const activeTab = ref('esg')
const esgSearch = ref('')
const esgYear = ref('2024')
const esgFramework = ref('all')
const carbonScope = ref('all')
const carbonDateRange = ref<[Date, Date] | null>(null)
const energyType = ref('all')
const energyPeriod = ref('yearly')
const previewDialogVisible = ref(false)
const generateDialogVisible = ref(false)
const previewReport = ref<any>(null)

// Metrics
const totalReports = ref(24)
const carbonReduction = ref(12.5)
const complianceScore = ref(94)
const nextDeadline = ref('Mar 31, 2024')

// ESG Reports Data
const esgReports = ref([
  { id: 1, title: 'Annual ESG Report 2024', description: 'Comprehensive environmental, social, and governance performance', date: '2024-01-15', framework: 'GRI', color: '#10b981', icon: 'TrendCharts', status: 'published', summary: 'Our 2024 ESG report highlights significant progress in carbon reduction, renewable energy adoption, and diversity initiatives.' },
  { id: 2, title: 'Sustainability Report', description: 'TCFD-aligned climate risk assessment', date: '2023-11-20', framework: 'TCFD', color: '#3b82f6', icon: 'DataLine', status: 'published' },
  { id: 3, title: 'ESG Performance Summary', description: 'Key metrics and achievements', date: '2023-09-10', framework: 'SASB', color: '#8b5cf6', icon: 'Connection', status: 'published' },
  { id: 4, title: 'CSRD Compliance Report', description: 'EU Corporate Sustainability Reporting Directive', date: '2023-12-05', framework: 'CSRD', color: '#f59e0b', icon: 'DocumentChecked', status: 'draft' },
  { id: 5, title: 'IFRS S2 Climate Disclosure', description: 'International sustainability standards', date: '2024-02-01', framework: 'IFRS', color: '#ef4444', icon: 'Document', status: 'published' },
  { id: 6, title: 'Stakeholder Engagement Report', description: 'Materiality assessment and stakeholder feedback', date: '2023-08-15', framework: 'GRI', color: '#06b6d4', icon: 'Share', status: 'published' },
])

// Carbon Reports Data
const carbonReports = ref([
  { id: 1, title: 'Scope 1 Emissions Report - Q4 2024', scope: 'Scope 1', total: 12500, progress: 85, date: '2024-01-10', status: 'verified' },
  { id: 2, title: 'Scope 2 Emissions Report - Q4 2024', scope: 'Scope 2', total: 8500, progress: 92, date: '2024-01-10', status: 'verified' },
  { id: 3, title: 'Scope 3 Supply Chain Emissions', scope: 'Scope 3', total: 45000, progress: 68, date: '2023-12-15', status: 'draft' },
  { id: 4, title: 'Carbon Reduction Roadmap 2025', scope: 'All Scopes', total: 66000, progress: 75, date: '2024-01-20', status: 'published' },
])

// Finance Reports
const financeReports = ref([
  { id: 1, type: 'Green Bond', title: 'Green Bond Allocation Report', description: 'Proceeds allocated to renewable energy and energy efficiency projects', date: '2024-01-15', status: 'audited' },
  { id: 2, type: 'Sustainability-Linked Loan', title: 'SLL Performance Report', description: 'KPIs met: Carbon intensity reduction 15%', date: '2023-12-20', status: 'verified' },
])

// Compliance Reports
const complianceReports = ref([
  { id: 1, name: 'GRI Standards Compliance', regulation: 'Global Reporting Initiative', date: '2024-01-15', status: 'compliant' },
  { id: 2, name: 'TCFD Alignment Check', regulation: 'Task Force on Climate-related Financial Disclosures', date: '2023-12-10', status: 'compliant' },
  { id: 3, name: 'CSRD Readiness Assessment', regulation: 'Corporate Sustainability Reporting Directive', date: '2024-02-01', status: 'partial' },
  { id: 4, name: 'SEC Climate Disclosure', regulation: 'SEC Proposed Rules', date: '2024-01-20', status: 'pending' },
])

// New Report Form
const newReportForm = ref({
  type: 'esg',
  period: null,
  framework: 'gri',
  format: 'pdf'
})

// Computed
const filteredEsgReports = computed(() => {
  let result = esgReports.value
  if (esgSearch.value) {
    result = result.filter(r => r.title.toLowerCase().includes(esgSearch.value.toLowerCase()))
  }
  if (esgYear.value !== 'all') {
    result = result.filter(r => r.date.includes(esgYear.value))
  }
  if (esgFramework.value !== 'all') {
    result = result.filter(r => r.framework.toLowerCase() === esgFramework.value.toLowerCase())
  }
  return result
})

const filteredCarbonReports = computed(() => {
  let result = carbonReports.value
  if (carbonScope.value !== 'all') {
    result = result.filter(r => r.scope === carbonScope.value || (carbonScope.value === 'scope1' && r.scope === 'Scope 1') ||
        (carbonScope.value === 'scope2' && r.scope === 'Scope 2') ||
        (carbonScope.value === 'scope3' && r.scope === 'Scope 3'))
  }
  return result
})

// Helper Functions
const getCarbonColor = (scope: string) => {
  const colors: Record<string, string> = {
    'Scope 1': '#3b82f6',
    'Scope 2': '#10b981',
    'Scope 3': '#8b5cf6',
    'All Scopes': '#f59e0b'
  }
  return colors[scope] || '#6b7280'
}

const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#10b981'
  if (progress >= 60) return '#f59e0b'
  return '#ef4444'
}

const getFinanceTagType = (status: string) => {
  const types: Record<string, string> = {
    audited: 'success',
    verified: 'primary',
    draft: 'info',
    pending: 'warning'
  }
  return types[status] || 'info'
}

const getReportTagType = (status: string) => {
  const types: Record<string, string> = {
    published: 'success',
    draft: 'info',
    verified: 'primary',
    partial: 'warning',
    pending: 'warning',
    audited: 'success'
  }
  return types[status] || 'info'
}

// Actions
const generateNewReport = () => {
  generateDialogVisible.value = true
}

const scheduleReport = () => {
  ElMessage.info('Report scheduling interface will open')
}

const openComplianceCenter = () => {
  ElMessage.info('Compliance center will open')
}

const viewReport = (report: any) => {
  previewReport.value = report
  previewDialogVisible.value = true
  setTimeout(() => {
    if (previewChartRef.value) {
      initPreviewChart()
    }
  }, 100)
}

const downloadReport = (report: any) => {
  ElMessage.success(`Downloading ${report.title}...`)
}

const shareReport = (report: any) => {
  ElMessage.info(`Share link for ${report.title} copied to clipboard`)
}

const applyGreenLoan = () => {
  ElMessage.info('Green loan application interface will open')
}

const viewFinanceReport = (report: any) => {
  ElMessage.info(`Viewing ${report.title}`)
}

const runComplianceCheck = () => {
  ElMessage.success('Compliance check initiated')
}

const viewComplianceReport = (report: any) => {
  ElMessage.info(`Viewing ${report.name}`)
}

const downloadComplianceReport = (report: any) => {
  ElMessage.success(`Downloading ${report.name}`)
}

const exportAllReports = () => {
  ElMessage.success('Exporting all reports as ZIP archive')
}

const scheduleAutoReports = () => {
  ElMessage.info('Auto-report settings will open')
}

const openDataVerification = () => {
  ElMessage.info('Data verification portal will open')
}

const confirmGenerateReport = () => {
  ElMessage.success(`Generating ${newReportForm.value.type} report...`)
  generateDialogVisible.value = false
}

const handleTabChange = () => {
  setTimeout(() => {
    if (activeTab.value === 'carbon') {
      initCarbonTrendChart()
      initScopeChart()
    } else if (activeTab.value === 'energy') {
      initEnergyMixChart()
      initRenewableChart()
      initPUEChart()
    } else if (activeTab.value === 'compliance') {
      initComplianceChart()
    }
  }, 200)
}

// Chart instances
let carbonTrendChart: echarts.ECharts | null = null
let scopeChart: echarts.ECharts | null = null
let energyMixChart: echarts.ECharts | null = null
let renewableChart: echarts.ECharts | null = null
let pueChart: echarts.ECharts | null = null
let complianceChart: echarts.ECharts | null = null
let previewChart: echarts.ECharts | null = null

// Chart refs
const carbonTrendChartRef = ref<HTMLElement | null>(null)
const scopeChartRef = ref<HTMLElement | null>(null)
const energyMixChartRef = ref<HTMLElement | null>(null)
const renewableChartRef = ref<HTMLElement | null>(null)
const pueChartRef = ref<HTMLElement | null>(null)
const complianceChartRef = ref<HTMLElement | null>(null)
const previewChartRef = ref<HTMLElement | null>(null)

// Chart initialization functions
const initCarbonTrendChart = () => {
  if (!carbonTrendChartRef.value) return
  if (carbonTrendChart) carbonTrendChart.dispose()
  carbonTrendChart = echarts.init(carbonTrendChartRef.value)
  carbonTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'tCO₂e' },
    series: [
      { name: 'Scope 1', type: 'line', data: [1250, 1180, 1120, 1080, 1050, 1020, 980, 950, 920, 890, 860, 830], smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 } },
      { name: 'Scope 2', type: 'line', data: [850, 820, 790, 760, 740, 720, 700, 680, 660, 640, 620, 600], smooth: true, lineStyle: { color: '#10b981', width: 2 } },
      { name: 'Scope 3', type: 'line', data: [4200, 4150, 4100, 4050, 4000, 3950, 3900, 3850, 3800, 3750, 3700, 3650], smooth: true, lineStyle: { color: '#8b5cf6', width: 2 } }
    ]
  })
}

const initScopeChart = () => {
  if (!scopeChartRef.value) return
  if (scopeChart) scopeChart.dispose()
  scopeChart = echarts.init(scopeChartRef.value)
  scopeChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#64748b' } },
    series: [{
      type: 'pie', radius: '55%', data: [
        { name: 'Scope 1', value: 12500, itemStyle: { color: '#3b82f6' } },
        { name: 'Scope 2', value: 8500, itemStyle: { color: '#10b981' } },
        { name: 'Scope 3', value: 45000, itemStyle: { color: '#8b5cf6' } }
      ], label: { show: true, formatter: '{b}: {d}%' }, emphasis: { scale: true }
    }]
  })
}

const initEnergyMixChart = () => {
  if (!energyMixChartRef.value) return
  if (energyMixChart) energyMixChart.dispose()
  energyMixChart = echarts.init(energyMixChartRef.value)
  energyMixChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: 'MWh' },
    series: [
      { name: 'Grid Electricity', type: 'bar', data: [12500, 11800, 11200, 10500, 9800], itemStyle: { color: '#f59e0b', borderRadius: [8, 8, 0, 0] } },
      { name: 'Solar', type: 'bar', data: [1200, 1800, 2500, 3200, 4000], itemStyle: { color: '#10b981', borderRadius: [8, 8, 0, 0] } },
      { name: 'Wind', type: 'bar', data: [800, 1200, 1800, 2400, 3000], itemStyle: { color: '#3b82f6', borderRadius: [8, 8, 0, 0] } }
    ]
  })
}

const initRenewableChart = () => {
  if (!renewableChartRef.value) return
  if (renewableChart) renewableChart.dispose()
  renewableChart = echarts.init(renewableChartRef.value)
  renewableChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] },
    yAxis: { type: 'value', name: 'Percentage (%)', max: 100 },
    series: [{
      type: 'line', data: [15, 22, 32, 42, 52], smooth: true,
      lineStyle: { color: '#10b981', width: 3 }, areaStyle: { opacity: 0.2, color: '#10b981' },
      symbol: 'circle', symbolSize: 8, label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initPUEChart = () => {
  if (!pueChartRef.value) return
  if (pueChart) pueChart.dispose()
  pueChart = echarts.init(pueChartRef.value)
  pueChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: { type: 'value', name: 'PUE', min: 1.2, max: 1.6 },
    series: [{
      type: 'line', data: [1.48, 1.47, 1.46, 1.45, 1.44, 1.43, 1.43, 1.42, 1.42, 1.41, 1.41, 1.40],
      smooth: true, lineStyle: { color: '#3b82f6', width: 3 },
      areaStyle: { opacity: 0.1 }, symbol: 'circle', symbolSize: 6,
      markLine: { data: [{ yAxis: 1.35, name: 'Target', lineStyle: { color: '#ef4444', type: 'dashed' } }] }
    }]
  })
}

const initComplianceChart = () => {
  if (!complianceChartRef.value) return
  if (complianceChart) complianceChart.dispose()
  complianceChart = echarts.init(complianceChartRef.value)
  complianceChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'category', data: ['GRI', 'SASB', 'TCFD', 'CSRD', 'IFRS S2', 'SEC'], axisLabel: { rotate: 45 } },
    yAxis: { type: 'value', name: 'Compliance Score (%)', max: 100 },
    series: [{
      type: 'bar', data: [98, 92, 88, 85, 82, 75],
      itemStyle: { borderRadius: [8, 8, 0, 0], color: (params: any) => {
          const colors = ['#10b981', '#10b981', '#f59e0b', '#f59e0b', '#f59e0b', '#ef4444']
          return colors[params.dataIndex]
        } }, label: { show: true, position: 'top', formatter: '{c}%' }
    }]
  })
}

const initPreviewChart = () => {
  if (!previewChartRef.value) return
  if (previewChart) previewChart.dispose()
  previewChart = echarts.init(previewChartRef.value)
  previewChart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: [65, 72, 78, 85], smooth: true, lineStyle: { color: '#3b82f6', width: 2 }, areaStyle: { opacity: 0.1 } }]
  })
}

// Loading Simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

// Resize handler
let resizeTimer: ReturnType<typeof setTimeout> | null = null
const handleResize = () => {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    if (carbonTrendChart) carbonTrendChart.resize()
    if (scopeChart) scopeChart.resize()
    if (energyMixChart) energyMixChart.resize()
    if (renewableChart) renewableChart.resize()
    if (pueChart) pueChart.resize()
    if (complianceChart) complianceChart.resize()
  }, 200)
}

onMounted(() => {
  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {
          initCarbonTrendChart()
          initScopeChart()
          initEnergyMixChart()
          initRenewableChart()
          initPUEChart()
          initComplianceChart()
          window.addEventListener('resize', handleResize)
        }, 200)
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeTimer) clearTimeout(resizeTimer)
  const charts = [carbonTrendChart, scopeChart, energyMixChart, renewableChart, pueChart, complianceChart, previewChart]
  charts.forEach(chart => chart?.dispose())
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.sustainability-reports-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
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

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
}

.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
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

/* ==================== Main Content ==================== */
.reports-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Metrics Banner */
.metrics-banner {
  margin-bottom: 24px;
}

.metric-banner-item {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.metric-banner-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.metric-icon.green { background: #ecfdf5; color: #10b981; }
.metric-icon.blue { background: #eff6ff; color: #3b82f6; }
.metric-icon.orange { background: #fffbeb; color: #f59e0b; }
.metric-icon.purple { background: #f3e8ff; color: #8b5cf6; }

.metric-info {
  flex: 1;
}

.metric-label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 4px;
}

.metric-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

/* Tabs */
.reports-tabs {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  margin-bottom: 24px;
}

.reports-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
  padding-bottom: 0;
}

.reports-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 500;
}

.tab-content {
  padding: 0 4px;
}

/* Section Header */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
}

/* Report Cards */
.report-card {
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 20px;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -12px rgba(0, 0, 0, 0.15);
}

.report-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  font-size: 24px;
  color: white;
}

.report-info h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1e293b;
}

.report-info p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.report-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.report-meta .el-icon {
  margin-right: 4px;
}

.report-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Chart Cards */
.chart-card {
  border-radius: 16px;
  height: 100%;
}

.chart-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-weight: 500;
  color: #1e293b;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* Reports List */
.reports-list {
  margin-top: 20px;
}

.report-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
  transition: all 0.2s;
}

.report-list-item:hover {
  background: #f1f5f9;
}

.item-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.item-info {
  flex: 1;
}

.item-title {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.item-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #64748b;
}

.item-progress {
  width: 150px;
}

.item-actions {
  display: flex;
  gap: 8px;
}

/* PUE Card */
.pue-card {
  border-radius: 16px;
  margin-top: 20px;
}

.pue-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-weight: 600;
}

.pue-chart-container {
  height: 250px;
  width: 100%;
}

.pue-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.pue-stat-item {
  text-align: center;
}

.pue-stat-item .stat-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.pue-stat-item .stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.pue-stat-item .stat-trend {
  display: block;
  font-size: 11px;
}

.stat-trend.down { color: #10b981; }
.stat-trend.up { color: #ef4444; }

/* Finance Cards */
.finance-metric-card {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 20px;
  padding: 24px;
  color: white;
}

.finance-metric-card .metric-title {
  font-size: 14px;
  opacity: 0.8;
  margin-bottom: 8px;
}

.finance-metric-card .metric-amount {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.finance-metric-card .metric-rate {
  font-size: 12px;
  opacity: 0.7;
}

.finance-report-card {
  border-radius: 16px;
  margin-bottom: 16px;
}

.finance-report-card .report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.finance-report-card .report-type {
  font-size: 12px;
  font-weight: 600;
  color: #3b82f6;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.finance-report-card h4 {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1e293b;
}

.finance-report-card p {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 16px 0;
}

.finance-report-card .report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}

/* Compliance */
.compliance-card {
  border-radius: 16px;
  height: 100%;
}

.compliance-chart-container {
  height: 300px;
  width: 100%;
}

.compliance-summary {
  background: #f8fafc;
  border-radius: 16px;
  padding: 20px;
  height: 100%;
}

.summary-score {
  text-align: center;
  margin-bottom: 24px;
}

.score-value {
  font-size: 56px;
  font-weight: 700;
  color: #10b981;
}

.score-value span {
  font-size: 24px;
}

.score-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat-row span {
  display: block;
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 4px;
}

.compliance-reports {
  margin-top: 20px;
}

.compliance-report-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
}

.report-status {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.report-status.compliant { background: #ecfdf5; color: #10b981; }
.report-status.partial { background: #fffbeb; color: #f59e0b; }
.report-status.pending { background: #eff6ff; color: #3b82f6; }

.report-details {
  flex: 1;
}

.report-name {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.report-reg {
  font-size: 12px;
  color: #64748b;
}

.report-date {
  font-size: 12px;
  color: #94a3b8;
}

.report-actions {
  display: flex;
  gap: 8px;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 24px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 24px;
}

/* Report Preview Dialog */
.report-preview-dialog :deep(.el-dialog__body) {
  padding: 0 20px 20px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.preview-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748b;
}

.preview-stats {
  display: flex;
  gap: 24px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 20px;
}

.preview-stat {
  flex: 1;
  text-align: center;
}

.preview-stat .stat-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.preview-stat .stat-value {
  display: block;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.preview-chart {
  height: 200px;
  margin-bottom: 20px;
}

.preview-summary h4 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.preview-summary p {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 1200px) {
  .reports-main { padding: 16px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .section-header { flex-direction: column; align-items: flex-start; gap: 12px; }
  .header-controls { flex-wrap: wrap; }
  .report-list-item { flex-wrap: wrap; }
  .item-progress { width: 100%; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>