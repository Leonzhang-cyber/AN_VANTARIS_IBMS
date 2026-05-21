<template>
  <div v-if="isPageLoaded" class="api-management-page">
    <div class="page-container">
      <!-- Page Header -->
      <div class="page-header">
        <div class="header-left">
          <h1>API Management</h1>
          <p>REST API gateway · Key management · Rate limiting · Monitoring & documentation</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" size="small" @click="openCreateAppDialog">
            <el-icon><Plus /></el-icon> New App
          </el-button>
          <el-button type="success" size="small" plain @click="refreshData" :loading="refreshing">
            <el-icon><Refresh /></el-icon> Refresh
          </el-button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card"><div class="stat-icon blue"><el-icon><Connection /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.totalApis }}</div><div class="stat-label">Total APIs</div></div></div>
        <div class="stat-card"><div class="stat-icon green"><el-icon><ChatLineSquare /></el-icon></div><div class="stat-info"><div class="stat-value">{{ formatNumber(stats.todayCalls) }}</div><div class="stat-label">Today Calls</div></div></div>
        <div class="stat-card"><div class="stat-icon orange"><el-icon><Timer /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.avgResponseTime }} ms</div><div class="stat-label">Avg Response</div></div></div>
        <div class="stat-card"><div class="stat-icon purple"><el-icon><Warning /></el-icon></div><div class="stat-info"><div class="stat-value">{{ stats.errorRate }}%</div><div class="stat-label">Error Rate</div></div></div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="card-header"><span><el-icon><TrendCharts /></el-icon> API Call Trend (Last 7 Days)</span></div>
          <div ref="trendChartRef" class="trend-chart" style="height: 260px;"></div>
        </div>
        <div class="chart-card">
          <div class="card-header"><span><el-icon><PieChart /></el-icon> API Usage by Endpoint</span></div>
          <div ref="pieChartRef" class="pie-chart" style="height: 260px;"></div>
        </div>
      </div>

      <!-- Applications Table -->
      <div class="section-card">
        <div class="section-header"><h3><el-icon><OfficeBuilding /></el-icon> Applications</h3><el-input v-model="appSearch" placeholder="Search..." size="small" clearable style="width: 200px" :prefix-icon="Search" /></div>
        <el-table :data="filteredApplications" stripe size="small" class="equal-width-table">
          <el-table-column prop="name" label="App Name" min-width="140" />
          <el-table-column prop="clientId" label="Client ID" min-width="180">
            <template #default="{ row }"><span class="mono">{{ shortenClientId(row.clientId) }}</span><el-icon class="copy-icon" @click="copyText(row.clientId)"><CopyDocument /></el-icon></template>
          </el-table-column>
          <el-table-column prop="clientSecret" label="Client Secret" min-width="200">
            <template #default="{ row }"><span class="mono secret">{{ row.clientSecret.slice(0, 20) }}...</span><el-icon class="copy-icon" @click="copyText(row.clientSecret)"><CopyDocument /></el-icon></template>
          </el-table-column>
          <el-table-column prop="environment" label="Env" width="90">
            <template #default="{ row }"><el-tag :type="row.environment === 'production' ? 'danger' : row.environment === 'staging' ? 'warning' : 'info'" size="small">{{ row.environment }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="90">
            <template #default="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag></template>
          </el-table-column>
          <el-table-column label="Actions" width="250" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="viewApiKeys(row)">Keys</el-button>
                <el-button size="small" @click="editRateLimit(row)">Rate Limit</el-button>
                <el-button size="small" type="primary" plain @click="editApplication(row)">Edit</el-button>
                <el-button size="small" type="danger" plain @click="deleteApplication(row)">Del</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- API Keys Table - 全部渲染 -->
      <div class="section-card">
        <div class="section-header"><h3><el-icon><Key /></el-icon> API Keys ({{ apiKeys.length }} keys)</h3><el-button size="small" type="primary" plain @click="generateNewKeyForActiveApp"><el-icon><Plus /></el-icon> Generate Key</el-button></div>
        <el-table :data="apiKeys" stripe size="small" class="equal-width-table">
          <el-table-column prop="appName" label="App Name" min-width="140" />
          <el-table-column prop="environment" label="Env" width="90">
            <template #default="{ row }"><el-tag :type="row.environment === 'production' ? 'danger' : row.environment === 'staging' ? 'warning' : 'info'" size="small">{{ row.environment }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="apiKey" label="API Key" min-width="300">
            <template #default="{ row }"><span class="mono">{{ row.apiKey }}</span><el-icon class="copy-icon" @click="copyText(row.apiKey)"><CopyDocument /></el-icon></template>
          </el-table-column>
          <el-table-column prop="createdAt" label="Created" width="110" />
          <el-table-column prop="expiresAt" label="Expires" width="110" />
          <el-table-column label="Action" width="80" fixed="right">
            <template #default="{ row }"><el-button size="small" type="danger" link @click="revokeKey(row)">Revoke</el-button></template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Rate Limits Table -->
      <div class="section-card">
        <div class="section-header"><h3><el-icon><Lock /></el-icon> Rate Limit Rules</h3><el-button size="small" type="primary" plain @click="createRateLimit"><el-icon><Plus /></el-icon> Add Rule</el-button></div>
        <el-table :data="rateLimits" stripe size="small" class="equal-width-table">
          <el-table-column prop="appName" label="App Name" min-width="140" />
          <el-table-column prop="apiPath" label="API Path" min-width="160" />
          <el-table-column prop="dimension" label="Dimension" width="100">
            <template #default="{ row }">{{ row.dimension === 'ip' ? 'By IP' : 'By User' }}</template>
          </el-table-column>
          <el-table-column label="Limit" width="130">
            <template #default="{ row }">{{ row.limit }} req / {{ row.period }}</template>
          </el-table-column>
          <el-table-column prop="action" label="Action" width="110">
            <template #default="{ row }">{{ row.action === '429' ? 'Return 429' : row.action === 'queue' ? 'Queue' : 'Throttle' }}</template>
          </el-table-column>
          <el-table-column label="Action" width="80" fixed="right">
            <template #default="{ row }"><el-button size="small" type="danger" link @click="deleteRateLimit(row)">Delete</el-button></template>
          </el-table-column>
        </el-table>
      </div>

      <!-- API Endpoints Table - 30+ endpoints -->
      <div class="section-card">
        <div class="section-header"><h3><el-icon><Connection /></el-icon> API Endpoints ({{ apiEndpoints.length }})</h3><el-input v-model="endpointSearch" placeholder="Search..." size="small" clearable style="width: 200px" :prefix-icon="Search" /></div>
        <el-table :data="filteredEndpoints" stripe size="small" class="equal-width-table">
          <el-table-column prop="method" label="Method" width="80">
            <template #default="{ row }"><el-tag :type="row.method === 'GET' ? 'success' : row.method === 'POST' ? 'primary' : 'warning'" size="small">{{ row.method }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="path" label="Path" min-width="220" />
          <el-table-column prop="summary" label="Summary" min-width="200" />
          <el-table-column label="Test" width="80" fixed="right">
            <template #default="{ row }"><el-button size="small" type="primary" link @click="openTestDialog(row)">Test</el-button></template>
          </el-table-column>
        </el-table>
      </div>

      <!-- API Logs Table -->
      <div class="section-card">
        <div class="section-header"><h3><el-icon><List /></el-icon> API Logs</h3><div class="logs-filters"><el-select v-model="logAppFilter" placeholder="App" size="small" clearable style="width: 130px"><el-option v-for="app in applications" :key="app.id" :label="app.name" :value="app.id" /></el-select><el-button size="small" @click="searchLogs">Search</el-button></div></div>
        <el-table :data="filteredLogs" stripe size="small" class="equal-width-table">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="appName" label="App" min-width="120" />
          <el-table-column prop="method" label="Method" width="80">
            <template #default="{ row }"><el-tag :type="row.method === 'GET' ? 'success' : row.method === 'POST' ? 'primary' : 'warning'" size="small">{{ row.method }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="path" label="Path" min-width="220" />
          <el-table-column prop="statusCode" label="Status" width="90">
            <template #default="{ row }"><el-tag :type="row.statusCode >= 200 && row.statusCode < 300 ? 'success' : 'danger'" size="small">{{ row.statusCode }}</el-tag></template>
          </el-table-column>
          <el-table-column prop="responseTime" label="Time" width="90">
            <template #default="{ row }"><span :class="row.responseTime > 500 ? 'slow' : 'fast'">{{ row.responseTime }} ms</span></template>
          </el-table-column>
        </el-table>
      </div>

      <!-- Webhooks Table -->
      <div class="section-card">
        <div class="section-header"><h3><el-icon><Share /></el-icon> Webhooks</h3><el-button size="small" type="primary" plain @click="createWebhook"><el-icon><Plus /></el-icon> Create</el-button></div>
        <el-table :data="webhooks" stripe size="small" class="equal-width-table">
          <el-table-column prop="name" label="Name" min-width="140" />
          <el-table-column prop="url" label="Target URL" min-width="260" />
          <el-table-column prop="events" label="Events" min-width="160">
            <template #default="{ row }"><el-tag v-for="e in row.events.slice(0, 2)" :key="e" size="small" style="margin-right: 4px">{{ e }}</el-tag><span v-if="row.events.length > 2">+{{ row.events.length - 2 }}</span></template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="90">
            <template #default="{ row }"><el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag></template>
          </el-table-column>
          <el-table-column label="Actions" width="150" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="testWebhook(row)">Test</el-button>
                <el-button size="small" type="danger" link @click="deleteWebhook(row)">Delete</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- API Test Dialog -->
    <el-dialog v-model="testDialogVisible" title="API Test" width="700px" destroy-on-close>
      <div class="test-container">
        <div class="test-header">
          <el-tag :type="selectedEndpoint?.method === 'GET' ? 'success' : selectedEndpoint?.method === 'POST' ? 'primary' : 'warning'" size="small">{{ selectedEndpoint?.method }}</el-tag>
          <span class="test-path">{{ selectedEndpoint?.path }}</span>
        </div>

        <div class="test-auth">
          <div class="auth-label">API Key</div>
          <el-select v-model="testApiKey" placeholder="Select API Key" size="small" style="width: 400px" filterable>
            <el-option v-for="key in apiKeys" :key="key.id" :label="`${key.appName} (${key.environment}) - ${key.apiKey.slice(0, 20)}...`" :value="key.apiKey" />
          </el-select>
        </div>

        <div v-if="selectedEndpoint?.parameters?.length" class="test-params">
          <div class="params-label">Parameters</div>
          <div v-for="param in selectedEndpoint.parameters" :key="param.name" class="param-row">
            <span class="param-name">{{ param.name }}</span>
            <span class="param-type">{{ param.type }}</span>
            <span v-if="param.required" class="param-required">required</span>
            <el-input v-model="testParams[param.name]" :placeholder="param.description || param.name" size="small" style="width: 280px" />
          </div>
        </div>

        <div class="test-actions">
          <el-button type="primary" @click="executeApiTest" :loading="testLoading">Send Request</el-button>
          <el-button @click="resetTestParams">Reset</el-button>
        </div>

        <div v-if="testResponse" class="test-response">
          <div class="response-header">
            <span>Response</span>
            <el-tag :type="testResponse.status >= 200 && testResponse.status < 300 ? 'success' : 'danger'" size="small">{{ testResponse.status }} {{ testResponse.statusText }}</el-tag>
            <span class="response-time">{{ testResponse.time }} ms</span>
          </div>
          <pre class="response-body">{{ JSON.stringify(testResponse.data, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>

    <!-- Dialogs -->
    <el-dialog v-model="appDialogVisible" :title="editingApp ? 'Edit Application' : 'New Application'" width="400px">
      <el-form :model="appForm" label-width="80px" size="small">
        <el-form-item label="Name" required><el-input v-model="appForm.name" /></el-form-item>
        <el-form-item label="Environment" required><el-radio-group v-model="appForm.environment"><el-radio label="development">Dev</el-radio><el-radio label="staging">Staging</el-radio><el-radio label="production">Prod</el-radio></el-radio-group></el-form-item>
      </el-form>
      <template #footer><el-button @click="appDialogVisible = false">Cancel</el-button><el-button type="primary" @click="saveApplication">Save</el-button></template>
    </el-dialog>

    <el-dialog v-model="rateLimitDialogVisible" title="Rate Limit" width="450px">
      <el-form :model="rateLimitForm" label-width="100px" size="small">
        <el-form-item label="Application" required><el-select v-model="rateLimitForm.appId" placeholder="Select" style="width: 100%"><el-option v-for="app in applications" :key="app.id" :label="app.name" :value="app.id" /></el-select></el-form-item>
        <el-form-item label="API Path"><el-input v-model="rateLimitForm.apiPath" placeholder="/api/v1/*" /></el-form-item>
        <el-form-item label="Limit"><el-input-number v-model="rateLimitForm.limit" :min="1" :max="10000" size="small" /> req / <el-select v-model="rateLimitForm.period" size="small" style="width: 90px"><el-option label="Sec" value="second" /><el-option label="Min" value="minute" /><el-option label="Hour" value="hour" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="rateLimitDialogVisible = false">Cancel</el-button><el-button type="primary" @click="saveRateLimit">Save</el-button></template>
    </el-dialog>

    <el-dialog v-model="apiKeysDialogVisible" title="API Keys" width="650px">
      <el-table :data="currentAppKeys" stripe size="small" class="equal-width-table">
        <el-table-column prop="environment" label="Env" width="80"><template #default="{ row }"><el-tag :type="row.environment === 'production' ? 'danger' : 'info'" size="small">{{ row.environment }}</el-tag></template></el-table-column>
        <el-table-column prop="apiKey" label="API Key" min-width="340"><template #default="{ row }"><span class="mono">{{ row.apiKey }}</span><el-icon class="copy-icon" @click="copyText(row.apiKey)"><CopyDocument /></el-icon></template></el-table-column>
        <el-table-column prop="createdAt" label="Created" width="100" />
        <el-table-column label="Action" width="80" fixed="right"><template #default="{ row }"><el-button size="small" type="danger" link @click="revokeKey(row)">Revoke</el-button></template></el-table-column>
      </el-table>
      <template #footer><el-button @click="generateNewKeyForApp">Generate New</el-button><el-button type="primary" @click="apiKeysDialogVisible = false">Close</el-button></template>
    </el-dialog>

    <el-dialog v-model="webhookDialogVisible" title="Webhook" width="450px">
      <el-form :model="webhookForm" label-width="80px" size="small">
        <el-form-item label="Name" required><el-input v-model="webhookForm.name" /></el-form-item>
        <el-form-item label="URL" required><el-input v-model="webhookForm.url" /></el-form-item>
        <el-form-item label="Events" required><el-select v-model="webhookForm.events" multiple style="width: 100%"><el-option label="Alarm" value="alarm.created" /><el-option label="Device Offline" value="device.offline" /><el-option label="Contract" value="contract.triggered" /></el-select></el-form-item>
      </el-form>
      <template #footer><el-button @click="webhookDialogVisible = false">Cancel</el-button><el-button type="primary" @click="saveWebhook">Save</el-button></template>
    </el-dialog>
  </div>

  <!-- Loading Screen -->
  <div v-else class="loading-container"><div class="loading-overlay"><div class="loading-content"><div class="loading-spinner"><div class="spinner-ring"></div><div class="spinner-ring"></div><div class="spinner-ring"></div></div><div class="loading-text"><span class="loading-title">Loading</span><span class="loading-dots">...</span></div><div class="loading-progress"><div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div></div><div class="loading-tip">API Management System</div><div class="loading-subtip">{{ loadingMessage }}</div></div></div></div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import { Refresh, Plus, Connection, ChatLineSquare, Timer, Warning, TrendCharts, PieChart, Search, CopyDocument, OfficeBuilding, Key, Lock, List, Share } from '@element-plus/icons-vue'

const isPageLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading...')
const refreshing = ref(false)
const loadingMessages = ['Loading...', 'Initializing...', 'Connecting...', 'Almost ready...']

const stats = ref({ totalApis: 36, todayCalls: 28450, avgResponseTime: 156, errorRate: 0.28 })

// 30+ API Endpoints
const apiEndpoints = ref([
  // Device APIs
  { path: '/api/v1/device/status', method: 'GET', summary: 'Get device status', parameters: [{ name: 'deviceId', type: 'string', required: false, description: 'Specific device ID', defaultValue: 'dev_001' }], responseExample: { status: 'online', device: { id: 'dev_001', name: 'HVAC-01', temperature: 23.5 } } },
  { path: '/api/v1/device/list', method: 'GET', summary: 'List all devices', parameters: [{ name: 'page', type: 'integer', required: false, description: 'Page number', defaultValue: 1 }, { name: 'limit', type: 'integer', required: false, description: 'Items per page', defaultValue: 20 }], responseExample: { total: 156, devices: [] } },
  { path: '/api/v1/device/control', method: 'POST', summary: 'Control device', parameters: [{ name: 'deviceId', type: 'string', required: true, description: 'Target device', defaultValue: 'dev_001' }, { name: 'action', type: 'string', required: true, description: 'Command', defaultValue: 'turn_on' }], responseExample: { success: true, message: 'Command sent' } },
  { path: '/api/v1/device/history', method: 'GET', summary: 'Device history data', parameters: [{ name: 'deviceId', type: 'string', required: true, defaultValue: 'dev_001' }, { name: 'startDate', type: 'string', required: false, defaultValue: '2026-05-01' }, { name: 'endDate', type: 'string', required: false, defaultValue: '2026-05-21' }], responseExample: { data: [{ timestamp: '2026-05-21', value: 23.5 }] } },
  { path: '/api/v1/device/alerts', method: 'GET', summary: 'Get device alerts', parameters: [{ name: 'deviceId', type: 'string', required: false }, { name: 'severity', type: 'string', required: false, defaultValue: 'warning' }], responseExample: { alerts: [{ id: 1, message: 'Temperature high' }] } },
  { path: '/api/v1/device/register', method: 'POST', summary: 'Register new device', parameters: [{ name: 'deviceType', type: 'string', required: true, defaultValue: 'sensor' }, { name: 'name', type: 'string', required: true, defaultValue: 'New Sensor' }, { name: 'location', type: 'string', required: false, defaultValue: 'Lobby' }], responseExample: { deviceId: 'dev_new_001', success: true } },
  { path: '/api/v1/device/delete', method: 'DELETE', summary: 'Delete device', parameters: [{ name: 'deviceId', type: 'string', required: true, defaultValue: 'dev_001' }], responseExample: { success: true, message: 'Device deleted' } },

  // Energy APIs
  { path: '/api/v1/energy/consumption', method: 'GET', summary: 'Get energy consumption', parameters: [{ name: 'zone', type: 'string', required: false, defaultValue: 'lobby' }, { name: 'date', type: 'string', required: false, defaultValue: '2026-05-21' }], responseExample: { total: 1245.6, unit: 'kWh' } },
  { path: '/api/v1/energy/record', method: 'POST', summary: 'Submit energy data', parameters: [{ name: 'value', type: 'number', required: true, defaultValue: 100 }, { name: 'timestamp', type: 'string', required: true, defaultValue: '2026-05-21T10:00:00Z' }, { name: 'zone', type: 'string', required: false, defaultValue: 'lobby' }], responseExample: { id: 'rec_12345', success: true } },
  { path: '/api/v1/energy/analytics', method: 'GET', summary: 'Energy analytics', parameters: [{ name: 'startDate', type: 'string', required: true, defaultValue: '2026-05-01' }, { name: 'endDate', type: 'string', required: true, defaultValue: '2026-05-21' }], responseExample: { avg: 1250, peak: 1890, total: 28450 } },
  { path: '/api/v1/energy/forecast', method: 'GET', summary: 'Energy forecast', parameters: [{ name: 'days', type: 'integer', required: false, defaultValue: 7 }], responseExample: { forecast: [1200, 1250, 1300, 1280, 1320, 1350, 1300] } },
  { path: '/api/v1/energy/cost', method: 'GET', summary: 'Energy cost calculation', parameters: [{ name: 'startDate', type: 'string', required: false, defaultValue: '2026-05-01' }, { name: 'endDate', type: 'string', required: false, defaultValue: '2026-05-21' }], responseExample: { totalCost: 2845.50, unitPrice: 0.12, currency: 'USD' } },

  // Alarm APIs
  { path: '/api/v1/alarm/list', method: 'GET', summary: 'Get alarms', parameters: [{ name: 'severity', type: 'string', required: false, defaultValue: 'warning' }, { name: 'status', type: 'string', required: false, defaultValue: 'active' }, { name: 'limit', type: 'integer', required: false, defaultValue: 10 }], responseExample: { alarms: [{ id: 1, severity: 'warning', message: 'Temperature high' }], total: 1 } },
  { path: '/api/v1/alarm/acknowledge', method: 'POST', summary: 'Acknowledge alarm', parameters: [{ name: 'alarmId', type: 'string', required: true, defaultValue: 'alm_001' }], responseExample: { success: true, message: 'Alarm acknowledged' } },
  { path: '/api/v1/alarm/history', method: 'GET', summary: 'Alarm history', parameters: [{ name: 'startDate', type: 'string', required: false, defaultValue: '2026-05-01' }, { name: 'endDate', type: 'string', required: false, defaultValue: '2026-05-21' }], responseExample: { total: 234, history: [] } },
  { path: '/api/v1/alarm/stats', method: 'GET', summary: 'Alarm statistics', parameters: [], responseExample: { critical: 5, warning: 12, info: 34, resolved: 40 } },
  { path: '/api/v1/alarm/clear', method: 'POST', summary: 'Clear alarm', parameters: [{ name: 'alarmId', type: 'string', required: true, defaultValue: 'alm_001' }], responseExample: { success: true } },

  // Contract APIs
  { path: '/api/v1/contract/list', method: 'GET', summary: 'List smart contracts', parameters: [{ name: 'status', type: 'string', required: false, defaultValue: 'active' }], responseExample: { contracts: [{ id: 1, name: 'Carbon Credit', status: 'active' }] } },
  { path: '/api/v1/contract/execute', method: 'POST', summary: 'Execute contract', parameters: [{ name: 'contractId', type: 'string', required: true, defaultValue: 'contract_001' }, { name: 'params', type: 'object', required: false, defaultValue: { amount: 100 } }], responseExample: { txHash: '0x7a8b9c0d...', status: 'pending' } },
  { path: '/api/v1/contract/status', method: 'GET', summary: 'Contract execution status', parameters: [{ name: 'txHash', type: 'string', required: true, defaultValue: '0x7a8b9c0d...' }], responseExample: { status: 'confirmed', blockNumber: 12456, gasUsed: 45000 } },
  { path: '/api/v1/contract/deploy', method: 'POST', summary: 'Deploy new contract', parameters: [{ name: 'name', type: 'string', required: true, defaultValue: 'NewContract' }, { name: 'bytecode', type: 'string', required: true, defaultValue: '0x60806040...' }], responseExample: { address: '0x1234...', success: true } },

  // HVAC APIs
  { path: '/api/v1/hvac/temperature', method: 'GET', summary: 'Get HVAC temperature', parameters: [{ name: 'zone', type: 'string', required: false, defaultValue: 'lobby' }], responseExample: { temperature: 23.5, setpoint: 24, mode: 'cool' } },
  { path: '/api/v1/hvac/setpoint', method: 'PUT', summary: 'Set temperature setpoint', parameters: [{ name: 'zone', type: 'string', required: true, defaultValue: 'lobby' }, { name: 'temperature', type: 'number', required: true, defaultValue: 24 }], responseExample: { success: true, newSetpoint: 24 } },
  { path: '/api/v1/hvac/mode', method: 'PUT', summary: 'Change HVAC mode', parameters: [{ name: 'zone', type: 'string', required: true, defaultValue: 'lobby' }, { name: 'mode', type: 'string', required: true, defaultValue: 'cool' }], responseExample: { success: true, mode: 'cool' } },

  // Lighting APIs
  { path: '/api/v1/lighting/status', method: 'GET', summary: 'Get lighting status', parameters: [{ name: 'zone', type: 'string', required: false, defaultValue: 'lobby' }], responseExample: { brightness: 80, status: 'on' } },
  { path: '/api/v1/lighting/control', method: 'POST', summary: 'Control lighting', parameters: [{ name: 'zone', type: 'string', required: true, defaultValue: 'lobby' }, { name: 'brightness', type: 'integer', required: false, defaultValue: 80 }, { name: 'status', type: 'string', required: true, defaultValue: 'on' }], responseExample: { success: true } },

  // Access Control APIs
  { path: '/api/v1/access/grant', method: 'POST', summary: 'Grant door access', parameters: [{ name: 'userId', type: 'string', required: true, defaultValue: 'user_001' }, { name: 'doorId', type: 'string', required: true, defaultValue: 'door_001' }], responseExample: { granted: true, message: 'Access granted' } },
  { path: '/api/v1/access/revoke', method: 'POST', summary: 'Revoke door access', parameters: [{ name: 'userId', type: 'string', required: true, defaultValue: 'user_001' }, { name: 'doorId', type: 'string', required: true, defaultValue: 'door_001' }], responseExample: { revoked: true } },
  { path: '/api/v1/access/logs', method: 'GET', summary: 'Access logs', parameters: [{ name: 'startDate', type: 'string', required: false, defaultValue: '2026-05-01' }, { name: 'limit', type: 'integer', required: false, defaultValue: 50 }], responseExample: { logs: [], total: 0 } },

  // Auth APIs
  { path: '/api/v1/auth/login', method: 'POST', summary: 'User login', parameters: [{ name: 'username', type: 'string', required: true, defaultValue: 'admin' }, { name: 'password', type: 'string', required: true, defaultValue: 'password123' }], responseExample: { token: 'eyJhbGciOiJIUzI1NiIs...', expiresIn: 3600 } },
  { path: '/api/v1/auth/logout', method: 'POST', summary: 'User logout', parameters: [], responseExample: { success: true } },
  { path: '/api/v1/auth/refresh', method: 'POST', summary: 'Refresh token', parameters: [{ name: 'refreshToken', type: 'string', required: true, defaultValue: 'refresh_token_123' }], responseExample: { token: 'new_token...' } },

  // System APIs
  { path: '/api/v1/system/health', method: 'GET', summary: 'System health check', parameters: [], responseExample: { status: 'healthy', uptime: 99.98, timestamp: '2026-05-21T10:00:00Z' } },
  { path: '/api/v1/system/metrics', method: 'GET', summary: 'System performance metrics', parameters: [], responseExample: { cpu: 45, memory: 62, disk: 38, requests: 1250 } },
  { path: '/api/v1/system/version', method: 'GET', summary: 'API version info', parameters: [], responseExample: { version: '2.1.0', buildDate: '2026-05-01', commit: 'a1b2c3d' } },

  // Report APIs
  { path: '/api/v1/report/daily', method: 'GET', summary: 'Daily report', parameters: [{ name: 'date', type: 'string', required: false, defaultValue: '2026-05-21' }], responseExample: { totalEnergy: 12450, alarms: 5, uptime: 99.98 } },
  { path: '/api/v1/report/export', method: 'POST', summary: 'Export report', parameters: [{ name: 'type', type: 'string', required: true, defaultValue: 'energy' }, { name: 'format', type: 'string', required: false, defaultValue: 'pdf' }, { name: 'startDate', type: 'string', required: true, defaultValue: '2026-05-01' }, { name: 'endDate', type: 'string', required: true, defaultValue: '2026-05-21' }], responseExample: { downloadUrl: '/reports/report.pdf', success: true } },

  // Notification APIs
  { path: '/api/v1/notification/send', method: 'POST', summary: 'Send notification', parameters: [{ name: 'userId', type: 'string', required: true, defaultValue: 'user_001' }, { name: 'title', type: 'string', required: true, defaultValue: 'Alert' }, { name: 'message', type: 'string', required: true, defaultValue: 'Device offline' }], responseExample: { sent: true, notificationId: 'notif_001' } },

  // Webhook APIs
  { path: '/api/v1/webhook/register', method: 'POST', summary: 'Register webhook', parameters: [{ name: 'url', type: 'string', required: true, defaultValue: 'https://example.com/webhook' }, { name: 'events', type: 'array', required: true, defaultValue: ['alarm.created'] }], responseExample: { webhookId: 'wh_001', success: true } }
])

const endpointSearch = ref('')
const filteredEndpoints = computed(() => {
  if (!endpointSearch.value) return apiEndpoints.value
  return apiEndpoints.value.filter(e => e.path.includes(endpointSearch.value) || e.summary.toLowerCase().includes(endpointSearch.value.toLowerCase()))
})

// Applications
const applications = ref([
  { id: 1, name: 'Mobile App', clientId: 'cli_mobile_7f3a4ba6', clientSecret: 'sec_8b9c0d1e2f3a4b5c', environment: 'production', status: 'active', createdAt: '2025-01-15' },
  { id: 2, name: 'Enterprise ERP', clientId: 'cli_erp_2b3c4d5e', clientSecret: 'sec_9c0d1e2f3a4b5c6d', environment: 'production', status: 'active', createdAt: '2025-02-01' },
  { id: 3, name: 'Third Party BMS', clientId: 'cli_bms_6f7g8h9i', clientSecret: 'sec_0d1e2f3a4b5c6d7e', environment: 'staging', status: 'active', createdAt: '2025-02-15' },
  { id: 4, name: 'IoT Gateway', clientId: 'cli_iot_4n5o6p7q', clientSecret: 'sec_2f3g4h5i6j7k8l9m', environment: 'production', status: 'active', createdAt: '2025-03-15' },
  { id: 5, name: 'Analytics Platform', clientId: 'cli_analytics_8r9s0t1u', clientSecret: 'sec_3g4h5i6j7k8l9m0n', environment: 'development', status: 'active', createdAt: '2025-04-01' }
])

const appSearch = ref('')
const filteredApplications = computed(() => {
  if (!appSearch.value) return applications.value
  return applications.value.filter(a => a.name.toLowerCase().includes(appSearch.value.toLowerCase()))
})

const shortenClientId = (id: string) => id?.length > 20 ? `${id.slice(0, 15)}...${id.slice(-6)}` : id

// API Keys - 全部渲染
const apiKeys = ref([
  { id: 1, appId: 1, appName: 'Mobile App', environment: 'production', apiKey: 'pk_live_7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d', createdAt: '2025-01-15', expiresAt: '2026-01-15' },
  { id: 2, appId: 1, appName: 'Mobile App', environment: 'staging', apiKey: 'pk_test_8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e', createdAt: '2025-01-15', expiresAt: '2026-01-15' },
  { id: 3, appId: 2, appName: 'Enterprise ERP', environment: 'production', apiKey: 'pk_live_9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f', createdAt: '2025-02-01', expiresAt: '2026-02-01' },
  { id: 4, appId: 2, appName: 'Enterprise ERP', environment: 'staging', apiKey: 'pk_test_0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5g', createdAt: '2025-02-01', expiresAt: '2026-02-01' },
  { id: 5, appId: 3, appName: 'Third Party BMS', environment: 'staging', apiKey: 'pk_test_1e2f3a4b5c6d7e8f9a0b1c2d3e4f5g6h', createdAt: '2025-02-15', expiresAt: '2026-02-15' },
  { id: 6, appId: 4, appName: 'IoT Gateway', environment: 'production', apiKey: 'pk_live_2f3a4b5c6d7e8f9a0b1c2d3e4f5g6h7i', createdAt: '2025-03-15', expiresAt: '2026-03-15' },
  { id: 7, appId: 5, appName: 'Analytics Platform', environment: 'development', apiKey: 'pk_dev_3f4a5b6c7d8e9f0a1b2c3d4e5f6g7h8i', createdAt: '2025-04-01', expiresAt: '2026-04-01' }
])

// Valid API Keys for authentication (simulated backend)
const validApiKeysSet = ref(new Set(apiKeys.value.map(k => k.apiKey)))

const rateLimits = ref([
  { id: 1, appId: 1, appName: 'Mobile App', apiPath: '/api/v1/device/*', dimension: 'user', limit: 1000, period: 'minute', action: '429' },
  { id: 2, appId: 2, appName: 'Enterprise ERP', apiPath: '*', dimension: 'ip', limit: 5000, period: 'hour', action: '429' },
  { id: 3, appId: 4, appName: 'IoT Gateway', apiPath: '/api/v1/device/*', dimension: 'ip', limit: 500, period: 'second', action: 'throttle' }
])

const apiLogs = ref([
  { id: 1, timestamp: '2026-05-21 09:32:15', appId: 1, appName: 'Mobile App', method: 'GET', path: '/api/v1/device/status', statusCode: 200, responseTime: 45, clientIp: '192.168.1.100' },
  { id: 2, timestamp: '2026-05-21 09:31:20', appId: 2, appName: 'Enterprise ERP', method: 'POST', path: '/api/v1/energy/record', statusCode: 201, responseTime: 128, clientIp: '10.0.0.50' },
  { id: 3, timestamp: '2026-05-21 09:28:30', appId: 3, appName: 'Third Party BMS', method: 'GET', path: '/api/v1/hvac/temperature', statusCode: 429, responseTime: 12, clientIp: '172.16.0.10' },
  { id: 4, timestamp: '2026-05-21 09:20:00', appId: 4, appName: 'IoT Gateway', method: 'POST', path: '/api/v1/device/register', statusCode: 500, responseTime: 1250, clientIp: '192.168.2.50' },
  { id: 5, timestamp: '2026-05-21 09:15:22', appId: 1, appName: 'Mobile App', method: 'GET', path: '/api/v1/alarm/list', statusCode: 200, responseTime: 67, clientIp: '192.168.1.101' }
])

const logAppFilter = ref<number | null>(null)
const filteredLogs = computed(() => {
  let result = apiLogs.value
  if (logAppFilter.value) result = result.filter(l => l.appId === logAppFilter.value)
  return result
})

const webhooks = ref([
  { id: 1, name: 'Alarm Webhook', url: 'https://api.example.com/webhook/alarm', events: ['alarm.created', 'device.offline'], status: 'active' },
  { id: 2, name: 'Energy Report', url: 'https://dashboard.company.com/webhook/energy', events: ['energy.threshold'], status: 'active' }
])

// Charts
const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart: any = null
let pieChart: any = null

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'axis' },
      grid: { left: '8%', right: '5%', bottom: '5%', top: '5%', containLabel: true },
      xAxis: { type: 'category', data: ['05/15', '05/16', '05/17', '05/18', '05/19', '05/20', '05/21'], axisLabel: { color: '#64748b' }, axisLine: { lineStyle: { color: '#e9ecef' } } },
      yAxis: { type: 'value', name: 'Calls', nameTextStyle: { color: '#64748b' }, axisLabel: { color: '#64748b' }, splitLine: { lineStyle: { color: '#e9ecef', type: 'dashed' } } },
      series: [{ data: [12450, 13580, 14200, 13800, 15600, 16800, 28450], type: 'line', smooth: true, lineStyle: { color: '#409eff', width: 3 }, areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#409eff40' }, { offset: 1, color: '#409eff05' }]) }, symbol: 'circle', symbolSize: 8, itemStyle: { color: '#409eff', borderColor: '#ffffff', borderWidth: 2 } }]
    })
  }
  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      backgroundColor: 'transparent', tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', left: 'left', textStyle: { color: '#64748b' } },
      series: [{ type: 'pie', radius: '55%', center: ['50%', '55%'], data: [
          { name: 'Device API', value: 12450, itemStyle: { color: '#3b82f6' } },
          { name: 'Energy API', value: 8230, itemStyle: { color: '#10b981' } },
          { name: 'Alarm API', value: 4560, itemStyle: { color: '#ef4444' } },
          { name: 'Contract API', value: 3210, itemStyle: { color: '#8b5cf6' } }
        ], label: { show: true, formatter: '{b}: {d}%', color: '#475569' } }]
    })
  }
}

// API Test Dialog
const testDialogVisible = ref(false)
const selectedEndpoint = ref<any>(null)
const testApiKey = ref('')
const testParams = ref<Record<string, any>>({})
const testLoading = ref(false)
const testResponse = ref<any>(null)

const openTestDialog = (endpoint: any) => {
  selectedEndpoint.value = endpoint
  testApiKey.value = ''
  testParams.value = {}
  testResponse.value = null

  if (endpoint.parameters) {
    endpoint.parameters.forEach((param: any) => {
      testParams.value[param.name] = param.defaultValue || ''
    })
  }
  testDialogVisible.value = true
}

const resetTestParams = () => {
  if (selectedEndpoint.value?.parameters) {
    selectedEndpoint.value.parameters.forEach((param: any) => {
      testParams.value[param.name] = param.defaultValue || ''
    })
  }
}

const executeApiTest = async () => {
  if (!testApiKey.value) {
    ElMessage.error('Please select API Key')
    return
  }

  const isValidKey = validApiKeysSet.value.has(testApiKey.value)

  if (!isValidKey) {
    testResponse.value = {
      status: 401,
      statusText: 'Unauthorized',
      time: Math.floor(Math.random() * 50 + 20),
      data: { error: 'Invalid API Key', message: 'The provided API key is not valid' }
    }
    return
  }

  testLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 500))

  const isSuccess = Math.random() > 0.1
  const endpoint = selectedEndpoint.value

  if (isSuccess) {
    let responseData = { ...endpoint.responseExample }
    if (Object.keys(testParams.value).length > 0) {
      responseData = { ...responseData, ...testParams.value }
    }
    testResponse.value = {
      status: endpoint.method === 'POST' ? 201 : 200,
      statusText: endpoint.method === 'POST' ? 'Created' : 'OK',
      time: Math.floor(Math.random() * 150 + 30),
      data: responseData
    }
    ElMessage.success('Request completed successfully')
  } else {
    testResponse.value = {
      status: 500,
      statusText: 'Internal Server Error',
      time: Math.floor(Math.random() * 200 + 100),
      data: { error: 'Internal Server Error', message: 'Something went wrong on the server' }
    }
    ElMessage.error('Request failed')
  }
  testLoading.value = false
}

const formatNumber = (num: number) => num >= 10000 ? (num / 10000).toFixed(1) + 'w' : num.toLocaleString()
const copyText = (text: string) => { navigator.clipboard.writeText(text); ElMessage.success('Copied') }
const refreshData = async () => { refreshing.value = true; await new Promise(r => setTimeout(r, 800)); ElMessage.success('Refreshed'); refreshing.value = false }
const searchLogs = () => ElMessage.success('Filtered')

// CRUD operations
const appDialogVisible = ref(false); const editingApp = ref<any>(null); const appForm = ref({ name: '', environment: 'production' })
const rateLimitDialogVisible = ref(false); const rateLimitForm = ref({ appId: null, apiPath: '*', limit: 1000, period: 'minute' })
const apiKeysDialogVisible = ref(false); const currentAppKeys = ref<any[]>([]); const currentAppId = ref<number | null>(null)
const webhookDialogVisible = ref(false); const editingWebhook = ref<any>(null); const webhookForm = ref({ name: '', url: '', events: [] })

const openCreateAppDialog = () => { editingApp.value = null; appForm.value = { name: '', environment: 'production' }; appDialogVisible.value = true }
const editApplication = (app: any) => { editingApp.value = app; appForm.value = { name: app.name, environment: app.environment }; appDialogVisible.value = true }
const saveApplication = () => {
  if (!appForm.value.name) { ElMessage.warning('Enter name'); return }
  if (editingApp.value) {
    const idx = applications.value.findIndex(a => a.id === editingApp.value.id)
    if (idx !== -1) applications.value[idx] = { ...applications.value[idx], name: appForm.value.name, environment: appForm.value.environment }
    ElMessage.success('Updated')
  } else {
    const newSecret = `sec_${Math.random().toString(36).substring(2, 20)}`
    const newId = Date.now()
    applications.value.push({ id: newId, name: appForm.value.name, clientId: `cli_${Math.random().toString(36).substring(2, 10)}`, clientSecret: newSecret, environment: appForm.value.environment, status: 'active', createdAt: new Date().toISOString().slice(0, 10) })
    ElMessage.success('Created')
  }
  appDialogVisible.value = false
}
const deleteApplication = async (app: any) => { await ElMessageBox.confirm(`Delete "${app.name}"?`, 'Confirm', { type: 'warning' }); applications.value = applications.value.filter(a => a.id !== app.id); ElMessage.success('Deleted') }

const viewApiKeys = (app: any) => { currentAppId.value = app.id; currentAppKeys.value = apiKeys.value.filter(k => k.appId === app.id); apiKeysDialogVisible.value = true }
const generateNewKeyForApp = () => {
  if (!currentAppId.value) return
  const app = applications.value.find(a => a.id === currentAppId.value)
  if (app) {
    const newKey = `pk_${app.environment === 'production' ? 'live' : app.environment === 'staging' ? 'test' : 'dev'}_${Math.random().toString(36).substring(2, 34)}`
    apiKeys.value.push({ id: Date.now(), appId: currentAppId.value, appName: app.name, environment: app.environment, apiKey: newKey, createdAt: new Date().toISOString().slice(0, 10), expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) })
    validApiKeysSet.value.add(newKey)
    currentAppKeys.value = apiKeys.value.filter(k => k.appId === currentAppId.value)
    ElMessage.success('Key generated')
  }
}
const generateNewKeyForActiveApp = () => {
  const activeApp = applications.value.find(a => a.status === 'active')
  if (activeApp) {
    const newKey = `pk_${activeApp.environment === 'production' ? 'live' : activeApp.environment === 'staging' ? 'test' : 'dev'}_${Math.random().toString(36).substring(2, 34)}`
    apiKeys.value.push({ id: Date.now(), appId: activeApp.id, appName: activeApp.name, environment: activeApp.environment, apiKey: newKey, createdAt: new Date().toISOString().slice(0, 10), expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10) })
    validApiKeysSet.value.add(newKey)
    ElMessage.success(`Key generated for ${activeApp.name}`)
  } else {
    ElMessage.warning('No active application found')
  }
}
const revokeKey = async (key: any) => { await ElMessageBox.confirm('Revoke this key?', 'Confirm', { type: 'warning' }); apiKeys.value = apiKeys.value.filter(k => k.id !== key.id); validApiKeysSet.value.delete(key.apiKey); if (currentAppId.value) currentAppKeys.value = apiKeys.value.filter(k => k.appId === currentAppId.value); ElMessage.success('Key revoked') }

const editRateLimit = (app: any) => { rateLimitForm.value = { appId: app.id, apiPath: '*', limit: 1000, period: 'minute' }; rateLimitDialogVisible.value = true }
const createRateLimit = () => { rateLimitForm.value = { appId: null, apiPath: '*', limit: 1000, period: 'minute' }; rateLimitDialogVisible.value = true }
const saveRateLimit = () => {
  if (!rateLimitForm.value.appId) { ElMessage.warning('Select app'); return }
  const app = applications.value.find(a => a.id === rateLimitForm.value.appId)
  if (app) { rateLimits.value.push({ id: Date.now(), appId: app.id, appName: app.name, apiPath: rateLimitForm.value.apiPath, dimension: 'user', limit: rateLimitForm.value.limit, period: rateLimitForm.value.period, action: '429' }); ElMessage.success('Rule added') }
  rateLimitDialogVisible.value = false
}
const deleteRateLimit = async (rule: any) => { await ElMessageBox.confirm('Delete rule?', 'Confirm', { type: 'warning' }); rateLimits.value = rateLimits.value.filter(r => r.id !== rule.id); ElMessage.success('Deleted') }

const createWebhook = () => { editingWebhook.value = null; webhookForm.value = { name: '', url: '', events: [] }; webhookDialogVisible.value = true }
const saveWebhook = () => {
  if (!webhookForm.value.name || !webhookForm.value.url) { ElMessage.warning('Fill required fields'); return }
  if (editingWebhook.value) {
    const idx = webhooks.value.findIndex(w => w.id === editingWebhook.value.id)
    if (idx !== -1) webhooks.value[idx] = { ...webhooks.value[idx], ...webhookForm.value }
    ElMessage.success('Updated')
  } else { webhooks.value.push({ id: Date.now(), name: webhookForm.value.name, url: webhookForm.value.url, events: webhookForm.value.events, status: 'active' }); ElMessage.success('Created') }
  webhookDialogVisible.value = false
}
const testWebhook = async (webhook: any) => { ElMessage.info(`Testing...`); await new Promise(r => setTimeout(r, 1000)); ElMessage.success('Test successful') }
const deleteWebhook = async (webhook: any) => { await ElMessageBox.confirm(`Delete "${webhook.name}"?`, 'Confirm', { type: 'warning' }); webhooks.value = webhooks.value.filter(w => w.id !== webhook.id); ElMessage.success('Deleted') }

const startLoading = () => {
  let progress = 0, msgIndex = 0
  const msgInterval = setInterval(() => { if (msgIndex < loadingMessages.length - 1) { msgIndex++; loadingMessage.value = loadingMessages[msgIndex] } }, 600)
  const progressInterval = setInterval(() => { if (progress < 90) { progress += Math.random() * 15; loadingProgress.value = Math.min(progress, 90) } }, 120)
  setTimeout(() => { clearInterval(msgInterval); clearInterval(progressInterval); loadingProgress.value = 100; setTimeout(() => { isPageLoaded.value = true; nextTick(() => setTimeout(initCharts, 200)) }, 400) }, 2000)
}
onMounted(() => startLoading())
</script>

<style scoped>
.api-management-page { background: #f5f7fa; min-height: 100%; padding: 24px; }
.page-container { max-width: 1400px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
.page-header h1 { font-size: 24px; font-weight: 700; color: #1a2c3e; margin: 0; }
.page-header p { color: #6c757d; margin: 2px 0 0; font-size: 12px; }
.header-actions { display: flex; gap: 10px; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: white; border-radius: 16px; padding: 16px; display: flex; align-items: center; gap: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; }
.stat-icon.blue { background: #e3f2fd; color: #2196f3; }
.stat-icon.green { background: #e8f5e9; color: #4caf50; }
.stat-icon.orange { background: #fff3e0; color: #ff9800; }
.stat-icon.purple { background: #f3e5f5; color: #9c27b0; }
.stat-value { font-size: 24px; font-weight: 700; color: #1a2c3e; }
.stat-label { font-size: 12px; color: #6c757d; }

.charts-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }
.chart-card { background: white; border-radius: 16px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.card-header { font-size: 15px; font-weight: 600; color: #1a2c3e; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.trend-chart, .pie-chart { width: 100%; }

.section-card { background: white; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
.section-header h3 { margin: 0; font-size: 16px; font-weight: 600; color: #1a2c3e; display: flex; align-items: center; gap: 8px; }

.equal-width-table { width: 100%; }
.equal-width-table :deep(.el-table__header), .equal-width-table :deep(.el-table__body) { width: 100% !important; }
.action-buttons { display: flex; gap: 6px; flex-wrap: nowrap; white-space: nowrap; }
.action-buttons .el-button { margin: 0; }

.mono { font-family: monospace; font-size: 11px; }
.copy-icon { margin-left: 6px; cursor: pointer; opacity: 0.5; font-size: 13px; vertical-align: middle; }
.copy-icon:hover { opacity: 1; }
.slow { color: #f44336; font-weight: 500; }
.fast { color: #4caf50; }
.empty-placeholder { text-align: center; padding: 30px; color: #999; }

.logs-filters { display: flex; gap: 10px; align-items: center; }

.test-container { padding: 8px; }
.test-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
.test-path { font-family: monospace; font-size: 14px; font-weight: 500; color: #1a2c3e; }
.test-auth { display: flex; gap: 12px; align-items: center; margin-bottom: 20px; flex-wrap: wrap; }
.auth-label { font-weight: 500; color: #1a2c3e; width: 70px; }
.test-params { margin-bottom: 20px; }
.params-label { font-weight: 500; color: #1a2c3e; margin-bottom: 12px; }
.param-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; flex-wrap: wrap; }
.param-name { font-family: monospace; font-weight: 500; width: 100px; }
.param-type { font-size: 11px; color: #6c757d; width: 60px; }
.param-required { font-size: 10px; color: #f44336; width: 60px; }
.test-actions { display: flex; gap: 12px; margin-bottom: 20px; }
.test-response { margin-top: 20px; border-top: 1px solid #e9ecef; padding-top: 16px; }
.response-header { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.response-time { font-size: 12px; color: #6c757d; }
.response-body { background: #1a2c3e; color: #e2e8f0; padding: 12px; border-radius: 8px; font-size: 11px; overflow-x: auto; margin: 0; }

.loading-container { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); z-index: 9999; display: flex; justify-content: center; align-items: center; }
.loading-content { text-align: center; padding: 40px; border-radius: 28px; background: rgba(15,23,42,0.6); backdrop-filter: blur(20px); border: 1px solid rgba(59,130,246,0.3); }
.loading-spinner { position: relative; width: 70px; height: 70px; margin: 0 auto 20px; }
.spinner-ring { position: absolute; width: 100%; height: 100%; border-radius: 50%; border: 3px solid transparent; animation: spin 1.5s infinite; }
.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.loading-text { font-size: 24px; font-weight: 700; color: #e2e8f0; margin-bottom: 16px; }
.loading-progress { width: 240px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 3px; margin: 0 auto 12px; overflow: hidden; }
.progress-bar { height: 100%; background: linear-gradient(90deg, #3b82f6, #8b5cf6); transition: width 0.3s; }
.loading-tip { font-size: 12px; color: #94a3b8; }
.loading-subtip { font-size: 10px; color: #64748b; margin-top: 6px; }

@media (max-width: 1000px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } .charts-row { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .api-management-page { padding: 12px; } .stats-grid { grid-template-columns: 1fr; } .section-header { flex-direction: column; align-items: flex-start; } .action-buttons { flex-wrap: wrap; } }

:deep(.el-table) { --el-table-bg-color: #fff; --el-table-header-bg-color: #f8f9fa; }
:deep(.el-table th) { background-color: #f8f9fa; font-weight: 600; color: #1a2c3e; }
</style>