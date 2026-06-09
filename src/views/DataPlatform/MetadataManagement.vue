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
        <div class="loading-tip">Metadata Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="metadata-management-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Metadata Management</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Metadata Management</h1>
        <p class="description">Centralized metadata repository for data assets, business terms, and lineage tracking</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Metadata
        </el-button>
        <el-button type="primary" @click="handleAddMetadata">
          <el-icon><Plus /></el-icon>
          Add Metadata
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

    <!-- Metadata Overview Charts -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Metadata Growth Trend</span>
              <el-radio-group v-model="growthPeriod" size="small">
                <el-radio-button value="weekly">Weekly</el-radio-button>
                <el-radio-button value="monthly">Monthly</el-radio-button>
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
              <span>Metadata by Type</span>
            </div>
          </template>
          <div ref="typeChartRef" class="pie-chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Search & Filter -->
    <el-card class="search-card" shadow="hover">
      <div class="search-container">
        <el-input
            v-model="searchKeyword"
            placeholder="Search metadata by name, description, or owner..."
            prefix-icon="Search"
            size="large"
            clearable
            style="flex: 1"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
        />
        <el-button type="primary" size="large" @click="handleSearch">Search</el-button>
        <el-button size="large" @click="showAdvancedFilters = !showAdvancedFilters">
          <el-icon><Filter /></el-icon>
          Advanced
        </el-button>
      </div>

      <el-collapse-transition>
        <div v-show="showAdvancedFilters" class="advanced-filters">
          <el-divider />
          <el-row :gutter="20">
            <el-col :span="6">
              <el-select v-model="filters.entityType" placeholder="Entity Type" clearable style="width: 100%">
                <el-option label="Table" value="Table" />
                <el-option label="Column" value="Column" />
                <el-option label="Business Term" value="Business Term" />
                <el-option label="Data Source" value="Data Source" />
                <el-option label="ETL Job" value="ETL Job" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.domain" placeholder="Domain" clearable style="width: 100%">
                <el-option label="Operations" value="Operations" />
                <el-option label="Finance" value="Finance" />
                <el-option label="Energy" value="Energy" />
                <el-option label="ESG" value="ESG" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.status" placeholder="Status" clearable style="width: 100%">
                <el-option label="Active" value="Active" />
                <el-option label="Deprecated" value="Deprecated" />
                <el-option label="Draft" value="Draft" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.owner" placeholder="Owner" clearable style="width: 100%">
                <el-option label="John Smith" value="John Smith" />
                <el-option label="Sarah Chen" value="Sarah Chen" />
                <el-option label="David Wang" value="David Wang" />
              </el-select>
            </el-col>
          </el-row>
          <div class="filter-actions">
            <el-button type="primary" @click="applyFilters">Apply Filters</el-button>
            <el-button @click="resetFilters">Reset</el-button>
          </div>
        </div>
      </el-collapse-transition>
    </el-card>

    <!-- Main Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Metadata Catalog ({{ filteredMetadata.length }} items)</span>
          <div class="table-actions">
            <el-button :icon="Refresh" @click="fetchMetadata" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedMetadata" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="entityType" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getEntityTypeTag(row.entityType)" size="small">{{ row.entityType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="Domain" width="110" />
        <el-table-column prop="owner" label="Owner" width="130" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="Created" width="120" />
        <el-table-column prop="updatedAt" label="Updated" width="120" />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">View</el-button>
            <el-button link type="success" size="small" @click="editMetadata(row)">Edit</el-button>
            <el-button link type="info" size="small" @click="viewLineage(row)">Lineage</el-button>
            <el-button link type="danger" size="small" @click="deleteMetadata(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredMetadata.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Metadata Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="currentMetadata?.name" width="750px" destroy-on-close>
      <div class="metadata-details" v-if="currentMetadata">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Name">{{ currentMetadata.name }}</el-descriptions-item>
          <el-descriptions-item label="Type">
            <el-tag :type="getEntityTypeTag(currentMetadata.entityType)" size="small">{{ currentMetadata.entityType }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Domain">{{ currentMetadata.domain }}</el-descriptions-item>
          <el-descriptions-item label="Owner">{{ currentMetadata.owner }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusTag(currentMetadata.status)" size="small">{{ currentMetadata.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Version">{{ currentMetadata.version || '1.0' }}</el-descriptions-item>
          <el-descriptions-item label="Created At">{{ currentMetadata.createdAt }}</el-descriptions-item>
          <el-descriptions-item label="Updated At">{{ currentMetadata.updatedAt }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentMetadata.description }}</el-descriptions-item>
        </el-descriptions>

        <!-- Technical Metadata -->
        <div class="metadata-section" v-if="currentMetadata.technicalMetadata">
          <h4>Technical Metadata</h4>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="Schema">{{ currentMetadata.technicalMetadata.schema || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Database">{{ currentMetadata.technicalMetadata.database || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Format">{{ currentMetadata.technicalMetadata.format || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Partition By">{{ currentMetadata.technicalMetadata.partitionBy || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Business Metadata -->
        <div class="metadata-section" v-if="currentMetadata.businessMetadata">
          <h4>Business Metadata</h4>
          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="Business Definition">{{ currentMetadata.businessMetadata.businessDefinition || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Data Classification">{{ currentMetadata.businessMetadata.dataClassification || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Sensitivity">{{ currentMetadata.businessMetadata.sensitivity || '-' }}</el-descriptions-item>
            <el-descriptions-item label="Retention Policy">{{ currentMetadata.businessMetadata.retentionPolicy || '-' }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Tags -->
        <div class="metadata-section" v-if="currentMetadata.tags?.length">
          <h4>Tags</h4>
          <div>
            <el-tag v-for="tag in currentMetadata.tags" :key="tag" size="small" style="margin-right: 8px">{{ tag }}</el-tag>
          </div>
        </div>

        <!-- Lineage -->
        <div class="metadata-section" v-if="currentMetadata.lineage">
          <h4>Data Lineage</h4>
          <div ref="lineageChartRef" class="lineage-chart"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="editMetadata(currentMetadata)">Edit</el-button>
      </template>
    </el-dialog>

    <!-- Add/Edit Metadata Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogMode === 'add' ? 'Add Metadata' : 'Edit Metadata'" width="600px" destroy-on-close>
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="120px">
        <el-form-item label="Name" prop="name">
          <el-input v-model="formData.name" placeholder="Enter metadata name" />
        </el-form-item>
        <el-form-item label="Entity Type" prop="entityType">
          <el-select v-model="formData.entityType" placeholder="Select type" style="width: 100%">
            <el-option label="Table" value="Table" />
            <el-option label="Column" value="Column" />
            <el-option label="Business Term" value="Business Term" />
            <el-option label="Data Source" value="Data Source" />
            <el-option label="ETL Job" value="ETL Job" />
          </el-select>
        </el-form-item>
        <el-form-item label="Domain" prop="domain">
          <el-select v-model="formData.domain" placeholder="Select domain" style="width: 100%">
            <el-option label="Operations" value="Operations" />
            <el-option label="Finance" value="Finance" />
            <el-option label="Energy" value="Energy" />
            <el-option label="ESG" value="ESG" />
          </el-select>
        </el-form-item>
        <el-form-item label="Owner" prop="owner">
          <el-input v-model="formData.owner" placeholder="Enter owner name" />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-select v-model="formData.status" placeholder="Select status" style="width: 100%">
            <el-option label="Active" value="Active" />
            <el-option label="Deprecated" value="Deprecated" />
            <el-option label="Draft" value="Draft" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Tags" prop="tags">
          <el-select v-model="formData.tags" multiple filterable allow-create default-first-option placeholder="Enter tags" style="width: 100%">
            <el-option label="Critical" value="Critical" />
            <el-option label="Sensitive" value="Sensitive" />
            <el-option label="PII" value="PII" />
            <el-option label="Archived" value="Archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitForm">Save</el-button>
      </template>
    </el-dialog>

    <!-- Lineage Dialog -->
    <el-dialog v-model="lineageDialogVisible" title="Data Lineage" width="800px" destroy-on-close>
      <div class="lineage-container">
        <div ref="lineageDetailChartRef" class="lineage-detail-chart"></div>
      </div>
      <template #footer>
        <el-button @click="lineageDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportLineage">Export</el-button>
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
  Filter, DataAnalysis, Connection, Coin, Loading
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading metadata catalog...',
  'Indexing data assets...',
  'Almost ready...'
]

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
const lineageChartRef = ref<HTMLElement>()
const lineageDetailChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let typeChart: echarts.ECharts | null = null
let lineageChart: echarts.ECharts | null = null
let lineageDetailChart: echarts.ECharts | null = null

// ==================== State ====================
const searchKeyword = ref('')
const showAdvancedFilters = ref(false)
const tableLoading = ref(false)
const detailsDialogVisible = ref(false)
const dialogVisible = ref(false)
const lineageDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const currentMetadata = ref<any>(null)
const formRef = ref()
const currentPage = ref(1)
const pageSize = ref(15)
const growthPeriod = ref('weekly')

const filters = reactive({
  entityType: '',
  domain: '',
  status: '',
  owner: ''
})

const formData = reactive({
  name: '',
  entityType: '',
  domain: '',
  owner: '',
  status: 'Active',
  description: '',
  tags: [] as string[]
})

const formRules = {
  name: [{ required: true, message: 'Please enter name', trigger: 'blur' }],
  entityType: [{ required: true, message: 'Please select entity type', trigger: 'change' }],
  domain: [{ required: true, message: 'Please select domain', trigger: 'change' }],
  owner: [{ required: true, message: 'Please enter owner', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Assets', value: 486, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Active Assets', value: 392, trend: 8, icon: 'Checked', bgColor: '#67c23a', key: 'active' },
  { title: 'Business Terms', value: 86, trend: 15, icon: 'DataAnalysis', bgColor: '#e6a23c', key: 'terms' },
  { title: 'Data Sources', value: 24, trend: 4, icon: 'Connection', bgColor: '#f56c6c', key: 'sources' }
])

const metadataItems = ref([
  {
    id: 1,
    name: 'device_master',
    entityType: 'Table',
    domain: 'Operations',
    owner: 'John Smith',
    status: 'Active',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-20',
    version: '1.2',
    description: 'Master table containing all device information including sensors, controllers, and gateways',
    technicalMetadata: {
      schema: 'public',
      database: 'PostgreSQL Main DB',
      format: 'Parquet',
      partitionBy: 'created_date'
    },
    businessMetadata: {
      businessDefinition: 'Single source of truth for all IoT devices deployed across facilities',
      dataClassification: 'Internal Use',
      sensitivity: 'Medium',
      retentionPolicy: '7 years'
    },
    tags: ['Critical', 'Master Data'],
    lineage: {
      sources: ['IoT Gateway', 'Device Registry'],
      targets: ['energy_consumption', 'device_health']
    }
  },
  {
    id: 2,
    name: 'energy_consumption',
    entityType: 'Table',
    domain: 'Energy',
    owner: 'Lisa Zhang',
    status: 'Active',
    createdAt: '2024-01-12',
    updatedAt: '2024-01-19',
    version: '1.0',
    description: 'Daily energy consumption data by building and device type',
    technicalMetadata: {
      schema: 'analytics',
      database: 'Data Warehouse',
      format: 'Parquet',
      partitionBy: 'date'
    },
    businessMetadata: {
      businessDefinition: 'Energy consumption metrics for ESG reporting and optimization',
      dataClassification: 'Confidential',
      sensitivity: 'High',
      retentionPolicy: '10 years'
    },
    tags: ['Energy', 'ESG', 'Time-series'],
    lineage: {
      sources: ['device_master', 'raw_readings'],
      targets: ['esg_dashboard', 'energy_report']
    }
  },
  {
    id: 3,
    name: 'customer_contract',
    entityType: 'Business Term',
    domain: 'Finance',
    owner: 'Anna Kim',
    status: 'Active',
    createdAt: '2024-01-05',
    updatedAt: '2024-01-18',
    version: '1.1',
    description: 'Customer contract information including terms, pricing, and service level agreements',
    businessMetadata: {
      businessDefinition: 'Legal agreement between company and customer defining service terms',
      dataClassification: 'Highly Confidential',
      sensitivity: 'Critical',
      retentionPolicy: '10 years after contract end'
    },
    tags: ['PII', 'Sensitive', 'Finance'],
    lineage: {
      sources: ['CRM System', 'Contract Management'],
      targets: ['billing', 'customer_360']
    }
  },
  {
    id: 4,
    name: 'esg_carbon_footprint',
    entityType: 'Table',
    domain: 'ESG',
    owner: 'Emily Zhao',
    status: 'Active',
    createdAt: '2024-01-08',
    updatedAt: '2024-01-17',
    version: '2.0',
    description: 'Carbon footprint data across Scope 1, 2, and 3 emissions',
    technicalMetadata: {
      schema: 'esg',
      database: 'Data Warehouse',
      format: 'Parquet',
      partitionBy: 'reporting_period'
    },
    businessMetadata: {
      businessDefinition: 'Greenhouse gas emissions data for regulatory reporting',
      dataClassification: 'Confidential',
      sensitivity: 'High',
      retentionPolicy: 'Permanent'
    },
    tags: ['ESG', 'Carbon', 'Compliance'],
    lineage: {
      sources: ['energy_consumption', 'transportation_logs', 'waste_management'],
      targets: ['esg_report', 'sustainability_dashboard']
    }
  },
  {
    id: 5,
    name: 'maintenance_work_orders',
    entityType: 'Table',
    domain: 'Operations',
    owner: 'Mike Johnson',
    status: 'Active',
    createdAt: '2024-01-15',
    updatedAt: '2024-01-20',
    version: '1.3',
    description: 'Maintenance work order history including preventive and corrective actions',
    technicalMetadata: {
      schema: 'operations',
      database: 'PostgreSQL Main DB',
      format: 'Parquet',
      partitionBy: 'created_date'
    },
    businessMetadata: {
      businessDefinition: 'Historical record of all maintenance activities',
      dataClassification: 'Internal Use',
      sensitivity: 'Medium',
      retentionPolicy: '7 years'
    },
    tags: ['Maintenance', 'Operations'],
    lineage: {
      sources: ['CMMS', 'work_order_system'],
      targets: ['asset_performance', 'maintenance_kpi']
    }
  },
  {
    id: 6,
    name: 'device_status',
    entityType: 'Column',
    domain: 'Operations',
    owner: 'John Smith',
    status: 'Active',
    createdAt: '2024-01-10',
    updatedAt: '2024-01-20',
    version: '1.0',
    description: 'Current operational status of each device (active, maintenance, offline)',
    technicalMetadata: {
      schema: 'public',
      database: 'device_master',
      format: 'String'
    },
    businessMetadata: {
      businessDefinition: 'Real-time status indicator for device health monitoring',
      dataClassification: 'Internal Use',
      sensitivity: 'Low',
      retentionPolicy: '7 years'
    },
    tags: ['Status', 'Monitoring']
  },
  {
    id: 7,
    name: 'PostgreSQL Main DB',
    entityType: 'Data Source',
    domain: 'Operations',
    owner: 'John Smith',
    status: 'Active',
    createdAt: '2024-01-02',
    updatedAt: '2024-01-15',
    version: '14.5',
    description: 'Primary operational database for facility management system',
    technicalMetadata: {
      schema: 'Multiple',
      database: 'postgres',
      format: 'Relational',
      connectionUrl: 'jdbc:postgresql://db.example.com:5432/ibms'
    },
    tags: ['Primary', 'Operational'],
    lineage: {
      targets: ['device_master', 'maintenance_work_orders']
    }
  },
  {
    id: 8,
    name: 'daily_energy_etl',
    entityType: 'ETL Job',
    domain: 'Energy',
    owner: 'Lisa Zhang',
    status: 'Active',
    createdAt: '2024-01-03',
    updatedAt: '2024-01-16',
    version: '2.1',
    description: 'Daily ETL pipeline for energy data aggregation and transformation',
    technicalMetadata: {
      schedule: '0 1 * * *',
      source: 'IoT Gateway',
      target: 'Data Warehouse',
      framework: 'Apache Spark'
    },
    tags: ['ETL', 'Energy', 'Daily'],
    lineage: {
      sources: ['raw_sensor_data'],
      targets: ['energy_consumption']
    }
  }
])

// ==================== Computed ====================
const filteredMetadata = computed(() => {
  let filtered = [...metadataItems.value]

  // Search filter
  if (searchKeyword.value) {
    filtered = filtered.filter(m =>
        m.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
        m.description?.toLowerCase().includes(searchKeyword.value.toLowerCase())
    )
  }

  // Advanced filters
  if (filters.entityType) {
    filtered = filtered.filter(m => m.entityType === filters.entityType)
  }

  if (filters.domain) {
    filtered = filtered.filter(m => m.domain === filters.domain)
  }

  if (filters.status) {
    filtered = filtered.filter(m => m.status === filters.status)
  }

  if (filters.owner) {
    filtered = filtered.filter(m => m.owner === filters.owner)
  }

  return filtered
})

const paginatedMetadata = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredMetadata.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getEntityTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'Table': 'primary',
    'Column': 'info',
    'Business Term': 'success',
    'Data Source': 'warning',
    'ETL Job': 'danger'
  }
  return map[type] || 'info'
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    'Active': 'success',
    'Deprecated': 'danger',
    'Draft': 'info'
  }
  return map[status] || 'info'
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const weeklyData = [12, 15, 18, 22, 25, 28, 32, 35, 38, 42, 45, 48]
  const monthlyData = [48, 52, 58, 65, 72, 78, 85, 92, 98, 105, 112, 118]
  const data = growthPeriod.value === 'weekly' ? weeklyData : monthlyData
  const xAxisData = growthPeriod.value === 'weekly'
      ? ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12']
      : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Metadata Count' },
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
    'Table': metadataItems.value.filter(m => m.entityType === 'Table').length,
    'Column': metadataItems.value.filter(m => m.entityType === 'Column').length,
    'Business Term': metadataItems.value.filter(m => m.entityType === 'Business Term').length,
    'Data Source': metadataItems.value.filter(m => m.entityType === 'Data Source').length,
    'ETL Job': metadataItems.value.filter(m => m.entityType === 'ETL Job').length
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item', formatter: '{b}: {d}% ({c} items)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: typeCount['Table'], name: 'Table', itemStyle: { color: '#409eff' } },
        { value: typeCount['Column'], name: 'Column', itemStyle: { color: '#67c23a' } },
        { value: typeCount['Business Term'], name: 'Business Term', itemStyle: { color: '#e6a23c' } },
        { value: typeCount['Data Source'], name: 'Data Source', itemStyle: { color: '#f56c6c' } },
        { value: typeCount['ETL Job'], name: 'ETL Job', itemStyle: { color: '#909399' } }
      ],
      emphasis: { scale: true },
      label: { show: true, formatter: '{b}: {d}%' }
    }]
  }

  typeChart.setOption(option)
  window.addEventListener('resize', () => typeChart?.resize())
}

const initLineageChart = () => {
  if (!lineageChartRef.value) return
  if (lineageChart) lineageChart.dispose()

  lineageChart = echarts.init(lineageChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'sankey',
      layout: 'none',
      data: [
        { name: 'IoT Gateway' },
        { name: 'Device Registry' },
        { name: 'device_master' },
        { name: 'energy_consumption' },
        { name: 'device_health' }
      ],
      links: [
        { source: 'IoT Gateway', target: 'device_master', value: 1 },
        { source: 'Device Registry', target: 'device_master', value: 1 },
        { source: 'device_master', target: 'energy_consumption', value: 1 },
        { source: 'device_master', target: 'device_health', value: 1 }
      ],
      lineStyle: { color: 'gradient', curveness: 0.5 }
    }]
  }

  lineageChart.setOption(option)
  window.addEventListener('resize', () => lineageChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleSearch = () => {
  currentPage.value = 1
}

const applyFilters = () => {
  currentPage.value = 1
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  filters.entityType = ''
  filters.domain = ''
  filters.status = ''
  filters.owner = ''
  searchKeyword.value = ''
  currentPage.value = 1
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success(`Exporting ${filteredMetadata.value.length} metadata records...`)
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchMetadata = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Metadata refreshed')
  }, 500)
}

const handleAddMetadata = () => {
  dialogMode.value = 'add'
  Object.assign(formData, {
    name: '',
    entityType: '',
    domain: '',
    owner: '',
    status: 'Active',
    description: '',
    tags: []
  })
  dialogVisible.value = true
}

const viewDetails = (item: any) => {
  currentMetadata.value = item
  detailsDialogVisible.value = true
  if (item.lineage) {
    nextTick(() => {
      initLineageChart()
    })
  }
}

const editMetadata = (item: any) => {
  dialogMode.value = 'edit'
  Object.assign(formData, item)
  dialogVisible.value = true
}

const viewLineage = (item: any) => {
  currentMetadata.value = item
  lineageDialogVisible.value = true
  nextTick(() => {
    if (lineageDetailChartRef.value) {
      if (lineageDetailChart) lineageDetailChart.dispose()
      lineageDetailChart = echarts.init(lineageDetailChartRef.value)

      const sources = item.lineage?.sources || []
      const targets = item.lineage?.targets || []
      const allNodes = [...sources, item.name, ...targets]
      const links = [
        ...sources.map(s => ({ source: s, target: item.name, value: 1 })),
        ...targets.map(t => ({ source: item.name, target: t, value: 1 }))
      ]

      lineageDetailChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'sankey',
          layout: 'none',
          data: allNodes.map(n => ({ name: n })),
          links: links,
          lineStyle: { color: 'gradient', curveness: 0.5 }
        }]
      })
    }
  })
}

const deleteMetadata = (item: any) => {
  ElMessageBox.confirm(`Delete "${item.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = metadataItems.value.findIndex(m => m.id === item.id)
    if (index !== -1) {
      metadataItems.value.splice(index, 1)
      ElMessage.success(`Deleted: ${item.name}`)
      initTypeChart()
    }
  }).catch(() => {})
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate((valid: boolean) => {
    if (valid) {
      if (dialogMode.value === 'add') {
        const newItem = {
          id: Date.now(),
          ...formData,
          createdAt: new Date().toISOString().split('T')[0],
          updatedAt: new Date().toISOString().split('T')[0],
          version: '1.0'
        }
        metadataItems.value.unshift(newItem)
        ElMessage.success('Metadata added successfully')
      } else {
        const index = metadataItems.value.findIndex(m => m.id === formData.id)
        if (index !== -1) {
          metadataItems.value[index] = { ...metadataItems.value[index], ...formData, updatedAt: new Date().toISOString().split('T')[0] }
          ElMessage.success('Metadata updated successfully')
        }
      }
      dialogVisible.value = false
      formRef.value?.resetFields()
      initTypeChart()
    }
  })
}

const exportLineage = () => {
  ElMessage.success('Lineage diagram exported')
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
      fetchMetadata()
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
.metadata-management-page {
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

.search-card {
  margin-bottom: 20px;

  .search-container {
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .advanced-filters {
    margin-top: 16px;

    .filter-actions {
      margin-top: 16px;
      display: flex;
      gap: 12px;
      justify-content: flex-end;
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

.metadata-details {
  .metadata-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }
}

.lineage-chart {
  width: 100%;
  height: 300px;
}

.lineage-container {
  .lineage-detail-chart {
    width: 100%;
    height: 500px;
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