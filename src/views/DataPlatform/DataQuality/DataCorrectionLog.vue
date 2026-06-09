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
        <div class="loading-tip">Data Correction Log</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="correction-log-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Quality</el-breadcrumb-item>
            <el-breadcrumb-item>Data Correction Log</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Correction Log</h1>
        <p class="description">Complete audit trail of all data corrections, changes, and quality improvements</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Log
        </el-button>
        <el-button type="primary" @click="handleCreateCorrection">
          <el-icon><Plus /></el-icon>
          Manual Correction
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

    <!-- Correction Trends Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Correction Activity Trend</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="daily">Daily</el-radio-button>
                <el-radio-button value="weekly">Weekly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Corrections by Type</span>
            </div>
          </template>
          <div ref="typeChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by table or column"
              prefix-icon="Search"
              clearable
              style="width: 220px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.correctionType" placeholder="Correction Type" clearable style="width: 150px">
            <el-option label="Missing Data" value="Missing Data" />
            <el-option label="Outlier" value="Outlier" />
            <el-option label="Format Error" value="Format Error" />
            <el-option label="Type Mismatch" value="Type Mismatch" />
            <el-option label="Duplicate" value="Duplicate" />
          </el-select>
          <el-select v-model="filters.method" placeholder="Method" clearable style="width: 140px">
            <el-option label="Fill Default" value="Fill Default" />
            <el-option label="Impute Median" value="Impute Median" />
            <el-option label="Impute Mean" value="Impute Mean" />
            <el-option label="Manual Edit" value="Manual Edit" />
            <el-option label="Auto-correct" value="Auto-correct" />
          </el-select>
          <el-select v-model="filters.initiator" placeholder="Initiator" clearable style="width: 140px">
            <el-option label="System" value="System" />
            <el-option label="John Smith" value="John Smith" />
            <el-option label="Sarah Chen" value="Sarah Chen" />
            <el-option label="David Wang" value="David Wang" />
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

    <!-- Correction Log Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Correction Log ({{ filteredLogs.length }} records)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchLogs" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedLogs" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="table" label="Table" width="160" show-overflow-tooltip />
        <el-table-column prop="column" label="Column" width="140" show-overflow-tooltip />
        <el-table-column prop="recordId" label="Record ID" width="120" />
        <el-table-column prop="oldValue" label="Old Value" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="old-value">{{ row.oldValue || 'NULL' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="newValue" label="New Value" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="new-value">{{ row.newValue || 'NULL' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="correctionType" label="Type" width="130">
          <template #default="{ row }">
            <el-tag :type="getCorrectionTypeTag(row.correctionType)" size="small">{{ row.correctionType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="Method" width="120" />
        <el-table-column prop="initiator" label="Initiator" width="130" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="danger" size="small" @click="revertCorrection(row)">Revert</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredLogs.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Correction Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Correction Details - #${currentLog?.id}`" width="700px" destroy-on-close>
      <div class="correction-details" v-if="currentLog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Timestamp">{{ currentLog.timestamp }}</el-descriptions-item>
          <el-descriptions-item label="Table">{{ currentLog.table }}</el-descriptions-item>
          <el-descriptions-item label="Column">{{ currentLog.column }}</el-descriptions-item>
          <el-descriptions-item label="Record ID">{{ currentLog.recordId }}</el-descriptions-item>
          <el-descriptions-item label="Old Value">
            <span class="old-value-highlight">{{ currentLog.oldValue || 'NULL' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="New Value">
            <span class="new-value-highlight">{{ currentLog.newValue || 'NULL' }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="Correction Type">
            <el-tag :type="getCorrectionTypeTag(currentLog.correctionType)" size="small">{{ currentLog.correctionType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Method">{{ currentLog.method }}</el-descriptions-item>
          <el-descriptions-item label="Initiator">{{ currentLog.initiator }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentLog.status === 'Applied' ? 'success' : 'info'" size="small">{{ currentLog.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Reason" :span="2">{{ currentLog.reason }}</el-descriptions-item>
          <el-descriptions-item label="Validation Rule" :span="2" v-if="currentLog.validationRule">{{ currentLog.validationRule }}</el-descriptions-item>
          <el-descriptions-item label="Source" :span="2" v-if="currentLog.source">{{ currentLog.source }}</el-descriptions-item>
        </el-descriptions>

        <!-- Affected Records -->
        <div class="affected-records" v-if="currentLog.affectedRecords?.length">
          <h4>Other Affected Records</h4>
          <el-table :data="currentLog.affectedRecords" size="small" border>
            <el-table-column prop="recordId" label="Record ID" width="150" />
            <el-table-column prop="oldValue" label="Old Value" min-width="150" />
            <el-table-column prop="newValue" label="New Value" min-width="150" />
          </el-table>
        </div>

        <!-- Before/After Stats -->
        <div class="impact-stats" v-if="currentLog.impactStats">
          <h4>Impact Statistics</h4>
          <el-row :gutter="16">
            <el-col :span="8">
              <div class="stat-mini">
                <div class="stat-mini-value">{{ currentLog.impactStats.recordsAffected }}</div>
                <div class="stat-mini-label">Records Affected</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-mini">
                <div class="stat-mini-value">{{ currentLog.impactStats.qualityImprovement }}%</div>
                <div class="stat-mini-label">Quality Improvement</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="stat-mini">
                <div class="stat-mini-value">{{ currentLog.impactStats.errorReduction }}%</div>
                <div class="stat-mini-label">Error Reduction</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="danger" @click="revertCorrection(currentLog)">Revert Correction</el-button>
      </template>
    </el-dialog>

    <!-- Manual Correction Dialog -->
    <el-dialog v-model="manualDialogVisible" title="Manual Data Correction" width="600px" destroy-on-close>
      <el-form :model="manualForm" :rules="manualRules" ref="manualFormRef" label-width="120px">
        <el-form-item label="Table" prop="table">
          <el-select v-model="manualForm.table" placeholder="Select table" style="width: 100%">
            <el-option label="device_master" value="device_master" />
            <el-option label="energy_consumption" value="energy_consumption" />
            <el-option label="customer_contract" value="customer_contract" />
            <el-option label="maintenance_work_orders" value="maintenance_work_orders" />
          </el-select>
        </el-form-item>
        <el-form-item label="Column" prop="column">
          <el-input v-model="manualForm.column" placeholder="Enter column name" />
        </el-form-item>
        <el-form-item label="Record ID" prop="recordId">
          <el-input v-model="manualForm.recordId" placeholder="Enter record ID" />
        </el-form-item>
        <el-form-item label="Current Value" prop="oldValue">
          <el-input v-model="manualForm.oldValue" placeholder="Current value" disabled />
        </el-form-item>
        <el-form-item label="New Value" prop="newValue">
          <el-input v-model="manualForm.newValue" placeholder="Enter new value" />
        </el-form-item>
        <el-form-item label="Correction Type" prop="correctionType">
          <el-select v-model="manualForm.correctionType" placeholder="Select type" style="width: 100%">
            <el-option label="Missing Data" value="Missing Data" />
            <el-option label="Outlier" value="Outlier" />
            <el-option label="Format Error" value="Format Error" />
            <el-option label="Type Mismatch" value="Type Mismatch" />
            <el-option label="Duplicate" value="Duplicate" />
          </el-select>
        </el-form-item>
        <el-form-item label="Reason" prop="reason">
          <el-input v-model="manualForm.reason" type="textarea" :rows="2" placeholder="Enter reason for correction" />
        </el-form-item>
        <el-form-item label="Apply to All Similar">
          <el-switch v-model="manualForm.applyToAll" />
          <span style="margin-left: 8px; color: #909399">Apply same correction to all matching records</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="manualDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitManualCorrection">Apply Correction</el-button>
      </template>
    </el-dialog>

    <!-- Revert Confirmation Dialog -->
    <el-dialog v-model="revertDialogVisible" title="Confirm Revert" width="400px">
      <p>Are you sure you want to revert this correction?</p>
      <p><strong>Record:</strong> {{ revertTarget?.table }}.{{ revertTarget?.column }} (ID: {{ revertTarget?.recordId }})</p>
      <p><strong>Will revert from:</strong> {{ revertTarget?.newValue }} → {{ revertTarget?.oldValue || 'NULL' }}</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action will create a new correction record.</p>
      <template #footer>
        <el-button @click="revertDialogVisible = false">Cancel</el-button>
        <el-button type="danger" @click="confirmRevert">Revert</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  DataAnalysis, Filter, Warning, Delete
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading correction log...',
  'Indexing changes...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const detailsDialogVisible = ref(false)
const manualDialogVisible = ref(false)
const revertDialogVisible = ref(false)
const currentLog = ref<any>(null)
const revertTarget = ref<any>(null)
const manualFormRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)
const trendPeriod = ref('daily')

const filters = reactive({
  keyword: '',
  correctionType: '',
  method: '',
  initiator: '',
  dateRange: null as [Date, Date] | null
})

const manualForm = reactive({
  table: '',
  column: '',
  recordId: '',
  oldValue: '',
  newValue: '',
  correctionType: '',
  reason: '',
  applyToAll: false
})

const manualRules = {
  table: [{ required: true, message: 'Please select table', trigger: 'change' }],
  column: [{ required: true, message: 'Please enter column name', trigger: 'blur' }],
  recordId: [{ required: true, message: 'Please enter record ID', trigger: 'blur' }],
  newValue: [{ required: true, message: 'Please enter new value', trigger: 'blur' }],
  correctionType: [{ required: true, message: 'Please select correction type', trigger: 'change' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Corrections', value: 1248, trend: 15, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Auto Corrections', value: 892, trend: 18, icon: 'DataAnalysis', bgColor: '#67c23a', key: 'auto' },
  { title: 'Manual Corrections', value: 356, trend: 8, icon: 'User', bgColor: '#e6a23c', key: 'manual' },
  { title: 'Reverts', value: 24, trend: -5, icon: 'Refresh', bgColor: '#f56c6c', key: 'reverts' }
])

const correctionLogs = ref([
  {
    id: 1,
    timestamp: '2024-01-20 08:30:15',
    table: 'device_master',
    column: 'location',
    recordId: 'DEV-045',
    oldValue: null,
    newValue: 'Building A - Floor 3',
    correctionType: 'Missing Data',
    method: 'Fill Default',
    initiator: 'System',
    status: 'Applied',
    reason: 'Missing location field populated from installation records',
    validationRule: 'location IS NOT NULL',
    source: 'Auto-detection',
    impactStats: {
      recordsAffected: 234,
      qualityImprovement: 8.5,
      errorReduction: 12
    }
  },
  {
    id: 2,
    timestamp: '2024-01-20 08:30:15',
    table: 'device_master',
    column: 'location',
    recordId: 'DEV-078',
    oldValue: null,
    newValue: 'Building B - Server Room',
    correctionType: 'Missing Data',
    method: 'Fill Default',
    initiator: 'System',
    status: 'Applied',
    reason: 'Missing location field populated from installation records',
    affectedRecords: [
      { recordId: 'DEV-089', oldValue: null, newValue: 'Building C - Cooling Tower' },
      { recordId: 'DEV-102', oldValue: null, newValue: 'Building A - Floor 1' }
    ]
  },
  {
    id: 3,
    timestamp: '2024-01-19 14:20:30',
    table: 'energy_consumption',
    column: 'consumption_kwh',
    recordId: 'REC-1023',
    oldValue: 15200,
    newValue: 3200,
    correctionType: 'Outlier',
    method: 'Manual Edit',
    initiator: 'John Smith',
    status: 'Applied',
    reason: 'Corrected abnormal consumption spike - confirmed data entry error',
    impactStats: {
      recordsAffected: 1,
      qualityImprovement: 0.5,
      errorReduction: 100
    }
  },
  {
    id: 4,
    timestamp: '2024-01-19 10:15:00',
    table: 'device_readings',
    column: 'temperature',
    recordId: 'SEN-0456',
    oldValue: 45.2,
    newValue: 22.5,
    correctionType: 'Outlier',
    method: 'Impute Median',
    initiator: 'System',
    status: 'Applied',
    reason: 'Temperature outlier corrected using median of neighboring values',
    validationRule: 'temperature BETWEEN 18 AND 28',
    source: 'IQR Detection'
  },
  {
    id: 5,
    timestamp: '2024-01-18 16:45:22',
    table: 'customer_contract',
    column: 'end_date',
    recordId: 'CT-089',
    oldValue: '2023-12-31',
    newValue: '2024-12-31',
    correctionType: 'Format Error',
    method: 'Manual Edit',
    initiator: 'Sarah Chen',
    status: 'Applied',
    reason: 'Incorrect contract end date corrected based on contract terms',
    validationRule: 'end_date > start_date'
  },
  {
    id: 6,
    timestamp: '2024-01-18 09:30:00',
    table: 'energy_consumption',
    column: 'cost_usd',
    recordId: 'INV-5678',
    oldValue: -1250,
    newValue: 1250,
    correctionType: 'Type Mismatch',
    method: 'Auto-correct',
    initiator: 'System',
    status: 'Applied',
    reason: 'Negative cost value converted to positive',
    validationRule: 'cost_usd >= 0'
  },
  {
    id: 7,
    timestamp: '2024-01-17 11:00:00',
    table: 'device_master',
    column: 'device_id',
    recordId: 'DEV-001',
    oldValue: 'DEV-001',
    newValue: 'DEV-001',
    correctionType: 'Duplicate',
    method: 'Manual Edit',
    initiator: 'David Wang',
    status: 'Applied',
    reason: 'Removed duplicate record',
    affectedRecords: [
      { recordId: 'DEV-001-DUP', oldValue: 'DEV-001', newValue: null }
    ]
  },
  {
    id: 8,
    timestamp: '2024-01-16 13:20:00',
    table: 'maintenance_work_orders',
    column: 'completion_date',
    recordId: 'WO-0456',
    oldValue: null,
    newValue: '2024-01-20',
    correctionType: 'Missing Data',
    method: 'Manual Edit',
    initiator: 'Mike Johnson',
    status: 'Applied',
    reason: 'Completion date added after work finished'
  }
])

// ==================== Computed ====================
const filteredLogs = computed(() => {
  let filtered = [...correctionLogs.value]

  if (filters.keyword) {
    filtered = filtered.filter(l =>
        l.table.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        l.column.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.correctionType) {
    filtered = filtered.filter(l => l.correctionType === filters.correctionType)
  }

  if (filters.method) {
    filtered = filtered.filter(l => l.method === filters.method)
  }

  if (filters.initiator) {
    filtered = filtered.filter(l => l.initiator === filters.initiator)
  }

  if (filters.dateRange && filters.dateRange[0] && filters.dateRange[1]) {
    filtered = filtered.filter(l => {
      const date = new Date(l.timestamp)
      return date >= filters.dateRange![0] && date <= filters.dateRange![1]
    })
  }

  return filtered
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCorrectionTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Missing Data': 'warning',
    'Outlier': 'danger',
    'Format Error': 'info',
    'Type Mismatch': 'primary',
    'Duplicate': 'success'
  }
  return map[type] || 'info'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const dailyData = [45, 52, 48, 61, 55, 58, 62, 59, 65, 68, 72, 75, 78, 82, 85, 88, 92, 95, 98, 102, 105, 108, 112, 115, 118, 122, 125, 128, 132, 135]
  const weeklyData = [312, 345, 378, 402, 425, 448, 472, 495, 518, 542, 565, 588]
  const data = trendPeriod.value === 'daily' ? dailyData : weeklyData
  const xAxisData = trendPeriod.value === 'daily'
      ? Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
      : ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Corrections' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 8
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initTypeChart = () => {
  if (!typeChartRef.value) return
  if (typeChart) typeChart.dispose()

  typeChart = echarts.init(typeChartRef.value)

  const typeCount = {
    'Missing Data': correctionLogs.value.filter(l => l.correctionType === 'Missing Data').length,
    'Outlier': correctionLogs.value.filter(l => l.correctionType === 'Outlier').length,
    'Format Error': correctionLogs.value.filter(l => l.correctionType === 'Format Error').length,
    'Type Mismatch': correctionLogs.value.filter(l => l.correctionType === 'Type Mismatch').length,
    'Duplicate': correctionLogs.value.filter(l => l.correctionType === 'Duplicate').length
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} corrections)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: typeCount['Missing Data'], name: 'Missing Data', itemStyle: { color: '#e6a23c' } },
        { value: typeCount['Outlier'], name: 'Outlier', itemStyle: { color: '#f56c6c' } },
        { value: typeCount['Format Error'], name: 'Format Error', itemStyle: { color: '#409eff' } },
        { value: typeCount['Type Mismatch'], name: 'Type Mismatch', itemStyle: { color: '#67c23a' } },
        { value: typeCount['Duplicate'], name: 'Duplicate', itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  typeChart.setOption(option)
  window.addEventListener('resize', () => typeChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleResetFilters = () => {
  filters.keyword = ''
  filters.correctionType = ''
  filters.method = ''
  filters.initiator = ''
  filters.dateRange = null
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredLogs.value.length} correction records...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleCreateCorrection = () => {
  Object.assign(manualForm, {
    table: '',
    column: '',
    recordId: '',
    oldValue: '',
    newValue: '',
    correctionType: '',
    reason: '',
    applyToAll: false
  })
  manualDialogVisible.value = true
}

const fetchLogs = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Logs refreshed')
  }, 500)
}

const viewDetails = (log: any) => {
  currentLog.value = log
  detailsDialogVisible.value = true
}

const revertCorrection = (log: any) => {
  revertTarget.value = log
  revertDialogVisible.value = true
}

const confirmRevert = () => {
  if (revertTarget.value) {
    ElMessage.success(`Reverted correction for ${revertTarget.value.table}.${revertTarget.value.column}`)
    revertDialogVisible.value = false
    revertTarget.value = null
  }
}

const submitManualCorrection = async () => {
  if (!manualFormRef.value) return
  await manualFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Manual correction applied successfully')
      manualDialogVisible.value = false
      manualFormRef.value?.resetFields()
    }
  })
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
      fetchLogs()
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
.correction-log-page {
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

.chart-card {
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

.old-value {
  color: #f56c6c;
  font-family: monospace;
}

.new-value {
  color: #67c23a;
  font-family: monospace;
}

.old-value-highlight {
  color: #f56c6c;
  font-weight: 600;
  font-family: monospace;
}

.new-value-highlight {
  color: #67c23a;
  font-weight: 600;
  font-family: monospace;
}

.correction-details {
  .affected-records, .impact-stats {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .stat-mini {
    text-align: center;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .stat-mini-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }

    .stat-mini-label {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
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