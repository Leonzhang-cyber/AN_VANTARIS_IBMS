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
          <span class="loading-title">Utility Billing</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Utility Cost Management & Bill Analytics</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="utility-billing-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          Utility Billing
        </h1>
        <div class="page-subtitle">Track utility costs, consumption trends, and bill analytics across multiple utilities</div>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="uploadBill">
          <el-icon><Upload /></el-icon> Upload Bill
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
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">${{ stats.totalCost.toLocaleString() }}</div>
          <div class="stat-label">Total Cost (YTD)</div>
          <div class="stat-trend" :class="stats.costTrend > 0 ? 'up' : 'down'">
            {{ stats.costTrend > 0 ? '↑' : '↓' }} {{ Math.abs(stats.costTrend) }}% vs last year
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">
          <el-icon><Lightning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.electricityCost }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Electricity Cost</div>
          <div class="stat-trend up">MTD</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">
          <el-icon><Tint /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.waterCost }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Water Cost</div>
          <div class="stat-trend up">MTD</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red">
          <el-icon><Fire /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.gasCost }}<span class="stat-unit">k</span></div>
          <div class="stat-label">Gas Cost</div>
          <div class="stat-trend down">MTD</div>
        </div>
      </div>
    </div>

    <!-- Key Metrics Row -->
    <div class="metrics-row">
      <div class="metric-card">
        <div class="metric-title">Average Electricity Rate</div>
        <div class="metric-value">${{ metrics.electricityRate }}<span class="metric-unit">/kWh</span></div>
        <div class="metric-trend" :class="metrics.electricityTrend < 0 ? 'positive' : 'negative'">
          {{ metrics.electricityTrend < 0 ? '↓' : '↑' }} {{ Math.abs(metrics.electricityTrend) }}% vs last month
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Water Rate</div>
        <div class="metric-value">${{ metrics.waterRate }}<span class="metric-unit">/m³</span></div>
        <div class="metric-trend positive">↓ 2.5% vs last month</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Average Gas Rate</div>
        <div class="metric-value">${{ metrics.gasRate }}<span class="metric-unit">/m³</span></div>
        <div class="metric-trend negative">↑ 3.2% vs last month</div>
      </div>
      <div class="metric-card">
        <div class="metric-title">Total Bill Savings</div>
        <div class="metric-value">${{ metrics.savings }}<span class="metric-unit">k</span></div>
        <div class="metric-sub">Due to efficiency improvements</div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="charts-row">
      <div class="chart-card large">
        <div class="chart-header">
          <span class="chart-title">Monthly Utility Cost Breakdown</span>
          <span class="chart-subtitle">Last 12 months</span>
        </div>
        <div class="chart-container" ref="costTrendChartEl"></div>
      </div>
    </div>

    <!-- Second Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Cost by Utility Type</span>
          <span class="chart-subtitle">YTD distribution</span>
        </div>
        <div class="chart-container" ref="costDistributionChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Monthly Consumption</span>
          <span class="chart-subtitle">Electricity vs Water vs Gas</span>
        </div>
        <div class="chart-container" ref="consumptionChartEl"></div>
      </div>
    </div>

    <!-- Third Charts Row -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Rate Comparison</span>
          <span class="chart-subtitle">Our rate vs Industry avg</span>
        </div>
        <div class="chart-container" ref="rateComparisonChartEl"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Budget vs Actual</span>
          <span class="chart-subtitle">Year-to-date variance</span>
        </div>
        <div class="chart-container" ref="budgetChartEl"></div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            style="width: 260px"
        />
        <el-select v-model="utilityFilter" placeholder="Utility Type" clearable style="width: 140px">
          <el-option label="Electricity" value="electricity" />
          <el-option label="Water" value="water" />
          <el-option label="Gas" value="gas" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 130px">
          <el-option label="Paid" value="paid" />
          <el-option label="Pending" value="pending" />
          <el-option label="Overdue" value="overdue" />
        </el-select>
      </div>
      <div class="filter-right">
        <el-button type="primary" link @click="resetFilters">
          <el-icon><RefreshLeft /></el-icon> Reset Filters
        </el-button>
      </div>
    </div>

    <!-- Bills Table -->
    <div class="table-container">
      <div class="table-header">
        <span class="table-title">Bill History</span>
        <el-button size="small" @click="viewAllBills">View All →</el-button>
      </div>
      <el-table :data="paginatedBills" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="period" label="Billing Period"  />
        <el-table-column prop="utilityType" label="Utility Type" >
          <template #default="{ row }">
            <el-tag :type="getUtilityTagType(row.utilityType)" size="small">{{ row.utilityType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="consumption" label="Consumption" width="140">
          <template #default="{ row }">
            {{ row.consumption.toLocaleString() }} {{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="rate" label="Rate" >
          <template #default="{ row }">
            ${{ row.rate.toFixed(3) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="Amount" >
          <template #default="{ row }">
            ${{ row.amount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="dueDate" label="Due Date"  />
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paidDate" label="Paid Date"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewBillDetail(row)">View</el-button>
            <el-button link type="success" size="small" v-if="row.status === 'pending'" @click="markAsPaid(row)">Pay</el-button>
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

    <!-- Bill Detail Dialog -->
    <el-dialog v-model="detailDialogVisible" :title="`Bill Details - ${selectedBill?.period}`" width="800px" class="bill-dialog">
      <div v-if="selectedBill" class="bill-detail">
        <!-- Header Stats -->
        <div class="detail-header-stats">
          <div class="detail-stat">
            <div class="detail-stat-value">${{ selectedBill.amount.toLocaleString() }}</div>
            <div class="detail-stat-label">Total Amount</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">{{ selectedBill.consumption.toLocaleString() }} {{ selectedBill.unit }}</div>
            <div class="detail-stat-label">Consumption</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value">${{ selectedBill.rate.toFixed(3) }}</div>
            <div class="detail-stat-label">Rate per {{ selectedBill.unit }}</div>
          </div>
          <div class="detail-stat">
            <div class="detail-stat-value" :style="{ color: getStatusColor(selectedBill.status) }">
              {{ getStatusText(selectedBill.status) }}
            </div>
            <div class="detail-stat-label">Status</div>
          </div>
        </div>

        <!-- Basic Info -->
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Bill ID">{{ selectedBill.id }}</el-descriptions-item>
          <el-descriptions-item label="Utility Type">
            <el-tag :type="getUtilityTagType(selectedBill.utilityType)" size="small">{{ selectedBill.utilityType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Billing Period">{{ selectedBill.period }}</el-descriptions-item>
          <el-descriptions-item label="Due Date">{{ selectedBill.dueDate }}</el-descriptions-item>
          <el-descriptions-item label="Payment Date">{{ selectedBill.paidDate || 'Not paid' }}</el-descriptions-item>
          <el-descriptions-item label="Meter Number">{{ selectedBill.meterNumber }}</el-descriptions-item>
          <el-descriptions-item label="Previous Reading">{{ selectedBill.previousReading }} {{ selectedBill.unit }}</el-descriptions-item>
          <el-descriptions-item label="Current Reading">{{ selectedBill.currentReading }} {{ selectedBill.unit }}</el-descriptions-item>
          <el-descriptions-item label="Vendor">{{ selectedBill.vendor }}</el-descriptions-item>
          <el-descriptions-item label="Account Number">{{ selectedBill.accountNumber }}</el-descriptions-item>
        </el-descriptions>

        <!-- Historical Comparison -->
        <div class="detail-section">
          <div class="section-title">Historical Comparison</div>
          <div class="comparison-grid">
            <div class="comparison-item">
              <span class="comparison-label">vs Last Month</span>
              <span :class="selectedBill.vsLastMonth > 0 ? 'metric-bad' : 'metric-good'">
                {{ selectedBill.vsLastMonth > 0 ? '+' : '' }}{{ selectedBill.vsLastMonth }}%
              </span>
            </div>
            <div class="comparison-item">
              <span class="comparison-label">vs Same Month Last Year</span>
              <span :class="selectedBill.vsLastYear > 0 ? 'metric-bad' : 'metric-good'">
                {{ selectedBill.vsLastYear > 0 ? '+' : '' }}{{ selectedBill.vsLastYear }}%
              </span>
            </div>
            <div class="comparison-item">
              <span class="comparison-label">vs Budget</span>
              <span :class="selectedBill.vsBudget > 0 ? 'metric-bad' : 'metric-good'">
                {{ selectedBill.vsBudget > 0 ? '+' : '' }}{{ selectedBill.vsBudget }}%
              </span>
            </div>
          </div>
        </div>

        <!-- Trend Chart -->
        <div class="detail-section">
          <div class="section-title">12-Month Consumption Trend</div>
          <div class="trend-chart" ref="billTrendChartEl"></div>
        </div>

        <!-- Breakdown -->
        <div class="detail-section" v-if="selectedBill.breakdown.length > 0">
          <div class="section-title">Cost Breakdown</div>
          <el-table :data="selectedBill.breakdown" border stripe>
            <el-table-column prop="item" label="Item" width="200" />
            <el-table-column prop="amount" label="Amount" width="150">
              <template #default="{ row }">
                ${{ row.amount.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column prop="percentage" label="Percentage" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.percentage" :stroke-width="6" :color="'#3b82f6'" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="250" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button type="primary" v-if="selectedBill?.status === 'pending'" @click="markAsPaid(selectedBill)">Mark as Paid</el-button>
        <el-button type="warning" @click="downloadBill(selectedBill)">Download Bill</el-button>
      </template>
    </el-dialog>

    <!-- Upload Bill Dialog -->
    <el-dialog v-model="uploadDialogVisible" title="Upload Bill" width="500px">
      <el-form :model="uploadForm" label-width="120px">
        <el-form-item label="Utility Type" required>
          <el-select v-model="uploadForm.utilityType" style="width: 100%">
            <el-option label="Electricity" value="electricity" />
            <el-option label="Water" value="water" />
            <el-option label="Gas" value="gas" />
          </el-select>
        </el-form-item>
        <el-form-item label="Billing Period" required>
          <el-date-picker v-model="uploadForm.period" type="month" placeholder="Select month" format="YYYY-MM" value-format="YYYY-MM" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Bill File">
          <el-upload
              drag
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                PDF, Excel or image files
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="Notes">
          <el-input v-model="uploadForm.notes" type="textarea" :rows="2" placeholder="Additional notes..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveUpload">Upload Bill</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Document, Money, Lightning, Upload, Download, Refresh,
  RefreshLeft, UploadFilled
} from '@element-plus/icons-vue'

// 注意：Tint 和 Fire 图标可能不存在，使用替代方案
// 如果 Tint 和 Fire 报错，请替换为 Iphone 和 HotWater

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading utility billing data...')
const refreshing = ref(false)
const tableLoading = ref(false)

const loadingMessages = [
  'Loading billing data...',
  'Fetching utility costs...',
  'Calculating trends...',
  'Analyzing consumption patterns...',
  'Almost ready...'
]

// ==================== Types ====================
interface BillBreakdown {
  item: string
  amount: number
  percentage: number
  description: string
}

interface UtilityBill {
  id: string
  utilityType: string
  period: string
  consumption: number
  unit: string
  rate: number
  amount: number
  dueDate: string
  status: string
  paidDate: string | null
  meterNumber: string
  previousReading: number
  currentReading: number
  vendor: string
  accountNumber: string
  vsLastMonth: number
  vsLastYear: number
  vsBudget: number
  breakdown: BillBreakdown[]
}

// ==================== Mock Data ====================
const generateBillData = (): UtilityBill[] => {
  const utilities = [
    { type: 'Electricity', unit: 'kWh', rate: 0.12, vendor: 'PowerCo', meterPrefix: 'ELEC' },
    { type: 'Water', unit: 'm³', rate: 0.85, vendor: 'WaterWorks', meterPrefix: 'WTR' },
    { type: 'Gas', unit: 'm³', rate: 0.45, vendor: 'GasCorp', meterPrefix: 'GAS' }
  ]

  const bills: UtilityBill[] = []
  let id = 1

  for (let month = 0; month < 12; month++) {
    const date = new Date()
    date.setMonth(date.getMonth() - month)
    const period = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
    const periodDisplay = `${date.toLocaleString('default', { month: 'long' })} ${date.getFullYear()}`

    for (const util of utilities) {
      const baseConsumption = util.type === 'Electricity' ? 45000 + Math.random() * 10000 :
          util.type === 'Water' ? 500 + Math.random() * 200 :
              3000 + Math.random() * 1000
      const consumption = Math.round(baseConsumption * (0.8 + Math.random() * 0.4))
      const rate = util.rate * (0.95 + Math.random() * 0.1)
      const amount = Math.round(consumption * rate)
      const previousReading = Math.round(consumption * 0.9)
      const currentReading = previousReading + consumption

      let status = 'paid'
      let paidDate = null
      if (month < 3) {
        status = 'paid'
        paidDate = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
      } else if (month < 6) {
        status = 'pending'
      } else {
        status = 'overdue'
      }

      const vsLastMonth = (Math.random() * 20 - 5).toFixed(1)
      const vsLastYear = (Math.random() * 15 - 3).toFixed(1)
      const vsBudget = (Math.random() * 12 - 2).toFixed(1)

      const breakdown: BillBreakdown[] = [
        { item: 'Base Charges', amount: Math.round(amount * 0.6), percentage: 60, description: 'Basic utility charges' },
        { item: 'Taxes & Fees', amount: Math.round(amount * 0.15), percentage: 15, description: 'Government taxes and regulatory fees' },
        { item: 'Demand Charges', amount: Math.round(amount * 0.15), percentage: 15, description: 'Peak demand charges' },
        { item: 'Environmental Levy', amount: Math.round(amount * 0.1), percentage: 10, description: 'Environmental surcharge' }
      ]

      bills.push({
        id: `${util.meterPrefix}-${String(id++).padStart(6, '0')}`,
        utilityType: util.type,
        period: periodDisplay,
        consumption: consumption,
        unit: util.unit,
        rate: parseFloat(rate.toFixed(4)),
        amount: amount,
        dueDate: new Date(date.getFullYear(), date.getMonth() + 1, 15).toISOString().slice(0, 10),
        status: status,
        paidDate: paidDate,
        meterNumber: `${util.meterPrefix}${Math.floor(Math.random() * 1000)}`,
        previousReading: previousReading,
        currentReading: currentReading,
        vendor: util.vendor,
        accountNumber: `ACC-${Math.floor(Math.random() * 100000)}`,
        vsLastMonth: parseFloat(vsLastMonth),
        vsLastYear: parseFloat(vsLastYear),
        vsBudget: parseFloat(vsBudget),
        breakdown: breakdown
      })
    }
  }

  return bills.sort((a, b) => b.period.localeCompare(a.period))
}

const bills = ref<UtilityBill[]>(generateBillData())

// ==================== State ====================
const utilityFilter = ref('')
const statusFilter = ref('')
const dateRange = ref<Date[] | null>(null)
const currentPage = ref(1)
const pageSize = ref(10)
const detailDialogVisible = ref(false)
const uploadDialogVisible = ref(false)
const selectedBill = ref<UtilityBill | null>(null)

// Chart refs
let costTrendChart: echarts.ECharts | null = null
let costDistributionChart: echarts.ECharts | null = null
let consumptionChart: echarts.ECharts | null = null
let rateComparisonChart: echarts.ECharts | null = null
let budgetChart: echarts.ECharts | null = null
let billTrendChart: echarts.ECharts | null = null

const costTrendChartEl = ref<HTMLElement | null>(null)
const costDistributionChartEl = ref<HTMLElement | null>(null)
const consumptionChartEl = ref<HTMLElement | null>(null)
const rateComparisonChartEl = ref<HTMLElement | null>(null)
const budgetChartEl = ref<HTMLElement | null>(null)
const billTrendChartEl = ref<HTMLElement | null>(null)

const uploadForm = ref({
  utilityType: 'electricity',
  period: '',
  notes: '',
  file: null
})

// ==================== Computed ====================
const stats = computed(() => {
  const currentYear = new Date().getFullYear()
  const yearBills = bills.value.filter(b => b.period.includes(currentYear.toString()))
  const totalCost = yearBills.reduce((sum, b) => sum + b.amount, 0) / 1000
  const electricityCost = yearBills.filter(b => b.utilityType === 'Electricity').reduce((sum, b) => sum + b.amount, 0) / 1000
  const waterCost = yearBills.filter(b => b.utilityType === 'Water').reduce((sum, b) => sum + b.amount, 0) / 1000
  const gasCost = yearBills.filter(b => b.utilityType === 'Gas').reduce((sum, b) => sum + b.amount, 0) / 1000

  return {
    totalCost: Math.round(totalCost),
    costTrend: 8.5,
    electricityCost: Math.round(electricityCost),
    waterCost: Math.round(waterCost),
    gasCost: Math.round(gasCost)
  }
})

const metrics = computed(() => {
  const electricityBills = bills.value.filter(b => b.utilityType === 'Electricity')
  const waterBills = bills.value.filter(b => b.utilityType === 'Water')
  const gasBills = bills.value.filter(b => b.utilityType === 'Gas')

  const avgElectricityRate = electricityBills.reduce((sum, b) => sum + b.rate, 0) / electricityBills.length
  const avgWaterRate = waterBills.reduce((sum, b) => sum + b.rate, 0) / waterBills.length
  const avgGasRate = gasBills.reduce((sum, b) => sum + b.rate, 0) / gasBills.length
  const totalSavings = 45

  return {
    electricityRate: avgElectricityRate.toFixed(3),
    electricityTrend: 2.5,
    waterRate: avgWaterRate.toFixed(3),
    gasRate: avgGasRate.toFixed(3),
    savings: totalSavings
  }
})

const filteredBills = computed(() => {
  let filtered = [...bills.value]

  if (utilityFilter.value) {
    filtered = filtered.filter(b => b.utilityType.toLowerCase() === utilityFilter.value)
  }

  if (statusFilter.value) {
    filtered = filtered.filter(b => b.status === statusFilter.value)
  }

  if (dateRange.value && dateRange.value.length === 2) {
    const [start, end] = dateRange.value
    filtered = filtered.filter(b => {
      const billDate = new Date(b.period)
      return billDate >= start && billDate <= end
    })
  }

  return filtered
})

const totalRecords = computed(() => filteredBills.value.length)

const paginatedBills = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBills.value.slice(start, end)
})

// ==================== Helper Functions ====================
const getUtilityTagType = (utility: string): string => {
  const map: Record<string, string> = { Electricity: 'warning', Water: 'info', Gas: 'danger' }
  return map[utility] || 'info'
}

const getStatusText = (status: string): string => {
  const map: Record<string, string> = { paid: 'Paid', pending: 'Pending', overdue: 'Overdue' }
  return map[status] || status
}

const getStatusTagType = (status: string): string => {
  const map: Record<string, string> = { paid: 'success', pending: 'warning', overdue: 'danger' }
  return map[status] || 'info'
}

const getStatusColor = (status: string): string => {
  const map: Record<string, string> = { paid: '#22c55e', pending: '#f59e0b', overdue: '#ef4444' }
  return map[status] || '#64748b'
}

const resetFilters = () => {
  utilityFilter.value = ''
  statusFilter.value = ''
  dateRange.value = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

// ==================== Chart Functions ====================
const initCostTrendChart = () => {
  if (!costTrendChartEl.value) return
  if (costTrendChart) {
    costTrendChart.dispose()
    costTrendChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const electricityData = [45, 42, 48, 52, 58, 65, 72, 78, 68, 58, 48, 52]
  const waterData = [12, 11, 13, 14, 16, 18, 20, 22, 19, 16, 13, 14]
  const gasData = [18, 15, 12, 8, 5, 3, 2, 3, 5, 8, 12, 16]

  costTrendChart = echarts.init(costTrendChartEl.value)
  costTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Electricity', 'Water', 'Gas'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Cost ($K)' },
    series: [
      { name: 'Electricity', type: 'line', data: electricityData, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Water', type: 'line', data: waterData, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } },
      { name: 'Gas', type: 'line', data: gasData, lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', areaStyle: { opacity: 0.1 } }
    ]
  })
}

const initCostDistributionChart = () => {
  if (!costDistributionChartEl.value) return
  if (costDistributionChart) {
    costDistributionChart.dispose()
    costDistributionChart = null
  }

  const currentYear = new Date().getFullYear()
  const yearBills = bills.value.filter(b => b.period.includes(currentYear.toString()))
  const electricityTotal = yearBills.filter(b => b.utilityType === 'Electricity').reduce((sum, b) => sum + b.amount, 0)
  const waterTotal = yearBills.filter(b => b.utilityType === 'Water').reduce((sum, b) => sum + b.amount, 0)
  const gasTotal = yearBills.filter(b => b.utilityType === 'Gas').reduce((sum, b) => sum + b.amount, 0)

  costDistributionChart = echarts.init(costDistributionChartEl.value)
  costDistributionChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: ${c}K ({d}%)' },
    legend: { orient: 'vertical', left: 'left', data: ['Electricity', 'Water', 'Gas'] },
    series: [{
      type: 'pie',
      radius: '55%',
      center: ['50%', '50%'],
      data: [
        { value: Math.round(electricityTotal / 1000), name: 'Electricity', itemStyle: { color: '#f59e0b' } },
        { value: Math.round(waterTotal / 1000), name: 'Water', itemStyle: { color: '#3b82f6' } },
        { value: Math.round(gasTotal / 1000), name: 'Gas', itemStyle: { color: '#ef4444' } }
      ],
      label: { show: true, formatter: '{b}: ${c}K' },
      emphasis: { scale: true }
    }]
  })
}

const initConsumptionChart = () => {
  if (!consumptionChartEl.value) return
  if (consumptionChart) {
    consumptionChart.dispose()
    consumptionChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const electricityConsumption = [38500, 36200, 39800, 42500, 46500, 49500, 53500, 56500, 50500, 44500, 38500, 40500]
  const waterConsumption = [485, 465, 505, 535, 585, 625, 665, 705, 635, 565, 505, 525]

  consumptionChart = echarts.init(consumptionChartEl.value)
  consumptionChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Electricity (kWh)', 'Water (m³)'], bottom: 0 },
    grid: { top: 40, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: [
      { type: 'value', name: 'Electricity (kWh)', position: 'left' },
      { type: 'value', name: 'Water (m³)', position: 'right' }
    ],
    series: [
      { name: 'Electricity (kWh)', type: 'line', data: electricityConsumption, lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', yAxisIndex: 0 },
      { name: 'Water (m³)', type: 'line', data: waterConsumption, lineStyle: { color: '#3b82f6', width: 2 }, symbol: 'diamond', yAxisIndex: 1 }
    ]
  })
}

const initRateComparisonChart = () => {
  if (!rateComparisonChartEl.value) return
  if (rateComparisonChart) {
    rateComparisonChart.dispose()
    rateComparisonChart = null
  }

  rateComparisonChart = echarts.init(rateComparisonChartEl.value)
  rateComparisonChart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['Our Rate', 'Industry Avg'], bottom: 0 },
    grid: { top: 30, left: 60, right: 30, bottom: 40 },
    xAxis: { type: 'category', data: ['Electricity (¢/kWh)', 'Water ($/m³)', 'Gas ($/m³)'] },
    yAxis: { type: 'value', name: 'Rate' },
    series: [
      { name: 'Our Rate', type: 'bar', data: [12.5, 0.85, 0.48], itemStyle: { color: '#3b82f6', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}' } },
      { name: 'Industry Avg', type: 'bar', data: [14.2, 0.92, 0.52], itemStyle: { color: '#94a3b8', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}' } }
    ]
  })
}

const initBudgetChart = () => {
  if (!budgetChartEl.value) return
  if (budgetChart) {
    budgetChart.dispose()
    budgetChart = null
  }

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
  const budgetData = [75, 72, 78, 82, 85, 90, 95, 98, 92, 85, 78, 82]
  const actualData = [68, 65, 72, 78, 82, 86, 90, 92, 88, 82, 75, 78]

  budgetChart = echarts.init(budgetChartEl.value)
  budgetChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Budget', 'Actual'], bottom: 0 },
    grid: { top: 30, left: 50, right: 20, bottom: 40 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: 'Cost ($K)' },
    series: [
      { name: 'Budget', type: 'line', data: budgetData, lineStyle: { color: '#94a3b8', width: 2, type: 'dashed' }, symbol: 'diamond' },
      { name: 'Actual', type: 'bar', data: actualData, itemStyle: { color: '#22c55e', borderRadius: [4, 4, 0, 0] }, label: { show: true, position: 'top', formatter: '${c}K' } }
    ]
  })
}

const initBillTrendChart = () => {
  if (!billTrendChartEl.value || !selectedBill.value) return
  if (billTrendChart) {
    billTrendChart.dispose()
    billTrendChart = null
  }

  const months = ['6 months ago', '5 months', '4 months', '3 months', '2 months', 'Last month', 'Current']
  const consumptionData = [420, 445, 430, 460, 480, 465, selectedBill.value.consumption / 100]

  billTrendChart = echarts.init(billTrendChartEl.value)
  billTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { top: 30, left: 50, right: 20, bottom: 30 },
    xAxis: { type: 'category', data: months },
    yAxis: { type: 'value', name: `Consumption (${selectedBill.value.unit})` },
    series: [{
      type: 'line',
      data: consumptionData,
      smooth: true,
      lineStyle: { color: '#3b82f6', width: 3 },
      symbol: 'circle',
      symbolSize: 8,
      areaStyle: { opacity: 0.1 },
      label: { show: true, position: 'top' }
    }]
  })
}

const refreshCharts = () => {
  nextTick(() => {
    initCostTrendChart()
    initCostDistributionChart()
    initConsumptionChart()
    initRateComparisonChart()
    initBudgetChart()
  })
}

// ==================== Actions ====================
const viewBillDetail = (bill: UtilityBill) => {
  selectedBill.value = bill
  detailDialogVisible.value = true
  nextTick(() => initBillTrendChart())
}

const markAsPaid = (bill: UtilityBill | null) => {
  if (bill) {
    ElMessage.success(`Bill ${bill.id} marked as paid`)
  }
}

const downloadBill = (bill: UtilityBill | null) => {
  if (bill) {
    ElMessage.success(`Downloading bill ${bill.id}...`)
  }
}

const viewAllBills = () => {
  ElMessage.info('Viewing all bills')
}

const uploadBill = () => {
  uploadForm.value = {
    utilityType: 'electricity',
    period: '',
    notes: '',
    file: null
  }
  uploadDialogVisible.value = true
}

const handleFileChange = (file: any) => {
  uploadForm.value.file = file
}

const saveUpload = () => {
  if (!uploadForm.value.period) {
    ElMessage.warning('Please select billing period')
    return
  }
  ElMessage.success('Bill uploaded successfully')
  uploadDialogVisible.value = false
}

const exportData = () => {
  ElMessage.success('Exporting billing data...')
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
    const charts = [costTrendChart, costDistributionChart, consumptionChart, rateComparisonChart, budgetChart, billTrendChart]
    charts.forEach(chart => {
      if (chart && !chart.isDisposed()) chart.resize()
    })
  }, 100)
}

// ==================== Watch ====================
watch([utilityFilter, statusFilter, dateRange], () => {
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
  const charts = [costTrendChart, costDistributionChart, consumptionChart, rateComparisonChart, budgetChart, billTrendChart]
  charts.forEach(chart => {
    if (chart && !chart.isDisposed()) chart.dispose()
  })
})
</script>

<style scoped>
.utility-billing-page {
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
.stat-icon.red { background: #fee2e2; color: #ef4444; }

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
  font-size: 28px;
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

.chart-card.large {
  flex: 2;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
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
  height: 300px;
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

/* Bill Detail */
.bill-detail {
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
  font-size: 28px;
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

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.comparison-item {
  text-align: center;
}

.comparison-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.comparison-item span:last-child {
  font-size: 20px;
  font-weight: 700;
}

.trend-chart {
  height: 280px;
  width: 100%;
}

.metric-good { color: #22c55e; font-weight: 600; }
.metric-warning { color: #f59e0b; font-weight: 600; }
.metric-bad { color: #ef4444; font-weight: 600; }

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
  .comparison-grid {
    grid-template-columns: 1fr;
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
  .filter-left .el-select,
  .filter-left .el-date-editor {
    width: 100% !important;
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
:deep(.el-upload-dragger) {
  width: 100%;
}
</style>