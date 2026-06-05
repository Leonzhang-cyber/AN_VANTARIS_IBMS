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
          <span class="loading-title">ESG Reports</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Environmental, Social & Governance Reporting Hub</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="esg-reports-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          ESG Reports
        </h1>
        <div class="page-subtitle">Comprehensive ESG reporting and compliance documentation</div>
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
        <div class="stat-icon blue">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.totalReports }}</div>
          <div class="stat-label">Total Reports</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
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
          <div class="stat-value">{{ stats.complianceRate }}<span class="stat-unit">%</span></div>
          <div class="stat-label">Compliance Rate</div>
        </div>
      </div>
    </div>

    <!-- Report Library - Card Grid -->
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
        <el-select v-model="reportTypeFilter" placeholder="Report Type" clearable style="width: 150px">
          <el-option label="Annual ESG Report" value="annual" />
          <el-option label="Sustainability Report" value="sustainability" />
          <el-option label="Carbon Disclosure" value="carbon" />
          <el-option label="Compliance Report" value="compliance" />
        </el-select>
        <el-select v-model="yearFilter" placeholder="Year" clearable style="width: 100px">
          <el-option :label="currentYear.toString()" :value="currentYear.toString()" />
          <el-option :label="(currentYear - 1).toString()" :value="(currentYear - 1).toString()" />
          <el-option :label="(currentYear - 2).toString()" :value="(currentYear - 2).toString()" />
        </el-select>
      </div>
    </div>

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
        <el-empty description="No reports found">
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
        <div class="detail-header" :style="{ background: `linear-gradient(135deg, ${selectedReport.coverColor} 0%, ${selectedReport.coverColor2} 100%)` }">
          <div class="detail-header-content">
            <div class="report-badge" :class="selectedReport.type">{{ getReportTypeLabel(selectedReport.type) }}</div>
            <h2>{{ selectedReport.title }}</h2>
            <div class="detail-meta">
              <span><el-icon><Calendar /></el-icon> {{ selectedReport.publishDate }}</span>
              <span><el-icon><User /></el-icon> {{ selectedReport.author }}</span>
              <span><el-icon><Document /></el-icon> {{ selectedReport.pages }} pages</span>
              <span><el-icon><Download /></el-icon> {{ selectedReport.downloads }}</span>
            </div>
          </div>
        </div>

        <div class="detail-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Report ID">{{ selectedReport.id }}</el-descriptions-item>
            <el-descriptions-item label="Version">{{ selectedReport.version }}</el-descriptions-item>
            <el-descriptions-item label="Frameworks">{{ selectedReport.frameworks.join(', ') }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusTagType(selectedReport.status)" size="small">{{ getStatusText(selectedReport.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Last Updated">{{ selectedReport.lastUpdated }}</el-descriptions-item>
            <el-descriptions-item label="Review Date">{{ selectedReport.reviewDate }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ selectedReport.description }}</el-descriptions-item>
          </el-descriptions>

          <div class="detail-section">
            <div class="section-title">Key Highlights</div>
            <div class="highlights-grid">
              <div v-for="highlight in selectedReport.highlights" :key="highlight.label" class="highlight-card">
                <div class="highlight-value">{{ highlight.value }}</div>
                <div class="highlight-label">{{ highlight.label }}</div>
                <div class="highlight-trend" :class="highlight.trend > 0 ? 'positive' : 'negative'">
                  {{ highlight.trend > 0 ? '↑' : '↓' }} {{ Math.abs(highlight.trend) }}% vs last year
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <div class="section-title">Table of Contents</div>
            <el-timeline>
              <el-timeline-item
                  v-for="section in selectedReport.sections"
                  :key="section.id"
                  :timestamp="section.pages"
                  placement="top"
              >
                {{ section.title }}
              </el-timeline-item>
            </el-timeline>
          </div>

          <div class="detail-section">
            <div class="section-title">Available Formats</div>
            <div class="downloads-grid">
              <div class="download-card" @click="downloadReport(selectedReport, 'pdf')">
                <el-icon><Document /></el-icon>
                <span>PDF Report</span>
                <span class="file-size">2.4 MB</span>
              </div>
              <div class="download-card" @click="downloadReport(selectedReport, 'excel')">
                <el-icon><DataAnalysis /></el-icon>
                <span>Excel Data</span>
                <span class="file-size">1.1 MB</span>
              </div>
              <div class="download-card" @click="downloadReport(selectedReport, 'ppt')">
                <el-icon><Picture /></el-icon>
                <span>Presentation</span>
                <span class="file-size">3.2 MB</span>
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
    <el-dialog v-model="generateDialogVisible" title="Generate New Report" width="600px">
      <el-form :model="reportForm" label-width="140px">
        <el-form-item label="Report Type" required>
          <el-select v-model="reportForm.type" placeholder="Select report type" style="width: 100%">
            <el-option label="Annual ESG Report" value="annual" />
            <el-option label="Sustainability Report" value="sustainability" />
            <el-option label="Carbon Disclosure Report" value="carbon" />
            <el-option label="Compliance Report" value="compliance" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reporting Period" required>
          <el-select v-model="reportForm.year" placeholder="Select year" style="width: 100%">
            <el-option :label="currentYear.toString()" :value="currentYear.toString()" />
            <el-option :label="(currentYear - 1).toString()" :value="(currentYear - 1).toString()" />
            <el-option :label="(currentYear - 2).toString()" :value="(currentYear - 2).toString()" />
          </el-select>
        </el-form-item>
        <el-form-item label="Frameworks">
          <el-select v-model="reportForm.frameworks" multiple placeholder="Select frameworks" style="width: 100%">
            <el-option label="GRI" value="GRI" />
            <el-option label="SASB" value="SASB" />
            <el-option label="TCFD" value="TCFD" />
            <el-option label="CSRD" value="CSRD" />
            <el-option label="UNGC" value="UNGC" />
          </el-select>
        </el-form-item>
        <el-form-item label="Include Sections">
          <el-checkbox-group v-model="reportForm.sections">
            <el-checkbox label="Executive Summary">Executive Summary</el-checkbox>
            <el-checkbox label="Environmental Performance">Environmental Performance</el-checkbox>
            <el-checkbox label="Social Performance">Social Performance</el-checkbox>
            <el-checkbox label="Governance">Governance</el-checkbox>
            <el-checkbox label="Climate Risk">Climate Risk</el-checkbox>
            <el-checkbox label="Data Tables">Data Tables</el-checkbox>
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document, Plus, Refresh, CircleCheck, Edit, DataLine,
  Search, Calendar, User, View, Download, Picture, DataAnalysis
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
const loadingMessage = ref('Loading ESG reports...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading ESG reports...',
  'Fetching report data...',
  'Loading compliance metrics...',
  'Almost ready...'
]

// ==================== Types ====================
interface ESGReport {
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
  frameworks: string[]
  lastUpdated: string
  reviewDate: string
  coverColor: string
  coverColor2: string
  highlights: { label: string; value: string; trend: number }[]
  sections: { id: number; title: string; pages: string }[]
}

// ==================== 生成模拟数据（使用当前年份和日期） ====================
const generateReportsData = (): ESGReport[] => {
  const lastYear = currentYear - 1
  const twoYearsAgo = currentYear - 2

  return [
    {
      id: `ESG-${currentYear}-001`, title: `Annual ESG Report ${currentYear}`, type: 'annual', year: currentYear.toString(),
      description: `Comprehensive overview of environmental, social, and governance performance for fiscal year ${currentYear}.`,
      publishDate: `${currentYear}-03-15`, author: 'ESG Committee', pages: 124, downloads: 2847,
      status: 'published', version: 'v2.1', frameworks: ['GRI', 'SASB', 'TCFD'],
      lastUpdated: formattedDate, reviewDate: `${currentYear}-04-01`,
      coverColor: '#1a73e8', coverColor2: '#0d47a1',
      highlights: [
        { label: 'Carbon Reduction', value: '24%', trend: -8 },
        { label: 'Renewable Energy', value: '42%', trend: 12 },
        { label: 'Water Savings', value: '18%', trend: -5 },
        { label: 'Diversity Score', value: '68%', trend: 6 }
      ],
      sections: [
        { id: 1, title: 'Executive Summary', pages: '4-6' },
        { id: 2, title: 'Environmental Performance', pages: '7-35' },
        { id: 3, title: 'Social Performance', pages: '36-58' },
        { id: 4, title: 'Governance', pages: '59-78' },
        { id: 5, title: 'Climate Risk Assessment', pages: '79-95' },
        { id: 6, title: 'Data Tables & Methodology', pages: '96-124' }
      ]
    },
    {
      id: `SUS-${currentYear}-002`, title: `Sustainability Report ${currentYear}`, type: 'sustainability', year: currentYear.toString(),
      description: 'Detailed sustainability metrics and progress toward 2030 goals.',
      publishDate: `${currentYear}-02-28`, author: 'Sustainability Team', pages: 98, downloads: 2156,
      status: 'published', version: 'v1.0', frameworks: ['GRI', 'SASB'],
      lastUpdated: `${currentYear}-02-28`, reviewDate: `${currentYear}-03-10`,
      coverColor: '#0d9488', coverColor2: '#0f766e',
      highlights: [
        { label: 'Waste Reduction', value: '32%', trend: -10 },
        { label: 'Supplier Engagement', value: '85%', trend: 15 },
        { label: 'Community Investment', value: '$2.5M', trend: 8 },
        { label: 'Employee Volunteering', value: '12,000 hrs', trend: 20 }
      ],
      sections: [
        { id: 1, title: 'CEO Message', pages: '2-3' },
        { id: 2, title: 'Materiality Assessment', pages: '4-12' },
        { id: 3, title: 'Environmental Impact', pages: '13-35' },
        { id: 4, title: 'Social Impact', pages: '36-55' },
        { id: 5, title: 'Supply Chain', pages: '56-70' },
        { id: 6, title: 'Goals & Progress', pages: '71-98' }
      ]
    },
    {
      id: `CAR-${currentYear}-003`, title: `Carbon Disclosure Report ${currentYear}`, type: 'carbon', year: currentYear.toString(),
      description: 'Detailed carbon emissions inventory and reduction strategies.',
      publishDate: `${currentYear}-01-20`, author: 'Carbon Management', pages: 76, downloads: 1892,
      status: 'published', version: 'v3.0', frameworks: ['TCFD', 'GHG Protocol'],
      lastUpdated: `${currentYear}-01-20`, reviewDate: `${currentYear}-02-01`,
      coverColor: '#059669', coverColor2: '#047857',
      highlights: [
        { label: 'Scope 1 Reduction', value: '18%', trend: -6 },
        { label: 'Scope 2 Reduction', value: '28%', trend: -10 },
        { label: 'Carbon Intensity', value: '0.185 kg/kWh', trend: -8 },
        { label: 'RECs Purchased', value: '125,000 MWh', trend: 25 }
      ],
      sections: [
        { id: 1, title: 'Emissions Overview', pages: '2-10' },
        { id: 2, title: 'Scope 1 Emissions', pages: '11-25' },
        { id: 3, title: 'Scope 2 Emissions', pages: '26-40' },
        { id: 4, title: 'Scope 3 Emissions', pages: '41-55' },
        { id: 5, title: 'Reduction Initiatives', pages: '56-68' },
        { id: 6, title: 'Verification Statement', pages: '69-76' }
      ]
    },
    {
      id: `COM-${currentYear}-004`, title: `ESG Compliance Report ${currentYear}`, type: 'compliance', year: currentYear.toString(),
      description: 'Regulatory compliance status against key ESG frameworks.',
      publishDate: formattedDate, author: 'Compliance Team', pages: 112, downloads: 1245,
      status: 'draft', version: 'v0.9', frameworks: ['CSRD', 'SFDR', 'GRI'],
      lastUpdated: formattedDate, reviewDate: `${currentYear}-04-20`,
      coverColor: '#7c3aed', coverColor2: '#6d28d9',
      highlights: [
        { label: 'GRI Compliance', value: '94%', trend: 3 },
        { label: 'TCFD Alignment', value: '88%', trend: 5 },
        { label: 'CSRD Ready', value: '76%', trend: 12 },
        { label: 'Audit Findings', value: '2', trend: -4 }
      ],
      sections: [
        { id: 1, title: 'Regulatory Overview', pages: '2-8' },
        { id: 2, title: 'GRI Compliance', pages: '9-28' },
        { id: 3, title: 'TCFD Compliance', pages: '29-45' },
        { id: 4, title: 'CSRD Readiness', pages: '46-65' },
        { id: 5, title: 'Gap Analysis', pages: '66-85' },
        { id: 6, title: 'Action Plan', pages: '86-112' }
      ]
    },
    {
      id: `ESG-${lastYear}-005`, title: `Annual ESG Report ${lastYear}`, type: 'annual', year: lastYear.toString(),
      description: `Annual ESG performance report for fiscal year ${lastYear}.`,
      publishDate: `${lastYear}-03-10`, author: 'ESG Committee', pages: 118, downloads: 3256,
      status: 'published', version: 'v1.0', frameworks: ['GRI', 'SASB'],
      lastUpdated: `${lastYear}-03-10`, reviewDate: `${lastYear}-03-25`,
      coverColor: '#1a73e8', coverColor2: '#0d47a1',
      highlights: [
        { label: 'Carbon Reduction', value: '18%', trend: -6 },
        { label: 'Renewable Energy', value: '35%', trend: 10 },
        { label: 'Water Savings', value: '12%', trend: -4 },
        { label: 'Diversity Score', value: '62%', trend: 5 }
      ],
      sections: [
        { id: 1, title: 'Executive Summary', pages: '4-6' },
        { id: 2, title: 'Environmental Performance', pages: '7-32' },
        { id: 3, title: 'Social Performance', pages: '33-52' },
        { id: 4, title: 'Governance', pages: '53-72' },
        { id: 5, title: 'Climate Risk', pages: '73-88' },
        { id: 6, title: 'Data Tables', pages: '89-118' }
      ]
    },
    {
      id: `SUS-${lastYear}-006`, title: `Sustainability Report ${lastYear}`, type: 'sustainability', year: lastYear.toString(),
      description: 'Progress toward sustainability goals and targets.',
      publishDate: `${lastYear}-02-15`, author: 'Sustainability Team', pages: 85, downloads: 1876,
      status: 'published', version: 'v1.0', frameworks: ['GRI'],
      lastUpdated: `${lastYear}-02-15`, reviewDate: `${lastYear}-02-28`,
      coverColor: '#0d9488', coverColor2: '#0f766e',
      highlights: [
        { label: 'Waste Reduction', value: '25%', trend: -8 },
        { label: 'Supplier Engagement', value: '78%', trend: 12 },
        { label: 'Community Investment', value: '$2.1M', trend: 6 }
      ],
      sections: [
        { id: 1, title: 'CEO Message', pages: '2-3' },
        { id: 2, title: 'Materiality Assessment', pages: '4-10' },
        { id: 3, title: 'Environmental', pages: '11-32' },
        { id: 4, title: 'Social', pages: '33-48' },
        { id: 5, title: 'Supply Chain', pages: '49-62' },
        { id: 6, title: 'Goals & Progress', pages: '63-85' }
      ]
    }
  ]
}

const reportsData = ref<ESGReport[]>(generateReportsData())

// ==================== State ====================
const searchText = ref('')
const reportTypeFilter = ref('')
const yearFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const detailDialogVisible = ref(false)
const generateDialogVisible = ref(false)
const selectedReport = ref<ESGReport | null>(null)

const reportForm = ref({
  type: 'annual',
  year: currentYear.toString(),
  frameworks: ['GRI', 'SASB'],
  sections: ['Executive Summary', 'Environmental Performance', 'Social Performance', 'Governance'],
  title: `ESG Report ${currentYear}`
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalReports = reportsData.value.length
  const publishedReports = reportsData.value.filter(r => r.status === 'published').length
  const draftReports = reportsData.value.filter(r => r.status === 'draft').length
  const complianceRate = 94
  return { totalReports, publishedReports, draftReports, complianceRate }
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
    annual: 'Annual ESG', sustainability: 'Sustainability',
    carbon: 'Carbon Disclosure', compliance: 'Compliance'
  }
  return map[type] || type
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { published: 'Published', draft: 'Draft', archived: 'Archived' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { published: 'success', draft: 'warning', archived: 'info' }
  return map[status] || 'info'
}

// ==================== Actions ====================
const viewReport = (report: ESGReport) => {
  selectedReport.value = report
  detailDialogVisible.value = true
}

const previewReport = (report: ESGReport) => {
  ElMessage.info(`Previewing ${report.title}`)
  setTimeout(() => {
    ElMessage.success('Preview ready')
  }, 500)
}

const downloadReport = (report: ESGReport, format = 'pdf') => {
  ElMessage.success(`Downloading ${report.title} (${format.toUpperCase()})...`)
  setTimeout(() => {
    ElMessage.success('Download completed')
  }, 1000)
}

const editReport = (report: ESGReport | null) => {
  if (report) {
    ElMessage.info(`Editing ${report.title}`)
  }
}

const publishReport = (report: ESGReport | null) => {
  if (report) {
    ElMessage.success(`${report.title} published successfully`)
  }
}

const createNewReport = () => {
  reportForm.value = {
    type: 'annual',
    year: currentYear.toString(),
    frameworks: ['GRI', 'SASB'],
    sections: ['Executive Summary', 'Environmental Performance', 'Social Performance', 'Governance'],
    title: `ESG Report ${currentYear}`
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
  reportsData.value = generateReportsData()
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
})
</script>

<style scoped>
/* 样式与之前相同，保持完整 */
.esg-reports-page {
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

/* Loading Screen - 保持原有样式 */
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

.stat-icon.blue { background: #eef2ff; color: #3b82f6; }
.stat-icon.green { background: #dcfce7; color: #22c55e; }
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
  height: 160px;
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
  font-size: 48px;
  font-weight: 700;
  opacity: 0.3;
  position: absolute;
  bottom: 16px;
  right: 16px;
  line-height: 1;
}

.report-icon {
  font-size: 32px;
  opacity: 0.5;
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
  line-height: 1.5;
  margin-bottom: 16px;
}

.report-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
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
  gap: 24px;
  padding: 12px 0;
  border-top: 1px solid #eef2f8;
  border-bottom: 1px solid #eef2f8;
  margin-bottom: 16px;
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
  padding: 32px;
  margin: -20px -20px 0 -20px;
  border-radius: 20px 20px 0 0;
}

.detail-header-content h2 {
  margin: 16px 0 12px 0;
  font-size: 24px;
}

.detail-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
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

.highlights-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.highlight-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
}

.highlight-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.highlight-label {
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.highlight-trend {
  font-size: 11px;
  margin-top: 8px;
}

.highlight-trend.positive { color: #22c55e; }
.highlight-trend.negative { color: #ef4444; }

.downloads-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.download-card {
  flex: 1;
  min-width: 140px;
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
  color: #3b82f6;
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
  .highlights-grid {
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
  }
  .section-actions .el-input,
  .section-actions .el-select {
    width: 100% !important;
  }
  .highlights-grid {
    grid-template-columns: 1fr;
  }
  .downloads-grid {
    flex-direction: column;
  }
}

/* Element Plus Overrides */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}
:deep(.el-button--primary) {
  background: #3b82f6;
  border-color: #3b82f6;
}
:deep(.el-button--primary:hover) {
  background: #2563eb;
}
:deep(.el-dialog__body) {
  padding: 20px;
}
</style>