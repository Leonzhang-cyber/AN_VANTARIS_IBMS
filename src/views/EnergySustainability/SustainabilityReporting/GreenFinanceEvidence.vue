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
          <span class="loading-title">Green Finance Evidence</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Green Finance Documentation & Impact Evidence</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="green-finance-evidence-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Money /></el-icon>
          Green Finance Evidence
        </h1>
        <div class="page-subtitle">Green bond, sustainability-linked loan, and ESG finance documentation and impact reporting</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="uploadEvidence">
          <el-icon><Upload /></el-icon> Upload Evidence
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
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.totalGreenFinance }}<span class="stat-unit">B</span></div>
          <div class="stat-label">Total Green Finance</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.greenBonds }}</div>
          <div class="stat-label">Green Bonds</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Link /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.sustainabilityLoans }}</div>
          <div class="stat-label">SLLs Issued</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">
          <el-icon><Document /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.documentsCount }}</div>
          <div class="stat-label">Evidence Documents</div>
        </div>
      </div>
    </div>

    <!-- Section Header -->
    <div class="section-header">
      <h2 class="section-title">Evidence Library</h2>
      <div class="section-actions">
        <el-input
            v-model="searchText"
            placeholder="Search by title or issuer..."
            style="width: 240px"
            clearable
            :prefix-icon="Search"
        />
        <el-select v-model="typeFilter" placeholder="Instrument Type" clearable style="width: 160px">
          <el-option label="Green Bond" value="green-bond" />
          <el-option label="Sustainability Bond" value="sustainability-bond" />
          <el-option label="Sustainability-Linked Loan" value="sll" />
          <el-option label="Green Loan" value="green-loan" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
          <el-option label="Active" value="active" />
          <el-option label="Matured" value="matured" />
        </el-select>
      </div>
    </div>

    <!-- Evidence Cards Grid -->
    <div class="evidence-grid">
      <div
          v-for="evidence in paginatedEvidence"
          :key="evidence.id"
          class="evidence-card"
          @click="viewEvidence(evidence)"
      >
        <div class="evidence-header" :style="{ background: `linear-gradient(135deg, ${getTypeColor(evidence.type)} 0%, ${getTypeColor2(evidence.type)} 100%)` }">
          <div class="evidence-type-badge" :class="evidence.type">
            {{ getTypeLabel(evidence.type) }}
          </div>
          <div class="evidence-amount">${{ evidence.amount }}B</div>
        </div>
        <div class="evidence-content">
          <h3 class="evidence-title">{{ evidence.title }}</h3>
          <p class="evidence-description">{{ evidence.description }}</p>
          <div class="evidence-meta">
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>Issued: {{ evidence.issueDate }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Timer /></el-icon>
              <span>Maturity: {{ evidence.maturityDate }}</span>
            </div>
          </div>
          <div class="evidence-impact">
            <div class="impact-item">
              <span class="impact-label">CO₂ Reduced</span>
              <span class="impact-value">{{ evidence.co2Reduction }} kt</span>
            </div>
            <div class="impact-item">
              <span class="impact-label">RE Generated</span>
              <span class="impact-value">{{ evidence.renewableGenerated }} MW</span>
            </div>
            <div class="impact-item">
              <span class="impact-label">Projects</span>
              <span class="impact-value">{{ evidence.projectsCount }}</span>
            </div>
          </div>
          <div class="evidence-docs">
            <span class="docs-count"><el-icon><Document /></el-icon> {{ evidence.documentsCount }} documents</span>
            <el-tag :type="evidence.status === 'active' ? 'success' : 'info'" size="small">{{ evidence.status === 'active' ? 'Active' : 'Matured' }}</el-tag>
          </div>
          <div class="evidence-actions">
            <el-button size="small" @click.stop="viewEvidence(evidence)">
              <el-icon><View /></el-icon> Details
            </el-button>
            <el-button size="small" type="primary" @click.stop="downloadReport(evidence)">
              <el-icon><Download /></el-icon> Report
            </el-button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredEvidence.length === 0" class="empty-state">
        <el-empty description="No green finance evidence found">
          <el-button type="primary" @click="uploadEvidence">Upload Evidence</el-button>
        </el-empty>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container" v-if="filteredEvidence.length > 0">
      <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 12, 18]"
          :total="totalRecords"
          layout="total, sizes, prev, pager, next"
          background
      />
    </div>

    <!-- Evidence Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="selectedEvidence?.title" width="900px" class="evidence-dialog">
      <div v-if="selectedEvidence" class="evidence-detail">
        <div class="detail-header" :style="{ background: `linear-gradient(135deg, ${getTypeColor(selectedEvidence.type)} 0%, ${getTypeColor2(selectedEvidence.type)} 100%)` }">
          <div class="detail-header-content">
            <div class="evidence-type-badge large" :class="selectedEvidence.type">
              {{ getTypeLabel(selectedEvidence.type) }}
            </div>
            <h2>{{ selectedEvidence.title }}</h2>
            <div class="detail-amount">${{ selectedEvidence.amount }}B</div>
          </div>
        </div>

        <div class="detail-content">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="ISIN/CUSIP">{{ selectedEvidence.isin }}</el-descriptions-item>
            <el-descriptions-item label="Issuer">{{ selectedEvidence.issuer }}</el-descriptions-item>
            <el-descriptions-item label="Issue Date">{{ selectedEvidence.issueDate }}</el-descriptions-item>
            <el-descriptions-item label="Maturity Date">{{ selectedEvidence.maturityDate }}</el-descriptions-item>
            <el-descriptions-item label="Coupon">{{ selectedEvidence.coupon }}%</el-descriptions-item>
            <el-descriptions-item label="Framework">{{ selectedEvidence.framework }}</el-descriptions-item>
            <el-descriptions-item label="External Review">{{ selectedEvidence.externalReview }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="selectedEvidence.status === 'active' ? 'success' : 'info'" size="small">
                {{ selectedEvidence.status === 'active' ? 'Active' : 'Matured' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <!-- Impact Metrics -->
          <div class="detail-section">
            <div class="section-title">Impact Metrics</div>
            <div class="impact-grid">
              <div class="impact-card">
                <div class="impact-value">{{ selectedEvidence.co2Reduction }} kt</div>
                <div class="impact-label">Annual CO₂ Reduction</div>
              </div>
              <div class="impact-card">
                <div class="impact-value">{{ selectedEvidence.renewableGenerated }} MW</div>
                <div class="impact-label">Renewable Energy Capacity</div>
              </div>
              <div class="impact-card">
                <div class="impact-value">{{ selectedEvidence.energySaved }} GWh</div>
                <div class="impact-label">Energy Saved Annually</div>
              </div>
              <div class="impact-card">
                <div class="impact-value">{{ selectedEvidence.waterSaved }} m³</div>
                <div class="impact-label">Water Saved Annually</div>
              </div>
              <div class="impact-card">
                <div class="impact-value">{{ selectedEvidence.projectsCount }}</div>
                <div class="impact-label">Projects Funded</div>
              </div>
              <div class="impact-card">
                <div class="impact-value">${{ selectedEvidence.allocatedAmount }}M</div>
                <div class="impact-label">Allocated to Green Projects</div>
              </div>
            </div>
          </div>

          <!-- Project Allocation -->
          <div class="detail-section">
            <div class="section-title">Use of Proceeds</div>
            <el-table :data="selectedEvidence.allocation" border stripe>
              <el-table-column prop="category" label="Category" min-width="200" />
              <el-table-column prop="amount" label="Amount (M)" width="150">
                <template #default="{ row }">
                  ${{ row.amount }}M
                </template>
              </el-table-column>
              <el-table-column prop="percentage" label="Percentage" width="150">
                <template #default="{ row }">
                  <el-progress :percentage="row.percentage" :stroke-width="8" :color="'#22c55e'" />
                </template>
              </el-table-column>
              <el-table-column prop="projects" label="Projects" min-width="200" />
            </el-table>
          </div>

          <!-- Allocation Chart -->
          <div class="detail-section">
            <div class="section-title">Allocation by Category</div>
            <div class="trend-chart" ref="allocationChartEl"></div>
          </div>

          <!-- Documents -->
          <div class="detail-section">
            <div class="section-title">Evidence Documents</div>
            <el-table :data="selectedEvidence.documents" border stripe>
              <el-table-column prop="name" label="Document Name" min-width="250" />
              <el-table-column prop="date" label="Date" width="120" />
              <el-table-column prop="type" label="Type" width="120">
                <template #default="{ row }">
                  <el-tag :type="row.type === 'Second Party Opinion' ? 'success' : (row.type === 'Allocation Report' ? 'primary' : 'info')" size="small">
                    {{ row.type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Action" width="80">
                <template #default>
                  <el-button link type="primary" size="small">View</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Certifications -->
          <div class="detail-section">
            <div class="section-title">Certifications & Framework</div>
            <div class="certifications-list">
              <el-tag v-for="cert in selectedEvidence.certifications" :key="cert" type="success" size="large" effect="plain">
                {{ cert }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="generateReport(selectedEvidence)">Generate Report</el-button>
        <el-button type="warning" @click="shareEvidence(selectedEvidence)">Share</el-button>
      </template>
    </el-dialog>

    <!-- Upload Evidence Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload Green Finance Evidence" width="600px">
      <el-form :model="uploadForm" label-width="140px">
        <el-form-item label="Instrument Type" required>
          <el-select v-model="uploadForm.type" style="width: 100%">
            <el-option label="Green Bond" value="green-bond" />
            <el-option label="Sustainability Bond" value="sustainability-bond" />
            <el-option label="Sustainability-Linked Loan" value="sll" />
            <el-option label="Green Loan" value="green-loan" />
          </el-select>
        </el-form-item>
        <el-form-item label="Title" required>
          <el-input v-model="uploadForm.title" placeholder="Enter instrument title" />
        </el-form-item>
        <el-form-item label="Amount ($B)" required>
          <el-input-number v-model="uploadForm.amount" :min="0" :step="0.5" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Issue Date" required>
          <el-date-picker v-model="uploadForm.issueDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Maturity Date">
          <el-date-picker v-model="uploadForm.maturityDate" type="date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Framework">
          <el-select v-model="uploadForm.framework" style="width: 100%">
            <el-option label="ICMA Green Bond Principles" value="ICMA Green Bond Principles" />
            <el-option label="ICMA Sustainability Bond Guidelines" value="ICMA Sustainability Bond Guidelines" />
            <el-option label="LMA Green Loan Principles" value="LMA Green Loan Principles" />
            <el-option label="Sustainability-Linked Loan Principles" value="Sustainability-Linked Loan Principles" />
          </el-select>
        </el-form-item>
        <el-form-item label="External Review">
          <el-select v-model="uploadForm.externalReview" style="width: 100%">
            <el-option label="Second Party Opinion" value="Second Party Opinion" />
            <el-option label="Verification" value="Verification" />
            <el-option label="Certification" value="Certification" />
            <el-option label="Rating" value="Rating" />
          </el-select>
        </el-form-item>
        <el-form-item label="Evidence Document">
          <el-upload
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="5"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              Drop files here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                PDF, Excel, Word files. Max 10MB each.
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="uploadForm.description" type="textarea" :rows="2" placeholder="Brief description..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveUpload">Upload Evidence</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Money, Document, Link, Upload, Refresh, Search, Calendar, Timer,
  View, Download, UploadFilled
} from '@element-plus/icons-vue'

// ==================== 获取当前日期 ====================
const currentDate = new Date()
const currentYear = currentDate.getFullYear()
const formattedDate = `${currentYear}-${String(currentDate.getMonth() + 1).padStart(2, '0')}-${String(currentDate.getDate()).padStart(2, '0')}`

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading green finance evidence...')
const refreshing = ref(false)

const loadingMessages = [
  'Loading green finance data...',
  'Fetching impact metrics...',
  'Loading evidence documents...',
  'Almost ready...'
]

// ==================== Types ====================
interface AllocationItem {
  category: string
  amount: number
  percentage: number
  projects: string
}

interface DocumentItem {
  name: string
  date: string
  type: string
}

interface GreenFinanceEvidence {
  id: string
  title: string
  type: string
  amount: number
  issuer: string
  isin: string
  issueDate: string
  maturityDate: string
  coupon: number
  framework: string
  externalReview: string
  status: string
  description: string
  co2Reduction: number
  renewableGenerated: number
  energySaved: number
  waterSaved: number
  projectsCount: number
  allocatedAmount: number
  allocation: AllocationItem[]
  documents: DocumentItem[]
  certifications: string[]
}

// ==================== Mock Data ====================
const generateEvidenceData = (): GreenFinanceEvidence[] => {
  return [
    {
      id: 'GB-2024-001', title: 'Green Bond 2024 - Series A', type: 'green-bond', amount: 1.2,
      issuer: 'Data Center REIT', isin: 'US1234567890', issueDate: '2024-01-15', maturityDate: '2034-01-15',
      coupon: 4.25, framework: 'ICMA Green Bond Principles', externalReview: 'Second Party Opinion - Sustainalytics',
      status: 'active', description: 'Proceeds allocated to renewable energy and energy efficiency projects across data centers.',
      co2Reduction: 125, renewableGenerated: 85, energySaved: 185, waterSaved: 5000,
      projectsCount: 12, allocatedAmount: 850,
      allocation: [
        { category: 'Renewable Energy - Solar', amount: 450, percentage: 37.5, projects: 'Solar Farm A, Solar Farm B' },
        { category: 'Energy Efficiency - Cooling', amount: 350, percentage: 29.2, projects: 'Chiller Upgrade, CRAC Replacement' },
        { category: 'Green Buildings', amount: 250, percentage: 20.8, projects: 'Data Center C Retrofit' },
        { category: 'Other Green Projects', amount: 150, percentage: 12.5, projects: 'Battery Storage' }
      ],
      documents: [
        { name: 'Green_Bond_Framework_2024.pdf', date: '2024-01-10', type: 'Framework' },
        { name: 'Second_Party_Opinion_Sustainalytics.pdf', date: '2024-01-12', type: 'Second Party Opinion' },
        { name: 'Allocation_Report_Q1_2024.pdf', date: '2024-04-15', type: 'Allocation Report' },
        { name: 'Impact_Report_2024.pdf', date: '2024-06-30', type: 'Impact Report' }
      ],
      certifications: ['ICMA Green Bond Principles', 'Climate Bonds Initiative Certified']
    },
    {
      id: 'SLL-2024-002', title: 'Sustainability-Linked Loan - Facility A', type: 'sll', amount: 0.85,
      issuer: 'Data Center REIT', isin: 'N/A', issueDate: '2023-06-01', maturityDate: '2028-06-01',
      coupon: 3.75, framework: 'Sustainability-Linked Loan Principles', externalReview: 'Verification - EcoVadis',
      status: 'active', description: 'Loan with KPI-linked margin adjustments tied to carbon reduction targets.',
      co2Reduction: 85, renewableGenerated: 0, energySaved: 95, waterSaved: 0,
      projectsCount: 5, allocatedAmount: 0,
      allocation: [
        { category: 'General Corporate Purposes', amount: 850, percentage: 100, projects: 'Operational improvements' }
      ],
      documents: [
        { name: 'SLL_Framework.pdf', date: '2023-05-15', type: 'Framework' },
        { name: 'KPI_Verification_Report_2024.pdf', date: '2024-03-20', type: 'Verification Report' }
      ],
      certifications: ['Sustainability-Linked Loan Principles', 'LMA Compliant']
    },
    {
      id: 'GB-2023-003', title: 'Green Bond 2023 - Series B', type: 'green-bond', amount: 0.75,
      issuer: 'Data Center REIT', isin: 'US9876543210', issueDate: '2023-03-10', maturityDate: '2033-03-10',
      coupon: 4.5, framework: 'ICMA Green Bond Principles', externalReview: 'Second Party Opinion - CICERO',
      status: 'active', description: 'Funding for energy-efficient cooling systems and renewable energy.',
      co2Reduction: 65, renewableGenerated: 45, energySaved: 95, waterSaved: 3500,
      projectsCount: 8, allocatedAmount: 520,
      allocation: [
        { category: 'Energy Efficiency', amount: 380, percentage: 50.7, projects: 'Cooling System Upgrades' },
        { category: 'Renewable Energy', amount: 220, percentage: 29.3, projects: 'Solar Installation' },
        { category: 'Water Efficiency', amount: 150, percentage: 20.0, projects: 'Water Recycling' }
      ],
      documents: [
        { name: 'Green_Bond_Framework_2023.pdf', date: '2023-02-20', type: 'Framework' },
        { name: 'Second_Party_Opinion_CICERO.pdf', date: '2023-02-25', type: 'Second Party Opinion' },
        { name: 'Annual_Allocation_Report_2023.pdf', date: '2024-01-15', type: 'Allocation Report' }
      ],
      certifications: ['ICMA Green Bond Principles']
    },
    {
      id: 'GL-2024-004', title: 'Green Loan - Data Center Expansion', type: 'green-loan', amount: 0.45,
      issuer: 'Data Center REIT', isin: 'N/A', issueDate: '2024-02-01', maturityDate: '2029-02-01',
      coupon: 4.0, framework: 'LMA Green Loan Principles', externalReview: 'Verification - DNV',
      status: 'active', description: 'Financing for energy-efficient data center expansion.',
      co2Reduction: 35, renewableGenerated: 0, energySaved: 42, waterSaved: 2000,
      projectsCount: 3, allocatedAmount: 450,
      allocation: [
        { category: 'Green Building', amount: 280, percentage: 62.2, projects: 'New Data Center Construction' },
        { category: 'Energy Efficiency', amount: 170, percentage: 37.8, projects: 'High-efficiency Cooling' }
      ],
      documents: [
        { name: 'Green_Loan_Framework.pdf', date: '2024-01-20', type: 'Framework' },
        { name: 'Verification_Statement_DNV.pdf', date: '2024-01-25', type: 'Verification' }
      ],
      certifications: ['LMA Green Loan Principles']
    },
    {
      id: 'SB-2024-005', title: 'Sustainability Bond - Climate Action', type: 'sustainability-bond', amount: 1.5,
      issuer: 'Data Center REIT', isin: 'US5555555555', issueDate: '2024-04-01', maturityDate: '2034-04-01',
      coupon: 4.35, framework: 'ICMA Sustainability Bond Guidelines', externalReview: 'Second Party Opinion - Vigeo Eiris',
      status: 'active', description: 'Combined green and social projects for climate action.',
      co2Reduction: 165, renewableGenerated: 110, energySaved: 220, waterSaved: 8000,
      projectsCount: 15, allocatedAmount: 1050,
      allocation: [
        { category: 'Renewable Energy', amount: 600, percentage: 40.0, projects: 'Wind & Solar Projects' },
        { category: 'Energy Efficiency', amount: 450, percentage: 30.0, projects: 'Data Center Optimization' },
        { category: 'Green Buildings', amount: 300, percentage: 20.0, projects: 'LEED Certification' },
        { category: 'Social Projects', amount: 150, percentage: 10.0, projects: 'Community Renewable Access' }
      ],
      documents: [
        { name: 'Sustainability_Bond_Framework.pdf', date: '2024-03-15', type: 'Framework' },
        { name: 'Second_Party_Opinion_Vigeo.pdf', date: '2024-03-20', type: 'Second Party Opinion' }
      ],
      certifications: ['ICMA Sustainability Bond Guidelines', 'UN SDG Aligned']
    },
    {
      id: 'SLL-2023-006', title: 'Sustainability-Linked Loan - ESG Facility', type: 'sll', amount: 0.6,
      issuer: 'Data Center REIT', isin: 'N/A', issueDate: '2023-09-01', maturityDate: '2028-09-01',
      coupon: 4.1, framework: 'Sustainability-Linked Loan Principles', externalReview: 'Verification - ISS ESG',
      status: 'active', description: 'Margin tied to renewable energy and diversity targets.',
      co2Reduction: 55, renewableGenerated: 0, energySaved: 65, waterSaved: 0,
      projectsCount: 4, allocatedAmount: 0,
      allocation: [
        { category: 'General Corporate Purposes', amount: 600, percentage: 100, projects: 'ESG initiatives' }
      ],
      documents: [
        { name: 'SLL_Framework_2023.pdf', date: '2023-08-10', type: 'Framework' },
        { name: 'KPI_Report_2023.pdf', date: '2024-02-28', type: 'KPI Report' }
      ],
      certifications: ['Sustainability-Linked Loan Principles']
    }
  ]
}

const evidenceData = ref<GreenFinanceEvidence[]>(generateEvidenceData())

// ==================== State ====================
const searchText = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const currentPage = ref(1)
const pageSize = ref(6)
const detailDialogVisible = ref(false)
const uploadDialogVisible = ref(false)
const selectedEvidence = ref<GreenFinanceEvidence | null>(null)

// Chart ref
let allocationChart: echarts.ECharts | null = null
const allocationChartEl = ref<HTMLElement | null>(null)

const uploadForm = ref({
  type: 'green-bond',
  title: '',
  amount: 0,
  issueDate: formattedDate,
  maturityDate: '',
  framework: 'ICMA Green Bond Principles',
  externalReview: 'Second Party Opinion',
  description: '',
  files: []
})

// ==================== Computed ====================
const stats = computed(() => {
  const totalGreenFinance = evidenceData.value.reduce((sum, e) => sum + e.amount, 0)
  const greenBonds = evidenceData.value.filter(e => e.type === 'green-bond' || e.type === 'sustainability-bond').length
  const sustainabilityLoans = evidenceData.value.filter(e => e.type === 'sll' || e.type === 'green-loan').length
  const documentsCount = evidenceData.value.reduce((sum, e) => sum + e.documents.length, 0)
  return { totalGreenFinance: totalGreenFinance.toFixed(1), greenBonds, sustainabilityLoans, documentsCount }
})

const filteredEvidence = computed(() => {
  let filtered = [...evidenceData.value]

  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    filtered = filtered.filter(e =>
        e.title.toLowerCase().includes(search) ||
        e.issuer.toLowerCase().includes(search) ||
        e.id.toLowerCase().includes(search)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(e => e.type === typeFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(e => e.status === statusFilter.value)
  }

  return filtered
})

const totalRecords = computed(() => filteredEvidence.value.length)

const paginatedEvidence = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEvidence.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getTypeLabel = (type: string): string => {
  const map: Record<string, string> = {
    'green-bond': 'Green Bond',
    'sustainability-bond': 'Sustainability Bond',
    'sll': 'Sustainability-Linked Loan',
    'green-loan': 'Green Loan'
  }
  return map[type] || type
}

const getTypeColor = (type: string): string => {
  const map: Record<string, string> = {
    'green-bond': '#10b981',
    'sustainability-bond': '#3b82f6',
    'sll': '#f59e0b',
    'green-loan': '#22c55e'
  }
  return map[type] || '#10b981'
}

const getTypeColor2 = (type: string): string => {
  const map: Record<string, string> = {
    'green-bond': '#059669',
    'sustainability-bond': '#2563eb',
    'sll': '#d97706',
    'green-loan': '#16a34a'
  }
  return map[type] || '#059669'
}

// ==================== Chart Functions ====================
const initAllocationChart = () => {
  if (!allocationChartEl.value || !selectedEvidence.value) return
  if (allocationChart) {
    allocationChart.dispose()
    allocationChart = null
  }

  const data = selectedEvidence.value.allocation.map(item => ({ name: item.category, value: item.amount }))

  allocationChart = echarts.init(allocationChartEl.value)
  allocationChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ${c}M ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: data.map(d => d.name) },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: data,
      label: { show: true, formatter: '{b}: ${c}M' },
      emphasis: { scale: true }
    }]
  })
}

// ==================== Actions ====================
const viewEvidence = (evidence: GreenFinanceEvidence) => {
  selectedEvidence.value = evidence
  detailDialogVisible.value = true
  nextTick(() => initAllocationChart())
}

const downloadReport = (evidence: GreenFinanceEvidence) => {
  ElMessage.success(`Downloading report for ${evidence.title}...`)
  setTimeout(() => {
    ElMessage.success('Download completed')
  }, 1000)
}

const generateReport = (evidence: GreenFinanceEvidence | null) => {
  if (evidence) {
    ElMessage.success(`Generating comprehensive report for ${evidence.title}...`)
    setTimeout(() => {
      ElMessage.success('Report generated successfully')
    }, 1500)
  }
}

const shareEvidence = (evidence: GreenFinanceEvidence | null) => {
  if (evidence) {
    ElMessage.success(`Share link created for ${evidence.title}`)
  }
}

const uploadEvidence = () => {
  uploadForm.value = {
    type: 'green-bond',
    title: '',
    amount: 0,
    issueDate: formattedDate,
    maturityDate: '',
    framework: 'ICMA Green Bond Principles',
    externalReview: 'Second Party Opinion',
    description: '',
    files: []
  }
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadForm.value.files.push(file)
}

const saveUpload = () => {
  if (!uploadForm.value.title || uploadForm.value.amount <= 0) {
    ElMessage.warning('Please fill in required fields')
    return
  }
  ElMessage.success('Evidence uploaded successfully')
  uploadDialogVisible.value = false
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Watch ====================
watch([searchText, typeFilter, statusFilter], () => {
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
  if (allocationChart && !allocationChart.isDisposed()) allocationChart.dispose()
})
</script>

<style scoped>
.green-finance-evidence-page {
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

/* Evidence Grid */
.evidence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.evidence-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.evidence-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.12);
}

.evidence-header {
  padding: 20px;
  color: white;
  position: relative;
}

.evidence-type-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(4px);
}

.evidence-amount {
  font-size: 32px;
  font-weight: 700;
  margin-top: 16px;
  opacity: 0.9;
}

.evidence-content {
  padding: 20px;
}

.evidence-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.evidence-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 12px;
}

.evidence-meta {
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

.evidence-impact {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid #eef2f8;
  border-bottom: 1px solid #eef2f8;
  margin-bottom: 12px;
}

.impact-item {
  flex: 1;
  text-align: center;
}

.impact-label {
  font-size: 11px;
  color: #94a3b8;
  display: block;
}

.impact-value {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.evidence-docs {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.docs-count {
  font-size: 12px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.evidence-actions {
  display: flex;
  gap: 12px;
}

/* Detail Dialog */
.evidence-detail {
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

.detail-amount {
  font-size: 28px;
  font-weight: 700;
  opacity: 0.9;
}

.evidence-type-badge.large {
  font-size: 14px;
  padding: 6px 16px;
}

.detail-content {
  padding: 24px 0 0 0;
}

.impact-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.impact-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
}

.impact-card .impact-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.impact-card .impact-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.detail-section {
  margin-top: 24px;
}

.section-title {
  font-weight: 600;
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 10px;
  border-left: 3px solid #10b981;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

.certifications-list {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
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
  .evidence-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
  .impact-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .evidence-grid {
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
  .impact-grid {
    grid-template-columns: 1fr;
  }
}

/* Element Plus Overrides */
:deep(.el-button--primary) {
  background: #10b981;
  border-color: #10b981;
}
:deep(.el-button--primary:hover) {
  background: #059669;
}
:deep(.el-dialog__body) {
  padding: 20px;
}
</style>