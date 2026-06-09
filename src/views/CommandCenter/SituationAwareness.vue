<template>
  <div class="situation-awareness-container">
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
            <span class="loading-title">Loading Situation Awareness</span>
            <span class="loading-dots"><span>.</span><span>.</span><span>.</span></span>
          </div>
          <div class="loading-progress">
            <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
          </div>
          <div class="loading-tip">Situational Awareness & Command Center</div>
          <div class="loading-subtip">{{ loadingMessage }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="sa-main">
      <!-- Page Header -->
      <div class="page-header">
        <div>
          <h1 class="page-title">Situation Awareness</h1>
          <p class="page-subtitle">Real-time situational monitoring, threat detection, and incident response</p>
        </div>
        <div class="header-actions">
          <div class="time-display">
            <el-icon><Clock /></el-icon>
            <span>{{ currentTime }}</span>
          </div>
          <el-button type="primary" @click="refreshSituation">
            <el-icon><Refresh /></el-icon>
            Refresh
          </el-button>
          <el-button @click="exportReport">
            <el-icon><Download /></el-icon>
            Export Report
          </el-button>
          <el-button @click="openCommandCenter">
            <el-icon><Monitor /></el-icon>
            Command Center
          </el-button>
        </div>
      </div>

      <!-- Overall Situation Status Banner -->
      <div class="situation-banner" :class="overallSituationClass">
        <div class="banner-left">
          <div class="situation-icon">
            <el-icon><component :is="overallSituationIcon" /></el-icon>
          </div>
          <div class="situation-info">
            <div class="situation-title">{{ overallSituationTitle }}</div>
            <div class="situation-description">{{ overallSituationDescription }}</div>
          </div>
        </div>
        <div class="banner-right">
          <div class="situation-metric">
            <span class="metric-label">Confidence Level</span>
            <span class="metric-value">{{ confidenceLevel }}%</span>
          </div>
          <div class="situation-metric">
            <span class="metric-label">Last Update</span>
            <span class="metric-value">{{ lastUpdateTime }}</span>
          </div>
          <div class="situation-metric">
            <span class="metric-label">Active Threats</span>
            <span class="metric-value threat">{{ activeThreats }}</span>
          </div>
        </div>
      </div>

      <!-- Key Metrics Row -->
      <el-row :gutter="20" class="metrics-row">
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">Incident Severity Index</span>
              <el-tooltip content="Overall incident severity score" placement="top">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <div class="metric-value severity">{{ incidentSeverityIndex }}</div>
            <div class="metric-trend up">+{{ severityTrend }} from yesterday</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">Response Readiness</span>
              <el-tooltip content="Current response capability score" placement="top">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <div class="metric-value readiness">{{ responseReadiness }}%</div>
            <el-progress :percentage="responseReadiness" :stroke-width="6" :color="getReadinessColor(responseReadiness)" />
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">Mean Time to Detect</span>
              <el-tooltip content="Average time to detect incidents" placement="top">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <div class="metric-value mttd">{{ mttd }}s</div>
            <div class="metric-trend down">-{{ mttdTrend }}s improvement</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-title">Mean Time to Respond</span>
              <el-tooltip content="Average time to respond to incidents" placement="top">
                <el-icon><InfoFilled /></el-icon>
              </el-tooltip>
            </div>
            <div class="metric-value mttr">{{ mttr }}min</div>
            <div class="metric-trend down">-{{ mttrTrend }}min improvement</div>
          </div>
        </el-col>
      </el-row>

      <!-- Main Grid -->
      <el-row :gutter="20" class="dashboard-grid">
        <!-- Real-time Threat Map -->
        <el-col :span="14">
          <el-card class="threat-map-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Location /></el-icon>
                  <span>Real-time Threat Map</span>
                </div>
                <div class="card-controls">
                  <el-radio-group v-model="mapViewMode" size="small">
                    <el-radio-button label="threats">Threats</el-radio-button>
                    <el-radio-button label="incidents">Incidents</el-radio-button>
                    <el-radio-button label="resources">Resources</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
            </template>
            <div class="threat-map-container">
              <div ref="threatMapCanvas" class="threat-map-canvas">
                <!-- Map Grid -->
                <div class="map-grid-bg">
                  <div v-for="i in 16" :key="'h-' + i" class="grid-line horizontal" :style="{ top: (i * 6.25) + '%' }"></div>
                  <div v-for="i in 16" :key="'v-' + i" class="grid-line vertical" :style="{ left: (i * 6.25) + '%' }"></div>
                </div>

                <!-- Facility Zones -->
                <div class="facility-zones">
                  <div class="zone" :style="{ left: '10%', top: '20%', width: '25%', height: '30%' }">
                    <div class="zone-label">Data Center East</div>
                    <div class="zone-status critical"></div>
                  </div>
                  <div class="zone" :style="{ left: '40%', top: '15%', width: '20%', height: '25%' }">
                    <div class="zone-label">Data Center West</div>
                    <div class="zone-status warning"></div>
                  </div>
                  <div class="zone" :style="{ left: '65%', top: '25%', width: '25%', height: '20%' }">
                    <div class="zone-label">Office Tower</div>
                    <div class="zone-status healthy"></div>
                  </div>
                  <div class="zone" :style="{ left: '15%', top: '55%', width: '30%', height: '25%' }">
                    <div class="zone-label">Cooling Plant</div>
                    <div class="zone-status critical"></div>
                  </div>
                  <div class="zone" :style="{ left: '55%', top: '50%', width: '35%', height: '30%' }">
                    <div class="zone-label">Backup Facility</div>
                    <div class="zone-status warning"></div>
                  </div>
                </div>

                <!-- Threat Markers -->
                <div v-for="threat in activeThreatsList" :key="threat.id" class="threat-marker" :style="{ left: threat.x + '%', top: threat.y + '%' }">
                  <div class="threat-pulse" :class="threat.severity"></div>
                  <div class="threat-icon" :class="threat.severity">
                    <el-icon><WarningFilled /></el-icon>
                  </div>
                  <div class="threat-popup" v-show="selectedThreatId === threat.id">
                    <div class="popup-header">
                      <span class="popup-title">{{ threat.title }}</span>
                      <el-button link @click="selectedThreatId = null"><el-icon><Close /></el-icon></el-button>
                    </div>
                    <div class="popup-content">
                      <div class="popup-row"><span>Severity:</span><el-tag :type="getSeverityTagType(threat.severity)" size="small">{{ threat.severity }}</el-tag></div>
                      <div class="popup-row"><span>Location:</span>{{ threat.location }}</div>
                      <div class="popup-row"><span>Detected:</span>{{ threat.detectedTime }}</div>
                      <div class="popup-row"><span>Status:</span>{{ threat.status }}</div>
                    </div>
                    <div class="popup-actions">
                      <el-button size="small" @click="investigateThreat(threat)">Investigate</el-button>
                      <el-button size="small" type="primary" @click="respondToThreat(threat)">Respond</el-button>
                    </div>
                  </div>
                </div>

                <!-- Resource Markers -->
                <div v-for="resource in activeResources" :key="resource.id" class="resource-marker" :style="{ left: resource.x + '%', top: resource.y + '%' }">
                  <div class="resource-icon" :style="{ background: resource.color }">
                    <el-icon><User /></el-icon>
                  </div>
                  <div class="resource-label">{{ resource.name }}</div>
                </div>

                <!-- Heatmap Overlay -->
                <div class="heatmap-overlay" v-if="showHeatmap">
                  <div v-for="i in 20" :key="i" class="heatmap-cell" :style="{ left: ((i-1)*5)+'%', top: '0', width: '5%', height: '100%', background: `rgba(239, 68, 68, ${Math.random() * 0.3})` }"></div>
                </div>
              </div>
              <div class="map-legend">
                <div class="legend-item"><span class="legend-dot critical"></span>Critical Threat</div>
                <div class="legend-item"><span class="legend-dot warning"></span>Warning</div>
                <div class="legend-item"><span class="legend-dot healthy"></span>Healthy</div>
                <div class="legend-item"><span class="legend-dot resource"></span>Resource</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Incident Timeline & Alerts -->
        <el-col :span="10">
          <el-card class="incident-timeline-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><List /></el-icon>
                  <span>Incident Timeline</span>
                </div>
                <el-button link @click="viewAllIncidents">View All →</el-button>
              </div>
            </template>
            <div class="timeline-container">
              <div class="timeline-line"></div>
              <div v-for="incident in incidentTimeline" :key="incident.id" class="timeline-item" :class="incident.type">
                <div class="timeline-dot" :class="incident.severity"></div>
                <div class="timeline-content">
                  <div class="timeline-header">
                    <span class="timeline-title">{{ incident.title }}</span>
                    <span class="timeline-time">{{ incident.time }}</span>
                  </div>
                  <div class="timeline-description">{{ incident.description }}</div>
                  <div class="timeline-footer">
                    <span class="timeline-location"><el-icon><Location /></el-icon> {{ incident.location }}</span>
                    <span class="timeline-assignee"><el-icon><User /></el-icon> {{ incident.assignee }}</span>
                  </div>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Second Row -->
      <el-row :gutter="20" class="dashboard-grid">
        <!-- Threat Intelligence Feed -->
        <el-col :span="8">
          <el-card class="threat-intel-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><Lock /></el-icon>
                  <span>Threat Intelligence Feed</span>
                </div>
                <el-badge :value="newIntelCount" class="item" v-if="newIntelCount > 0">
                  <el-button link>New</el-button>
                </el-badge>
              </div>
            </template>
            <div class="intel-feed">
              <div v-for="intel in threatIntel" :key="intel.id" class="intel-item" :class="{ unread: !intel.read }">
                <div class="intel-icon" :class="intel.type">
                  <el-icon><component :is="getIntelIcon(intel.type)" /></el-icon>
                </div>
                <div class="intel-content">
                  <div class="intel-title">{{ intel.title }}</div>
                  <div class="intel-source">{{ intel.source }} • {{ intel.time }}</div>
                </div>
                <div class="intel-severity" :class="intel.severity">{{ intel.severity }}</div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Resource Status -->
        <el-col :span="8">
          <el-card class="resource-status-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><UserFilled /></el-icon>
                  <span>Resource Status</span>
                </div>
                <el-button link @click="viewResources">Manage →</el-button>
              </div>
            </template>
            <div class="resource-grid">
              <div v-for="team in responseTeams" :key="team.id" class="team-card">
                <div class="team-header">
                  <span class="team-name">{{ team.name }}</span>
                  <el-tag :type="getTeamStatusTag(team.status)" size="small">{{ team.status }}</el-tag>
                </div>
                <div class="team-members">
                  <div v-for="member in team.members" :key="member.id" class="member-item">
                    <div class="member-avatar" :style="{ background: member.color }">
                      <span>{{ member.initials }}</span>
                    </div>
                    <div class="member-info">
                      <span class="member-name">{{ member.name }}</span>
                      <span class="member-role">{{ member.role }}</span>
                    </div>
                    <div class="member-status" :class="member.status"></div>
                  </div>
                </div>
                <div class="team-footer">
                  <span>ETA: {{ team.eta }}</span>
                  <el-button size="small" @click="contactTeam(team)">Contact</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Predictive Analytics -->
        <el-col :span="8">
          <el-card class="predictive-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><TrendCharts /></el-icon>
                  <span>Predictive Analytics</span>
                </div>
                <el-tag type="info" size="small">AI Powered</el-tag>
              </div>
            </template>
            <div class="predictive-content">
              <div class="prediction-item" v-for="prediction in predictions" :key="prediction.id">
                <div class="prediction-header">
                  <span class="prediction-title">{{ prediction.title }}</span>
                  <span class="prediction-probability" :class="getProbabilityClass(prediction.probability)">
                    {{ prediction.probability }}% probability
                  </span>
                </div>
                <div class="prediction-bar">
                  <div class="prediction-progress" :style="{ width: prediction.probability + '%', background: getProbabilityColor(prediction.probability) }"></div>
                </div>
                <div class="prediction-time">{{ prediction.expectedTime }}</div>
              </div>
            </div>
            <div class="ai-insight">
              <div class="insight-header">
                <el-icon><Cpu /></el-icon>
                <span>AI Insight</span>
              </div>
              <p>{{ aiInsight }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Third Row - Communication & Decision Support -->
      <el-row :gutter="20" class="dashboard-grid">
        <el-col :span="12">
          <el-card class="communication-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><ChatDotRound /></el-icon>
                  <span>Emergency Communication</span>
                </div>
                <el-button type="primary" size="small" @click="broadcastMessage">
                  <el-icon><Bell /></el-icon>
                  Broadcast
                </el-button>
              </div>
            </template>
            <div class="chat-messages">
              <div v-for="msg in chatMessages" :key="msg.id" class="chat-message" :class="msg.type">
                <div class="message-avatar">
                  <el-icon><User /></el-icon>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="message-sender">{{ msg.sender }}</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-text">{{ msg.text }}</div>
                </div>
              </div>
            </div>
            <div class="chat-input">
              <el-input v-model="newMessage" placeholder="Type a message..." @keyup.enter="sendMessage">
                <template #append>
                  <el-button @click="sendMessage">Send</el-button>
                </template>
              </el-input>
            </div>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card class="decision-support-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div class="card-title">
                  <el-icon><DocumentChecked /></el-icon>
                  <span>Decision Support</span>
                </div>
              </div>
            </template>
            <div class="decision-list">
              <div v-for="decision in decisions" :key="decision.id" class="decision-item">
                <div class="decision-icon" :class="decision.type">
                  <el-icon><component :is="decision.icon" /></el-icon>
                </div>
                <div class="decision-content">
                  <div class="decision-title">{{ decision.title }}</div>
                  <div class="decision-description">{{ decision.description }}</div>
                </div>
                <div class="decision-actions">
                  <el-button size="small" @click="executeDecision(decision)">Execute</el-button>
                  <el-button size="small" type="primary" @click="reviewDecision(decision)">Review</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <el-button type="danger" size="large" @click="activateEmergencyProtocol">
          <el-icon><WarningFilled /></el-icon>
          Activate Emergency Protocol
        </el-button>
        <el-button type="primary" size="large" @click="generateSituationReport">
          <el-icon><Document /></el-icon>
          Generate Situation Report
        </el-button>
        <el-button size="large" @click="scheduleBriefing">
          <el-icon><VideoCamera /></el-icon>
          Schedule Briefing
        </el-button>
      </div>
    </div>

    <!-- Incident Detail Dialog -->
    <el-dialog v-model="incidentDialogVisible" :title="selectedIncident?.title" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Severity">
          <el-tag :type="getSeverityTagType(selectedIncident?.severity)">{{ selectedIncident?.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Status">{{ selectedIncident?.status }}</el-descriptions-item>
        <el-descriptions-item label="Location">{{ selectedIncident?.location }}</el-descriptions-item>
        <el-descriptions-item label="Detected">{{ selectedIncident?.detectedTime }}</el-descriptions-item>
        <el-descriptions-item label="Assignee">{{ selectedIncident?.assignee }}</el-descriptions-item>
        <el-descriptions-item label="ETA">{{ selectedIncident?.eta }}</el-descriptions-item>
        <el-descriptions-item label="Description" :span="2">{{ selectedIncident?.description }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="incidentDialogVisible = false">Close</el-button>
        <el-button type="primary" @click="assignIncident(selectedIncident)">Assign Team</el-button>
        <el-button type="danger" @click="escalateIncident(selectedIncident)">Escalate</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import {
  Clock, Refresh, Download, Monitor, Location, InfoFilled, WarningFilled,
  List, User, Lock, UserFilled, TrendCharts, Cpu, ChatDotRound, Bell,
  DocumentChecked, Document, VideoCamera, Close, Plus, Setting, Search,
  DataLine, PieChart, Connection, SuccessFilled, CircleCheck, CircleClose
} from '@element-plus/icons-vue'

// ==================== Loading State ====================
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing situation awareness...')

// ==================== Time ====================
const currentTime = ref('')
const lastUpdateTime = ref('')
let timeInterval: ReturnType<typeof setInterval> | null = null

// ==================== Situation State ====================
const mapViewMode = ref('threats')
const showHeatmap = ref(false)
const selectedThreatId = ref<number | null>(null)
const incidentDialogVisible = ref(false)
const selectedIncident = ref<any>(null)
const newMessage = ref('')
const newIntelCount = ref(3)

// Overall Situation
const overallSituationClass = computed(() => {
  if (activeThreats.value > 3) return 'critical'
  if (activeThreats.value > 0) return 'warning'
  return 'normal'
})

const overallSituationIcon = computed(() => {
  if (activeThreats.value > 3) return 'CircleClose'
  if (activeThreats.value > 0) return 'WarningFilled'
  return 'SuccessFilled'
})

const overallSituationTitle = computed(() => {
  if (activeThreats.value > 3) return 'Critical Situation - Multiple Threats Detected'
  if (activeThreats.value > 0) return 'Elevated Alert - Active Threats Present'
  return 'All Clear - Normal Operations'
})

const overallSituationDescription = computed(() => {
  if (activeThreats.value > 3) return `${activeThreats.value} active threats require immediate attention`
  if (activeThreats.value > 0) return `${activeThreats.value} active threats being monitored`
  return 'No active threats detected. Systems operational.'
})

// Metrics
const activeThreats = ref(4)
const incidentSeverityIndex = ref(72)
const severityTrend = ref(8)
const responseReadiness = ref(85)
const mttd = ref(45)
const mttdTrend = ref(12)
const mttr = ref(18)
const mttrTrend = ref(5)
const confidenceLevel = ref(94)

// Active Threats List
const activeThreatsList = ref([
  { id: 1, title: 'Cooling System Failure', severity: 'critical', location: 'Data Center East', detectedTime: '08:23:45', status: 'Investigating', x: 22, y: 32 },
  { id: 2, title: 'Power Fluctuation Detected', severity: 'critical', location: 'Cooling Plant', detectedTime: '08:15:22', status: 'Response Deployed', x: 28, y: 68 },
  { id: 3, title: 'Unauthorized Access Attempt', severity: 'warning', location: 'Office Tower - Floor 3', detectedTime: '08:42:10', status: 'Contained', x: 72, y: 32 },
  { id: 4, title: 'Network Anomaly', severity: 'warning', location: 'Data Center West', detectedTime: '08:05:33', status: 'Monitoring', x: 48, y: 25 }
])

// Active Resources
const activeResources = ref([
  { id: 1, name: 'Team Alpha', x: 35, y: 45, color: '#3b82f6' },
  { id: 2, name: 'Team Bravo', x: 65, y: 55, color: '#10b981' },
  { id: 3, name: 'EMT Unit', x: 45, y: 70, color: '#ef4444' }
])

// Incident Timeline
const incidentTimeline = ref([
  { id: 1, title: 'Cooling System Critical Alert', description: 'Temperature spike detected in Data Center East', location: 'DC East - Floor 2', time: '08:23:45', severity: 'critical', type: 'alert', assignee: 'John Smith', status: 'investigating' },
  { id: 2, title: 'Power Quality Issue', description: 'Voltage fluctuation detected at UPS input', location: 'Cooling Plant', time: '08:15:22', severity: 'critical', type: 'alert', assignee: 'Sarah Chen', status: 'responding' },
  { id: 3, title: 'Security Breach Attempt', description: 'Multiple failed access attempts', location: 'Office Tower', time: '08:42:10', severity: 'warning', type: 'security', assignee: 'Mike Johnson', status: 'resolved' },
  { id: 4, title: 'Network Latency Spike', description: 'Unexpected latency increase on backbone', location: 'Network Room', time: '08:05:33', severity: 'warning', type: 'alert', assignee: 'Lisa Wong', status: 'monitoring' },
  { id: 5, title: 'Fire Alarm Test', description: 'Scheduled system test completed', location: 'All Facilities', time: '07:30:00', severity: 'info', type: 'info', assignee: 'System', status: 'completed' }
])

// Threat Intelligence
const threatIntel = ref([
  { id: 1, title: 'New Ransomware Variant Targeting ICS Systems', source: 'CISA Alert', time: '5 min ago', severity: 'critical', type: 'malware', read: false },
  { id: 2, title: 'APT Group Activity in Southeast Asia', source: 'Mandiant', time: '15 min ago', severity: 'high', type: 'apt', read: false },
  { id: 3, title: 'Vulnerability in Popular HVAC Controllers', source: 'NIST', time: '1 hour ago', severity: 'medium', type: 'vulnerability', read: false },
  { id: 4, title: 'Weather Alert: Storm Approaching', source: 'National Weather', time: '2 hours ago', severity: 'low', type: 'weather', read: true },
  { id: 5, title: 'Phishing Campaign Targeting Facility Managers', source: 'Security Vendor', time: '3 hours ago', severity: 'medium', type: 'phishing', read: true }
])

// Response Teams
const responseTeams = ref([
  { id: 1, name: 'Emergency Response Team', status: 'deployed', eta: '5 min', members: [
      { id: 1, name: 'John Smith', role: 'Team Lead', initials: 'JS', status: 'active', color: '#3b82f6' },
      { id: 2, name: 'Sarah Chen', role: 'HVAC Specialist', initials: 'SC', status: 'active', color: '#10b981' },
      { id: 3, name: 'Mike Johnson', role: 'Electrical', initials: 'MJ', status: 'en-route', color: '#f59e0b' }
    ] },
  { id: 2, name: 'Security Response Unit', status: 'standby', eta: '15 min', members: [
      { id: 1, name: 'Lisa Wong', role: 'Security Lead', initials: 'LW', status: 'active', color: '#8b5cf6' },
      { id: 2, name: 'David Kim', role: 'Analyst', initials: 'DK', status: 'standby', color: '#6b7280' }
    ] }
])

// Predictions
const predictions = ref([
  { id: 1, title: 'Cooling System Failure Risk', probability: 78, expectedTime: 'Next 2 hours', trend: 'up' },
  { id: 2, title: 'Power Grid Instability', probability: 45, expectedTime: 'Next 6 hours', trend: 'down' },
  { id: 3, title: 'Security Breach Probability', probability: 62, expectedTime: 'Next 4 hours', trend: 'up' },
  { id: 4, title: 'Network Congestion Risk', probability: 34, expectedTime: 'Next 12 hours', trend: 'down' }
])

const aiInsight = ref('Based on historical data and current telemetry, there is a 78% probability of cooling system failure in DC East within the next 2 hours. Recommend proactive maintenance and resource pre-positioning.')

// Chat Messages
const chatMessages = ref([
  { id: 1, sender: 'John Smith (ERT Lead)', text: 'Arriving at DC East now. Initial assessment shows chiller pump failure.', time: '08:25:32', type: 'team' },
  { id: 2, sender: 'Sarah Chen', text: 'Spare parts available at warehouse. ETA 10 minutes.', time: '08:26:15', type: 'team' },
  { id: 3, sender: 'Command Center', text: 'Roger. Coordinate with facility manager for access.', time: '08:27:00', type: 'system' },
  { id: 4, sender: 'Mike Johnson', text: 'Power backup engaged. No disruption to critical loads.', time: '08:28:45', type: 'team' }
])

// Decisions
const decisions = ref([
  { id: 1, title: 'Evacuation Recommendation', description: 'Data Center East cooling failure may require evacuation if not resolved', type: 'urgent', icon: 'WarningFilled' },
  { id: 2, title: 'Resource Allocation', description: 'Additional HVAC technicians recommended for rapid response', type: 'recommendation', icon: 'UserFilled' },
  { id: 3, title: 'Communication Protocol', description: 'Notify stakeholders of potential service impact', type: 'action', icon: 'Bell' }
])

// Helper Functions
const getSeverityTagType = (severity: string) => {
  const types: Record<string, string> = {
    critical: 'danger',
    high: 'danger',
    warning: 'warning',
    medium: 'warning',
    low: 'info',
    info: 'info'
  }
  return types[severity] || 'info'
}

const getReadinessColor = (score: number) => {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#f59e0b'
  return '#ef4444'
}

const getTeamStatusTag = (status: string) => {
  const types: Record<string, string> = {
    deployed: 'danger',
    standby: 'warning',
    available: 'success'
  }
  return types[status] || 'info'
}

const getIntelIcon = (type: string) => {
  const icons: Record<string, string> = {
    malware: 'WarningFilled',
    apt: 'Lock',
    vulnerability: 'WarningFilled',
    weather: 'Cloudy',
    phishing: 'Message'
  }
  return icons[type] || 'InfoFilled'
}

const getProbabilityClass = (probability: number) => {
  if (probability >= 70) return 'high'
  if (probability >= 50) return 'medium'
  return 'low'
}

const getProbabilityColor = (probability: number) => {
  if (probability >= 70) return '#ef4444'
  if (probability >= 50) return '#f59e0b'
  return '#10b981'
}

// Actions
const refreshSituation = () => {
  ElMessage.success('Situation data refreshed')
}

const exportReport = () => {
  ElMessage.success('Situation report export started')
}

const openCommandCenter = () => {
  ElMessage.info('Opening command center')
}

const investigateThreat = (threat: any) => {
  ElMessage.info(`Investigating: ${threat.title}`)
}

const respondToThreat = (threat: any) => {
  ElMessage.info(`Response initiated for: ${threat.title}`)
}

const viewAllIncidents = () => {
  ElMessage.info('Viewing all incidents')
}

const viewResources = () => {
  ElMessage.info('Viewing all resources')
}

const contactTeam = (team: any) => {
  ElMessage.info(`Contacting ${team.name}`)
}

const broadcastMessage = () => {
  ElMessage.success('Broadcast message sent to all teams')
}

const sendMessage = () => {
  if (newMessage.value.trim()) {
    chatMessages.value.push({
      id: Date.now(),
      sender: 'You',
      text: newMessage.value,
      time: new Date().toLocaleTimeString(),
      type: 'user'
    })
    newMessage.value = ''
    ElMessage.success('Message sent')
  }
}

const executeDecision = (decision: any) => {
  ElMessage.info(`Executing: ${decision.title}`)
}

const reviewDecision = (decision: any) => {
  ElMessage.info(`Reviewing: ${decision.title}`)
}

const activateEmergencyProtocol = () => {
  ElMessage.warning('Emergency protocol activated! Notifying all response teams.')
  ElNotification({
    title: 'Emergency Protocol Activated',
    message: 'All response teams have been notified. Incident command established.',
    type: 'warning',
    duration: 0
  })
}

const generateSituationReport = () => {
  ElMessage.success('Situation report generation started')
}

const scheduleBriefing = () => {
  ElMessage.info('Briefing scheduling will open')
}

const assignIncident = (incident: any) => {
  ElMessage.success(`Incident assigned to response team`)
  incidentDialogVisible.value = false
}

const escalateIncident = (incident: any) => {
  ElMessage.warning(`Incident escalated to higher command`)
  incidentDialogVisible.value = false
}

// Simulate real-time updates
let dataInterval: ReturnType<typeof setInterval> | null = null
let alertInterval: ReturnType<typeof setInterval> | null = null

const startDataSimulation = () => {
  dataInterval = setInterval(() => {
    // Update metrics with random variations
    incidentSeverityIndex.value = Math.min(100, Math.max(0, incidentSeverityIndex.value + (Math.random() - 0.5) * 5))
    responseReadiness.value = Math.min(100, Math.max(0, responseReadiness.value + (Math.random() - 0.5) * 2))
    confidenceLevel.value = Math.min(100, Math.max(80, confidenceLevel.value + (Math.random() - 0.5) * 2))

    // Update time
    lastUpdateTime.value = new Date().toLocaleTimeString()
  }, 5000)

  // Random new alerts
  alertInterval = setInterval(() => {
    if (Math.random() > 0.85) {
      const newAlert = {
        id: Date.now(),
        title: 'New Alert Detected',
        severity: Math.random() > 0.7 ? 'critical' : 'warning',
        location: 'Unknown',
        detectedTime: new Date().toLocaleTimeString(),
        status: 'New',
        x: 20 + Math.random() * 60,
        y: 20 + Math.random() * 60
      }
      activeThreatsList.value.unshift(newAlert as any)
      activeThreats.value++
      if (activeThreatsList.value.length > 10) activeThreatsList.value.pop()

      ElNotification({
        title: 'New Threat Detected',
        message: `${newAlert.severity.toUpperCase()} alert: ${newAlert.title}`,
        type: newAlert.severity === 'critical' ? 'error' : 'warning',
        duration: 5000
      })
    }
  }, 15000)
}

// Update time
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Loading simulation
const startLoading = () => {
  const interval = setInterval(() => {
    if (loadingProgress.value < 90) loadingProgress.value += Math.random() * 10
  }, 200)
  return interval
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  lastUpdateTime.value = new Date().toLocaleTimeString()

  const interval = startLoading()
  setTimeout(() => {
    clearInterval(interval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => {
      isLoaded.value = true
      nextTick(() => {
        startDataSimulation()
      })
    }, 400)
  }, 2800)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
  if (dataInterval) clearInterval(dataInterval)
  if (alertInterval) clearInterval(alertInterval)
})
</script>

<style scoped>
/* ==================== Loading Screen ==================== */
.situation-awareness-container {
  min-height: 100vh;
  background: #f0f2f6;
}

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

.loading-content {
  text-align: center;
  padding: 40px;
  border-radius: 32px;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.3);
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

.spinner-ring:nth-child(1) { border-top-color: #3b82f6; }
.spinner-ring:nth-child(2) { border-right-color: #f59e0b; animation-delay: 0.2s; width: 70%; height: 70%; top: 15%; left: 15%; }
.spinner-ring:nth-child(3) { border-bottom-color: #10b981; animation-delay: 0.4s; width: 40%; height: 40%; top: 30%; left: 30%; }

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  margin-bottom: 24px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
}

.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-progress {
  width: 320px;
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
}

.loading-subtip {
  font-size: 11px;
  color: #64748b;
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
.sa-main {
  padding: 24px 32px;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.time-display {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border-radius: 12px;
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

/* Situation Banner */
.situation-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-radius: 20px;
  margin-bottom: 24px;
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.situation-banner.critical {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-left: 4px solid #ef4444;
}

.situation-banner.warning {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border-left: 4px solid #f59e0b;
}

.situation-banner.normal {
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border-left: 4px solid #10b981;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.situation-icon {
  font-size: 32px;
}
.situation-banner.critical .situation-icon { color: #ef4444; }
.situation-banner.warning .situation-icon { color: #f59e0b; }
.situation-banner.normal .situation-icon { color: #10b981; }

.situation-title {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.situation-description {
  font-size: 13px;
  color: #64748b;
  margin-top: 4px;
}

.banner-right {
  display: flex;
  gap: 24px;
}

.situation-metric {
  text-align: center;
}

.situation-metric .metric-label {
  display: block;
  font-size: 11px;
  color: #64748b;
}

.situation-metric .metric-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.situation-metric .metric-value.threat {
  color: #ef4444;
}

/* Metrics Row */
.metrics-row {
  margin-bottom: 24px;
}

.metric-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.metric-title {
  font-size: 13px;
  color: #64748b;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.metric-value.severity { color: #ef4444; }
.metric-value.readiness { color: #10b981; }
.metric-value.mttd { color: #3b82f6; }
.metric-value.mttr { color: #8b5cf6; }

.metric-trend {
  font-size: 12px;
}

.metric-trend.up { color: #ef4444; }
.metric-trend.down { color: #10b981; }

/* Dashboard Grid */
.dashboard-grid {
  margin-bottom: 24px;
}

/* Threat Map Card */
.threat-map-card {
  border-radius: 20px;
  height: 100%;
}

.threat-map-container {
  position: relative;
}

.threat-map-canvas {
  position: relative;
  width: 100%;
  height: 400px;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 100%);
  border-radius: 16px;
  overflow: hidden;
}

.map-grid-bg {
  position: absolute;
  width: 100%;
  height: 100%;
}

.grid-line {
  position: absolute;
  background: rgba(59, 130, 246, 0.1);
}

.grid-line.horizontal { width: 100%; height: 1px; }
.grid-line.vertical { height: 100%; width: 1px; }

.facility-zones {
  position: absolute;
  width: 100%;
  height: 100%;
}

.zone {
  position: absolute;
  border: 2px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.05);
}

.zone-label {
  position: absolute;
  top: -20px;
  left: 8px;
  font-size: 10px;
  color: #94a3b8;
}

.zone-status {
  position: absolute;
  top: -8px;
  right: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.zone-status.critical { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
.zone-status.warning { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.zone-status.healthy { background: #10b981; box-shadow: 0 0 8px #10b981; }

/* Threat Markers */
.threat-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 10;
}

.threat-pulse {
  position: absolute;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: threatPulse 1.5s infinite;
}

.threat-pulse.critical { background: rgba(239, 68, 68, 0.4); }
.threat-pulse.warning { background: rgba(245, 158, 11, 0.4); }

@keyframes threatPulse {
  0% { transform: translate(-50%, -50%) scale(0.5); opacity: 1; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.threat-icon {
  position: relative;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  z-index: 2;
}

.threat-icon.critical { background: #ef4444; animation: threatShake 0.5s infinite; }
.threat-icon.warning { background: #f59e0b; }

@keyframes threatShake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

.threat-popup {
  position: absolute;
  bottom: 35px;
  left: 50%;
  transform: translateX(-50%);
  width: 220px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
  z-index: 20;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-bottom: 1px solid #e2e8f0;
}

.popup-title {
  font-weight: 600;
  font-size: 13px;
}

.popup-content {
  padding: 10px 12px;
}

.popup-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  margin-bottom: 6px;
}

.popup-actions {
  display: flex;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid #e2e8f0;
}

/* Resource Markers */
.resource-marker {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 10;
}

.resource-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  animation: resourceBounce 2s infinite;
}

@keyframes resourceBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.resource-label {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-size: 9px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
}

/* Map Legend */
.map-legend {
  display: flex;
  gap: 20px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.critical { background: #ef4444; }
.legend-dot.warning { background: #f59e0b; }
.legend-dot.healthy { background: #10b981; }
.legend-dot.resource { background: #3b82f6; }

/* Incident Timeline Card */
.incident-timeline-card {
  border-radius: 20px;
  height: 100%;
}

.timeline-container {
  position: relative;
  padding-left: 20px;
  max-height: 380px;
  overflow-y: auto;
}

.timeline-line {
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(180deg, #3b82f6, #8b5cf6, #ec489a);
}

.timeline-item {
  position: relative;
  margin-bottom: 20px;
}

.timeline-dot {
  position: absolute;
  left: -16px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.timeline-dot.critical { background: #ef4444; box-shadow: 0 0 0 3px #fee2e2; }
.timeline-dot.warning { background: #f59e0b; box-shadow: 0 0 0 3px #fef3c7; }
.timeline-dot.info { background: #3b82f6; box-shadow: 0 0 0 3px #dbeafe; }

.timeline-content {
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  margin-left: 12px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.timeline-title {
  font-weight: 600;
  font-size: 13px;
  color: #1e293b;
}

.timeline-time {
  font-size: 10px;
  color: #94a3b8;
}

.timeline-description {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.timeline-footer {
  display: flex;
  gap: 16px;
  font-size: 10px;
  color: #94a3b8;
}

.timeline-footer .el-icon {
  margin-right: 2px;
}

/* Threat Intel Card */
.threat-intel-card {
  border-radius: 20px;
  height: 100%;
}

.intel-feed {
  max-height: 320px;
  overflow-y: auto;
}

.intel-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  transition: all 0.2s;
  cursor: pointer;
}

.intel-item.unread {
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.intel-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.intel-icon.critical { background: #fef2f2; color: #ef4444; }
.intel-icon.high { background: #fffbeb; color: #f59e0b; }
.intel-icon.medium { background: #eff6ff; color: #3b82f6; }
.intel-icon.low { background: #ecfdf5; color: #10b981; }

.intel-content {
  flex: 1;
}

.intel-title {
  font-weight: 500;
  font-size: 13px;
  color: #1e293b;
}

.intel-source {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 2px;
}

.intel-severity {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  align-self: center;
}

.intel-severity.critical { background: #fef2f2; color: #ef4444; }
.intel-severity.high { background: #fffbeb; color: #f59e0b; }
.intel-severity.medium { background: #eff6ff; color: #3b82f6; }
.intel-severity.low { background: #ecfdf5; color: #10b981; }

/* Resource Status Card */
.resource-status-card {
  border-radius: 20px;
  height: 100%;
}

.resource-grid {
  max-height: 320px;
  overflow-y: auto;
}

.team-card {
  background: #f8fafc;
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
}

.team-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.team-name {
  font-weight: 600;
  color: #1e293b;
}

.team-members {
  margin-bottom: 12px;
}

.member-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.member-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.member-info {
  flex: 1;
}

.member-name {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.member-role {
  display: block;
  font-size: 10px;
  color: #64748b;
}

.member-status {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.member-status.active { background: #10b981; box-shadow: 0 0 0 2px #d1fae5; }
.member-status.en-route { background: #f59e0b; box-shadow: 0 0 0 2px #fef3c7; }
.member-status.standby { background: #94a3b8; }

.team-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
  font-size: 12px;
  color: #64748b;
}

/* Predictive Card */
.predictive-card {
  border-radius: 20px;
  height: 100%;
}

.predictive-content {
  max-height: 240px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.prediction-item {
  margin-bottom: 16px;
}

.prediction-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.prediction-title {
  font-size: 13px;
  font-weight: 500;
  color: #1e293b;
}

.prediction-probability {
  font-size: 12px;
  font-weight: 600;
}

.prediction-probability.high { color: #ef4444; }
.prediction-probability.medium { color: #f59e0b; }
.prediction-probability.low { color: #10b981; }

.prediction-bar {
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}

.prediction-progress {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s;
}

.prediction-time {
  font-size: 10px;
  color: #94a3b8;
}

.ai-insight {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  padding: 16px;
  margin-top: 12px;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #8b5cf6;
  font-weight: 600;
  font-size: 13px;
}

.ai-insight p {
  font-size: 12px;
  color: #cbd5e1;
  line-height: 1.5;
  margin: 0;
}

/* Communication Card */
.communication-card {
  border-radius: 20px;
  height: 100%;
}

.chat-messages {
  height: 280px;
  overflow-y: auto;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 12px;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.chat-message.user .message-content {
  background: #3b82f6;
  color: white;
}

.chat-message.user .message-header {
  color: rgba(255, 255, 255, 0.8);
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

.message-content {
  flex: 1;
  background: white;
  padding: 10px 12px;
  border-radius: 12px;
  max-width: 80%;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 11px;
}

.message-sender {
  font-weight: 600;
  color: #1e293b;
}

.message-time {
  color: #94a3b8;
}

.message-text {
  font-size: 13px;
}

.chat-input {
  display: flex;
  gap: 8px;
}

/* Decision Support Card */
.decision-support-card {
  border-radius: 20px;
  height: 100%;
}

.decision-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.decision-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 12px;
}

.decision-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.decision-icon.urgent { background: #fef2f2; color: #ef4444; }
.decision-icon.recommendation { background: #eff6ff; color: #3b82f6; }
.decision-icon.action { background: #fffbeb; color: #f59e0b; }

.decision-content {
  flex: 1;
}

.decision-title {
  font-weight: 600;
  font-size: 14px;
  color: #1e293b;
}

.decision-description {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.decision-actions {
  display: flex;
  gap: 8px;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 8px;
}

.action-buttons .el-button {
  border-radius: 12px;
  padding: 10px 24px;
}

/* Responsive */
@media (max-width: 1200px) {
  .sa-main { padding: 16px; }
}

@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; gap: 16px; }
  .banner-left { flex-direction: column; text-align: center; }
  .banner-right { flex-direction: column; gap: 8px; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; }
}
</style>