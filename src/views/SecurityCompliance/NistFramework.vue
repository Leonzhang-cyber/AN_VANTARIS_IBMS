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
          <span class="loading-title">Loading NIST Framework</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">NIST Cybersecurity Framework (CSF) 2.0</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="nist-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">NIST Cybersecurity Framework</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>NIST Framework</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runFrameworkAssessment">
          <el-icon><Refresh /></el-icon>
          Run Assessment
        </el-button>
        <el-button type="success" plain @click="exportFrameworkReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="info" plain @click="viewMaturityModel">
          <el-icon><TrendCharts /></el-icon>
          Maturity Model
        </el-button>
      </div>
    </div>

    <!-- Framework Overview Banner -->
    <el-card class="overview-banner" shadow="hover">
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon :size="48"><Flag /></el-icon>
        </div>
        <div class="banner-info">
          <div class="banner-title">NIST CSF 2.0 Framework Implementation</div>
          <div class="banner-description">The NIST Cybersecurity Framework provides a policy framework of computer security guidance for how private sector organizations can assess and improve their ability to prevent, detect, and respond to cyber attacks.</div>
        </div>
        <div class="banner-stats">
          <div class="banner-stat">
            <span class="stat-value">Tier {{ maturityTier }}</span>
            <span class="stat-label">Maturity Tier</span>
          </div>
          <div class="banner-stat">
            <span class="stat-value">{{ overallScore }}%</span>
            <span class="stat-label">Implementation Score</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- Five Core Functions -->
    <div class="functions-section">
      <h3 class="section-title">NIST CSF Core Functions</h3>
      <div class="functions-grid">
        <el-card v-for="func in functions" :key="func.id" class="function-card" shadow="hover" @click="viewFunctionDetails(func)">
          <div class="function-header">
            <div class="function-icon" :style="{ backgroundColor: func.color }">
              <el-icon :size="28"><component :is="func.icon" /></el-icon>
            </div>
            <el-tag :type="getTierType(func.tier)" size="small">Tier {{ func.tier }}</el-tag>
          </div>
          <h4 class="function-name">{{ func.name }}</h4>
          <div class="function-progress">
            <el-progress :percentage="func.progress" :stroke-width="8" :color="func.color" />
          </div>
          <div class="function-stats">
            <span>{{ func.implemented }}/{{ func.total }} Categories</span>
            <span>{{ func.subcategories }} Subcategories</span>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Detailed Categories by Function -->
    <div class="categories-section">
      <h3 class="section-title">Framework Categories by Function</h3>
      <el-tabs v-model="activeFunction" type="border-card" class="function-tabs">
        <el-tab-pane v-for="func in functions" :key="func.id" :name="func.id">
          <template #label>
            <div class="function-tab-label">
              <el-icon><component :is="func.icon" /></el-icon>
              <span>{{ func.name }}</span>
            </div>
          </template>
          <div class="categories-content">
            <div v-for="category in getCategoriesByFunction(func.id)" :key="category.id" class="category-group">
              <div class="category-header">
                <div class="category-title">
                  <span class="category-id">{{ category.id }}</span>
                  <span class="category-name">{{ category.name }}</span>
                </div>
                <el-tag :type="getCategoryStatusType(category.status)" size="small">{{ category.status }}</el-tag>
              </div>
              <div class="category-progress">
                <el-progress :percentage="category.progress" :stroke-width="6" :color="getScoreColor(category.progress)" />
              </div>
              <div class="subcategories-list">
                <div v-for="sub in category.subcategories" :key="sub.id" class="subcategory-item">
                  <div class="subcategory-info">
                    <span class="subcategory-id">{{ sub.id }}</span>
                    <span class="subcategory-name">{{ sub.name }}</span>
                  </div>
                  <div class="subcategory-status">
                    <el-select v-model="sub.status" size="small" style="width: 120px" @change="updateSubcategoryStatus(sub)">
                      <el-option label="Implemented" value="implemented" />
                      <el-option label="Partially" value="partial" />
                      <el-option label="Not Started" value="not-started" />
                      <el-option label="Not Applicable" value="na" />
                    </el-select>
                    <el-button size="small" text type="primary" @click="viewEvidence(sub)">Evidence</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Implementation Tiers -->
    <div class="tiers-section">
      <el-card class="tiers-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Implementation Tiers</span>
            <el-button text type="primary" @click="viewTierDetails">View Details</el-button>
          </div>
        </template>
        <div class="tiers-content">
          <div class="tiers-description">
            NIST CSF Implementation Tiers describe the degree to which an organization's cybersecurity practices exhibit the characteristics defined in the Framework.
          </div>
          <div class="tiers-grid">
            <div v-for="tier in implementationTiers" :key="tier.level" :class="['tier-item', { active: tier.level === maturityTier }]">
              <div class="tier-level">Tier {{ tier.level }}</div>
              <div class="tier-name">{{ tier.name }}</div>
              <div class="tier-description">{{ tier.description }}</div>
              <div class="tier-progress" v-if="tier.level === maturityTier">
                <el-progress :percentage="tierProgress" :stroke-width="4" :show-text="false" />
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Current vs Target Profile -->
    <div class="profile-section">
      <el-card class="profile-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><DataLine /></el-icon> Current vs Target Profile</span>
            <el-button text type="primary" @click="defineTargetProfile">Define Target Profile</el-button>
          </div>
        </template>
        <div ref="profileChartRef" class="profile-chart"></div>
      </el-card>
    </div>

    <!-- Action Plan & Roadmap -->
    <div class="roadmap-section">
      <el-card class="roadmap-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Calendar /></el-icon> Improvement Roadmap</span>
            <el-button type="primary" size="small" @click="createActionPlan">Create Action Plan</el-button>
          </div>
        </template>
        <div class="roadmap-timeline">
          <el-timeline>
            <el-timeline-item v-for="item in roadmapItems" :key="item.id" :type="item.type" :timestamp="item.date" placement="top" size="large">
              <el-card shadow="hover" class="roadmap-item-card">
                <div class="roadmap-header">
                  <span class="roadmap-title">{{ item.title }}</span>
                  <el-tag :type="getPriorityType(item.priority)" size="small">{{ item.priority }}</el-tag>
                </div>
                <div class="roadmap-description">{{ item.description }}</div>
                <div class="roadmap-meta">
                  <span>Function: {{ item.function }}</span>
                  <span>Owner: {{ item.owner }}</span>
                  <span>Status: {{ item.status }}</span>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="uploadAssessment">
          <el-icon><Upload /></el-icon>
          Upload Assessment
        </el-button>
        <el-button type="success" plain @click="generateGapAnalysis">
          <el-icon><Warning /></el-icon>
          Gap Analysis
        </el-button>
        <el-button type="warning" plain @click="benchmarkComparison">
          <el-icon><TrendCharts /></el-icon>
          Industry Benchmark
        </el-button>
        <el-button type="info" plain @click="viewResources">
          <el-icon><Reading /></el-icon>
          Framework Resources
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
  Refresh, Download, TrendCharts, Flag, DataLine, Calendar, Upload,
  Warning, Reading, Monitor, Lock, Search, Tools, Key, Bell, User, Setting, Connection
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading NIST Cybersecurity Framework...')

const loadingMessages = [
  'Loading NIST Cybersecurity Framework...',
  'Analyzing core functions...',
  'Mapping subcategories...',
  'Framework assessment ready!'
]

// Framework data
const maturityTier = ref(3)
const overallScore = ref(76)
const tierProgress = ref(76)

// Five Core Functions
const functions = ref([
  { id: 'identify', name: 'IDENTIFY', icon: 'Search', color: '#3b82f6', progress: 85, implemented: 5, total: 6, tier: 3, subcategories: 28 },
  { id: 'protect', name: 'PROTECT', icon: 'Lock', color: '#10b981', progress: 82, implemented: 8, total: 10, tier: 3, subcategories: 42 },
  { id: 'detect', name: 'DETECT', icon: 'Bell', color: '#f59e0b', progress: 78, implemented: 3, total: 4, tier: 3, subcategories: 16 },
  { id: 'respond', name: 'RESPOND', icon: 'Tools', color: '#ef4444', progress: 70, implemented: 4, total: 6, tier: 2, subcategories: 24 },
  { id: 'recover', name: 'RECOVER', icon: 'Refresh', color: '#8b5cf6', progress: 65, implemented: 3, total: 5, tier: 2, subcategories: 18 }
])

const activeFunction = ref('identify')

// Categories by function
const categoriesData = ref([
  // IDENTIFY Function Categories
  { id: 'ID.AM', function: 'identify', name: 'Asset Management', status: 'Implemented', progress: 90,
    subcategories: [
      { id: 'ID.AM-1', name: 'Physical devices and systems within the organization are inventoried', status: 'implemented' },
      { id: 'ID.AM-2', name: 'Software platforms and applications within the organization are inventoried', status: 'implemented' },
      { id: 'ID.AM-3', name: 'Organizational communication and data flows are mapped', status: 'partial' },
      { id: 'ID.AM-4', name: 'External information systems are catalogued', status: 'implemented' },
      { id: 'ID.AM-5', name: 'Resources are prioritized based on their classification', status: 'partial' }
    ] },
  { id: 'ID.BE', function: 'identify', name: 'Business Environment', status: 'Implemented', progress: 88,
    subcategories: [
      { id: 'ID.BE-1', name: 'Organizational role in supply chain is identified', status: 'implemented' },
      { id: 'ID.BE-2', name: 'Criticality of organizational assets is established', status: 'implemented' },
      { id: 'ID.BE-3', name: 'Organization is positioned in critical infrastructure', status: 'partial' }
    ] },
  { id: 'ID.GV', function: 'identify', name: 'Governance', status: 'Implemented', progress: 85,
    subcategories: [
      { id: 'ID.GV-1', name: 'Cybersecurity policy is established and communicated', status: 'implemented' },
      { id: 'ID.GV-2', name: 'Roles and responsibilities are defined', status: 'implemented' },
      { id: 'ID.GV-3', name: 'Legal and regulatory requirements are understood', status: 'implemented' },
      { id: 'ID.GV-4', name: 'Governance and risk management processes address cybersecurity', status: 'partial' }
    ] },
  { id: 'ID.RA', function: 'identify', name: 'Risk Assessment', status: 'Partial', progress: 75,
    subcategories: [
      { id: 'ID.RA-1', name: 'Asset vulnerabilities are identified and documented', status: 'implemented' },
      { id: 'ID.RA-2', name: 'Threat intelligence is received from information sharing forums', status: 'partial' },
      { id: 'ID.RA-3', name: 'Internal and external threats are identified', status: 'implemented' },
      { id: 'ID.RA-4', name: 'Potential impacts are identified', status: 'partial' },
      { id: 'ID.RA-5', name: 'Threats, vulnerabilities, likelihoods are used to determine risk', status: 'partial' }
    ] },
  { id: 'ID.RM', function: 'identify', name: 'Risk Management Strategy', status: 'Implemented', progress: 82,
    subcategories: [
      { id: 'ID.RM-1', name: 'Risk management processes are established and managed', status: 'implemented' },
      { id: 'ID.RM-2', name: 'Risk tolerance is determined and expressed', status: 'partial' },
      { id: 'ID.RM-3', name: 'Risk management activities are informed by risk tolerance', status: 'implemented' }
    ] },
  // PROTECT Function Categories
  { id: 'PR.AC', function: 'protect', name: 'Access Control', status: 'Implemented', progress: 88,
    subcategories: [
      { id: 'PR.AC-1', name: 'Identities and credentials are managed for authorized devices and users', status: 'implemented' },
      { id: 'PR.AC-2', name: 'Physical access to assets is managed and protected', status: 'implemented' },
      { id: 'PR.AC-3', name: 'Remote access is managed', status: 'implemented' },
      { id: 'PR.AC-4', name: 'Access permissions are managed', status: 'partial' }
    ] },
  { id: 'PR.AT', function: 'protect', name: 'Awareness and Training', status: 'Partial', progress: 70,
    subcategories: [
      { id: 'PR.AT-1', name: 'All users are informed and trained', status: 'partial' },
      { id: 'PR.AT-2', name: 'Privileged users understand their roles and responsibilities', status: 'partial' }
    ] },
  { id: 'PR.DS', function: 'protect', name: 'Data Security', status: 'Implemented', progress: 85,
    subcategories: [
      { id: 'PR.DS-1', name: 'Data-at-rest is protected', status: 'implemented' },
      { id: 'PR.DS-2', name: 'Data-in-transit is protected', status: 'implemented' },
      { id: 'PR.DS-3', name: 'Assets are formally managed throughout removal', status: 'partial' },
      { id: 'PR.DS-4', name: 'Adequate capacity to ensure availability is maintained', status: 'implemented' }
    ] },
  { id: 'PR.IP', function: 'protect', name: 'Information Protection', status: 'Partial', progress: 78,
    subcategories: [
      { id: 'PR.IP-1', name: 'Baselines of configurations are created and maintained', status: 'implemented' },
      { id: 'PR.IP-2', name: 'System development life cycle is managed', status: 'partial' },
      { id: 'PR.IP-3', name: 'Configuration change control processes are in place', status: 'implemented' },
      { id: 'PR.IP-4', name: 'Backups of information are conducted and maintained', status: 'implemented' }
    ] },
  // DETECT Function Categories
  { id: 'DE.AE', function: 'detect', name: 'Anomalies and Events', status: 'Implemented', progress: 82,
    subcategories: [
      { id: 'DE.AE-1', name: 'Baseline of network operations is established', status: 'implemented' },
      { id: 'DE.AE-2', name: 'Detected events are analyzed to understand attack targets', status: 'partial' },
      { id: 'DE.AE-3', name: 'Event data are aggregated and correlated', status: 'implemented' }
    ] },
  { id: 'DE.CM', function: 'detect', name: 'Continuous Monitoring', status: 'Partial', progress: 75,
    subcategories: [
      { id: 'DE.CM-1', name: 'Network is monitored to detect cybersecurity events', status: 'implemented' },
      { id: 'DE.CM-2', name: 'Physical environment is monitored', status: 'implemented' },
      { id: 'DE.CM-3', name: 'Personnel activity is monitored', status: 'partial' },
      { id: 'DE.CM-4', name: 'Malicious code is detected', status: 'implemented' }
    ] },
  // RESPOND Function Categories
  { id: 'RS.RP', function: 'respond', name: 'Response Planning', status: 'Partial', progress: 68,
    subcategories: [
      { id: 'RS.RP-1', name: 'Response plan is executed during or after an event', status: 'partial' }
    ] },
  { id: 'RS.CO', function: 'respond', name: 'Communications', status: 'Partial', progress: 65,
    subcategories: [
      { id: 'RS.CO-1', name: 'Personnel know their roles when a response is needed', status: 'partial' },
      { id: 'RS.CO-2', name: 'Events are reported consistent with established criteria', status: 'implemented' }
    ] },
  // RECOVER Function Categories
  { id: 'RC.RP', function: 'recover', name: 'Recovery Planning', status: 'Partial', progress: 70,
    subcategories: [
      { id: 'RC.RP-1', name: 'Recovery plan is executed during or after an event', status: 'partial' }
    ] },
  { id: 'RC.IM', function: 'recover', name: 'Improvements', status: 'Partial', progress: 60,
    subcategories: [
      { id: 'RC.IM-1', name: 'Recovery plans incorporate lessons learned', status: 'partial' },
      { id: 'RC.IM-2', name: 'Recovery strategies are updated', status: 'not-started' }
    ] }
])

// Implementation Tiers
const implementationTiers = ref([
  { level: 1, name: 'Partial', description: 'Cybersecurity practices are performed on an ad-hoc basis and may not be repeatable.' },
  { level: 2, name: 'Risk Informed', description: 'Cybersecurity practices are approved but not established as organizational-wide policy.' },
  { level: 3, name: 'Repeatable', description: 'Cybersecurity practices are formally approved and expressed as policy.' },
  { level: 4, name: 'Adaptive', description: 'Cybersecurity practices are adapted based on lessons learned and predictive indicators.' }
])

// Roadmap items
const roadmapItems = ref([
  { id: 1, title: 'Implement SIEM Solution', description: 'Deploy Security Information and Event Management for centralized log collection and real-time alerting', date: 'Q1 2024', owner: 'Security Team', function: 'Detect', priority: 'High', status: 'In Progress', type: 'warning' },
  { id: 2, title: 'Enhance Access Control', description: 'Implement MFA for all remote access and privileged accounts', date: 'Q1 2024', owner: 'IT Operations', function: 'Protect', priority: 'Critical', status: 'In Progress', type: 'danger' },
  { id: 3, title: 'Conduct Annual Risk Assessment', description: 'Perform comprehensive risk assessment across all critical assets and systems', date: 'Q2 2024', owner: 'Risk Management', function: 'Identify', priority: 'High', status: 'Planned', type: 'info' },
  { id: 4, title: 'Update Incident Response Plan', description: 'Revise IR plan to include recent threat intelligence and lessons learned', date: 'Q2 2024', owner: 'Security Team', function: 'Respond', priority: 'Medium', status: 'Planned', type: 'info' },
  { id: 5, title: 'Business Continuity Testing', description: 'Test and validate disaster recovery and business continuity procedures', date: 'Q3 2024', owner: 'BCP Team', function: 'Recover', priority: 'Medium', status: 'Not Started', type: 'info' }
])

// Chart ref
const profileChartRef = ref<HTMLElement>()
let profileChart: echarts.ECharts | null = null

// Helper functions
const getTierType = (tier: number) => {
  if (tier >= 3) return 'success'
  if (tier >= 2) return 'warning'
  return 'danger'
}

const getScoreColor = (score: number) => {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

const getCategoryStatusType = (status: string) => {
  switch (status) {
    case 'Implemented': return 'success'
    case 'Partial': return 'warning'
    case 'Not Started': return 'danger'
    default: return 'info'
  }
}

const getPriorityType = (priority: string) => {
  switch (priority) {
    case 'Critical': return 'danger'
    case 'High': return 'warning'
    case 'Medium': return 'primary'
    default: return 'info'
  }
}

const getCategoriesByFunction = (functionId: string) => {
  return categoriesData.value.filter(c => c.function === functionId)
}

// Chart data
const currentProfile = [85, 82, 78, 70, 65]
const targetProfile = [95, 90, 88, 85, 80]

// Initialize profile chart
const initProfileChart = () => {
  if (!profileChartRef.value) return
  profileChart = echarts.init(profileChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Current Profile', 'Target Profile'], left: 'left' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Identify', 'Protect', 'Detect', 'Respond', 'Recover'] },
    yAxis: { type: 'value', name: 'Implementation Score (%)', min: 0, max: 100 },
    series: [
      { name: 'Current Profile', type: 'line', data: currentProfile, lineStyle: { color: '#3b82f6', width: 3 }, smooth: true, symbol: 'circle', symbolSize: 8, itemStyle: { color: '#3b82f6' } },
      { name: 'Target Profile', type: 'line', data: targetProfile, lineStyle: { color: '#f59e0b', width: 3, type: 'dashed' }, smooth: true, symbol: 'diamond', symbolSize: 8, itemStyle: { color: '#f59e0b' } }
    ]
  }
  profileChart.setOption(option)
}

// Event handlers
const runFrameworkAssessment = () => {
  ElMessage.info('Framework assessment initiated. Evaluating all functions...')
  setTimeout(() => {
    ElMessage.success('Assessment completed. Gaps identified in Respond and Recover functions.')
  }, 3000)
}

const exportFrameworkReport = () => {
  ElMessage.info('Exporting NIST framework report...')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 2000)
}

const viewMaturityModel = () => {
  ElMessage.info('Viewing maturity model details')
}

const viewFunctionDetails = (func: any) => {
  ElMessage.info(`Viewing details for ${func.name} function`)
}

const updateSubcategoryStatus = (sub: any) => {
  ElMessage.success(`Subcategory ${sub.id} status updated to ${sub.status}`)
}

const viewEvidence = (sub: any) => {
  ElMessage.info(`Viewing evidence for ${sub.id}`)
}

const viewTierDetails = () => {
  ElMessage.info('Viewing implementation tier details')
}

const defineTargetProfile = () => {
  ElMessage.info('Define target profile dialog opened')
}

const createActionPlan = () => {
  ElMessage.info('Creating action plan from roadmap')
}

const uploadAssessment = () => {
  ElMessage.info('Upload assessment document')
}

const generateGapAnalysis = () => {
  ElMessage.info('Generating gap analysis report')
}

const benchmarkComparison = () => {
  ElMessage.info('Viewing industry benchmark comparison')
}

const viewResources = () => {
  ElMessage.info('Opening NIST framework resources')
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
        initProfileChart()
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (profileChart) profileChart.dispose()
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
.nist-container {
  padding: 20px;
  background: #ffffff;
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

/* Overview Banner */
.overview-banner {
  margin-bottom: 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #eff6ff 0%, #e0f2fe 100%);
  border-color: #bae6fd;
}

.banner-content {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px;
}

.banner-icon {
  color: #3b82f6;
}

.banner-info {
  flex: 1;
}

.banner-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.banner-description {
  font-size: 13px;
  color: #475569;
  line-height: 1.5;
}

.banner-stats {
  display: flex;
  gap: 24px;
}

.banner-stat {
  text-align: center;
  padding: 8px 16px;
  background: white;
  border-radius: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
  display: block;
}

.stat-label {
  font-size: 11px;
  color: #64748b;
}

/* Functions Section */
.functions-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.functions-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.function-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.function-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.function-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.function-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.function-name {
  font-size: 14px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 12px 0;
}

.function-progress {
  margin-bottom: 8px;
}

.function-stats {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #64748b;
}

/* Categories Section */
.categories-section {
  margin-bottom: 32px;
}

.function-tabs {
  border-radius: 12px;
}

.function-tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.categories-content {
  padding: 20px;
  max-height: 600px;
  overflow-y: auto;
}

.category-group {
  margin-bottom: 28px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.category-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.category-title {
  display: flex;
  gap: 12px;
  align-items: baseline;
}

.category-id {
  font-size: 16px;
  font-weight: 700;
  color: #3b82f6;
}

.category-name {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.category-progress {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.subcategories-list {
  padding: 8px 0;
}

.subcategory-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
}

.subcategory-item:last-child {
  border-bottom: none;
}

.subcategory-info {
  display: flex;
  gap: 12px;
  align-items: baseline;
}

.subcategory-id {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
  font-family: monospace;
}

.subcategory-name {
  font-size: 13px;
  color: #334155;
}

.subcategory-status {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* Tiers Section */
.tiers-section {
  margin-bottom: 32px;
}

.tiers-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #1e293b;
}

.tiers-content {
  padding: 8px;
}

.tiers-description {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  margin-bottom: 20px;
}

.tiers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.tier-item {
  padding: 16px;
  border-radius: 10px;
  background: #f8fafc;
  transition: all 0.2s;
}

.tier-item.active {
  background: #eff6ff;
  border: 2px solid #3b82f6;
}

.tier-level {
  font-size: 20px;
  font-weight: 700;
  color: #3b82f6;
  margin-bottom: 8px;
}

.tier-name {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.tier-description {
  font-size: 11px;
  color: #64748b;
  line-height: 1.4;
  margin-bottom: 12px;
}

/* Profile Section */
.profile-section {
  margin-bottom: 32px;
}

.profile-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.profile-chart {
  height: 350px;
  width: 100%;
}

/* Roadmap Section */
.roadmap-section {
  margin-bottom: 24px;
}

.roadmap-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.roadmap-timeline {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
}

.roadmap-item-card {
  margin-bottom: 12px;
  border-radius: 8px;
}

.roadmap-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.roadmap-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.roadmap-description {
  font-size: 13px;
  color: #475569;
  margin-bottom: 8px;
}

.roadmap-meta {
  display: flex;
  gap: 20px;
  font-size: 11px;
  color: #94a3b8;
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
  background: #f8fafc;
  border-radius: 12px;
}

/* Responsive */
@media (max-width: 1200px) {
  .functions-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .tiers-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .banner-stats {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .functions-grid {
    grid-template-columns: 1fr;
  }

  .tiers-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .subcategory-item {
    flex-direction: column;
    gap: 8px;
    align-items: flex-start;
  }

  .category-header {
    flex-direction: column;
    gap: 8px;
  }
}
</style>