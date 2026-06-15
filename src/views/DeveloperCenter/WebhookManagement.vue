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
          <span class="loading-title">Loading Webhook Management</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Configure and Monitor Webhook Integrations</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="webhook-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Webhook Management</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Developer Center</el-breadcrumb-item>
          <el-breadcrumb-item>Webhook Management</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="createWebhook">
          <el-icon><Plus /></el-icon>
          Create Webhook
        </el-button>
        <el-button type="success" plain @click="exportWebhooks">
          <el-icon><Download /></el-icon>
          Export Config
        </el-button>
        <el-button type="info" plain @click="viewDocumentation">
          <el-icon><Document /></el-icon>
          Documentation
        </el-button>
      </div>
    </div>

    <!-- Webhook Statistics -->
    <div class="stats-section">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><Connection /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalWebhooks }}</div>
            <div class="stat-label">Total Webhooks</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><SuccessFilled /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ activeWebhooks }}</div>
            <div class="stat-label">Active Webhooks</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><DataLine /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ totalDeliveries }}</div>
            <div class="stat-label">Total Deliveries (30d)</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-icon"><el-icon :size="32"><CircleCheck /></el-icon></div>
          <div class="stat-info">
            <div class="stat-value">{{ successRate }}%</div>
            <div class="stat-label">Success Rate</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Webhooks List -->
    <div class="webhooks-section">
      <el-card class="webhooks-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><List /></el-icon> Webhook Endpoints</span>
            <div class="webhook-filters">
              <el-select v-model="statusFilter" placeholder="Status" size="small" style="width: 120px" clearable>
                <el-option label="All" value="" />
                <el-option label="Active" value="active" />
                <el-option label="Inactive" value="inactive" />
                <el-option label="Failed" value="failed" />
              </el-select>
              <el-input v-model="searchWebhook" placeholder="Search webhooks..." size="small" style="width: 200px" clearable />
              <el-button size="small" @click="refreshWebhooks">
                <el-icon><Refresh /></el-icon> Refresh
              </el-button>
            </div>
          </div>
        </template>
        <div class="webhooks-list">
          <div v-for="webhook in filteredWebhooks" :key="webhook.id" class="webhook-item">
            <div class="webhook-header">
              <div class="webhook-info">
                <div class="webhook-name">
                  <span class="name">{{ webhook.name }}</span>
                  <el-tag :type="webhook.status === 'active' ? 'success' : 'danger'" size="small">{{ webhook.status }}</el-tag>
                </div>
                <div class="webhook-url">{{ webhook.url }}</div>
                <div class="webhook-meta">
                  <span><el-icon><Message /></el-icon> Events: {{ webhook.events.join(', ') }}</span>
                  <span><el-icon><Clock /></el-icon> Created: {{ webhook.createdAt }}</span>
                  <span><el-icon><DataLine /></el-icon> Deliveries: {{ webhook.deliveries }}</span>
                </div>
              </div>
              <div class="webhook-actions">
                <el-button size="small" text type="primary" @click="testWebhook(webhook)">
                  <el-icon><MagicStick /></el-icon> Test
                </el-button>
                <el-button size="small" text type="primary" @click="editWebhook(webhook)">
                  <el-icon><Edit /></el-icon> Edit
                </el-button>
                <el-button size="small" text type="danger" @click="deleteWebhook(webhook)">
                  <el-icon><Delete /></el-icon> Delete
                </el-button>
                <el-switch v-model="webhook.status" active-value="active" inactive-value="inactive" @change="toggleWebhook(webhook)" />
              </div>
            </div>
            <div class="webhook-stats">
              <div class="stat-bar">
                <div class="stat-label">Last 7 days delivery rate</div>
                <div class="stat-progress">
                  <el-progress :percentage="webhook.successRate" :stroke-width="8" :color="webhook.successRate >= 90 ? '#10b981' : webhook.successRate >= 70 ? '#f59e0b' : '#ef4444'" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Recent Deliveries -->
    <div class="deliveries-section">
      <el-card class="deliveries-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Clock /></el-icon> Recent Deliveries</span>
            <el-button text type="primary" @click="viewAllDeliveries">View All</el-button>
          </div>
        </template>
        <el-table :data="recentDeliveries" stripe style="width: 100%">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="webhookName" label="Webhook" width="180" />
          <el-table-column prop="event" label="Event" width="140">
            <template #default="{ row }">
              <el-tag size="small">{{ row.event }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 200 ? 'success' : 'danger'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="duration" label="Duration" width="80" />
          <el-table-column prop="response" label="Response" min-width="200" show-overflow-tooltip />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="viewDeliveryDetails(row)">Details</el-button>
              <el-button size="small" text type="warning" @click="redeliverDelivery(row)">Redeliver</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Failed Deliveries -->
    <div class="failed-section">
      <el-card class="failed-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Warning /></el-icon> Failed Deliveries</span>
            <el-button text type="primary" @click="retryAllFailed">Retry All</el-button>
          </div>
        </template>
        <el-table :data="failedDeliveries" stripe style="width: 100%">
          <el-table-column prop="timestamp" label="Time" width="160" />
          <el-table-column prop="webhookName" label="Webhook" width="180" />
          <el-table-column prop="event" label="Event" width="140" />
          <el-table-column prop="error" label="Error" min-width="250" show-overflow-tooltip />
          <el-table-column prop="retryCount" label="Retries" width="80" />
          <el-table-column label="Actions" width="150">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="retryDelivery(row)">Retry</el-button>
              <el-button size="small" text type="info" @click="viewErrorDetails(row)">Details</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Event Types Configuration -->
    <div class="events-section">
      <el-card class="events-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Tickets /></el-icon> Available Event Types</span>
            <el-button text type="primary" @click="subscribeToEvents">Subscribe to Events</el-button>
          </div>
        </template>
        <div class="events-grid">
          <div v-for="event in eventTypes" :key="event.name" class="event-item">
            <div class="event-icon" :style="{ backgroundColor: event.color }">
              <el-icon :size="20"><component :is="event.icon" /></el-icon>
            </div>
            <div class="event-info">
              <div class="event-name">{{ event.name }}</div>
              <div class="event-description">{{ event.description }}</div>
            </div>
            <div class="event-count">{{ event.subscriptions }} webhooks</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Security Settings -->
    <div class="security-section">
      <el-card class="security-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Lock /></el-icon> Security Settings</span>
            <el-button text type="primary" @click="configureSecurity">Configure</el-button>
          </div>
        </template>
        <div class="security-grid">
          <div class="security-item">
            <div class="security-label">HMAC Signature</div>
            <div class="security-value">{{ hmacEnabled ? 'Enabled' : 'Disabled' }}</div>
            <el-tag :type="hmacEnabled ? 'success' : 'info'" size="small">{{ hmacEnabled ? 'Active' : 'Inactive' }}</el-tag>
          </div>
          <div class="security-item">
            <div class="security-label">IP Whitelisting</div>
            <div class="security-value">{{ ipWhitelist.length }} IPs configured</div>
            <el-button size="small" text type="primary" @click="editIpWhitelist">Edit</el-button>
          </div>
          <div class="security-item">
            <div class="security-label">Rate Limiting</div>
            <div class="security-value">{{ rateLimit }} req/minute</div>
            <el-tag type="warning" size="small">Per endpoint</el-tag>
          </div>
          <div class="security-item">
            <div class="security-label">SSL Verification</div>
            <div class="security-value">{{ sslVerification ? 'Strict' : 'Disabled' }}</div>
            <el-tag :type="sslVerification ? 'success' : 'warning'" size="small">{{ sslVerification ? 'Enabled' : 'Disabled' }}</el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="testEndpoint">
          <el-icon><MagicStick /></el-icon>
          Test Endpoint
        </el-button>
        <el-button type="success" plain @click="generateWebhookSecret">
          <el-icon><Key /></el-icon>
          Generate Secret
        </el-button>
        <el-button type="warning" plain @click="viewLogs">
          <el-icon><List /></el-icon>
          View Logs
        </el-button>
        <el-button type="info" plain @click="viewMetrics">
          <el-icon><TrendCharts /></el-icon>
          Metrics
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
const loadingMessage = ref('Loading Webhook Management...')

const loadingMessages = [
  'Loading Webhook Management...',
  'Fetching webhook endpoints...',
  'Loading delivery history...',
  'Webhook management ready!'
]

// Statistics
const totalWebhooks = ref(24)
const activeWebhooks = ref(18)
const totalDeliveries = ref(12450)
const successRate = ref(94.2)

// Filters
const statusFilter = ref('')
const searchWebhook = ref('')

// Webhooks data
const webhooks = ref([
  {
    id: 1,
    name: 'Alert Notification Service',
    url: 'https://alerts.mycompany.com/webhook/ibms',
    events: ['alarm.triggered', 'device.offline', 'threshold.exceeded'],
    status: 'active',
    createdAt: '2024-01-10',
    deliveries: 1245,
    successRate: 98.5
  },
  {
    id: 2,
    name: 'SIEM Integration',
    url: 'https://siem.security.com/ingest/ibms-events',
    events: ['security.intrusion', 'access.denied', 'login.failed'],
    status: 'active',
    createdAt: '2024-01-08',
    deliveries: 2340,
    successRate: 99.2
  },
  {
    id: 3,
    name: 'Slack Notifications',
    url: 'https://hooks.slack.com/services/T0001/B0001/XXX',
    events: ['workorder.created', 'workorder.completed', 'alarm.acknowledged'],
    status: 'active',
    createdAt: '2024-01-05',
    deliveries: 3456,
    successRate: 97.8
  },
  {
    id: 4,
    name: 'ITSM Ticket System',
    url: 'https://itsm.company.com/api/webhooks/ibms',
    events: ['incident.reported', 'maintenance.scheduled'],
    status: 'inactive',
    createdAt: '2023-12-28',
    deliveries: 567,
    successRate: 45.2
  },
  {
    id: 5,
    name: 'Dashboard Widget',
    url: 'https://dashboard.internal/events/ingest',
    events: ['energy.updated', 'device.status.changed'],
    status: 'active',
    createdAt: '2023-12-20',
    deliveries: 3567,
    successRate: 96.3
  }
])

const filteredWebhooks = computed(() => {
  let result = webhooks.value
  if (statusFilter.value) {
    result = result.filter(w => w.status === statusFilter.value)
  }
  if (searchWebhook.value) {
    const search = searchWebhook.value.toLowerCase()
    result = result.filter(w => w.name.toLowerCase().includes(search) || w.url.toLowerCase().includes(search))
  }
  return result
})

// Recent deliveries
const recentDeliveries = ref([
  { id: 1, timestamp: '2024-01-15 09:45:32', webhookName: 'Alert Notification Service', event: 'alarm.triggered', status: 200, duration: '124ms', response: 'OK' },
  { id: 2, timestamp: '2024-01-15 09:32:18', webhookName: 'SIEM Integration', event: 'security.intrusion', status: 200, duration: '187ms', response: 'Ingested' },
  { id: 3, timestamp: '2024-01-15 09:28:45', webhookName: 'Slack Notifications', event: 'workorder.created', status: 200, duration: '98ms', response: 'sent' },
  { id: 4, timestamp: '2024-01-15 09:15:22', webhookName: 'ITSM Ticket System', event: 'incident.reported', status: 500, duration: '302ms', response: 'Internal Server Error' },
  { id: 5, timestamp: '2024-01-15 09:08:33', webhookName: 'Dashboard Widget', event: 'energy.updated', status: 200, duration: '76ms', response: 'OK' }
])

// Failed deliveries
const failedDeliveries = ref([
  { id: 101, timestamp: '2024-01-15 09:15:22', webhookName: 'ITSM Ticket System', event: 'incident.reported', error: 'Connection timeout after 30s', retryCount: 3 },
  { id: 102, timestamp: '2024-01-14 23:45:12', webhookName: 'Alert Notification Service', event: 'alarm.triggered', error: 'SSL certificate verification failed', retryCount: 2 },
  { id: 103, timestamp: '2024-01-14 14:20:33', webhookName: 'SIEM Integration', event: 'login.failed', error: 'HTTP 429 - Rate limit exceeded', retryCount: 1 }
])

// Event types
const eventTypes = ref([
  { name: 'Alarm Events', icon: 'Warning', description: 'Triggered when alarms are raised or acknowledged', color: '#ef4444', subscriptions: 12 },
  { name: 'Device Events', icon: 'Monitor', description: 'Device status changes, online/offline events', color: '#3b82f6', subscriptions: 18 },
  { name: 'Work Order Events', icon: 'Document', description: 'Work order creation, updates, completion', color: '#10b981', subscriptions: 8 },
  { name: 'Security Events', icon: 'Lock', description: 'Access control, login attempts, intrusion', color: '#8b5cf6', subscriptions: 6 },
  { name: 'Energy Events', icon: 'DataLine', description: 'Energy consumption thresholds and updates', color: '#f59e0b', subscriptions: 4 },
  { name: 'System Events', icon: 'Setting', description: 'System startup, shutdown, configuration changes', color: '#ec489a', subscriptions: 3 }
])

// Security settings
const hmacEnabled = ref(true)
const ipWhitelist = ref(['192.168.1.0/24', '10.0.0.0/8'])
const rateLimit = ref(100)
const sslVerification = ref(true)

// Event handlers
const createWebhook = () => {
  ElMessageBox.prompt('Enter webhook name', 'Create Webhook', {
    confirmButtonText: 'Create',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'e.g., Slack Notifications'
  }).then(({ value }) => {
    if (value) {
      ElMessage.success(`Webhook "${value}" created. Configure URL and events next.`)
    }
  }).catch(() => {})
}

const exportWebhooks = () => {
  ElMessage.info('Exporting webhook configuration...')
  setTimeout(() => {
    ElMessage.success('Configuration exported')
  }, 1000)
}

const viewDocumentation = () => {
  ElMessage.info('Opening webhook documentation')
}

const refreshWebhooks = () => {
  ElMessage.info('Refreshing webhook list...')
  setTimeout(() => {
    ElMessage.success('Webhooks refreshed')
  }, 800)
}

const testWebhook = (webhook: any) => {
  ElMessage.info(`Testing webhook: ${webhook.name}`)
  setTimeout(() => {
    ElMessage.success(`Test payload sent to ${webhook.name} - Response received`)
  }, 1500)
}

const editWebhook = (webhook: any) => {
  ElMessage.info(`Editing webhook: ${webhook.name}`)
}

const deleteWebhook = (webhook: any) => {
  ElMessageBox.confirm(`Delete webhook "${webhook.name}"? This action cannot be undone.`, 'Confirm Delete', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'danger'
  }).then(() => {
    webhooks.value = webhooks.value.filter(w => w.id !== webhook.id)
    ElMessage.success(`Webhook "${webhook.name}" deleted`)
  }).catch(() => {})
}

const toggleWebhook = (webhook: any) => {
  ElMessage.success(`Webhook "${webhook.name}" ${webhook.status === 'active' ? 'activated' : 'deactivated'}`)
}

const viewAllDeliveries = () => {
  ElMessage.info('Viewing all deliveries')
}

const viewDeliveryDetails = (delivery: any) => {
  ElMessageBox.alert(
      `Delivery ID: ${delivery.id}\nWebhook: ${delivery.webhookName}\nEvent: ${delivery.event}\nStatus: ${delivery.status}\nDuration: ${delivery.duration}\nResponse: ${delivery.response}\nTimestamp: ${delivery.timestamp}`,
      'Delivery Details',
      { confirmButtonText: 'OK', type: 'info' }
  )
}

const redeliverDelivery = (delivery: any) => {
  ElMessageBox.confirm(`Redeliver event "${delivery.event}" to ${delivery.webhookName}?`, 'Confirm Redelivery', {
    confirmButtonText: 'Redeliver',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    ElMessage.success(`Redelivery initiated for ${delivery.webhookName}`)
  }).catch(() => {})
}

const retryDelivery = (failed: any) => {
  ElMessageBox.confirm(`Retry delivery for "${failed.event}" to ${failed.webhookName}?`, 'Confirm Retry', {
    confirmButtonText: 'Retry',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    failedDeliveries.value = failedDeliveries.value.filter(f => f.id !== failed.id)
    ElMessage.success(`Retry queued for ${failed.webhookName}`)
  }).catch(() => {})
}

const retryAllFailed = () => {
  ElMessageBox.confirm('Retry all failed deliveries?', 'Confirm Retry All', {
    confirmButtonText: 'Retry All',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    failedDeliveries.value = []
    ElMessage.success('All failed deliveries queued for retry')
  }).catch(() => {})
}

const viewErrorDetails = (failed: any) => {
  ElMessageBox.alert(
      `Webhook: ${failed.webhookName}\nEvent: ${failed.event}\nTime: ${failed.timestamp}\nError: ${failed.error}\nRetry Count: ${failed.retryCount}\n\nRecommendation: Check endpoint availability and authentication.`,
      'Error Details',
      { confirmButtonText: 'OK', type: 'error' }
  )
}

const subscribeToEvents = () => {
  ElMessage.info('Subscribe to events dialog opened')
}

const configureSecurity = () => {
  ElMessage.info('Security configuration dialog opened')
}

const editIpWhitelist = () => {
  ElMessage.info('Edit IP whitelist dialog opened')
}

const testEndpoint = () => {
  ElMessageBox.prompt('Enter endpoint URL to test', 'Test Webhook Endpoint', {
    confirmButtonText: 'Test',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'https://your-endpoint.com/webhook'
  }).then(({ value }) => {
    if (value) {
      ElMessage.info(`Testing endpoint: ${value}`)
      setTimeout(() => {
        ElMessage.success('Endpoint responded successfully')
      }, 2000)
    }
  }).catch(() => {})
}

const generateWebhookSecret = () => {
  const secret = 'whsec_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 8)
  ElMessageBox.alert(
      `Your webhook secret: ${secret}\n\nKeep this secret secure. Use it to verify webhook signatures.`,
      'Webhook Secret',
      { confirmButtonText: 'Copy', type: 'success' }
  ).then(() => {
    navigator.clipboard.writeText(secret)
    ElMessage.success('Secret copied to clipboard')
  }).catch(() => {})
}

const viewLogs = () => {
  ElMessage.info('Viewing webhook logs')
}

const viewMetrics = () => {
  ElMessage.info('Viewing webhook metrics')
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
    }, 400)
  }, 2500)
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
.webhook-management-container {
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

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  background: white;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  background: #f8fafc;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

/* Webhooks Section */
.webhooks-section {
  margin-bottom: 24px;
}

.webhooks-card {
  border-radius: 12px;
  background: white;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.webhook-filters {
  display: flex;
  gap: 12px;
}

.webhooks-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.webhook-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.webhook-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.webhook-name {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.webhook-name .name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.webhook-url {
  font-family: monospace;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  word-break: break-all;
}

.webhook-meta {
  display: flex;
  gap: 20px;
  font-size: 12px;
  color: #94a3b8;
}

.webhook-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.webhook-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.webhook-stats {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.stat-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  min-width: 180px;
}

.stat-progress {
  flex: 1;
}

/* Deliveries Section */
.deliveries-section,
.failed-section,
.events-section,
.security-section {
  margin-bottom: 24px;
}

.deliveries-card,
.failed-card,
.events-card,
.security-card {
  border-radius: 12px;
  background: white;
}

/* Events Grid */
.events-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.event-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.event-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.event-info {
  flex: 1;
}

.event-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 2px;
}

.event-description {
  font-size: 11px;
  color: #64748b;
}

.event-count {
  font-size: 12px;
  color: #3b82f6;
  font-weight: 500;
}

/* Security Grid */
.security-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.security-item {
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
  text-align: center;
}

.security-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 6px;
}

.security-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
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
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }

  .events-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .security-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: 1fr;
  }

  .events-grid {
    grid-template-columns: 1fr;
  }

  .security-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .webhook-header {
    flex-direction: column;
    gap: 12px;
  }

  .webhook-actions {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .webhook-filters {
    flex-wrap: wrap;
  }
}
</style>