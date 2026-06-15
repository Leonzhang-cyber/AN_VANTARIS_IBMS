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
          <span class="loading-title">Loading Device Security</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">{{ loadingMessage }}</div>
        <div class="loading-subtip">Comprehensive Device Security Posture Management</div>
      </div>
    </div>
  </div>

  <!-- Main Content -->
  <div v-else class="device-security-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2 class="page-title">Device Security</h2>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">Home</el-breadcrumb-item>
          <el-breadcrumb-item>Security & Compliance</el-breadcrumb-item>
          <el-breadcrumb-item>Device Security</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="runDeviceScan">
          <el-icon><Refresh /></el-icon>
          Run Device Scan
        </el-button>
        <el-button type="success" plain @click="exportDeviceReport">
          <el-icon><Download /></el-icon>
          Export Report
        </el-button>
        <el-button type="info" plain @click="configurePolicies">
          <el-icon><Setting /></el-icon>
          Configure Policies
        </el-button>
      </div>
    </div>

    <!-- Security Posture Summary -->
    <div class="summary-section">
      <el-card class="summary-card" shadow="hover">
        <div class="summary-grid">
          <div class="summary-item">
            <div class="summary-label">Total Devices</div>
            <div class="summary-value">{{ totalDevices }}</div>
            <div class="summary-sub">Managed endpoints</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Compliant Devices</div>
            <div class="summary-value success">{{ compliantDevices }}</div>
            <div class="summary-sub">{{ complianceRate }}% compliance</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Non-Compliant</div>
            <div class="summary-value critical">{{ nonCompliantDevices }}</div>
            <div class="summary-sub">Requires attention</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">At-Risk Devices</div>
            <div class="summary-value warning">{{ atRiskDevices }}</div>
            <div class="summary-sub">Critical vulnerabilities</div>
          </div>
          <div class="summary-item">
            <div class="summary-label">Average Security Score</div>
            <div class="summary-value">{{ avgSecurityScore }}%</div>
            <el-progress :percentage="avgSecurityScore" :stroke-width="6" :color="getScoreColor(avgSecurityScore)" style="margin-top: 8px" />
          </div>
        </div>
      </el-card>
    </div>

    <!-- Security Status Charts -->
    <div class="charts-row">
      <!-- Device Security Distribution -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><PieChart /></el-icon> Device Security Distribution</span>
            <el-button text type="primary" @click="refreshDistributionChart">Refresh</el-button>
          </div>
        </template>
        <div ref="distributionChartRef" class="distribution-chart"></div>
      </el-card>

      <!-- Security Posture Trend -->
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><TrendCharts /></el-icon> Security Posture Trend</span>
            <el-button text type="primary" @click="refreshTrendChart">Refresh</el-button>
          </div>
        </template>
        <div ref="trendChartRef" class="trend-chart"></div>
      </el-card>
    </div>

    <!-- Device Inventory Table -->
    <div class="inventory-section">
      <el-card class="inventory-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Monitor /></el-icon> Device Inventory</span>
            <div class="inventory-filters">
              <el-select v-model="deviceTypeFilter" placeholder="Device Type" size="small" style="width: 130px" clearable>
                <el-option label="All Types" value="" />
                <el-option label="Server" value="server" />
                <el-option label="Workstation" value="workstation" />
                <el-option label="Network Device" value="network" />
                <el-option label="OT/IoT" value="ot" />
                <el-option label="Mobile" value="mobile" />
              </el-select>
              <el-select v-model="complianceFilter" placeholder="Compliance" size="small" style="width: 130px" clearable>
                <el-option label="All" value="" />
                <el-option label="Compliant" value="compliant" />
                <el-option label="Non-Compliant" value="non-compliant" />
                <el-option label="At-Risk" value="at-risk" />
              </el-select>
              <el-input v-model="deviceSearch" placeholder="Search devices..." size="small" style="width: 200px" clearable />
              <el-button type="primary" size="small" @click="applyFilters">Apply</el-button>
            </div>
          </div>
        </template>
        <el-table :data="filteredDevices" stripe style="width: 100%">
          <el-table-column prop="name" label="Device Name" width="180" />
          <el-table-column prop="type" label="Type" width="120">
            <template #default="{ row }">
              <el-tag :type="getDeviceTypeTag(row.type)" size="small">{{ row.type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="ip" label="IP Address" width="140" />
          <el-table-column prop="os" label="OS Version" width="140" />
          <el-table-column prop="securityScore" label="Security Score" width="120" sortable>
            <template #default="{ row }">
              <el-progress :percentage="row.securityScore" :stroke-width="6" :format="(p) => `${p}%`" :color="getScoreColor(row.securityScore)" />
            </template>
          </el-table-column>
          <el-table-column prop="complianceStatus" label="Compliance" width="110">
            <template #default="{ row }">
              <el-tag :type="getComplianceTagType(row.complianceStatus)" size="small">{{ row.complianceStatus }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastScan" label="Last Scan" width="140" />
          <el-table-column label="Actions" width="150" fixed="right">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="viewDeviceDetails(row)">Details</el-button>
              <el-button size="small" text type="warning" @click="remediateDevice(row)">Remediate</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Security Policies & Compliance Rules -->
    <div class="policies-section">
      <el-card class="policies-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Lock /></el-icon> Security Policies & Compliance Rules</span>
            <el-button type="primary" size="small" @click="createPolicy">Create Policy</el-button>
          </div>
        </template>
        <el-table :data="securityPolicies" stripe style="width: 100%">
          <el-table-column prop="name" label="Policy Name" min-width="200" />
          <el-table-column prop="category" label="Category" width="140" />
          <el-table-column prop="compliance" label="Compliance" width="120">
            <template #default="{ row }">
              <el-progress :percentage="row.compliance" :stroke-width="6" :format="(p) => `${p}%`" :color="getScoreColor(row.compliance)" />
            </template>
          </el-table-column>
          <el-table-column prop="affectedDevices" label="Affected Devices" width="120" />
          <el-table-column prop="status" label="Status" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'Active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="editPolicy(row)">Edit</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Compliance Violations & Remediation -->
    <div class="violations-section">
      <el-card class="violations-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><WarningFilled /></el-icon> Compliance Violations & Remediation</span>
            <el-button type="primary" size="small" @click="bulkRemediation">Bulk Remediation</el-button>
          </div>
        </template>
        <el-table :data="violations" stripe style="width: 100%">
          <el-table-column prop="device" label="Device" width="180" />
          <el-table-column prop="violation" label="Violation" min-width="250" />
          <el-table-column prop="severity" label="Severity" width="100">
            <template #default="{ row }">
              <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="detected" label="Detected" width="120" />
          <el-table-column prop="remediation" label="Remediation Action" width="180" />
          <el-table-column label="Actions" width="100">
            <template #default="{ row }">
              <el-button size="small" text type="primary" @click="fixViolation(row)">Fix</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- Endpoint Protection Status -->
    <div class="protection-section">
      <el-card class="protection-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span><el-icon><Cpu /></el-icon> Endpoint Protection Status</span>
            <el-button text type="primary" @click="refreshProtectionStatus">Refresh</el-button>
          </div>
        </template>
        <div class="protection-grid">
          <div class="protection-item">
            <div class="protection-label">Antivirus Coverage</div>
            <div class="protection-value">{{ antivirusCoverage }}%</div>
            <el-progress :percentage="antivirusCoverage" :stroke-width="8" :color="getScoreColor(antivirusCoverage)" />
            <div class="protection-detail">{{ antivirusProtected }}/{{ totalDevices }} devices protected</div>
          </div>
          <div class="protection-item">
            <div class="protection-label">Firewall Enabled</div>
            <div class="protection-value">{{ firewallEnabled }}%</div>
            <el-progress :percentage="firewallEnabled" :stroke-width="8" :color="getScoreColor(firewallEnabled)" />
            <div class="protection-detail">{{ firewallActive }}/{{ totalDevices }} devices</div>
          </div>
          <div class="protection-item">
            <div class="protection-label">Encryption Status</div>
            <div class="protection-value">{{ encryptionEnabled }}%</div>
            <el-progress :percentage="encryptionEnabled" :stroke-width="8" :color="getScoreColor(encryptionEnabled)" />
            <div class="protection-detail">{{ encryptedDevices }}/{{ totalDevices }} devices</div>
          </div>
          <div class="protection-item">
            <div class="protection-label">Patch Compliance</div>
            <div class="protection-value">{{ patchCompliance }}%</div>
            <el-progress :percentage="patchCompliance" :stroke-width="8" :color="getScoreColor(patchCompliance)" />
            <div class="protection-detail">{{ patchedDevices }}/{{ totalDevices }} up to date</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- Quick Actions Footer -->
    <div class="footer-actions">
      <div class="action-group">
        <el-button type="primary" plain @click="scheduleDeviceScan">
          <el-icon><Calendar /></el-icon>
          Schedule Scan
        </el-button>
        <el-button type="success" plain @click="generateComplianceReport">
          <el-icon><Document /></el-icon>
          Compliance Report
        </el-button>
        <el-button type="warning" plain @click="isolateDevice">
          <el-icon><Lock /></el-icon>
          Isolate Device
        </el-button>
        <el-button type="info" plain @click="viewAuditLogs">
          <el-icon><List /></el-icon>
          Audit Logs
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
  Refresh, Download, Setting, PieChart, TrendCharts, Monitor, Lock,
  WarningFilled, Calendar, Document, List, Cpu, Key, User
} from '@element-plus/icons-vue'

// Loading state
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Initializing Device Security Module...')

const loadingMessages = [
  'Initializing Device Security Module...',
  'Loading device inventory...',
  'Analyzing security posture...',
  'Device security dashboard ready!'
]

// Summary statistics
const totalDevices = ref(342)
const compliantDevices = ref(267)
const nonCompliantDevices = ref(75)
const atRiskDevices = ref(23)
const avgSecurityScore = ref(78)
const complianceRate = computed(() => Math.round((compliantDevices.value / totalDevices.value) * 100))

// Device inventory
const devices = ref([
  { id: 1, name: 'SRV-DC-01', type: 'server', ip: '192.168.1.10', os: 'Windows Server 2022', securityScore: 92, complianceStatus: 'Compliant', lastScan: '2024-01-15' },
  { id: 2, name: 'SRV-DC-02', type: 'server', ip: '192.168.1.11', os: 'Windows Server 2022', securityScore: 88, complianceStatus: 'Compliant', lastScan: '2024-01-15' },
  { id: 3, name: 'WS-ENG-01', type: 'workstation', ip: '192.168.1.50', os: 'Windows 11 Pro', securityScore: 75, complianceStatus: 'Non-Compliant', lastScan: '2024-01-14' },
  { id: 4, name: 'WS-ENG-02', type: 'workstation', ip: '192.168.1.51', os: 'Windows 11 Pro', securityScore: 82, complianceStatus: 'Compliant', lastScan: '2024-01-14' },
  { id: 5, name: 'GW-BACNET-01', type: 'ot', ip: '192.168.2.10', os: 'Linux Embedded', securityScore: 65, complianceStatus: 'At-Risk', lastScan: '2024-01-13' },
  { id: 6, name: 'SW-CORE-01', type: 'network', ip: '192.168.1.1', os: 'Cisco IOS', securityScore: 85, complianceStatus: 'Compliant', lastScan: '2024-01-15' },
  { id: 7, name: 'FW-EDGE-01', type: 'network', ip: '192.168.1.254', os: 'FortiOS', securityScore: 90, complianceStatus: 'Compliant', lastScan: '2024-01-15' },
  { id: 8, name: 'MB-LAPTOP-01', type: 'mobile', ip: '10.0.0.25', os: 'Windows 11', securityScore: 58, complianceStatus: 'At-Risk', lastScan: '2024-01-12' },
  { id: 9, name: 'HVAC-CTRL-01', type: 'ot', ip: '192.168.3.20', os: 'Proprietary RTOS', securityScore: 45, complianceStatus: 'At-Risk', lastScan: '2024-01-11' },
  { id: 10, name: 'SRV-SQL-01', type: 'server', ip: '192.168.1.20', os: 'Windows Server 2019', securityScore: 80, complianceStatus: 'Compliant', lastScan: '2024-01-15' }
])

const deviceTypeFilter = ref('')
const complianceFilter = ref('')
const deviceSearch = ref('')

const filteredDevices = computed(() => {
  let result = devices.value
  if (deviceTypeFilter.value) {
    result = result.filter(d => d.type === deviceTypeFilter.value)
  }
  if (complianceFilter.value) {
    result = result.filter(d => d.complianceStatus.toLowerCase() === complianceFilter.value)
  }
  if (deviceSearch.value) {
    const search = deviceSearch.value.toLowerCase()
    result = result.filter(d => d.name.toLowerCase().includes(search) || d.ip.includes(search))
  }
  return result
})

// Security policies
const securityPolicies = ref([
  { name: 'Antivirus Requirement', category: 'Endpoint Protection', compliance: 94, affectedDevices: 342, status: 'Active' },
  { name: 'OS Patch Level', category: 'Patch Management', compliance: 82, affectedDevices: 310, status: 'Active' },
  { name: 'Disk Encryption', category: 'Data Protection', compliance: 76, affectedDevices: 298, status: 'Active' },
  { name: 'Firewall Configuration', category: 'Network Security', compliance: 88, affectedDevices: 325, status: 'Active' },
  { name: 'Least Privilege Access', category: 'Access Control', compliance: 71, affectedDevices: 280, status: 'Active' }
])

// Compliance violations
const violations = ref([
  { id: 1, device: 'WS-ENG-01', violation: 'Missing critical security patches (KB5034441)', severity: 'High', detected: '2024-01-14', remediation: 'Install Windows Update' },
  { id: 2, device: 'GW-BACNET-01', violation: 'Default credentials still active', severity: 'Critical', detected: '2024-01-13', remediation: 'Change default passwords' },
  { id: 3, device: 'MB-LAPTOP-01', violation: 'Antivirus definitions out of date', severity: 'Medium', detected: '2024-01-12', remediation: 'Update antivirus signatures' },
  { id: 4, device: 'HVAC-CTRL-01', violation: 'TLS 1.0 enabled (deprecated protocol)', severity: 'High', detected: '2024-01-11', remediation: 'Disable TLS 1.0, enable TLS 1.2' },
  { id: 5, device: 'WS-ENG-02', violation: 'Local admin privileges granted', severity: 'Medium', detected: '2024-01-10', remediation: 'Remove local admin rights' }
])

// Endpoint protection stats
const antivirusCoverage = ref(94)
const antivirusProtected = ref(321)
const firewallEnabled = ref(88)
const firewallActive = ref(301)
const encryptionEnabled = ref(76)
const encryptedDevices = ref(260)
const patchCompliance = ref(82)
const patchedDevices = ref(280)

// Chart refs
const distributionChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()

let distributionChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// Helper functions
const getScoreColor = (score: number) => {
  if (score >= 80) return '#10b981'
  if (score >= 60) return '#3b82f6'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

const getDeviceTypeTag = (type: string) => {
  switch (type) {
    case 'server': return 'danger'
    case 'workstation': return 'primary'
    case 'network': return 'success'
    case 'ot': return 'warning'
    case 'mobile': return 'info'
    default: return ''
  }
}

const getComplianceTagType = (status: string) => {
  switch (status) {
    case 'Compliant': return 'success'
    case 'Non-Compliant': return 'warning'
    case 'At-Risk': return 'danger'
    default: return 'info'
  }
}

const getSeverityType = (severity: string) => {
  switch (severity) {
    case 'Critical': return 'danger'
    case 'High': return 'warning'
    case 'Medium': return 'primary'
    default: return 'info'
  }
}

// Initialize distribution chart
const initDistributionChart = () => {
  if (!distributionChartRef.value) return
  distributionChart = echarts.init(distributionChartRef.value)
  const option = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: '55%',
      data: [
        { value: compliantDevices.value, name: 'Compliant', itemStyle: { color: '#10b981' } },
        { value: nonCompliantDevices.value - atRiskDevices.value, name: 'Non-Compliant', itemStyle: { color: '#f59e0b' } },
        { value: atRiskDevices.value, name: 'At-Risk', itemStyle: { color: '#ef4444' } }
      ],
      label: { formatter: '{b}: {d}%' },
      emphasis: { scale: true }
    }]
  }
  distributionChart.setOption(option)
}

// Initialize trend chart
const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['Compliant', 'Non-Compliant', 'At-Risk'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'] },
    yAxis: { type: 'value', name: 'Number of Devices' },
    series: [
      { name: 'Compliant', type: 'line', data: [245, 250, 258, 262, 265, 267], lineStyle: { color: '#10b981', width: 2 }, smooth: true, areaStyle: { opacity: 0.1 } },
      { name: 'Non-Compliant', type: 'line', data: [65, 62, 58, 55, 52, 52], lineStyle: { color: '#f59e0b', width: 2 }, smooth: true, areaStyle: { opacity: 0.1 } },
      { name: 'At-Risk', type: 'line', data: [32, 30, 28, 26, 24, 23], lineStyle: { color: '#ef4444', width: 2 }, smooth: true, areaStyle: { opacity: 0.1 } }
    ]
  }
  trendChart.setOption(option)
}

// Event handlers
const runDeviceScan = () => {
  ElMessage.info('Initiating device security scan across all endpoints...')
  setTimeout(() => {
    ElMessage.success('Device scan completed. 12 new vulnerabilities detected.')
  }, 8000)
}

const exportDeviceReport = () => {
  ElMessage.info('Exporting device security report...')
  setTimeout(() => {
    ElMessage.success('Report exported successfully')
  }, 2000)
}

const configurePolicies = () => {
  ElMessage.info('Opening policy configuration')
}

const refreshDistributionChart = () => {
  if (distributionChart) {
    distributionChart.setOption({ series: [] })
    initDistributionChart()
    ElMessage.success('Chart refreshed')
  }
}

const refreshTrendChart = () => {
  if (trendChart) {
    trendChart.setOption({ series: [] })
    initTrendChart()
    ElMessage.success('Chart refreshed')
  }
}

const applyFilters = () => {
  ElMessage.info('Filters applied')
}

const viewDeviceDetails = (device: any) => {
  ElMessageBox.alert(
      `Device: ${device.name}\nType: ${device.type}\nIP: ${device.ip}\nOS: ${device.os}\nSecurity Score: ${device.securityScore}%\nCompliance: ${device.complianceStatus}\nLast Scan: ${device.lastScan}\n\nInstalled Security Software: Antivirus (Active), Firewall (Enabled)\nPending Patches: 3 critical updates available.`,
      'Device Details',
      { confirmButtonText: 'OK', type: 'info' }
  )
}

const remediateDevice = (device: any) => {
  ElMessageBox.confirm(`Start remediation for ${device.name}? This will apply all recommended security patches and configuration changes.`, 'Remediate Device', {
    confirmButtonText: 'Start',
    cancelButtonText: 'Cancel',
    type: 'info'
  }).then(() => {
    device.securityScore = Math.min(100, device.securityScore + 15)
    if (device.securityScore >= 80) device.complianceStatus = 'Compliant'
    ElMessage.success(`Remediation started for ${device.name}`)
  }).catch(() => {})
}

const createPolicy = () => {
  ElMessage.info('Create new security policy dialog opened')
}

const editPolicy = (policy: any) => {
  ElMessage.info(`Editing policy: ${policy.name}`)
}

const fixViolation = (violation: any) => {
  ElMessageBox.confirm(`Apply fix for: ${violation.violation} on ${violation.device}?`, 'Fix Violation', {
    confirmButtonText: 'Apply Fix',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    violations.value = violations.value.filter(v => v.id !== violation.id)
    ElMessage.success(`Violation fixed on ${violation.device}`)
  }).catch(() => {})
}

const bulkRemediation = () => {
  ElMessage.info('Bulk remediation wizard opened')
}

const refreshProtectionStatus = () => {
  ElMessage.info('Refreshing endpoint protection status')
}

const scheduleDeviceScan = () => {
  ElMessage.info('Schedule device scan dialog opened')
}

const generateComplianceReport = () => {
  ElMessage.info('Generating compliance report...')
}

const isolateDevice = () => {
  ElMessageBox.prompt('Enter device name or IP to isolate', 'Isolate Device', {
    confirmButtonText: 'Isolate',
    cancelButtonText: 'Cancel',
    inputPlaceholder: 'Device name or IP address'
  }).then(({ value }) => {
    ElMessage.warning(`Device ${value} has been isolated from the network`)
  }).catch(() => {})
}

const viewAuditLogs = () => {
  ElMessage.info('Viewing device security audit logs')
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
        initDistributionChart()
        initTrendChart()
      }, 100)
    }, 400)
  }, 2500)
})

onUnmounted(() => {
  if (distributionChart) distributionChart.dispose()
  if (trendChart) trendChart.dispose()
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
.device-security-container {
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

/* Summary Section */
.summary-section {
  margin-bottom: 24px;
}

.summary-card {
  border-radius: 12px;
  background: white;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  padding: 8px;
}

.summary-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.summary-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.summary-value.success { color: #10b981; }
.summary-value.critical { color: #ef4444; }
.summary-value.warning { color: #f59e0b; }

.summary-sub {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
}

/* Charts Row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1.5fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
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

.distribution-chart,
.trend-chart {
  height: 320px;
  width: 100%;
}

/* Inventory Section */
.inventory-section {
  margin-bottom: 24px;
}

.inventory-card {
  border-radius: 12px;
  background: white;
}

.inventory-filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* Policies Section */
.policies-section {
  margin-bottom: 24px;
}

.policies-card {
  border-radius: 12px;
  background: white;
}

/* Violations Section */
.violations-section {
  margin-bottom: 24px;
}

.violations-card {
  border-radius: 12px;
  background: white;
}

/* Protection Section */
.protection-section {
  margin-bottom: 24px;
}

.protection-card {
  border-radius: 12px;
  background: white;
}

.protection-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.protection-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.protection-label {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.protection-value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 8px;
}

.protection-detail {
  font-size: 11px;
  color: #94a3b8;
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
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 1200px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .charts-row {
    grid-template-columns: 1fr;
  }

  .protection-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .protection-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    flex-wrap: wrap;
  }

  .inventory-filters {
    flex-wrap: wrap;
  }

  .action-group {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>