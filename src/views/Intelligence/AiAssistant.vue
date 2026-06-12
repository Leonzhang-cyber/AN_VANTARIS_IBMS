<script setup lang="ts">
import { ref, onMounted, computed, reactive, nextTick } from 'vue'
import * as echarts from 'echarts'
import {
  Refresh, Setting, User, Clock,
  Warning, CircleCheck, TrendCharts, DataLine,
  Star, Share, CopyDocument, Delete, Mic,
  Picture, Document, Upload, Download,
  MagicStick, ChatDotRound, Message, Service
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')

const loadingMessages = [
  'Preparing...',
  'Loading modules...',
  'Initializing AI model...',
  'Loading knowledge base...',
  'Preparing response system...',
  'Almost ready...'
]

// ==================== Component State ====================
const loading = ref(false)
const inputMessage = ref('')
const chatContainer = ref<HTMLElement | null>(null)
const chartRef = ref<HTMLElement | null>(null)

let usageChart: echarts.ECharts | null = null

// Message interface
interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  suggestions?: string[]
  metrics?: any
  thinking?: boolean
}

// Chat history
const messages = ref<Message[]>([
  {
    id: '1',
    role: 'assistant',
    content: 'Hello! I\'m your AI Assistant for the IBMS system. I can help you with:\n\n• System health monitoring and alerts\n• Energy consumption analysis\n• Maintenance scheduling and tracking\n• Report generation and customization\n• Anomaly detection and predictions\n\nHow can I assist you today?',
    timestamp: new Date().toLocaleString(),
    suggestions: [
      'Show system health status',
      'Analyze energy consumption',
      'List active alarms',
      'Generate weekly report'
    ]
  }
])

// Suggestions
const quickSuggestions = ref([
  { icon: '📊', text: 'Show system health status', category: 'monitoring' },
  { icon: '⚡', text: 'Analyze energy consumption', category: 'energy' },
  { icon: '🔔', text: 'List active alarms', category: 'alerts' },
  { icon: '📄', text: 'Generate weekly report', category: 'reports' },
  { icon: '🔧', text: 'Schedule maintenance', category: 'maintenance' },
  { icon: '📈', text: 'Predictive analytics', category: 'analytics' }
])

// AI Statistics
const aiStats = reactive({
  totalQueries: 1245,
  avgResponseTime: 1.8,
  satisfactionRate: 94.5,
  activeTopics: 8
})

// ==================== Loading Simulation ====================
onMounted(() => {
  let messageIndex = 0

  const messageInterval = setInterval(() => {
    if (messageIndex < loadingMessages.length - 1) {
      messageIndex++
      loadingMessage.value = loadingMessages[messageIndex]
    }
  }, 600)

  const progressInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 12 + 4
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
      setTimeout(() => {
        initChart()
        window.addEventListener('resize', handleResize)
      }, 100)
    }, 400)
  }, 2500)
})

// ==================== Chart Functions ====================
const initChart = () => {
  if (!chartRef.value) return

  usageChart = echarts.init(chartRef.value)
  usageChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['Queries', 'Avg Response (s)'], bottom: 0 },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: [
      { type: 'value', name: 'Queries' },
      { type: 'value', name: 'Response Time (s)' }
    ],
    series: [
      { name: 'Queries', type: 'bar', data: [165, 189, 210, 198, 245, 132, 98], itemStyle: { color: '#409EFF', borderRadius: [4, 4, 0, 0] } },
      { name: 'Avg Response (s)', type: 'line', data: [1.8, 1.7, 1.6, 1.5, 1.4, 1.6, 1.9], smooth: true, lineStyle: { color: '#67C23A', width: 2 }, symbol: 'circle', symbolSize: 8, yAxisIndex: 1 }
    ]
  })
}

const handleResize = () => {
  usageChart?.resize()
}

// ==================== AI Response Functions ====================
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const simulateTyping = async (content: string, messageId: string) => {
  const words = content.split('')
  let currentText = ''

  for (let i = 0; i < words.length; i++) {
    currentText += words[i]
    const index = messages.value.findIndex(m => m.id === messageId)
    if (index !== -1) {
      messages.value[index].content = currentText
    }
    await new Promise(resolve => setTimeout(resolve, 15))
    await scrollToBottom()
  }

  const index = messages.value.findIndex(m => m.id === messageId)
  if (index !== -1) {
    messages.value[index].thinking = false
  }
}

const generateAIResponse = async (userMessage: string): Promise<{ content: string, suggestions: string[] }> => {
  await new Promise(resolve => setTimeout(resolve, 1500))

  const lowerMessage = userMessage.toLowerCase()

  if (lowerMessage.includes('health') || lowerMessage.includes('status') || lowerMessage.includes('system')) {
    return {
      content: `📊 **System Health Report**

**Overall Health Score:** 98.5% ✅

**Key Metrics:**
• CPU Usage: 42%
• Memory Usage: 56%
• Network Latency: 24ms
• Active Alarms: 8
• System Uptime: 99.98%

**Status by Component:**
✅ HVAC Systems: Operational
✅ Lighting Control: Operational
⚠️ Security Cameras: 2 offline
✅ Access Control: Operational
✅ Energy Meters: All online

**Recommendations:**
1. Check offline cameras at North Gate
2. Schedule preventive maintenance for HVAC next week
3. Review alarm history for recurring issues

Would you like more details on any specific component?`,
      suggestions: ['Show alarm details', 'View camera status', 'Schedule maintenance', 'Export health report']
    }
  }

  if (lowerMessage.includes('energy') || lowerMessage.includes('consumption')) {
    return {
      content: `⚡ **Energy Consumption Analysis**

**Today's Usage:** 12,450 kWh
**Weekly Trend:** ↓ 3.2% from last week
**Monthly Projection:** 385,000 kWh

**Breakdown by Category:**
• HVAC: 45% (5,602 kWh)
• Lighting: 28% (3,486 kWh)
• Equipment: 18% (2,241 kWh)
• Other: 9% (1,121 kWh)

**Peak Hours:** 2:00 PM - 4:00 PM
**Off-Peak Savings:** 12.5%

**Recommendations:**
1. Implement demand response during peak hours
2. Schedule HVAC optimization for after-hours
3. Consider LED lighting upgrades for Zone B

Would you like to see the detailed breakdown by zone?`,
      suggestions: ['Show zone breakdown', 'Compare with last month', 'Set energy alerts', 'Generate energy report']
    }
  }

  if (lowerMessage.includes('alarm') || lowerMessage.includes('alert')) {
    return {
      content: `🔔 **Active Alarms Summary**

**Total Active Alarms:** 8
**Critical:** 2 | **High:** 3 | **Medium:** 2 | **Low:** 1

**Critical Alarms:**
1. 🔴 Chiller-1 - High Temperature (10:23 AM)
2. 🔴 UPS Battery - Low Capacity (09:45 AM)

**High Priority Alarms:**
1. 🟠 Fire Alarm Panel - Communication Lost (08:30 AM)
2. 🟠 VFD Pump - Vibration High (07:15 AM)
3. 🟠 Access Door - Forced Entry Detected (06:50 AM)

**Resolved Today:** 12 alarms
**Avg Response Time:** 4.2 minutes

**Recommendations:**
1. Immediate attention required for Chiller-1
2. Schedule battery replacement for UPS
3. Investigate forced entry incident

Would you like me to create a ticket for any of these alarms?`,
      suggestions: ['Create ticket for Chiller-1', 'View alarm history', 'Acknowledge alarms', 'Generate alarm report']
    }
  }

  if (lowerMessage.includes('report') || lowerMessage.includes('generate')) {
    return {
      content: `📄 **Report Generation**

I can help you generate the following reports:

**Available Report Types:**
1. 📊 **System Health Report** - Overall system status and KPIs
2. ⚡ **Energy Report** - Consumption analysis and trends
3. 🔔 **Alarms Report** - Incident summary and resolution
4. 🔧 **Maintenance Report** - Work order status and compliance
5. 💰 **Financial Report** - Cost analysis and savings

**Customize Your Report:**
• Date Range: Last 7 days / Last 30 days / Custom
• Format: PDF / Excel / CSV
• Schedule: One-time / Daily / Weekly / Monthly
• Recipients: Add email addresses for automatic delivery

**Quick Actions:**
• Generate weekly health report
• Export energy data to Excel
• Schedule monthly alarms report

Which report would you like to generate?`,
      suggestions: ['Generate weekly health report', 'Export energy data', 'Schedule monthly report', 'Custom report builder']
    }
  }

  if (lowerMessage.includes('maintenance') || lowerMessage.includes('schedule')) {
    return {
      content: `🔧 **Maintenance Overview**

**Current Status:**
• Open Work Orders: 12
• Completed Today: 5
• Overdue: 2
• SLA Compliance: 96%

**Upcoming Scheduled Maintenance:**
1. 📅 HVAC Filter Replacement - Tomorrow 9:00 AM
2. 📅 UPS Battery Testing - Jan 20, 2:00 PM
3. 📅 Fire Alarm System Test - Jan 22, 10:00 AM

**Pending Approvals:**
• Chiller Preventive Maintenance (Requested by: John Smith)
• Lighting Control Upgrade (Requested by: Sarah Johnson)

**Recommendations:**
• Schedule belt replacement for AHU-3 (due in 5 days)
• Plan annual generator test for next month
• Review pending maintenance requests

Would you like to create a new work order or view details of existing ones?`,
      suggestions: ['Create work order', 'View pending approvals', 'Check SLA status', 'Schedule inspection']
    }
  }

  return {
    content: `I understand you're asking about "${userMessage}". Here's what I can help you with:

**Available Services:**
• 📊 **System Monitoring** - Check health status and performance metrics
• ⚡ **Energy Management** - Analyze consumption and optimize usage
• 🔔 **Alarm Management** - View and resolve system alerts
• 🔧 **Maintenance** - Schedule and track work orders
• 📄 **Reports** - Generate and export various reports
• 📈 **Analytics** - Predictive insights and trend analysis

**Quick Commands:**
• "Show system health"
• "Energy consumption today"
• "List active alarms"
• "Schedule maintenance"

How would you like to proceed?`,
    suggestions: ['Show system health', 'Energy analysis', 'List alarms', 'Schedule maintenance', 'Generate report']
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: inputMessage.value,
    timestamp: new Date().toLocaleString()
  }
  messages.value.push(userMessage)
  await scrollToBottom()

  const userInput = inputMessage.value
  inputMessage.value = ''

  const assistantMessage: Message = {
    id: (Date.now() + 1).toString(),
    role: 'assistant',
    content: '',
    timestamp: new Date().toLocaleString(),
    thinking: true
  }
  messages.value.push(assistantMessage)
  await scrollToBottom()

  const response = await generateAIResponse(userInput)

  const index = messages.value.findIndex(m => m.id === assistantMessage.id)
  if (index !== -1) {
    messages.value[index].thinking = false
    messages.value[index].suggestions = response.suggestions
    await simulateTyping(response.content, assistantMessage.id)
  }
}

const sendSuggestion = (suggestion: string) => {
  inputMessage.value = suggestion
  sendMessage()
}

const clearChat = async () => {
  await ElMessageBox.confirm(
      'Clear all chat history? This action cannot be undone.',
      'Confirm Clear',
      {
        confirmButtonText: 'Clear',
        cancelButtonText: 'Cancel',
        type: 'warning'
      }
  )

  messages.value = [messages.value[0]]
  ElMessage.success('Chat history cleared')
}

const copyMessage = (content: string) => {
  navigator.clipboard.writeText(content)
  ElMessage.success('Message copied to clipboard')
}

const formatTime = (timestamp: string) => {
  return timestamp
}
</script>

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
          <span class="loading-title">Loading AI Assistant</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Intelligence - AI Assistant</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-assistant-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">AI Assistant</h1>
        <p class="page-subtitle">Your intelligent virtual assistant for IBMS operations</p>
      </div>
      <div class="header-right">
        <el-button size="large" @click="clearChat">
          <el-icon><Delete /></el-icon>
          Clear Chat
        </el-button>
        <el-button size="large">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <!-- Stats Cards Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon queries-icon">
          <el-icon><ChatDotRound /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ aiStats.totalQueries.toLocaleString() }}</div>
          <div class="stat-label">Total Queries</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+12% this week</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon response-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ aiStats.avgResponseTime }}s</div>
          <div class="stat-label">Avg Response Time</div>
        </div>
        <div class="stat-trend">
          <span class="trend-down">-0.2s</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon satisfaction-icon">
          <el-icon><Star /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ aiStats.satisfactionRate }}%</div>
          <div class="stat-label">Satisfaction Rate</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+2.5%</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon topics-icon">
          <el-icon><DataLine /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ aiStats.activeTopics }}</div>
          <div class="stat-label">Active Topics</div>
        </div>
        <div class="stat-trend">
          <span class="trend-up">+3 new</span>
        </div>
      </div>
    </div>

    <!-- Chart Section -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Usage Analytics</h3>
        <el-button text type="primary" @click="initChart">Refresh</el-button>
      </div>
      <div ref="chartRef" class="usage-chart" style="height: 280px"></div>
    </div>

    <!-- Chat Interface -->
    <div class="chat-interface">
      <!-- Sidebar -->
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <h3>Quick Actions</h3>
        </div>
        <div class="suggestions-list">
          <button
              v-for="suggestion in quickSuggestions"
              :key="suggestion.text"
              class="suggestion-btn"
              @click="sendSuggestion(suggestion.text)"
          >
            <span class="suggestion-icon">{{ suggestion.icon }}</span>
            <span class="suggestion-text">{{ suggestion.text }}</span>
          </button>
        </div>

        <div class="sidebar-footer">
          <div class="status-indicator">
            <span class="status-dot online"></span>
            <span>AI Model Online</span>
          </div>
          <div class="version-info">
            Version 2.0.1
          </div>
        </div>
      </div>

      <!-- Chat Main -->
      <div class="chat-main">
        <div class="chat-header">
          <div class="chat-title">
            <el-icon><MagicStick /></el-icon>
            <span>AI Assistant Conversation</span>
          </div>
          <div class="chat-actions">
            <el-tooltip content="Clear chat" placement="top">
              <el-button circle size="small" @click="clearChat">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>

        <!-- Messages Container -->
        <div ref="chatContainer" class="messages-container">
          <div
              v-for="message in messages"
              :key="message.id"
              class="message-wrapper"
              :class="message.role"
          >
            <div class="message-avatar">
              <div v-if="message.role === 'assistant'" class="avatar assistant-avatar">
                <el-icon><MagicStick /></el-icon>
              </div>
              <div v-else class="avatar user-avatar">
                <el-icon><User /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-role">{{ message.role === 'assistant' ? 'AI Assistant' : 'You' }}</span>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-bubble">
                <div v-if="message.thinking" class="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
                <div v-else class="message-text" v-html="message.content.replace(/\n/g, '<br>')"></div>
              </div>

              <!-- Suggestions -->
              <div v-if="message.suggestions && message.suggestions.length" class="message-suggestions">
                <button
                    v-for="suggestion in message.suggestions"
                    :key="suggestion"
                    class="suggestion-chip"
                    @click="sendSuggestion(suggestion)"
                >
                  {{ suggestion }}
                </button>
              </div>

              <!-- Copy Button -->
              <div v-if="!message.thinking && message.content" class="message-actions">
                <el-button link size="small" @click="copyMessage(message.content)">
                  <el-icon><CopyDocument /></el-icon>
                  Copy
                </el-button>
              </div>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="chat-input-area">
          <div class="input-container">
            <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="2"
                placeholder="Ask me anything about your IBMS system..."
                @keydown.enter.prevent="sendMessage"
                resize="none"
            />
            <div class="input-actions">
              <div class="input-tools">
                <el-button circle size="small">
                  <el-icon><Picture /></el-icon>
                </el-button>
                <el-button circle size="small">
                  <el-icon><Document /></el-icon>
                </el-button>
                <el-button circle size="small">
                  <el-icon><Mic /></el-icon>
                </el-button>
              </div>
              <el-button type="primary" :loading="loading" @click="sendMessage">
                <el-icon><TrendCharts /></el-icon>
                Send
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

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

/* ==================== Main Content ==================== */
.ai-assistant-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #eef2f6 100%);
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
  flex-wrap: wrap;
  gap: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #1e293b 0%, #2d3a4e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.queries-icon {
  background: linear-gradient(135deg, #e6f7ff 0%, #bae7ff 100%);
  color: #409eff;
}

.response-icon {
  background: linear-gradient(135deg, #f0f9ff 0%, #d4f1f9 100%);
  color: #67c23a;
}

.satisfaction-icon {
  background: linear-gradient(135deg, #fdf6ec 0%, #f9e8cc 100%);
  color: #e6a23c;
}

.topics-icon {
  background: linear-gradient(135deg, #fef0f0 0%, #fcd9d9 100%);
  color: #f56c6c;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

.stat-trend {
  position: absolute;
  top: 16px;
  right: 16px;
}

.trend-up {
  font-size: 11px;
  color: #67c23a;
  background: #f0f9ff;
  padding: 4px 8px;
  border-radius: 20px;
}

.trend-down {
  font-size: 11px;
  color: #f56c6c;
  background: #fef0f0;
  padding: 4px 8px;
  border-radius: 20px;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.usage-chart {
  width: 100%;
}

/* Chat Interface */
.chat-interface {
  display: flex;
  gap: 24px;
  background: white;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  min-height: 600px;
}

/* Chat Sidebar */
.chat-sidebar {
  width: 280px;
  background: #fafbfc;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.suggestions-list {
  flex: 1;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
}

.suggestion-btn:hover {
  border-color: #409eff;
  background: #f0f9ff;
  transform: translateX(4px);
}

.suggestion-icon {
  font-size: 20px;
}

.suggestion-text {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.online {
  background: #67c23a;
  box-shadow: 0 0 4px #67c23a;
}

.version-info {
  font-size: 12px;
  color: #909399;
}

/* Chat Main */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* Messages Container */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-height: 500px;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-wrapper.user .message-content {
  align-items: flex-end;
}

.message-wrapper.user .message-bubble {
  background: #409eff;
  color: white;
}

.message-wrapper.assistant .message-bubble {
  background: #f5f7fa;
  color: #1e293b;
}

.message-avatar {
  flex-shrink: 0;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.assistant-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user-avatar {
  background: #f5f7fa;
  color: #909399;
}

.message-content {
  flex: 1;
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-wrapper.user .message-content {
  align-items: flex-end;
}

.message-header {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.message-role {
  font-weight: 500;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  line-height: 1.5;
  font-size: 14px;
}

.message-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.message-text :deep(strong) {
  color: #409eff;
}

.message-text :deep(ul), .message-text :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-text :deep(li) {
  margin: 4px 0;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-10px); opacity: 1; }
}

/* Message Suggestions */
.message-suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.suggestion-chip {
  padding: 4px 12px;
  background: #f0f9ff;
  border: 1px solid #d9ecff;
  border-radius: 20px;
  font-size: 12px;
  color: #409eff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-chip:hover {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

/* Message Actions */
.message-actions {
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-wrapper:hover .message-actions {
  opacity: 1;
}

/* Input Area */
.chat-input-area {
  padding: 16px 24px;
  border-top: 1px solid #e4e7ed;
  background: white;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-container :deep(.el-textarea__inner) {
  border-radius: 16px;
  resize: none;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.input-tools {
  display: flex;
  gap: 8px;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .ai-assistant-container {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .chat-interface {
    flex-direction: column;
  }

  .chat-sidebar {
    width: 100%;
  }

  .message-content {
    max-width: 85%;
  }

  .page-header {
    flex-direction: column;
    text-align: center;
  }

  .header-right {
    width: 100%;
    justify-content: center;
  }
}
</style>