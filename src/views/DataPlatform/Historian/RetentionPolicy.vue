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
        <div class="loading-tip">Retention Policy Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="retention-policy-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Historian</el-breadcrumb-item>
            <el-breadcrumb-item>Retention Policy</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Retention Policy</h1>
        <p class="description">Configure and manage data lifecycle, archiving, and deletion policies for telemetry data</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Policies
        </el-button>
        <el-button type="primary" @click="handleCreatePolicy">
          <el-icon><Plus /></el-icon>
          Create Policy
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

    <!-- Storage Overview Chart -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Storage Usage Trend</span>
              <el-radio-group v-model="storagePeriod" size="small">
                <el-radio-button value="monthly">Monthly</el-radio-button>
                <el-radio-button value="quarterly">Quarterly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="storageChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Data Distribution by Age</span>
            </div>
          </template>
          <div ref="ageChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by policy name or description"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.dataType" placeholder="Data Type" clearable style="width: 140px">
            <el-option label="Raw Telemetry" value="raw" />
            <el-option label="Clean Telemetry" value="clean" />
            <el-option label="Aggregated Data" value="aggregated" />
            <el-option label="Events" value="events" />
          </el-select>
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Active" value="active" />
            <el-option label="Pending" value="pending" />
            <el-option label="Archived" value="archived" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Policies Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Retention Policies ({{ filteredPolicies.length }} policies)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchPolicies" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedPolicies" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Policy Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="dataType" label="Data Type" width="140">
          <template #default="{ row }">
            <el-tag :type="getDataTypeTag(row.dataType)" size="small">{{ row.dataType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="retentionPeriod" label="Retention Period"  />
        <el-table-column prop="storageTier" label="Storage Tier" >
          <template #default="{ row }">
            <el-tag :type="getStorageTierTag(row.storageTier)" size="small">{{ row.storageTier }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="currentSize" label="Current Size"  align="right" />
        <el-table-column prop="status" label="Status" >
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="nextCleanup" label="Next Cleanup"  />
        <el-table-column label="Actions"  fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewPolicy(row)">View</el-button>
            <el-button link type="success" size="small" @click="editPolicy(row)">Edit</el-button>
            <el-button link type="info" size="small" @click="runCleanup(row)">Run Cleanup</el-button>
            <el-button link type="danger" size="small" @click="deletePolicy(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredPolicies.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit Policy Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create Retention Policy' : 'Edit Retention Policy'" width="650px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="Policy Name" prop="name">
              <el-input v-model="formData.name" placeholder="Enter policy name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Data Type" prop="dataType">
              <el-select v-model="formData.dataType" placeholder="Select data type" style="width: 100%">
                <el-option label="Raw Telemetry" value="Raw Telemetry" />
                <el-option label="Clean Telemetry" value="Clean Telemetry" />
                <el-option label="Aggregated Data" value="Aggregated Data" />
                <el-option label="Events" value="Events" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Storage Tier" prop="storageTier">
              <el-select v-model="formData.storageTier" placeholder="Select storage tier" style="width: 100%">
                <el-option label="Hot" value="Hot" />
                <el-option label="Warm" value="Warm" />
                <el-option label="Cold" value="Cold" />
                <el-option label="Archive" value="Archive" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Retention Period" prop="retentionValue">
              <el-input-number v-model="formData.retentionValue" :min="1" :max="3650" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Retention Unit" prop="retentionUnit">
              <el-select v-model="formData.retentionUnit" placeholder="Select unit" style="width: 100%">
                <el-option label="Days" value="Days" />
                <el-option label="Months" value="Months" />
                <el-option label="Years" value="Years" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Action" prop="action">
              <el-radio-group v-model="formData.action">
                <el-radio value="delete">Delete Permanently</el-radio>
                <el-radio value="archive">Archive to Cold Storage</el-radio>
                <el-radio value="aggregate">Aggregate & Downsample</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="formData.action === 'archive'">
            <el-form-item label="Archive Target" prop="archiveTarget">
              <el-input v-model="formData.archiveTarget" placeholder="e.g., s3://archive-bucket/telemetry/" />
            </el-form-item>
          </el-col>
          <el-col :span="24" v-if="formData.action === 'aggregate'">
            <el-form-item label="Aggregation Level" prop="aggregationLevel">
              <el-select v-model="formData.aggregationLevel" placeholder="Select aggregation level" style="width: 100%">
                <el-option label="Hourly" value="Hourly" />
                <el-option label="Daily" value="Daily" />
                <el-option label="Weekly" value="Weekly" />
                <el-option label="Monthly" value="Monthly" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter policy description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save Policy</el-button>
      </template>
    </el-dialog>

    <!-- Policy Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Policy Details - ${currentPolicy?.name}`" width="700px" destroy-on-close>
      <div class="policy-details" v-if="currentPolicy">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Policy Name">{{ currentPolicy.name }}</el-descriptions-item>
          <el-descriptions-item label="Data Type">
            <el-tag :type="getDataTypeTag(currentPolicy.dataType)" size="small">{{ currentPolicy.dataType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Storage Tier">
            <el-tag :type="getStorageTierTag(currentPolicy.storageTier)" size="small">{{ currentPolicy.storageTier }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentPolicy.status)" size="small">{{ currentPolicy.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Retention Period">{{ currentPolicy.retentionPeriod }}</el-descriptions-item>
          <el-descriptions-item label="Current Size">{{ currentPolicy.currentSize }}</el-descriptions-item>
          <el-descriptions-item label="Next Cleanup">{{ currentPolicy.nextCleanup }}</el-descriptions-item>
          <el-descriptions-item label="Last Cleanup">{{ currentPolicy.lastCleanup || 'Never' }}</el-descriptions-item>
          <el-descriptions-item label="Action">{{ currentPolicy.action }}</el-descriptions-item>
          <el-descriptions-item label="Records Deleted" v-if="currentPolicy.recordsDeleted">{{ currentPolicy.recordsDeleted.toLocaleString() }}</el-descriptions-item>
          <el-descriptions-item label="Space Freed" v-if="currentPolicy.spaceFreed">{{ currentPolicy.spaceFreed }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentPolicy.description }}</el-descriptions-item>
        </el-descriptions>

        <!-- Cleanup History -->
        <div class="cleanup-history" v-if="currentPolicy.cleanupHistory?.length">
          <h4>Cleanup History</h4>
          <el-table :data="currentPolicy.cleanupHistory" size="small" border>
            <el-table-column prop="date" label="Date"  />
            <el-table-column prop="recordsDeleted" label="Records Deleted" width="140" align="right" />
            <el-table-column prop="sizeFreed" label="Space Freed"  />
            <el-table-column prop="duration" label="Duration"  />
            <el-table-column prop="status" label="Status" >
              <template #default="{ row }">
                <el-tag :type="row.status === 'Success' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="runCleanup(currentPolicy)">Run Cleanup Now</el-button>
      </template>
    </el-dialog>

    <!-- Cleanup Confirmation Dialog -->
    <el-dialog v-model="cleanupDialogVisible" title="Run Cleanup" width="450px">
      <p>Are you sure you want to run cleanup for policy:</p>
      <p><strong>{{ cleanupTarget?.name }}</strong></p>
      <p>This will {{ cleanupTarget?.action === 'delete' ? 'permanently delete' : cleanupTarget?.action === 'archive' ? 'archive' : 'aggregate' }}
        data older than {{ cleanupTarget?.retentionPeriod }}.</p>
      <p style="color: #e6a23c; font-size: 12px; margin-top: 8px">This action may take some time and cannot be undone.</p>
      <template #footer>
        <el-button @click="cleanupDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmCleanup">Run Cleanup</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete policy "{{ deleteTarget?.name }}"?</p>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Delete, Folder
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading retention policies...',
  'Analyzing storage usage...',
  'Almost ready...'
]

// ==================== Chart References ====================
const storageChartRef = ref<HTMLElement>()
const ageChartRef = ref<HTMLElement>()
let storageChart: echarts.ECharts | null = null
let ageChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const cleanupDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentPolicy = ref<any>(null)
const cleanupTarget = ref<any>(null)
const deleteTarget = ref<any>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(10)
const storagePeriod = ref('monthly')

const filters = reactive({
  keyword: '',
  dataType: '',
  status: ''
})

const formData = reactive({
  name: '',
  dataType: '',
  storageTier: 'Hot',
  retentionValue: 365,
  retentionUnit: 'Days',
  action: 'delete',
  archiveTarget: '',
  aggregationLevel: 'Daily',
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter policy name', trigger: 'blur' }],
  dataType: [{ required: true, message: 'Please select data type', trigger: 'change' }],
  retentionValue: [{ required: true, message: 'Please enter retention period', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Storage', value: '156 TB', trend: 12, icon: 'Document', bgColor: '#409eff', key: 'storage' },
  { title: 'Active Policies', value: 8, trend: 0, icon: 'Checked', bgColor: '#67c23a', key: 'active' },
  { title: 'Scheduled Cleanups', value: 24, trend: 8, icon: 'Clock', bgColor: '#e6a23c', key: 'scheduled' },
  { title: 'Space Reclaimed', value: '12.4 TB', trend: 18, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'reclaimed' }
])

const retentionPolicies = ref([
  {
    id: 1,
    name: 'Raw Telemetry - Hot Storage',
    dataType: 'Raw Telemetry',
    retentionPeriod: '90 Days',
    storageTier: 'Hot',
    currentSize: '45.2 TB',
    status: 'active',
    nextCleanup: '2024-01-25 02:00:00',
    lastCleanup: '2024-01-18 02:15:23',
    action: 'delete',
    recordsDeleted: 12500000,
    spaceFreed: '2.4 TB',
    description: 'Raw telemetry data retention on hot storage for fast access',
    cleanupHistory: [
      { date: '2024-01-18 02:15:23', recordsDeleted: 12500000, sizeFreed: '2.4 TB', duration: '8 min', status: 'Success' },
      { date: '2024-01-11 02:10:15', recordsDeleted: 11800000, sizeFreed: '2.2 TB', duration: '7 min', status: 'Success' }
    ]
  },
  {
    id: 2,
    name: 'Raw Telemetry - Warm Archive',
    dataType: 'Raw Telemetry',
    retentionPeriod: '1 Year',
    storageTier: 'Warm',
    currentSize: '78.5 TB',
    status: 'active',
    nextCleanup: '2024-02-01 03:00:00',
    lastCleanup: '2024-01-15 03:30:12',
    action: 'archive',
    archiveTarget: 's3://archive-bucket/raw-telemetry/',
    description: 'Raw telemetry data moved to warm storage after 90 days',
    cleanupHistory: [
      { date: '2024-01-15 03:30:12', recordsDeleted: 0, sizeFreed: '0 TB', duration: '15 min', status: 'Success' }
    ]
  },
  {
    id: 3,
    name: 'Clean Telemetry',
    dataType: 'Clean Telemetry',
    retentionPeriod: '2 Years',
    storageTier: 'Cold',
    currentSize: '28.3 TB',
    status: 'active',
    nextCleanup: '2024-02-10 01:00:00',
    lastCleanup: '2024-01-10 01:45:30',
    action: 'delete',
    recordsDeleted: 8500000,
    spaceFreed: '1.8 TB',
    description: 'Cleaned and validated telemetry data',
    cleanupHistory: [
      { date: '2024-01-10 01:45:30', recordsDeleted: 8500000, sizeFreed: '1.8 TB', duration: '6 min', status: 'Success' }
    ]
  },
  {
    id: 4,
    name: 'Aggregated Data',
    dataType: 'Aggregated Data',
    retentionPeriod: '5 Years',
    storageTier: 'Cold',
    currentSize: '3.2 TB',
    status: 'active',
    nextCleanup: '2024-02-15 04:00:00',
    description: 'Hourly and daily aggregated data for long-term trend analysis',
    cleanupHistory: []
  },
  {
    id: 5,
    name: 'Event Logs',
    dataType: 'Events',
    retentionPeriod: '90 Days',
    storageTier: 'Hot',
    currentSize: '0.8 TB',
    status: 'pending',
    nextCleanup: '2024-01-30 02:00:00',
    description: 'System event and audit logs',
    cleanupHistory: []
  }
])

// ==================== Computed ====================
const filteredPolicies = computed(() => {
  let filtered = [...retentionPolicies.value]

  if (filters.keyword) {
    filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        p.description.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.dataType) {
    filtered = filtered.filter(p => p.dataType === filters.dataType)
  }

  if (filters.status) {
    filtered = filtered.filter(p => p.status === filters.status)
  }

  return filtered
})

const paginatedPolicies = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredPolicies.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getDataTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Raw Telemetry': 'warning',
    'Clean Telemetry': 'success',
    'Aggregated Data': 'primary',
    'Events': 'info'
  }
  return map[type] || 'info'
}

const getStorageTierTag = (tier: string) => {
  const map: Record<string, string> = {
    'Hot': 'danger',
    'Warm': 'warning',
    'Cold': 'info',
    'Archive': 'success'
  }
  return map[tier] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'active': 'success',
    'pending': 'warning',
    'archived': 'info'
  }
  return map[status] || 'info'
}

// ==================== Chart Initializations ====================
const initStorageChart = () => {
  if (!storageChartRef.value) return
  if (storageChart) storageChart.dispose()

  storageChart = echarts.init(storageChartRef.value)

  const monthlyData = [142, 148, 152, 158, 162, 165, 168, 172, 175, 178, 182, 185]
  const quarterlyData = [430, 465, 495, 525]
  const data = storagePeriod.value === 'monthly' ? monthlyData : quarterlyData
  const xAxisData = storagePeriod.value === 'monthly'
      ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      : ['Q1', 'Q2', 'Q3', 'Q4']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Storage (TB)' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 8
    }]
  }

  storageChart.setOption(option)
  window.addEventListener('resize', () => storageChart?.resize())
}

const initAgeChart = () => {
  if (!ageChartRef.value) return
  if (ageChart) ageChart.dispose()

  ageChart = echarts.init(ageChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} TB)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 45, name: '< 30 days', itemStyle: { color: '#67c23a' } },
        { value: 38, name: '30-90 days', itemStyle: { color: '#409eff' } },
        { value: 28, name: '90-365 days', itemStyle: { color: '#e6a23c' } },
        { value: 45, name: '> 1 year', itemStyle: { color: '#f56c6c' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  ageChart.setOption(option)
  window.addEventListener('resize', () => ageChart?.resize())
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
  filters.dataType = ''
  filters.status = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredPolicies.value.length} policies...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchPolicies = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Policies refreshed')
  }, 500)
}

const handleCreatePolicy = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    name: '',
    dataType: '',
    storageTier: 'Hot',
    retentionValue: 365,
    retentionUnit: 'Days',
    action: 'delete',
    archiveTarget: '',
    aggregationLevel: 'Daily',
    description: ''
  })
  dialogVisible.value = true
}

const viewPolicy = (policy: any) => {
  currentPolicy.value = policy
  detailsDialogVisible.value = true
}

const editPolicy = (policy: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, policy)
  dialogVisible.value = true
}

const runCleanup = (policy: any) => {
  cleanupTarget.value = policy
  cleanupDialogVisible.value = true
}

const confirmCleanup = () => {
  if (cleanupTarget.value) {
    ElMessage.info(`Running cleanup for policy "${cleanupTarget.value.name}"...`)
    setTimeout(() => {
      ElMessage.success(`Cleanup completed for "${cleanupTarget.value.name}"`)
      cleanupDialogVisible.value = false
      cleanupTarget.value = null
    }, 3000)
  }
}

const deletePolicy = (policy: any) => {
  deleteTarget.value = policy
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = retentionPolicies.value.findIndex(p => p.id === deleteTarget.value!.id)
    if (index !== -1) {
      retentionPolicies.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.name}`)
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      const retentionPeriod = `${formData.retentionValue} ${formData.retentionUnit}`
      if (dialogMode.value === 'create') {
        const newPolicy = {
          id: Date.now(),
          ...formData,
          retentionPeriod,
          currentSize: '0 TB',
          status: 'pending',
          nextCleanup: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 19).replace('T', ' '),
          description: formData.description
        }
        retentionPolicies.value.unshift(newPolicy)
        ElMessage.success('Policy created successfully')
      } else {
        const index = retentionPolicies.value.findIndex(p => p.id === formData.id)
        if (index !== -1) {
          retentionPolicies.value[index] = { ...retentionPolicies.value[index], ...formData, retentionPeriod }
          ElMessage.success('Policy updated successfully')
        }
      }
      dialogVisible.value = false
      formRef.value?.resetFields()
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
    initStorageChart()
    initAgeChart()
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
      fetchPolicies()
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
.retention-policy-page {
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

.policy-details {
  .cleanup-history {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
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