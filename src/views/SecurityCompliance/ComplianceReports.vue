<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service,
  Search, Edit, Plus, VideoPlay, VideoPause,
  Operation, Headset, Monitor, Cpu, Connection,
  Lock, Key, Medal, Flag, DataAnalysis,
  EditPen, Tickets, Filter, SuccessFilled, List, Download as DownloadIcon,
  Printer
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Loading compliance reports...',
  'Analyzing compliance data...',
  'Preparing report templates...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const searchKeyword = ref('')
const selectedStandard = ref('all')
const selectedStatus = ref('all')
const detailsVisible = ref(false)
const generateReportVisible = ref(false)
const scheduleReportVisible = ref(false)
const chartRef = ref(null)

let complianceChart: echarts.ECharts | null = null

// Standards filters
const standardOptions = [
  { value: 'all', label: 'All Standards' },
  { value: 'iso27001', label: 'ISO 27001', color: '#409EFF' },
  { value: 'soc2', label: 'SOC 2', color: '#67C23A' },
  { value: 'gdpr', label: 'GDPR', color: '#E6A23C' },
  { value: 'hipaa', label: 'HIPAA', color: '#F56C6C' },
  { value: 'pci', label: 'PCI DSS', color: '#9B59B6' }
]

// Status filters
const statusOptions = [
  { value: 'all', label: 'All Status' },
  { value: 'compliant', label: 'Compliant', color: '#67C23A' },
  { value: 'partial', label: 'Partial', color: '#E6A23C' },
  { value: 'non-compliant', label: 'Non-Compliant', color: '#F56C6C' }
]

// Compliance reports data
const reports = ref([
  {
    id: 'RPT001', name: 'ISO 27001 Compliance Report', standard: 'iso27001', status: 'compliant',
    score: 94.5, lastAudit: '2024-01-15', nextAudit: '2024-07-15', findings: 3,
    controls: 114, passed: 108, failed: 6, createdBy: 'Audit Team', createdAt: '2024-01-15',
    summary: 'Overall compliance status meets ISO 27001 requirements with minor findings to address.'
  },
  {
    id: 'RPT002', name: 'SOC 2 Type II Report', standard: 'soc2', status: 'compliant',
    score: 96.2, lastAudit: '2024-01-10', nextAudit: '2024-07-10', findings: 2,
    controls: 89, passed: 86, failed: 3, createdBy: 'Audit Team', createdAt: '2024-01-10',
    summary: 'Trust services criteria met across security, availability, and confidentiality.'
  },
  {
    id: 'RPT003', name: 'GDPR Readiness Assessment', standard: 'gdpr', status: 'partial',
    score: 78.5, lastAudit: '2024-01-05', nextAudit: '2024-04-05', findings: 12,
    controls: 67, passed: 52, failed: 15, createdBy: 'Privacy Team', createdAt: '2024-01-05',
    summary: 'Data protection measures partially compliant. Data retention and consent management need improvement.'
  },
  {
    id: 'RPT004', name: 'HIPAA Security Rule Assessment', standard: 'hipaa', status: 'non-compliant',
    score: 65.2, lastAudit: '2023-12-20', nextAudit: '2024-03-20', findings: 18,
    controls: 78, passed: 51, failed: 27, createdBy: 'Compliance Team', createdAt: '2023-12-20',
    summary: 'Multiple security safeguards require immediate attention. Audit logging and access controls deficient.'
  },
  {
    id: 'RPT005', name: 'PCI DSS Compliance Report', standard: 'pci', status: 'compliant',
    score: 92.8, lastAudit: '2023-12-15', nextAudit: '2024-06-15', findings: 4,
    controls: 325, passed: 312, failed: 13, createdBy: 'Security Team', createdAt: '2023-12-15',
    summary: 'Payment card data security requirements met. Ongoing monitoring required.'
  },
  {
    id: 'RPT006', name: 'ISO 27001 Mid-Year Review', standard: 'iso27001', status: 'partial',
    score: 82.3, lastAudit: '2023-12-10', nextAudit: '2024-06-10', findings: 7,
    controls: 114, passed: 94, failed: 20, createdBy: 'Internal Audit', createdAt: '2023-12-10',
    summary: 'Progress made on previous findings. Risk assessment updates needed.'
  },
  {
    id: 'RPT007', name: 'SOC 2 Readiness Assessment', standard: 'soc2', status: 'partial',
    score: 71.5, lastAudit: '2023-12-05', nextAudit: '2024-03-05', findings: 15,
    controls: 89, passed: 63, failed: 26, createdBy: 'Audit Team', createdAt: '2023-12-05',
    summary: 'Several control gaps identified. Vendor management and change control need improvement.'
  },
  {
    id: 'RPT008', name: 'Data Protection Impact Assessment', standard: 'gdpr', status: 'compliant',
    score: 88.9, lastAudit: '2023-11-28', nextAudit: '2024-05-28', findings: 6,
    controls: 52, passed: 46, failed: 6, createdBy: 'DPO', createdAt: '2023-11-28',
    summary: 'DPIA completed for high-risk processing activities. Remediation plan in place.'
  }
])

// Compliance statistics
const complianceStats = reactive({
  total: 0,
  compliant: 0,
  partial: 0,
  nonCompliant: 0,
  avgScore: 0,
  totalControls: 0,
  totalFindings: 0
})

// Generate report form
const generateForm = reactive({
  standard: 'iso27001',
  scope: 'full',
  format: 'pdf',
  includeFindings: true,
  includeRecommendations: true,
  recipients: ''
})

// Schedule report form
const scheduleForm = reactive({
  reportId: '',
  frequency: 'monthly',
  recipients: '',
  format: 'pdf'
})

// Pagination
const pagination = reactive({
  page: 1,
  pageSize: 8,
  total: reports.value.length
})

// Filtered reports
const filteredReports = computed(() => {
  let filtered = reports.value
  if (searchKeyword.value) {
    filtered = filtered.filter(r =>
        r.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        r.summary.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }
  if (selectedStandard.value !== 'all') {
    filtered = filtered.filter(r => r.standard === selectedStandard.value)
  }
  if (selectedStatus.value !== 'all') {
    filtered = filtered.filter(r => r.status === selectedStatus.value)
  }
  pagination.total = filtered.length
  const start = (pagination.page - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return filtered.slice(start, end)
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initChart()
        updateStats()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  complianceChart = echarts.init(chartRef.value)
  complianceChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Compliant', 'Partial', 'Non-Compliant'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: reports.value.map(r => r.standard.toUpperCase()), axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: 'Number of Reports' },
    series: [
      { name: 'Compliant', type: 'bar', data: reports.value.filter(r => r.status === 'compliant').length, itemStyle: { color: '#67C23A', borderRadius: [4, 4, 0, 0] } },
      { name: 'Partial', type: 'bar', data: reports.value.filter(r => r.status === 'partial').length, itemStyle: { color: '#E6A23C', borderRadius: [4, 4, 0, 0] } },
      { name: 'Non-Compliant', type: 'bar', data: reports.value.filter(r => r.status === 'non-compliant').length, itemStyle: { color: '#F56C6C', borderRadius: [4, 4, 0, 0] } }
    ]
  })
}

const updateStats = () => {
  complianceStats.total = reports.value.length
  complianceStats.compliant = reports.value.filter(r => r.status === 'compliant').length
  complianceStats.partial = reports.value.filter(r => r.status === 'partial').length
  complianceStats.nonCompliant = reports.value.filter(r => r.status === 'non-compliant').length
  complianceStats.avgScore = Math.round(reports.value.reduce((sum, r) => sum + r.score, 0) / reports.value.length)
  complianceStats.totalControls = reports.value.reduce((sum, r) => sum + r.controls, 0)
  complianceStats.totalFindings = reports.value.reduce((sum, r) => sum + r.findings, 0)
}

const handleResize = () => {
  complianceChart?.resize()
}

// ==================== Report Functions ====================
const refreshReports = async () => {
  loading.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  updateStats()
  loading.value = false
  ElMessage.success('Compliance reports refreshed successfully')
}

const viewReport = (report: any) => {
  selectedReport.value = report
  detailsVisible.value = true
}

const downloadReport = async (report: any) => {
  ElMessage.info(`Downloading ${report.name}...`)
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`${report.name} downloaded successfully`)
}

const shareReport = (report: any) => {
  ElMessage.success(`Share link generated for ${report.name}`)
}

const printReport = (report: any) => {
  ElMessage.info(`Preparing ${report.name} for printing...`)
  setTimeout(() => {
    ElMessage.success(`Report ready for printing`)
  }, 1000)
}

const openGenerateReport = () => {
  generateForm.standard = 'iso27001'
  generateForm.scope = 'full'
  generateForm.format = 'pdf'
  generateForm.includeFindings = true
  generateForm.includeRecommendations = true
  generateForm.recipients = ''
  generateReportVisible.value = true
}

const generateReport = async () => {
  await new Promise(resolve => setTimeout(resolve, 1500))
  ElMessage.success('Compliance report generated successfully')
  generateReportVisible.value = false
}

const openScheduleReport = () => {
  scheduleForm.reportId = ''
  scheduleForm.frequency = 'monthly'
  scheduleForm.recipients = ''
  scheduleForm.format = 'pdf'
  scheduleReportVisible.value = true
}

const scheduleReport = async () => {
  if (!scheduleForm.reportId) {
    ElMessage.warning('Please select a report to schedule')
    return
  }
  await new Promise(resolve => setTimeout(resolve, 1000))
  ElMessage.success(`Report scheduled ${scheduleForm.frequency}ly`)
  scheduleReportVisible.value = false
}

const handleSizeChange = (val: number) => {
  pagination.pageSize = val
  pagination.page = 1
}

const handlePageChange = (val: number) => {
  pagination.page = val
}

const getStandardType = (standard: string) => {
  switch (standard) {
    case 'iso27001': return 'primary'
    case 'soc2': return 'success'
    case 'gdpr': return 'warning'
    case 'hipaa': return 'danger'
    case 'pci': return 'info'
    default: return ''
  }
}

const getStandardIcon = (standard: string) => {
  switch (standard) {
    case 'iso27001': return '🔒'
    case 'soc2': return '🔐'
    case 'gdpr': return '🇪🇺'
    case 'hipaa': return '🏥'
    case 'pci': return '💳'
    default: return '📋'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'compliant': return 'success'
    case 'partial': return 'warning'
    case 'non-compliant': return 'danger'
    default: return 'info'
  }
}

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'compliant': return CircleCheck
    case 'partial': return Warning
    case 'non-compliant': return Filter
    default: return Clock
  }
}

const getScoreColor = (score: number) => {
  if (score >= 90) return '#67C23A'
  if (score >= 70) return '#E6A23C'
  return '#F56C6C'
}

const selectedReport = ref<any>(null)
</script>

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
          <span class="loading-title">Loading Compliance Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Security & Compliance - Compliance Reports</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="compliance-reports-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">Compliance Reports</h1>
        <p class="page-subtitle">Comprehensive compliance assessment and audit reports</p>
      </div>
      <div class="header-right">
        <el-button type="primary" size="large" @click="openGenerateReport">
          <el-icon><Plus /></el-icon>
          Generate Report
        </el-button>
        <el-button size="large" @click="openScheduleReport">
          <el-icon><Clock /></el-icon>
          Schedule Report
        </el-button>
        <el-button size="large" @click="refreshReports" :loading="loading">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ complianceStats.total }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ complianceStats.compliant }} Compliant</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon score-icon">
          <el-icon><TrendCharts /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ complianceStats.avgScore }}%</div>
          <div class="stat-label">Avg Compliance Score</div>
        </div>
        <div class="stat-trend">
          <el-progress :percentage="complianceStats.avgScore" :stroke-width="4" :show-text="false" />
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon controls-icon">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ complianceStats.totalControls.toLocaleString() }}</div>
          <div class="stat-label">Controls Assessed</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">{{ complianceStats.totalFindings }} Findings</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon standards-icon">
          <el-icon><Medal /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">5</div>
          <div class="stat-label">Standards</div>
        </div>
        <div class="stat-trend">
          <span class="trend-neutral">ISO 27001, SOC 2, GDPR, HIPAA, PCI DSS</span>
        </div>
      </div>
    </div>

    <!-- Compliance Chart -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Compliance Status by Standard</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="compliance-chart" style="height: 320px"></div>
    </div>

    <!-- Filters Bar -->
    <div class="filters-bar">
      <div class="filters-left">
        <div class="search-box">
          <el-input
              v-model="searchKeyword"
              placeholder="Search reports..."
              :prefix-icon="Search"
              clearable
              style="width: 240px"
          />
        </div>
        <div class="standard-filters">
          <span class="filter-label">Standard:</span>
          <button
              v-for="s in standardOptions"
              :key="s.value"
              class="standard-chip"
              :class="{ active: selectedStandard === s.value }"
              @click="selectedStandard = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
        <div class="status-filters">
          <span class="filter-label">Status:</span>
          <button
              v-for="s in statusOptions"
              :key="s.value"
              class="status-chip"
              :class="{ active: selectedStatus === s.value }"
              @click="selectedStatus = s.value"
          >
            <span class="chip-dot" :style="{ background: s.color }"></span>
            <span>{{ s.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Reports Grid -->
    <div class="reports-grid">
      <div
          v-for="report in filteredReports"
          :key="report.id"
          class="report-card"
          :class="report.status"
      >
        <!-- Card Header -->
        <div class="card-header">
          <div class="report-standard">
            <span class="standard-icon">{{ getStandardIcon(report.standard) }}</span>
            <span class="standard-name">{{ report.standard.toUpperCase() }}</span>
          </div>
          <div class="report-status">
            <el-tag :type="getStatusType(report.status)" size="small" effect="light">
              <el-icon><component :is="getStatusIcon(report.status)" /></el-icon>
              {{ report.status.toUpperCase() }}
            </el-tag>
          </div>
        </div>

        <!-- Card Body -->
        <div class="card-body">
          <h4 class="report-name">{{ report.name }}</h4>
          <p class="report-summary">{{ report.summary }}</p>

          <!-- Compliance Score -->
          <div class="score-section">
            <div class="score-header">
              <span>Compliance Score</span>
              <span class="score-value" :style="{ color: getScoreColor(report.score) }">
                {{ report.score }}%
              </span>
            </div>
            <div class="score-bar">
              <div class="bar-fill" :style="{ width: report.score + '%', background: getScoreColor(report.score) }"></div>
            </div>
          </div>

          <!-- Key Metrics -->
          <div class="key-metrics">
            <div class="metric">
              <span class="metric-label">Controls</span>
              <span class="metric-value">{{ report.passed }}/{{ report.controls }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">Findings</span>
              <span class="metric-value" :class="{ 'has-findings': report.findings > 0 }">
                {{ report.findings }}
              </span>
            </div>
            <div class="metric">
              <span class="metric-label">Pass Rate</span>
              <span class="metric-value">{{ Math.round((report.passed / report.controls) * 100) }}%</span>
            </div>
          </div>

          <!-- Dates -->
          <div class="dates">
            <div class="date-item">
              <span class="date-label">Last Audit:</span>
              <span class="date-value">{{ report.lastAudit }}</span>
            </div>
            <div class="date-item">
              <span class="date-label">Next Audit:</span>
              <span class="date-value">{{ report.nextAudit }}</span>
            </div>
          </div>

          <!-- Created By -->
          <div class="created-by">
            <el-icon><User /></el-icon>
            <span>{{ report.createdBy }}</span>
            <span class="created-date">{{ report.createdAt }}</span>
          </div>
        </div>

        <!-- Card Footer -->
        <div class="card-footer">
          <div class="card-actions">
            <el-button size="small" @click="viewReport(report)">
              <el-icon><List /></el-icon> View
            </el-button>
            <el-button size="small" @click="downloadReport(report)">
              <el-icon><DownloadIcon /></el-icon> Download
            </el-button>
            <el-button size="small" @click="shareReport(report)">
              <el-icon><Share /></el-icon> Share
            </el-button>
            <el-button size="small" @click="printReport(report)">
              <el-icon><Printer /></el-icon> Print
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredReports.length === 0" class="empty-state">
      <el-empty description="No compliance reports found">
        <el-button type="primary" @click="openGenerateReport">Generate Report</el-button>
      </el-empty>
    </div>

    <!-- Pagination -->
    <div v-if="filteredReports.length > 0" class="pagination-wrapper">
      <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[8, 12, 16, 24]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
      />
    </div>

    <!-- Report Details Dialog -->
    <el-dialog v-model="detailsVisible" :title="selectedReport?.name" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Report ID">{{ selectedReport?.id }}</el-descriptions-item>
        <el-descriptions-item label="Standard">{{ selectedReport?.standard?.toUpperCase() }}</el-descriptions-item>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(selectedReport?.status)" size="small">
            {{ selectedReport?.status?.toUpperCase() }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Compliance Score">{{ selectedReport?.score }}%</el-descriptions-item>
        <el-descriptions-item label="Last Audit">{{ selectedReport?.lastAudit }}</el-descriptions-item>
        <el-descriptions-item label="Next Audit">{{ selectedReport?.nextAudit }}</el-descriptions-item>
        <el-descriptions-item label="Controls Assessed">{{ selectedReport?.controls }}</el-descriptions-item>
        <el-descriptions-item label="Controls Passed">{{ selectedReport?.passed }}</el-descriptions-item>
        <el-descriptions-item label="Controls Failed">{{ selectedReport?.failed }}</el-descriptions-item>
        <el-descriptions-item label="Findings">{{ selectedReport?.findings }}</el-descriptions-item>
        <el-descriptions-item label="Created By">{{ selectedReport?.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="Created At">{{ selectedReport?.createdAt }}</el-descriptions-item>
        <el-descriptions-item label="Summary" :span="2">{{ selectedReport?.summary }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailsVisible = false">Close</el-button>
        <el-button type="primary" @click="downloadReport(selectedReport)">Download Report</el-button>
      </template>
    </el-dialog>

    <!-- Generate Report Dialog -->
    <el-dialog v-model="generateReportVisible" title="Generate Compliance Report" width="500px">
      <el-form :model="generateForm" label-width="120px">
        <el-form-item label="Standard" required>
          <el-select v-model="generateForm.standard" style="width: 100%">
            <el-option label="ISO 27001" value="iso27001" />
            <el-option label="SOC 2" value="soc2" />
            <el-option label="GDPR" value="gdpr" />
            <el-option label="HIPAA" value="hipaa" />
            <el-option label="PCI DSS" value="pci" />
          </el-select>
        </el-form-item>
        <el-form-item label="Scope">
          <el-select v-model="generateForm.scope" style="width: 100%">
            <el-option label="Full Assessment" value="full" />
            <el-option label="Quick Assessment" value="quick" />
            <el-option label="Gap Analysis" value="gap" />
          </el-select>
        </el-form-item>
        <el-form-item label="Format">
          <el-radio-group v-model="generateForm.format">
            <el-radio value="pdf">PDF</el-radio>
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Include Findings">
          <el-switch v-model="generateForm.includeFindings" />
        </el-form-item>
        <el-form-item label="Include Recommendations">
          <el-switch v-model="generateForm.includeRecommendations" />
        </el-form-item>
        <el-form-item label="Email Recipients">
          <el-input v-model="generateForm.recipients" placeholder="email@example.com (comma separated)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="generateReport">Generate</el-button>
      </template>
    </el-dialog>

    <!-- Schedule Report Dialog -->
    <el-dialog v-model="scheduleReportVisible" title="Schedule Compliance Report" width="500px">
      <el-form :model="scheduleForm" label-width="120px">
        <el-form-item label="Report" required>
          <el-select v-model="scheduleForm.reportId" style="width: 100%">
            <el-option v-for="r in reports" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Frequency">
          <el-select v-model="scheduleForm.frequency" style="width: 100%">
            <el-option label="Monthly" value="monthly" />
            <el-option label="Quarterly" value="quarterly" />
            <el-option label="Annually" value="annually" />
          </el-select>
        </el-form-item>
        <el-form-item label="Format">
          <el-select v-model="scheduleForm.format" style="width: 100%">
            <el-option label="PDF" value="pdf" />
            <el-option label="Excel" value="excel" />
          </el-select>
        </el-form-item>
        <el-form-item label="Recipients">
          <el-input v-model="scheduleForm.recipients" placeholder="email@example.com (comma separated)" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleReportVisible = false">Cancel</el-button>
        <el-button type="primary" @click="scheduleReport">Schedule</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
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

/* ==================== Main Content ==================== */
.compliance-reports-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
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
  font-size: 28px;
}

.total-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.score-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.controls-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.standards-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
  font-size: 11px;
  background: #f5f7fa;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-up {
  color: #67c23a;
}

.trend-neutral {
  color: #909399;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

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

.compliance-chart {
  width: 100%;
}

/* Filters Bar */
.filters-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 24px;
}

.filters-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
  margin-right: 8px;
}

.standard-filters,
.status-filters {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.standard-chip,
.status-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  font-size: 12px;
  color: #606266;
  cursor: pointer;
  transition: all 0.2s ease;
}

.standard-chip:hover,
.status-chip:hover {
  border-color: #409eff;
  color: #409eff;
}

.standard-chip.active,
.status-chip.active {
  background: #409eff;
  border-color: #409eff;
  color: white;
}

.chip-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
}

.report-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.report-card.compliant {
  border-left: 4px solid #67c23a;
}

.report-card.partial {
  border-left: 4px solid #e6a23c;
}

.report-card.non-compliant {
  border-left: 4px solid #f56c6c;
}

/* Card Header */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 0 20px;
}

.report-standard {
  display: flex;
  align-items: center;
  gap: 8px;
}

.standard-icon {
  font-size: 18px;
}

.standard-name {
  font-size: 12px;
  font-weight: 600;
  color: #409eff;
  background: #e6f7ff;
  padding: 4px 8px;
  border-radius: 12px;
}

/* Card Body */
.card-body {
  padding: 16px 20px;
}

.report-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 10px 0;
  line-height: 1.4;
}

.report-summary {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  margin: 0 0 16px 0;
}

.score-section {
  margin-bottom: 16px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: #606266;
}

.score-value {
  font-weight: 600;
}

.score-bar {
  height: 6px;
  background: #e4e7ed;
  border-radius: 3px;
  overflow: hidden;
}

.score-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.key-metrics {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
  padding: 12px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.metric {
  text-align: center;
}

.metric-label {
  font-size: 11px;
  color: #909399;
  display: block;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.metric-value.has-findings {
  color: #f56c6c;
}

.dates {
  margin-bottom: 12px;
}

.date-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 4px;
}

.date-label {
  color: #909399;
}

.date-value {
  color: #1e293b;
  font-weight: 500;
}

.created-by {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.created-date {
  margin-left: auto;
}

/* Card Footer */
.card-footer {
  padding: 12px 20px 16px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafbfc;
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}

/* Empty State */
.empty-state {
  padding: 60px 0;
  text-align: center;
}

/* Pagination */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  padding-top: 8px;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .reports-grid {
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  }
}

@media (max-width: 768px) {
  .compliance-reports-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filters-left {
    flex-direction: column;
    align-items: stretch;
  }

  .standard-filters,
  .status-filters {
    flex-wrap: wrap;
    justify-content: center;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }

  .reports-grid {
    grid-template-columns: 1fr;
  }

  .key-metrics {
    flex-direction: column;
    gap: 8px;
  }

  .card-actions {
    flex-direction: column;
  }

  .card-actions .el-button {
    width: 100%;
  }
}
</style>