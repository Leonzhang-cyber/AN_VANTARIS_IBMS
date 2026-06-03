<template>
  <!-- Loading Screen -->
  <div v-if="!isLoaded" class="loading-container">
    <div class="loading-overlay">
      <div class="loading-content">
        <div class="loading-spinner">
          <div class="spinner-ring"></div>
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
        <div class="loading-tip">Notification Center</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="notification-center-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Bell /></el-icon>
          Notification Center
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Message /></el-icon>
            {{ totalNotifications }} Total
          </div>
          <div class="stat-badge">
            <el-icon><Reading /></el-icon>
            {{ unreadCount }} Unread
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="markAllAsRead">
          <el-icon><CircleCheck /></el-icon>
          Mark All as Read
        </el-button>
        <el-button @click="refreshData" :loading="refreshing">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">📧</div>
        <div class="stat-info">
          <div class="stat-value">{{ emailCount }}</div>
          <div class="stat-label">Email</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c;">📱</div>
        <div class="stat-info">
          <div class="stat-value">{{ smsCount }}</div>
          <div class="stat-label">SMS</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #fbbf24;">💬</div>
        <div class="stat-info">
          <div class="stat-value">{{ slackCount }}</div>
          <div class="stat-label">Slack</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">🌐</div>
        <div class="stat-info">
          <div class="stat-value">{{ webhookCount }}</div>
          <div class="stat-label">Webhook</div>
        </div>
      </div>
    </div>

    <!-- Main Two-Column Layout -->
    <div class="dashboard-main">
      <!-- Left Column - Notification Channels -->
      <div class="main-left">
        <!-- Email Configuration -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Message /></el-icon>
              Email Configuration
            </div>
            <el-switch v-model="emailConfig.enabled" active-text="Enabled" inactive-text="Disabled" />
          </div>
          <div class="card-body">
            <el-form :model="emailConfig" label-width="100px" size="small">
              <el-form-item label="SMTP Server">
                <el-input v-model="emailConfig.smtpServer" placeholder="smtp.example.com" />
              </el-form-item>
              <el-form-item label="Port">
                <el-input-number v-model="emailConfig.port" :min="1" :max="65535" />
              </el-form-item>
              <el-form-item label="Username">
                <el-input v-model="emailConfig.username" placeholder="user@example.com" />
              </el-form-item>
              <el-form-item label="From Email">
                <el-input v-model="emailConfig.fromEmail" placeholder="noreply@example.com" />
              </el-form-item>
              <el-form-item label="Recipients">
                <el-select v-model="emailConfig.recipients" multiple filterable allow-create default-first-option placeholder="Add email addresses" style="width: 100%">
                  <el-option v-for="email in emailRecipientOptions" :key="email" :label="email" :value="email" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="testEmail">Send Test Email</el-button>
            <el-button size="small" @click="saveConfig('email')">Save Changes</el-button>
          </div>
        </div>

        <!-- SMS Configuration -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Phone /></el-icon>
              SMS Configuration
            </div>
            <el-switch v-model="smsConfig.enabled" active-text="Enabled" inactive-text="Disabled" />
          </div>
          <div class="card-body">
            <el-form :model="smsConfig" label-width="100px" size="small">
              <el-form-item label="Provider">
                <el-select v-model="smsConfig.provider" placeholder="Select provider">
                  <el-option label="Twilio" value="twilio" />
                  <el-option label="AWS SNS" value="aws" />
                  <el-option label="Vonage" value="vonage" />
                </el-select>
              </el-form-item>
              <el-form-item label="Account SID">
                <el-input v-model="smsConfig.accountSid" placeholder="Account SID" />
              </el-form-item>
              <el-form-item label="Auth Token">
                <el-input v-model="smsConfig.authToken" type="password" placeholder="Auth Token" show-password />
              </el-form-item>
              <el-form-item label="From Number">
                <el-input v-model="smsConfig.fromNumber" placeholder="+1234567890" />
              </el-form-item>
              <el-form-item label="Recipients">
                <el-select v-model="smsConfig.recipients" multiple filterable allow-create default-first-option placeholder="Add phone numbers" style="width: 100%">
                  <el-option v-for="phone in smsRecipientOptions" :key="phone" :label="phone" :value="phone" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="testSMS">Send Test SMS</el-button>
            <el-button size="small" @click="saveConfig('sms')">Save Changes</el-button>
          </div>
        </div>

        <!-- Slack Configuration -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><ChatDotSquare /></el-icon>
              Slack Configuration
            </div>
            <el-switch v-model="slackConfig.enabled" active-text="Enabled" inactive-text="Disabled" />
          </div>
          <div class="card-body">
            <el-form :model="slackConfig" label-width="100px" size="small">
              <el-form-item label="Webhook URL">
                <el-input v-model="slackConfig.webhookUrl" placeholder="https://hooks.slack.com/services/..." />
              </el-form-item>
              <el-form-item label="Channel">
                <el-input v-model="slackConfig.channel" placeholder="#alerts" />
              </el-form-item>
              <el-form-item label="Username">
                <el-input v-model="slackConfig.username" placeholder="Alert Bot" />
              </el-form-item>
              <el-form-item label="Icon Emoji">
                <el-input v-model="slackConfig.iconEmoji" placeholder=":warning:" />
              </el-form-item>
            </el-form>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="testSlack">Send Test Message</el-button>
            <el-button size="small" @click="saveConfig('slack')">Save Changes</el-button>
          </div>
        </div>

        <!-- Webhook Configuration -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Connection /></el-icon>
              Webhook Configuration
            </div>
            <el-switch v-model="webhookConfig.enabled" active-text="Enabled" inactive-text="Disabled" />
          </div>
          <div class="card-body">
            <el-form :model="webhookConfig" label-width="100px" size="small">
              <el-form-item label="Endpoint URL">
                <el-input v-model="webhookConfig.endpointUrl" placeholder="https://api.example.com/webhook" />
              </el-form-item>
              <el-form-item label="Method">
                <el-select v-model="webhookConfig.method" style="width: 100%">
                  <el-option label="POST" value="POST" />
                  <el-option label="PUT" value="PUT" />
                </el-select>
              </el-form-item>
              <el-form-item label="Headers">
                <div v-for="(header, idx) in webhookConfig.headers" :key="idx" class="header-row">
                  <el-input v-model="header.key" placeholder="Header Name" style="width: 40%" size="small" />
                  <el-input v-model="header.value" placeholder="Header Value" style="width: 55%" size="small" />
                  <el-button type="danger" link @click="removeHeader(idx)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <el-button type="primary" link size="small" @click="addHeader">
                  <el-icon><Plus /></el-icon>
                  Add Header
                </el-button>
              </el-form-item>
            </el-form>
          </div>
          <div class="card-footer">
            <el-button type="primary" size="small" @click="testWebhook">Send Test Webhook</el-button>
            <el-button size="small" @click="saveConfig('webhook')">Save Changes</el-button>
          </div>
        </div>
      </div>

      <!-- Right Column - Notification History & Templates -->
      <div class="main-right">
        <!-- Notification Templates -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Document /></el-icon>
              Notification Templates
            </div>
            <el-button type="primary" link @click="handleCreateTemplate">
              <el-icon><Plus /></el-icon>
              New Template
            </el-button>
          </div>
          <div class="templates-list">
            <div v-for="template in notificationTemplates" :key="template.id" class="template-item">
              <div class="template-header">
                <span class="template-name">{{ template.name }}</span>
                <div class="template-actions">
                  <el-button type="primary" link size="small" @click="editTemplate(template)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="danger" link size="small" @click="deleteTemplate(template)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
              <div class="template-preview">{{ template.preview }}</div>
              <div class="template-meta">
                <el-tag :type="getTemplateTypeTag(template.type)" size="small">{{ template.type }}</el-tag>
                <span>Used: {{ template.usageCount }} times</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Notifications -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><List /></el-icon>
              Recent Notifications
            </div>
            <el-select v-model="notificationFilter" size="small" style="width: 120px" clearable>
              <el-option label="All" value="all" />
              <el-option label="Email" value="email" />
              <el-option label="SMS" value="sms" />
              <el-option label="Slack" value="slack" />
              <el-option label="Webhook" value="webhook" />
            </el-select>
          </div>
          <div class="notifications-list">
            <div v-for="notif in filteredNotifications" :key="notif.id" class="notification-item" :class="{ unread: !notif.read }">
              <div class="notification-icon" :class="notif.type">
                <el-icon v-if="notif.type === 'email'"><Message /></el-icon>
                <el-icon v-else-if="notif.type === 'sms'"><Phone /></el-icon>
                <el-icon v-else-if="notif.type === 'slack'"><ChatDotSquare /></el-icon>
                <el-icon v-else><Connection /></el-icon>
              </div>
              <div class="notification-content">
                <div class="notification-title">{{ notif.title }}</div>
                <div class="notification-message">{{ notif.message }}</div>
                <div class="notification-time">{{ notif.time }}</div>
              </div>
              <div class="notification-status">
                <el-tag :type="notif.status === 'sent' ? 'success' : (notif.status === 'failed' ? 'danger' : 'warning')" size="small">
                  {{ notif.status }}
                </el-tag>
                <el-button v-if="!notif.read" type="primary" link size="small" @click="markAsRead(notif)">
                  Mark Read
                </el-button>
              </div>
            </div>
            <div v-if="filteredNotifications.length === 0" class="empty-state">
              <el-empty description="No notifications" :image-size="60" />
            </div>
          </div>
        </div>

        <!-- Notification Rules -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              Notification Rules
            </div>
            <el-button type="primary" link @click="handleCreateRule">
              <el-icon><Plus /></el-icon>
              New Rule
            </el-button>
          </div>
          <div class="rules-list">
            <div v-for="rule in notificationRules" :key="rule.id" class="rule-item">
              <div class="rule-header">
                <span class="rule-name">{{ rule.name }}</span>
                <el-switch v-model="rule.enabled" size="small" @change="toggleRule(rule)" />
              </div>
              <div class="rule-condition">{{ rule.condition }}</div>
              <div class="rule-channels">
                <el-tag v-for="channel in rule.channels" :key="channel" size="small" class="channel-tag">
                  {{ channel }}
                </el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Template Dialog -->
    <el-dialog v-model="templateDialogVisible" :title="templateDialogTitle" width="550px">
      <el-form :model="templateForm" :rules="templateRules" ref="templateFormRef" label-width="100px">
        <el-form-item label="Template Name" prop="name">
          <el-input v-model="templateForm.name" placeholder="Enter template name" />
        </el-form-item>
        <el-form-item label="Type" prop="type">
          <el-select v-model="templateForm.type" style="width: 100%">
            <el-option label="Email" value="email" />
            <el-option label="SMS" value="sms" />
            <el-option label="Slack" value="slack" />
            <el-option label="Webhook" value="webhook" />
          </el-select>
        </el-form-item>
        <el-form-item label="Subject" prop="subject" v-if="templateForm.type === 'email'">
          <el-input v-model="templateForm.subject" placeholder="Email subject" />
        </el-form-item>
        <el-form-item label="Content" prop="content">
          <el-input v-model="templateForm.content" type="textarea" :rows="4" placeholder="Template content" />
        </el-form-item>
        <el-form-item label="Variables">
          <div class="variables-hint">
            Available variables: <code>{{ '{alarm_title}' }}</code>, <code>{{ '{severity}' }}</code>, <code>{{ '{location}' }}</code>, <code>{{ '{time}' }}</code>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="templateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveTemplate">Save Template</el-button>
      </template>
    </el-dialog>

    <!-- Rule Dialog -->
    <el-dialog v-model="ruleDialogVisible" title="Create Notification Rule" width="500px">
      <el-form :model="ruleForm" :rules="ruleFormRules" ref="ruleFormRef" label-width="100px">
        <el-form-item label="Rule Name" prop="name">
          <el-input v-model="ruleForm.name" placeholder="Enter rule name" />
        </el-form-item>
        <el-form-item label="Condition" prop="condition">
          <el-select v-model="ruleForm.condition" style="width: 100%">
            <el-option label="Critical Severity" value="severity = critical" />
            <el-option label="Major Severity" value="severity = major" />
            <el-option label="Warning Severity" value="severity = warning" />
            <el-option label="All Alarms" value="severity in (critical, major, warning)" />
            <el-option label="Custom" value="custom" />
          </el-select>
        </el-form-item>
        <el-form-item label="Channels" prop="channels">
          <el-checkbox-group v-model="ruleForm.channels">
            <el-checkbox value="email">Email</el-checkbox>
            <el-checkbox value="sms">SMS</el-checkbox>
            <el-checkbox value="slack">Slack</el-checkbox>
            <el-checkbox value="webhook">Webhook</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRule">Save Rule</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell, Message, Reading, CircleCheck, Refresh, Phone, ChatDotSquare, Connection, Document, Plus, Edit, Delete, List, Setting } from '@element-plus/icons-vue'
import { useCounterStore } from '@/stores/counter.js'
import { getCurrentInstance } from 'vue'

const getStore = () => {
  const instance = getCurrentInstance()
  if (!instance) throw new Error('useStore() must be called within a setup function')
  const pinia = instance.appContext.config.globalProperties.$pinia
  if (!pinia) throw new Error('Pinia instance not found')
  return useCounterStore(pinia)
}
const counterStore = getStore()
const isFullscreen = computed(() => counterStore.isFullscreen)
const route = useRoute()

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const refreshing = ref(false)

const loadingMessages = [
  'Preparing...',
  'Loading notification channels...',
  'Initializing templates...',
  'Starting dashboard...',
  'Almost ready...'
]

// ==================== Data State ====================
const notificationFilter = ref('all')
const templateDialogVisible = ref(false)
const ruleDialogVisible = ref(false)
const templateDialogTitle = ref('Create Template')
const templateFormRef = ref()
const ruleFormRef = ref()

// Email Config
const emailConfig = ref({
  enabled: true,
  smtpServer: 'smtp.gmail.com',
  port: 587,
  username: 'alerts@company.com',
  fromEmail: 'noreply@company.com',
  recipients: ['admin@company.com', 'ops@company.com']
})

// SMS Config
const smsConfig = ref({
  enabled: true,
  provider: 'twilio',
  accountSid: 'ACxxxxxxxxxxxxxx',
  authToken: 'xxxxxxxxxxxxxx',
  fromNumber: '+1234567890',
  recipients: ['+1234567890', '+1987654321']
})

// Slack Config
const slackConfig = ref({
  enabled: true,
  webhookUrl: 'https://hooks.slack.com/services/xxx/yyy/zzz',
  channel: '#alerts',
  username: 'Alert Bot',
  iconEmoji: ':warning:'
})

// Webhook Config
const webhookConfig = ref({
  enabled: true,
  endpointUrl: 'https://api.example.com/webhook',
  method: 'POST',
  headers: [
    { key: 'Content-Type', value: 'application/json' },
    { key: 'Authorization', value: 'Bearer token' }
  ]
})

// Statistics
const totalNotifications = ref(156)
const unreadCount = ref(23)
const emailCount = ref(89)
const smsCount = ref(34)
const slackCount = ref(28)
const webhookCount = ref(5)

// Recipient options
const emailRecipientOptions = ref(['admin@company.com', 'ops@company.com', 'security@company.com', 'it@company.com'])
const smsRecipientOptions = ref(['+1234567890', '+1987654321', '+1122334455'])

// Notification Templates
interface NotificationTemplate {
  id: number
  name: string
  type: string
  subject: string
  content: string
  usageCount: number
  preview: string
}

const notificationTemplates = ref<NotificationTemplate[]>([
  { id: 1, name: 'Critical Alert Email', type: 'email', subject: '[CRITICAL] {{alarm_title}}', content: 'Dear team,\n\nA critical alarm has been triggered.\n\nAlarm: {{alarm_title}}\nSeverity: {{severity}}\nLocation: {{location}}\nTime: {{time}}\n\nPlease take immediate action.\n\nBest regards,\nMonitoring System', usageCount: 45, preview: '[CRITICAL] UPS Overload - Please take immediate action' },
  { id: 2, name: 'Major Alert SMS', type: 'sms', subject: '', content: 'ALERT: {{severity}} - {{alarm_title}} at {{location}}', usageCount: 28, preview: 'ALERT: Major - High CPU Usage at Server Room' },
  { id: 3, name: 'Slack Notification', type: 'slack', subject: '', content: '🚨 *{{severity|upper}} Alert*\n> *{{alarm_title}}*\n> Location: {{location}}\n> Time: {{time}}', usageCount: 52, preview: '🚨 *CRITICAL Alert* - UPS Overload at Data Center' }
])

// Notification Rules
interface NotificationRule {
  id: number
  name: string
  condition: string
  channels: string[]
  enabled: boolean
}

const notificationRules = ref<NotificationRule[]>([
  { id: 1, name: 'Critical Alerts', condition: 'severity = critical', channels: ['email', 'sms', 'slack'], enabled: true },
  { id: 2, name: 'Major Alerts', condition: 'severity = major', channels: ['email', 'slack'], enabled: true },
  { id: 3, name: 'Warning Alerts', condition: 'severity = warning', channels: ['email'], enabled: true },
  { id: 4, name: 'After Hours', condition: 'time between 18:00-08:00', channels: ['sms'], enabled: false }
])

// Recent Notifications
interface Notification {
  id: number
  type: string
  title: string
  message: string
  time: string
  status: string
  read: boolean
}

const notifications = ref<Notification[]>([
  { id: 1, type: 'email', title: 'Critical Alert: UPS Overload', message: 'UPS load exceeded 90% capacity. Action required.', time: '2 min ago', status: 'sent', read: false },
  { id: 2, type: 'slack', title: 'Major Alert: High CPU Usage', message: 'CPU usage at 85% on db-server-01', time: '5 min ago', status: 'sent', read: false },
  { id: 3, type: 'sms', title: 'Warning: Temperature High', message: 'Server room temperature at 28°C', time: '12 min ago', status: 'sent', read: false },
  { id: 4, type: 'email', title: 'Info: Backup Completed', message: 'Daily backup completed successfully', time: '25 min ago', status: 'sent', read: true },
  { id: 5, type: 'webhook', title: 'Webhook: System Event', message: 'Configuration change detected', time: '1 hour ago', status: 'failed', read: true },
  { id: 6, type: 'slack', title: 'Info: Maintenance Started', message: 'Weekly maintenance window started', time: '2 hours ago', status: 'sent', read: true }
])

const filteredNotifications = computed(() => {
  if (notificationFilter.value === 'all') return notifications.value
  return notifications.value.filter(n => n.type === notificationFilter.value)
})

// Template form
const templateForm = ref({
  id: null,
  name: '',
  type: 'email',
  subject: '',
  content: '',
  preview: ''
})

const templateRules = {
  name: [{ required: true, message: 'Please enter template name', trigger: 'blur' }],
  content: [{ required: true, message: 'Please enter content', trigger: 'blur' }]
}

// Rule form
const ruleForm = ref({
  name: '',
  condition: '',
  channels: []
})

const ruleFormRules = {
  name: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
  condition: [{ required: true, message: 'Please select condition', trigger: 'change' }],
  channels: [{ required: true, message: 'Please select at least one channel', trigger: 'change' }]
}

// ==================== Helper Functions ====================
const getTemplateTypeTag = (type: string) => {
  const map: Record<string, string> = {
    email: 'primary',
    sms: 'success',
    slack: 'warning',
    webhook: 'info'
  }
  return map[type] || 'info'
}

// ==================== Actions ====================
const addHeader = () => {
  webhookConfig.value.headers.push({ key: '', value: '' })
}

const removeHeader = (index: number) => {
  webhookConfig.value.headers.splice(index, 1)
}

const testEmail = () => {
  ElMessage.success('Test email sent successfully')
}

const testSMS = () => {
  ElMessage.success('Test SMS sent successfully')
}

const testSlack = () => {
  ElMessage.success('Test Slack message sent successfully')
}

const testWebhook = () => {
  ElMessage.success('Test webhook sent successfully')
}

const saveConfig = (type: string) => {
  ElMessage.success(`${type} configuration saved successfully`)
}

const markAsRead = (notif: Notification) => {
  notif.read = true
  unreadCount.value--
  ElMessage.success('Marked as read')
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
  unreadCount.value = 0
  ElMessage.success('All notifications marked as read')
}

const handleCreateTemplate = () => {
  templateDialogTitle.value = 'Create Template'
  templateForm.value = { id: null, name: '', type: 'email', subject: '', content: '', preview: '' }
  templateDialogVisible.value = true
}

const editTemplate = (template: NotificationTemplate) => {
  templateDialogTitle.value = 'Edit Template'
  templateForm.value = { ...template }
  templateDialogVisible.value = true
}

const deleteTemplate = (template: NotificationTemplate) => {
  ElMessageBox.confirm(`Delete template "${template.name}"?`, 'Confirm', {
    confirmButtonText: 'Delete',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    const index = notificationTemplates.value.findIndex(t => t.id === template.id)
    if (index > -1) {
      notificationTemplates.value.splice(index, 1)
      ElMessage.success('Template deleted')
    }
  }).catch(() => {})
}

const saveTemplate = async () => {
  try {
    await templateFormRef.value?.validate()
    ElMessage.success('Template saved successfully')
    templateDialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const handleCreateRule = () => {
  ruleForm.value = { name: '', condition: '', channels: [] }
  ruleDialogVisible.value = true
}

const toggleRule = (rule: NotificationRule) => {
  ElMessage.success(`Rule "${rule.name}" ${rule.enabled ? 'enabled' : 'disabled'}`)
}

const saveRule = async () => {
  try {
    await ruleFormRef.value?.validate()
    ElMessage.success('Notification rule created successfully')
    ruleDialogVisible.value = false
  } catch (error) {
    ElMessage.error('Please fill all required fields')
  }
}

const refreshData = async () => {
  refreshing.value = true
  await new Promise(resolve => setTimeout(resolve, 1000))
  refreshing.value = false
  ElMessage.success('Data refreshed')
}

// ==================== Loading Animation ====================
const startLoading = () => {
  let progress = 0
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (progress < 90) {
      progress += Math.random() * 12
      loadingProgress.value = Math.min(progress, 90)
    }
  }, 100)

  setTimeout(() => {
    clearInterval(messageInterval)
    clearInterval(progressInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'

    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        setTimeout(() => {}, 100)
      })
    }, 500)
  }, 2500)
}

// ==================== Lifecycle ====================
onMounted(() => {
  startLoading()
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; animation-delay: 0s; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }
.spinner-ring:nth-child(4) { border-left-color: #ec489a; animation-delay: 0.6s; width: 20%; height: 20%; top: 40%; left: 40%; }

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

/* ==================== Main Dashboard Styles ==================== */
.notification-center-dashboard {
  min-height: 100vh;
  background: #ffffff;
  padding: 24px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.dashboard-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: #1f2f3d;
  margin: 0;
}

.dashboard-title .el-icon {
  color: #409eff;
}

.header-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.stat-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 12px;
  background: #f5f7fa;
  border-radius: 20px;
  font-size: 13px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #1f2f3d;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Dashboard Main */
.dashboard-main {
  display: flex;
  gap: 20px;
}

.main-left {
  flex: 1.2;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-right {
  flex: 0.8;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-wrap: wrap;
  gap: 12px;
  background: #fafafa;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #1f2f3d;
}

.card-title .el-icon {
  color: #409eff;
}

.card-body {
  padding: 20px;
}

.card-footer {
  padding: 12px 20px;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: #fafafa;
}

/* Header Row */
.header-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}

/* Templates List */
.templates-list {
  padding: 8px;
  max-height: 350px;
  overflow-y: auto;
}

.template-item {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  transition: background 0.2s;
}

.template-item:hover {
  background: #f5f7fa;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.template-name {
  font-weight: 600;
  color: #1f2f3d;
}

.template-preview {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
  font-family: monospace;
}

.template-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #909399;
  align-items: center;
}

/* Notifications List */
.notifications-list {
  padding: 8px;
  max-height: 350px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  transition: background 0.2s;
}

.notification-item.unread {
  background: #ecf5ff;
}

.notification-item:hover {
  background: #f5f7fa;
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-icon.email { background: #ecf5ff; color: #409eff; }
.notification-icon.sms { background: #f0f9eb; color: #67c23a; }
.notification-icon.slack { background: #fdf6ec; color: #e6a23c; }
.notification-icon.webhook { background: #f4f4f5; color: #909399; }

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 500;
  color: #1f2f3d;
  margin-bottom: 4px;
}

.notification-message {
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}

.notification-time {
  font-size: 11px;
  color: #909399;
}

.notification-status {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

/* Rules List */
.rules-list {
  padding: 8px;
}

.rule-item {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.rule-name {
  font-weight: 600;
  color: #1f2f3d;
}

.rule-condition {
  font-size: 11px;
  color: #909399;
  margin-bottom: 8px;
  font-family: monospace;
}

.rule-channels {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.channel-tag {
  font-size: 11px;
}

.empty-state {
  padding: 20px;
  text-align: center;
}

.variables-hint {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 8px;
  border-radius: 6px;
}

.variables-hint code {
  background: #e4e7ed;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}

/* Responsive */
@media (max-width: 1000px) {
  .dashboard-main {
    flex-direction: column;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .notification-center-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .header-row {
    flex-wrap: wrap;
  }
  .notification-item {
    flex-direction: column;
  }
  .notification-status {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

/* Element Plus 样式覆盖 */
:deep(.el-form-item) {
  margin-bottom: 18px;
}
</style>