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
        <div class="loading-tip">REST API Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="restapi-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>REST API</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>REST API Gateway Management</h1>
        <p class="description">Manage REST API endpoints, authentication, request/response mapping, and data integration</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export OpenAPI
        </el-button>
        <el-button type="primary" @click="openAddEndpointDialog">
          <el-icon><Plus /></el-icon>
          Add Endpoint
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

    <!-- API Endpoints Table -->
    <el-card class="endpoints-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>REST API Endpoints</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or URL"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="methodFilter" placeholder="Method" clearable style="width: 120px">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
              <el-option label="PATCH" value="PATCH" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Active" value="Active" />
              <el-option label="Inactive" value="Inactive" />
              <el-option label="Error" value="Error" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchEndpoints" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedEndpoints" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Endpoint Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="method" label="Method" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodTag(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="URL" min-width="250" show-overflow-tooltip />
        <el-table-column prop="authType" label="Auth" width="100">
          <template #default="{ row }">
            <el-tag :type="row.authType === 'None' ? 'info' : 'success'" size="small">{{ row.authType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pollingInterval" label="Interval" width="90" align="center">
          <template #default="{ row }">
            {{ row.pollingInterval }}s
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Active' ? 'success' : row.status === 'Error' ? 'danger' : 'info'" size="small">
              <span class="status-dot" :class="row.status === 'Active' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastCall" label="Last Call" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="testEndpoint(row)">Test</el-button>
            <el-button link type="success" size="small" @click="viewDetails(row)">Details</el-button>
            <el-button link type="info" size="small" @click="viewDocs(row)">Docs</el-button>
            <el-button link type="danger" size="small" @click="deleteEndpoint(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredEndpoints.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- API Test Console -->
    <el-card class="test-console-card" shadow="hover" v-if="showTestConsole">
      <template #header>
        <div class="card-header">
          <span>API Test Console - {{ testingEndpoint?.name }}</span>
          <div class="console-actions">
            <el-button size="small" @click="showTestConsole = false">Close</el-button>
          </div>
        </div>
      </template>

      <div class="test-console">
        <div class="request-section">
          <div class="request-header">
            <el-select v-model="testMethod" size="small" style="width: 100px">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
              <el-option label="PATCH" value="PATCH" />
            </el-select>
            <el-input v-model="testUrl" size="small" placeholder="Request URL" style="flex: 1; margin-left: 8px" />
            <el-button type="primary" size="small" @click="sendRequest" :loading="sending">
              Send
            </el-button>
          </div>

          <el-tabs v-model="activeTestTab">
            <el-tab-pane label="Headers" name="headers">
              <div class="headers-editor">
                <div v-for="(header, idx) in testHeaders" :key="idx" class="header-row">
                  <el-input v-model="header.key" placeholder="Header name" size="small" style="width: 200px" />
                  <el-input v-model="header.value" placeholder="Header value" size="small" style="width: 300px; margin-left: 8px" />
                  <el-button link type="danger" size="small" @click="removeHeader(idx)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <el-button size="small" @click="addHeader">+ Add Header</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Params" name="params">
              <div class="params-editor">
                <div v-for="(param, idx) in testParams" :key="idx" class="param-row">
                  <el-input v-model="param.key" placeholder="Parameter name" size="small" style="width: 200px" />
                  <el-input v-model="param.value" placeholder="Parameter value" size="small" style="width: 300px; margin-left: 8px" />
                  <el-button link type="danger" size="small" @click="removeParam(idx)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <el-button size="small" @click="addParam">+ Add Parameter</el-button>
              </div>
            </el-tab-pane>

            <el-tab-pane label="Body" name="body">
              <el-select v-model="testBodyType" size="small" style="width: 120px; margin-bottom: 8px">
                <el-option label="JSON" value="json" />
                <el-option label="XML" value="xml" />
                <el-option label="Form Data" value="form" />
                <el-option label="Raw" value="raw" />
              </el-select>
              <el-input
                  v-model="testBody"
                  type="textarea"
                  :rows="6"
                  placeholder='{"key": "value"}'
                  style="font-family: monospace"
              />
            </el-tab-pane>

            <el-tab-pane label="Auth" name="auth">
              <el-form label-width="80px" size="small">
                <el-form-item label="Auth Type">
                  <el-radio-group v-model="testAuthType">
                    <el-radio value="none">None</el-radio>
                    <el-radio value="basic">Basic Auth</el-radio>
                    <el-radio value="bearer">Bearer Token</el-radio>
                    <el-radio value="apikey">API Key</el-radio>
                  </el-radio-group>
                </el-form-item>
                <template v-if="testAuthType === 'basic'">
                  <el-form-item label="Username">
                    <el-input v-model="testUsername" placeholder="Username" />
                  </el-form-item>
                  <el-form-item label="Password">
                    <el-input v-model="testPassword" type="password" placeholder="Password" />
                  </el-form-item>
                </template>
                <template v-if="testAuthType === 'bearer'">
                  <el-form-item label="Token">
                    <el-input v-model="testToken" placeholder="Bearer token" />
                  </el-form-item>
                </template>
                <template v-if="testAuthType === 'apikey'">
                  <el-form-item label="Key Name">
                    <el-input v-model="testApiKeyName" placeholder="X-API-Key" />
                  </el-form-item>
                  <el-form-item label="Key Value">
                    <el-input v-model="testApiKeyValue" placeholder="API key value" />
                  </el-form-item>
                  <el-form-item label="Key Location">
                    <el-radio-group v-model="testApiKeyLocation">
                      <el-radio value="header">Header</el-radio>
                      <el-radio value="query">Query</el-radio>
                    </el-radio-group>
                  </el-form-item>
                </template>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </div>

        <div class="response-section" v-if="testResponse">
          <div class="response-header">
            <div class="response-status">
              <el-tag :type="testResponse.status >= 200 && testResponse.status < 300 ? 'success' : 'danger'" size="small">
                Status: {{ testResponse.status }} {{ testResponse.statusText }}
              </el-tag>
              <span class="response-time">Time: {{ testResponse.time }}ms</span>
              <span class="response-size">Size: {{ testResponse.size }} bytes</span>
            </div>
            <el-button size="small" @click="copyResponse">Copy</el-button>
          </div>
          <div class="response-body">
            <pre>{{ JSON.stringify(testResponse.data, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Add/Edit Endpoint Dialog -->
    <el-dialog v-model="endpointDialogVisible" :title="dialogMode === 'add' ? 'Add REST API Endpoint' : 'Edit REST API Endpoint'" width="700px" destroy-on-close class="endpoint-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Basic Configuration" name="basic">
          <el-form :model="endpointForm" :rules="endpointRules" ref="endpointFormRef" label-width="130px">
            <el-form-item label="Endpoint Name" prop="name">
              <el-input v-model="endpointForm.name" placeholder="Enter endpoint name" />
            </el-form-item>
            <el-form-item label="Base URL" prop="baseUrl">
              <el-input v-model="endpointForm.baseUrl" placeholder="https://api.example.com/v1" />
            </el-form-item>
            <el-form-item label="Endpoint Path" prop="path">
              <el-input v-model="endpointForm.path" placeholder="/devices" />
            </el-form-item>
            <el-form-item label="HTTP Method" prop="method">
              <el-select v-model="endpointForm.method" style="width: 100%">
                <el-option label="GET" value="GET" />
                <el-option label="POST" value="POST" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
                <el-option label="PATCH" value="PATCH" />
              </el-select>
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="endpointForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Authentication" name="auth">
          <el-form label-width="130px">
            <el-form-item label="Auth Type" prop="authType">
              <el-select v-model="endpointForm.authType" style="width: 100%">
                <el-option label="None" value="None" />
                <el-option label="Basic Auth" value="basic" />
                <el-option label="Bearer Token" value="bearer" />
                <el-option label="API Key" value="apikey" />
                <el-option label="OAuth 2.0" value="oauth2" />
              </el-select>
            </el-form-item>

            <template v-if="endpointForm.authType === 'basic'">
              <el-form-item label="Username" prop="username">
                <el-input v-model="endpointForm.username" />
              </el-form-item>
              <el-form-item label="Password" prop="password">
                <el-input v-model="endpointForm.password" type="password" />
              </el-form-item>
            </template>

            <template v-if="endpointForm.authType === 'bearer'">
              <el-form-item label="Token" prop="token">
                <el-input v-model="endpointForm.token" type="password" />
              </el-form-item>
            </template>

            <template v-if="endpointForm.authType === 'apikey'">
              <el-form-item label="API Key Name" prop="apiKeyName">
                <el-input v-model="endpointForm.apiKeyName" placeholder="X-API-Key" />
              </el-form-item>
              <el-form-item label="API Key Value" prop="apiKeyValue">
                <el-input v-model="endpointForm.apiKeyValue" type="password" />
              </el-form-item>
              <el-form-item label="Key Location" prop="apiKeyLocation">
                <el-radio-group v-model="endpointForm.apiKeyLocation">
                  <el-radio value="header">Header</el-radio>
                  <el-radio value="query">Query Parameter</el-radio>
                </el-radio-group>
              </el-form-item>
            </template>

            <template v-if="endpointForm.authType === 'oauth2'">
              <el-form-item label="Token URL" prop="tokenUrl">
                <el-input v-model="endpointForm.tokenUrl" placeholder="https://auth.example.com/oauth/token" />
              </el-form-item>
              <el-form-item label="Client ID" prop="clientId">
                <el-input v-model="endpointForm.clientId" />
              </el-form-item>
              <el-form-item label="Client Secret" prop="clientSecret">
                <el-input v-model="endpointForm.clientSecret" type="password" />
              </el-form-item>
              <el-form-item label="Scope" prop="scope">
                <el-input v-model="endpointForm.scope" placeholder="read write" />
              </el-form-item>
            </template>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Request/Response" name="mapping">
          <el-form label-width="130px">
            <el-form-item label="Request Template">
              <el-input v-model="endpointForm.requestTemplate" type="textarea" :rows="3" placeholder='{"deviceId": "{{deviceId}}", "timestamp": "{{timestamp}}"}' />
            </el-form-item>
            <el-form-item label="Response Mapping">
              <el-input v-model="endpointForm.responseMapping" type="textarea" :rows="3" placeholder='{"id": "{{data.id}}", "value": "{{data.value}}"}' />
            </el-form-item>
            <el-form-item label="Polling Interval (s)">
              <el-input-number v-model="endpointForm.pollingInterval" :min="5" :max="3600" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Timeout (ms)">
              <el-input-number v-model="endpointForm.timeout" :min="1000" :max="60000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Retry Count">
              <el-input-number v-model="endpointForm.retryCount" :min="0" :max="10" style="width: 100%" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Headers" name="headers">
          <div class="static-headers">
            <div v-for="(header, idx) in endpointForm.headers" :key="idx" class="header-row">
              <el-input v-model="header.key" placeholder="Header name" size="small" style="width: 200px" />
              <el-input v-model="header.value" placeholder="Header value" size="small" style="width: 300px; margin-left: 8px" />
              <el-button link type="danger" size="small" @click="removeStaticHeader(idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button size="small" @click="addStaticHeader">+ Add Header</el-button>
          </div>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="endpointDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testEndpointConfig" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveEndpoint">
          Save Endpoint
        </el-button>
      </template>
    </el-dialog>

    <!-- Endpoint Details Dialog -->
    <el-dialog v-model="detailsDialogVisible" :title="`Endpoint Details - ${currentEndpoint?.name}`" width="700px" destroy-on-close>
      <div class="endpoint-details" v-if="currentEndpoint">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Name">{{ currentEndpoint.name }}</el-descriptions-item>
          <el-descriptions-item label="Method">
            <el-tag :type="getMethodTag(currentEndpoint.method)" size="small">{{ currentEndpoint.method }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="URL">{{ currentEndpoint.url }}</el-descriptions-item>
          <el-descriptions-item label="Auth Type">{{ currentEndpoint.authType }}</el-descriptions-item>
          <el-descriptions-item label="Polling Interval">{{ currentEndpoint.pollingInterval }}s</el-descriptions-item>
          <el-descriptions-item label="Timeout">{{ currentEndpoint.timeout }}ms</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="currentEndpoint.status === 'Active' ? 'success' : 'info'" size="small">{{ currentEndpoint.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Last Call">{{ currentEndpoint.lastCall || 'Never' }}</el-descriptions-item>
          <el-descriptions-item label="Success Rate">{{ currentEndpoint.successRate || '100%' }}</el-descriptions-item>
          <el-descriptions-item label="Avg Response Time">{{ currentEndpoint.avgResponseTime || '125ms' }}</el-descriptions-item>
          <el-descriptions-item label="Description" :span="2">{{ currentEndpoint.description }}</el-descriptions-item>
        </el-descriptions>

        <div class="metrics-chart" v-if="currentEndpoint.metrics">
          <h4>Performance Metrics</h4>
          <div ref="metricsChartRef" class="metrics-chart-container"></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="testEndpoint(currentEndpoint)">Test</el-button>
      </template>
    </el-dialog>

    <!-- Documentation Dialog -->
    <el-dialog v-model="docsDialogVisible" :title="`API Documentation - ${currentEndpoint?.name}`" width="800px" destroy-on-close>
      <div class="api-docs" v-if="currentEndpoint">
        <div class="docs-header">
          <h3>{{ currentEndpoint.method }} {{ currentEndpoint.path }}</h3>
          <p>{{ currentEndpoint.description }}</p>
        </div>

        <div class="docs-section">
          <h4>Authentication</h4>
          <p>Type: <code>{{ currentEndpoint.authType }}</code></p>
          <pre class="docs-code">{{ getAuthExample(currentEndpoint) }}</pre>
        </div>

        <div class="docs-section">
          <h4>Request Example</h4>
          <pre class="docs-code">{{ getRequestExample(currentEndpoint) }}</pre>
        </div>

        <div class="docs-section">
          <h4>Response Example</h4>
          <pre class="docs-code">{{ getResponseExample(currentEndpoint) }}</pre>
        </div>

        <div class="docs-section">
          <h4>Error Codes</h4>
          <el-table :data="errorCodes" size="small" border>
            <el-table-column prop="code" label="Code" width="100" />
            <el-table-column prop="message" label="Message" min-width="200" />
            <el-table-column prop="description" label="Description" min-width="250" />
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="docsDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportOpenAPI">Export OpenAPI</el-button>
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
  Clock, TrendCharts, Refresh, Search, Download,
  Delete, Connection, Edit, DataAnalysis, Link, CopyDocument
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing REST API gateway...', 'Loading endpoints...', 'Almost ready...']

// ==================== Chart References ====================
const metricsChartRef = ref<HTMLElement>()
let metricsChart: echarts.ECharts | null = null

// ==================== State ====================
const tableLoading = ref(false)
const testing = ref(false)
const sending = ref(false)
const endpointDialogVisible = ref(false)
const detailsDialogVisible = ref(false)
const docsDialogVisible = ref(false)
const showTestConsole = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const currentEndpoint = ref<any>(null)
const testingEndpoint = ref<any>(null)
const searchKeyword = ref('')
const methodFilter = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const activeTestTab = ref('headers')
const currentPage = ref(1)
const pageSize = ref(10)

// Test console state
const testMethod = ref('GET')
const testUrl = ref('')
const testHeaders = ref<{ key: string; value: string }[]>([{ key: 'Content-Type', value: 'application/json' }])
const testParams = ref<{ key: string; value: string }[]>([])
const testBody = ref('')
const testBodyType = ref('json')
const testAuthType = ref('none')
const testUsername = ref('')
const testPassword = ref('')
const testToken = ref('')
const testApiKeyName = ref('X-API-Key')
const testApiKeyValue = ref('')
const testApiKeyLocation = ref('header')
const testResponse = ref<any>(null)

const endpointFormRef = ref()

const testResult = reactive({ success: false, message: '', details: null as any })

// Mock error codes
const errorCodes = ref([
  { code: 400, message: 'Bad Request', description: 'Invalid request parameters' },
  { code: 401, message: 'Unauthorized', description: 'Authentication failed' },
  { code: 403, message: 'Forbidden', description: 'Insufficient permissions' },
  { code: 404, message: 'Not Found', description: 'Resource not found' },
  { code: 429, message: 'Too Many Requests', description: 'Rate limit exceeded' },
  { code: 500, message: 'Internal Server Error', description: 'Server-side error' }
])

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'API Endpoints', value: '24', trend: 4, icon: 'Link', bgColor: '#409eff', key: 'endpoints', subTitle: 'Active: 22' },
  { title: 'Requests/Day', value: '45.2K', trend: 12, icon: 'TrendCharts', bgColor: '#67c23a', key: 'requests', subTitle: 'Peak: 3.2K/h' },
  { title: 'Avg Response', value: '124ms', trend: -8, icon: 'Clock', bgColor: '#e6a23c', key: 'response', subTitle: 'P95: 245ms' },
  { title: 'Success Rate', value: '99.2%', trend: 0.5, icon: 'Checked', bgColor: '#f56c6c', key: 'rate', subTitle: 'Errors: 0.8%' }
])

const endpoints = ref([
  { id: 1, name: 'Get Devices', method: 'GET', url: 'https://api.ibms.com/v1/devices', authType: 'Bearer', pollingInterval: 60, status: 'Active', lastCall: '2024-01-20 10:30:00' },
  { id: 2, name: 'Get Device Details', method: 'GET', url: 'https://api.ibms.com/v1/devices/{id}', authType: 'Bearer', pollingInterval: 60, status: 'Active', lastCall: '2024-01-20 10:28:00' },
  { id: 3, name: 'Create Device', method: 'POST', url: 'https://api.ibms.com/v1/devices', authType: 'Bearer', pollingInterval: 0, status: 'Active', lastCall: '2024-01-20 10:32:00' },
  { id: 4, name: 'Update Device', method: 'PUT', url: 'https://api.ibms.com/v1/devices/{id}', authType: 'Bearer', pollingInterval: 0, status: 'Active', lastCall: '2024-01-20 10:25:00' },
  { id: 5, name: 'Delete Device', method: 'DELETE', url: 'https://api.ibms.com/v1/devices/{id}', authType: 'Bearer', pollingInterval: 0, status: 'Inactive', lastCall: '2024-01-19 15:30:00' },
  { id: 6, name: 'Get Telemetry', method: 'GET', url: 'https://api.ibms.com/v1/telemetry', authType: 'API Key', pollingInterval: 30, status: 'Active', lastCall: '2024-01-20 10:29:00' }
])

// ==================== Computed ====================
const filteredEndpoints = computed(() => {
  let filtered = [...endpoints.value]
  if (searchKeyword.value) filtered = filtered.filter(e => e.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || e.url.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  if (methodFilter.value) filtered = filtered.filter(e => e.method === methodFilter.value)
  if (statusFilter.value) filtered = filtered.filter(e => e.status === statusFilter.value)
  return filtered
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

const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting OpenAPI specification...')
const fetchEndpoints = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Endpoints refreshed') }, 500) }

const openAddEndpointDialog = () => {
  dialogMode.value = 'add'
  Object.assign(endpointForm, {
    id: null, name: '', baseUrl: '', path: '', method: 'GET', description: '',
    authType: 'None', username: '', password: '', token: '', apiKeyName: '', apiKeyValue: '', apiKeyLocation: 'header',
    tokenUrl: '', clientId: '', clientSecret: '', scope: '',
    requestTemplate: '', responseMapping: '', pollingInterval: 60, timeout: 30000, retryCount: 3,
    headers: [{ key: 'Content-Type', value: 'application/json' }]
  })
  endpointDialogVisible.value = true
}

const editEndpoint = (endpoint: any) => {
  dialogMode.value = 'edit'
  Object.assign(endpointForm, endpoint)
  endpointDialogVisible.value = true
}

const testEndpointConfig = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Connection successful'
    testResult.details = { responseTime: 45, status: 200 }
    ElMessage.success('Connection test successful')
  }, 1500)
}

const saveEndpoint = async () => {
  if (!endpointFormRef.value) return
  await endpointFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Endpoint added successfully' : 'Endpoint updated successfully')
      endpointDialogVisible.value = false
    }
  })
}

const deleteEndpoint = (endpoint: any) => {
  ElMessageBox.confirm(`Delete endpoint "${endpoint.name}"?`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = endpoints.value.findIndex(e => e.id === endpoint.id)
    if (index !== -1) { endpoints.value.splice(index, 1); ElMessage.success(`Deleted: ${endpoint.name}`) }
  }).catch(() => {})
}

const testEndpoint = (endpoint: any) => {
  testingEndpoint.value = endpoint
  testMethod.value = endpoint.method
  testUrl.value = endpoint.url
  showTestConsole.value = true
}

const viewDetails = (endpoint: any) => {
  currentEndpoint.value = endpoint
  detailsDialogVisible.value = true
  nextTick(() => {
    if (metricsChartRef.value) {
      if (metricsChart) metricsChart.dispose()
      metricsChart = echarts.init(metricsChartRef.value)
      metricsChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
        yAxis: { type: 'value', name: 'Requests' },
        series: [{ type: 'line', data: [1250, 1420, 1380, 1560, 1890, 2100, 1450], smooth: true, lineStyle: { width: 2, color: '#409eff' }, areaStyle: { opacity: 0.1 } }]
      })
    }
  })
}

const viewDocs = (endpoint: any) => {
  currentEndpoint.value = endpoint
  docsDialogVisible.value = true
}

const getAuthExample = (endpoint: any) => {
  if (endpoint.authType === 'Bearer') return `Authorization: Bearer your_token_here`
  if (endpoint.authType === 'Basic') return `Authorization: Basic base64_encode(username:password)`
  if (endpoint.authType === 'API Key') return `X-API-Key: your_api_key_here`
  return 'No authentication required'
}

const getRequestExample = (endpoint: any) => {
  return `${endpoint.method} ${endpoint.url}\nContent-Type: application/json\n\n{\n  "example": "request body"\n}`
}

const getResponseExample = (endpoint: any) => {
  return `{\n  "status": "success",\n  "data": {\n    "id": "example_id",\n    "name": "example_name"\n  },\n  "timestamp": "2024-01-20T10:30:00Z"\n}`
}

const exportOpenAPI = () => {
  ElMessage.success('OpenAPI specification exported')
}

// ==================== Test Console Methods ====================
const addHeader = () => { testHeaders.value.push({ key: '', value: '' }) }
const removeHeader = (idx: number) => { testHeaders.value.splice(idx, 1) }
const addParam = () => { testParams.value.push({ key: '', value: '' }) }
const removeParam = (idx: number) => { testParams.value.splice(idx, 1) }
const addStaticHeader = () => { endpointForm.headers.push({ key: '', value: '' }) }
const removeStaticHeader = (idx: number) => { endpointForm.headers.splice(idx, 1) }

const sendRequest = () => {
  sending.value = true
  setTimeout(() => {
    sending.value = false
    testResponse.value = {
      status: 200,
      statusText: 'OK',
      time: Math.floor(Math.random() * 100) + 20,
      size: Math.floor(Math.random() * 5000) + 500,
      data: { message: 'Request successful', data: { id: 'DEV-001', name: 'Test Device', status: 'active' } }
    }
    ElMessage.success('Request completed')
  }, 1000)
}

const copyResponse = () => {
  if (testResponse.value) {
    navigator.clipboard.writeText(JSON.stringify(testResponse.value.data, null, 2))
    ElMessage.success('Response copied to clipboard')
  }
}

// ==================== Form ====================
const endpointForm = reactive({
  id: null, name: '', baseUrl: '', path: '', method: 'GET', description: '',
  authType: 'None', username: '', password: '', token: '', apiKeyName: '', apiKeyValue: '', apiKeyLocation: 'header',
  tokenUrl: '', clientId: '', clientSecret: '', scope: '',
  requestTemplate: '', responseMapping: '', pollingInterval: 60, timeout: 30000, retryCount: 3,
  headers: [{ key: 'Content-Type', value: 'application/json' }]
})

const endpointRules = {
  name: [{ required: true, message: 'Please enter endpoint name', trigger: 'blur' }],
  baseUrl: [{ required: true, message: 'Please enter base URL', trigger: 'blur' }],
  path: [{ required: true, message: 'Please enter endpoint path', trigger: 'blur' }]
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchEndpoints() }, 400)
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

.restapi-page {
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

.endpoints-card { margin-bottom: 20px; }
.endpoints-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.endpoints-card .table-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.test-console-card { margin-bottom: 20px; }
.test-console-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.test-console { display: flex; gap: 20px; }
.test-console .request-section { flex: 1; .request-header { display: flex; margin-bottom: 16px; } .headers-editor .header-row, .params-editor .param-row { display: flex; align-items: center; margin-bottom: 8px; } .response-section { flex: 1; .response-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; } .response-body { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; overflow-x: auto; pre { margin: 0; font-family: monospace; font-size: 12px; } } } }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.endpoint-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.endpoint-details .metrics-chart { margin-top: 20px; .metrics-chart-container { width: 100%; height: 300px; } }
.api-docs .docs-section { margin-top: 20px; h4 { margin-bottom: 8px; } .docs-code { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; overflow-x: auto; } }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>