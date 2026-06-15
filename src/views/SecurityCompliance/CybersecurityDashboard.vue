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
          <span class="loading-title">Loading Cybersecurity Dashboard</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">IBMS Security & Compliance Monitoring System</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="cybersecurity-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Cybersecurity Dashboard</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>Cybersecurity Dashboard</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runSecurityScan">
          <el-icon><Refresh /></el-icon>
          Run Security Scan
        </el-button>
        <el-button type="info" plain @click="generateReport">
          <el-icon><Document /></el-icon>
          Generate Report
        </el-button>
      </div>
    </div>

    <!-- Security Score Cards -->
    <div class="stats-grid">
      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Overall Security Score</div>
            <div class="stat-value" :class="getScoreClass(securityScore)">{{ securityScore }}%</div>
            <div class="stat-trend positive">↑ {{ scoreChange }}% from last month</div>
          </div>
          <div class="stat-icon security">
            <el-icon :size="40"><Lock /></el-icon>
          </div>
        </div>
        <el-progress :percentage="securityScore" :stroke-width="8" :color="getScoreColor(securityScore)" />
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Active Threats</div>
            <div class="stat-value critical">{{ activeThreats }}</div>
            <div class="stat-trend negative">↑ {{ threatIncrease }} this week</div>
          </div>
          <div class="stat-icon threat">
            <el-icon :size="40"><WarningFilled /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Vulnerabilities</div>
            <div class="stat-value warning">{{ vulnerabilities.total }}</div>
            <div class="stat-trend">{{ vulnerabilities.critical }} critical, {{ vulnerabilities.high }} high</div>
          </div>
          <div class="stat-icon vuln">
            <el-icon :size="40"><Warning /></el-icon>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <div class="stat-content">
          <div class="stat-info">
            <div class="stat-label">Compliance Status</div>
            <div class="stat-value">{{ complianceRate }}%</div>
            <div class="stat-trend">{{ compliantStandards }}/{{ totalStandards }} standards met</div>
          </div>
          <div class="stat-icon compliance">
            <el-icon :size="40"><CircleCheck /></el-icon>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Threat Intelligence & Attack Vector Charts -->
    <div class="charts-row">
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Threat Intelligence (Last 30 Days)</span>
            <el-button text type="primary" @click="refreshThreatChart">Refresh</el-button>
          </div>
        </template>
        <div ref="threatChartRef" class="threat-chart"></div>
      </el-card>

      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><PieChart /></el-icon> Attack Vector Distribution</span>
            <el-button text type="primary" @click="refreshAttackChart">Refresh</el-button>
          </div>
        </template>
        <div ref="attackChartRef" class="attack-chart"></div>
      </el-card>
    </div>

    <!-- Security Events Timeline -->
    <el-card class="events-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><List /></el-icon> Security Events Timeline</span>
          <div class="event-filters">
            <el-select v-model="eventFilter" size="small" placeholder="Filter by severity" style="width: 140px">
              <el-option label="All Events" value="all" />
              <el-option label="Critical" value="critical" />
              <el-option label="High" value="high" />
              <el-option label="Medium" value="medium" />
              <el-option label="Low" value="low" />
            </el-select>
            <el-date-picker v-model="eventDateRange" type="daterange" size="small" range-separator="to" start-placeholder="Start" end-placeholder="End" style="width: 260px" />
          </div>
        </div>
      </template>
      <div class="events-timeline">
        <el-timeline>
          <el-timeline-item v-for="event in filteredEvents" :key="event.id" :type="getEventType(event.severity)" :timestamp="event.time" placement="top" size="large">
            <el-card shadow="hover" class="event-card">
              <div class="event-content">
                <div class="event-header">
                  <el-tag :type="getSeverityTagType(event.severity)" size="large">{{ event.severity.toUpperCase() }}</el-tag>
                  <span class="event-title">{{ event.title }}</span>
                </div>
                <div class="event-details">
                  <span><el-icon><Location /></el-icon> {{ event.source }}</span>
                  <span><el-icon><User /></el-icon> {{ event.target }}</span>
                  <span><el-icon><Monitor /></el-icon> {{ event.protocol }}</span>
                </div>
                <div class="event-description">{{ event.description }}</div>
                <div class="event-actions">
                  <el-button size="small" type="primary" plain @click="investigateEvent(event)">Investigate</el-button>
                  <el-button size="small" type="success" plain @click="resolveEvent(event)">Resolve</el-button>
                  <el-button size="small" type="info" plain @click="viewEventDetails(event)">Details</el-button>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-card>

    <!-- Vulnerability Management & Device Security -->
    <div class="vulnerability-row">
      <el-card class="vuln-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Warning /></el-icon> Vulnerability Management</span>
            <el-button text type="primary" @click="viewAllVulnerabilities">View All</el-button>
          </div>
        </template>
        <div class="vuln-list">
          <div v-for="vuln in topVulnerabilities" :key="vuln.id" class="vuln-item">
            <div class="vuln-severity" :class="vuln.severity">{{ vuln.severity }}</div>
            <div class="vuln-info">
              <div class="vuln-name">{{ vuln.name }}</div>
              <div class="vuln-desc">{{ vuln.description }}</div>
              <div class="vuln-meta">
                <span>CVE: {{ vuln.cve }}</span>
                <span>CVSS: {{ vuln.cvss }}</span>
                <span>Affected: {{ vuln.affectedDevices }} devices</span>
              </div>
            </div>
            <el-button size="small" type="danger" plain @click="patchVulnerability(vuln)">Patch</el-button>
          </div>
        </div>
      </el-card>

      <el-card class="device-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Monitor /></el-icon> Device Security Posture</span>
            <el-input v-model="deviceSearch" placeholder="Search devices..." size="small" style="width: 180px" clearable />
          </div>
        </template>
        <div class="device-security-list">
          <div v-for="device in filteredDevices" :key="device.id" class="device-security-item">
            <div class="device-icon" :class="getDeviceStatusClass(device.status)">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="device-info">
              <div class="device-name">{{ device.name }}</div>
              <div class="device-ip">{{ device.ip }}</div>
            </div>
            <div class="device-security-score">
              <el-progress type="circle" :percentage="device.securityScore" :width="50" :stroke-width="6" :color="getScoreColor(device.securityScore)" />
            </div>
            <div class="device-compliance">
              <el-tag v-for="standard in device.compliance" :key="standard" size="small" type="success">{{ standard }}</el-tag>
            </div>
            <el-dropdown trigger="click">
              <el-button size="small" type="info" plain>
                Actions <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="scanDevice(device)">Scan Device</el-dropdown-item>
                  <el-dropdown-item @click="isolateDevice(device)">Isolate Device</el-dropdown-item>
                  <el-dropdown-item @click="viewDeviceLogs(device)">View Logs</el-dropdown-item>
                  <el-dropdown-item divided @click="applyPolicy(device)">Apply Policy</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Compliance Standards & Audit Trail -->
    <div class="compliance-row">
      <el-card class="compliance-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Checked /></el-icon> Compliance Standards</span>
            <el-button text type="primary" @click="viewComplianceDetails">Details</el-button>
          </div>
        </template>
        <div class="standards-grid">
          <div v-for="standard in complianceStandards" :key="standard.name" class="standard-item">
            <div class="standard-header">
              <span class="standard-name">{{ standard.name }}</span>
              <el-tag :type="standard.compliant ? 'success' : 'danger'" size="small">{{ standard.compliant ? 'Compliant' : 'Non-Compliant' }}</el-tag>
            </div>
            <el-progress :percentage="standard.progress" :stroke-width="8" :color="standard.compliant ? '#10b981' : '#ef4444'" />
            <div class="standard-requirements">{{ standard.requirementsMet }}/{{ standard.totalRequirements }} requirements met</div>
            <div class="standard-last-audit">Last Audit: {{ standard.lastAudit }}</div>
          </div>
        </div>
      </el-card>

      <el-card class="audit-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Document /></el-icon> Recent Audit Trail</span>
            <el-button text type="primary" @click="viewFullAuditLog">View All</el-button>
          </div>
        </template>
        <div class="audit-list">
          <div v-for="audit in auditTrail" :key="audit.id" class="audit-item">
            <div class="audit-icon" :class="audit.actionType">
              <el-icon><component :is="getAuditIcon(audit.actionType)" /></el-icon>
            </div>
            <div class="audit-info">
              <div class="audit-action">{{ audit.action }}</div>
              <div class="audit-detail">{{ audit.detail }}</div>
              <div class="audit-meta">{{ audit.user }} • {{ audit.time }}</div>
            </div>
            <div class="audit-status">
              <el-tag :type="audit.status === 'success' ? 'success' : 'danger'" size="small">{{ audit.status }}</el-tag>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Security Recommendations -->
    <el-card class="recommendations-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span><el-icon><Star /></el-icon> Security Recommendations</span>
          <el-button text type="primary" @click="refreshRecommendations">Refresh</el-button>
        </div>
      </template>
      <div class="recommendations-grid">
        <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
          <div class="rec-priority" :class="rec.priority">{{ rec.priority }}</div>
          <div class="rec-content">
            <div class="rec-title">{{ rec.title }}</div>
            <div class="rec-description">{{ rec.description }}</div>
            <div class="rec-impact">Impact: {{ rec.impact }}</div>
          </div>
          <el-button size="small" type="primary" plain @click="applyRecommendation(rec)">Apply</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import {
  Refresh, Document, Lock, WarningFilled, Warning, CircleCheck, TrendCharts,
  PieChart, List, Location, User, Monitor, Cpu, ArrowDown, Checked, Star,
  Edit, Delete, Key, Setting, InfoFilled
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Loading Cybersecurity Dashboard...')

const loadingMessages = [
  'Loading Cybersecurity Dashboard...',
  'Analyzing threat intelligence...',
  'Scanning for vulnerabilities...',
  'Security systems operational!'
]

// Security scores
const securityScore = ref(87)
const scoreChange = ref(5)
const activeThreats = ref(3)
const threatIncrease = ref(2)
const vulnerabilities = ref({
  total: 24,
  critical: 4,
  high: 7,
  medium: 8,
  low: 5
})
const complianceRate = ref(82)
const compliantStandards = ref(9)
const totalStandards = ref(11)

// Security events
const eventFilter = ref('all')
const eventDateRange = ref<[Date, Date] | null>(null)
const securityEvents = ref([
  { id: 1, severity: 'critical', title: 'Failed Login Attempts Detected', source: '192.168.1.45', target: 'BACnet Gateway', protocol: 'BACnet', description: 'Multiple failed authentication attempts from unknown IP address. Brute force pattern detected.', time: '2024-01-15 09:30:22' },
  { id: 2, severity: 'high', title: 'Unusual Network Traffic', source: '10.0.0.87', target: 'HVAC Controller', protocol: 'Modbus', description: 'Unexpected write commands detected on HVAC controller during non-operational hours.', time: '2024-01-15 08:15:45' },
  { id: 3, severity: 'high', title: 'Privilege Escalation Attempt', source: 'User: jdoe', target: 'SCADA Server', protocol: 'RDP', description: 'User attempted to access restricted configuration panels without authorization.', time: '2024-01-14 23:45:12' },
  { id: 4, severity: 'medium', title: 'Suspicious USB Device Connected', source: 'Workstation WS-023', target: 'Engineering Console', protocol: 'USB', description: 'Unrecognized USB storage device connected to engineering workstation.', time: '2024-01-14 14:20:33' },
  { id: 5, severity: 'medium', title: 'Outdated Firmware Detected', source: 'Chiller Controller', target: 'Device Management', protocol: 'SNMP', description: 'Device firmware version is 6 months behind current security patches.', time: '2024-01-14 10:05:18' },
  { id: 6, severity: 'low', title: 'Default Credentials Still Active', source: 'Security Camera NVR', target: 'Device Inventory', protocol: 'ONVIF', description: 'Device still using factory default credentials. Change recommended.', time: '2024-01-13 16:30:44' },
  { id: 7, severity: 'critical', title: 'Ransomware Indicator Detected', source: 'File Server', target: 'Backup System', protocol: 'SMB', description: 'Pattern matching known ransomware signatures detected on file shares.', time: '2024-01-13 11:22:09' },
  { id: 8, severity: 'high', title: 'Unauthorized Configuration Change', source: 'Remote Console', target: 'UPS Controller', protocol: 'SNMP', description: 'UPS power configuration was modified without change request approval.', time: '2024-01-13 08:45:30' }
])

const filteredEvents = computed(() => {
  let events = securityEvents.value
  if (eventFilter.value !== 'all') {
    events = events.filter(e => e.severity === eventFilter.value)
  }
  if (eventDateRange.value && eventDateRange.value.length === 2) {
    const [start, end] = eventDateRange.value
    events = events.filter(e => {
      const eventTime = new Date(e.time)
      return eventTime >= start && eventTime <= end
    })
  }
  return events
})

// Vulnerabilities
const topVulnerabilities = ref([
  { id: 1, severity: 'critical', name: 'CVE-2024-1234 - BACnet Gateway RCE', description: 'Remote code execution vulnerability in BACnet gateway firmware', cve: 'CVE-2024-1234', cvss: '9.8', affectedDevices: 12 },
  { id: 2, severity: 'high', name: 'Modbus Protocol Weak Authentication', description: 'Modbus devices lack proper authentication mechanisms', cve: 'CVE-2024-5678', cvss: '7.5', affectedDevices: 34 },
  { id: 3, severity: 'high', name: 'SNMP v1/v2 Enabled', description: 'Insecure SNMP versions exposing community strings', cve: 'CVE-2024-9012', cvss: '7.2', affectedDevices: 23 },
  { id: 4, severity: 'medium', name: 'TLS 1.0 Still Supported', description: 'Deprecated TLS version on web interfaces', cve: 'CVE-2024-3456', cvss: '5.9', affectedDevices: 18 }
])

// Device security
const deviceSearch = ref('')
const devices = ref([
  { id: 1, name: 'BACnet Gateway', ip: '192.168.1.10', status: 'at-risk', securityScore: 72, compliance: ['IEC62443', 'NIST'] },
  { id: 2, name: 'HVAC Controller', ip: '192.168.1.20', status: 'critical', securityScore: 45, compliance: [] },
  { id: 3, name: 'SCADA Server', ip: '192.168.1.30', status: 'secure', securityScore: 94, compliance: ['IEC62443', 'NIST', 'ISO27001'] },
  { id: 4, name: 'Chiller PLC', ip: '192.168.1.40', status: 'at-risk', securityScore: 68, compliance: ['IEC62443'] },
  { id: 5, name: 'UPS Controller', ip: '192.168.1.50', status: 'warning', securityScore: 55, compliance: [] },
  { id: 6, name: 'Security NVR', ip: '192.168.1.60', status: 'secure', securityScore: 88, compliance: ['NIST'] },
  { id: 7, name: 'Access Control Panel', ip: '192.168.1.70', status: 'secure', securityScore: 91, compliance: ['IEC62443', 'ISO27001'] }
])

const filteredDevices = computed(() => {
  if (!deviceSearch.value) return devices.value
  return devices.value.filter(d =>
      d.name.toLowerCase().includes(deviceSearch.value.toLowerCase()) ||
      d.ip.includes(deviceSearch.value)
  )
})

// Compliance standards
const complianceStandards = ref([
  { name: 'IEC 62443', compliant: true, progress: 100, requirementsMet: 24, totalRequirements: 24, lastAudit: '2024-01-10' },
  { name: 'ISO 27001', compliant: true, progress: 98, requirementsMet: 45, totalRequirements: 46, lastAudit: '2024-01-05' },
  { name: 'NIST SP 800-82', compliant: true, progress: 92, requirementsMet: 33, totalRequirements: 36, lastAudit: '2024-01-12' },
  { name: 'GDPR', compliant: true, progress: 95, requirementsMet: 19, totalRequirements: 20, lastAudit: '2024-01-08' },
  { name: 'NERC CIP', compliant: false, progress: 45, requirementsMet: 9, totalRequirements: 20, lastAudit: '2023-12-15' }
])

// Audit trail
const auditTrail = ref([
  { id: 1, actionType: 'config', action: 'Configuration Change', detail: 'Firewall rule updated to block SSH from external networks', user: 'admin@ibms', time: '2024-01-15 10:30:22', status: 'success' },
  { id: 2, actionType: 'login', action: 'Login Attempt', detail: 'Successful login from IP 192.168.1.100', user: 'jsmith', time: '2024-01-15 09:15:44', status: 'success' },
  { id: 3, actionType: 'policy', action: 'Policy Applied', detail: 'Security policy v2.3 applied to all BACnet devices', user: 'security@ibms', time: '2024-01-15 08:00:00', status: 'success' },
  { id: 4, actionType: 'alert', action: 'Alert Acknowledged', detail: 'Critical alert #1234 acknowledged', user: 'operator1', time: '2024-01-14 23:45:12', status: 'success' },
  { id: 5, actionType: 'config', action: 'User Permission Change', detail: 'User jdoe granted read-only access to HVAC group', user: 'admin@ibms', time: '2024-01-14 14:20:33', status: 'success' },
  { id: 6, actionType: 'security', action: 'Security Scan', detail: 'Full vulnerability scan completed. 24 vulnerabilities found.', user: 'system', time: '2024-01-14 10:05:18', status: 'success' }
])

// Recommendations
const recommendations = ref([
  { id: 1, priority: 'critical', title: 'Update BACnet Gateway Firmware', description: 'Critical security patch available for CVE-2024-1234 affecting BACnet gateway devices', impact: 'Prevents remote code execution vulnerability' },
  { id: 2, priority: 'high', title: 'Enable MFA for Administrative Access', description: 'Multi-factor authentication not enforced for privileged accounts', impact: 'Reduces risk of credential compromise' },
  { id: 3, priority: 'high', title: 'Disable SNMP v1/v2', description: 'Upgrade SNMP to v3 with authentication and encryption', impact: 'Prevents community string exposure' },
  { id: 4, priority: 'medium', title: 'Segment OT Network', description: 'Implement network segmentation between OT and IT networks', impact: 'Contains potential breaches' },
  { id: 5, priority: 'medium', title: 'Implement Log Monitoring', description: 'Deploy SIEM solution for centralized log collection and alerting', impact: 'Improved threat detection' }
])

// Chart refs
const threatChartRef = ref<HTMLElement>()
const attackChartRef = ref<HTMLElement>()
let threatChart: echarts.ECharts | null = null
let attackChart: echarts.ECharts | null = null

// Initialize threat chart
const initThreatChart = () => {
  if (!threatChartRef.value) return
  threatChart = echarts.init(threatChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0, textStyle: { color: '#e2e8f0' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Week 1', 'Week 2', 'Week 3', 'Week 4'], axisLabel: { color: '#94a3b8' } },
    yAxis: { type: 'value', name: 'Number of Threats', nameTextStyle: { color: '#94a3b8' }, axisLabel: { color: '#94a3b8' } },
    series: [
      { name: 'Critical', type: 'line', data: [8, 12, 7, 4], lineStyle: { color: '#ef4444', width: 2 }, symbol: 'circle', symbolSize: 6 },
      { name: 'High', type: 'line', data: [15, 18, 14, 11], lineStyle: { color: '#f59e0b', width: 2 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Medium', type: 'line', data: [22, 25, 20, 18], lineStyle: { color: '#eab308', width: 2 }, symbol: 'circle', symbolSize: 6 },
      { name: 'Low', type: 'line', data: [30, 28, 25, 22], lineStyle: { color: '#10b981', width: 2 }, symbol: 'circle', symbolSize: 6 }
    ]
  }
  threatChart.setOption(option)
}

// Initialize attack chart
const initAttackChart = () => {
  if (!attackChartRef.value) return
  attackChart = echarts.init(attackChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: '#e2e8f0' } },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: 35, name: 'Brute Force', itemStyle: { color: '#ef4444' } },
        { value: 28, name: 'Malware', itemStyle: { color: '#f59e0b' } },
        { value: 18, name: 'Phishing', itemStyle: { color: '#eab308' } },
        { value: 12, name: 'Man-in-Middle', itemStyle: { color: '#8b5cf6' } },
        { value: 7, name: 'Insider Threat', itemStyle: { color: '#ec489a' } }
      ],
      label: { color: '#e2e8f0', formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }
  attackChart.setOption(option)
}

// Helper functions
const getScoreClass = (score: number) => {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  if (score >= 40) return 'warning'
  return 'critical'
}

const getScoreColor = (score: number) => {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

const getEventType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getSeverityTagType = (severity: string) => {
  switch (severity) {
    case 'critical': return 'danger'
    case 'high': return 'warning'
    case 'medium': return 'primary'
    default: return 'info'
  }
}

const getDeviceStatusClass = (status: string) => {
  switch (status) {
    case 'secure': return 'secure'
    case 'at-risk': return 'at-risk'
    case 'warning': return 'warning'
    case 'critical': return 'critical'
    default: return 'secure'
  }
}

const getAuditIcon = (actionType: string) => {
  switch (actionType) {
    case 'config': return 'Setting'
    case 'login': return 'Key'
    case 'policy': return 'Document'
    case 'alert': return 'Warning'
    case 'security': return 'Lock'
    default: return 'InfoFilled'
  }
}

// Event handlers
const runSecurityScan = () => {
  ElMessage.info('Security scan initiated. This may take a few minutes...')
  setTimeout(() => {
    ElMessage.success('Security scan completed. No new threats detected.')
  }, 3000)
}

const generateReport = () => {
  ElMessage.info('Generating security report...')
  setTimeout(() => {
    ElMessage.success('Report generated successfully')
  }, 2000)
}

const investigateEvent = (event: any) => {
  ElMessage.info(`Investigating event: ${event.title}`)
}

const resolveEvent = (event: any) => {
  ElMessageBox.confirm(`Mark event "${event.title}" as resolved?`, 'Confirm', {
    confirmButtonText: 'Resolve',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    securityEvents.value = securityEvents.value.filter(e => e.id !== event.id)
    ElMessage.success('Event resolved')
  }).catch(() => {})
}

const viewEventDetails = (event: any) => {
  ElMessageBox.alert(
      `Event: ${event.title}\nSource: ${event.source}\nTarget: ${event.target}\nProtocol: ${event.protocol}\nTime: ${event.time}\n\nDescription: ${event.description}\n\nRecommended Action: Review logs and implement containment measures.`,
      'Event Details',
      { confirmButtonText: 'OK', type: 'warning' }
  )
}

const viewAllVulnerabilities = () => {
  ElMessage.info('Viewing all vulnerabilities')
}

const patchVulnerability = (vuln: any) => {
  ElMessageBox.confirm(`Apply patch for ${vuln.name}?`, 'Patch Vulnerability', {
    confirmButtonText: 'Apply Patch',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    topVulnerabilities.value = topVulnerabilities.value.filter(v => v.id !== vuln.id)
    vulnerabilities.value.total--
    if (vuln.severity === 'critical') vulnerabilities.value.critical--
    if (vuln.severity === 'high') vulnerabilities.value.high--
    ElMessage.success('Patch applied successfully')
  }).catch(() => {})
}

const scanDevice = (device: any) => {
  ElMessage.info(`Scanning device: ${device.name}`)
  setTimeout(() => {
    ElMessage.success(`Scan completed for ${device.name}`)
  }, 2000)
}

const isolateDevice = (device: any) => {
  ElMessageBox.confirm(`Isolate ${device.name} from the network?`, 'Isolate Device', {
    confirmButtonText: 'Isolate',
    cancelButtonText: 'Cancel',
    type: 'danger'
  }).then(() => {
    ElMessage.warning(`${device.name} has been isolated from the network`)
  }).catch(() => {})
}

const viewDeviceLogs = (device: any) => {
  ElMessage.info(`Viewing logs for ${device.name}`)
}

const applyPolicy = (device: any) => {
  ElMessage.info(`Applying security policy to ${device.name}`)
}

const viewComplianceDetails = () => {
  ElMessage.info('Viewing compliance details')
}

const viewFullAuditLog = () => {
  ElMessage.info('Viewing full audit log')
}

const refreshRecommendations = () => {
  ElMessage.info('Refreshing recommendations')
}

const applyRecommendation = (rec: any) => {
  ElMessage.info(`Applying recommendation: ${rec.title}`)
}

const refreshThreatChart = () => {
  if (threatChart) threatChart.setOption({ series: [] })
  initThreatChart()
  ElMessage.success('Chart refreshed')
}

const refreshAttackChart = () => {
  if (attackChart) attackChart.setOption({ series: [] })
  initAttackChart()
  ElMessage.success('Chart refreshed')
}

// Lifecycle
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
        initThreatChart()
        initAttackChart()
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (threatChart) threatChart.dispose()
  if (attackChart) attackChart.dispose()
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
.cybersecurity-container {
  padding: 20px;
  background: #0f172a;
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
  color: #e2e8f0;
  margin: 0 0 8px 0;
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
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-value.excellent { color: #10b981; }
.stat-value.good { color: #3b82f6; }
.stat-value.warning { color: #f59e0b; }
.stat-value.critical { color: #ef4444; }

.stat-trend {
  font-size: 12px;
}

.stat-trend.positive { color: #10b981; }
.stat-trend.negative { color: #ef4444; }

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.security { background: #3b82f620; color: #3b82f6; }
.stat-icon.threat { background: #ef444420; color: #ef4444; }
.stat-icon.vuln { background: #f59e0b20; color: #f59e0b; }
.stat-icon.compliance { background: #10b98120; color: #10b981; }

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #e2e8f0;
  font-weight: 600;
}

.threat-chart,
.attack-chart {
  height: 320px;
  width: 100%;
}

/* Events Card */
.events-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  margin-bottom: 24px;
}

.event-filters {
  display: flex;
  gap: 12px;
}

.events-timeline {
  max-height: 500px;
  overflow-y: auto;
  padding: 16px;
}

.event-card {
  background: #0f172a;
  border: 1px solid #334155;
  margin-bottom: 12px;
}

.event-content {
  padding: 8px;
}

.event-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.event-title {
  font-size: 16px;
  font-weight: 600;
  color: #e2e8f0;
}

.event-details {
  display: flex;
  gap: 24px;
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 12px;
}

.event-details span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.event-description {
  font-size: 13px;
  color: #cbd5e1;
  margin-bottom: 12px;
  line-height: 1.5;
}

.event-actions {
  display: flex;
  gap: 8px;
}

/* Vulnerability Row */
.vulnerability-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.vuln-card,
.device-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.vuln-list {
  max-height: 400px;
  overflow-y: auto;
}

.vuln-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #334155;
}

.vuln-severity {
  width: 80px;
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.vuln-severity.critical { background: #ef444420; color: #ef4444; }
.vuln-severity.high { background: #f59e0b20; color: #f59e0b; }
.vuln-severity.medium { background: #eab30820; color: #eab308; }
.vuln-severity.low { background: #10b98120; color: #10b981; }

.vuln-info {
  flex: 1;
}

.vuln-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.vuln-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 6px;
}

.vuln-meta {
  display: flex;
  gap: 16px;
  font-size: 11px;
  color: #64748b;
}

/* Device Security List */
.device-security-list {
  max-height: 400px;
  overflow-y: auto;
}

.device-security-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #334155;
}

.device-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.device-icon.secure { background: #10b98120; color: #10b981; }
.device-icon.at-risk { background: #f59e0b20; color: #f59e0b; }
.device-icon.warning { background: #eab30820; color: #eab308; }
.device-icon.critical { background: #ef444420; color: #ef4444; }

.device-info {
  flex: 1;
}

.device-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.device-ip {
  font-size: 11px;
  color: #64748b;
  font-family: monospace;
}

.device-compliance {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

/* Compliance Row */
.compliance-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.compliance-card,
.audit-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.standards-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.standard-item {
  padding: 12px;
  background: #0f172a;
  border-radius: 8px;
}

.standard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.standard-name {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
}

.standard-requirements {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 6px;
}

.standard-last-audit {
  font-size: 10px;
  color: #64748b;
  margin-top: 4px;
}

/* Audit Trail */
.audit-list {
  max-height: 300px;
  overflow-y: auto;
}

.audit-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #334155;
}

.audit-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.audit-icon.config { background: #3b82f620; color: #3b82f6; }
.audit-icon.login { background: #10b98120; color: #10b981; }
.audit-icon.policy { background: #8b5cf620; color: #8b5cf6; }
.audit-icon.alert { background: #f59e0b20; color: #f59e0b; }
.audit-icon.security { background: #ef444420; color: #ef4444; }

.audit-info {
  flex: 1;
}

.audit-action {
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
}

.audit-detail {
  font-size: 11px;
  color: #94a3b8;
}

.audit-meta {
  font-size: 10px;
  color: #64748b;
  margin-top: 2px;
}

/* Recommendations Card */
.recommendations-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #0f172a;
  border-radius: 10px;
}

.rec-priority {
  width: 70px;
  padding: 4px 8px;
  border-radius: 6px;
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.rec-priority.critical { background: #ef444420; color: #ef4444; }
.rec-priority.high { background: #f59e0b20; color: #f59e0b; }
.rec-priority.medium { background: #eab30820; color: #eab308; }
.rec-priority.low { background: #10b98120; color: #10b981; }

.rec-content {
  flex: 1;
}

.rec-title {
  font-size: 14px;
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.rec-description {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.rec-impact {
  font-size: 11px;
  color: #3b82f6;
}

/* Responsive */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .charts-row,
  .vulnerability-row,
  .compliance-row {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .event-filters {
    flex-direction: column;
  }
}
</style>