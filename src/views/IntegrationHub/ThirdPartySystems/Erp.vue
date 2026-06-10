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
        <div class="loading-tip">ERP System Integration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="erp-integration-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Third-Party Systems</el-breadcrumb-item>
            <el-breadcrumb-item>ERP</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>ERP System Integration</h1>
        <p class="description">Manage SAP, Oracle, Microsoft Dynamics ERP integrations for enterprise data synchronization</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Logs
        </el-button>
        <el-button type="primary" @click="openAddConnectionDialog">
          <el-icon><Plus /></el-icon>
          Add Connection
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
                <span class="trend-label">vs last week</span>
              </div>
            </div>
            <div class="stat-icon" :style="{ background: stat.bgColor }">
              <el-icon :size="28" color="white">
                <component :is="stat.icon" />
              </el-icon>
            </div>
          </div>
          <div class="stat-footer">
            <span>{{ stat.subTitle }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ERP System Cards -->
    <el-row :gutter="20" class="erp-cards-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="erp in erpSystems" :key="erp.name">
        <el-card class="erp-card" shadow="hover" @click="selectERPSystem(erp)">
          <div class="erp-card-content">
            <div class="erp-icon" :style="{ background: erp.color }">
              <el-icon :size="32"><component :is="erp.icon" /></el-icon>
            </div>
            <div class="erp-info">
              <div class="erp-name">{{ erp.name }}</div>
              <div class="erp-status">
                <el-tag :type="erp.status === 'Connected' ? 'success' : 'danger'" size="small">
                  {{ erp.status }}
                </el-tag>
              </div>
              <div class="erp-version">{{ erp.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Connection Status Overview -->
    <el-card class="connection-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Connection Status</span>
          <div class="connection-controls">
            <el-button size="small" @click="refreshConnections">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <div class="connection-stat">
            <div class="stat-number">4</div>
            <div class="stat-label">Active Connections</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="connection-stat">
            <div class="stat-number">12</div>
            <div class="stat-label">Sync Jobs</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="connection-stat">
            <div class="stat-number">156K</div>
            <div class="stat-label">Records Synced</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="connection-stat">
            <div class="stat-number">99.8%</div>
            <div class="stat-label">Success Rate</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Data Synchronization Jobs -->
    <el-card class="jobs-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Data Synchronization Jobs</span>
          <div class="jobs-actions">
            <el-button size="small" type="primary" @click="openAddJobDialog">
              <el-icon><Plus /></el-icon> Add Job
            </el-button>
            <el-button size="small" @click="fetchJobs">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="syncJobs" stripe style="width: 100%" v-loading="jobsLoading">
        <el-table-column prop="name" label="Job Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="erpSystem" label="ERP System" width="140">
          <template #default="{ row }">
            <el-tag :type="getERPTypeTag(row.erpSystem)" size="small">{{ row.erpSystem }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="direction" label="Direction" width="120">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'IBMS to ERP' ? 'primary' : 'success'" size="small">
              {{ row.direction }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="entityType" label="Entity Type" width="130" />
        <el-table-column prop="schedule" label="Schedule" width="120" />
        <el-table-column prop="lastRun" label="Last Run" width="150" />
        <el-table-column prop="recordsSynced" label="Records" width="100" align="right" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Success' ? 'success' : row.status === 'Running' ? 'warning' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="runJob(row)">Run Now</el-button>
            <el-button link type="info" size="small" @click="viewJobDetails(row)">Details</el-button>
            <el-button link type="danger" size="small" @click="deleteJob(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="jobsPage"
            v-model:page-size="jobsPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="syncJobs.length"
            @size-change="jobsPage = 1"
        />
      </div>
    </el-card>

    <!-- Sync History -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Synchronization History</span>
          <div class="history-controls">
            <el-date-picker
                v-model="historyDateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start Date"
                end-placeholder="End Date"
                size="small"
                style="width: 240px"
            />
            <el-button size="small" @click="filterHistory">Filter</el-button>
          </div>
        </div>
      </template>

      <el-table :data="syncHistory" stripe style="width: 100%" v-loading="historyLoading">
        <el-table-column prop="timestamp" label="Timestamp" width="160" />
        <el-table-column prop="jobName" label="Job Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="erpSystem" label="ERP System" width="140" />
        <el-table-column prop="recordsProcessed" label="Records" width="100" align="right" />
        <el-table-column prop="duration" label="Duration" width="100" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Success' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="Message" min-width="250" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="historyPage"
            v-model:page-size="historyPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="syncHistory.length"
            @size-change="historyPage = 1"
        />
      </div>
    </el-card>

    <!-- Add Connection Dialog -->
    <el-dialog v-model="connectionDialogVisible" title="Add ERP Connection" width="600px" destroy-on-close>
      <el-form :model="connectionForm" :rules="connectionRules" ref="connectionFormRef" label-width="120px">
        <el-form-item label="ERP System" prop="erpSystem">
          <el-select v-model="connectionForm.erpSystem" style="width: 100%">
            <el-option label="SAP S/4HANA" value="SAP S/4HANA" />
            <el-option label="SAP ECC" value="SAP ECC" />
            <el-option label="Oracle E-Business Suite" value="Oracle EBS" />
            <el-option label="Oracle Fusion Cloud" value="Oracle Fusion" />
            <el-option label="Microsoft Dynamics 365" value="Microsoft Dynamics 365" />
            <el-option label="Infor M3" value="Infor M3" />
          </el-select>
        </el-form-item>
        <el-form-item label="Connection Name" prop="name">
          <el-input v-model="connectionForm.name" placeholder="Enter connection name" />
        </el-form-item>
        <el-form-item label="Host/Server" prop="host">
          <el-input v-model="connectionForm.host" placeholder="erp.example.com or 192.168.1.100" />
        </el-form-item>
        <el-form-item label="Port" prop="port">
          <el-input-number v-model="connectionForm.port" :min="1" :max="65535" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Username" prop="username">
          <el-input v-model="connectionForm.username" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="connectionForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="Client/Instance" prop="client">
          <el-input v-model="connectionForm.client" placeholder="Client ID or Instance Name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="connectionForm.description" type="textarea" :rows="2" placeholder="Enter description" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="connectionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testConnection">Test Connection</el-button>
        <el-button type="success" @click="saveConnection">Save Connection</el-button>
      </template>
    </el-dialog>

    <!-- Add Job Dialog -->
    <el-dialog v-model="jobDialogVisible" title="Add Sync Job" width="600px" destroy-on-close>
      <el-form :model="jobForm" :rules="jobRules" ref="jobFormRef" label-width="140px">
        <el-form-item label="Job Name" prop="name">
          <el-input v-model="jobForm.name" placeholder="Enter job name" />
        </el-form-item>
        <el-form-item label="ERP System" prop="erpSystem">
          <el-select v-model="jobForm.erpSystem" style="width: 100%">
            <el-option label="SAP S/4HANA" value="SAP S/4HANA" />
            <el-option label="SAP ECC" value="SAP ECC" />
            <el-option label="Oracle EBS" value="Oracle EBS" />
            <el-option label="Microsoft Dynamics 365" value="Microsoft Dynamics 365" />
          </el-select>
        </el-form-item>
        <el-form-item label="Direction" prop="direction">
          <el-radio-group v-model="jobForm.direction">
            <el-radio value="IBMS to ERP">IBMS → ERP</el-radio>
            <el-radio value="ERP to IBMS">ERP → IBMS</el-radio>
            <el-radio value="Bidirectional">Bidirectional</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Entity Type" prop="entityType">
          <el-select v-model="jobForm.entityType" style="width: 100%">
            <el-option label="Assets" value="Assets" />
            <el-option label="Maintenance Orders" value="Maintenance Orders" />
            <el-option label="Inventory" value="Inventory" />
            <el-option label="Purchase Orders" value="Purchase Orders" />
            <el-option label="Work Orders" value="Work Orders" />
            <el-option label="Spare Parts" value="Spare Parts" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule" prop="schedule">
          <el-select v-model="jobForm.schedule" style="width: 100%">
            <el-option label="Manual Only" value="Manual" />
            <el-option label="Every 15 Minutes" value="15min" />
            <el-option label="Every Hour" value="hourly" />
            <el-option label="Every 6 Hours" value="6hours" />
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
          </el-select>
        </el-form-item>
        <el-form-item label="Field Mapping" prop="fieldMapping">
          <el-input v-model="jobForm.fieldMapping" type="textarea" :rows="3" placeholder="JSON field mapping configuration" />
        </el-form-item>
        <el-form-item label="Filters" prop="filters">
          <el-input v-model="jobForm.filters" type="textarea" :rows="2" placeholder="Optional: JSON filters" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="jobDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testJob">Test Connection</el-button>
        <el-button type="success" @click="saveJob">Save Job</el-button>
      </template>
    </el-dialog>

    <!-- Job Details Dialog -->
    <el-dialog v-model="jobDetailVisible" :title="`Job Details - ${currentJob?.name}`" width="700px" destroy-on-close>
      <div class="job-details" v-if="currentJob">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Job Name">{{ currentJob.name }}</el-descriptions-item>
          <el-descriptions-item label="ERP System">{{ currentJob.erpSystem }}</el-descriptions-item>
          <el-descriptions-item label="Direction">{{ currentJob.direction }}</el-descriptions-item>
          <el-descriptions-item label="Entity Type">{{ currentJob.entityType }}</el-descriptions-item>
          <el-descriptions-item label="Schedule">{{ currentJob.schedule }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentJob.status === 'Success' ? 'success' : 'warning'" size="small">{{ currentJob.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Run">{{ currentJob.lastRun }}</el-descriptions-item>
          <el-descriptions-item label="Next Run">{{ currentJob.nextRun || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Records Synced">{{ currentJob.recordsSynced?.toLocaleString() || 0 }}</el-descriptions-item>
          <el-descriptions-item label="Error Rate">{{ currentJob.errorRate || '0.1%' }}</el-descriptions-item>
          <el-descriptions-item label="Field Mapping" :span="2">
            <pre class="mapping-preview">{{ currentJob.fieldMapping }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="Filters" :span="2" v-if="currentJob.filters">
            <pre class="mapping-preview">{{ currentJob.filters }}</pre>
          </el-descriptions-item>
        </el-descriptions>

        <div class="job-stats">
          <h4>Execution Statistics (Last 7 Days)</h4>
          <div ref="jobStatsChartRef" class="job-stats-chart"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="jobDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="runJob(currentJob)">Run Now</el-button>
      </template>
    </el-dialog>

    <!-- Test Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Server:</strong> {{ testResult.details.server }}</p>
          <p><strong>Version:</strong> {{ testResult.details.version }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
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
  Delete, Connection, Edit, DataAnalysis, Monitor, Share
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing ERP integrations...', 'Loading connections...', 'Almost ready...']

// ==================== Chart References ====================
const jobStatsChartRef = ref<HTMLElement>()
let jobStatsChart: echarts.ECharts | null = null

// ==================== State ====================
const jobsLoading = ref(false)
const historyLoading = ref(false)
const connectionDialogVisible = ref(false)
const jobDialogVisible = ref(false)
const jobDetailVisible = ref(false)
const testDialogVisible = ref(false)
const currentJob = ref<any>(null)
const jobsPage = ref(1)
const jobsPageSize = ref(10)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyDateRange = ref<[Date, Date] | null>(null)

const connectionFormRef = ref()
const jobFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'ERP Systems', value: '4', trend: 0, icon: 'Connection', bgColor: '#409eff', key: 'systems', subTitle: 'All Connected' },
  { title: 'Sync Jobs', value: '12', trend: 2, icon: 'Document', bgColor: '#67c23a', key: 'jobs', subTitle: 'Active: 10' },
  { title: 'Records Synced', value: '156K', trend: 18, icon: 'DataAnalysis', bgColor: '#e6a23c', key: 'records', subTitle: 'Last 30 days' },
  { title: 'Success Rate', value: '99.8%', trend: 0.5, icon: 'Checked', bgColor: '#f56c6c', key: 'rate', subTitle: 'Avg response: 245ms' }
])

const erpSystems = ref([
  { name: 'SAP S/4HANA', icon: 'DataAnalysis', color: '#409eff', status: 'Connected', version: '2023 FPS01' },
  { name: 'Oracle E-Business Suite', icon: 'Monitor', color: '#f56c6c', status: 'Connected', version: '12.2.10' },
  { name: 'Microsoft Dynamics 365', icon: 'Share', color: '#67c23a', status: 'Connected', version: '9.2' }
])

const syncJobs = ref([
  { id: 1, name: 'Asset Master Sync', erpSystem: 'SAP S/4HANA', direction: 'Bidirectional', entityType: 'Assets', schedule: 'Hourly', lastRun: '2024-01-20 10:00:00', recordsSynced: 12450, status: 'Success', fieldMapping: '{"asset_id": "EQUNR", "name": "EQKTX", "location": "STORT"}', filters: '{"status": "active"}' },
  { id: 2, name: 'Maintenance Orders Export', erpSystem: 'SAP S/4HANA', direction: 'IBMS to ERP', entityType: 'Maintenance Orders', schedule: 'Daily', lastRun: '2024-01-20 01:00:00', recordsSynced: 345, status: 'Success', fieldMapping: '{"work_order": "AUFNR", "description": "LTEXT"}' },
  { id: 3, name: 'Inventory Sync', erpSystem: 'Oracle EBS', direction: 'ERP to IBMS', entityType: 'Inventory', schedule: 'Every 6 Hours', lastRun: '2024-01-20 08:00:00', recordsSynced: 2456, status: 'Running', fieldMapping: '{"part_number": "INVENTORY_ITEM_ID", "quantity": "QUANTITY"}' },
  { id: 4, name: 'Purchase Orders Sync', erpSystem: 'Microsoft Dynamics 365', direction: 'Bidirectional', entityType: 'Purchase Orders', schedule: 'Daily', lastRun: '2024-01-19 23:00:00', recordsSynced: 89, status: 'Failed', fieldMapping: '{"po_number": "PURCHID", "vendor": "VENDACCOUNT"}' },
  { id: 5, name: 'Spare Parts Sync', erpSystem: 'SAP S/4HANA', direction: 'ERP to IBMS', entityType: 'Spare Parts', schedule: 'Hourly', lastRun: '2024-01-20 09:00:00', recordsSynced: 5678, status: 'Success', fieldMapping: '{"part_id": "MATNR", "description": "MAKTX"}' },
  { id: 6, name: 'Work Orders Sync', erpSystem: 'Oracle EBS', direction: 'IBMS to ERP', entityType: 'Work Orders', schedule: 'Every 15 Minutes', lastRun: '2024-01-20 10:15:00', recordsSynced: 123, status: 'Success', fieldMapping: '{"wo_number": "WIP_ENTITY_ID", "status": "STATUS"}' }
])

const syncHistory = ref([
  { id: 1, timestamp: '2024-01-20 10:00:00', jobName: 'Asset Master Sync', erpSystem: 'SAP S/4HANA', recordsProcessed: 12450, duration: '2 min 34 sec', status: 'Success', message: 'Sync completed successfully' },
  { id: 2, timestamp: '2024-01-20 09:00:00', jobName: 'Asset Master Sync', erpSystem: 'SAP S/4HANA', recordsProcessed: 12340, duration: '2 min 28 sec', status: 'Success', message: 'Sync completed successfully' },
  { id: 3, timestamp: '2024-01-20 08:00:00', jobName: 'Inventory Sync', erpSystem: 'Oracle EBS', recordsProcessed: 2456, duration: '1 min 45 sec', status: 'Running', message: 'Sync in progress' },
  { id: 4, timestamp: '2024-01-19 23:00:00', jobName: 'Purchase Orders Sync', erpSystem: 'Microsoft Dynamics 365', recordsProcessed: 89, duration: '45 sec', status: 'Failed', message: 'Connection timeout' },
  { id: 5, timestamp: '2024-01-20 01:00:00', jobName: 'Maintenance Orders Export', erpSystem: 'SAP S/4HANA', recordsProcessed: 345, duration: '1 min 12 sec', status: 'Success', message: 'Sync completed successfully' },
  { id: 6, timestamp: '2024-01-20 09:00:00', jobName: 'Spare Parts Sync', erpSystem: 'SAP S/4HANA', recordsProcessed: 5678, duration: '3 min 22 sec', status: 'Success', message: 'Sync completed successfully' },
  { id: 7, timestamp: '2024-01-20 10:15:00', jobName: 'Work Orders Sync', erpSystem: 'Oracle EBS', recordsProcessed: 123, duration: '28 sec', status: 'Success', message: 'Sync completed successfully' }
])

// Forms
const connectionForm = reactive({
  erpSystem: '',
  name: '',
  host: '',
  port: 443,
  username: '',
  password: '',
  client: '',
  description: ''
})

const jobForm = reactive({
  name: '',
  erpSystem: '',
  direction: 'IBMS to ERP',
  entityType: '',
  schedule: 'daily',
  fieldMapping: '',
  filters: ''
})

// Rules
const connectionRules = {
  erpSystem: [{ required: true, message: 'Please select ERP system', trigger: 'change' }],
  name: [{ required: true, message: 'Please enter connection name', trigger: 'blur' }],
  host: [{ required: true, message: 'Please enter host', trigger: 'blur' }],
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const jobRules = {
  name: [{ required: true, message: 'Please enter job name', trigger: 'blur' }],
  erpSystem: [{ required: true, message: 'Please select ERP system', trigger: 'change' }],
  entityType: [{ required: true, message: 'Please select entity type', trigger: 'change' }]
}

// ==================== Helper Methods ====================
const getERPTypeTag = (erpSystem: string) => {
  const map: Record<string, string> = {
    'SAP S/4HANA': 'primary',
    'SAP ECC': 'primary',
    'Oracle EBS': 'danger',
    'Oracle Fusion': 'danger',
    'Microsoft Dynamics 365': 'success'
  }
  return map[erpSystem] || 'info'
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting ERP integration logs...')
}

const selectERPSystem = (erp: any) => {
  ElMessage.info(`Selected ${erp.name} - ${erp.status}`)
}

const refreshConnections = () => {
  ElMessage.success('Connections refreshed')
}

const fetchJobs = () => {
  jobsLoading.value = true
  setTimeout(() => {
    jobsLoading.value = false
    ElMessage.success('Jobs refreshed')
  }, 500)
}

const filterHistory = () => {
  ElMessage.success('History filtered')
}

const openAddConnectionDialog = () => {
  connectionDialogVisible.value = true
}

const openAddJobDialog = () => {
  jobDialogVisible.value = true
}

const testConnection = () => {
  ElMessage.info('Testing connection...')
  setTimeout(() => {
    testResult.success = true
    testResult.message = 'Successfully connected to ERP system'
    testResult.details = {
      server: connectionForm.host,
      version: '2023',
      responseTime: 156
    }
    testDialogVisible.value = true
  }, 1500)
}

const saveConnection = async () => {
  if (!connectionFormRef.value) return
  await connectionFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Connection saved successfully')
      connectionDialogVisible.value = false
      connectionFormRef.value?.resetFields()
    }
  })
}

const testJob = () => {
  ElMessage.info('Testing job configuration...')
  setTimeout(() => {
    ElMessage.success('Job configuration is valid')
  }, 1000)
}

const saveJob = async () => {
  if (!jobFormRef.value) return
  await jobFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success('Job created successfully')
      jobDialogVisible.value = false
      jobFormRef.value?.resetFields()
    }
  })
}

const runJob = (job: any) => {
  ElMessage.info(`Starting job "${job.name}"...`)
  setTimeout(() => {
    ElMessage.success(`Job "${job.name}" completed successfully`)
  }, 2000)
}

const viewJobDetails = (job: any) => {
  currentJob.value = job
  jobDetailVisible.value = true
  nextTick(() => {
    if (jobStatsChartRef.value) {
      if (jobStatsChart) jobStatsChart.dispose()
      jobStatsChart = echarts.init(jobStatsChartRef.value)
      jobStatsChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: { type: 'value', name: 'Records' },
        series: [{ type: 'line', data: [1250, 1420, 1380, 1560, 1890, 2100, 1450], smooth: true, lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.1 } }]
      })
    }
  })
}

const deleteJob = (job: any) => {
  ElMessageBox.confirm(`Delete job "${job.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = syncJobs.value.findIndex(j => j.id === job.id)
    if (index !== -1) {
      syncJobs.value.splice(index, 1)
      ElMessage.success(`Deleted: ${job.name}`)
    }
  }).catch(() => {})
}

// ==================== Mounted ====================
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
      fetchJobs()
    }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
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
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%,80%,100% { transform: scale(0); opacity: 0.3; } 40% { transform: scale(1); opacity: 1; } }
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
@keyframes shimmer { 0% { background-position: 0% 0%; } 100% { background-position: 200% 0%; } }
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
@keyframes pulse { 0%,100% { opacity: 0.6; } 50% { opacity: 1; } }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.erp-integration-page {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-header .breadcrumb { margin-bottom: 8px; }
.page-header h1 { font-size: 28px; font-weight: 600; color: #303133; margin: 0 0 8px 0; }
.page-header .description { color: #909399; font-size: 14px; margin: 0; }
.page-header .header-actions { display: flex; gap: 12px; }

.stats-row { margin-bottom: 20px; }
.stat-card { cursor: pointer; transition: all 0.3s; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card .stat-content { display: flex; justify-content: space-between; align-items: center; }
.stat-card .stat-info { flex: 1; }
.stat-card .stat-title { font-size: 14px; color: #909399; margin-bottom: 8px; }
.stat-card .stat-value { font-size: 28px; font-weight: 600; color: #303133; margin-bottom: 8px; }
.stat-card .stat-trend { font-size: 12px; display: flex; align-items: center; gap: 4px; }
.stat-card .stat-trend.up { color: #67c23a; }
.stat-card .stat-trend.down { color: #f56c6c; }
.stat-card .stat-trend .trend-label { color: #909399; margin-left: 4px; }
.stat-card .stat-icon { width: 56px; height: 56px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.stat-card .stat-footer { margin-top: 12px; padding-top: 8px; border-top: 1px solid #ebeef5; font-size: 12px; color: #909399; }

.erp-cards-row { margin-bottom: 20px; }
.erp-card { cursor: pointer; transition: all 0.3s; }
.erp-card:hover { transform: translateY(-4px); }
.erp-card .erp-card-content { display: flex; gap: 16px; align-items: center; }
.erp-card .erp-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.erp-card .erp-info { flex: 1; }
.erp-card .erp-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.erp-card .erp-version { font-size: 12px; color: #909399; margin-top: 4px; }

.connection-card { margin-bottom: 20px; }
.connection-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.connection-stat { text-align: center; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.connection-stat .stat-number { font-size: 28px; font-weight: 600; color: #409eff; }
.connection-stat .stat-label { font-size: 13px; color: #909399; margin-top: 8px; }

.jobs-card, .history-card { margin-bottom: 20px; }
.jobs-card .card-header, .history-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.jobs-card .jobs-actions, .history-card .history-controls { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.job-details .job-stats { margin-top: 20px; }
.job-details .job-stats h4 { margin-bottom: 12px; }
.job-stats-chart { width: 100%; height: 300px; }
.mapping-preview { background: #f5f7fa; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; margin: 0; overflow-x: auto; }

.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>