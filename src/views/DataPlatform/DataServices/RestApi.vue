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
        <div class="loading-tip">REST API Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="rest-api-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Services</el-breadcrumb-item>
            <el-breadcrumb-item>REST API</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>REST API Management</h1>
        <p class="description">Manage, test, and monitor REST API endpoints for data platform services</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export OpenAPI
        </el-button>
        <el-button type="primary" @click="handleCreateAPI">
          <el-icon><Plus /></el-icon>
          Create API
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
        </el-card>
      </el-col>
    </el-row>

    <!-- API Usage Chart -->
    <el-card class="chart-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>API Request Volume</span>
          <el-radio-group v-model="chartPeriod" size="small">
            <el-radio-button value="hourly">Hourly</el-radio-button>
            <el-radio-button value="daily">Daily</el-radio-button>
            <el-radio-button value="weekly">Weekly</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="usageChartRef" class="chart-container"></div>
    </el-card>

    <!-- API Endpoints Table -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>API Endpoints ({{ filteredEndpoints.length }} endpoints)</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search endpoints"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-button :icon="Refresh" @click="fetchEndpoints" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedEndpoints" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="API Name" min-width="180" show-overflow-tooltip />
        <el-table-column prop="method" label="Method" width="100">
          <template #default="{ row }">
            <el-tag :type="getMethodTag(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="Path" min-width="220" show-overflow-tooltip />
        <el-table-column prop="version" label="Version" width="80" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="requests" label="Requests (24h)" width="120" align="right">
          <template #default="{ row }">
            {{ row.requests.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column prop="avgLatency" label="Avg Latency (ms)" width="130" align="right">
          <template #default="{ row }">
            {{ row.avgLatency }}
          </template>
        </el-table-column>
        <el-table-column prop="errorRate" label="Error Rate" width="100" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.errorRate > 5 ? '#f56c6c' : '#67c23a' }">{{ row.errorRate }}%</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="220" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testAPI(row)">Test</el-button>
            <el-button link type="success" size="small" @click="viewDocs(row)">Docs</el-button>
            <el-button link type="info" size="small" @click="viewMetrics(row)">Metrics</el-button>
            <el-button link type="danger" size="small" @click="deleteAPI(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[15, 30, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredEndpoints.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- API Test Dialog -->
    <el-dialog v-model="testDialogVisible" title="API Test Console" width="800px" destroy-on-close>
      <div class="api-test-console">
        <div class="test-request">
          <el-form :model="testForm" label-width="80px">
            <el-form-item label="Method">
              <el-select v-model="testForm.method" style="width: 120px">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
            <el-form-item label="URL">
              <el-input v-model="testForm.url" placeholder="https://api.example.com/v1/endpoint" />
            </el-form-item>
            <el-form-item label="Headers">
              <div class="headers-editor">
                <div v-for="(header, index) in testForm.headers" :key="index" class="header-row">
                  <el-input v-model="header.key" placeholder="Header name" style="width: 200px" />
                  <el-input v-model="header.value" placeholder="Header value" style="width: 300px; margin-left: 8px" />
                  <el-button link type="danger" @click="removeHeader(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <el-button size="small" @click="addHeader">+ Add Header</el-button>
              </div>
            </el-form-item>
            <el-form-item label="Body" v-if="testForm.method !== 'GET'">
              <el-select v-model="testForm.bodyType" size="small" style="width: 120px; margin-bottom: 8px">
                <el-option label="JSON" value="json" />
                <el-option label="Form Data" value="form" />
                <el-option label="Raw" value="raw" />
              </el-select>
              <el-input
                  v-model="testForm.body"
                  type="textarea"
                  :rows="6"
                  placeholder='{"key": "value"}'
              />
            </el-form-item>
          </el-form>
          <div class="test-actions">
            <el-button type="primary" @click="sendRequest" :loading="sending">
              <el-icon><CaretRight /></el-icon>
              Send Request
            </el-button>
            <el-button @click="clearTest">Clear</el-button>
          </div>
        </div>

        <div class="test-response" v-if="testResponse">
          <el-tabs>
            <el-tab-pane label="Response">
              <div class="response-status">
                <el-tag :type="testResponse.status >= 200 && testResponse.status < 300 ? 'success' : 'danger'">
                  Status: {{ testResponse.status }} {{ testResponse.statusText }}
                </el-tag>
                <span class="response-time">Time: {{ testResponse.time }}ms</span>
              </div>
              <pre class="response-body">{{ JSON.stringify(testResponse.data, null, 2) }}</pre>
            </el-tab-pane>
            <el-tab-pane label="Headers">
              <pre class="response-headers">{{ JSON.stringify(testResponse.headers, null, 2) }}</pre>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
      <template #footer>
        <el-button @click="testDialogVisible = false">Close</el-button>
      </template>
    </el-dialog>

    <!-- API Details Dialog -->
    <el-dialog v-model="docsDialogVisible" :title="`API Documentation - ${currentAPI?.name}`" width="700px" destroy-on-close>
      <div class="api-docs" v-if="currentAPI">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="API Name">{{ currentAPI.name }}</el-descriptions-item>
          <el-descriptions-item label="Method">
            <el-tag :type="getMethodTag(currentAPI.method)" size="small">{{ currentAPI.method }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Path">{{ currentAPI.path }}</el-descriptions-item>
          <el-descriptions-item label="Version">{{ currentAPI.version }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentAPI.status === 'Active' ? 'success' : 'info'" size="small">{{ currentAPI.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Rate Limit">{{ currentAPI.rateLimit || '1000/hour' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentAPI.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="docs-parameters">
          <h4>Request Parameters</h4>
          <el-table :data="currentAPI.parameters || []" size="small" border>
            <el-table-column prop="name" label="Name" width="150" />
            <el-table-column prop="in" label="In" width="80" />
            <el-table-column prop="type" label="Type" width="100" />
            <el-table-column prop="required" label="Required" width="80">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'" size="small">{{ row.required ? 'Yes' : 'No' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="Description" min-width="200" />
          </el-table>
        </div>

        <div class="docs-response">
          <h4>Response Schema</h4>
          <pre class="response-schema">{{ JSON.stringify(currentAPI.responseSchema, null, 2) }}</pre>
        </div>

        <div class="docs-example">
          <h4>Example Request</h4>
          <pre class="example-code">{{ currentAPI.exampleRequest }}</pre>
        </div>

        <div class="docs-example">
          <h4>Example Response</h4>
          <pre class="example-code">{{ currentAPI.exampleResponse }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button @click="docsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="testAPI(currentAPI)">Test API</el-button>
        <el-button @click="exportOpenAPISpec">Export OpenAPI</el-button>
      </template>
    </el-dialog>

    <!-- Metrics Dialog -->
    <el-dialog v-model="metricsDialogVisible" :title="`API Metrics - ${currentAPI?.name}`" width="800px" destroy-on-close>
      <div class="api-metrics" v-if="currentAPI">
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-value">{{ currentAPI.requests?.toLocaleString() || '0' }}</div>
              <div class="metric-label">Total Requests</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-value">{{ currentAPI.avgLatency || '0' }} ms</div>
              <div class="metric-label">Avg Latency</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-value">{{ currentAPI.errorRate || '0' }}%</div>
              <div class="metric-label">Error Rate</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="metric-card">
              <div class="metric-value">{{ currentAPI.availability || '99.95' }}%</div>
              <div class="metric-label">Availability</div>
            </div>
          </el-col>
        </el-row>

        <div class="metrics-chart">
          <h4>Request Trend (Last 24 Hours)</h4>
          <div ref="metricsChartRef" class="metrics-chart-container"></div>
        </div>

        <div class="status-codes">
          <h4>Status Code Distribution</h4>
          <el-table :data="currentAPI.statusCodes || []" size="small" border>
            <el-table-column prop="code" label="Status Code" width="120" />
            <el-table-column prop="count" label="Count" width="150" align="right" />
            <el-table-column prop="percentage" label="Percentage" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.percentage" :stroke-width="8" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="metricsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportMetrics">Export Metrics</el-button>
      </template>
    </el-dialog>

    <!-- Create API Dialog -->
    <el-dialog v-model="createDialogVisible" title="Create API Endpoint" width="650px" destroy-on-close>
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
        <el-form-item label="API Name" prop="name">
          <el-input v-model="createForm.name" placeholder="Enter API name" />
        </el-form-item>
        <el-form-item label="Method" prop="method">
          <el-select v-model="createForm.method" style="width: 100%">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
            <el-option label="PATCH" value="PATCH" />
          </el-select>
        </el-form-item>
        <el-form-item label="Path" prop="path">
          <el-input v-model="createForm.path" placeholder="/api/v1/resource" />
        </el-form-item>
        <el-form-item label="Version" prop="version">
          <el-input v-model="createForm.version" placeholder="v1" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="createForm.description" type="textarea" :rows="2" placeholder="Enter API description" />
        </el-form-item>
        <el-form-item label="Rate Limit" prop="rateLimit">
          <el-input v-model="createForm.rateLimit" placeholder="1000/hour" />
        </el-form-item>
        <el-form-item label="Status" prop="status">
          <el-radio-group v-model="createForm.status">
            <el-radio value="Active">Active</el-radio>
            <el-radio value="Inactive">Inactive</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitCreate">Create API</el-button>
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
  Delete, CaretRight
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading API endpoints...',
  'Fetching metrics...',
  'Almost ready...'
]

// ==================== Chart References ====================
const usageChartRef = ref<HTMLElement>()
const metricsChartRef = ref<HTMLElement>()
let usageChart: echarts.ECharts | null = null
let metricsChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const testDialogVisible = ref(false)
const docsDialogVisible = ref(false)
const metricsDialogVisible = ref(false)
const createDialogVisible = ref(false)
const sending = ref(false)
const currentAPI = ref<any>(null)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(15)
const chartPeriod = ref('hourly')
const createFormRef = ref()

const testForm = reactive({
  method: 'GET',
  url: '',
  headers: [{ key: 'Content-Type', value: 'application/json' }],
  bodyType: 'json',
  body: ''
})

const testResponse = ref<any>(null)

const createForm = reactive({
  name: '',
  method: 'GET',
  path: '',
  version: 'v1',
  description: '',
  rateLimit: '1000/hour',
  status: 'Active'
})

const createRules = {
  name: [{ required: true, message: 'Please enter API name', trigger: 'blur' }],
  method: [{ required: true, message: 'Please select method', trigger: 'change' }],
  path: [{ required: true, message: 'Please enter path', trigger: 'blur' }]
}

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Total APIs', value: 48, trend: 12, icon: 'Document', bgColor: '#409eff', key: 'total' },
  { title: 'Active APIs', value: 42, trend: 8, icon: 'Checked', bgColor: '#67c23a', key: 'active' },
  { title: 'Total Requests', value: '2.45M', trend: 18, icon: 'TrendCharts', bgColor: '#e6a23c', key: 'requests' },
  { title: 'Avg Latency', value: '124ms', trend: -5, icon: 'Clock', bgColor: '#f56c6c', key: 'latency' }
])

const apiEndpoints = ref([
  {
    id: 1,
    name: 'Get Devices',
    method: 'GET',
    path: '/api/v1/devices',
    version: 'v1',
    status: 'Active',
    requests: 125000,
    avgLatency: 45,
    errorRate: 0.2,
    description: 'Retrieve all devices with optional filters',
    rateLimit: '10000/hour',
    parameters: [
      { name: 'limit', in: 'query', type: 'integer', required: false, description: 'Max number of results' },
      { name: 'offset', in: 'query', type: 'integer', required: false, description: 'Pagination offset' },
      { name: 'status', in: 'query', type: 'string', required: false, description: 'Filter by device status' }
    ],
    responseSchema: {
      type: 'object',
      properties: {
        data: { type: 'array', items: { type: 'object' } },
        total: { type: 'integer' },
        limit: { type: 'integer' },
        offset: { type: 'integer' }
      }
    },
    exampleRequest: 'curl -X GET "https://api.ibms.com/api/v1/devices?limit=10&status=active"',
    exampleResponse: '{\n  "data": [...],\n  "total": 156,\n  "limit": 10,\n  "offset": 0\n}',
    statusCodes: [
      { code: 200, count: 124500, percentage: 99.6 },
      { code: 400, count: 300, percentage: 0.24 },
      { code: 401, count: 100, percentage: 0.08 },
      { code: 500, count: 100, percentage: 0.08 }
    ],
    availability: 99.95
  },
  {
    id: 2,
    name: 'Create Device',
    method: 'POST',
    path: '/api/v1/devices',
    version: 'v1',
    status: 'Active',
    requests: 12500,
    avgLatency: 78,
    errorRate: 0.5,
    description: 'Create a new device',
    rateLimit: '1000/hour',
    parameters: [
      { name: 'device', in: 'body', type: 'object', required: true, description: 'Device object' }
    ],
    responseSchema: {
      type: 'object',
      properties: {
        id: { type: 'string' },
        name: { type: 'string' },
        created_at: { type: 'string' }
      }
    },
    exampleRequest: 'curl -X POST "https://api.ibms.com/api/v1/devices" -d \'{"name":"New Device"}\'',
    exampleResponse: '{\n  "id": "DEV-001",\n  "name": "New Device",\n  "created_at": "2024-01-20T10:00:00Z"\n}',
    statusCodes: [
      { code: 201, count: 12400, percentage: 99.2 },
      { code: 400, count: 100, percentage: 0.8 }
    ],
    availability: 99.98
  },
  {
    id: 3,
    name: 'Get Device by ID',
    method: 'GET',
    path: '/api/v1/devices/{id}',
    version: 'v1',
    status: 'Active',
    requests: 245000,
    avgLatency: 32,
    errorRate: 0.1,
    description: 'Get a specific device by ID',
    rateLimit: '10000/hour',
    parameters: [
      { name: 'id', in: 'path', type: 'string', required: true, description: 'Device ID' }
    ],
    responseSchema: {
      type: 'object',
      properties: {
        id: { type: 'string' },
        name: { type: 'string' },
        type: { type: 'string' },
        status: { type: 'string' }
      }
    },
    exampleRequest: 'curl -X GET "https://api.ibms.com/api/v1/devices/DEV-001"',
    exampleResponse: '{\n  "id": "DEV-001",\n  "name": "Chiller-01",\n  "type": "HVAC",\n  "status": "active"\n}',
    statusCodes: [
      { code: 200, count: 244500, percentage: 99.8 },
      { code: 404, count: 500, percentage: 0.2 }
    ],
    availability: 99.99
  },
  {
    id: 4,
    name: 'Update Device',
    method: 'PUT',
    path: '/api/v1/devices/{id}',
    version: 'v1',
    status: 'Active',
    requests: 8500,
    avgLatency: 95,
    errorRate: 0.8,
    description: 'Update an existing device',
    rateLimit: '1000/hour',
    parameters: [
      { name: 'id', in: 'path', type: 'string', required: true, description: 'Device ID' },
      { name: 'device', in: 'body', type: 'object', required: true, description: 'Updated device object' }
    ],
    responseSchema: {
      type: 'object',
      properties: {
        id: { type: 'string' },
        name: { type: 'string' },
        updated_at: { type: 'string' }
      }
    },
    exampleRequest: 'curl -X PUT "https://api.ibms.com/api/v1/devices/DEV-001" -d \'{"name":"Updated Name"}\'',
    exampleResponse: '{\n  "id": "DEV-001",\n  "name": "Updated Name",\n  "updated_at": "2024-01-20T10:00:00Z"\n}',
    statusCodes: [
      { code: 200, count: 8430, percentage: 99.2 },
      { code: 400, count: 70, percentage: 0.8 }
    ],
    availability: 99.95
  },
  {
    id: 5,
    name: 'Delete Device',
    method: 'DELETE',
    path: '/api/v1/devices/{id}',
    version: 'v1',
    status: 'Active',
    requests: 1200,
    avgLatency: 65,
    errorRate: 0.3,
    description: 'Delete a device',
    rateLimit: '500/hour',
    parameters: [
      { name: 'id', in: 'path', type: 'string', required: true, description: 'Device ID' }
    ],
    responseSchema: {
      type: 'object',
      properties: {
        message: { type: 'string' }
      }
    },
    exampleRequest: 'curl -X DELETE "https://api.ibms.com/api/v1/devices/DEV-001"',
    exampleResponse: '{\n  "message": "Device deleted successfully"\n}',
    statusCodes: [
      { code: 200, count: 1196, percentage: 99.7 },
      { code: 404, count: 4, percentage: 0.3 }
    ],
    availability: 99.99
  },
  {
    id: 6,
    name: 'Get Telemetry Data',
    method: 'GET',
    path: '/api/v1/telemetry',
    version: 'v2',
    status: 'Active',
    requests: 890000,
    avgLatency: 120,
    errorRate: 0.5,
    description: 'Query historical telemetry data',
    rateLimit: '5000/hour',
    parameters: [
      { name: 'device_id', in: 'query', type: 'string', required: true, description: 'Device ID' },
      { name: 'start_time', in: 'query', type: 'string', required: true, description: 'Start timestamp' },
      { name: 'end_time', in: 'query', type: 'string', required: true, description: 'End timestamp' },
      { name: 'resolution', in: 'query', type: 'string', required: false, description: 'Data resolution' }
    ],
    responseSchema: {
      type: 'object',
      properties: {
        data: { type: 'array' },
        device_id: { type: 'string' },
        count: { type: 'integer' }
      }
    },
    exampleRequest: 'curl -X GET "https://api.ibms.com/api/v2/telemetry?device_id=DEV-001&start_time=2024-01-01T00:00:00Z&end_time=2024-01-02T00:00:00Z"',
    exampleResponse: '{\n  "data": [...],\n  "device_id": "DEV-001",\n  "count": 1440\n}',
    statusCodes: [
      { code: 200, count: 885000, percentage: 99.44 },
      { code: 400, count: 3000, percentage: 0.34 },
      { code: 429, count: 2000, percentage: 0.22 }
    ],
    availability: 99.9
  }
])

// ==================== Computed ====================
const filteredEndpoints = computed(() => {
  if (!searchKeyword.value) return apiEndpoints.value
  return apiEndpoints.value.filter(e =>
      e.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      e.path.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const paginatedEndpoints = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredEndpoints.value.slice(start, end)
})

// ==================== Helper Methods ====================
const getMethodTag = (method: string) => {
  const map: Record<string, string> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger',
    'PATCH': 'info'
  }
  return map[method] || 'info'
}

// ==================== Chart Initializations ====================
const initUsageChart = () => {
  if (!usageChartRef.value) return
  if (usageChart) usageChart.dispose()

  usageChart = echarts.init(usageChartRef.value)

  const hourlyData = [1250, 1420, 1380, 1560, 1890, 2100, 2450, 2670, 2890, 3120, 2980, 2750, 2650, 2580, 2620, 2780, 2950, 3100, 3250, 2980, 2450, 1980, 1650, 1320]
  const dailyData = Array.from({ length: 30 }, () => Math.floor(Math.random() * 50000) + 30000)
  const weeklyData = [245000, 268000, 289000, 312000, 298000, 275000, 256000]

  let data, xAxisData
  if (chartPeriod.value === 'hourly') {
    data = hourlyData
    xAxisData = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  } else if (chartPeriod.value === 'daily') {
    data = dailyData
    xAxisData = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`)
  } else {
    data = weeklyData
    xAxisData = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7']
  }

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: chartPeriod.value === 'daily' ? 45 : 0 } },
    yAxis: { type: 'value', name: 'Requests' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 6
    }]
  }

  usageChart.setOption(option)
  window.addEventListener('resize', () => usageChart?.resize())
}

const initMetricsChart = () => {
  if (!metricsChartRef.value) return
  if (metricsChart) metricsChart.dispose()

  metricsChart = echarts.init(metricsChartRef.value)

  const hourlyRequests = [1250, 1420, 1380, 1560, 1890, 2100, 2450, 2670, 2890, 3120, 2980, 2750]
  const hourlyLatency = [45, 48, 52, 50, 55, 58, 62, 60, 65, 68, 66, 64]

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Requests', 'Latency (ms)'], bottom: 0 },
    xAxis: { type: 'category', data: Array.from({ length: 12 }, (_, i) => `${i}:00`) },
    yAxis: [{ type: 'value', name: 'Requests' }, { type: 'value', name: 'Latency (ms)' }],
    series: [
      { name: 'Requests', type: 'line', data: hourlyRequests, smooth: true, lineStyle: { width: 2, color: '#409eff' }, yAxisIndex: 0 },
      { name: 'Latency (ms)', type: 'line', data: hourlyLatency, smooth: true, lineStyle: { width: 2, color: '#f56c6c' }, yAxisIndex: 1 }
    ]
  }

  metricsChart.setOption(option)
  window.addEventListener('resize', () => metricsChart?.resize())
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting OpenAPI specification...')
}

const handleCreateAPI = () => {
  createDialogVisible.value = true
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchEndpoints = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const testAPI = (api: any) => {
  currentAPI.value = api
  testForm.method = api.method
  testForm.url = `https://api.ibms.com${api.path}`
  testForm.headers = [{ key: 'Content-Type', value: 'application/json' }]
  testForm.body = ''
  testResponse.value = null
  testDialogVisible.value = true
}

const sendRequest = () => {
  sending.value = true
  setTimeout(() => {
    sending.value = false
    testResponse.value = {
      status: 200,
      statusText: 'OK',
      time: Math.floor(Math.random() * 100) + 20,
      data: { message: 'Request successful', data: { id: 'DEV-001', name: 'Test Device' } },
      headers: { 'content-type': 'application/json', 'x-request-id': 'req_12345' }
    }
    ElMessage.success('Request completed')
  }, 1500)
}

const clearTest = () => {
  testForm.body = ''
  testResponse.value = null
}

const addHeader = () => {
  testForm.headers.push({ key: '', value: '' })
}

const removeHeader = (index: number) => {
  testForm.headers.splice(index, 1)
}

const viewDocs = (api: any) => {
  currentAPI.value = api
  docsDialogVisible.value = true
}

const viewMetrics = (api: any) => {
  currentAPI.value = api
  metricsDialogVisible.value = true
  nextTick(() => {
    initMetricsChart()
  })
}

const deleteAPI = (api: any) => {
  ElMessageBox.confirm(`Delete API "${api.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = apiEndpoints.value.findIndex(e => e.id === api.id)
    if (index !== -1) {
      apiEndpoints.value.splice(index, 1)
      ElMessage.success(`Deleted: ${api.name}`)
    }
  }).catch(() => {})
}

const exportOpenAPISpec = () => {
  ElMessage.success('Exporting OpenAPI specification...')
}

const exportMetrics = () => {
  ElMessage.success('Exporting metrics data...')
}

const submitCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const newAPI = {
        id: apiEndpoints.value.length + 1,
        name: createForm.name,
        method: createForm.method,
        path: createForm.path,
        version: createForm.version,
        status: createForm.status,
        requests: 0,
        avgLatency: 0,
        errorRate: 0,
        description: createForm.description,
        rateLimit: createForm.rateLimit
      }
      apiEndpoints.value.push(newAPI)
      ElMessage.success('API created successfully')
      createDialogVisible.value = false
      createFormRef.value?.resetFields()
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
    initUsageChart()
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
      fetchEndpoints()
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
.rest-api-page {
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

.chart-card {
  margin-bottom: 20px;

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

.table-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  .table-actions {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.api-test-console {
  .test-request {
    .headers-editor {
      .header-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
      }
    }

    .test-actions {
      margin-top: 16px;
      text-align: right;
    }
  }

  .test-response {
    margin-top: 24px;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;

    .response-status {
      display: flex;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .response-body, .response-headers {
      background: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      font-family: monospace;
      font-size: 12px;
      overflow-x: auto;
      max-height: 300px;
    }
  }
}

.api-docs {
  .docs-parameters, .docs-response, .docs-example {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .response-schema, .example-code {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    overflow-x: auto;
  }
}

.api-metrics {
  .metric-card {
    text-align: center;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 8px;

    .metric-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }

    .metric-label {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }

  .metrics-chart {
    margin-top: 20px;

    h4 {
      margin-bottom: 12px;
      color: #303133;
    }
  }

  .metrics-chart-container {
    width: 100%;
    height: 300px;
  }

  .status-codes {
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