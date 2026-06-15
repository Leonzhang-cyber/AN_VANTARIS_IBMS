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
          <span class="loading-title">Loading IEC62443 Compliance</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IEC 62443 Industrial Cybersecurity Compliance Dashboard</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="iec-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">IEC 62443 Compliance</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>IEC 62443 Compliance</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runComplianceScan">
          <el-icon><Refresh /></el-icon>
          Run Compliance Scan
        </el-button>
        <el-button type="success" plain @click="exportReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="info" plain @click="viewAuditHistory">
          <el-icon><Clock /></el-icon>
          Audit History
        </el-button>
      </div>
    </div>

    <!-- Overall Compliance Score -->
    <div class="score-section">
      <el-card class="score-card" shadow="hover">
        <div class="score-content">
          <div class="score-gauge">
            <el-progress type="circle" :percentage="overallCompliance" :width="160" :stroke-width="12" :color="getScoreColor(overallCompliance)">
              <template #default>
                <div class="score-text">
                  <span class="score-value">{{ overallCompliance }}%</span>
                  <span class="score-label">Overall Compliance</span>
                </div>
              </template>
            </el-progress>
          </div>
          <div class="score-details">
            <div class="detail-item">
              <div class="detail-label">Compliance Level</div>
              <div class="detail-value">{{ complianceLevel }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Requirements Met</div>
              <div class="detail-value">{{ requirementsMet }}/{{ totalRequirements }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Last Assessment</div>
              <div class="detail-value">{{ lastAssessment }}</div>
            </div>
            <div class="detail-item">
              <div class="detail-label">Next Audit Due</div>
              <div class="detail-value">{{ nextAuditDue }}</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Four Pillars of IEC 62443 -->
    <div class="pillars-section">
      <h3 class="section-title">IEC 62443 Framework Pillars</h3>
      <div class="pillars-grid">
        <el-card v-for="pillar in pillars" :key="pillar.name" class="pillar-card" shadow="hover" @click="viewPillarDetails(pillar)">
          <div class="pillar-icon" :style="{ backgroundColor: pillar.color }">
            <el-icon :size="32"><component :is="pillar.icon" /></el-icon>
          </div>
          <div class="pillar-info">
            <h4 class="pillar-name">{{ pillar.name }}</h4>
            <p class="pillar-desc">{{ pillar.description }}</p>
            <div class="pillar-progress">
              <el-progress :percentage="pillar.progress" :stroke-width="8" :color="getScoreColor(pillar.progress)" />
            </div>
            <div class="pillar-stats">
              <span>{{ pillar.compliant }}/{{ pillar.total }} requirements met</span>
              <span class="pillar-status" :class="pillar.status">{{ pillar.status }}</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- Detailed Requirements by Zone -->
    <div class="zones-section">
      <h3 class="section-title">Security Zones & Conduits</h3>
      <el-tabs v-model="activeZone" type="border-card" class="zone-tabs">
        <el-tab-pane v-for="zone in securityZones" :key="zone.id" :name="zone.id">
          <template #label>
            <div class="zone-tab-label">
              <el-icon><component :is="zone.icon" /></el-icon>
              <span>{{ zone.name }}</span>
              <el-tag :type="zone.compliance >= 80 ? 'success' : zone.compliance >= 60 ? 'warning' : 'danger'" size="small">
                {{ zone.compliance }}%
              </el-tag>
            </div>
          </template>
          <div class="zone-content">
            <div class="zone-description">{{ zone.description }}</div>
            <div class="requirements-table">
              <el-table :data="zone.requirements" stripe style="width: 100%">
                <el-table-column prop="id" label="ID" width="120" />
                <el-table-column prop="requirement" label="Requirement" min-width="300" />
                <el-table-column prop="status" label="Status" width="120" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="evidence" label="Evidence" width="150" align="center">
                  <template #default="{ row }">
                    <el-button v-if="row.evidence" text type="primary" size="small" @click="viewEvidence(row)">View</el-button>
                    <span v-else class="no-evidence">-</span>
                  </template>
                </el-table-column>
                <el-table-column label="Actions" width="120" align="center">
                  <template #default="{ row }">
                    <el-dropdown trigger="click">
                      <el-button size="small" type="info" plain>
                        Actions <el-icon><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item @click="uploadEvidence(row)">Upload Evidence</el-dropdown-item>
                          <el-dropdown-item @click="reviewRequirement(row)">Review</el-dropdown-item>
                          <el-dropdown-item @click="addComment(row)">Add Comment</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- Compliance Status Overview Charts -->
    <div class="charts-section">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Compliance Progress Trend</span>
            <el-button text type="primary" @click="refreshTrendChart">Refresh</el-button>
          </div>
        </template>
        <div ref="trendChartRef" class="trend-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><PieChart /></el-icon> Requirement Status Distribution</span>
            <el-button text type="primary" @click="refreshStatusChart">Refresh</el-button>
          </div>
        </template>
        <div ref="statusChartRef" class="status-chart"></div>
      </el-card>
    </div>

    <!-- Gap Analysis & Remediation Plan -->
    <div class="gap-section">
      <el-card class="gap-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Warning /></el-icon> Gap Analysis & Remediation Plan</span>
            <el-button type="primary" size="small" @click="createRemediationPlan">Create Plan</el-button>
          </div>
        </template>
        <div class="gap-list">
          <div v-for="gap in gaps" :key="gap.id" class="gap-item">
            <div class="gap-severity" :class="gap.severity">
              {{ gap.severity }}
            </div>
            <div class="gap-info">
              <div class="gap-title">{{ gap.title }}</div>
              <div class="gap-description">{{ gap.description }}</div>
              <div class="gap-meta">
                <span>Standard: {{ gap.standard }}</span>
                <span>Affected Zone: {{ gap.zone }}</span>
                <span>Target Date: {{ gap.targetDate }}</span>
              </div>
            </div>
            <div class="gap-progress">
              <el-progress :percentage="gap.progress" :stroke-width="6" :color="getProgressColor(gap.progress)" />
              <span class="progress-text">{{ gap.progress }}%</span>
            </div>
            <el-button size="small" type="primary" plain @click="remediateGap(gap)">Remediate</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Audit Trail & Documentation -->
    <div class="audit-section">
      <el-card class="audit-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Document /></el-icon> Audit Trail & Documentation</span>
            <el-button text type="primary" @click="viewAllAudits">View All</el-button>
          </div>
        </template>
        <div class="audit-timeline">
          <el-timeline>
            <el-timeline-item v-for="audit in auditTrail" :key="audit.id" :type="audit.type" :timestamp="audit.date" placement="top" size="large">
              <el-card shadow="hover" class="audit-item-card">
                <div class="audit-header">
                  <span class="audit-action">{{ audit.action }}</span>
                  <el-tag :type="audit.status === 'passed' ? 'success' : audit.status === 'failed' ? 'danger' : 'warning'" size="small">
                    {{ audit.status }}
                  </el-tag>
                </div>
                <div class="audit-detail">{{ audit.detail }}</div>
                <div class="auditor">Auditor: {{ audit.auditor }}</div>
                <div class="audit-evidence" v-if="audit.evidence">
                  <el-link type="primary" :underline="false" @click="downloadEvidence(audit.evidence)">
                    <el-icon><Link /></el-icon> Download Evidence
                  </el-link>
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
        <el-button type="primary" plain @click="scheduleAudit">
          <el-icon><Calendar /></el-icon>
          Schedule Audit
        </el-button>
        <el-button type="success" plain @click="generateComplianceReport">
          <el-icon><Document /></el-icon>
          Generate Report
        </el-button>
        <el-button type="warning" plain @click="requestException">
          <el-icon><Warning /></el-icon>
          Request Exception
        </el-button>
        <el-button type="info" plain @click="viewDocumentation">
          <el-icon><Reading /></el-icon>
          View Documentation
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Download, Clock, TrendCharts, PieChart, Warning, Document,
  ArrowDown, Calendar, Reading, Link, Lock, Setting, Key, Monitor, Connection, Grid
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading IEC62443 Compliance Framework...')

const loadingMessages = [
  'Loading IEC62443 Compliance Framework...',
  'Analyzing security zones...',
  'Validating requirements...',
  'Compliance dashboard ready!'
]

// Compliance data
const overallCompliance = ref(78)
const complianceLevel = ref('Level 2 - Implemented')
const requirementsMet = ref(127)
const totalRequirements = ref(163)
const lastAssessment = ref('2024-01-10')
const nextAuditDue = ref('2024-04-10')

// IEC 62443 Four Pillars
const pillars = ref([
  { name: 'General Requirements', icon: 'Lock', description: 'Organizational processes, policies, and procedures for IACS security', progress: 85, compliant: 18, total: 21, status: 'compliant', color: '#3b82f6' },
  { name: 'Policies & Procedures', icon: 'Document', description: 'Security policies, standards, and procedures documentation', progress: 82, compliant: 14, total: 17, status: 'compliant', color: '#10b981' },
  { name: 'System Requirements', icon: 'Setting', description: 'Technical controls for the IACS solution', progress: 72, compliant: 52, total: 72, status: 'partial', color: '#f59e0b' },
  { name: 'Development Requirements', icon: 'Grid', description: 'Secure development lifecycle requirements', progress: 68, compliant: 43, total: 63, status: 'partial', color: '#8b5cf6' }
])

// Security Zones
const securityZones = ref([
  {
    id: 'zone-1',
    name: 'Control Network Zone',
    icon: 'Monitor',
    description: 'Primary industrial control network including PLCs, RTUs, and HMIs',
    compliance: 85,
    requirements: [
      { id: 'SR-1.1', requirement: 'Human user identification and authentication', status: 'Compliant', evidence: 'auth_policy.pdf' },
      { id: 'SR-1.2', requirement: 'Software process and device identification', status: 'Compliant', evidence: 'device_inventory.xlsx' },
      { id: 'SR-1.3', requirement: 'Account management', status: 'Compliant', evidence: 'account_policy.pdf' },
      { id: 'SR-1.4', requirement: 'Identifier management', status: 'Partial', evidence: null },
      { id: 'SR-1.5', requirement: 'Authenticator management', status: 'Compliant', evidence: 'auth_config.pdf' },
      { id: 'SR-1.6', requirement: 'Wireless access management', status: 'Non-Compliant', evidence: null }
    ]
  },
  {
    id: 'zone-2',
    name: 'Safety System Zone',
    icon: 'Warning',
    description: 'Safety instrumented systems and emergency shutdown systems',
    compliance: 92,
    requirements: [
      { id: 'SR-2.1', requirement: 'Authorization enforcement', status: 'Compliant', evidence: 'rbac_policy.pdf' },
      { id: 'SR-2.2', requirement: 'Wireless use control', status: 'Compliant', evidence: 'wireless_policy.pdf' },
      { id: 'SR-2.3', requirement: 'Port and service control', status: 'Compliant', evidence: 'firewall_config.pdf' },
      { id: 'SR-2.4', requirement: 'Information flow enforcement', status: 'Compliant', evidence: 'network_diagram.pdf' },
      { id: 'SR-2.5', requirement: 'Physical access control', status: 'Partial', evidence: null }
    ]
  },
  {
    id: 'zone-3',
    name: 'Enterprise Zone',
    icon: 'Grid',
    description: 'Corporate IT network interfacing with OT systems',
    compliance: 71,
    requirements: [
      { id: 'SR-3.1', requirement: 'Communication integrity', status: 'Compliant', evidence: 'integrity_checks.pdf' },
      { id: 'SR-3.2', requirement: 'Communication confidentiality', status: 'Compliant', evidence: 'encryption_config.pdf' },
      { id: 'SR-3.3', requirement: 'Non-repudiation', status: 'Partial', evidence: null },
      { id: 'SR-3.4', requirement: 'Session management', status: 'Non-Compliant', evidence: null },
      { id: 'SR-3.5', requirement: 'Network segmentation', status: 'Compliant', evidence: 'vlan_config.pdf' }
    ]
  },
  {
    id: 'zone-4',
    name: 'DMZ Zone',
    icon: 'Connection',
    description: 'Demilitarized zone for secure OT-IT data exchange',
    compliance: 64,
    requirements: [
      { id: 'SR-4.1', requirement: 'Data flow enforcement', status: 'Partial', evidence: null },
      { id: 'SR-4.2', requirement: 'Proxy services', status: 'Partial', evidence: null },
      { id: 'SR-4.3', requirement: 'Application firewalls', status: 'Non-Compliant', evidence: null },
      { id: 'SR-4.4', requirement: 'Intrusion detection', status: 'Compliant', evidence: 'ids_config.pdf' }
    ]
  }
])

const activeZone = ref('zone-1')

// Gap analysis
const gaps = ref([
  { id: 1, severity: 'high', title: 'Missing Multi-Factor Authentication', description: 'MFA not implemented for remote access to control network', standard: 'SR-1.8', zone: 'Control Network Zone', targetDate: '2024-02-15', progress: 25 },
  { id: 2, severity: 'critical', title: 'Outdated Firmware on PLCs', description: 'Critical security patches missing on 12 PLC devices', standard: 'SR-7.7', zone: 'Control Network Zone', targetDate: '2024-01-30', progress: 60 },
  { id: 3, severity: 'medium', title: 'Incomplete Incident Response Plan', description: 'IR plan lacks specific OT incident procedures', standard: 'SR-5.1', zone: 'Enterprise Zone', targetDate: '2024-03-01', progress: 40 },
  { id: 4, severity: 'high', title: 'No Network Segmentation between Zones', description: 'Lack of proper firewalling between control and enterprise networks', standard: 'SR-3.5', zone: 'DMZ Zone', targetDate: '2024-02-28', progress: 15 },
  { id: 5, severity: 'medium', title: 'Insufficient Logging & Monitoring', description: 'Security logs not centralized for OT devices', standard: 'SR-6.1', zone: 'Safety System Zone', targetDate: '2024-03-15', progress: 55 }
])

// Audit trail
const auditTrail = ref([
  { id: 1, action: 'Compliance Assessment', detail: 'Q4 2023 compliance audit completed for all zones', date: '2024-01-10', auditor: 'Deloitte', status: 'passed', evidence: 'q4_2023_audit_report.pdf', type: 'success' },
  { id: 2, action: 'Remediation Review', detail: 'Gap remediation status review for high severity items', date: '2024-01-05', auditor: 'Internal Audit', status: 'in-progress', evidence: null, type: 'warning' },
  { id: 3, action: 'Policy Update', detail: 'Access control policy updated to meet SR-1 requirements', date: '2023-12-20', auditor: 'Security Team', status: 'passed', evidence: 'access_policy_v3.pdf', type: 'success' },
  { id: 4, action: 'Technical Assessment', detail: 'Network segmentation vulnerability scan', date: '2023-12-15', auditor: 'External Consultant', status: 'failed', evidence: 'scan_report.pdf', type: 'danger' }
])

// Chart refs
const trendChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let statusChart: echarts.ECharts | null = null

// Helper functions
const getScoreColor = (score: number) => {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

const getProgressColor = (progress: number) => {
  if (progress >= 80) return '#10b981'
  if (progress >= 50) return '#3b82f6'
  if (progress >= 25) return '#f59e0b'
  return '#ef4444'
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'Compliant': return 'success'
    case 'Partial': return 'warning'
    case 'Non-Compliant': return 'danger'
    default: return 'info'
  }
}

// Initialize trend chart
const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0, data: ['Compliance Score', 'Requirements Met'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] },
    yAxis: [
      { type: 'value', name: 'Compliance %', min: 0, max: 100 },
      { type: 'value', name: 'Requirements', min: 0, max: 200 }
    ],
    series: [
      { name: 'Compliance Score', type: 'line', data: [62, 65, 68, 70, 72, 73, 74, 75, 76, 77, 78, 78], lineStyle: { color: '#3b82f6', width: 3 }, smooth: true, symbol: 'circle', yAxisIndex: 0 },
      { name: 'Requirements Met', type: 'bar', data: [98, 102, 106, 109, 112, 114, 116, 118, 121, 124, 126, 127], itemStyle: { color: '#10b981', borderRadius: [4, 4, 0, 0] }, yAxisIndex: 1 }
    ]
  }
  trendChart.setOption(option)
}

// Initialize status distribution chart
const initStatusChart = () => {
  if (!statusChartRef.value) return
  statusChart = echarts.init(statusChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 97, name: 'Compliant', itemStyle: { color: '#10b981' } },
        { value: 42, name: 'Partial', itemStyle: { color: '#f59e0b' } },
        { value: 24, name: 'Non-Compliant', itemStyle: { color: '#ef4444' } }
      ],
      label: { formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }
  statusChart.setOption(option)
}

// Event handlers
const runComplianceScan = () => {
  ElMessage.info('Compliance scan initiated. Analyzing all zones...')
  setTimeout(() => {
    ElMessage.success('Compliance scan completed. No new gaps identified.')
  }, 3000)
}

const exportReport = () => {
  ElMessage.info('Exporting compliance report...')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 2000)
}

const viewAuditHistory = () => {
  ElMessage.info('Viewing audit history')
}

const viewPillarDetails = (pillar: any) => {
  ElMessage.info(`Viewing details for: ${pillar.name}`)
}

const viewEvidence = (req: any) => {
  ElMessage.info(`Viewing evidence: ${req.evidence}`)
}

const uploadEvidence = (req: any) => {
  ElMessage.info(`Upload evidence for requirement: ${req.id}`)
}

const reviewRequirement = (req: any) => {
  ElMessage.info(`Reviewing requirement: ${req.id}`)
}

const addComment = (req: any) => {
  ElMessageBox.prompt('Add comment for this requirement', 'Add Comment', {
    confirmButtonText: 'Submit',
    cancelButtonText: 'Cancel'
  }).then(({ value }) => {
    ElMessage.success(`Comment added: ${value}`)
  }).catch(() => {})
}

const createRemediationPlan = () => {
  ElMessage.info('Creating remediation plan')
}

const remediateGap = (gap: any) => {
  ElMessageBox.confirm(`Start remediation for: ${gap.title}?`, 'Remediation', {
    confirmButtonText: 'Start',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    ElMessage.success(`Remediation started for ${gap.title}`)
  }).catch(() => {})
}

const viewAllAudits = () => {
  ElMessage.info('Viewing all audit records')
}

const downloadEvidence = (evidence: string) => {
  ElMessage.info(`Downloading: ${evidence}`)
}

const scheduleAudit = () => {
  ElMessage.info('Schedule audit dialog opened')
}

const generateComplianceReport = () => {
  ElMessage.info('Generating compliance report...')
}

const requestException = () => {
  ElMessageBox.prompt('Enter justification for compliance exception', 'Request Exception', {
    confirmButtonText: 'Submit',
    cancelButtonText: 'Cancel'
  }).then(({ value }) => {
    ElMessage.success(`Exception request submitted: ${value}`)
  }).catch(() => {})
}

const viewDocumentation = () => {
  ElMessage.info('Opening documentation library')
}

const refreshTrendChart = () => {
  if (trendChart) trendChart.setOption({ series: [] })
  initTrendChart()
  ElMessage.success('Chart refreshed')
}

const refreshStatusChart = () => {
  if (statusChart) statusChart.setOption({ series: [] })
  initStatusChart()
  ElMessage.success('Chart refreshed')
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
        initTrendChart()
        initStatusChart()
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (trendChart) trendChart.dispose()
  if (statusChart) statusChart.dispose()
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
.iec-container {
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

/* Score Section */
.score-section {
  margin-bottom: 24px;
}

.score-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.score-content {
  display: flex;
  align-items: center;
  gap: 48px;
  padding: 20px;
}

.score-gauge {
  flex-shrink: 0;
}

.score-text {
  text-align: center;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  display: block;
}

.score-label {
  font-size: 12px;
  color: #64748b;
}

.score-details {
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
}

.detail-item {
  min-width: 140px;
}

.detail-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* Pillars Section */
.pillars-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.pillars-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.pillar-card {
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.pillar-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.pillar-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.pillar-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.pillar-desc {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
  line-height: 1.4;
}

.pillar-progress {
  margin-bottom: 8px;
}

.pillar-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.pillar-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.pillar-status.compliant {
  background: #10b98120;
  color: #10b981;
}

.pillar-status.partial {
  background: #f59e0b20;
  color: #f59e0b;
}

.pillar-status.non-compliant {
  background: #ef444420;
  color: #ef4444;
}

/* Zones Section */
.zones-section {
  margin-bottom: 32px;
}

.zone-tabs {
  border-radius: 12px;
}

.zone-tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.zone-content {
  padding: 20px;
}

.zone-description {
  background: #f8fafc;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: #475569;
  margin-bottom: 20px;
}

.requirements-table {
  overflow-x: auto;
}

.no-evidence {
  color: #cbd5e1;
}

/* Charts Section */
.charts-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 32px;
}

.chart-card {
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

.trend-chart,
.status-chart {
  height: 300px;
  width: 100%;
}

/* Gap Section */
.gap-section {
  margin-bottom: 32px;
}

.gap-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.gap-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.gap-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.gap-severity {
  width: 70px;
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.gap-severity.critical {
  background: #ef444420;
  color: #ef4444;
}

.gap-severity.high {
  background: #f59e0b20;
  color: #f59e0b;
}

.gap-severity.medium {
  background: #eab30820;
  color: #eab308;
}

.gap-severity.low {
  background: #10b98120;
  color: #10b981;
}

.gap-info {
  flex: 1;
}

.gap-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.gap-description {
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
}

.gap-meta {
  display: flex;
  gap: 20px;
  font-size: 11px;
  color: #94a3b8;
}

.gap-progress {
  width: 120px;
  text-align: center;
}

.progress-text {
  font-size: 11px;
  color: #3b82f6;
  margin-top: 4px;
  display: block;
}

/* Audit Section */
.audit-section {
  margin-bottom: 24px;
}

.audit-card {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.audit-timeline {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.audit-item-card {
  margin-bottom: 12px;
  border-radius: 8px;
}

.audit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.audit-action {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.audit-detail {
  font-size: 13px;
  color: #475569;
  margin-bottom: 8px;
}

.auditor {
  font-size: 11px;
  color: #94a3b8;
}

.audit-evidence {
  margin-top: 8px;
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
  .pillars-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .score-content {
    flex-direction: column;
    text-align: center;
  }

  .score-details {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .pillars-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .gap-item {
    flex-direction: column;
  }

  .gap-progress {
    width: 100%;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }

  .score-details {
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .detail-item {
    text-align: center;
  }
}
</style>