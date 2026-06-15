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
          <span class="loading-title">Loading Threat Detection</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">AI-Powered Threat Detection & Analysis System</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="threat-detection-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Threat Detection</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>Threat Detection</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runThreatScan">
          <el-icon><Refresh /></el-icon>
          Run Threat Scan
        </el-button>
        <el-button type="success" plain @click="exportThreatReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="info" plain @click="configureDetection">
          <el-icon><Setting /></el-icon>
          Configure
        </el-button>
      </div>
    </div>

    <!-- Threat Detection Status -->
    <div class="status-section">
      <el-card class="status-card" shadow="hover">
        <div class="status-grid">
          <div class="status-item">
            <div class="status-label">Detection Engine</div>
            <div class="status-value">{{ detectionEngine }}</div>
            <el-tag type="success" size="small">Active</el-tag>
          </div>
          <div class="status-item">
            <div class="status-label">Threats Detected (24h)</div>
            <div class="status-value critical">{{ totalThreats }}</div>
            <div class="status-trend" :class="threatTrend > 0 ? 'up' : 'down'">
              {{ threatTrend > 0 ? '+' : '' }}{{ threatTrend }}% vs yesterday
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">Detection Accuracy</div>
            <div class="status-value">{{ detectionAccuracy }}%</div>
            <el-progress :percentage="detectionAccuracy" :stroke-width="6" :color="getAccuracyColor(detectionAccuracy)" style="width: 100px" />
          </div>
          <div class="status-item">
            <div class="status-label">False Positive Rate</div>
            <div class="status-value">{{ falsePositiveRate }}%</div>
            <div class="status-trend down">↓ 2.1% from last week</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Real-time Threat Detection Charts -->
    <div class="detection-row">
      <!-- Real-time Threat Score -->
      <el-card class="threat-score-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Real-time Threat Score</span>
            <div class="score-indicator" :class="getThreatLevelClass(currentThreatScore)">
              {{ getThreatLevel(currentThreatScore) }}
            </div>
          </div>
        </template>
        <div ref="threatGaugeRef" class="threat-gauge"></div>
        <div class="threat-description">{{ threatDescription }}</div>
      </el-card>

      <!-- Threat Detection Timeline -->
      <el-card class="detection-timeline-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Clock /></el-icon> Threat Detection Timeline</span>
            <el-select v-model="timelineRange" size="small" style="width: 100px">
              <el-option label="6h" value="6h" />
              <el-option label="12h" value="12h" />
              <el-option label="24h" value="24h" />
            </el-select>
          </div>
        </template>
        <div ref="timelineChartRef" class="timeline-chart"></div>
      </el-card>
    </div>

    <!-- Detected Threats List -->
    <div class="threats-section">
      <el-card class="threats-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><WarningFilled /></el-icon> Detected Threats</span>
            <div class="threat-filters">
              <el-select v-model="threatFilter" placeholder="Severity" size="small" style="width: 120px" clearable>
                <el-option label="Critical" value="critical" />
                <el-option label="High" value="high" />
                <el-option label="Medium" value="medium" />
                <el-option label="Low" value="low" />
              </el-select>
              <el-select v-model="statusFilter" placeholder="Status" size="small" style="width: 120px" clearable>
                <el-option label="Active" value="active" />
                <el-option label="Investigating" value="investigating" />
                <el-option label="Contained" value="contained" />
                <el-option label="Resolved" value="resolved" />
              </el-select>
              <el-input v-model="searchThreat" placeholder="Search threats..." size="small" style="width: 200px" clearable />
            </div>
          </div>
        </template>
        <el-table :data="filteredThreats" stripe style="width: 100%">
          <el-table-column prop="time" label="Time" width="150" />
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity.toUpperCase() }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="Threat Name" min-width="200" />
          <el-table-column prop="type" label="Type" width="140" />
          <el-table-column prop="source" label="Source" width="160" />
          <el-table-column prop="target" label="Target" width="160" />
          <el-table-column prop="confidence" label="Confidence" width="120">
            <template #default="{ row }">
              <el-progress :percentage="row.confidence" :stroke-width="6" :format="(p) => `${p}%`" />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="120">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="140" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="investigateThreat(row)">Investigate</el-button>
              <el-button size="small" text type="danger" @click="containThreat(row)">Contain</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Threat Intelligence & Indicators -->
    <div class="intelligence-row">
      <!-- Threat Intelligence Feeds -->
      <el-card class="intel-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Connection /></el-icon> Threat Intelligence Feeds</span>
            <el-button text type="primary" @click="refreshIntel">Refresh</el-button>
          </div>
        </template>
        <div class="intel-feeds">
          <div v-for="feed in threatIntel" :key="feed.id" class="intel-item">
            <div class="intel-header">
              <span class="intel-source">{{ feed.source }}</span>
              <el-tag :type="getIntelType(feed.severity)" size="small">{{ feed.severity }}</el-tag>
            </div>
            <div class="intel-title">{{ feed.title }}</div>
            <div class="intel-description">{{ feed.description }}</div>
            <div class="intel-meta">
              <span>IOCs: {{ feed.iocs }}</span>
              <span>Published: {{ feed.published }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- Indicators of Compromise (IOCs) -->
      <el-card class="ioc-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Document /></el-icon> Indicators of Compromise (IOCs)</span>
            <el-button text type="primary" @click="addIOC">Add IOC</el-button>
          </div>
        </template>
        <el-table :data="iocs" stripe style="width: 100%">
          <el-table-column prop="type" label="Type" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="Value" min-width="200" />
          <el-table-column prop="threat" label="Associated Threat" width="160" />
          <el-table-column prop="firstSeen" label="First Seen" width="140" />
          <el-table-column prop="lastSeen" label="Last Seen" width="140" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="danger" @click="blockIOC(row)">Block</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Detection Rules & Behavioral Analytics -->
    <div class="rules-row">
      <el-card class="rules-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Setting /></el-icon> Detection Rules (Active)</span>
            <el-button text type="primary" @click="createRule">Create Rule</el-button>
          </div>
        </template>
        <div class="rules-grid">
          <div v-for="rule in detectionRules" :key="rule.id" class="rule-item">
            <div class="rule-header">
              <span class="rule-name">{{ rule.name }}</span>
              <el-switch v-model="rule.enabled" @change="toggleRule(rule)" />
            </div>
            <div class="rule-description">{{ rule.description }}</div>
            <div class="rule-meta">
              <span>Severity: <el-tag :type="getSeverityType(rule.severity)" size="small">{{ rule.severity }}</el-tag></span>
              <span>Triggered: {{ rule.triggered }} times</span>
              <span>Last Trigger: {{ rule.lastTrigger }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- AI Threat Prediction -->
    <div class="prediction-section">
      <el-card class="prediction-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Cpu /></el-icon> AI Threat Prediction (Next 24h)</span>
            <el-button text type="primary" @click="refreshPrediction">Refresh Prediction</el-button>
          </div>
        </template>
        <div ref="predictionChartRef" class="prediction-chart"></div>
        <div class="prediction-summary">
          <div class="prediction-item">
            <div class="prediction-label">Predicted Attack Vector</div>
            <div class="prediction-value">{{ predictedAttackVector }}</div>
          </div>
          <div class="prediction-item">
            <div class="prediction-label">Expected Impact</div>
            <div class="prediction-value">{{ predictedImpact }}</div>
          </div>
          <div class="prediction-item">
            <div class="prediction-label">Recommended Actions</div>
            <div class="prediction-value">{{ recommendedActions }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="runThreatHunt">
          <el-icon><Search /></el-icon>
          Threat Hunting
        </el-button>
        <el-button type="success" plain @click="generateThreatBrief">
          <el-icon><Document /></el-icon>
          Threat Brief
        </el-button>
        <el-button type="warning" plain @click="simulateAttack">
          <el-icon><Guide /></el-icon>
          Attack Simulation
        </el-button>
        <el-button type="info" plain @click="viewThreatLibrary">
          <el-icon><Reading /></el-icon>
          Threat Library
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, Setting, TrendCharts, Clock, WarningFilled,
  Connection, Document, Cpu, Search, Guide, Reading, DataAnalysis, Monitor
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing Threat Detection Engine...')

const loadingMessages = [
  'Initializing Threat Detection Engine...',
  'Loading threat intelligence feeds...',
  'Analyzing behavioral patterns...',
  'Threat detection system ready!'
]

// Detection status
const detectionEngine = ref('AI-Powered Behavioral Analysis')
const totalThreats = ref(47)
const threatTrend = ref(12)
const detectionAccuracy = ref(94)
const falsePositiveRate = ref(3.2)

// Real-time threat score
const currentThreatScore = ref(42)
const threatDescription = ref('Elevated threat level detected. Multiple suspicious activities observed from external sources.')

// Timeline range
const timelineRange = ref('24h')

// Filters
const threatFilter = ref('')
const statusFilter = ref('')
const searchThreat = ref('')

// Threats data
const threats = ref([
  { id: 1, time: '09:45:32', severity: 'critical', name: 'Ransomware Variant Detected', type: 'Malware', source: 'external-ip-45.123.45.67', target: 'File Server Cluster', confidence: 98, status: 'active' },
  { id: 2, time: '09:32:18', severity: 'high', name: 'Privilege Escalation Attempt', type: 'Access', source: 'User: jdoe', target: 'SCADA Server', confidence: 92, status: 'investigating' },
  { id: 3, time: '09:28:45', severity: 'high', name: 'C2 Communication Detected', type: 'Command & Control', source: 'internal-192.168.1.45', target: '185.142.53.12', confidence: 87, status: 'active' },
  { id: 4, time: '09:15:22', severity: 'medium', name: 'Data Exfiltration Attempt', type: 'Exfiltration', source: 'DB Server', target: 'cloud-storage-unknown', confidence: 78, status: 'contained' },
  { id: 5, time: '09:08:33', severity: 'medium', name: 'Suspicious PowerShell Execution', type: 'Script', source: 'Engineering WS-03', target: 'Local System', confidence: 72, status: 'investigating' },
  { id: 6, time: '08:55:12', severity: 'low', name: 'Port Scanning Activity', type: 'Reconnaissance', source: '203.45.67.89', target: 'DMZ Network', confidence: 65, status: 'contained' },
  { id: 7, time: '08:42:05', severity: 'critical', name: 'Zero-Day Exploit Attempt', type: 'Exploit', source: 'unknown-ip', target: 'BACnet Gateway', confidence: 95, status: 'active' },
  { id: 8, time: '08:30:44', severity: 'high', name: 'Lateral Movement Detected', type: 'Movement', source: 'WS-012', target: 'DC-01', confidence: 88, status: 'investigating' }
])

const filteredThreats = computed(() => {
  let result = threats.value
  if (threatFilter.value) {
    result = result.filter(t => t.severity === threatFilter.value)
  }
  if (statusFilter.value) {
    result = result.filter(t => t.status === statusFilter.value)
  }
  if (searchThreat.value) {
    const search = searchThreat.value.toLowerCase()
    result = result.filter(t => t.name.toLowerCase().includes(search) || t.source.toLowerCase().includes(search) || t.target.toLowerCase().includes(search))
  }
  return result
})

// Threat intelligence feeds
const threatIntel = ref([
  { id: 1, source: 'AlienVault OTX', severity: 'high', title: 'New Ransomware Family "LockBit 4.0"', description: 'New variant targeting industrial control systems with double extortion', iocs: '12 IPs, 8 Hashes', published: '1 hour ago' },
  { id: 2, source: 'CISA Alerts', severity: 'critical', title: 'Active Exploitation of BACnet Gateway CVE-2024-1234', description: 'Critical RCE vulnerability being exploited in the wild', iocs: '5 IPs, 3 Domains', published: '3 hours ago' },
  { id: 3, source: 'IBM X-Force', severity: 'medium', title: 'Phishing Campaign Targeting Engineering Departments', description: 'Spear-phishing emails with malicious attachments', iocs: '8 Hashes, 4 URLs', published: '6 hours ago' }
])

// IOCs
const iocs = ref([
  { type: 'IP', value: '45.123.45.67', threat: 'LockBit Ransomware', firstSeen: '2024-01-15', lastSeen: '2024-01-15' },
  { type: 'Domain', value: 'malicious-update[.]com', threat: 'C2 Server', firstSeen: '2024-01-14', lastSeen: '2024-01-15' },
  { type: 'Hash', value: 'a1b2c3d4e5f6...', threat: 'Ransomware Dropper', firstSeen: '2024-01-13', lastSeen: '2024-01-15' },
  { type: 'URL', value: 'http://update-service[.]net/payload', threat: 'Malware Downloader', firstSeen: '2024-01-12', lastSeen: '2024-01-15' },
  { type: 'IP', value: '185.142.53.12', threat: 'C2 Infrastructure', firstSeen: '2024-01-10', lastSeen: '2024-01-15' }
])

// Detection rules
const detectionRules = ref([
  { id: 1, name: 'SMB Brute Force Detection', description: 'Detects multiple failed SMB login attempts', severity: 'high', enabled: true, triggered: 23, lastTrigger: '09:30:15' },
  { id: 2, name: 'Ransomware File Pattern', description: 'Identifies known ransomware file extensions and behavior', severity: 'critical', enabled: true, triggered: 12, lastTrigger: '09:32:18' },
  { id: 3, name: 'C2 Domain Communication', description: 'Detects communication with known C2 domains', severity: 'high', enabled: true, triggered: 18, lastTrigger: '09:28:45' },
  { id: 4, name: 'Privilege Escalation Patterns', description: 'Identifies suspicious privilege escalation techniques', severity: 'high', enabled: true, triggered: 8, lastTrigger: '09:15:22' },
  { id: 5, name: 'Data Exfiltration Threshold', description: 'Alerts on large outbound data transfers', severity: 'medium', enabled: false, triggered: 4, lastTrigger: '08:45:00' }
])

// AI predictions
const predictedAttackVector = ref('Ransomware via Phishing')
const predictedImpact = ref('Critical - Potential data encryption and exfiltration')
const recommendedActions = ref('Update EDR signatures, block known IOCs, enable MFA')

// Chart refs
const threatGaugeRef = ref<HTMLElement>()
const timelineChartRef = ref<HTMLElement>()
const predictionChartRef = ref<HTMLElement>()

let threatGauge: echarts.ECharts | null = null
let timelineChart: echarts.ECharts | null = null
let predictionChart: echarts.ECharts | null = null
let scoreInterval: number

// Helper functions
const getThreatLevelClass = (score: number) => {
  if (score >= 70) return 'critical'
  if (score >= 40) return 'elevated'
  if (score >= 20) return 'guarded'
  return 'normal'
}

const getThreatLevel = (score: number) => {
  if (score >= 70) return 'CRITICAL'
  if (score >= 40) return 'ELEVATED'
  if (score >= 20) return 'GUARDED'
  return 'NORMAL'
}

const getAccuracyColor = (score: number) => {
  if (score >= 90) return '#10b981'
  if (score >= 80) return '#3b82f6'
  return '#f59e0b'
}

const getSeverityType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'active': return 'danger'
    case 'investigating': return 'warning'
    case 'contained': return 'primary'
    default: return 'success'
  }
}

const getIntelType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    default: return 'info'
  }
}

// Initialize threat gauge chart
const initThreatGauge = () => {
  if (!threatGaugeRef.value) return
  threatGauge = echarts.init(threatGaugeRef.value)
  const option = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      radius: '80%',
      center: ['50%', '55%'],
      progress: { show: true, width: 18, itemStyle: { color: getScoreColor(currentThreatScore.value) } },
      axisLine: { lineStyle: { width: 18, color: [[0.3, '#10b981'],[0.6, '#f59e0b'],[1, '#ef4444']] } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { show: false },
      title: { show: false }
    }]
  }
  threatGauge.setOption(option)
}

const getScoreColor = (score: number) => {
  if (score >= 70) return '#ef4444'
  if (score >= 40) return '#f59e0b'
  return '#10b981'
}

// Initialize timeline chart
const initTimelineChart = () => {
  if (!timelineChartRef.value) return
  timelineChart = echarts.init(timelineChartRef.value)
  updateTimelineChart()
}

const updateTimelineChart = () => {
  if (!timelineChart) return
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Critical', 'High', 'Medium', 'Low'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: getTimeLabels() },
    yAxis: { type: 'value', name: 'Number of Threats' },
    series: [
      { name: 'Critical', type: 'bar', data: [2, 1, 3, 2, 4, 1, 2], itemStyle: { color: '#ef4444', borderRadius: [4, 4, 0, 0] } },
      { name: 'High', type: 'bar', data: [3, 4, 2, 5, 3, 4, 2], itemStyle: { color: '#f59e0b', borderRadius: [4, 4, 0, 0] } },
      { name: 'Medium', type: 'bar', data: [5, 6, 4, 7, 5, 6, 4], itemStyle: { color: '#eab308', borderRadius: [4, 4, 0, 0] } },
      { name: 'Low', type: 'bar', data: [8, 7, 6, 9, 7, 8, 6], itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] } }
    ]
  }
  timelineChart.setOption(option)
}

const getTimeLabels = () => {
  if (timelineRange.value === '6h') return ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00']
  if (timelineRange.value === '12h') return ['03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']
  return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
}

// Initialize prediction chart
const initPredictionChart = () => {
  if (!predictionChartRef.value) return
  predictionChart = echarts.init(predictionChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Historical Average', 'Predicted'] },
    xAxis: { type: 'category', data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'] },
    yAxis: { type: 'value', name: 'Threat Probability (%)' },
    series: [
      { name: 'Historical Average', type: 'line', data: [15, 12, 18, 35, 42, 38, 25], lineStyle: { color: '#94a3b8', width: 2 }, smooth: true },
      { name: 'Predicted', type: 'line', data: [18, 15, 25, 45, 58, 48, 30], lineStyle: { color: '#ef4444', width: 3 }, smooth: true, areaStyle: { opacity: 0.2, color: '#ef4444' } }
    ]
  }
  predictionChart.setOption(option)
}

// Simulate real-time threat score updates
const simulateThreatScore = () => {
  currentThreatScore.value = Math.floor(Math.random() * 60) + 20
  if (threatGauge) {
    threatGauge.setOption({
      series: [{
        progress: { itemStyle: { color: getScoreColor(currentThreatScore.value) } }
      }]
    })
  }

  if (currentThreatScore.value >= 70) threatDescription.value = 'CRITICAL: Active threat campaign detected. Immediate action required.'
  else if (currentThreatScore.value >= 40) threatDescription.value = 'Elevated threat level detected. Multiple suspicious activities observed from external sources.'
  else if (currentThreatScore.value >= 20) threatDescription.value = 'Guarded: Normal threat activity with occasional anomalies.'
  else threatDescription.value = 'Normal: Baseline threat activity. No immediate concerns.'
}

// Event handlers
const runThreatScan = () => {
  ElMessage.info('Initiating full system threat scan...')
  setTimeout(() => {
    const newThreats = Math.floor(Math.random() * 5)
    ElMessage.success(`Threat scan completed. ${newThreats} new threats detected.`)
  }, 5000)
}

const exportThreatReport = () => {
  ElMessage.info('Generating threat detection report...')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 2000)
}

const configureDetection = () => {
  ElMessage.info('Opening threat detection configuration')
}

const investigateThreat = (threat: any) => {
  ElMessageBox.alert(
      `Threat: ${threat.name}\nType: ${threat.type}\nSource: ${threat.source}\nTarget: ${threat.target}\nConfidence: ${threat.confidence}%\nStatus: ${threat.status}\n\nRecommended Action: Isolate affected systems and initiate incident response.`,
      'Threat Investigation',
      { confirmButtonText: 'OK', type: 'warning' }
  )
}

const containThreat = (threat: any) => {
  ElMessageBox.confirm(`Initiate containment for ${threat.name}? This will isolate affected systems.`, 'Contain Threat', {
    confirmButtonText: 'Contain',
    cancelButtonText: 'Cancel',
    type: 'danger'
  }).then(() => {
    threat.status = 'contained'
    ElMessage.success(`Threat contained: ${threat.name}`)
  }).catch(() => {})
}

const refreshIntel = () => {
  ElMessage.info('Refreshing threat intelligence feeds...')
  setTimeout(() => {
    ElMessage.success('Threat intelligence updated')
  }, 2000)
}

const addIOC = () => {
  ElMessage.info('Add IOC dialog opened')
}

const blockIOC = (ioc: any) => {
  ElMessageBox.confirm(`Block ${ioc.type}: ${ioc.value}?`, 'Block Indicator', {
    confirmButtonText: 'Block',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.success(`${ioc.type} ${ioc.value} has been blocked`)
  }).catch(() => {})
}

const createRule = () => {
  ElMessage.info('Create detection rule dialog opened')
}

const toggleRule = (rule: any) => {
  ElMessage.success(`Rule ${rule.name} ${rule.enabled ? 'enabled' : 'disabled'}`)
}

const refreshPrediction = () => {
  ElMessage.info('Refreshing AI threat prediction...')
  setTimeout(() => {
    ElMessage.success('Prediction updated')
  }, 2000)
}

const runThreatHunt = () => {
  ElMessage.info('Initiating proactive threat hunting...')
  setTimeout(() => {
    ElMessage.success('Threat hunt completed. No hidden threats detected.')
  }, 8000)
}

const generateThreatBrief = () => {
  ElMessage.info('Generating threat brief...')
}

const simulateAttack = () => {
  ElMessageBox.confirm('Run attack simulation to test detection capabilities?', 'Attack Simulation', {
    confirmButtonText: 'Run',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    ElMessage.warning('Attack simulation started. Monitoring detection response...')
    setTimeout(() => {
      ElMessage.success('Attack simulation completed. Detection systems responded correctly.')
    }, 5000)
  }).catch(() => {})
}

const viewThreatLibrary = () => {
  ElMessage.info('Opening threat library')
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
      setTimeout(() => {
        initThreatGauge()
        initTimelineChart()
        initPredictionChart()
        scoreInterval = setInterval(simulateThreatScore, 10000)
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (scoreInterval) clearInterval(scoreInterval)
  if (threatGauge) threatGauge.dispose()
  if (timelineChart) timelineChart.dispose()
  if (predictionChart) predictionChart.dispose()
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

/* ==================== Main Content - White Background ==================== */
.threat-detection-container {
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
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.status-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.status-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.status-value.critical { color: #ef4444; }

.status-trend {
  font-size: 11px;
  margin-top: 4px;
}

.status-trend.up { color: #ef4444; }
.status-trend.down { color: #10b981; }

/* Detection Row */
.detection-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  margin-bottom: 24px;
}

.threat-score-card,
.detection-timeline-card {
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.score-indicator {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.score-indicator.critical { background: #ef444420; color: #ef4444; }
.score-indicator.elevated { background: #f59e0b20; color: #f59e0b; }
.score-indicator.guarded { background: #eab30820; color: #eab308; }
.score-indicator.normal { background: #10b98120; color: #10b981; }

.threat-gauge {
  height: 220px;
  width: 100%;
}

.threat-description {
  text-align: center;
  font-size: 13px;
  color: #64748b;
  margin-top: 8px;
}

.timeline-chart {
  height: 320px;
  width: 100%;
}

/* Threats Section */
.threats-section {
  margin-bottom: 24px;
}

.threats-card {
  border-radius: 12px;
}

.threat-filters {
  display: flex;
  gap: 12px;
}

/* Intelligence Row */
.intelligence-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.intel-card,
.ioc-card {
  border-radius: 12px;
}

.intel-feeds {
  max-height: 400px;
  overflow-y: auto;
}

.intel-item {
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.intel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.intel-source {
  font-weight: 600;
  color: #1e293b;
}

.intel-title {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 8px;
}

.intel-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.intel-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #94a3b8;
}

/* Rules Row */
.rules-row {
  margin-bottom: 24px;
}

.rules-card {
  border-radius: 12px;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.rule-item {
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.rule-name {
  font-weight: 600;
  color: #1e293b;
}

.rule-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
}

.rule-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: #94a3b8;
}

/* Prediction Section */
.prediction-section {
  margin-bottom: 24px;
}

.prediction-card {
  border-radius: 12px;
}

.prediction-chart {
  height: 280px;
  width: 100%;
}

.prediction-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.prediction-item {
  text-align: center;
}

.prediction-label {
  font-size: 11px;
  color: #64748b;
  margin-bottom: 4px;
}

.prediction-value {
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
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
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .detection-row {
    grid-template-columns: 1fr;
  }

  .intelligence-row,
  .rules-grid {
    grid-template-columns: 1fr;
  }

  .prediction-summary {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .threat-filters {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>