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
          <span class="loading-title">Loading</span>
          <span class="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
        </div>
        <div class="loading-progress">
          <div class="progress-bar" :style="{ width: loadingProgress + '%' }"></div>
        </div>
        <div class="loading-tip">Fault Management System</div>
        <div class="loading-subtip">{{ loadingMessage }}</div>
      </div>
    </div>
  </div>

  <!-- Fault History Page Content -->
  <div v-else class="fault-history-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-title">
        <div class="title-badge">
          <el-icon><List /></el-icon>
          <span>FMS - History</span>
        </div>
        <h1>Fault History</h1>
        <p class="subtitle">Complete historical record of resolved faults with root cause analysis and resolution details</p>
      </div>
      <div class="header-actions">
        <button class="action-btn" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          <span>Refresh</span>
        </button>
        <button class="action-btn primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          <span>Export</span>
        </button>
        <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="to"
            start-placeholder="Start Date"
            end-placeholder="End Date"
            size="default"
            class="date-picker"
            @change="handleDateChange"
        />
      </div>
    </div>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon total">
          <el-icon><List /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ totalResolved }}</div>
          <div class="kpi-label">Total Resolved</div>
        </div>
        <div class="kpi-trend positive">
          <el-icon><CaretTop /></el-icon>
          +8.5%
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon critical">
          <el-icon><CircleCloseFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ criticalResolved }}</div>
          <div class="kpi-label">Critical Resolved</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon major">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ majorResolved }}</div>
          <div class="kpi-label">Major Resolved</div>
        </div>
      </div>
      <div class="kpi-card">
        <div class="kpi-icon minor">
          <el-icon><InfoFilled /></el-icon>
        </div>
        <div class="kpi-info">
          <div class="kpi-value">{{ minorResolved }}</div>
          <div class="kpi-label">Minor Resolved</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Severity</label>
        <select v-model="filters.severity" class="filter-select">
          <option value="all">All Severities</option>
          <option value="critical">Critical</option>
          <option value="major">Major</option>
          <option value="minor">Minor</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Category</label>
        <select v-model="filters.category" class="filter-select">
          <option value="all">All Categories</option>
          <option value="HVAC">HVAC</option>
          <option value="Electrical">Electrical</option>
          <option value="DCIM">DCIM</option>
          <option value="Security">Security</option>
          <option value="Plumbing">Plumbing</option>
          <option value="Lighting">Lighting</option>
          <option value="BMS">BMS</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Resolved By</label>
        <select v-model="filters.resolvedBy" class="filter-select">
          <option value="all">All Technicians</option>
          <option value="Mike Johnson">Mike Johnson</option>
          <option value="John Smith">John Smith</option>
          <option value="Sarah Chen">Sarah Chen</option>
          <option value="Lisa Wong">Lisa Wong</option>
          <option value="Tom Davis">Tom Davis</option>
        </select>
      </div>
      <div class="filter-group">
        <label>Search</label>
        <input type="text" v-model="filters.search" placeholder="Search by title or asset..." class="search-input" />
      </div>
      <button class="clear-btn" @click="clearFilters">Clear All</button>
    </div>

    <!-- Fault History Table -->
    <div class="table-card">
      <el-table :data="paginatedFaults" stripe v-loading="tableLoading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="Fault Title" min-width="220" show-overflow-tooltip />
        <el-table-column prop="category" label="Category" width="110">
          <template #default="{ row }">
            <el-tag size="small">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="Severity" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityTagType(row.severity)" size="small" effect="dark">
              {{ row.severity.toUpperCase() }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="asset" label="Asset" width="130" />
        <el-table-column prop="detectedAt" label="Detected" width="150" sortable />
        <el-table-column prop="resolvedAt" label="Resolved" width="150" sortable />
        <el-table-column prop="resolutionTime" label="Resolution Time" width="160" sortable>
          <template #default="{ row }">
            <span :class="getResolutionTimeClass(row.resolutionTime)">
              {{ row.resolutionTime }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="resolvedBy" label="Resolved By" width="130" />
        <el-table-column label="Actions" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetails(row)">Details</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="filteredFaults.length"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- Fault Detail Drawer -->
    <el-drawer v-model="detailDrawerVisible" title="Fault Details" size="550px" direction="rtl">
      <div class="drawer-content" v-if="selectedFault">
        <div class="detail-section">
          <div class="detail-header">
            <h3>{{ selectedFault.title }}</h3>
            <div class="detail-badges">
              <el-tag :type="getSeverityTagType(selectedFault.severity)" size="large">
                {{ selectedFault.severity.toUpperCase() }}
              </el-tag>
              <el-tag type="success" size="large">RESOLVED</el-tag>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-row">
            <span class="detail-label">Fault ID:</span>
            <span class="detail-value">#{{ selectedFault.id }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Category:</span>
            <span class="detail-value">{{ selectedFault.category }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Asset:</span>
            <span class="detail-value">{{ selectedFault.asset }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Location:</span>
            <span class="detail-value">{{ selectedFault.location }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Detected:</span>
            <span class="detail-value">{{ selectedFault.detectedAt }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Resolved:</span>
            <span class="detail-value">{{ selectedFault.resolvedAt }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Resolution Time:</span>
            <span class="detail-value" :class="getResolutionTimeClass(selectedFault.resolutionTime)">
              {{ selectedFault.resolutionTime }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">Resolved By:</span>
            <span class="detail-value">{{ selectedFault.resolvedBy }}</span>
          </div>
        </div>

        <div class="detail-section">
          <div class="detail-label">Description</div>
          <p class="detail-description">{{ selectedFault.description }}</p>
        </div>

        <div class="detail-section">
          <div class="detail-label">Root Cause Analysis</div>
          <p class="detail-description">{{ selectedFault.rootCause }}</p>
        </div>

        <div class="detail-section">
          <div class="detail-label">Resolution Actions</div>
          <ul class="action-list">
            <li v-for="action in selectedFault.resolutionActions" :key="action">{{ action }}</li>
          </ul>
        </div>

        <div class="detail-section">
          <div class="detail-label">Preventive Measures</div>
          <ul class="action-list">
            <li v-for="measure in selectedFault.preventiveMeasures" :key="measure">{{ measure }}</li>
          </ul>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Refresh, Download, WarningFilled, CircleCloseFilled, InfoFilled,
  List, CaretTop, CaretBottom
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// Loading State
const isLoaded = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('Preparing...')
const tableLoading = ref(false)
const loadingMessages = ['Preparing...', 'Loading fault history...', 'Processing data...', 'Almost ready...']

// Data Models
interface ResolvedFault {
  id: number
  title: string
  category: string
  severity: 'critical' | 'major' | 'minor'
  asset: string
  location: string
  detectedAt: string
  resolvedAt: string
  resolutionTime: string
  resolvedBy: string
  description: string
  rootCause: string
  resolutionActions: string[]
  preventiveMeasures: string[]
}

// State
const dateRange = ref<[Date, Date] | null>(null)
const filters = ref({
  severity: 'all',
  category: 'all',
  resolvedBy: 'all',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(10)
const detailDrawerVisible = ref(false)
const selectedFault = ref<ResolvedFault | null>(null)

// Mock Data - Resolved Faults
const resolvedFaults = ref<ResolvedFault[]>([
  {
    id: 9001, title: 'AHU-103 Fan Belt Failure', category: 'HVAC', severity: 'major', asset: 'AHU-103', location: 'Building A - Mechanical Room',
    detectedAt: '2025-05-25 10:30:00', resolvedAt: '2025-05-25 14:45:00', resolutionTime: '4h 15m', resolvedBy: 'Mike Johnson',
    description: 'AHU-103 fan belt snapped, causing airflow interruption to floors 2-4.',
    rootCause: 'Belt worn beyond service life due to lack of preventive maintenance.',
    resolutionActions: ['Replaced fan belt', 'Realigned pulleys', 'Tension adjustment'],
    preventiveMeasures: ['Implement quarterly belt inspection', 'Schedule replacement every 6 months', 'Install vibration monitoring']
  },
  {
    id: 9002, title: 'UPS Battery Replacement Required', category: 'Electrical', severity: 'critical', asset: 'UPS-02', location: 'Data Center - UPS Room',
    detectedAt: '2025-05-24 08:15:00', resolvedAt: '2025-05-24 16:30:00', resolutionTime: '8h 15m', resolvedBy: 'John Smith',
    description: 'UPS battery string failed self-test, unable to support full load during outage simulation.',
    rootCause: 'Battery end-of-life reached after 5 years of service.',
    resolutionActions: ['Replaced all 40 batteries', 'Cleaned terminals', 'Conducted load test'],
    preventiveMeasures: ['Implement monthly battery monitoring', 'Schedule replacement every 4 years', 'Install temperature monitoring']
  },
  {
    id: 9003, title: 'Server Room Cooling Capacity Degraded', category: 'DCIM', severity: 'major', asset: 'CRAC-02', location: 'Data Center - Row B',
    detectedAt: '2025-05-23 14:20:00', resolvedAt: '2025-05-24 11:00:00', resolutionTime: '20h 40m', resolvedBy: 'Sarah Chen',
    description: 'CRAC-02 cooling capacity reduced by 40%, causing temperature rise in Zone B.',
    rootCause: 'Refrigerant leak due to corroded evaporator coil.',
    resolutionActions: ['Repaired refrigerant leak', 'Recharged refrigerant', 'Cleaned evaporator coil', 'Calibrated sensors'],
    preventiveMeasures: ['Quarterly refrigerant leak check', 'Annual coil inspection', 'Install refrigerant monitoring']
  },
  {
    id: 9004, title: 'Lighting Control System Malfunction', category: 'Lighting', severity: 'minor', asset: 'LCP-03', location: 'Building B - Floor 2',
    detectedAt: '2025-05-22 09:00:00', resolvedAt: '2025-05-22 11:30:00', resolutionTime: '2h 30m', resolvedBy: 'Lisa Wong',
    description: 'Lighting control panel firmware caused intermittent zone control issues.',
    rootCause: 'Outdated firmware version with known bug.',
    resolutionActions: ['Upgraded firmware', 'Reset controller', 'Verified all zones'],
    preventiveMeasures: ['Quarterly firmware review', 'Automated update notifications', 'Backup configuration before updates']
  },
  {
    id: 9005, title: 'Water Pressure Fluctuation', category: 'Plumbing', severity: 'major', asset: 'Booster Pump-01', location: 'Building B - Basement',
    detectedAt: '2025-05-21 13:45:00', resolvedAt: '2025-05-22 09:30:00', resolutionTime: '19h 45m', resolvedBy: 'Tom Davis',
    description: 'Water pressure dropped intermittently affecting restrooms on floors 3-5.',
    rootCause: 'VFD drive parameter corruption causing pump speed instability.',
    resolutionActions: ['Reprogrammed VFD parameters', 'Tested pump operation', 'Verified pressure stability'],
    preventiveMeasures: ['Weekly pressure monitoring', 'Monthly VFD parameter backup', 'Install pressure trend analysis']
  },
  {
    id: 9006, title: 'Access Control Database Sync Error', category: 'Security', severity: 'minor', asset: 'ACS-DB', location: 'Building A - Security Office',
    detectedAt: '2025-05-20 07:30:00', resolvedAt: '2025-05-20 10:15:00', resolutionTime: '2h 45m', resolvedBy: 'Security Team',
    description: 'Access control database synchronization failure between primary and backup servers.',
    rootCause: 'Network timeout during scheduled sync.',
    resolutionActions: ['Restarted sync service', 'Verified data integrity', 'Tested failover'],
    preventiveMeasures: ['Monitor sync logs daily', 'Implement retry mechanism', 'Network optimization']
  },
  {
    id: 9007, title: 'BMS Controller Time Synchronization Issue', category: 'BMS', severity: 'minor', asset: 'BMS-CTRL-05', location: 'Building A - BMS Room',
    detectedAt: '2025-05-19 15:00:00', resolvedAt: '2025-05-19 16:45:00', resolutionTime: '1h 45m', resolvedBy: 'Sarah Chen',
    description: 'BMS controller time drifted causing scheduling misalignment.',
    rootCause: 'NTP server unreachable for 30 days.',
    resolutionActions: ['Resynced NTP configuration', 'Verified time on all controllers', 'Updated network settings'],
    preventiveMeasures: ['Weekly NTP connectivity check', 'Monitor time drift', 'Alert on sync failure']
  },
  {
    id: 9008, title: 'VFD Overheating Alarm', category: 'Electrical', severity: 'major', asset: 'VFD-108', location: 'Building B - Electrical Room',
    detectedAt: '2025-05-18 11:20:00', resolvedAt: '2025-05-18 14:30:00', resolutionTime: '3h 10m', resolvedBy: 'John Smith',
    description: 'VFD reported over-temperature alarm during peak load operation.',
    rootCause: 'Cooling fan failure and dust accumulation on heatsink.',
    resolutionActions: ['Replaced cooling fan', 'Cleaned heatsink', 'Checked airflow', 'Tested operation'],
    preventiveMeasures: ['Quarterly VFD cleaning', 'Monitor temperature trends', 'Replace fans every 3 years']
  },
  {
    id: 9009, title: 'FCU Valve Actuator Stuck', category: 'HVAC', severity: 'minor', asset: 'FCU-108', location: 'Building A - Floor 4',
    detectedAt: '2025-05-17 10:00:00', resolvedAt: '2025-05-17 12:30:00', resolutionTime: '2h 30m', resolvedBy: 'Mike Johnson',
    description: 'FCU-108 water valve actuator stuck in closed position, no cooling.',
    rootCause: 'Actuator gear stripped due to mechanical wear.',
    resolutionActions: ['Replaced actuator', 'Valve stem lubrication', 'Tested operation'],
    preventiveMeasures: ['Annual actuator inspection', 'Track actuator life cycle', 'Install position feedback']
  },
  {
    id: 9010, title: 'Generator Weekly Test Failure', category: 'Electrical', severity: 'critical', asset: 'GEN-02', location: 'Building B - Generator Room',
    detectedAt: '2025-05-16 09:30:00', resolvedAt: '2025-05-17 13:00:00', resolutionTime: '27h 30m', resolvedBy: 'John Smith',
    description: 'Generator failed automatic weekly start test due to battery issue.',
    rootCause: 'Battery charger malfunction causing battery sulfation.',
    resolutionActions: ['Replaced batteries', 'Repaired charger', 'Tested generator', 'Verified auto-start'],
    preventiveMeasures: ['Weekly battery voltage check', 'Monthly load test', 'Annual charger inspection']
  },
  {
    id: 9011, title: 'Network Switch PoE Failure', category: 'Security', severity: 'major', asset: 'SW-05', location: 'Building B - Comms Room',
    detectedAt: '2025-05-15 08:00:00', resolvedAt: '2025-05-15 15:00:00', resolutionTime: '7h', resolvedBy: 'Security Team',
    description: 'Network switch PoE ports failed, cameras offline for 4 hours.',
    rootCause: 'PoE controller chip failure due to power surge.',
    resolutionActions: ['Replaced switch', 'Reconnected cameras', 'Verified coverage', 'Installed surge protector'],
    preventiveMeasures: ['Install UPS protection', 'Annual switch health check', 'Monitor PoE power budget']
  },
  {
    id: 9012, title: 'Chiller High Pressure Trip', category: 'HVAC', severity: 'critical', asset: 'Chiller-03', location: 'Building A - Plant Room',
    detectedAt: '2025-05-14 14:00:00', resolvedAt: '2025-05-15 11:00:00', resolutionTime: '21h', resolvedBy: 'Mike Johnson',
    description: 'Chiller-03 tripped on high pressure, causing cooling loss to Building A.',
    rootCause: 'Condenser tube fouling due to water treatment issues.',
    resolutionActions: ['Cleaned condenser tubes', 'Optimized water treatment', 'Reset chiller', 'Verified operation'],
    preventiveMeasures: ['Monthly water quality testing', 'Bi-annual tube cleaning', 'Monitor approach temperature']
  }
])

// Computed
const totalResolved = computed(() => resolvedFaults.value.length)
const criticalResolved = computed(() => resolvedFaults.value.filter(f => f.severity === 'critical').length)
const majorResolved = computed(() => resolvedFaults.value.filter(f => f.severity === 'major').length)
const minorResolved = computed(() => resolvedFaults.value.filter(f => f.severity === 'minor').length)

const filteredFaults = computed(() => {
  let result = [...resolvedFaults.value]

  if (filters.value.severity !== 'all') {
    result = result.filter(f => f.severity === filters.value.severity)
  }
  if (filters.value.category !== 'all') {
    result = result.filter(f => f.category === filters.value.category)
  }
  if (filters.value.resolvedBy !== 'all') {
    result = result.filter(f => f.resolvedBy === filters.value.resolvedBy)
  }
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(f =>
        f.title.toLowerCase().includes(search) ||
        f.asset.toLowerCase().includes(search) ||
        f.location.toLowerCase().includes(search)
    )
  }
  if (dateRange.value && dateRange.value[0] && dateRange.value[1]) {
    const [start, end] = dateRange.value
    result = result.filter(f => {
      const resolvedDate = new Date(f.resolvedAt)
      return resolvedDate >= start && resolvedDate <= end
    })
  }

  return result
})

const paginatedFaults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFaults.value.slice(start, end)
})

// Helper Functions
const getSeverityTagType = (severity: string) => {
  const map: Record<string, string> = { critical: 'danger', major: 'warning', minor: 'info' }
  return map[severity] || 'info'
}

const getResolutionTimeClass = (time: string) => {
  const hours = parseFloat(time)
  if (hours > 8) return 'text-danger'
  if (hours > 4) return 'text-warning'
  return 'text-success'
}

const clearFilters = () => {
  filters.value = {
    severity: 'all',
    category: 'all',
    resolvedBy: 'all',
    search: ''
  }
  dateRange.value = null
  currentPage.value = 1
}

const handleDateChange = () => {
  currentPage.value = 1
}

// Actions
const refreshData = async () => {
  tableLoading.value = true
  await new Promise(resolve => setTimeout(resolve, 800))
  ElMessage.success('Fault history refreshed')
  tableLoading.value = false
}

const exportReport = () => {
  ElMessage.info('Exporting fault history report...')
}

const viewDetails = (fault: ResolvedFault) => {
  selectedFault.value = fault
  detailDrawerVisible.value = true
}

const handleSizeChange = () => { currentPage.value = 1 }
const handleCurrentChange = () => {}

// Lifecycle
onMounted(() => {
  let idx = 0
  const msgInterval = setInterval(() => {
    if (idx < loadingMessages.length - 1) {
      idx++
      loadingMessage.value = loadingMessages[idx]
    }
  }, 400)
  const progInterval = setInterval(() => {
    if (loadingProgress.value < 100) {
      loadingProgress.value += Math.random() * 15 + 5
      if (loadingProgress.value > 100) loadingProgress.value = 100
    }
  }, 200)
  setTimeout(() => {
    clearInterval(msgInterval)
    clearInterval(progInterval)
    loadingProgress.value = 100
    loadingMessage.value = 'Ready!'
    setTimeout(() => { isLoaded.value = true }, 400)
  }, 2000)
})
</script>

<style scoped>
/* Loading Screen */
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
.loading-dots { display: inline-flex; gap: 2px; }
.loading-dots span { animation: bounce 1.4s infinite ease-in-out both; }
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

/* Main Content */
.fault-history-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}
.title-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: white;
  margin-bottom: 12px;
}
.header-title h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px 0;
}
.header-title .subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}
.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
  background: white;
  color: #475569;
}
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.action-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border: none;
  color: white;
}
.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3);
}
.date-picker {
  background: white;
  border-radius: 10px;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.kpi-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.kpi-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.kpi-icon.total { background: #e8f4ff; color: #3b82f6; }
.kpi-icon.critical { background: #fee2e2; color: #dc2626; }
.kpi-icon.major { background: #fef3c7; color: #d97706; }
.kpi-icon.minor { background: #dbeafe; color: #2563eb; }
.kpi-info { flex: 1; }
.kpi-value { font-size: 28px; font-weight: 700; color: #1a1a2e; }
.kpi-label { font-size: 13px; color: #64748b; margin-top: 4px; }
.kpi-trend { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 2px; }
.kpi-trend.positive { color: #10b981; }
.kpi-trend.negative { color: #dc2626; }

/* Filters Bar */
.filters-bar {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
  padding: 16px 20px;
  background: white;
  border-radius: 16px;
  align-items: flex-end;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.filter-group label {
  font-size: 12px;
  font-weight: 500;
  color: #64748b;
}
.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 13px;
  background: white;
  min-width: 130px;
}
.search-input {
  width: 200px;
}
.clear-btn {
  padding: 8px 20px;
  background: #f1f5f9;
  border: none;
  border-radius: 10px;
  color: #64748b;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  align-self: center;
}
.clear-btn:hover {
  background: #e2e8f0;
}

/* Table Card */
.table-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
.pagination-wrapper {
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #e2e8f0;
  margin-top: 16px;
}
.text-success { color: #10b981; font-weight: 500; }
.text-warning { color: #d97706; font-weight: 500; }
.text-danger { color: #dc2626; font-weight: 500; }

/* Drawer Styles */
.drawer-content {
  padding: 16px;
}
.detail-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}
.detail-section:last-child {
  border-bottom: none;
}
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}
.detail-badges {
  display: flex;
  gap: 8px;
}
.detail-row {
  display: flex;
  margin-bottom: 12px;
}
.detail-label {
  width: 110px;
  color: #64748b;
  font-size: 13px;
}
.detail-value {
  color: #1a1a2e;
  font-size: 13px;
  font-weight: 500;
}
.detail-description {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
}
.action-list {
  margin: 8px 0 0;
  padding-left: 20px;
}
.action-list li {
  color: #475569;
  font-size: 13px;
  margin-bottom: 6px;
}

:deep(.el-table) { border-radius: 12px; }
:deep(.el-table th) { background-color: #fafafa; font-weight: 600; }
:deep(.el-drawer__header) { margin-bottom: 0; padding: 16px 20px; border-bottom: 1px solid #e2e8f0; }
</style>