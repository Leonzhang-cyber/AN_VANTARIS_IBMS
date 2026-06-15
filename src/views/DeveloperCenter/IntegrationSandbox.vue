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
          <span class="loading-title">Loading Integration Sandbox</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Test and Validate Integrations in a Safe Environment</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="integration-sandbox-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Integration Sandbox</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Developer Center</el-breadcrumb-item>
          <el-breadcrumb-item>Integration Sandbox</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createNewSandbox">
          <el-icon><Plus /></el-icon>
          New Sandbox
        </el-button>
        <el-button type="success" plain @click="importConfiguration">
          <el-icon><Upload /></el-icon>
          Import Config
        </el-button>
        <el-button type="info" plain @click="viewDocumentation">
          <el-icon><Document /></el-icon>
          Documentation
        </el-button>
      </div>
    </div>

    <!-- Sandbox Environment Status -->
    <div class="status-section">
      <el-card class="status-card" shadow="hover">
        <div class="status-grid">
          <div class="status-item">
            <div class="status-icon"><el-icon :size="28"><Service /></el-icon></div>
            <div class="status-info">
              <div class="status-label">Sandbox Status</div>
              <div class="status-value success">Active</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon"><el-icon :size="28"><Clock /></el-icon></div>
            <div class="status-info">
              <div class="status-label">Session Time</div>
              <div class="status-value">{{ sessionTime }}</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon"><el-icon :size="28"><DataLine /></el-icon></div>
            <div class="status-info">
              <div class="status-label">API Calls (Today)</div>
              <div class="status-value">{{ apiCallsToday }}</div>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon"><el-icon :size="28"><CircleCheck /></el-icon></div>
            <div class="status-info">
              <div class="status-label">Success Rate</div>
              <div class="status-value">{{ successRate }}%</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Main Sandbox Layout -->
    <div class="sandbox-layout">
      <!-- Left Panel - Request Builder -->
      <div class="request-panel">
        <el-card class="request-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Edit /></el-icon> Request Builder</span>
              <div class="request-controls">
                <el-select v-model="selectedMethod" size="small" style="width: 110px">
                  <el-option label="GET" value="GET" />
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                  <el-option label="DELETE" value="DELETE" />
                  <el-option label="PATCH" value="PATCH" />
                </el-select>
                <el-button size="small" @click="formatJson">
                  <el-icon><MagicStick /></el-icon> Format
                </el-button>
                <el-button size="small" @click="clearRequest">
                  <el-icon><Delete /></el-icon> Clear
                </el-button>
              </div>
            </div>
          </template>
          <div class="endpoint-section">
            <div class="endpoint-input">
              <span class="endpoint-label">Endpoint URL</span>
              <el-input v-model="endpointUrl" placeholder="/api/v1/devices" size="large">
                <template #prepend>https://api.ibms.com</template>
              </el-input>
            </div>
          </div>
          <div class="headers-section">
            <div class="section-title">
              <span>Headers</span>
              <el-button text type="primary" size="small" @click="addHeader">
                <el-icon><Plus /></el-icon> Add Header
              </el-button>
            </div>
            <div v-for="(header, idx) in headers" :key="idx" class="header-row">
              <el-input v-model="header.key" placeholder="Header Name" size="small" style="width: 200px" />
              <el-input v-model="header.value" placeholder="Header Value" size="small" style="flex: 1" />
              <el-button size="small" text type="danger" @click="removeHeader(idx)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          <div class="body-section">
            <div class="section-title">
              <span>Request Body</span>
              <el-radio-group v-model="bodyType" size="small">
                <el-radio-button label="json">JSON</el-radio-button>
                <el-radio-button label="xml">XML</el-radio-button>
                <el-radio-button label="form">Form Data</el-radio-button>
              </el-radio-group>
            </div>
            <el-input
                v-model="requestBody"
                type="textarea"
                :rows="10"
                placeholder='{
  "deviceId": "bacnet-gw-01",
  "command": "read_point",
  "parameters": {
    "pointId": "analog_input_1"
  }
}'
                class="body-textarea"
            />
          </div>
          <div class="action-buttons">
            <el-button type="primary" size="large" @click="sendRequest" :loading="sending">
              <el-icon><Share /></el-icon> Send Request
            </el-button>
            <el-button size="large" @click="saveToCollection">
              <el-icon><Document /></el-icon> Save to Collection
            </el-button>
            <el-button size="large" @click="generateCodeSnippet">
              <el-icon><CopyDocument /></el-icon> Generate Code
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- Right Panel - Response -->
      <div class="response-panel">
        <el-card class="response-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataAnalysis /></el-icon> Response</span>
              <div class="response-controls">
                <el-tag :type="responseStatus === 200 ? 'success' : 'danger'" size="small">
                  Status: {{ responseStatus }}
                </el-tag>
                <el-button size="small" text @click="copyResponse">
                  <el-icon><CopyDocument /></el-icon> Copy
                </el-button>
                <el-button size="small" text @click="downloadResponse">
                  <el-icon><Download /></el-icon> Download
                </el-button>
              </div>
            </div>
          </template>
          <div class="response-tabs">
            <el-tabs v-model="activeResponseTab">
              <el-tab-pane label="Body" name="body">
                <div class="response-body">
                  <pre class="response-pre">{{ formattedResponse }}</pre>
                </div>
              </el-tab-pane>
              <el-tab-pane label="Headers" name="headers">
                <el-table :data="responseHeadersList" stripe size="small">
                  <el-table-column prop="key" label="Header" width="200" />
                  <el-table-column prop="value" label="Value" />
                </el-table>
              </el-tab-pane>
              <el-tab-pane label="Timeline" name="timeline">
                <div class="timeline-info">
                  <div class="timeline-item">
                    <span class="timeline-label">DNS Lookup:</span>
                    <span class="timeline-value">{{ dnsLookup }} ms</span>
                  </div>
                  <div class="timeline-item">
                    <span class="timeline-label">TCP Connection:</span>
                    <span class="timeline-value">{{ tcpConnection }} ms</span>
                  </div>
                  <div class="timeline-item">
                    <span class="timeline-label">SSL Handshake:</span>
                    <span class="timeline-value">{{ sslHandshake }} ms</span>
                  </div>
                  <div class="timeline-item">
                    <span class="timeline-label">Request Sent:</span>
                    <span class="timeline-value">{{ requestSent }} ms</span>
                  </div>
                  <div class="timeline-item">
                    <span class="timeline-label">Waiting (TTFB):</span>
                    <span class="timeline-value">{{ ttfb }} ms</span>
                  </div>
                  <div class="timeline-item">
                    <span class="timeline-label">Content Download:</span>
                    <span class="timeline-value">{{ contentDownload }} ms</span>
                  </div>
                  <div class="timeline-item total">
                    <span class="timeline-label">Total Time:</span>
                    <span class="timeline-value">{{ totalTime }} ms</span>
                  </div>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </div>
    </div>

    <!-- API Documentation & Examples -->
    <div class="docs-section">
      <el-card class="docs-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Document /></el-icon> API Documentation & Examples</span>
            <el-button text type="primary" @click="viewFullDocs">View Full Documentation</el-button>
          </div>
        </template>
        <div class="docs-grid">
          <div v-for="api in apiExamples" :key="api.name" class="api-item">
            <div class="api-header">
              <el-tag :type="api.method === 'GET' ? 'success' : api.method === 'POST' ? 'primary' : 'warning'" size="small">{{ api.method }}</el-tag>
              <span class="api-path">{{ api.path }}</span>
              <el-button size="small" text type="primary" @click="tryExample(api)">
                <el-icon><MagicStick /></el-icon> Try it
              </el-button>
            </div>
            <div class="api-description">{{ api.description }}</div>
            <div class="api-params" v-if="api.params">
              <span class="params-label">Parameters:</span>
              <span class="params-value">{{ api.params }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Test History -->
    <div class="history-section">
      <el-card class="history-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><List /></el-icon> Test History</span>
            <el-button text type="primary" @click="clearHistory">Clear History</el-button>
          </div>
        </template>
        <el-table :data="testHistory" stripe style="width: 100%">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="method" label="Method" width="80">
            <template #default="{ row }">
              <el-tag :type="getMethodTagType(row.method)" size="small">{{ row.method }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="endpoint" label="Endpoint" min-width="250" show-overflow-tooltip />
          <el-table-column prop="status" label="Status" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 200 ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="Duration" width="80" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="replayRequest(row)">Replay</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Environment Variables -->
    <div class="env-section">
      <el-card class="env-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Setting /></el-icon> Environment Variables</span>
            <el-button text type="primary" size="small" @click="addVariable">
              <el-icon><Plus /></el-icon> Add Variable
            </el-button>
          </div>
        </template>
        <div class="env-grid">
          <div v-for="(variable, idx) in environmentVariables" :key="idx" class="env-row">
            <el-input v-model="variable.key" placeholder="Variable Name" size="small" style="width: 200px" />
            <el-input v-model="variable.value" placeholder="Variable Value" size="small" style="flex: 1" />
            <el-input v-model="variable.description" placeholder="Description" size="small" style="width: 200px" />
            <el-button size="small" text type="danger" @click="removeVariable(idx)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="runTests">
          <el-icon><VideoPlay /></el-icon>
          Run Integration Tests
        </el-button>
        <el-button type="success" plain @click="exportCollection">
          <el-icon><Download /></el-icon>
          Export Collection
        </el-button>
        <el-button type="warning" plain @click="validateSchema">
          <el-icon><CircleCheck /></el-icon>
          Validate Schema
        </el-button>
        <el-button type="info" plain @click="viewLogs">
          <el-icon><List /></el-icon>
          View Logs
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Setting, User, Clock, Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic, Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service, Search, Edit, Plus, VideoPlay,
  VideoPause, Operation, Headset, Monitor, Cpu, Connection, Lock, Key, Medal,
  Flag, DataAnalysis, EditPen, Tickets, Filter, SuccessFilled, List
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing Integration Sandbox...')

const loadingMessages = [
  'Initializing Integration Sandbox...',
  'Loading API endpoints...',
  'Preparing test environment...',
  'Sandbox ready for testing!'
]

// Sandbox status
const sessionTime = ref('04:32:18')
const apiCallsToday = ref(156)
const successRate = ref(94.2)
let timerInterval: number

// Request builder
const selectedMethod = ref('GET')
const endpointUrl = ref('/api/v1/devices')
const headers = ref<Array<{ key: string; value: string }>>([
  { key: 'Content-Type', value: 'application/json' },
  { key: 'Authorization', value: 'Bearer {{api_key}}' }
])
const bodyType = ref('json')
const requestBody = ref(`{
  "deviceId": "bacnet-gw-01",
  "command": "read_point",
  "parameters": {
    "pointId": "analog_input_1"
  }
}`)
const sending = ref(false)

// Response
const responseStatus = ref(200)
const responseBody = ref('')
const activeResponseTab = ref('body')
const dnsLookup = ref(12)
const tcpConnection = ref(34)
const sslHandshake = ref(56)
const requestSent = ref(0)
const ttfb = ref(78)
const contentDownload = ref(23)
const totalTime = ref(203)

const responseHeadersList = ref([
  { key: 'content-type', value: 'application/json' },
  { key: 'content-length', value: '1245' },
  { key: 'x-request-id', value: 'req_abc123def456' },
  { key: 'x-response-time', value: '78ms' }
])

const formattedResponse = computed(() => {
  try {
    return JSON.stringify(JSON.parse(responseBody.value || '{}'), null, 2)
  } catch {
    return responseBody.value || 'No response yet. Send a request to see results.'
  }
})

// API Examples
const apiExamples = ref([
  { name: 'Get All Devices', method: 'GET', path: '/api/v1/devices', description: 'Retrieve list of all registered devices', params: '?limit=10&offset=0' },
  { name: 'Get Device Details', method: 'GET', path: '/api/v1/devices/{deviceId}', description: 'Get detailed information about a specific device', params: 'deviceId: bacnet-gw-01' },
  { name: 'Write Point Value', method: 'POST', path: '/api/v1/devices/{deviceId}/points/{pointId}/write', description: 'Write a value to a device point', params: 'value: 22.5' },
  { name: 'Execute Command', method: 'POST', path: '/api/v1/devices/{deviceId}/commands', description: 'Execute a command on a device', params: 'command: restart' },
  { name: 'Get Alarms', method: 'GET', path: '/api/v1/alarms', description: 'Retrieve active alarms', params: 'severity=critical&limit=20' }
])

// Test history
const testHistory = ref([
  { timestamp: '2024-01-15 09:45:32', method: 'GET', endpoint: '/api/v1/devices', status: 200, duration: '203ms' },
  { timestamp: '2024-01-15 09:32:18', method: 'POST', endpoint: '/api/v1/devices/bacnet-gw-01/commands', status: 201, duration: '187ms' },
  { timestamp: '2024-01-15 09:15:22', method: 'GET', endpoint: '/api/v1/alarms?severity=critical', status: 200, duration: '156ms' },
  { timestamp: '2024-01-15 08:55:12', method: 'PUT', endpoint: '/api/v1/devices/hvac-01/points/temp', status: 400, duration: '98ms' }
])

// Environment variables
const environmentVariables = ref([
  { key: 'api_key', value: 'ibms_live_sk_abc123xyz', description: 'API Authentication Key' },
  { key: 'base_url', value: 'https://api.ibms.com', description: 'Base API URL' },
  { key: 'tenant_id', value: 'tenant_acme_corp', description: 'Tenant/Organization ID' }
])

// Helper functions
const getMethodTagType = (method: string) => {
  switch (method) {
    case 'GET': return 'success'
    case 'POST': return 'primary'
    case 'PUT': return 'warning'
    case 'DELETE': return 'danger'
    default: return 'info'
  }
}

const formatJson = () => {
  try {
    const parsed = JSON.parse(requestBody.value)
    requestBody.value = JSON.stringify(parsed, null, 2)
    ElMessage.success('JSON formatted')
  } catch {
    ElMessage.error('Invalid JSON format')
  }
}

const clearRequest = () => {
  requestBody.value = ''
  endpointUrl.value = '/api/v1/devices'
  headers.value = [{ key: 'Content-Type', value: 'application/json' }]
  ElMessage.info('Request cleared')
}

const addHeader = () => {
  headers.value.push({ key: '', value: '' })
}

const removeHeader = (idx: number) => {
  headers.value.splice(idx, 1)
}

const sendRequest = async () => {
  sending.value = true
  // Simulate API request
  setTimeout(() => {
    responseStatus.value = 200
    responseBody.value = JSON.stringify({
      success: true,
      data: {
        deviceId: 'bacnet-gw-01',
        name: 'BACnet Gateway',
        status: 'online',
        points: [
          { id: 'analog_input_1', name: 'Temperature Sensor', value: 22.5, unit: '°C' },
          { id: 'analog_input_2', name: 'Humidity Sensor', value: 55, unit: '%' },
          { id: 'binary_output_1', name: 'Chiller Status', value: 'running' }
        ],
        lastSeen: new Date().toISOString()
      },
      timestamp: new Date().toISOString()
    }, null, 2)

    // Add to history
    testHistory.value.unshift({
      timestamp: new Date().toLocaleString(),
      method: selectedMethod.value,
      endpoint: endpointUrl.value,
      status: responseStatus.value,
      duration: `${totalTime.value}ms`
    })

    sending.value = false
    ElMessage.success('Request sent successfully')
  }, 800)
}

const saveToCollection = () => {
  ElMessage.info('Request saved to collection')
}

const generateCodeSnippet = () => {
  ElMessageBox.alert(
      `// JavaScript Example\nfetch('https://api.ibms.com${endpointUrl.value}', {\n  method: '${selectedMethod.value}',\n  headers: {\n    'Content-Type': 'application/json',\n    'Authorization': 'Bearer YOUR_API_KEY'\n  },\n  body: JSON.stringify(${requestBody.value || 'null'})\n})\n.then(res => res.json())\n.then(data => console.log(data));`,
      'Code Snippet',
      { confirmButtonText: 'Copy', type: 'info' }
  )
}

const copyResponse = () => {
  navigator.clipboard.writeText(responseBody.value)
  ElMessage.success('Response copied to clipboard')
}

const downloadResponse = () => {
  const blob = new Blob([responseBody.value], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `response_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('Response downloaded')
}

const tryExample = (api: any) => {
  selectedMethod.value = api.method
  endpointUrl.value = api.path
  if (api.method === 'POST') {
    requestBody.value = JSON.stringify({ example: true, params: api.params }, null, 2)
  }
  ElMessage.info(`Loaded example: ${api.name}`)
}

const clearHistory = () => {
  ElMessageBox.confirm('Clear all test history?', 'Confirm', {
    confirmButtonText: 'Clear',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    testHistory.value = []
    ElMessage.success('History cleared')
  }).catch(() => {})
}

const replayRequest = (item: any) => {
  selectedMethod.value = item.method as any
  endpointUrl.value = item.endpoint
  sendRequest()
  ElMessage.info(`Replaying: ${item.method} ${item.endpoint}`)
}

const addVariable = () => {
  environmentVariables.value.push({ key: '', value: '', description: '' })
}

const removeVariable = (idx: number) => {
  environmentVariables.value.splice(idx, 1)
}

const createNewSandbox = () => {
  ElMessage.info('Creating new sandbox environment...')
  setTimeout(() => {
    ElMessage.success('New sandbox created')
  }, 1500)
}

const importConfiguration = () => {
  ElMessage.info('Import configuration dialog opened')
}

const viewDocumentation = () => {
  ElMessage.info('Opening API documentation')
}

const runTests = () => {
  ElMessage.info('Running integration tests...')
  setTimeout(() => {
    ElMessage.success('All tests passed (12/12)')
  }, 2000)
}

const exportCollection = () => {
  ElMessage.info('Exporting collection...')
}

const validateSchema = () => {
  ElMessage.info('Validating JSON schema...')
  setTimeout(() => {
    ElMessage.success('Schema validation passed')
  }, 1000)
}

const viewLogs = () => {
  ElMessage.info('Viewing sandbox logs')
}

const viewFullDocs = () => {
  ElMessage.info('Opening full API documentation')
}

// Update session timer
const updateSessionTimer = () => {
  const hours = Math.floor(Math.random() * 2)
  const minutes = Math.floor(Math.random() * 60)
  const seconds = Math.floor(Math.random() * 60)
  sessionTime.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

// Loading animation
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
      timerInterval = setInterval(updateSessionTimer, 1000)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style scoped>
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
  font-size: 24px;
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

/* ==================== Main Content ==================== */
.integration-sandbox-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Status Section */
.status-section {
  margin-bottom: 24px;
}

.status-card {
  border-radius: 12px;
  background: white;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 8px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.status-icon {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.status-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.status-value {
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
}

.status-value.success {
  color: #10b981;
}

/* Sandbox Layout */
.sandbox-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.request-card,
.response-card {
  border-radius: 12px;
  background: white;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.request-controls,
.response-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.endpoint-section {
  margin-bottom: 20px;
}

.endpoint-input {
  margin-bottom: 12px;
}

.endpoint-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  color: #475569;
  margin-bottom: 12px;
}

.headers-section {
  margin-bottom: 20px;
}

.header-row {
  display: flex;
  gap: 12px;
  margin-bottom: 8px;
  align-items: center;
}

.body-section {
  margin-bottom: 20px;
}

.body-textarea {
  font-family: monospace;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

/* Response Panel */
.response-body {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px;
  max-height: 400px;
  overflow: auto;
}

.response-pre {
  font-family: monospace;
  font-size: 12px;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  color: #1e293b;
}

.timeline-info {
  padding: 12px;
}

.timeline-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.timeline-item.total {
  font-weight: 700;
  color: #1e293b;
  border-bottom: none;
  padding-top: 12px;
}

.timeline-label {
  color: #64748b;
}

.timeline-value {
  color: #1e293b;
  font-family: monospace;
}

/* Docs Section */
.docs-section {
  margin-bottom: 24px;
}

.docs-card {
  border-radius: 12px;
  background: white;
}

.docs-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.api-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.api-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.api-path {
  font-family: monospace;
  font-size: 13px;
  color: #1e293b;
}

.api-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 6px;
}

.api-params {
  font-size: 11px;
  color: #94a3b8;
}

.params-label {
  font-weight: 500;
  color: #64748b;
}

/* History Section */
.history-section {
  margin-bottom: 24px;
}

.history-card {
  border-radius: 12px;
  background: white;
}

/* Env Section */
.env-section {
  margin-bottom: 24px;
}

.env-card {
  border-radius: 12px;
  background: white;
}

.env-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.env-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* Footer Actions */
.footer-actions {
  margin-top: 8px;
}

.action-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .sandbox-layout {
    grid-template-columns: 1fr;
  }

  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .status-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .env-row {
    flex-direction: column;
  }

  .env-row .el-input {
    width: 100% !important;
  }
}
</style>