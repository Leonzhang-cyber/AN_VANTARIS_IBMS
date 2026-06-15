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
          <span class="loading-title">Loading AI Q&A Assistant</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IBMS AI-Powered Question Answering System</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="ai-qa-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">AI Q&A Assistant</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Operational Assistance</el-breadcrumb-item>
          <el-breadcrumb-item>AI Q&A Assistant</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" plain @click="clearConversation">
          <el-icon><Delete /></el-icon>
          New Conversation
        </el-button>
        <el-button type="info" plain @click="openSettings">
          <el-icon><Setting /></el-icon>
          Settings
        </el-button>
      </div>
    </div>

    <div class="main-layout">
      <!-- Sidebar - Conversation History -->
      <div class="sidebar">
        <el-card class="sidebar-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span><el-icon><Paperclip /></el-icon> Conversation History</span>
              <el-button text type="primary" size="small" @click="clearHistory">Clear All</el-button>
            </div>
          </template>
          <div class="conversation-list">
            <div
                v-for="conv in conversations"
                :key="conv.id"
                :class="['conversation-item', { active: currentConversationId === conv.id }]"
                @click="switchConversation(conv.id)"
            >
              <div class="conv-info">
                <div class="conv-title">{{ conv.title }}</div>
                <div class="conv-time">{{ conv.time }}</div>
              </div>
              <el-dropdown trigger="click" @command="(cmd) => handleConvAction(cmd, conv.id)">
                <el-icon class="conv-more"><MoreFilled /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="rename">Rename</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>Delete</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
            <div v-if="conversations.length === 0" class="empty-history">
              <el-empty description="No conversations yet" :image-size="80" />
            </div>
          </div>
        </el-card>

        <!-- Quick Stats -->
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <span><el-icon><DataAnalysis /></el-icon> Usage Statistics</span>
          </template>
          <div class="stats-list">
            <div class="stat-item">
              <span class="stat-label">Total Queries</span>
              <span class="stat-number">{{ stats.totalQueries }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Avg Response Time</span>
              <span class="stat-number">{{ stats.avgResponseTime }}s</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Accuracy Rate</span>
              <span class="stat-number">{{ stats.accuracyRate }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Satisfaction Score</span>
              <span class="stat-number">{{ stats.satisfactionScore }}/5</span>
            </div>
          </div>
        </el-card>

        <!-- Knowledge Base Status -->
        <el-card class="knowledge-status-card" shadow="hover">
          <template #header>
            <span><el-icon><Document /></el-icon> Knowledge Status</span>
          </template>
          <div class="knowledge-progress">
            <div class="progress-item">
              <span>Documents Indexed</span>
              <el-progress :percentage="94" :stroke-width="8" />
            </div>
            <div class="progress-item">
              <span>Models Trained</span>
              <el-progress :percentage="100" :stroke-width="8" status="success" />
            </div>
            <div class="progress-item">
              <span>Real-time Sync</span>
              <el-progress :percentage="87" :stroke-width="8" />
            </div>
          </div>
        </el-card>
      </div>

      <!-- Main Chat Area -->
      <div class="chat-area">
        <el-card class="chat-card" shadow="hover">
          <!-- Chat Messages -->
          <div class="chat-messages" ref="messagesContainer">
            <div v-if="messages.length === 0" class="welcome-section">
              <div class="welcome-icon">
                <el-icon :size="64"><Cpu /></el-icon>
              </div>
              <h3>AI Q&A Assistant</h3>
              <p>Ask me anything about IBMS operations, device troubleshooting, maintenance procedures, or system configuration.</p>
              <div class="suggestion-chips">
                <el-tag
                    v-for="suggestion in suggestions"
                    :key="suggestion"
                    class="suggestion-chip"
                    @click="sendSuggestion(suggestion)"
                >
                  {{ suggestion }}
                </el-tag>
              </div>
            </div>
            <div v-else>
              <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="msg.role === 'user' ? UserFilled : Cpu" />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="message-name">{{ msg.role === 'user' ? 'You' : 'AI Assistant' }}</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-text" v-html="formatMessage(msg.content)"></div>
                  <div v-if="msg.role === 'assistant' && msg.sources" class="message-sources">
                    <span class="sources-label">Sources:</span>
                    <el-link v-for="src in msg.sources" :key="src" type="info" :underline="false" @click="viewSource(src)">
                      {{ src }}
                    </el-link>
                  </div>
                </div>
              </div>
              <div v-if="isTyping" class="message assistant typing">
                <div class="message-avatar">
                  <el-avatar :size="36" :icon="Cpu" />
                </div>
                <div class="message-content">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="chat-input-area">
            <el-input
                v-model="currentQuery"
                type="textarea"
                :rows="3"
                placeholder="Ask me anything about IBMS operations, device issues, maintenance, energy management, or ESG compliance..."
                @keydown.ctrl.enter="sendMessage"
                :disabled="isTyping"
                resize="none"
            />
            <div class="input-actions">
              <div class="input-tools">
                <el-tooltip content="Attach file" placement="top">
                  <el-button text @click="attachFile">
                    <el-icon><Paperclip /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="Voice input" placement="top">
                  <el-button text @click="voiceInput">
                    <el-icon><Microphone /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="Clear chat" placement="top">
                  <el-button text @click="clearChat">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
              <el-button
                  type="primary"
                  :loading="isTyping"
                  :disabled="!currentQuery.trim()"
                  @click="sendMessage"
              >
                <el-icon><Promotion /></el-icon>
                Send
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- Right Sidebar - Quick Actions & Context -->
      <div class="right-sidebar">
        <!-- Quick Actions -->
        <el-card class="quick-actions-card" shadow="hover">
          <template #header>
            <span><el-icon><Lightning /></el-icon> Quick Actions</span>
          </template>
          <div class="quick-actions-list">
            <div class="quick-action" @click="quickAction('troubleshoot')">
              <el-icon><Tools /></el-icon>
              <span>Troubleshoot Device</span>
            </div>
            <div class="quick-action" @click="quickAction('maintenance')">
              <el-icon><Setting /></el-icon>
              <span>Find Maintenance Guide</span>
            </div>
            <div class="quick-action" @click="quickAction('sop')">
              <el-icon><Document /></el-icon>
              <span>Get SOP Document</span>
            </div>
            <div class="quick-action" @click="quickAction('alarm')">
              <el-icon><Bell /></el-icon>
              <span>Alarm Resolution</span>
            </div>
            <div class="quick-action" @click="quickAction('energy')">
              <el-icon><Orange /></el-icon>
              <span>Energy Optimization</span>
            </div>
            <div class="quick-action" @click="quickAction('esg')">
              <el-icon><TrendCharts /></el-icon>
              <span>ESG Reporting</span>
            </div>
          </div>
        </el-card>

        <!-- Recent Answers -->
        <el-card class="recent-answers-card" shadow="hover">
          <template #header>
            <span><el-icon><Clock /></el-icon> Recent Answers</span>
          </template>
          <div class="recent-list">
            <div v-for="answer in recentAnswers" :key="answer.id" class="recent-item" @click="reuseAnswer(answer)">
              <div class="recent-question">{{ answer.question }}</div>
              <div class="recent-time">{{ answer.time }}</div>
            </div>
          </div>
        </el-card>

        <!-- Context Info -->
        <el-card class="context-card" shadow="hover">
          <template #header>
            <span><el-icon><InfoFilled /></el-icon> Session Context</span>
          </template>
          <div class="context-info">
            <div class="context-item">
              <span>Current Site:</span>
              <el-select v-model="currentSite" size="small" placeholder="Select site">
                <el-option label="All Sites" value="all" />
                <el-option label="Data Center A" value="dc_a" />
                <el-option label="Data Center B" value="dc_b" />
                <el-option label="Office Tower" value="office" />
              </el-select>
            </div>
            <div class="context-item">
              <span>Knowledge Domain:</span>
              <el-select v-model="knowledgeDomain" size="small" multiple placeholder="Select domains">
                <el-option label="HVAC Systems" value="hvac" />
                <el-option label="Electrical Systems" value="electrical" />
                <el-option label="Fire Safety" value="fire" />
                <el-option label="Security Systems" value="security" />
                <el-option label="Energy Management" value="energy" />
                <el-option label="ESG Compliance" value="esg" />
              </el-select>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Delete, Setting, MoreFilled, DataAnalysis, Document,
  Cpu, UserFilled, Promotion, Paperclip, Microphone, Tools,
  Bell, Orange, TrendCharts, Clock, InfoFilled, Lightning,
  Edit, Check, Close
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing AI Q&A Assistant...')

const loadingMessages = [
  'Initializing AI Q&A Assistant...',
  'Loading knowledge base...',
  'Starting language model...',
  'Ready to answer your questions!'
]

// Chat state
const currentQuery = ref('')
const messages = ref<any[]>([])
const isTyping = ref(false)
const currentConversationId = ref<string>('')
const messagesContainer = ref<HTMLElement>()

// Conversations
const conversations = ref([
  { id: '1', title: 'HVAC Troubleshooting', time: '10:30 AM' },
  { id: '2', title: 'BACnet Integration Issues', time: 'Yesterday' },
  { id: '3', title: 'Energy Savings Tips', time: 'Jan 15, 2024' }
])

// Statistics
const stats = ref({
  totalQueries: 1248,
  avgResponseTime: 1.2,
  accuracyRate: 94.5,
  satisfactionScore: 4.6
})

// Recent answers
const recentAnswers = ref([
  { id: 1, question: 'How to reset chiller fault?', answer: 'To reset a chiller fault...', time: '2h ago' },
  { id: 2, question: 'BACnet device not responding', answer: 'Check network connectivity...', time: '5h ago' },
  { id: 3, question: 'PUE calculation method', answer: 'PUE = Total Facility Energy / IT Equipment Energy...', time: '1d ago' }
])

// Suggestions
const suggestions = [
  'How do I troubleshoot a BACnet communication failure?',
  'What is the procedure for emergency generator testing?',
  'How to calculate PUE for my data center?',
  'Explain ESG compliance requirements for 2024',
  'How to optimize HVAC energy consumption?',
  'What to do when fire alarm triggers?'
]

// Filters and settings
const currentSite = ref('all')
const knowledgeDomain = ref(['hvac', 'electrical'])

// Scroll to bottom of chat
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Format message with markdown-like syntax
const formatMessage = (content: string) => {
  let formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br>')
  return formatted
}

// Send message
const sendMessage = async () => {
  if (!currentQuery.value.trim() || isTyping.value) return

  const userMessage = {
    role: 'user',
    content: currentQuery.value,
    time: new Date().toLocaleTimeString()
  }

  messages.value.push(userMessage)
  scrollToBottom()

  const query = currentQuery.value
  currentQuery.value = ''
  isTyping.value = true

  // Simulate AI response
  setTimeout(() => {
    const response = generateResponse(query)
    const assistantMessage = {
      role: 'assistant',
      content: response.content,
      time: new Date().toLocaleTimeString(),
      sources: response.sources
    }
    messages.value.push(assistantMessage)
    isTyping.value = false
    scrollToBottom()

    // Update stats
    stats.value.totalQueries++

    // Add to recent answers
    recentAnswers.value.unshift({
      id: Date.now(),
      question: query,
      answer: response.content,
      time: 'Just now'
    })
    if (recentAnswers.value.length > 10) recentAnswers.value.pop()
  }, 1500)
}

// Generate AI response based on query
const generateResponse = (query: string) => {
  const lowerQuery = query.toLowerCase()

  if (lowerQuery.includes('hvac') || lowerQuery.includes('chiller')) {
    return {
      content: '**HVAC System Troubleshooting Guide**\n\n1. Check if the chiller is powered on and receiving proper voltage.\n2. Verify the temperature setpoints are correctly configured.\n3. Inspect for any active alarms on the chiller controller.\n4. Check water flow rates and pump operation.\n5. Review the chiller log for any recent events or warnings.\n\nFor persistent issues, please refer to the manufacturer documentation or contact your facility manager.',
      sources: ['HVAC Maintenance Guide v2.1', 'Chiller Operation Manual']
    }
  }

  if (lowerQuery.includes('bacnet')) {
    return {
      content: '**BACnet Communication Issue Resolution**\n\n**Step 1: Physical Connection Check**\n- Verify all wiring connections are secure\n- Check termination resistors on MS/TP networks\n\n**Step 2: Device Configuration**\n- Confirm MAC addresses are unique on the network\n- Verify baud rate matches across all devices\n\n**Step 3: Network Diagnostics**\n- Use BACnet scan tool to discover devices\n- Check for duplicate device instance numbers\n\n**Step 4: Testing**\n- Perform point reads from the controller\n- Test write commands on non-critical points',
      sources: ['BACnet Integration Guide', 'Network Troubleshooting SOP']
    }
  }

  if (lowerQuery.includes('pue')) {
    return {
      content: '**Power Usage Effectiveness (PUE) Calculation**\n\nPUE = **Total Facility Energy** / **IT Equipment Energy**\n\n**Formula Breakdown:**\n- **Total Facility Energy**: All energy consumed by the data center including IT equipment, cooling, lighting, and power distribution losses.\n- **IT Equipment Energy**: Energy consumed exclusively by IT equipment (servers, storage, networking).\n\n**Industry Benchmarks:**\n- Legacy Data Centers: 2.0 - 2.5\n- Typical Modern: 1.6 - 1.8\n- Optimized: 1.3 - 1.5\n- Best in Class: < 1.2\n\n**Improvement Strategies:**\n1. Implement hot aisle/cold aisle containment\n2. Increase cooling setpoints\n3. Use free cooling when available\n4. Upgrade to high-efficiency UPS systems',
      sources: ['Energy Efficiency Guide', 'Green Grid PUE Standard']
    }
  }

  if (lowerQuery.includes('esg') || lowerQuery.includes('compliance')) {
    return {
      content: '**ESG Compliance Overview for 2024**\n\n**Key Reporting Frameworks:**\n- **IFRS S2**: Climate-related disclosures required for fiscal years starting 2024\n- **CSRD**: Applies to large EU companies from 2024\n- **SEC Climate Rule**: Proposed, expected 2024-2025\n\n**Data Center Specific Requirements:**\n1. Scope 1 & 2 emissions reporting mandatory\n2. Scope 3 reporting for large enterprises\n3. Water usage effectiveness (WUE) tracking\n4. Renewable Energy Attribution (REA)\n\n**Recommended Actions:**\n- Implement automated data collection\n- Establish baseline metrics for 2023\n- Set science-based reduction targets\n- Prepare for third-party assurance',
      sources: ['ESG Compliance Matrix 2024', 'IFRS S2 Implementation Guide']
    }
  }

  if (lowerQuery.includes('energy') || lowerQuery.includes('optimization')) {
    return {
      content: '**Energy Optimization Strategies**\n\n**HVAC Optimization:**\n- Implement optimal start/stop scheduling\n- Use demand-controlled ventilation (CO2 sensors)\n- Regular filter replacement and coil cleaning\n\n**Lighting Optimization:**\n- Install occupancy sensors in low-traffic areas\n- Implement daylight harvesting controls\n- Schedule lighting based on operational hours\n\n**Power Management:**\n- Power down unused servers\n- Virtualize workloads to reduce physical servers\n- Use high-efficiency power supplies\n\n**Expected Savings:** 15-25% reduction in energy consumption',
      sources: ['Energy Optimization Playbook', 'Case Study: Data Center A']
    }
  }

  return {
    content: `**Question:** ${query}\n\nI understand you're asking about this topic. Here's what I can help with:\n\n1. **Check the knowledge base** for relevant documentation\n2. **Review system logs** for related events\n3. **Consult the operator manual** for specific procedures\n\nFor more specific assistance, please provide additional details about the device, system, or issue you're encountering. You can also try rephrasing your question or selecting one of the suggested queries above.`,
    sources: ['IBMS Knowledge Base', 'System Documentation']
  }
}

// Clear chat
const clearChat = () => {
  messages.value = []
  ElMessage.success('Chat cleared')
}

// Clear conversation history
const clearHistory = () => {
  conversations.value = []
  ElMessage.success('Conversation history cleared')
}

// New conversation
const clearConversation = () => {
  messages.value = []
  currentConversationId.value = ''
  ElMessage.success('New conversation started')
}

// Switch conversation
const switchConversation = (id: string) => {
  currentConversationId.value = id
  ElMessage.info(`Switched to conversation: ${conversations.value.find(c => c.id === id)?.title}`)
}

// Handle conversation actions
const handleConvAction = (cmd: string, id: string) => {
  if (cmd === 'delete') {
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (currentConversationId.value === id) {
      messages.value = []
      currentConversationId.value = ''
    }
    ElMessage.success('Conversation deleted')
  } else if (cmd === 'rename') {
    ElMessage.info('Rename feature coming soon')
  }
}

// Send suggestion
const sendSuggestion = (suggestion: string) => {
  currentQuery.value = suggestion
  sendMessage()
}

// Quick action
const quickAction = (action: string) => {
  const actions: Record<string, string> = {
    troubleshoot: 'How do I troubleshoot a device communication failure?',
    maintenance: 'What is the preventive maintenance schedule for HVAC?',
    sop: 'Show me the SOP for emergency generator testing',
    alarm: 'How to resolve a critical alarm in the system?',
    energy: 'How can I optimize energy consumption?',
    esg: 'What are the latest ESG reporting requirements?'
  }
  currentQuery.value = actions[action] || action
  sendMessage()
}

// Reuse previous answer
const reuseAnswer = (answer: any) => {
  currentQuery.value = answer.question
  sendMessage()
}

// Attach file
const attachFile = () => {
  ElMessage.info('File attachment feature coming soon')
}

// Voice input
const voiceInput = () => {
  ElMessage.info('Voice input feature coming soon')
}

// Open settings
const openSettings = () => {
  ElMessage.info('Settings panel coming soon')
}

// View source document
const viewSource = (source: string) => {
  ElMessage.info(`Opening source: ${source}`)
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

/* ==================== Main Content Styles ==================== */
.ai-qa-container {
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

.main-layout {
  display: grid;
  grid-template-columns: 300px 1fr 320px;
  gap: 20px;
}

/* Sidebar Styles */
.sidebar,
.right-sidebar {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card,
.stats-card,
.knowledge-status-card,
.quick-actions-card,
.recent-answers-card,
.context-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.conversation-list {
  max-height: 300px;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.conversation-item:hover {
  background: #f8fafc;
}

.conversation-item.active {
  background: #eef2ff;
  border-left: 3px solid #3b82f6;
}

.conv-info {
  flex: 1;
}

.conv-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.conv-time {
  font-size: 11px;
  color: #94a3b8;
}

.conv-more {
  color: #94a3b8;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .conv-more {
  opacity: 1;
}

.empty-history {
  padding: 20px;
  text-align: center;
}

.stats-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.stat-number {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.knowledge-progress {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-item span {
  font-size: 13px;
  color: #475569;
  display: block;
  margin-bottom: 8px;
}

/* Chat Area Styles */
.chat-area {
  display: flex;
  flex-direction: column;
}

.chat-card {
  border-radius: 12px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  height: 500px;
  overflow-y: auto;
  padding: 20px;
}

.welcome-section {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  margin-bottom: 20px;
  color: #3b82f6;
}

.welcome-section h3 {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 12px;
}

.welcome-section p {
  color: #64748b;
  margin-bottom: 24px;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.suggestion-chip {
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-chip:hover {
  transform: translateY(-2px);
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background: #3b82f6;
  color: white;
}

.message.user .message-header {
  justify-content: flex-end;
}

.message.user .message-name {
  color: #bfdbfe;
}

.message-content {
  flex: 1;
  max-width: 80%;
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.message-name {
  font-weight: 600;
  color: #1e293b;
}

.message-time {
  color: #94a3b8;
  font-size: 11px;
}

.message-text {
  line-height: 1.5;
  font-size: 14px;
}

.message-text :deep(strong) {
  color: #3b82f6;
}

.message-text :deep(code) {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.message-sources {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  font-size: 12px;
}

.sources-label {
  color: #64748b;
  margin-right: 8px;
}

.message-sources .el-link {
  margin-right: 12px;
  font-size: 12px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.chat-input-area {
  padding: 16px;
  border-top: 1px solid #e2e8f0;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.input-tools {
  display: flex;
  gap: 8px;
}

/* Right Sidebar Styles */
.quick-actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.quick-action:hover {
  background: #f8fafc;
}

.quick-action .el-icon {
  color: #3b82f6;
  font-size: 20px;
}

.quick-action span {
  font-size: 14px;
  color: #1e293b;
}

.recent-list {
  max-height: 250px;
  overflow-y: auto;
}

.recent-item {
  padding: 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 8px;
}

.recent-item:hover {
  background: #f8fafc;
}

.recent-question {
  font-size: 13px;
  color: #1e293b;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recent-time {
  font-size: 11px;
  color: #94a3b8;
}

.context-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.context-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.context-item span {
  font-size: 13px;
  color: #64748b;
}

/* Responsive */
@media (max-width: 1200px) {
  .main-layout {
    grid-template-columns: 260px 1fr 280px;
  }
}

@media (max-width: 992px) {
  .main-layout {
    grid-template-columns: 1fr;
  }

  .sidebar,
  .right-sidebar {
    display: none;
  }
}
</style>