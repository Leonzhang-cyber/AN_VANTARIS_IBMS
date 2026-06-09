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
        <div class="loading-tip">Data Sources Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="data-sources-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Sources</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Sources</h1>
        <p class="description">Configure and manage data source connections, protocols, and ingestion settings</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="primary" @click="handleAddSource">
          <el-icon><Plus /></el-icon>
          Add Data Source
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

    <!-- Data Source Type Tabs -->
    <el-card class="type-tabs-card" shadow="hover">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <el-tab-pane label="All Sources" name="all">
          <template #label>
            <span><el-icon><Connection /></el-icon> All Sources</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Databases" name="databases">
          <template #label>
            <span><el-icon><Coin /></el-icon> Databases</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="Message Queues" name="mq">
          <template #label>
            <span><el-icon><Message /></el-icon> Message Queues</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="APIs" name="api">
          <template #label>
            <span><el-icon><Link /></el-icon> APIs</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="IoT Protocols" name="iot">
          <template #label>
            <span><el-icon><Connection /></el-icon> IoT Protocols</span>
          </template>
        </el-tab-pane>
        <el-tab-pane label="File Systems" name="files">
          <template #label>
            <span><el-icon><Folder /></el-icon> File Systems</span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- Filters -->
    <el-card class="filter-card" shadow="hover">
      <div class="filter-container">
        <div class="filter-row">
          <el-input
              v-model="filters.keyword"
              placeholder="Search by name or connection string"
              prefix-icon="Search"
              clearable
              style="width: 260px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
          />
          <el-select v-model="filters.status" placeholder="Status" clearable style="width: 120px">
            <el-option label="Connected" value="Connected" />
            <el-option label="Disconnected" value="Disconnected" />
            <el-option label="Error" value="Error" />
          </el-select>
          <el-select v-model="filters.protocol" placeholder="Protocol" clearable style="width: 140px">
            <el-option label="PostgreSQL" value="PostgreSQL" />
            <el-option label="MySQL" value="MySQL" />
            <el-option label="Kafka" value="Kafka" />
            <el-option label="REST API" value="REST API" />
            <el-option label="MQTT" value="MQTT" />
            <el-option label="OPC-UA" value="OPC-UA" />
          </el-select>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleResetFilters">Reset</el-button>
        </div>
      </div>
    </el-card>

    <!-- Data Sources Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Data Sources ({{ filteredSources.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchSources" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedSources" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Name" width="180" show-overflow-tooltip />
        <el-table-column prop="type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="protocol" label="Protocol" width="120" />
        <el-table-column prop="connectionString" label="Connection String" min-width="220" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">
              <el-icon><component :is="row.status === 'Connected' ? 'CircleCheck' : (row.status === 'Error' ? 'CircleClose' : 'Clock')" /></el-icon>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataPoints" label="Data Points" width="110" align="center" />
        <el-table-column prop="throughput" label="Throughput" width="100" />
        <el-table-column prop="lastIngestion" label="Last Ingestion" width="160" />
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="success" size="small" @click="editSource(row)">Edit</el-button>
            <el-button link type="info" size="small" @click="viewMetrics(row)">Metrics</el-button>
            <el-button link type="danger" size="small" @click="deleteSource(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredSources.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Add/Edit Data Source Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'add' ? 'Add Data Source' : 'Edit Data Source'" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="130px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Source Name" prop="name">
              <el-input v-model="formData.name" placeholder="Enter data source name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Source Type" prop="type">
              <el-select v-model="formData.type" placeholder="Select type" style="width: 100%">
                <el-option label="Database" value="Database" />
                <el-option label="Message Queue" value="Message Queue" />
                <el-option label="API" value="API" />
                <el-option label="IoT Gateway" value="IoT Gateway" />
                <el-option label="File System" value="File System" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Protocol" prop="protocol">
              <el-select v-model="formData.protocol" placeholder="Select protocol" style="width: 100%">
                <el-option label="PostgreSQL" value="PostgreSQL" />
                <el-option label="MySQL" value="MySQL" />
                <el-option label="MongoDB" value="MongoDB" />
                <el-option label="Kafka" value="Kafka" />
                <el-option label="REST API" value="REST API" />
                <el-option label="WebSocket" value="WebSocket" />
                <el-option label="MQTT" value="MQTT" />
                <el-option label="OPC-UA" value="OPC-UA" />
                <el-option label="Modbus" value="Modbus" />
                <el-option label="BACnet" value="BACnet" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Ingestion Interval" prop="interval">
              <el-select v-model="formData.interval" placeholder="Select interval" style="width: 100%">
                <el-option label="Real-time (Streaming)" value="Streaming" />
                <el-option label="Every 5 seconds" value="5s" />
                <el-option label="Every 30 seconds" value="30s" />
                <el-option label="Every 1 minute" value="1m" />
                <el-option label="Every 5 minutes" value="5m" />
                <el-option label="Every 1 hour" value="1h" />
                <el-option label="Daily" value="1d" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Connection String / URL" prop="connectionString">
              <el-input v-model="formData.connectionString" placeholder="jdbc:postgresql://localhost:5432/dbname or https://api.example.com" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Username" prop="username">
              <el-input v-model="formData.username" placeholder="Username" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Password" prop="password">
              <el-input v-model="formData.password" type="password" placeholder="Password" show-password />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max Connections" prop="maxConnections">
              <el-input-number v-model="formData.maxConnections" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Timeout (seconds)" prop="timeout">
              <el-input-number v-model="formData.timeout" :min="1" :max="300" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item label="Description" prop="description">
              <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testConnectionBeforeSave">Test Connection</el-button>
        <el-button type="success" @click="submitForm">Save Source</el-button>
      </template>
    </el-dialog>

    <!-- Metrics Dialog -->
    <el-dialog v-model="metricsDialogVisible" title="Data Source Metrics" width="700px" destroy-on-close>
      <div class="metrics-container" v-if="selectedSource">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Source Name">{{ selectedSource.name }}</el-descriptions-item>
          <el-descriptions-item label="Type">{{ selectedSource.type }}</el-descriptions-item>
          <el-descriptions-item label="Protocol">{{ selectedSource.protocol }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(selectedSource.status)" size="small">{{ selectedSource.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Data Points">{{ selectedSource.dataPoints }}</el-descriptions-item>
          <el-descriptions-item label="Throughput">{{ selectedSource.throughput }}</el-descriptions-item>
          <el-descriptions-item label="Last Ingestion">{{ selectedSource.lastIngestion }}</el-descriptions-item>
          <el-descriptions-item label="Uptime">{{ selectedSource.uptime || '99.95%' }}</el-descriptions-item>
        </el-descriptions>

        <div class="metrics-chart">
          <h4>Ingestion Rate (last 24 hours)</h4>
          <div ref="metricsChartRef" class="metrics-chart-container"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="metricsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="refreshMetrics">Refresh</el-button>
      </template>
    </el-dialog>

    <!-- Test Connection Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div :class="testResult.success ? 'test-success' : 'test-failure'">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}</p>
          <p><strong>Data Source Version:</strong> {{ testResult.details.version }}</p>
          <p><strong>Available Tables/Streams:</strong> {{ testResult.details.tableCount }}</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog v-model="deleteDialogVisible" title="Confirm Delete" width="400px">
      <p>Are you sure you want to delete data source "{{ deleteTarget?.name }}"?</p>
      <p style="color: #f56c6c; font-size: 12px; margin-top: 8px">This action cannot be undone and will stop all data ingestion from this source.</p>
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
  Connection, Coin, Message, Link, Folder, CircleCheck, CircleClose
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading data sources...',
  'Checking connections...',
  'Almost ready...'
]

// ==================== Chart References ====================
const metricsChartRef = ref<HTMLElement>()
let metricsChart: echarts.ECharts | null = null

// ==================== State ====================
const activeTab = ref('all')
const tableLoading = ref(false)
const dialogVisible = ref(false)
const metricsDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedSource = ref<any>(null)
const deleteTarget = ref<any>(null)
const deleteDialogVisible = ref(false)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)

const filters = reactive({
  keyword: '',
  status: '',
  protocol: ''
})

const testResult = reactive({
  success: false,
  message: '',
  details: null as any
})

const formData = reactive({
  name: '',
  type: '',
  protocol: '',
  connectionString: '',
  username: '',
  password: '',
  maxConnections: 10,
  timeout: 30,
  interval: '1m',
  description: ''
})

const formRules = {
  name: [{ required: true, message: 'Please enter source name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select source type', trigger: 'change' }],
  protocol: [{ required: true, message: 'Please select protocol', trigger: 'change' }],
  connectionString: [{ required: true, message: 'Please enter connection string', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Sources', value: 24, trend: 12, icon: 'Connection', bgColor: '#409eff', key: 'total' },
  { title: 'Active Sources', value: 18, trend: 8, icon: 'CircleCheck', bgColor: '#67c23a', key: 'active' },
  { title: 'Data Points/sec', value: '12.4K', trend: 15, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'throughput' },
  { title: 'Total Storage', value: '156 TB', trend: 22, icon: 'Document', bgColor: '#f56c6c', key: 'storage' }
])

const dataSources = ref([
  {
    id: 1,
    name: 'PostgreSQL Main DB',
    type: 'Database',
    protocol: 'PostgreSQL',
    connectionString: 'jdbc:postgresql://db.example.com:5432/ibms_main',
    status: 'Connected',
    dataPoints: '2,345,678',
    throughput: '1,234/s',
    lastIngestion: '2024-01-20 15:30:00',
    uptime: '99.99%'
  },
  {
    id: 2,
    name: 'Kafka Events Stream',
    type: 'Message Queue',
    protocol: 'Kafka',
    connectionString: 'kafka://kafka.example.com:9092',
    status: 'Connected',
    dataPoints: '8,765,432',
    throughput: '5,678/s',
    lastIngestion: '2024-01-20 15:30:05',
    uptime: '99.95%'
  },
  {
    id: 3,
    name: 'IoT Sensor Gateway',
    type: 'IoT Gateway',
    protocol: 'MQTT',
    connectionString: 'mqtt://mqtt.example.com:1883',
    status: 'Connected',
    dataPoints: '3,456,789',
    throughput: '890/s',
    lastIngestion: '2024-01-20 15:29:58',
    uptime: '99.98%'
  },
  {
    id: 4,
    name: 'REST API - Weather Service',
    type: 'API',
    protocol: 'REST API',
    connectionString: 'https://api.weather.com/v1/forecast',
    status: 'Connected',
    dataPoints: '123,456',
    throughput: '45/s',
    lastIngestion: '2024-01-20 15:30:00',
    uptime: '99.90%'
  },
  {
    id: 5,
    name: 'MySQL Timeseries DB',
    type: 'Database',
    protocol: 'MySQL',
    connectionString: 'jdbc:mysql://mysql.example.com:3306/timeseries',
    status: 'Disconnected',
    dataPoints: '0',
    throughput: '0/s',
    lastIngestion: '2024-01-19 23:45:00',
    uptime: '99.85%'
  },
  {
    id: 6,
    name: 'OPC-UA Factory Server',
    type: 'IoT Gateway',
    protocol: 'OPC-UA',
    connectionString: 'opc.tcp://factory.example.com:4840',
    status: 'Error',
    dataPoints: '0',
    throughput: '0/s',
    lastIngestion: '2024-01-20 14:20:00',
    uptime: '98.50%'
  },
  {
    id: 7,
    name: 'MongoDB Document Store',
    type: 'Database',
    protocol: 'MongoDB',
    connectionString: 'mongodb://mongo.example.com:27017/ibms',
    status: 'Connected',
    dataPoints: '1,234,567',
    throughput: '567/s',
    lastIngestion: '2024-01-20 15:29:55',
    uptime: '99.97%'
  },
  {
    id: 8,
    name: 'WebSocket Real-time Feed',
    type: 'API',
    protocol: 'WebSocket',
    connectionString: 'ws://ws.example.com:8080/feed',
    status: 'Connected',
    dataPoints: '987,654',
    throughput: '234/s',
    lastIngestion: '2024-01-20 15:30:00',
    uptime: '99.92%'
  },
  {
    id: 9,
    name: 'BACnet Building Controller',
    type: 'IoT Gateway',
    protocol: 'BACnet',
    connectionString: 'bacnet://192.168.1.100:47808',
    status: 'Connected',
    dataPoints: '456,789',
    throughput: '123/s',
    lastIngestion: '2024-01-20 15:29:50',
    uptime: '99.88%'
  },
  {
    id: 10,
    name: 'Modbus PLC Gateway',
    type: 'IoT Gateway',
    protocol: 'Modbus',
    connectionString: 'modbus://192.168.1.50:502',
    status: 'Connected',
    dataPoints: '234,567',
    throughput: '67/s',
    lastIngestion: '2024-01-20 15:29:52',
    uptime: '99.91%'
  }
])

// ==================== Computed ====================
const filteredSources = computed(() => {
  let filtered = [...dataSources.value]

  // Filter by tab
  if (activeTab.value === 'databases') {
    filtered = filtered.filter(s => s.type === 'Database')
  } else if (activeTab.value === 'mq') {
    filtered = filtered.filter(s => s.type === 'Message Queue')
  } else if (activeTab.value === 'api') {
    filtered = filtered.filter(s => s.type === 'API')
  } else if (activeTab.value === 'iot') {
    filtered = filtered.filter(s => s.type === 'IoT Gateway')
  }

  // Filter by search
  if (filters.keyword) {
    filtered = filtered.filter(s =>
        s.name.toLowerCase().includes(filters.keyword.toLowerCase()) ||
        s.connectionString.toLowerCase().includes(filters.keyword.toLowerCase())
    )
  }

  if (filters.status) {
    filtered = filtered.filter(s => s.status === filters.status)
  }

  if (filters.protocol) {
    filtered = filtered.filter(s => s.protocol === filters.protocol)
  }

  return filtered
})

const paginatedSources = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredSources.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getTypeTag = (type: string): string => {
  const map: Record<string, string> = {
    'Database': 'primary',
    'Message Queue': 'success',
    'API': 'warning',
    'IoT Gateway': 'info',
    'File System': 'danger'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string): string => {
  const map: Record<string, string> = {
    'Connected': 'success',
    'Disconnected': 'info',
    'Error': 'danger'
  }
  return map[status] || 'info'
}

// ==================== Chart Initialization ====================
const initMetricsChart = () => {
  if (!metricsChartRef.value) return
  if (metricsChart) metricsChart.dispose()

  metricsChart = echarts.init(metricsChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Array.from({ length: 24 }, (_, i) => `${i}:00`) },
    yAxis: { type: 'value', name: 'Records/sec' },
    series: [{
      type: 'line',
      data: [1200, 1250, 1180, 1220, 1350, 1400, 1450, 1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000, 1950, 1900, 1850, 1800, 1750, 1700],
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 }
    }]
  }

  metricsChart.setOption(option)
  window.addEventListener('resize', () => metricsChart?.resize())
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
  filters.protocol = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredSources.value.length} data source configurations...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const handleTabChange = () => {
  currentPage.value = 1
}

const fetchSources = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const handleAddSource = () => {
  dialogMode.value = 'add'
  Object.assign(formData, {
    name: '',
    type: '',
    protocol: '',
    connectionString: '',
    username: '',
    password: '',
    maxConnections: 10,
    timeout: 30,
    interval: '1m',
    description: ''
  })
  dialogVisible.value = true
}

const editSource = (source: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, source)
  dialogVisible.value = true
}

const testConnection = (source: any) => {
  ElMessage.info(`Testing connection to ${source.name}...`)
  setTimeout(() => {
    testResult.success = source.status === 'Connected'
    testResult.message = source.status === 'Connected'
        ? 'Successfully connected to data source'
        : `Connection failed: ${source.status === 'Error' ? 'Authentication failed' : 'Connection timeout'}`
    testResult.details = source.status === 'Connected' ? {
      responseTime: '45ms',
      version: source.protocol === 'PostgreSQL' ? '14.5' : '2.0',
      tableCount: 42
    } : null
    testDialogVisible.value = true
  }, 1000)
}

const testConnectionBeforeSave = () => {
  ElMessage.info('Testing connection...')
  setTimeout(() => {
    testResult.success = true
    testResult.message = 'Successfully connected to data source'
    testResult.details = {
      responseTime: '52ms',
      version: '1.0',
      tableCount: 0
    }
    testDialogVisible.value = true
  }, 1000)
}

const viewMetrics = (source: any) => {
  selectedSource.value = source
  metricsDialogVisible.value = true
  nextTick(() => {
    initMetricsChart()
  })
}

const refreshMetrics = () => {
  initMetricsChart()
  ElMessage.success('Metrics refreshed')
}

const deleteSource = (source: any) => {
  deleteTarget.value = source
  deleteDialogVisible.value = true
}

const confirmDelete = () => {
  if (deleteTarget.value) {
    const index = dataSources.value.findIndex(s => s.id === deleteTarget.value!.id)
    if (index !== -1) {
      dataSources.value.splice(index, 1)
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
      if (dialogMode.value === 'add') {
        const newSource = {
          id: Date.now(),
          ...formData,
          status: 'Connected',
          dataPoints: '0',
          throughput: '0/s',
          lastIngestion: new Date().toLocaleString()
        }
        dataSources.value.unshift(newSource)
        ElMessage.success('Data source added successfully')
      } else {
        const index = dataSources.value.findIndex(s => s.id === formData.id)
        if (index !== -1) {
          dataSources.value[index] = { ...dataSources.value[index], ...formData }
          ElMessage.success('Data source updated successfully')
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
      fetchSources()
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
.data-sources-page {
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

.type-tabs-card {
  margin-bottom: 20px;
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

.metrics-container {
  .metrics-chart {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }
}

.metrics-chart-container {
  width: 100%;
  height: 300px;
}

.test-success, .test-failure {
  text-align: center;
}

.test-details {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  text-align: left;

  p {
    margin: 8px 0;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>