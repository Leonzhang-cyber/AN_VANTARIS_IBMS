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
        <div class="loading-tip">Alarm Correlation</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="alarm-correlation-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="dashboard-title">
          <el-icon><Connection /></el-icon>
          Alarm Correlation
        </h1>
        <div class="header-stats">
          <div class="stat-badge">
            <el-icon><Grid /></el-icon>
            {{ totalCorrelations }} Correlation Rules
          </div>
          <div class="stat-badge">
            <el-icon><Bell /></el-icon>
            {{ totalAlarms }} Alarms Analyzed
          </div>
        </div>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="analyzeCorrelation">
          <el-icon><DataAnalysis /></el-icon>
          Analyze Now
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
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c;">🔗</div>
        <div class="stat-info">
          <div class="stat-value">{{ rootCauseCount }}</div>
          <div class="stat-label">Root Causes</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c;">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ correlationRate }}%</div>
          <div class="stat-label">Correlation Rate</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #fbbf24;">⏱️</div>
        <div class="stat-info">
          <div class="stat-value">{{ avgCorrelationTime }}<span class="unit">s</span></div>
          <div class="stat-label">Avg Correlation Time</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff;">🎯</div>
        <div class="stat-info">
          <div class="stat-value">{{ accuracyRate }}%</div>
          <div class="stat-label">Correlation Accuracy</div>
        </div>
      </div>
    </div>

    <!-- Search & Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="to"
            start-placeholder="Start Time"
            end-placeholder="End Time"
            size="default"
            style="width: 360px"
        />
        <el-select v-model="severityFilter" placeholder="Severity" size="default" style="width: 120px" clearable>
          <el-option label="All" value="all" />
          <el-option label="Critical" value="critical" />
          <el-option label="Major" value="major" />
          <el-option label="Warning" value="warning" />
        </el-select>
        <el-input v-model="searchText" placeholder="Search alarms..." size="default" style="width: 200px" clearable>
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
    </div>

    <!-- Correlation Graph using Vue Flow -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><Share /></el-icon>
          Alarm Correlation Graph
        </div>
        <div class="card-actions">
          <el-radio-group v-model="graphLayout" size="small" @change="changeLayout">
            <el-radio-button label="dagre">Hierarchical</el-radio-button>
            <el-radio-button label="force">Force</el-radio-button>
          </el-radio-group>
          <el-button size="small" @click="fitView">
            <el-icon><FullScreen /></el-icon>
            Fit View
          </el-button>
          <el-button size="small" @click="resetTransform">
            <el-icon><RefreshRight /></el-icon>
            Reset
          </el-button>
        </div>
      </div>
      <div class="graph-container">
        <VueFlow
            ref="vueFlowRef"
            v-model:nodes="nodes"
            v-model:edges="edges"
            :fit-view-on-init="true"
            :default-viewport="{ zoom: 1, x: 0, y: 0 }"
            :min-zoom="0.2"
            :max-zoom="4"
            :snap-to-grid="true"
            :snap-grid="[15, 15]"
            class="flow-chart"
            @node-click="onNodeClick"
            @edge-click="onEdgeClick"
        >
          <Background pattern-color="#c0c4cc" :gap="20" />
          <Controls position="bottom-right" />
          <MiniMap position="bottom-left" :width="150" :height="120" />
        </VueFlow>
      </div>
    </div>

    <!-- Correlation Rules & Matches -->
    <div class="two-columns">
      <!-- Left: Correlation Rules -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><Document /></el-icon>
            Correlation Rules
          </div>
          <el-button type="primary" link @click="handleCreateRule">
            <el-icon><Plus /></el-icon>
            New Rule
          </el-button>
        </div>
        <div class="rules-list">
          <div v-for="rule in correlationRules" :key="rule.id" class="rule-item">
            <div class="rule-header">
              <span class="rule-name">{{ rule.name }}</span>
              <el-switch v-model="rule.enabled" size="small" @change="toggleRule(rule)" />
            </div>
            <div class="rule-pattern">{{ rule.pattern }}</div>
            <div class="rule-meta">
              <span>Matches: {{ rule.matchCount }}</span>
              <span>Confidence: {{ rule.confidence }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Recent Correlations -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">
            <el-icon><List /></el-icon>
            Recent Correlations
          </div>
        </div>
        <div class="correlations-list">
          <div v-for="corr in recentCorrelations" :key="corr.id" class="correlation-item">
            <div class="correlation-header">
              <el-tag :type="getSeverityTag(corr.severity)" size="small">{{ corr.severity.toUpperCase() }}</el-tag>
              <span class="correlation-time">{{ corr.time }}</span>
            </div>
            <div class="correlation-title">{{ corr.rootCause }}</div>
            <div class="correlation-alarms">
              <el-tag v-for="alarm in corr.relatedAlarms" :key="alarm" size="small" class="alarm-tag">
                {{ alarm }}
              </el-tag>
            </div>
            <div class="correlation-confidence">
              Confidence: {{ corr.confidence }}% • {{ corr.ruleName }}
            </div>
          </div>
          <div v-if="recentCorrelations.length === 0" class="empty-state">
            <el-empty description="No correlations found" :image-size="60" />
          </div>
        </div>
      </div>
    </div>

    <!-- Root Cause Analysis -->
    <div class="card">
      <div class="card-header">
        <div class="card-title">
          <el-icon><TrendCharts /></el-icon>
          Root Cause Analysis
        </div>
      </div>
      <div class="root-cause-grid">
        <div v-for="rootCause in rootCauses" :key="rootCause.id" class="root-cause-card">
          <div class="root-cause-header">
            <span class="root-cause-name">{{ rootCause.name }}</span>
            <el-tag :type="getSeverityTag(rootCause.severity)" size="small">{{ rootCause.severity.toUpperCase() }}</el-tag>
          </div>
          <div class="root-cause-stats">
            <div class="stat">
              <span>Occurrences:</span>
              <strong>{{ rootCause.count }}</strong>
            </div>
            <div class="stat">
              <span>Impact:</span>
              <strong>{{ rootCause.impact }} alarms</strong>
            </div>
            <div class="stat">
              <span>Confidence:</span>
              <strong>{{ rootCause.confidence }}%</strong>
            </div>
          </div>
          <div class="root-cause-symptoms">
            <div v-for="symptom in rootCause.symptoms" :key="symptom" class="symptom-tag">
              {{ symptom }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Rule Dialog -->
    <el-dialog v-model="ruleDialogVisible" title="Create Correlation Rule" width="500px">
      <el-form :model="ruleForm" :rules="ruleFormRules" ref="ruleFormRef" label-width="100px">
        <el-form-item label="Rule Name" prop="name">
          <el-input v-model="ruleForm.name" placeholder="Enter rule name" />
        </el-form-item>
        <el-form-item label="Pattern" prop="pattern">
          <el-input v-model="ruleForm.pattern" type="textarea" :rows="2" placeholder="e.g., Temperature > 35°C AND Power > 150kW" />
        </el-form-item>
        <el-form-item label="Time Window" prop="timeWindow">
          <el-input-number v-model="ruleForm.timeWindow" :min="1" :max="3600" :step="10" style="width: 100%" />
          <span class="form-tip">seconds</span>
        </el-form-item>
        <el-form-item label="Min Matches" prop="minMatches">
          <el-input-number v-model="ruleForm.minMatches" :min="1" :max="100" :step="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ruleDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="saveRule">Create Rule</el-button>
      </template>
    </el-dialog>

    <!-- Node Detail Dialog -->
    <el-dialog v-model="nodeDialogVisible" :title="`Alarm Details - ${selectedNode?.label}`" width="500px">
      <el-descriptions :column="1" border v-if="selectedNode">
        <el-descriptions-item label="Node Name">{{ selectedNode.label }}</el-descriptions-item>
        <el-descriptions-item label="Type">{{ selectedNode.data?.type || 'Alarm' }}</el-descriptions-item>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTag(selectedNode.data?.severity || 'warning')" size="small">
            {{ selectedNode.data?.severity?.toUpperCase() || 'WARNING' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Description">{{ selectedNode.data?.description || 'Alarm detected in the system' }}</el-descriptions-item>
        <el-descriptions-item label="Connections">{{ selectedNode.data?.connections || 0 }} related alarms</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="nodeDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="investigateNode">Investigate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Connection, Grid, Bell, DataAnalysis, Refresh, Share, Document, Plus, List, Search, TrendCharts, FullScreen, RefreshRight } from '@element-plus/icons-vue'
import { VueFlow, useVueFlow, type Node, type Edge } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'
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
  'Loading correlation engine...',
  'Analyzing alarm patterns...',
  'Building correlation graph...',
  'Almost ready...'
]

// ==================== Vue Flow ====================
const vueFlowRef = ref()
const { fitView, zoomIn, zoomOut, resetTransform } = useVueFlow()

// Node and Edge definitions
const nodes = ref<Node[]>([
  { id: '1', label: 'UPS Overload', position: { x: 250, y: 50 }, data: { type: 'Root Cause', severity: 'critical', description: 'UPS load exceeds 90% capacity', connections: 4 }, style: { backgroundColor: '#fef0f0', borderColor: '#f56c6c', borderRadius: '8px' } },
  { id: '2', label: 'Power Spike', position: { x: 100, y: 200 }, data: { type: 'Secondary', severity: 'major', description: 'Power consumption spike detected', connections: 2 }, style: { backgroundColor: '#fdf6ec', borderColor: '#e6a23c', borderRadius: '8px' } },
  { id: '3', label: 'Temperature Rise', position: { x: 400, y: 200 }, data: { type: 'Secondary', severity: 'warning', description: 'Temperature increased above threshold', connections: 2 }, style: { backgroundColor: '#fdf6ec', borderColor: '#fbbf24', borderRadius: '8px' } },
  { id: '4', label: 'CPU High', position: { x: 100, y: 350 }, data: { type: 'Resource', severity: 'major', description: 'CPU usage above 85%', connections: 3 }, style: { backgroundColor: '#ecf5ff', borderColor: '#409eff', borderRadius: '8px' } },
  { id: '5', label: 'Memory High', position: { x: 250, y: 350 }, data: { type: 'Resource', severity: 'warning', description: 'Memory usage above 80%', connections: 2 }, style: { backgroundColor: '#f0f9eb', borderColor: '#67c23a', borderRadius: '8px' } },
  { id: '6', label: 'Network Latency', position: { x: 400, y: 350 }, data: { type: 'Network', severity: 'warning', description: 'Network latency exceeded 100ms', connections: 2 }, style: { backgroundColor: '#f4f4f5', borderColor: '#909399', borderRadius: '8px' } },
  { id: '7', label: 'Packet Loss', position: { x: 550, y: 350 }, data: { type: 'Network', severity: 'major', description: 'Packet loss detected', connections: 1 }, style: { backgroundColor: '#fef0f0', borderColor: '#f97316', borderRadius: '8px' } },
  { id: '8', label: 'Disk I/O High', position: { x: 250, y: 500 }, data: { type: 'Storage', severity: 'warning', description: 'Disk I/O operations high', connections: 1 }, style: { backgroundColor: '#f3f0ff', borderColor: '#8b5cf6', borderRadius: '8px' } }
])

const edges = ref<Edge[]>([
  { id: 'e1-2', source: '1', target: '2', label: 'causes', animated: true, style: { stroke: '#f56c6c' } },
  { id: 'e1-3', source: '1', target: '3', label: 'causes', animated: true, style: { stroke: '#f56c6c' } },
  { id: 'e2-4', source: '2', target: '4', label: 'triggers', style: { stroke: '#e6a23c' } },
  { id: 'e3-5', source: '3', target: '5', label: 'affects', style: { stroke: '#fbbf24' } },
  { id: 'e4-5', source: '4', target: '5', label: 'correlates', style: { stroke: '#409eff' } },
  { id: 'e4-6', source: '4', target: '6', label: 'impacts', style: { stroke: '#409eff' } },
  { id: 'e6-7', source: '6', target: '7', label: 'causes', animated: true, style: { stroke: '#f97316' } },
  { id: 'e4-8', source: '4', target: '8', label: 'correlates', style: { stroke: '#8b5cf6' } }
])

const graphLayout = ref('dagre')
const nodeDialogVisible = ref(false)
const selectedNode = ref<Node | null>(null)

const changeLayout = () => {
  // Layout change would be handled by dagre layout calculation
  // For simplicity, we just reset view
  setTimeout(() => {
    fitView()
  }, 100)
}

const onNodeClick = (event: any) => {
  selectedNode.value = event.node
  nodeDialogVisible.value = true
}

const onEdgeClick = (event: any) => {
  ElMessage.info(`Edge: ${event.edge.source} → ${event.edge.target}`)
}

const investigateNode = () => {
  ElMessage.info(`Investigating ${selectedNode.value?.label}`)
  nodeDialogVisible.value = false
}

// ==================== Data State ====================
const dateRange = ref<[Date, Date] | null>(null)
const severityFilter = ref('all')
const searchText = ref('')
const ruleDialogVisible = ref(false)
const ruleFormRef = ref()

const totalCorrelations = ref(24)
const totalAlarms = ref(1256)
const rootCauseCount = ref(8)
const correlationRate = ref(76)
const avgCorrelationTime = ref(12)
const accuracyRate = ref(94)

// Correlation Rules
interface CorrelationRule {
  id: number
  name: string
  pattern: string
  enabled: boolean
  matchCount: number
  confidence: number
}

const correlationRules = ref<CorrelationRule[]>([
  { id: 1, name: 'Temperature-Power Correlation', pattern: 'Temperature > 35°C → Power > 150kW', enabled: true, matchCount: 23, confidence: 92 },
  { id: 2, name: 'CPU-Memory Cascade', pattern: 'CPU > 80% → Memory > 75%', enabled: true, matchCount: 45, confidence: 88 },
  { id: 3, name: 'Network-CPU Spike', pattern: 'Network > 500Mbps → CPU > 70%', enabled: true, matchCount: 18, confidence: 85 },
  { id: 4, name: 'Power-Temperature Cascade', pattern: 'Power > 180kW → Temperature > 32°C', enabled: true, matchCount: 12, confidence: 90 },
  { id: 5, name: 'Disk-Memory Pattern', pattern: 'Disk > 90% → Memory > 85%', enabled: false, matchCount: 8, confidence: 75 }
])

// Recent Correlations
const recentCorrelations = ref([
  { id: 1, severity: 'critical', time: '2024-06-03 14:30:22', rootCause: 'UPS Overload caused cascading failures', relatedAlarms: ['UPS Overload', 'Power Spike', 'Temperature Rise'], confidence: 95, ruleName: 'Temperature-Power Correlation' },
  { id: 2, severity: 'critical', time: '2024-06-03 13:20:45', rootCause: 'Database server overload', relatedAlarms: ['High CPU Usage', 'Memory Threshold', 'Slow Queries'], confidence: 88, ruleName: 'CPU-Memory Cascade' },
  { id: 3, severity: 'major', time: '2024-06-03 11:15:33', rootCause: 'Network congestion', relatedAlarms: ['High Latency', 'Packet Loss', 'Bandwidth Exceeded'], confidence: 82, ruleName: 'Network-CPU Spike' },
  { id: 4, severity: 'warning', time: '2024-06-03 09:45:12', rootCause: 'Cooling inefficiency', relatedAlarms: ['High Temperature', 'Fan Speed High'], confidence: 78, ruleName: 'Power-Temperature Cascade' },
  { id: 5, severity: 'major', time: '2024-06-02 16:20:00', rootCause: 'Storage bottleneck', relatedAlarms: ['Disk I/O High', 'Memory Pressure'], confidence: 85, ruleName: 'Disk-Memory Pattern' }
])

// Root Causes
const rootCauses = ref([
  { id: 1, name: 'UPS Overload', severity: 'critical', count: 5, impact: 23, confidence: 95, symptoms: ['UPS Load > 90%', 'Power Spike', 'Temperature Rise', 'Voltage Drop'] },
  { id: 2, name: 'Database Server Overload', severity: 'critical', count: 4, impact: 18, confidence: 92, symptoms: ['High CPU Usage', 'Memory Threshold', 'Slow Queries', 'Connection Pool Exhausted'] },
  { id: 3, name: 'Network Congestion', severity: 'major', count: 3, impact: 15, confidence: 88, symptoms: ['High Latency', 'Packet Loss', 'Bandwidth Exceeded', 'Queue Drops'] },
  { id: 4, name: 'Cooling System Failure', severity: 'major', count: 2, impact: 12, confidence: 85, symptoms: ['High Temperature', 'Fan Speed High', 'CRAC Offline'] }
])

const ruleForm = ref({
  name: '',
  pattern: '',
  timeWindow: 60,
  minMatches: 2
})

const ruleFormRules = {
  name: [{ required: true, message: 'Please enter rule name', trigger: 'blur' }],
  pattern: [{ required: true, message: 'Please enter pattern', trigger: 'blur' }]
}

// ==================== Helper Functions ====================
const getSeverityTag = (severity: string) => {
  const map: Record<string, string> = {
    critical: 'danger',
    major: 'warning',
    warning: 'warning',
    info: 'info'
  }
  return map[severity] || 'info'
}

// ==================== Actions ====================
const toggleRule = (rule: CorrelationRule) => {
  ElMessage.success(`Rule "${rule.name}" ${rule.enabled ? 'enabled' : 'disabled'}`)
}

const analyzeCorrelation = () => {
  ElMessage.success('Correlation analysis completed')
}

const handleCreateRule = () => {
  ruleForm.value = { name: '', pattern: '', timeWindow: 60, minMatches: 2 }
  ruleDialogVisible.value = true
}

const saveRule = async () => {
  try {
    await ruleFormRef.value?.validate()
    ElMessage.success('Correlation rule created successfully')
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
        setTimeout(() => {
          fitView()
        }, 200)
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
.alarm-correlation-dashboard {
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

.stat-value .unit {
  font-size: 12px;
  font-weight: normal;
  color: #909399;
  margin-left: 2px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* Filter Bar */
.filter-bar {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

/* Card */
.card {
  background: #ffffff;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
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

.card-actions {
  display: flex;
  gap: 8px;
}

/* Vue Flow Graph */
.graph-container {
  width: 100%;
  height: 500px;
  position: relative;
  background: #fafafa;
}

.flow-chart {
  width: 100%;
  height: 100%;
  background: #fafafa;
}

/* Two Columns */
.two-columns {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.two-columns .card {
  flex: 1;
  margin-bottom: 0;
}

/* Rules List */
.rules-list {
  padding: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.rule-item {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
  transition: background 0.2s;
}

.rule-item:hover {
  background: #f5f7fa;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.rule-name {
  font-weight: 600;
  color: #1f2f3d;
}

.rule-pattern {
  font-size: 12px;
  color: #606266;
  font-family: monospace;
  margin-bottom: 8px;
}

.rule-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #909399;
}

/* Correlations List */
.correlations-list {
  padding: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.correlation-item {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.correlation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.correlation-time {
  font-size: 11px;
  color: #909399;
}

.correlation-title {
  font-weight: 600;
  color: #1f2f3d;
  margin-bottom: 8px;
}

.correlation-alarms {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.alarm-tag {
  font-size: 11px;
}

.correlation-confidence {
  font-size: 11px;
  color: #909399;
}

.empty-state {
  padding: 20px;
  text-align: center;
}

/* Root Cause Grid */
.root-cause-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
  padding: 16px;
}

.root-cause-card {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  padding: 16px;
  transition: all 0.2s;
}

.root-cause-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.root-cause-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.root-cause-name {
  font-weight: 600;
  font-size: 15px;
  color: #1f2f3d;
}

.root-cause-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 12px;
  font-size: 12px;
}

.root-cause-stats .stat {
  display: flex;
  gap: 4px;
}

.root-cause-stats .stat span {
  color: #909399;
}

.root-cause-stats .stat strong {
  color: #409eff;
}

.root-cause-symptoms {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.symptom-tag {
  background: #ecf5ff;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
}

/* Form Tip */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 12px;
}

/* Responsive */
@media (max-width: 1000px) {
  .two-columns {
    flex-direction: column;
  }
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .alarm-correlation-dashboard {
    padding: 16px;
  }
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .stats-grid {
    grid-template-columns: 1fr;
  }
  .filter-group {
    flex-direction: column;
    width: 100%;
  }
  .filter-group .el-date-picker,
  .filter-group .el-select,
  .filter-group .el-input {
    width: 100% !important;
  }
  .root-cause-grid {
    grid-template-columns: 1fr;
  }
  .graph-container {
    height: 400px;
  }
}

/* Vue Flow 样式覆盖 */
:deep(.vue-flow__node) {
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

:deep(.vue-flow__node:hover) {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

:deep(.vue-flow__edge) {
  stroke-width: 2;
}

:deep(.vue-flow__edge-path) {
  stroke: #c0c4cc;
  stroke-width: 2;
}

:deep(.vue-flow__edge-textbg) {
  fill: #ffffff;
}

:deep(.vue-flow__edge-text) {
  fill: #606266;
  font-size: 10px;
}

:deep(.vue-flow__controls) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

:deep(.vue-flow__controls-button) {
  background: #ffffff;
  border: 1px solid #e4e7ed;
}

:deep(.vue-flow__minimap) {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}
</style>