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
        <div class="loading-tip">WebSocket Services</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="websocket-page">
    <!-- Page Header -->
    <div class="page-header">
      <div>
        <div class="breadcrumb">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>Data Platform</el-breadcrumb-item>
            <el-breadcrumb-item>Data Services</el-breadcrumb-item>
            <el-breadcrumb-item>WebSocket</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <h1>WebSocket Services</h1>
        <p class="description">Manage real-time WebSocket connections, subscriptions, and message streams</p>
      </div>
      <div class="header-actions">
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          Export Logs
        </el-button>
        <el-button type="primary" @click="openConnectionDialog">
          <el-icon><Plus /></el-icon>
          New Connection
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
                <span class="trend-label">vs last hour</span>
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

    <!-- Active Connections & Message Rate -->
    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="14">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Message Rate (messages/sec)</span>
              <el-radio-group v-model="ratePeriod" size="small">
                <el-radio-button value="realtime">Real-time</el-radio-button>
                <el-radio-button value="hourly">Hourly</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="rateChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="10">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Connection Summary</span>
            </div>
          </template>
          <div class="connection-summary">
            <div class="summary-item">
              <div class="summary-label">Active Connections</div>
              <div class="summary-value">{{ activeConnections }}</div>
              <div class="summary-trend up">+{{ newConnections }} new</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">Total Messages</div>
              <div class="summary-value">{{ totalMessages.toLocaleString() }}</div>
              <div class="summary-trend up">+{{ newMessages.toLocaleString() }}</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">Avg Latency</div>
              <div class="summary-value">{{ avgLatency }} ms</div>
              <div class="summary-trend down">-{{ latencyImprovement }} ms</div>
            </div>
            <div class="summary-item">
              <div class="summary-label">Uptime</div>
              <div class="summary-value">{{ uptime }}</div>
              <div class="summary-trend up">100%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Connection List -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Active Connections ({{ filteredConnections.length }})</span>
          <div class="table-actions">
            <el-input
                v-model="searchKeyword"
                placeholder="Search by ID or topic"
                prefix-icon="Search"
                clearable
                style="width: 200px"
            />
            <el-button :icon="Refresh" @click="fetchConnections" circle />
            <el-button :icon="Setting" @click="handleColumnSettings" circle />
          </div>
        </div>
      </template>

      <el-table :data="paginatedConnections" stripe style="width: 100%" v-loading="tableLoading">
        <el-table-column prop="id" label="Connection ID" width="140" />
        <el-table-column prop="url" label="URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'Connected' ? 'success' : 'danger'" size="small">
              <span class="status-dot" :class="row.status === 'Connected' ? 'connected' : 'disconnected'"></span>
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subscriptions" label="Subscriptions" width="120">
          <template #default="{ row }">
            <el-popover placement="top" :width="250" trigger="hover">
              <template #reference>
                <el-tag type="info" size="small" style="cursor: pointer">
                  {{ row.subscriptions.length }} topics
                </el-tag>
              </template>
              <div v-for="sub in row.subscriptions" :key="sub" class="topic-item">
                {{ sub }}
              </div>
            </el-popover>
          </template>
        </el-table-column>
        <el-table-column prop="messagesReceived" label="Messages" width="100" align="right" />
        <el-table-column prop="connectedAt" label="Connected At" width="160" />
        <el-table-column prop="lastActivity" label="Last Activity" width="160" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewMessages(row)">Messages</el-button>
            <el-button link type="danger" size="small" @click="disconnect(row)">Disconnect</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredConnections.length"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- WebSocket Client Tester -->
    <el-card class="tester-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>WebSocket Client Tester</span>
          <el-button-group>
            <el-button size="small" @click="clearMessages">Clear</el-button>
            <el-button size="small" @click="saveSession">Save Session</el-button>
          </el-button-group>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="16">
          <div class="connection-panel">
            <div class="connection-url">
              <el-input
                  v-model="wsUrl"
                  placeholder="ws://localhost:8080 or wss://example.com/ws"
                  style="width: 400px"
              />
              <el-button
                  :type="wsConnected ? 'danger' : 'primary'"
                  @click="toggleConnection"
                  :loading="connecting"
              >
                {{ wsConnected ? 'Disconnect' : 'Connect' }}
              </el-button>
              <el-tag v-if="wsConnected" type="success" size="default">Connected</el-tag>
              <el-tag v-else-if="wsConnecting" type="warning" size="default">Connecting...</el-tag>
            </div>

            <div class="subscription-panel">
              <div class="sub-header">
                <span>Subscriptions</span>
                <el-button size="small" @click="addSubscription">+ Add</el-button>
              </div>
              <div class="subscription-list">
                <div v-for="(sub, idx) in subscriptions" :key="idx" class="subscription-item">
                  <el-input v-model="sub.topic" placeholder="Topic name" size="small" style="width: 200px" />
                  <el-button
                      size="small"
                      type="primary"
                      @click="subscribe(sub.topic)"
                      :disabled="!wsConnected"
                  >
                    Subscribe
                  </el-button>
                  <el-button size="small" type="danger" @click="unsubscribe(sub.topic)">
                    Unsubscribe
                  </el-button>
                  <el-button size="small" @click="removeSubscription(idx)">Remove</el-button>
                </div>
              </div>
            </div>

            <div class="send-panel">
              <div class="send-header">
                <span>Send Message</span>
              </div>
              <el-input
                  v-model="sendTopic"
                  placeholder="Topic"
                  style="width: 200px; margin-right: 8px"
                  size="small"
              />
              <el-input
                  v-model="sendMessage"
                  placeholder='{"type": "message", "data": "hello"}'
                  style="flex: 1; margin-right: 8px"
                  size="small"
              />
              <el-button type="primary" @click="sendMessageWS" :disabled="!wsConnected">
                Send
              </el-button>
            </div>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="message-panel">
            <div class="message-header">
              <span>Received Messages</span>
              <el-badge :value="unreadCount" class="badge" />
            </div>
            <div class="message-list" ref="messageListRef">
              <div
                  v-for="(msg, idx) in displayedMessages"
                  :key="idx"
                  class="message-item"
                  :class="msg.type"
              >
                <div class="message-time">{{ msg.time }}</div>
                <div class="message-content">
                  <span class="message-topic">{{ msg.topic }}:</span>
                  <pre class="message-data">{{ formatMessage(msg.data) }}</pre>
                </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Message History Dialog -->
    <el-dialog v-model="messageDialogVisible" :title="`Message History - ${currentConnection?.id}`" width="800px" destroy-on-close>
      <div class="message-history">
        <el-table :data="currentConnection?.messages || []" size="small" border>
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="topic" label="Topic" width="150" />
          <el-table-column prop="data" label="Message" min-width="300">
            <template #default="{ row }">
              <pre class="message-preview">{{ JSON.stringify(row.data, null, 2) }}</pre>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="messageDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="exportMessages">Export</el-button>
      </template>
    </el-dialog>

    <!-- New Connection Dialog -->
    <el-dialog v-model="connectionDialogVisible" title="New WebSocket Connection" width="500px" destroy-on-close>
      <el-form :model="newConnectionForm" :rules="connectionRules" ref="connectionFormRef" label-width="100px">
        <el-form-item label="URL" prop="url">
          <el-input v-model="newConnectionForm.url" placeholder="ws://localhost:8080/ws" />
        </el-form-item>
        <el-form-item label="Protocols" prop="protocols">
          <el-input v-model="newConnectionForm.protocols" placeholder="Optional: graphql-ws, mqtt" />
        </el-form-item>
        <el-form-item label="Headers" prop="headers">
          <el-input v-model="newConnectionForm.headers" type="textarea" :rows="2" placeholder='{"Authorization": "Bearer token"}' />
        </el-form-item>
        <el-form-item label="Auto Reconnect" prop="autoReconnect">
          <el-switch v-model="newConnectionForm.autoReconnect" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="connectionDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="createConnection">Connect</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import {
  Plus, ArrowUp, ArrowDown, Document, Checked,
  Clock, TrendCharts, Refresh, Search, Download, Setting,
  Connection, Link, Message, Warning
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Initializing WebSocket services...',
  'Loading active connections...',
  'Almost ready...'
]

// ==================== Chart References ====================
const rateChartRef = ref<HTMLElement>()
let rateChart: echarts.ECharts | null = null
let messageInterval: any = null

// ==================== State ====================
const tableLoading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const ratePeriod = ref('realtime')
const activeConnections = ref(28)
const newConnections = ref(3)
const totalMessages = ref(1250000)
const newMessages = ref(12500)
const avgLatency = ref(45)
const latencyImprovement = ref(8)
const uptime = ref('99.95%')

// WebSocket Client State
const wsUrl = ref('wss://echo.websocket.org')
const wsConnected = ref(false)
const wsConnecting = ref(false)
let ws: WebSocket | null = null
const connecting = ref(false)
const subscriptions = ref<{ topic: string }[]>([{ topic: 'telemetry' }])
const sendTopic = ref('telemetry')
const sendMessage = ref('{"type": "ping"}')
const wsMessages = ref<any[]>([])
const unreadCount = ref(0)
const messageListRef = ref<HTMLElement>()

// Dialog States
const messageDialogVisible = ref(false)
const connectionDialogVisible = ref(false)
const currentConnection = ref<any>(null)
const connectionFormRef = ref()

const newConnectionForm = reactive({
  url: 'ws://localhost:8080/ws',
  protocols: '',
  headers: '',
  autoReconnect: true
})

const connectionRules = {
  url: [{ required: true, message: 'Please enter WebSocket URL', trigger: 'blur' }]
}

// Mock Connections Data
const connections = ref([
  {
    id: 'conn_001',
    url: 'wss://api.ibms.com/ws/telemetry',
    status: 'Connected',
    subscriptions: ['telemetry', 'alerts', 'device/status'],
    messagesReceived: 125000,
    connectedAt: '2024-01-20 08:00:00',
    lastActivity: '2024-01-20 10:30:00',
    messages: [
      { timestamp: '10:30:00', topic: 'telemetry', data: { device: 'CH-01', temp: 22.5 } },
      { timestamp: '10:29:55', topic: 'telemetry', data: { device: 'CH-01', temp: 22.4 } }
    ]
  },
  {
    id: 'conn_002',
    url: 'wss://api.ibms.com/ws/alerts',
    status: 'Connected',
    subscriptions: ['alerts', 'critical'],
    messagesReceived: 89000,
    connectedAt: '2024-01-20 07:30:00',
    lastActivity: '2024-01-20 10:28:00',
    messages: []
  },
  {
    id: 'conn_003',
    url: 'wss://api.ibms.com/ws/device/CH-01',
    status: 'Disconnected',
    subscriptions: ['telemetry'],
    messagesReceived: 45000,
    connectedAt: '2024-01-19 09:00:00',
    lastActivity: '2024-01-20 08:00:00',
    messages: []
  }
])

// ==================== Computed ====================
const filteredConnections = computed(() => {
  if (!searchKeyword.value) return connections.value
  return connections.value.filter(c =>
      c.id.toLowerCase().includes(searchKeyword.value.toLowerCase()) ||
      c.url.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

const paginatedConnections = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredConnections.value.slice(start, end)
})

const displayedMessages = computed(() => {
  return wsMessages.value.slice(-50)
})

// ==================== Helper Methods ====================
const formatMessage = (data: any) => {
  if (typeof data === 'string') return data
  return JSON.stringify(data, null, 2)
}

// ==================== Chart Initialization ====================
const initRateChart = () => {
  if (!rateChartRef.value) return
  if (rateChart) rateChart.dispose()

  rateChart = echarts.init(rateChartRef.value)

  const realtimeData = Array.from({ length: 60 }, () => Math.floor(Math.random() * 500) + 300)
  const hourlyData = [320, 380, 450, 520, 580, 620, 590, 550, 480, 420, 380, 340]

  const data = ratePeriod.value === 'realtime' ? realtimeData : hourlyData
  const xAxisData = ratePeriod.value === 'realtime'
      ? Array.from({ length: 60 }, (_, i) => `${i}s`)
      : ['1h', '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', '10h', '11h', '12h']

  const option: echarts.EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: xAxisData, axisLabel: { rotate: ratePeriod.value === 'realtime' ? 0 : 45 } },
    yAxis: { type: 'value', name: 'Messages/sec' },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      lineStyle: { width: 3, color: '#409eff' },
      areaStyle: { opacity: 0.1 },
      symbolSize: 4
    }]
  }

  rateChart.setOption(option)
  window.addEventListener('resize', () => rateChart?.resize())
}

// ==================== WebSocket Methods ====================
const toggleConnection = () => {
  if (wsConnected) {
    disconnectWS()
  } else {
    connectWS()
  }
}

const connectWS = () => {
  if (!wsUrl.value) {
    ElMessage.warning('Please enter WebSocket URL')
    return
  }

  connecting.value = true
  wsConnecting.value = true

  try {
    ws = new WebSocket(wsUrl.value)

    ws.onopen = () => {
      wsConnected.value = true
      wsConnecting.value = false
      connecting.value = false
      ElMessage.success('WebSocket connected')

      // Auto-subscribe
      subscriptions.value.forEach(sub => {
        if (sub.topic) subscribe(sub.topic)
      })

      // Start heartbeat
      startHeartbeat()
    }

    ws.onmessage = (event) => {
      const message = {
        time: new Date().toLocaleTimeString(),
        topic: 'received',
        data: event.data,
        type: 'received'
      }
      wsMessages.value.push(message)
      unreadCount.value++

      // Auto-scroll
      nextTick(() => {
        if (messageListRef.value) {
          messageListRef.value.scrollTop = messageListRef.value.scrollHeight
        }
      })
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      ElMessage.error('WebSocket connection error')
      wsConnecting.value = false
      connecting.value = false
    }

    ws.onclose = () => {
      wsConnected.value = false
      wsConnecting.value = false
      connecting.value = false
      ElMessage.warning('WebSocket disconnected')
      stopHeartbeat()

      if (newConnectionForm.autoReconnect) {
        setTimeout(() => {
          if (!wsConnected) connectWS()
        }, 3000)
      }
    }
  } catch (e) {
    ElMessage.error('Failed to connect')
    wsConnecting.value = false
    connecting.value = false
  }
}

const disconnectWS = () => {
  if (ws) {
    ws.close()
    ws = null
  }
  wsConnected.value = false
}

const subscribe = (topic: string) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    const subscribeMsg = JSON.stringify({ type: 'subscribe', topic: topic })
    ws.send(subscribeMsg)
    ElMessage.success(`Subscribed to ${topic}`)
  }
}

const unsubscribe = (topic: string) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    const unsubscribeMsg = JSON.stringify({ type: 'unsubscribe', topic: topic })
    ws.send(unsubscribeMsg)
    ElMessage.info(`Unsubscribed from ${topic}`)
  }
}

const sendMessageWS = () => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    let message = sendMessage.value
    try {
      // Try to parse as JSON to validate
      JSON.parse(message)
    } catch (e) {
      // Keep as string
    }

    const msg = JSON.stringify({
      type: 'publish',
      topic: sendTopic.value,
      payload: message
    })
    ws.send(msg)

    // Add to sent messages
    wsMessages.value.push({
      time: new Date().toLocaleTimeString(),
      topic: sendTopic.value,
      data: message,
      type: 'sent'
    })

    sendMessage.value = ''
  }
}

let heartbeatInterval: any = null

const startHeartbeat = () => {
  heartbeatInterval = setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'ping' }))
    }
  }, 30000)
}

const stopHeartbeat = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval)
    heartbeatInterval = null
  }
}

const addSubscription = () => {
  subscriptions.value.push({ topic: '' })
}

const removeSubscription = (index: number) => {
  const sub = subscriptions.value[index]
  if (sub.topic) unsubscribe(sub.topic)
  subscriptions.value.splice(index, 1)
}

const clearMessages = () => {
  wsMessages.value = []
  unreadCount.value = 0
  ElMessage.success('Messages cleared')
}

const saveSession = () => {
  const session = {
    url: wsUrl.value,
    subscriptions: subscriptions.value,
    timestamp: new Date().toISOString()
  }
  localStorage.setItem('ws_session', JSON.stringify(session))
  ElMessage.success('Session saved')
}

// ==================== Interactive Methods ====================
const handleCardClick = (stat: any) => {
  ElMessage.info(`Viewing ${stat.title} details`)
}

const handleExport = () => {
  ElMessage.success('Exporting WebSocket logs...')
}

const handleColumnSettings = () => {
  ElMessage.info('Column settings dialog would open here')
}

const fetchConnections = () => {
  tableLoading.value = true
  setTimeout(() => {
    tableLoading.value = false
    ElMessage.success('Data refreshed')
  }, 500)
}

const openConnectionDialog = () => {
  connectionDialogVisible.value = true
}

const createConnection = async () => {
  if (!connectionFormRef.value) return
  await connectionFormRef.value.validate((valid: boolean) => {
    if (valid) {
      wsUrl.value = newConnectionForm.url
      connectionDialogVisible.value = false
      connectWS()
    }
  })
}

const viewMessages = (connection: any) => {
  currentConnection.value = connection
  messageDialogVisible.value = true
}

const disconnect = (connection: any) => {
  ElMessage.info(`Disconnecting ${connection.id}...`)
  connection.status = 'Disconnected'
}

const exportMessages = () => {
  ElMessage.success('Exporting messages...')
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {}

// ==================== Simulate Real-time Data ====================
const startSimulation = () => {
  messageInterval = setInterval(() => {
    if (rateChart && ratePeriod.value === 'realtime') {
      const newData = Math.floor(Math.random() * 500) + 300
      const currentData = (rateChart.getOption() as any).series[0].data
      const newSeriesData = [...currentData.slice(1), newData]
      rateChart.setOption({ series: [{ data: newSeriesData }] })
    }
  }, 1000)
}

// ==================== Loading Simulation ====================
const initCharts = async () => {
  await nextTick()
  setTimeout(() => {
    initRateChart()
    startSimulation()
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
      fetchConnections()

      // Load saved session
      const saved = localStorage.getItem('ws_session')
      if (saved) {
        try {
          const session = JSON.parse(saved)
          wsUrl.value = session.url
          subscriptions.value = session.subscriptions
        } catch (e) {}
      }
    }, 400)
  }, 2000)
})

onUnmounted(() => {
  if (messageInterval) clearInterval(messageInterval)
  if (heartbeatInterval) clearInterval(heartbeatInterval)
  if (ws) ws.close()
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
.websocket-page {
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

.chart-card, .stats-card {
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

.connection-summary {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 8px;

  .summary-item {
    background: #f5f7fa;
    border-radius: 8px;
    padding: 16px;
    text-align: center;

    .summary-label {
      font-size: 13px;
      color: #909399;
      margin-bottom: 8px;
    }

    .summary-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
    }

    .summary-trend {
      font-size: 12px;
      margin-top: 4px;

      &.up { color: #67c23a; }
      &.down { color: #f56c6c; }
    }
  }
}

.table-card {
  margin-bottom: 20px;

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

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;

  &.connected {
    background-color: #67c23a;
    box-shadow: 0 0 4px #67c23a;
  }

  &.disconnected {
    background-color: #909399;
  }
}

.topic-item {
  padding: 4px 0;
  font-size: 13px;
  font-family: monospace;
}

.tester-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }
}

.connection-panel {
  .connection-url {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
  }

  .subscription-panel {
    margin-bottom: 16px;
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .sub-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      font-weight: 500;
    }

    .subscription-list {
      .subscription-item {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 8px;
      }
    }
  }

  .send-panel {
    padding: 12px;
    background: #f5f7fa;
    border-radius: 8px;

    .send-header {
      margin-bottom: 12px;
      font-weight: 500;
    }

    display: flex;
    flex-direction: column;

    > div:last-child {
      display: flex;
      align-items: center;
    }
  }
}

.message-panel {
  height: 100%;
  display: flex;
  flex-direction: column;

  .message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    font-weight: 500;
  }

  .message-list {
    height: 400px;
    overflow-y: auto;
    background: #1e1e1e;
    border-radius: 8px;
    padding: 8px;

    .message-item {
      margin-bottom: 8px;
      padding: 8px;
      border-radius: 6px;

      &.received {
        background: #2d2d2d;
        border-left: 3px solid #409eff;
      }

      &.sent {
        background: #2d2d2d;
        border-left: 3px solid #67c23a;
      }

      .message-time {
        font-size: 10px;
        color: #909399;
        margin-bottom: 4px;
      }

      .message-content {
        .message-topic {
          color: #e6a23c;
          font-size: 12px;
          font-family: monospace;
        }

        .message-data {
          display: inline;
          color: #d4d4d4;
          font-size: 12px;
          font-family: monospace;
          white-space: pre-wrap;
          word-break: break-all;
          margin: 0;
        }
      }
    }
  }
}

.message-history {
  .message-preview {
    background: #f5f7fa;
    padding: 8px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 11px;
    margin: 0;
    max-height: 100px;
    overflow-y: auto;
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