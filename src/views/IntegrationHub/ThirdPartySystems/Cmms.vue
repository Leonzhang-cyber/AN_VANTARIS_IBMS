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
        <div class="loading-tip">CMMS System Integration</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cmms-integration-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Third-Party Systems</el-breadcrumb-item>
            <el-breadcrumb-item>CMMS</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>CMMS System Integration</h1>
        <p class="description">Integrate with Maximo, SAP PM, IBM Maximo, and other CMMS platforms for maintenance management</p>
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

    <!-- CMMS System Cards -->
    <el-row :gutter="20" class="cmms-cards-row">
      <el-col :xs="24" :sm="12" :lg="8" v-for="cmms in cmmsSystems" :key="cmms.name">
        <el-card class="cmms-card" shadow="hover" @click="selectCMMSSystem(cmms)">
          <div class="cmms-card-content">
            <div class="cmms-icon" :style="{ background: cmms.color }">
              <el-icon :size="32"><component :is="cmms.icon" /></el-icon>
            </div>
            <div class="cmms-info">
              <div class="cmms-name">{{ cmms.name }}</div>
              <div class="cmms-status">
                <el-tag :type="cmms.status === 'Connected' ? 'success' : 'danger'" size="small">
                  {{ cmms.status }}
                </el-tag>
              </div>
              <div class="cmms-version">{{ cmms.version }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Integration Overview -->
    <el-row :gutter="20" class="overview-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Work Order Sync Trend</span>
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
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Integration Status</span>
            </div>
          </template>
          <div class="integration-status">
            <div class="status-item">
              <div class="status-label">API Gateway</div>
              <div class="status-value good">Online</div>
            </div>
            <div class="status-item">
              <div class="status-label">Message Queue</div>
              <div class="status-value good">Online</div>
            </div>
            <div class="status-item">
              <div class="status-label">Database Sync</div>
              <div class="status-value warning">Degraded</div>
            </div>
            <div class="status-item">
              <div class="status-label">Webhook Service</div>
              <div class="status-value good">Online</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Work Order Sync Jobs -->
    <el-card class="jobs-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Work Order Synchronization Jobs</span>
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

      <el-table :data="paginatedJobs" stripe style="width: 100%" v-loading="jobsLoading">
        <el-table-column prop="name" label="Job Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="cmmsSystem" label="CMMS System" width="150">
          <template #default="{ row }">
            <el-tag :type="getCMMSTypeTag(row.cmmsSystem)" size="small">{{ row.cmmsSystem }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="syncType" label="Sync Type" width="130">
          <template #default="{ row }">
            <el-tag :type="row.syncType === 'Real-time' ? 'success' : 'primary'" size="small">
              {{ row.syncType }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="direction" label="Direction" width="120">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'Bidirectional' ? 'warning' : 'info'" size="small">
              {{ row.direction }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="schedule" label="Schedule" width="120" />
        <el-table-column prop="lastSync" label="Last Sync" width="150" />
        <el-table-column prop="recordsSynced" label="Records" width="100" align="right" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Success' ? 'success' : row.status === 'Running' ? 'warning' : 'danger'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
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

    <!-- Work Orders Table -->
    <el-card class="workorders-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Recent Work Orders</span>
          <div class="wo-actions">
            <el-input
                v-model="woSearch"
                placeholder="Search by WO number"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-select v-model="woStatusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Open" value="Open" />
              <el-option label="In Progress" value="In Progress" />
              <el-option label="Completed" value="Completed" />
              <el-option label="Cancelled" value="Cancelled" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchWorkOrders" circle />
          </div>
        </div>
      </template>

      <el-table :data="filteredWorkOrders" stripe style="width: 100%" v-loading="woLoading">
        <el-table-column prop="woNumber" label="WO Number" width="140" />
        <el-table-column prop="title" label="Title" min-width="200" show-overflow-tooltip />
        <el-table-column prop="assetName" label="Asset" width="160" show-overflow-tooltip />
        <el-table-column prop="priority" label="Priority" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="getWOTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scheduledDate" label="Scheduled Date" width="110" />
        <el-table-column prop="assignedTo" label="Assigned To" width="120" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewWorkOrder(row)">View</el-button>
            <el-button link type="success" size="small" @click="syncWorkOrder(row)">Sync</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="woPage"
            v-model:page-size="woPageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            :total="filteredWorkOrders.length"
            @size-change="woPage = 1"
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
        <el-table-column prop="cmmsSystem" label="CMMS System" width="150" />
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
    <el-dialog v-model="connectionDialogVisible" title="Add CMMS Connection" width="600px" destroy-on-close>
      <el-form :model="connectionForm" :rules="connectionRules" ref="connectionFormRef" label-width="130px">
        <el-form-item label="CMMS System" prop="cmmsSystem">
          <el-select v-model="connectionForm.cmmsSystem" style="width: 100%">
            <el-option label="IBM Maximo" value="IBM Maximo" />
            <el-option label="SAP PM" value="SAP PM" />
            <el-option label="Infor EAM" value="Infor EAM" />
            <el-option label="Maintenance Connection" value="Maintenance Connection" />
            <el-option label="Fiix" value="Fiix" />
            <el-option label="UpKeep" value="UpKeep" />
            <el-option label="eMaint" value="eMaint" />
          </el-select>
        </el-form-item>
        <el-form-item label="Connection Name" prop="name">
          <el-input v-model="connectionForm.name" placeholder="Enter connection name" />
        </el-form-item>
        <el-form-item label="API Endpoint" prop="endpoint">
          <el-input v-model="connectionForm.endpoint" placeholder="https://cmms.example.com/api" />
        </el-form-item>
        <el-form-item label="API Key" prop="apiKey">
          <el-input v-model="connectionForm.apiKey" placeholder="Enter API key" />
        </el-form-item>
        <el-form-item label="API Secret" prop="apiSecret">
          <el-input v-model="connectionForm.apiSecret" type="password" placeholder="Enter API secret" />
        </el-form-item>
        <el-form-item label="Organization ID" prop="orgId">
          <el-input v-model="connectionForm.orgId" placeholder="Optional" />
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
        <el-form-item label="CMMS System" prop="cmmsSystem">
          <el-select v-model="jobForm.cmmsSystem" style="width: 100%">
            <el-option label="IBM Maximo" value="IBM Maximo" />
            <el-option label="SAP PM" value="SAP PM" />
            <el-option label="Infor EAM" value="Infor EAM" />
            <el-option label="Maintenance Connection" value="Maintenance Connection" />
          </el-select>
        </el-form-item>
        <el-form-item label="Sync Type" prop="syncType">
          <el-radio-group v-model="jobForm.syncType">
            <el-radio value="Real-time">Real-time</el-radio>
            <el-radio value="Batch">Batch</el-radio>
            <el-radio value="Scheduled">Scheduled</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Direction" prop="direction">
          <el-radio-group v-model="jobForm.direction">
            <el-radio value="IBMS to CMMS">IBMS → CMMS</el-radio>
            <el-radio value="CMMS to IBMS">CMMS → IBMS</el-radio>
            <el-radio value="Bidirectional">Bidirectional</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Entity Type" prop="entityType">
          <el-select v-model="jobForm.entityType" style="width: 100%">
            <el-option label="Work Orders" value="Work Orders" />
            <el-option label="Assets" value="Assets" />
            <el-option label="Maintenance Plans" value="Maintenance Plans" />
            <el-option label="Spare Parts" value="Spare Parts" />
            <el-option label="Labor" value="Labor" />
          </el-select>
        </el-form-item>
        <el-form-item label="Schedule" prop="schedule">
          <el-select v-model="jobForm.schedule" style="width: 100%">
            <el-option label="Manual Only" value="Manual" />
            <el-option label="Every 15 Minutes" value="15min" />
            <el-option label="Every Hour" value="hourly" />
            <el-option label="Daily" value="daily" />
            <el-option label="Weekly" value="weekly" />
          </el-select>
        </el-form-item>
        <el-form-item label="Field Mapping" prop="fieldMapping">
          <el-input v-model="jobForm.fieldMapping" type="textarea" :rows="3" placeholder="JSON field mapping configuration" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="jobDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testJob">Test Connection</el-button>
        <el-button type="success" @click="saveJob">Save Job</el-button>
      </template>
    </el-dialog>

    <!-- Work Order Detail Dialog -->
    <el-dialog v-model="woDetailVisible" :title="`Work Order - ${currentWorkOrder?.woNumber}`" width="700px" destroy-on-close>
      <div class="wo-details" v-if="currentWorkOrder">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="WO Number">{{ currentWorkOrder.woNumber }}</el-descriptions-item>
          <el-descriptions-item label="Title">{{ currentWorkOrder.title }}</el-descriptions-item>
          <el-descriptions-item label="Asset">{{ currentWorkOrder.assetName }}</el-descriptions-item>
          <el-descriptions-item label="Asset ID">{{ currentWorkOrder.assetId }}</el-descriptions-item>
          <el-descriptions-item label="Priority">
            <el-tag :type="getPriorityTag(currentWorkOrder.priority)" size="small">{{ currentWorkOrder.priority }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getWOTag(currentWorkOrder.status)" size="small">{{ currentWorkOrder.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Reported By">{{ currentWorkOrder.reportedBy }}</el-descriptions-item>
          <el-descriptions-item label="Assigned To">{{ currentWorkOrder.assignedTo }}</el-descriptions-item>
          <el-descriptions-item label="Scheduled Date">{{ currentWorkOrder.scheduledDate }}</el-descriptions-item>
          <el-descriptions-item label="Completion Date">{{ currentWorkOrder.completionDate || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentWorkOrder.description }}</el-descriptions-item>
          <el-descriptions-item label="Resolution" :span="2" v-if="currentWorkOrder.resolution">{{ currentWorkOrder.resolution }}</el-descriptions-item>
        </el-descriptions>

        <div class="wo-timeline">
          <h4>Timeline</h4>
          <el-timeline>
            <el-timeline-item
                v-for="event in currentWorkOrder.timeline"
                :key="event.id"
                :timestamp="event.timestamp"
                :type="event.type"
            >
              {{ event.description }}
            </el-timeline-item>
          </el-timeline>
        </div>
      </div>
      <template #footer>
        <el-button @click="woDetailVisible = false">Close</el-button>
        <el-button type="primary" @click="syncWorkOrder(currentWorkOrder)">Sync to CMMS</el-button>
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
          <p><strong>System:</strong> {{ testResult.details.system }}</p>
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
  Delete, Connection, Edit, DataAnalysis, Monitor, Share,
  Tools, List
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing CMMS integrations...', 'Loading work orders...', 'Almost ready...']

// ==================== Chart References ====================
const trendChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null

// ==================== State ====================
const jobsLoading = ref(false)
const woLoading = ref(false)
const historyLoading = ref(false)
const connectionDialogVisible = ref(false)
const jobDialogVisible = ref(false)
const woDetailVisible = ref(false)
const testDialogVisible = ref(false)
const currentWorkOrder = ref<any>(null)
const woSearch = ref('')
const woStatusFilter = ref('')
const trendPeriod = ref('daily')
const jobsPage = ref(1)
const jobsPageSize = ref(10)
const woPage = ref(1)
const woPageSize = ref(10)
const historyPage = ref(1)
const historyPageSize = ref(10)
const historyDateRange = ref<[Date, Date] | null>(null)

const connectionFormRef = ref()
const jobFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'CMMS Systems', value: '3', trend: 0, icon: 'Connection', bgColor: '#409eff', key: 'systems', subTitle: 'All Connected' },
  { title: 'Sync Jobs', value: '8', trend: 2, icon: 'Document', bgColor: '#67c23a', key: 'jobs', subTitle: 'Active: 7' },
  { title: 'Work Orders', value: '156', trend: 12, icon: 'List', bgColor: '#e6a23c', key: 'workorders', subTitle: 'Open: 42' },
  { title: 'Sync Success', value: '98.5%', trend: 1.2, icon: 'Checked', bgColor: '#f56c6c', key: 'success', subTitle: 'Last 30 days' }
])

const cmmsSystems = ref([
  { name: 'IBM Maximo', icon: 'DataAnalysis', color: '#409eff', status: 'Connected', version: '7.6.1.2' },
  { name: 'SAP PM', icon: 'Monitor', color: '#f56c6c', status: 'Connected', version: '2023' },
  { name: 'Maintenance Connection', icon: 'Tools', color: '#67c23a', status: 'Connected', version: '9.0' }
])

const syncJobs = ref([
  { id: 1, name: 'Work Order Sync - Maximo', cmmsSystem: 'IBM Maximo', syncType: 'Real-time', direction: 'Bidirectional', entityType: 'Work Orders', schedule: 'Continuous', lastSync: '2024-01-20 10:30:00', recordsSynced: 12450, status: 'Success' },
  { id: 2, name: 'Asset Sync - SAP PM', cmmsSystem: 'SAP PM', syncType: 'Batch', direction: 'CMMS to IBMS', entityType: 'Assets', schedule: 'Hourly', lastSync: '2024-01-20 10:00:00', recordsSynced: 345, status: 'Success' },
  { id: 3, name: 'Maintenance Plan Sync', cmmsSystem: 'IBM Maximo', syncType: 'Scheduled', direction: 'IBMS to CMMS', entityType: 'Maintenance Plans', schedule: 'Daily', lastSync: '2024-01-20 01:00:00', recordsSynced: 56, status: 'Running' },
  { id: 4, name: 'Spare Parts Sync', cmmsSystem: 'Maintenance Connection', syncType: 'Batch', direction: 'Bidirectional', entityType: 'Spare Parts', schedule: 'Weekly', lastSync: '2024-01-19 00:00:00', recordsSynced: 234, status: 'Failed' }
])

const workOrders = ref([
  { id: 1, woNumber: 'WO-001', title: 'Chiller-01 Compressor Replacement', assetName: 'Chiller-01', assetId: 'CH-001', priority: 'Critical', status: 'In Progress', reportedBy: 'John Smith', assignedTo: 'Mike Johnson', scheduledDate: '2024-01-20', completionDate: null, description: 'Compressor failure requiring replacement', resolution: null, timeline: [{ id: 1, timestamp: '2024-01-19 08:00:00', description: 'Work order created', type: 'primary' }, { id: 2, timestamp: '2024-01-19 09:00:00', description: 'Assigned to Mike Johnson', type: 'primary' }, { id: 3, timestamp: '2024-01-20 08:00:00', description: 'Work started', type: 'success' }] },
  { id: 2, woNumber: 'WO-002', title: 'AHU-03 Filter Replacement', assetName: 'AHU-03', assetId: 'AHU-003', priority: 'Medium', status: 'Completed', reportedBy: 'Lisa Zhang', assignedTo: 'David Wang', scheduledDate: '2024-01-18', completionDate: '2024-01-18', description: 'Scheduled filter replacement', resolution: 'Filters replaced successfully', timeline: [] },
  { id: 3, woNumber: 'WO-003', title: 'UPS Battery Testing', assetName: 'UPS-01', assetId: 'UPS-001', priority: 'High', status: 'Open', reportedBy: 'Tom Harris', assignedTo: 'John Smith', scheduledDate: '2024-01-21', completionDate: null, description: 'Quarterly battery capacity testing', resolution: null, timeline: [] },
  { id: 4, woNumber: 'WO-004', title: 'Cooling Tower Fan Repair', assetName: 'CT-02', assetId: 'CT-002', priority: 'High', status: 'In Progress', reportedBy: 'Mike Johnson', assignedTo: 'Robert Liu', scheduledDate: '2024-01-19', completionDate: null, description: 'Fan bearing noise investigation', resolution: null, timeline: [] },
  { id: 5, woNumber: 'WO-005', title: 'VAV Box Calibration', assetName: 'VAV-101', assetId: 'VAV-101', priority: 'Low', status: 'Completed', reportedBy: 'David Wang', assignedTo: 'Lisa Zhang', scheduledDate: '2024-01-15', completionDate: '2024-01-16', description: 'Annual VAV calibration', resolution: 'Calibration completed', timeline: [] }
])

const syncHistory = ref([
  { id: 1, timestamp: '2024-01-20 10:30:00', jobName: 'Work Order Sync - Maximo', cmmsSystem: 'IBM Maximo', recordsProcessed: 12450, duration: '2 min 34 sec', status: 'Success', message: 'Sync completed successfully' },
  { id: 2, timestamp: '2024-01-20 10:00:00', jobName: 'Asset Sync - SAP PM', cmmsSystem: 'SAP PM', recordsProcessed: 345, duration: '1 min 12 sec', status: 'Success', message: 'Sync completed successfully' },
  { id: 3, timestamp: '2024-01-20 01:00:00', jobName: 'Maintenance Plan Sync', cmmsSystem: 'IBM Maximo', recordsProcessed: 56, duration: '45 sec', status: 'Running', message: 'Sync in progress' },
  { id: 4, timestamp: '2024-01-19 00:00:00', jobName: 'Spare Parts Sync', cmmsSystem: 'Maintenance Connection', recordsProcessed: 234, duration: '1 min 20 sec', status: 'Failed', message: 'API rate limit exceeded' }
])

// ==================== Computed ====================
const filteredWorkOrders = computed(() => {
  let filtered = [...workOrders.value]
  if (woSearch.value) filtered = filtered.filter(wo => wo.woNumber.toLowerCase().includes(woSearch.value.toLowerCase()))
  if (woStatusFilter.value) filtered = filtered.filter(wo => wo.status === woStatusFilter.value)
  return filtered
})

const paginatedJobs = computed(() => {
  const start = (jobsPage.value - 1) * jobsPageSize.value
  const end = start + jobsPageSize.value
  return syncJobs.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getCMMSTypeTag = (cmmsSystem: string) => {
  const map: Record<string, string> = {
    'IBM Maximo': 'primary',
    'SAP PM': 'danger',
    'Maintenance Connection': 'success',
    'Infor EAM': 'warning'
  }
  return map[cmmsSystem] || 'info'
}

const getPriorityTag = (priority: string) => {
  const map: Record<string, string> = {
    'Critical': 'danger',
    'High': 'warning',
    'Medium': 'info',
    'Low': 'success'
  }
  return map[priority] || 'info'
}

const getWOTag = (status: string) => {
  const map: Record<string, string> = {
    'Open': 'danger',
    'In Progress': 'warning',
    'Completed': 'success',
    'Cancelled': 'info'
  }
  return map[status] || 'info'
}

const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting CMMS integration logs...')
}

const selectCMMSSystem = (cmms: any) => {
  ElMessage.info(`Selected ${cmms.name} - ${cmms.status}`)
}

const fetchJobs = () => {
  jobsLoading.value = true
  setTimeout(() => {
    jobsLoading.value = false
    ElMessage.success('Jobs refreshed')
  }, 500)
}

const fetchWorkOrders = () => {
  woLoading.value = true
  setTimeout(() => {
    woLoading.value = false
    ElMessage.success('Work orders refreshed')
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
    testResult.message = 'Successfully connected to CMMS system'
    testResult.details = {
      system: connectionForm.cmmsSystem,
      version: '2023.1',
      responseTime: 234
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
  ElMessage.info(`Viewing details for job: ${job.name}`)
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

const viewWorkOrder = (wo: any) => {
  currentWorkOrder.value = wo
  woDetailVisible.value = true
}

const syncWorkOrder = (wo: any) => {
  ElMessage.info(`Synchronizing work order ${wo.woNumber} to CMMS...`)
  setTimeout(() => {
    ElMessage.success(`Work order ${wo.woNumber} synchronized successfully`)
  }, 1500)
}

// ==================== Chart Initializations ====================
const initTrendChart = () => {
  if (!trendChartRef.value) return
  if (trendChart) trendChart.dispose()

  trendChart = echarts.init(trendChartRef.value)

  const dailyData = [12, 15, 18, 22, 20, 25, 28, 30, 32, 28, 35, 38, 40, 42, 45, 48, 50, 52, 55, 58, 60, 62, 65, 68, 70, 72, 75, 78, 80, 82]
  const weeklyData = [85, 92, 98, 105, 112, 118, 125, 132, 138, 145, 152, 158]

  const data = trendPeriod.value === 'daily' ? dailyData : weeklyData
  const xAxisData = trendPeriod.value === 'daily'
      ? Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
      : ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8', 'Week 9', 'Week 10', 'Week 11', 'Week 12']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData },
    yAxis: { type: 'value', name: 'Work Orders' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 6
    }]
  }

  trendChart.setOption(option)
  window.addEventListener('resize', () => trendChart?.resize())
}

// ==================== Forms ====================
const connectionForm = reactive({
  cmmsSystem: '',
  name: '',
  endpoint: '',
  apiKey: '',
  apiSecret: '',
  orgId: '',
  description: ''
})

const jobForm = reactive({
  name: '',
  cmmsSystem: '',
  syncType: 'Scheduled',
  direction: 'Bidirectional',
  entityType: '',
  schedule: 'daily',
  fieldMapping: ''
})

const connectionRules = {
  cmmsSystem: [{ required: true, message: 'Please select CMMS system', trigger: 'change' }],
  name: [{ required: true, message: 'Please enter connection name', trigger: 'blur' }],
  endpoint: [{ required: true, message: 'Please enter API endpoint', trigger: 'blur' }],
  apiKey: [{ required: true, message: 'Please enter API key', trigger: 'blur' }],
  apiSecret: [{ required: true, message: 'Please enter API secret', trigger: 'blur' }]
}

const jobRules = {
  name: [{ required: true, message: 'Please enter job name', trigger: 'blur' }],
  cmmsSystem: [{ required: true, message: 'Please select CMMS system', trigger: 'change' }],
  entityType: [{ required: true, message: 'Please select entity type', trigger: 'change' }]
}

// ==================== Mounted ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initTrendChart()
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
      fetchWorkOrders()
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

.cmms-integration-page {
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

.cmms-cards-row { margin-bottom: 20px; }
.cmms-card { cursor: pointer; transition: all 0.3s; }
.cmms-card:hover { transform: translateY(-4px); }
.cmms-card .cmms-card-content { display: flex; gap: 16px; align-items: center; }
.cmms-card .cmms-icon { width: 60px; height: 60px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; }
.cmms-card .cmms-info { flex: 1; }
.cmms-card .cmms-name { font-size: 18px; font-weight: 600; margin-bottom: 8px; }
.cmms-card .cmms-version { font-size: 12px; color: #909399; margin-top: 4px; }

.overview-row { margin-bottom: 20px; }
.chart-card, .stats-card { margin-bottom: 20px; }
.chart-card .card-header, .stats-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.chart-container { width: 100%; height: 320px; }

.integration-status { padding: 8px; }
.status-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #ebeef5; }
.status-item:last-child { border-bottom: none; }
.status-label { font-size: 14px; color: #606266; }
.status-value { font-size: 14px; font-weight: 500; }
.status-value.good { color: #67c23a; }
.status-value.warning { color: #e6a23c; }
.status-value.bad { color: #f56c6c; }

.jobs-card, .workorders-card, .history-card { margin-bottom: 20px; }
.jobs-card .card-header, .workorders-card .card-header, .history-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.jobs-card .jobs-actions, .workorders-card .wo-actions, .history-card .history-controls { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.wo-details .wo-timeline { margin-top: 20px; }
.wo-details .wo-timeline h4 { margin-bottom: 12px; }

.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
</style>