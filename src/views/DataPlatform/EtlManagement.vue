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
        <div class="loading-tip">ETL Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="etl-management-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>ETL Management</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>ETL Management</h1>
        <p class="description">Design, schedule, and monitor data pipeline jobs for extraction, transformation, and loading</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Jobs
        </el-button>
        <el-button type="primary" @click="handleCreateJob">
          <el-icon><Plus /></el-icon>
          Create Pipeline
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

    <!-- Pipeline Status Overview -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="jobs-chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Job Execution Trend</span>
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
        <el-card class="status-chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Job Status Distribution</span>
            </div>
          </template>
          <div ref="statusChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by job name or description"
              prefix-icon="Search"
              clearable
              style="width: 240px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Running" value="Running" />
            <el-option label="Succeeded" value="Succeeded" />
            <el-option label="Failed" value="Failed" />
            <el-option label="Scheduled" value="Scheduled" />
          </el-select>
          <el-select v-model="filters.type" placeholder="Type" clearable style="width: 130px">
            <el-option label="Batch" value="Batch" />
            <el-option label="Streaming" value="Streaming" />
            <el-option label="Incremental" value="Incremental" />
          </el-select>
          <el-select v-model="filters.priority" placeholder="Priority" clearable style="width: 110px">
            <el-option label="High" value="High" />
            <el-option label="Medium" value="Medium" />
            <el-option label="Low" value="Low" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- ETL Jobs Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>ETL Pipelines ({{ filteredJobs.length }} jobs)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchJobs" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedJobs" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Job Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'Streaming' ? 'success' : 'primary'" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="Source" width="150" show-overflow-tooltip />
        <el-table-column prop="target" label="Target" width="150" show-overflow-tooltip />
        <el-table-column prop="records" label="Records" width="110" align="right">
          <template #default="{ row }">
            {{ row.records?.toLocaleString() || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="Duration" width="90" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              <el-icon v-if="row.status === 'Running'" class="is-loading"><Loading /></el-icon>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastRun" label="Last Run" width="160" />
        <el-table-column prop="nextRun" label="Next Run" width="160" />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="runJob(row)">Run</el-button>
            <el-button link type="success" size="small" @click="viewJobDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="editJob(row)">Edit</el-button>
            <el-button link type="danger" size="small" @click="deleteJob(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredJobs.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Create/Edit Job Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'create' ? 'Create ETL Pipeline' : 'Edit ETL Pipeline'" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Job Name" prop="name">
              <el-input v-model="formData.name" placeholder="Enter job name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Job Type" prop="type">
              <el-select v-model="formData.type" placeholder="Select type" style="width: 100%">
                <el-option label="Batch" value="Batch" />
                <el-option label="Streaming" value="Streaming" />
                <el-option label="Incremental" value="Incremental" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Priority" prop="priority">
              <el-select v-model="formData.priority" placeholder="Select priority" style="width: 100%">
                <el-option label="High" value="High" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Low" value="Low" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Schedule" prop="schedule">
              <el-select v-model="formData.schedule" placeholder="Select schedule" style="width: 100%">
                <el-option label="Every hour" value="0 * * * *" />
                <el-option label="Every 6 hours" value="0 */6 * * *" />
                <el-option label="Daily at 1am" value="0 1 * * *" />
                <el-option label="Weekly on Sunday" value="0 2 * * 0" />
                <el-option label="Monthly on 1st" value="0 3 1 * *" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Source" prop="source">
              <el-select v-model="formData.source" placeholder="Select source" style="width: 100%">
                <el-option label="PostgreSQL Main DB" value="PostgreSQL Main DB" />
                <el-option label="Kafka Stream" value="Kafka Stream" />
                <el-option label="IoT Gateway" value="IoT Gateway" />
                <el-option label="S3 Bucket" value="S3 Bucket" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Target" prop="target">
              <el-select v-model="formData.target" placeholder="Select target" style="width: 100%">
                <el-option label="Data Lake" value="Data Lake" />
                <el-option label="Data Warehouse" value="Data Warehouse" />
                <el-option label="Kafka Topic" value="Kafka Topic" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Transformations" prop="transformations">
              <el-select v-model="formData.transformations" multiple placeholder="Select transformations" style="width: 100%">
                <el-option label="Data Cleaning" value="Data Cleaning" />
                <el-option label="Schema Mapping" value="Schema Mapping" />
                <el-option label="Aggregation" value="Aggregation" />
                <el-option label="Data Enrichment" value="Data Enrichment" />
                <el-option label="Deduplication" value="Deduplication" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter job description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save Pipeline</el-button>
      </template>
    </el-dialog>

    <!-- Job Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="currentJob?.name" width="750px" destroy-on-close>
      <div class="job-details" v-if="currentJob">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Job ID">{{ currentJob.id }}</el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="currentJob.type === 'Streaming' ? 'success' : 'primary'" size="small">{{ currentJob.type }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentJob.status)" size="small">{{ currentJob.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTag(currentJob.priority)" size="small">{{ currentJob.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Source">{{ currentJob.source }}</el-descriptions-item>
          <el-descriptions-item label="Target">{{ currentJob.target }}</el-descriptions-item>
          <el-descriptions-item label="Schedule">{{ currentJob.scheduleDisplay || currentJob.schedule }}</el-descriptions-item>
          <el-descriptions-item label="Last Run">{{ currentJob.lastRun }}</el-descriptions-item>
          <el-descriptions-item label="Duration">{{ currentJob.duration }}</el-descriptions-item>
          <el-descriptions-item label="Records Processed">{{ currentJob.records?.toLocaleString() || '-' }}</el-descriptions-item>
          <el-descriptions-item label="Next Run">{{ currentJob.nextRun }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentJob.description || 'No description' }}</el-descriptions-item>
        </el-descriptions>

        <div class="job-metrics" v-if="currentJob.metrics">
          <h4>Execution Metrics</h4>
          <el-row :gutter="16">
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ currentJob.metrics.throughput || 'N/A' }}</div>
                <div class="metric-label">Throughput (rec/s)</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ currentJob.metrics.errorRate || '0%' }}</div>
                <div class="metric-label">Error Rate</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ currentJob.metrics.cpu || '0%' }}</div>
                <div class="metric-label">CPU Usage</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="metric-card">
                <div class="metric-value">{{ currentJob.metrics.memory || '0 MB' }}</div>
                <div class="metric-label">Memory Usage</div>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="job-history" v-if="currentJob.executionHistory">
          <h4>Execution History</h4>
          <el-table :data="currentJob.executionHistory" size="small" border>
            <el-table-column prop="startTime" label="Start Time" width="160" />
            <el-table-column prop="endTime" label="End Time" width="160" />
            <el-table-column prop="duration" label="Duration" width="100" />
            <el-table-column prop="records" label="Records" width="120" />
            <el-table-column prop="status" label="Status" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="runJob(currentJob)">Run Now</el-button>
      </template>
    </el-dialog>

    <!-- Run Confirmation Dialog -->
    <el-dialog v-model="runDialogVisible" title="Run Pipeline" width="400px">
      <p>Are you sure you want to run pipeline "{{ runTarget?.name }}"?</p>
      <template #footer>
        <el-button @click="runDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmRun">Run Now</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete pipeline "{{ deleteTarget?.name }}"?</p>
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
  Loading
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading ETL jobs...',
  'Checking pipeline status...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const dialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const runDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const currentJob = ref<any>(null)
const runTarget = ref<any>(null)
const deleteTarget = ref<any>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)
const trendPeriod = ref('daily')

const filters = reactive({
  keyword: '',
  status: '',
  type: '',
  priority: ''
})

const formData = reactive({
  name: '',
  type: 'Batch',
  priority: 'Medium',
  schedule: '0 1 * * *',
  source: '',
  target: '',
  transformations: [] as string[],
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter job name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select job type', trigger: 'change' }],
  source: [{ required: true, message: 'Please select source', trigger: 'change' }],
  target: [{ required: true, message: 'Please select target', trigger: 'change' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Jobs', value: 28, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Running', value: 6, trend: -2, icon: 'Loading', bgColor: '#e6a23c', key: 'running' },
  { title: 'Succeeded (24h)', value: 156, trend: 18, icon: 'Checked', bgColor: '#67c23a', key: 'succeeded' },
  { title: 'Failed (24h)', value: 8, trend: -25, icon: 'TrendCharts', bgColor: '#f56c6c', key: 'failed' }
])

const etlJobs = ref([
  {
    id: 1,
    name: 'IoT Sensor Data Ingestion',
    type: 'Streaming',
    source: 'Kafka Stream',
    target: 'Data Lake',
    records: 1250000,
    duration: '00:02:35',
    status: 'Running',
    priority: 'High',
    lastRun: '2024-01-20 10:30:00',
    nextRun: 'Continuous',
    schedule: 'Continuous',
    scheduleDisplay: 'Continuous Streaming',
    description: 'Real-time ingestion of IoT sensor data from Kafka to data lake',
    metrics: {
      throughput: '8,234 rec/s',
      errorRate: '0.02%',
      cpu: '45%',
      memory: '2.4 GB'
    },
    executionHistory: [
      { startTime: '2024-01-20 10:30:00', endTime: '2024-01-20 10:32:35', duration: '00:02:35', records: 1250000, status: 'Succeeded' },
      { startTime: '2024-01-20 10:00:00', endTime: '2024-01-20 10:02:28', duration: '00:02:28', records: 1180000, status: 'Succeeded' }
    ]
  },
  {
    id: 2,
    name: 'Daily Energy Aggregation',
    type: 'Batch',
    source: 'PostgreSQL Main DB',
    target: 'Data Warehouse',
    records: 345000,
    duration: '00:15:42',
    status: 'Succeeded',
    priority: 'High',
    lastRun: '2024-01-20 01:15:42',
    nextRun: '2024-01-21 01:00:00',
    schedule: '0 1 * * *',
    scheduleDisplay: 'Daily at 1am',
    description: 'Daily aggregation of energy consumption data',
    metrics: {
      throughput: '23,456 rec/s',
      errorRate: '0%',
      cpu: '32%',
      memory: '1.2 GB'
    },
    executionHistory: [
      { startTime: '2024-01-20 01:00:00', endTime: '2024-01-20 01:15:42', duration: '00:15:42', records: 345000, status: 'Succeeded' },
      { startTime: '2024-01-19 01:00:00', endTime: '2024-01-19 01:14:58', duration: '00:14:58', records: 332000, status: 'Succeeded' }
    ]
  },
  {
    id: 3,
    name: 'Device Data Enrichment',
    type: 'Batch',
    source: 'Data Lake',
    target: 'Data Lake',
    records: 89000,
    duration: '00:08:23',
    status: 'Succeeded',
    priority: 'Medium',
    lastRun: '2024-01-20 03:08:23',
    nextRun: '2024-01-21 03:00:00',
    schedule: '0 3 * * *',
    scheduleDisplay: 'Daily at 3am',
    description: 'Enrich device data with location and metadata',
    executionHistory: [
      { startTime: '2024-01-20 03:00:00', endTime: '2024-01-20 03:08:23', duration: '00:08:23', records: 89000, status: 'Succeeded' }
    ]
  },
  {
    id: 4,
    name: 'Customer Data Sync',
    type: 'Incremental',
    source: 'PostgreSQL Main DB',
    target: 'Data Warehouse',
    records: 12500,
    duration: '00:03:15',
    status: 'Running',
    priority: 'High',
    lastRun: '2024-01-20 11:45:00',
    nextRun: '2024-01-20 12:00:00',
    schedule: '0 * * * *',
    scheduleDisplay: 'Every hour',
    description: 'Incremental sync of customer data changes',
    metrics: {
      throughput: '12,345 rec/s',
      errorRate: '0%',
      cpu: '18%',
      memory: '512 MB'
    },
    executionHistory: [
      { startTime: '2024-01-20 11:00:00', endTime: '2024-01-20 11:03:15', duration: '00:03:15', records: 12500, status: 'Succeeded' }
    ]
  },
  {
    id: 5,
    name: 'Temperature Anomaly Detection',
    type: 'Streaming',
    source: 'Kafka Stream',
    target: 'Kafka Topic',
    records: 456000,
    duration: '00:01:48',
    status: 'Running',
    priority: 'Medium',
    lastRun: '2024-01-20 10:00:00',
    nextRun: 'Continuous',
    schedule: 'Continuous',
    scheduleDisplay: 'Continuous Streaming',
    description: 'Real-time anomaly detection on temperature readings',
    metrics: {
      throughput: '4,567 rec/s',
      errorRate: '0.05%',
      cpu: '28%',
      memory: '1.8 GB'
    }
  },
  {
    id: 6,
    name: 'Weekly Report Generation',
    type: 'Batch',
    source: 'Data Warehouse',
    target: 'File System',
    records: 0,
    duration: '00:25:30',
    status: 'Succeeded',
    priority: 'Low',
    lastRun: '2024-01-19 02:25:30',
    nextRun: '2024-01-26 02:00:00',
    schedule: '0 2 * * 0',
    scheduleDisplay: 'Weekly on Sunday at 2am',
    description: 'Generate weekly operational reports',
    executionHistory: [
      { startTime: '2024-01-19 02:00:00', endTime: '2024-01-19 02:25:30', duration: '00:25:30', records: 0, status: 'Succeeded' }
    ]
  },
  {
    id: 7,
    name: 'ESG Data Processing',
    type: 'Batch',
    source: 'PostgreSQL Main DB',
    target: 'Data Warehouse',
    records: 25600,
    duration: '00:05:22',
    status: 'Failed',
    priority: 'High',
    lastRun: '2024-01-20 04:05:22',
    nextRun: '2024-01-21 04:00:00',
    schedule: '0 4 * * *',
    scheduleDisplay: 'Daily at 4am',
    description: 'Process ESG metrics and carbon footprint data',
    metrics: {
      throughput: '0 rec/s',
      errorRate: '100%',
      cpu: '0%',
      memory: '0 MB'
    },
    executionHistory: [
      { startTime: '2024-01-20 04:00:00', endTime: '2024-01-20 04:05:22', duration: '00:05:22', records: 0, status: 'Failed' }
    ]
  }
])

// ==================== Computed ====================
const filteredJobs = computed(() => {
  let filtered = [...etlJobs.value]

  if (filters.keyword) {
    filtered = filtered.filter(j =>
        j.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        j.description?.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.status) {
    filtered = filtered.filter(j => j.status === filters.status)
  }

  if (filters.type) {
    filtered = filtered.filter(j => j.type === filters.type)
  }

  if (filters.priority) {
    filtered = filtered.filter(j => j.priority === filters.priority)
  }

  return filtered
})

const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredJobs.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'Running': 'warning',
    'Succeeded': 'success',
    'Failed': 'danger',
    'Scheduled': 'info'
  }
  return map[status] || 'info'
}

const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = {
    'High': 'danger',
    'Medium': 'warning',
    'Low': 'info'
  }
  return map[priority] || 'info'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const dailySucceeded = [18, 22, 20, 25, 23, 28, 26, 30, 32, 28, 35, 40, 38, 42, 45, 48, 52, 55, 58, 62, 65, 68, 72, 75, 78, 82, 85, 88, 90, 92]
  const dailyFailed = [2, 1, 3, 2, 1, 4, 2, 3, 1, 2, 3, 1, 2, 4, 2, 1, 3, 2, 1, 2, 3, 1, 2, 3, 1, 2, 1, 2, 1, 2]
  const weeklySucceeded = [125, 132, 128, 135, 142, 148, 155, 162, 158, 165, 172, 178]
  const weeklyFailed = [12, 10, 14, 11, 9, 13, 10, 12, 8, 11, 9, 10]

  const succeededData = trendPeriod.value === 'daily' ? dailySucceeded : weeklySucceeded
  const failedData = trendPeriod.value === 'daily' ? dailyFailed : weeklyFailed
  const xAxisData = trendPeriod.value === 'daily'
      ? Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
      : ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Succeeded', 'Failed'], bottom: 0 },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Job Count' },
    series: [
      { name: 'Succeeded', type: 'bar', data: succeededData, itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] } },
      { name: 'Failed', type: 'bar', data: failedData, itemStyle: { color: '#f56c6c', borderRadius: [4, 4, 0, 0] } }
    ]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

const initStatusChart = () => {
  if (!statusChartRef.value) return
  if (statusChart) statusChart.dispose()

  statusChart = echarts.init(statusChartRef.value)

  const runningCount = etlJobs.value.filter(j => j.status === 'Running').length
  const succeededCount = etlJobs.value.filter(j => j.status === 'Succeeded').length
  const failedCount = etlJobs.value.filter(j => j.status === 'Failed').length
  const scheduledCount = etlJobs.value.filter(j => j.status === 'Scheduled').length

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} jobs)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: runningCount, name: 'Running', itemStyle: { color: '#e6a23c' } },
        { value: succeededCount, name: 'Succeeded', itemStyle: { color: '#67c23a' } },
        { value: failedCount, name: 'Failed', itemStyle: { color: '#f56c6c' } },
        { value: scheduledCount, name: 'Scheduled', itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  statusChart.setOption(option)
  window.addEventListener('resize', () => statusChart?.resize())
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
  filters.status = ''
  filters.type = ''
  filters.priority = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredJobs.value.length} job configurations...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchJobs = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Jobs refreshed')
    initStatusChart()
  }, 500)
}

const handleCreateJob = () => {
  dialogMode.value = 'create'
  Object.assign(formData, {
    name: '',
    type: 'Batch',
    priority: 'Medium',
    schedule: '0 1 * * *',
    source: '',
    target: '',
    transformations: [],
    description: ''
  })
  dialogVisible.value = true
}

const editJob = (job: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, job)
  dialogVisible.value = true
}

const viewJobDetails = (job: any) => {
  currentJob.value = job
  detailsDialogVisible.value = true
}

const runJob = (job: any) => {
  runTarget.value = job
  runDialogVisible.value = true
}

const confirmRun = () => {
  if (runTarget.value) {
    ElMessage.success(`Pipeline "${runTarget.value.name}" started`)
    runDialogVisible.value = false
    runTarget.value = null
  }
}

const deleteJob = (job: any) => {
  deleteTarget.value = job
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = etlJobs.value.findIndex(j => j.id === deleteTarget.value!.id)
    if (index !== -1) {
      etlJobs.value.splice(index, 1)
      ElMessage.success(`Deleted: ${deleteTarget.value.name}`)
      initStatusChart()
    }
  }
  deleteDialogVisible.value = false
  deleteTarget.value = null
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'create') {
        const newJob = {
          id: Date.now(),
          ...formData,
          status: 'Scheduled',
          records: 0,
          duration: '00:00:00',
          lastRun: 'Never',
          nextRun: 'Scheduled',
          scheduleDisplay: formData.schedule === '0 1 * * *' ? 'Daily at 1am' : formData.schedule
        }
        etlJobs.value.unshift(newJob)
        ElMessage.success('Pipeline created successfully')
      } else {
        ElMessage.success('Pipeline updated successfully')
      }
      dialogVisible.value = false
      formRef.value?.resetFields()
      initStatusChart()
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
    initStatusChart()
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
      fetchJobs()
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
.etl-management-page {
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

.jobs-chart-card, .status-chart-card {
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

.job-details {
  .job-metrics, .job-history {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .metric-card {
    text-align: center;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .metric-value {
      font-size: 20px;
      font-weight: 600;
      color: #303133;
    }

    .metric-label {
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