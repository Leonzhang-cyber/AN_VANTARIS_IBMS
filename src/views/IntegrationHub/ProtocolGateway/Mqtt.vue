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
        <div class="loading-tip">MQTT Gateway Management</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="mqtt-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Integration Hub</el-breadcrumb-item>
            <el-breadcrumb-item>Protocol Gateway</el-breadcrumb-item>
            <el-breadcrumb-item>MQTT</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>MQTT Gateway Management</h1>
        <p class="description">Manage MQTT broker connections, subscribe to topics, and publish messages</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="primary" @click="openAddConnectionDialog">
          <el-icon><Plus /></el-icon>
          Add Broker
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

    <!-- MQTT Brokers Table -->
    <el-card class="brokers-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>MQTT Brokers</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by name or host"
                prefix-icon="Search"
                clearable
                style="width: 220px"
            />
            <el-select v-model="statusFilter" placeholder="Status" clearable style="width: 120px">
              <el-option label="Connected" value="Connected" />
              <el-option label="Disconnected" value="Disconnected" />
              <el-option label="Connecting" value="Connecting" />
            </el-select>
            <el-button :icon="Refresh" @click="fetchBrokers" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedBrokers" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="name" label="Broker Name" min-width="160" show-overflow-tooltip />
        <el-table-column prop="host" label="Host" width="180" />
        <el-table-column prop="port" label="Port" width="80" />
        <el-table-column prop="clientId" label="Client ID" min-width="160" show-overflow-tooltip />
        <el-table-column prop="subscriptionCount" label="Subscriptions" width="110" align="center" />
        <el-table-column prop="messageRate" label="Msg Rate" width="90" align="center" />
        <el-table-column prop="status" label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Connected' ? 'success' : row.status === 'Connecting' ? 'warning' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Connected' ? 'online' : 'offline'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastSeen" label="Last Seen" width="150" />
        <el-table-column label="Actions" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewTopics(row)">Topics ({{ row.subscriptionCount }})</el-button>
            <el-button link type="success" size="small" @click="publishMessage(row)">Publish</el-button>
            <el-button link type="info" size="small" @click="testConnection(row)">Test</el-button>
            <el-button link type="danger" size="small" @click="deleteBroker(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredBrokers.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- Topics & Messages Section -->
    <el-card class="topics-card" shadow="hover" v-if="selectedBroker">
      <template #header>
        <div class="card-header">
          <span>Topics & Messages - {{ selectedBroker.name }}</span>
          <div class="topics-actions">
            <el-button size="small" type="primary" @click="openSubscribeDialog">
              <el-icon><Plus /></el-icon> Subscribe
            </el-button>
            <el-button size="small" @click="refreshTopics">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div class="topics-list">
            <el-table :data="subscriptions" stripe size="small" v-loading="topicsLoading" max-height="400">
              <el-table-column prop="topic" label="Topic" min-width="200" show-overflow-tooltip />
              <el-table-column prop="qos" label="QoS" width="60" align="center" />
              <el-table-column prop="status" label="Status" width="80">
                <template #default="{ row }">
                  <el-tag :type="row.status === 'Subscribed' ? 'success' : 'warning'" size="small">{{ row.status }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Actions" width="100">
                <template #default="{ row }">
                  <el-button link type="primary" size="small" @click="unsubscribe(row)">Unsubscribe</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-col>

        <el-col :span="12">
          <div class="messages-panel">
            <div class="messages-header">
              <span>Received Messages</span>
              <el-button size="small" @click="clearMessages">Clear</el-button>
            </div>
            <div class="messages-list" ref="messagesListRef">
              <div v-for="(msg, idx) in displayedMessages" :key="idx" class="message-item">
                <div class="message-time">{{ msg.time }}</div>
                <div class="message-topic">{{ msg.topic }}</div>
                <div class="message-payload">{{ formatPayload(msg.payload) }}</div>
              </div>
              <div v-if="displayedMessages.length === 0" class="empty-messages">
                <el-empty description="No messages received" :image-size="60" />
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Add/Edit Broker Connection Dialog -->
    <el-dialog v-model="brokerDialogVisible" :title="dialogMode === 'add' ? 'Add MQTT Broker' : 'Edit MQTT Broker'" width="650px" destroy-on-close class="broker-dialog">
      <el-tabs v-model="activeConfigTab">
        <el-tab-pane label="Connection Settings" name="basic">
          <el-form :model="brokerForm" :rules="brokerRules" ref="brokerFormRef" label-width="130px">
            <el-form-item label="Broker Name" prop="name">
              <el-input v-model="brokerForm.name" placeholder="Enter broker name" />
            </el-form-item>
            <el-form-item label="Host" prop="host">
              <el-input v-model="brokerForm.host" placeholder="mqtt.example.com or 192.168.1.100" />
            </el-form-item>
            <el-form-item label="Port" prop="port">
              <el-input-number v-model="brokerForm.port" :min="1" :max="65535" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Protocol" prop="protocol">
              <el-radio-group v-model="brokerForm.protocol">
                <el-radio value="tcp">TCP (mqtt://)</el-radio>
                <el-radio value="ssl">SSL/TLS (mqtts://)</el-radio>
                <el-radio value="ws">WebSocket (ws://)</el-radio>
                <el-radio value="wss">WebSocket Secure (wss://)</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="Client ID" prop="clientId">
              <el-input v-model="brokerForm.clientId" placeholder="Auto-generated if empty" />
            </el-form-item>
            <el-form-item label="Username" prop="username">
              <el-input v-model="brokerForm.username" placeholder="Optional" />
            </el-form-item>
            <el-form-item label="Password" prop="password">
              <el-input v-model="brokerForm.password" type="password" placeholder="Optional" show-password />
            </el-form-item>
            <el-form-item label="Keep Alive (s)" prop="keepAlive">
              <el-input-number v-model="brokerForm.keepAlive" :min="5" :max="300" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Clean Session" prop="cleanSession">
              <el-switch v-model="brokerForm.cleanSession" />
              <span style="margin-left: 8px; color: #909399">Start a clean session on each connection</span>
            </el-form-item>
            <el-form-item label="Description" prop="description">
              <el-input v-model="brokerForm.description" type="textarea" :rows="2" placeholder="Enter description" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="TLS/SSL Settings" name="tls" v-if="brokerForm.protocol === 'ssl' || brokerForm.protocol === 'wss'">
          <el-form label-width="130px">
            <el-form-item label="CA Certificate">
              <el-upload action="#" :auto-upload="false" :on-change="handleCACertUpload" :limit="1">
                <el-button size="small">Select CA Certificate</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="Client Certificate">
              <el-upload action="#" :auto-upload="false" :on-change="handleClientCertUpload" :limit="1">
                <el-button size="small">Select Client Certificate</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="Private Key">
              <el-upload action="#" :auto-upload="false" :on-change="handleKeyUpload" :limit="1">
                <el-button size="small">Select Private Key</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="Verify Certificate">
              <el-switch v-model="brokerForm.verifyCert" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="150px">
            <el-form-item label="Auto Reconnect">
              <el-switch v-model="brokerForm.autoReconnect" />
            </el-form-item>
            <el-form-item label="Max Reconnect Attempts">
              <el-input-number v-model="brokerForm.maxReconnectAttempts" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Reconnect Delay (ms)">
              <el-input-number v-model="brokerForm.reconnectDelay" :min="1000" :max="60000" :step="1000" style="width: 100%" />
            </el-form-item>
            <el-form-item label="Enable Logging">
              <el-switch v-model="brokerForm.enableLogging" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="brokerDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="testBrokerConnection" :loading="testing">
          Test Connection
        </el-button>
        <el-button type="success" @click="saveBroker">
          Save Broker
        </el-button>
      </template>
    </el-dialog>

    <!-- Subscribe Dialog -->
    <el-dialog v-model="subscribeDialogVisible" title="Subscribe to Topic" width="500px" destroy-on-close>
      <el-form :model="subscribeForm" :rules="subscribeRules" ref="subscribeFormRef" label-width="100px">
        <el-form-item label="Topic" prop="topic">
          <el-input v-model="subscribeForm.topic" placeholder="e.g., sensors/+/temperature" />
        </el-form-item>
        <el-form-item label="QoS" prop="qos">
          <el-radio-group v-model="subscribeForm.qos">
            <el-radio :label="0">0 - At most once</el-radio>
            <el-radio :label="1">1 - At least once</el-radio>
            <el-radio :label="2">2 - Exactly once</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="subscribeDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="doSubscribe">Subscribe</el-button>
      </template>
    </el-dialog>

    <!-- Publish Message Dialog -->
    <el-dialog v-model="publishDialogVisible" title="Publish Message" width="550px" destroy-on-close>
      <el-form :model="publishForm" :rules="publishRules" ref="publishFormRef" label-width="100px">
        <el-form-item label="Topic" prop="topic">
          <el-input v-model="publishForm.topic" placeholder="e.g., sensors/device1/temperature" />
        </el-form-item>
        <el-form-item label="QoS" prop="qos">
          <el-radio-group v-model="publishForm.qos">
            <el-radio :label="0">0 - At most once</el-radio>
            <el-radio :label="1">1 - At least once</el-radio>
            <el-radio :label="2">2 - Exactly once</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Retain" prop="retain">
          <el-switch v-model="publishForm.retain" />
          <span style="margin-left: 8px; color: #909399">Keep message on broker</span>
        </el-form-item>
        <el-form-item label="Payload" prop="payload">
          <el-input
              v-model="publishForm.payload"
              type="textarea"
              :rows="4"
              placeholder='{"temperature": 22.5, "unit": "°C"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="publishDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="doPublish">Publish</el-button>
      </template>
    </el-dialog>

    <!-- Test Connection Result Dialog -->
    <el-dialog v-model="testDialogVisible" title="Connection Test Result" width="450px">
      <div class="test-result">
        <el-result
            :icon="testResult.success ? 'success' : 'error'"
            :title="testResult.success ? 'Connection Successful' : 'Connection Failed'"
            :sub-title="testResult.message"
        />
        <div v-if="testResult.success && testResult.details" class="test-details">
          <p><strong>Broker:</strong> {{ testResult.details.broker }}</p>
          <p><strong>Version:</strong> {{ testResult.details.version }}</p>
          <p><strong>Response Time:</strong> {{ testResult.details.responseTime }}ms</p>
          <p><strong>Session Present:</strong> {{ testResult.details.sessionPresent ? 'Yes' : 'No' }}</p>
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
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download,
  Delete, Connection, Edit, Message, Lock
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const loadingMessages = ['Preparing...', 'Initializing MQTT gateway...', 'Loading brokers...', 'Almost ready...']

// ==================== State ====================
const tableLoading = ref(false)
const topicsLoading = ref(false)
const testing = ref(false)
const brokerDialogVisible = ref(false)
const subscribeDialogVisible = ref(false)
const publishDialogVisible = ref(false)
const testDialogVisible = ref(false)
const dialogMode = ref<'add' | 'edit'>('add')
const selectedBroker = ref<any>(null)
const searchKeyword = ref('')
const statusFilter = ref('')
const activeConfigTab = ref('basic')
const currentPage = ref(1)
const pageSize = ref(10)
const messagesListRef = ref<HTMLElement>()

const testResult = reactive({ success: false, message: '', details: null as any })
const brokerFormRef = ref()
const subscribeFormRef = ref()
const publishFormRef = ref()

// Mock messages data
const receivedMessages = ref<any[]>([])

// ==================== Mock Data ====================
const statsCards = ref([
  { title: 'Brokers', value: '6', trend: 2, icon: 'Connection', bgColor: '#409eff', key: 'brokers', subTitle: 'Connected: 5' },
  { title: 'Subscriptions', value: '24', trend: 8, icon: 'Document', bgColor: '#67c23a', key: 'subscriptions', subTitle: 'Active: 22' },
  { title: 'Messages/sec', value: '1,234', trend: 15, icon: 'Message', bgColor: '#e6a23c', key: 'rate', subTitle: 'Peak: 1,567' },
  { title: 'Retained Msgs', value: '156', trend: 5, icon: 'Clock', bgColor: '#f56c6c', key: 'retained', subTitle: 'Total stored' }
])

const brokers = ref([
  { id: 1, name: 'Production MQTT Broker', host: 'mqtt.production.com', port: 1883, protocol: 'tcp', clientId: 'gateway_prod_01', subscriptionCount: 12, messageRate: 456, status: 'Connected', lastSeen: '2024-01-20 10:30:00' },
  { id: 2, name: 'Test Broker', host: 'test.mqtt.local', port: 1883, protocol: 'tcp', clientId: 'gateway_test_01', subscriptionCount: 5, messageRate: 89, status: 'Connected', lastSeen: '2024-01-20 10:28:00' },
  { id: 3, name: 'Secure Broker', host: 'mqtts.secure.com', port: 8883, protocol: 'ssl', clientId: 'gateway_secure_01', subscriptionCount: 7, messageRate: 234, status: 'Connected', lastSeen: '2024-01-20 10:32:00' },
  { id: 4, name: 'Development Broker', host: 'dev.mqtt.local', port: 1883, protocol: 'tcp', clientId: 'gateway_dev_01', subscriptionCount: 0, messageRate: 0, status: 'Disconnected', lastSeen: '2024-01-20 08:15:00' },
  { id: 5, name: 'Cloud MQTT', host: 'mqtt.cloud.com', port: 1883, protocol: 'tcp', clientId: 'gateway_cloud_01', subscriptionCount: 8, messageRate: 567, status: 'Connected', lastSeen: '2024-01-20 10:31:00' }
])

const subscriptionsMap = ref<Record<number, any[]>>({
  1: [
    { id: 1, topic: 'sensors/+/temperature', qos: 1, status: 'Subscribed' },
    { id: 2, topic: 'devices/+/status', qos: 0, status: 'Subscribed' },
    { id: 3, topic: 'alerts/+/critical', qos: 2, status: 'Subscribed' }
  ],
  2: [
    { id: 4, topic: 'test/+/data', qos: 0, status: 'Subscribed' }
  ],
  3: [
    { id: 5, topic: 'secure/+/telemetry', qos: 1, status: 'Subscribed' }
  ],
  5: [
    { id: 6, topic: 'cloud/+/metrics', qos: 1, status: 'Subscribed' }
  ]
})

// Forms
const brokerForm = reactive({
  id: null, name: '', host: '', port: 1883, protocol: 'tcp', clientId: '',
  username: '', password: '', keepAlive: 60, cleanSession: true, description: '',
  autoReconnect: true, maxReconnectAttempts: 10, reconnectDelay: 5000, enableLogging: true,
  verifyCert: true, caCert: '', clientCert: '', privateKey: ''
})

const subscribeForm = reactive({ topic: '', qos: 1 })
const publishForm = reactive({ topic: '', qos: 1, retain: false, payload: '{"message": "test"}' })

// Rules
const brokerRules = {
  name: [{ required: true, message: 'Please enter broker name', trigger: 'blur' }],
  host: [{ required: true, message: 'Please enter host', trigger: 'blur' }],
  port: [{ required: true, message: 'Please enter port', trigger: 'blur' }]
}

const subscribeRules = {
  topic: [{ required: true, message: 'Please enter topic', trigger: 'blur' }]
}

const publishRules = {
  topic: [{ required: true, message: 'Please enter topic', trigger: 'blur' }],
  payload: [{ required: true, message: 'Please enter payload', trigger: 'blur' }]
}

// ==================== Computed ====================
const filteredBrokers = computed(() => {
  let filtered = [...brokers.value]
  if (searchKeyword.value) filtered = filtered.filter(b => b.name.toLowerCase().includes(searchKeyword.value.toLowerCase()) || b.host.toLowerCase().includes(searchKeyword.value.toLowerCase()))
  if (statusFilter.value) filtered = filtered.filter(b => b.status === statusFilter.value)
  return filtered
})

const paginatedBrokers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBrokers.value.slice(start, end)
})

const subscriptions = computed(() => subscriptionsMap.value[selectedBroker.value?.id] || [])
const displayedMessages = computed(() => receivedMessages.value.slice(-50))

// ==================== Helper Methods ====================
const formatPayload = (payload: any) => {
  if (typeof payload === 'object') return JSON.stringify(payload, null, 2)
  return payload
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesListRef.value) {
      messagesListRef.value.scrollTop = messagesListRef.value.scrollHeight
    }
  })
}

// Simulate receiving a message
const simulateMessage = (topic: string, payload: any) => {
  receivedMessages.value.push({
    time: new Date().toLocaleTimeString(),
    topic: topic,
    payload: payload
  })
  scrollToBottom()
}

// ==================== Broker Methods ====================
const handleCardClick = (stat: any) => ElMessage.info(`Viewing ${stat.title} details`)
const handleExport = () => ElMessage.success('Exporting MQTT configuration...')
const fetchBrokers = () => { tableLoading.value = true; setTimeout(() => { tableLoading.value = false; ElMessage.success('Brokers refreshed') }, 500) }

const openAddConnectionDialog = () => {
  dialogMode.value = 'add'
  Object.assign(brokerForm, {
    id: null, name: '', host: '', port: 1883, protocol: 'tcp', clientId: '',
    username: '', password: '', keepAlive: 60, cleanSession: true, description: '',
    autoReconnect: true, maxReconnectAttempts: 10, reconnectDelay: 5000, enableLogging: true,
    verifyCert: true, caCert: '', clientCert: '', privateKey: ''
  })
  brokerDialogVisible.value = true
}

const editBroker = (broker: any) => {
  dialogMode.value = 'edit'
  Object.assign(brokerForm, broker)
  brokerDialogVisible.value = true
}

const testBrokerConnection = () => {
  testing.value = true
  setTimeout(() => {
    testing.value = false
    testResult.success = true
    testResult.message = 'Successfully connected to MQTT broker'
    testResult.details = { broker: `${brokerForm.host}:${brokerForm.port}`, version: '5.0', responseTime: 45, sessionPresent: true }
    testDialogVisible.value = true
  }, 1500)
}

const saveBroker = async () => {
  if (!brokerFormRef.value) return
  await brokerFormRef.value.validate((valid: boolean) => {
    if (valid) {
      ElMessage.success(dialogMode.value === 'add' ? 'Broker added successfully' : 'Broker updated successfully')
      brokerDialogVisible.value = false
    }
  })
}

const deleteBroker = (broker: any) => {
  ElMessageBox.confirm(`Delete broker "${broker.name}"? This will also remove all subscriptions.`, 'Confirm Delete', {
    confirmButtonText: 'Delete', cancelButtonText: 'Cancel', type: 'warning'
  }).then(() => {
    const index = brokers.value.findIndex(b => b.id === broker.id)
    if (index !== -1) { brokers.value.splice(index, 1); if (selectedBroker.value?.id === broker.id) selectedBroker.value = null; ElMessage.success(`Deleted: ${broker.name}`) }
  }).catch(() => {})
}

const testConnection = (broker: any) => {
  ElMessage.info(`Testing connection to ${broker.name}...`)
  setTimeout(() => { ElMessage.success(`Connection to ${broker.name} is ${broker.status}`) }, 1000)
}

const viewTopics = (broker: any) => {
  selectedBroker.value = broker
  refreshTopics()
}

const refreshTopics = () => {
  topicsLoading.value = true
  setTimeout(() => { topicsLoading.value = false; ElMessage.success('Topics refreshed') }, 500)
}

const publishMessage = (broker: any) => {
  selectedBroker.value = broker
  publishForm.topic = ''
  publishForm.payload = '{"message": "test"}'
  publishForm.qos = 1
  publishForm.retain = false
  publishDialogVisible.value = true
}

// ==================== Subscription Methods ====================
const openSubscribeDialog = () => {
  subscribeForm.topic = ''
  subscribeForm.qos = 1
  subscribeDialogVisible.value = true
}

const doSubscribe = async () => {
  if (!subscribeFormRef.value) return
  await subscribeFormRef.value.validate((valid: boolean) => {
    if (valid) {
      const newSub = {
        id: Date.now(),
        topic: subscribeForm.topic,
        qos: subscribeForm.qos,
        status: 'Subscribed'
      }
      if (!subscriptionsMap.value[selectedBroker.value.id]) {
        subscriptionsMap.value[selectedBroker.value.id] = []
      }
      subscriptionsMap.value[selectedBroker.value.id].push(newSub)
      ElMessage.success(`Subscribed to ${subscribeForm.topic}`)
      subscribeDialogVisible.value = false
      refreshTopics()

      // Simulate receiving a message on this topic
      setTimeout(() => {
        simulateMessage(subscribeForm.topic, { message: 'Test message', timestamp: new Date().toISOString() })
      }, 500)
    }
  })
}

const unsubscribe = (sub: any) => {
  ElMessageBox.confirm(`Unsubscribe from "${sub.topic}"?`, 'Confirm', {
    confirmButtonText: 'Unsubscribe', cancelButtonText: 'Cancel', type: 'info'
  }).then(() => {
    const subs = subscriptionsMap.value[selectedBroker.value.id]
    const index = subs.findIndex(s => s.id === sub.id)
    if (index !== -1) subs.splice(index, 1)
    ElMessage.success(`Unsubscribed from ${sub.topic}`)
    refreshTopics()
  }).catch(() => {})
}

// ==================== Publish Methods ====================
const doPublish = async () => {
  if (!publishFormRef.value) return
  await publishFormRef.value.validate((valid: boolean) => {
    if (valid) {
      let payload = publishForm.payload
      try {
        // Try to parse as JSON for display
        JSON.parse(payload)
      } catch (e) {
        // Keep as string
      }
      ElMessage.success(`Published to ${publishForm.topic}`)
      publishDialogVisible.value = false

      // Simulate receiving the published message (echo)
      simulateMessage(publishForm.topic, payload)
    }
  })
}

const clearMessages = () => {
  receivedMessages.value = []
  ElMessage.success('Messages cleared')
}

// File upload handlers
const handleCACertUpload = (file: any) => { brokerForm.caCert = file.name }
const handleClientCertUpload = (file: any) => { brokerForm.clientCert = file.name }
const handleKeyUpload = (file: any) => { brokerForm.privateKey = file.name }

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// ==================== Mounted ====================
onMounted(() => {
  let messageIndex = 0
  const messageInterval = setInterval(() => { if (messageIndex < loadingMessages.length - 1) messageIndex++; loadingMessage.value = loadingMessages[messageIndex] }, 400)
  const progressInterval = setInterval(() => { if (loadingProgress.value < 100) { loadingProgress.value += Math.random() * 15 + 5; if (loadingProgress.value > 100) loadingProgress.value = 100 } }, 200)
  setTimeout(() => {
    clearInterval(messageInterval); clearInterval(progressInterval); loadingProgress.value = 100; loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true; fetchBrokers() }, 400)
  }, 2000)
})
</script>

<style scoped lang="scss">
/* Loading screen styles */
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
.loading-dots span {
  animation: bounce 1.4s infinite ease-in-out both;
}
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

/* Main page styles */
.mqtt-page {
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

.brokers-card, .topics-card { margin-bottom: 20px; }
.brokers-card .card-header, .topics-card .card-header { display: flex; justify-content: space-between; align-items: center; font-weight: 600; }
.brokers-card .table-actions, .topics-card .topics-actions { display: flex; gap: 12px; align-items: center; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.topics-list { border: 1px solid #ebeef5; border-radius: 8px; overflow: hidden; }
.messages-panel {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  height: 400px;
  display: flex;
  flex-direction: column;
}
.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #ebeef5;
  background: #f5f7fa;
  font-weight: 500;
}
.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.message-item {
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 12px;
}
.message-item:hover { background: #f5f7fa; }
.message-time { color: #909399; font-size: 11px; margin-bottom: 4px; }
.message-topic { font-weight: 600; color: #409eff; font-family: monospace; margin-bottom: 4px; }
.message-payload { color: #606266; font-family: monospace; white-space: pre-wrap; word-break: break-all; background: #fafafa; padding: 4px; border-radius: 4px; }
.empty-messages { padding: 40px; text-align: center; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.online { background-color: #67c23a; box-shadow: 0 0 4px #67c23a; }
.status-dot.offline { background-color: #909399; }

.broker-dialog :deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
.test-details { margin-top: 16px; padding: 16px; background: #f5f7fa; border-radius: 8px; }
.test-details p { margin: 8px 0; }

:deep(.el-table) { font-size: 13px; }
:deep(.el-dialog__body) { max-height: 60vh; overflow-y: auto; }
:deep(.el-tabs__header) { margin-bottom: 0; }
</style>