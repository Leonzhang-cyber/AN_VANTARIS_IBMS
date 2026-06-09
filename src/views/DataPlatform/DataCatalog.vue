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
        <div class="loading-tip">Data Catalog</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="data-catalog-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Catalog</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>Data Catalog</h1>
        <p class="description">Discover, understand, and govern your data assets across the enterprise</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Catalog
        </el-button>
        <el-button type="primary" @click="handleAddAsset">
          <el-icon><Plus /></el-icon>
          Register Asset
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

    <!-- Search & Filters -->
    <el-card class="search-card" shadow="hover">
      <div class="search-container">
        <el-input
            v-model="searchKeyword"
            placeholder="Search for datasets, tables, columns, or descriptions..."
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
          Filters
        </el-button>
      </div>

      <el-collapse-transition>
        <div v-show="showAdvancedFilters" class="advanced-filters">
          <el-divider />
          <el-row :gutter="20">
            <el-col :span="6">
              <el-select v-model="filters.dataDomain" placeholder="Data Domain" clearable style="width: 100%">
                <el-option label="Operations" value="Operations" />
                <el-option label="Finance" value="Finance" />
                <el-option label="Customer" value="Customer" />
                <el-option label="Asset" value="Asset" />
                <el-option label="Energy" value="Energy" />
                <el-option label="ESG" value="ESG" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.dataType" placeholder="Data Type" clearable style="width: 100%">
                <el-option label="Structured" value="Structured" />
                <el-option label="Semi-structured" value="Semi-structured" />
                <el-option label="Unstructured" value="Unstructured" />
                <el-option label="Time-series" value="Time-series" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.sourceSystem" placeholder="Source System" clearable style="width: 100%">
                <el-option label="BMS" value="BMS" />
                <el-option label="SCADA" value="SCADA" />
                <el-option label="ERP" value="ERP" />
                <el-option label="IoT" value="IoT" />
                <el-option label="Manual" value="Manual" />
              </el-select>
            </el-col>
            <el-col :span="6">
              <el-select v-model="filters.quality" placeholder="Data Quality" clearable style="width: 100%">
                <el-option label="Certified" value="Certified" />
                <el-option label="Verified" value="Verified" />
                <el-option label="Draft" value="Draft" />
                <el-option label="Deprecated" value="Deprecated" />
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

    <!-- Data Asset Tree & Detail View -->
    <el-row :gutter="20" class="catalog-row">
      <!-- Left: Data Asset Tree -->
      <el-col :xs="24" :lg="8">
        <el-card class="tree-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Data Assets</span>
              <el-button link type="primary" size="small" @click="refreshTree">
                <el-icon><Refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <el-tree
              ref="treeRef"
              :data="treeData"
              :props="treeProps"
              node-key="id"
              default-expand-all
              highlight-current
              @node-click="handleNodeClick"
          >
            <template #default="{ node, data }">
              <span class="tree-node">
                <el-icon :color="getNodeIconColor(data.type)">
                  <component :is="getNodeIcon(data.type)" />
                </el-icon>
                <span>{{ node.label }}</span>
                <el-tag v-if="data.quality" :type="getQualityTagType(data.quality)" size="small" class="tree-tag">
                  {{ data.quality }}
                </el-tag>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- Right: Asset Details -->
      <el-col :xs="24" :lg="16">
        <el-card class="detail-card" shadow="hover" v-if="selectedAsset">
          <template #header>
            <div class="card-header">
              <div class="asset-title">
                <el-icon :size="20" :color="getNodeIconColor(selectedAsset.type)"><component :is="getNodeIcon(selectedAsset.type)" /></el-icon>
                <span>{{ selectedAsset.name }}</span>
                <el-tag :type="getQualityTagType(selectedAsset.quality)" size="small">{{ selectedAsset.quality }}</el-tag>
              </div>
              <div class="asset-actions">
                <el-button link type="primary" size="small" @click="viewLineage(selectedAsset)">Lineage</el-button>
                <el-button link type="success" size="small" @click="previewData(selectedAsset)">Preview</el-button>
                <el-button link type="info" size="small" @click="editAsset(selectedAsset)">Edit</el-button>
              </div>
            </div>
          </template>

          <!-- Asset Metadata -->
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Asset ID">{{ selectedAsset.id }}</el-descriptions-item>
            <el-descriptions-item label="Data Domain">{{ selectedAsset.domain || 'Operations' }}</el-descriptions-item>
            <el-descriptions-item label="Source System">{{ selectedAsset.sourceSystem || 'BMS' }}</el-descriptions-item>
            <el-descriptions-item label="Data Type">{{ selectedAsset.dataType || 'Structured' }}</el-descriptions-item>
            <el-descriptions-item label="Owner">{{ selectedAsset.owner || 'Data Platform Team' }}</el-descriptions-item>
            <el-descriptions-item label="Last Updated">{{ selectedAsset.lastUpdated }}</el-descriptions-item>
            <el-descriptions-item label="Row Count">{{ selectedAsset.rowCount?.toLocaleString() || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Size">{{ selectedAsset.size || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="Description" :span="2">{{ selectedAsset.description || 'No description available' }}</el-descriptions-item>
          </el-descriptions>

          <!-- Schema / Columns -->
          <div class="schema-section" v-if="selectedAsset.columns">
            <h4>Schema / Columns</h4>
            <el-table :data="selectedAsset.columns" size="small" border>
              <el-table-column prop="name" label="Column Name" width="180" />
              <el-table-column prop="type" label="Data Type" width="120" />
              <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
              <el-table-column label="Key" width="80">
                <template #default="{ row }">
                  <el-tag v-if="row.isPrimaryKey" type="danger" size="small">PK</el-tag>
                  <el-tag v-else-if="row.isForeignKey" type="warning" size="small">FK</el-tag>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column label="Nullable" width="80" align="center">
                <template #default="{ row }">
                  <el-icon :color="row.nullable ? '#67c23a' : '#f56c6c'">
                    <component :is="row.nullable ? 'CircleCheck' : 'CircleClose'" />
                  </el-icon>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- Sample Data Preview -->
          <div class="preview-section" v-if="previewDataVisible">
            <h4>Sample Data (Top 10 rows)</h4>
            <el-table :data="sampleData" size="small" border v-loading="previewLoading">
              <el-table-column v-for="col in sampleColumns" :key="col" :prop="col" :label="col" min-width="100" />
            </el-table>
          </div>

          <!-- Tags -->
          <div class="tags-section" v-if="selectedAsset.tags?.length">
            <h4>Tags</h4>
            <div>
              <el-tag v-for="tag in selectedAsset.tags" :key="tag" size="small" style="margin-right: 8px">{{ tag }}</el-tag>
            </div>
          </div>

          <!-- Usage Statistics -->
          <div class="usage-section">
            <h4>Usage Statistics</h4>
            <el-row :gutter="16">
              <el-col :span="8">
                <div class="stat-mini">
                  <div class="stat-mini-value">{{ selectedAsset.queries || 0 }}</div>
                  <div class="stat-mini-label">Queries (30d)</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-mini">
                  <div class="stat-mini-value">{{ selectedAsset.users || 0 }}</div>
                  <div class="stat-mini-label">Active Users</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-mini">
                  <div class="stat-mini-value">{{ selectedAsset.jobs || 0 }}</div>
                  <div class="stat-mini-label">ETL Jobs</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- Empty State -->
        <el-card class="detail-card" shadow="hover" v-else>
          <div class="empty-state">
            <el-empty description="Select a data asset from the left to view details" />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Data Lineage Dialog -->
    <el-dialog v-model="lineageDialogVisible" title="Data Lineage" width="800px" destroy-on-close>
      <div class="lineage-container">
        <div ref="lineageChartRef" class="lineage-chart"></div>
      </div>
      <template #footer>
        <el-button @click="lineageDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportLineage">Export Lineage</el-button>
      </template>
    </el-dialog>

    <!-- Register Asset Dialog -->
    <el-dialog v-model="registerDialogVisible" title="Register Data Asset" width="600px" destroy-on-close>
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" label-width="120px">
        <el-form-item label="Asset Name" prop="name">
          <el-input v-model="registerForm.name" placeholder="Enter asset name" />
        </el-form-item>
        <el-form-item label="Asset Type" prop="type">
          <el-select v-model="registerForm.type" placeholder="Select type" style="width: 100%">
            <el-option label="Database" value="database" />
            <el-option label="Schema" value="schema" />
            <el-option label="Table" value="table" />
            <el-option label="View" value="view" />
            <el-option label="Stream" value="stream" />
          </el-select>
        </el-form-item>
        <el-form-item label="Data Domain" prop="domain">
          <el-select v-model="registerForm.domain" placeholder="Select domain" style="width: 100%">
            <el-option label="Operations" value="Operations" />
            <el-option label="Finance" value="Finance" />
            <el-option label="Customer" value="Customer" />
            <el-option label="Asset" value="Asset" />
            <el-option label="Energy" value="Energy" />
            <el-option label="ESG" value="ESG" />
          </el-select>
        </el-form-item>
        <el-form-item label="Source System" prop="sourceSystem">
          <el-select v-model="registerForm.sourceSystem" placeholder="Select source" style="width: 100%">
            <el-option label="BMS" value="BMS" />
            <el-option label="SCADA" value="SCADA" />
            <el-option label="ERP" value="ERP" />
            <el-option label="IoT" value="IoT" />
          </el-select>
        </el-form-item>
        <el-form-item label="Connection" prop="connectionId">
          <el-select v-model="registerForm.connectionId" placeholder="Select data source" style="width: 100%">
            <el-option label="PostgreSQL Main DB" value="1" />
            <el-option label="MySQL Timeseries DB" value="2" />
            <el-option label="MongoDB Document Store" value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="registerForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Owner" prop="owner">
          <el-input v-model="registerForm.owner" placeholder="Enter owner name" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="registerDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitRegister">Register</el-button>
      </template>
    </el-dialog>

    <!-- Edit Asset Dialog -->
    <el-dialog v-model="editDialogVisible" title="Edit Data Asset" width="500px" destroy-on-close>
      <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
        <el-form-item label="Description" prop="description">
          <el-input v-model="editForm.description" type="textarea" :rows="3" placeholder="Enter description" />
        </el-form-item>
        <el-form-item label="Owner" prop="owner">
          <el-input v-model="editForm.owner" placeholder="Enter owner name" />
        </el-form-item>
        <el-form-item label="Quality" prop="quality">
          <el-select v-model="editForm.quality" placeholder="Select quality" style="width: 100%">
            <el-option label="Certified" value="Certified" />
            <el-option label="Verified" value="Verified" />
            <el-option label="Draft" value="Draft" />
            <el-option label="Deprecated" value="Deprecated" />
          </el-select>
        </el-form-item>
        <el-form-item label="Tags">
          <el-select v-model="editForm.tags" multiple filterable allow-create default-first-option placeholder="Enter tags" style="width: 100%">
            <el-option label="Critical" value="Critical" />
            <el-option label="Sensitive" value="Sensitive" />
            <el-option label="PII" value="PII" />
            <el-option label="Archived" value="Archived" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitEdit">Save Changes</el-button>
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
  Filter, Folder, DataAnalysis, Coin, Connection,
  CircleCheck, CircleClose
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading data catalog...',
  'Building asset tree...',
  'Almost ready...'
]

// ==================== Chart References ====================
const lineageChartRef = ref<HTMLElement>()
let lineageChart: echarts.ECharts | null = null

// ==================== State ====================
const searchKeyword = ref('')
const showAdvancedFilters = ref(false)
const selectedAsset = ref<any>(null)
const previewDataVisible = ref(false)
const previewLoading = ref(false)
const sampleData = ref<any[]>([])
const sampleColumns = ref<string[]>([])
const lineageDialogVisible = ref(false)
const registerDialogVisible = ref(false)
const editDialogVisible = ref(false)
const treeRef = ref()
const registerFormRef = ref()
const editFormRef = ref()

const filters = reactive({
  dataDomain: '',
  dataType: '',
  sourceSystem: '',
  quality: ''
})

const registerForm = reactive({
  name: '',
  type: '',
  domain: '',
  sourceSystem: '',
  connectionId: '',
  description: '',
  owner: ''
})

const editForm = reactive({
  description: '',
  owner: '',
  quality: '',
  tags: [] as string[]
})

const registerRules = {
  name: [{ required: true, message: 'Please enter asset name', trigger: 'blur' }],
  type: [{ required: true, message: 'Please select asset type', trigger: 'change' }],
  connectionId: [{ required: true, message: 'Please select connection', trigger: 'change' }]
}

const editRules = {
  description: [{ required: true, message: 'Please enter description', trigger: 'blur' }],
  owner: [{ required: true, message: 'Please enter owner name', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total Assets', value: 248, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Databases', value: 12, trend: 0, icon: 'Coin', bgColor: '#67c23a', key: 'databases' },
  { title: 'Tables/Views', value: 186, trend: 15, icon: 'DataAnalysis', bgColor: '#e6a23c', key: 'tables' },
  { title: 'Certified Assets', value: 142, trend: 18, icon: 'Checked', bgColor: '#f56c6c', key: 'certified' }
])

const treeData = ref([
  {
    id: 'db1',
    label: 'Operations Database',
    type: 'database',
    quality: 'Certified',
    children: [
      {
        id: 'schema1',
        label: 'public',
        type: 'schema',
        children: [
          {
            id: 'table1',
            label: 'devices',
            type: 'table',
            quality: 'Certified',
            metadata: {
              id: 'table1',
              name: 'devices',
              type: 'table',
              domain: 'Asset',
              sourceSystem: 'BMS',
              dataType: 'Structured',
              owner: 'John Smith',
              lastUpdated: '2024-01-20 10:30:00',
              rowCount: 12450,
              size: '45 MB',
              description: 'Device master table containing all IoT devices and sensors',
              quality: 'Certified',
              columns: [
                { name: 'device_id', type: 'VARCHAR(50)', description: 'Unique device identifier', isPrimaryKey: true, isForeignKey: false, nullable: false },
                { name: 'device_name', type: 'VARCHAR(200)', description: 'Device display name', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'device_type', type: 'VARCHAR(50)', description: 'Type of device (sensor, controller, etc.)', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'location', type: 'VARCHAR(100)', description: 'Installation location', isPrimaryKey: false, isForeignKey: false, nullable: true },
                { name: 'status', type: 'VARCHAR(20)', description: 'Current device status', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'last_heartbeat', type: 'TIMESTAMP', description: 'Last communication timestamp', isPrimaryKey: false, isForeignKey: false, nullable: true }
              ],
              queries: 1245,
              users: 18,
              jobs: 3,
              tags: ['Critical', 'Sensitive']
            }
          },
          {
            id: 'table2',
            label: 'readings',
            type: 'table',
            quality: 'Certified',
            metadata: {
              id: 'table2',
              name: 'readings',
              type: 'table',
              domain: 'Operations',
              sourceSystem: 'IoT',
              dataType: 'Time-series',
              owner: 'John Smith',
              lastUpdated: '2024-01-20 10:30:00',
              rowCount: 8450000,
              size: '2.4 GB',
              description: 'Time-series readings from all IoT sensors',
              quality: 'Certified',
              columns: [
                { name: 'reading_id', type: 'BIGINT', description: 'Unique reading identifier', isPrimaryKey: true, isForeignKey: false, nullable: false },
                { name: 'device_id', type: 'VARCHAR(50)', description: 'Reference to devices table', isPrimaryKey: false, isForeignKey: true, nullable: false },
                { name: 'timestamp', type: 'TIMESTAMP', description: 'Reading timestamp', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'metric_name', type: 'VARCHAR(50)', description: 'Type of reading (temperature, pressure, etc.)', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'value', type: 'DOUBLE', description: 'Reading value', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'unit', type: 'VARCHAR(20)', description: 'Unit of measurement', isPrimaryKey: false, isForeignKey: false, nullable: true }
              ],
              queries: 3456,
              users: 24,
              jobs: 5,
              tags: ['Time-series', 'Critical']
            }
          }
        ]
      }
    ]
  },
  {
    id: 'db2',
    label: 'Energy Analytics',
    type: 'database',
    quality: 'Verified',
    children: [
      {
        id: 'schema2',
        label: 'energy',
        type: 'schema',
        children: [
          {
            id: 'table3',
            label: 'consumption_summary',
            type: 'table',
            quality: 'Verified',
            metadata: {
              id: 'table3',
              name: 'consumption_summary',
              type: 'table',
              domain: 'Energy',
              sourceSystem: 'SCADA',
              dataType: 'Structured',
              owner: 'Lisa Zhang',
              lastUpdated: '2024-01-20 09:00:00',
              rowCount: 36500,
              size: '125 MB',
              description: 'Daily energy consumption summary by building',
              quality: 'Verified',
              columns: [
                { name: 'date', type: 'DATE', description: 'Date of consumption', isPrimaryKey: true, isForeignKey: false, nullable: false },
                { name: 'building_id', type: 'VARCHAR(20)', description: 'Building identifier', isPrimaryKey: true, isForeignKey: false, nullable: false },
                { name: 'consumption_kwh', type: 'DOUBLE', description: 'Total energy consumption in kWh', isPrimaryKey: false, isForeignKey: false, nullable: false },
                { name: 'cost_usd', type: 'DOUBLE', description: 'Estimated cost in USD', isPrimaryKey: false, isForeignKey: false, nullable: true }
              ],
              queries: 890,
              users: 12,
              jobs: 2,
              tags: ['Energy', 'Finance']
            }
          }
        ]
      }
    ]
  },
  {
    id: 'stream1',
    label: 'Real-time Sensor Stream',
    type: 'stream',
    quality: 'Certified',
    metadata: {
      id: 'stream1',
      name: 'Real-time Sensor Stream',
      type: 'stream',
      domain: 'Operations',
      sourceSystem: 'Kafka',
      dataType: 'Semi-structured',
      owner: 'Tom Harris',
      lastUpdated: '2024-01-20 10:35:00',
      rowCount: 1250000,
      size: 'N/A',
      description: 'Real-time sensor data stream from Kafka topic',
      quality: 'Certified',
      columns: [
        { name: 'device_id', type: 'STRING', description: 'Device identifier', isPrimaryKey: false, isForeignKey: false, nullable: false },
        { name: 'timestamp', type: 'TIMESTAMP', description: 'Reading timestamp', isPrimaryKey: false, isForeignKey: false, nullable: false },
        { name: 'payload', type: 'JSON', description: 'Sensor reading payload', isPrimaryKey: false, isForeignKey: false, nullable: false }
      ],
      queries: 5678,
      users: 8,
      jobs: 1,
      tags: ['Real-time', 'Streaming']
    }
  }
])

const treeProps = {
  children: 'children',
  label: 'label'
}

// ==================== Helper Methods ====================
const getNodeIcon = (type: string) => {
  const map: Record<string, string> = {
    'database': 'Coin',
    'schema': 'Folder',
    'table': 'DataAnalysis',
    'view': 'Document',
    'stream': 'Connection'
  }
  return map[type] || 'Document'
}

const getNodeIconColor = (type: string) => {
  const map: Record<string, string> = {
    'database': '#409eff',
    'schema': '#e6a23c',
    'table': '#67c23a',
    'view': '#909399',
    'stream': '#f56c6c'
  }
  return map[type] || '#909399'
}

const getQualityTagType = (quality: string) => {
  const map: Record<string, string> = {
    'Certified': 'success',
    'Verified': 'primary',
    'Draft': 'info',
    'Deprecated': 'danger'
  }
  return map[quality] || 'info'
}

// ==================== Chart Initialization ====================
const initLineageChart = () => {
  if (!lineageChartRef.value) return
  if (lineageChart) lineageChart.dispose()

  lineageChart = echarts.init(lineageChartRef.value)

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'sankey',
      layout: 'none',
      emphasis: { focus: 'adjacency' },
      data: [
        { name: 'IoT Sensors' },
        { name: 'Kafka Stream' },
        { name: 'Raw Data Lake' },
        { name: 'ETL Process' },
        { name: 'devices Table' },
        { name: 'readings Table' },
        { name: 'Energy Dashboard' },
        { name: 'ML Model' }
      ],
      links: [
        { source: 'IoT Sensors', target: 'Kafka Stream', value: 10000 },
        { source: 'Kafka Stream', target: 'Raw Data Lake', value: 10000 },
        { source: 'Raw Data Lake', target: 'ETL Process', value: 10000 },
        { source: 'ETL Process', target: 'devices Table', value: 1000 },
        { source: 'ETL Process', target: 'readings Table', value: 9000 },
        { source: 'devices Table', target: 'Energy Dashboard', value: 500 },
        { source: 'readings Table', target: 'Energy Dashboard', value: 500 },
        { source: 'readings Table', target: 'ML Model', value: 5000 }
      ],
      lineStyle: { color: 'gradient', curveness: 0.5 },
      nodeAlign: 'justify'
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
  ElMessage.info(`Searching for: ${searchKeyword.value}`)
}

const applyFilters = () => {
  ElMessage.success('Filters applied')
}

const resetFilters = () => {
  filters.dataDomain = ''
  filters.dataType = ''
  filters.sourceSystem = ''
  filters.quality = ''
  ElMessage.success('Filters reset')
}

const handleExport = () => {
  ElMessage.success('Exporting data catalog...')
}

const handleAddAsset = () => {
  registerDialogVisible.value = true
}

const refreshTree = () => {
  ElMessage.success('Tree refreshed')
}

const handleNodeClick = (data: any) => {
  if (data.metadata) {
    selectedAsset.value = data.metadata
    previewDataVisible.value = false
  } else {
    selectedAsset.value = null
  }
}

const viewLineage = (asset: any) => {
  lineageDialogVisible.value = true
  nextTick(() => {
    initLineageChart()
  })
}

const previewData = (asset: any) => {
  previewLoading.value = true
  previewDataVisible.value = true

  // Mock sample data
  setTimeout(() => {
    if (asset.name === 'devices') {
      sampleColumns.value = ['device_id', 'device_name', 'device_type', 'location', 'status', 'last_heartbeat']
      sampleData.value = [
        { device_id: 'DEV-001', device_name: 'Temperature Sensor A1', device_type: 'sensor', location: 'Building A', status: 'active', last_heartbeat: '2024-01-20 10:30:00' },
        { device_id: 'DEV-002', device_name: 'Pressure Sensor B2', device_type: 'sensor', location: 'Building B', status: 'active', last_heartbeat: '2024-01-20 10:29:00' },
        { device_id: 'DEV-003', device_name: 'HVAC Controller C3', device_type: 'controller', location: 'Building A', status: 'active', last_heartbeat: '2024-01-20 10:31:00' }
      ]
    } else if (asset.name === 'readings') {
      sampleColumns.value = ['reading_id', 'device_id', 'timestamp', 'metric_name', 'value', 'unit']
      sampleData.value = [
        { reading_id: 1, device_id: 'DEV-001', timestamp: '2024-01-20 10:30:00', metric_name: 'temperature', value: 22.5, unit: '°C' },
        { reading_id: 2, device_id: 'DEV-001', timestamp: '2024-01-20 10:29:00', metric_name: 'humidity', value: 45, unit: '%' },
        { reading_id: 3, device_id: 'DEV-002', timestamp: '2024-01-20 10:30:00', metric_name: 'pressure', value: 1013.2, unit: 'hPa' }
      ]
    }
    previewLoading.value = false
  }, 1000)
}

const editAsset = (asset: any) => {
  editForm.description = asset.description || ''
  editForm.owner = asset.owner || ''
  editForm.quality = asset.quality || 'Draft'
  editForm.tags = asset.tags || []
  editDialogVisible.value = true
}

const submitRegister = async () => {
  if (!registerFormRef.value) return
  await registerFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Asset registered successfully')
      registerDialogVisible.value = false
      registerFormRef.value?.resetFields()
    }
  })
}

const submitEdit = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate((valid: boolean) => {
    if (valid) {
      if (selectedAsset.value) {
        selectedAsset.value.description = editForm.description
        selectedAsset.value.owner = editForm.owner
        selectedAsset.value.quality = editForm.quality
        selectedAsset.value.tags = editForm.tags
      }
      ElMessage.success('Asset updated successfully')
      editDialogVisible.value = false
    }
  })
}

const exportLineage = () => {
  ElMessage.success('Lineage diagram exported')
}

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
.data-catalog-page {
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

.catalog-row {
  margin-bottom: 20px;
}

.tree-card {
  height: 600px;
  overflow-y: auto;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .tree-node {
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      flex-shrink: 0;
    }

    .tree-tag {
      margin-left: auto;
    }
  }
}

.detail-card {
  height: 600px;
  overflow-y: auto;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;

    .asset-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      font-size: 16px;
    }

    .asset-actions {
      display: flex;
      gap: 8px;
    }
  }

  .schema-section, .preview-section, .tags-section, .usage-section {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
      font-size: 15px;
    }
  }

  .usage-section {
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

  .empty-state {
    height: 500px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.lineage-container {
  .lineage-chart {
    width: 100%;
    height: 500px;
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-tree-node__content) {
  height: 36px;
}

:deep(.el-dialog__body) {
  max-height: 60vh;
  overflow-y: auto;
}
</style>